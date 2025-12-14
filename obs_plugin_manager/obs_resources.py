"""
OBS Resources - queries the official OBS website for plugins and scripts.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
from .logger import get_logger


class OBSResourcesFetcher:
    """Fetches plugins and resources from the official OBS website."""
    
    # OBS Project URLs
    OBS_RESOURCES_URL = "https://obsproject.com/forum/resources/"
    OBS_FORUM_PLUGINS_URL = "https://obsproject.com/forum/list/plugins.26/"
    
    # Resource categories on OBS site
    RESOURCE_CATEGORIES = {
        "plugins": 5,
        "scripts": 22,
        "themes": 10,
        "overlays": 12
    }
    
    def __init__(self, cache_dir: str = "obs_resources_cache"):
        """
        Initialize the OBS resources fetcher.
        
        Args:
            cache_dir: Directory for caching OBS website data
        """
        self.logger = get_logger(__name__)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "obs_resources_cache.json"
        self.logger.info(f"OBS Resources fetcher initialized with cache dir: {cache_dir}")
        self._load_cache()
    
    def _load_cache(self):
        """Load cached OBS resources data."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                self.logger.debug(f"Loaded OBS resources cache with {len(self.cache)} entries")
            except json.JSONDecodeError as e:
                self.logger.error(f"OBS resources cache corrupted: {e}. Starting fresh.")
                self.cache = {}
            except Exception as e:
                self.logger.exception(f"Unexpected error loading OBS resources cache: {e}")
                self.cache = {}
        else:
            self.logger.debug("No OBS resources cache found, will fetch from website")
            self.cache = {}
    
    def _save_cache(self):
        """Save OBS resources to cache."""
        try:
            # Write to temp file first (atomic operation)
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            # Atomic rename
            temp_file.replace(self.cache_file)
            self.logger.debug(f"Saved OBS resources cache with {len(self.cache)} entries")
        except Exception as e:
            self.logger.error(f"Error saving OBS resources cache: {e}")
    
    def fetch_obs_plugins(self, max_results: int = 50, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch plugins from OBS resources page.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of plugin dictionaries
        """
        cache_key = "obs_plugins"
        
        # Check cache
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = cached_data.get("cached_at", "")
            try:
                cached_dt = datetime.fromisoformat(cached_time)
                age_hours = (datetime.now() - cached_dt).total_seconds() / 3600
                if age_hours < 24:  # Cache for 24 hours
                    return cached_data.get("resources", [])[:max_results]
            except Exception:
                pass
        
        plugins = []
        
        try:
            # Query OBS resources page for plugins
            url = f"{self.OBS_RESOURCES_URL}?category_id={self.RESOURCE_CATEGORIES['plugins']}"
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find resource items
                resource_items = soup.find_all('div', class_='resourceListItem')
                
                for item in resource_items[:max_results]:
                    plugin_info = self._parse_resource_item(item, "plugin")
                    if plugin_info:
                        plugins.append(plugin_info)
            
            # Cache results
            self.cache[cache_key] = {
                "cached_at": datetime.now().isoformat(),
                "resources": plugins
            }
            self._save_cache()
            
        except Exception as e:
            print(f"Error fetching OBS plugins: {e}")
            # Return cached data if available
            if cache_key in self.cache:
                return self.cache[cache_key].get("resources", [])[:max_results]
        
        return plugins[:max_results]
    
    def fetch_obs_scripts(self, max_results: int = 50, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch scripts from OBS resources page.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of script dictionaries
        """
        cache_key = "obs_scripts"
        
        # Check cache
        if not force_refresh and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = cached_data.get("cached_at", "")
            try:
                cached_dt = datetime.fromisoformat(cached_time)
                age_hours = (datetime.now() - cached_dt).total_seconds() / 3600
                if age_hours < 24:  # Cache for 24 hours
                    return cached_data.get("resources", [])[:max_results]
            except Exception:
                pass
        
        scripts = []
        
        try:
            # Query OBS resources page for scripts
            url = f"{self.OBS_RESOURCES_URL}?category_id={self.RESOURCE_CATEGORIES['scripts']}"
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find resource items
                resource_items = soup.find_all('div', class_='resourceListItem')
                
                for item in resource_items[:max_results]:
                    script_info = self._parse_resource_item(item, "script")
                    if script_info:
                        scripts.append(script_info)
            
            # Cache results
            self.cache[cache_key] = {
                "cached_at": datetime.now().isoformat(),
                "resources": scripts
            }
            self._save_cache()
            
        except Exception as e:
            print(f"Error fetching OBS scripts: {e}")
            # Return cached data if available
            if cache_key in self.cache:
                return self.cache[cache_key].get("resources", [])[:max_results]
        
        return scripts[:max_results]
    
    def fetch_popular_plugins(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch popular plugins sorted by downloads/ratings.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query
            
        Returns:
            List of popular plugin dictionaries
        """
        plugins = self.fetch_obs_plugins(max_results=100, force_refresh=force_refresh)
        
        # Sort by rating/downloads (if available in data)
        plugins.sort(key=lambda x: (
            x.get('rating_weighted', 0) * 100 + 
            x.get('downloads', 0) / 100
        ), reverse=True)
        
        return plugins[:max_results]
    
    def fetch_recent_plugins(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch recently updated plugins.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query
            
        Returns:
            List of recent plugin dictionaries
        """
        plugins = self.fetch_obs_plugins(max_results=100, force_refresh=force_refresh)
        
        # Sort by last update
        plugins.sort(key=lambda x: x.get('last_update', ''), reverse=True)
        
        return plugins[:max_results]
    
    def _parse_resource_item(self, item, resource_type: str) -> Optional[Dict]:
        """
        Parse a resource item from the OBS website.
        
        Args:
            item: BeautifulSoup element
            resource_type: "plugin" or "script"
            
        Returns:
            Resource dictionary or None
        """
        try:
            # Extract title and URL
            title_elem = item.find('a', class_='resourceTitle')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            resource_url = title_elem.get('href', '')
            if resource_url and not resource_url.startswith('http'):
                resource_url = f"https://obsproject.com/forum/{resource_url}"
            
            # Extract author
            author_elem = item.find('a', class_='username')
            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
            
            # Extract version
            version_elem = item.find('span', class_='version')
            version = version_elem.get_text(strip=True) if version_elem else "Unknown"
            
            # Extract description
            desc_elem = item.find('div', class_='resourceTagLine')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract stats
            stats = {}
            stat_elems = item.find_all('dl', class_='resourceStats')
            for stat_elem in stat_elems:
                dt = stat_elem.find('dt')
                dd = stat_elem.find('dd')
                if dt and dd:
                    key = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    stats[key] = value
            
            # Extract rating
            rating_elem = item.find('span', class_='rating')
            rating = 0
            rating_weighted = 0
            if rating_elem:
                rating_text = rating_elem.get('title', '')
                # Parse rating like "4.5/5"
                match = re.search(r'([\d.]+)/5', rating_text)
                if match:
                    rating = float(match.group(1))
                    rating_weighted = rating
            
            # Extract downloads
            downloads = 0
            if 'downloads' in stats:
                try:
                    downloads = int(stats['downloads'].replace(',', ''))
                except ValueError:
                    pass
            
            # Extract last update
            last_update = stats.get('last update', stats.get('updated', ''))
            
            # Determine category from title/description
            category = self._determine_category(title, description, resource_type)
            
            return {
                "name": self._clean_name(title),
                "display_name": title,
                "description": description,
                "author": author,
                "version": version,
                "category": category,
                "homepage_url": resource_url,
                "download_url": resource_url,  # Same as homepage for OBS resources
                "rating": rating,
                "rating_weighted": rating_weighted,
                "downloads": downloads,
                "last_update": last_update,
                "source": "OBS Resources",
                "resource_type": resource_type,
                "discovered_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error parsing resource item: {e}")
            return None
    
    def _clean_name(self, title: str) -> str:
        """Clean title to create a name identifier."""
        # Remove version numbers and common suffixes
        name = re.sub(r'\s+v?[\d.]+$', '', title)
        name = re.sub(r'\s+\([^)]+\)$', '', name)
        # Convert to lowercase, replace spaces with hyphens
        name = name.lower().strip()
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        return name
    
    def _determine_category(self, title: str, description: str, resource_type: str) -> str:
        """Determine category from title and description."""
        text = (title + " " + description).lower()
        
        if resource_type == "script":
            return "Scripts"
        
        # Check for keywords
        if any(word in text for word in ["filter", "effect", "blur", "color", "shader", "transition"]):
            return "Effects"
        elif any(word in text for word in ["source", "input", "capture", "browser", "media"]):
            return "Sources"
        elif any(word in text for word in ["stream", "output", "rtmp", "record"]):
            return "Output"
        elif any(word in text for word in ["audio", "sound", "volume", "mixer"]):
            return "Audio"
        elif any(word in text for word in ["websocket", "remote", "control", "api", "midi", "ndi", "integration"]):
            return "Integration"
        elif any(word in text for word in ["scene", "switch", "auto"]):
            return "Automation"
        else:
            return "Other"
    
    def search_obs_resources(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search OBS resources by query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching resources
        """
        # Fetch all plugins and scripts
        all_resources = []
        all_resources.extend(self.fetch_obs_plugins(max_results=100))
        all_resources.extend(self.fetch_obs_scripts(max_results=100))
        
        # Filter by query
        query_lower = query.lower()
        results = []
        
        for resource in all_resources:
            if (query_lower in resource.get('display_name', '').lower() or
                query_lower in resource.get('description', '').lower() or
                query_lower in resource.get('author', '').lower()):
                results.append(resource)
        
        return results[:max_results]
    
    def get_resource_details(self, resource_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific resource.
        
        Args:
            resource_url: URL to the resource page
            
        Returns:
            Detailed resource dictionary or None
        """
        try:
            response = requests.get(resource_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract more detailed information
                details = {}
                
                # Get download link
                download_elem = soup.find('a', class_='downloadButton')
                if download_elem:
                    download_url = download_elem.get('href', '')
                    if download_url and not download_url.startswith('http'):
                        download_url = f"https://obsproject.com/forum/{download_url}"
                    details['download_url'] = download_url
                
                # Get full description
                desc_elem = soup.find('div', class_='resourceDescription')
                if desc_elem:
                    details['full_description'] = desc_elem.get_text(strip=True)
                
                # Get version history
                version_elems = soup.find_all('div', class_='versionUpdate')
                versions = []
                for ver_elem in version_elems[:5]:  # Last 5 versions
                    version_info = {}
                    version_title = ver_elem.find('h3')
                    if version_title:
                        version_info['version'] = version_title.get_text(strip=True)
                    versions.append(version_info)
                
                if versions:
                    details['version_history'] = versions
                
                return details
        except Exception as e:
            print(f"Error getting resource details: {e}")
        
        return None
    
    def get_cache_info(self) -> Dict:
        """Get information about cached data."""
        info = {}
        for key, data in self.cache.items():
            cached_at = data.get("cached_at", "Unknown")
            resource_count = len(data.get("resources", []))
            
            try:
                cached_dt = datetime.fromisoformat(cached_at)
                age_hours = (datetime.now() - cached_dt).total_seconds() / 3600
                is_valid = age_hours < 24
            except Exception:
                age_hours = 0
                is_valid = False
            
            info[key] = {
                "cached_at": cached_at,
                "age_hours": age_hours,
                "resource_count": resource_count,
                "is_valid": is_valid
            }
        
        return info
    
    def clear_cache(self):
        """Clear all cached OBS resources data."""
        self.cache = {}
        self._save_cache()
