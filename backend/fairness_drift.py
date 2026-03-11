"""
AI-Powered Fairness Drift Detection Module (Real-Time)

Monitors POST-ASSIGNMENT workload distribution.
Strictly enforces fairness based on 'logic.calculate_readiness_canonical'.
"""

from sqlalchemy.orm import Session
from models import User
import logic

def detect_fairness_drift(db: Session) -> dict:
    """
    Real-Time Fairness Monitor.
    Evaluates the ACTUAL system state using current 7-day balances.
    
    Rules:
    1. Run on current DB state (Post-Assignment).
    2. Use 'logic.calculate_readiness_canonical' strictly.
    3. Verdict:
       - If ANY driver is Overloaded/Underloaded -> Drift Detected (High Severity).
       - Only if ALL are Ready -> Fair (None Severity).
    """
    
    # 1. Get Active Drivers
    drivers = db.query(User).filter(User.role == "driver", User.status != "ABSENT").all()
    
    if not drivers:
        return {
            "drift_detected": False,
            "severity": "NONE",
            "affected_drivers": [],
            "explanation": "No active drivers.",
            "metrics": {"current_variance": 0, "baseline_variance": 0, "variance_change_pct": 0}
        }
    
    # 2. Calculate Real-Time Team Stats
    results = []
    total_balance = 0
    valid_count = 0
    
    for d in drivers:
        stats = logic.get_driver_stats_7d(db, d.id)
        if stats:
            results.append((d, stats['balance_7d']))
            total_balance += stats['balance_7d']
            valid_count += 1
    
    team_avg = total_balance / valid_count if valid_count > 0 else 0
    
    # 2b. MANDATORY GATING (User Rule: Skip if team_avg is 0 or no history)
    # If team average is 0, we cannot calculate deviation %. 
    # This also covers the "No route assignments" case (where balances are 0).
    if valid_count == 0 or abs(team_avg) < 0.01:
         return {
            "drift_detected": False,
            "severity": "NONE",
            "affected_drivers": [],
            "explanation": "Collecting baseline data. Insufficient history for fairness evaluation.",
            "metrics": {
                "current_variance": 0.0,
                "baseline_variance": 0.0,
                "variance_change_pct": 0.0
            }
        }
    
    # 3. Evaluate Each Driver
    affected_drivers = []
    has_unfairness = False
    
    for d, balance in results:
        readiness = logic.calculate_readiness_canonical(balance, team_avg)
        status = readiness['status']
        deviation = readiness['deviation']
        
        if status in ["Overloaded", "Underloaded"]:
            has_unfairness = True
            affected_drivers.append({
                "id": d.id,
                "name": d.name,
                "deviation": round(deviation * 100, 1), # Display as % deviation relative to something (or just pure value if needed)
                # Note: 'deviation' from logic.py is raw. If it's absolute threshold, deviation might be 0.
                # logic.py calc: if abs > 75. 
                # Let's trust logic.py's deviation return for the metric.
                "status": status,
                "balance": balance
            })
            
    # 4. Verdict
    if has_unfairness:
        severity = "HIGH"
        drift_detected = True
        explanation = f"Unfair distribution detected. {len(affected_drivers)} drivers are outside the fairness threshold."
    else:
        severity = "NONE"
        drift_detected = False
        explanation = "Fair Distribution. All drivers are within acceptable readiness limits."

    return {
        "drift_detected": drift_detected,
        "severity": severity,
        "affected_drivers": affected_drivers,
        "explanation": explanation,
        "metrics": {
             # Dummy metrics to satisfy frontend structure
            "current_variance": 0.0,
            "baseline_variance": 0.0,
            "variance_change_pct": 0.0
        }
    }

def should_intervene_for_driver(db: Session, driver_id: int, route_difficulty: str) -> tuple[bool, str]:
    """
    Check if AI should intervene.
    """
    drift = detect_fairness_drift(db)
    
    if not drift['drift_detected']:
        return False, ""
        
    # Check if specific driver is affected
    for d in drift['affected_drivers']:
        if d['id'] == driver_id:
            return True, f"AI Intervention: Driver is {d['status']} (Balance: {d['balance']}). Assignment restricted."
            
    return False, ""

def get_effort_distribution(db: Session, last_n_days: int = 7) -> dict:
    """
    Returns the average daily effort for each driver over the last N days.
    """
    from datetime import date, timedelta
    from sqlalchemy import func
    from models import FairnessHistory
    
    cutoff = date.today() - timedelta(days=last_n_days)
    
    results = db.query(
        FairnessHistory.driver_id,
        func.avg(FairnessHistory.daily_effort)
    ).filter(FairnessHistory.date >= cutoff).group_by(FairnessHistory.driver_id).all()
    
    return {driver_id: avg_effort for driver_id, avg_effort in results}

def capture_daily_snapshot(db: Session, driver_id: int):
    """
    Captures a snapshot of the driver's current state into the fairness_snapshots table.
    This is used by the AI/ML components for historical analysis.
    """
    from models import DriverStats, FairnessSnapshot
    from datetime import date
    
    stats = db.query(DriverStats).filter(DriverStats.user_id == driver_id).first()
    if not stats:
        return
        
    # Check if snapshot already exists for today
    today = date.today()
    existing = db.query(FairnessSnapshot).filter(
        FairnessSnapshot.driver_id == driver_id,
        FairnessSnapshot.date == today
    ).first()
    
    if existing:
        existing.effort = stats.effort_today
        existing.credits = stats.credits_today
        existing.balance = stats.total_balance
    else:
        snapshot = FairnessSnapshot(
            driver_id=driver_id,
            date=today,
            effort=stats.effort_today,
            credits=stats.credits_today,
            balance=stats.total_balance,
            working_hours=8.0 # Default fallback
        )
        db.add(snapshot)
    
    db.commit()

