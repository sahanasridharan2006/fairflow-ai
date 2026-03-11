import logic
import routes_data

def test_effort_consistency():
    all_routes = routes_data.get_all_routes()
    print(f"{'Address ID':<10} | {'Expected (Top Box)':<20} | {'Calculated (Logic)':<20} | {'Status'}")
    print("-" * 70)
    
    for route in all_routes:
        expected = route['computed_effort']
        # Backend uses lowercase dictionary keys from RouteFactors schema
        calculated = logic.calculate_effort_score(route)
        status = "✅ MATCH" if expected == calculated else f"❌ MISMATCH (Diff: {calculated})"
        print(f"{route['address_id']:<10} | {expected:<20} | {calculated:<20} | {status}")

if __name__ == "__main__":
    test_effort_consistency()
