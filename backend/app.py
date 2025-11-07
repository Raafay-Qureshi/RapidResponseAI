from flask import Flask, jsonify
from flask_cors import CORS
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Note: Flask endpoints are sync by default.
# To call async methods, we use asyncio.run()
# A better production setup would use an async framework like FastAPI

@app.route('/api/test/satellite', methods=['GET'])
def test_satellite():
    client = SatelliteClient()
    # Use asyncio.run to execute the async function
    data = asyncio.run(client.fetch_imagery({'lat': 43.7315, 'lon': -79.8620}))
    return jsonify(data)

@app.route('/api/test/weather', methods=['GET'])
def test_weather():
    client = WeatherClient()
    # Use asyncio.run to execute the async function
    data = asyncio.run(client.fetch_current({'lat': 43.7315, 'lon': -79.8620}))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)