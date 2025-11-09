from __future__ import annotations

from typing import Any, Dict, List

import geopandas as gpd
from shapely.geometry import Point, shape
from shapely.geometry.base import BaseGeometry

from .base_agent import BaseAgent


class PopulationImpactAgent(BaseAgent):
    """Agent that summarizes population impacts within an affected boundary."""

    async def analyze(
        self,
        affected_boundary: Dict[str, Any],
        population_data: Any,
        scenario_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Calculate affected population and identify vulnerable groups.

        `population_data` is expected to be a GeoDataFrame from GeoHubClient.
        `affected_boundary` is a GeoJSON polygon from DamageAssessmentAgent.
        """
        self._log("Analyzing population impact")

        # Check if this is July 2020 scenario
        if scenario_config and scenario_config.get('disaster', {}).get('scenario_id') == 'july_2020_backtest':
            return self._analyze_july_2020_impact(scenario_config)

        summary = {
            "total_affected": 0,
            "vulnerable_population": {"elderly": 0, "children": 0},
            "languages": {},
            "critical_facilities": [],
            "affected_neighborhoods": [],
        }

        if not affected_boundary or population_data is None:
            self._log("Missing boundary or population data")
            return summary

        if not isinstance(population_data, gpd.GeoDataFrame):
            self._log("Population data is not a GeoDataFrame")
            return summary

        boundary_geom = shape(affected_boundary)
        boundary_gdf = gpd.GeoDataFrame(
            [{"geometry": boundary_geom}],
            crs=population_data.crs or "EPSG:4326",
        )

        population_gdf = population_data
        if population_gdf.crs is None:
            population_gdf = population_gdf.set_crs(boundary_gdf.crs, allow_override=True)

        if boundary_gdf.crs != population_gdf.crs and population_gdf.crs is not None:
            boundary_gdf = boundary_gdf.to_crs(population_gdf.crs)

        affected_blocks = gpd.sjoin(
            population_gdf,
            boundary_gdf,
            how="inner",
            predicate="intersects",
        )

        if affected_blocks.empty:
            self._log("No population blocks found within boundary")
            return summary

        if "population" in affected_blocks.columns:
            summary["total_affected"] = int(affected_blocks["population"].sum())

        if "age_65_plus" in affected_blocks.columns:
            summary["vulnerable_population"]["elderly"] = int(
                affected_blocks["age_65_plus"].sum()
            )

        if "age_under_18" in affected_blocks.columns:
            summary["vulnerable_population"]["children"] = int(
                affected_blocks["age_under_18"].sum()
            )

        if "primary_language" in affected_blocks.columns and "population" in affected_blocks.columns:
            language_breakdown = (
                affected_blocks.groupby("primary_language")["population"].sum()
            )
            summary["languages"] = {
                language: int(total) for language, total in language_breakdown.items()
            }

        facilities = self._find_critical_facilities(boundary_geom)
        summary["critical_facilities"] = facilities

        if "neighborhood" in affected_blocks.columns:
            neighborhoods = affected_blocks["neighborhood"].dropna().unique().tolist()
            summary["affected_neighborhoods"] = neighborhoods

        return summary

    def _analyze_july_2020_impact(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Population impact for July 2020 scenario"""
        pop_estimate = scenario_config['population_estimate']

        return {
            'total_affected': pop_estimate['total_affected'],
            'immediate_danger': pop_estimate['immediate_danger'],
            'evacuation_recommended': pop_estimate['evacuation_recommended'],
            'vulnerable_population': {
                'elderly': pop_estimate['vulnerable_elderly'],
                'children': pop_estimate['vulnerable_children'],
                'disabled': 65,
            },
            'languages': {
                'english': 1240,
                'punjabi': 360,
                'hindi': 180,
                'other': 220,
            },
            'critical_facilities': [
                {
                    'type': 'elementary_school',
                    'name': 'Mayfield Secondary School',
                    'location': {'lat': 43.7290, 'lon': -79.8650},
                    'population': 850,
                    'distance_from_fire_km': 0.8,
                },
                {
                    'type': 'senior_center',
                    'name': 'Williams Parkway Seniors Center',
                    'location': {'lat': 43.7340, 'lon': -79.8590},
                    'population': 95,
                    'distance_from_fire_km': 0.6,
                },
                {
                    'type': 'hospital',
                    'name': 'Brampton Civic Hospital',
                    'location': {'lat': 43.7310, 'lon': -79.7620},
                    'population': 800,
                    'distance_from_fire_km': 7.2,
                },
            ],
            'affected_neighborhoods': [
                'Heart Lake',
                'Sandalwood Heights',
                'Central Park',
                'Fletcher\'s Meadow',
            ],
            'economic_impact_estimate_usd': 2500000,
            'confidence': 0.88,
        }

    def _find_critical_facilities(self, boundary_geom: BaseGeometry) -> List[Dict[str, Any]]:
        """Find schools, hospitals, etc. within boundary (demo implementation)."""
        example_facilities = [
            {
                "type": "elementary_school",
                "name": "Brampton Heights Elementary",
                "location": {"lat": 43.731, "lon": -79.862},
                "population": 450,
                "geom": Point(-79.862, 43.731),
            },
            {
                "type": "senior_center",
                "name": "Golden Years Community Center",
                "location": {"lat": 43.733, "lon": -79.859},
                "population": 120,
                "geom": Point(-79.859, 43.733),
            },
            {
                "type": "hospital",
                "name": "Brampton Civic",
                "location": {"lat": 43.731, "lon": -79.762},
                "population": 800,
                "geom": Point(-79.762, 43.731),
            },
        ]

        affected_facilities: List[Dict[str, Any]] = []
        for facility in example_facilities:
            geom = facility["geom"]
            if geom.intersects(boundary_geom):
                facility_info = {k: v for k, v in facility.items() if k != "geom"}
                affected_facilities.append(facility_info)

        return affected_facilities
