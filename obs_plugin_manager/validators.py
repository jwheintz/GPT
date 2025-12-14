"""
Input Validation - Sanitization and validation utilities.
"""

import re
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_plugin_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate plugin name for security and correctness.
    
    Args:
        name: Plugin name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Plugin name cannot be empty"
    
    if len(name) > 200:
        return False, "Plugin name too long (max 200 characters)"
    
    # Allow alphanumeric, dash, underscore, dot
    if not re.match(r'^[a-zA-Z0-9._-]+$', name):
        return False, "Plugin name contains invalid characters (only alphanumeric, dash, underscore, dot allowed)"
    
    # Prevent path traversal
    if '..' in name or '/' in name or '\\' in name:
        return False, "Plugin name contains path traversal characters"
    
    # Prevent reserved names
    reserved = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'lpt1', 'lpt2']
    if name.lower() in reserved:
        return False, f"Plugin name '{name}' is reserved"
    
    return True, None


def sanitize_plugin_name(name: str) -> str:
    """
    Sanitize plugin name to be filesystem-safe.
    
    Args:
        name: Plugin name to sanitize
        
    Returns:
        Sanitized plugin name
    """
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace spaces with dashes
    name = name.replace(' ', '-')
    
    # Remove path traversal attempts
    name = name.replace('..', '')
    
    # Limit length
    if len(name) > 200:
        name = name[:200]
    
    # Ensure it's not empty after sanitization
    if not name:
        name = "unknown-plugin"
    
    return name


def validate_version_string(version: str) -> Tuple[bool, Optional[str]]:
    """
    Validate version string format.
    
    Args:
        version: Version string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not version:
        return False, "Version cannot be empty"
    
    if len(version) > 50:
        return False, "Version string too long (max 50 characters)"
    
    # Allow semantic versioning and common formats
    # Examples: 1.0.0, v1.2.3, 2.0.0-beta, 1.0, etc.
    pattern = r'^v?\d+(\.\d+)*(-[a-zA-Z0-9]+)?$'
    if not re.match(pattern, version):
        return False, "Invalid version format (use semantic versioning like 1.0.0)"
    
    return True, None


def sanitize_version_string(version: str) -> str:
    """
    Sanitize version string.
    
    Args:
        version: Version string to sanitize
        
    Returns:
        Sanitized version string
    """
    # Remove leading/trailing whitespace
    version = version.strip()
    
    # Remove invalid characters
    version = re.sub(r'[^a-zA-Z0-9.-]', '', version)
    
    # Limit length
    if len(version) > 50:
        version = version[:50]
    
    # Fallback
    if not version:
        version = "unknown"
    
    return version


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and safety.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    if len(url) > 2000:
        return False, "URL too long (max 2000 characters)"
    
    try:
        parsed = urlparse(url)
        
        # Require scheme
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must use http or https protocol"
        
        # Require netloc
        if not parsed.netloc:
            return False, "URL must have a valid domain"
        
        # Block localhost/local IPs for security
        forbidden_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if parsed.netloc.lower() in forbidden_hosts or parsed.netloc.startswith('192.168.') or parsed.netloc.startswith('10.'):
            return False, "Local URLs are not allowed"
        
        return True, None
    except Exception as e:
        return False, f"Invalid URL format: {e}"


def validate_file_path(path: Path, must_exist: bool = False, allowed_extensions: Optional[list] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate file path for security and correctness.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must already exist
        allowed_extensions: List of allowed extensions (e.g., ['.dll', '.exe'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Resolve path (this will detect path traversal)
        resolved_path = path.resolve()
        
        # Check for path traversal attempts
        if '..' in str(path):
            return False, "Path contains path traversal characters"
        
        # Check if exists (if required)
        if must_exist and not resolved_path.exists():
            return False, f"Path does not exist: {resolved_path}"
        
        # Check extension (if provided)
        if allowed_extensions:
            if resolved_path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                return False, f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        return True, None
    except Exception as e:
        return False, f"Invalid path: {e}"


def validate_directory_path(path: Path, must_exist: bool = False, create_if_missing: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate directory path.
    
    Args:
        path: Directory path to validate
        must_exist: Whether the directory must already exist
        create_if_missing: Create directory if it doesn't exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Resolve path
        resolved_path = path.resolve()
        
        # Check for path traversal
        if '..' in str(path):
            return False, "Path contains path traversal characters"
        
        # Check if exists
        if resolved_path.exists():
            if not resolved_path.is_dir():
                return False, "Path exists but is not a directory"
        elif must_exist:
            return False, f"Directory does not exist: {resolved_path}"
        elif create_if_missing:
            resolved_path.mkdir(parents=True, exist_ok=True)
        
        return True, None
    except Exception as e:
        return False, f"Invalid directory path: {e}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be filesystem-safe.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    
    # Remove invalid characters for Windows/Linux
    invalid_chars = '<>:"/\\|?*\x00-\x1f'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Limit length (Windows has 255 char limit)
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:245]  # Leave room for extension
        filename = f"{name}.{ext}" if ext else name
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def validate_json_data(data: dict, required_keys: list) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON data structure.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required keys
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    return True, None


# Convenience functions for quick validation

def safe_plugin_name(name: str) -> str:
    """Get a safe plugin name or raise ValidationError."""
    is_valid, error = validate_plugin_name(name)
    if not is_valid:
        sanitized = sanitize_plugin_name(name)
        # Try again with sanitized version
        is_valid, error = validate_plugin_name(sanitized)
        if not is_valid:
            raise ValidationError(f"Invalid plugin name: {error}")
        return sanitized
    return name


def safe_version(version: str) -> str:
    """Get a safe version string or raise ValidationError."""
    is_valid, error = validate_version_string(version)
    if not is_valid:
        sanitized = sanitize_version_string(version)
        is_valid, error = validate_version_string(sanitized)
        if not is_valid:
            raise ValidationError(f"Invalid version: {error}")
        return sanitized
    return version


def safe_url(url: str) -> str:
    """Get a safe URL or raise ValidationError."""
    is_valid, error = validate_url(url)
    if not is_valid:
        raise ValidationError(f"Invalid URL: {error}")
    return url


def safe_path(path: Path, **kwargs) -> Path:
    """Get a safe path or raise ValidationError."""
    is_valid, error = validate_file_path(path, **kwargs)
    if not is_valid:
        raise ValidationError(f"Invalid path: {error}")
    return path
