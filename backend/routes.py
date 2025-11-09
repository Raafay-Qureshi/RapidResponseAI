from flask import Blueprint, jsonify, request
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
from utils.config import config
from utils.cached_loader import is_cached_data_available
import asyncio
import uuid

def create_routes(orchestrator):
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Backend is running"})

    @main_bp.route('/disaster/trigger', methods=['POST'])
    def trigger_disaster():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            # Check scenario type
            metadata = data.get("metadata", {})
            scenario_type = metadata.get("scenario", "")
            is_july_2020 = scenario_type == "july_2020_backtest"
            is_march_2022 = scenario_type == "march_2022_backtest"
            
            # Determine which mode to use
            use_real_apis = data.get("use_real_apis", config.USE_REAL_APIS)

            # Generate disaster ID based on scenario
            if is_july_2020:
                disaster_id = f"wildfire-july-2020-{uuid.uuid4().hex[:8]}"
            elif is_march_2022:
                disaster_id = f"fire-march-2022-{uuid.uuid4().hex[:8]}"
            else:
                disaster_type = data.get("type", "event").lower()
                disaster_id = f"{disaster_type}-{uuid.uuid4().hex[:8]}"

            response = {
                "disaster_id": disaster_id,
                "status": "created",
                "type": data.get("type", "wildfire"),
                "location": data.get("location", {"lat": 43.7315, "lon": -79.8620}),
                "severity": data.get("severity", "high"),
                "mode": "real_apis" if (use_real_apis and orchestrator) else "simulation"
            }

            if metadata:
                response["metadata"] = metadata

            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @main_bp.route('/disaster/<disaster_id>', methods=['GET'])
    def get_disaster(disaster_id):
        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500

        disaster = orchestrator.get_disaster(disaster_id)
        if not disaster:
            return jsonify({"error": "Disaster not found"}), 404
        return jsonify(disaster)

    @main_bp.route('/disaster/<disaster_id>/plan', methods=['GET'])
    def get_disaster_plan(disaster_id):
        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500

        plan = orchestrator.get_plan(disaster_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        return jsonify(plan)

    @main_bp.route('/test/satellite', methods=['GET'])
    def test_satellite():
        client = SatelliteClient()
        data = asyncio.run(client.fetch_imagery({'lat': 43.7315, 'lon': -79.8620}))
        return jsonify(data)

    @main_bp.route('/test/weather', methods=['GET'])
    def test_weather():
        client = WeatherClient()
        data = asyncio.run(client.fetch_current({'lat': 43.7315, 'lon': -79.8620}))
        return jsonify(data)

    @main_bp.route('/config', methods=['GET'])
    def get_config():
        """Return current configuration status"""
        return jsonify({
            'demo_mode': config.DEMO_MODE,
            'cached_mode': config.USE_CACHED_RESPONSES,
            'cached_available': is_cached_data_available(),
            'use_real_apis': config.USE_REAL_APIS,
            'orchestrator_available': orchestrator is not None,
        })

    @main_bp.route('/disaster/analyze-coordinates', methods=['POST'])
    def analyze_coordinates():
        """Trigger full agentic process for custom coordinates"""
        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate coordinates
            location = data.get("location", {})
            lat = location.get("lat")
            lon = location.get("lon")
            
            if lat is None or lon is None:
                return jsonify({"error": "Latitude and longitude are required"}), 400
            
            # Validate coordinate ranges
            if not (-90 <= lat <= 90):
                return jsonify({"error": "Latitude must be between -90 and 90"}), 400
            if not (-180 <= lon <= 180):
                return jsonify({"error": "Longitude must be between -180 and 180"}), 400
            
            # Create disaster with custom coordinates
            disaster_type = data.get("type", "wildfire")
            disaster_data = {
                "type": disaster_type,
                "location": {"lat": lat, "lon": lon},
                "severity": data.get("severity", "high"),
                "metadata": {
                    "custom_coordinates": True,
                    "description": data.get("description", f"Custom analysis at {lat}, {lon}"),
                },
                "use_real_apis": True  # Always use real APIs for custom coordinates
            }
            
            disaster_id = orchestrator.create_disaster(disaster_data)
            
            # Return complete disaster data for WebSocket subscription
            response = {
                "disaster_id": disaster_id,
                "status": "created",
                "type": disaster_type,
                "location": {"lat": lat, "lon": lon},
                "severity": data.get("severity", "high"),
                "use_real_apis": True,
                "metadata": disaster_data["metadata"],
                "message": "Disaster created and ready for processing"
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return main_bp
