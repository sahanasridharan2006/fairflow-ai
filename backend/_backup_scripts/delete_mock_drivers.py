from database import SessionLocal
from models import User, DriverStats, Route, FairnessHistory

# Simple ORM deletion - let SQLAlchemy handle cascades
MOCK_EMAILS = [
    "sarah@fairflow.com",
    "mark@fairflow.com", 
    "anita@fairflow.com",
    "leo@fairflow.com",
    "ravi@fairflow.com"
]

db = SessionLocal()

try:
    print("Deleting mock/seeded drivers...")
    
    # Get count before  
    count_before = db.query(User).filter(User.role == 'driver').count()
    print(f"Total drivers before cleanup: {count_before}")
    
    for email in MOCK_EMAILS:
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            print(f"\nDeleting: {user.name} ({email}) [ID: {user.id}]")
            
            # Manually delete related records in correct order
            # 1. Fairness history first
            fairness_deleted = db.query(FairnessHistory).filter(FairnessHistory.driver_id == user.id).delete()
            print(f"  - Deleted {fairness_deleted} fairness_history records")
            
            # 2. Routes
            routes_deleted = db.query(Route).filter(Route.driver_id == user.id).delete()
            print(f"  - Deleted {routes_deleted} routes")
            
            # 3. Driver stats
            stats_deleted = db.query(DriverStats).filter(DriverStats.driver_id == user.id).delete()
            print(f"  - Deleted {stats_deleted} driver_stats records")
            
            # 4. Finally delete the user
            db.delete(user)
            db.commit()
            print(f"  - Deleted user ✅")
    
    # Get count after
    count_after = db.query(User).filter(User.role == 'driver').count()
    print(f"\n📊 Total drivers after cleanup: {count_after}")
    print(f"✅ Deleted {count_before - count_after} mock drivers")
    
    print("\n👥 Remaining drivers:")
    remaining = db.query(User).filter(User.role == 'driver').all()
    for driver in remaining:
        print(f"  - [{driver.id}] {driver.name} ({driver.email})")
    
    print("\n✅ Cleanup complete! Only real user-created drivers remain.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
