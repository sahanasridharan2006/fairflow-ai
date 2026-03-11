from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import date
from logic import update_fairness_ledger

def clear_today():
    db = SessionLocal()
    today = date.today()
    print(f"Clearing assignments for {today}...")
    
    # 1. Get today's routes
    routes = db.query(models.Route).filter(models.Route.date == today).all()
    count = len(routes)
    
    # 2. Revert logic (Optional but good for data integrity - we'll just delete for now as 'Unassign' implies reset)
    # Ideally should revert metrics, but 'reset' usually implies wiping the slate.
    # Given the complexity of dependent metrics (fairness ledger, credits), 
    # and that this is a 'reset' request, we'll just delete the route rows.
    # The fairness calculations (7-day view) will naturally update on next fetch as they aggregate 'past' routes.
    # Since 'today' is no longer 'past' once deleted, it won't count.
    
    try:
        if count > 0:
            db.query(models.Route).filter(models.Route.date == today).delete()
            
            # Reset driver daily stats if any (like effort_today)
            drivers = db.query(models.User).filter(models.User.role == "driver").all()
            for driver in drivers:
                stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver.id).first()
                if stats:
                    stats.effort_today = 0
            
            db.commit()
            print(f"Successfully removed {count} assignments.")
        else:
            print("No assignments found for today.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_today()
