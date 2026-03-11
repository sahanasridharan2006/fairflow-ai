
from database import SessionLocal
from models import User
import logic

def verify():
    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == 'driver').all()
        print(f"Checking Logic Output for {len(drivers)} drivers:")
        for d in drivers:
            stats = logic.get_driver_stats_7d(db, d.id)
            print(f"  - {d.name}: 7d_Effort={stats['effort_7d']}, 7d_Balance={stats['balance_7d']}")
            
            # Also check Readiness logic if possible (mocking team avg?)
    finally:
        db.close()

if __name__ == "__main__":
    verify()
