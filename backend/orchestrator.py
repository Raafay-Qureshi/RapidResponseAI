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

    def create_july_2020_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt specifically engineered for July 2020 scenario with HWY 407 emphasis."""
        agent_outputs = context.get("agent_outputs", {})

        prompt = f"""You are an emergency response coordinator generating a critical emergency response plan for the City of Brampton Fire Chief.

SITUATION:
This is a WILDLAND-URBAN INTERFACE (WUI) FIRE at the Highway 407/410 interchange.

CRITICAL CONTEXT:
{json.dumps(agent_outputs, indent=2)}

YOUR TASK:
Generate a complete emergency response plan with the following sections:

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Start with: "CRITICAL WUI FIRE AT HWY 407/410 INTERCHANGE"
   - MUST explicitly state: "RECOMMEND PROACTIVE CLOSURE OF HWY 407 EASTBOUND LANES"
   - Mention the timeline to highway impact
   - Mention mutual aid requirement
   - Be urgent and direct - this is life-safety critical
   - Use all-caps for critical recommendations

2. SITUATION OVERVIEW (1 paragraph)
   - Fire size, type, spread rate
   - Weather conditions driving spread
   - Population at risk
   - Infrastructure threatened (emphasize HWY 407)
   - Why immediate action is required

3. COMMUNICATION TEMPLATES
   Generate emergency alerts in three languages. Each should be 140-160 characters for SMS:

   a) English: Clear, direct, actionable. Mention location, action required, where to go.
   b) Punjabi (ਪੰਜਾਬੀ): Translate the English message accurately
   c) Hindi (हिंदी): Translate the English message accurately

CRITICAL REQUIREMENTS:
- The executive summary MUST mention "Highway 407" or "HWY 407"
- The executive summary MUST recommend "proactive closure" or "immediate closure"
- Use specific numbers from the data (affected population, timeline, etc.)
- Tone should be urgent but professional
- This plan will be acted upon immediately - be specific and actionable
- Emphasize that satellite detection gives us a head start before 911 calls

Format your response EXACTLY as follows:

===EXECUTIVE_SUMMARY===
[Your 2-3 sentence executive summary here]

===SITUATION_OVERVIEW===
[Your situation overview paragraph here]

===COMMUNICATION_EN===
[English alert message]

===COMMUNICATION_PA===
[Punjabi alert message]

===COMMUNICATION_HI===
[Hindi alert message]

Remember: Lives depend on this plan. Be specific, urgent, and actionable."""

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

        # Check if this is July 2020 scenario and use specialized prompt
        agent_outputs = context.get('agent_outputs', {})
        predictions = agent_outputs.get('prediction', {})
        critical_arrivals = predictions.get('critical_arrival_times', [])

        is_july_2020 = (
            context.get('disaster_type') == 'wildfire' and
            any('407' in str(arrival.get('location', ''))
                for arrival in critical_arrivals)
        )

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
