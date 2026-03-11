
from fairness_validator import FairnessValidator

def test_ranking():
    validator = FairnessValidator()
    
    # Mock Drivers
    drivers = [
        {'driver_id': 1, 'driver_context': {'driver_state': 'Overloaded', 'fairness_balance': 200}, 'driver_name': 'Over200', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
        {'driver_id': 2, 'driver_context': {'driver_state': 'Overloaded', 'fairness_balance': 50}, 'driver_name': 'Over50', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
        {'driver_id': 3, 'driver_context': {'driver_state': 'Ready', 'fairness_balance': 10}, 'driver_name': 'Ready10', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
        {'driver_id': 4, 'driver_context': {'driver_state': 'Ready', 'fairness_balance': -20}, 'driver_name': 'Ready-20', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
        {'driver_id': 5, 'driver_context': {'driver_state': 'Underloaded', 'fairness_balance': -10}, 'driver_name': 'Under-10', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
        {'driver_id': 6, 'driver_context': {'driver_state': 'Underloaded', 'fairness_balance': -100}, 'driver_name': 'Under-100', 'fairflow_decision': {'action': 'approved'}, 'ml_recommendation': {'preference_score': 0}},
    ]

    print("\n--- EASY ROUTE RANKING ---")
    print("Goal: Overloaded (DESC) > Ready (ABS) > Underloaded (DESC)")
    print("Expect: Over200, Over50, Ready10, Ready-20, Under-10, Under-100")
    res = validator.rank_drivers(list(drivers), "Easy")
    for d in res: print(f"{d['preference_rank']}. {d['driver_name']} ({d['driver_context']['driver_state']}, {d['driver_context']['fairness_balance']})")

    print("\n--- MEDIUM ROUTE RANKING ---")
    print("Goal: Ready (ABS) > Underloaded (DESC) > Overloaded (ASC)")
    print("Expect: Ready10, Ready-20, Under-10, Under-100, Over50, Over200")
    res = validator.rank_drivers(list(drivers), "Medium")
    for d in res: print(f"{d['preference_rank']}. {d['driver_name']} ({d['driver_context']['driver_state']}, {d['driver_context']['fairness_balance']})")

    print("\n--- HARD ROUTE RANKING ---")
    print("Goal: Underloaded (ASC) > Ready (ABS) > Overloaded (ASC)")
    print("Expect: Under-100, Under-10, Ready10, Ready-20, Over50, Over200")
    res = validator.rank_drivers(list(drivers), "Hard")
    for d in res: print(f"{d['preference_rank']}. {d['driver_name']} ({d['driver_context']['driver_state']}, {d['driver_context']['fairness_balance']})")

if __name__ == "__main__":
    test_ranking()
