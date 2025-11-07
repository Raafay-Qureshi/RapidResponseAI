import requests
import os
from typing import Dict

class WeatherClient:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def fetch_current(self, location: Dict) -> Dict:
        """Fetch current weather conditions"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Weather API error: {response.status_code}")
    
    async def fetch_forecast(self, location: Dict) -> Dict:
        """Fetch weather forecast (next 6 hours)"""
        url = f"{self.base_url}/forecast"
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': self.api_key,
            'units': 'metric',
            'cnt': 2  # Next 6 hours (3-hour intervals)
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {}