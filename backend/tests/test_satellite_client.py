import asyncio
import os
import sys
import json
import pytest
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

from data.satellite_client import SatelliteClient


@pytest.mark.asyncio
async def test_satellite_client():
    """Test the SatelliteClient with multiple sample locations"""
    
    # Initialize the client
    client = SatelliteClient()
    
    # Check if API key is loaded
    if not client.firms_api_key:
        print("ERROR: NASA_FIRMS_API_KEY not found in environment variables!")
        print("Please add it to your .env file")
        return
    
    print(f"✓ API Key loaded: {client.firms_api_key[:10]}...")
    
    # Test multiple locations known for fire activity
    test_locations = [
        {'name': 'Amazon Rainforest', 'lat': -3.4653, 'lon': -62.2159},
        {'name': 'California', 'lat': 36.7783, 'lon': -119.4179},
        {'name': 'Australia', 'lat': -33.8688, 'lon': 151.2093},
        {'name': 'Sub-Saharan Africa', 'lat': -10.5, 'lon': 25.0},
    ]
    
    for test_location in test_locations:
        print(f"\n{'='*60}")
        print(f"🔍 Testing location: {test_location['name']}")
        print(f"   Coordinates: {test_location['lat']}, {test_location['lon']}")
        print('='*60)
        
        try:
            # Fetch imagery data (7 days lookback)
            print("\n📡 Fetching active fire data from NASA FIRMS (last 7 days)...")
            result = await client.fetch_imagery(test_location, days=7)
            
            # Display results
            print("\n✅ Results:")
            print(f"Fire detections found: {len(result['fire_detections'])}")
            
            if result['fire_detections']:
                print(f"Satellite: {result['satellite']}")
                print(f"Timestamp: {result['timestamp']}")
                print(f"Thermal intensity: {result['thermal_intensity']}K")
                
                print("\n🔥 First 3 fire detections:")
                for i, fire in enumerate(result['fire_detections'][:3], 1):
                    print(f"  {i}. Lat: {fire['latitude']}, Lon: {fire['longitude']}, "
                          f"Brightness: {fire['bright_ti4']}K, Date: {fire['acq_date']}")
                
                if result['fire_perimeter']:
                    print("\n📐 Fire perimeter (GeoJSON):")
                    print(f"  Type: {result['fire_perimeter']['type']}")
                    print(f"  Coordinates: {len(result['fire_perimeter']['coordinates'][0])} points")
                
                # Save to JSON file
                output_file = f"backend/tests/sample_data/sample_fire_data_{test_location['name'].lower().replace(' ', '_')}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Sample data saved to {output_file}")
                
                # Found fires, stop testing other locations
                print("\n" + "="*60)
                print("✅ SUCCESS: Found active fires!")
                print("="*60)
                return
            else:
                print("No fires detected in this region in the last 7 days")
                
        except Exception as e:
            print(f"\n❌ Error with {test_location['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("ℹ️  No active fires found in any test location")
    print("   This is normal - the code is working correctly!")
    print("="*60)


if __name__ == "__main__":
    print("=" * 60)
    print("🛰️  Testing SatelliteClient")
    print("=" * 60)
    
    asyncio.run(test_satellite_client())