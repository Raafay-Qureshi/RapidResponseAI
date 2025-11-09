"""
Disaster scenario configurations for testing and demonstration
"""

from .july_2020_fire import (
    load_july_2020_scenario,
    is_july_2020_scenario,
    july_2020_scenario,
)

from .march_2022_fire import (
    load_march_2022_scenario,
    is_march_2022_scenario,
    march_2022_scenario,
)

__all__ = [
    'load_july_2020_scenario',
    'is_july_2020_scenario',
    'july_2020_scenario',
    'load_march_2022_scenario',
    'is_march_2022_scenario',
    'march_2022_scenario',
]
