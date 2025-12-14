import os
import hashlib
from typing import Dict, List, Optional
from .database import PluginDatabase

class OBSScanner:
    def __init__(self, obs_path: str, db: PluginDatabase):
        self.obs_path = obs_path
        self.db = db
        # Default Windows path if not provided or testing on Linux
        if not self.obs_path:
            self.obs_path = r"C:\Program Files\obs-studio" 

    def _get_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return ""

    def scan_plugins(self) -> Dict[str, Dict]:
        """
        Scans the OBS directory for known plugins from the database.
        Returns a dictionary of installed plugins and their detected status.
        """
        installed_plugins = {}
        known_plugins = self.db.plugins.get("plugins", {})

        for name, data in known_plugins.items():
            # Check if the main file exists
            # We assume the first file in 'files' is the main indicator (e.g., the DLL)
            if not data.get("files"):
                continue

            main_file_rel = data["files"][0]
            full_path = os.path.join(self.obs_path, main_file_rel)

            if os.path.exists(full_path):
                # Plugin detected
                # To determine version, we would ideally hash it and compare with known hashes in DB.
                # Since we don't have a hash DB yet, we'll mark it as 'unknown version' or 'detected'
                # For this prototype, we'll assume if it's there, we detected it.
                # Future improvement: Store hashes in DB.
                
                installed_plugins[name] = {
                    "installed": True,
                    "path": full_path,
                    "version": "detected" # Placeholder for version detection logic
                }
            else:
                 installed_plugins[name] = {
                    "installed": False,
                    "version": None
                }
        
        return installed_plugins
