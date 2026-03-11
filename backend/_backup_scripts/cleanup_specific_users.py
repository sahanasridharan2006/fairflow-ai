from database import SessionLocal
import models

def cleanup_users():
    db = SessionLocal()
    
    # Emails to remove
    emails_to_remove = [
        "ridu@test.com"
    ]
    
    print("\n" + "="*60)
    print("CLEANING UP SPECIFIC USERS")
    print("="*60 + "\n")
    
    deleted_count = 0
    
    for email in emails_to_remove:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            print(f"🗑️ Deleting user: {user.name} ({user.email}) - ID: {user.id}")
            
            # Delete related stats first
            db.query(models.DriverStats).filter(models.DriverStats.user_id == user.id).delete()
            db.query(models.FairnessHistory).filter(models.FairnessHistory.driver_id == user.id).delete()
            db.query(models.Route).filter(models.Route.driver_id == user.id).delete()
            db.query(models.FairnessSnapshot).filter(models.FairnessSnapshot.driver_id == user.id).delete()
            
            # Delete user
            db.delete(user)
            deleted_count += 1
        else:
            print(f"⚠️ User not found: {email}")
            
    db.commit()
    
    print(f"\n✅ Deleted {deleted_count} users.")
    
    # Verify remaining
    print("\nREMAINING USERS:")
    print("-" * 60)
    users = db.query(models.User).all()
    for u in users:
        print(f"   {u.id}: {u.name} ({u.email})")
    
    print("="*60 + "\n")
    db.close()

if __name__ == "__main__":
    cleanup_users()
