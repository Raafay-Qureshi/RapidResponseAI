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
    ) -> Dict[str, Any]:
        self._log("Planning resource allocation")

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
