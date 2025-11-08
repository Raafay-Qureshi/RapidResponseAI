"""
Helper functions for PredictionAgent.
These are stubs that will be implemented in subsequent tasks.
"""

from typing import Dict, List, Tuple
from shapely.geometry import shape


def _calculate_fire_spread_rate(weather: Dict) -> Tuple[float, Dict]:
    """
    Calculates a simplified fire spread rate based on weather conditions.
    """
    # Extract data, providing sane defaults
    wind_speed_ms = weather.get('wind', {}).get('speed', 10)  # m/s from API
    wind_speed = wind_speed_ms * 3.6  # Convert to km/h
    temperature = weather.get('main', {}).get('temp', 20)     # Celsius
    humidity = weather.get('main', {}).get('humidity', 50)  # Percent
    wind_direction = weather.get('wind', {}).get('deg', 0)    # degrees

    # Simplified fire spread rate calculation
    # Real models use Rothermel equations, but this is hackathon-friendly
    base_spread_rate = 2.0  # km/hour base rate

    # Wind factor (0.5x to 3x multiplier)
    wind_factor = 1 + (wind_speed / 50)

    # Temperature factor
    temp_factor = 1 + ((temperature - 20) / 40)

    # Humidity factor (inverse)
    humidity_factor = 1.5 - (humidity / 100)

    # Ensure factors are non-negative
    wind_factor = max(0.5, wind_factor)
    temp_factor = max(0.5, temp_factor)
    humidity_factor = max(0.1, humidity_factor)

    spread_rate = base_spread_rate * wind_factor * temp_factor * humidity_factor

    factors = {
        'wind_speed_kmh': wind_speed,
        'wind_direction_deg': wind_direction,
        'temperature_c': temperature,
        'humidity_percent': humidity
    }

    return spread_rate, factors


def _generate_timeline_predictions(current_boundary_geojson: Dict, spread_rate: float) -> List[Dict]:
    """
    Generate timeline predictions for fire spread.

    Args:
        current_boundary_geojson: Current fire perimeter
        spread_rate: Spread rate in km/h

    Returns:
        List of prediction dictionaries
    """
    # Stub implementation - will be replaced in Task #25
    predictions = [
        {
            'time': '2023-10-01T12:00:00Z',
            'area': 100.0,
            'perimeter': current_boundary_geojson
        },
        {
            'time': '2023-10-01T13:00:00Z',
            'area': 100.0 + (spread_rate * 1),  # 1 hour prediction
            'perimeter': current_boundary_geojson  # Would be expanded boundary
        },
        {
            'time': '2023-10-01T14:00:00Z',
            'area': 100.0 + (spread_rate * 2),  # 2 hour prediction
            'perimeter': current_boundary_geojson  # Would be further expanded
        }
    ]

    return predictions


def _identify_critical_points(location: Dict) -> List[Dict]:
    """
    Identify critical points that need protection from fire spread.

    Args:
        location: Disaster location dictionary

    Returns:
        List of critical point dictionaries
    """
    # Stub implementation - will be replaced in Task #26
    # For now, return some sample points near the disaster location
    lat = location.get('lat', 43.7)
    lon = location.get('lon', -79.8)

    critical_points = [
        {'lat': lat + 0.01, 'lon': lon + 0.01, 'type': 'residential'},
        {'lat': lat - 0.01, 'lon': lon - 0.01, 'type': 'school'},
        {'lat': lat + 0.005, 'lon': lon - 0.005, 'type': 'hospital'}
    ]

    return critical_points


def _calculate_arrival_times(current_boundary_geom, critical_points: List[Dict],
                           spread_rate: float, wind_direction_deg: float) -> List[Dict]:
    """
    Calculate arrival times for fire to reach critical points.

    Args:
        current_boundary_geom: Current fire boundary geometry
        critical_points: List of critical points
        spread_rate: Spread rate in km/h
        wind_direction_deg: Wind direction in degrees

    Returns:
        List of arrival time dictionaries
    """
    # Stub implementation - will be replaced in Task #26
    arrival_times = []

    for point in critical_points:
        # Simple distance-based calculation (would be more sophisticated)
        # Assume points are within 1-5 km and calculate time based on spread rate
        distance_km = 2.0  # Placeholder distance
        time_hours = distance_km / spread_rate
        time_seconds = int(time_hours * 3600)

        arrival_times.append({
            'point': point,
            'arrival_time': f'2023-10-01T{12 + int(time_hours):02d}:00:00Z',
            'distance_km': distance_km,
            'time_hours': round(time_hours, 2)
        })

    return arrival_times