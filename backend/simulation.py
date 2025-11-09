import time
from flask_socketio import emit

def simulate_disaster_processing(socketio, disaster_id):
    """
    Simulate disaster processing with progress updates.
    This function is for testing and simulation purposes.
    """
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
    mock_plan = get_mock_plan(disaster_id)
    
    time.sleep(1)
    socketio.emit('disaster_complete', {
        'disaster_id': disaster_id,
        'plan': mock_plan
    }, room=disaster_id)
    print(f'[WebSocket] Disaster processing complete for {disaster_id}')

def get_mock_plan(disaster_id):
    """
    Returns a mock emergency response plan.
    """
    return {
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
