import database
import fairness_validator
import models
from sqlalchemy.orm import Session

def check_james():
    db = database.SessionLocal()
    v = fairness_validator.FairnessValidator()
    
    # Mock ML recommendation
    ml = {
        'recommended_difficulty': 'Easy',
        'confidence': 0.9,
        'reason': 'Test',
        'preference_score': 0.9
    }
    
    # Check James Williams (ID 7)
    res = v.validate_recommendation(ml, 7, db)
    print(f"Driver ID: 7")
    print(f"Approved Levels: {res.get('approved_levels')}")
    print(f"Action: {res.get('action')}")
    print(f"Reason: {res.get('reason')}")

if __name__ == "__main__":
    check_james()
