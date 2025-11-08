from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from .data.geohub_client import GeoHubClient
from .data.satellite_client import SatelliteClient
from .data.weather_client import WeatherClient
from .agents.damage_assessment import DamageAssessmentAgent
from .agents.population_impact import PopulationImpactAgent
from .agents.prediction import PredictionAgent
from .agents.resource_allocation import ResourceAllocationAgent
from .agents.routing import RoutingAgent


class DisasterOrchestrator:
    """Coordinate data ingestion and analysis across all agents."""

    def __init__(self, socketio_instance: Any):
        self.active_disasters: Dict[str, Dict[str, Any]] = {}
        self.socketio = socketio_instance

        self.data_clients = {
            "satellite": SatelliteClient(),
            "weather": WeatherClient(),
            "geohub": GeoHubClient(),
        }

        self.agents = {
            "damage": DamageAssessmentAgent(),
            "population": PopulationImpactAgent(),
            "routing": RoutingAgent(),
            "resource": ResourceAllocationAgent(),
            "prediction": PredictionAgent(),
        }

    def create_disaster(self, trigger_data: Dict[str, Any]) -> str:
        """Create new disaster event state."""
        disaster_type = trigger_data.get("type", "event").lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        disaster_id = f"{disaster_type}-{timestamp}-{unique_id}"

        self.active_disasters[disaster_id] = {
            "id": disaster_id,
            "type": trigger_data.get("type"),
            "location": trigger_data.get("location", {}),
            "status": "initializing",
            "created_at": datetime.utcnow().isoformat(),
            "data": {},
            "agent_results": {},
            "plan": None,
            "trigger": trigger_data,
        }

        self._emit("disaster_created", self.active_disasters[disaster_id], room=disaster_id)
        return disaster_id

    def get_disaster(self, disaster_id: str) -> Optional[Dict[str, Any]]:
        return self.active_disasters.get(disaster_id)

    def get_plan(self, disaster_id: str) -> Optional[Dict[str, Any]]:
        disaster = self.active_disasters.get(disaster_id)
        return disaster.get("plan") if disaster else None

    async def process_disaster(self, disaster_id: str) -> Optional[Dict[str, Any]]:
        """Main processing pipeline."""
        disaster = self.active_disasters.get(disaster_id)
        if not disaster:
            raise ValueError(f"Disaster '{disaster_id}' not found")

        try:
            disaster["status"] = "fetching_data"
            self._emit("disaster_status", {"status": "fetching_data"}, room=disaster_id)
            data = await self._fetch_all_data(disaster)
            disaster["data"] = data

            disaster["status"] = "analyzing"
            self._emit("disaster_status", {"status": "analyzing"}, room=disaster_id)
            agent_results = await self._run_agents(disaster, data)
            disaster["agent_results"] = agent_results

            disaster["status"] = "generating_plan"
            self._emit("disaster_status", {"status": "generating_plan"}, room=disaster_id)
            plan = self._synthesize_plan(disaster, agent_results)
            disaster["plan"] = plan
            disaster["status"] = "complete"

            self._emit("disaster_complete", {"plan": plan}, room=disaster_id)
            return plan

        except Exception as exc:
            disaster["status"] = "error"
            disaster["error"] = str(exc)
            self._emit(
                "disaster_error",
                {"disaster_id": disaster_id, "error": str(exc)},
                room=disaster_id,
            )
            raise

    async def _fetch_all_data(self, disaster: Dict[str, Any]) -> Dict[str, Any]:
        location = disaster.get("location", {})

        tasks = {
            "satellite": asyncio.create_task(
                self.data_clients["satellite"].fetch_imagery(location)
            ),
            "weather_current": asyncio.create_task(
                self.data_clients["weather"].fetch_current(location)
            ),
            "weather_forecast": asyncio.create_task(
                self.data_clients["weather"].fetch_forecast(location)
            ),
            "population": asyncio.create_task(
                self.data_clients["geohub"].fetch_population(location)
            ),
            "infrastructure": asyncio.create_task(
                self.data_clients["geohub"].fetch_infrastructure(location)
            ),
            "roads": asyncio.create_task(self.data_clients["geohub"].fetch_roads(location)),
        }

        results: Dict[str, Any] = {}
        for key, task in tasks.items():
            try:
                results[key] = await task
            except Exception as exc:
                results[key] = None
                self._log(f"Failed to fetch {key} data: {exc}")
        return results

    async def _run_agents(
        self,
        disaster: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        damage_result = await self.agents["damage"].analyze(
            data.get("satellite"),
            disaster.get("type", "unknown"),
        )

        population_result = await self.agents["population"].analyze(
            damage_result.get("fire_perimeter"),
            data.get("population"),
        )

        routing_result = await self.agents["routing"].analyze(
            data.get("roads"),
            data.get("infrastructure"),
            damage_result,
        )

        resource_result = await self.agents["resource"].analyze(
            population_result,
            routing_result,
            data.get("infrastructure"),
        )

        prediction_result = await self.agents["prediction"].analyze(
            disaster.get("type", "unknown"),
            data.get("weather_forecast"),
        )

        return {
            "damage": damage_result,
            "population": population_result,
            "routing": routing_result,
            "resource": resource_result,
            "prediction": prediction_result,
        }

    def _synthesize_plan(
        self,
        disaster: Dict[str, Any],
        agent_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        damage = agent_results.get("damage", {})
        population = agent_results.get("population", {})
        routing = agent_results.get("routing", {})
        resources = agent_results.get("resource", {})
        prediction = agent_results.get("prediction", {})

        recommendations = [
            "Deploy rapid assessment teams to confirm satellite findings.",
            "Stage relief supplies near critical facilities highlighted by the population agent.",
            routing.get("priority_routes", [])[0]["notes"]
            if routing.get("priority_routes")
            else "Establish temporary wayfinding signage for evac routes.",
            prediction.get("recommendation", "Review forecast data with meteorology team."),
        ]

        return {
            "disaster_id": disaster["id"],
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "type": disaster.get("type"),
                "status": disaster.get("status"),
                "affected_area_km2": damage.get("affected_area_km2", 0),
                "total_population_impacted": population.get("total_affected", 0),
                "severity": damage.get("severity"),
                "outlook": prediction.get("outlook"),
            },
            "recommendations": recommendations,
            "agent_snapshots": agent_results,
        }

    def _emit(self, event: str, payload: Dict[str, Any], room: Optional[str] = None) -> None:
        if self.socketio:
            self.socketio.emit(event, payload, room=room)

    def _log(self, message: str) -> None:
        print(f"[DisasterOrchestrator] {message}")
