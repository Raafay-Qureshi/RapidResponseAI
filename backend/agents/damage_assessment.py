from .base_agent import BaseAgent
from typing import Dict
from datetime import datetime


class DamageAssessmentAgent(BaseAgent):
    async def analyze(self, satellite_imagery: Dict, disaster_type: str) -> Dict:
        """
        Analyze satellite imagery to assess damage extent
        
        For hackathon: Simplified using bounding box calculations
        Production: Would use computer vision models
        """
        self._log(f"Analyzing {disaster_type} damage from satellite data")
        
        if disaster_type == "wildfire":
            return await self._assess_fire_damage(satellite_imagery)
        elif disaster_type == "flood":
            return await self._assess_flood_damage(satellite_imagery)
        else:
            raise ValueError(f"Unknown disaster type: {disaster_type}")
    
    async def _assess_fire_damage(self, imagery: Dict) -> Dict:
        """Assess fire damage extent"""
        # In real system: Use thermal bands, NDVI analysis, etc.
        # For demo: Simulate based on NASA FIRMS data
        
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
            
    async def _assess_flood_damage(self, imagery: Dict) -> Dict:
        # Placeholder for hackathon
        self._log("Flood assessment not implemented")
        return {'status': 'not_implemented'}
