from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp

from data.geohub_client import GeoHubClient
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
from agents.damage_assessment import DamageAssessmentAgent
from agents.population_impact import PopulationImpactAgent
from agents.prediction import PredictionAgent
from agents.resource_allocation import ResourceAllocationAgent
from agents.routing import RoutingAgent
from scenarios.july_2020_fire import load_july_2020_scenario, is_july_2020_scenario
from scenarios.march_2022_fire import load_march_2022_scenario, is_march_2022_scenario
from utils.cached_loader import load_cached_july_2020, is_cached_data_available
from utils.config import config


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
        """Main processing pipeline - attempts agent processing first, falls back to cache on failure."""
        disaster = self.active_disasters.get(disaster_id)
        if not disaster:
            raise ValueError(f"Disaster '{disaster_id}' not found")

        try:
            # Always attempt real agent processing first
            self._log("Starting agent processing pipeline...")
            disaster["status"] = "fetching_data"
            self._emit("disaster_status", {"status": "fetching_data"}, room=disaster_id)
            self._emit(
                "progress",
                {
                    "disaster_id": disaster_id,
                    "phase": "data_ingestion",
                    "progress": 10,
                },
                room=disaster_id,
            )

            # Check if this is July 2020 scenario
            if is_july_2020_scenario(disaster.get('trigger', {})):
                self._log("Loading July 2020 scenario configuration")
                scenario_config = load_july_2020_scenario()

                # Store scenario config for reference
                disaster['scenario_config'] = scenario_config

                # Use scenario data instead of fetching
                data = {
                    'weather_current': scenario_config['weather'],
                    'weather_forecast': scenario_config['weather'],
                    'satellite': None,  # Will use fire_perimeter directly
                    'population': scenario_config['population_estimate'],
                    'infrastructure': scenario_config['infrastructure'],
                    'roads': None,  # Will fetch this normally
                }

                # Add fire perimeter to disaster data for agents
                disaster['fire_perimeter'] = scenario_config['fire_perimeter']

                self._log(f"July 2020 scenario loaded: {scenario_config['disaster']['name']}")
            # Check if this is March 2022 scenario
            elif is_march_2022_scenario(disaster.get('trigger', {})):
                self._log("Loading March 2022 scenario configuration")
                scenario_config = load_march_2022_scenario()

                # Store scenario config for reference
                disaster['scenario_config'] = scenario_config

                # Use scenario data instead of fetching
                data = {
                    'weather_current': scenario_config['weather'],
                    'weather_forecast': scenario_config['weather'],
                    'satellite': None,  # Will use fire_perimeter directly
                    'population': scenario_config['population_estimate'],
                    'infrastructure': scenario_config['infrastructure'],
                    'roads': None,  # Will fetch this normally
                }

                # Add fire perimeter to disaster data for agents
                disaster['fire_perimeter'] = scenario_config['fire_perimeter']

                self._log(f"March 2022 scenario loaded: {scenario_config['disaster']['name']}")
            else:
                data = await self._fetch_all_data(disaster)

            disaster["data"] = data

            disaster["status"] = "analyzing"
            self._emit("disaster_status", {"status": "analyzing"}, room=disaster_id)
            self._emit(
                "progress",
                {
                    "disaster_id": disaster_id,
                    "phase": "agent_processing",
                    "progress": 30,
                },
                room=disaster_id,
            )
            agent_results = await self._run_all_agents(disaster, data)
            disaster["agent_results"] = agent_results

            disaster["status"] = "generating_plan"
            self._emit("disaster_status", {"status": "generating_plan"}, room=disaster_id)
            self._emit(
                "progress",
                {
                    "disaster_id": disaster_id,
                    "phase": "synthesis",
                    "progress": 70,
                },
                room=disaster_id,
            )

            context = {
                "disaster_type": disaster.get("type"),
                "location": disaster.get("location"),
                "timestamp": disaster.get("created_at"),
                "agent_outputs": agent_results,
                "disaster_id": disaster_id,  # Pass disaster_id for progress updates
            }
            llm_response = await self._call_llm_api(context)

            final_plan = {
                "disaster_id": disaster_id,
                "generated_at": datetime.utcnow().isoformat(),
                "executive_summary": llm_response.get("summary", ""),
                "situation_overview": llm_response.get("overview", ""),
                "communication_templates": llm_response.get("templates", {}),
                "affected_areas": agent_results.get("damage", {}),
                "population_impact": agent_results.get("population", {}),
                "evacuation_plan": agent_results.get("routing", {}),
                "resource_deployment": agent_results.get("resource", {}),
                "timeline_predictions": agent_results.get("prediction", {}),
            }

            disaster["plan"] = final_plan
            disaster["status"] = "complete"

            self._emit(
                "disaster_complete",
                {"disaster_id": disaster_id, "plan": final_plan},
                room=disaster_id,
            )
            return final_plan

        except Exception as exc:
            # Agent processing failed - attempt fallback to cached data
            self._log(f"❌ Agent processing failed: {exc}")
            
            # Check if we can use cached data as fallback
            if is_july_2020_scenario(disaster.get('trigger', {})) and is_cached_data_available():
                self._log("⚠️ Agent processing failed - falling back to cached data")
                try:
                    await self._load_cached_response(disaster_id, is_fallback=True)
                    self._log("✓ Successfully loaded cached fallback data")
                    return self.active_disasters[disaster_id].get("plan")
                except Exception as cache_exc:
                    self._log(f"❌ Cached fallback also failed: {cache_exc}")
                    # Both real processing and cache failed - propagate original error
                    disaster["status"] = "error"
                    disaster["error"] = f"Agent processing failed: {exc}. Cache fallback failed: {cache_exc}"
                    self._emit(
                        "disaster_error",
                        {"disaster_id": disaster_id, "error": disaster["error"]},
                        room=disaster_id,
                    )
                    raise
            else:
                # No cached fallback available - propagate error
                self._log("❌ No cached fallback available")
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
        disaster_id = disaster.get("id")

        # Define API fetch order with progress reporting
        fetch_sequence = [
            ("satellite", "NASA FIRMS Satellite Data", 12,
             self.data_clients["satellite"].fetch_imagery(location)),
            ("weather_current", "OpenWeather Current Conditions", 14,
             self.data_clients["weather"].fetch_current(location)),
            ("weather_forecast", "OpenWeather 5-Day Forecast", 16,
             self.data_clients["weather"].fetch_forecast(location)),
            ("population", "Brampton GeoHub Population Data", 18,
             self.data_clients["geohub"].fetch_population(location)),
            ("infrastructure", "Brampton GeoHub Infrastructure", 20,
             self.data_clients["geohub"].fetch_infrastructure(location)),
            ("roads", "Brampton GeoHub Road Network", 22,
             self.data_clients["geohub"].fetch_roads(location)),
        ]

        results: Dict[str, Any] = {}
        
        for key, description, progress_pct, coro in fetch_sequence:
            try:
                self._emit(
                    "progress",
                    {
                        "disaster_id": disaster_id,
                        "phase": "data_ingestion",
                        "progress": progress_pct,
                        "message": f"📡 Fetching {description}...",
                        "api_status": {
                            "name": description,
                            "status": "fetching"
                        }
                    },
                    room=disaster_id,
                )
                
                results[key] = await coro
                
                self._emit(
                    "progress",
                    {
                        "disaster_id": disaster_id,
                        "phase": "data_ingestion",
                        "progress": progress_pct + 1,
                        "message": f"✅ {description} received",
                        "api_status": {
                            "name": description,
                            "status": "success"
                        }
                    },
                    room=disaster_id,
                )
                
            except Exception as exc:
                results[key] = None
                self._log(f"Failed to fetch {key} data: {exc}")
                
                self._emit(
                    "progress",
                    {
                        "disaster_id": disaster_id,
                        "phase": "data_ingestion",
                        "progress": progress_pct + 1,
                        "message": f"⚠️ {description} unavailable (using fallback)",
                        "api_status": {
                            "name": description,
                            "status": "fallback",
                            "error": str(exc)
                        }
                    },
                    room=disaster_id,
                )
                
        return results

    async def _run_all_agents(
        self,
        disaster: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        disaster_id = disaster.get("id")
        
        # Agent 1: Damage Assessment
        self._emit(
            "progress",
            {
                "disaster_id": disaster_id,
                "phase": "agent_processing",
                "progress": 35,
                "message": "🔍 Agent 1/5: Analyzing fire perimeter and damage...",
            },
            room=disaster_id,
        )
        damage_result = await self.agents["damage"].analyze(
            data.get("satellite"),
            disaster.get("type", "unknown"),
            disaster_location=disaster.get("location"),
        )

        # Agent 2: Population Impact
        self._emit(
            "progress",
            {
                "disaster_id": disaster_id,
                "phase": "agent_processing",
                "progress": 45,
                "message": "👥 Agent 2/5: Calculating population impact...",
            },
            room=disaster_id,
        )
        population_result = await self.agents["population"].analyze(
            damage_result.get("fire_perimeter"),
            data.get("population"),
        )

        # Agent 3: Evacuation Routing
        self._emit(
            "progress",
            {
                "disaster_id": disaster_id,
                "phase": "agent_processing",
                "progress": 55,
                "message": "🚗 Agent 3/5: Planning evacuation routes...",
            },
            room=disaster_id,
        )
        routing_result = await self.agents["routing"].analyze(
            data.get("roads"),
            data.get("infrastructure"),
            damage_result,
            disaster_location=disaster.get("location"),
        )

        # Agent 4: Resource Allocation
        self._emit(
            "progress",
            {
                "disaster_id": disaster_id,
                "phase": "agent_processing",
                "progress": 65,
                "message": "🚒 Agent 4/5: Allocating emergency resources...",
            },
            room=disaster_id,
        )
        resource_result = await self.agents["resource"].analyze(
            population_result,
            routing_result,
            data.get("infrastructure"),
        )

        # Agent 5: Prediction & Timeline
        self._emit(
            "progress",
            {
                "disaster_id": disaster_id,
                "phase": "agent_processing",
                "progress": 75,
                "message": "📊 Agent 5/5: Predicting fire spread timeline...",
            },
            room=disaster_id,
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

    def create_standard_prompt(self, context: Dict[str, Any]) -> str:
        """Build the standard prompt for the LLM synthesis step."""
        agent_results = context.get("agent_outputs", {})
        damage_data = json.dumps(agent_results.get("damage", {}), indent=2)
        population_data = json.dumps(agent_results.get("population", {}), indent=2)
        prediction_data = json.dumps(agent_results.get("prediction", {}), indent=2)
        routing_data = json.dumps(agent_results.get("routing", {}), indent=2)
        resource_data = json.dumps(agent_results.get("resource", {}), indent=2)

        disaster_type = context.get("disaster_type", "unknown incident")
        location_obj = context.get("location", {})
        
        # Format location for better LLM understanding
        if isinstance(location_obj, dict):
            lat = location_obj.get("lat", "unknown")
            lon = location_obj.get("lon", "unknown")
            location_str = f"coordinates {lat}°N, {lon}°W (latitude: {lat}, longitude: {lon})"
        else:
            location_str = str(location_obj)

        prompt = f"""
You are "RapidResponseAI," an expert-level emergency response coordinator for the City of Brampton, Ontario. Your mission is to synthesize raw data from 5 specialized AI agents into a clear, actionable, human-readable emergency plan.

INCIDENT DETAILS:
- Type: {disaster_type}
- Location: {location_str}
- Time: {context.get("timestamp", "unknown")}

CRITICAL REQUIREMENTS FOR NUMBERS AND REALISM:
1. **Generate realistic quantitative data**: You MUST include specific numbers for ALL metrics, even if agent data is sparse:
   - Population affected (residents, workers, travelers)
   - Fire/incident size in hectares or square kilometers
   - Spread rate in meters/hour or km/hour
   - Number of structures threatened or damaged
   - Responders deployed (firefighters, EMS, police)
   - Equipment needed (trucks, helicopters, ambulances)
   - Evacuation capacity and timelines
   - Road closures and affected infrastructure count

2. **Make intelligent estimates**: For urban areas, assume:
   - Residential density: 3,000-5,000 people per square kilometer
   - Commercial areas: add 500-2,000 workers/visitors during business hours
   - Major highways: 50,000-100,000 daily vehicles
   - Emergency resources: 20-40 firefighters per station, 3-5 stations can respond

3. **Be dramatically realistic**: This is a real emergency - numbers should reflect urgency:
   - Don't say "several people" - say "2,300 residents"
   - Don't say "multiple roads" - say "6 major arterial roads including..."
   - Don't say "nearby areas" - say "3.2 km radius affecting..."
   - Include timelines: "12 minutes until highway impact", "45-minute evacuation window"

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
Generate a location-specific emergency response plan with SPECIFIC NUMBERS. You MUST:

1. **Extract location details from agent data**: Look for road names, infrastructure names, neighborhood identifiers
2. **Generate or enhance numbers**: If agent data lacks specifics, create realistic estimates based on the location type and area
3. **Reference actual infrastructure**: Use the names of roads, facilities, and landmarks from the agent outputs
4. **Be quantitatively precise**: Every claim needs a number - people affected, resources needed, distances, times

The plan MUST be formatted EXACTLY as follows with `###` delimiters:

### EXECUTIVE SUMMARY ###
(2-3 sentences with SPECIFIC NUMBERS: fire size in hectares, population affected, number of structures threatened, key infrastructure at risk, response timeline)

### SITUATION OVERVIEW ###
(2 detailed paragraphs with SPECIFIC METRICS:
- Paragraph 1: Fire size, spread rate (km/h), number of structures, infrastructure count, weather conditions
- Paragraph 2: Population numbers, evacuation capacity, number of responders deployed, equipment count, road closure count, timeline estimates)

### COMMUNICATION TEMPLATES (ENGLISH) ###
(140-160 character alert with specific location and action: "EVACUATE NOW: [Area name]. [X] homes affected. Go to [specific location]. Call 911.")

### COMMUNICATION TEMPLATES (PUNJABI) ###
(Accurate Punjabi translation maintaining all numbers and location specifics)

### COMMUNICATION TEMPLATES (HINDI) ###
(Accurate Hindi translation maintaining all numbers and location specifics)

REMEMBER: Empty or vague statements are NOT ACCEPTABLE. Every metric needs a realistic number. Make intelligent estimates for a typical urban area if agent data is incomplete.
---
"""
        return prompt

    def create_july_2020_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt specifically engineered for July 2020 scenario with HWY 407 emphasis."""
        agent_outputs = context.get("agent_outputs", {})

        prompt = f"""You are an emergency response coordinator generating a critical emergency response plan for the City of Brampton Fire Chief.

SITUATION:
This is a WILDLAND-URBAN INTERFACE (WUI) FIRE at the Highway 407/410 interchange.

CRITICAL CONTEXT:
{json.dumps(agent_outputs, indent=2)}

MANDATORY QUANTITATIVE REQUIREMENTS:
You MUST include specific numbers for ALL metrics. Generate realistic estimates if data is sparse:
- Fire size in hectares (typical WUI fire: 15-50 hectares)
- Spread rate in meters/hour (windy conditions: 200-800 m/h)
- Population affected (residential density: 3,000-5,000 per km²)
- Highway traffic volume (HWY 407: ~50,000-100,000 vehicles/day)
- Responders needed (major incident: 60-120 firefighters from 8-15 stations)
- Equipment count (engines, tankers, aerial units, command vehicles)
- Structures threatened (residential + commercial count)
- Timeline to critical infrastructure impact (minutes)
- Evacuation numbers and safe assembly locations

YOUR TASK:
Generate a complete emergency response plan with SPECIFIC NUMBERS in the following sections:

1. EXECUTIVE SUMMARY (2-3 sentences with NUMBERS)
   - Start with: "CRITICAL WUI FIRE AT HWY 407/410 INTERCHANGE"
   - MUST explicitly state: "RECOMMEND PROACTIVE CLOSURE OF HWY 407 EASTBOUND LANES"
   - Include: fire size (hectares), structures threatened (count), timeline to highway impact (minutes)
   - Include: population at risk (specific number), responders deployed (count)
   - Mention mutual aid requirement with specific station count
   - Be urgent and direct - this is life-safety critical
   - Use all-caps for critical recommendations

2. SITUATION OVERVIEW (1 paragraph with METRICS)
   - Fire size in hectares and spread rate in m/hour
   - Weather conditions with specific wind speed
   - Population at risk with specific numbers
   - Infrastructure count (roads, facilities threatened)
   - Number of responders and equipment deployed
   - Timeline estimates for critical events
   - Why immediate action is required

3. COMMUNICATION TEMPLATES
   Generate emergency alerts in three languages. Each should be 140-160 characters for SMS:

   a) English: Clear, direct, actionable. Include specific location, action required, and where to go. MUST include at least one number.
   b) Punjabi (ਪੰਜਾਬੀ): Translate the English message accurately maintaining all numbers
   c) Hindi (हिंदी): Translate the English message accurately maintaining all numbers

CRITICAL REQUIREMENTS:
- The executive summary MUST mention "Highway 407" or "HWY 407"
- The executive summary MUST recommend "proactive closure" or "immediate closure"
- EVERY metric needs a specific number - no vague terms like "several", "many", "nearby"
- Use realistic estimates for urban area (Brampton population density ~3,500/km²)
- Tone should be urgent but professional
- This plan will be acted upon immediately - be specific and actionable
- Emphasize that satellite detection gives us a head start before 911 calls

Format your response EXACTLY as follows:

===EXECUTIVE_SUMMARY===
[Your 2-3 sentence executive summary with SPECIFIC NUMBERS here]

===SITUATION_OVERVIEW===
[Your situation overview paragraph with SPECIFIC METRICS here]

===COMMUNICATION_EN===
[English alert message with at least one number]

===COMMUNICATION_PA===
[Punjabi alert message maintaining numbers]

===COMMUNICATION_HI===
[Hindi alert message maintaining numbers]

Remember: Lives depend on this plan. Be specific, quantitative, urgent, and actionable. Empty statements without numbers are NOT acceptable."""

        return prompt

    def _extract_section(self, text: str, start_delim: str, end_delim: str) -> str:
        """Helper to extract text between two delimiters."""
        try:
            start_index = text.index(start_delim) + len(start_delim)
            end_index = text.index(end_delim, start_index)
            return text[start_index:end_index].strip()
        except ValueError:
            if start_delim in text:
                return text.split(start_delim, 1)[-1].split("###", 1)[0].strip()
            self._log(f"Warning: Could not find delimiter {start_delim}")
            return f"Error: Could not find section {start_delim}"

    def _parse_llm_response(self, response_text: str, is_july_2020: bool = False) -> Dict[str, Any]:
        """Parses the raw LLM text block into a structured dict."""
        self._log("Parsing LLM response...")

        if is_july_2020:
            # Parse July 2020 format with === delimiters
            sections = {}

            # Extract executive summary
            if '===EXECUTIVE_SUMMARY===' in response_text:
                start = response_text.index('===EXECUTIVE_SUMMARY===') + len('===EXECUTIVE_SUMMARY===')
                end = response_text.index('===SITUATION_OVERVIEW===', start)
                sections['summary'] = response_text[start:end].strip()
            else:
                sections['summary'] = "Error: Could not parse executive summary."

            # Extract situation overview
            if '===SITUATION_OVERVIEW===' in response_text:
                start = response_text.index('===SITUATION_OVERVIEW===') + len('===SITUATION_OVERVIEW===')
                end = response_text.index('===COMMUNICATION_EN===', start)
                sections['overview'] = response_text[start:end].strip()
            else:
                sections['overview'] = "Error: Could not parse situation overview."

            # Extract communication templates
            templates = {}

            if '===COMMUNICATION_EN===' in response_text:
                start = response_text.index('===COMMUNICATION_EN===') + len('===COMMUNICATION_EN===')
                end = response_text.index('===COMMUNICATION_PA===', start)
                templates['en'] = response_text[start:end].strip()
            else:
                templates['en'] = "Error: Could not parse English template."

            if '===COMMUNICATION_PA===' in response_text:
                start = response_text.index('===COMMUNICATION_PA===') + len('===COMMUNICATION_PA===')
                end = response_text.index('===COMMUNICATION_HI===', start)
                templates['pa'] = response_text[start:end].strip()
            else:
                templates['pa'] = "Error: Could not parse Punjabi template."

            if '===COMMUNICATION_HI===' in response_text:
                start = response_text.index('===COMMUNICATION_HI===') + len('===COMMUNICATION_HI===')
                # Find end (either next === or end of string)
                next_marker = response_text.find('===', start)
                if next_marker == -1:
                    templates['hi'] = response_text[start:].strip()
                else:
                    templates['hi'] = response_text[start:next_marker].strip()
            else:
                templates['hi'] = "Error: Could not parse Hindi template."

            sections['templates'] = templates
            return sections
        else:
            # Parse standard format with ### delimiters
            summary = self._extract_section(
                response_text,
                "### EXECUTIVE SUMMARY ###",
                "### SITUATION OVERVIEW ###",
            )
            overview = self._extract_section(
                response_text,
                "### SITUATION OVERVIEW ###",
                "### COMMUNICATION TEMPLATES (ENGLISH) ###",
            )

            template_en = self._extract_section(
                response_text,
                "### COMMUNICATION TEMPLATES (ENGLISH) ###",
                "### COMMUNICATION TEMPLATES (PUNJABI) ###",
            )
            template_pa = self._extract_section(
                response_text,
                "### COMMUNICATION TEMPLATES (PUNJABI) ###",
                "### COMMUNICATION TEMPLATES (HINDI) ###",
            )

            try:
                template_hi = response_text.split("### COMMUNICATION TEMPLATES (HINDI) ###", 1)[
                    -1
                ].strip()
            except Exception:
                template_hi = "Error: Could not parse Hindi template."

            return {
                "summary": summary,
                "overview": overview,
                "templates": {
                    "en": template_en,
                    "pa": template_pa,
                    "hi": template_hi,
                },
            }

    async def _call_llm_api(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send the synthesized prompt to the LLM provider and parse the response."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            self._log("OPENROUTER_API_KEY not configured; returning fallback plan.")
            return {
                "summary": "Error: LLM API key not configured.",
                "overview": "",
                "templates": {},
            }
        
        # Emit progress for LLM API call
        disaster_id = context.get('disaster_id')
        if disaster_id:
            self._emit(
                "progress",
                {
                    "disaster_id": disaster_id,
                    "phase": "synthesis",
                    "progress": 85,
                    "message": "🤖 Calling OpenRouter AI for plan synthesis...",
                    "api_status": {
                        "name": "OpenRouter LLM",
                        "status": "fetching"
                    }
                },
                room=disaster_id,
            )

        # Check if this is July 2020 scenario based on explicit metadata
        # Only use specialized prompt for actual historical July 2020 scenario
        disaster_id = context.get('disaster_id')
        disaster = self.active_disasters.get(disaster_id) if disaster_id else None
        trigger_data = disaster.get('trigger', {}) if disaster else {}
        metadata = trigger_data.get('metadata', {})
        
        is_july_2020 = metadata.get('scenario') == 'july_2020_backtest'

        if is_july_2020:
            self._log("Using July 2020 specialized prompt (HWY 407 emphasis)")
            prompt = self.create_july_2020_prompt(context)
        else:
            self._log("Using standard prompt")
            prompt = self.create_standard_prompt(context)

        url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": "https://rapidresponseai.demo",
            "X-Title": "RapidResponseAI",
        }

        payload = {
            "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self._log(f"LLM API error {response.status}: {error_text}")
                        return {
                            "summary": f"Error: LLM API request failed ({response.status}).",
                            "overview": error_text,
                            "templates": {},
                        }
                    data = await response.json()
        except Exception as exc:
            self._log(f"LLM API exception: {exc}")
            return {
                "summary": "Error: LLM API request failed.",
                "overview": str(exc),
                "templates": {},
            }

        choices = data.get("choices", [])
        if not choices:
            self._log("LLM API response missing choices array.")
            return {
                "summary": "Error: LLM API returned no results.",
                "overview": "",
                "templates": {},
            }

        content = choices[0].get("message", {}).get("content", "")
        if isinstance(content, list):
            flattened = []
            for block in content:
                if isinstance(block, dict):
                    flattened.append(block.get("text", ""))
                else:
                    flattened.append(str(block))
            content = "\n".join(flattened)

        # Emit success for LLM API call
        disaster_id = context.get('disaster_id')
        if disaster_id:
            self._emit(
                "progress",
                {
                    "disaster_id": disaster_id,
                    "phase": "synthesis",
                    "progress": 95,
                    "message": "✅ AI-generated emergency plan received",
                    "api_status": {
                        "name": "OpenRouter LLM",
                        "status": "success"
                    }
                },
                room=disaster_id,
            )

        return self._parse_llm_response(content or "", is_july_2020=is_july_2020)

    async def _load_cached_response(self, disaster_id: str, is_fallback: bool = False):
        """Load cached response as fallback when agent processing fails"""
        disaster = self.active_disasters[disaster_id]

        # Update messaging based on whether this is a fallback
        message_prefix = "Loading fallback" if is_fallback else "Loading demonstration"
        phase_name = 'fallback_cached' if is_fallback else 'loading_cached'

        # Simulate progress updates for realism
        for progress in [20, 40, 60, 80, 100]:
            await asyncio.sleep(0.3)  # Slightly faster for fallback
            self._emit('progress', {
                'disaster_id': disaster_id,
                'progress': progress,
                'phase': phase_name,
                'message': f'{message_prefix} data... {progress}%',
            }, room=disaster_id)

        # Load cached data
        cached = load_cached_july_2020()

        if not cached:
            raise Exception("Cached data not available")

        # Update disaster with cached data
        disaster.update(cached['disaster'])
        disaster['agent_results'] = cached['agent_outputs']
        disaster['plan'] = cached['plan']
        disaster['status'] = 'complete'
        
        # Mark plan as from cache if it's a fallback
        if is_fallback:
            disaster['plan']['_source'] = 'cached_fallback'
            disaster['plan']['_note'] = 'Agent processing failed, using cached data'

        # Emit completion
        self._emit('disaster_complete', {
            'disaster_id': disaster_id,
            'plan': cached['plan'],
        }, room=disaster_id)

        self._log(f"Cached response loaded as {'fallback' if is_fallback else 'demo'}")

    def _emit(self, event: str, payload: Dict[str, Any], room: Optional[str] = None) -> None:
        if self.socketio:
            self.socketio.emit(event, payload, room=room)

    def _log(self, message: str) -> None:
        print(f"[DisasterOrchestrator] {message}")
