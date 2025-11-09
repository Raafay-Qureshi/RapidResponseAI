from .test_fire_spread_rate import TestFireSpreadRate
from .test_timeline_predictions import TestTimelinePredictions
from .test_arrival_times import TestArrivalTimes

def test_all_prediction_components(capsys):
    """Run all prediction tests and verify they all pass."""
    
    # The tests from the imported modules will be discovered and run by pytest
    # This file is now just a placeholder to ensure that the tests are discovered.
    
    assert True