"""Simple test for driver history endpoint"""
import requests

try:
    print("\nTesting /driver/history endpoint...")
    r = requests.get('http://localhost:8000/driver/history?user_email=sarah.chen@fairflow.test')
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ SUCCESS - {len(data)} records found\n")
        
        for record in data[:3]:
            print(f"  {record['date']}: Effort={record['daily_effort']:.1f}, Credits={record['credits_earned']:+.1f}, Balance={record['balance_snapshot']:+.1f}")
    else:
        print(f"❌ Error: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"❌ Error: {e}")
