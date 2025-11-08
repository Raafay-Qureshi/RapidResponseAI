"""
Helper functions for PredictionAgent.
Implements fire spread modeling with weather-based calculations.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from shapely.geometry import shape, Point, Polygon
from shapely.errors import GEOSException

try:
    from pyproj import Geod
except ImportError:
    # Fallback for systems without pyproj
    Geod = None

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration Constants
# ============================================================================

# Fire Spread Model Constants
BASE_SPREAD_RATE_KMH = 2.0  # Base fire spread rate in km/h
WIND_SPEED_DENOMINATOR = 50.0  # Wind speed factor denominator
TEMP_REFERENCE = 20.0  # Reference temperature in Celsius
TEMP_DENOMINATOR = 40.0  # Temperature factor denominator
HUMIDITY_BASE = 1.5  # Base humidity factor
HUMIDITY_DENOMINATOR = 100.0  # Humidity factor denominator

# Factor Bounds
MIN_WIND_FACTOR = 0.5
MIN_TEMP_FACTOR = 0.5
MIN_HUMIDITY_FACTOR = 0.1

# Default Weather Values
DEFAULT_WIND_SPEED_MS = 10.0  # m/s
DEFAULT_WIND_DIRECTION = 0.0  # degrees
DEFAULT_TEMPERATURE = 20.0  # Celsius
DEFAULT_HUMIDITY = 50.0  # percent

# Confidence Constants
BASE_CONFIDENCE = 0.75
CONFIDENCE_DECAY_PER_HOUR = 0.05
ARRIVAL_TIME_HIGH_CONFIDENCE_THRESHOLD = 6.0  # hours

# Geometry Constants
KM_PER_DEGREE = 111.1  # Approximate km per degree of latitude/longitude
M_TO_KM = 1_000_000  # Conversion factor from m² to km²
MS_TO_KMH = 3.6  # Conversion factor from m/s to km/h

# Directional Factor Constants
DOWNWIND_FACTOR_MAX = 1.5
UPWIND_FACTOR_MIN = 0.5

# Prediction Time Horizons (hours)
PREDICTION_HOURS = [1, 3, 6]


# ============================================================================
# Core Fire Spread Rate Calculation
# ============================================================================

def _calculate_fire_spread_rate(weather: Dict) -> Tuple[float, Dict]:
    """
    Calculates a simplified fire spread rate based on weather conditions.
    
    Uses a simplified physics-based model that considers:
    - Wind speed (increases spread rate)
    - Temperature (higher temps increase spread)
    - Humidity (higher humidity decreases spread)
    
    Args:
        weather: Dictionary containing weather data with keys:
            - 'wind': {'speed': m/s, 'deg': degrees}
            - 'main': {'temp': Celsius, 'humidity': percent}
    
    Returns:
        Tuple of (spread_rate_kmh, factors_dict)
        - spread_rate_kmh: Calculated fire spread rate in km/h
        - factors_dict: Dictionary containing extracted weather factors
    
    Raises:
        ValueError: If weather data is invalid or contains non-numeric values
    
    Example:
        >>> weather = {'wind': {'speed': 5}, 'main': {'temp': 25, 'humidity': 40}}
        >>> rate, factors = _calculate_fire_spread_rate(weather)
        >>> print(f"Spread rate: {rate:.2f} km/h")
    """
    logger.debug(f"Calculating fire spread rate with weather data: {weather}")
    
    try:
        # Extract weather data with validation
        wind_data = weather.get('wind', {})
        main_data = weather.get('main', {})
        
        # Validate and extract wind speed (convert from m/s to km/h)
        wind_speed_ms = wind_data.get('speed', DEFAULT_WIND_SPEED_MS)
        if not isinstance(wind_speed_ms, (int, float)) or wind_speed_ms < 0:
            logger.warning(f"Invalid wind speed: {wind_speed_ms}, using default")
            wind_speed_ms = DEFAULT_WIND_SPEED_MS
        wind_speed = wind_speed_ms * MS_TO_KMH
        
        # Validate and extract temperature
        temperature = main_data.get('temp', DEFAULT_TEMPERATURE)
        if not isinstance(temperature, (int, float)):
            logger.warning(f"Invalid temperature: {temperature}, using default")
            temperature = DEFAULT_TEMPERATURE
        
        # Validate and extract humidity
        humidity = main_data.get('humidity', DEFAULT_HUMIDITY)
        if not isinstance(humidity, (int, float)) or humidity < 0 or humidity > 100:
            logger.warning(f"Invalid humidity: {humidity}, using default")
            humidity = DEFAULT_HUMIDITY
        
        # Validate and extract wind direction
        wind_direction = wind_data.get('deg', DEFAULT_WIND_DIRECTION)
        if not isinstance(wind_direction, (int, float)) or wind_direction < 0 or wind_direction >= 360:
            logger.warning(f"Invalid wind direction: {wind_direction}, using default")
            wind_direction = DEFAULT_WIND_DIRECTION
        
        # Calculate spread factors
        # Wind factor: Higher wind = faster spread (0.5x to 3x multiplier)
        wind_factor = 1 + (wind_speed / WIND_SPEED_DENOMINATOR)
        
        # Temperature factor: Higher temp = faster spread
        temp_factor = 1 + ((temperature - TEMP_REFERENCE) / TEMP_DENOMINATOR)
        
        # Humidity factor: Higher humidity = slower spread (inverse relationship)
        humidity_factor = HUMIDITY_BASE - (humidity / HUMIDITY_DENOMINATOR)
        
        # Apply bounds to ensure factors are reasonable
        wind_factor = max(MIN_WIND_FACTOR, wind_factor)
        temp_factor = max(MIN_TEMP_FACTOR, temp_factor)
        humidity_factor = max(MIN_HUMIDITY_FACTOR, humidity_factor)
        
        # Calculate final spread rate
        spread_rate = BASE_SPREAD_RATE_KMH * wind_factor * temp_factor * humidity_factor
        
        factors = {
            'wind_speed_kmh': round(wind_speed, 2),
            'wind_direction_deg': wind_direction,
            'temperature_c': temperature,
            'humidity_percent': humidity
        }
        
        logger.info(f"Calculated spread rate: {spread_rate:.2f} km/h with factors: {factors}")
        return spread_rate, factors
        
    except Exception as e:
        logger.error(f"Error calculating fire spread rate: {e}")
        raise ValueError(f"Failed to calculate fire spread rate: {e}")


# ============================================================================
# Polygon Geometry Utilities
# ============================================================================

def _calculate_polygon_area(polygon: Optional[Dict]) -> float:
    """
    Calculate area of GeoJSON polygon in km².
    
    Uses pyproj for accurate geodesic calculations when available,
    falls back to approximation otherwise.
    
    Args:
        polygon: GeoJSON polygon dict or None
    
    Returns:
        Area in square kilometers (0.0 if polygon is None or invalid)
    
    Example:
        >>> polygon = {'type': 'Polygon', 'coordinates': [[[0,0], [1,0], [1,1], [0,1], [0,0]]]}
        >>> area = _calculate_polygon_area(polygon)
    """
    if not polygon:
        logger.debug("Polygon is None, returning 0 area")
        return 0.0
    
    try:
        geom = shape(polygon)
        
        if not isinstance(geom, Polygon):
            logger.warning(f"Geometry type {type(geom)} is not a Polygon")
            return 0.0
        
        if Geod is not None:
            # Use accurate geodesic calculation
            geod = Geod(ellps="WGS84")
            area_m2, _ = geod.geometry_area_perimeter(geom)
            area_km2 = abs(area_m2) / M_TO_KM
            logger.debug(f"Calculated polygon area (geodesic): {area_km2:.2f} km²")
        else:
            # Fallback: use shapely's planar area (rough approximation)
            # 1 degree² ≈ 111² km² ≈ 12321 km² at equator
            area_km2 = geom.area * (KM_PER_DEGREE ** 2)
            logger.debug(f"Calculated polygon area (planar approximation): {area_km2:.2f} km²")
        
        return area_km2
        
    except (GEOSException, Exception) as e:
        logger.error(f"Error calculating polygon area: {e}")
        return 0.0


def _expand_polygon(polygon: Optional[Dict], distance_km: float) -> Optional[Dict]:
    """
    Expands a polygon by a buffer distance in kilometers.
    
    Creates a buffer zone around the polygon to simulate fire spread.
    Uses a simplified approach assuming roughly equal degrees at all latitudes.
    
    Args:
        polygon: GeoJSON polygon dict or None
        distance_km: Buffer distance in kilometers
    
    Returns:
        Expanded polygon as GeoJSON dict, or None if input is invalid
    
    Raises:
        ValueError: If distance_km is negative
    
    Example:
        >>> polygon = {'type': 'Polygon', 'coordinates': [[[0,0], [1,0], [1,1], [0,1], [0,0]]]}
        >>> expanded = _expand_polygon(polygon, 5.0)  # 5 km buffer
    """
    if not polygon:
        logger.debug("Polygon is None, returning None")
        return None
    
    if distance_km < 0:
        raise ValueError(f"Buffer distance cannot be negative: {distance_km}")
    
    if distance_km == 0:
        logger.debug("Buffer distance is 0, returning original polygon")
        return polygon
    
    try:
        # Convert km to degrees (approximate)
        buffer_degrees = distance_km / KM_PER_DEGREE
        
        geom = shape(polygon)
        expanded_geom = geom.buffer(buffer_degrees)
        
        result = expanded_geom.__geo_interface__
        logger.debug(f"Expanded polygon by {distance_km:.2f} km ({buffer_degrees:.4f} degrees)")
        return result
        
    except (GEOSException, Exception) as e:
        logger.error(f"Error expanding polygon: {e}")
        return None


# ============================================================================
# Timeline Prediction Generation
# ============================================================================

def _generate_timeline_predictions(current_boundary_geojson: Optional[Dict], spread_rate: float) -> Dict:
    """
    Projects fire spread forward for multiple time horizons (1, 3, and 6 hours).
    
    Generates prediction boundaries by expanding the current fire perimeter
    based on the calculated spread rate. Confidence decreases with time.
    
    Args:
        current_boundary_geojson: Current fire perimeter as GeoJSON polygon
        spread_rate: Fire spread rate in km/h
    
    Returns:
        Dictionary with keys 'hour_1', 'hour_3', 'hour_6', each containing:
            - boundary: Predicted fire perimeter (GeoJSON)
            - area_km2: Predicted fire area in km²
            - confidence: Prediction confidence (0-1)
    
    Example:
        >>> boundary = {'type': 'Polygon', 'coordinates': [...]}
        >>> predictions = _generate_timeline_predictions(boundary, 2.5)
        >>> print(predictions['hour_3']['area_km2'])
    """
    logger.info(f"Generating timeline predictions with spread rate {spread_rate:.2f} km/h")
    
    if spread_rate < 0:
        logger.warning(f"Negative spread rate {spread_rate}, using 0")
        spread_rate = 0
    
    predictions = {}
    
    for hours in PREDICTION_HOURS:
        spread_distance_km = spread_rate * hours
        
        logger.debug(f"Predicting {hours}h: spread distance = {spread_distance_km:.2f} km")
        
        # Expand boundary by predicted spread distance
        # Note: A real model would expand more in the wind direction
        expanded_boundary_geojson = _expand_polygon(
            current_boundary_geojson,
            spread_distance_km
        )
        
        # Calculate confidence (decreases over time)
        confidence = max(0.0, BASE_CONFIDENCE - (hours * CONFIDENCE_DECAY_PER_HOUR))
        
        predictions[f'hour_{hours}'] = {
            'boundary': expanded_boundary_geojson,
            'area_km2': _calculate_polygon_area(expanded_boundary_geojson),
            'confidence': round(confidence, 2)
        }
        
        logger.debug(f"Hour {hours} prediction: area={predictions[f'hour_{hours}']['area_km2']:.2f} km², confidence={confidence:.2f}")
    
    return predictions


# ============================================================================
# Distance and Directional Calculations
# ============================================================================

def _distance_to_boundary(boundary_geom: Optional[shape], point_geom: Optional[Point]) -> float:
    """
    Calculate distance from a point to a polygon boundary in kilometers.
    
    Args:
        boundary_geom: Shapely geometry representing fire boundary
        point_geom: Shapely Point representing target location
    
    Returns:
        Distance in kilometers, or infinity if input is invalid
    
    Example:
        >>> from shapely.geometry import Point
        >>> boundary = shape({'type': 'Polygon', 'coordinates': [...]})
        >>> point = Point(-79.8, 43.7)
        >>> dist = _distance_to_boundary(boundary, point)
    """
    if not boundary_geom or not point_geom:
        logger.debug("Boundary or point is None, returning infinity")
        return float('inf')
    
    try:
        # Calculate distance in degrees, then convert to km
        distance_degrees = boundary_geom.distance(point_geom)
        distance_km = distance_degrees * KM_PER_DEGREE
        
        logger.debug(f"Distance to boundary: {distance_km:.2f} km")
        return distance_km
        
    except Exception as e:
        logger.error(f"Error calculating distance to boundary: {e}")
        return float('inf')


def _calculate_directional_factor(fire_center: Point, target_point: Point, wind_dir: float) -> float:
    """
    Calculate directional spread factor based on wind direction.
    
    Fire spreads faster downwind and slower upwind. This function calculates
    a multiplier (0.5-1.5) based on the angle between fire-to-target direction
    and wind direction.
    
    Args:
        fire_center: Center point of the fire (Shapely Point)
        target_point: Target location (Shapely Point)
        wind_dir: Wind direction in degrees (0-360, meteorological convention)
    
    Returns:
        Directional factor (0.5 = upwind, 1.0 = crosswind, 1.5 = downwind)
    
    Example:
        >>> fire = Point(-79.8, 43.7)
        >>> target = Point(-79.85, 43.75)
        >>> factor = _calculate_directional_factor(fire, target, 90)
    """
    try:
        # Calculate angle from fire to target
        dx = target_point.x - fire_center.x
        dy = target_point.y - fire_center.y
        target_angle = np.degrees(np.arctan2(dy, dx))
        
        # Convert wind direction from meteorological (coming from) to mathematical (going to)
        wind_angle = (wind_dir - 180) % 360
        
        # Calculate angular difference (0-180 degrees)
        angle_diff = 180 - abs(abs(target_angle - wind_angle) - 180)
        
        # Convert to directional factor using cosine
        # cos(0°) = 1 (downwind), cos(90°) = 0 (crosswind), cos(180°) = -1 (upwind)
        # Scale to range [0.5, 1.5]
        factor = (np.cos(np.radians(angle_diff)) + 1) / 2  # Scale to [0, 1]
        factor = UPWIND_FACTOR_MIN + factor  # Scale to [0.5, 1.5]
        
        logger.debug(f"Directional factor: {factor:.2f} (angle_diff={angle_diff:.1f}°)")
        return factor
        
    except Exception as e:
        logger.error(f"Error calculating directional factor: {e}")
        return 1.0  # Default to no directional effect


# ============================================================================
# Critical Points and Arrival Times
# ============================================================================

def _identify_critical_points(location: Dict) -> List[Dict]:
    """
    Identify critical infrastructure or population centers near the fire.
    
    Note: Currently returns hardcoded demo points for Brampton area.
    In production, this would query a database or GeoHub API.
    
    Args:
        location: Dictionary with 'lat' and 'lon' keys (currently unused)
    
    Returns:
        List of dicts with keys: 'name', 'lat', 'lon'
    
    Example:
        >>> points = _identify_critical_points({'lat': 43.7, 'lon': -79.8})
        >>> for point in points:
        ...     print(f"{point['name']}: ({point['lat']}, {point['lon']})")
    """
    logger.debug(f"Identifying critical points near location: {location}")
    
    # Hardcoded for demo - in production, query from database
    critical_points = [
        {'name': 'Residential Area A', 'lat': 43.735, 'lon': -79.860},
        {'name': 'Highway 410', 'lat': 43.740, 'lon': -79.855},
        {'name': 'Main Street Commercial', 'lat': 43.745, 'lon': -79.850}
    ]
    
    logger.info(f"Identified {len(critical_points)} critical points")
    return critical_points


def _calculate_arrival_times(
    boundary_geom: Optional[shape],
    points: List[Dict],
    spread_rate: float,
    wind_dir: float
) -> List[Dict]:
    """
    Calculate estimated arrival times at critical points.
    
    Estimates when the fire will reach each critical point based on:
    - Current distance from fire boundary
    - Spread rate
    - Wind direction (directional factor)
    
    Args:
        boundary_geom: Current fire boundary (Shapely geometry)
        points: List of critical points with 'name', 'lat', 'lon'
        spread_rate: Base fire spread rate in km/h
        wind_dir: Wind direction in degrees
    
    Returns:
        List of dicts sorted by arrival time, each containing:
            - location: Name of the location
            - hours_until_arrival: Estimated hours until fire arrival
            - confidence: 'high' (< 6h) or 'medium' (≥ 6h)
    
    Example:
        >>> from shapely.geometry import shape
        >>> boundary = shape({'type': 'Polygon', 'coordinates': [...]})
        >>> points = [{'name': 'Town A', 'lat': 43.7, 'lon': -79.8}]
        >>> times = _calculate_arrival_times(boundary, points, 2.5, 90)
    """
    logger.info(f"Calculating arrival times for {len(points)} critical points")
    
    results = []
    
    if not boundary_geom:
        logger.warning("No boundary geometry provided, returning empty list")
        return []
    
    if spread_rate <= 0:
        logger.warning(f"Invalid spread rate {spread_rate}, returning empty list")
        return []
    
    try:
        fire_center = boundary_geom.centroid
        logger.debug(f"Fire center: ({fire_center.x:.4f}, {fire_center.y:.4f})")
        
        for point_data in points:
            try:
                # Create point geometry
                point_geom = Point(point_data['lon'], point_data['lat'])
                
                # Calculate distance from boundary to point
                distance_km = _distance_to_boundary(boundary_geom, point_geom)
                
                # Adjust spread rate for wind direction
                directional_factor = _calculate_directional_factor(
                    fire_center, point_geom, wind_dir
                )
                
                effective_spread_rate = spread_rate * directional_factor
                
                # Calculate arrival time
                if effective_spread_rate <= 0:
                    hours_until_arrival = float('inf')
                else:
                    hours_until_arrival = distance_km / effective_spread_rate
                
                # Determine confidence level
                confidence = 'high' if hours_until_arrival < ARRIVAL_TIME_HIGH_CONFIDENCE_THRESHOLD else 'medium'
                
                results.append({
                    'location': point_data['name'],
                    'hours_until_arrival': round(hours_until_arrival, 1),
                    'confidence': confidence
                })
                
                logger.debug(
                    f"{point_data['name']}: {hours_until_arrival:.1f}h "
                    f"(distance={distance_km:.2f} km, factor={directional_factor:.2f})"
                )
                
            except Exception as e:
                logger.error(f"Error processing point {point_data.get('name', 'unknown')}: {e}")
                continue
        
        # Sort by arrival time (closest first)
        results.sort(key=lambda x: x['hours_until_arrival'])
        logger.info(f"Calculated {len(results)} arrival times")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating arrival times: {e}")
        return []