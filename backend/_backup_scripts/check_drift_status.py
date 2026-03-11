import database
import fairness_drift
from sqlalchemy.orm import Session

def check_drift():
    db = database.SessionLocal()
    drift = fairness_drift.detect_fairness_drift(db)
    print(f"Severity: {drift.get('severity')}")
    print(f"Detected: {drift.get('drift_detected')}")
    print("\nAffected Drivers:")
    for d in drift.get('affected_drivers', []):
        print(f" - {d.get('name')} (ID: {d.get('id')}): {d.get('deviation')}%")

if __name__ == "__main__":
    check_drift()
