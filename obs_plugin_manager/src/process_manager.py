"""
OBS Process Manager.
Handles detection, monitoring, and termination of OBS Studio process.
"""

import os
import time
import logging
import subprocess
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil not available, process management will be limited")


@dataclass
class OBSProcess:
    """Information about a running OBS process."""
    
    pid: int
    name: str
    exe_path: str
    create_time: float
    status: str
    memory_mb: float
    cpu_percent: float


class ProcessManager:
    """Manages OBS Studio process detection and control."""
    
    # OBS process names to look for
    OBS_PROCESS_NAMES = [
        'obs64.exe',
        'obs32.exe',
        'obs.exe',
        'obs-studio.exe',
    ]
    
    def __init__(self):
        self._obs_process_cache: Optional[OBSProcess] = None
        self._cache_time: float = 0
        self._cache_ttl: float = 1.0  # Cache TTL in seconds
    
    def is_obs_running(self) -> bool:
        """
        Check if OBS Studio is currently running.
        
        Returns:
            True if OBS is running, False otherwise.
        """
        process = self.get_obs_process()
        return process is not None
    
    def get_obs_process(self, use_cache: bool = True) -> Optional[OBSProcess]:
        """
        Get information about the running OBS process.
        
        Args:
            use_cache: Whether to use cached result if available.
            
        Returns:
            OBSProcess info if OBS is running, None otherwise.
        """
        # Check cache
        if use_cache and self._obs_process_cache:
            if time.time() - self._cache_time < self._cache_ttl:
                # Verify process still exists
                try:
                    if HAS_PSUTIL:
                        proc = psutil.Process(self._obs_process_cache.pid)
                        if proc.is_running():
                            return self._obs_process_cache
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        # Find OBS process
        process = self._find_obs_process()
        
        # Update cache
        self._obs_process_cache = process
        self._cache_time = time.time()
        
        return process
    
    def _find_obs_process(self) -> Optional[OBSProcess]:
        """Find OBS process using psutil or fallback method."""
        if HAS_PSUTIL:
            return self._find_obs_process_psutil()
        else:
            return self._find_obs_process_fallback()
    
    def _find_obs_process_psutil(self) -> Optional[OBSProcess]:
        """Find OBS process using psutil."""
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'status']):
            try:
                proc_name = proc.info['name'].lower()
                
                if proc_name in [n.lower() for n in self.OBS_PROCESS_NAMES]:
                    # Get additional info
                    memory_info = proc.memory_info()
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    
                    return OBSProcess(
                        pid=proc.info['pid'],
                        name=proc.info['name'],
                        exe_path=proc.info['exe'] or '',
                        create_time=proc.info['create_time'],
                        status=proc.info['status'],
                        memory_mb=memory_info.rss / (1024 * 1024),
                        cpu_percent=cpu_percent
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return None
    
    def _find_obs_process_fallback(self) -> Optional[OBSProcess]:
        """Find OBS process using tasklist (Windows fallback)."""
        try:
            # Use tasklist command on Windows
            result = subprocess.run(
                ['tasklist', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                # Parse CSV line
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    proc_name = parts[0].lower()
                    
                    if proc_name in [n.lower() for n in self.OBS_PROCESS_NAMES]:
                        pid = int(parts[1])
                        
                        return OBSProcess(
                            pid=pid,
                            name=proc_name,
                            exe_path='',
                            create_time=0,
                            status='running',
                            memory_mb=0,
                            cpu_percent=0
                        )
        
        except Exception as e:
            logger.error(f"Failed to find OBS process (fallback): {e}")
        
        return None
    
    def kill_obs(self, force: bool = False, timeout: float = 10.0) -> bool:
        """
        Terminate the OBS Studio process.
        
        Args:
            force: If True, forcefully kill the process immediately.
                   If False, try graceful termination first.
            timeout: Time to wait for graceful termination before forcing.
            
        Returns:
            True if OBS was terminated successfully, False otherwise.
        """
        process = self.get_obs_process(use_cache=False)
        
        if not process:
            logger.info("OBS is not running, nothing to kill")
            return True
        
        logger.info(f"Attempting to terminate OBS (PID: {process.pid}, force={force})")
        
        if HAS_PSUTIL:
            return self._kill_obs_psutil(process.pid, force, timeout)
        else:
            return self._kill_obs_fallback(process.pid, force)
    
    def _kill_obs_psutil(self, pid: int, force: bool, timeout: float) -> bool:
        """Kill OBS process using psutil."""
        try:
            proc = psutil.Process(pid)
            
            if force:
                # Force kill immediately
                proc.kill()
                logger.info(f"Forcefully killed OBS (PID: {pid})")
                return True
            
            # Try graceful termination first
            proc.terminate()
            
            try:
                proc.wait(timeout=timeout)
                logger.info(f"OBS terminated gracefully (PID: {pid})")
                return True
            except psutil.TimeoutExpired:
                # Force kill after timeout
                logger.warning(f"OBS did not terminate gracefully, forcing kill")
                proc.kill()
                proc.wait(timeout=5)
                logger.info(f"OBS force killed after timeout (PID: {pid})")
                return True
        
        except psutil.NoSuchProcess:
            logger.info(f"OBS process already terminated (PID: {pid})")
            return True
        except psutil.AccessDenied as e:
            logger.error(f"Access denied killing OBS: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to kill OBS: {e}")
            return False
    
    def _kill_obs_fallback(self, pid: int, force: bool) -> bool:
        """Kill OBS process using taskkill (Windows fallback)."""
        try:
            # Use taskkill command on Windows
            args = ['taskkill']
            
            if force:
                args.append('/F')
            
            args.extend(['/PID', str(pid)])
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"OBS terminated via taskkill (PID: {pid})")
                return True
            else:
                logger.error(f"taskkill failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("taskkill timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to kill OBS (fallback): {e}")
            return False
    
    def wait_for_obs_exit(self, timeout: float = 30.0) -> bool:
        """
        Wait for OBS to exit.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            True if OBS has exited, False if timeout reached.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_obs_running():
                return True
            time.sleep(0.5)
        
        return False
    
    def start_obs(self, obs_path: Optional[str] = None) -> bool:
        """
        Start OBS Studio.
        
        Args:
            obs_path: Path to OBS executable. If None, tries to find it.
            
        Returns:
            True if OBS was started, False otherwise.
        """
        if self.is_obs_running():
            logger.warning("OBS is already running")
            return False
        
        # Find OBS path if not provided
        if not obs_path:
            from .config import get_config
            config = get_config()
            obs_info = config.detect_obs_installation()
            
            if obs_info:
                obs_path = os.path.join(obs_info, "bin", "64bit", "obs64.exe")
        
        if not obs_path or not os.path.exists(obs_path):
            logger.error("OBS executable not found")
            return False
        
        try:
            # Start OBS in detached mode
            subprocess.Popen(
                [obs_path],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info(f"Started OBS: {obs_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start OBS: {e}")
            return False
    
    def get_all_obs_processes(self) -> List[OBSProcess]:
        """Get all running OBS-related processes."""
        processes = []
        
        if not HAS_PSUTIL:
            process = self.get_obs_process()
            if process:
                processes.append(process)
            return processes
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'status']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Check for OBS processes and related processes
                if any(obs_name.lower() in proc_name for obs_name in self.OBS_PROCESS_NAMES):
                    memory_info = proc.memory_info()
                    
                    processes.append(OBSProcess(
                        pid=proc.info['pid'],
                        name=proc.info['name'],
                        exe_path=proc.info['exe'] or '',
                        create_time=proc.info['create_time'],
                        status=proc.info['status'],
                        memory_mb=memory_info.rss / (1024 * 1024),
                        cpu_percent=proc.cpu_percent(interval=0.1)
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get detailed information about OBS process status."""
        process = self.get_obs_process(use_cache=False)
        
        if not process:
            return {
                "running": False,
                "message": "OBS Studio is not running"
            }
        
        # Calculate uptime
        uptime_seconds = time.time() - process.create_time if process.create_time else 0
        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        return {
            "running": True,
            "pid": process.pid,
            "name": process.name,
            "exe_path": process.exe_path,
            "status": process.status,
            "memory_mb": round(process.memory_mb, 1),
            "cpu_percent": round(process.cpu_percent, 1),
            "uptime": uptime_str,
            "message": f"OBS is running (PID: {process.pid})"
        }
    
    def require_obs_not_running(self) -> bool:
        """
        Check that OBS is not running before performing write operations.
        Raises an exception if OBS is running.
        
        Returns:
            True if OBS is not running.
            
        Raises:
            RuntimeError: If OBS is running.
        """
        if self.is_obs_running():
            raise RuntimeError(
                "OBS Studio is currently running. "
                "Please close OBS before modifying plugins."
            )
        return True


# Global instance
_process_manager: Optional[ProcessManager] = None


def get_process_manager() -> ProcessManager:
    """Get the global ProcessManager instance."""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager
