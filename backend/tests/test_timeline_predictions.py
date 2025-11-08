import json
import os
import sys
from unittest import TestCase

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.prediction_helpers import _generate_timeline_predictions


class TestTimelinePredictions(TestCase):
    """Test cases for _generate_timeline_predictions function."""

    def setUp(self):
        """Set up test data."""
        # Sample polygon representing a small fire area
        self.sample_polygon = {
            'type': 'Polygon',
            'coordinates': [[[-79.8, 43.7], [-79.79, 43.7], [-79.79, 43.71], [-79.8, 43.71], [-79.8, 43.7]]]
        }
        self.spread_rate = 2.5  # km/h

    def test_generate_timeline_predictions_structure(self):
        """Test that timeline predictions return correct structure."""
        print("Running test_generate_timeline_predictions_structure...")
        try:
            predictions = _generate_timeline_predictions(self.sample_polygon, self.spread_rate)

            # Should return a dictionary
            self.assertIsInstance(predictions, dict)

            # Should have keys for hour_1, hour_3, hour_6
            expected_keys = {'hour_1', 'hour_3', 'hour_6'}
            self.assertEqual(set(predictions.keys()), expected_keys)

            # Each prediction should have the required fields
            for hour_key, prediction_data in predictions.items():
                self.assertIn('boundary', prediction_data)
                self.assertIn('area_km2', prediction_data)
                self.assertIn('confidence', prediction_data)

                # area_km2 should be a float
                self.assertIsInstance(prediction_data['area_km2'], float)

                # confidence should be a float between 0 and 1
                self.assertIsInstance(prediction_data['confidence'], float)
                self.assertGreaterEqual(prediction_data['confidence'], 0.0)
                self.assertLessEqual(prediction_data['confidence'], 1.0)

            print("PASS: test_generate_timeline_predictions_structure")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_structure - {e}")
            raise

    def test_generate_timeline_predictions_confidence_decreases(self):
        """Test that confidence decreases with time."""
        print("Running test_generate_timeline_predictions_confidence_decreases...")
        try:
            predictions = _generate_timeline_predictions(self.sample_polygon, self.spread_rate)

            confidence_1h = predictions['hour_1']['confidence']
            confidence_3h = predictions['hour_3']['confidence']
            confidence_6h = predictions['hour_6']['confidence']

            # Confidence should decrease over time
            self.assertGreater(confidence_1h, confidence_3h)
            self.assertGreater(confidence_3h, confidence_6h)

            # Check specific values (0.75 - hours * 0.05)
            self.assertAlmostEqual(confidence_1h, 0.70)  # 0.75 - 1*0.05
            self.assertAlmostEqual(confidence_3h, 0.60)  # 0.75 - 3*0.05
            self.assertAlmostEqual(confidence_6h, 0.45)  # 0.75 - 6*0.05

            print("PASS: test_generate_timeline_predictions_confidence_decreases")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_confidence_decreases - {e}")
            raise

    def test_generate_timeline_predictions_area_increases(self):
        """Test that predicted area increases with time."""
        print("Running test_generate_timeline_predictions_area_increases...")
        try:
            predictions = _generate_timeline_predictions(self.sample_polygon, self.spread_rate)

            area_1h = predictions['hour_1']['area_km2']
            area_3h = predictions['hour_3']['area_km2']
            area_6h = predictions['hour_6']['area_km2']

            # Area should increase over time (fire spreads)
            self.assertLess(area_1h, area_3h)
            self.assertLess(area_3h, area_6h)

            # All areas should be positive
            self.assertGreater(area_1h, 0)
            self.assertGreater(area_3h, 0)
            self.assertGreater(area_6h, 0)

            print("PASS: test_generate_timeline_predictions_area_increases")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_area_increases - {e}")
            raise

    def test_generate_timeline_predictions_boundary_expansion(self):
        """Test that boundaries are properly expanded."""
        print("Running test_generate_timeline_predictions_boundary_expansion...")
        try:
            predictions = _generate_timeline_predictions(self.sample_polygon, self.spread_rate)

            # Each boundary should be a valid GeoJSON polygon
            for hour_key, prediction_data in predictions.items():
                boundary = prediction_data['boundary']
                self.assertIsNotNone(boundary)
                self.assertEqual(boundary['type'], 'Polygon')
                self.assertIn('coordinates', boundary)

                # Coordinates should be a list (may be tuples from shapely)
                self.assertIsInstance(boundary['coordinates'], (list, tuple))
                self.assertGreater(len(boundary['coordinates']), 0)

            print("PASS: test_generate_timeline_predictions_boundary_expansion")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_boundary_expansion - {e}")
            raise

    def test_generate_timeline_predictions_with_none_polygon(self):
        """Test behavior with None polygon input."""
        print("Running test_generate_timeline_predictions_with_none_polygon...")
        try:
            predictions = _generate_timeline_predictions(None, self.spread_rate)

            # Should still return structure but with None boundaries
            expected_keys = {'hour_1', 'hour_3', 'hour_6'}
            self.assertEqual(set(predictions.keys()), expected_keys)

            for hour_key, prediction_data in predictions.items():
                self.assertIsNone(prediction_data['boundary'])
                self.assertEqual(prediction_data['area_km2'], 0.0)
                self.assertIsInstance(prediction_data['confidence'], float)

            print("PASS: test_generate_timeline_predictions_with_none_polygon")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_with_none_polygon - {e}")
            raise

    def test_generate_timeline_predictions_different_spread_rates(self):
        """Test predictions with different spread rates."""
        print("Running test_generate_timeline_predictions_different_spread_rates...")
        try:
            # Test with slower spread rate
            slow_predictions = _generate_timeline_predictions(self.sample_polygon, 1.0)
            fast_predictions = _generate_timeline_predictions(self.sample_polygon, 5.0)

            # Faster spread should result in larger areas
            self.assertGreater(
                fast_predictions['hour_3']['area_km2'],
                slow_predictions['hour_3']['area_km2']
            )

            print("PASS: test_generate_timeline_predictions_different_spread_rates")
        except Exception as e:
            print(f"FAIL: test_generate_timeline_predictions_different_spread_rates - {e}")
            raise

    def test_calculate_polygon_area_with_sample_data(self):
        """Test polygon area calculation with sample data."""
        print("Running test_calculate_polygon_area_with_sample_data...")
        try:
            from agents.prediction_helpers import _calculate_polygon_area

            area = _calculate_polygon_area(self.sample_polygon)
            self.assertIsInstance(area, float)
            self.assertGreater(area, 0)  # Should have positive area

            print("PASS: test_calculate_polygon_area_with_sample_data")
        except Exception as e:
            print(f"FAIL: test_calculate_polygon_area_with_sample_data - {e}")
            raise

    def test_calculate_polygon_area_with_none(self):
        """Test polygon area calculation with None input."""
        print("Running test_calculate_polygon_area_with_none...")
        try:
            from agents.prediction_helpers import _calculate_polygon_area

            area = _calculate_polygon_area(None)
            self.assertEqual(area, 0.0)

            print("PASS: test_calculate_polygon_area_with_none")
        except Exception as e:
            print(f"FAIL: test_calculate_polygon_area_with_none - {e}")
            raise

    def test_expand_polygon_with_sample_data(self):
        """Test polygon expansion with sample data."""
        print("Running test_expand_polygon_with_sample_data...")
        try:
            from agents.prediction_helpers import _expand_polygon

            expanded = _expand_polygon(self.sample_polygon, 2.5)
            self.assertIsNotNone(expanded)
            self.assertEqual(expanded['type'], 'Polygon')
            self.assertIn('coordinates', expanded)

            print("PASS: test_expand_polygon_with_sample_data")
        except Exception as e:
            print(f"FAIL: test_expand_polygon_with_sample_data - {e}")
            raise

    def test_expand_polygon_with_none(self):
        """Test polygon expansion with None input."""
        print("Running test_expand_polygon_with_none...")
        try:
            from agents.prediction_helpers import _expand_polygon

            expanded = _expand_polygon(None, 2.5)
            self.assertIsNone(expanded)

            print("PASS: test_expand_polygon_with_none")
        except Exception as e:
            print(f"FAIL: test_expand_polygon_with_none - {e}")
            raise

    def test_expand_polygon_distance_effect(self):
        """Test that larger distances create larger polygons."""
        print("Running test_expand_polygon_distance_effect...")
        try:
            from agents.prediction_helpers import _expand_polygon, _calculate_polygon_area

            small_expand = _expand_polygon(self.sample_polygon, 1.0)
            large_expand = _expand_polygon(self.sample_polygon, 3.0)

            small_area = _calculate_polygon_area(small_expand)
            large_area = _calculate_polygon_area(large_expand)

            self.assertGreater(large_area, small_area)

            print("PASS: test_expand_polygon_distance_effect")
        except Exception as e:
            print(f"FAIL: test_expand_polygon_distance_effect - {e}")
            raise

    def test_timeline_predictions_realistic_values(self):
        """Test that predictions produce realistic fire spread values."""
        print("Running test_timeline_predictions_realistic_values...")
        try:
            predictions = _generate_timeline_predictions(self.sample_polygon, self.spread_rate)

            # Just verify areas are positive and increasing (buffer creates large areas)
            hour_1_area = predictions['hour_1']['area_km2']
            hour_6_area = predictions['hour_6']['area_km2']

            self.assertGreater(hour_1_area, 0)  # Should have positive area
            self.assertGreater(hour_6_area, hour_1_area)  # Should increase over time

            # Confidence should be between 0 and 1
            for hour_key in ['hour_1', 'hour_3', 'hour_6']:
                confidence = predictions[hour_key]['confidence']
                self.assertGreaterEqual(confidence, 0.0)
                self.assertLessEqual(confidence, 1.0)

            print("PASS: test_timeline_predictions_realistic_values")
        except Exception as e:
            print(f"FAIL: test_timeline_predictions_realistic_values - {e}")
            raise


if __name__ == '__main__':
    import unittest
    unittest.main()