"""
OBS Installation Scanner.
Scans OBS installation to detect installed plugins and their versions.
"""

import os
import re
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScannedPlugin:
    """Information about a scanned/discovered plugin."""
    
    name: str
    dll_path: str
    dll_name: str
    version: str
    file_size: int
    file_hash: str
    modified_date: str
    data_folder: Optional[str] = None
    matched_catalog_id: Optional[str] = None


@dataclass
class OBSInstallation:
    """Information about an OBS installation."""
    
    install_path: str
    version: str
    is_64bit: bool
    exe_path: str
    plugins_path: str
    data_path: str
    config_path: str


class OBSScanner:
    """Scans OBS installation and discovers installed plugins."""
    
    # Common OBS plugin DLL patterns and their catalog IDs
    KNOWN_PLUGIN_PATTERNS = {
        r'obs-websocket\.dll': 'obs-websocket',
        r'obs-ndi\.dll': 'obs-ndi',
        r'obs-browser\.dll': 'obs-browser',
        r'obs-asio\.dll': 'obs-asio',
        r'audio-monitor\.dll': 'obs-audio-monitor',
        r'waveform\.dll': 'waveform',
        r'obs-shaderfilter\.dll': 'obs-shaderfilter',
        r'StreamFX\.dll': 'obs-streamfx',
        r'move-transition\.dll': 'obs-move-transition',
        r'obs-backgroundremoval\.dll': 'obs-backgroundremoval',
        r'obs-composite-blur\.dll': 'obs-composite-blur',
        r'source-record\.dll': 'obs-source-record',
        r'source-clone\.dll': 'obs-source-clone',
        r'advanced-scene-switcher\.dll': 'advanced-scene-switcher',
        r'transition-table\.dll': 'obs-transition-table',
        r'obs-teleport\.dll': 'obs-teleport',
        r'obs-rtspserver\.dll': 'obs-rtspserver',
        r'obs-localvocal\.dll': 'obs-localvocal',
        r'input-overlay\.dll': 'input-overlay',
        r'obs-multi-rtmp\.dll': 'obs-multi-rtmp',
        r'nvfbc\.dll': 'obs-nvfbc',
        r'replay-source\.dll': 'obs-replay-source',
        r'scene-collection-manager\.dll': 'obs-scene-collection-manager',
        r'downstream-keyer\.dll': 'obs-downstream-keyer',
        r'text-pthread\.dll': 'obs-text-pthread',
    }
    
    # Built-in OBS plugins (to filter out from user plugins)
    BUILTIN_PLUGINS = {
        'obs-outputs.dll',
        'obs-ffmpeg.dll',
        'obs-x264.dll',
        'obs-filters.dll',
        'obs-transitions.dll',
        'obs-qsv11.dll',
        'win-capture.dll',
        'win-dshow.dll',
        'win-wasapi.dll',
        'text-freetype2.dll',
        'image-source.dll',
        'rtmp-services.dll',
        'decklink.dll',
        'aja.dll',
        'obs-vst.dll',
        'vlc-video.dll',
        'frontend-tools.dll',
        'coreaudio-encoder.dll',
    }
    
    def __init__(self, config_manager=None):
        if config_manager is None:
            from .config import get_config
            config_manager = get_config()
        self.config = config_manager
    
    def scan_obs_installation(self) -> Optional[OBSInstallation]:
        """Scan and return OBS installation details."""
        install_path = self.config.detect_obs_installation()
        
        if not install_path:
            logger.warning("OBS installation not found")
            return None
        
        install_path = Path(install_path)
        
        # Detect OBS version
        version = self._get_obs_version(install_path)
        
        # Check architecture (64-bit)
        exe_path = install_path / "bin" / "64bit" / "obs64.exe"
        is_64bit = exe_path.exists()
        
        if not is_64bit:
            exe_path = install_path / "bin" / "32bit" / "obs32.exe"
        
        # Plugin paths
        if is_64bit:
            plugins_path = install_path / "obs-plugins" / "64bit"
        else:
            plugins_path = install_path / "obs-plugins" / "32bit"
        
        # Data path
        data_path = install_path / "data" / "obs-plugins"
        
        # Config path (user-specific)
        config_path = Path(os.environ.get('APPDATA', '')) / "obs-studio"
        
        return OBSInstallation(
            install_path=str(install_path),
            version=version,
            is_64bit=is_64bit,
            exe_path=str(exe_path),
            plugins_path=str(plugins_path),
            data_path=str(data_path),
            config_path=str(config_path)
        )
    
    def _get_obs_version(self, install_path: Path) -> str:
        """Extract OBS version from installation."""
        version = "Unknown"
        
        # Try to get version from version.txt
        version_file = install_path / "data" / "obs-studio" / "version.txt"
        if version_file.exists():
            try:
                version = version_file.read_text().strip()
                return version
            except Exception:
                pass
        
        # Try to extract from exe file properties (Windows)
        try:
            exe_path = install_path / "bin" / "64bit" / "obs64.exe"
            if exe_path.exists():
                version = self._get_file_version(str(exe_path))
        except Exception as e:
            logger.debug(f"Could not get version from exe: {e}")
        
        return version
    
    def _get_file_version(self, filepath: str) -> str:
        """Get file version from Windows executable."""
        try:
            import ctypes
            from ctypes import wintypes
            
            # GetFileVersionInfoSize
            version_dll = ctypes.windll.version
            size = version_dll.GetFileVersionInfoSizeW(filepath, None)
            
            if size == 0:
                return "Unknown"
            
            # GetFileVersionInfo
            buffer = ctypes.create_string_buffer(size)
            if not version_dll.GetFileVersionInfoW(filepath, 0, size, buffer):
                return "Unknown"
            
            # VerQueryValue
            pBlock = ctypes.c_void_p()
            pLen = ctypes.c_uint()
            
            if version_dll.VerQueryValueW(
                buffer, "\\", ctypes.byref(pBlock), ctypes.byref(pLen)
            ):
                # VS_FIXEDFILEINFO structure
                class VS_FIXEDFILEINFO(ctypes.Structure):
                    _fields_ = [
                        ("dwSignature", wintypes.DWORD),
                        ("dwStrucVersion", wintypes.DWORD),
                        ("dwFileVersionMS", wintypes.DWORD),
                        ("dwFileVersionLS", wintypes.DWORD),
                        ("dwProductVersionMS", wintypes.DWORD),
                        ("dwProductVersionLS", wintypes.DWORD),
                        ("dwFileFlagsMask", wintypes.DWORD),
                        ("dwFileFlags", wintypes.DWORD),
                        ("dwFileOS", wintypes.DWORD),
                        ("dwFileType", wintypes.DWORD),
                        ("dwFileSubtype", wintypes.DWORD),
                        ("dwFileDateMS", wintypes.DWORD),
                        ("dwFileDateLS", wintypes.DWORD),
                    ]
                
                ffi = ctypes.cast(pBlock, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
                
                major = (ffi.dwFileVersionMS >> 16) & 0xFFFF
                minor = ffi.dwFileVersionMS & 0xFFFF
                patch = (ffi.dwFileVersionLS >> 16) & 0xFFFF
                build = ffi.dwFileVersionLS & 0xFFFF
                
                return f"{major}.{minor}.{patch}"
            
        except Exception as e:
            logger.debug(f"Failed to get file version: {e}")
        
        return "Unknown"
    
    def get_all_plugin_directories(self) -> List[str]:
        """Get all directories where OBS plugins might be installed."""
        directories = []
        
        obs_info = self.scan_obs_installation()
        if obs_info:
            # Main installation plugins
            if Path(obs_info.plugins_path).exists():
                directories.append(obs_info.plugins_path)
        
        # AppData plugins (user-installed)
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            user_plugins = Path(appdata) / "obs-studio" / "obs-plugins" / "64bit"
            if user_plugins.exists():
                directories.append(str(user_plugins))
        
        # LocalAppData plugins
        localappdata = os.environ.get('LOCALAPPDATA', '')
        if localappdata:
            local_plugins = Path(localappdata) / "obs-studio" / "obs-plugins" / "64bit"
            if local_plugins.exists():
                directories.append(str(local_plugins))
        
        return directories
    
    def scan_plugins(self) -> List[ScannedPlugin]:
        """Scan all plugin directories and return found plugins."""
        plugins = []
        seen_dlls = set()
        
        for plugin_dir in self.get_all_plugin_directories():
            dir_path = Path(plugin_dir)
            
            if not dir_path.exists():
                continue
            
            logger.info(f"Scanning plugin directory: {plugin_dir}")
            
            # Scan for DLL files
            for dll_file in dir_path.glob("*.dll"):
                dll_name = dll_file.name.lower()
                
                # Skip built-in plugins
                if dll_name in self.BUILTIN_PLUGINS:
                    continue
                
                # Skip duplicates
                if dll_name in seen_dlls:
                    continue
                seen_dlls.add(dll_name)
                
                try:
                    plugin = self._analyze_plugin(dll_file)
                    if plugin:
                        plugins.append(plugin)
                except Exception as e:
                    logger.warning(f"Failed to analyze plugin {dll_file}: {e}")
        
        return plugins
    
    def _analyze_plugin(self, dll_path: Path) -> Optional[ScannedPlugin]:
        """Analyze a single plugin DLL."""
        if not dll_path.exists():
            return None
        
        dll_name = dll_path.name
        
        # Get file info
        stat = dll_path.stat()
        file_size = stat.st_size
        modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(dll_path)
        
        # Try to get version
        version = self._get_plugin_version(dll_path)
        
        # Match to catalog
        matched_id = self._match_to_catalog(dll_name)
        
        # Get display name
        name = self._get_plugin_name(dll_path, matched_id)
        
        # Look for associated data folder
        data_folder = self._find_data_folder(dll_path)
        
        return ScannedPlugin(
            name=name,
            dll_path=str(dll_path),
            dll_name=dll_name,
            version=version,
            file_size=file_size,
            file_hash=file_hash,
            modified_date=modified_date,
            data_folder=data_folder,
            matched_catalog_id=matched_id
        )
    
    def _calculate_file_hash(self, filepath: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash."""
        hasher = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _get_plugin_version(self, dll_path: Path) -> str:
        """Try to extract version from plugin DLL."""
        # First try Windows file version
        try:
            version = self._get_file_version(str(dll_path))
            if version != "Unknown":
                return version
        except Exception:
            pass
        
        # Try to find version in associated manifest/json
        plugin_name = dll_path.stem
        
        # Check for version.txt or manifest.json in data folder
        data_folder = self._find_data_folder(dll_path)
        if data_folder:
            data_path = Path(data_folder)
            
            for version_file in ['version.txt', 'manifest.json', 'plugin.json']:
                vf = data_path / version_file
                if vf.exists():
                    try:
                        content = vf.read_text()
                        if version_file.endswith('.json'):
                            data = json.loads(content)
                            if 'version' in data:
                                return data['version']
                        else:
                            return content.strip()
                    except Exception:
                        pass
        
        return "Unknown"
    
    def _match_to_catalog(self, dll_name: str) -> Optional[str]:
        """Match a DLL name to a catalog plugin ID."""
        dll_lower = dll_name.lower()
        
        for pattern, plugin_id in self.KNOWN_PLUGIN_PATTERNS.items():
            if re.match(pattern, dll_lower, re.IGNORECASE):
                return plugin_id
        
        return None
    
    def _get_plugin_name(self, dll_path: Path, catalog_id: Optional[str]) -> str:
        """Get a display name for the plugin."""
        # If matched to catalog, use catalog name
        if catalog_id:
            try:
                from .database import PluginDatabase
                db = PluginDatabase()
                plugin = db.get_plugin(catalog_id)
                if plugin:
                    return plugin.name
            except Exception:
                pass
        
        # Otherwise, derive from filename
        name = dll_path.stem
        # Convert hyphens/underscores to spaces and title case
        name = name.replace('-', ' ').replace('_', ' ')
        name = name.title()
        
        return name
    
    def _find_data_folder(self, dll_path: Path) -> Optional[str]:
        """Find associated data folder for a plugin."""
        plugin_name = dll_path.stem
        
        # Check common data locations
        obs_info = self.scan_obs_installation()
        if not obs_info:
            return None
        
        data_locations = [
            Path(obs_info.install_path) / "data" / "obs-plugins" / plugin_name,
            Path(obs_info.data_path) / plugin_name,
        ]
        
        # AppData data folders
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            data_locations.append(Path(appdata) / "obs-studio" / "obs-plugins" / plugin_name)
        
        for loc in data_locations:
            if loc.exists() and loc.is_dir():
                return str(loc)
        
        return None
    
    def get_plugin_details(self, dll_path: str) -> Dict[str, Any]:
        """Get detailed information about a specific plugin."""
        path = Path(dll_path)
        
        if not path.exists():
            return {"error": "Plugin file not found"}
        
        plugin = self._analyze_plugin(path)
        if not plugin:
            return {"error": "Failed to analyze plugin"}
        
        details = {
            "name": plugin.name,
            "dll_path": plugin.dll_path,
            "dll_name": plugin.dll_name,
            "version": plugin.version,
            "file_size": plugin.file_size,
            "file_size_formatted": self._format_size(plugin.file_size),
            "file_hash": plugin.file_hash,
            "modified_date": plugin.modified_date,
            "data_folder": plugin.data_folder,
            "catalog_id": plugin.matched_catalog_id,
        }
        
        # Add catalog info if matched
        if plugin.matched_catalog_id:
            try:
                from .database import PluginDatabase
                db = PluginDatabase()
                catalog_plugin = db.get_plugin(plugin.matched_catalog_id)
                if catalog_plugin:
                    details["catalog_info"] = {
                        "latest_version": catalog_plugin.latest_version,
                        "description": catalog_plugin.description,
                        "author": catalog_plugin.author,
                        "homepage": catalog_plugin.homepage_url,
                        "github": catalog_plugin.github_url,
                    }
                    
                    # Check if update available
                    if plugin.version != "Unknown" and catalog_plugin.latest_version:
                        details["update_available"] = self._is_update_available(
                            plugin.version, catalog_plugin.latest_version
                        )
            except Exception as e:
                logger.warning(f"Failed to get catalog info: {e}")
        
        return details
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _is_update_available(self, current: str, latest: str) -> bool:
        """Check if an update is available by comparing versions."""
        from packaging import version
        
        try:
            # Clean version strings
            current_clean = re.sub(r'[^0-9.]', '', current)
            latest_clean = re.sub(r'[^0-9.]', '', latest)
            
            if not current_clean or not latest_clean:
                return False
            
            return version.parse(latest_clean) > version.parse(current_clean)
        except Exception:
            # Fall back to string comparison
            return current != latest and current != "Unknown"
    
    def check_updates(self) -> List[Dict[str, Any]]:
        """Check all installed plugins for available updates."""
        updates = []
        
        plugins = self.scan_plugins()
        
        try:
            from .database import PluginDatabase
            db = PluginDatabase()
        except Exception as e:
            logger.error(f"Failed to access plugin database: {e}")
            return updates
        
        for plugin in plugins:
            if not plugin.matched_catalog_id:
                continue
            
            catalog_plugin = db.get_plugin(plugin.matched_catalog_id)
            if not catalog_plugin:
                continue
            
            if self._is_update_available(plugin.version, catalog_plugin.latest_version):
                updates.append({
                    "plugin_name": plugin.name,
                    "plugin_id": plugin.matched_catalog_id,
                    "current_version": plugin.version,
                    "latest_version": catalog_plugin.latest_version,
                    "dll_path": plugin.dll_path,
                    "download_url": catalog_plugin.download_url,
                    "release_date": catalog_plugin.release_date,
                })
        
        return updates
    
    def get_suggestions(self) -> List[Dict[str, Any]]:
        """Get plugin suggestions based on installed plugins and popularity."""
        suggestions = []
        
        # Get installed plugin IDs
        installed_ids = set()
        for plugin in self.scan_plugins():
            if plugin.matched_catalog_id:
                installed_ids.add(plugin.matched_catalog_id)
        
        try:
            from .database import PluginDatabase
            db = PluginDatabase()
            
            # Get recommended plugins not installed
            recommended = db.get_recommended_plugins()
            for plugin in recommended:
                if plugin.id not in installed_ids:
                    suggestions.append({
                        "plugin_id": plugin.id,
                        "name": plugin.name,
                        "description": plugin.description,
                        "author": plugin.author,
                        "category": plugin.category,
                        "reason": "Recommended",
                        "download_url": plugin.download_url,
                    })
            
            # Get popular plugins not installed
            popular = db.get_popular_plugins()
            for plugin in popular:
                if plugin.id not in installed_ids and not plugin.is_recommended:
                    suggestions.append({
                        "plugin_id": plugin.id,
                        "name": plugin.name,
                        "description": plugin.description,
                        "author": plugin.author,
                        "category": plugin.category,
                        "reason": "Popular",
                        "download_url": plugin.download_url,
                    })
        
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
        
        return suggestions
