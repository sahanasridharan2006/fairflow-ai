"""
Create a test user through the signup flow
This mimics a real signup to test the system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_drivers():
    """Create multiple test driver accounts"""
    drivers = [
        {"name": "Ridu", "email": "ridu@test.com"},
        {"name": "Sajin", "email": "sajin@test.com"},
        {"name": "Mohan", "email": "mohan@test.com"},
        {"name": "Priya", "email": "priya@test.com"},
        {"name": "Anita", "email": "anita@test.com"}
    ]
    
    results = []
    for d in drivers:
        print(f"🚗 Creating test driver: {d['name']}...")
        signup_data = {
            "name": d["name"],
            "email": d["email"],
            "password": "test123"
        }
        try:
            response = requests.post(
                f"{BASE_URL}/signup/driver",
                json=signup_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Driver created: {d['email']}")
                results.append(response.json())
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    return results

if __name__ == "__main__":
    print("=" * 50)
    print("Creating test drivers via signup endpoints")
    print("=" * 50)
    
    create_test_drivers()
    print("\n✅ Database is ready with test drivers!")
