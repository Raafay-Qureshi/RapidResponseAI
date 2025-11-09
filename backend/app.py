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
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])

# SocketIO Initialization
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"])

# Orchestrator Initialization
from orchestrator import DisasterOrchestrator
from utils.config import config

orchestrator = DisasterOrchestrator(socketio) if config.USE_REAL_APIS else None

# Register Routes
from routes import create_routes
app.register_blueprint(create_routes(orchestrator))

# Initialize SocketIO Handlers
from sockets import init_socketio
init_socketio(socketio, orchestrator)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)