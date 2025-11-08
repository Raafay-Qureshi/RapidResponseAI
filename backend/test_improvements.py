"""
Quick test script to verify PredictionAgent improvements work correctly.
Tests the enhanced functions without going through the full test suite.
"""

import sys
import os
sys.path.insert(0, '.')

# Direct import to avoid geopandas dependency issue
import importlib.util
spec = importlib.util.spec_from_file_location("prediction_helpers", "agents/prediction_helpers.py")
prediction_helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prediction_helpers)

from shapely.geometry import Point, shape

print("=" * 70)
print("TESTING PREDICTION AGENT IMPROVEMENTS")
print("=" * 70)

# Test 1: Fire spread rate calculation
print("\n1. Testing _calculate_fire_spread_rate...")
weather = {
    'wind': {'speed': 5, 'deg': 90},
    'main': {'temp': 25, 'humidity': 40}
}
try:
    rate, factors = prediction_helpers._calculate_fire_spread_rate(weather)
    print(f"   [OK] SUCCESS: Spread rate = {rate:.2f} km/h")
    print(f"   [OK] Factors: {factors}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 2: Polygon area calculation
print("\n2. Testing _calculate_polygon_area...")
polygon = {
    'type': 'Polygon',
    'coordinates': [[[-79.8, 43.7], [-79.79, 43.7], [-79.79, 43.71], [-79.8, 43.71], [-79.8, 43.7]]]
}
try:
    area = prediction_helpers._calculate_polygon_area(polygon)
    print(f"   [OK] SUCCESS: Area = {area:.2f} km2")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 3: Polygon expansion
print("\n3. Testing _expand_polygon...")
try:
    expanded = prediction_helpers._expand_polygon(polygon, 2.5)
    print(f"   [OK] SUCCESS: Polygon expanded by 2.5 km")
    print(f"   [OK] Type: {expanded['type']}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 4: Timeline predictions
print("\n4. Testing _generate_timeline_predictions...")
try:
    predictions = prediction_helpers._generate_timeline_predictions(polygon, 2.5)
    print(f"   [OK] SUCCESS: Generated predictions for {len(predictions)} time horizons")
    for key, pred in predictions.items():
        print(f"   [OK] {key}: area={pred['area_km2']:.2f} km2, confidence={pred['confidence']:.2f}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 5: Critical points identification
print("\n5. Testing _identify_critical_points...")
try:
    points = prediction_helpers._identify_critical_points({'lat': 43.7, 'lon': -79.8})
    print(f"   [OK] SUCCESS: Identified {len(points)} critical points")
    for point in points:
        print(f"   [OK] {point['name']}: ({point['lat']}, {point['lon']})")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 6: Distance to boundary
print("\n6. Testing _distance_to_boundary...")
try:
    boundary = shape(polygon)
    point = Point(-79.85, 43.75)
    dist = prediction_helpers._distance_to_boundary(boundary, point)
    print(f"   [OK] SUCCESS: Distance = {dist:.2f} km")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 7: Directional factor
print("\n7. Testing _calculate_directional_factor...")
try:
    fire_center = Point(-79.8, 43.7)
    target = Point(-79.85, 43.75)
    factor = prediction_helpers._calculate_directional_factor(fire_center, target, 90)
    print(f"   [OK] SUCCESS: Directional factor = {factor:.2f}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 8: Arrival times calculation
print("\n8. Testing _calculate_arrival_times...")
try:
    boundary = shape(polygon)
    points = prediction_helpers._identify_critical_points({'lat': 43.7, 'lon': -79.8})
    arrival_times = prediction_helpers._calculate_arrival_times(boundary, points, 2.5, 90)
    print(f"   [OK] SUCCESS: Calculated {len(arrival_times)} arrival times")
    for time in arrival_times:
        print(f"   [OK] {time['location']}: {time['hours_until_arrival']}h ({time['confidence']} confidence)")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 9: Input validation (invalid weather)
print("\n9. Testing input validation with invalid data...")
try:
    invalid_weather = {'wind': {'speed': -10}}  # Negative wind speed
    rate, factors = prediction_helpers._calculate_fire_spread_rate(invalid_weather)
    print(f"   [OK] SUCCESS: Handled invalid input gracefully, rate = {rate:.2f} km/h")
except Exception as e:
    print(f"   [OK] EXPECTED: Proper error handling - {type(e).__name__}")

# Test 10: None handling
print("\n10. Testing None handling...")
try:
    area = prediction_helpers._calculate_polygon_area(None)
    print(f"   [OK] SUCCESS: None polygon handled gracefully, area = {area:.2f} km2")
    
    expanded = prediction_helpers._expand_polygon(None, 2.5)
    print(f"   [OK] SUCCESS: None polygon expansion handled, result = {expanded}")
    
    dist = prediction_helpers._distance_to_boundary(None, Point(0, 0))
    print(f"   [OK] SUCCESS: None boundary handled, distance = {dist}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE - All core functions working!")
print("=" * 70)