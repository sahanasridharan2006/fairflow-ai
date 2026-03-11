
from typing import List, Dict

def classify_route_effort(route: Dict) -> Dict:
    """
    Classifies a route into Easy, Medium, or Hard based on logistical effort rules.
    
    Rules:
    - Base effort starts with distance (km * 2)
    - Apartment/Commercial area +10
    - Floors: Each floor +2
    - Stairs present: +15
    - Heavy packages: Each package +5
    - Traffic: Low: 0, Normal: 10, High: 25
    - Weather: Clear: 0, Rain: 15, Snow: 30
    
    Difficulty Mapping:
    - Easy: effort < 50
    - Medium: 50–75
    - Hard: > 75
    """
    effort = 0
    
    # Distance (Base)
    effort += route.get('distance_km', 0) * 2
    
    # Area Type
    area = route.get('area_type', 'Residential')
    if area in ['Apartment', 'Commercial']:
        effort += 10
    
    # Floors
    effort += route.get('floors', 1) * 2
    
    # Stairs
    if route.get('stairs_present', False):
        effort += 15
        
    # Heavy Packages
    effort += route.get('heavy_packages_count', 0) * 5
    
    # Traffic
    traffic_scores = {'Low': 0, 'Normal': 10, 'High': 25}
    effort += traffic_scores.get(route.get('traffic_level', 'Normal'), 10)
    
    # Weather
    weather_scores = {'Clear': 0, 'Rain': 15, 'Snow': 30}
    effort += weather_scores.get(route.get('weather_severity', 'Clear'), 0)
    
    # Classification
    if effort < 50:
        difficulty = "Easy"
    elif effort <= 75:
        difficulty = "Medium"
    else:
        difficulty = "Hard"
        
    route['computed_effort'] = effort
    route['difficulty_label'] = difficulty
    return route

# Mock Dataset: 6 Easy, 6 Medium, 4 Hard
MOCK_ROUTES = [
    # EASY ROUTES (Target: < 50)
    {"address_id": "ADDR_001", "address": "Door No. 12, 3rd Cross Street, Velachery, Chennai – 600042", "area_type": "Residential", "floors": 1, "stairs_present": False, "distance_km": 5, "heavy_packages_count": 0, "traffic_level": "Low", "weather_severity": "Clear"},
    {"address_id": "ADDR_002", "address": "H.No. 45, 2nd Main Road, BTM Layout 1st Stage, Bengaluru – 560029", "area_type": "Residential", "floors": 1, "stairs_present": False, "distance_km": 8, "heavy_packages_count": 0, "traffic_level": "Low", "weather_severity": "Clear"},
    {"address_id": "ADDR_003", "address": "Flat 101, Sai Nagar Main Road, Madipakkam, Chennai – 600091", "area_type": "Residential", "floors": 1, "stairs_present": False, "distance_km": 4, "heavy_packages_count": 0, "traffic_level": "Normal", "weather_severity": "Clear"},
    
    # MEDIUM ROUTES (Target: 50-75)
    {"address_id": "ADDR_101", "address": "Flat 504, Block C, Prestige Sunrise Apartments, Electronic City, Bengaluru – 560100", "area_type": "Apartment", "floors": 5, "stairs_present": False, "distance_km": 10, "heavy_packages_count": 0, "traffic_level": "Normal", "weather_severity": "Clear"},
    {"address_id": "ADDR_102", "address": "Flat 302, Lotus Heights, OMR Road, Sholinganallur, Chennai – 600119", "area_type": "Apartment", "floors": 3, "stairs_present": True, "distance_km": 8, "heavy_packages_count": 0, "traffic_level": "Normal", "weather_severity": "Clear"},
    {"address_id": "ADDR_103", "address": "Door No. 8/112, Gandhi Street, Chromepet, Chennai – 600044", "area_type": "Residential", "floors": 2, "stairs_present": False, "distance_km": 15, "heavy_packages_count": 4, "traffic_level": "Normal", "weather_severity": "Clear"},
    
    # HARD ROUTES (Target: > 75)
    {"address_id": "ADDR_201", "address": "Shop No. 12, Koyambedu Wholesale Market, Chennai – 600107", "area_type": "Commercial", "floors": 5, "stairs_present": True, "distance_km": 15, "heavy_packages_count": 10, "traffic_level": "High", "weather_severity": "Rain"},
    {"address_id": "ADDR_202", "address": "Warehouse Unit 5, Peenya Industrial Area Phase 2, Bengaluru – 560058", "area_type": "Commercial", "floors": 4, "stairs_present": True, "distance_km": 20, "heavy_packages_count": 12, "traffic_level": "High", "weather_severity": "Clear"}
]

# Process routes
CLASSIFIED_ROUTES = [classify_route_effort(r.copy()) for r in MOCK_ROUTES]

def get_all_routes():
    return CLASSIFIED_ROUTES
