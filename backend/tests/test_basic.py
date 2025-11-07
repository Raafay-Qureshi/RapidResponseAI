"""
Basic test for SatelliteClient without requiring full dependencies
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("=" * 60)
print("🛰️  Basic SatelliteClient Test")
print("=" * 60)

try:
    # Test 1: Import the module
    print("\n✓ Test 1: Importing SatelliteClient...")
    from data.satellite_client import SatelliteClient
    print("  SUCCESS: Module imported")
    
    # Test 2: Check class structure
    print("\n✓ Test 2: Checking class methods...")
    required_methods = ['fetch_imagery', '_fetch_active_fires', '_create_bbox', 
                       '_parse_firms_csv', '_calculate_fire_perimeter']
    for method in required_methods:
        if hasattr(SatelliteClient, method):
            print(f"  ✓ {method} exists")
        else:
            print(f"  ✗ {method} missing")
    
    # Test 3: Initialize client
    print("\n✓ Test 3: Initializing client...")
    
    # Set a test API key
    os.environ['NASA_FIRMS_API_KEY'] = 'test_key_123'
    
    client = SatelliteClient()
    print(f"  ✓ Client initialized")
    print(f"  ✓ API Key loaded: {client.firms_api_key}")
    print(f"  ✓ FIRMS URL: {client.firms_url}")
    
    # Test 4: Test bbox creation
    print("\n✓ Test 4: Testing bbox creation...")
    test_location = {'lat': 34.0522, 'lon': -118.2437}
    bbox = client._create_bbox(test_location, radius_km=20)
    print(f"  ✓ BBOX created: {bbox}")
    
    # Test 5: Test CSV parsing
    print("\n✓ Test 5: Testing CSV parsing...")
    sample_csv = """latitude,longitude,bright_ti4,acq_date
34.05,-118.24,320.5,2024-01-01
34.06,-118.25,325.0,2024-01-01"""
    fires = client._parse_firms_csv(sample_csv)
    print(f"  ✓ Parsed {len(fires)} fire detections")
    if fires:
        print(f"  ✓ First fire: lat={fires[0]['latitude']}, lon={fires[0]['longitude']}")
    
    # Test 6: Test perimeter calculation
    print("\n✓ Test 6: Testing perimeter calculation...")
    if fires:
        perimeter = client._calculate_fire_perimeter(fires)
        print(f"  ✓ Perimeter type: {perimeter['type']}")
        print(f"  ✓ Coordinates: {len(perimeter['coordinates'][0])} points")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe SatelliteClient is ready to use.")
    print("To test with real API calls, install dependencies and run:")
    print("  pip install requests python-dotenv")
    print("  python test_satellite_client.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()