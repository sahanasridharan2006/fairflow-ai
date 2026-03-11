"""
Verify all 8 drivers have 7 days of scenario data
"""
from database import SessionLocal
import models

db = SessionLocal()

print("\n" + "="*70)
print("VERIFICATION: 7-DAY DATA FOR ALL 8 DRIVERS")
print("="*70 + "\n")

drivers = db.query(models.User).filter(models.User.role == "driver").all()

print(f"Total Drivers: {len(drivers)}\n")

for i, driver in enumerate(drivers, 1):
    snapshots = db.query(models.FairnessSnapshot).filter(
        models.FairnessSnapshot.driver_id == driver.id
    ).all()
    
    routes = db.query(models.Route).filter(
        models.Route.driver_id == driver.id
    ).all()
    
    # Calculate average normalized effort (excluding absent days)
    active_snapshots = [s for s in snapshots if s.normalized_effort is not None]
    avg_normalized = sum(s.normalized_effort for s in active_snapshots) / len(active_snapshots) if active_snapshots else 0
    
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver.id).first()
    
    print(f"{i}. {driver.name:20}")
    print(f"   📊 Snapshots: {len(snapshots)}/7 days")
    print(f"   🚗 Routes: {len(routes)}")
    print(f"   📈 Avg Normalized Effort: {avg_normalized:.2f}")
    print(f"   💰 Balance: {stats.total_balance:.2f}" if stats else "   💰 Balance: N/A")
    print()

print("="*70)
print("SCENARIO BREAKDOWN:")
print("="*70 + "\n")

# Check each scenario
scenarios = {
    "Balanced (Sarah)": "Sarah Chen",
    "Balanced (Marcus)": "Marcus Johnson", 
    "Balanced (Aisha)": "Aisha Mohammed",
    "Overloaded (Elena)": "Elena Rodriguez",
    "Underloaded (David)": "David Park",
    "Leave (Priya)": "Priya Sharma",
    "Part-Time (James)": "James Williams",
    "Sick Days (Carlos)": "Carlos Santos"
}

for scenario_name, driver_name in scenarios.items():
    driver = db.query(models.User).filter(models.User.name == driver_name).first()
    if driver:
        snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == driver.id
        ).all()
        
        active_days = sum(1 for s in snapshots if s.availability_units > 0)
        absent_days = sum(1 for s in snapshots if s.availability_units == 0)
        
        active_snapshots = [s for s in snapshots if s.normalized_effort is not None]
        avg_normalized = sum(s.normalized_effort for s in active_snapshots) / len(active_snapshots) if active_snapshots else 0
        
        status = "✅" if len(snapshots) == 7 else "❌"
        print(f"{status} {scenario_name:25} → {len(snapshots)}/7 days | Active: {active_days} | Absent: {absent_days} | Avg: {avg_normalized:.1f}")

print("\n" + "="*70 + "\n")

db.close()
