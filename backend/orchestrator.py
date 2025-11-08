from __future__ import annotations

import asyncio
import json
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

        prediction_context = {
            "type": disaster.get("type", "unknown"),
            "location": disaster.get("location", {}),
        }
        prediction_inputs = {
            "weather": data.get("weather_forecast") or {},
            "fire_perimeter": damage_result.get("fire_perimeter"),
        }

        prediction_result = await self.agents["prediction"].analyze(
            prediction_context,
            prediction_inputs,
        )

        return {
            "damage": damage_result,
            "population": population_result,
            "routing": routing_result,
            "resource": resource_result,
            "prediction": prediction_result,
        }

    def _build_master_prompt(self, context: Dict[str, Any]) -> str:
        """Build the master prompt for the LLM synthesis step."""
        agent_results = context.get("agent_outputs", {})
        damage_data = json.dumps(agent_results.get("damage", {}), indent=2)
        population_data = json.dumps(agent_results.get("population", {}), indent=2)
        prediction_data = json.dumps(agent_results.get("prediction", {}), indent=2)
        routing_data = json.dumps(agent_results.get("routing", {}), indent=2)
        resource_data = json.dumps(agent_results.get("resource", {}), indent=2)

        disaster_type = context.get("disaster_type", "unknown incident")
        location = context.get("location", "unknown location")

        prompt = f"""
You are "RapidResponseAI," an expert-level emergency response coordinator for the City of Brampton, Ontario. Your mission is to synthesize raw data from 5 specialized AI agents into a clear, actionable, human-readable emergency plan.
The incident is a **{disaster_type}** detected at **{location}**.
Here is the raw data from your 5 agents:
### AGENT 1: DAMAGE ASSESSMENT ###
{damage_data}
### AGENT 2: POPULATION IMPACT ###
{population_data}
### AGENT 3: PREDICTION & TIMELINE ###
{prediction_data}
### AGENT 4: EVACUATION ROUTING ###
{routing_data}
### AGENT 5: RESOURCE ALLOCATION ###
{resource_data}
---
**YOUR TASK:**
Generate the complete emergency response plan. The plan MUST be formatted EXACTLY as follows. Use the specified headers with `###` delimiters. Be specific, actionable, and use the exact data provided by the agents (e.g., population numbers, km/h spread rate, highway names).
### EXECUTIVE SUMMARY ###
(Write a 2-3 sentence summary of the most critical information: What is happening, who is at immediate risk, and the #1 priority action.)
### SITUATION OVERVIEW ###
(Write a detailed 2-paragraph analysis of the situation. Combine the data from the Damage, Population, and Prediction agents to paint a clear picture of the threat.)
### COMMUNICATION TEMPLATES (ENGLISH) ###
(Write a clear, concise public safety alert for Twitter/X based on the agent data. Use clear instructions.)
### COMMUNICATION TEMPLATES (PUNJABI) ###
(Translate the English template into Punjabi. Be accurate and respectful.)
### COMMUNICATION TEMPLATES (HINDI) ###
(Translate the English template into Hindi. Be accurate and respectful.)
---
"""
        return prompt

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
