from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import sys

# Add backend directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv()

# App Initialization
app = Flask(__name__)

# CORS Configuration - supports both local development and production
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
CORS(app, origins=ALLOWED_ORIGINS)

# SocketIO Initialization
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

# Orchestrator Initialization
from orchestrator import DisasterOrchestrator
from utils.config import config

orchestrator = DisasterOrchestrator(socketio) if config.USE_REAL_APIS else None

# Register Routes
from routes import create_routes
app.register_blueprint(create_routes(orchestrator), url_prefix='/api')

# Initialize SocketIO Handlers
from sockets import init_socketio
init_socketio(socketio, orchestrator)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)