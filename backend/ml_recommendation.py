"""
ML-Based Route Difficulty Recommender

IMPORTANT: This module provides SUGGESTIONS ONLY.
FairFlow's fairness logic is the final authority.

Architecture: Layer 1 of 3-layer decision support system
- Layer 1: ML Recommendation (this module) - SUGGESTS ONLY
- Layer 2: FairFlow Validation - VALIDATES & OVERRIDES
- Layer 3: Admin Decision - FINAL CONTROL
"""

from typing import Dict, Optional
import math


class RouteDifficultyRecommender:
    """
    ML-based route difficulty recommendation system.
    
    CRITICAL: This is a SUGGESTION system, not a decision system.
    All recommendations must be validated by FairFlow's fairness logic.
    """
    
    def __init__(self):
        # Feature weights for difficulty scoring (rule-based explainable model)
        self.weights = {
            'apartments': 1.5,
            'stairs': 12.0,
            'heavy_boxes': 1.5,
            'traffic': 2.0,
            'weather': 3.0
        }
        
        # Thresholds for difficulty classification
        self.thresholds = {
            'easy': 45,      # Score < 45 = Easy (Generous easy range for high impact)
            'medium': 65,    # Score 45-65 = Medium
            # Score > 65 = Hard
        }
    
    def recommend(
        self, 
        route_features: Dict, 
        driver_context: Dict,
        route_difficulty: str = "Medium"
    ) -> Dict:
        """
        Generate route difficulty recommendation with explanation.
        """
        
        # Calculate base route difficulty score
        route_score = self._calculate_route_score(route_features)
        
        # Calculate driver fatigue factor
        fatigue_factor = self._calculate_fatigue_factor(driver_context)
        
        # Adjust score based on driver context
        adjusted_score = route_score * fatigue_factor
        
        # Classify difficulty
        if adjusted_score < self.thresholds['easy']:
            difficulty = 'Easy'
            confidence = self._calculate_confidence(adjusted_score, 0, self.thresholds['easy'])
        elif adjusted_score < self.thresholds['medium']:
            difficulty = 'Medium'
            confidence = self._calculate_confidence(
                adjusted_score, 
                self.thresholds['easy'], 
                self.thresholds['medium']
            )
        else:
            difficulty = 'Hard'
            confidence = self._calculate_confidence(adjusted_score, self.thresholds['medium'], 100)
        
        # Generate explanation
        reason = self._generate_explanation(
            route_features, 
            driver_context, 
            route_score, 
            fatigue_factor,
            difficulty
        )
        
        return {
            'recommended_difficulty': difficulty,
            'confidence': round(confidence, 2),
            'reason': reason,
            'route_score': round(route_score, 1),
            'driver_fatigue_factor': round(fatigue_factor, 2),
            'preference_score': self.calculate_preference_score(route_features, driver_context, route_difficulty)
        }

    def calculate_preference_score(self, route_features: Dict, context: Dict, route_difficulty: str = "Medium") -> float:
        """
        Calculates ranking score (0-1000).
        STRICT TIERS based on Fairness Logic. NO BLOCKING.
        
        Tiers:
        - Priority 1 (Best Fit): 800 - 1000
        - Priority 2 (Good Fit): 500 - 700
        - Priority 3 (Acceptable): 200 - 400
        """
        driver_state = context.get('driver_state', 'Ready') # Overloaded, Underloaded, Ready
        balance = context.get('fairness_balance', 0.0)
        deviation = context.get('normalized_effort_deviation', 0.0)
        
        base_score = 0.0
        
        # === ROUTE SPECIFIC RANKING ===
        
        if route_difficulty == "Hard":
            # Target: Underloaded > Ready > Overloaded
            if driver_state == "Underloaded":
                # Priority 1: 900 range. Tie-break: Most negative balance (e.g. -50 > -20)
                # Formula: 900 - balance (Since balance < 0, this adds to score)
                # e.g. -50 -> 950, -20 -> 920.
                base_score = 900.0 - balance
            elif driver_state == "Ready":
                # Priority 2: 600 range.
                base_score = 600.0
            else: # Overloaded
                # Priority 3: 300 range. Tie-break: Least positive balance (e.g. 20 > 50)
                # Formula: 300 - balance
                # e.g. 50 -> 250, 20 -> 280.
                base_score = 300.0 - balance

        elif route_difficulty == "Easy":
            # Target: Overloaded > Ready > Underloaded
            if driver_state == "Overloaded":
                # Priority 1: 900 range. Tie-break: Highest positive balance (e.g. 50 > 20)
                # Formula: 900 + balance
                # e.g. 50 -> 950, 20 -> 920.
                base_score = 900.0 + balance
            elif driver_state == "Ready":
                # Priority 2: 600 range.
                base_score = 600.0
            else: # Underloaded
                # Priority 3: 300 range. Tie-break: Least negative balance (e.g. -20 > -50)
                # Formula: 300 + balance (balance is negative)
                # e.g. -20 -> 280, -50 -> 250.
                base_score = 300.0 + balance

        else: # Medium
            # Target: Ready > Underloaded > Overloaded
            if driver_state == "Ready":
                 # Priority 1: 900 range. Tie-break: Closest to team avg (smallest abs deviation)
                 # Formula: 900 - abs(deviation)
                 base_score = 900.0 - abs(deviation)
            elif driver_state == "Underloaded":
                # Priority 2: 600 range.
                base_score = 600.0 - abs(deviation)
            else: # Overloaded
                 # Priority 3: 300 range.
                 base_score = 300.0 - abs(deviation)
        
        # Clamp to ensure valid 0-1000 range
        return round(max(0.0, min(1000.0, base_score)), 1)
    
    def _calculate_route_score(self, features: Dict) -> float:
        """Calculate base difficulty score from route features"""
        score = 0.0
        
        # Distance (Base complexity)
        distance = features.get('distance_km', 0)
        score += distance * 2.0
        
        # Area Type + Floors (Apartment complexity)
        area = features.get('area_type', 'Residential')
        floors = features.get('floors', 1)
        if area == 'Apartment':
            score += 10.0 + (floors * 2.0)
        elif area == 'Commercial':
            score += 10.0
        
        # Stairs (major difficulty factor)
        if features.get('stairs_present', False):
            score += self.weights['stairs'] # Fixed weight multiplier
        
        # Heavy packages (supporting both names for compatibility)
        heavy_pkgs = features.get('heavy_packages_count', features.get('heavy_boxes_count', 0))
        score += heavy_pkgs * self.weights['heavy_boxes']
        
        # Traffic level
        traffic = features.get('traffic_level', 'Normal')
        traffic_score = {'Low': 0, 'Normal': 10, 'High': 25}.get(traffic, 10)
        score += (traffic_score / 5.0) * self.weights['traffic'] # Normalize to previous scale
        
        # Weather severity
        weather = features.get('weather_severity', 'Clear')
        weather_score = {'Clear': 0, 'Rain': 15, 'Snow': 30}.get(weather, 0)
        score += (weather_score / 5.0) * self.weights['weather'] # Normalize to previous scale
        
        return score
    
    def _calculate_fatigue_factor(self, context: Dict) -> float:
        """
        Calculate driver fatigue factor for recommendation adjustment.
        
        High Effort -> Factor < 1.0 (Bias toward Easy)
        Low Effort -> Factor > 1.0 (Bias toward Hard/Medium to balance)
        """
        factor = 1.0
        
        # Normalized effort (effort per working hour)
        normalized_effort = context.get('normalized_effort_last_3_days', 7.5)
        
        # If driver has high effort per hour, decrease factor (recommend easier)
        if normalized_effort > 8.5:
            factor -= 0.15  # Overloaded
        elif normalized_effort > 8.0:
            factor -= 0.05
        elif normalized_effort < 6.5:
            factor += 0.15  # Underloaded
        
        # Consecutive hard routes (if many, recommend easy)
        consecutive = context.get('consecutive_hard_routes', 0)
        if consecutive >= 3:
            factor -= 0.15
        elif consecutive >= 2:
            factor -= 0.1
        
        # Fairness balance
        balance = context.get('fairness_balance', 0)
        if balance > 40:
            factor -= 0.2  # Overloaded -> Bias toward Easy
        elif balance > 15:
            factor -= 0.1
        elif balance < -40:
            factor += 0.2  # Underloaded -> Bias toward Hard
        elif balance < -15:
            factor += 0.1
        
        # Drift severity
        drift = context.get('drift_severity', 'NONE')
        if drift in ['MEDIUM', 'HIGH']:
            if balance < 0: factor -= 0.05
            if balance > 0: factor += 0.05
        
        return max(0.7, min(1.4, factor))  # Clamp between 0.7 and 1.4 (prioritize route complexity)
    
    def _calculate_confidence(self, score: float, lower: float, upper: float) -> float:
        """Calculate confidence based on how clearly the score fits in a category"""
        
        # Calculate distance from boundaries
        range_size = upper - lower if upper > lower else 10
        center = (lower + upper) / 2
        
        # Distance from center (closer to center = higher confidence)
        distance_from_center = abs(score - center)
        max_distance = range_size / 2
        
        # Confidence: 100% at center, decreases toward boundaries
        if max_distance > 0:
            confidence = 1.0 - (distance_from_center / max_distance) * 0.3
        else:
            confidence = 0.85
        
        return max(0.5, min(1.0, confidence))
    
    def _generate_explanation(
        self, 
        route_features: Dict,
        driver_context: Dict,
        route_score: float,
        fatigue_factor: float,
        difficulty: str
    ) -> str:
        """Generate human-readable explanation for recommendation"""
        
        parts = []
        
        # Route complexity
        area = route_features.get('area_type', 'Residential')
        floors = route_features.get('floors', 1)
        stairs = route_features.get('stairs_present', False)
        heavy_pkgs = route_features.get('heavy_packages_count', route_features.get('heavy_boxes_count', 0))
        distance = route_features.get('distance_km', 0)
        
        if area == 'Apartment':
            parts.append(f"{floors}-floor apartment")
        elif area == 'Commercial':
            parts.append("commercial area")
        
        if stairs:
            parts.append("stairs present")
        
        if heavy_pkgs > 5:
            parts.append("many heavy packages")
        
        if distance > 15:
            parts.append("long distance")
        
        # Environmental factors
        traffic = route_features.get('traffic_level', 'Normal')
        weather = route_features.get('weather_severity', 'Clear')
        
        if traffic == 'High':
            parts.append("heavy traffic")
        
        if weather in ['Rain', 'Snow']:
            parts.append(f"{weather.lower()}y conditions")
        
        # Driver context (Logic: Factor > 1.0 means capacity available to balance team)
        if fatigue_factor > 1.15:
            parts.append("driver has workload capacity")
        elif fatigue_factor < 0.85:
            parts.append("driver requires fairness protection")
        
        if not parts:
            parts.append("balanced route and driver conditions")
            
        route_desc = ", ".join(parts[:4])  # Take first 4 factors
        
        return f"{route_desc.capitalize()}. Route score: {route_score:.1f}, driver context considered."
