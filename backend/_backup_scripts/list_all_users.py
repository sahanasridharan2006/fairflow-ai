"""
Quick check of all users in database
"""
from database import SessionLocal
import models

db = SessionLocal()

print("\n" + "="*70)
print("DATABASE USER CHECK")
print("="*70 + "\n")

users = db.query(models.User).all()

print(f"Total Users: {len(users)}\n")

drivers = [u for u in users if u.role == "driver"]
admins = [u for u in users if u.role == "admin"]

print(f"📊 Breakdown:")
print(f"   Drivers: {len(drivers)}")
print(f"   Admins: {len(admins)}\n")

print("DRIVERS:")
print("-"*70)
for i, driver in enumerate(drivers, 1):
    print(f"{i}. {driver.name}")
    print(f"   Email: {driver.email}")
    print(f"   ID: {driver.id}\n")

print("ADMINS:")
print("-"*70)
for admin in admins:
    print(f"   {admin.name} ({admin.email})\n")

print("="*70 + "\n")

db.close()
