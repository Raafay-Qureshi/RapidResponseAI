from flask_socketio import emit, join_room
from orchestrator import DisasterOrchestrator
from simulation import simulate_disaster_processing
from utils.config import config
from datetime import datetime
import asyncio
import traceback

def init_socketio(socketio, orchestrator):
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
        mode = data.get('mode', 'simulation')
        
        if disaster_id:
            print(f'[WebSocket] Client subscribed to disaster: {disaster_id} (mode: {mode})')
            join_room(disaster_id)
            emit('subscribed', {'disaster_id': disaster_id, 'mode': mode})
            
            # Route to appropriate processing based on mode
            if mode == 'real_apis' and orchestrator:
                # Use real orchestrator with actual APIs
                socketio.start_background_task(process_disaster_with_orchestrator, socketio, orchestrator, disaster_id, data.get('trigger_data'))
            else:
                # Use simulation with mock data
                socketio.start_background_task(simulate_disaster_processing, socketio, disaster_id)

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
            socketio.start_background_task(process_disaster_async, orchestrator, disaster_id)

def process_disaster_with_orchestrator(socketio, orchestrator, disaster_id, trigger_data):
    """Process disaster using real orchestrator with actual APIs"""
    if not orchestrator:
        socketio.emit('disaster_error', {
            'disaster_id': disaster_id,
            'error': 'Orchestrator not initialized - set USE_REAL_APIS=true in .env'
        }, room=disaster_id)
        return

    try:
        # Check if disaster already exists (e.g., from analyze-coordinates endpoint)
        if disaster_id not in orchestrator.active_disasters:
            # Create disaster in orchestrator only if it doesn't exist
            orchestrator.active_disasters[disaster_id] = {
                'id': disaster_id,
                'type': trigger_data.get('type', 'wildfire'),
                'location': trigger_data.get('location', {}),
                'status': 'initializing',
                'created_at': datetime.utcnow().isoformat(),
                'data': {},
                'agent_results': {},
                'plan': None,
                'trigger': trigger_data,
            }
            print(f'[Backend] Created new disaster: {disaster_id}')
        else:
            print(f'[Backend] Using existing disaster: {disaster_id}')
        
        # Run async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(orchestrator.process_disaster(disaster_id))
        loop.close()
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f'[Backend] Error processing disaster with orchestrator: {error_details}')
        socketio.emit('disaster_error', {
            'disaster_id': disaster_id,
            'error': f'Real API processing failed: {str(e)}'
        }, room=disaster_id)

async def process_disaster_async(orchestrator, disaster_id):
    if not orchestrator:
        socketio.emit('disaster_error', {'disaster_id': disaster_id, 'error': 'Orchestrator not initialized'}, room=disaster_id)
        return

    try:
        await orchestrator.process_disaster(disaster_id)
    except Exception as e:
        socketio.emit('disaster_error', {'disaster_id': disaster_id, 'error': str(e)}, room=disaster_id)
