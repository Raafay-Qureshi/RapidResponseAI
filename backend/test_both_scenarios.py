"""
Test script to verify both fire scenarios work correctly
"""
import sys
import os

# Fix Unicode issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenarios.july_2020_fire import load_july_2020_scenario, is_july_2020_scenario, july_2020_scenario
from scenarios.march_2022_fire import load_march_2022_scenario, is_march_2022_scenario, march_2022_scenario

def test_july_2020_scenario():
    """Test July 2020 scenario loading and detection"""
    print("\n=== Testing July 2020 Scenario ===")
    
    # Test scenario validation
    assert july_2020_scenario.validate(), "July 2020 scenario validation failed"
    print("✓ July 2020 scenario validation passed")
    
    # Test scenario loading
    scenario_data = load_july_2020_scenario()
    assert scenario_data is not None, "Failed to load July 2020 scenario"
    assert 'disaster' in scenario_data, "Missing disaster data"
    assert 'weather' in scenario_data, "Missing weather data"
    assert 'fire_perimeter' in scenario_data, "Missing fire perimeter"
    print("✓ July 2020 scenario loaded successfully")
    
    # Test scenario detection
    test_data = {
        'metadata': {
            'scenario': 'july_2020_backtest',
            'description': 'July 2020 HWY 407/410 Fire'
        },
        'location': {
            'lat': 43.7315,
            'lon': -79.8620
        }
    }
    assert is_july_2020_scenario(test_data), "Failed to detect July 2020 scenario"
    print("✓ July 2020 scenario detection works")
    
    # Verify key data
    disaster = scenario_data['disaster']
    assert disaster['type'] == 'wildfire', "Wrong disaster type"
    assert disaster['subtype'] == 'WUI', "Wrong subtype"
    assert disaster['location']['lat'] == 43.7315, "Wrong latitude"
    print("✓ July 2020 scenario data is correct")
    
    print("✅ July 2020 scenario: ALL TESTS PASSED\n")

def test_march_2022_scenario():
    """Test March 2022 scenario loading and detection"""
    print("=== Testing March 2022 Scenario ===")
    
    # Test scenario validation
    assert march_2022_scenario.validate(), "March 2022 scenario validation failed"
    print("✓ March 2022 scenario validation passed")
    
    # Test scenario loading
    scenario_data = load_march_2022_scenario()
    assert scenario_data is not None, "Failed to load March 2022 scenario"
    assert 'disaster' in scenario_data, "Missing disaster data"
    assert 'weather' in scenario_data, "Missing weather data"
    assert 'fire_perimeter' in scenario_data, "Missing fire perimeter"
    print("✓ March 2022 scenario loaded successfully")
    
    # Test scenario detection
    test_data = {
        'metadata': {
            'scenario': 'march_2022_backtest',
            'description': 'March 2022 Conestoga Drive Fire'
        },
        'location': {
            'lat': 43.7091,
            'lon': -79.7358
        }
    }
    assert is_march_2022_scenario(test_data), "Failed to detect March 2022 scenario"
    print("✓ March 2022 scenario detection works")
    
    # Verify key data
    disaster = scenario_data['disaster']
    assert disaster['type'] == 'fire', "Wrong disaster type"
    assert disaster['subtype'] == 'residential', "Wrong subtype"
    assert disaster['location']['lat'] == 43.7091, "Wrong latitude"
    assert disaster['severity'] == 'critical', "Wrong severity"
    print("✓ March 2022 scenario data is correct")
    
    print("✅ March 2022 scenario: ALL TESTS PASSED\n")

def test_scenario_independence():
    """Test that both scenarios can coexist without conflicts"""
    print("=== Testing Scenario Independence ===")
    
    # Load both scenarios
    july_data = load_july_2020_scenario()
    march_data = load_march_2022_scenario()
    
    # Verify they have different locations
    july_loc = july_data['disaster']['location']
    march_loc = march_data['disaster']['location']
    
    assert july_loc['lat'] != march_loc['lat'], "Scenarios have same latitude"
    assert july_loc['lon'] != march_loc['lon'], "Scenarios have same longitude"
    print("✓ Scenarios have different locations")
    
    # Verify they have different characteristics
    assert july_data['disaster']['type'] != march_data['disaster']['type'], "Scenarios have same type"
    assert july_data['disaster']['subtype'] != march_data['disaster']['subtype'], "Scenarios have same subtype"
    print("✓ Scenarios have different characteristics")
    
    # Verify detection doesn't cross-contaminate
    july_trigger = {
        'metadata': {'scenario': 'july_2020_backtest'},
        'location': july_loc
    }
    march_trigger = {
        'metadata': {'scenario': 'march_2022_backtest'},
        'location': march_loc
    }
    
    assert is_july_2020_scenario(july_trigger) and not is_march_2022_scenario(july_trigger), \
        "July scenario detected as March"
    assert is_march_2022_scenario(march_trigger) and not is_july_2020_scenario(march_trigger), \
        "March scenario detected as July"
    print("✓ Scenario detection is independent")
    
    print("✅ Scenario independence: ALL TESTS PASSED\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing Both Fire Scenarios")
    print("="*60)
    
    try:
        test_july_2020_scenario()
        test_march_2022_scenario()
        test_scenario_independence()
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nBoth scenarios are ready for use:")
        print("  1. July 2020 HWY 407/410 Fire (WUI)")
        print("  2. March 2022 Conestoga Drive Fire (Residential)")
        print("\n")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())