"""
Helper functions for PredictionAgent.
These are stubs that will be implemented in subsequent tasks.
"""

import numpy as np
from typing import Dict, List, Tuple
from shapely.geometry import shape, Point
try:
    from pyproj import Geod
except ImportError:
    # Fallback for systems without pyproj
    Geod = None


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


def _calculate_polygon_area(polygon: Dict) -> float:
    """Calculate area of GeoJSON polygon in km²"""
    if not polygon:
        return 0.0
    geom = shape(polygon)
    if Geod is not None:
        geod = Geod(ellps="WGS84")
        area_m2, _ = geod.geometry_area_perimeter(geom)
        return abs(area_m2) / 1_000_000  # Convert to km²
    else:
        # Fallback: use shapely's area (in degrees², approximate)
        # Very rough approximation: 1 degree² ≈ 111² km² ≈ 12321 km²
        return geom.area * 12321


def _expand_polygon(polygon: Dict, distance_km: float) -> Dict:
    """Expands a polygon by a buffer distance in km"""
    if not polygon:
        return None
    # 1 degree is approx 111.1 km
    buffer_degrees = distance_km / 111.1
    geom = shape(polygon)
    expanded_geom = geom.buffer(buffer_degrees)
    return expanded_geom.__geo_interface__


def _generate_timeline_predictions(current_boundary_geojson: Dict, spread_rate: float) -> Dict:
    """
    Projects fire spread forward for 1, 3, and 6 hours.
    """
    predictions = {}
    for hours in [1, 3, 6]:
        spread_distance_km = spread_rate * hours

        # Simplified: Just expand radius (buffer)
        # A real model would expand more in the wind_direction
        expanded_boundary_geojson = _expand_polygon(
            current_boundary_geojson,
            spread_distance_km
        )

        predictions[f'hour_{hours}'] = {
            'boundary': expanded_boundary_geojson,
            'area_km2': _calculate_polygon_area(expanded_boundary_geojson),
            'confidence': 0.75 - (hours * 0.05)  # Confidence decreases with time
        }
    return predictions


def _distance_to_boundary(boundary_geom: shape, point_geom: Point) -> float:
    """Calculate distance from a point to a polygon boundary in km"""
    if not boundary_geom or not point_geom:
        return float('inf')
    # .distance returns degrees, convert to km
    distance_degrees = boundary_geom.distance(point_geom)
    return distance_degrees * 111.1  # Approx km per degree


def _calculate_directional_factor(fire_center: Point, target_point: Point, wind_dir: float) -> float:
    """
    Very simple directional model.
    Returns > 1 if target is downwind, < 1 if upwind.
    """
    # Calculate angle from fire to target
    target_angle = np.degrees(np.arctan2(target_point.y - fire_center.y, target_point.x - fire_center.x))
    # Convert wind direction (from) to angle (to)
    wind_angle = (wind_dir - 180) % 360

    # Find difference in angles
    angle_diff = 180 - abs(abs(target_angle - wind_angle) - 180)

    # Cosine function gives 1 for 0 diff, 0 for 90 diff, -1 for 180 diff
    # We'll scale it to be 1.5 (downwind) to 0.5 (upwind)
    factor = (np.cos(np.radians(angle_diff)) + 1) / 2  # Scale 0-1
    return 0.5 + factor  # Scale 0.5 - 1.5


def _identify_critical_points(location: Dict) -> List[Dict]:
    """Identify critical infrastructure or population centers"""
    # Hardcoded for demo
    return [
        {'name': 'Residential Area A', 'lat': 43.735, 'lon': -79.860},
        {'name': 'Highway 410', 'lat': 43.740, 'lon': -79.855},
        {'name': 'Main Street Commercial', 'lat': 43.745, 'lon': -79.850}
    ]


def _calculate_arrival_times(boundary_geom: shape, points: List, spread_rate: float, wind_dir: float) -> List[Dict]:
    """Calculate when fire will reach each critical point"""
    results = []
    if not boundary_geom:
        return []

    fire_center = boundary_geom.centroid

    for point_data in points:
        point_geom = Point(point_data['lon'], point_data['lat'])

        # Calculate distance from boundary to point
        distance_km = _distance_to_boundary(boundary_geom, point_geom)

        # Adjust for wind direction
        directional_factor = _calculate_directional_factor(
            fire_center, point_geom, wind_dir
        )

        effective_spread_rate = spread_rate * directional_factor
        if effective_spread_rate <= 0:  # or very small
            hours_until_arrival = float('inf')
        else:
            hours_until_arrival = distance_km / effective_spread_rate

        results.append({
            'location': point_data['name'],
            'hours_until_arrival': round(hours_until_arrival, 1),
            'confidence': 'high' if hours_until_arrival < 6 else 'medium'
        })

    return sorted(results, key=lambda x: x['hours_until_arrival'])