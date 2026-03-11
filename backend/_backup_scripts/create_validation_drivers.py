"""
AI Validation Environment Setup - Phase 2: Realistic Driver Signups

Creates 8 realistic driver profiles for scenario-based validation testing.
Each driver has unique email, secure password, and specific role in validation scenarios.
"""

from database import SessionLocal
import models
import auth

# Realistic driver profiles for validation scenarios
VALIDATION_DRIVERS = [
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@fairflow.test",
        "password": "SafePass2024!",
        "role_in_validation": "balanced",  # Normal workload
        "description": "Full-time driver, balanced workload"
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.j@fairflow.test",
        "password": "MarcusSecure99",
        "role_in_validation": "balanced",  # Normal workload
        "description": "Full-time driver, balanced workload"
    },
    {
        "name": "Elena Rodriguez",
        "email": "elena.r@fairflow.test",
        "password": "Elena#Strong88",
        "role_in_validation": "overloaded",  # Will receive hard routes consistently
        "description": "Worker who will be systematically overloaded"
    },
    {
        "name": "David Park",
        "email": "david.park@fairflow.test",
        "password": "DavidSecure77!",
        "role_in_validation": "underloaded",  # Will receive easy routes
        "description": "Worker with lighter workload"
    },
    {
        "name": "Priya Sharma",
        "email": "priya.s@fairflow.test",
        "password": "PriyaSafe2024",
        "role_in_validation": "leave",  # Will take leave days
        "description": "Driver with planned absences (leave scenario)"
    },
    {
        "name": "James Williams",
        "email": "james.w@fairflow.test",
        "password": "JamesPass#66",
        "role_in_validation": "part_time",  # Part-time worker
        "description": "Part-time driver (half shifts)"
    },
    {
        "name": "Aisha Mohammed",
        "email": "aisha.m@fairflow.test",
        "password": "AishaSafe55!",
        "role_in_validation": "balanced",  # Normal workload
        "description": "Full-time driver, balanced workload"
    },
    {
        "name": "Carlos Santos",
        "email": "carlos.s@fairflow.test",
        "password": "CarlosStrong44",
        "role_in_validation": "sick",  # Will have sick days
        "description": "Driver with sick days (reduced capacity scenario)"
    }
]

def create_validation_drivers():
    """Create 8 realistic drivers for AI validation testing"""
    
    print("\n" + "="*70)
    print("👥 FAIRFLOW AI VALIDATION - DRIVER SIGNUP")
    print("="*70 + "\n")
    
    db = SessionLocal()
    created_drivers = []
    
    try:
        print(f"Creating {len(VALIDATION_DRIVERS)} realistic driver profiles...\n")
        
        for i, driver_data in enumerate(VALIDATION_DRIVERS, 1):
            # Create user
            user = models.User(
                name=driver_data["name"],
                email=driver_data["email"],
                hashed_password=auth.get_password_hash(driver_data["password"]),
                role="driver",
                status="ACTIVE"
            )
            db.add(user)
            db.flush()  # Get user ID
            
            # Create driver stats
            stats = models.DriverStats(
                user_id=user.id,
                effort_today=0.0,
                credits_today=0.0,
                total_balance=0.0
            )
            db.add(stats)
            
            created_drivers.append({
                "id": user.id,
                "name": driver_data["name"],
                "email": driver_data["email"],
                "password": driver_data["password"],
                "role_in_validation": driver_data["role_in_validation"],
                "description": driver_data["description"]
            })
            
            print(f"✅ {i}. {driver_data['name']}")
            print(f"   Email: {driver_data['email']}")
            print(f"   Role: {driver_data['role_in_validation']}")
            print(f"   Description: {driver_data['description']}\n")
        
        db.commit()
        
        print("="*70)
        print(f"✅ ALL {len(created_drivers)} DRIVERS CREATED SUCCESSFULLY")
        print("="*70 + "\n")
        
        # Create admin user
        print("👤 Creating admin user...\n")
        admin = models.User(
            name="Admin Validator",
            email="admin@fairflow.test",
            hashed_password=auth.get_password_hash("AdminSecure2024!"),
            role="admin",
            status="ACTIVE"
        )
        db.add(admin)
        db.commit()
        
        print("✅ Admin created:")
        print("   Email: admin@fairflow.test")
        print("   Password: AdminSecure2024!\n")
        
        # Save credentials to file
        save_credentials(created_drivers)
        
        return created_drivers
        
    except Exception as e:
        print(f"\n❌ Error creating drivers: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def save_credentials(drivers):
    """Save driver credentials to file for future reference"""
    
    credentials_file = "validation_driver_credentials.txt"
    
    with open(credentials_file, "w") as f:
        f.write("="*70 + "\n")
        f.write("FAIRFLOW AI VALIDATION - DRIVER CREDENTIALS\n")
        f.write("="*70 + "\n\n")
        
        f.write("ADMIN CREDENTIALS:\n")
        f.write("-" * 70 + "\n")
        f.write("Name: Admin Validator\n")
        f.write("Email: admin@fairflow.test\n")
        f.write("Password: AdminSecure2024!\n\n")
        
        f.write("DRIVER CREDENTIALS:\n")
        f.write("-" * 70 + "\n\n")
        
        for i, driver in enumerate(drivers, 1):
            f.write(f"{i}. {driver['name']}\n")
            f.write(f"   Email: {driver['email']}\n")
            f.write(f"   Password: {driver['password']}\n")
            f.write(f"   Validation Role: {driver['role_in_validation']}\n")
            f.write(f"   Description: {driver['description']}\n\n")
        
        f.write("="*70 + "\n")
        f.write(f"Total Drivers: {len(drivers)}\n")
        f.write("="*70 + "\n")
    
    print(f"📄 Credentials saved to: {credentials_file}\n")

if __name__ == "__main__":
    drivers = create_validation_drivers()
    
    print("\n" + "🎯 "*35)
    print("READY FOR 7-DAY HISTORICAL DATA GENERATION")
    print("🎯 "*35 + "\n")
