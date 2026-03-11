
from database import SessionLocal
from models import User, DriverStats, FairnessHistory

def check():
    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == 'driver').all()
        print(f"Found {len(drivers)} drivers:")
        for d in drivers:
            stats = db.query(DriverStats).filter(DriverStats.user_id == d.id).first()
            if stats:
                print(f"  - {d.name}: Effort={stats.effort_today} (Daily), Balance={stats.total_balance}")
            else:
                 print(f"  - {d.name}: NO STATS")
                 
            # Check history
            hist = db.query(FairnessHistory).filter(FairnessHistory.driver_id == d.id).all()
            print(f"    History entries: {len(hist)}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
