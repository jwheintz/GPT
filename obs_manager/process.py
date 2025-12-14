import psutil
import os
import sys

class ProcessManager:
    def __init__(self):
        self.obs_process_name = "obs64.exe" if os.name == 'nt' else "obs"

    def is_obs_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if self.obs_process_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def kill_obs(self) -> bool:
        killed = False
        for proc in psutil.process_iter(['name']):
            try:
                if self.obs_process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return killed

    def ensure_obs_closed(self):
        if self.is_obs_running():
            print("OBS is running. Attempting to close...")
            if self.kill_obs():
                print("OBS process terminated.")
            else:
                raise Exception("Failed to close OBS. Please close it manually.")
