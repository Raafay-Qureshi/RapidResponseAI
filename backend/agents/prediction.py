from .base_agent import BaseAgent
import numpy as np
from typing import Dict, List
from datetime import datetime
from shapely.geometry import shape, Point

# Import helper functions that will be built in other tasks
# (Or they can be methods within this class)
from .prediction_helpers import (
    _calculate_fire_spread_rate,
    _generate_timeline_predictions,
    _calculate_arrival_times,
    _identify_critical_points
)

class PredictionAgent(BaseAgent):
    async def analyze(self, disaster: Dict, data: Dict) -> Dict:
        """
        Model disaster spread and generate timeline predictions
        """
        self._log(f"Modeling {disaster['type']} spread")

        if disaster['type'] == 'wildfire':
            return await self._model_fire_spread(disaster, data)
        elif disaster['type'] == 'flood':
            return await self._model_flood_spread(disaster, data)
        else:
            raise ValueError(f"Unknown disaster type: {disaster['type']}")

    async def _model_fire_spread(self, disaster: Dict, data: Dict) -> Dict:
        """
        Main coordinator for modeling fire spread.
        Calls helper functions to do the actual work.
        """
        weather = data['weather']
        current_boundary_geojson = data.get('fire_perimeter')
        current_boundary_geom = shape(current_boundary_geojson) if current_boundary_geojson else None

        # --- Task #24 ---
        spread_rate, factors = _calculate_fire_spread_rate(weather)

        # --- Task #25 ---
        timeline_predictions = _generate_timeline_predictions(
            current_boundary_geojson,
            spread_rate
        )

        # --- Task #26 ---
        critical_points = _identify_critical_points(disaster['location'])
        arrival_times = _calculate_arrival_times(
            current_boundary_geom,
            critical_points,
            spread_rate,
            factors['wind_direction_deg']
        )

        return {
            'current_spread_rate_kmh': round(spread_rate, 2),
            'predictions': timeline_predictions,
            'critical_arrival_times': arrival_times,
            'factors': factors
        }

    async def _model_flood_spread(self, disaster: Dict, data: Dict) -> Dict:
        # Placeholder for hackathon
        self._log("Flood modeling not implemented")
        return {'status': 'not_implemented'}
