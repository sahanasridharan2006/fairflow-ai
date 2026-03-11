"""
Database Migration Script for Availability-Aware Fairness

Adds availability_units and normalized_effort columns to fairness_snapshots table
and backfills existing data.
"""

from database import engine, SessionLocal
from sqlalchemy import text, inspect
import models

def check_columns_exist():
    """Check if new columns already exist"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('fairness_snapshots')]
    
    has_availability = 'availability_units' in columns
    has_normalized = 'normalized_effort' in columns
    
    return has_availability, has_normalized

def migrate_database():
    """Add new columns and backfill existing data"""
    
    print("\n" + "="*60)
    print("AVAILABILITY-AWARE FAIRNESS MIGRATION")
    print("="*60 + "\n")
    
    # Check if migration needed
    has_availability, has_normalized = check_columns_exist()
    
    if has_availability and has_normalized:
        print("✅ Migration already completed!")
        print("   - availability_units column exists")
        print("   - normalized_effort column exists\n")
        return
    
    print("🔄 Starting database migration...\n")
    
    try:
        with engine.begin() as conn:
            # Add availability_units column if missing
            if not has_availability:
                print("📝 Adding availability_units column...")
                conn.execute(text(
                    "ALTER TABLE fairness_snapshots ADD COLUMN availability_units FLOAT DEFAULT 1.0"
                ))
                print("   ✅ availability_units column added\n")
            
            # Add normalized_effort column if missing
            if not has_normalized:
                print("📝 Adding normalized_effort column...")
                conn.execute(text(
                    "ALTER TABLE fairness_snapshots ADD COLUMN normalized_effort FLOAT"
                ))
                print("   ✅ normalized_effort column added\n")
            
            # Backfill normalized_effort for existing records
            print("📝 Backfilling normalized_effort for existing snapshots...")
            result = conn.execute(text("""
                UPDATE fairness_snapshots 
                SET normalized_effort = effort / NULLIF(availability_units, 0)
                WHERE normalized_effort IS NULL AND availability_units > 0
            """))
            print(f"   ✅ Updated {result.rowcount} existing snapshots\n")
        
        print("="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
        # Show sample of migrated data
        db = SessionLocal()
        sample_snapshots = db.query(models.FairnessSnapshot).limit(3).all()
        
        if sample_snapshots:
            print("📊 Sample of migrated data:")
            for snapshot in sample_snapshots:
                print(f"   - Driver {snapshot.driver_id}: effort={snapshot.effort}, "
                      f"availability={snapshot.availability_units}, "
                      f"normalized={snapshot.normalized_effort}")
        
        db.close()
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}\n")
        raise

if __name__ == "__main__":
    migrate_database()
