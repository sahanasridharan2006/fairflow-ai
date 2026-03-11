import requests
import json

url = "http://localhost:8000/admin/assign_route"
payload = {
    "driver_id": 1,
    "route_factors": {
        "apartments": 6,
        "stairs": True,
        "heavy_boxes": 4,
        "traffic": True,
        "rain": True
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
