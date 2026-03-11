"""
AI Validation Environment Setup - Phase 1: Database Reset

Removes all mock/demo drivers and historical data while keeping schema intact.
Prepares clean slate for scenario-based validation.
"""

from database import SessionLocal, engine
import models
from sqlalchemy import text

def reset_validation_environment():
    """Reset database to clean state for AI validation"""
    
    print("\n" + "="*70)
    print("🔄 FAIRFLOW AI VALIDATION - ENVIRONMENT RESET")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Show current state
        user_count = db.query(models.User).count()
        snapshot_count = db.query(models.FairnessSnapshot).count()
        route_count = db.query(models.Route).count()
        
        print(f"📊 Current Database State:")
        print(f"   - Users: {user_count}")
        print(f"   - Fairness Snapshots: {snapshot_count}")
        print(f"   - Routes: {route_count}\n")
        
        # Confirm reset
        print("⚠️  This will DELETE all existing data (users, routes, snapshots)")
        print("   Database schema will remain intact.\n")
        
        # Delete all data
        print("🗑️  Deleting historical data...")
        
        # Delete in correct order (respect foreign keys)
        db.query(models.FairnessSnapshot).delete()
        print("   ✅ Fairness snapshots deleted")
        
        db.query(models.FairnessHistory).delete()
        print("   ✅ Fairness history deleted")
        
        db.query(models.Route).delete()
        print("   ✅ Routes deleted")
        
        db.query(models.DriverStats).delete()
        print("   ✅ Driver stats deleted")
        
        db.query(models.User).delete()
        print("   ✅ Users deleted")
        
        db.commit()
        
        # Verify clean state
        final_count = db.query(models.User).count()
        
        print(f"\n{'='*70}")
        print(f"✅ ENVIRONMENT RESET COMPLETE")
        print(f"{'='*70}")
        print(f"\n📊 Final State:")
        print(f"   - Users: {final_count}")
        print(f"   - Database: Clean slate ready for validation")
        print(f"   - Schema: Intact\n")
        
    except Exception as e:
        print(f"\n❌ Error during reset: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_validation_environment()
