"""
AI Validation Environment Setup - Phase 3: 7-Day Historical Data Generation

Generates scenario-driven historical data to validate AI fairness drift detection.
Each scenario is carefully crafted to test specific AI behaviors.
"""

from database import SessionLocal
import models
from datetime import date, timedelta
# Working hours based fairness (Amazon-scale logistics)
from working_hours import get_working_hours
import random

# Scenario-driven route assignments for 7 days
def generate_7_day_validation_data():
    """
    Generate 7 days of historical data across multiple validation scenarios
    """
    
    print("\n" + "="*70)
    print("📊 FAIRFLOW AI VALIDATION - 7-DAY DATA GENERATION")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Get all drivers
        drivers = db.query(models.User).filter(models.User.role == "driver").all()
        
        if len(drivers) != 8:
            print(f"❌ Expected 8 drivers, found {len(drivers)}")
            return
        
        # Map drivers to their validation roles
        driver_map = {}
        for driver in drivers:
            if "Sarah" in driver.name or "Marcus" in driver.name or "Aisha" in driver.name:
                driver_map[driver.id] = ("balanced", driver.name)
            elif "Elena" in driver.name:
                driver_map[driver.id] = ("overloaded", driver.name)
            elif "David" in driver.name:
                driver_map[driver.id] = ("underloaded", driver.name)
            elif "Priya" in driver.name:
                driver_map[driver.id] = ("leave", driver.name)
            elif "James" in driver.name:
                driver_map[driver.id] = ("part_time", driver.name)
            elif "Carlos" in driver.name:
                driver_map[driver.id] = ("sick", driver.name)
        
        print(f"📋 Driver Validation Roles:")
        for driver_id, (role, name) in driver_map.items():
            print(f"   - {name}: {role}")
        print()
        
        # Generate 7 days of data
        today = date.today()
        
        for day_offset in range(7):
            current_date = today - timedelta(days=7 - day_offset)  # Start from 7 days ago
            
            print(f"\n📅 Day {day_offset + 1} ({current_date}):")
            print("-" * 70)
            
            for driver_id, (role, name) in driver_map.items():
                # Determine status, effort, and working hours based on role and day
                status, difficulty, effort, working_hours_scenario = get_scenario_data(role, day_offset)
                
                # Get driver and stats
                driver = db.query(models.User).filter(models.User.id == driver_id).first()
                stats = db.query(models.DriverStats).filter(models.DriverStats.user_id == driver_id).first()
                
                # Update driver status
                driver.status = status
                
                # Use scenario-specific working hours (not status-based!)
                working_hours = working_hours_scenario
                
                # Create route if driver is available
                if working_hours > 0:
                    route = models.Route(
                        driver_id=driver_id,
                        date=current_date,
                        difficulty=difficulty,
                        status="Completed",
                        calculated_effort_score=effort
                    )
                    db.add(route)
                    
                    # Update stats
                    stats.effort_today = effort
                    
                    # Calculate credits (simplified: deviation from baseline 60)
                    team_baseline = 60.0
                    credits = team_baseline - effort
                    stats.credits_today = credits
                    stats.total_balance += credits
                else:
                    # Absent day
                    stats.effort_today = 0.0
                    stats.credits_today = 0.0
                
                # Calculate normalized effort (effort per working hour)
                normalized_effort = stats.effort_today / working_hours if working_hours > 0 else None
                
                # Create fairness snapshot
                snapshot = models.FairnessSnapshot(
                    driver_id=driver_id,
                    date=current_date,
                    effort=stats.effort_today,
                    credits=stats.credits_today,
                    balance=stats.total_balance,
                    working_hours=working_hours,
                    normalized_effort=normalized_effort
                )
                db.add(snapshot)
                
                # Print day summary
                norm_str = f"{normalized_effort:.1f}" if normalized_effort else "N/A"
                print(f"   {name:20} | Status: {status:10} | Effort: {effort:5.1f} | "
                      f"Hours: {working_hours:.1f} | Norm/hr: {norm_str:6}")
            
            db.commit()
        
        print("\n" + "="*70)
        print("✅ 7-DAY DATA GENERATION COMPLETE")
        print("="*70 + "\n")
        
        # Summary statistics
        print_summary_statistics(db)
        
    except Exception as e:
        print(f"\n❌ Error generating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_scenario_data(role, day_offset):
    """
    Returns (status, difficulty, effort, working_hours) based on driver role and day
   
    This is scenario-driven with WORKING HOURS for Amazon-scale logistics!
    """
    
    if role == "balanced":
        # Balanced drivers: consistent moderate effort, 8 hour shifts
        return ("ACTIVE", "Medium", random.uniform(55, 65), 8.0)
    
    elif role == "overloaded":
        # Elena: Overloaded - LONG WORKING HOURS + High Effort
        if day_offset < 2:
            return ("ACTIVE", "Medium", random.uniform(58, 62), 8.0)  # Start normal
        else:
            # Long-haul routes: 10-12 hour days with high effort
            hours = random.uniform(10, 12)
            effort = random.uniform(85, 95)
            return ("ACTIVE", "Hard", effort, hours)
    
    elif role == "underloaded":
        # David: Underloaded - short hours, easy routes
        hours = random.uniform(5, 7)
        effort = random.uniform(35, 45)
        return ("ACTIVE", "Easy", effort, hours)
    
    elif role == "leave":
        # Priya: Takes leave on days 2, 3, 5
        if day_offset in [1, 2, 4]:  # 0-indexed
            return ("ABSENT", "N/A", 0.0, 0.0)  # 0 hours!
        else:
            return ("ACTIVE", "Medium", random.uniform(55, 65), 8.0)
    
    elif role == "part_time":
        # James: Part-time - ONLY 4 hours/day, but normal effort intensity
        # This tests if system correctly measures per-hour fairness
        effort = random.uniform(28, 32)  # ~30 effort in 4 hours = 7.5/hour (FAIR!)
        return ("HALF_SHIFT", "Medium", effort, 4.0)
    
    elif role == "sick":
        # Carlos: Sick on days 3, 4 - reduced hours, protected routes
        if day_offset in [2, 3]:  # 0-indexed
            return ("SICK", "Easy", random.uniform(20, 28), 4.0)  # 4 hours, light work
        else:
            return ("ACTIVE", "Medium", random.uniform(55, 65), 8.0)
    
    return ("ACTIVE", "Medium", 60.0, 8.0)  # Default

def print_summary_statistics(db):
    """Print summary statistics after data generation"""
    
    print("\n📊 Summary Statistics:")
    print("="*70 + "\n")
    
    drivers = db.query(models.User).filter(models.User.role == "driver").all()
    
    for driver in drivers:
        snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == driver.id
        ).all()
        
        # Calculate average normalized effort (excluding absent days)
        active_snapshots = [s for s in snapshots if s.normalized_effort is not None]
        
        if active_snapshots:
            avg_normalized = sum(s.normalized_effort for s in active_snapshots) / len(active_snapshots)
            total_balance = snapshots[-1].balance if snapshots else 0
            
            print(f"{driver.name:20}")
            print(f"   Total Snapshots: {len(snapshots)}")
            print(f"   Active Days: {len(active_snapshots)}")
            print(f"   Avg Normalized Effort: {avg_normalized:.2f}")
            print(f"   Total Balance: {total_balance:.2f}\n")

if __name__ == "__main__":
    generate_7_day_validation_data()
