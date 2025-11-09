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
# from orchestrator import DisasterOrchestrator
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

        # Mock response for demo purposes with location data
        import uuid
        disaster_id = f"wildfire-{uuid.uuid4().hex[:8]}"
        return jsonify({
            "disaster_id": disaster_id,
            "status": "created",
            "type": data.get("type", "wildfire"),
            "location": data.get("location", {"lat": 43.7315, "lon": -79.8620}),
            "severity": data.get("severity", "high")
        })
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

@socketio.on('test_message')
def handle_test_message(data):
    print('[Backend] Test message received:', data, flush=True)
    emit('test_response', {'status': 'received', 'data': data})

@socketio.on('subscribe_disaster')
def handle_subscribe_disaster(data):
    """Handle disaster subscription from frontend"""
    disaster_id = data.get('disaster_id')
    if disaster_id:
        print(f'[WebSocket] Client subscribed to disaster: {disaster_id}')
        join_room(disaster_id)
        emit('subscribed', {'disaster_id': disaster_id})
        
        # For testing: Simulate progress updates since orchestrator is not active
        # Remove this when orchestrator is integrated
        socketio.start_background_task(simulate_disaster_processing, disaster_id)

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

def simulate_disaster_processing(disaster_id):
    """
    Simulate disaster processing with progress updates
    This is a temporary function for testing until the orchestrator is integrated
    """
    import time
    
    phases = [
        (20, 'data_ingestion', 'Fetching satellite and weather data...'),
        (40, 'agent_processing', 'Analyzing fire perimeter and damage...'),
        (60, 'agent_processing', 'Calculating population impact...'),
        (80, 'synthesis', 'Running fire spread predictions...'),
        (95, 'synthesis', 'Generating emergency response plan...'),
        (100, 'complete', 'Finalizing plan and preparing deployment...')
    ]
    
    for progress, phase, message in phases:
        time.sleep(2)  # Simulate processing time
        socketio.emit('progress', {
            'disaster_id': disaster_id,
            'progress': progress,
            'phase': phase,
            'message': message
        }, room=disaster_id)
        print(f'[WebSocket] Progress update sent: {progress}% - {phase}')
    
    # Send completion with mock plan
    mock_plan = {
        'disaster_id': disaster_id,
        'executive_summary': '40-acre wildfire detected at HWY 407/410 interchange. High-risk WUI area with immediate evacuation needed.',
        'situation_overview': {
            'fire_size': '40 acres',
            'spread_rate': '2.5 km/h',
            'wind_conditions': 'SW 15-20 km/h, gusts to 30 km/h',
            'population_at_risk': '2,500 residents',
            'structures_threatened': '150 homes'
        },
        'timeline': [
            {'time': 'T+0:00', 'action': 'Initial alert and evacuation order issued'},
            {'time': 'T+0:15', 'action': 'First responders dispatched to perimeter'},
            {'time': 'T+0:30', 'action': 'Aerial water drops commence'},
            {'time': 'T+1:00', 'action': 'Secondary evacuation zone established'}
        ],
        'resources': [
            {'type': 'Fire Trucks', 'quantity': 8, 'status': 'En Route'},
            {'type': 'Water Bombers', 'quantity': 2, 'status': 'Active'},
            {'type': 'Ambulances', 'quantity': 4, 'status': 'Standby'}
        ],
        'communication_templates': {
            'en': '🚨 WILDFIRE ALERT: Evacuate immediately from HWY 407/410 area. Fire spreading rapidly. Follow emergency routes. Stay tuned for updates.',
            'pa': '🚨 ਅੱਗ ਸੰਕਟ ਚੇਤਾਵਨੀ: HWY 407/410 ਖੇਤਰ ਤੋਂ ਤੁਰੰਤ ਖਾਲੀ ਕਰੋ। ਅੱਗ ਤੇਜ਼ੀ ਨਾਲ ਫੈਲ ਰਹੀ ਹੈ।',
            'hi': '🚨 अग्नि संकट चेतावनी: HWY 407/410 क्षेत्र से तुरंत खाली करें। आग तेजी से फैल रही है।'
        }
    }
    
    time.sleep(1)
    socketio.emit('disaster_complete', {
        'disaster_id': disaster_id,
        'plan': mock_plan
    }, room=disaster_id)
    print(f'[WebSocket] Disaster processing complete for {disaster_id}')

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
