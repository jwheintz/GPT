"""
OBS Process Manager - handles OBS detection, status checking, and process management.
"""

import psutil
import winreg
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple


class OBSManager:
    """Manages OBS Studio process and installation detection."""
    
    # Common OBS executable names
    OBS_PROCESS_NAMES = ["obs64.exe", "obs32.exe", "obs.exe"]
    
    # Common registry paths for OBS installation
    REGISTRY_PATHS = [
        (winreg.HKEY_CURRENT_USER, r"Software\OBS Studio"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\OBS Studio"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\OBS Studio"),
    ]
    
    # Common installation directories
    COMMON_INSTALL_DIRS = [
        Path(r"C:\Program Files\obs-studio"),
        Path(r"C:\Program Files (x86)\obs-studio"),
    ]
    
    def __init__(self):
        """Initialize the OBS Manager."""
        self.obs_path = None
        self.plugin_dirs = []
        self._detect_obs_installation()
    
    def _detect_obs_installation(self) -> bool:
        """Detect OBS Studio installation path."""
        # Try registry first
        for hkey, subkey in self.REGISTRY_PATHS:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    try:
                        path = winreg.QueryValueEx(key, "")[0]
                        obs_path = Path(path)
                        if obs_path.exists():
                            self.obs_path = obs_path
                            self._detect_plugin_directories()
                            return True
                    except WindowsError:
                        pass
            except WindowsError:
                continue
        
        # Try common directories
        for install_dir in self.COMMON_INSTALL_DIRS:
            if install_dir.exists():
                # Check for obs executable
                for exe_name in self.OBS_PROCESS_NAMES:
                    exe_path = install_dir / "bin" / "64bit" / exe_name
                    if exe_path.exists():
                        self.obs_path = install_dir
                        self._detect_plugin_directories()
                        return True
                    
                    exe_path = install_dir / "bin" / exe_name
                    if exe_path.exists():
                        self.obs_path = install_dir
                        self._detect_plugin_directories()
                        return True
        
        # Try to find running OBS process
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] in self.OBS_PROCESS_NAMES:
                    exe_path = Path(proc.info['exe'])
                    self.obs_path = exe_path.parent.parent
                    self._detect_plugin_directories()
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        
        return False
    
    def _detect_plugin_directories(self):
        """Detect plugin directories for OBS installation."""
        if not self.obs_path:
            return
        
        # Common plugin locations
        possible_dirs = [
            self.obs_path / "obs-plugins" / "64bit",
            self.obs_path / "obs-plugins",
            self.obs_path / "plugins",
            Path.home() / "AppData" / "Roaming" / "obs-studio" / "obs-plugins" / "64bit",
            Path.home() / "AppData" / "Roaming" / "obs-studio" / "obs-plugins",
        ]
        
        self.plugin_dirs = [d for d in possible_dirs if d.exists()]
    
    def is_obs_installed(self) -> bool:
        """Check if OBS Studio is installed."""
        return self.obs_path is not None
    
    def get_obs_path(self) -> Optional[Path]:
        """Get the OBS installation path."""
        return self.obs_path
    
    def get_plugin_directories(self) -> List[Path]:
        """Get list of plugin directories."""
        return self.plugin_dirs
    
    def is_obs_running(self) -> bool:
        """Check if OBS is currently running."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.OBS_PROCESS_NAMES:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def get_obs_processes(self) -> List[psutil.Process]:
        """Get all running OBS processes."""
        obs_processes = []
        for proc in psutil.process_iter(['name', 'pid', 'exe']):
            try:
                if proc.info['name'] in self.OBS_PROCESS_NAMES:
                    obs_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return obs_processes
    
    def kill_obs(self, force: bool = False) -> Tuple[bool, str]:
        """
        Kill all OBS processes.
        
        Args:
            force: If True, use forceful termination
            
        Returns:
            Tuple of (success, message)
        """
        processes = self.get_obs_processes()
        
        if not processes:
            return True, "No OBS processes running"
        
        killed = []
        failed = []
        
        for proc in processes:
            try:
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                
                # Wait for process to end (max 5 seconds)
                proc.wait(timeout=5)
                killed.append(proc.pid)
            except psutil.TimeoutExpired:
                # Try force kill if terminate didn't work
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                    killed.append(proc.pid)
                except Exception as e:
                    failed.append(f"PID {proc.pid}: {str(e)}")
            except Exception as e:
                failed.append(f"PID {proc.pid}: {str(e)}")
        
        if failed:
            return False, f"Killed {len(killed)} processes, failed: {', '.join(failed)}"
        else:
            return True, f"Successfully killed {len(killed)} OBS process(es)"
    
    def get_obs_version(self) -> Optional[str]:
        """Try to get OBS version."""
        if not self.obs_path:
            return None
        
        # Try to find version file
        version_file = self.obs_path / "data" / "obs-studio" / "version.txt"
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except Exception:
                pass
        
        # Try to get version from executable
        for exe_name in self.OBS_PROCESS_NAMES:
            exe_path = self.obs_path / "bin" / "64bit" / exe_name
            if not exe_path.exists():
                exe_path = self.obs_path / "bin" / exe_name
            
            if exe_path.exists():
                try:
                    # Try using PowerShell to get file version
                    result = subprocess.run(
                        ['powershell', '-Command', 
                         f'(Get-Item "{exe_path}").VersionInfo.FileVersion'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except Exception:
                    pass
        
        return None
    
    def refresh_installation_info(self) -> bool:
        """Re-detect OBS installation."""
        self.obs_path = None
        self.plugin_dirs = []
        return self._detect_obs_installation()
