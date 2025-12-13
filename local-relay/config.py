"""
Classroom Control - Local Relay Configuration

Copy this file to config_local.py and fill in your values.
config_local.py is gitignored for security.
"""

# =============================================================================
# SUPABASE CONFIGURATION
# Get these from your Supabase project: Settings > API
# =============================================================================
SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"  # e.g., "https://xxxxx.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"      # The "anon" / "public" key

# Table name (must match web frontend config)
TABLE_NAME = "classroom_commands"

# =============================================================================
# OBS WEBSOCKET CONFIGURATION  
# OBS 28+ has WebSocket server built-in. Enable it in:
# Tools > WebSocket Server Settings
# =============================================================================
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Set this if you enabled authentication in OBS

# =============================================================================
# EFFECT MAPPINGS
# Map action names from web interface to OBS source/filter names
# Format: "action_name": {"source": "SourceName", "filter": "FilterName", "type": "toggle/show/trigger"}
# =============================================================================
VISUAL_EFFECTS = {
    # These map to OBS sources or filters you've set up
    # Example: A "Confetti" Browser source that plays an animation
    "confetti": {
        "type": "source",
        "source_name": "Confetti",  # Name of your OBS source
        "duration": 3000,            # How long to show (ms), 0 = toggle
    },
    "thumbsup": {
        "type": "source",
        "source_name": "ThumbsUp",
        "duration": 2000,
    },
    "applause": {
        "type": "source", 
        "source_name": "Applause",
        "duration": 3000,
    },
    "question": {
        "type": "source",
        "source_name": "Question",
        "duration": 5000,
    },
    "lightbulb": {
        "type": "source",
        "source_name": "Lightbulb",
        "duration": 2000,
    },
    "heart": {
        "type": "source",
        "source_name": "Heart",
        "duration": 2000,
    },
    "mindblown": {
        "type": "source",
        "source_name": "MindBlown",
        "duration": 3000,
    },
    "slowdown": {
        "type": "source",
        "source_name": "SlowDown",
        "duration": 5000,
    },
}

# Reaction effects - typically shown as floating emojis
REACTION_EFFECTS = {
    "laugh": {"type": "source", "source_name": "Reaction_Laugh", "duration": 2000},
    "wow": {"type": "source", "source_name": "Reaction_Wow", "duration": 2000},
    "thinking": {"type": "source", "source_name": "Reaction_Thinking", "duration": 2000},
    "fire": {"type": "source", "source_name": "Reaction_Fire", "duration": 2000},
    "star": {"type": "source", "source_name": "Reaction_Star", "duration": 2000},
    "rocket": {"type": "source", "source_name": "Reaction_Rocket", "duration": 2000},
}

# Sound effects - can trigger media sources or VoiceMod (future)
SOUND_EFFECTS = {
    "ding": {"type": "media", "source_name": "SFX_Ding"},
    "drumroll": {"type": "media", "source_name": "SFX_Drumroll"},
    "airhorn": {"type": "media", "source_name": "SFX_Airhorn"},
    "crickets": {"type": "media", "source_name": "SFX_Crickets"},
}

# Poll responses - can show overlays or trigger counter sources
POLL_EFFECTS = {
    "poll_a": {"type": "source", "source_name": "Poll_A", "duration": 1000},
    "poll_b": {"type": "source", "source_name": "Poll_B", "duration": 1000},
    "poll_c": {"type": "source", "source_name": "Poll_C", "duration": 1000},
    "poll_d": {"type": "source", "source_name": "Poll_D", "duration": 1000},
    "poll_yes": {"type": "source", "source_name": "Poll_Yes", "duration": 1000},
    "poll_no": {"type": "source", "source_name": "Poll_No", "duration": 1000},
}

# =============================================================================
# ADVANCED: FILTER EFFECTS
# For applying OBS filters (color correction, blur, etc.)
# =============================================================================
FILTER_EFFECTS = {
    # Example: Apply a "Party Mode" color filter to your camera
    # "party_mode": {
    #     "type": "filter",
    #     "source_name": "Webcam",
    #     "filter_name": "PartyColors",
    #     "duration": 5000,
    # },
}

# =============================================================================
# VOICEMOD INTEGRATION
# Enable VoiceMod Control API in VoiceMod settings first
# Documentation: https://control-api.voicemod.net/
# =============================================================================
VOICEMOD_ENABLED = False  # Set to True to enable
VOICEMOD_HOST = "localhost"
VOICEMOD_PORT = 59129
VOICEMOD_API_KEY = ""  # If VoiceMod requires authentication

# VoiceMod voice effects - map to web interface actions
VOICEMOD_EFFECTS = {
    # Voice changing effects
    # "robot_voice": {
    #     "type": "voice",
    #     "voice_id": "robot",
    #     "duration": 10000,  # 10 seconds
    # },
    # "chipmunk_voice": {
    #     "type": "voice", 
    #     "voice_id": "chipmunk",
    #     "duration": 10000,
    # },
    # "deep_voice": {
    #     "type": "voice",
    #     "voice_id": "deep",
    #     "duration": 10000,
    # },
    
    # Soundboard effects (plays through VoiceMod)
    # "vm_airhorn": {
    #     "type": "voicemod_sound",
    #     "sound_id": "airhorn",
    # },
    # "vm_applause": {
    #     "type": "voicemod_sound",
    #     "sound_id": "applause",
    # },
}

# =============================================================================
# RATE LIMITING & SAFETY
# =============================================================================
# Minimum time between processing commands (ms)
COMMAND_RATE_LIMIT = 500

# Maximum commands to process per minute (0 = unlimited)
MAX_COMMANDS_PER_MINUTE = 60

# Auto-pause after this many commands in quick succession
SPAM_THRESHOLD = 10
SPAM_WINDOW_SECONDS = 5

# =============================================================================
# LOGGING
# =============================================================================
LOG_FILE = "classroom_relay.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
