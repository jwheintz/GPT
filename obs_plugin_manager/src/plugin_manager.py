"""
Plugin Manager.
Handles plugin downloading, installation, archiving, and rollback.
"""

import os
import re
import json
import shutil
import hashlib
import logging
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, unquote

import requests

logger = logging.getLogger(__name__)


@dataclass
class DownloadProgress:
    """Progress information for downloads."""
    
    total_bytes: int
    downloaded_bytes: int
    percent: float
    speed_bps: float
    eta_seconds: float
    filename: str


@dataclass 
class InstallResult:
    """Result of a plugin installation."""
    
    success: bool
    message: str
    plugin_id: str
    version: str
    installed_files: List[str]
    archived_version: Optional[str] = None


class PluginManager:
    """Manages plugin downloads, installations, and rollbacks."""
    
    # Supported archive formats
    SUPPORTED_EXTENSIONS = ['.zip', '.7z', '.rar', '.exe']
    
    def __init__(self, config_manager=None):
        if config_manager is None:
            from .config import get_config
            config_manager = get_config()
        
        self.config = config_manager
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        dirs = [
            self.config.config.plugin_archive_path,
            self.config.config.download_temp_path,
        ]
        
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def _check_obs_not_running(self) -> None:
        """Ensure OBS is not running before write operations."""
        from .process_manager import get_process_manager
        pm = get_process_manager()
        pm.require_obs_not_running()
    
    def download_plugin(
        self,
        url: str,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
        plugin_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Download a plugin from URL.
        
        Args:
            url: URL to download from (can be GitHub release page).
            progress_callback: Callback for progress updates.
            plugin_id: Optional plugin ID for naming.
            
        Returns:
            Path to downloaded file, or None if failed.
        """
        try:
            # Resolve GitHub URLs to direct download links
            download_url = self._resolve_download_url(url)
            
            if not download_url:
                logger.error(f"Could not resolve download URL: {url}")
                return None
            
            logger.info(f"Downloading from: {download_url}")
            
            # Start download with streaming
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file info
            total_size = int(response.headers.get('content-length', 0))
            
            # Determine filename
            filename = self._get_filename_from_response(response, download_url, plugin_id)
            
            # Download to temp directory
            temp_path = Path(self.config.config.download_temp_path) / filename
            
            downloaded = 0
            start_time = datetime.now()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size:
                            elapsed = (datetime.now() - start_time).total_seconds()
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            eta = (total_size - downloaded) / speed if speed > 0 else 0
                            
                            progress = DownloadProgress(
                                total_bytes=total_size,
                                downloaded_bytes=downloaded,
                                percent=(downloaded / total_size) * 100,
                                speed_bps=speed,
                                eta_seconds=eta,
                                filename=filename
                            )
                            progress_callback(progress)
            
            logger.info(f"Downloaded to: {temp_path}")
            return str(temp_path)
        
        except requests.RequestException as e:
            logger.error(f"Download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def _resolve_download_url(self, url: str) -> Optional[str]:
        """Resolve URL to direct download link."""
        parsed = urlparse(url)
        
        # Already a direct download link
        if any(url.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
            return url
        
        # GitHub release page
        if 'github.com' in parsed.netloc:
            return self._resolve_github_url(url)
        
        # Try to fetch and find download link
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            content_type = response.headers.get('content-type', '')
            
            if 'application' in content_type:
                return url
        except Exception:
            pass
        
        return url
    
    def _resolve_github_url(self, url: str) -> Optional[str]:
        """Resolve GitHub URL to direct download link."""
        # Convert releases/latest to actual release URL
        if '/releases/latest' in url:
            try:
                # Get latest release info via API
                api_url = url.replace('github.com', 'api.github.com/repos')
                api_url = api_url.replace('/releases/latest', '/releases/latest')
                
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                
                release_data = response.json()
                assets = release_data.get('assets', [])
                
                # Find Windows 64-bit asset
                for asset in assets:
                    name = asset.get('name', '').lower()
                    
                    # Prefer Windows 64-bit
                    if any(x in name for x in ['win64', 'windows-x64', 'x64', 'windows64']):
                        if name.endswith('.zip') or name.endswith('.exe'):
                            return asset.get('browser_download_url')
                
                # Fall back to any zip file
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if name.endswith('.zip'):
                        return asset.get('browser_download_url')
                
                # Fall back to first asset
                if assets:
                    return assets[0].get('browser_download_url')
            
            except Exception as e:
                logger.warning(f"Failed to resolve GitHub URL: {e}")
        
        # Direct release download URL
        if '/releases/download/' in url:
            return url
        
        return url
    
    def _get_filename_from_response(
        self,
        response: requests.Response,
        url: str,
        plugin_id: Optional[str]
    ) -> str:
        """Extract filename from response or URL."""
        # Try content-disposition header
        cd = response.headers.get('content-disposition', '')
        if cd:
            match = re.findall(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', cd)
            if match:
                return unquote(match[0][0].strip('"\''))
        
        # Try URL path
        parsed = urlparse(url)
        path = unquote(parsed.path)
        if path:
            filename = os.path.basename(path)
            if filename and '.' in filename:
                return filename
        
        # Generate filename
        ext = '.zip'
        if plugin_id:
            return f"{plugin_id}{ext}"
        return f"plugin_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    
    def extract_plugin(self, archive_path: str, extract_to: Optional[str] = None) -> Optional[str]:
        """
        Extract a plugin archive.
        
        Args:
            archive_path: Path to archive file.
            extract_to: Directory to extract to. If None, uses temp directory.
            
        Returns:
            Path to extracted directory, or None if failed.
        """
        archive_path = Path(archive_path)
        
        if not archive_path.exists():
            logger.error(f"Archive not found: {archive_path}")
            return None
        
        if extract_to is None:
            extract_to = Path(self.config.config.download_temp_path) / archive_path.stem
        else:
            extract_to = Path(extract_to)
        
        extract_to.mkdir(parents=True, exist_ok=True)
        
        try:
            suffix = archive_path.suffix.lower()
            
            if suffix == '.zip':
                self._extract_zip(archive_path, extract_to)
            elif suffix == '.7z':
                self._extract_7z(archive_path, extract_to)
            elif suffix == '.rar':
                self._extract_rar(archive_path, extract_to)
            elif suffix == '.exe':
                # Some plugins come as self-extracting archives or installers
                # For now, just copy the exe
                shutil.copy(archive_path, extract_to)
            else:
                logger.error(f"Unsupported archive format: {suffix}")
                return None
            
            logger.info(f"Extracted to: {extract_to}")
            return str(extract_to)
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None
    
    def _extract_zip(self, archive_path: Path, extract_to: Path) -> None:
        """Extract ZIP archive."""
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(extract_to)
    
    def _extract_7z(self, archive_path: Path, extract_to: Path) -> None:
        """Extract 7z archive."""
        try:
            import py7zr
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(path=extract_to)
        except ImportError:
            logger.error("py7zr not installed. Install with: pip install py7zr")
            raise
    
    def _extract_rar(self, archive_path: Path, extract_to: Path) -> None:
        """Extract RAR archive."""
        try:
            import rarfile
            with rarfile.RarFile(archive_path, 'r') as rf:
                rf.extractall(extract_to)
        except ImportError:
            logger.error("rarfile not installed. Install with: pip install rarfile")
            raise
    
    def archive_current_plugin(
        self,
        plugin_id: str,
        version: str,
        dll_path: str,
        data_folder: Optional[str] = None
    ) -> Optional[str]:
        """
        Archive current plugin files for rollback.
        
        Args:
            plugin_id: Plugin identifier.
            version: Current version being archived.
            dll_path: Path to main DLL file.
            data_folder: Optional path to plugin data folder.
            
        Returns:
            Path to created archive, or None if failed.
        """
        try:
            # Create archive name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f"{plugin_id}_{version}_{timestamp}.zip"
            archive_path = Path(self.config.config.plugin_archive_path) / archive_name
            
            # Create archive
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add main DLL
                dll_path = Path(dll_path)
                if dll_path.exists():
                    zf.write(dll_path, dll_path.name)
                
                # Add data folder if exists
                if data_folder:
                    data_path = Path(data_folder)
                    if data_path.exists():
                        for item in data_path.rglob('*'):
                            if item.is_file():
                                arc_name = f"data/{item.relative_to(data_path)}"
                                zf.write(item, arc_name)
            
            # Record in database
            from .database import PluginDatabase
            db = PluginDatabase()
            
            file_hash = self._calculate_file_hash(archive_path)
            db.add_archive(plugin_id, version, str(archive_path), file_hash)
            
            # Clean up old archives
            max_archives = self.config.config.max_archive_versions
            old_archives = db.delete_old_archives(plugin_id, max_archives)
            
            for old_path in old_archives:
                try:
                    Path(old_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to delete old archive: {e}")
            
            logger.info(f"Archived plugin {plugin_id} v{version} to {archive_path}")
            return str(archive_path)
        
        except Exception as e:
            logger.error(f"Failed to archive plugin: {e}")
            return None
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file."""
        hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def install_plugin(
        self,
        plugin_id: str,
        source_path: str,
        version: str = "Unknown",
        archive_current: bool = True
    ) -> InstallResult:
        """
        Install a plugin from extracted source.
        
        Args:
            plugin_id: Plugin identifier.
            source_path: Path to extracted plugin files.
            version: Version being installed.
            archive_current: Whether to archive current version first.
            
        Returns:
            InstallResult with success status and details.
        """
        # Safety check - ensure OBS is not running
        self._check_obs_not_running()
        
        source_path = Path(source_path)
        if not source_path.exists():
            return InstallResult(
                success=False,
                message=f"Source path not found: {source_path}",
                plugin_id=plugin_id,
                version=version,
                installed_files=[]
            )
        
        # Get OBS installation info
        from .obs_scanner import OBSScanner
        scanner = OBSScanner(self.config)
        obs_info = scanner.scan_obs_installation()
        
        if not obs_info:
            return InstallResult(
                success=False,
                message="OBS installation not found",
                plugin_id=plugin_id,
                version=version,
                installed_files=[]
            )
        
        try:
            # Find plugin files in source
            plugin_files = self._find_plugin_files(source_path)
            
            if not plugin_files['dlls']:
                return InstallResult(
                    success=False,
                    message="No DLL files found in plugin archive",
                    plugin_id=plugin_id,
                    version=version,
                    installed_files=[]
                )
            
            archived_version = None
            
            # Archive current version if requested
            if archive_current:
                current_plugins = scanner.scan_plugins()
                for current in current_plugins:
                    if current.matched_catalog_id == plugin_id:
                        archived_version = current.version
                        self.archive_current_plugin(
                            plugin_id,
                            current.version,
                            current.dll_path,
                            current.data_folder
                        )
                        break
            
            installed_files = []
            
            # Install DLLs to plugin directory
            plugins_dir = Path(obs_info.plugins_path)
            plugins_dir.mkdir(parents=True, exist_ok=True)
            
            for dll_src in plugin_files['dlls']:
                dll_dst = plugins_dir / dll_src.name
                shutil.copy2(dll_src, dll_dst)
                installed_files.append(str(dll_dst))
                logger.info(f"Installed DLL: {dll_dst}")
            
            # Install data files
            data_dir = Path(obs_info.data_path)
            
            for data_src in plugin_files['data_folders']:
                # Determine target folder name
                folder_name = data_src.name
                data_dst = data_dir / folder_name
                
                if data_dst.exists():
                    shutil.rmtree(data_dst)
                
                shutil.copytree(data_src, data_dst)
                installed_files.append(str(data_dst))
                logger.info(f"Installed data folder: {data_dst}")
            
            # Update installed plugins database
            from .database import PluginDatabase, InstalledPlugin
            db = PluginDatabase()
            
            if plugin_files['dlls']:
                main_dll = plugin_files['dlls'][0]
                db.add_installed_plugin(InstalledPlugin(
                    plugin_id=plugin_id,
                    name=plugin_id,
                    dll_path=str(plugins_dir / main_dll.name),
                    version=version,
                    install_date=datetime.now().isoformat(),
                    file_hash=self._calculate_file_hash(main_dll),
                    file_size=main_dll.stat().st_size
                ))
            
            return InstallResult(
                success=True,
                message=f"Plugin {plugin_id} installed successfully",
                plugin_id=plugin_id,
                version=version,
                installed_files=installed_files,
                archived_version=archived_version
            )
        
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return InstallResult(
                success=False,
                message=f"Installation failed: {e}",
                plugin_id=plugin_id,
                version=version,
                installed_files=[]
            )
    
    def _find_plugin_files(self, source_path: Path) -> Dict[str, List[Path]]:
        """Find plugin files in extracted archive."""
        result = {
            'dlls': [],
            'data_folders': [],
            'other': []
        }
        
        # Search for DLLs
        for dll in source_path.rglob('*.dll'):
            # Filter out system DLLs
            if not any(x in dll.name.lower() for x in ['msvc', 'vcruntime', 'api-ms-']):
                result['dlls'].append(dll)
        
        # Search for data folders (usually in obs-plugins/data or data/obs-plugins)
        for folder in source_path.rglob('*'):
            if folder.is_dir():
                folder_name = folder.name.lower()
                parent_name = folder.parent.name.lower() if folder.parent != source_path else ''
                
                # Common data folder patterns
                if parent_name in ['data', 'obs-plugins'] or 'data' in folder_name:
                    if any(folder.iterdir()):  # Has contents
                        result['data_folders'].append(folder)
        
        return result
    
    def rollback_plugin(self, plugin_id: str, version: Optional[str] = None) -> InstallResult:
        """
        Rollback plugin to a previous archived version.
        
        Args:
            plugin_id: Plugin identifier.
            version: Specific version to rollback to. If None, uses most recent archive.
            
        Returns:
            InstallResult with status.
        """
        # Safety check
        self._check_obs_not_running()
        
        try:
            from .database import PluginDatabase
            db = PluginDatabase()
            
            # Get archives for this plugin
            archives = db.get_archives(plugin_id)
            
            if not archives:
                return InstallResult(
                    success=False,
                    message=f"No archived versions found for {plugin_id}",
                    plugin_id=plugin_id,
                    version="",
                    installed_files=[]
                )
            
            # Find the requested version
            archive = None
            if version:
                for a in archives:
                    if a['version'] == version:
                        archive = a
                        break
            else:
                # Use most recent
                archive = archives[0]
            
            if not archive:
                return InstallResult(
                    success=False,
                    message=f"Archive version {version} not found for {plugin_id}",
                    plugin_id=plugin_id,
                    version=version or "",
                    installed_files=[]
                )
            
            archive_path = Path(archive['archive_path'])
            
            if not archive_path.exists():
                return InstallResult(
                    success=False,
                    message=f"Archive file not found: {archive_path}",
                    plugin_id=plugin_id,
                    version=archive['version'],
                    installed_files=[]
                )
            
            # Extract archive to temp
            extract_dir = self.extract_plugin(str(archive_path))
            
            if not extract_dir:
                return InstallResult(
                    success=False,
                    message="Failed to extract archive",
                    plugin_id=plugin_id,
                    version=archive['version'],
                    installed_files=[]
                )
            
            # Install without archiving current (we're rolling back)
            result = self.install_plugin(
                plugin_id,
                extract_dir,
                archive['version'],
                archive_current=False
            )
            
            # Clean up temp
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            if result.success:
                result.message = f"Rolled back {plugin_id} to version {archive['version']}"
            
            return result
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return InstallResult(
                success=False,
                message=f"Rollback failed: {e}",
                plugin_id=plugin_id,
                version=version or "",
                installed_files=[]
            )
    
    def uninstall_plugin(self, plugin_id: str, archive_first: bool = True) -> InstallResult:
        """
        Uninstall a plugin.
        
        Args:
            plugin_id: Plugin identifier.
            archive_first: Whether to archive before uninstalling.
            
        Returns:
            InstallResult with status.
        """
        # Safety check
        self._check_obs_not_running()
        
        try:
            from .obs_scanner import OBSScanner
            scanner = OBSScanner(self.config)
            
            # Find the installed plugin
            plugins = scanner.scan_plugins()
            target_plugin = None
            
            for plugin in plugins:
                if plugin.matched_catalog_id == plugin_id:
                    target_plugin = plugin
                    break
            
            if not target_plugin:
                return InstallResult(
                    success=False,
                    message=f"Plugin {plugin_id} is not installed",
                    plugin_id=plugin_id,
                    version="",
                    installed_files=[]
                )
            
            # Archive first if requested
            if archive_first:
                self.archive_current_plugin(
                    plugin_id,
                    target_plugin.version,
                    target_plugin.dll_path,
                    target_plugin.data_folder
                )
            
            removed_files = []
            
            # Remove DLL
            dll_path = Path(target_plugin.dll_path)
            if dll_path.exists():
                dll_path.unlink()
                removed_files.append(str(dll_path))
            
            # Remove data folder
            if target_plugin.data_folder:
                data_path = Path(target_plugin.data_folder)
                if data_path.exists():
                    shutil.rmtree(data_path)
                    removed_files.append(str(data_path))
            
            # Update database
            from .database import PluginDatabase
            db = PluginDatabase()
            db.remove_installed_plugin(plugin_id)
            
            return InstallResult(
                success=True,
                message=f"Plugin {plugin_id} uninstalled successfully",
                plugin_id=plugin_id,
                version=target_plugin.version,
                installed_files=removed_files
            )
        
        except Exception as e:
            logger.error(f"Uninstall failed: {e}")
            return InstallResult(
                success=False,
                message=f"Uninstall failed: {e}",
                plugin_id=plugin_id,
                version="",
                installed_files=[]
            )
    
    def get_archive_info(self, plugin_id: str) -> List[Dict[str, Any]]:
        """Get information about archived versions of a plugin."""
        from .database import PluginDatabase
        db = PluginDatabase()
        
        archives = db.get_archives(plugin_id)
        
        result = []
        for archive in archives:
            archive_path = Path(archive['archive_path'])
            
            info = {
                'version': archive['version'],
                'archive_date': archive['archive_date'],
                'archive_path': archive['archive_path'],
                'file_hash': archive.get('file_hash', ''),
                'exists': archive_path.exists(),
            }
            
            if archive_path.exists():
                info['file_size'] = archive_path.stat().st_size
                info['file_size_formatted'] = self._format_size(info['file_size'])
            
            result.append(info)
        
        return result
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def cleanup_temp_files(self) -> int:
        """Clean up temporary download files. Returns count of deleted files."""
        temp_dir = Path(self.config.config.download_temp_path)
        
        if not temp_dir.exists():
            return 0
        
        count = 0
        for item in temp_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete temp item {item}: {e}")
        
        return count
    
    def download_and_install(
        self,
        plugin_id: str,
        download_url: str,
        version: str = "Unknown",
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> InstallResult:
        """
        Download and install a plugin in one operation.
        
        Args:
            plugin_id: Plugin identifier.
            download_url: URL to download from.
            version: Version being installed.
            progress_callback: Optional callback for download progress.
            
        Returns:
            InstallResult with status.
        """
        # Download
        downloaded_path = self.download_plugin(download_url, progress_callback, plugin_id)
        
        if not downloaded_path:
            return InstallResult(
                success=False,
                message="Download failed",
                plugin_id=plugin_id,
                version=version,
                installed_files=[]
            )
        
        try:
            # Extract
            extracted_path = self.extract_plugin(downloaded_path)
            
            if not extracted_path:
                return InstallResult(
                    success=False,
                    message="Extraction failed",
                    plugin_id=plugin_id,
                    version=version,
                    installed_files=[]
                )
            
            # Install
            result = self.install_plugin(plugin_id, extracted_path, version)
            
            # Cleanup
            Path(downloaded_path).unlink(missing_ok=True)
            shutil.rmtree(extracted_path, ignore_errors=True)
            
            return result
        
        except Exception as e:
            # Cleanup on error
            Path(downloaded_path).unlink(missing_ok=True)
            
            return InstallResult(
                success=False,
                message=f"Installation failed: {e}",
                plugin_id=plugin_id,
                version=version,
                installed_files=[]
            )


# Global instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global PluginManager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
