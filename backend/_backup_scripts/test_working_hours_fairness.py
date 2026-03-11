from database import SessionLocal
import models
from fairness_drift import detect_fairness_drift, should_intervene_for_driver

db = SessionLocal()

print("\n" + "="*80)
print("🧪 WORKING-HOURS FAIRNESS VALIDATION")
print("="*80)

# Check snapshots
total_snaps = db.query(models.FairnessSnapshot).count()
print(f"\n✅ Total Fairness Snapshots: {total_snaps}")

# Check working hours data
sample = db.query(models.FairnessSnapshot).filter(models.FairnessSnapshot.working_hours > 0).limit(5).all()

print(f"\n📊 Sample Snapshots (Working-Hours Based):")
print("-" * 80)
for s in sample:
    driver = db.query(models.User).filter(models.User.id == s.driver_id).first()
    norm_str = f"{s.normalized_effort:.2f}" if s.normalized_effort else "N/A"
    print(f"{driver.name[:15]:<15} | Effort: {s.effort:6.1f} | Hours: {s.working_hours:4.1f} | Per Hour: {norm_str:6}")

# Test drift detection
print(f"\n🔍 Testing Drift Detection:")
print("-" * 80)

try:
    drift = detect_fairness_drift(db)
    
    print(f"Drift Detected: {drift['drift_detected']}")
    print(f"Severity: {drift['severity']}")
    print(f"Explanation: {drift['explanation']}")
    
    if drift['affected_drivers']:
        print(f"\n⚠️  Affected Drivers:")
        for d in drift['affected_drivers']:
            print(f"  - {d['name']}: {d['deviation']:+.1f}% (avg effort/hour: {d['avg_effort']:.1f})")
    
    print(f"\n📈 Metrics:")
    print(f"  Current Variance: {drift['metrics']['current_variance']:.2f}")
    print(f"  Baseline Variance: {drift['metrics']['baseline_variance']:.2f}")
    print(f"  Change: {drift['metrics']['variance_change_pct']:+.1f}%")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test AI intervention
print(f"\n🤖 Testing AI Intervention:")
print("-" * 80)

drivers = db.query(models.User).filter(models.User.role == "driver").limit(3).all()

for driver in drivers:
    try:
        should_block, reason = should_intervene_for_driver(db, driver.id, "Hard")
        
        if should_block:
            print(f"🛑 {driver.name}: BLOCKED")
            print(f"   Reason: {reason}")
        else:
            print(f"✅ {driver.name}: Can receive Hard routes")
    except Exception as e:
        print(f"❌ {driver.name}: Error - {e}")

print("\n" + "="*80)
print("✅ VALIDATION COMPLETE")
print("="*80)

db.close()
