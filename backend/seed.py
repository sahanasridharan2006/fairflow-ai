
from database import SessionLocal, engine
from models import Base, User, DriverStats, FairnessHistory, Route
from auth import get_password_hash
from datetime import date, timedelta
import random

def seed_database():
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🔄 Database reset complete")
        print("📝 Creating admin user...")
        
        # Create admin
        admin = User(
            name="Admin",
            email="admin@fairflow.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            status="ACTIVE"
        )
        db.add(admin)
        
        print("📝 Creating drivers with STEP 914 SCREENSHOT stats...")
        
        # VALUES FROM STEP 914 SCREENSHOT
        # Sarah: 525 / +143 / MEDIUM
        # Marcus: 490 / +89 / EASY
        # Elena: 580 / +192 / EASY
        # David: 350 / +48 / EASY
        # Priya: 605 / +261 / HARD
        # James: 585 / +276 / HARD
        # Aisha: 130 / -171 / EASY
        # Carlos: 130 / -170 / EASY
        
        drivers_data = [
            {"name": "Sarah Chen", "effort": 525, "balance": 143, "diff": "Medium", "addr": "Flat 302, Lotus Heights, OMR"},
            {"name": "Marcus Johnson", "effort": 490, "balance": 89, "diff": "Easy", "addr": "Door No. 12, 3rd Cross Street"},
            {"name": "Elena Rodriguez", "effort": 580, "balance": 192, "diff": "Easy", "addr": "Door No. 8/112, Gandhi Street"},
            {"name": "David Park", "effort": 350, "balance": 48, "diff": "Easy", "addr": "Flat 504, Block C, Prestige Sunrise"},
            {"name": "Priya Sharma", "effort": 605, "balance": 261, "diff": "Hard", "addr": "Warehouse Unit 5, Peenya"},
            {"name": "James Williams", "effort": 585, "balance": 276, "diff": "Hard", "addr": "Shop No. 12, Koyambedu Market"},
            {"name": "Aisha Mohammed", "effort": 130, "balance": -171, "diff": "Easy", "addr": "Flat 101, Sai Nagar Main Road"},
            {"name": "Carlos Santos", "effort": 130, "balance": -170, "diff": "Easy", "addr": "H.No. 45, 2nd Main Road"}
        ]
        
        today = date.today()
        
        for i, d_data in enumerate(drivers_data):
            driver = User(
                name=d_data["name"],
                email=f"driver{i+1}@fairflow.com",
                hashed_password=get_password_hash("password123"),
                role="driver",
                status="ACTIVE"
            )
            db.add(driver)
            db.flush() # get ID
            
            # 1. Driver Stats
            stats = DriverStats(
                user_id=driver.id,
                total_balance=d_data["balance"],
                effort_today=30, 
                credits_today=0 
            )
            db.add(stats)
            
            # 2. Fairness History (To drive 7-day display)
            history = FairnessHistory(
                driver_id=driver.id,
                date=today - timedelta(days=1),
                daily_effort=d_data["effort"], 
                credits_earned=d_data["balance"],
                team_average=500.0,
                balance_snapshot=d_data["balance"]
            )
            db.add(history)
            
            # 3. Assigned Route (Manually created)
            assigned_route = Route(
                driver_id=driver.id,
                address=d_data["addr"],
                difficulty=d_data["diff"],
                date=today,
                stops=10,
                apartments=0,
                stairs=False,
                heavy_boxes=0,
                traffic_level="Normal",
                weather_condition="Clear",
                calculated_effort_score=30.0,
                status="Assigned"
            )
            db.add(assigned_route)
            
        db.commit()
        print(f"✅ Created {len(drivers_data)} drivers matching Step 914 screenshot.")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
