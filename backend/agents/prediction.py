from __future__ import annotations

from typing import Any, Dict, Optional

from .base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    """Provide short-term risk outlooks based on weather forecasts."""

    async def analyze(
        self,
        disaster_type: str,
        weather_forecast: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        self._log("Modeling disaster spread potential")

        outlook = "stable"
        drivers = {}

        if weather_forecast and "list" in weather_forecast:
            periods = weather_forecast["list"]
            max_wind = max((period["wind"]["speed"] for period in periods if "wind" in period), default=0)
            avg_humidity = sum(
                period["main"].get("humidity", 0) for period in periods if period.get("main")
            ) / len(periods or [1])

            if max_wind > 10:
                outlook = "deteriorating"
            elif avg_humidity > 80:
                outlook = "improving"

            drivers = {"max_wind_speed": max_wind, "avg_humidity": round(avg_humidity, 1)}

        return {
            "disaster_type": disaster_type,
            "outlook": outlook,
            "drivers": drivers,
            "recommendation": self._recommendation(outlook, disaster_type),
        }

    def _recommendation(self, outlook: str, disaster_type: str) -> str:
        if outlook == "deteriorating":
            return f"Escalate response posture for {disaster_type} within 6 hours."
        if outlook == "improving":
            return "Maintain current response levels and monitor conditions."
        return "Hold steady and reassess with next data update."
