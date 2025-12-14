"""
Plugin database and catalog management.
Maintains a database of known OBS plugins with version information.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Plugin categories for organization."""
    STREAMING = "streaming"
    RECORDING = "recording"
    SOURCES = "sources"
    FILTERS = "filters"
    AUDIO = "audio"
    VIDEO = "video"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    UTILITY = "utility"
    THEMES = "themes"
    OTHER = "other"


@dataclass
class PluginInfo:
    """Information about an OBS plugin."""
    
    id: str  # Unique identifier
    name: str
    description: str
    author: str
    category: str
    
    # Version info
    latest_version: str
    release_date: str
    
    # Download info
    download_url: str
    github_url: str
    homepage_url: str
    
    # File info
    dll_name: str  # Main DLL file name
    additional_files: str  # JSON list of additional files/folders
    
    # Metadata
    is_popular: bool = False
    is_recommended: bool = False
    obs_min_version: str = "28.0.0"
    obs_max_version: str = ""
    
    # Timestamps
    added_date: str = ""
    updated_date: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginInfo':
        return cls(**data)


@dataclass
class InstalledPlugin:
    """Information about an installed plugin."""
    
    plugin_id: str
    name: str
    dll_path: str
    version: str
    install_date: str
    file_hash: str
    file_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PluginDatabase:
    """SQLite database for plugin catalog and installed plugins."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from .config import get_config
            config = get_config()
            db_path = str(Path(config.config.app_data_path) / "plugins.db")
        
        self.db_path = db_path
        self._init_database()
        self._populate_default_catalog()
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Plugin catalog table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_catalog (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    category TEXT,
                    latest_version TEXT,
                    release_date TEXT,
                    download_url TEXT,
                    github_url TEXT,
                    homepage_url TEXT,
                    dll_name TEXT,
                    additional_files TEXT,
                    is_popular INTEGER DEFAULT 0,
                    is_recommended INTEGER DEFAULT 0,
                    obs_min_version TEXT,
                    obs_max_version TEXT,
                    added_date TEXT,
                    updated_date TEXT
                )
            ''')
            
            # Installed plugins table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS installed_plugins (
                    plugin_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dll_path TEXT,
                    version TEXT,
                    install_date TEXT,
                    file_hash TEXT,
                    file_size INTEGER
                )
            ''')
            
            # Plugin archives table (for rollback)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_archives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    archive_date TEXT NOT NULL,
                    file_hash TEXT,
                    UNIQUE(plugin_id, version)
                )
            ''')
            
            # Metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            conn.commit()
    
    def _populate_default_catalog(self) -> None:
        """Populate the catalog with known popular plugins."""
        
        # Check if already populated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM plugin_catalog")
            count = cursor.fetchone()[0]
            if count > 0:
                return
        
        # Default plugin catalog - Popular and recommended plugins
        default_plugins = self._get_default_plugins()
        
        for plugin in default_plugins:
            self.add_or_update_plugin(plugin)
        
        logger.info(f"Populated catalog with {len(default_plugins)} default plugins")
    
    def _get_default_plugins(self) -> List[PluginInfo]:
        """Get the default list of popular OBS plugins."""
        now = datetime.now().isoformat()
        
        return [
            # BarRaider Plugins
            PluginInfo(
                id="streamdeck-obs",
                name="Stream Deck OBS Plugin",
                description="Control OBS Studio from your Elgato Stream Deck",
                author="BarRaider",
                category=PluginCategory.INTEGRATION.value,
                latest_version="1.9.0",
                release_date="2024-01-15",
                download_url="https://github.com/BarRaider/streamdeck-obs-plugin/releases/latest",
                github_url="https://github.com/BarRaider/streamdeck-obs-plugin",
                homepage_url="https://barraider.com/",
                dll_name="",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            # Source plugins
            PluginInfo(
                id="obs-websocket",
                name="OBS WebSocket",
                description="Remote control OBS via WebSockets (now built into OBS 28+)",
                author="OBS Project",
                category=PluginCategory.INTEGRATION.value,
                latest_version="5.3.0",
                release_date="2024-02-01",
                download_url="https://github.com/obsproject/obs-websocket/releases/latest",
                github_url="https://github.com/obsproject/obs-websocket",
                homepage_url="https://obsproject.com/",
                dll_name="obs-websocket.dll",
                additional_files='["data/obs-plugins/obs-websocket"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-ndi",
                name="OBS NDI",
                description="Network Device Interface (NDI) integration for OBS",
                author="Palakis",
                category=PluginCategory.VIDEO.value,
                latest_version="4.13.0",
                release_date="2024-01-20",
                download_url="https://github.com/obs-ndi/obs-ndi/releases/latest",
                github_url="https://github.com/obs-ndi/obs-ndi",
                homepage_url="https://github.com/obs-ndi/obs-ndi",
                dll_name="obs-ndi.dll",
                additional_files='["data/obs-plugins/obs-ndi"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-virtualcam",
                name="OBS Virtual Camera",
                description="Virtual camera output (now built into OBS 26+)",
                author="OBS Project",
                category=PluginCategory.VIDEO.value,
                latest_version="2.0.5",
                release_date="2023-06-01",
                download_url="https://github.com/obsproject/obs-studio/releases/latest",
                github_url="https://github.com/obsproject/obs-studio",
                homepage_url="https://obsproject.com/",
                dll_name="win-dshow.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-browser",
                name="OBS Browser Source",
                description="Browser source for displaying web content",
                author="OBS Project",
                category=PluginCategory.SOURCES.value,
                latest_version="2.23.0",
                release_date="2024-01-10",
                download_url="https://github.com/obsproject/obs-browser/releases/latest",
                github_url="https://github.com/obsproject/obs-browser",
                homepage_url="https://obsproject.com/",
                dll_name="obs-browser.dll",
                additional_files='["obs-plugins/64bit/obs-browser-page.exe"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            # StreamElements
            PluginInfo(
                id="streamelements-obs",
                name="StreamElements OBS.Live",
                description="StreamElements integration with activity feed, chat, and more",
                author="StreamElements",
                category=PluginCategory.STREAMING.value,
                latest_version="1.5.0",
                release_date="2024-01-25",
                download_url="https://streamelements.com/obslive",
                github_url="",
                homepage_url="https://streamelements.com/",
                dll_name="obs-browser.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            # Audio plugins
            PluginInfo(
                id="obs-asio",
                name="OBS ASIO",
                description="ASIO audio device support for professional audio interfaces",
                author="Andersama",
                category=PluginCategory.AUDIO.value,
                latest_version="3.1.0",
                release_date="2023-12-15",
                download_url="https://github.com/Andersama/obs-asio/releases/latest",
                github_url="https://github.com/Andersama/obs-asio",
                homepage_url="https://github.com/Andersama/obs-asio",
                dll_name="obs-asio.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-audio-monitor",
                name="Audio Monitor",
                description="Monitor audio sources independently of OBS output",
                author="Exeldro",
                category=PluginCategory.AUDIO.value,
                latest_version="0.8.5",
                release_date="2024-01-05",
                download_url="https://github.com/exeldro/obs-audio-monitor/releases/latest",
                github_url="https://github.com/exeldro/obs-audio-monitor",
                homepage_url="https://obsproject.com/forum/resources/audio-monitor.1186/",
                dll_name="audio-monitor.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="waveform",
                name="Waveform",
                description="Audio visualization with waveforms and spectrum analyzers",
                author="phandasm",
                category=PluginCategory.AUDIO.value,
                latest_version="1.8.0",
                release_date="2023-11-20",
                download_url="https://github.com/phandasm/waveform/releases/latest",
                github_url="https://github.com/phandasm/waveform",
                homepage_url="https://obsproject.com/forum/resources/waveform.1423/",
                dll_name="waveform.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            # Video filters
            PluginInfo(
                id="obs-shaderfilter",
                name="Shader Filter",
                description="Apply custom HLSL/GLSL shaders as filters",
                author="Exeldro",
                category=PluginCategory.FILTERS.value,
                latest_version="2.3.0",
                release_date="2024-01-12",
                download_url="https://github.com/exeldro/obs-shaderfilter/releases/latest",
                github_url="https://github.com/exeldro/obs-shaderfilter",
                homepage_url="https://obsproject.com/forum/resources/obs-shaderfilter.1736/",
                dll_name="obs-shaderfilter.dll",
                additional_files='["data/obs-plugins/obs-shaderfilter"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-streamfx",
                name="StreamFX",
                description="Advanced filters, sources, and transitions",
                author="Xaymar",
                category=PluginCategory.FILTERS.value,
                latest_version="0.12.0",
                release_date="2023-10-01",
                download_url="https://github.com/Xaymar/obs-StreamFX/releases/latest",
                github_url="https://github.com/Xaymar/obs-StreamFX",
                homepage_url="https://streamfx.xaymar.com/",
                dll_name="StreamFX.dll",
                additional_files='["data/obs-plugins/StreamFX"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-move-transition",
                name="Move Transition",
                description="Animate source position, size, and crop in transitions",
                author="Exeldro",
                category=PluginCategory.FILTERS.value,
                latest_version="3.0.0",
                release_date="2024-02-01",
                download_url="https://github.com/exeldro/obs-move-transition/releases/latest",
                github_url="https://github.com/exeldro/obs-move-transition",
                homepage_url="https://obsproject.com/forum/resources/move.913/",
                dll_name="move-transition.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-backgroundremoval",
                name="Background Removal",
                description="AI-powered background removal without green screen",
                author="royshil",
                category=PluginCategory.FILTERS.value,
                latest_version="1.1.7",
                release_date="2024-01-28",
                download_url="https://github.com/occ-ai/obs-backgroundremoval/releases/latest",
                github_url="https://github.com/occ-ai/obs-backgroundremoval",
                homepage_url="https://obsproject.com/forum/resources/background-removal-portrait-segmentation.1260/",
                dll_name="obs-backgroundremoval.dll",
                additional_files='["data/obs-plugins/obs-backgroundremoval"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-composite-blur",
                name="Composite Blur",
                description="Advanced blur filters with multiple algorithms",
                author="FiniteSingularity",
                category=PluginCategory.FILTERS.value,
                latest_version="1.1.0",
                release_date="2024-01-15",
                download_url="https://github.com/FiniteSingularity/obs-composite-blur/releases/latest",
                github_url="https://github.com/FiniteSingularity/obs-composite-blur",
                homepage_url="https://obsproject.com/forum/resources/composite-blur.1780/",
                dll_name="obs-composite-blur.dll",
                additional_files='["data/obs-plugins/obs-composite-blur"]',
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            # Source plugins
            PluginInfo(
                id="obs-source-record",
                name="Source Record",
                description="Record individual sources separately",
                author="Exeldro",
                category=PluginCategory.RECORDING.value,
                latest_version="0.4.0",
                release_date="2024-01-10",
                download_url="https://github.com/exeldro/obs-source-record/releases/latest",
                github_url="https://github.com/exeldro/obs-source-record",
                homepage_url="https://obsproject.com/forum/resources/source-record.1285/",
                dll_name="source-record.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-source-clone",
                name="Source Clone",
                description="Clone sources across scenes with independent properties",
                author="Exeldro",
                category=PluginCategory.SOURCES.value,
                latest_version="0.1.5",
                release_date="2023-12-01",
                download_url="https://github.com/exeldro/obs-source-clone/releases/latest",
                github_url="https://github.com/exeldro/obs-source-clone",
                homepage_url="https://obsproject.com/forum/resources/source-clone.1632/",
                dll_name="source-clone.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-text-pthread",
                name="Advanced Text GDI+",
                description="Enhanced text source with more options",
                author="Exeldro",
                category=PluginCategory.SOURCES.value,
                latest_version="1.0.0",
                release_date="2023-08-15",
                download_url="https://github.com/exeldro/obs-text-pthread/releases/latest",
                github_url="https://github.com/exeldro/obs-text-pthread",
                homepage_url="https://obsproject.com/forum/resources/text-pthread.1756/",
                dll_name="text-pthread.dll",
                additional_files="[]",
                is_popular=False,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            # Automation
            PluginInfo(
                id="advanced-scene-switcher",
                name="Advanced Scene Switcher",
                description="Powerful automatic scene switching based on conditions",
                author="WarmUpTill",
                category=PluginCategory.AUTOMATION.value,
                latest_version="1.25.0",
                release_date="2024-02-05",
                download_url="https://github.com/WarmUpTill/SceneSwitcher/releases/latest",
                github_url="https://github.com/WarmUpTill/SceneSwitcher",
                homepage_url="https://obsproject.com/forum/resources/advanced-scene-switcher.395/",
                dll_name="advanced-scene-switcher.dll",
                additional_files='["data/obs-plugins/advanced-scene-switcher"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-transition-table",
                name="Transition Table",
                description="Set different transitions for specific scene changes",
                author="Exeldro",
                category=PluginCategory.AUTOMATION.value,
                latest_version="0.2.8",
                release_date="2024-01-08",
                download_url="https://github.com/exeldro/obs-transition-table/releases/latest",
                github_url="https://github.com/exeldro/obs-transition-table",
                homepage_url="https://obsproject.com/forum/resources/transition-table.1174/",
                dll_name="transition-table.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            # Integration
            PluginInfo(
                id="obs-teleport",
                name="Teleport",
                description="NDI-like video/audio transport over network",
                author="fzwoch",
                category=PluginCategory.VIDEO.value,
                latest_version="0.7.0",
                release_date="2023-11-10",
                download_url="https://github.com/fzwoch/obs-teleport/releases/latest",
                github_url="https://github.com/fzwoch/obs-teleport",
                homepage_url="https://obsproject.com/forum/resources/teleport.1178/",
                dll_name="obs-teleport.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-rtspserver",
                name="RTSP Server",
                description="Stream OBS output via RTSP protocol",
                author="iamscottxu",
                category=PluginCategory.STREAMING.value,
                latest_version="3.0.0",
                release_date="2024-01-20",
                download_url="https://github.com/iamscottxu/obs-rtspserver/releases/latest",
                github_url="https://github.com/iamscottxu/obs-rtspserver",
                homepage_url="https://obsproject.com/forum/resources/obs-rtspserver.1037/",
                dll_name="obs-rtspserver.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-localvocal",
                name="LocalVocal",
                description="Local speech-to-text transcription using AI",
                author="occ-ai",
                category=PluginCategory.AUDIO.value,
                latest_version="0.3.0",
                release_date="2024-01-30",
                download_url="https://github.com/occ-ai/obs-localvocal/releases/latest",
                github_url="https://github.com/occ-ai/obs-localvocal",
                homepage_url="https://obsproject.com/forum/resources/localvocal-live-stream-ai-assistant.1769/",
                dll_name="obs-localvocal.dll",
                additional_files='["data/obs-plugins/obs-localvocal"]',
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="input-overlay",
                name="Input Overlay",
                description="Show keyboard, mouse, and gamepad inputs on stream",
                author="univrsal",
                category=PluginCategory.SOURCES.value,
                latest_version="5.0.5",
                release_date="2024-01-05",
                download_url="https://github.com/univrsal/input-overlay/releases/latest",
                github_url="https://github.com/univrsal/input-overlay",
                homepage_url="https://obsproject.com/forum/resources/input-overlay.552/",
                dll_name="input-overlay.dll",
                additional_files='["data/obs-plugins/input-overlay"]',
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-multi-rtmp",
                name="Multi RTMP",
                description="Stream to multiple RTMP destinations simultaneously",
                author="sorayuki",
                category=PluginCategory.STREAMING.value,
                latest_version="0.5.0",
                release_date="2024-01-18",
                download_url="https://github.com/sorayuki/obs-multi-rtmp/releases/latest",
                github_url="https://github.com/sorayuki/obs-multi-rtmp",
                homepage_url="https://obsproject.com/forum/resources/multiple-rtmp-outputs-plugin.964/",
                dll_name="obs-multi-rtmp.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-nvfbc",
                name="NvFBC Source",
                description="NVIDIA frame buffer capture for lower latency screen capture",
                author="pj-games",
                category=PluginCategory.SOURCES.value,
                latest_version="0.0.9",
                release_date="2023-09-01",
                download_url="https://github.com/pj-games/obs-nvfbc/releases/latest",
                github_url="https://github.com/pj-games/obs-nvfbc",
                homepage_url="https://obsproject.com/forum/resources/obs-nvfbc.796/",
                dll_name="nvfbc.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                obs_min_version="28.0.0",
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-replay-source",
                name="Replay Source",
                description="Replay buffer as a source for instant replays",
                author="Exeldro",
                category=PluginCategory.SOURCES.value,
                latest_version="1.7.0",
                release_date="2024-01-02",
                download_url="https://github.com/exeldro/obs-replay-source/releases/latest",
                github_url="https://github.com/exeldro/obs-replay-source",
                homepage_url="https://obsproject.com/forum/resources/replay-source.686/",
                dll_name="replay-source.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=True,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-scene-collection-manager",
                name="Scene Collection Manager",
                description="Backup and manage scene collections",
                author="Exeldro",
                category=PluginCategory.UTILITY.value,
                latest_version="0.1.0",
                release_date="2023-12-20",
                download_url="https://github.com/exeldro/obs-scene-collection-manager/releases/latest",
                github_url="https://github.com/exeldro/obs-scene-collection-manager",
                homepage_url="https://obsproject.com/forum/resources/scene-collection-manager.1517/",
                dll_name="scene-collection-manager.dll",
                additional_files="[]",
                is_popular=False,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
            
            PluginInfo(
                id="obs-downstream-keyer",
                name="Downstream Keyer",
                description="Add overlays after all scene transitions",
                author="Exeldro",
                category=PluginCategory.SOURCES.value,
                latest_version="0.3.0",
                release_date="2024-01-15",
                download_url="https://github.com/exeldro/obs-downstream-keyer/releases/latest",
                github_url="https://github.com/exeldro/obs-downstream-keyer",
                homepage_url="https://obsproject.com/forum/resources/downstream-keyer.1254/",
                dll_name="downstream-keyer.dll",
                additional_files="[]",
                is_popular=True,
                is_recommended=False,
                added_date=now,
                updated_date=now
            ),
        ]
    
    def add_or_update_plugin(self, plugin: PluginInfo) -> None:
        """Add or update a plugin in the catalog."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO plugin_catalog
                (id, name, description, author, category, latest_version, release_date,
                 download_url, github_url, homepage_url, dll_name, additional_files,
                 is_popular, is_recommended, obs_min_version, obs_max_version,
                 added_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin.id, plugin.name, plugin.description, plugin.author,
                plugin.category, plugin.latest_version, plugin.release_date,
                plugin.download_url, plugin.github_url, plugin.homepage_url,
                plugin.dll_name, plugin.additional_files,
                1 if plugin.is_popular else 0, 1 if plugin.is_recommended else 0,
                plugin.obs_min_version, plugin.obs_max_version,
                plugin.added_date, plugin.updated_date
            ))
            conn.commit()
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get a plugin from the catalog by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugin_catalog WHERE id = ?", (plugin_id,))
            row = cursor.fetchone()
            
            if row:
                return PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                )
            return None
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all plugins from the catalog."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugin_catalog ORDER BY name")
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                ))
            return plugins
    
    def get_popular_plugins(self) -> List[PluginInfo]:
        """Get all popular plugins."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugin_catalog WHERE is_popular = 1 ORDER BY name")
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                ))
            return plugins
    
    def get_recommended_plugins(self) -> List[PluginInfo]:
        """Get all recommended plugins."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugin_catalog WHERE is_recommended = 1 ORDER BY name")
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                ))
            return plugins
    
    def get_plugins_by_category(self, category: str) -> List[PluginInfo]:
        """Get plugins by category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plugin_catalog WHERE category = ? ORDER BY name", (category,))
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                ))
            return plugins
    
    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search plugins by name, description, or author."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM plugin_catalog 
                WHERE name LIKE ? OR description LIKE ? OR author LIKE ?
                ORDER BY is_popular DESC, name
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(PluginInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    author=row['author'],
                    category=row['category'],
                    latest_version=row['latest_version'],
                    release_date=row['release_date'],
                    download_url=row['download_url'],
                    github_url=row['github_url'],
                    homepage_url=row['homepage_url'],
                    dll_name=row['dll_name'],
                    additional_files=row['additional_files'],
                    is_popular=bool(row['is_popular']),
                    is_recommended=bool(row['is_recommended']),
                    obs_min_version=row['obs_min_version'],
                    obs_max_version=row['obs_max_version'] or "",
                    added_date=row['added_date'],
                    updated_date=row['updated_date']
                ))
            return plugins
    
    # Installed plugins management
    def add_installed_plugin(self, plugin: InstalledPlugin) -> None:
        """Add or update an installed plugin."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO installed_plugins
                (plugin_id, name, dll_path, version, install_date, file_hash, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                plugin.plugin_id, plugin.name, plugin.dll_path,
                plugin.version, plugin.install_date, plugin.file_hash, plugin.file_size
            ))
            conn.commit()
    
    def get_installed_plugins(self) -> List[InstalledPlugin]:
        """Get all installed plugins."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM installed_plugins ORDER BY name")
            
            plugins = []
            for row in cursor.fetchall():
                plugins.append(InstalledPlugin(
                    plugin_id=row['plugin_id'],
                    name=row['name'],
                    dll_path=row['dll_path'],
                    version=row['version'],
                    install_date=row['install_date'],
                    file_hash=row['file_hash'],
                    file_size=row['file_size']
                ))
            return plugins
    
    def remove_installed_plugin(self, plugin_id: str) -> None:
        """Remove an installed plugin from tracking."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM installed_plugins WHERE plugin_id = ?", (plugin_id,))
            conn.commit()
    
    # Archive management
    def add_archive(self, plugin_id: str, version: str, archive_path: str, file_hash: str = "") -> None:
        """Add a plugin archive for rollback."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO plugin_archives
                (plugin_id, version, archive_path, archive_date, file_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (plugin_id, version, archive_path, datetime.now().isoformat(), file_hash))
            conn.commit()
    
    def get_archives(self, plugin_id: str) -> List[Dict[str, Any]]:
        """Get all archives for a plugin."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM plugin_archives 
                WHERE plugin_id = ? 
                ORDER BY archive_date DESC
            ''', (plugin_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_old_archives(self, plugin_id: str, keep_count: int = 2) -> List[str]:
        """Delete old archives, keeping only the most recent ones. Returns paths of deleted archives."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get archives to delete
            cursor.execute('''
                SELECT archive_path FROM plugin_archives 
                WHERE plugin_id = ? 
                ORDER BY archive_date DESC
                LIMIT -1 OFFSET ?
            ''', (plugin_id, keep_count))
            
            paths_to_delete = [row['archive_path'] for row in cursor.fetchall()]
            
            # Delete from database
            cursor.execute('''
                DELETE FROM plugin_archives 
                WHERE plugin_id = ? AND id NOT IN (
                    SELECT id FROM plugin_archives 
                    WHERE plugin_id = ? 
                    ORDER BY archive_date DESC 
                    LIMIT ?
                )
            ''', (plugin_id, plugin_id, keep_count))
            
            conn.commit()
            return paths_to_delete
    
    def set_metadata(self, key: str, value: str) -> None:
        """Set a metadata value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Get a metadata value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def export_catalog_to_json(self, filepath: str) -> None:
        """Export the plugin catalog to JSON for backup/sharing."""
        plugins = self.get_all_plugins()
        data = {
            "version": "1.0",
            "exported_date": datetime.now().isoformat(),
            "plugins": [p.to_dict() for p in plugins]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def import_catalog_from_json(self, filepath: str) -> int:
        """Import plugins from JSON file. Returns count of imported plugins."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        for plugin_data in data.get('plugins', []):
            try:
                plugin = PluginInfo.from_dict(plugin_data)
                self.add_or_update_plugin(plugin)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to import plugin: {e}")
        
        return count
