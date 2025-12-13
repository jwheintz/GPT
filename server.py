"""
OBS Classroom Control Server
Runs on your local Windows machine and receives commands from the web interface
to control OBS Studio filters and effects.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from obswebsocket import obsws, requests as obs_requests
import threading
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
config = {}
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

# CORS configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', config.get('server', {}).get('allowed_origins', ['*']))
if isinstance(allowed_origins, str):
    allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]

CORS(app, origins=allowed_origins, supports_credentials=True)

# Global state
emergency_stop_enabled = False
obs_client = None
obs_connected = False
obs_lock = threading.Lock()

# OBS WebSocket connection settings
OBS_HOST = os.getenv('OBS_HOST', config.get('obs', {}).get('host', 'localhost'))
OBS_PORT = int(os.getenv('OBS_PORT', config.get('obs', {}).get('port', 4455)))
OBS_PASSWORD = os.getenv('OBS_PASSWORD', config.get('obs', {}).get('password', ''))

# Server settings
WEB_PASSWORD = os.getenv('WEB_PASSWORD', config.get('server', {}).get('password', 'changeme'))
SERVER_PORT = int(os.getenv('SERVER_PORT', config.get('server', {}).get('port', 8080)))


def connect_obs():
    """Connect to OBS WebSocket"""
    global obs_client, obs_connected
    try:
        with obs_lock:
            if obs_client:
                try:
                    obs_client.disconnect()
                except:
                    pass
            
            obs_client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
            obs_client.connect()
            obs_connected = True
            logger.info(f"Connected to OBS at {OBS_HOST}:{OBS_PORT}")
            return True
    except Exception as e:
        logger.error(f"Failed to connect to OBS: {e}")
        obs_connected = False
        return False


def disconnect_obs():
    """Disconnect from OBS WebSocket"""
    global obs_client, obs_connected
    try:
        with obs_lock:
            if obs_client:
                obs_client.disconnect()
                obs_client = None
            obs_connected = False
            logger.info("Disconnected from OBS")
    except Exception as e:
        logger.error(f"Error disconnecting from OBS: {e}")


def ensure_obs_connection():
    """Ensure OBS connection is active"""
    global obs_connected
    if not obs_connected or not obs_client:
        return connect_obs()
    try:
        # Test connection
        obs_client.call(obs_requests.GetVersion())
        return True
    except:
        logger.warning("OBS connection lost, reconnecting...")
        return connect_obs()


def check_password(password):
    """Verify password"""
    return password == WEB_PASSWORD


def check_emergency_stop():
    """Check if emergency stop is enabled"""
    if emergency_stop_enabled:
        raise Exception("Emergency stop is active. All commands are disabled.")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'obs_connected': obs_connected,
        'emergency_stop': emergency_stop_enabled
    })


@app.route('/auth', methods=['POST'])
def auth():
    """Authenticate with password"""
    data = request.json
    password = data.get('password', '')
    
    if check_password(password):
        return jsonify({'success': True, 'message': 'Authenticated'})
    else:
        return jsonify({'success': False, 'message': 'Invalid password'}), 401


@app.route('/emergency/stop', methods=['POST'])
def emergency_stop():
    """Enable emergency stop"""
    data = request.json
    password = data.get('password', '')
    
    if not check_password(password):
        return jsonify({'success': False, 'message': 'Invalid password'}), 401
    
    global emergency_stop_enabled
    emergency_stop_enabled = True
    logger.warning("EMERGENCY STOP ACTIVATED")
    return jsonify({'success': True, 'message': 'Emergency stop activated'})


@app.route('/emergency/resume', methods=['POST'])
def emergency_resume():
    """Resume from emergency stop"""
    data = request.json
    password = data.get('password', '')
    
    if not check_password(password):
        return jsonify({'success': False, 'message': 'Invalid password'}), 401
    
    global emergency_stop_enabled
    emergency_stop_enabled = False
    logger.info("Emergency stop deactivated - operations resumed")
    return jsonify({'success': True, 'message': 'Operations resumed'})


@app.route('/obs/scenes', methods=['GET'])
def get_scenes():
    """Get list of OBS scenes"""
    check_emergency_stop()
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            response = obs_client.call(obs_requests.GetSceneList())
            scenes = [scene['sceneName'] for scene in response.datain['scenes']]
            return jsonify({'scenes': scenes})
    except Exception as e:
        logger.error(f"Error getting scenes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/obs/sources', methods=['GET'])
def get_sources():
    """Get list of sources in a scene"""
    check_emergency_stop()
    
    scene_name = request.args.get('scene', '')
    if not scene_name:
        return jsonify({'error': 'Scene name required'}), 400
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            response = obs_client.call(obs_requests.GetSceneItemList(sceneName=scene_name))
            sources = []
            for item in response.datain['sceneItems']:
                sources.append({
                    'name': item['sourceName'],
                    'id': item['sceneItemId']
                })
            return jsonify({'sources': sources})
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/obs/filters', methods=['GET'])
def get_filters():
    """Get list of filters for a source"""
    check_emergency_stop()
    
    source_name = request.args.get('source', '')
    if not source_name:
        return jsonify({'error': 'Source name required'}), 400
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            response = obs_client.call(obs_requests.GetSourceFilterList(sourceName=source_name))
            filters = []
            for filter_info in response.datain['filters']:
                filters.append({
                    'name': filter_info['filterName'],
                    'type': filter_info['filterType'],
                    'enabled': filter_info['filterEnabled']
                })
            return jsonify({'filters': filters})
    except Exception as e:
        logger.error(f"Error getting filters: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/obs/filter/toggle', methods=['POST'])
def toggle_filter():
    """Toggle a filter on/off"""
    check_emergency_stop()
    
    data = request.json
    source_name = data.get('source', '')
    filter_name = data.get('filter', '')
    
    if not source_name or not filter_name:
        return jsonify({'error': 'Source and filter names required'}), 400
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            # Get current filter state
            response = obs_client.call(obs_requests.GetSourceFilter(sourceName=source_name, filterName=filter_name))
            current_state = response.datain['filterEnabled']
            
            # Toggle it
            new_state = not current_state
            obs_client.call(obs_requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=new_state
            ))
            
            logger.info(f"Toggled filter {filter_name} on {source_name} to {new_state}")
            return jsonify({
                'success': True,
                'filter': filter_name,
                'source': source_name,
                'enabled': new_state
            })
    except Exception as e:
        logger.error(f"Error toggling filter: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/obs/filter/set', methods=['POST'])
def set_filter():
    """Set filter enabled state"""
    check_emergency_stop()
    
    data = request.json
    source_name = data.get('source', '')
    filter_name = data.get('filter', '')
    enabled = data.get('enabled', True)
    
    if not source_name or not filter_name:
        return jsonify({'error': 'Source and filter names required'}), 400
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            obs_client.call(obs_requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=bool(enabled)
            ))
            
            logger.info(f"Set filter {filter_name} on {source_name} to {enabled}")
            return jsonify({
                'success': True,
                'filter': filter_name,
                'source': source_name,
                'enabled': enabled
            })
    except Exception as e:
        logger.error(f"Error setting filter: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/obs/filter/settings', methods=['POST'])
def set_filter_settings():
    """Set filter settings (for filters with adjustable parameters)"""
    check_emergency_stop()
    
    data = request.json
    source_name = data.get('source', '')
    filter_name = data.get('filter', '')
    settings = data.get('settings', {})
    
    if not source_name or not filter_name:
        return jsonify({'error': 'Source and filter names required'}), 400
    
    if not ensure_obs_connection():
        return jsonify({'error': 'OBS not connected'}), 500
    
    try:
        with obs_lock:
            obs_client.call(obs_requests.SetSourceFilterSettings(
                sourceName=source_name,
                filterName=filter_name,
                filterSettings=settings
            ))
            
            logger.info(f"Updated settings for filter {filter_name} on {source_name}")
            return jsonify({
                'success': True,
                'filter': filter_name,
                'source': source_name
            })
    except Exception as e:
        logger.error(f"Error setting filter settings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/voicemod/effect', methods=['POST'])
def voicemod_effect():
    """Placeholder for VoiceMod sound effects (future expansion)"""
    check_emergency_stop()
    
    data = request.json
    effect_name = data.get('effect', '')
    
    # TODO: Implement VoiceMod API integration
    logger.info(f"VoiceMod effect requested: {effect_name} (not yet implemented)")
    
    return jsonify({
        'success': False,
        'message': 'VoiceMod integration coming soon'
    })


if __name__ == '__main__':
    logger.info("Starting OBS Classroom Control Server...")
    logger.info(f"OBS WebSocket: {OBS_HOST}:{OBS_PORT}")
    logger.info(f"Server will listen on port {SERVER_PORT}")
    
    # Try to connect to OBS on startup
    connect_obs()
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=SERVER_PORT,
        debug=False,
        threaded=True
    )
