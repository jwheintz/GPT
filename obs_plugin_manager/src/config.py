"""
Configuration management for OBS Plugin Manager.
Handles paths, settings, and user preferences.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # OBS paths
    obs_install_path: str = ""
    obs_plugins_path: str = ""
    obs_data_path: str = ""
    
    # App paths
    app_data_path: str = ""
    plugin_archive_path: str = ""
    download_temp_path: str = ""
    
    # Settings
    max_archive_versions: int = 2
    auto_check_updates: bool = True
    check_obs_running_before_write: bool = True
    
    # Plugin database
    plugin_db_url: str = "https://raw.githubusercontent.com/obsproject/obs-studio/master/plugins/"
    last_db_refresh: str = ""
    
    # Window settings
    window_width: int = 1200
    window_height: int = 800
    
    def __post_init__(self):
        """Initialize default paths if not set."""
        if not self.app_data_path:
            self.app_data_path = str(Path.home() / "AppData" / "Local" / "OBSPluginManager")
        
        if not self.plugin_archive_path:
            self.plugin_archive_path = str(Path(self.app_data_path) / "archives")
        
        if not self.download_temp_path:
            self.download_temp_path = str(Path(self.app_data_path) / "temp")


class ConfigManager:
    """Manages application configuration persistence."""
    
    DEFAULT_OBS_PATHS = [
        r"C:\Program Files\obs-studio",
        r"C:\Program Files (x86)\obs-studio",
        os.path.expandvars(r"%LOCALAPPDATA%\obs-studio"),
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = AppConfig()
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(self.config.app_data_path) / "config.json"
        
        self._ensure_directories()
        self.load()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.config.app_data_path,
            self.config.plugin_archive_path,
            self.config.download_temp_path,
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def detect_obs_installation(self) -> Optional[str]:
        """
        Auto-detect OBS Studio installation path.
        Returns the path if found, None otherwise.
        """
        # Check configured path first
        if self.config.obs_install_path and Path(self.config.obs_install_path).exists():
            return self.config.obs_install_path
        
        # Check default paths
        for path in self.DEFAULT_OBS_PATHS:
            expanded_path = os.path.expandvars(path)
            obs_exe = Path(expanded_path) / "bin" / "64bit" / "obs64.exe"
            if obs_exe.exists():
                self.config.obs_install_path = expanded_path
                self._set_obs_paths(expanded_path)
                return expanded_path
        
        # Try to find via registry (Windows)
        registry_path = self._check_registry()
        if registry_path:
            self.config.obs_install_path = registry_path
            self._set_obs_paths(registry_path)
            return registry_path
        
        return None
    
    def _check_registry(self) -> Optional[str]:
        """Check Windows registry for OBS installation."""
        try:
            import winreg
            
            # Check both 64-bit and 32-bit registry locations
            keys_to_check = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\OBS Studio"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\OBS Studio"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\OBS Studio"),
            ]
            
            for hkey, subkey in keys_to_check:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        path, _ = winreg.QueryValueEx(key, "")
                        if path and Path(path).exists():
                            return path
                except FileNotFoundError:
                    continue
            
        except ImportError:
            logger.debug("winreg not available (non-Windows platform)")
        except Exception as e:
            logger.warning(f"Registry check failed: {e}")
        
        return None
    
    def _set_obs_paths(self, install_path: str) -> None:
        """Set OBS-related paths based on installation path."""
        install_path = Path(install_path)
        
        # Plugin paths can be in multiple locations
        # Primary: obs-studio/obs-plugins/64bit/
        # Also: %APPDATA%/obs-studio/obs-plugins/64bit/
        
        self.config.obs_plugins_path = str(install_path / "obs-plugins" / "64bit")
        
        # Data path is usually in AppData
        appdata_obs = Path(os.environ.get('APPDATA', '')) / "obs-studio"
        if appdata_obs.exists():
            self.config.obs_data_path = str(appdata_obs)
        else:
            self.config.obs_data_path = str(install_path / "data")
    
    def get_all_plugin_paths(self) -> list:
        """Get all possible OBS plugin paths."""
        paths = []
        
        # Installation directory plugins
        if self.config.obs_install_path:
            install_plugins = Path(self.config.obs_install_path) / "obs-plugins" / "64bit"
            if install_plugins.exists():
                paths.append(str(install_plugins))
        
        # AppData plugins
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            appdata_plugins = Path(appdata) / "obs-studio" / "obs-plugins" / "64bit"
            if appdata_plugins.exists():
                paths.append(str(appdata_plugins))
        
        # LocalAppData plugins
        localappdata = os.environ.get('LOCALAPPDATA', '')
        if localappdata:
            local_plugins = Path(localappdata) / "obs-studio" / "obs-plugins" / "64bit"
            if local_plugins.exists():
                paths.append(str(local_plugins))
        
        return paths
    
    def set_obs_path(self, path: str) -> bool:
        """Manually set OBS installation path."""
        expanded_path = os.path.expandvars(path)
        
        # Verify it's a valid OBS installation
        obs_exe = Path(expanded_path) / "bin" / "64bit" / "obs64.exe"
        if not obs_exe.exists():
            logger.error(f"Invalid OBS path: {expanded_path}")
            return False
        
        self.config.obs_install_path = expanded_path
        self._set_obs_paths(expanded_path)
        self.save()
        return True


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
