"""
Local Repository Manager - manages local storage of plugin files and versions.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib


class LocalRepository:
    """Manages local storage of plugin files with version tracking."""
    
    def __init__(self, repo_dir: str = "local_repository"):
        """
        Initialize the local repository.
        
        Args:
            repo_dir: Directory for local plugin storage
        """
        self.repo_dir = Path(repo_dir)
        self.repo_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.plugins_dir = self.repo_dir / "plugins"
        self.scripts_dir = self.repo_dir / "scripts"
        self.metadata_dir = self.repo_dir / "metadata"
        
        for directory in [self.plugins_dir, self.scripts_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True)
        
        self.index_file = self.repo_dir / "repository_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load repository index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
                self.index = {"plugins": {}, "scripts": {}}
        else:
            self.index = {"plugins": {}, "scripts": {}}
    
    def _save_index(self):
        """Save repository index."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def add_plugin_file(self, plugin_name: str, version: str, file_path: Path,
                       metadata: Dict = None) -> Tuple[bool, str]:
        """
        Add a plugin file to the local repository.
        
        Args:
            plugin_name: Name of the plugin
            version: Version string
            file_path: Path to the plugin file
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create plugin directory
            plugin_dir = self.plugins_dir / plugin_name
            plugin_dir.mkdir(exist_ok=True)
            
            # Create version directory
            version_dir = plugin_dir / version
            version_dir.mkdir(exist_ok=True)
            
            # Copy file to repository
            dest_file = version_dir / file_path.name
            shutil.copy2(file_path, dest_file)
            
            # Calculate hash
            file_hash = self._calculate_hash(dest_file)
            
            # Update index
            if plugin_name not in self.index["plugins"]:
                self.index["plugins"][plugin_name] = {"versions": []}
            
            version_entry = {
                "version": version,
                "filename": file_path.name,
                "path": str(dest_file),
                "size": dest_file.stat().st_size,
                "hash": file_hash,
                "added_date": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Check if version already exists
            existing_versions = [v["version"] for v in self.index["plugins"][plugin_name]["versions"]]
            if version not in existing_versions:
                self.index["plugins"][plugin_name]["versions"].append(version_entry)
                
                # Keep only last 2 versions
                self._cleanup_old_versions(plugin_name, "plugins")
            else:
                # Update existing version
                for i, v in enumerate(self.index["plugins"][plugin_name]["versions"]):
                    if v["version"] == version:
                        self.index["plugins"][plugin_name]["versions"][i] = version_entry
                        break
            
            self._save_index()
            return True, f"Added {plugin_name} v{version} to local repository"
        except Exception as e:
            return False, f"Failed to add to repository: {str(e)}"
    
    def add_script_file(self, script_name: str, version: str, file_path: Path,
                       metadata: Dict = None) -> Tuple[bool, str]:
        """
        Add a script file to the local repository.
        
        Args:
            script_name: Name of the script
            version: Version string
            file_path: Path to the script file
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create script directory
            script_dir = self.scripts_dir / script_name
            script_dir.mkdir(exist_ok=True)
            
            # Create version directory
            version_dir = script_dir / version
            version_dir.mkdir(exist_ok=True)
            
            # Copy file to repository
            dest_file = version_dir / file_path.name
            shutil.copy2(file_path, dest_file)
            
            # Calculate hash
            file_hash = self._calculate_hash(dest_file)
            
            # Update index
            if script_name not in self.index["scripts"]:
                self.index["scripts"][script_name] = {"versions": []}
            
            version_entry = {
                "version": version,
                "filename": file_path.name,
                "path": str(dest_file),
                "size": dest_file.stat().st_size,
                "hash": file_hash,
                "added_date": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Check if version already exists
            existing_versions = [v["version"] for v in self.index["scripts"][script_name]["versions"]]
            if version not in existing_versions:
                self.index["scripts"][script_name]["versions"].append(version_entry)
                
                # Keep only last 2 versions
                self._cleanup_old_versions(script_name, "scripts")
            else:
                # Update existing version
                for i, v in enumerate(self.index["scripts"][script_name]["versions"]):
                    if v["version"] == version:
                        self.index["scripts"][script_name]["versions"][i] = version_entry
                        break
            
            self._save_index()
            return True, f"Added {script_name} v{version} to local repository"
        except Exception as e:
            return False, f"Failed to add to repository: {str(e)}"
    
    def _cleanup_old_versions(self, name: str, repo_type: str):
        """
        Keep only the last 2 versions of a plugin/script.
        
        Args:
            name: Plugin or script name
            repo_type: "plugins" or "scripts"
        """
        versions = self.index[repo_type][name]["versions"]
        
        if len(versions) > 2:
            # Sort by added date
            versions.sort(key=lambda x: x.get("added_date", ""), reverse=True)
            
            # Keep first 2, delete rest
            to_delete = versions[2:]
            self.index[repo_type][name]["versions"] = versions[:2]
            
            # Delete files
            for version_entry in to_delete:
                try:
                    file_path = Path(version_entry["path"])
                    if file_path.exists():
                        # Delete the version directory
                        version_dir = file_path.parent
                        shutil.rmtree(version_dir)
                except Exception as e:
                    print(f"Error deleting old version: {e}")
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return ""
    
    def get_plugin_versions(self, plugin_name: str) -> List[Dict]:
        """Get all versions of a plugin in the repository."""
        if plugin_name in self.index["plugins"]:
            versions = self.index["plugins"][plugin_name]["versions"]
            # Sort by version (newest first)
            return sorted(versions, key=lambda x: x.get("added_date", ""), reverse=True)
        return []
    
    def get_script_versions(self, script_name: str) -> List[Dict]:
        """Get all versions of a script in the repository."""
        if script_name in self.index["scripts"]:
            versions = self.index["scripts"][script_name]["versions"]
            # Sort by version (newest first)
            return sorted(versions, key=lambda x: x.get("added_date", ""), reverse=True)
        return []
    
    def get_plugin_file(self, plugin_name: str, version: str = None) -> Optional[Path]:
        """
        Get the file path for a plugin version.
        
        Args:
            plugin_name: Plugin name
            version: Version string (None for latest)
            
        Returns:
            Path to plugin file or None
        """
        versions = self.get_plugin_versions(plugin_name)
        
        if not versions:
            return None
        
        if version is None:
            # Return latest version
            return Path(versions[0]["path"])
        
        # Find specific version
        for v in versions:
            if v["version"] == version:
                return Path(v["path"])
        
        return None
    
    def get_script_file(self, script_name: str, version: str = None) -> Optional[Path]:
        """
        Get the file path for a script version.
        
        Args:
            script_name: Script name
            version: Version string (None for latest)
            
        Returns:
            Path to script file or None
        """
        versions = self.get_script_versions(script_name)
        
        if not versions:
            return None
        
        if version is None:
            # Return latest version
            return Path(versions[0]["path"])
        
        # Find specific version
        for v in versions:
            if v["version"] == version:
                return Path(v["path"])
        
        return None
    
    def list_all_plugins(self) -> List[Dict]:
        """Get list of all plugins in repository."""
        plugins = []
        for name, data in self.index["plugins"].items():
            if data["versions"]:
                latest = data["versions"][0]
                plugins.append({
                    "name": name,
                    "latest_version": latest["version"],
                    "version_count": len(data["versions"]),
                    "latest_added": latest.get("added_date", ""),
                    "size": latest.get("size", 0),
                    "metadata": latest.get("metadata", {})
                })
        return plugins
    
    def list_all_scripts(self) -> List[Dict]:
        """Get list of all scripts in repository."""
        scripts = []
        for name, data in self.index["scripts"].items():
            if data["versions"]:
                latest = data["versions"][0]
                scripts.append({
                    "name": name,
                    "latest_version": latest["version"],
                    "version_count": len(data["versions"]),
                    "latest_added": latest.get("added_date", ""),
                    "size": latest.get("size", 0),
                    "metadata": latest.get("metadata", {})
                })
        return scripts
    
    def get_repository_stats(self) -> Dict:
        """Get statistics about the repository."""
        total_plugins = len(self.index["plugins"])
        total_scripts = len(self.index["scripts"])
        
        total_plugin_versions = sum(len(data["versions"]) for data in self.index["plugins"].values())
        total_script_versions = sum(len(data["versions"]) for data in self.index["scripts"].values())
        
        # Calculate total size
        total_size = 0
        for plugin_data in self.index["plugins"].values():
            for version in plugin_data["versions"]:
                total_size += version.get("size", 0)
        for script_data in self.index["scripts"].values():
            for version in script_data["versions"]:
                total_size += version.get("size", 0)
        
        return {
            "total_plugins": total_plugins,
            "total_scripts": total_scripts,
            "total_plugin_versions": total_plugin_versions,
            "total_script_versions": total_script_versions,
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024)
        }
    
    def has_plugin(self, plugin_name: str, version: str = None) -> bool:
        """Check if a plugin version exists in repository."""
        if plugin_name not in self.index["plugins"]:
            return False
        
        if version is None:
            return len(self.index["plugins"][plugin_name]["versions"]) > 0
        
        versions = [v["version"] for v in self.index["plugins"][plugin_name]["versions"]]
        return version in versions
    
    def has_script(self, script_name: str, version: str = None) -> bool:
        """Check if a script version exists in repository."""
        if script_name not in self.index["scripts"]:
            return False
        
        if version is None:
            return len(self.index["scripts"][script_name]["versions"]) > 0
        
        versions = [v["version"] for v in self.index["scripts"][script_name]["versions"]]
        return version in versions
    
    def export_index(self, export_path: Path) -> bool:
        """Export repository index to a file."""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.index, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting index: {e}")
            return False
    
    def cleanup_orphaned_files(self) -> Tuple[int, int]:
        """
        Remove files not referenced in the index.
        
        Returns:
            Tuple of (files_removed, space_freed_bytes)
        """
        files_removed = 0
        space_freed = 0
        
        # Get all files referenced in index
        indexed_paths = set()
        for plugin_data in self.index["plugins"].values():
            for version in plugin_data["versions"]:
                indexed_paths.add(Path(version["path"]))
        for script_data in self.index["scripts"].values():
            for version in script_data["versions"]:
                indexed_paths.add(Path(version["path"]))
        
        # Check plugins directory
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                for version_dir in plugin_dir.iterdir():
                    if version_dir.is_dir():
                        for file_path in version_dir.iterdir():
                            if file_path.is_file() and file_path not in indexed_paths:
                                try:
                                    size = file_path.stat().st_size
                                    file_path.unlink()
                                    files_removed += 1
                                    space_freed += size
                                except Exception:
                                    pass
        
        # Check scripts directory
        for script_dir in self.scripts_dir.iterdir():
            if script_dir.is_dir():
                for version_dir in script_dir.iterdir():
                    if version_dir.is_dir():
                        for file_path in version_dir.iterdir():
                            if file_path.is_file() and file_path not in indexed_paths:
                                try:
                                    size = file_path.stat().st_size
                                    file_path.unlink()
                                    files_removed += 1
                                    space_freed += size
                                except Exception:
                                    pass
        
        return files_removed, space_freed
