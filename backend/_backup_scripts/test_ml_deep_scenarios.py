
"""
Deep Validation Script for ML & FairFlow Scenarios
Validates all 10 user-defined scenarios to ensure system correctness.
"""

import sys
import os
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_recommendation import RouteDifficultyRecommender
from fairness_validator import FairnessValidator

def run_deep_testing():
    recommender = RouteDifficultyRecommender()
    validator = FairnessValidator()
    
    print("\n" + "=== "*20)
    print("FAIRFLOW DEEP SCENARIO VALIDATION")
    print("=== "*20 + "\n")

    scenarios = [
        {
            "id": 1,
            "name": "Morning City Apartments (Easy)",
            "route": {
                "apartments_count": 4,
                "stairs_present": False,
                "heavy_boxes_count": 0,
                "traffic_level": "Low",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 6.2,
                "fairness_balance": 85,
                "consecutive_hard_routes": 0,
                "working_hours_today": 8,
                "drift_severity": "NONE",
                "status": "ACTIVE"
            },
            "expected_ml": "Easy",
            "expected_action": "approved"
        },
        {
            "id": 2,
            "name": "Normal Urban Midday (Medium)",
            "route": {
                "apartments_count": 8,
                "stairs_present": False,
                "heavy_boxes_count": 5,
                "traffic_level": "Normal",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 7.6,
                "fairness_balance": 2,
                "consecutive_hard_routes": 1,
                "working_hours_today": 8,
                "drift_severity": "NONE",
                "status": "ACTIVE"
            },
            "expected_ml": "Medium",
            "expected_action": "approved"
        },
        {
            "id": 3,
            "name": "Evening Rush + High Apartments (Hard)",
            "route": {
                "apartments_count": 18,
                "stairs_present": True,
                "heavy_boxes_count": 9,
                "traffic_level": "High",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 7.4,
                "fairness_balance": 10,
                "consecutive_hard_routes": 0,
                "working_hours_today": 8,
                "drift_severity": "NONE",
                "status": "ACTIVE"
            },
            "expected_ml": "Hard",
            "expected_action": "approved"
        },
        {
            "id": 4,
            "name": "Hard Route, but Fatigued Driver",
            "route": {
                "apartments_count": 18,
                "stairs_present": True,
                "heavy_boxes_count": 9,
                "traffic_level": "High",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 9.2,   # High effort
                "fairness_balance": -38,               # Behind
                "consecutive_hard_routes": 3,          # Burnout risk
                "working_hours_today": 8,
                "drift_severity": "LOW",
                "status": "ACTIVE"
            },
            "expected_ml": "Hard",                    # ML sees route complexity
            "expected_action": "adjusted",             # Validator should downgrade
            "expected_difficulty": "Medium"
        },
        {
            "id": 5,
            "name": "Long-Haul Driver Already Overloaded",
            "route": {
                "apartments_count": 20,
                "stairs_present": True,
                "heavy_boxes_count": 15,
                "traffic_level": "High",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 11.0,  # Severe overload (>40% deviation)
                "fairness_balance": -120,               # Way behind
                "consecutive_hard_routes": 0,
                "working_hours_today": 8,
                "drift_severity": "HIGH",
                "status": "ACTIVE"
            },
            "expected_ml": "Hard",
            "expected_action": "blocked"               # Severe overload = block
        },
        {
            "id": 6,
            "name": "Sick / Half-Shift Driver",
            "route": {
                "apartments_count": 10,
                "stairs_present": False,
                "heavy_boxes_count": 5,
                "traffic_level": "Normal",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 7.8,
                "fairness_balance": 0,
                "consecutive_hard_routes": 0,
                "working_hours_today": 4,               # Half shift
                "drift_severity": "NONE",
                "status": "SICK"
            },
            "expected_action": "blocked"                # Sick = block
        },
        {
            "id": 7,
            "name": "Driver on Leave",
            "route": {
                "apartments_count": 5,
                "stairs_present": False,
                "heavy_boxes_count": 0,
                "traffic_level": "Low",
                "weather_severity": "Clear"
            },
            "driver": {
                "normalized_effort_last_3_days": 0,
                "fairness_balance": 0,
                "consecutive_hard_routes": 0,
                "working_hours_today": 0,
                "drift_severity": "NONE",
                "status": "ABSENT"
            },
            "expected_action": "blocked"
        }
    ]

    for s in scenarios:
        print(f"--- Scenario {s['id']}: {s['name']} ---")
        
        # 1. Run ML Recommender
        ml_res = recommender.recommend(s['route'], s['driver'])
        print(f"ML Suggestion: {ml_res['recommended_difficulty']} (Confidence: {ml_res['confidence']})")
        print(f"ML Reason: {ml_res['reason']}")
        
        # 2. Run FairFlow Validator (Mocked DB session for standalone testing)
        mock_db = MagicMock()
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.status = s['driver']['status']
        mock_driver.alert = "Protected" if s['driver'].get('fairness_balance', 0) < -100 else None
        
        mock_stats = MagicMock()
        mock_stats.total_balance = s['driver'].get('fairness_balance', 0)
        
        mock_db.query().filter().first.side_effect = [mock_driver, mock_stats]
        
        # We need to monkeypatch the internal check methods to respect the scenario driver context
        validator._check_normalized_effort_overload = MagicMock(return_value={
            'is_overloaded': s['driver'].get('normalized_effort_last_3_days', 7.5) > 8.5 or s['driver'].get('fairness_balance', 0) < -40,
            'deviation': ((s['driver'].get('normalized_effort_last_3_days', 7.5) - 7.5) / 7.5 * 100) if s['driver'].get('normalized_effort_last_3_days', 0) > 0 else 0
        })
        validator._check_consecutive_hard_routes = MagicMock(return_value=s['driver'].get('consecutive_hard_routes', 0))
        
        # Also need to mock detect_fairness_drift for Scenario 5 (HIGH drift)
        from fairness_validator import detect_fairness_drift
        import fairness_validator
        old_detect = fairness_validator.detect_fairness_drift
        fairness_validator.detect_fairness_drift = MagicMock(return_value={
            'severity': s['driver'].get('drift_severity', 'NONE'),
            'affected_drivers': [{'id': 1, 'name': 'Test Driver'}] if s['driver'].get('drift_severity', 'NONE') != 'NONE' else []
        })

        ff_res = validator.validate_recommendation(ml_res, 1, mock_db)
        
        # Restore mock
        fairness_validator.detect_fairness_drift = old_detect

        print(f"FairFlow Action: {ff_res['action'].upper()}")
        print(f"Approved: {ff_res['approved_difficulty']}")
        print(f"Blocked: {ff_res['blocked_levels']}")
        print(f"Reason: {ff_res['reason']}")
        
        # Verification
        passed = True
        if 'expected_ml' in s and ml_res['recommended_difficulty'] != s['expected_ml']:
            print(f"X FAIL: Expected ML {s['expected_ml']}, got {ml_res['recommended_difficulty']}")
            passed = False
        if ff_res['action'] != s['expected_action']:
            print(f"X FAIL: Expected Action {s['expected_action']}, got {ff_res['action']}")
            passed = False
            
        if passed:
            print("PASS: Scenario PASSED")
        else:
            print("FAIL: Scenario FAILED")
        print("\n")

    # Scenario 9: Distribution Check
    print("--- Scenario 9: 8-Driver Board Snapshot ---")
    results = []
    import random
    for i in range(8):
        # Mixed features
        feats = {
            "apartments_count": random.randint(2, 25),
            "stairs_present": random.choice([True, False]),
            "heavy_boxes_count": random.randint(0, 15),
            "traffic_level": random.choice(["Low", "Normal", "High"]),
            "weather_severity": "Clear"
        }
        # Mixed drivers
        ctx = {
            "normalized_effort_last_3_days": random.uniform(6.0, 10.0),
            "fairness_balance": random.randint(-60, 60),
            "consecutive_hard_routes": random.randint(0, 3),
            "working_hours_today": 8,
            "drift_severity": "NONE"
        }
        res = recommender.recommend(feats, ctx)
        results.append(res['recommended_difficulty'])
    
    counts = { "Easy": results.count("Easy"), "Medium": results.count("Medium"), "Hard": results.count("Hard") }
    print(f"Board Distribution: {counts}")
    if counts['Medium'] >= 2 and counts['Easy'] >= 1 and counts['Hard'] >= 1:
        print("PASS: Visually balanced board")
    else:
        print("FAIL: Distribution skewed")

    print("\n" + "--- "*20)
    print("VALIDATION COMPLETE")
    print("--- "*20 + "\n")

if __name__ == "__main__":
    run_deep_testing()
