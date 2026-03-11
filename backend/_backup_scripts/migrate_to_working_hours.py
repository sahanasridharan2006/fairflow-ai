"""
Migration script to convert availability_units to working_hours
Run this ONCE after adding working_hours column to schema
"""
from database import SessionLocal
import models

def migrate_availability_to_working_hours():
    """Convert existing availability_units data to working_hours"""
    db = SessionLocal()
    
    try:
        # Get all fairness snapshots
        snapshots = db.query(models.FairnessSnapshot).all()
        
        if not snapshots:
            print("ℹ️  No snapshots found. Database may be empty or newly created.")
            print("✅ Migration complete (nothing to migrate)")
            return
        
        print(f"Found {len(snapshots)} snapshots to migrate...")
        
        migrated = 0
        for snapshot in snapshots:
            # If working_hours already set, skip
            if hasattr(snapshot, 'working_hours') and snapshot.working_hours > 0:
                print(f"Skipping snapshot {snapshot.id} - already has working_hours={snapshot.working_hours}")
                continue
            
            # Convert availability to working hours
            # availability = 1.0 → 8 hours (full day)
            # availability = 0.5 → 4 hours (half day)
            # availability = 0.0 → 0 hours (absent)
            if hasattr(snapshot, 'availability_units') and snapshot.availability_units is not None:
                snapshot.working_hours = snapshot.availability_units * 8.0
            else:
                # Default to 8 hours full day
                snapshot.working_hours = 8.0
            
            # Recalculate normalized effort
            if snapshot.working_hours > 0:
                snapshot.normalized_effort = snapshot.effort / snapshot.working_hours
            else:
                snapshot.normalized_effort = None  # Exclude from fairness calculations
            
            migrated += 1
            
            if migrated % 100 == 0:
                print(f"Migrated {migrated}/{len(snapshots)}...")
        
        db.commit()
        print(f"✅ Successfully migrated {migrated} snapshots")
        print(f"✅ All normalized_effort values recalculated using working_hours")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("FairFlow: Availability → Working Hours Migration")
    print("=" * 60)
    migrate_availability_to_working_hours()
