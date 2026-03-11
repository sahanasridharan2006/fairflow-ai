from datetime import date
from sqlalchemy.orm import Session
from models import DriverStats, User, Route, FairnessHistory

# Constants for Effort Calculation
EFFORT_FACTORS = {
    "apartment": 10,
    "stairs": 15,
    "heavy_box": 20,
    "traffic": 10,
    "weather": 10,
    "distance": 2
}

SAFEGUARD_THRESHOLD = -500

def calculate_effort_score(route_data: dict) -> float:
    """
    Calculates a workload effort score based on simple factors.
    """
    score = 0
    score += route_data.get("apartments", 0) * 10
    if route_data.get("stairs", False):
        score += 15
    score += route_data.get("heavy_boxes", 0) * 20
    if route_data.get("traffic", False):
        score += 10
    if route_data.get("rain", False):
        score += 10
    return float(score)

def calculate_team_average(db: Session) -> float:
    """
    Calculate team average excluding ABSENT drivers.
    Only ACTIVE and SICK drivers are included.
    """
    eligible_drivers = db.query(User).filter(
        User.role == "driver",
        User.status.in_(["ACTIVE", "SICK"])
    ).all()
    
    if not eligible_drivers:
        return 0.0
    
    total_effort = 0
    for driver in eligible_drivers:
        stats = db.query(DriverStats).filter(DriverStats.user_id == driver.id).first()
        if stats:
            total_effort += stats.effort_today or 0
    
    return total_effort / len(eligible_drivers)

def can_assign_route(driver, effort_score: float, team_avg: float, db: Session) -> tuple[bool, str]:
    """
    FIX ISSUE #2: Check if route can be assigned based on adaptive threshold.
    Hard route is defined as: effort_score >= team_avg
    """
    # Check if ABSENT
    if driver.status == "ABSENT":
        return False, "Driver is Absent"
    
    # Check if route is considered "Hard" (adaptive threshold)
    is_hard = effort_score >= team_avg if team_avg > 0 else effort_score >= 70
    
    if is_hard:
        # Block SICK drivers from hard routes
        if driver.status == "SICK":
            return False, "Protected: Sick Driver - Cannot assign hard route (effort >= team average)"
        
        # Block drivers with low balance
        stats = db.query(DriverStats).filter(DriverStats.user_id == driver.id).first()
        if stats and stats.total_balance < SAFEGUARD_THRESHOLD:
            return False, f"Fairness Balance ({stats.total_balance}) is below threshold ({SAFEGUARD_THRESHOLD})"
    
    return True, "Driver is available for assignment"

def update_fairness_ledger(driver_id: int, today_effort: float, team_avg: float, db: Session):
    """
    Updates the fairness ledger for a driver. 
    Handles UPSERT to prevent double-counting if assigned multiple times in a day.
    """
    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver or driver.status == "ABSENT":
        return # Do not update for absent drivers
        
    stats = db.query(DriverStats).filter(DriverStats.user_id == driver_id).first()
    if not stats:
        return
    
    # Check for existing history for today
    today = date.today()
    existing_history = db.query(FairnessHistory).filter(
        FairnessHistory.driver_id == driver_id, 
        FairnessHistory.date == today
    ).first()
    
    # If updating, first revert the previous impact on balance
    if existing_history:
        stats.total_balance -= existing_history.credits_earned
    
    # Calculate new credits
    credits = today_effort - team_avg
    
    if driver.status == "SICK":
        # Sick drivers do not lose credits on lighter routes
        if credits < 0:
            credits = 0
            
    # Update Stats
    stats.effort_today = today_effort
    stats.credits_today = credits
    stats.total_balance += credits
    
    # Update or Create History
    if existing_history:
        existing_history.daily_effort = today_effort
        existing_history.team_average = team_avg
        existing_history.credits_earned = credits
        existing_history.balance_snapshot = stats.total_balance
    else:
        history = FairnessHistory(
            driver_id=driver_id,
            date=today,
            daily_effort=today_effort,
            team_average=team_avg,
            credits_earned=credits,
            balance_snapshot=stats.total_balance
        )
        db.add(history)
        
    db.commit()

def assign_route_to_driver(driver_id: int, route_factors: dict, db: Session, difficulty: str = None, address: str = None) -> dict:
    """
    FIX ISSUE #3: Shared assignment logic to avoid duplication.
    
    This function:
    1. Calculates effort score
    2. Calculates team average
    3. Applies safeguards (ABSENT, SICK, balance)
    4. Updates fairness ledger
    5. Saves route to database
    
    Returns: Assignment result with effort, credits, balance
    """
    from models import Route
    
    # 1. Fetch driver
    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver:
        raise ValueError(f"Driver with ID {driver_id} not found")
    
    if driver.role != "driver":
        raise ValueError("User is not a driver")
    
    # 2. Calculate effort score
    effort_score = calculate_effort_score(route_factors)
    
    # 3. Calculate team average (before this assignment)
    team_avg = calculate_team_average(db)
    
    # 4. Get or create driver stats
    stats = db.query(DriverStats).filter(DriverStats.user_id == driver.id).first()
    if not stats:
        stats = DriverStats(
            user_id=driver.id,
            total_balance=0,
            effort_today=0,
            credits_today=0
        )
        db.add(stats)
        db.flush()
    
    # 5. Apply safeguards (adaptive threshold)
    can_assign, reason = can_assign_route(driver, effort_score, team_avg, db)
    if not can_assign:
        raise ValueError(f"Assignment blocked: {reason}")
    
    # 6. Update fairness ledger
    update_fairness_ledger(driver.id, effort_score, team_avg, db)
    
    # Refresh stats after update
    db.refresh(stats)
    
    # 7. EXCLUSIVITY: Remove any previous assignments for this driver OR this address TODAY
    # This ensures "One Driver, One Route" and "One Route, One Driver"
    db.query(Route).filter(
        Route.date == date.today(),
        (Route.driver_id == driver.id) | (Route.address == address)
    ).delete(synchronize_session=False)

    # 8. Save new route
    route = Route(
        driver_id=driver.id,
        address=address,
        difficulty=difficulty if difficulty else ("Hard" if effort_score > 75 else "Medium" if effort_score >= 50 else "Easy"),
        date=date.today(),
        stops=10,
        apartments=route_factors.get("apartments", 0),
        stairs=route_factors.get("stairs", False),
        heavy_boxes=route_factors.get("heavy_boxes", 0),
        traffic_level="High" if route_factors.get("traffic", False) else "Low",
        weather_condition="Rain" if route_factors.get("rain", False) else "Clear",
        calculated_effort_score=effort_score,
        status="assigned"
    )
    db.add(route)
    db.commit()
    
    return {
        "status": "success",
        "driver_name": driver.name,
        "effort_score": effort_score,
        "team_average": round(team_avg, 2),
        "credits": round(stats.credits_today, 2),
        "new_balance": round(stats.total_balance, 2)
    }

def get_driver_stats_7d(db: Session, driver_id: int):
    """
    Aggregates effort, credits and balance for the last 7 days from FairnessHistory.
    """
    from datetime import timedelta, date
    from sqlalchemy import func
    
    seven_days_ago = date.today() - timedelta(days=7)
    
    stats = db.query(
        func.sum(FairnessHistory.daily_effort).label("total_effort"),
        func.sum(FairnessHistory.credits_earned).label("total_credits")
    ).filter(
        FairnessHistory.driver_id == driver_id,
        FairnessHistory.date >= seven_days_ago
    ).first()
    
    # Balance is the sum of credits (or we can just take the latest snapshot)
    effort = stats.total_effort or 0
    credits = stats.total_credits or 0
    balance = credits # Cumulative credits over 7 days
    
    return {
        "effort_7d": round(effort, 1),
        "credits_7d": round(credits, 1),
        "balance_7d": round(balance, 1)
    }

def calculate_readiness_canonical(driver_balance: float, team_avg_balance: float) -> dict:
    """
    🔒 CANONICAL READINESS ALGORITHM (ALIGNED WITH SCREENSHOT)
    
    Logic inferred from User Requirement (Step 914 & 927):
    - +48 is Ready
    - +89 is Overloaded
    - -170 is Underloaded
    
    This implies an Absolute Threshold system (approx +/- 75).
    Relative Deviation is not used for status to ensure stability.
    """
    
    # Thresholds derived from visual evidence
    OVERLOAD_THRESHOLD = 75.0
    UNDERLOAD_THRESHOLD = -75.0
    
    # Calculate pure deviation for display purposes
    if abs(team_avg_balance) > 0.01:
        deviation = (driver_balance - team_avg_balance) / team_avg_balance
    else:
        deviation = 0.0
    
    if driver_balance > OVERLOAD_THRESHOLD:
        return {"status": "Overloaded", "deviation": deviation}
    elif driver_balance < UNDERLOAD_THRESHOLD:
        return {"status": "Underloaded", "deviation": deviation}
    else:
        return {"status": "Ready", "deviation": deviation}
