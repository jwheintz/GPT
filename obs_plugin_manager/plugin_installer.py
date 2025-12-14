"""
Plugin Installer - handles downloading, installing, updating, and removing plugins.
"""

import os
import shutil
import zipfile
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime


class PluginInstaller:
    """Manages plugin installation, updates, and removal."""
    
    def __init__(self, plugin_dirs: List[Path], archive_dir: str = "plugin_archives"):
        """
        Initialize the plugin installer.
        
        Args:
            plugin_dirs: List of OBS plugin directories
            archive_dir: Directory to store plugin archives
        """
        self.plugin_dirs = plugin_dirs
        self.primary_plugin_dir = plugin_dirs[0] if plugin_dirs else None
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
        self.download_dir = Path(tempfile.gettempdir()) / "obs_plugin_downloads"
        self.download_dir.mkdir(exist_ok=True)
    
    def download_plugin(self, url: str, plugin_name: str,
                       progress_callback: Optional[Callable[[int, int], None]] = None) -> Optional[Path]:
        """
        Download a plugin from URL.
        
        Args:
            url: Download URL
            plugin_name: Name of the plugin
            progress_callback: Optional callback for progress (bytes_downloaded, total_bytes)
            
        Returns:
            Path to downloaded file or None on failure
        """
        try:
            # Determine filename
            if url.endswith('.zip'):
                filename = f"{plugin_name}.zip"
            else:
                filename = f"{plugin_name}_download.zip"
            
            download_path = self.download_dir / filename
            
            # Download with progress
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return download_path
        except Exception as e:
            print(f"Error downloading plugin: {e}")
            return None
    
    def extract_plugin(self, archive_path: Path, extract_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Extract a plugin archive.
        
        Args:
            archive_path: Path to the plugin archive
            extract_dir: Optional directory to extract to
            
        Returns:
            Path to extracted directory or None on failure
        """
        if not extract_dir:
            extract_dir = self.download_dir / f"extracted_{archive_path.stem}"
        
        try:
            extract_dir.mkdir(exist_ok=True, parents=True)
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            else:
                print(f"Unsupported archive format: {archive_path.suffix}")
                return None
            
            return extract_dir
        except Exception as e:
            print(f"Error extracting plugin: {e}")
            return None
    
    def find_plugin_files(self, extracted_dir: Path) -> Dict[str, List[Path]]:
        """
        Find plugin files in extracted directory.
        
        Args:
            extracted_dir: Path to extracted plugin directory
            
        Returns:
            Dictionary with categorized plugin files
        """
        plugin_files = {
            'dlls': [],
            'data': [],
            'other': []
        }
        
        # Find all DLL files
        for dll_file in extracted_dir.rglob("*.dll"):
            plugin_files['dlls'].append(dll_file)
        
        # Find data directories
        for item in extracted_dir.rglob("*"):
            if item.is_dir() and item.name in ['data', 'locale', 'config']:
                plugin_files['data'].append(item)
            elif item.is_file() and item.suffix in ['.ini', '.json', '.txt', '.cfg']:
                plugin_files['other'].append(item)
        
        return plugin_files
    
    def create_archive(self, plugin_name: str, version: str, files: List[Path]) -> Optional[Path]:
        """
        Create an archive of plugin files for rollback.
        
        Args:
            plugin_name: Name of the plugin
            version: Version of the plugin
            files: List of files to archive
            
        Returns:
            Path to archive or None on failure
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{plugin_name}_{version}_{timestamp}"
            archive_path = self.archive_dir / archive_name
            archive_path.mkdir(exist_ok=True, parents=True)
            
            archived_count = 0
            total_size = 0
            
            for file_path in files:
                if file_path.exists() and file_path.is_file():
                    # Preserve directory structure
                    rel_path = file_path.name
                    dest_path = archive_path / rel_path
                    dest_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    shutil.copy2(file_path, dest_path)
                    archived_count += 1
                    total_size += file_path.stat().st_size
                elif file_path.exists() and file_path.is_dir():
                    # Archive entire directory
                    dest_path = archive_path / file_path.name
                    shutil.copytree(file_path, dest_path, dirs_exist_ok=True)
                    archived_count += sum(1 for _ in file_path.rglob("*") if _.is_file())
                    total_size += sum(f.stat().st_size for f in file_path.rglob("*") if f.is_file())
            
            # Save metadata
            metadata = {
                'plugin_name': plugin_name,
                'version': version,
                'archived_date': timestamp,
                'file_count': archived_count,
                'total_size': total_size,
                'files': [str(f) for f in files]
            }
            
            metadata_file = archive_path / "archive_metadata.json"
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return archive_path
        except Exception as e:
            print(f"Error creating archive: {e}")
            return None
    
    def install_plugin_files(self, plugin_files: Dict[str, List[Path]],
                            plugin_name: str, backup: bool = True) -> Tuple[bool, str, List[Path]]:
        """
        Install plugin files to OBS directory.
        
        Args:
            plugin_files: Dictionary of plugin files
            plugin_name: Name of the plugin
            backup: Whether to create backup before installing
            
        Returns:
            Tuple of (success, message, installed_files)
        """
        if not self.primary_plugin_dir:
            return False, "No plugin directory available", []
        
        installed_files = []
        
        try:
            # Backup existing files if requested
            if backup:
                existing_files = []
                for dll in plugin_files['dlls']:
                    target = self.primary_plugin_dir / dll.name
                    if target.exists():
                        existing_files.append(target)
                
                if existing_files:
                    # Get version of existing plugin (if possible)
                    existing_version = "backup"
                    archive_path = self.create_archive(plugin_name, existing_version, existing_files)
                    if not archive_path:
                        return False, "Failed to create backup archive", []
            
            # Install DLL files
            for dll_file in plugin_files['dlls']:
                target_path = self.primary_plugin_dir / dll_file.name
                shutil.copy2(dll_file, target_path)
                installed_files.append(target_path)
            
            # Install data directories (if any)
            for data_dir in plugin_files['data']:
                target_path = self.primary_plugin_dir / data_dir.name
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(data_dir, target_path)
                installed_files.append(target_path)
            
            # Install other files
            for other_file in plugin_files['other']:
                target_path = self.primary_plugin_dir / other_file.name
                shutil.copy2(other_file, target_path)
                installed_files.append(target_path)
            
            return True, f"Successfully installed {len(installed_files)} file(s)", installed_files
        except Exception as e:
            return False, f"Installation failed: {str(e)}", installed_files
    
    def remove_plugin(self, plugin_info: Dict, create_backup: bool = True) -> Tuple[bool, str]:
        """
        Remove an installed plugin.
        
        Args:
            plugin_info: Plugin information dictionary
            create_backup: Whether to create backup before removal
            
        Returns:
            Tuple of (success, message)
        """
        try:
            plugin_path = Path(plugin_info['path'])
            
            if not plugin_path.exists():
                return False, "Plugin file not found"
            
            # Create backup if requested
            if create_backup:
                files_to_backup = [plugin_path]
                archive_path = self.create_archive(
                    plugin_info['name'],
                    plugin_info.get('version', 'unknown'),
                    files_to_backup
                )
                if not archive_path:
                    return False, "Failed to create backup"
            
            # Remove the plugin file
            plugin_path.unlink()
            
            # Remove associated files/directories
            plugin_dir = plugin_path.parent / plugin_info['name']
            if plugin_dir.exists() and plugin_dir.is_dir():
                shutil.rmtree(plugin_dir)
            
            return True, f"Successfully removed {plugin_info['name']}"
        except Exception as e:
            return False, f"Removal failed: {str(e)}"
    
    def restore_from_archive(self, archive_path: Path, plugin_name: str) -> Tuple[bool, str]:
        """
        Restore a plugin from archive (rollback).
        
        Args:
            archive_path: Path to the archive directory
            plugin_name: Name of the plugin
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not archive_path.exists():
                return False, "Archive not found"
            
            # Read metadata
            metadata_file = archive_path / "archive_metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Remove current version first
            for plugin_dir in self.plugin_dirs:
                for dll_file in plugin_dir.glob("*.dll"):
                    if plugin_name.lower() in dll_file.stem.lower():
                        dll_file.unlink()
            
            # Restore files from archive
            restored_count = 0
            for item in archive_path.iterdir():
                if item.name == "archive_metadata.json":
                    continue
                
                target_path = self.primary_plugin_dir / item.name
                
                if item.is_file():
                    shutil.copy2(item, target_path)
                    restored_count += 1
                elif item.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
                    restored_count += 1
            
            return True, f"Successfully restored {restored_count} item(s) from archive"
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def install_from_url(self, url: str, plugin_name: str,
                        progress_callback: Optional[Callable[[str, int], None]] = None) -> Tuple[bool, str]:
        """
        Download and install a plugin from URL.
        
        Args:
            url: Download URL
            plugin_name: Name of the plugin
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Download
            if progress_callback:
                progress_callback("Downloading plugin...", 10)
            
            downloaded_file = self.download_plugin(
                url, 
                plugin_name,
                lambda d, t: progress_callback("Downloading...", int(10 + (d/t * 40))) if progress_callback and t > 0 else None
            )
            
            if not downloaded_file:
                return False, "Download failed"
            
            # Extract
            if progress_callback:
                progress_callback("Extracting plugin...", 60)
            
            extracted_dir = self.extract_plugin(downloaded_file)
            if not extracted_dir:
                return False, "Extraction failed"
            
            # Find plugin files
            if progress_callback:
                progress_callback("Finding plugin files...", 70)
            
            plugin_files = self.find_plugin_files(extracted_dir)
            
            if not plugin_files['dlls']:
                return False, "No plugin DLL files found in archive"
            
            # Install
            if progress_callback:
                progress_callback("Installing plugin...", 80)
            
            success, message, installed_files = self.install_plugin_files(
                plugin_files,
                plugin_name,
                backup=True
            )
            
            # Cleanup
            if progress_callback:
                progress_callback("Cleaning up...", 95)
            
            try:
                downloaded_file.unlink()
                shutil.rmtree(extracted_dir)
            except Exception:
                pass
            
            if progress_callback:
                progress_callback("Complete!", 100)
            
            return success, message
        except Exception as e:
            return False, f"Installation failed: {str(e)}"
    
    def get_archive_list(self, plugin_name: str = None) -> List[Dict]:
        """
        Get list of available archives.
        
        Args:
            plugin_name: Optional plugin name to filter by
            
        Returns:
            List of archive information dictionaries
        """
        archives = []
        
        for archive_dir in self.archive_dir.iterdir():
            if not archive_dir.is_dir():
                continue
            
            metadata_file = archive_dir / "archive_metadata.json"
            if metadata_file.exists():
                try:
                    import json
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    if plugin_name and metadata.get('plugin_name') != plugin_name:
                        continue
                    
                    metadata['archive_path'] = str(archive_dir)
                    archives.append(metadata)
                except Exception:
                    pass
        
        return sorted(archives, key=lambda x: x.get('archived_date', ''), reverse=True)
