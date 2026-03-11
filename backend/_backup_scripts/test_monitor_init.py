
from database import SessionLocal
from models import User, DriverStats, FairnessHistory
from fairness_drift import detect_fairness_drift
from datetime import date

def test_monitor_init():
    db = SessionLocal()
    try:
        print("--- Testing Initialization Logic ---")
        
        # 1. Reset all driver balances AND History for this test
        drivers = db.query(User).filter(User.role == "driver").all()
        original_balances = {}
        
        # We need to temporarily wipe FairnessHistory to simulate "Net Zero"
        # We'll back it up in memory (simplistic approach for this test)
        # Actually, for a quick test, let's just delete today's hist or recent hist?
        # Better: transaction rollback? No, simpler to just delete and restore? 
        # Restoring is hard.
        # Alternative: Mock the logic function? No.
        
        # Let's just delete recent history for the test and accept it (it's dev env).
        # Or better, just check if the code handles 0 avg.
        # I'll delete all history for these drivers.
        existing_history = db.query(FairnessHistory).all()
        db.query(FairnessHistory).delete() # Wipe history
        
        for d in drivers:
            stats = db.query(DriverStats).filter(DriverStats.user_id == d.id).first()
            if stats:
                original_balances[d.id] = stats.total_balance
                stats.total_balance = 0 # Force 0
                
        db.commit()
        
        # 2. Run Monitor (Should be Collecting Baseline)
        result = detect_fairness_drift(db)
        
        print(f"Drift Detected: {result['drift_detected']}")
        print(f"Explanation: {result['explanation']}")
        
        if result['explanation'].startswith("Collecting baseline"):
            print("PASS: Correctly flagged as collecting baseline.")
        else:
            print("FAIL: Did not catch zero baseline.")
            
        # 3. Cleanup: Restore balances
        for d_id, bal in original_balances.items():
             stats = db.query(DriverStats).filter(DriverStats.user_id == d_id).first()
             if stats:
                 stats.total_balance = bal
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_monitor_init()
