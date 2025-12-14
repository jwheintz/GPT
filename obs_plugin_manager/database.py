"""
Database module for managing plugin metadata and installation history.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from .logger import get_logger


class PluginDatabase:
    """Manages the SQLite database for plugin information."""
    
    def __init__(self, db_path: str = "obs_plugins.db"):
        """Initialize the database connection."""
        self.logger = get_logger(__name__)
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
        self.logger.info(f"Database initialized: {db_path}")
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.logger.debug(f"Database connection established: {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        # Plugin catalog table (known plugins)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                description TEXT,
                author TEXT,
                category TEXT,
                download_url TEXT,
                latest_version TEXT,
                homepage_url TEXT,
                is_recommended BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Installed plugins table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS installed_plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                version TEXT NOT NULL,
                install_path TEXT NOT NULL,
                install_date TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (plugin_name) REFERENCES plugin_catalog(name)
            )
        """)
        
        # Plugin archives table (for rollback)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_archives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                version TEXT NOT NULL,
                archive_path TEXT NOT NULL,
                archived_date TIMESTAMP NOT NULL,
                file_count INTEGER,
                total_size INTEGER,
                is_stable BOOLEAN DEFAULT 0,
                marked_stable_date TIMESTAMP,
                FOREIGN KEY (plugin_name) REFERENCES plugin_catalog(name)
            )
        """)
        
        # Installation history table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS installation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                action TEXT NOT NULL,
                version TEXT,
                timestamp TIMESTAMP NOT NULL,
                success BOOLEAN,
                notes TEXT
            )
        """)
        
        self.conn.commit()
    
    def add_plugin_to_catalog(self, name: str, display_name: str, description: str = "",
                             author: str = "", category: str = "", download_url: str = "",
                             latest_version: str = "", homepage_url: str = "",
                             is_recommended: bool = False, metadata: Dict = None) -> bool:
        """Add or update a plugin in the catalog."""
        try:
            metadata_json = json.dumps(metadata) if metadata else "{}"
            self.cursor.execute("""
                INSERT OR REPLACE INTO plugin_catalog 
                (name, display_name, description, author, category, download_url, 
                 latest_version, homepage_url, is_recommended, last_updated, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, display_name, description, author, category, download_url,
                  latest_version, homepage_url, is_recommended, datetime.now(), metadata_json))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding plugin to catalog: {e}")
            return False
    
    def get_catalog_plugins(self, category: str = None, recommended_only: bool = False) -> List[Dict]:
        """Retrieve plugins from the catalog."""
        query = "SELECT * FROM plugin_catalog WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if recommended_only:
            query += " AND is_recommended = 1"
        
        query += " ORDER BY display_name"
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        plugins = []
        for row in rows:
            plugin = dict(row)
            if plugin['metadata']:
                plugin['metadata'] = json.loads(plugin['metadata'])
            plugins.append(plugin)
        
        return plugins
    
    def get_plugin_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific plugin from the catalog."""
        self.cursor.execute("SELECT * FROM plugin_catalog WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        
        if row:
            plugin = dict(row)
            if plugin['metadata']:
                plugin['metadata'] = json.loads(plugin['metadata'])
            return plugin
        return None
    
    def add_installed_plugin(self, plugin_name: str, version: str, install_path: str) -> bool:
        """Record a newly installed plugin."""
        try:
            self.cursor.execute("""
                INSERT INTO installed_plugins 
                (plugin_name, version, install_path, install_date, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (plugin_name, version, install_path, datetime.now()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording installed plugin: {e}")
            return False
    
    def update_installed_plugin(self, plugin_name: str, version: str, install_path: str) -> bool:
        """Update an installed plugin's version."""
        try:
            # Deactivate old version
            self.cursor.execute("""
                UPDATE installed_plugins 
                SET is_active = 0 
                WHERE plugin_name = ? AND is_active = 1
            """, (plugin_name,))
            
            # Add new version
            self.add_installed_plugin(plugin_name, version, install_path)
            return True
        except sqlite3.Error as e:
            print(f"Error updating installed plugin: {e}")
            return False
    
    def get_installed_plugins(self, active_only: bool = True) -> List[Dict]:
        """Retrieve installed plugins."""
        query = "SELECT * FROM installed_plugins"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY plugin_name"
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_installed_plugin(self, plugin_name: str) -> Optional[Dict]:
        """Get a specific installed plugin."""
        self.cursor.execute("""
            SELECT * FROM installed_plugins 
            WHERE plugin_name = ? AND is_active = 1
        """, (plugin_name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def add_archive(self, plugin_name: str, version: str, archive_path: str,
                   file_count: int = 0, total_size: int = 0) -> bool:
        """Record a plugin archive for rollback."""
        try:
            self.cursor.execute("""
                INSERT INTO plugin_archives 
                (plugin_name, version, archive_path, archived_date, file_count, total_size)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (plugin_name, version, archive_path, datetime.now(), file_count, total_size))
            self.conn.commit()
            
            # Keep only last 2 archives per plugin
            self._cleanup_old_archives(plugin_name)
            return True
        except sqlite3.Error as e:
            print(f"Error recording archive: {e}")
            return False
    
    def _cleanup_old_archives(self, plugin_name: str):
        """Keep only the last 2 archives for a plugin."""
        self.cursor.execute("""
            SELECT id, archive_path FROM plugin_archives 
            WHERE plugin_name = ? 
            ORDER BY archived_date DESC
        """, (plugin_name,))
        
        archives = self.cursor.fetchall()
        if len(archives) > 2:
            # Delete old archives (keep first 2)
            for archive in archives[2:]:
                archive_path = Path(archive['archive_path'])
                if archive_path.exists():
                    try:
                        import shutil
                        shutil.rmtree(archive_path)
                    except Exception as e:
                        print(f"Error deleting old archive: {e}")
                
                self.cursor.execute("DELETE FROM plugin_archives WHERE id = ?", (archive['id'],))
            
            self.conn.commit()
    
    def get_archives(self, plugin_name: str) -> List[Dict]:
        """Get available archives for a plugin."""
        self.cursor.execute("""
            SELECT * FROM plugin_archives 
            WHERE plugin_name = ? 
            ORDER BY archived_date DESC 
            LIMIT 2
        """, (plugin_name,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def add_history_entry(self, plugin_name: str, action: str, version: str = "",
                         success: bool = True, notes: str = "") -> bool:
        """Add an entry to the installation history."""
        try:
            self.cursor.execute("""
                INSERT INTO installation_history 
                (plugin_name, action, version, timestamp, success, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (plugin_name, action, version, datetime.now(), success, notes))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding history entry: {e}")
            return False
    
    def get_history(self, plugin_name: str = None, limit: int = 50) -> List[Dict]:
        """Get installation history."""
        if plugin_name:
            self.cursor.execute("""
                SELECT * FROM installation_history 
                WHERE plugin_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (plugin_name, limit))
        else:
            self.cursor.execute("""
                SELECT * FROM installation_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def mark_version_as_stable(self, plugin_name: str, version: str) -> bool:
        """
        Mark a specific version as stable (the known-good version).
        Only one version can be stable at a time per plugin.
        
        Args:
            plugin_name: Name of the plugin
            version: Version to mark as stable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, unmark any existing stable version for this plugin
            self.cursor.execute("""
                UPDATE plugin_archives 
                SET is_stable = 0, marked_stable_date = NULL
                WHERE plugin_name = ? AND is_stable = 1
            """, (plugin_name,))
            
            # Mark the specified version as stable
            self.cursor.execute("""
                UPDATE plugin_archives 
                SET is_stable = 1, marked_stable_date = datetime('now')
                WHERE plugin_name = ? AND version = ?
            """, (plugin_name, version))
            
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.logger.info(f"Marked {plugin_name} v{version} as STABLE")
                return True
            else:
                self.logger.warning(f"Could not mark {plugin_name} v{version} as stable (not found)")
                return False
                
        except Exception as e:
            self.logger.error(f"Error marking version as stable: {e}")
            return False
    
    def get_stable_version(self, plugin_name: str) -> Optional[Dict]:
        """
        Get the stable version for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dictionary with stable version info, or None if no stable version
        """
        try:
            self.cursor.execute("""
                SELECT * FROM plugin_archives 
                WHERE plugin_name = ? AND is_stable = 1
                LIMIT 1
            """, (plugin_name,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Error getting stable version: {e}")
            return None
    
    def get_all_versions(self, plugin_name: str) -> List[Dict]:
        """
        Get all archived versions for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List of version dictionaries, ordered by date (newest first)
        """
        try:
            self.cursor.execute("""
                SELECT * FROM plugin_archives 
                WHERE plugin_name = ?
                ORDER BY archived_date DESC
            """, (plugin_name,))
            
            return [dict(row) for row in self.cursor.fetchall()]
            
        except Exception as e:
            self.logger.error(f"Error getting versions: {e}")
            return []
    
    def unmark_stable_version(self, plugin_name: str) -> bool:
        """
        Remove stable marking from a plugin (no stable version).
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute("""
                UPDATE plugin_archives 
                SET is_stable = 0, marked_stable_date = NULL
                WHERE plugin_name = ? AND is_stable = 1
            """, (plugin_name,))
            
            self.conn.commit()
            self.logger.info(f"Unmarked stable version for {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unmarking stable version: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            try:
                self.conn.commit()  # Commit any pending changes
                self.conn.close()
                self.logger.debug(f"Database connection closed: {self.db_path}")
            except Exception as e:
                self.logger.error(f"Error closing database: {e}")
            finally:
                self.conn = None
                self.cursor = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()
        return False
    
    def __del__(self):
        """Cleanup - ensure connection is closed."""
        try:
            self.close()
        except Exception:
            pass  # Suppress errors during cleanup
