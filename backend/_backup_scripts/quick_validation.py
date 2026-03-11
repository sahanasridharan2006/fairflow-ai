"""
Simplified AI Validation - Quick Drift Check

Simple validation to verify AI fairness drift detection is working correctly
"""

from database import SessionLocal
from fairness_drift import detect_fairness_drift, should_intervene_for_driver, get_effort_distribution
import models

def quick_validation():
    """Quick validation of AI drift detection"""
    
    print("\n" + "="*70)
    print("FAIRFLOW AI VALIDATION - QUICK CHECK")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Get all drivers
        drivers = db.query(models.User).filter(models.User.role == "driver").all()
        
        print(f"📋 Total Drivers: {len(drivers)}\n")
        
        # Show effort distribution
        print("📊 Effort Distribution (Normalized, Last 7 Days):")
        print("-"*70)
        
        effort_dist = get_effort_distribution(db, last_n_days=7)
        
        for driver_id, avg_normalized in sorted(effort_dist.items(), key=lambda x: x[1], reverse=True):
            driver = db.query(models.User).filter(models.User.id == driver_id).first()
            if driver:
                print(f"   {driver.name:20} → {avg_normalized:.2f} (normalized effort)")
        
        print()
        
        # Detect drift
        print("\n" + "="*70)
        print("DRIFT DETECTION RESULT")
        print("="*70 + "\n")
        
        drift = detect_fairness_drift(db)
        
        print(f"🔍 Drift Detected: {drift['drift_detected']}")
        print(f"📊 Severity: {drift['severity']}")
        print(f"💬 Explanation:\n   {drift['explanation']}\n")
        
        if drift['affected_drivers']:
            print(f"⚠️  Affected Drivers ({len(drift['affected_drivers'])}):")
            print("-"*70)
            for driver_info in drift['affected_drivers']:
                print(f"   {driver_info['name']:20} → {driver_info['deviation']:+.1f}% deviation (avg: {driver_info['avg_effort']:.2f})")
            print()
        
        # Test intervention
        print("\n" + "="*70)
        print("AI INTERVENTION TEST")
        print("="*70 + "\n")
        
        # Find Elena (overloaded driver)
        elena = next((d for d in drivers if "Elena" in d.name), None)
        
        if elena:
            should_block, reason = should_intervene_for_driver(db, elena.id, "Hard")
            
            print(f"Testing hard route assignment to {elena.name}:")
            print(f"   Should Block: {should_block}")
            if should_block:
                print(f"   Reason: {reason}")
            print()
        
        # Summary
        print("\n" + "="*70)
        print("✅ VALIDATION COMPLETE")
        print("="*70)
        print(f"\nKey Findings:")
        print(f"   - {len(drivers)} drivers with 7 days of data")
        print(f"   - Drift severity: {drift['severity']}")
        print(f"   - Affected drivers: {len(drift['affected_drivers'])}")
        print(f"   - AI intervention: {'Active' if should_block else 'Inactive'}")
        print()
        
    finally:
        db.close()

if __name__ == "__main__":
    quick_validation()
