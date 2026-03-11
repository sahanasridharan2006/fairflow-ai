
from database import SessionLocal
from models import User
from logic import calculate_readiness_canonical, get_driver_stats_7d, calculate_team_average

def verify_locked_logic():
    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == 'driver').all()
        
        # Calculate Team Average Manually first to compare
        total_balance = 0
        count = 0
        stats_map = {}
        for d in drivers:
             s7 = get_driver_stats_7d(db, d.id)
             stats_map[d.id] = s7
             if d.status != 'ABSENT':
                 total_balance += s7['balance_7d']
                 count += 1
        
        team_avg = total_balance / count if count > 0 else 0
        print(f"Team Average Balance: {team_avg}")
        
        print(f"\nVerifying Canonical Logic for {len(drivers)} drivers:")
        for d in drivers:
            stats = stats_map[d.id]
            balance = stats['balance_7d']
            
            # Canonical Call
            result = calculate_readiness_canonical(balance, team_avg)
            status = result['status']
            dev = result['deviation']
            
            print(f"  - {d.name}: Balance={balance} -> Deviation={dev:.2f} -> Status={status}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_locked_logic()
