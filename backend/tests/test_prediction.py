import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.prediction import PredictionAgent


async def test_prediction_agent_wildfire():
    """Test PredictionAgent for wildfire disaster type."""
    agent = PredictionAgent()

    # Mock disaster and data
    disaster = {'type': 'wildfire', 'location': {'lat': 43.7, 'lon': -79.8}}
    data = {
        'weather': {
            'temperature': 25,
            'humidity': 40,
            'wind_speed': 15,
            'wind_direction': 90
        },
        'fire_perimeter': {
            'type': 'Polygon',
            'coordinates': [[[-79.8, 43.7], [-79.79, 43.7], [-79.79, 43.71], [-79.8, 43.71], [-79.8, 43.7]]]
        }
    }

    # Mock the helper functions
    with patch('agents.prediction._calculate_fire_spread_rate') as mock_spread_rate, \
         patch('agents.prediction._generate_timeline_predictions') as mock_timeline, \
         patch('agents.prediction._identify_critical_points') as mock_critical, \
         patch('agents.prediction._calculate_arrival_times') as mock_arrival:

        # Set up mock returns
        mock_spread_rate.return_value = (10.5, {'wind_direction_deg': 90, 'temperature': 25})
        mock_timeline.return_value = [{'time': '2023-10-01T12:00:00Z', 'area': 100}]
        mock_critical.return_value = [{'lat': 43.71, 'lon': -79.79}]
        mock_arrival.return_value = [{'point': {'lat': 43.71, 'lon': -79.79}, 'arrival_time': '2023-10-01T13:00:00Z'}]

        result = await agent.analyze(disaster, data)

        # Assertions
        assert 'current_spread_rate_kmh' in result
        assert result['current_spread_rate_kmh'] == 10.5
        assert 'predictions' in result
        assert len(result['predictions']) == 1
        assert 'critical_arrival_times' in result
        assert len(result['critical_arrival_times']) == 1
        assert 'factors' in result

        print("PASS: PredictionAgent wildfire analysis works correctly")


async def test_prediction_agent_flood():
    """Test PredictionAgent for flood disaster type (placeholder)."""
    agent = PredictionAgent()

    disaster = {'type': 'flood', 'location': {'lat': 43.7, 'lon': -79.8}}
    data = {'weather': {}}

    result = await agent.analyze(disaster, data)

    assert result == {'status': 'not_implemented'}
    print("PASS: PredictionAgent flood analysis returns placeholder")


async def test_prediction_agent_unknown_disaster():
    """Test PredictionAgent raises error for unknown disaster type."""
    agent = PredictionAgent()

    disaster = {'type': 'earthquake', 'location': {'lat': 43.7, 'lon': -79.8}}
    data = {}

    try:
        await agent.analyze(disaster, data)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown disaster type: earthquake" in str(e)
        print("PASS: PredictionAgent raises error for unknown disaster type")


async def main():
    await test_prediction_agent_wildfire()
    await test_prediction_agent_flood()
    await test_prediction_agent_unknown_disaster()
    print("\nSUCCESS: All PredictionAgent tests passed!")


if __name__ == "__main__":
    asyncio.run(main())