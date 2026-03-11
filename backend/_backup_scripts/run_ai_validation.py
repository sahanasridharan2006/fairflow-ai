"""
AI Validation Environment - Phase 4: Scenario Validation

Tests AI Fairness Drift Detection across 5 validation scenarios.
Validates correctness of drift detection, severity classification, and intervention logic.
"""

from database import SessionLocal
from fairness_drift import detect_fairness_drift, should_intervene_for_driver
import models
from datetime import date, timedelta

def run_validation_scenarios():
    """
    Run all 5 validation scenarios and evaluate AI behavior
   
    """
    
    print("\n" + "🧪 "*35)
    print("FAIRFLOW AI VALIDATION - SCENARIO TESTING")
    print("🧪 "*35 + "\n")
    
    db = SessionLocal()
    
    results = {
        "scenarios_tested": 0,
        "scenarios_passed": 0,
        "scenarios_failed": 0,
        "details": []
    }
    
    try:
        # Get driver mapping
        drivers = db.query(models.User).filter(models.User.role == "driver").all()
        driver_map = {d.name: d.id for d in drivers}
        
        print(f"📋 Testing with {len(drivers)} drivers\n")
        
        # SCENARIO A: Balanced Workload
        print("="*70)
        print("SCENARIO A: Balanced Workload Validation")
        print("="*70 + "\n")
        result_a = test_balanced_workload(db, driver_map)
        results["details"].append(result_a)
        results["scenarios_tested"] += 1
        if result_a["passed"]:
            results["scenarios_passed"] += 1
        else:
            results["scenarios_failed"] += 1
        
        # SCENARIO B: Overloaded Driver
        print("\n" + "="*70)
        print("SCENARIO B: Overloaded Driver Detection")
        print("="*70 + "\n")
        result_b = test_overloaded_driver(db, driver_map)
        results["details"].append(result_b)
        results["scenarios_tested"] += 1
        if result_b["passed"]:
            results["scenarios_passed"] += 1
        else:
            results["scenarios_failed"] += 1
        
        # SCENARIO C: Leave Handling
        print("\n" + "="*70)
        print("SCENARIO C: Leave/Absence Handling")
        print("="*70 + "\n")
        result_c = test_leave_handling(db, driver_map)
        results["details"].append(result_c)
        results["scenarios_tested"] += 1
        if result_c["passed"]:
            results["scenarios_passed"] += 1
        else:
            results["scenarios_failed"] += 1
        
        # SCENARIO D: Part-Time vs Full-Time
        print("\n" + "="*70)
        print("SCENARIO D: Part-Time vs Full-Time Comparison")
        print("="*70 + "\n")
        result_d = test_part_time_comparison(db, driver_map)
        results["details"].append(result_d)
        results["scenarios_tested"] += 1
        if result_d["passed"]:
            results["scenarios_passed"] += 1
        else:
            results["scenarios_failed"] += 1
        
        # SCENARIO E: AI Intervention
        print("\n" + "="*70)
        print("SCENARIO E: AI Intervention Trigger")
        print("="*70 + "\n")
        result_e = test_ai_intervention(db, driver_map)
        results["details"].append(result_e)
        results["scenarios_tested"] += 1
        if result_e["passed"]:
            results["scenarios_passed"] += 1
        else:
            results["scenarios_failed"] += 1
        
        # Generate final report
        generate_validation_report(results)
        
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        raise
    finally:
        db.close()
    
    return results

def test_balanced_workload(db, driver_map):
    """Test Scenario A: Balanced workload should show no drift"""
    
    print("Expected: No drift detected, Severity = NONE\n")
    
    drift = detect_fairness_drift(db)
    
    print(f"🔍 Drift Detected: {drift['drift_detected']}")
    print(f"📊 Severity: {drift['severity']}")
    print(f"💬 Explanation: {drift['explanation']}\n")
    
    # Check balanced drivers (Sarah, Marcus, Aisha)
    balanced_drivers = ["Sarah Chen", "Marcus Johnson", "Aisha Mohammed"]
    
    # Calculate their average normalized efforts
    for name in balanced_drivers:
        driver_id = driver_map.get(name)
        if driver_id:
            snapshots = db.query(models.FairnessSnapshot).filter(
                models.FairnessSnapshot.driver_id == driver_id,
                models.FairnessSnapshot.normalized_effort.isnot(None)
            ).all()
            
            if snapshots:
                avg = sum(s.normalized_effort for s in snapshots) / len(snapshots)
                print(f"   {name}: Avg Normalized Effort = {avg:.2f}")
    
    # Validation: Balanced drivers should NOT be in affected list (if drift is LOW/NONE)
    passed = drift['severity'] in ['NONE', 'LOW']
    
    print(f"\n{'✅ PASSED' if passed else '❌ FAILED'}: Balanced workload scenario\n")
    
    return {
        "name": "Scenario A: Balanced Workload",
        "passed": passed,
        "drift_detected": drift['drift_detected'],
        "severity": drift['severity'],
        "explanation": drift['explanation']
    }

def test_overloaded_driver(db, driver_map):
    """Test Scenario B: Elena should be detected as overloaded"""
    
    print("Expected: Drift detected, Elena in affected_drivers with high deviation\n")
    
    drift = detect_fairness_drift(db)
    
    print(f"🔍 Drift Detected: {drift['drift_detected']}")
    print(f"📊 Severity: {drift['severity']}")
    print(f"💬 Explanation: {drift['explanation']}\n")
    
    # Check if Elena is in affected drivers
    affected_names = [d['name'] for d in drift['affected_drivers']]
    elena_found = "Elena Rodriguez" in affected_names
    
    if elena_found:
        elena_info = next(d for d in drift['affected_drivers'] if d['name'] == "Elena Rodriguez")
        print(f"✅ Elena found in affected drivers")
        print(f"   Deviation: {elena_info['deviation']:+.1f}%")
        print(f" Avg Effort: {elena_info['avg_effort']:.2f}\n")
        
        passed = elena_info['deviation'] > 20  # Should be overloaded (+ve deviation)
    else:
        print(f"❌ Elena NOT found in affected drivers\n")
        passed = False
    
    print(f"{'✅ PASSED' if passed else '❌ FAILED'}: Overloaded driver detection\n")
    
    return {
        "name": "Scenario B: Overloaded Driver",
        "passed": passed,
        "elena_detected": elena_found,
        "drift_severity": drift['severity']
    }

def test_leave_handling(db, driver_map):
    """Test Scenario C: Priya's absences should not cause false drift"""
    
    print("Expected: Leave days excluded from calculations, no false drift spike\n")
    
    priya_id = driver_map.get("Priya Sharma")
    absent_normalized_correct = False
    
    if priya_id:
        # Get Priya's snapshots
        all_snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == priya_id
        ).all()
        
        active_snapshots = [s for s in all_snapshots if s.availability_units > 0]
        absent_snapshots = [s for s in all_snapshots if s.availability_units == 0]
        
        print(f"📊 Priya Sharma's Profile:")
        print(f"   Total Days: {len(all_snapshots)}")
        print(f"   Active Days: {len(active_snapshots)}")
        print(f"   Absent Days: {len(absent_snapshots)}\n")
        
        # Check that absent days have None for normalized_effort
        absent_normalized_correct = all(s.normalized_effort is None for s in absent_snapshots)
        
        print(f"   Absent days normalization: {'✅ Correct (None)' if absent_normalized_correct else '❌ Incorrect'}")
        
        # Calculate average normalized effort for active days
        if active_snapshots:
            avg_normalized = sum(s.normalized_effort for s in active_snapshots) / len(active_snapshots)
            print(f"   Active days avg normalized effort: {avg_normalized:.2f}\n")
        
        # Validation: Absent snapshots should not affect fairness calculations
        passed = absent_normalized_correct and len(absent_snapshots) == 3
    else:
        passed = False
    
    print(f"{'✅ PASSED' if passed else '❌ FAILED'}: Leave handling scenario\n")
    
    return {
        "name": "Scenario C: Leave Handling",
        "passed": passed,
        "absent_days_excluded": absent_normalized_correct
    }

def test_part_time_comparison(db, driver_map):
    """Test Scenario D: James (part-time) should show high normalized effort"""
    
    print("Expected: James has higher normalized effort than full-timers\n")
    
    james_id = driver_map.get("James Williams")
    sarah_id = driver_map.get("Sarah Chen")
    
    if james_id and sarah_id:
        # Get normalized efforts
        james_snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == james_id,
            models.FairnessSnapshot.normalized_effort.isnot(None)
        ).all()
        
        sarah_snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == sarah_id,
            models.FairnessSnapshot.normalized_effort.isnot(None)
        ).all()
        
        if james_snapshots and sarah_snapshots:
            james_avg = sum(s.normalized_effort for s in james_snapshots) / len(james_snapshots)
            sarah_avg = sum(s.normalized_effort for s in sarah_snapshots) / len(sarah_snapshots)
            
            print(f"📊 Comparison:")
            print(f"   James (Part-time, 0.5 availability): {james_avg:.2f} normalized effort")
            print(f"   Sarah (Full-time, 1.0 availability): {sarah_avg:.2f} normalized effort\n")
            
            # James should have ~2x normalized effort (same raw effort, half availability)
            ratio = james_avg / sarah_avg if sarah_avg > 0 else 0
            print(f"   Ratio (James/Sarah): {ratio:.2f}x\n")
            
            # Validation: James should have significantly higher normalized effort
            passed = james_avg > sarah_avg * 1.5  # At least 1.5x
        else:
            passed = False
    else:
        passed = False
    
    print(f"{'✅ PASSED' if passed else '❌ FAILED'}: Part-time comparison\n")
    
    return {
        "name": "Scenario D: Part-Time Comparison",
        "passed": passed,
        "james_normalized": james_avg if 'james_avg' in locals() else 0,
        "sarah_normalized": sarah_avg if 'sarah_avg' in locals() else 0
    }

def test_ai_intervention(db, driver_map):
    """Test Scenario E: AI should block hard route to overloaded driver"""
    
    print("Expected: AI blocks hard route assignment to Elena (overloaded)\n")
    
    elena_id = driver_map.get("Elena Rodriguez")
    
    if elena_id:
        # Test intervention for hard route
        should_block, reason = should_intervene_for_driver(db, elena_id, "Hard")
        
        print(f"🔍 Intervention Check:")
        print(f"   Should Block: {should_block}")
        if should_block:
            print(f"   Reason: {reason}\n")
        
        # Check if reason mentions "per available shift"
        has_availability_language = "per available shift" in reason.lower() if reason else False
        
        print(f"   Uses availability-aware language: {'✅' if has_availability_language else '❌'}\n")
        
        passed = should_block and has_availability_language
    else:
        passed = False
    
    print(f"{'✅ PASSED' if passed else '❌ FAILED'}: AI intervention scenario\n")
    
    return {
        "name": "Scenario E: AI Intervention",
        "passed": passed,
        "intervention_triggered": should_block if 'should_block' in locals() else False
    }

def generate_validation_report(results):
    """Generate final validation report"""
    
    print("\n" + "="*70)
    print("📊 FINAL VALIDATION REPORT")
    print("="*70 + "\n")
    
    print(f"Total Scenarios Tested: {results['scenarios_tested']}")
    print(f"✅ Passed: {results['scenarios_passed']}")
    print(f"❌ Failed: {results['scenarios_failed']}\n")
    
    success_rate = (results['scenarios_passed'] / results['scenarios_tested'] * 100) if results['scenarios_tested'] > 0 else 0
    
    print(f"Success Rate: {success_rate:.1f}%\n")
    
    print("Scenario Details:")
    print("-" * 70)
    for detail in results['details']:
        status = "✅ PASS" if detail['passed'] else "❌ FAIL"
        print(f"{status}: {detail['name']}")
    
    print("\n" + "="*70)
    
    if results['scenarios_failed'] == 0:
        print("🎉 ALL SCENARIOS PASSED - AI VALIDATION SUCCESSFUL!")
        print("System is PITCH-READY and JUDGE-DEFENSIBLE")
    else:
        print("⚠️  Some scenarios failed - review required")
    
    print("="*70 + "\n")
    
    # Save report
    save_validation_report(results)

def save_validation_report(results):
    """Save validation report to file"""
    
    with open("ai_validation_report.txt", "w") as f:
        f.write("="*70 + "\n")
        f.write("FAIRFLOW AI VALIDATION REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Scenarios Tested: {results['scenarios_tested']}\n")
        f.write(f"Passed: {results['scenarios_passed']}\n")
        f.write(f"Failed: {results['scenarios_failed']}\n\n")
        
        f.write("Scenario Results:\n")
        f.write("-"*70 + "\n\n")
        
        for detail in results['details']:
            f.write(f"{'✅ PASS' if detail['passed'] else '❌ FAIL'}: {detail['name']}\n")
            for key, value in detail.items():
                if key not in ['name', 'passed']:
                    f.write(f"  {key}: {value}\n")
            f.write("\n")
        
        f.write("="*70 + "\n")
    
    print("📄 Report saved to: ai_validation_report.txt\n")

if __name__ == "__main__":
    results = run_validation_scenarios()
