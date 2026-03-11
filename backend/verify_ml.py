import requests
import json

url = "http://localhost:8000/admin/recommend_routes_batch"
payload = {
    "route_features": {
        "address": "123 Test St",
        "distance_km": 25,
        "stairs_present": True,
        "heavy_packages_count": 10,
        "traffic_level": "High",
        "weather_severity": "Clear"
    }
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    results = response.json()
    
    # Check if Underloaded drivers are ranked first for this "Hard" route
    print(f"{'Rank':<5} {'Name':<20} {'Balance':<10} {'State':<15} {'Label':<15}")
    print("-" * 65)
    for r in results:
        rank = r.get('preference_rank', 'N/A')
        name = r.get('driver_name', 'N/A')
        ctx = r.get('driver_context', {})
        balance = ctx.get('fairness_balance', 0)
        state = ctx.get('driver_state', 'N/A')
        label = r.get('preference_label', 'N/A')
        print(f"{rank:<5} {name:<20} {balance:<10} {state:<15} {label:<15}")

except Exception as e:
    print(f"Error: {e}")
