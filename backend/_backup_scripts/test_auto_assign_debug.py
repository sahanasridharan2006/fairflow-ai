import requests
import json

def test_auto_assign():
    url = "http://localhost:8000/admin/auto_assign"
    
    # Mock route features mimicking frontend
    payload = {
        "route_features": {
            "address": "123 Debug St",
            "distance_km": 12.0,
            "area_type": "Residential",
            "floors": 1,
            "stairs_present": False,
            "heavy_packages_count": 0,
            "traffic_level": "Normal",
            "weather_severity": "Clear"
        }
    }
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success:", json.dumps(response.json(), indent=2))
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_auto_assign()
