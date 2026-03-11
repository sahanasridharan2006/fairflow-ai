"""
Detailed 7-Day Scenario Report for All 8 Drivers
Shows every snapshot with effort, availability, and normalized effort
"""
from database import SessionLocal
import models
from datetime import date, timedelta

db = SessionLocal()

# Create detailed report file
report_file = "DETAILED_8_DRIVER_SCENARIOS.txt"

with open(report_file, "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("FAIRFLOW AI VALIDATION - DETAILED 7-DAY SCENARIO REPORT\n")
    f.write("="*80 + "\n\n")
    
    f.write("This report shows ALL snapshots for ALL 8 drivers across 7 days.\n")
    f.write("Each driver has a specific validation scenario.\n\n")
    
    drivers = db.query(models.User).filter(models.User.role == "driver").order_by(models.User.id).all()
    
    f.write(f"Total Drivers: {len(drivers)}\n")
    f.write(f"Days per Driver: 7\n")
    f.write(f"Total Snapshots: {len(drivers) * 7}\n\n")
    
    f.write("="*80 + "\n\n")
    
    # Map drivers to scenarios
    scenario_map = {
        "Sarah Chen": "SCENARIO A: Balanced Workload",
        "Marcus Johnson": "SCENARIO A: Balanced Workload",
        "Aisha Mohammed": "SCENARIO A: Balanced Workload",
        "Elena Rodriguez": "SCENARIO B: Progressive Overload",
        "David Park": "SCENARIO D: Underloaded (Easy Routes)",
        "Priya Sharma": "SCENARIO C: Leave/Absence Handling",
        "James Williams": "SCENARIO D: Part-Time (Half Shifts)",
        "Carlos Santos": "SCENARIO E: Sick Days (Reduced Capacity)"
    }
    
    for i, driver in enumerate(drivers, 1):
        scenario = scenario_map.get(driver.name, "Unknown")
        
        f.write(f"\n{'='*80}\n")
        f.write(f"DRIVER {i}: {driver.name}\n")
        f.write(f"{'='*80}\n\n")
        
        f.write(f"Email: {driver.email}\n")
        f.write(f"Scenario: {scenario}\n")
        f.write(f"Current Status: {driver.status}\n\n")
        
        # Get all snapshots
        snapshots = db.query(models.FairnessSnapshot).filter(
            models.FairnessSnapshot.driver_id == driver.id
        ).order_by(models.FairnessSnapshot.date).all()
        
        # Get stats
        stats = db.query(models.DriverStats).filter(
            models.DriverStats.user_id == driver.id
        ).first()
        
        f.write(f"Final Balance: {stats.total_balance:.2f}\n" if stats else "Final Balance: N/A\n")
        f.write(f"Total Snapshots: {len(snapshots)}\n\n")
        
        # Calculate averages
        active_snapshots = [s for s in snapshots if s.normalized_effort is not None]
        avg_effort = sum(s.effort for s in snapshots) / len(snapshots) if snapshots else 0
        avg_normalized = sum(s.normalized_effort for s in active_snapshots) / len(active_snapshots) if active_snapshots else 0
        
        f.write(f"Average Raw Effort: {avg_effort:.2f}\n")
        f.write(f"Average Normalized Effort: {avg_normalized:.2f} (active days only)\n\n")
        
        f.write("-"*80 + "\n")
        f.write("DAY-BY-DAY BREAKDOWN:\n")
        f.write("-"*80 + "\n\n")
        
        # Header
        f.write(f"{'Day':<6} {'Date':<12} {'Effort':<8} {'Avail':<7} {'Normalized':<12} {'Credits':<10} {'Balance':<10} {'Status'}\n")
        f.write("-"*80 + "\n")
        
        for day_num, snapshot in enumerate(snapshots, 1):
            effort_str = f"{snapshot.effort:.1f}"
            avail_str = f"{snapshot.availability_units:.1f}"
            norm_str = f"{snapshot.normalized_effort:.1f}" if snapshot.normalized_effort is not None else "N/A"
            credits_str = f"{snapshot.credits:.1f}"
            balance_str = f"{snapshot.balance:.1f}"
            
            # Determine status based on availability
            if snapshot.availability_units == 0:
                status = "ABSENT"
            elif snapshot.availability_units == 0.5:
                status = "HALF/SICK"
            else:
                status = "ACTIVE"
            
            f.write(f"{day_num:<6} {str(snapshot.date):<12} {effort_str:<8} {avail_str:<7} {norm_str:<12} {credits_str:<10} {balance_str:<10} {status}\n")
        
        f.write("\n")
        
        # Get routes for context
        routes = db.query(models.Route).filter(
            models.Route.driver_id == driver.id
        ).order_by(models.Route.date).all()
        
        if routes:
            f.write("ROUTES ASSIGNED:\n")
            f.write("-"*80 + "\n")
            for route in routes:
                f.write(f"  {route.date}: {route.difficulty} (Effort: {route.calculated_effort_score:.1f})\n")
            f.write("\n")
        
        # Scenario explanation
        f.write("SCENARIO EXPLANATION:\n")
        f.write("-"*80 + "\n")
        
        if "Sarah" in driver.name or "Marcus" in driver.name or "Aisha" in driver.name:
            f.write("This driver represents a BALANCED workload scenario.\n")
            f.write("Expected: Consistent moderate effort (55-65) all 7 days.\n")
            f.write("Purpose: Establish baseline for 'fair' distribution.\n")
        
        elif "Elena" in driver.name:
            f.write("This driver represents a PROGRESSIVE OVERLOAD scenario.\n")
            f.write("Expected: Days 1-2 normal (58-62), Days 3-7 overloaded (85-95).\n")
            f.write("Purpose: Test AI detection of accumulated unfairness.\n")
        
        elif "David" in driver.name:
            f.write("This driver represents an UNDERLOADED scenario.\n")
            f.write("Expected: Consistently easy routes (35-45 effort) all 7 days.\n")
            f.write("Purpose: Test identification of drivers with capacity.\n")
        
        elif "Priya" in driver.name:
            f.write("This driver represents a LEAVE/ABSENCE scenario.\n")
            f.write("Expected: 3 ABSENT days (availability=0.0), 4 active days.\n")
            f.write("Purpose: Ensure absences don't create false drift.\n")
            f.write("Key Check: Absent days should have normalized_effort = N/A.\n")
        
        elif "James" in driver.name:
            f.write("This driver represents a PART-TIME scenario.\n")
            f.write("Expected: All 7 days with HALF_SHIFT status (availability=0.5).\n")
            f.write("Purpose: Test per-shift fairness (raw effort ~60, normalized ~120).\n")
            f.write("Key Check: Normalized effort should be ~2x raw effort.\n")
        
        elif "Carlos" in driver.name:
            f.write("This driver represents a SICK DAYS scenario.\n")
            f.write("Expected: 2 SICK days (availability=0.5, protected), 5 active days.\n")
            f.write("Purpose: Verify reduced capacity handling.\n")
        
        f.write("\n\n")
    
    # Summary section
    f.write("="*80 + "\n")
    f.write("VALIDATION SUMMARY\n")
    f.write("="*80 + "\n\n")
    
    f.write("SCENARIO CHECKLIST:\n")
    f.write("-"*80 + "\n\n")
    
    f.write("✓ Scenario A (Balanced): 3 drivers (Sarah, Marcus, Aisha)\n")
    f.write("  Expected: ~60 normalized effort for all\n\n")
    
    f.write("✓ Scenario B (Overload): 1 driver (Elena)\n")
    f.write("  Expected: Normalized effort spikes on days 3-7 to 85-95\n\n")
    
    f.write("✓ Scenario C (Leave): 1 driver (Priya)\n")
    f.write("  Expected: 3 days with availability=0.0, normalized=N/A\n\n")
    
    f.write("✓ Scenario D (Part-Time): 1 driver (James)\n")
    f.write("  Expected: All days availability=0.5, normalized ~2x raw effort\n\n")
    
    f.write("✓ Scenario D (Underload): 1 driver (David)\n")
    f.write("  Expected: ~40 normalized effort (easy routes)\n\n")
    
    f.write("✓ Scenario E (Sick): 1 driver (Carlos)\n")
    f.write("  Expected: 2 days with availability=0.5 (sick), lower effort\n\n")
    
    f.write("\n" + "="*80 + "\n")
    f.write("END OF REPORT\n")
    f.write("="*80 + "\n")

db.close()

print(f"\n✅ Detailed report created: {report_file}\n")
print("This file contains:")
print("  - All 8 drivers")
print("  - 7 days of snapshots per driver")
print("  - Effort, Availability, Normalized Effort for each day")
print("  - Route assignments")
print("  - Scenario explanations")
print("\nYou can now manually verify all scenarios!\n")
