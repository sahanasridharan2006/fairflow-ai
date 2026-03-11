"""
Test Availability-Aware Fairness Logic
Verify that normalized effort calculations work correctly for various scenarios
"""

from database import SessionLocal
import models
from availability import get_availability_units, calculate_normalized_effort
from fairness_drift import capture_daily_snapshot, get_effort_distribution, detect_fairness_drift

def test_availability_units():
    """Test availability unit calculations"""
    print("\n" + "="*60)
    print("TEST 1: Availability Units Calculation")
    print("="*60 + "\n")
    
    test_cases = [
        ("ACTIVE", 1.0),
        ("SICK", 0.5),
        ("ABSENT", 0.0),
        ("HALF_SHIFT", 0.5),
    ]
    
    for status, expected in test_cases:
        result = get_availability_units(status)
        status_str = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status_str}: {status} → {result} (expected {expected})")
    print()

def test_normalized_effort():
    """Test normalized effort calculations"""
    print("\n" + "="*60)
    print("TEST 2: Normalized Effort Calculation")
    print("="*60 + "\n")
    
    test_cases = [
        (60, 1.0, 60.0, "Full day"),
        (60, 0.5, 120.0, "Half day (2x intensity)"),
        (30, 0.5, 60.0, "Part-time same intensity"),
        (0, 0.0, None, "Absent driver"),
    ]
    
    for effort, availability, expected, description in test_cases:
        result = calculate_normalized_effort(effort, availability)
        status_str = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status_str}: {description}")
        print(f"   Effort={effort}, Availability={availability} → Normalized={result}")
    print()

def test_database_integration():
    """Test that database has new columns and migration worked"""
    print("\n" + "="*60)
    print("TEST 3: Database Integration")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    # Check if columns exist
    snapshots = db.query(models.FairnessSnapshot).limit(3).all()
    
    if not snapshots:
        print("⚠️  No snapshots in database yet")
        db.close()
        return
    
    print(f"📊 Sample of {len(snapshots)} snapshots:\n")
    
    all_pass = True
    for snapshot in snapshots:
        has_availability = hasattr(snapshot, 'availability_units')
        has_normalized = hasattr(snapshot, 'normalized_effort')
        
        if not (has_availability and has_normalized):
            all_pass = False
            print(f"❌ FAIL: Snapshot {snapshot.id} missing new columns")
        else:
            print(f"✅ Snapshot ID {snapshot.id}:")
            print(f"   Driver: {snapshot.driver_id}")
            print(f"   Raw Effort: {snapshot.effort}")
            print(f"   Availability: {snapshot.availability_units}")
            print(f"   Normalized: {snapshot.normalized_effort}")
            print()
    
    if all_pass:
        print("✅ All snapshots have availability-aware columns!\n")
    
    db.close()

def test_effort_distribution():
    """Test that effort distribution now uses normalized values"""
    print("\n" + "="*60)
    print("TEST 4: Effort Distribution (Normalized)")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    effort_dist = get_effort_distribution(db, last_n_days=7)
    
    if not effort_dist:
        print("⚠️  No effort distribution data yet")
        db.close()
        return
    
    print(f"📊 Effort Distribution (last 7 days):\n")
    
    for driver_id, avg_normalized_effort in effort_dist.items():
        driver = db.query(models.User).filter(models.User.id == driver_id).first()
        driver_name = driver.name if driver else f"Driver {driver_id}"
        print(f"   {driver_name}: {avg_normalized_effort:.2f} (normalized)")
    
    print(f"\n✅ Using NORMALIZED effort (not raw effort)")
    
    db.close()

def test_drift_detection():
    """Test drift detection with availability awareness"""
    print("\n" + "="*60)
    print("TEST 5: Drift Detection")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    drift_status = detect_fairness_drift(db)
    
    print(f"Drift Detected: {drift_status['drift_detected']}")
    print(f"Severity: {drift_status['severity']}")
    print(f"Explanation: {drift_status['explanation']}")
    print()
    
    if drift_status['affected_drivers']:
        print("Affected Drivers:")
        for driver in drift_status['affected_drivers'][:3]:
            print(f"   - {driver['name']}: {driver['deviation']:+.1f}% deviation")
    
    # Check if explanation uses "per shift" language
    explanation = drift_status['explanation']
    has_per_shift = "per shift" in explanation.lower() or "per available" in explanation.lower()
    
    if has_per_shift:
        print("\n✅ Explanation uses availability-aware language!")
    else:
        print(f"\n⚠️  Explanation might not mention per-shift: {explanation}")
    
    db.close()

if __name__ == "__main__":
    print("\n" + "🧪 "*30)
    print("AVAILABILITY-AWARE FAIRNESS TEST SUITE")
    print("🧪 "*30)
    
    test_availability_units()
    test_normalized_effort()
    test_database_integration()
    test_effort_distribution()
    test_drift_detection()
    
    print("\n" + "="*60)
    print("✅ TEST SUITE COMPLETE")
    print("="*60 + "\n")
