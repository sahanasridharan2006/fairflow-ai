"""
Test ML Recommendation System with FairFlow Validation

Tests the 3-layer decision support architecture:
Layer 1: ML suggests route difficulty
Layer 2: FairFlow validates and overrides based on working-hours fairness
Layer 3: Admin final decision
"""

from database import SessionLocal
import models
from ml_recommendation import RouteDifficultyRecommender
from fairness_validator import FairnessValidator
from fairness_drift import get_effort_distribution

db = SessionLocal()

print("\n" + "="*80)
print("🧪 ML RECOMMENDATION + FAIRFLOW VALIDATION TEST")
print("="*80)

# Get a test driver
drivers = db.query(models.User).filter(models.User.role == "driver").limit(3).all()

if not drivers:
    print("❌ No drivers found. Run generate_validation_data.py first.")
    db.close()
    exit()

print(f"\n📋 Testing with {len(drivers)} drivers:\n")

# Test scenarios
test_scenarios = [
    {
        'name': 'Easy Route (Low Complexity)',
        'route_features': {
            'apartments_count': 5,
            'stairs_present': False,
            'heavy_boxes_count': 2,
            'traffic_level': 'Low',
            'weather_severity': 'Clear'
        }
    },
    {
        'name': 'Medium Route (Moderate Complexity)',
        'route_features': {
            'apartments_count': 12,
            'stairs_present': False,
            'heavy_boxes_count': 8,
            'traffic_level': 'Normal',
            'weather_severity': 'Clear'
        }
    },
    {
        'name': 'Hard Route (High Complexity)',
        'route_features': {
            'apartments_count': 20,
            'stairs_present': True,
            'heavy_boxes_count': 15,
            'traffic_level': 'High',
            'weather_severity': 'Rain'
        }
    }
]

for driver in drivers:
    print(f"\n{'='*80}")
    print(f"🚗 Driver: {driver.name}")
    print(f"   Status: {driver.status}")
    print("="*80)
    
    # Get driver context
    effort_dist = get_effort_distribution(db, last_n_days=3)
    driver_normalized_effort = effort_dist.get(driver.id, 7.5)
    
    stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver.id).first()
    fairness_balance = stats.total_balance if stats else 0.0
    
    print(f"   Effort per hour (last 3 days): {driver_normalized_effort:.2f}")
    print(f"   Fairness Balance: {fairness_balance:+.1f}")
    
    driver_context = {
        'normalized_effort_last_3_days': driver_normalized_effort,
        'fairness_balance': fairness_balance,
        'consecutive_hard_routes': 0,
        'working_hours_today': 8.0,
        'drift_severity': 'NONE'
    }
    
    # Test each scenario
    for scenario in test_scenarios:
        print(f"\n📦 {scenario['name']}")
        print("-" * 80)
        
        # Layer 1: ML Recommendation
        ml_recommender = RouteDifficultyRecommender()
        ml_result = ml_recommender.recommend(scenario['route_features'], driver_context)
        
        print(f"🤖 ML Recommendation:")
        print(f"   Suggested: {ml_result['recommended_difficulty']}")
        print(f"   Confidence: {ml_result['confidence']*100:.0f}%")
        print(f"   Reason: {ml_result['reason']}")
        print(f"   Route Score: {ml_result['route_score']:.1f}")
        
        # Layer 2: FairFlow Validation
        validator = FairnessValidator()
        fairflow_decision = validator.validate_recommendation(ml_result, driver.id, db)
        
        print(f"\n🧠 FairFlow Decision:")
        print(f"   Action: {fairflow_decision['action'].upper()}")
        print(f"   Approved Difficulty: {fairflow_decision['approved_difficulty']}")
        
        if fairflow_decision['fairness_override']:
            print(f"   ⚠️  FAIRNESS OVERRIDE: {fairflow_decision['override_reason']}")
        
        print(f"   Reason: {fairflow_decision['reason']}")
        
        # Layer 3: Final outcome
        if fairflow_decision['action'] == 'approved':
            print(f"\n✅ RESULT: ML suggestion APPROVED by FairFlow")
        elif fairflow_decision['action'] == 'adjusted':
            print(f"\n⚠️  RESULT: ML suggestion ADJUSTED by FairFlow")
            print(f"    {ml_result['recommended_difficulty']} → {fairflow_decision['approved_difficulty']}")
        else:
            print(f"\n🛑 RESULT: Assignment BLOCKED by FairFlow")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
print("\nKey Takeaways:")
print("  - ML provides intelligent suggestions based on route features + driver context")
print("  - FairFlow validates ALL suggestions against working-hours fairness rules")
print("  - FairFlow can OVERRIDE ML to protect driver fairness")
print("  - Admin always has final control")
print("\nArchitecture validated: ML suggests → FairFlow validates → Admin decides")

db.close()
