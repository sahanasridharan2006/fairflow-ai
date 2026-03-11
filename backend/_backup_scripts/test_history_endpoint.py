"""
Test Driver History page with validation drivers
Checks if the page loads correctly for drivers with data
"""

import requests

# Test credentials from validation drivers
test_drivers = [
    {"name": "Sarah Chen", "email": "sarah.chen@fairflow.test"},
    {"name": "Elena Rodriguez", "email": "elena.r@fairflow.test"},
    {"name": "James Williams", "email": "james.w@fairflow.test"},
]

print("\n" + "="*70)
print("TESTING DRIVER HISTORY ENDPOINT")
print("="*70 + "\n")

for driver in test_drivers:
    print(f"Testing {driver['name']}...")
    
    try:
        response = requests.get(
            f"http://localhost:8000/driver/history?user_email={driver['email']}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ SUCCESS - {len(data)} history records found")
            
            if data:
                latest = data[0]
                print(f"     Latest: {latest['date']} | Effort: {latest['daily_effort']:.1f} | Credits: {latest['credits_earned']:+.1f} | Balance: {latest['balance_snapshot']:+.1f}")
        else:
            print(f"  ❌ FAILED - Status {response.status_code}}")
            
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
    
    print()

print("="*70)
print("✅ Test complete - check if all drivers have history data")
print("="*70 + "\n")
