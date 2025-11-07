import asyncio
import os
import sys

import geopandas as gpd
from shapely.geometry import Polygon, mapping

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.population_impact import PopulationImpactAgent


def _make_square(lon: float, lat: float, size: float = 0.003) -> Polygon:
    """Create a small square polygon around the provided coordinate."""
    return Polygon(
        [
            (lon - size, lat - size),
            (lon + size, lat - size),
            (lon + size, lat + size),
            (lon - size, lat + size),
            (lon - size, lat - size),
        ]
    )


def _build_population_gdf() -> gpd.GeoDataFrame:
    """Synthetic census block data for testing."""
    data = {
        "population": [150, 200, 50],
        "age_65_plus": [30, 20, 10],
        "age_under_18": [40, 60, 15],
        "primary_language": ["English", "Punjabi", "English"],
        "neighborhood": ["Downtown", "North Ridge", "East Side"],
        "geometry": [
            _make_square(-79.865, 43.732),
            _make_square(-79.855, 43.738),
            _make_square(-79.770, 43.730),
        ],
    }
    return gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")


async def test_population_summary():
    agent = PopulationImpactAgent()
    population_gdf = _build_population_gdf()

    boundary = mapping(
        Polygon(
            [
                (-79.875, 43.720),
                (-79.840, 43.720),
                (-79.840, 43.750),
                (-79.875, 43.750),
                (-79.875, 43.720),
            ]
        )
    )

    result = await agent.analyze(boundary, population_gdf)

    assert result["total_affected"] == 350, "Should sum only intersecting blocks"
    assert result["vulnerable_population"]["elderly"] == 50
    assert result["vulnerable_population"]["children"] == 100
    assert result["languages"]["English"] == 150
    assert result["languages"]["Punjabi"] == 200
    assert set(result["affected_neighborhoods"]) == {"Downtown", "North Ridge"}

    facility_types = {facility["type"] for facility in result["critical_facilities"]}
    assert {"elementary_school", "senior_center"} <= facility_types
    assert "hospital" not in facility_types

    print("✓ PopulationImpactAgent aggregates affected census blocks correctly")


async def test_population_empty_inputs():
    agent = PopulationImpactAgent()
    empty_gdf = gpd.GeoDataFrame(
        {
            "population": [],
            "age_65_plus": [],
            "age_under_18": [],
            "primary_language": [],
            "neighborhood": [],
        },
        geometry=[],
        crs="EPSG:4326",
    )
    dummy_boundary = mapping(_make_square(-79.800, 43.700, size=0.001))

    result = await agent.analyze(dummy_boundary, empty_gdf)

    assert result["total_affected"] == 0
    assert result["vulnerable_population"]["elderly"] == 0
    assert result["languages"] == {}
    assert result["critical_facilities"] == []
    assert result["affected_neighborhoods"] == []

    print("✓ PopulationImpactAgent gracefully handles empty population datasets")


async def main():
    await test_population_summary()
    await test_population_empty_inputs()
    print("\n✅ All PopulationImpactAgent tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
