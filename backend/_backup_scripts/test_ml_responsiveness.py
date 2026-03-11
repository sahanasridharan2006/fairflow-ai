import requests
import time
import json

def test_responsiveness():
    url = "http://localhost:8000/admin/recommend_routes_batch"
    
    # Mock route features
    payload = {
        "route_features": {
            "address_id": 1,
            "address": "123 Test St",
            "area_type": "Apartment",
            "floors": 3,
            "stairs_present": True,
            "heavy_packages_count": 2,
            "traffic_level": "Normal",
            "weather_severity": "Clear",
            "distance_km": 5.0
        }
    }
    
    print(f"Testing {url}...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.4f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Received {len(data)} suggestions.")
            if len(data) > 0:
                print("Sample suggestion:", json.dumps(data[0], indent=2))
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_responsiveness()
