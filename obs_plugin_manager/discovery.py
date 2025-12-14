"""
Discovery Module - finds new, popular, and trending OBS plugins and scripts.
Queries both GitHub API and official OBS website.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
from obs_resources import OBSResourcesFetcher


class PluginDiscovery:
    """Discovers new, popular, and trending OBS plugins."""
    
    # GitHub API endpoints
    GITHUB_API = "https://api.github.com"
    GITHUB_SEARCH = f"{GITHUB_API}/search/repositories"
    
    # Search queries for OBS plugins
    PLUGIN_QUERIES = [
        "obs-studio plugin",
        "obs plugin",
        "obs-websocket",
        "obs filter",
        "obs source",
        "obs transition"
    ]
    
    # Known OBS plugin developers
    KNOWN_DEVELOPERS = [
        "obsproject",
        "Exeldro",
        "royshil",
        "FiniteSingularity",
        "WarmUpTill",
        "cpyarger",
        "sorayuki",
        "Xaymar",
        "obs-ndi"
    ]
    
    def __init__(self, cache_dir: str = "discovery_cache"):
        """
        Initialize the discovery module.
        
        Args:
            cache_dir: Directory for caching discovery results
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.cache_file = self.cache_dir / "discovery_cache.json"
        self.cache_expiry = timedelta(hours=6)  # Refresh every 6 hours
        
        # Initialize OBS Resources fetcher
        self.obs_resources = OBSResourcesFetcher()
        
        self._load_cache()
    
    def _load_cache(self):
        """Load cached discovery results."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}
        else:
            self.cache = {}
    
    def _save_cache(self):
        """Save discovery results to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get("cached_at")
        if not cached_time:
            return False
        
        try:
            cached_dt = datetime.fromisoformat(cached_time)
            return datetime.now() - cached_dt < self.cache_expiry
        except Exception:
            return False
    
    def _github_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a GitHub API request with error handling.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response or None
        """
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "OBS-Plugin-Manager-Discovery"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"GitHub API returned {response.status_code}")
                return None
        except Exception as e:
            print(f"GitHub API request failed: {e}")
            return None
    
    def discover_new_plugins(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Discover newly released/updated OBS plugins.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of plugin dictionaries
        """
        cache_key = "new_plugins"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        plugins = []
        seen_repos = set()
        
        # Search for recently updated OBS plugins
        for query in self.PLUGIN_QUERIES[:2]:  # Limit queries to avoid rate limiting
            params = {
                "q": f"{query} language:C language:C++ pushed:>30days",
                "sort": "updated",
                "order": "desc",
                "per_page": 10
            }
            
            data = self._github_request(self.GITHUB_SEARCH, params)
            
            if data and "items" in data:
                for repo in data["items"]:
                    repo_full_name = repo["full_name"]
                    
                    if repo_full_name in seen_repos:
                        continue
                    
                    seen_repos.add(repo_full_name)
                    
                    # Parse plugin info
                    plugin_info = self._parse_repo_info(repo)
                    if plugin_info:
                        plugins.append(plugin_info)
        
        # Sort by updated date
        plugins.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": plugins[:max_results]
        }
        self._save_cache()
        
        return plugins[:max_results]
    
    def discover_popular_plugins(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Discover popular OBS plugins by stars.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of plugin dictionaries
        """
        cache_key = "popular_plugins"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        plugins = []
        seen_repos = set()
        
        # Search for popular OBS plugins
        for query in self.PLUGIN_QUERIES[:3]:
            params = {
                "q": f"{query} language:C language:C++ stars:>100",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            data = self._github_request(self.GITHUB_SEARCH, params)
            
            if data and "items" in data:
                for repo in data["items"]:
                    repo_full_name = repo["full_name"]
                    
                    if repo_full_name in seen_repos:
                        continue
                    
                    seen_repos.add(repo_full_name)
                    
                    plugin_info = self._parse_repo_info(repo)
                    if plugin_info:
                        plugins.append(plugin_info)
        
        # Sort by stars
        plugins.sort(key=lambda x: x.get("stars", 0), reverse=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": plugins[:max_results]
        }
        self._save_cache()
        
        return plugins[:max_results]
    
    def discover_trending_plugins(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Discover trending OBS plugins (recently popular).
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of plugin dictionaries
        """
        cache_key = "trending_plugins"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        plugins = []
        seen_repos = set()
        
        # Search for trending OBS plugins (created recently with good stars)
        for query in self.PLUGIN_QUERIES[:2]:
            params = {
                "q": f"{query} language:C language:C++ created:>180days stars:>50",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            data = self._github_request(self.GITHUB_SEARCH, params)
            
            if data and "items" in data:
                for repo in data["items"]:
                    repo_full_name = repo["full_name"]
                    
                    if repo_full_name in seen_repos:
                        continue
                    
                    seen_repos.add(repo_full_name)
                    
                    plugin_info = self._parse_repo_info(repo)
                    if plugin_info:
                        # Calculate trending score
                        plugin_info["trending_score"] = self._calculate_trending_score(repo)
                        plugins.append(plugin_info)
        
        # Sort by trending score
        plugins.sort(key=lambda x: x.get("trending_score", 0), reverse=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": plugins[:max_results]
        }
        self._save_cache()
        
        return plugins[:max_results]
    
    def discover_by_developer(self, developer: str, max_results: int = 10) -> List[Dict]:
        """
        Discover plugins from a specific developer.
        
        Args:
            developer: GitHub username
            max_results: Maximum number of results
            
        Returns:
            List of plugin dictionaries
        """
        params = {
            "q": f"user:{developer} obs",
            "sort": "updated",
            "order": "desc",
            "per_page": max_results
        }
        
        data = self._github_request(self.GITHUB_SEARCH, params)
        
        plugins = []
        if data and "items" in data:
            for repo in data["items"]:
                plugin_info = self._parse_repo_info(repo)
                if plugin_info:
                    plugins.append(plugin_info)
        
        return plugins
    
    def discover_obs_scripts(self, max_results: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Discover OBS Lua/Python scripts.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of script dictionaries
        """
        cache_key = "obs_scripts"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        scripts = []
        seen_repos = set()
        
        # Search for OBS scripts (Lua and Python)
        for language in ["Lua", "Python"]:
            params = {
                "q": f"obs-studio script language:{language}",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            data = self._github_request(self.GITHUB_SEARCH, params)
            
            if data and "items" in data:
                for repo in data["items"]:
                    repo_full_name = repo["full_name"]
                    
                    if repo_full_name in seen_repos:
                        continue
                    
                    seen_repos.add(repo_full_name)
                    
                    script_info = self._parse_repo_info(repo, is_script=True)
                    if script_info:
                        scripts.append(script_info)
        
        # Sort by stars
        scripts.sort(key=lambda x: x.get("stars", 0), reverse=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": scripts[:max_results]
        }
        self._save_cache()
        
        return scripts[:max_results]
    
    def _parse_repo_info(self, repo: Dict, is_script: bool = False) -> Optional[Dict]:
        """
        Parse GitHub repository data into plugin/script info.
        
        Args:
            repo: GitHub repository data
            is_script: Whether this is a script (vs plugin)
            
        Returns:
            Plugin/script dictionary or None
        """
        try:
            # Extract basic info
            name = repo["name"]
            full_name = repo["full_name"]
            description = repo.get("description", "No description available")
            homepage = repo.get("html_url", "")
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            language = repo.get("language", "Unknown")
            updated_at = repo.get("updated_at", "")
            created_at = repo.get("created_at", "")
            
            # Get author from full_name
            author = full_name.split("/")[0] if "/" in full_name else "Unknown"
            
            # Try to get download URL (check for releases)
            download_url = f"{homepage}/releases/latest"
            
            # Determine category from name/description
            category = self._determine_category(name, description)
            
            # Check if Windows compatible (look for keywords)
            has_windows = any(keyword in description.lower() or keyword in name.lower() 
                            for keyword in ["windows", "win32", "win64", "cross-platform"])
            
            return {
                "name": name,
                "full_name": full_name,
                "display_name": self._format_display_name(name),
                "description": description,
                "author": author,
                "category": category,
                "homepage_url": homepage,
                "download_url": download_url,
                "stars": stars,
                "forks": forks,
                "language": language,
                "updated_at": updated_at,
                "created_at": created_at,
                "is_script": is_script,
                "windows_compatible": has_windows or not is_script,  # Assume plugins are Windows by default
                "discovered_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error parsing repo info: {e}")
            return None
    
    def _format_display_name(self, name: str) -> str:
        """Format repository name as display name."""
        # Remove common prefixes
        name = re.sub(r'^obs[-_]', '', name, flags=re.IGNORECASE)
        
        # Convert hyphens/underscores to spaces
        name = name.replace('-', ' ').replace('_', ' ')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def _determine_category(self, name: str, description: str) -> str:
        """Determine plugin category from name and description."""
        text = (name + " " + description).lower()
        
        if any(word in text for word in ["filter", "effect", "blur", "color", "shader"]):
            return "Effects"
        elif any(word in text for word in ["source", "input", "capture"]):
            return "Sources"
        elif any(word in text for word in ["transition", "move", "slide"]):
            return "Transitions"
        elif any(word in text for word in ["stream", "rtmp", "output", "record"]):
            return "Output"
        elif any(word in text for word in ["audio", "sound", "volume", "mixer"]):
            return "Audio"
        elif any(word in text for word in ["websocket", "remote", "control", "api", "midi", "ndi"]):
            return "Integration"
        elif any(word in text for word in ["scene", "switch", "auto"]):
            return "Automation"
        elif any(word in text for word in ["script", "lua", "python"]):
            return "Scripts"
        else:
            return "Other"
    
    def _calculate_trending_score(self, repo: Dict) -> float:
        """
        Calculate trending score based on recent activity.
        
        Args:
            repo: GitHub repository data
            
        Returns:
            Trending score (higher is more trending)
        """
        try:
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            
            # Calculate days since creation
            created_str = repo.get("created_at", "")
            if created_str:
                created = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ")
                days_old = (datetime.now() - created).days
                
                # Avoid division by zero
                days_old = max(days_old, 1)
                
                # Trending score: stars per day + forks per day
                score = (stars / days_old) * 10 + (forks / days_old) * 5
                return score
        except Exception:
            pass
        
        return 0.0
    
    def get_known_developers(self) -> List[str]:
        """Get list of known OBS plugin developers."""
        return self.KNOWN_DEVELOPERS.copy()
    
    def clear_cache(self):
        """Clear all cached discovery data."""
        self.cache = {}
        self._save_cache()
    
    def get_cache_info(self) -> Dict:
        """Get information about cached data."""
        info = {}
        for key, data in self.cache.items():
            cached_at = data.get("cached_at", "Unknown")
            result_count = len(data.get("results", []))
            
            try:
                cached_dt = datetime.fromisoformat(cached_at)
                age_hours = (datetime.now() - cached_dt).total_seconds() / 3600
                is_valid = age_hours < self.cache_expiry.total_seconds() / 3600
            except Exception:
                age_hours = 0
                is_valid = False
            
            info[key] = {
                "cached_at": cached_at,
                "age_hours": age_hours,
                "result_count": result_count,
                "is_valid": is_valid
            }
        
        return info
    
    def discover_obs_website_plugins(self, max_results: int = 50, force_refresh: bool = False) -> List[Dict]:
        """
        Discover plugins from the official OBS website.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of plugin dictionaries from OBS Resources
        """
        cache_key = "obs_website_plugins"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        plugins = self.obs_resources.fetch_obs_plugins(max_results=max_results, force_refresh=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": plugins[:max_results]
        }
        self._save_cache()
        
        return plugins[:max_results]
    
    def discover_obs_website_scripts(self, max_results: int = 50, force_refresh: bool = False) -> List[Dict]:
        """
        Discover scripts from the official OBS website.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query (ignore cache)
            
        Returns:
            List of script dictionaries from OBS Resources
        """
        cache_key = "obs_website_scripts"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        scripts = self.obs_resources.fetch_obs_scripts(max_results=max_results, force_refresh=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": scripts[:max_results]
        }
        self._save_cache()
        
        return scripts[:max_results]
    
    def discover_combined_popular(self, max_results: int = 30, force_refresh: bool = False) -> List[Dict]:
        """
        Discover popular plugins from both GitHub and OBS website.
        
        Args:
            max_results: Maximum number of results
            force_refresh: Force fresh query
            
        Returns:
            Combined list of popular plugins from both sources
        """
        cache_key = "combined_popular"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key].get("results", [])[:max_results]
        
        # Get from both sources
        github_plugins = self.discover_popular_plugins(max_results=20, force_refresh=force_refresh)
        obs_plugins = self.obs_resources.fetch_popular_plugins(max_results=20, force_refresh=force_refresh)
        
        # Combine and deduplicate
        combined = []
        seen_names = set()
        
        # Add GitHub plugins first (they have more metadata)
        for plugin in github_plugins:
            name = plugin.get('name', '').lower()
            if name not in seen_names:
                plugin['source'] = 'GitHub'
                combined.append(plugin)
                seen_names.add(name)
        
        # Add OBS website plugins
        for plugin in obs_plugins:
            name = plugin.get('name', '').lower()
            if name not in seen_names:
                plugin['source'] = 'OBS Resources'
                combined.append(plugin)
                seen_names.add(name)
        
        # Sort by popularity (stars for GitHub, rating*downloads for OBS)
        combined.sort(key=lambda x: (
            x.get('stars', 0) if x.get('source') == 'GitHub' 
            else x.get('rating_weighted', 0) * 100 + x.get('downloads', 0) / 100
        ), reverse=True)
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": combined[:max_results]
        }
        self._save_cache()
        
        return combined[:max_results]
