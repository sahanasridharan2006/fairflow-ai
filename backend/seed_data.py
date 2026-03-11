from database import SessionLocal, engine
import models
import auth
from datetime import date, timedelta

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

drivers = [
    ("Ravi Kumar","ravi@fairflow.com",120),
    ("Meena Sharma","meena@fairflow.com",110),
    ("Arjun Patel","arjun@fairflow.com",-90),
    ("Karthik Reddy","karthik@fairflow.com",-85),
    ("Shakthi","shakthi@fairflow.com",5)
]

for name,email,balance in drivers:

    user = db.query(models.User).filter(models.User.email==email).first()

    if not user:
        user = models.User(
            name=name,
            email=email,
            hashed_password=auth.get_password_hash("123456"),
            role="driver",
            status="ACTIVE"
        )
        db.add(user)
        db.flush()

    stats = models.DriverStats(
        user_id=user.id,
        total_balance=balance,
        effort_today=0,
        credits_today=0
    )
    db.add(stats)

    # create last 7 day snapshots
    for i in range(7):
        snapshot = models.FairnessSnapshot(
            driver_id=user.id,
            date=date.today()-timedelta(days=i),
            effort=70+i,
            credits=5-i,
            balance=balance
        )
        db.add(snapshot)

db.commit()
db.close()

print("Demo data inserted successfully")