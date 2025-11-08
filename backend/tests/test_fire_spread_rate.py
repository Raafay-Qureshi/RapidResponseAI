import json
import os
import sys
from unittest import TestCase

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.prediction_helpers import _calculate_fire_spread_rate


class TestFireSpreadRate(TestCase):
    """Test cases for _calculate_fire_spread_rate function."""

    def setUp(self):
        """Load sample weather data for testing."""
        sample_data_path = os.path.join(
            os.path.dirname(__file__),
            'sample_data',
            'sample_weather_current_toronto_canada.json'
        )
        with open(sample_data_path, 'r') as f:
            self.sample_weather = json.load(f)

    def test_calculate_fire_spread_rate_with_sample_data(self):
        """Test fire spread rate calculation with Toronto sample weather data."""
        spread_rate, factors = _calculate_fire_spread_rate(self.sample_weather)

        # Verify return types
        self.assertIsInstance(spread_rate, float)
        self.assertIsInstance(factors, dict)

        # Verify factors dictionary structure
        expected_keys = {'wind_speed_kmh', 'wind_direction_deg', 'temperature_c', 'humidity_percent'}
        self.assertEqual(set(factors.keys()), expected_keys)

        # Verify reasonable ranges for Toronto weather
        self.assertGreater(spread_rate, 0)
        self.assertLess(spread_rate, 20)  # Should be reasonable

        # Verify wind speed conversion (m/s to km/h)
        wind_ms = self.sample_weather['wind']['speed']
        expected_wind_kmh = wind_ms * 3.6
        self.assertAlmostEqual(factors['wind_speed_kmh'], expected_wind_kmh, places=2)

        # Verify other factors match sample data
        self.assertEqual(factors['wind_direction_deg'], self.sample_weather['wind']['deg'])
        self.assertEqual(factors['temperature_c'], self.sample_weather['main']['temp'])
        self.assertEqual(factors['humidity_percent'], self.sample_weather['main']['humidity'])

    def test_calculate_fire_spread_rate_high_wind_low_humidity(self):
        """Test with high wind and low humidity (fast spread conditions)."""
        weather = {
            'wind': {'speed': 10, 'deg': 180},  # 36 km/h wind
            'main': {'temp': 30, 'humidity': 20}  # Hot, dry
        }

        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # Should result in higher spread rate due to wind and low humidity
        self.assertGreater(spread_rate, 4.0)  # Higher than base rate

        # Verify factors
        self.assertAlmostEqual(factors['wind_speed_kmh'], 36.0)
        self.assertEqual(factors['wind_direction_deg'], 180)
        self.assertEqual(factors['temperature_c'], 30)
        self.assertEqual(factors['humidity_percent'], 20)

    def test_calculate_fire_spread_rate_low_wind_high_humidity(self):
        """Test with low wind and high humidity (slow spread conditions)."""
        weather = {
            'wind': {'speed': 1, 'deg': 0},  # 3.6 km/h wind
            'main': {'temp': 15, 'humidity': 80}  # Cool, humid
        }

        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # Should result in lower spread rate due to low wind and high humidity
        self.assertLess(spread_rate, 2.5)  # Lower than base rate

        # Verify factors
        self.assertAlmostEqual(factors['wind_speed_kmh'], 3.6)
        self.assertEqual(factors['wind_direction_deg'], 0)
        self.assertEqual(factors['temperature_c'], 15)
        self.assertEqual(factors['humidity_percent'], 80)

    def test_calculate_fire_spread_rate_default_values(self):
        """Test with empty weather dict (should use defaults)."""
        weather = {}

        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # Should use default values - calculate expected rate
        # wind_speed = 10 m/s = 36 km/h
        # wind_factor = 1 + (36/50) = 1.72
        # temp_factor = 1 + ((20-20)/40) = 1.0
        # humidity_factor = 1.5 - (50/100) = 1.0
        # expected = 2.0 * 1.72 * 1.0 * 1.0 = 3.44
        self.assertAlmostEqual(spread_rate, 3.44, places=2)

        # Verify default factors
        self.assertAlmostEqual(factors['wind_speed_kmh'], 36.0)  # 10 m/s * 3.6
        self.assertEqual(factors['wind_direction_deg'], 0)
        self.assertEqual(factors['temperature_c'], 20)
        self.assertEqual(factors['humidity_percent'], 50)

    def test_calculate_fire_spread_rate_extreme_values(self):
        """Test with extreme weather values (bounds testing)."""
        weather = {
            'wind': {'speed': 50, 'deg': 90},  # Very high wind
            'main': {'temp': 50, 'humidity': 0}  # Very hot, dry
        }

        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # Should still be reasonable (factors are clamped)
        self.assertGreater(spread_rate, 0)
        self.assertLess(spread_rate, 50)  # Not excessively high

        # Verify factors are clamped appropriately
        self.assertAlmostEqual(factors['wind_speed_kmh'], 180.0)  # 50 m/s * 3.6
        self.assertEqual(factors['wind_direction_deg'], 90)
        self.assertEqual(factors['temperature_c'], 50)
        self.assertEqual(factors['humidity_percent'], 0)

    def test_calculate_fire_spread_rate_formula_validation(self):
        """Test that the formula is calculated correctly."""
        # Use known values to validate formula
        weather = {
            'wind': {'speed': 5, 'deg': 45},    # 18 km/h wind
            'main': {'temp': 25, 'humidity': 40} # Warm, moderate humidity
        }

        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # Manual calculation for validation
        base_rate = 2.0
        wind_factor = 1 + (18 / 50)  # 1 + 0.36 = 1.36
        temp_factor = 1 + ((25 - 20) / 40)  # 1 + 0.125 = 1.125
        humidity_factor = 1.5 - (40 / 100)  # 1.5 - 0.4 = 1.1

        expected_rate = base_rate * wind_factor * temp_factor * humidity_factor
        expected_rate = max(0.1, expected_rate)  # Apply min bounds

        self.assertAlmostEqual(spread_rate, expected_rate, places=5)


if __name__ == '__main__':
    import unittest
    unittest.main()