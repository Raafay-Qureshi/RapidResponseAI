from .base_agent import BaseAgent
from typing import Dict
from datetime import datetime


class DamageAssessmentAgent(BaseAgent):
    async def analyze(self, satellite_imagery: Dict, disaster_type: str, scenario_config: Dict = None, disaster_location: Dict = None) -> Dict:
        """
        Analyze satellite imagery to assess damage extent

        For hackathon: Simplified using bounding box calculations
        Production: Would use computer vision models
        """
        self._log(f"Analyzing {disaster_type} damage from satellite data")

        # Check if this is July 2020 scenario
        if scenario_config and scenario_config.get('disaster', {}).get('scenario_id') == 'july_2020_backtest':
            self._log("Using July 2020 scenario parameters")
            return self._assess_july_2020_fire(scenario_config)

        if disaster_type == "wildfire":
            return await self._assess_fire_damage(satellite_imagery, disaster_location)
        elif disaster_type == "flood":
            return await self._assess_flood_damage(satellite_imagery)
        else:
            raise ValueError(f"Unknown disaster type: {disaster_type}")
    
    async def _assess_fire_damage(self, imagery: Dict, disaster_location: Dict = None) -> Dict:
        """Assess fire damage extent"""
        # In real system: Use thermal bands, NDVI analysis, etc.
        # For demo: Simulate based on NASA FIRMS data
        
        if not imagery or not imagery.get('fire_perimeter'):
            # No satellite data available - generate estimated fire perimeter
            self._log("No satellite data - generating estimated fire perimeter")
            return self._generate_estimated_fire_perimeter(disaster_location)
        
        fire_perimeter = imagery.get('fire_perimeter')  # GeoJSON polygon
        
        # Calculate area
        area_km2 = self._calculate_polygon_area(fire_perimeter)
        
        # Estimate severity based on thermal data
        thermal_intensity = imagery.get('thermal_intensity', 350)  # Kelvin
        severity = self._calculate_severity(thermal_intensity)
        
        return {
            'affected_area_km2': area_km2,
            'fire_perimeter': fire_perimeter,
            'severity': severity,
            'confidence': 0.92,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _calculate_polygon_area(self, polygon: Dict) -> float:
        """Calculate area of GeoJSON polygon in km²"""
        if not polygon:
            return 0.0
            
        from shapely.geometry import shape
        from pyproj import Geod
        
        geom = shape(polygon)
        geod = Geod(ellps="WGS84")
        area_m2, _ = geod.geometry_area_perimeter(geom)
        return abs(area_m2) / 1_000_000  # Convert to km²
    
    def _calculate_severity(self, thermal_intensity: float) -> str:
        """Classify severity based on thermal intensity"""
        if thermal_intensity > 400:
            return "extreme"
        elif thermal_intensity > 370:
            return "high"
        elif thermal_intensity >= 340:
            return "moderate"
        else:
            return "low"
            
    def _assess_july_2020_fire(self, scenario_config: Dict) -> Dict:
        """Assess July 2020 specific fire"""
        fire_params = scenario_config['disaster']['fire_params']
        fire_perimeter = scenario_config['fire_perimeter']

        return {
            'affected_area_km2': fire_params['initial_size_km2'],
            'affected_area_acres': fire_params['initial_size_acres'],
            'fire_perimeter': fire_perimeter,
            'fire_type': 'WUI',
            'fuel_type': 'grass_brush',
            'severity': 'high',
            'spread_potential': 'extreme',
            'confidence': 0.92,
            'analysis_notes': 'Fast-moving grass fire near major infrastructure',
            'analysis_time': datetime.now().isoformat(),
        }
    
    def _generate_estimated_fire_perimeter(self, disaster_location: Dict = None) -> Dict:
        """Generate estimated fire perimeter when satellite data unavailable"""
        from shapely.geometry import Point
        
        # Get actual disaster location or use default
        if disaster_location and 'lat' in disaster_location and 'lon' in disaster_location:
            center_lon = disaster_location['lon']
            center_lat = disaster_location['lat']
            self._log(f"Generating fire perimeter at {center_lat}, {center_lon}")
        else:
            # Default to HWY 407/410 interchange if no location provided
            center_lon = -79.8620
            center_lat = 43.7315
            self._log("Using default fire location (HWY 407/410)")
        
        # Create a realistic fire perimeter (approximately 0.5 km radius = 0.785 km²)
        # This represents a medium-sized urban fire
        center = Point(center_lon, center_lat)
        radius_degrees = 0.0045  # Approximately 0.5 km at mid-latitudes
        
        # Create circle as fire perimeter
        fire_polygon = center.buffer(radius_degrees)
        
        # Convert to GeoJSON
        fire_perimeter = {
            "type": "Polygon",
            "coordinates": [list(fire_polygon.exterior.coords)]
        }
        
        # Calculate area
        area_km2 = self._calculate_polygon_area(fire_perimeter)
        
        return {
            'affected_area_km2': area_km2,
            'affected_area_acres': area_km2 * 247.105,  # Convert to acres
            'fire_perimeter': fire_perimeter,
            'severity': 'high',
            'spread_potential': 'moderate',
            'confidence': 0.60,  # Lower confidence for estimates
            'analysis_time': datetime.now().isoformat(),
            '_estimated': True,
            '_estimation_note': 'Fire perimeter estimated due to unavailable satellite data. Assumes 0.5km radius urban fire.',
        }

    async def _assess_flood_damage(self, imagery: Dict) -> Dict:
        # Placeholder for hackathon
        self._log("Flood assessment not implemented")
        return {'status': 'not_implemented'}
