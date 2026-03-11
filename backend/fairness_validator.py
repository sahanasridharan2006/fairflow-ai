"""
FairFlow Fairness Validator

AUTHORITY LAYER: This module validates ML recommendations against 
working-hours-based fairness rules and can OVERRIDE ML suggestions.

Architecture: Layer 2 of 3-layer decision support system
- Layer 1: ML Recommendation - SUGGESTS
- Layer 2: FairFlow Validation (this module) - VALIDATES & OVERRIDES
- Layer 3: Admin Decision - FINAL CONTROL

CRITICAL: FairFlow ALWAYS has veto power over ML suggestions.
"""

from typing import Dict, Tuple, List
from sqlalchemy.orm import Session
from models import User, DriverStats, FairnessSnapshot
from fairness_drift import detect_fairness_drift, get_effort_distribution
from working_hours import get_working_hours
import statistics


class FairnessValidator:
    """
    FairFlow authority layer that validates and overrides ML recommendations.
    
    This ensures working-hours-based fairness is preserved regardless of ML suggestions.
    """
    
    def validate_recommendation(
        self,
        ml_recommendation: Dict,
        driver_id: int,
        db: Session
    ) -> Dict:
        """
        Apply FairFlow working-hours fairness rules to validate ML suggestion.
        
        Args:
            ml_recommendation: {
                'recommended_difficulty': str,
                'confidence': float,
                'reason': str,
                'preference_score': float
            }
            driver_id: int
            db: Database session
        
        Returns: {
            'approved_difficulty': str,
            'approved_levels': List[str],
            'blocked_levels': List[str],
            'action': 'approved' | 'adjusted' | 'blocked',
            'reason': str,
            'ml_suggestion': str,
            'fairness_override': bool,
            'override_reason': str | None,
            'readiness': str  # Added for ranking gating
        }
        """
        
        ml_difficulty = ml_recommendation['recommended_difficulty']
        
        # Get driver and stats
        driver = db.query(User).filter(User.id == driver_id).first()
        stats = db.query(DriverStats).filter(DriverStats.user_id == driver_id).first()
        
        if not driver or not stats:
            return self._block_response(
                ml_difficulty,
                "Driver not found or has no stats"
            )
        
        # MANDATORY CHECK 1: Driver status
        if driver.status in ['ABSENT', 'SICK']:
            return self._block_response(
                ml_difficulty,
                f"Driver status is {driver.status}. No routes should be assigned."
            )
        
        # MANDATORY CHECK 2: Working hours
        working_hours = get_working_hours(driver.status)
        if working_hours == 0:
            return self._block_response(
                ml_difficulty,
                "Driver has 0 working hours today. Cannot assign routes."
            )

        # 3. Check for Overload (Normalized Effort)
        overload_status = self._check_normalized_effort_overload(driver_id, db)
        
        # 4. Check for Fatigue (Consecutive Hard Routes)
        consecutive_hard = self._check_consecutive_hard_routes(driver_id, db)
        
        # === FAIRNESS LOGIC ===
        
        # RULE 1: Overloaded drivers cannot take Hard routes
        if overload_status['is_overloaded'] and ml_difficulty == 'Hard':
            return self._adjust_response(
                ml_difficulty,
                'Medium',
                f"Driver is Overloaded ({int(overload_status['deviation'])}% above avg). Downgrading to protect fairness."
            )
            
        # RULE 2: Driver fatigue (consecutive hard routes)
        if consecutive_hard >= 2 and ml_difficulty == 'Hard':
             return self._adjust_response(
                ml_difficulty,
                'Medium',
                f"Driver has {consecutive_hard} consecutive hard routes. Downgrading to prevent burnout."
            )
            
        # RULE 3: Underloaded drivers should ideally get Hard/Medium (Recommendation only)
        # We don't block them from taking Easy, but we might flag it.
        # For now, we approve ML suggestion if it passes negative checks.
        
        return self._approve_response(
            ml_difficulty,
            "Validation successful. No fairness constraints violated."
        )

    def rank_drivers(self, driver_results: List[Dict], route_difficulty: str = "Medium") -> List[Dict]:
        """
        STRICT FAIRNESS RANKING (Backend Only)
        
        Rules:
        1. All ACTIVE drivers participate (blocked only if ABSENT/SICK).
        2. Primary Key: fairness_balance.
        3. Tie-breaker: ML Score.
        
        Logic per Difficulty:
        - Easy:   Overloaded (DESC) > Ready (ABS) > Underloaded (DESC)
        - Medium: Ready (ABS) > Underloaded (DESC) > Overloaded (ASC)
        - Hard:   Underloaded (ASC) > Ready (ABS) > Overloaded (ASC)
        """
        # 1. ELIGIBILITY FILTER
        # Exclude drivers blocked by validation (Absent, Sick, 0 hours)
        eligible = [d for d in driver_results if d['fairflow_decision']['action'] != 'blocked']
        
        def ranking_key(item):
            # Extract metrics
            ctx = item.get('driver_context', {})
            state = ctx.get('driver_state', 'Ready')
            balance = ctx.get('fairness_balance', 0)
            ml_score = item['ml_recommendation'].get('preference_score', 0)
            
            # Priorities (Lower is better)
            priority = 99
            sort_val = 0.0
            
            if route_difficulty == 'Easy':
                # Purpose: reduce overload
                # Order: Overloaded (0) > Ready (1) > Underloaded (2)
                if state == 'Overloaded':
                    priority = 0
                    sort_val = -balance # DESC (Highest positive first, e.g. 200 before 50)
                elif state == 'Ready':
                    priority = 1
                    sort_val = abs(balance) # Closest to zero
                else: # Underloaded
                    priority = 2
                    sort_val = -balance # DESC (Least negative first, e.g. -10 before -100)
            
            elif route_difficulty == 'Medium':
                # Purpose: neutral balancing
                # Order: Ready (0) > Underloaded (1) > Overloaded (2)
                if state == 'Ready':
                    priority = 0
                    sort_val = abs(balance) # Closest to zero
                elif state == 'Underloaded':
                    priority = 1
                    sort_val = -balance # DESC (Closer to zero first, e.g. -10 before -100)
                else: # Overloaded
                    priority = 2
                    sort_val = balance # ASC (Closer to zero first, e.g. 10 before 100)
                    
            elif route_difficulty == 'Hard':
                # Purpose: fix underloading
                # Order: Underloaded (0) > Ready (1) > Overloaded (2)
                if state == 'Underloaded':
                    priority = 0
                    sort_val = balance # ASC (Most negative first, e.g. -100 before -10)
                elif state == 'Ready':
                    priority = 1
                    sort_val = abs(balance)
                else: # Overloaded
                    priority = 2
                    sort_val = balance # ASC (Least positive first, e.g. 10 before 100)

            # Tuple: Priority, Primary Sort, Tie-Breaker (ML Score Desc)
            return (priority, sort_val, -ml_score)

        # 2. SORT
        eligible.sort(key=ranking_key)
        
        # 3. RANKING & LABELING
        for i, result in enumerate(eligible):
            rank = i + 1
            result['preference_rank'] = rank
            
            # Labeling
            if rank == 1:
                result['preference_label'] = "Best Fit"
            elif rank <= 3:
                result['preference_label'] = "Good Fit"
            else:
                result['preference_label'] = "Acceptable"
                
        # Handle blocked items
        for result in driver_results:
            if result not in eligible:
                result['preference_rank'] = None
                result['preference_label'] = "Not Recommended"
        
        # Return sorted list (Eligible first)
        return sorted(driver_results, key=lambda x: (x['preference_rank'] is None, x['preference_rank'] if x['preference_rank'] else 999))
    
    def _check_normalized_effort_overload(self, driver_id: int, db: Session) -> Dict:
        """
        Check if driver is overloaded based on normalized effort per working hour.
        """
        effort_dist = get_effort_distribution(db, last_n_days=3)
        
        if len(effort_dist) < 2:
            return {'is_overloaded': False, 'deviation': 0.0}
        
        team_avg = statistics.mean(effort_dist.values())
        driver_avg = effort_dist.get(driver_id, team_avg)
        
        if team_avg > 0:
            deviation = ((driver_avg - team_avg) / team_avg) * 100
        else:
            deviation = 0.0
        
        is_overloaded = deviation > 20
        
        return {
            'is_overloaded': is_overloaded,
            'deviation': deviation
        }
    
    def _check_consecutive_hard_routes(self, driver_id: int, db: Session) -> int:
        """Count consecutive hard routes for this driver"""
        from datetime import date, timedelta
        from models import Route
        
        cutoff = date.today() - timedelta(days=7)
        routes = db.query(Route).filter(
            Route.driver_id == driver_id,
            Route.date >= cutoff
        ).order_by(Route.date.desc()).limit(10).all()
        
        consecutive = 0
        for route in routes:
            if route.difficulty == 'Hard':
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _approve_response(self, ml_difficulty: str, reason: str, readiness: str = 'Ready') -> Dict:
        return {
            'approved_difficulty': ml_difficulty,
            'approved_levels': ['Easy', 'Medium', 'Hard'],
            'blocked_levels': [],
            'action': 'approved',
            'reason': reason,
            'ml_suggestion': ml_difficulty,
            'fairness_override': False,
            'override_reason': None,
            'readiness': readiness
        }
    
    def _adjust_response(
        self, 
        ml_difficulty: str, 
        new_difficulty: str, 
        reason: str,
        approved: list = None,
        blocked: list = None,
        readiness: str = 'Ready'
    ) -> Dict:
        if approved is None:
            if new_difficulty == 'Easy':
                approved = ['Easy']
                blocked = ['Medium', 'Hard']
            elif new_difficulty == 'Medium':
                approved = ['Easy', 'Medium']
                blocked = ['Hard']
            else:
                approved = ['Easy', 'Medium', 'Hard']
                blocked = []
        
        return {
            'approved_difficulty': new_difficulty,
            'approved_levels': approved,
            'blocked_levels': blocked if blocked else [],
            'action': 'adjusted',
            'reason': reason,
            'ml_suggestion': ml_difficulty,
            'fairness_override': True,
            'override_reason': f"Downgraded from {ml_difficulty} to {new_difficulty}",
            'readiness': readiness
        }
    
    def _block_response(self, ml_difficulty: str, reason: str, readiness: str = 'Ready') -> Dict:
        return {
            'approved_difficulty': 'Blocked',
            'approved_levels': [],
            'blocked_levels': ['Easy', 'Medium', 'Hard'],
            'action': 'blocked',
            'reason': reason,
            'ml_suggestion': ml_difficulty,
            'fairness_override': True,
            'override_reason': 'Assignment blocked by FairFlow',
            'readiness': readiness
        }
