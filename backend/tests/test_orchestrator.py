import asyncio
import os
import sys
import types
import pytest
from typing import Any, Dict, List

from unittest.mock import AsyncMock

if "aiohttp" not in sys.modules:
    class _ClientTimeout:
        def __init__(self, total: int | float | None = None):
            self.total = total

    class _ClientSession:
        def __init__(self, *args: Any, **kwargs: Any):
            raise RuntimeError("aiohttp is not installed in the test environment.")

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    sys.modules["aiohttp"] = types.SimpleNamespace(
        ClientTimeout=_ClientTimeout,
        ClientSession=_ClientSession,
    )

if "geopandas" not in sys.modules:
    class _GeoDataFrame:
        ...

    def _read_file(*args: Any, **kwargs: Any):
        raise RuntimeError("geopandas is not installed in the test environment.")

    sys.modules["geopandas"] = types.SimpleNamespace(
        GeoDataFrame=_GeoDataFrame,
        read_file=_read_file,
    )

if "shapely" not in sys.modules:
    class _Point:
        def __init__(self, *args: Any, **kwargs: Any):
            self.args = args

        def buffer(self, *_args: Any, **_kwargs: Any):
            return self

        def intersects(self, *_args: Any, **_kwargs: Any) -> bool:
            return True

    class _Polygon:
        def __init__(self, *args: Any, **kwargs: Any):
            self.args = args

    def _shape(obj: Any) -> Any:
        return obj

    geometry_module = types.ModuleType("shapely.geometry")
    geometry_module.Point = _Point
    geometry_module.shape = _shape
    geometry_module.Polygon = _Polygon

    geometry_base_module = types.ModuleType("shapely.geometry.base")
    geometry_base_module.BaseGeometry = object

    shapely_module = types.ModuleType("shapely")
    shapely_module.geometry = geometry_module
    errors_module = types.ModuleType("shapely.errors")
    errors_module.GEOSException = Exception

    sys.modules["shapely"] = shapely_module
    sys.modules["shapely.geometry"] = geometry_module
    sys.modules["shapely.geometry.base"] = geometry_base_module
    sys.modules["shapely.errors"] = errors_module

# Ensure backend package is on path
TESTS_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(TESTS_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, ROOT_DIR)

from backend.orchestrator import DisasterOrchestrator


class FakeSocket:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def emit(self, event: str, payload: Dict[str, Any], room: str | None = None):
        self.events.append({"event": event, "payload": payload, "room": room})


@pytest.mark.asyncio
async def test_disaster_pipeline():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)
    orchestrator._fetch_all_data = AsyncMock(
        return_value={"satellite": {"fire_perimeter": "mock"}}
    )
    mock_agents = {
        "damage": {"severity": "moderate", "affected_area_km2": 12},
        "population": {"total_affected": 350},
        "routing": {"priority_routes": []},
        "resource": {"crews": 5},
        "prediction": {"outlook": "stable"},
    }
    orchestrator._run_all_agents = AsyncMock(return_value=mock_agents)
    orchestrator._call_llm_api = AsyncMock(
        return_value={
            "summary": "Mock summary",
            "overview": "Mock overview",
            "templates": {"en": "English alert", "pa": "Punjabi alert", "hi": "Hindi alert"},
        }
    )

    trigger = {
        "type": "wildfire",
        "location": {"lat": 43.74, "lon": -79.85},
    }
    disaster_id = orchestrator.create_disaster(trigger)
    plan = await orchestrator.process_disaster(disaster_id)

    assert plan["executive_summary"] == "Mock summary"
    assert plan["situation_overview"] == "Mock overview"
    assert plan["communication_templates"]["pa"] == "Punjabi alert"
    assert plan["affected_areas"] == orchestrator.get_disaster(disaster_id)["agent_results"]["damage"]
    assert plan["population_impact"]["total_affected"] == 350
    assert orchestrator.get_plan(disaster_id) == plan
    assert orchestrator.get_disaster(disaster_id)["status"] == "complete"

    emitted_events = [event["event"] for event in socket.events]
    assert emitted_events[0] == "disaster_created"
    assert emitted_events[-1] == "disaster_complete"

    print("✓ DisasterOrchestrator pipeline produced a synthesized plan successfully")


@pytest.mark.asyncio
async def test_create_and_fetch():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    trigger = {"type": "flood", "location": {"lat": 43.70, "lon": -79.80}}
    disaster_id = orchestrator.create_disaster(trigger)

    stored = orchestrator.get_disaster(disaster_id)
    assert stored["type"] == "flood"
    assert stored["status"] == "initializing"
    assert stored["agent_results"] == {}

    print("✓ DisasterOrchestrator stores new disasters correctly")


def test_build_master_prompt_structure():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    context = {
        "disaster_type": "wildfire",
        "location": "Downtown Brampton",
        "agent_outputs": {
            "damage": {"severity": "extreme", "affected_area_km2": 12.5},
            "population": {"total_affected": 4200, "languages": {"Punjabi": 1500}},
            "prediction": {"outlook": "worsening", "spread_kmh": 3},
            "routing": {
                "priority_routes": [
                    {"name": "Queen St E", "notes": "Keep westbound lanes open"}
                ]
            },
            "resource": {"fire_crews_needed": 6, "relief_centers": ["Century Gardens"]},
        },
    }

    prompt = orchestrator.create_standard_prompt(context)

    expected_sections = [
        "### AGENT 1: DAMAGE ASSESSMENT ###",
        "### AGENT 2: POPULATION IMPACT ###",
        "### AGENT 3: PREDICTION & TIMELINE ###",
        "### AGENT 4: EVACUATION ROUTING ###",
        "### AGENT 5: RESOURCE ALLOCATION ###",
        "### EXECUTIVE SUMMARY ###",
        "### SITUATION OVERVIEW ###",
        "### COMMUNICATION TEMPLATES (ENGLISH) ###",
        "### COMMUNICATION TEMPLATES (PUNJABI) ###",
        "### COMMUNICATION TEMPLATES (HINDI) ###",
    ]

    for section in expected_sections:
        assert section in prompt, f"Missing section header: {section}"

    assert "RapidResponseAI" in prompt
    assert "**wildfire**" in prompt
    assert "**Downtown Brampton**" in prompt
    assert '"severity": "extreme"' in prompt
    assert '"total_affected": 4200' in prompt
    assert '"spread_kmh": 3' in prompt
    assert "Queen St E" in prompt
    assert "Century Gardens" in prompt


def test_build_master_prompt_defaults():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    prompt = orchestrator.create_standard_prompt({"agent_outputs": {}})

    assert "**unknown incident**" in prompt
    assert "**unknown location**" in prompt
    assert prompt.count("{}") >= 5  # each empty agent block renders a JSON placeholder


def test_extract_section_and_missing_delimiter():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    llm_text = """
### EXECUTIVE SUMMARY ###
Critical update here.
### SITUATION OVERVIEW ###
Detailed overview lines.
### COMMUNICATION TEMPLATES (ENGLISH) ###
English alert text.
### COMMUNICATION TEMPLATES (PUNJABI) ###
Punjabi alert text.
### COMMUNICATION TEMPLATES (HINDI) ###
Hindi alert text.
"""
    summary = orchestrator._extract_section(
        llm_text,
        "### EXECUTIVE SUMMARY ###",
        "### SITUATION OVERVIEW ###",
    )
    assert summary == "Critical update here."

    missing_section = orchestrator._extract_section(
        llm_text,
        "### UNKNOWN SECTION ###",
        "### SITUATION OVERVIEW ###",
    )
    assert missing_section.startswith("Error: Could not find section")


def test_parse_llm_response_structure():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    response = """
### EXECUTIVE SUMMARY ###
Fire is spreading rapidly near Main St.
### SITUATION OVERVIEW ###
Paragraph one details.
Paragraph two details.
### COMMUNICATION TEMPLATES (ENGLISH) ###
English template text.
### COMMUNICATION TEMPLATES (PUNJABI) ###
Punjabi template text.
### COMMUNICATION TEMPLATES (HINDI) ###
Hindi template text.
"""

    parsed = orchestrator._parse_llm_response(response)

    assert parsed["summary"] == "Fire is spreading rapidly near Main St."
    assert "Paragraph one details." in parsed["overview"]
    assert parsed["templates"]["en"] == "English template text."
    assert parsed["templates"]["pa"] == "Punjabi template text."
    assert parsed["templates"]["hi"] == "Hindi template text."


@pytest.mark.asyncio
async def test_process_disaster_emits_progress_and_context():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)

    mock_data = {"roads": {"segments": 2}}
    mock_agents = {
        "damage": {"severity": "moderate"},
        "population": {"total_affected": 123},
        "routing": {"priority_routes": []},
        "resource": {"crews": 4},
        "prediction": {"outlook": "stable"},
    }
    orchestrator._fetch_all_data = AsyncMock(return_value=mock_data)
    orchestrator._run_all_agents = AsyncMock(return_value=mock_agents)
    orchestrator._call_llm_api = AsyncMock(
        return_value={
            "summary": "Integration summary",
            "overview": "Integration overview",
            "templates": {"en": "T1", "pa": "T2", "hi": "T3"},
        }
    )

    trigger = {"type": "flood", "location": {"lat": 43.7, "lon": -79.8}}
    disaster_id = orchestrator.create_disaster(trigger)
    await orchestrator.process_disaster(disaster_id)

    progress_events = [evt for evt in socket.events if evt["event"] == "progress"]
    assert [evt["payload"]["phase"] for evt in progress_events] == [
        "data_ingestion",
        "agent_processing",
        "synthesis",
    ]
    assert progress_events[-1]["payload"]["progress"] == 70

    orchestrator._call_llm_api.assert_awaited_once()
    context = orchestrator._call_llm_api.call_args.args[0]
    assert context["disaster_type"] == "flood"
    assert context["location"] == {"lat": 43.7, "lon": -79.8}
    assert context["agent_outputs"] == mock_agents

    final_event = socket.events[-1]
    assert final_event["event"] == "disaster_complete"
    assert final_event["payload"]["plan"]["executive_summary"] == "Integration summary"
    assert final_event["payload"]["plan"]["resource_deployment"] == mock_agents["resource"]


async def main():
    await test_disaster_pipeline()
    await test_create_and_fetch()
    await test_process_disaster_emits_progress_and_context()
    print("\n✅ All DisasterOrchestrator tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
    test_build_master_prompt_structure()
    test_build_master_prompt_defaults()
