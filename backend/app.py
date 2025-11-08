from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*")

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

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('[WebSocket] Client connected')
    emit('message', {'data': 'Connected to RapidResponse AI server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('[WebSocket] Client disconnected')

@socketio.on('ping')
def handle_ping(data):
    print(f'[WebSocket] Ping received: {data}')
    import time
    emit('pong', {'timestamp': data.get('timestamp'), 'server_time': time.time()})

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)