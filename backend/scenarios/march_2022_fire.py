"""
March 27, 2022 Conestoga Drive Residential Fire Scenario Configuration

Historical Event:
- Date: March 27, 2022, ~2:00 AM
- Location: Conestoga Drive, Brampton (Kennedy Rd & Sandalwood Parkway area)
- Type: Urban Residential Fire (three-alarm)
- Size: Single-family home (<0.5 acre)
- Severity: High - rapid spread, heavy smoke/flames
- Casualties: 5 deaths (family of 5), grandmother hospitalized
- Response: Multiple fire stations, 4 rescues performed
- Investigation: Under investigation, possible non-working smoke alarms

This configuration represents what RapidResponseAI would have detected
through satellite thermal anomalies and smoke detection, potentially
providing early warning before the fire escalated.
"""

from datetime import datetime
from typing import Dict, Any

# Historical fire location (Conestoga Drive area)
MARCH_2022_LOCATION = {
    'lat': 43.7091,  # Kennedy Rd & Sandalwood Parkway area
    'lon': -79.7358,
    'description': 'Conestoga Drive, residential neighborhood',
    'address': 'Conestoga Drive, Brampton, ON L6R',
}

# Historical weather conditions (early morning, late March)
MARCH_2022_WEATHER = {
    'temperature_c': 2,       # Cool early morning
    'humidity_percent': 65,   # Moderate humidity
    'wind_speed_kmh': 15,     # Moderate wind
    'wind_direction_deg': 180, # Southerly wind
    'conditions': 'clear',
    'fire_weather_index': 'low',  # Urban fire, not weather-driven
    'description': 'Early morning, cool conditions',
}

# Initial fire parameters
MARCH_2022_FIRE_PARAMS = {
    'initial_size_acres': 0.25,  # Single residential home
    'initial_size_km2': 0.001,   # ~0.25 acres
    'fire_type': 'residential',   # Urban residential
    'fuel_type': 'structure',
    'ignition_source': 'under_investigation',
    'spread_rate_multiplier': 1.5,  # Rapid spread within structure
}

# Fire perimeter polygon (single home footprint)
MARCH_2022_FIRE_PERIMETER = {
    'type': 'Feature',
    'geometry': {
        'type': 'Polygon',
        'coordinates': [[
            [-79.7368, 43.7086],  # SW corner
            [-79.7348, 43.7086],  # SE corner
            [-79.7348, 43.7096],  # NE corner
            [-79.7368, 43.7096],  # NW corner
            [-79.7368, 43.7086],  # Close polygon
        ]],
    },
    'properties': {
        'size_acres': 0.25,
        'size_km2': 0.001,
        'perimeter_m': 80,
    },
}

# Expected population impact (immediate neighborhood)
MARCH_2022_POPULATION_ESTIMATE = {
    'total_affected': 850,  # Immediate neighborhood
    'immediate_danger': 12,  # Residents in affected home and adjacent
    'evacuation_recommended': 150,  # Surrounding homes due to smoke
    'vulnerable_elderly': 95,
    'vulnerable_children': 180,
}

# Critical infrastructure at risk
MARCH_2022_INFRASTRUCTURE = {
    'residential_block': {
        'type': 'residential_neighborhood',
        'impact': 'immediate evacuation',
        'homes_at_risk': 8,  # Adjacent homes
        'density': 'high',
    },
    'kennedy_road': {
        'type': 'major_arterial',
        'impact': 'potential closure for emergency access',
        'daily_traffic': 35000,
    },
    'sandalwood_parkway': {
        'type': 'collector_road',
        'impact': 'potential closure',
        'daily_traffic': 15000,
    },
}

# Historical response (what actually happened)
MARCH_2022_ACTUAL_RESPONSE = {
    'first_911_call_time': '02:00',  # Early morning
    'response_time_minutes': 5,
    'alarm_level': '3',  # Three-alarm fire
    'units_dispatched': 'Multiple stations from Brampton Fire',
    'rescues_performed': 4,
    'casualties': {
        'deaths': 5,
        'injuries': 1,  # Grandmother hospitalized
        'escaped_unharmed': 2,
    },
    'cause': 'Under investigation - possible non-working smoke alarms',
    'lessons': 'Importance of working smoke alarms and early detection',
}


class March2022Scenario:
    """March 2022 residential fire scenario configuration"""

    def __init__(self):
        self.scenario_id = 'march_2022_backtest'
        self.name = 'March 2022 Conestoga Drive Fire'
        self.description = 'Three-alarm residential fire with casualties'

    def get_disaster_config(self) -> Dict[str, Any]:
        """Get complete disaster configuration"""
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'type': 'fire',
            'subtype': 'residential',
            'location': MARCH_2022_LOCATION,
            'severity': 'critical',  # High casualties
            'fire_params': MARCH_2022_FIRE_PARAMS,
            'metadata': {
                'historical': True,
                'date': '2022-03-27',
                'time': '02:00',
                'purpose': 'early_detection_demonstration',
                'description': 'Demonstrates satellite thermal detection capability',
            },
        }

    def get_weather_config(self) -> Dict[str, Any]:
        """Get weather conditions for this scenario"""
        return MARCH_2022_WEATHER

    def get_fire_perimeter(self) -> Dict[str, Any]:
        """Get initial fire perimeter"""
        return MARCH_2022_FIRE_PERIMETER

    def get_expected_population_impact(self) -> Dict[str, Any]:
        """Get expected population impact"""
        return MARCH_2022_POPULATION_ESTIMATE

    def get_infrastructure_at_risk(self) -> Dict[str, Any]:
        """Get critical infrastructure data"""
        return MARCH_2022_INFRASTRUCTURE

    def get_historical_response(self) -> Dict[str, Any]:
        """Get what actually happened (for comparison)"""
        return MARCH_2022_ACTUAL_RESPONSE

    def validate(self) -> bool:
        """Validate scenario configuration"""
        try:
            # Check required fields exist
            assert MARCH_2022_LOCATION['lat'] is not None
            assert MARCH_2022_LOCATION['lon'] is not None
            assert MARCH_2022_FIRE_PARAMS['initial_size_km2'] > 0
            assert MARCH_2022_WEATHER['temperature_c'] is not None

            # Check coordinates are in Brampton area
            assert 43.6 < MARCH_2022_LOCATION['lat'] < 43.8
            assert -80.0 < MARCH_2022_LOCATION['lon'] < -79.6

            print(f"[{self.scenario_id}] Validation passed ✓")
            return True

        except AssertionError as e:
            print(f"[{self.scenario_id}] Validation failed: {e}")
            return False


# Singleton instance
march_2022_scenario = March2022Scenario()


def load_march_2022_scenario() -> Dict[str, Any]:
    """
    Load the March 2022 scenario configuration

    Returns:
        Complete scenario configuration dictionary
    """
    scenario = march_2022_scenario

    # Validate before returning
    if not scenario.validate():
        raise ValueError("March 2022 scenario validation failed")

    return {
        'disaster': scenario.get_disaster_config(),
        'weather': scenario.get_weather_config(),
        'fire_perimeter': scenario.get_fire_perimeter(),
        'population_estimate': scenario.get_expected_population_impact(),
        'infrastructure': scenario.get_infrastructure_at_risk(),
        'historical_comparison': scenario.get_historical_response(),
    }


# Helper function for orchestrator integration
def is_march_2022_scenario(disaster_data: Dict) -> bool:
    """
    Check if incoming disaster is the March 2022 scenario

    Args:
        disaster_data: Disaster trigger data from frontend

    Returns:
        True if this is the March 2022 scenario
    """
    metadata = disaster_data.get('metadata', {})
    scenario = metadata.get('scenario', '')

    # Check for March 2022 identifiers
    return (
        scenario == 'march_2022_backtest' or
        metadata.get('description', '').lower().find('march 2022') != -1 or
        metadata.get('description', '').lower().find('conestoga') != -1 or
        (
            abs(disaster_data.get('location', {}).get('lat', 0) - MARCH_2022_LOCATION['lat']) < 0.001 and
            abs(disaster_data.get('location', {}).get('lon', 0) - MARCH_2022_LOCATION['lon']) < 0.001
        )
    )