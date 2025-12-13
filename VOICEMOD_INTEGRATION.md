# VoiceMod Integration Guide

This document outlines how to integrate VoiceMod sound effects into the classroom control system.

## VoiceMod API Overview

VoiceMod provides a REST API and WebSocket interface for controlling sound effects. The integration will allow students to trigger sound effects during class.

## Implementation Steps

### 1. Install VoiceMod SDK

VoiceMod provides SDKs for various platforms. For Python integration:

```bash
pip install voicemod-api  # If available
# OR use REST API directly with requests library
```

### 2. VoiceMod Setup

1. Install VoiceMod Desktop App
2. Enable API access in VoiceMod settings
3. Note the API endpoint (typically `http://localhost:59129`)

### 3. API Endpoints

VoiceMod REST API endpoints (typical):
- `GET /v1/soundboard` - List available sound effects
- `POST /v1/soundboard/play` - Play a sound effect
- `POST /v1/soundboard/stop` - Stop current sound

### 4. Update Server Code

Add VoiceMod client to `server.py`:

```python
import requests

VOICEMOD_HOST = os.getenv('VOICEMOD_HOST', 'localhost')
VOICEMOD_PORT = int(os.getenv('VOICEMOD_PORT', 59129))
VOICEMOD_API_KEY = os.getenv('VOICEMOD_API_KEY', '')

def play_voicemod_sound(sound_id):
    """Play a VoiceMod sound effect"""
    try:
        url = f"http://{VOICEMOD_HOST}:{VOICEMOD_PORT}/v1/soundboard/play"
        headers = {
            'Authorization': f'Bearer {VOICEMOD_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {'soundId': sound_id}
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        logger.error(f"VoiceMod error: {e}")
        return None
```

### 5. Update Web Interface

Add sound effect controls to `web/index.html`:

```html
<div class="control-section">
    <h2>🎵 Sound Effects</h2>
    <div id="sound-effects-list">
        <!-- Populated dynamically -->
    </div>
</div>
```

### 6. Configuration

Add to `.env`:
```
VOICEMOD_HOST=localhost
VOICEMOD_PORT=59129
VOICEMOD_API_KEY=your_api_key_here
```

## Alternative: VoiceMod WebSocket

VoiceMod also supports WebSocket connections for real-time control:

```python
import websocket
import json

def connect_voicemod_ws():
    ws = websocket.create_connection(f"ws://{VOICEMOD_HOST}:{VOICEMOD_PORT}")
    return ws

def play_sound_ws(ws, sound_id):
    message = {
        'action': 'playSound',
        'soundId': sound_id
    }
    ws.send(json.dumps(message))
```

## Security Considerations

1. **Rate Limiting**: Implement rate limiting to prevent spam
2. **Sound Whitelist**: Only allow specific sounds to be played
3. **Cooldown Period**: Add delays between sound plays
4. **Volume Control**: Limit maximum volume

## Example Implementation

See the placeholder endpoint in `server.py`:
- `/voicemod/effect` - Currently returns "coming soon"
- Update this endpoint with actual VoiceMod integration

## Resources

- VoiceMod API Documentation: https://www.voicemod.net/api
- VoiceMod Developer Portal: Check VoiceMod website for latest API docs
- Community Forums: VoiceMod Discord/Forums for support

## Testing

1. Install VoiceMod Desktop
2. Enable API access
3. Test API connection:
   ```python
   python test_voicemod_connection.py
   ```
4. Test sound playback
5. Integrate into main server

## Future Enhancements

- [ ] Sound effect categories
- [ ] Volume control per sound
- [ ] Sound queue system
- [ ] Custom sound uploads
- [ ] Sound effect voting
- [ ] Playback history
