from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class RoutingAgent(BaseAgent):
    """Plan evacuation routes using available road network information."""

    async def analyze(
        self,
        roads_data: Optional[Any],
        infrastructure_data: Optional[Any],
        damage_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._log("Planning evacuation routes")

        severity = damage_summary.get("severity", "unknown")
        affected_area = damage_summary.get("affected_area_km2", 0)

        status = "monitor"
        if severity in ("low", "unknown"):
            status = "open"
        elif severity == "extreme":
            status = "closed"

        routes = [
            {
                "name": "Primary Evacuation Corridor",
                "status": status,
                "distance_km": round(max(affected_area, 5), 1),
                "notes": f"Route planned with severity '{severity}'.",
            },
            {
                "name": "Secondary Relief Route",
                "status": "open" if status != "closed" else "monitor",
                "distance_km": round(max(affected_area / 2, 3), 1),
                "notes": "Alternative path for supply and medical teams.",
            },
        ]

        return {
            "severity": severity,
            "priority_routes": routes,
            "infrastructure_used": self._summarize_infrastructure(infrastructure_data),
        }

    def _summarize_infrastructure(self, infrastructure_data: Optional[Any]) -> List[str]:
        """Extract a short list of infrastructure names if data is available."""
        if infrastructure_data is None:
            return []

        names: List[str] = []
        try:
            head = infrastructure_data.head(3)
            for _, row in head.iterrows():
                if "name" in row:
                    names.append(row["name"])
        except AttributeError:
            extracted = getattr(infrastructure_data, "name", None)
            if extracted:
                names.append(str(extracted))

        return names
