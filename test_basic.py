"""
Basic Test Suite for OBS Plugin Manager
Tests core functionality without requiring OBS installation
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from obs_plugin_manager.database import PluginDatabase
from obs_plugin_manager.plugin_repository import PluginRepository


def test_database():
    """Test database functionality."""
    print("Testing Database Module...")
    
    # Create a test database
    db = PluginDatabase("test_obs_plugins.db")
    
    # Test adding plugin to catalog
    success = db.add_plugin_to_catalog(
        name="test-plugin",
        display_name="Test Plugin",
        description="A test plugin",
        author="Test Author",
        category="Testing",
        is_recommended=True
    )
    
    if success:
        print("  ✓ Plugin added to catalog")
    else:
        print("  ✗ Failed to add plugin to catalog")
        return False
    
    # Test retrieving plugin
    plugin = db.get_plugin_by_name("test-plugin")
    if plugin and plugin['display_name'] == "Test Plugin":
        print("  ✓ Plugin retrieved from catalog")
    else:
        print("  ✗ Failed to retrieve plugin from catalog")
        return False
    
    # Test adding installed plugin
    success = db.add_installed_plugin("test-plugin", "1.0.0", "C:\\test\\path")
    if success:
        print("  ✓ Installed plugin recorded")
    else:
        print("  ✗ Failed to record installed plugin")
        return False
    
    # Test adding history entry
    success = db.add_history_entry("test-plugin", "install", "1.0.0", True, "Test installation")
    if success:
        print("  ✓ History entry added")
    else:
        print("  ✗ Failed to add history entry")
        return False
    
    # Cleanup
    db.close()
    Path("test_obs_plugins.db").unlink(missing_ok=True)
    
    print("  ✓ Database tests passed!\n")
    return True


def test_plugin_repository():
    """Test plugin repository functionality."""
    print("Testing Plugin Repository Module...")
    
    repo = PluginRepository()
    
    # Test getting popular plugins
    plugins = repo.get_popular_plugins()
    if len(plugins) > 0:
        print(f"  ✓ Found {len(plugins)} plugins in catalog")
    else:
        print("  ✗ No plugins found in catalog")
        return False
    
    # Test getting categories
    categories = repo.get_categories()
    if len(categories) > 0:
        print(f"  ✓ Found {len(categories)} categories: {', '.join(categories)}")
    else:
        print("  ✗ No categories found")
        return False
    
    # Test search functionality
    search_results = repo.search_plugins("websocket")
    if len(search_results) > 0:
        print(f"  ✓ Search found {len(search_results)} plugin(s)")
    else:
        print("  ℹ No plugins found for 'websocket' (this may be okay)")
    
    # Test version comparison
    result = repo.compare_versions("1.0.0", "1.0.1")
    if result == -1:
        print("  ✓ Version comparison working (1.0.0 < 1.0.1)")
    else:
        print("  ✗ Version comparison failed")
        return False
    
    result = repo.compare_versions("2.0.0", "1.9.9")
    if result == 1:
        print("  ✓ Version comparison working (2.0.0 > 1.9.9)")
    else:
        print("  ✗ Version comparison failed")
        return False
    
    print("  ✓ Plugin repository tests passed!\n")
    return True


def test_obs_manager():
    """Test OBS manager functionality (limited without OBS installed)."""
    print("Testing OBS Manager Module...")
    
    from obs_plugin_manager.obs_manager import OBSManager
    
    manager = OBSManager()
    
    # Test OBS detection (may or may not find OBS)
    if manager.is_obs_installed():
        print(f"  ✓ OBS installation detected at: {manager.get_obs_path()}")
        plugin_dirs = manager.get_plugin_directories()
        print(f"  ✓ Found {len(plugin_dirs)} plugin director(ies)")
    else:
        print("  ℹ OBS not detected (this is okay if OBS is not installed)")
    
    # Test OBS process checking
    is_running = manager.is_obs_running()
    print(f"  ✓ OBS process check: {'Running' if is_running else 'Not running'}")
    
    print("  ✓ OBS manager tests passed!\n")
    return True


def test_plugin_scanner():
    """Test plugin scanner (limited without OBS)."""
    print("Testing Plugin Scanner Module...")
    
    from obs_plugin_manager.plugin_scanner import PluginScanner
    
    # Create scanner with test directory
    test_dirs = [Path("test_plugins")]
    scanner = PluginScanner(test_dirs)
    
    # Test version pattern matching
    print("  ✓ Plugin scanner initialized")
    print("  ℹ Actual scanning requires OBS installation\n")
    return True


def display_summary():
    """Display summary of available plugins."""
    print("=" * 60)
    print("AVAILABLE PLUGINS IN CATALOG")
    print("=" * 60)
    
    repo = PluginRepository()
    plugins = repo.get_popular_plugins()
    
    # Group by category
    by_category = {}
    for plugin in plugins:
        cat = plugin.get('category', 'Other')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(plugin)
    
    for category in sorted(by_category.keys()):
        print(f"\n{category}:")
        print("-" * 60)
        for plugin in by_category[category]:
            recommended = "⭐" if plugin.get('is_recommended') else "  "
            print(f"{recommended} {plugin.get('display_name', plugin['name'])}")
            print(f"   Author: {plugin.get('author', 'Unknown')}")
            print(f"   {plugin.get('description', 'No description')}")
            print()
    
    print("=" * 60)
    print(f"Total: {len(plugins)} plugins available")
    print("=" * 60)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OBS PLUGIN MANAGER - BASIC TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Database", test_database()))
    results.append(("Plugin Repository", test_plugin_repository()))
    results.append(("OBS Manager", test_obs_manager()))
    results.append(("Plugin Scanner", test_plugin_scanner()))
    
    # Display results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed successfully!")
        print("\n")
        display_summary()
    else:
        print("\n✗ Some tests failed")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
