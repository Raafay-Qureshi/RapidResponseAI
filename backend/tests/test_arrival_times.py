import json
import os
import sys
from unittest import TestCase

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.prediction_helpers import _calculate_arrival_times, _identify_critical_points, _distance_to_boundary, _calculate_directional_factor
from shapely.geometry import shape, Point


class TestArrivalTimes(TestCase):
    """Test cases for arrival time calculation functions."""

    def setUp(self):
        """Set up test data."""
        # Sample polygon representing a small fire area
        self.sample_polygon = {
            'type': 'Polygon',
            'coordinates': [[[-79.8, 43.7], [-79.79, 43.7], [-79.79, 43.71], [-79.8, 43.71], [-79.8, 43.7]]]
        }
        self.sample_geom = shape(self.sample_polygon)
        self.spread_rate = 2.5  # km/h
        self.wind_dir = 90  # degrees

    def test_distance_to_boundary_with_sample_data(self):
        """Test distance calculation with sample data."""
        print("Running test_distance_to_boundary_with_sample_data...")
        try:
            point = Point(-79.85, 43.75)
            dist = _distance_to_boundary(self.sample_geom, point)
            self.assertIsInstance(dist, float)
            self.assertGreater(dist, 0)  # Should have positive distance
            print("PASS: test_distance_to_boundary_with_sample_data")
        except Exception as e:
            print(f"FAIL: test_distance_to_boundary_with_sample_data - {e}")
            raise

    def test_distance_to_boundary_with_none(self):
        """Test distance calculation with None input."""
        print("Running test_distance_to_boundary_with_none...")
        try:
            dist = _distance_to_boundary(None, Point(0, 0))
            self.assertEqual(dist, float('inf'))
            print("PASS: test_distance_to_boundary_with_none")
        except Exception as e:
            print(f"FAIL: test_distance_to_boundary_with_none - {e}")
            raise

    def test_calculate_directional_factor(self):
        """Test directional factor calculation."""
        print("Running test_calculate_directional_factor...")
        try:
            fire_center = Point(-79.8, 43.7)
            target = Point(-79.85, 43.75)
            factor = _calculate_directional_factor(fire_center, target, 90)
            self.assertIsInstance(factor, float)
            self.assertGreaterEqual(factor, 0.5)
            self.assertLessEqual(factor, 1.5)
            print("PASS: test_calculate_directional_factor")
        except Exception as e:
            print(f"FAIL: test_calculate_directional_factor - {e}")
            raise

    def test_identify_critical_points(self):
        """Test critical points identification."""
        print("Running test_identify_critical_points...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
            self.assertIsInstance(points, list)
            self.assertGreater(len(points), 0)
            for point in points:
                self.assertIn('name', point)
                self.assertIn('lat', point)
                self.assertIn('lon', point)
            print("PASS: test_identify_critical_points")
        except Exception as e:
            print(f"FAIL: test_identify_critical_points - {e}")
            raise

    def test_calculate_arrival_times_structure(self):
        """Test that arrival times return correct structure."""
        print("Running test_calculate_arrival_times_structure...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
            arrival_times = _calculate_arrival_times(self.sample_geom, points, self.spread_rate, self.wind_dir)

            # Should return a list
            self.assertIsInstance(arrival_times, list)

            # Should have entries for each critical point
            self.assertEqual(len(arrival_times), len(points))

            # Each entry should have required fields
            for entry in arrival_times:
                self.assertIn('location', entry)
                self.assertIn('hours_until_arrival', entry)
                self.assertIn('confidence', entry)

                # hours_until_arrival should be a float
                self.assertIsInstance(entry['hours_until_arrival'], float)

                # confidence should be a string
                self.assertIsInstance(entry['confidence'], str)

            print("PASS: test_calculate_arrival_times_structure")
        except Exception as e:
            print(f"FAIL: test_calculate_arrival_times_structure - {e}")
            raise

    def test_calculate_arrival_times_sorted(self):
        """Test that arrival times are sorted by time."""
        print("Running test_calculate_arrival_times_sorted...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
            arrival_times = _calculate_arrival_times(self.sample_geom, points, self.spread_rate, self.wind_dir)

            # Should be sorted by hours_until_arrival
            times = [entry['hours_until_arrival'] for entry in arrival_times]
            self.assertEqual(times, sorted(times))

            print("PASS: test_calculate_arrival_times_sorted")
        except Exception as e:
            print(f"FAIL: test_calculate_arrival_times_sorted - {e}")
            raise

    def test_calculate_arrival_times_with_none_boundary(self):
        """Test behavior with None boundary input."""
        print("Running test_calculate_arrival_times_with_none_boundary...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
            arrival_times = _calculate_arrival_times(None, points, self.spread_rate, self.wind_dir)

            # Should return empty list
            self.assertEqual(arrival_times, [])

            print("PASS: test_calculate_arrival_times_with_none_boundary")
        except Exception as e:
            print(f"FAIL: test_calculate_arrival_times_with_none_boundary - {e}")
            raise

    def test_calculate_arrival_times_different_spread_rates(self):
        """Test arrival times with different spread rates."""
        print("Running test_calculate_arrival_times_different_spread_rates...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})

            # Test with slower spread rate
            slow_times = _calculate_arrival_times(self.sample_geom, points, 1.0, self.wind_dir)
            fast_times = _calculate_arrival_times(self.sample_geom, points, 5.0, self.wind_dir)

            # Faster spread should result in shorter arrival times
            for slow, fast in zip(slow_times, fast_times):
                self.assertGreater(slow['hours_until_arrival'], fast['hours_until_arrival'])

            print("PASS: test_calculate_arrival_times_different_spread_rates")
        except Exception as e:
            print(f"FAIL: test_calculate_arrival_times_different_spread_rates - {e}")
            raise

    def test_calculate_arrival_times_confidence_levels(self):
        """Test that confidence levels are assigned correctly."""
        print("Running test_calculate_arrival_times_confidence_levels...")
        try:
            points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
            arrival_times = _calculate_arrival_times(self.sample_geom, points, self.spread_rate, self.wind_dir)

            for entry in arrival_times:
                confidence = entry['confidence']
                hours = entry['hours_until_arrival']

                # High confidence for short times, medium for longer
                if hours < 6:
                    self.assertEqual(confidence, 'high')
                else:
                    self.assertEqual(confidence, 'medium')

            print("PASS: test_calculate_arrival_times_confidence_levels")
        except Exception as e:
            print(f"FAIL: test_calculate_arrival_times_confidence_levels - {e}")
            raise


if __name__ == '__main__':
    import unittest
    unittest.main()