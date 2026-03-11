import unittest
from ml_recommendation import RouteDifficultyRecommender

class TestMLFairnessLogic(unittest.TestCase):
    
    def setUp(self):
        self.recommender = RouteDifficultyRecommender()
        
    def test_ranking_hard_route(self):
        """Hard Route: Underloaded (900s) > Ready (600s) > Overloaded (300s)"""
        
        # Drivers
        u_driver = {"driver_state": "UNDERLOADED", "fairness_balance": -50.0}
        r_driver = {"driver_state": "BALANCED", "fairness_balance": 10.0}
        o_driver = {"driver_state": "OVERLOADED", "fairness_balance": 60.0}
        
        s_u = self.recommender.calculate_preference_score({}, u_driver, "Hard")
        s_r = self.recommender.calculate_preference_score({}, r_driver, "Hard")
        s_o = self.recommender.calculate_preference_score({}, o_driver, "Hard")
        
        print(f"\n[Test] Hard Route Scores: U={s_u}, R={s_r}, O={s_o}")
        
        self.assertGreater(s_u, 800)
        self.assertGreater(s_r, 500)
        self.assertLess(s_o, 400)
        self.assertGreater(s_u, s_r)
        self.assertGreater(s_r, s_o)

    def test_ranking_easy_route(self):
        """Easy Route: Overloaded (900s) > Ready (600s) > Underloaded (300s)"""
        
        u_driver = {"driver_state": "UNDERLOADED", "fairness_balance": -50.0}
        r_driver = {"driver_state": "BALANCED", "fairness_balance": 10.0}
        o_driver = {"driver_state": "OVERLOADED", "fairness_balance": 60.0}
        
        s_u = self.recommender.calculate_preference_score({}, u_driver, "Easy")
        s_r = self.recommender.calculate_preference_score({}, r_driver, "Easy")
        s_o = self.recommender.calculate_preference_score({}, o_driver, "Easy")
        
        print(f"\n[Test] Easy Route Scores: O={s_o}, R={s_r}, U={s_u}")
        
        self.assertGreater(s_o, 800)
        self.assertGreater(s_r, 500)
        self.assertLess(s_u, 400)
        self.assertGreater(s_o, s_r)
        self.assertGreater(s_r, s_u)

    def test_tie_breakers(self):
        """Verify sorting within groups"""
        
        # Two Overloaded Drivers for Easy Route (Priority 1)
        # 100 vs 60. 100 should be greater score (More overloaded -> Needs easy more)
        o1 = {"driver_state": "OVERLOADED", "fairness_balance": 100.0}
        o2 = {"driver_state": "OVERLOADED", "fairness_balance": 60.0}
        
        s1 = self.recommender.calculate_preference_score({}, o1, "Easy")
        s2 = self.recommender.calculate_preference_score({}, o2, "Easy")
        
        print(f"\n[Test] Easy Route Tie Break: +100->{s1}, +60->{s2}")
        self.assertGreater(s1, s2)
        
        # Two Underloaded Drivers for Hard Route (Priority 1)
        # -50 vs -30. -50 should be greater score (More underloaded -> Needs hard more)
        u1 = {"driver_state": "UNDERLOADED", "fairness_balance": -50.0}
        u2 = {"driver_state": "UNDERLOADED", "fairness_balance": -30.0}
        
        s_u1 = self.recommender.calculate_preference_score({}, u1, "Hard")
        s_u2 = self.recommender.calculate_preference_score({}, u2, "Hard")
        
        print(f"\n[Test] Hard Route Tie Break: -50->{s_u1}, -30->{s_u2}")
        self.assertGreater(s_u1, s_u2)

if __name__ == '__main__':
    unittest.main()
