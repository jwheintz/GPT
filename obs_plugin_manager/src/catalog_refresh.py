"""
Plugin Catalog Refresh.
Handles refreshing and updating the plugin catalog from online sources.
"""

import json
import logging
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CatalogUpdate:
    """Information about a catalog update."""
    
    plugins_added: int
    plugins_updated: int
    plugins_total: int
    update_time: str
    source: str


class CatalogRefresher:
    """Handles refreshing the plugin catalog from online sources."""
    
    # Known sources for plugin information
    CATALOG_SOURCES = {
        'github_obsproject': 'https://api.github.com/orgs/obsproject/repos',
        'github_exeldro': 'https://api.github.com/users/exeldro/repos',
        'obsproject_forum': 'https://obsproject.com/forum/resources/',
    }
    
    # GitHub users/orgs known for OBS plugins
    PLUGIN_AUTHORS = [
        'exeldro',
        'Xaymar',
        'Palakis',
        'obs-ndi',
        'WarmUpTill',
        'FiniteSingularity',
        'univrsal',
        'occ-ai',
        'Andersama',
        'fzwoch',
        'iamscottxu',
        'sorayuki',
    ]
    
    def __init__(self, database=None):
        if database is None:
            from .database import PluginDatabase
            database = PluginDatabase()
        
        self.db = database
    
    def refresh_from_github(self, author: str) -> List[Dict[str, Any]]:
        """
        Fetch plugin information from a GitHub user/org.
        
        Args:
            author: GitHub username or organization.
            
        Returns:
            List of discovered plugin information.
        """
        plugins = []
        
        try:
            # Fetch repos
            url = f"https://api.github.com/users/{author}/repos?per_page=100"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            repos = response.json()
            
            for repo in repos:
                name = repo.get('name', '')
                description = repo.get('description', '')
                
                # Filter for OBS-related repos
                if not self._is_obs_plugin_repo(name, description):
                    continue
                
                # Get latest release info
                releases_url = repo.get('releases_url', '').replace('{/id}', '/latest')
                
                try:
                    release_resp = requests.get(releases_url, timeout=10)
                    if release_resp.status_code == 200:
                        release = release_resp.json()
                        
                        # Find Windows asset
                        download_url = self._find_windows_asset(release.get('assets', []))
                        version = release.get('tag_name', '').lstrip('v')
                        release_date = release.get('published_at', '')[:10]
                    else:
                        download_url = repo.get('html_url') + '/releases'
                        version = ''
                        release_date = ''
                except Exception:
                    download_url = repo.get('html_url') + '/releases'
                    version = ''
                    release_date = ''
                
                plugins.append({
                    'id': f"{author}-{name}".lower().replace('_', '-'),
                    'name': self._format_plugin_name(name),
                    'description': description or '',
                    'author': author,
                    'github_url': repo.get('html_url', ''),
                    'download_url': download_url,
                    'latest_version': version,
                    'release_date': release_date,
                    'stars': repo.get('stargazers_count', 0),
                })
        
        except Exception as e:
            logger.error(f"Failed to fetch repos from {author}: {e}")
        
        return plugins
    
    def _is_obs_plugin_repo(self, name: str, description: str) -> bool:
        """Check if a repo is likely an OBS plugin."""
        name_lower = name.lower()
        desc_lower = (description or '').lower()
        
        # Keywords that indicate OBS plugins
        keywords = ['obs', 'obs-studio', 'obs-plugin', 'streaming', 'broadcast']
        
        # Check name
        if any(kw in name_lower for kw in keywords):
            return True
        
        # Check description
        if any(kw in desc_lower for kw in keywords):
            return True
        
        # Known plugin patterns
        plugin_patterns = [
            'source', 'filter', 'transition', 'output', 'dock',
            'websocket', 'ndi', 'asio', 'virtualcam'
        ]
        
        if any(p in name_lower for p in plugin_patterns):
            if 'obs' in desc_lower:
                return True
        
        return False
    
    def _find_windows_asset(self, assets: List[Dict]) -> str:
        """Find Windows download asset from release assets."""
        # Priority order for Windows 64-bit
        patterns = [
            'win64', 'windows-x64', 'x64', 'win', 'windows'
        ]
        
        for pattern in patterns:
            for asset in assets:
                name = asset.get('name', '').lower()
                if pattern in name and (name.endswith('.zip') or name.endswith('.exe')):
                    return asset.get('browser_download_url', '')
        
        # Fall back to any zip file
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.zip'):
                return asset.get('browser_download_url', '')
        
        return ''
    
    def _format_plugin_name(self, name: str) -> str:
        """Format repository name to display name."""
        # Remove common prefixes
        prefixes = ['obs-', 'obs_', 'obs-studio-']
        name_lower = name.lower()
        
        for prefix in prefixes:
            if name_lower.startswith(prefix):
                name = name[len(prefix):]
                break
        
        # Convert to title case
        name = name.replace('-', ' ').replace('_', ' ')
        name = name.title()
        
        return name
    
    def refresh_all(self, progress_callback=None) -> CatalogUpdate:
        """
        Refresh catalog from all known sources.
        
        Args:
            progress_callback: Optional callback(current, total, message).
            
        Returns:
            CatalogUpdate with refresh statistics.
        """
        added = 0
        updated = 0
        total_found = 0
        
        # Get existing plugins for comparison
        existing = {p.id: p for p in self.db.get_all_plugins()}
        
        # Refresh from each author
        total_authors = len(self.PLUGIN_AUTHORS)
        
        for i, author in enumerate(self.PLUGIN_AUTHORS):
            if progress_callback:
                progress_callback(i + 1, total_authors, f"Scanning {author}...")
            
            plugins = self.refresh_from_github(author)
            total_found += len(plugins)
            
            for plugin_data in plugins:
                plugin_id = plugin_data['id']
                
                if plugin_id in existing:
                    # Update existing
                    old = existing[plugin_id]
                    if plugin_data['latest_version'] and plugin_data['latest_version'] != old.latest_version:
                        self._update_plugin_from_data(plugin_data)
                        updated += 1
                else:
                    # Add new
                    self._add_plugin_from_data(plugin_data)
                    added += 1
        
        # Update metadata
        update_time = datetime.now().isoformat()
        self.db.set_metadata('last_catalog_refresh', update_time)
        
        return CatalogUpdate(
            plugins_added=added,
            plugins_updated=updated,
            plugins_total=len(self.db.get_all_plugins()),
            update_time=update_time,
            source='GitHub'
        )
    
    def _add_plugin_from_data(self, data: Dict[str, Any]) -> None:
        """Add a new plugin from discovered data."""
        from .database import PluginInfo
        
        now = datetime.now().isoformat()
        
        plugin = PluginInfo(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            author=data.get('author', ''),
            category='other',
            latest_version=data.get('latest_version', ''),
            release_date=data.get('release_date', ''),
            download_url=data.get('download_url', ''),
            github_url=data.get('github_url', ''),
            homepage_url=data.get('github_url', ''),
            dll_name='',
            additional_files='[]',
            is_popular=data.get('stars', 0) > 100,
            is_recommended=False,
            added_date=now,
            updated_date=now
        )
        
        self.db.add_or_update_plugin(plugin)
    
    def _update_plugin_from_data(self, data: Dict[str, Any]) -> None:
        """Update existing plugin with new data."""
        existing = self.db.get_plugin(data['id'])
        
        if existing:
            existing.latest_version = data.get('latest_version', existing.latest_version)
            existing.release_date = data.get('release_date', existing.release_date)
            existing.download_url = data.get('download_url', existing.download_url)
            existing.updated_date = datetime.now().isoformat()
            
            self.db.add_or_update_plugin(existing)
    
    def get_last_refresh_time(self) -> Optional[str]:
        """Get the last time the catalog was refreshed."""
        return self.db.get_metadata('last_catalog_refresh')
    
    def check_for_updates(self, installed_plugins: List[Dict]) -> List[Dict[str, Any]]:
        """
        Check for updates to installed plugins.
        
        Args:
            installed_plugins: List of installed plugin info dicts.
            
        Returns:
            List of available updates.
        """
        updates = []
        
        for installed in installed_plugins:
            plugin_id = installed.get('catalog_id')
            if not plugin_id:
                continue
            
            catalog_plugin = self.db.get_plugin(plugin_id)
            if not catalog_plugin:
                continue
            
            current_version = installed.get('version', '')
            latest_version = catalog_plugin.latest_version
            
            if current_version and latest_version:
                if self._is_newer_version(latest_version, current_version):
                    updates.append({
                        'plugin_id': plugin_id,
                        'plugin_name': catalog_plugin.name,
                        'current_version': current_version,
                        'latest_version': latest_version,
                        'download_url': catalog_plugin.download_url,
                        'release_date': catalog_plugin.release_date,
                    })
        
        return updates
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings to check if update is available."""
        from packaging import version
        
        try:
            # Clean version strings
            latest_clean = self._clean_version(latest)
            current_clean = self._clean_version(current)
            
            if not latest_clean or not current_clean:
                return False
            
            return version.parse(latest_clean) > version.parse(current_clean)
        except Exception:
            return latest != current
    
    def _clean_version(self, ver: str) -> str:
        """Clean version string for comparison."""
        import re
        
        # Remove common prefixes
        ver = ver.lstrip('vV')
        
        # Keep only version-like characters
        match = re.match(r'[\d.]+', ver)
        return match.group(0) if match else ver
    
    def import_from_file(self, filepath: str) -> CatalogUpdate:
        """
        Import plugin catalog from a JSON file.
        
        Args:
            filepath: Path to JSON file.
            
        Returns:
            CatalogUpdate with import statistics.
        """
        count = self.db.import_catalog_from_json(filepath)
        
        return CatalogUpdate(
            plugins_added=count,
            plugins_updated=0,
            plugins_total=len(self.db.get_all_plugins()),
            update_time=datetime.now().isoformat(),
            source=f'File: {filepath}'
        )
    
    def export_to_file(self, filepath: str) -> None:
        """Export plugin catalog to a JSON file."""
        self.db.export_catalog_to_json(filepath)


# Global instance
_catalog_refresher: Optional[CatalogRefresher] = None


def get_catalog_refresher() -> CatalogRefresher:
    """Get the global CatalogRefresher instance."""
    global _catalog_refresher
    if _catalog_refresher is None:
        _catalog_refresher = CatalogRefresher()
    return _catalog_refresher
