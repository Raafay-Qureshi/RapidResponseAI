"""
Test script for July 2020 scenario configuration
"""

import sys
import os

# Add parent directory to path so we can import the scenarios module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scenarios.july_2020_fire import july_2020_scenario, load_july_2020_scenario, is_july_2020_scenario


def test_scenario_validation():
    """Test that scenario validation passes"""
    print("Testing scenario validation...")
    assert july_2020_scenario.validate()
    print("[OK] Validation passed")


def test_configuration_loading():
    """Test that configuration loads successfully"""
    print("\nTesting configuration loading...")
    config = load_july_2020_scenario()
    print("[OK] Configuration loaded")
    return config


def test_configuration_structure(config):
    """Test that configuration has all required fields"""
    print("\nTesting configuration structure...")

    # Check top-level keys
    assert 'disaster' in config
    assert 'weather' in config
    assert 'fire_perimeter' in config
    assert 'population_estimate' in config
    assert 'infrastructure' in config
    assert 'historical_comparison' in config
    print("[OK] All top-level keys present")

    # Check disaster config
    disaster = config['disaster']
    assert disaster['scenario_id'] == 'july_2020_backtest'
    assert disaster['type'] == 'wildfire'
    assert disaster['location']['lat'] == 43.7315
    assert disaster['location']['lon'] == -79.8620
    print("[OK] Disaster configuration valid")

    # Check weather config
    weather = config['weather']
    assert weather['temperature_c'] == 32
    assert weather['humidity_percent'] == 18
    assert weather['wind_speed_kmh'] == 25
    print("[OK] Weather configuration valid")

    # Check fire perimeter
    perimeter = config['fire_perimeter']
    assert perimeter['type'] == 'Feature'
    assert perimeter['properties']['size_acres'] == 40
    print("[OK] Fire perimeter valid")


def test_scenario_detection():
    """Test that scenario detection function works"""
    print("\nTesting scenario detection...")

    # Test with scenario ID
    test_data_1 = {
        'metadata': {
            'scenario': 'july_2020_backtest'
        }
    }
    assert is_july_2020_scenario(test_data_1)
    print("[OK] Detects scenario by ID")

    # Test with description
    test_data_2 = {
        'metadata': {
            'description': 'This is the July 2020 fire scenario'
        }
    }
    assert is_july_2020_scenario(test_data_2)
    print("[OK] Detects scenario by description")

    # Test with coordinates
    test_data_3 = {
        'location': {
            'lat': 43.7315,
            'lon': -79.8620
        },
        'metadata': {}
    }
    assert is_july_2020_scenario(test_data_3)
    print("[OK] Detects scenario by coordinates")

    # Test negative case
    test_data_4 = {
        'location': {
            'lat': 43.6,
            'lon': -79.7
        },
        'metadata': {}
    }
    assert not is_july_2020_scenario(test_data_4)
    print("[OK] Correctly rejects non-matching scenario")


def print_configuration_summary(config):
    """Print a summary of the configuration"""
    print("\n" + "="*60)
    print("JULY 2020 SCENARIO CONFIGURATION SUMMARY")
    print("="*60)

    disaster = config['disaster']
    print(f"\nScenario: {disaster['name']}")
    print(f"ID: {disaster['scenario_id']}")
    print(f"Type: {disaster['type']} ({disaster['subtype']})")

    print(f"\nLocation:")
    print(f"  Coordinates: {disaster['location']['lat']}, {disaster['location']['lon']}")
    print(f"  Description: {disaster['location']['description']}")
    print(f"  Address: {disaster['location']['address']}")

    print(f"\nFire Parameters:")
    fire_params = disaster['fire_params']
    print(f"  Size: {fire_params['initial_size_acres']} acres ({fire_params['initial_size_km2']} km²)")
    print(f"  Type: {fire_params['fire_type']}")
    print(f"  Fuel: {fire_params['fuel_type']}")
    print(f"  Spread Multiplier: {fire_params['spread_rate_multiplier']}x")

    print(f"\nWeather Conditions:")
    weather = config['weather']
    print(f"  Temperature: {weather['temperature_c']}°C")
    print(f"  Humidity: {weather['humidity_percent']}%")
    print(f"  Wind: {weather['wind_speed_kmh']} km/h from {weather['wind_direction_deg']}°")
    print(f"  Fire Weather Index: {weather['fire_weather_index']}")

    print(f"\nPopulation Impact:")
    pop = config['population_estimate']
    print(f"  Total Affected: ~{pop['total_affected']}")
    print(f"  Immediate Danger: {pop['immediate_danger']}")
    print(f"  Evacuation Recommended: {pop['evacuation_recommended']}")
    print(f"  Vulnerable (Elderly): {pop['vulnerable_elderly']}")
    print(f"  Vulnerable (Children): {pop['vulnerable_children']}")

    print(f"\nInfrastructure at Risk:")
    infra = config['infrastructure']
    print(f"  HWY 407: {infra['highway_407']['daily_traffic']:,} vehicles/day")
    print(f"  HWY 410: {infra['highway_410']['daily_traffic']:,} vehicles/day")

    print(f"\nHistorical Response:")
    historical = config['historical_comparison']
    print(f"  First 911 Call: {historical['first_911_call_time']}")
    print(f"  Response Time: {historical['response_time_minutes']} minutes")
    print(f"  Units: {historical['units_dispatched']}")
    print(f"  Mutual Aid: {historical['mutual_aid']}")
    print(f"  Casualties: {historical['casualties']}")

    print("\n" + "="*60)


def main():
    """Run all tests"""
    print("="*60)
    print("JULY 2020 SCENARIO CONFIGURATION TESTS")
    print("="*60)

    try:
        # Run tests
        test_scenario_validation()
        config = test_configuration_loading()
        test_configuration_structure(config)
        test_scenario_detection()

        # Print summary
        print_configuration_summary(config)

        # Final result
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*60)
        print("\nThe July 2020 scenario is ready for use.")
        print("Frontend can trigger it with metadata.scenario = 'july_2020_backtest'")
        print("="*60 + "\n")

        return 0

    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
