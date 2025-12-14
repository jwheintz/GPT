"""
Fix for Database Thread Safety Issue

The current PluginDatabase shares one connection across threads,
causing race conditions. This adds thread-safe wrapper.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional


class ThreadSafeDatabase:
    """
    Thread-safe wrapper for database operations.
    Uses one connection per thread to avoid SQLite threading issues.
    """
    
    def __init__(self, db_path: str = "obs_plugins.db"):
        """Initialize thread-safe database."""
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._lock = threading.Lock()
        
    def _get_connection(self):
        """Get connection for current thread."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.cursor = self._local.conn.cursor()
        return self._local.conn, self._local.cursor
    
    def execute_with_lock(self, query: str, params: tuple = ()):
        """
        Execute query with thread lock.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Cursor after execution
        """
        with self._lock:
            conn, cursor = self._get_connection()
            cursor.execute(query, params)
            conn.commit()
            return cursor
    
    def close_all(self):
        """Close all thread-local connections."""
        # Note: This won't close connections in other threads
        # Each thread should close its own connection
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            delattr(self._local, 'conn')
            delattr(self._local, 'cursor')


# Example of proper thread-safe usage
class ImprovedPluginDatabase:
    """
    Improved version with thread safety.
    Can be used as drop-in replacement for PluginDatabase.
    """
    
    def __init__(self, db_path: str = "obs_plugins.db"):
        """Initialize thread-safe database."""
        self.db_path = Path(db_path)
        self._connections = {}  # Thread ID -> Connection
        self._lock = threading.Lock()
        
        # Create tables on first connection
        conn = self._get_connection()
        self._create_tables(conn)
    
    def _get_connection(self):
        """Get or create connection for current thread."""
        thread_id = threading.get_ident()
        
        if thread_id not in self._connections:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._connections[thread_id] = conn
        
        return self._connections[thread_id]
    
    def _create_tables(self, conn):
        """Create tables using provided connection."""
        cursor = conn.cursor()
        
        # Plugin catalog table
        cursor.execute("""
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installed_plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_name TEXT NOT NULL,
                version TEXT NOT NULL,
                install_path TEXT NOT NULL,
                install_date TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = (), commit: bool = True):
        """
        Execute query with thread-safety.
        
        Args:
            query: SQL query
            params: Query parameters
            commit: Whether to commit after execution
            
        Returns:
            Cursor result
        """
        with self._lock:  # Ensure only one thread writes at a time
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor
    
    def close(self):
        """Close all connections."""
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Testing function
def test_thread_safety():
    """Test that database operations are thread-safe."""
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    print("Testing database thread safety...")
    
    # Create test database
    db = ImprovedPluginDatabase("test_threading.db")
    
    def insert_plugin(thread_num):
        """Insert a plugin from a thread."""
        try:
            query = """
                INSERT INTO plugin_catalog (name, display_name, description)
                VALUES (?, ?, ?)
            """
            params = (f"plugin-{thread_num}", f"Plugin {thread_num}", f"Test {thread_num}")
            db.execute_query(query, params)
            print(f"  Thread {thread_num}: Inserted successfully")
            return True
        except Exception as e:
            print(f"  Thread {thread_num}: ERROR - {e}")
            return False
    
    # Run 10 threads simultaneously
    print("  Running 10 concurrent insertions...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(insert_plugin, range(10)))
    
    # Check results
    successes = sum(results)
    print(f"  Results: {successes}/10 insertions successful")
    
    # Verify count
    cursor = db.execute_query("SELECT COUNT(*) FROM plugin_catalog", commit=False)
    count = cursor.fetchone()[0]
    print(f"  Verification: {count} records in database")
    
    # Cleanup
    db.close()
    Path("test_threading.db").unlink()
    
    if successes == 10 and count == 10:
        print("  ✓ Thread safety test PASSED!")
        return True
    else:
        print("  ✗ Thread safety test FAILED!")
        return False


if __name__ == "__main__":
    print("\nDatabase Thread Safety Fix\n")
    print("="*70)
    
    # Run test
    success = test_thread_safety()
    
    print("\n" + "="*70)
    if success:
        print("✅ Thread-safe implementation working correctly!")
        print("\nRecommendation: Replace PluginDatabase with ImprovedPluginDatabase")
    else:
        print("⚠ Thread safety issues detected!")
    
    print("\nKey improvements:")
    print("  1. One connection per thread (thread-local storage)")
    print("  2. Lock for write operations (prevents race conditions)")
    print("  3. Proper cleanup in __del__")
    print("  4. check_same_thread=False for SQLite")
