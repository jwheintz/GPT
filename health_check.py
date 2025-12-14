"""
Health Check & Maintenance Utility

Checks application health, cleans up resources, and performs maintenance tasks.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))


def check_database_health():
    """Check database integrity and size."""
    print("Checking database health...")
    
    from obs_plugin_manager.database import PluginDatabase
    
    db_file = Path("obs_plugins.db")
    if not db_file.exists():
        print("  ⚠ Database file not found (will be created on first run)")
        return True
    
    try:
        db = PluginDatabase()
        
        # Check if we can query
        catalog = db.get_catalog_plugins()
        installed = db.get_installed_plugins()
        
        db_size_mb = db_file.stat().st_size / (1024 * 1024)
        
        print(f"  ✓ Database accessible")
        print(f"  ✓ Catalog plugins: {len(catalog)}")
        print(f"  ✓ Installed plugins: {len(installed)}")
        print(f"  ✓ Database size: {db_size_mb:.2f} MB")
        
        db.close()
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def check_cache_health():
    """Check cache files and cleanup old entries."""
    print("\nChecking cache health...")
    
    cache_dirs = [
        "plugin_cache",
        "discovery_cache",
        "obs_resources_cache",
        "local_repository"
    ]
    
    total_size = 0
    for cache_dir in cache_dirs:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            dir_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
            total_size += dir_size
            print(f"  ✓ {cache_dir}: {dir_size / (1024*1024):.2f} MB")
        else:
            print(f"  ℹ {cache_dir}: Not yet created")
    
    print(f"  Total cache size: {total_size / (1024*1024):.2f} MB")
    
    return True


def cleanup_old_logs(days_to_keep=30):
    """Clean up log files older than specified days."""
    print(f"\nCleaning up logs older than {days_to_keep} days...")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print("  ℹ No logs directory found")
        return True
    
    try:
        import time
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        deleted_count = 0
        deleted_size = 0
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                size = log_file.stat().st_size
                log_file.unlink()
                deleted_count += 1
                deleted_size += size
        
        if deleted_count > 0:
            print(f"  ✓ Deleted {deleted_count} old log file(s) ({deleted_size / 1024:.2f} KB)")
        else:
            print(f"  ✓ No old logs to clean up")
        
        return True
    except Exception as e:
        print(f"  ✗ Error cleaning logs: {e}")
        return False


def cleanup_temp_files():
    """Clean up temporary files."""
    print("\nCleaning up temporary files...")
    
    patterns = [
        "*.tmp",
        "*.bak",
        "*.backup",
        "**/temp/*",
        "**/tmp/*"
    ]
    
    deleted_count = 0
    deleted_size = 0
    
    for pattern in patterns:
        for temp_file in Path(".").glob(pattern):
            if temp_file.is_file():
                try:
                    size = temp_file.stat().st_size
                    temp_file.unlink()
                    deleted_count += 1
                    deleted_size += size
                except Exception:
                    pass
    
    if deleted_count > 0:
        print(f"  ✓ Deleted {deleted_count} temporary file(s) ({deleted_size / 1024:.2f} KB)")
    else:
        print(f"  ✓ No temporary files to clean up")
    
    return True


def verify_file_integrity():
    """Verify critical files exist."""
    print("\nVerifying file integrity...")
    
    critical_files = [
        "obs_plugin_manager/__init__.py",
        "obs_plugin_manager/database.py",
        "obs_plugin_manager/obs_manager.py",
        "obs_plugin_manager/plugin_scanner.py",
        "obs_plugin_manager/plugin_repository.py",
        "obs_plugin_manager/plugin_installer.py",
        "obs_plugin_manager/local_repository.py",
        "obs_plugin_manager/discovery.py",
        "obs_plugin_manager/obs_resources.py",
        "obs_plugin_manager/gui.py",
        "obs_plugin_manager/logger.py",
        "obs_plugin_manager/validators.py",
        "obs_plugin_manager/safe_cache.py",
        "requirements.txt",
        "obs_plugin_manager.py"
    ]
    
    missing = []
    for file in critical_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ {file}")
    
    if missing:
        print(f"\n  ⚠ WARNING: {len(missing)} critical file(s) missing!")
        return False
    
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies...")
    
    dependencies = {
        "psutil": "Process management",
        "requests": "HTTP library",
        "beautifulsoup4": "HTML parsing (as bs4)",
        "tkinter": "GUI framework"
    }
    
    missing = []
    for dep, description in dependencies.items():
        try:
            if dep == "beautifulsoup4":
                import bs4
                print(f"  ✓ {dep} ({description})")
            elif dep == "tkinter":
                import tkinter
                print(f"  ✓ {dep} ({description})")
            else:
                __import__(dep)
                print(f"  ✓ {dep} ({description})")
        except ImportError:
            print(f"  ✗ {dep} ({description}) - NOT INSTALLED")
            missing.append(dep)
    
    if missing:
        print(f"\n  ⚠ WARNING: {len(missing)} dependency/ies missing!")
        print("  Run: pip install -r requirements.txt")
        return False
    
    return True


def get_system_info():
    """Get system information."""
    print("\nSystem Information:")
    
    try:
        import platform
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        print(f"  Architecture: {platform.machine()}")
    except Exception as e:
        print(f"  ✗ Could not get system info: {e}")


def repair_cache():
    """Attempt to repair corrupted cache files."""
    print("\nRepairing cache files...")
    
    cache_files = [
        "plugin_cache/plugins_cache.json",
        "discovery_cache/discovery_cache.json",
        "obs_resources_cache/obs_resources_cache.json",
        "local_repository/repository_index.json"
    ]
    
    repaired = 0
    for cache_file in cache_files:
        cache_path = Path(cache_file)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Try to parse
                print(f"  ✓ {cache_file} - OK")
            except json.JSONDecodeError:
                print(f"  ⚠ {cache_file} - CORRUPTED, backing up and resetting")
                backup = cache_path.with_suffix('.json.corrupted')
                cache_path.rename(backup)
                repaired += 1
        else:
            print(f"  ℹ {cache_file} - Not yet created")
    
    if repaired > 0:
        print(f"  ✓ Repaired {repaired} corrupted cache file(s)")
    
    return True


def generate_health_report():
    """Generate a comprehensive health report."""
    print("="*70)
    print("OBS PLUGIN MANAGER - HEALTH CHECK & MAINTENANCE")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = []
    
    checks.append(("System Info", get_system_info()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("File Integrity", verify_file_integrity()))
    checks.append(("Database Health", check_database_health()))
    checks.append(("Cache Health", check_cache_health()))
    checks.append(("Cache Repair", repair_cache()))
    checks.append(("Log Cleanup", cleanup_old_logs()))
    checks.append(("Temp Cleanup", cleanup_temp_files()))
    
    print("\n" + "="*70)
    print("HEALTH CHECK SUMMARY")
    print("="*70)
    
    passed = sum(1 for name, result in checks if result and name != "System Info")
    total = len(checks) - 1  # Exclude System Info from count
    
    for name, result in checks:
        if name == "System Info":
            continue
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All health checks passed! Application is healthy.")
        return 0
    else:
        print(f"\n⚠ {total - passed} check(s) failed. See details above.")
        return 1


def main():
    """Main entry point."""
    try:
        exit_code = generate_health_report()
        
        if exit_code == 0:
            print("\n✓ Maintenance complete. Application is ready to use.")
        else:
            print("\n⚠ Some issues found. Please address them before using the application.")
        
        return exit_code
    except Exception as e:
        print(f"\n✗ Health check error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
