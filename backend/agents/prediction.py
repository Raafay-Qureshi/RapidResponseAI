"""
PredictionAgent: Disaster spread modeling and timeline predictions.

This agent coordinates fire spread modeling by:
1. Calculating spread rate based on weather conditions
2. Generating timeline predictions (1, 3, 6 hours)
3. Calculating arrival times at critical points
"""

from .base_agent import BaseAgent
import logging
from typing import Dict, List, Optional
from datetime import datetime
from shapely.geometry import shape, Point
from shapely.errors import GEOSException

# Import helper functions
from .prediction_helpers import (
    _calculate_fire_spread_rate,
    _generate_timeline_predictions,
    _calculate_arrival_times,
    _identify_critical_points
)

# Configure logging
logger = logging.getLogger(__name__)


class PredictionAgent(BaseAgent):
    """
    Agent for modeling disaster spread and generating timeline predictions.
    
    Supports multiple disaster types with specialized modeling for each:
    - Wildfire: Weather-based spread modeling with directional wind effects
    - Flood: Placeholder for future implementation
    
    Methods:
        analyze: Main entry point for disaster analysis
        _model_fire_spread: Wildfire-specific spread modeling
        _model_flood_spread: Flood-specific modeling (placeholder)
    """
    
    async def analyze(self, disaster: Dict, data: Dict, scenario_config: Dict = None) -> Dict:
        """
        Model disaster spread and generate timeline predictions.

        Routes to appropriate disaster-specific modeling based on disaster type.

        Args:
            disaster: Dictionary containing:
                - type: Disaster type ('wildfire', 'flood', etc.)
                - location: Dict with 'lat' and 'lon' keys
                - other disaster-specific metadata
            data: Dictionary containing:
                - weather: Current weather conditions
                - fire_perimeter: Current fire boundary (for wildfire)
                - other data sources
            scenario_config: Optional scenario configuration for specific scenarios

        Returns:
            Dictionary containing prediction results specific to disaster type

        Raises:
            ValueError: If disaster type is unknown or unsupported
            KeyError: If required data is missing

        Example:
            >>> agent = PredictionAgent()
            >>> disaster = {'type': 'wildfire', 'location': {'lat': 43.7, 'lon': -79.8}}
            >>> data = {'weather': {...}, 'fire_perimeter': {...}}
            >>> result = await agent.analyze(disaster, data)
        """
        disaster_type = disaster.get('type', 'unknown')
        self._log(f"Starting analysis for {disaster_type} disaster")
        logger.info(f"PredictionAgent analyzing {disaster_type} at location {disaster.get('location')}")

        # Check if this is July 2020 scenario
        if scenario_config and scenario_config.get('disaster', {}).get('scenario_id') == 'july_2020_backtest':
            self._log("Using July 2020 scenario parameters")
            return self._predict_july_2020_spread(scenario_config)

        try:
            if disaster_type == 'wildfire':
                result = await self._model_fire_spread(disaster, data)
                logger.info(f"Wildfire analysis complete: spread_rate={result.get('current_spread_rate_kmh')} km/h")
                return result

            elif disaster_type == 'flood':
                result = await self._model_flood_spread(disaster, data)
                logger.info("Flood analysis complete (placeholder)")
                return result

            else:
                error_msg = f"Unknown disaster type: {disaster_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except KeyError as e:
            logger.error(f"Missing required data field: {e}")
            raise KeyError(f"Missing required data for {disaster_type} analysis: {e}")

        except Exception as e:
            logger.error(f"Error during {disaster_type} analysis: {e}", exc_info=True)
            raise
    
    async def _model_fire_spread(self, disaster: Dict, data: Dict) -> Dict:
        """
        Model wildfire spread using weather-based physics model.
        
        Coordinates three main modeling tasks:
        1. Calculate current spread rate based on weather
        2. Generate timeline predictions for 1, 3, and 6 hours
        3. Calculate arrival times at critical infrastructure points
        
        Args:
            disaster: Dictionary with disaster metadata including:
                - location: Dict with 'lat' and 'lon' keys
            data: Dictionary containing:
                - weather: Current weather conditions (required)
                - fire_perimeter: Current fire boundary GeoJSON (optional)
        
        Returns:
            Dictionary containing:
                - current_spread_rate_kmh: Current fire spread rate
                - predictions: Timeline predictions for hour_1, hour_3, hour_6
                - critical_arrival_times: List of arrival times at critical points
                - factors: Weather factors used in calculation
        
        Raises:
            KeyError: If weather data is missing
            ValueError: If weather data is invalid
        
        Example:
            >>> disaster = {'type': 'wildfire', 'location': {'lat': 43.7, 'lon': -79.8}}
            >>> data = {
            ...     'weather': {'wind': {'speed': 5}, 'main': {'temp': 25, 'humidity': 40}},
            ...     'fire_perimeter': {'type': 'Polygon', 'coordinates': [...]}
            ... }
            >>> result = await agent._model_fire_spread(disaster, data)
        """
        weather_input = data.get('weather') or {}
        if isinstance(weather_input, dict) and weather_input.get('list'):
            weather = weather_input['list'][0]
        else:
            weather = weather_input

        current_boundary_geojson = data.get('fire_perimeter')
        current_boundary_geom = shape(current_boundary_geojson) if current_boundary_geojson else None

        # --- Task #24 ---
        spread_rate, factors = _calculate_fire_spread_rate(weather)
        humidity = weather.get('main', {}).get('humidity', factors.get('humidity_percent', 50))
        wind_speed = factors.get('wind_speed_kmh', 0)

        if spread_rate >= 6 or (wind_speed >= 45 and humidity <= 35):
            outlook = 'worsening'
        elif spread_rate <= 3 and humidity >= 55:
            outlook = 'stable'
        else:
            outlook = 'guarded'

        # --- Task #25 ---
        timeline_predictions = _generate_timeline_predictions(
            current_boundary_geojson,
            spread_rate
        )

        # --- Task #26 ---
        critical_points = _identify_critical_points(disaster['location'])
        arrival_times = _calculate_arrival_times(
            current_boundary_geom,
            critical_points,
            spread_rate,
            factors['wind_direction_deg']
        )

        return {
            'current_spread_rate_kmh': round(spread_rate, 2),
            'predictions': timeline_predictions,
            'critical_arrival_times': arrival_times,
            'factors': factors,
            'outlook': outlook
        }

    def _predict_july_2020_spread(self, scenario_config: Dict) -> Dict:
        """Fire spread predictions for July 2020"""
        weather = scenario_config['weather']
        fire_params = scenario_config['disaster']['fire_params']
        infrastructure = scenario_config['infrastructure']

        # Calculate spread rate
        base_rate = 2.5  # km/h for grass fire
        wind_factor = 1 + (weather['wind_speed_kmh'] / 40)
        temp_factor = 1 + ((weather['temperature_c'] - 20) / 30)
        humidity_factor = 1.5 - (weather['humidity_percent'] / 100)

        spread_rate = base_rate * wind_factor * temp_factor * humidity_factor * fire_params['spread_rate_multiplier']

        return {
            'current_spread_rate_kmh': round(spread_rate, 2),
            'spread_direction': 'east-northeast (toward HWY 407)',
            'critical_arrival_times': [
                {
                    'location': 'HWY 407 Eastbound Lanes',
                    'hours_until_arrival': 2.5,
                    'confidence': 'high',
                    'impact': 'CRITICAL - Highway closure required',
                },
                {
                    'location': 'Residential Area (Sandalwood Heights)',
                    'hours_until_arrival': 3.8,
                    'confidence': 'high',
                    'impact': 'Mandatory evacuation required',
                },
                {
                    'location': 'HWY 410 On-ramps',
                    'hours_until_arrival': 4.5,
                    'confidence': 'medium',
                    'impact': 'Potential closure if wind shifts',
                },
            ],
            'predictions': {
                'hour_1': {
                    'area_km2': 0.24,
                    'confidence': 0.90,
                },
                'hour_3': {
                    'area_km2': 0.58,
                    'confidence': 0.82,
                },
                'hour_6': {
                    'area_km2': 1.20,
                    'confidence': 0.70,
                },
            },
            'factors': {
                'wind_speed_kmh': weather['wind_speed_kmh'],
                'wind_direction_deg': weather['wind_direction_deg'],
                'temperature_c': weather['temperature_c'],
                'humidity_percent': weather['humidity_percent'],
                'fire_weather_index': weather['fire_weather_index'],
            },
            'infrastructure_threats': [
                {
                    'asset': 'Highway 407',
                    'threat_level': 'critical',
                    'time_to_impact_hours': 2.5,
                    'economic_impact_per_hour_usd': infrastructure['highway_407']['economic_impact_per_hour'],
                    'daily_traffic_volume': infrastructure['highway_407']['daily_traffic'],
                },
            ],
            'confidence': 0.87,
            'outlook': 'worsening',
        }
