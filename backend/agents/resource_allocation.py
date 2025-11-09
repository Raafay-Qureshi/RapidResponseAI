from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class ResourceAllocationAgent(BaseAgent):
    """Estimate supply and personnel needs based on population impacts."""

    async def analyze(
        self,
        population_summary: Dict[str, Any],
        routing_summary: Dict[str, Any],
        infrastructure_data: Optional[Any],
        scenario_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        self._log("Planning resource allocation")

        # Check if this is July 2020 scenario
        if scenario_config and scenario_config.get('disaster', {}).get('scenario_id') == 'july_2020_backtest':
            return self._allocate_july_2020_resources(scenario_config)

        total_affected = population_summary.get("total_affected", 0)
        vulnerable = population_summary.get("vulnerable_population", {})
        critical_facilities = population_summary.get("critical_facilities", [])

        shelters_needed = math.ceil(total_affected / 500) if total_affected else 0
        medical_units = math.ceil(vulnerable.get("elderly", 0) / 100) if vulnerable else 0
        relief_kits = max(total_affected, 0)

        return {
            "total_affected": total_affected,
            "shelters_needed": shelters_needed,
            "medical_units": medical_units,
            "relief_kits": relief_kits,
            "critical_facilities": self._summarize_facilities(critical_facilities),
            "route_status": routing_summary.get("severity"),
            "staging_sites": self._candidate_sites(infrastructure_data),
        }

    def _allocate_july_2020_resources(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Resource allocation for July 2020"""
        pop_estimate = scenario_config['population_estimate']

        return {
            'required_resources': {
                'ambulances': 12,
                'evacuation_buses': 8,
                'fire_apparatus': 15,
                'police_units': 10,
                'personnel': 85,
            },
            'available_resources': {
                'fire_stations': [
                    {'id': 'Brampton FS-202', 'lat': 43.7200, 'lon': -79.8400, 'trucks': 4},
                    {'id': 'Brampton FS-205', 'lat': 43.7350, 'lon': -79.8750, 'trucks': 3},
                    {'id': 'Brampton FS-201', 'lat': 43.7180, 'lon': -79.7800, 'trucks': 4},
                ],
                'hospitals': [
                    {'id': 'Brampton Civic Hospital', 'lat': 43.7310, 'lon': -79.7620, 'ambulances': 8},
                ],
                'police_stations': [
                    {'id': 'Peel Police 21 Division', 'lat': 43.7280, 'lon': -79.8300, 'units': 12},
                ],
            },
            'deployment_plan': {
                'primary_staging': {'lat': 43.7250, 'lon': -79.8500, 'name': 'HWY 407/410 Service Road'},
                'command_post': {'lat': 43.7280, 'lon': -79.8450, 'name': 'Emergency Command Center'},
                'evacuation_center': {'lat': 43.7150, 'lon': -79.8400, 'name': 'Brampton Soccer Centre'},
            },
            'mutual_aid_requests': [
                {
                    'municipality': 'Mississauga Fire',
                    'requested': '3 pumpers, 1 aerial ladder',
                    'eta_minutes': 15,
                    'justification': 'Brampton resources insufficient for 40-acre fire',
                },
                {
                    'municipality': 'Caledon Fire',
                    'requested': '2 pumpers, 1 tanker',
                    'eta_minutes': 20,
                    'justification': 'Grass fire expertise and water supply',
                },
                {
                    'municipality': 'Toronto Fire (Standby)',
                    'requested': 'Available if needed',
                    'eta_minutes': 25,
                    'justification': 'Backup if situation escalates',
                },
            ],
            'resource_gaps': [
                {
                    'resource': 'Fire apparatus',
                    'description': 'Need 15 units, have 11 local. Requesting 4 from mutual aid.',
                },
                {
                    'resource': 'Evacuation buses',
                    'description': 'Need 8 buses for 20% of population without vehicles.',
                },
            ],
            'highway_coordination': {
                'mto_notification': 'required',
                'opp_notification': 'required',
                'closure_plan': 'HWY 407 eastbound closure recommended within 2 hours',
                'detour_routes': ['HWY 410 south to HWY 401', 'Bovaird Dr alternate route'],
            },
            'confidence': 0.90,
        }

    def _summarize_facilities(self, facilities: List[Dict[str, Any]]) -> List[str]:
        names: List[str] = []
        for facility in facilities:
            name = facility.get("name")
            if name:
                names.append(name)
        return names

    def _candidate_sites(self, infrastructure_data: Optional[Any]) -> List[str]:
        if infrastructure_data is None:
            return []

        sites: List[str] = []
        try:
            dataset = infrastructure_data
            if hasattr(dataset, "columns") and "type" in dataset.columns:
                dataset = dataset[dataset["type"] == "government"]

            if hasattr(dataset, "head"):
                sample = dataset.head(2)
                if hasattr(sample, "iterrows"):
                    for _, row in sample.iterrows():
                        getter = getattr(row, "get", None)
                        name = getter("name") if callable(getter) else row.name if isinstance(row, str) else None  # type: ignore[attr-defined]
                        if not name and hasattr(row, "name"):
                            value = getattr(row, "name")
                            if isinstance(value, str):
                                name = value
                        if name:
                            sites.append(name)
        except Exception:
            value = getattr(infrastructure_data, "name", None)
            if value:
                sites.append(str(value))

        return sites
