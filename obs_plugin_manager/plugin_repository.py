"""
Plugin Repository - manages the catalog of available plugins and checks for updates.
"""

import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re


class PluginRepository:
    """Manages the repository of available OBS plugins."""
    
    # Built-in catalog of popular plugins
    POPULAR_PLUGINS = [
        {
            "name": "obs-websocket",
            "display_name": "OBS WebSocket",
            "description": "Remote control OBS Studio through WebSocket protocol",
            "author": "obs-websocket contributors",
            "category": "Integration",
            "homepage_url": "https://github.com/obsproject/obs-websocket",
            "download_url": "https://github.com/obsproject/obs-websocket/releases/latest",
            "is_recommended": True,
        },
        {
            "name": "obs-browser",
            "display_name": "Browser Source Plugin",
            "description": "CEF-based browser source plugin for OBS Studio",
            "author": "OBS Project",
            "category": "Sources",
            "homepage_url": "https://github.com/obsproject/obs-browser",
            "is_recommended": True,
        },
        {
            "name": "obs-virtualcam",
            "display_name": "OBS Virtual Camera",
            "description": "Virtual camera output for OBS Studio",
            "author": "OBS Project",
            "category": "Output",
            "homepage_url": "https://github.com/obsproject/obs-virtualcam",
            "is_recommended": True,
        },
        {
            "name": "obs-streamfx",
            "display_name": "StreamFX",
            "description": "Modern effects plugin for OBS Studio",
            "author": "Xaymar",
            "category": "Effects",
            "homepage_url": "https://github.com/Xaymar/obs-StreamFX",
            "download_url": "https://github.com/Xaymar/obs-StreamFX/releases/latest",
            "is_recommended": True,
        },
        {
            "name": "obs-ndi",
            "display_name": "OBS NDI Plugin",
            "description": "Network Device Interface (NDI) integration for OBS",
            "author": "obs-ndi contributors",
            "category": "Integration",
            "homepage_url": "https://github.com/obs-ndi/obs-ndi",
            "download_url": "https://github.com/obs-ndi/obs-ndi/releases/latest",
            "is_recommended": True,
        },
        {
            "name": "obs-multi-rtmp",
            "display_name": "Multiple RTMP Outputs",
            "description": "Multiple RTMP streaming outputs plugin",
            "author": "sorayuki",
            "category": "Output",
            "homepage_url": "https://github.com/sorayuki/obs-multi-rtmp",
            "download_url": "https://github.com/sorayuki/obs-multi-rtmp/releases/latest",
            "is_recommended": True,
        },
        {
            "name": "obs-move-transition",
            "display_name": "Move Transition",
            "description": "Move source/filter transition plugin for OBS Studio",
            "author": "Exeldro",
            "category": "Transitions",
            "homepage_url": "https://github.com/exeldro/obs-move-transition",
            "download_url": "https://github.com/exeldro/obs-move-transition/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-replay-source",
            "display_name": "Replay Source",
            "description": "Instant replay source for OBS Studio",
            "author": "Exeldro",
            "category": "Sources",
            "homepage_url": "https://github.com/exeldro/obs-replay-source",
            "download_url": "https://github.com/exeldro/obs-replay-source/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-shaderfilter",
            "display_name": "Shader Filter",
            "description": "Apply custom GLSL shaders to sources",
            "author": "Exeldro",
            "category": "Effects",
            "homepage_url": "https://github.com/exeldro/obs-shaderfilter",
            "download_url": "https://github.com/exeldro/obs-shaderfilter/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-transition-table",
            "display_name": "Transition Table",
            "description": "Customize scene transitions",
            "author": "Exeldro",
            "category": "Transitions",
            "homepage_url": "https://github.com/exeldro/obs-transition-table",
            "download_url": "https://github.com/exeldro/obs-transition-table/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-composite-blur",
            "display_name": "Composite Blur",
            "description": "Comprehensive blur plugin with multiple algorithms",
            "author": "FiniteSingularity",
            "category": "Effects",
            "homepage_url": "https://github.com/FiniteSingularity/obs-composite-blur",
            "download_url": "https://github.com/FiniteSingularity/obs-composite-blur/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-backgroundremoval",
            "display_name": "Background Removal",
            "description": "AI-powered background removal for OBS",
            "author": "royshil",
            "category": "Effects",
            "homepage_url": "https://github.com/royshil/obs-backgroundremoval",
            "download_url": "https://github.com/royshil/obs-backgroundremoval/releases/latest",
            "is_recommended": True,
        },
        {
            "name": "obs-advanced-scene-switcher",
            "display_name": "Advanced Scene Switcher",
            "description": "Automated scene switching based on various conditions",
            "author": "WarmUpTill",
            "category": "Automation",
            "homepage_url": "https://github.com/WarmUpTill/SceneSwitcher",
            "download_url": "https://github.com/WarmUpTill/SceneSwitcher/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-midi",
            "display_name": "OBS MIDI",
            "description": "Control OBS with MIDI devices",
            "author": "cpyarger",
            "category": "Integration",
            "homepage_url": "https://github.com/cpyarger/obs-midi",
            "download_url": "https://github.com/cpyarger/obs-midi/releases/latest",
            "is_recommended": False,
        },
        {
            "name": "obs-audio-monitor",
            "display_name": "Audio Monitor",
            "description": "Advanced audio monitoring for OBS",
            "author": "Exeldro",
            "category": "Audio",
            "homepage_url": "https://github.com/exeldro/obs-audio-monitor",
            "download_url": "https://github.com/exeldro/obs-audio-monitor/releases/latest",
            "is_recommended": False,
        },
    ]
    
    def __init__(self, cache_dir: str = "plugin_cache"):
        """
        Initialize the plugin repository.
        
        Args:
            cache_dir: Directory to cache plugin information
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.plugins_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cached plugin information."""
        cache_file = self.cache_dir / "plugins_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.plugins_cache = json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.plugins_cache = {}
    
    def _save_cache(self):
        """Save plugin information to cache."""
        cache_file = self.cache_dir / "plugins_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.plugins_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_popular_plugins(self) -> List[Dict]:
        """Get the list of popular plugins."""
        return self.POPULAR_PLUGINS.copy()
    
    def refresh_plugin_info(self, plugin: Dict, timeout: int = 10) -> Dict:
        """
        Refresh plugin information from its homepage.
        
        Args:
            plugin: Plugin dictionary
            timeout: Request timeout in seconds
            
        Returns:
            Updated plugin dictionary
        """
        updated_plugin = plugin.copy()
        
        # Try to get latest version from GitHub releases
        if "github.com" in plugin.get("homepage_url", ""):
            try:
                version_info = self._get_github_latest_release(
                    plugin["homepage_url"], 
                    timeout
                )
                if version_info:
                    updated_plugin["latest_version"] = version_info["version"]
                    updated_plugin["download_url"] = version_info["download_url"]
                    updated_plugin["release_date"] = version_info["release_date"]
                    updated_plugin["release_notes"] = version_info.get("notes", "")
            except Exception as e:
                print(f"Error getting version for {plugin['name']}: {e}")
        
        # Update cache
        self.plugins_cache[plugin["name"]] = {
            "plugin": updated_plugin,
            "last_updated": datetime.now().isoformat()
        }
        self._save_cache()
        
        return updated_plugin
    
    def _get_github_latest_release(self, repo_url: str, timeout: int = 10) -> Optional[Dict]:
        """
        Get latest release information from GitHub.
        
        Args:
            repo_url: GitHub repository URL
            timeout: Request timeout
            
        Returns:
            Dictionary with version information or None
        """
        try:
            # Extract owner and repo from URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                return None
            
            owner, repo = match.groups()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "OBS-Plugin-Manager"
            }
            
            response = requests.get(api_url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Find Windows asset
                windows_asset = None
                for asset in data.get("assets", []):
                    name = asset["name"].lower()
                    if "win" in name or "windows" in name or name.endswith(".zip"):
                        windows_asset = asset
                        break
                
                return {
                    "version": data.get("tag_name", "").lstrip("v"),
                    "download_url": windows_asset["browser_download_url"] if windows_asset else data.get("html_url", ""),
                    "release_date": data.get("published_at", ""),
                    "notes": data.get("body", "")
                }
        except Exception as e:
            print(f"Error fetching GitHub release: {e}")
        
        return None
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        def normalize_version(version: str) -> List[int]:
            """Convert version string to list of integers."""
            # Remove 'v' prefix and split by dots
            version = version.lstrip('v').strip()
            parts = re.split(r'[.\-_]', version)
            
            numbers = []
            for part in parts:
                # Extract numbers from part
                match = re.search(r'\d+', part)
                if match:
                    numbers.append(int(match.group()))
                else:
                    break
            
            return numbers
        
        try:
            v1_parts = normalize_version(version1)
            v2_parts = normalize_version(version2)
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for p1, p2 in zip(v1_parts, v2_parts):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            
            return 0
        except Exception:
            # If comparison fails, assume versions are different
            return -1 if version1 != version2 else 0
    
    def check_for_updates(self, installed_plugins: List[Dict]) -> List[Dict]:
        """
        Check for available updates for installed plugins.
        
        Args:
            installed_plugins: List of currently installed plugins
            
        Returns:
            List of plugins with available updates
        """
        updates_available = []
        
        for installed in installed_plugins:
            # Find matching plugin in catalog
            catalog_plugin = None
            for popular in self.POPULAR_PLUGINS:
                if popular["name"].lower() == installed["name"].lower():
                    catalog_plugin = popular
                    break
            
            if not catalog_plugin:
                continue
            
            # Refresh plugin info to get latest version
            updated_info = self.refresh_plugin_info(catalog_plugin)
            
            if "latest_version" in updated_info:
                current_version = installed.get("version", "Unknown")
                latest_version = updated_info["latest_version"]
                
                # Compare versions
                if current_version != "Unknown" and self.compare_versions(current_version, latest_version) < 0:
                    updates_available.append({
                        "plugin": installed,
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "download_url": updated_info.get("download_url", ""),
                        "catalog_info": updated_info
                    })
        
        return updates_available
    
    def get_cached_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """Get cached plugin information."""
        cache_entry = self.plugins_cache.get(plugin_name)
        if cache_entry:
            return cache_entry.get("plugin")
        return None
    
    def search_plugins(self, query: str, category: str = None) -> List[Dict]:
        """
        Search for plugins by name or description.
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching plugins
        """
        results = []
        query_lower = query.lower()
        
        for plugin in self.POPULAR_PLUGINS:
            # Check category filter
            if category and plugin.get("category", "").lower() != category.lower():
                continue
            
            # Search in name, display name, and description
            if (query_lower in plugin["name"].lower() or
                query_lower in plugin.get("display_name", "").lower() or
                query_lower in plugin.get("description", "").lower()):
                results.append(plugin)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get list of all plugin categories."""
        categories = set()
        for plugin in self.POPULAR_PLUGINS:
            if "category" in plugin:
                categories.add(plugin["category"])
        return sorted(list(categories))
