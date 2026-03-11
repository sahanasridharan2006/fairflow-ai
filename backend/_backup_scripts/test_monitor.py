
from database import SessionLocal
from models import User, DriverStats, FairnessHistory
from fairness_drift import detect_fairness_drift
from logic import update_fairness_ledger
from datetime import date

def test_monitor():
    db = SessionLocal()
    try:
        # 1. Setup Data: Create one Overloaded Driver
        # We'll just pick the first driver and force their stats
        driver = db.query(User).filter(User.role == "driver").first()
        if not driver:
            print("No drivers found")
            return

        # Force high balance stats
        stats = db.query(DriverStats).filter(DriverStats.user_id == driver.id).first()
        original_balance = stats.total_balance
        
        # Set to +200 (Overloaded > 75)
        stats.total_balance = 200
        
        # Also ensure history reflects this so get_driver_stats_7d picks it up
        # We'll just create a history entry for today with +200 credits
        today = date.today()
        history = db.query(FairnessHistory).filter(
            FairnessHistory.driver_id == driver.id, 
            FairnessHistory.date == today
        ).first()
        
        if history:
            original_history_bal = history.credits_earned
            history.credits_earned = 200
            history.balance_snapshot = 200
        
        db.commit()
        
        print(f"Testing with Driver {driver.name} Balance = 200 (Overloaded)...")
        
        # 2. Run Monitor
        result = detect_fairness_drift(db)
        
        print(f"Drift Detected: {result['drift_detected']}")
        print(f"Severity: {result['severity']}")
        print(f"Affected: {[d['name'] + ': ' + d['status'] for d in result['affected_drivers']]}")
        
        # 3. Cleanup (Try to restore)
        stats.total_balance = original_balance
        if history:
            history.credits_earned = original_history_bal
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_monitor()
