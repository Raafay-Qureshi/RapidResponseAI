import json
import os
import sys
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_fire_spread_rate import TestFireSpreadRate
from test_timeline_predictions import TestTimelinePredictions
from test_arrival_times import TestArrivalTimes


class ComprehensivePredictionTests(TestCase):
    """Comprehensive test suite for all prediction functionality."""

    def test_all_prediction_components(self):
        """Run all prediction tests and verify they all pass."""
        print("=== COMPREHENSIVE PREDICTION TEST SUITE ===")
        print()

        # Create test suite
        loader = TestLoader()
        suite = TestSuite()

        # Add all test classes
        suite.addTests(loader.loadTestsFromTestCase(TestFireSpreadRate))
        suite.addTests(loader.loadTestsFromTestCase(TestTimelinePredictions))
        suite.addTests(loader.loadTestsFromTestCase(TestArrivalTimes))

        # Run tests with custom runner that shows individual results
        runner = TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        # Summary
        print()
        print("=== COMPREHENSIVE TEST SUMMARY ===")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

        if result.failures:
            print("FAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")

        if result.errors:
            print("ERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")

        # Assert all tests passed
        self.assertEqual(len(result.failures), 0, "Some tests failed")
        self.assertEqual(len(result.errors), 0, "Some tests had errors")
        print("PASS: ALL COMPREHENSIVE PREDICTION TESTS PASSED")


if __name__ == '__main__':
    import unittest

    # Run comprehensive tests
    suite = TestLoader().loadTestsFromTestCase(ComprehensivePredictionTests)
    runner = TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)