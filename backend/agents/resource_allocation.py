from .base_agent import BaseAgent
from typing import Dict, List


class ResourceAllocationAgent(BaseAgent):
    async def analyze(self, population_impact: Dict, infrastructure: Dict) -> Dict:
        """
        Determine resource needs and optimal deployment
        'population_impact' is the output from PopulationImpactAgent
        'infrastructure' is the (static) data from GeoHubClient
        """
        self._log("Planning resource allocation")
        
        # Get population impact data
        affected_population = population_impact.get('total_affected', 0)
        vulnerable_population = population_impact.get('vulnerable_population', {})
        
        # Calculate needs
        ambulances_needed = self._calculate_ambulances(vulnerable_population)
        buses_needed = self._calculate_buses(affected_population)
        personnel_needed = self._calculate_personnel(affected_population)
        
        # Map current resources (hardcoded for demo)
        current_resources = self._map_current_resources()
        
        # In a real app, you'd run an optimization model here.
        # For demo, just listing needs vs. availability is enough.
        
        return {
            'required_resources': {
                'ambulances': ambulances_needed,
                'evacuation_buses': buses_needed,
                'personnel': personnel_needed
            },
            'available_resources': current_resources
            # 'deployment_plan': deployment_plan,
            # 'resource_gaps': self._identify_gaps(current_resources, deployment_plan)
        }
    
    def _calculate_ambulances(self, vulnerable_pop: Dict) -> int:
        """Estimate ambulance needs"""
        elderly = vulnerable_pop.get('elderly', 0)
        disabled = vulnerable_pop.get('disabled', 0)  # Assuming this key exists
        # Assume 1 ambulance per 100 vulnerable individuals
        return max(1, (int(elderly) + int(disabled)) // 100)
    
    def _calculate_buses(self, total_population: int) -> int:
        """Estimate evacuation bus needs"""
        # Assume 80% have cars, 20% need buses
        # Each bus holds ~50 people
        people_needing_buses = total_population * 0.20
        return max(1, int(people_needing_buses / 50))

    def _calculate_personnel(self, total_population: int) -> int:
        """Estimate police/fire personnel needed"""
        # Simple ratio: 1 responder per 200 affected people
        return max(5, int(total_population / 200))
    
    def _map_current_resources(self) -> Dict:
        """Map fire stations, hospitals, ambulance bases"""
        # Query infrastructure databases
        # Simplified for demo
        return {
            'fire_stations': [
                {'id': 'FS-202', 'lat': 43.720, 'lon': -79.840, 'trucks': 3},
                {'id': 'FS-205', 'lat': 43.735, 'lon': -79.875, 'trucks': 2}
            ],
            'hospitals': [
                {'id': 'Brampton Civic', 'lat': 43.731, 'lon': -79.762, 'ambulances': 8}
            ],
            'police_stations': [
                {'id': 'PS-21', 'lat': 43.728, 'lon': -79.830, 'units': 12}
            ]
        }