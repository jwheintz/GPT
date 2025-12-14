"""
Logging Infrastructure - Centralized logging for OBS Plugin Manager.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class PluginManagerLogger:
    """Centralized logger for the application."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once)."""
        if not self._initialized:
            self._setup_logging()
            PluginManagerLogger._initialized = True
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        log_filename = f"obs_plugin_manager_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_file = self.log_dir / log_filename
        
        # Configure root logger
        self.logger = logging.getLogger("OBSPluginManager")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # File handler (detailed logs)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler (info and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info("="*70)
        self.logger.info("OBS Plugin Manager - Logging Initialized")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("="*70)
    
    def get_logger(self, name: Optional[str] = None):
        """
        Get a logger instance.
        
        Args:
            name: Optional name for the logger (usually module name)
            
        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"OBSPluginManager.{name}")
        return self.logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log an info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log an error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log an exception with traceback."""
        self.logger.exception(message, *args, **kwargs)
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up log files older than specified days.
        
        Args:
            days_to_keep: Number of days to keep logs (default 30)
        """
        try:
            import time
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            
            deleted_count = 0
            for log_file in self.log_dir.glob("obs_plugin_manager_*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old log file(s)")
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")


# Global logger instance
_global_logger = None


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance (convenience function).
    
    Args:
        name: Optional name for the logger (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        from logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is a log message")
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = PluginManagerLogger()
    return _global_logger.get_logger(name)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and results.
    
    Example:
        @log_function_call
        def my_function(param1, param2):
            return param1 + param2
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned successfully")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised {type(e).__name__}: {e}")
            raise
    
    return wrapper


def log_exceptions(func):
    """
    Decorator to log exceptions with full traceback.
    
    Example:
        @log_exceptions
        def risky_function():
            # code that might raise
            pass
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__qualname__}: {e}")
            raise
    
    return wrapper


# Initialize logger on module import
_global_logger = PluginManagerLogger()
