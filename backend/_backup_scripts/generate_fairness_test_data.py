"""
Generate realistic test data for AI Fairness Drift Detection
Creates drivers with historical snapshots to demonstrate drift detection
"""

from database import SessionLocal
from models import User, DriverStats, FairnessSnapshot
from auth import get_password_hash
from datetime import date, timedelta
import random

def generate_fairness_test_data():
    """Create test drivers with realistic snapshot history showing drift"""
    db = SessionLocal()
    
    print("🧪 Generating AI Fairness Drift Test Data...")
    
    # Create 5 test drivers
    drivers_data = [
        {"name": "Alice Chen", "email": "alice@test.com"},
        {"name": "Bob Martinez", "email": "bob@test.com"},
        {"name": "Carol Singh", "email": "carol@test.com"},
        {"name": "David Kim", "email": "david@test.com"},
        {"name": "Emma Wilson", "email": "emma@test.com"},
    ]
    
    created_drivers = []
    
    for idx, d_data in enumerate(drivers_data):
        # Create user with unique password based on email
        driver = User(
            name=d_data["name"],
            email=d_data["email"],
            hashed_password=get_password_hash(f"password{idx+1}"),  # password1, password2, etc.
            role="driver",
            status="ACTIVE"
        )
        db.add(driver)
        db.flush()
        
        # Create stats
        stats = DriverStats(
            user_id=driver.id,
            total_balance=0.0,
            credits_today=0.0,
            effort_today=0.0
        )
        db.add(stats)
        
        created_drivers.append((driver, stats))
        print(f"✅ Created driver: {driver.name} (ID: {driver.id})")
    
    db.commit()
    
    # Generate 14 days of historical snapshots
    print("\n📊 Generating 14 days of historical snapshots...")
    
    today = date.today()
    
    # Days 1-10: Balanced workload (baseline)
    for day_offset in range(14, 4, -1):
        snapshot_date = today - timedelta(days=day_offset)
        
        for driver, stats in created_drivers:
            # Balanced effort: 80-120 (avg ~100)
            effort = random.uniform(80, 120)
            credits = random.uniform(-30, 30)
            balance = random.uniform(-20, 20)
            
            snapshot = FairnessSnapshot(
                driver_id=driver.id,
                date=snapshot_date,
                effort=effort,
                credits=credits,
                balance=balance
            )
            db.add(snapshot)
    
    print(f"  ✅ Days 14-5 ago: Balanced baseline (avg effort ~100)")
    
    # Days 4-1: Introduce drift (Alice overloaded, David underloaded)
    for day_offset in range(4, 0, -1):
        snapshot_date = today - timedelta(days=day_offset)
        
        for driver, stats in created_drivers:
            if driver.name == "Alice Chen":
                # Overloaded: High effort
                effort = random.uniform(140, 180)
                credits = random.uniform(-80, -50)
                balance = random.uniform(-150, -100)
            elif driver.name == "David Kim":
                # Underloaded: Low effort
                effort = random.uniform(30, 60)
                credits = random.uniform(50, 80)
                balance = random.uniform(100, 150)
            else:
                # Others: Normal range
                effort = random.uniform(85, 115)
                credits = random.uniform(-35, 35)
                balance = random.uniform(-25, 25)
            
            snapshot = FairnessSnapshot(
                driver_id=driver.id,
                date=snapshot_date,
                effort=effort,
                credits=credits,
                balance=balance
            )
            db.add(snapshot)
            
            # Update current stats to match today's values
            if day_offset == 1:
                stats.effort_today = effort
                stats.credits_today = credits
                stats.total_balance = balance
    
    print(f"  ⚠️ Days 4-1 ago: DRIFT INTRODUCED")
    print(f"     - Alice Chen: Overloaded (effort 140-180)")
    print(f"     - David Kim: Underloaded (effort 30-60)")
    print(f"     - Others: Normal (effort 85-115)")
    
    db.commit()
    
    # Calculate expected drift metrics
    print("\n📈 Expected Drift Detection Results:")
    
    # Baseline variance (days 14-5): effort ~80-120, should be low
    print(f"  - Baseline variance (days 14-5): Low (~12-15)")
    
    # Current variance (days 4-1): Alice 140-180, David 30-60, others 85-115
    print(f"  - Current variance (days 4-1): High (~40-50)")
    
    # Expected change
    print(f"  - Expected variance change: >150% (HIGH severity)")
    print(f"  - Affected drivers: Alice (overloaded), David (underloaded)")
    
    print("\n✅ Test data generation complete!")
    print(f"\n🔍 Test the API:")
    print(f"   curl http://localhost:8000/admin/fairness_drift")
    print(f"\n🌐 Or visit Admin Dashboard:")
    print(f"   http://localhost:5173")
    print(f"   Login: admin@fairflow.com / admin123")
    
    db.close()

if __name__ == "__main__":
    generate_fairness_test_data()
