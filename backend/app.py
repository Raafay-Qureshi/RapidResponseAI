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
    
    # Send completion with mock plan matching orchestrator structure
    mock_plan = {
        'disaster_id': disaster_id,
        'disaster_type': 'wildfire',
        'confidence': 0.85,
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'executive_summary': '40-acre wildfire detected at HWY 407/410 interchange. High-risk WUI area with immediate evacuation needed. 2,500+ residents affected.',
        'situation_overview': {
            'fire_size': '40 acres',
            'spread_rate': '2.5 km/h',
            'wind_conditions': 'SW 15-20 km/h, gusts to 30 km/h',
            'population_at_risk': '2,500 residents',
            'structures_threatened': '150 homes'
        },
        'affected_areas': {
            'affected_area_km2': 1.6,
            'fire_perimeter': {
                'type': 'Polygon',
                'coordinates': [[
                    [-79.8620, 43.7315],
                    [-79.8600, 43.7315],
                    [-79.8600, 43.7295],
                    [-79.8620, 43.7295],
                    [-79.8620, 43.7315]
                ]]
            }
        },
        'timeline_predictions': {
            'critical_arrival_times': [
                {
                    'location': 'Bovaird Business District',
                    'hours_until_arrival': 2.3,
                    'confidence': 'high'
                },
                {
                    'location': 'Mount Pleasant Village',
                    'hours_until_arrival': 4.5,
                    'confidence': 'high'
                },
                {
                    'location': 'Sandalwood Heights',
                    'hours_until_arrival': 6.2,
                    'confidence': 'medium'
                },
                {
                    'location': 'Highway 410 Corridor',
                    'hours_until_arrival': 1.8,
                    'confidence': 'high'
                }
            ],
            'current_spread_rate_kmh': 2.5,
            'factors': {
                'wind_speed_kmh': 18,
                'wind_direction_deg': 225,
                'temperature_c': 28,
                'humidity_percent': 32
            }
        },
        'resource_deployment': {
            'required_resources': {
                'personnel': 120,
                'ambulances': 8,
                'evacuation_buses': 12
            },
            'available_resources': {
                'fire_stations': [
                    {'id': 'Fire Station 202', 'lat': 43.7200, 'lon': -79.8400, 'trucks': 3},
                    {'id': 'Fire Station 205', 'lat': 43.7350, 'lon': -79.8750, 'trucks': 2},
                    {'id': 'Fire Station 201', 'lat': 43.7450, 'lon': -79.7800, 'trucks': 4}
                ],
                'hospitals': [
                    {'id': 'Brampton Civic Hospital', 'lat': 43.7315, 'lon': -79.7624, 'ambulances': 8},
                    {'id': 'Peel Memorial Centre', 'lat': 43.6900, 'lon': -79.7500, 'ambulances': 5}
                ],
                'police_stations': [
                    {'id': 'Peel Police 21 Division', 'lat': 43.7280, 'lon': -79.8300, 'units': 12},
                    {'id': 'Peel Police 22 Division', 'lat': 43.7100, 'lon': -79.7600, 'units': 10}
                ]
            },
            'resource_gaps': [
                {
                    'resource': 'Fire Personnel',
                    'description': 'Need additional 40 firefighters for perimeter control'
                },
                {
                    'resource': 'Evacuation Transport',
                    'description': 'Require 4 more buses for assisted evacuation'
                }
            ]
        },
        'evacuation_plan': {
            'routes': [
                {
                    'id': 'route-1',
                    'origin': {'lat': 43.7315, 'lon': -79.8620},
                    'destination': {
                        'name': 'Brampton Soccer Centre',
                        'lat': 43.7150,
                        'lon': -79.8400,
                        'capacity': 2000
                    },
                    'path': {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [-79.8620, 43.7315],
                                [-79.8580, 43.7290],
                                [-79.8540, 43.7265],
                                [-79.8500, 43.7240],
                                [-79.8460, 43.7215],
                                [-79.8420, 43.7190],
                                [-79.8400, 43.7150]
                            ]
                        }
                    },
                    'distance_km': 3.2,
                    'time_minutes': 45,
                    'status': 'open',
                    'priority': 'primary'
                },
                {
                    'id': 'route-2',
                    'origin': {'lat': 43.7315, 'lon': -79.8620},
                    'destination': {
                        'name': 'CAA Centre',
                        'lat': 43.7300,
                        'lon': -79.7500,
                        'capacity': 5000
                    },
                    'path': {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [-79.8620, 43.7315],
                                [-79.8400, 43.7312],
                                [-79.8180, 43.7309],
                                [-79.7960, 43.7306],
                                [-79.7740, 43.7303],
                                [-79.7500, 43.7300]
                            ]
                        }
                    },
                    'distance_km': 8.5,
                    'time_minutes': 60,
                    'status': 'open',
                    'priority': 'alternate'
                },
                {
                    'id': 'route-3',
                    'origin': {'lat': 43.7315, 'lon': -79.8620},
                    'destination': {
                        'name': 'Cassie Campbell Community Centre',
                        'lat': 43.7100,
                        'lon': -79.7800,
                        'capacity': 1500
                    },
                    'path': {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [-79.8620, 43.7315],
                                [-79.8520, 43.7267],
                                [-79.8420, 43.7219],
                                [-79.8320, 43.7171],
                                [-79.8220, 43.7123],
                                [-79.8120, 43.7075],
                                [-79.8020, 43.7027],
                                [-79.7920, 43.6979],
                                [-79.7820, 43.6931],
                                [-79.7800, 43.7100]
                            ]
                        }
                    },
                    'distance_km': 5.8,
                    'time_minutes': 52,
                    'status': 'open',
                    'priority': 'alternate'
                }
            ],
            'priority_routes': [
                {
                    'name': 'Primary Evacuation Corridor',
                    'status': 'open',
                    'distance_km': 3.2,
                    'notes': 'Route planned with severity \'high\'.'
                },
                {
                    'name': 'Secondary Relief Route',
                    'status': 'open',
                    'distance_km': 8.5,
                    'notes': 'Alternative path for supply and medical teams.'
                }
            ]
        },
        'population_impact': {
            'total_affected': 2580,
            'vulnerable_population': {
                'elderly': 450,
                'children': 620,
                'disabled': 185
            },
            'languages': {
                'English': 1200,
                'Punjabi': 680,
                'Hindi': 380,
                'Urdu': 180,
                'Other': 140
            },
            'critical_facilities': [
                {
                    'name': 'Bovaird Public School',
                    'type': 'elementary_school',
                    'population': 420,
                    'location': {'lat': 43.7305, 'lon': -79.8610}
                },
                {
                    'name': 'Mount Pleasant Care Centre',
                    'type': 'senior_center',
                    'population': 85,
                    'location': {'lat': 43.7325, 'lon': -79.8605}
                },
                {
                    'name': 'Little Explorers Daycare',
                    'type': 'daycare',
                    'population': 65,
                    'location': {'lat': 43.7310, 'lon': -79.8615}
                }
            ],
            'affected_neighborhoods': [
                'Bovaird Business District',
                'Mount Pleasant Village',
                'Sandalwood Heights',
                'Highway 410 Corridor'
            ]
        },
        'communication_templates': {
            'en': '🚨 WILDFIRE ALERT: Evacuate immediately from HWY 407/410 area. Fire spreading rapidly at 2.5 km/h. Follow emergency routes. Stay tuned for updates.',
            'pa': '🚨 ਅੱਗ ਸੰਕਟ ਚੇਤਾਵਨੀ: HWY 407/410 ਖੇਤਰ ਤੋਂ ਤੁਰੰਤ ਖਾਲੀ ਕਰੋ। ਅੱਗ 2.5 km/h ਦੀ ਰਫ਼ਤਾਰ ਨਾਲ ਫੈਲ ਰਹੀ ਹੈ। ਐਮਰਜੈਂਸੀ ਰੂਟਾਂ ਦੀ ਪਾਲਣਾ ਕਰੋ।',
            'hi': '🚨 अग्नि संकट चेतावनी: HWY 407/410 क्षेत्र से तुरंत खाली करें। आग 2.5 km/h की गति से फैल रही है। आपातकालीन मार्गों का पालन करें।'
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
