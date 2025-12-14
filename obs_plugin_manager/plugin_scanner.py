"""
Plugin Scanner - scans OBS installation to detect installed plugins and their versions.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
from .logger import get_logger


class PluginScanner:
    """Scans OBS directories to detect installed plugins."""
    
    # Common plugin file extensions
    PLUGIN_EXTENSIONS = ['.dll', '.so']
    
    # Patterns to extract version from DLL files
    VERSION_PATTERNS = [
        re.compile(r'(\d+\.\d+\.\d+\.\d+)'),
        re.compile(r'(\d+\.\d+\.\d+)'),
        re.compile(r'(\d+\.\d+)'),
    ]
    
    def __init__(self, plugin_dirs: List[Path]):
        """
        Initialize the plugin scanner.
        
        Args:
            plugin_dirs: List of directories to scan for plugins
        """
        self.logger = get_logger(__name__)
        self.plugin_dirs = plugin_dirs
        self.scanned_plugins = []
        self.logger.info(f"Plugin scanner initialized with {len(plugin_dirs)} directories")
    
    def scan_plugins(self) -> List[Dict]:
        """
        Scan all plugin directories for installed plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        self.scanned_plugins = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            # Scan for DLL files
            for dll_file in plugin_dir.glob("*.dll"):
                plugin_info = self._analyze_plugin_file(dll_file)
                if plugin_info:
                    self.scanned_plugins.append(plugin_info)
            
            # Scan subdirectories
            for subdir in plugin_dir.iterdir():
                if subdir.is_dir():
                    for dll_file in subdir.rglob("*.dll"):
                        plugin_info = self._analyze_plugin_file(dll_file)
                        if plugin_info:
                            self.scanned_plugins.append(plugin_info)
        
        # Remove duplicates (same plugin in multiple locations)
        self.scanned_plugins = self._deduplicate_plugins(self.scanned_plugins)
        self.logger.info(f"Scan complete: found {len(self.scanned_plugins)} plugins")
        
        return self.scanned_plugins
    
    def _analyze_plugin_file(self, file_path: Path) -> Optional[Dict]:
        """
        Analyze a plugin file to extract information.
        
        Args:
            file_path: Path to the plugin file
            
        Returns:
            Dictionary with plugin information or None
        """
        try:
            file_stat = file_path.stat()
            
            # Get file hash for identification
            file_hash = self._get_file_hash(file_path)
            
            # Try to extract version from file properties
            version = self._extract_version_from_file(file_path)
            
            # Get file size and modification time
            plugin_info = {
                'name': file_path.stem,
                'filename': file_path.name,
                'path': str(file_path),
                'version': version or "Unknown",
                'size': file_stat.st_size,
                'modified': file_stat.st_mtime,
                'hash': file_hash,
                'directory': str(file_path.parent),
            }
            
            return plugin_info
        except Exception as e:
            print(f"Error analyzing plugin file {file_path}: {e}")
            return None
    
    def _extract_version_from_file(self, file_path: Path) -> Optional[str]:
        """
        Try to extract version information from a DLL file.
        
        Args:
            file_path: Path to the DLL file
            
        Returns:
            Version string or None
        """
        try:
            # Try using PowerShell to get file version (Windows)
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command', 
                 f'(Get-Item "{file_path}").VersionInfo.FileVersion'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                version = result.stdout.strip()
                # Clean up version string
                version = version.replace(',', '.').strip()
                if version and version != '0.0.0.0':
                    return version
        except Exception:
            pass
        
        # Try reading file content for version strings
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Look for version patterns in the binary
                content_str = content.decode('utf-8', errors='ignore')
                
                for pattern in self.VERSION_PATTERNS:
                    matches = pattern.findall(content_str)
                    if matches:
                        # Return the first reasonable version found
                        for match in matches:
                            if not match.startswith('0.0'):
                                return match
        except Exception:
            pass
        
        return None
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _deduplicate_plugins(self, plugins: List[Dict]) -> List[Dict]:
        """
        Remove duplicate plugins based on hash.
        
        Args:
            plugins: List of plugin dictionaries
            
        Returns:
            Deduplicated list
        """
        seen_hashes = set()
        unique_plugins = []
        
        for plugin in plugins:
            plugin_hash = plugin.get('hash', '')
            if plugin_hash and plugin_hash not in seen_hashes:
                seen_hashes.add(plugin_hash)
                unique_plugins.append(plugin)
            elif not plugin_hash:
                # If no hash, keep it anyway
                unique_plugins.append(plugin)
        
        return unique_plugins
    
    def get_plugin_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a specific plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin dictionary or None
        """
        for plugin in self.scanned_plugins:
            if plugin['name'].lower() == name.lower():
                return plugin
        return None
    
    def get_all_plugins(self) -> List[Dict]:
        """Get all scanned plugins."""
        return self.scanned_plugins
    
    def get_plugin_files(self, plugin_name: str) -> List[Path]:
        """
        Get all files associated with a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List of file paths
        """
        files = []
        plugin = self.get_plugin_by_name(plugin_name)
        
        if not plugin:
            return files
        
        plugin_path = Path(plugin['path'])
        plugin_dir = plugin_path.parent
        
        # Get the main DLL
        files.append(plugin_path)
        
        # Look for related files (configs, data, etc.)
        # Common patterns: plugin_name.*, *_plugin_name.*
        base_name = plugin_path.stem
        
        for file_path in plugin_dir.iterdir():
            if file_path.is_file() and base_name.lower() in file_path.name.lower():
                if file_path not in files:
                    files.append(file_path)
        
        # Check for plugin-specific data directory
        data_dir = plugin_dir / base_name
        if data_dir.exists() and data_dir.is_dir():
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    files.append(file_path)
        
        return files
