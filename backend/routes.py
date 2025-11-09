from flask import Blueprint, jsonify, request
from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
from utils.config import config
from utils.cached_loader import is_cached_data_available
import asyncio
import uuid

def create_routes(orchestrator):
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Backend is running"})

    @main_bp.route('/api/disaster/trigger', methods=['POST'])
    def trigger_disaster():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            # Check if this is a July 2020 scenario
            metadata = data.get("metadata", {})
            is_july_2020 = metadata.get("scenario") == "july_2020_backtest"
            
            # Determine which mode to use
            use_real_apis = data.get("use_real_apis", config.USE_REAL_APIS)

            # Generate disaster ID
            if is_july_2020:
                disaster_id = f"wildfire-july-2020-{uuid.uuid4().hex[:8]}"
            else:
                disaster_id = f"wildfire-{uuid.uuid4().hex[:8]}"

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

    @main_bp.route('/api/disaster/<disaster_id>', methods=['GET'])
    def get_disaster(disaster_id):
        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500

        disaster = orchestrator.get_disaster(disaster_id)
        if not disaster:
            return jsonify({"error": "Disaster not found"}), 404
        return jsonify(disaster)

    @main_bp.route('/api/disaster/<disaster_id>/plan', methods=['GET'])
    def get_disaster_plan(disaster_id):
        if not orchestrator:
            return jsonify({"error": "Orchestrator not initialized"}), 500

        plan = orchestrator.get_plan(disaster_id)
        if not plan:
            return jsonify({"error": "Plan not found"}), 404
        return jsonify(plan)

    @main_bp.route('/api/test/satellite', methods=['GET'])
    def test_satellite():
        client = SatelliteClient()
        data = asyncio.run(client.fetch_imagery({'lat': 43.7315, 'lon': -79.8620}))
        return jsonify(data)

    @main_bp.route('/api/test/weather', methods=['GET'])
    def test_weather():
        client = WeatherClient()
        data = asyncio.run(client.fetch_current({'lat': 43.7315, 'lon': -79.8620}))
        return jsonify(data)

    @main_bp.route('/api/config', methods=['GET'])
    def get_config():
        """Return current configuration status"""
        return jsonify({
            'demo_mode': config.DEMO_MODE,
            'cached_mode': config.USE_CACHED_RESPONSES,
            'cached_available': is_cached_data_available(),
            'use_real_apis': config.USE_REAL_APIS,
            'orchestrator_available': orchestrator is not None,
        })

    return main_bp
