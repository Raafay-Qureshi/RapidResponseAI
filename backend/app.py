from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Allow both common dev ports for CORS
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])

# Initialize SocketIO with CORS support - allow both dev ports
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"])

# Initialize orchestrator with socketio instance (commented out for now due to missing dependencies)
# orchestrator = DisasterOrchestrator(socketio)
orchestrator = None

# Note: Flask endpoints are sync by default.
# To call async methods, we use asyncio.run()
# A better production setup would use an async framework like FastAPI

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/api/disaster/trigger', methods=['POST'])
def trigger_disaster():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500

        disaster_id = orchestrator.create_disaster(data)
        return jsonify({"disaster_id": disaster_id, "status": "created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disaster/<disaster_id>', methods=['GET'])
def get_disaster(disaster_id):
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500

    disaster = orchestrator.get_disaster(disaster_id)
    if not disaster:
        return jsonify({"error": "Disaster not found"}), 404
    return jsonify(disaster)

@app.route('/api/disaster/<disaster_id>/plan', methods=['GET'])
def get_disaster_plan(disaster_id):
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500

    plan = orchestrator.get_plan(disaster_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan)

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

@socketio.on('join_disaster')
def handle_join_disaster(data):
    disaster_id = data.get('disaster_id')
    if disaster_id:
        join_room(disaster_id)
        emit('joined', {'disaster_id': disaster_id})

@socketio.on('start_processing')
def handle_start_processing(data):
    disaster_id = data.get('disaster_id')
    if disaster_id and orchestrator:
        # Run async processing in background
        socketio.start_background_task(process_disaster_async, disaster_id)

async def process_disaster_async(disaster_id):
    if not orchestrator:
        socketio.emit('disaster_error', {'disaster_id': disaster_id, 'error': 'Orchestrator not initialized'}, room=disaster_id)
        return

    try:
        await orchestrator.process_disaster(disaster_id)
    except Exception as e:
        socketio.emit('disaster_error', {'disaster_id': disaster_id, 'error': str(e)}, room=disaster_id)

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
