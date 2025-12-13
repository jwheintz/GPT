"""
VoiceMod Integration Module

VoiceMod provides a Control API for programmatic control.
Documentation: https://control-api.voicemod.net/

Prerequisites:
1. VoiceMod installed and running
2. VoiceMod Control API enabled (in VoiceMod settings)
3. API key from VoiceMod (if required)

This module provides:
- Voice changer activation/deactivation
- Soundboard triggering
- Voice effect selection
"""

import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class VoiceModController:
    """
    Controls VoiceMod via its HTTP Control API.
    
    Note: VoiceMod's Control API uses WebSocket, but they also provide
    a REST-like interface for simpler integrations.
    """
    
    # Default VoiceMod Control API endpoint
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 59129
    
    def __init__(self, host: str = None, port: int = None, api_key: str = None):
        """
        Initialize VoiceMod controller.
        
        Args:
            host: VoiceMod API host (default: localhost)
            port: VoiceMod API port (default: 59129)
            api_key: API key if VoiceMod requires authentication
        """
        self.host = host or self.DEFAULT_HOST
        self.port = port or self.DEFAULT_PORT
        self.api_key = api_key
        self.base_url = f"http://{self.host}:{self.port}/v1"
        self.connected = False
        self.available_voices = []
        self.available_soundboard = []
        
    def connect(self) -> bool:
        """
        Test connection to VoiceMod Control API.
        
        Returns:
            True if connected successfully
        """
        try:
            # Try to get VoiceMod status
            response = self._request("GET", "/status")
            if response:
                self.connected = True
                logger.info("Connected to VoiceMod Control API")
                
                # Load available voices and soundboard
                self._load_voices()
                self._load_soundboard()
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to VoiceMod: {e}")
            self.connected = False
            return False
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """
        Make a request to VoiceMod API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            
        Returns:
            Response data or None on error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=5)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"VoiceMod API returned {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.debug("VoiceMod API not available")
            return None
        except Exception as e:
            logger.error(f"VoiceMod API error: {e}")
            return None
    
    def _load_voices(self):
        """Load available voice effects from VoiceMod."""
        try:
            response = self._request("GET", "/voices")
            if response and "voices" in response:
                self.available_voices = response["voices"]
                logger.info(f"Loaded {len(self.available_voices)} VoiceMod voices")
        except Exception as e:
            logger.error(f"Failed to load voices: {e}")
    
    def _load_soundboard(self):
        """Load available soundboard sounds from VoiceMod."""
        try:
            response = self._request("GET", "/soundboard")
            if response and "sounds" in response:
                self.available_soundboard = response["sounds"]
                logger.info(f"Loaded {len(self.available_soundboard)} soundboard sounds")
        except Exception as e:
            logger.error(f"Failed to load soundboard: {e}")
    
    def enable_voice_changer(self) -> bool:
        """
        Enable the VoiceMod voice changer.
        
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/voicechanger/enable")
        return response is not None
    
    def disable_voice_changer(self) -> bool:
        """
        Disable the VoiceMod voice changer.
        
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/voicechanger/disable")
        return response is not None
    
    def toggle_voice_changer(self) -> bool:
        """
        Toggle the VoiceMod voice changer on/off.
        
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/voicechanger/toggle")
        return response is not None
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the active voice effect.
        
        Args:
            voice_id: The voice ID or name to activate
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/voices/select", {"voiceId": voice_id})
        if response:
            logger.info(f"Set VoiceMod voice to: {voice_id}")
            return True
        return False
    
    def play_sound(self, sound_id: str) -> bool:
        """
        Play a soundboard sound.
        
        Args:
            sound_id: The sound ID or name to play
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/soundboard/play", {"soundId": sound_id})
        if response:
            logger.info(f"Playing soundboard sound: {sound_id}")
            return True
        return False
    
    def stop_all_sounds(self) -> bool:
        """
        Stop all currently playing soundboard sounds.
        
        Returns:
            True if successful
        """
        if not self.connected:
            return False
            
        response = self._request("POST", "/soundboard/stop")
        return response is not None
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voice effects.
        
        Returns:
            List of voice dictionaries with id and name
        """
        return self.available_voices
    
    def get_soundboard(self) -> List[Dict[str, Any]]:
        """
        Get list of available soundboard sounds.
        
        Returns:
            List of sound dictionaries with id and name
        """
        return self.available_soundboard
    
    def set_voice_timed(self, voice_id: str, duration_ms: int):
        """
        Set a voice effect for a specific duration, then reset.
        
        Args:
            voice_id: Voice ID to activate
            duration_ms: How long to keep the voice active
        """
        import threading
        import time
        
        if self.set_voice(voice_id):
            def reset_voice():
                time.sleep(duration_ms / 1000)
                # Reset to "clean" voice or disable
                self.set_voice("clean")  # or call disable_voice_changer()
            
            thread = threading.Thread(target=reset_voice, daemon=True)
            thread.start()


# Convenience function for quick testing
def test_voicemod():
    """Test VoiceMod connection and list available effects."""
    vm = VoiceModController()
    
    if vm.connect():
        print("✅ Connected to VoiceMod!")
        print(f"\nAvailable Voices ({len(vm.available_voices)}):")
        for voice in vm.available_voices[:10]:  # Show first 10
            print(f"  - {voice.get('id', 'unknown')}: {voice.get('name', 'unnamed')}")
        
        print(f"\nAvailable Sounds ({len(vm.available_soundboard)}):")
        for sound in vm.available_soundboard[:10]:  # Show first 10
            print(f"  - {sound.get('id', 'unknown')}: {sound.get('name', 'unnamed')}")
    else:
        print("❌ Could not connect to VoiceMod")
        print("   Make sure VoiceMod is running and Control API is enabled")


if __name__ == "__main__":
    test_voicemod()
