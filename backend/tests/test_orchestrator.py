import asyncio
import os
import sys
from typing import Any, Dict, List

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, mapping

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


def _sample_population() -> gpd.GeoDataFrame:
    polygons = [
        Polygon([(-79.87, 43.72), (-79.85, 43.72), (-79.85, 43.74), (-79.87, 43.74)]),
        Polygon([(-79.86, 43.74), (-79.84, 43.74), (-79.84, 43.76), (-79.86, 43.76)]),
        Polygon([(-80.00, 43.60), (-79.98, 43.60), (-79.98, 43.62), (-80.00, 43.62)]),
    ]

    data = {
        "population": [120, 230, 15],
        "age_65_plus": [20, 45, 2],
        "age_under_18": [30, 70, 5],
        "primary_language": ["English", "Punjabi", "English"],
        "neighborhood": ["Downtown", "North Ridge", "Far West"],
        "geometry": polygons,
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


def _sample_infrastructure() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Civic Centre", "Central High School", "Emergency Ops"],
            "type": ["government", "school", "emergency"],
        }
    )


class DummySatelliteClient:
    async def fetch_imagery(self, location: Dict[str, float]) -> Dict[str, Any]:
        perimeter = Polygon(
            [
                (-79.88, 43.71),
                (-79.83, 43.71),
                (-79.83, 43.77),
                (-79.88, 43.77),
                (-79.88, 43.71),
            ]
        )
        return {
            "fire_perimeter": mapping(perimeter),
            "thermal_intensity": 365,
            "satellite": "TESTSAT",
        }


class DummyWeatherClient:
    async def fetch_current(self, location: Dict[str, float]) -> Dict[str, Any]:
        return {"main": {"temp": 21, "humidity": 55}}

    async def fetch_forecast(self, location: Dict[str, float]) -> Dict[str, Any]:
        return {
            "list": [
                {"wind": {"speed": 6}, "main": {"humidity": 65}},
                {"wind": {"speed": 8}, "main": {"humidity": 72}},
            ]
        }


class DummyGeoHubClient:
    def __init__(self):
        self.population = _sample_population()
        self.infrastructure = _sample_infrastructure()

    async def fetch_population(self, location: Dict[str, float]):
        return self.population

    async def fetch_infrastructure(self, location: Dict[str, float]):
        return self.infrastructure

    async def fetch_roads(self, location: Dict[str, float]):
        return {"road_segments": 12}


async def test_disaster_pipeline():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)
    orchestrator.data_clients = {
        "satellite": DummySatelliteClient(),
        "weather": DummyWeatherClient(),
        "geohub": DummyGeoHubClient(),
    }

    trigger = {
        "type": "wildfire",
        "location": {"lat": 43.74, "lon": -79.85},
    }
    disaster_id = orchestrator.create_disaster(trigger)
    plan = await orchestrator.process_disaster(disaster_id)

    assert plan["summary"]["total_population_impacted"] == 350
    assert plan["summary"]["severity"] in {"high", "extreme"}
    assert plan["summary"]["outlook"] == "stable"
    assert orchestrator.get_plan(disaster_id) == plan
    assert orchestrator.get_disaster(disaster_id)["status"] == "complete"

    emitted_events = [event["event"] for event in socket.events]
    assert emitted_events[0] == "disaster_created"
    assert emitted_events[-1] == "disaster_complete"

    print("✓ DisasterOrchestrator pipeline produced a plan successfully")


async def test_create_and_fetch():
    socket = FakeSocket()
    orchestrator = DisasterOrchestrator(socket)
    orchestrator.data_clients = {
        "satellite": DummySatelliteClient(),
        "weather": DummyWeatherClient(),
        "geohub": DummyGeoHubClient(),
    }

    trigger = {"type": "flood", "location": {"lat": 43.70, "lon": -79.80}}
    disaster_id = orchestrator.create_disaster(trigger)

    stored = orchestrator.get_disaster(disaster_id)
    assert stored["type"] == "flood"
    assert stored["status"] == "initializing"
    assert stored["agent_results"] == {}

    print("✓ DisasterOrchestrator stores new disasters correctly")


async def main():
    await test_disaster_pipeline()
    await test_create_and_fetch()
    print("\n✅ All DisasterOrchestrator tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
