from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, logic, routes_data
from database import get_db, engine
models.Base.metadata.create_all(bind=engine)
from datetime import timedelta, date
import statistics

app = FastAPI(title="FairFlow API")

# Setup CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to FairFlow API"}

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
        expires_delta=access_token_expires
    )
    
    # Return token with driver details for frontend localStorage
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "driver_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

# Driver Endpoints
@app.get("/driver/dashboard", response_model=schemas.DriverDashboard)
def get_driver_dashboard(user_email: str, db: Session = Depends(get_db)):
    # In real app, extract user from token. For prototype simple param is fine but better to use dependency.
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user or user.role != "driver":
        raise HTTPException(status_code=404, detail="Driver not found")
        
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == user.id).first()
    route = db.query(models.Route).filter(models.Route.driver_id == user.id, models.Route.date == logic.date.today()).first()
    
    # Calculate Team Average 7-Day and Deviation for Driver
    stats_7d = logic.get_driver_stats_7d(db, user.id)
    
    # Need team average 7d - simplified fetch
    # (In prod, cache this or making it efficient)
    drivers = db.query(models.User).filter(models.User.role == "driver", models.User.status != "ABSENT").all()
    total_effort = 0
    count = 0
    for d in drivers:
        s = logic.get_driver_stats_7d(db, d.id)
        total_effort += s['effort_7d']
        count += 1
    team_avg_7d = total_effort / count if count > 0 else 0
    
    if team_avg_7d > 0:
        deviation = ((stats_7d['effort_7d'] - team_avg_7d) / team_avg_7d) * 100
    else:
        deviation = 0
        
    readiness = logic.get_readiness_from_deviation(deviation)
    
    message = "Route assigned based on fairness balance."
    if user.status == "SICK":
         message = "Sick Mode: Protected from hard routes. No credit penalty."
    elif readiness == "Underloaded":
        message = "You have a lighter route today to recover your balance."
    elif readiness == "Overloaded":
        message = "You have a heavier route today to use your credits."

    return {
        "stats": stats,
        "route": route,
        "team_average": round(team_avg_7d, 1),
        "message": message,
        "status": user.status,
        "readiness_status": readiness
    }

@app.get("/driver/history", response_model=List[schemas.FairnessHistoryDisplay])
def get_driver_history(user_email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Query fairness_history (actual data) instead of fairness_snapshots
    history_records = db.query(models.FairnessHistory).filter(
        models.FairnessHistory.driver_id == user.id
    ).order_by(models.FairnessHistory.date.desc()).limit(7).all()
    
    # Convert history records to history display format
    history_display = []
    for record in history_records:
        history_display.append({
            "date": record.date,
            "daily_effort": record.daily_effort,
            "team_average": record.team_average,
            "credits_earned": record.credits_earned,
            "balance_snapshot": record.balance_snapshot
        })
    
    return history_display


@app.post("/driver/feedback")
def submit_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    route = db.query(models.Route).filter(models.Route.id == feedback.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route.feedback_score = feedback.difficulty
    route.feedback_comment = feedback.comment
    route.status = "Completed"
    
    # Trigger logic update (Mock: update effort for today? Or just store feedback)
    # For MVP just store it.
    db.commit()
    return {"status": "success"}

# Admin Endpoints
@app.get("/admin/dashboard", response_model=List[schemas.AdminDriverView])
def get_admin_dashboard(db: Session = Depends(get_db)):
    drivers = db.query(models.User).filter(models.User.role == "driver").all()
    
    # 1. Gather all 7-Day Balances to compute Team Baseline
    driver_stats_map = {}
    total_balance = 0
    valid_count = 0
    
    for driver in drivers:
         s7 = logic.get_driver_stats_7d(db, driver.id)
         driver_stats_map[driver.id] = s7
         # Include all Active/Sick drivers in baseline? Prompt says "mean of all drivers' 7-day balance"
         if driver.status != 'ABSENT':
             total_balance += s7['balance_7d']
             valid_count += 1
             
    team_avg_balance = total_balance / valid_count if valid_count > 0 else 0
    
    dashboard_data = []
    
    for driver in drivers:
        stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver.id).first()        
        route = db.query(models.Route).filter(
            models.Route.driver_id == driver.id,
            models.Route.date == date.today()
        ).first()
        
        stats_7d = driver_stats_map.get(driver.id, {"effort_7d": 0, "credits_7d": 0, "balance_7d": 0})
        
        # 🔒 CANONICAL READINESS CHECK
        readiness_data = logic.calculate_readiness_canonical(
            stats_7d['balance_7d'], 
            team_avg_balance
        )
        
        readiness = readiness_data['status']
        deviation = readiness_data['deviation']
        
        if readiness == "Overloaded":
            alert_msg = "Overloaded"
            reason = f"Balance is {int(deviation * 100)}% above team average"
        elif readiness == "Underloaded":
             alert_msg = "Underloaded" 
             reason = f"Balance is {abs(int(deviation * 100))}% below team average"
        else:
            alert_msg = None
            reason = None
            
        # Overrides for status
        if driver.status == 'ABSENT':
            readiness = "Absent"
            alert_msg = "Absent"
        elif driver.status == 'SICK':
            readiness = "Protected"
            alert_msg = "Protected"

        dashboard_data.append({
            "id": driver.id,
            "name": driver.name,
            "email": driver.email,
            "status": driver.status,
            "stats": stats,
            "current_route_difficulty": route.difficulty if route else "Unassigned",
            "current_route_address": route.address if route else None,
            "alert": alert_msg,
            "alert_reason": reason,
            "effort_7d": stats_7d["effort_7d"],
            "credits_7d": stats_7d["credits_7d"],
            "balance_7d": stats_7d["balance_7d"],
            "readiness_status": readiness
        })
    
    return dashboard_data

@app.get("/admin/routes")
def get_admin_routes():
    """
    Returns pre-classified mock routes for simulation.
    """
    return routes_data.get_all_routes()

@app.get("/driver/{driver_id}/dashboard")
def get_driver_dashboard_by_id(driver_id: int, db: Session = Depends(get_db)):
    """
    Fetch dashboard data for a specific driver by ID (FIX ISSUE #1)
    """
    driver = db.query(models.User).filter(models.User.id == driver_id).first()
    if not driver or driver.role != "driver":
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Use same logic as email-based endpoint
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver.id).first()
    route_today = db.query(models.Route).filter(
        models.Route.driver_id == driver.id,
        models.Route.date == date.today()
    ).first()
    
    team_avg = logic.calculate_team_average(db)
    
    return {
        "name": driver.name,
        "status": driver.status,
        "stats": stats,
        "route": route_today,
        "team_average": team_avg,
        "message": f"Today's workload: {route_today.difficulty if route_today else 'No route assigned'}"
    }

@app.post("/admin/assign_route")
def admin_assign_route(request: schemas.AssignRouteRequest, db: Session = Depends(get_db)):
    """
    Real-time route assignment with AI fairness intervention
    """
    import fairness_drift
    
    # === AI INTERVENTION CHECK ===
    # Determine route difficulty for intervention logic
    effort_score = logic.calculate_effort_score(request.route_factors.dict())
    route_difficulty = "Easy" if effort_score < 60 else ("Hard" if effort_score > 80 else "Medium")
    
    should_block, intervention_msg = fairness_drift.should_intervene_for_driver(
        db, request.driver_id, route_difficulty
    )
    
    if should_block:
        raise HTTPException(status_code=400, detail=intervention_msg)
    
    # === PROCEED WITH ASSIGNMENT ===
    try:
        result = logic.assign_route_to_driver(
            driver_id=request.driver_id,
            route_factors=request.route_factors.dict(),
            db=db,
            difficulty=request.difficulty,
            address=request.address
        )
        
        # === CAPTURE SNAPSHOT AFTER ASSIGNMENT ===
        fairness_drift.capture_daily_snapshot(db, request.driver_id)
        
        # === CHECK DRIFT STATUS FOR RESPONSE ===
        drift_status = fairness_drift.detect_fairness_drift(db)
        
        # Add AI status to response
        result["ai_intervention"] = should_block
        result["drift_severity"] = drift_status["severity"]
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/auto_assign")
def auto_assign_route(request: schemas.BatchRecommendationRequest, db: Session = Depends(get_db)):
    """
    Auto-assign the selected route using ML recommendations.
    Picks the #1 ranked/approved driver and performs assignment.
    """
    from ml_recommendation import RouteDifficultyRecommender
    from fairness_validator import FairnessValidator
    from fairness_validator import FairnessValidator
    from fairness_drift import get_effort_distribution, detect_fairness_drift
    from working_hours import get_working_hours
    import logic
    import models
    import statistics
    from datetime import date, timedelta
    
    try:
        recommender = RouteDifficultyRecommender()
        validator = FairnessValidator()
    
        # 1. Get rankings (Re-using logic from recommend_routes_batch)
        # Calculate Team Average Balance (7-Day)
        drivers_all = db.query(models.User).filter(models.User.role == "driver").all()
        total_balance = 0
        valid_count = 0
        for d in drivers_all:
            s7 = logic.get_driver_stats_7d(db, d.id)
            if s7 is None:
                s7 = {'balance_7d': 0.0, 'effort_7d': 0.0, 'credits_7d': 0.0}
            if d.status != 'ABSENT':
                total_balance += s7['balance_7d']
                valid_count += 1
        team_avg_balance = total_balance / valid_count if valid_count > 0 else 0
        
        effort_dist = get_effort_distribution(db, last_n_days=7) or {}
            
        drift_status = detect_fairness_drift(db)
        if drift_status is None:
             drift_status = {'severity': 'NONE', 'affected_drivers': []}
        route_features = request.route_features
        
        # Check if we have route features
        if not route_features or 'address' not in route_features:
            raise HTTPException(status_code=400, detail="No route selected or missing address")
            
        # Check if this route is already assigned today as a safeguard
        existing_route = db.query(models.Route).filter(
            models.Route.address == route_features["address"],
            models.Route.date == date.today()
        ).first()
        if existing_route:
            # Get the driver name
            assigned_driver = db.query(models.User).filter(models.User.id == existing_route.driver_id).first()
            driver_name = assigned_driver.name if assigned_driver else "another driver"
            raise HTTPException(status_code=400, detail=f"This route is already assigned to {driver_name} today.")
    
        obj_score = recommender._calculate_route_score(route_features)
        if obj_score < 45:
            route_difficulty = "Easy"
        elif obj_score <= 65:
            route_difficulty = "Medium"
        else:
            route_difficulty = "Hard"
        
        drivers = db.query(models.User).filter(models.User.role == "driver", models.User.status == "ACTIVE").all()
        all_results = []
        
        for driver in drivers:
            driver_id = driver.id
            driver_normalized_effort = effort_dist.get(driver_id, 7.5)
            stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
            fairness_balance = stats.total_balance if stats else 0.0
            
            # Count consecutive hard
            cutoff = date.today() - timedelta(days=7)
            hard_routes = db.query(models.Route).filter(
                models.Route.driver_id == driver_id,
                models.Route.date >= cutoff,
                models.Route.difficulty == 'Hard'
            ).order_by(models.Route.date.desc()).limit(5).all()
            
            consecutive_hard = len(hard_routes)
            working_hours_today = get_working_hours(driver.status)
            
            # Calculate Balance Deviation & State from Canonical Logic
            stats_7d = logic.get_driver_stats_7d(db, driver_id)
            if stats_7d is None:
                stats_7d = {'balance_7d': 0.0}
            
            readiness_data = logic.calculate_readiness_canonical(
                stats_7d['balance_7d'], 
                team_avg_balance
            )
            
            driver_state = readiness_data['status'] # "Ready", "Overloaded", or "Underloaded"
            deviation = readiness_data['deviation']
    
            driver_context = {
                'normalized_effort_last_3_days': driver_normalized_effort,
                'normalized_effort_deviation': deviation,
                'driver_state': driver_state,
                'fairness_balance': fairness_balance,
                'consecutive_hard_routes': consecutive_hard,
                'working_hours_today': working_hours_today,
                'drift_severity': drift_status.get('severity', 'NONE')
            }
            
            ml_result = recommender.recommend(route_features, driver_context, route_difficulty=route_difficulty)
            fairflow_result = validator.validate_recommendation(ml_result, driver_id, db)
            
            all_results.append({
                'driver_id': driver_id,
                'driver_name': driver.name,
                'ml_recommendation': ml_result,
                'fairflow_decision': fairflow_result,
                'driver_context': driver_context
            })
        
        # 2. Rank drivers
        ranked_results = validator.rank_drivers(all_results, route_difficulty=route_difficulty)
        
        # 3. Filter for drivers who are NOT yet assigned for today
        assigned_driver_ids = {r.driver_id for r in db.query(models.Route).filter(models.Route.date == date.today()).all()}
        
        # Sort by rank (1 at top)
        best_options = [r for r in ranked_results if r['preference_rank'] is not None and r['driver_id'] not in assigned_driver_ids]
        best_options.sort(key=lambda x: x['preference_rank'])
    
        if not best_options:
            raise HTTPException(status_code=400, detail="All eligible drivers already have assignments for today.")
    
        best_fit = best_options[0]
        
        # 3. Select the best fit (#1 preferred)
        
        # Prepare route factors for logic.py (it expects specific keys)
        route_factors = {
            "apartments": route_features.get("apartments", route_features.get("floors", 0)),
            "stairs": route_features.get("stairs", route_features.get("stairs_present", False)),
            "heavy_boxes": route_features.get("heavy_boxes", route_features.get("heavy_packages_count", 0)),
            "traffic": route_features.get("traffic_level") == "High",
            "rain": route_features.get("weather_severity") == "Rain"
        }
    
        # 4. Perform assignment
        result = logic.assign_route_to_driver(
            driver_id=best_fit["driver_id"],
            route_factors=route_factors,
            db=db,
            difficulty=route_difficulty,
            address=route_features["address"]
        )
        result["driver_assigned"] = best_fit["driver_name"]
        result["reason"] = f"Auto-selected by AI as Best Fit (#{best_fit['preference_rank']})"
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/fairness_drift")
def get_fairness_drift_status(db: Session = Depends(get_db)):
    """
    AI-Powered Fairness Drift Detection
    Returns current drift status, affected drivers, and metrics
    """
    import fairness_drift
    
    result = fairness_drift.detect_fairness_drift(db)
    return result

@app.post("/admin/toggle_status")
def toggle_driver_status(driver_id: int, status: str, db: Session = Depends(get_db)):
    # Simple endpoint to toggle status for testing
    if status not in ["ACTIVE", "SICK", "ABSENT"]:
         raise HTTPException(status_code=400, detail="Invalid status")
         
    driver = db.query(models.User).filter(models.User.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    driver.status = status
    db.commit()
    return {"message": f"Driver {driver.name} status updated to {status}"}


@app.post("/admin/unassign_route")
def unassign_route(driver_id: int, db: Session = Depends(get_db)):
    """Remove today's route assignment for a driver"""
    from datetime import date
    today = date.today()
    
    route = db.query(models.Route).filter(
        models.Route.driver_id == driver_id,
        models.Route.date == today
    ).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="No active route assignment found for today")
    
    try:
        # 1. Delete the route
        db.delete(route)
        
        # 2. Revert Fairness History & Balance
        history = db.query(models.FairnessHistory).filter(
            models.FairnessHistory.driver_id == driver_id,
            models.FairnessHistory.date == today
        ).first()
        
        stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
        
        if history and stats:
            # Revert the balance impact
            stats.total_balance -= history.credits_earned
            # Delete the history record
            db.delete(history)
            
        # 3. Reset daily stats
        if stats:
            stats.effort_today = 0
            stats.credits_today = 0
            
        db.commit()
        return {"message": "Route unassigned and fairness ledger reverted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))





@app.post("/admin/recommend_route")
def get_ml_route_recommendation(
    request: schemas.MLRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    3-Layer ML Decision Support System for Route Assignment
    
    Layer 1: ML Recommendation (suggests difficulty)
    Layer 2: FairFlow Validation (enforces working-hours fairness, can override)
    Layer 3: Admin Decision (final control - returned for UI)
    
    CRITICAL: ML SUGGESTS ONLY. FairFlow has veto power. Admin has final control.
    """
    from ml_recommendation import RouteDifficultyRecommender
    from fairness_validator import FairnessValidator
    from fairness_drift import get_effort_distribution
    import statistics
    
    # Get driver context for ML
    driver_id = request.driver_id
    route_features = request.route_features
    
    driver = db.query(models.User).filter(models.User.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Get normalized effort (per working hour) for last 7 days
    effort_dist = get_effort_distribution(db, last_n_days=7)
    driver_normalized_effort = effort_dist.get(driver_id, 7.5)
    
    # Get fairness balance
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
    fairness_balance = stats.total_balance if stats else 0.0
    
    # Count consecutive hard routes
    from datetime import date, timedelta
    cutoff = date.today() - timedelta(days=7)
    hard_routes = db.query(models.Route).filter(
        models.Route.driver_id == driver_id,
        models.Route.date >= cutoff,
        models.Route.difficulty == 'Hard'
    ).order_by(models.Route.date.desc()).limit(5).all()
    
    consecutive_hard = 0
    for route in hard_routes:
        if route.difficulty == 'Hard':
            consecutive_hard += 1
        else:
            break
    
    # Get drift severity
    import fairness_drift as fd
    drift_status = fd.detect_fairness_drift(db)
    drift_severity = drift_status['severity']
    
    # Get working hours
    from working_hours import get_working_hours
    working_hours_today = get_working_hours(driver.status)
    
    # Build driver context
    # Calculate Team Average and Deviation
    # Calculate Team Average Balance (7-Day)
    drivers_all = db.query(models.User).filter(models.User.role == "driver").all()
    total_balance = 0
    valid_count = 0
    for d in drivers_all:
         s = logic.get_driver_stats_7d(db, d.id)
         if d.status != 'ABSENT':
             total_balance += s['balance_7d']
             valid_count += 1
    team_avg_balance = total_balance / valid_count if valid_count > 0 else 0

    stats_7d = logic.get_driver_stats_7d(db, driver_id)
    driver_balance = stats_7d['balance_7d']
    denominator = abs(team_avg_balance)
    
    if denominator > 0.1:
        deviation = ((driver_balance - team_avg_balance) / denominator) * 100
    else:
        if abs(driver_balance) < 0.1: deviation = 0
        else: deviation = 100 if driver_balance > 0 else -100
    
    if effort_dist:
        team_avg = statistics.mean(effort_dist.values())
    else:
        team_avg = 7.5

    # STRICT STATE DEFINITION
    # STRICT STATE DEFINITION
    driver_state = logic.get_readiness_from_deviation(deviation)
    
    # Build driver context
    driver_context = {
        'normalized_effort_last_3_days': driver_normalized_effort,
        'normalized_effort_deviation': deviation,
        'driver_state': driver_state,
        'fairness_balance': fairness_balance,
        'consecutive_hard_routes': consecutive_hard,
        'working_hours_today': working_hours_today,
        'drift_severity': drift_severity
    }
    
    # LAYER 1: ML Recommendation (SUGGESTION ONLY)
    ml_recommender = RouteDifficultyRecommender()
    ml_result = ml_recommender.recommend(route_features, driver_context)
    
    # LAYER 2: FairFlow Validation (CAN OVERRIDE ML)
    validator = FairnessValidator()
    fairflow_decision = validator.validate_recommendation(ml_result, driver_id, db)
    
    # LAYER 3: Return for Admin UI (FINAL HUMAN CONTROL)
    return {
        'ml_recommendation': {
            'suggested_difficulty': ml_result['recommended_difficulty'],
            'confidence': ml_result['confidence'],
            'reason': ml_result['reason'],
            'route_score': ml_result['route_score'],
            'driver_fatigue_factor': ml_result['driver_fatigue_factor']
        },
        'fairflow_decision': {
            'approved_difficulty': fairflow_decision['approved_difficulty'],
            'approved_levels': fairflow_decision.get('approved_levels', ['Easy', 'Medium', 'Hard']),
            'blocked_levels': fairflow_decision.get('blocked_levels', []),
            'action': fairflow_decision['action'],
            'reason': fairflow_decision['reason'],
            'fairness_override': fairflow_decision['fairness_override'],
            'override_reason': fairflow_decision['override_reason']
        },
        'driver_context': {
            'name': driver.name,
            'status': driver.status,
            'normalized_effort_per_hour': round(driver_normalized_effort, 2),
            'fairness_balance': round(fairness_balance, 1),
            'working_hours_today': working_hours_today
        },
        'final_note': 'Admin has final control. This is decision support, not automatic assignment.'
    }


@app.post("/admin/recommend_routes_batch")
def get_ml_route_recommendations_batch(
    request: schemas.BatchRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    3-Layer Batch Recommendation System
    Returns ranked suitabilities for all active drivers for a single route.
    """
    from ml_recommendation import RouteDifficultyRecommender
    from ml_recommendation import RouteDifficultyRecommender
    from fairness_validator import FairnessValidator
    from fairness_drift import get_effort_distribution, detect_fairness_drift
    from working_hours import get_working_hours
    from datetime import date, timedelta
    import statistics
    
    try:
        import traceback
        recommender = RouteDifficultyRecommender()
        validator = FairnessValidator()
        
        # 1. Setup global context
        drivers = db.query(models.User).filter(models.User.role == "driver").all()
        effort_dist = get_effort_distribution(db, last_n_days=7)
        drift_status = detect_fairness_drift(db)
        route_features = request.route_features
        
        # 2. Determine objective route difficulty
        obj_score = recommender._calculate_route_score(route_features)
        if obj_score < 45:
            route_difficulty = "Easy"
        elif obj_score <= 65:
            route_difficulty = "Medium"
        else:
            route_difficulty = "Hard"
        
        all_results = []
        
        # Pre-calculate team average for deviation
        if effort_dist:
            team_avg_effort = statistics.mean(effort_dist.values())
        else:
            team_avg_effort = 7.5 # Fallback
            
        # Calculate Team Average Balance (7-Day)
        total_balance = 0
        valid_count = 0
        driver_params = {} # Cache stats
        for d in drivers:
            s7 = logic.get_driver_stats_7d(db, d.id)
            driver_params[d.id] = s7
            if d.status != 'ABSENT':
                total_balance += s7['balance_7d']
                valid_count += 1
        team_avg_balance = total_balance / valid_count if valid_count > 0 else 0
            
        for driver in drivers:
            # Get driver context
            driver_id = driver.id
            driver_normalized_effort = effort_dist.get(driver_id, 7.5)
            stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
            fairness_balance = stats.total_balance if stats else 0.0
            
            # 🔒 CANONICAL READINESS CHECK
            stats_7d = logic.get_driver_stats_7d(db, driver_id)
            if stats_7d is None:
                stats_7d = {'balance_7d': 0.0}
            
            readiness_data = logic.calculate_readiness_canonical(
                stats_7d['balance_7d'], 
                team_avg_balance
            )
            
            driver_state = readiness_data['status'] # "Ready", "Overloaded", or "Underloaded"
            deviation = readiness_data['deviation']

            # Count consecutive hard
            cutoff = date.today() - timedelta(days=7)
            hard_routes = db.query(models.Route).filter(
                models.Route.driver_id == driver_id,
                models.Route.date >= cutoff,
                models.Route.difficulty == 'Hard'
            ).order_by(models.Route.date.desc()).limit(5).all()
            
            consecutive_hard = 0
            for r in hard_routes:
                if r.difficulty == 'Hard':
                    consecutive_hard += 1
                else:
                    break
            
            working_hours_today = get_working_hours(driver.status)
            
            driver_context = {
                'normalized_effort_last_3_days': driver_normalized_effort,
                'normalized_effort_deviation': deviation,
                'driver_state': driver_state, # CRITICAL INJECTION
                'fairness_balance': fairness_balance,
                'consecutive_hard_routes': consecutive_hard,
                'working_hours_today': working_hours_today,
                'drift_severity': drift_status['severity']
            }
            
            # LAYER 1: ML Suggestion (score-based)
            ml_result = recommender.recommend(route_features, driver_context, route_difficulty=route_difficulty)
            
            # LAYER 2: FairFlow Validation (Authority)
            fairflow_result = validator.validate_recommendation(ml_result, driver_id, db)
            
            all_results.append({
                'driver_id': driver_id,
                'driver_name': driver.name,
                'ml_recommendation': ml_result,
                'fairflow_decision': fairflow_result,
                'driver_context': {
                    'name': driver.name,
                    'status': driver.status,
                    'normalized_effort_per_hour': round(driver_normalized_effort, 2),
                    'driver_state': driver_state,
                    'fairness_balance': round(fairness_balance, 1),
                    'working_hours_today': working_hours_today
                }
            })
        
        # LAYER 3: Preference Ranking (Global Priority)
        ranked_results = validator.rank_drivers(all_results, route_difficulty=route_difficulty)
        
        return ranked_results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signup/driver")
def signup_driver(signup: schemas.DriverSignupRequest, db: Session = Depends(get_db)):
    """Create a new driver account"""
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == signup.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create driver
    driver = models.User(
        name=signup.name,
        email=signup.email,
        hashed_password=auth.get_password_hash(signup.password),  # Use user's password
        role="driver",
        status="ACTIVE"
    )
    db.add(driver)
    db.flush()
    
    # Initialize stats
    stats = models.DriverStats(
        user_id=driver.id,
        total_balance=0,
        effort_today=0,
        credits_today=0
    )
    db.add(stats)
    db.commit()
    
    return {"status": "success", "driver_id": driver.id, "email": driver.email}

@app.post("/signup/admin")
def signup_admin(signup: schemas.DriverSignupRequest, db: Session = Depends(get_db)):
    """Create a new admin account"""
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == signup.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create admin
    admin = models.User(
        name=signup.name,
        email=signup.email,
        hashed_password=auth.get_password_hash(signup.password),
        role="admin",
        status="ACTIVE"
    )
    db.add(admin)
    db.commit()
    
    return {"status": "success", "admin_id": admin.id, "email": admin.email}
