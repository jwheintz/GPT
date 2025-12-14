import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class PluginDatabase:
    def __init__(self, db_path: str = "obs_manager/data/plugins.json"):
        self.db_path = db_path
        self.plugins = self._load_db()

    def _load_db(self) -> Dict:
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {"last_updated": None, "plugins": {}}

    def save_db(self):
        self.plugins["last_updated"] = datetime.now().isoformat()
        with open(self.db_path, 'w') as f:
            json.dump(self.plugins, f, indent=4)

    def add_plugin(self, name: str, version: str, download_url: str, description: str = "", files: List[str] = []):
        self.plugins["plugins"][name] = {
            "version": version,
            "download_url": download_url,
            "description": description,
            "files": files,  # Expected file paths relative to OBS root
            "last_checked": datetime.now().isoformat()
        }
        self.save_db()

    def get_plugin(self, name: str) -> Optional[Dict]:
        return self.plugins["plugins"].get(name)

    def list_plugins(self) -> List[str]:
        return list(self.plugins["plugins"].keys())

    # Mock method to simulate fetching from an external resource
    def refresh_from_remote(self):
        # In a real app, this would fetch from a URL
        # For now, we'll populate with some known popular plugins
        popular_plugins = {
            "obs-websocket": {
                "version": "5.0.1",
                "download_url": "https://github.com/obsproject/obs-websocket/releases/download/5.0.1/obs-websocket-5.0.1-Windows.zip",
                "description": "Remote control OBS Studio from WebSockets",
                "files": ["obs-plugins/64bit/obs-websocket.dll", "data/obs-plugins/obs-websocket/"]
            },
            "move-transition": {
                "version": "2.9.0",
                "download_url": "https://obsproject.com/forum/resources/move-transition.913/",
                "description": "Move sources to a new position during a transition",
                "files": ["obs-plugins/64bit/move-transition.dll", "data/obs-plugins/move-transition/"]
            }
        }
        for name, data in popular_plugins.items():
            self.add_plugin(name, data["version"], data["download_url"], data["description"], data["files"])
