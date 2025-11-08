from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pyproj import Geod
from shapely.geometry import shape

from .base_agent import BaseAgent


class DamageAssessmentAgent(BaseAgent):
    """Estimate impacted area and severity from satellite observations."""

    async def analyze(self, satellite_imagery: Optional[Dict[str, Any]], disaster_type: str) -> Dict[str, Any]:
        self._log(f"Analyzing {disaster_type} damage from satellite data")

        if not satellite_imagery:
            return self._empty_result()

        perimeter = satellite_imagery.get("fire_perimeter")
        area_km2 = self._calculate_polygon_area(perimeter) if perimeter else 0.0
        thermal_intensity = satellite_imagery.get("thermal_intensity", 0)
        severity = self._calculate_severity(thermal_intensity)

        return {
            "disaster_type": disaster_type,
            "affected_area_km2": area_km2,
            "fire_perimeter": perimeter,
            "thermal_intensity": thermal_intensity,
            "severity": severity,
            "analysis_time": datetime.utcnow().isoformat(),
        }

    def _calculate_polygon_area(self, polygon: Optional[Dict[str, Any]]) -> float:
        """Calculate area of a GeoJSON polygon in km²."""
        if not polygon:
            return 0.0

        geom = shape(polygon)
        geod = Geod(ellps="WGS84")
        area_m2, _ = geod.geometry_area_perimeter(geom)
        return abs(area_m2) / 1_000_000

    def _calculate_severity(self, thermal_intensity: float) -> str:
        if thermal_intensity >= 400:
            return "extreme"
        if thermal_intensity >= 350:
            return "high"
        if thermal_intensity >= 300:
            return "moderate"
        return "low"

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "disaster_type": None,
            "affected_area_km2": 0.0,
            "fire_perimeter": None,
            "thermal_intensity": 0.0,
            "severity": "unknown",
            "analysis_time": datetime.utcnow().isoformat(),
        }
