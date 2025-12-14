"""
Thread-Safe Cache - Provides thread-safe caching with file locking.
"""

import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from contextlib import contextmanager
import time


class ThreadSafeCache:
    """Thread-safe cache with file locking and expiration."""
    
    def __init__(self, cache_file: Path, expiry: timedelta = timedelta(hours=6)):
        """
        Initialize thread-safe cache.
        
        Args:
            cache_file: Path to cache file
            expiry: Cache expiration time
        """
        self.cache_file = Path(cache_file)
        self.expiry = expiry
        self.lock = threading.Lock()
        self._cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file (thread-safe)."""
        with self.lock:
            if self.cache_file.exists():
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except Exception as e:
                    from .logger import get_logger
                    logger = get_logger(__name__)
                    logger.error(f"Error loading cache from {self.cache_file}: {e}")
                    self._cache = {}
            else:
                self._cache = {}
    
    def _save_cache(self):
        """Save cache to file (thread-safe)."""
        with self.lock:
            try:
                # Ensure parent directory exists
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to temporary file first
                temp_file = self.cache_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f, indent=2, ensure_ascii=False)
                
                # Atomic rename
                temp_file.replace(self.cache_file)
            except Exception as e:
                from .logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"Error saving cache to {self.cache_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        with self.lock:
            if key not in self._cache:
                return default
            
            entry = self._cache[key]
            
            # Check expiration
            if 'cached_at' in entry:
                try:
                    cached_time = datetime.fromisoformat(entry['cached_at'])
                    if datetime.now() - cached_time >= self.expiry:
                        # Expired, remove and return default
                        del self._cache[key]
                        return default
                except Exception:
                    pass
            
            return entry.get('value', default)
    
    def set(self, key: str, value: Any):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            self._cache[key] = {
                'value': value,
                'cached_at': datetime.now().isoformat()
            }
        self._save_cache()
    
    def delete(self, key: str):
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        with self.lock:
            if key in self._cache:
                del self._cache[key]
        self._save_cache()
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self._cache = {}
        self._save_cache()
    
    def is_valid(self, key: str) -> bool:
        """
        Check if cache key exists and is not expired.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if valid and not expired, False otherwise
        """
        with self.lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if 'cached_at' not in entry:
                return False
            
            try:
                cached_time = datetime.fromisoformat(entry['cached_at'])
                return datetime.now() - cached_time < self.expiry
            except Exception:
                return False
    
    def get_age(self, key: str) -> Optional[timedelta]:
        """
        Get age of cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Age as timedelta or None if not found
        """
        with self.lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if 'cached_at' not in entry:
                return None
            
            try:
                cached_time = datetime.fromisoformat(entry['cached_at'])
                return datetime.now() - cached_time
            except Exception:
                return None
    
    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        with self.lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if 'cached_at' in entry:
                    try:
                        cached_time = datetime.fromisoformat(entry['cached_at'])
                        if datetime.now() - cached_time >= self.expiry:
                            expired_keys.append(key)
                    except Exception:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        if expired_keys:
            self._save_cache()
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self.lock:
            total_entries = len(self._cache)
            valid_entries = sum(1 for key in self._cache if self.is_valid(key))
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': total_entries - valid_entries,
                'expiry_hours': self.expiry.total_seconds() / 3600,
                'cache_file': str(self.cache_file),
                'file_size_bytes': self.cache_file.stat().st_size if self.cache_file.exists() else 0
            }


@contextmanager
def file_lock(lock_file: Path, timeout: int = 10):
    """
    Context manager for file-based locking.
    
    Args:
        lock_file: Path to lock file
        timeout: Timeout in seconds
        
    Example:
        with file_lock(Path("my.lock")):
            # Critical section
            pass
    """
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Try to acquire lock
    start_time = time.time()
    while True:
        try:
            # Try to create lock file exclusively
            with open(lock_file, 'x') as f:
                f.write(str(threading.get_ident()))
            break
        except FileExistsError:
            # Lock already exists, wait
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Could not acquire lock on {lock_file} within {timeout} seconds")
            time.sleep(0.1)
    
    try:
        yield
    finally:
        # Release lock
        try:
            lock_file.unlink()
        except Exception:
            pass


class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()
            
            # Remove calls older than 1 minute
            self.calls = [t for t in self.calls if now - t < 60]
            
            # Check if we've exceeded limit
            if len(self.calls) >= self.calls_per_minute:
                # Calculate wait time
                oldest_call = self.calls[0]
                wait_time = 60 - (now - oldest_call)
                
                if wait_time > 0:
                    from .logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
            
            # Record this call
            self.calls.append(time.time())
    
    def can_call(self) -> bool:
        """Check if a call can be made without waiting."""
        with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < 60]
            return len(self.calls) < self.calls_per_minute
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current minute."""
        with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < 60]
            return max(0, self.calls_per_minute - len(self.calls))
