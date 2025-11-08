from .base_agent import BaseAgent
import requests
import aiohttp
import asyncio
from typing import Dict, List, Any

class RoutingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.osrm_url = "http://router.project-osrm.org"
    
    async def analyze(self, location: Dict, roads: Dict, danger_zone_geom) -> Dict:
        """
        Plan optimal evacuation routes
        'danger_zone_geom' is a Shapely object from the DamageAssessmentAgent
        """
        self._log("Planning evacuation routes")
        
        # Define safe zones (hardcoded for demo)
        safe_zones = self._identify_safe_zones(location, danger_zone_geom)
        
        # Find evacuation origins (e.g., centroids from PopulationImpactAgent)
        origins = self._get_evacuation_origins(danger_zone_geom)
        
        # Calculate routes for each origin
        routes = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for origin in origins:
                tasks.append(self._calculate_best_route(session, origin, safe_zones))
            
            calculated_routes = await asyncio.gather(*tasks)
            routes = [r for r in calculated_routes if r is not None]
        
        # Estimate total evacuation time
        evacuation_time = self._estimate_evacuation_time(routes)
        
        return {
            'routes': routes,
            'safe_zones': safe_zones,
            'estimated_evacuation_time_minutes': evacuation_time,
            'primary_route': routes[0] if routes else None,
            'alternate_routes': routes[1:] if len(routes) > 1 else []
        }
    
    async def _calculate_best_route(self, session: aiohttp.ClientSession, origin: Dict, safe_zones: List[Dict]) -> Dict:
        """Use OSRM to calculate optimal route"""
        best_route = None
        best_time = float('inf')
        
        origin_coords = f"{origin['lon']},{origin['lat']}"
        
        for safe_zone in safe_zones:
            dest_coords = f"{safe_zone['lon']},{safe_zone['lat']}"
            url = f"{self.osrm_url}/route/v1/driving/{origin_coords};{dest_coords}"
            params = {'overview': 'full', 'geometries': 'geojson'}
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        continue
                    data = await response.json()
                    route = data['routes'][0]
                    
                    if route['duration'] < best_time:
                        best_time = route['duration']
                        best_route = {
                            'origin': origin,
                            'destination': safe_zone,
                            'path': route['geometry'],  # GeoJSON LineString
                            'distance_km': route['distance'] / 1000,
                            'time_minutes': route['duration'] / 60
                        }
            except Exception as e:
                self._log(f"OSRM request failed: {e}")
        
        return best_route
    
    def _identify_safe_zones(self, location: Dict, danger_zone) -> List[Dict]:
        """Identify safe evacuation destinations"""
        # Query for community centers, arenas, schools outside danger zone
        # Simplified for demo
        all_zones = [
            {'name': 'Brampton Soccer Centre', 'lat': 43.7150, 'lon': -79.8400, 'capacity': 2000},
            {'name': 'CAA Centre', 'lat': 43.7300, 'lon': -79.7500, 'capacity': 5000}
        ]
        # In a real app, you'd filter these by distance and ensure they aren't *in* the danger_zone
        return all_zones

    def _get_evacuation_origins(self, danger_zone) -> List[Dict]:
        """Get centroids of affected areas"""
        # For demo, we can just use the centroid of the danger zone
        if danger_zone is None:
            return []
        centroid = danger_zone.centroid
        return [{'name': 'Affected Area Centroid', 'lat': centroid.y, 'lon': centroid.x}]

    def _estimate_evacuation_time(self, routes: List[Dict]) -> float:
        """Estimate overall evac time (e.g., max route time)"""
        if not routes:
            return 0.0
        return max(r['time_minutes'] for r in routes)