"""
Quick test of ML recommendation endpoint
"""
import requests
import json

# Test ML recommendation endpoint
url = "http://localhost:8000/admin/recommend_route"

payload = {
    "route_features": {
        "apartments_count": 10,
        "stairs_present": False,
        "heavy_boxes_count": 5,
        "traffic_level": "Normal",
        "weather_severity": "Clear"
    },
    "driver_id": 1
}

print("Testing ML Recommendation Endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
