import os
import shutil
import zipfile
import requests
import glob
from datetime import datetime
from typing import List, Optional
from .database import PluginDatabase
from .process import ProcessManager

class PluginManager:
    def __init__(self, obs_path: str, db: PluginDatabase, backup_path: str = "obs_manager/backups"):
        self.obs_path = obs_path
        self.db = db
        self.backup_path = backup_path
        self.process_manager = ProcessManager()
        
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)

    def download_plugin(self, url: str, dest_path: str):
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")

    def backup_plugin(self, plugin_name: str, files: List[str]):
        """Backs up existing plugin files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.backup_path, plugin_name, timestamp)
        
        files_backed_up = False
        for file_rel in files:
            src = os.path.join(self.obs_path, file_rel)
            if os.path.exists(src):
                dst = os.path.join(backup_dir, file_rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    files_backed_up = True
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    files_backed_up = True

        if files_backed_up:
            print(f"Backup created at {backup_dir}")
            self._rotate_backups(plugin_name)
        else:
            # If no files existed, just remove the empty backup dir
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

    def _rotate_backups(self, plugin_name: str, keep: int = 2):
        plugin_backup_dir = os.path.join(self.backup_path, plugin_name)
        if not os.path.exists(plugin_backup_dir):
            return

        backups = sorted([os.path.join(plugin_backup_dir, d) for d in os.listdir(plugin_backup_dir) if os.path.isdir(os.path.join(plugin_backup_dir, d))])
        
        while len(backups) > keep:
            oldest = backups.pop(0)
            print(f"Removing old backup: {oldest}")
            shutil.rmtree(oldest)

    def install_plugin(self, plugin_name: str):
        # 1. Check Safety
        if self.process_manager.is_obs_running():
            raise Exception("OBS is running. Cannot install plugin.")

        plugin_data = self.db.get_plugin(plugin_name)
        if not plugin_data:
            raise Exception(f"Plugin {plugin_name} not found in database.")

        # 2. Download
        download_url = plugin_data["download_url"]
        temp_zip = os.path.join(self.backup_path, f"{plugin_name}_temp.zip")
        try:
            self.download_plugin(download_url, temp_zip)

            # 3. Backup Existing
            print("Backing up existing files...")
            self.backup_plugin(plugin_name, plugin_data["files"])

            # 4. Install (Extract)
            print("Installing...")
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                # We need to be careful about structure.
                # Assuming zip root corresponds to OBS root or contains 'obs-plugins' folder.
                # This logic might need refinement based on specific zip structures.
                zip_ref.extractall(self.obs_path)
            
            print(f"Successfully installed {plugin_name}")

        finally:
            if os.path.exists(temp_zip):
                os.remove(temp_zip)

    def rollback_plugin(self, plugin_name: str):
         # 1. Check Safety
        if self.process_manager.is_obs_running():
            raise Exception("OBS is running. Cannot rollback plugin.")

        plugin_backup_dir = os.path.join(self.backup_path, plugin_name)
        if not os.path.exists(plugin_backup_dir):
            raise Exception("No backups found for this plugin.")

        backups = sorted([os.path.join(plugin_backup_dir, d) for d in os.listdir(plugin_backup_dir) if os.path.isdir(os.path.join(plugin_backup_dir, d))])
        
        if not backups:
             raise Exception("No backups found for this plugin.")

        latest_backup = backups[-1]
        print(f"Rolling back to {latest_backup}...")

        # Copy back
        # Note: This simply copies backup files OVER current files. 
        # It does not delete files that were added in the newer version but don't exist in backup.
        # For a cleaner rollback, we might want to delete tracked files first, but that's risky.
        
        for root, dirs, files in os.walk(latest_backup):
            rel_path = os.path.relpath(root, latest_backup)
            dest_dir = os.path.join(self.obs_path, rel_path)
            
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir, file)
                shutil.copy2(src_file, dst_file)

        print("Rollback complete.")

