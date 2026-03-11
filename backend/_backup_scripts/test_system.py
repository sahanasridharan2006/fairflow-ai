import requests

print("=" * 60)
print("Testing FairFlow Real-Time Assignment System")
print("=" * 60)

base_url = "http://localhost:8000"

# Test 1: Assign Easy Route
print("\n1️⃣ Testing Easy Route Assignment...")
easy_payload = {
    "driver_id": 1,
    "route_factors": {
        "apartments": 1,
        "stairs": False,
        "heavy_boxes": 0,
        "traffic": False,
        "rain": False
    }
}

try:
    response = requests.post(f"{base_url}/admin/assign_route", json=easy_payload)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Effort Score: {data['effort_score']}")
        print(f"   ✅ Team Average: {data['team_average']}")
        print(f"   ✅ Credits: {data['credits']}")
        print(f"   ✅ New Balance: {data['new_balance']}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# Test 2: Get Driver Dashboard
print("\n2️⃣ Testing Driver Dashboard (driver_id=1)...")
try:
    response = requests.get(f"{base_url}/driver/1/dashboard")
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Driver: {data.get('name', 'N/A')}")
        print(f"   ✅ Status: {data.get('status', 'N/A')}")
        if data.get('stats'):
            print(f"   ✅ Effort Today: {data['stats']['effort_today']}")
            print(f"   ✅ Balance: {data['stats']['total_balance']}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# Test 3: Auto-Assign
print("\n3️⃣ Testing Auto-Assignment...")
try:
    response = requests.post(f"{base_url}/admin/auto_assign")
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Assigned to: {data.get('driver_assigned', 'N/A')}")
        print(f"   ✅ Reason: {data.get('reason', 'N/A')}")
        print(f"   ✅ Effort: {data.get('effort_score', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
