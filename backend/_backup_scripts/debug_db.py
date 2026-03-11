from database import SessionLocal
import models
from datetime import date

db = SessionLocal()
user = db.query(models.User).filter(models.User.email == "ravi@fairflow.com").first()

if not user:
    print("User Ravi NOT FOUND")
else:
    print(f"User found: {user.name} ID: {user.id}")
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == user.id).first()
    if not stats:
        print("Stats NOT FOUND")
    else:
        print(f"Stats found: {stats.total_balance}")

    today = date.today()
    print(f"Checking route for date: {today}")
    route = db.query(models.Route).filter(models.Route.driver_id == user.id, models.Route.date == today).first()
    if not route:
        print("Route NOT FOUND")
        # Check all routes for this user
        all_routes = db.query(models.Route).filter(models.Route.driver_id == user.id).all()
        print(f"Total routes for user: {len(all_routes)}")
        for r in all_routes:
            print(f"Route Date: {r.date}")
    else:
        print(f"Route found: difficult={route.difficulty}")

db.close()
