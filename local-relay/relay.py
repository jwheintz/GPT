#!/usr/bin/env python3
"""
Classroom Control - Local Relay Application

This application:
1. Listens to Supabase for incoming commands from the web interface
2. Translates commands to OBS WebSocket actions
3. Provides a system tray icon with kill switch
4. Supports future VoiceMod integration

Run: python relay.py
Build EXE: pyinstaller --onefile --windowed --icon=icon.ico relay.py
"""

import sys
import time
import threading
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Optional, Dict, Any
import queue

# Try to import config_local first (user's custom config), fall back to config
try:
    import config_local as config
except ImportError:
    import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VoiceModHandler:
    """Handles VoiceMod integration (optional)."""
    
    def __init__(self):
        self.controller = None
        self.enabled = False
        
    def connect(self) -> bool:
        """Try to connect to VoiceMod if enabled."""
        if not config.VOICEMOD_ENABLED:
            logger.info("VoiceMod integration disabled in config")
            return False
            
        try:
            from voicemod import VoiceModController
            self.controller = VoiceModController()
            
            if self.controller.connect():
                self.enabled = True
                logger.info("VoiceMod integration active")
                return True
            else:
                logger.warning("VoiceMod not available - continuing without it")
                return False
                
        except ImportError:
            logger.warning("VoiceMod module not found")
            return False
        except Exception as e:
            logger.warning(f"VoiceMod connection failed: {e}")
            return False
    
    def execute(self, effect: dict) -> bool:
        """Execute a VoiceMod effect."""
        if not self.enabled or not self.controller:
            return False
            
        try:
            effect_type = effect.get("type", "voice")
            
            if effect_type == "voice":
                voice_id = effect.get("voice_id")
                duration = effect.get("duration", 0)
                
                if duration > 0:
                    self.controller.set_voice_timed(voice_id, duration)
                else:
                    self.controller.set_voice(voice_id)
                return True
                
            elif effect_type == "sound":
                sound_id = effect.get("sound_id")
                self.controller.play_sound(sound_id)
                return True
                
            elif effect_type == "toggle":
                self.controller.toggle_voice_changer()
                return True
                
        except Exception as e:
            logger.error(f"VoiceMod effect error: {e}")
            return False


class OBSController:
    """Handles communication with OBS via WebSocket."""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self._pending_hides = {}  # Track sources to hide after duration
        
    def connect(self) -> bool:
        """Connect to OBS WebSocket server."""
        try:
            import obsws_python as obs
            
            self.client = obs.ReqClient(
                host=config.OBS_HOST,
                port=config.OBS_PORT,
                password=config.OBS_PASSWORD or None
            )
            self.connected = True
            logger.info(f"Connected to OBS at {config.OBS_HOST}:{config.OBS_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to OBS: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from OBS."""
        if self.client:
            try:
                self.client = None
            except:
                pass
        self.connected = False
        logger.info("Disconnected from OBS")
    
    def show_source(self, source_name: str, scene_name: str = None) -> bool:
        """Show a source in OBS."""
        if not self.connected or not self.client:
            return False
            
        try:
            # Get current scene if not specified
            if not scene_name:
                response = self.client.get_current_program_scene()
                scene_name = response.current_program_scene_name
            
            # Get the scene item ID
            response = self.client.get_scene_item_id(scene_name, source_name)
            item_id = response.scene_item_id
            
            # Enable the source
            self.client.set_scene_item_enabled(scene_name, item_id, True)
            logger.debug(f"Showed source: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error showing source {source_name}: {e}")
            return False
    
    def hide_source(self, source_name: str, scene_name: str = None) -> bool:
        """Hide a source in OBS."""
        if not self.connected or not self.client:
            return False
            
        try:
            if not scene_name:
                response = self.client.get_current_program_scene()
                scene_name = response.current_program_scene_name
            
            response = self.client.get_scene_item_id(scene_name, source_name)
            item_id = response.scene_item_id
            
            self.client.set_scene_item_enabled(scene_name, item_id, False)
            logger.debug(f"Hid source: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error hiding source {source_name}: {e}")
            return False
    
    def show_source_timed(self, source_name: str, duration_ms: int):
        """Show a source for a specific duration, then hide it."""
        if self.show_source(source_name):
            # Schedule hiding
            def hide_later():
                time.sleep(duration_ms / 1000)
                self.hide_source(source_name)
            
            thread = threading.Thread(target=hide_later, daemon=True)
            thread.start()
    
    def toggle_filter(self, source_name: str, filter_name: str, enabled: bool) -> bool:
        """Toggle a filter on a source."""
        if not self.connected or not self.client:
            return False
            
        try:
            self.client.set_source_filter_enabled(source_name, filter_name, enabled)
            logger.debug(f"Set filter {filter_name} on {source_name} to {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error toggling filter: {e}")
            return False
    
    def play_media_source(self, source_name: str) -> bool:
        """Trigger a media source to play (restart from beginning)."""
        if not self.connected or not self.client:
            return False
            
        try:
            self.client.trigger_media_input_action(source_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
            logger.debug(f"Triggered media source: {source_name}")
            return True
        except Exception as e:
            logger.error(f"Error playing media source {source_name}: {e}")
            return False


class SupabaseListener:
    """Listens to Supabase for incoming commands."""
    
    def __init__(self, callback):
        self.callback = callback
        self.client = None
        self.channel = None
        self.running = False
        
    def connect(self) -> bool:
        """Connect to Supabase and subscribe to changes."""
        try:
            from supabase import create_client
            
            self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Connected to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return False
    
    def start_listening(self):
        """Start listening for real-time updates."""
        if not self.client:
            return False
        
        self.running = True
        
        # Use polling approach for simplicity (realtime requires async)
        def poll_commands():
            last_check = datetime.utcnow() - timedelta(seconds=5)
            
            while self.running:
                try:
                    # Query for new commands since last check
                    response = self.client.table(config.TABLE_NAME) \
                        .select("*") \
                        .gt("timestamp", last_check.isoformat()) \
                        .order("timestamp") \
                        .execute()
                    
                    if response.data:
                        for command in response.data:
                            self.callback(command)
                        # Update last check to most recent command
                        last_check = datetime.fromisoformat(
                            response.data[-1]["timestamp"].replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                    
                    time.sleep(0.5)  # Poll every 500ms
                    
                except Exception as e:
                    logger.error(f"Error polling commands: {e}")
                    time.sleep(2)  # Back off on error
        
        self.poll_thread = threading.Thread(target=poll_commands, daemon=True)
        self.poll_thread.start()
        logger.info("Started listening for commands")
    
    def stop_listening(self):
        """Stop listening for updates."""
        self.running = False
    
    def set_paused(self, paused: bool) -> bool:
        """Update the system paused status in Supabase."""
        if not self.client:
            return False
            
        try:
            # Upsert the system status
            self.client.table("system_status").upsert({
                "id": "main",
                "paused": paused,
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            logger.info(f"Set system paused to: {paused}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting paused status: {e}")
            return False


class ClassroomRelay:
    """Main application controller."""
    
    def __init__(self):
        self.obs = OBSController()
        self.voicemod = VoiceModHandler()
        self.supabase = SupabaseListener(self.handle_command)
        self.paused = False
        self.command_queue = queue.Queue()
        self.command_times = deque(maxlen=config.SPAM_THRESHOLD)
        self.last_command_time = 0
        
        # Combine all effect mappings
        self.effects = {
            **config.VISUAL_EFFECTS,
            **config.REACTION_EFFECTS,
            **config.SOUND_EFFECTS,
            **config.POLL_EFFECTS,
            **config.FILTER_EFFECTS,
        }
        
        # Add VoiceMod effects if configured
        if hasattr(config, 'VOICEMOD_EFFECTS'):
            self.effects.update(config.VOICEMOD_EFFECTS)
    
    def start(self) -> bool:
        """Start the relay service."""
        logger.info("Starting Classroom Control Relay...")
        
        # Connect to OBS
        if not self.obs.connect():
            logger.warning("OBS connection failed - will retry when processing commands")
        
        # Try to connect to VoiceMod (optional)
        self.voicemod.connect()
        
        # Connect to Supabase
        if not self.supabase.connect():
            logger.error("Supabase connection failed - cannot start")
            return False
        
        # Start listening
        self.supabase.start_listening()
        
        # Start command processor
        self.processor_thread = threading.Thread(target=self.process_commands, daemon=True)
        self.processor_thread.start()
        
        logger.info("Classroom Control Relay started successfully!")
        return True
    
    def stop(self):
        """Stop the relay service."""
        logger.info("Stopping Classroom Control Relay...")
        self.supabase.stop_listening()
        self.obs.disconnect()
    
    def handle_command(self, command: Dict[str, Any]):
        """Handle an incoming command from Supabase."""
        if self.paused:
            logger.debug(f"Ignoring command (paused): {command}")
            return
        
        self.command_queue.put(command)
    
    def process_commands(self):
        """Process commands from the queue with rate limiting."""
        while True:
            try:
                command = self.command_queue.get(timeout=1)
                
                # Rate limiting
                now = time.time()
                if now - self.last_command_time < config.COMMAND_RATE_LIMIT / 1000:
                    time.sleep((config.COMMAND_RATE_LIMIT / 1000) - (now - self.last_command_time))
                
                # Spam detection
                self.command_times.append(now)
                if len(self.command_times) >= config.SPAM_THRESHOLD:
                    time_window = now - self.command_times[0]
                    if time_window < config.SPAM_WINDOW_SECONDS:
                        logger.warning("Spam detected! Auto-pausing for 10 seconds")
                        self.set_paused(True)
                        time.sleep(10)
                        self.set_paused(False)
                        self.command_times.clear()
                        continue
                
                self.execute_command(command)
                self.last_command_time = time.time()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def execute_command(self, command: Dict[str, Any]):
        """Execute a command in OBS or VoiceMod."""
        action = command.get("action")
        category = command.get("category")
        
        logger.info(f"Executing command: {action} (category: {category})")
        
        # Reconnect to OBS if needed
        if not self.obs.connected:
            self.obs.connect()
        
        if action not in self.effects:
            logger.warning(f"Unknown action: {action}")
            return
        
        effect = self.effects[action]
        effect_type = effect.get("type", "source")
        
        try:
            # Handle VoiceMod effects
            if effect_type in ("voice", "voicemod_sound", "voicemod_toggle"):
                if self.voicemod.enabled:
                    self.voicemod.execute(effect)
                else:
                    logger.debug(f"VoiceMod not available for effect: {action}")
                return
            
            # Handle OBS effects
            if effect_type == "source":
                source_name = effect.get("source_name")
                duration = effect.get("duration", 0)
                
                if duration > 0:
                    self.obs.show_source_timed(source_name, duration)
                else:
                    self.obs.show_source(source_name)
                    
            elif effect_type == "filter":
                source_name = effect.get("source_name")
                filter_name = effect.get("filter_name")
                duration = effect.get("duration", 0)
                
                self.obs.toggle_filter(source_name, filter_name, True)
                
                if duration > 0:
                    def disable_later():
                        time.sleep(duration / 1000)
                        self.obs.toggle_filter(source_name, filter_name, False)
                    threading.Thread(target=disable_later, daemon=True).start()
                    
            elif effect_type == "media":
                source_name = effect.get("source_name")
                self.obs.play_media_source(source_name)
                
        except Exception as e:
            logger.error(f"Error executing command {action}: {e}")
    
    def set_paused(self, paused: bool):
        """Set the paused state."""
        self.paused = paused
        self.supabase.set_paused(paused)
        
        # Clear command queue when pausing
        if paused:
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except queue.Empty:
                    break
        
        logger.info(f"System {'PAUSED' if paused else 'RESUMED'}")
    
    def toggle_paused(self):
        """Toggle the paused state."""
        self.set_paused(not self.paused)
        return self.paused


def create_tray_icon(relay: ClassroomRelay):
    """Create system tray icon with menu."""
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        logger.warning("pystray or Pillow not installed - running without system tray")
        return None
    
    def create_image(color):
        """Create a simple icon image."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a circle
        margin = 4
        draw.ellipse([margin, margin, size-margin, size-margin], fill=color)
        
        # Draw "C" for Classroom
        draw.text((size//2 - 12, size//2 - 15), "C", fill="white")
        
        return image
    
    def get_icon_image():
        """Get icon based on current state."""
        if relay.paused:
            return create_image("#ef4444")  # Red when paused
        elif relay.obs.connected:
            return create_image("#22c55e")  # Green when connected
        else:
            return create_image("#f59e0b")  # Yellow when OBS disconnected
    
    def on_toggle_pause(icon, item):
        """Toggle pause from tray menu."""
        is_paused = relay.toggle_paused()
        icon.icon = get_icon_image()
        icon.title = f"Classroom Control ({'PAUSED' if is_paused else 'Active'})"
    
    def on_reconnect_obs(icon, item):
        """Reconnect to OBS."""
        relay.obs.disconnect()
        if relay.obs.connect():
            icon.icon = get_icon_image()
    
    def on_quit(icon, item):
        """Quit the application."""
        relay.stop()
        icon.stop()
    
    # Create menu
    menu = pystray.Menu(
        pystray.MenuItem(
            lambda item: "▶️ Resume" if relay.paused else "⏸️ Pause (KILL SWITCH)",
            on_toggle_pause,
            default=True
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🔄 Reconnect OBS", on_reconnect_obs),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Quit", on_quit)
    )
    
    # Create icon
    icon = pystray.Icon(
        "classroom_control",
        get_icon_image(),
        "Classroom Control (Active)",
        menu
    )
    
    return icon


def main():
    """Main entry point."""
    print("=" * 50)
    print("  Classroom Control - Local Relay")
    print("=" * 50)
    print()
    
    # Check configuration
    if config.SUPABASE_URL == "YOUR_SUPABASE_PROJECT_URL":
        print("ERROR: Please configure Supabase settings in config.py or config_local.py")
        print("See the setup documentation for instructions.")
        sys.exit(1)
    
    # Create and start relay
    relay = ClassroomRelay()
    
    if not relay.start():
        print("Failed to start relay service")
        sys.exit(1)
    
    # Create system tray icon
    icon = create_tray_icon(relay)
    
    if icon:
        print()
        print("✅ Relay is running!")
        print("   - Look for the icon in your system tray")
        print("   - Double-click or right-click for options")
        print("   - Use 'Pause' as kill switch to stop all incoming effects")
        print()
        
        # Run tray icon (blocking)
        icon.run()
    else:
        # No tray icon, run in console mode
        print()
        print("✅ Relay is running in console mode!")
        print("   Press Ctrl+C to stop")
        print("   Press 'p' + Enter to toggle pause")
        print()
        
        try:
            while True:
                user_input = input()
                if user_input.lower() == 'p':
                    is_paused = relay.toggle_paused()
                    print(f"System {'PAUSED' if is_paused else 'RESUMED'}")
                elif user_input.lower() == 'q':
                    break
        except KeyboardInterrupt:
            pass
        
        relay.stop()
    
    print("Goodbye!")


if __name__ == "__main__":
    main()
