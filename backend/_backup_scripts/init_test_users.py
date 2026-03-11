"""
Directly create test users in database using the same logic as signup endpoints
"""
from database import SessionLocal
import models
import auth

db = SessionLocal()

print("\n" + "="*60)
print("CREATING TEST USERS DIRECTLY")
print("="*60 + "\n")

# Check if users already exist
existing_driver = db.query(models.User).filter(models.User.email == "ridu@test.com").first()
existing_admin = db.query(models.User).filter(models.User.email == "admin@fairflow.com").first()

if existing_driver or existing_admin:
    print("⚠️  Users already exist! Skipping creation.\n")
    if existing_driver:
        print(f"  ✓ Driver: {existing_driver.name} ({existing_driver.email})")
    if existing_admin:
        print(f"  ✓ Admin: {existing_admin.name} ({existing_admin.email})")
else:
    # Create driver
    driver = models.User(
        name="Ridu",
        email="ridu@test.com",
        hashed_password=auth.get_password_hash("test123"),
        role="driver",
        status="ACTIVE"
    )
    db.add(driver)
    db.flush()  # Get driver.id before commit
    
    # Create driver stats
    driver_stats = models.DriverStats(
        user_id=driver.id,
        effort_today=0.0,
        credits_today=0.0,
        total_balance=0.0
    )
    db.add(driver_stats)
    
    # Create admin
    admin = models.User(
        name="Admin User",
        email="admin@fairflow.com",
        hashed_password=auth.get_password_hash("admin123"),
        role="admin",
        status="ACTIVE"
    )
    db.add(admin)
    
    db.commit()
    
    print("✅ Created Driver:")
    print(f"   Name: {driver.name}")
    print(f"   Email: {driver.email}")
    print(f"   Password: test123")
    print(f"   ID: {driver.id}\n")
    
    print("✅ Created Admin:")
    print(f"   Name: {admin.name}")
    print(f"   Email: {admin.email}")
    print(f"   Password: admin123")
    print(f"   ID: {admin.id}\n")

# Show all users
all_users = db.query(models.User).all()
print(f"{'='*60}")
print(f"TOTAL USERS IN DATABASE: {len(all_users)}")
print(f"{'='*60}\n")

for user in all_users:
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == user.id).first()
    print(f"✓ {user.name} ({user.email})")
    print(f"  Role: {user.role}, Status: {user.status}, ID: {user.id}")
    if stats:
        print(f"  Stats: Balance={stats.total_balance}, Effort={stats.effort_today}")
    print()

print("="*60 + "\n")
db.close()
