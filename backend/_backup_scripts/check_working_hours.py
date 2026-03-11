from database import SessionLocal
import models

db = SessionLocal()

# Check snapshots
snapshots = db.query(models.FairnessSnapshot).limit(10).all()

print("\n✅ Sample Fairness Snapshots (Working-Hours Based):")
print("=" * 80)
print(f"{'Driver':<10} | {'Effort':<8} | {'Hours':<6} | {'Norm/hr':<8} | {'Balance':<8}")
print("-" * 80)

for s in snapshots:
    driver = db.query(models.User).filter(models.User.id == s.driver_id).first()
    norm_str = f"{s.normalized_effort:.2f}" if s.normalized_effort else "N/A"
    print(f"{driver.name[:10]:<10} | {s.effort:<8.1f} | {s.working_hours:<6.1f} | {norm_str:<8} | {s.balance:<8.1f}")

print("\n📊 Summary by Driver:")
print("=" * 80)

drivers = db.query(models.User).filter(models.User.role == "driver").all()

for driver in drivers:
    driver_snaps = db.query(models.FairnessSnapshot).filter(
        models.FairnessSnapshot.driver_id == driver.id
    ).all()
    
    active_snaps = [s for s in driver_snaps if s.working_hours > 0]
    
    if active_snaps:
        avg_effort = sum(s.effort for s in active_snaps) / len(active_snaps)
        avg_hours = sum(s.working_hours for s in active_snaps) / len(active_snaps)
        avg_norm = sum(s.normalized_effort for s in active_snaps) / len(active_snaps)
        
        print(f"\n{driver.name}:")
        print(f"  Avg Effort: {avg_effort:.1f}")
        print(f"  Avg Hours: {avg_hours:.1f}")
        print(f"  Avg Effort/Hour: {avg_norm:.2f} ⭐")
        print(f"  Total Snapshots: {len(driver_snaps)} ({len(active_snaps)} active)")

db.close()
