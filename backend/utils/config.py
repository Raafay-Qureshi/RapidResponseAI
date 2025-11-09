import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    NASA_FIRMS_API_KEY = os.getenv('NASA_FIRMS_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')

    # Server
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    # Demo Mode
    DEMO_MODE = os.getenv('DEMO_MODE', 'False') == 'True'
    USE_CACHED_RESPONSES = os.getenv('USE_CACHED_RESPONSES', 'False') == 'True'
    
    # API Integration Mode
    # When True, uses real APIs (NASA FIRMS, OpenWeather, OpenRouter)
    # When False, uses mock/simulation data
    USE_REAL_APIS = os.getenv('USE_REAL_APIS', 'False') == 'True'

    # Update intervals
    UPDATE_INTERVAL_SECONDS = 900  # 15 minutes

    # Brampton coordinates
    BRAMPTON_CENTER = {'lat': 43.7315, 'lon': -79.7624}

config = Config()
