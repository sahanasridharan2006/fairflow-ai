import database
import models
from datetime import date, timedelta
import random

def seed_demo_data():
    db = database.SessionLocal()
    
    # 1. Clear existing history and daily stats
    db.query(models.FairnessHistory).delete()
    stats = db.query(models.DriverStats).all()
    for s in stats:
        s.effort_today = 0
        s.credits_today = 0
        s.total_balance = 0
    db.commit()
    print("Cleared existing fairness data.")

    # 2. Define Driver Groups
    # IDs: 2,3,4,5,6,7,8,9 (Total 8)
    # Target: 3 Overloaded, 3 Ready, 2 Underloaded
    
    overloaded_ids = [2, 3, 4] # Sarah, Marcus, Elena
    ready_ids = [5, 6, 7]      # David, Priya, James
    underloaded_ids = [8, 9]   # Aisha, Carlos
    
    today = date.today()
    
    # 3. Insert History for last 7 days
    # Strategy: 
    # Overloaded: Consistently doing Hard routes (+credits)
    # Ready: Doing Medium routes (0 credits)
    # Underloaded: Doing Easy routes (-credits)
    
    for i in range(7):
        day = today - timedelta(days=i+1) # Past 7 days excluding today
        
        # Overloaded Drivers (Accumulate positive credits)
        for driver_id in overloaded_ids:
            effort = 80 # High effort
            avg = 50
            credits = effort - avg # +30 per day
            balance = credits * (7-i) # Rough accumulation
            
            db.add(models.FairnessHistory(
                driver_id=driver_id,
                date=day,
                daily_effort=effort,
                team_average=avg,
                credits_earned=credits,
                balance_snapshot=balance
            ))
            
        # Ready Drivers (Stay near zero)
        for driver_id in ready_ids:
            effort = 50 # Medium effort
            avg = 50
            credits = 0 # 0 per day
            balance = random.uniform(-10, 10)
            
            db.add(models.FairnessHistory(
                driver_id=driver_id,
                date=day,
                daily_effort=effort,
                team_average=avg,
                credits_earned=credits,
                balance_snapshot=balance
            ))

        # Underloaded Drivers (Accumulate negative credits)
        for driver_id in underloaded_ids:
            effort = 20 # Low effort
            avg = 50
            credits = effort - avg # -30 per day
            balance = credits * (7-i) 
            
            db.add(models.FairnessHistory(
                driver_id=driver_id,
                date=day,
                daily_effort=effort,
                team_average=avg,
                credits_earned=credits,
                balance_snapshot=balance
            ))
    
    db.commit()
    print("Seeded 7 days of history.")
    
    # 4. Update Current DriverStats to match the cumulative history
    # This ensures the dashboard "Current Balance" also aligns (though we rely on 7-day view now)
    
    # Overloaded (+210 balance approx)
    for driver_id in overloaded_ids:
        stat = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
        if stat: stat.total_balance = 210.0
        
    # Ready (~0 balance)
    for driver_id in ready_ids:
        stat = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
        if stat: stat.total_balance = 0.0
        
    # Underloaded (-210 balance approx)
    for driver_id in underloaded_ids:
        stat = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
        if stat: stat.total_balance = -210.0
        
    db.commit()
    print("Updated current driver stats.")
    print("Done! Refresh dashboard to see 3-3-2 distribution.")

if __name__ == "__main__":
    seed_demo_data()
