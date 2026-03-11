from database import SessionLocal
from models import User, DriverStats, Route, FairnessHistory

# Keep only the first 5 seeded drivers
KEEP_EMAILS = [
    "sarah@fairflow.com",
    "mark@fairflow.com", 
    "anita@fairflow.com",
    "leo@fairflow.com",
    "ravi@fairflow.com"
]

db = SessionLocal()

# Get all drivers
all_drivers = db.query(User).filter(User.role == "driver").all()

print(f"Total drivers before cleanup: {len(all_drivers)}")

# Delete drivers not in the keep list
for driver in all_drivers:
    if driver.email not in KEEP_EMAILS:
        print(f"Deleting: {driver.name} ({driver.email})")
        
        # Delete related records first
        db.query(FairnessHistory).filter(FairnessHistory.driver_id == driver.id).delete()
        db.query(Route).filter(Route.driver_id == driver.id).delete()
        db.query(DriverStats).filter(DriverStats.user_id == driver.id).delete()
        
        # Delete the driver
        db.delete(driver)

db.commit()

# Verify
remaining = db.query(User).filter(User.role == "driver").all()
print(f"\nTotal drivers after cleanup: {len(remaining)}")
print("Remaining drivers:")
for d in remaining:
    print(f"  - {d.name} ({d.email})")

db.close()
print("\nCleanup complete!")
