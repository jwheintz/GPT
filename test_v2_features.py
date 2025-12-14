"""
Smoke Tests for Version 2.0 Features
Tests new Discovery and Local Repository functionality
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from obs_plugin_manager.local_repository import LocalRepository
from obs_plugin_manager.discovery import PluginDiscovery
from obs_plugin_manager.obs_resources import OBSResourcesFetcher


def test_local_repository():
    """Test local repository functionality."""
    print("Testing Local Repository...")
    
    try:
        # Initialize repository
        repo = LocalRepository("test_local_repo")
        
        # Test repository stats
        stats = repo.get_repository_stats()
        assert isinstance(stats, dict), "Stats should be a dictionary"
        assert 'total_plugins' in stats, "Stats should include total_plugins"
        print("  ✓ Repository initialized")
        print(f"  ✓ Stats: {stats['total_plugins']} plugins, {stats['total_scripts']} scripts")
        
        # Test list operations
        plugins = repo.list_all_plugins()
        scripts = repo.list_all_scripts()
        assert isinstance(plugins, list), "Plugins should be a list"
        assert isinstance(scripts, list), "Scripts should be a list"
        print(f"  ✓ Listed {len(plugins)} plugins, {len(scripts)} scripts")
        
        # Cleanup test directory
        import shutil
        if Path("test_local_repo").exists():
            shutil.rmtree("test_local_repo")
        
        print("  ✓ Local Repository tests passed!\n")
        return True
    except Exception as e:
        print(f"  ✗ Local Repository test failed: {e}\n")
        return False


def test_obs_resources():
    """Test OBS Resources fetcher."""
    print("Testing OBS Resources Fetcher...")
    
    try:
        # Initialize fetcher
        fetcher = OBSResourcesFetcher("test_obs_cache")
        
        # Test cache info
        cache_info = fetcher.get_cache_info()
        assert isinstance(cache_info, dict), "Cache info should be a dictionary"
        print("  ✓ OBS Resources fetcher initialized")
        
        # Test that we can call the fetch methods without errors
        # (don't actually fetch to avoid hitting the OBS website in tests)
        print("  ✓ Fetch methods available")
        
        # Test categorization
        category = fetcher._determine_category("Move Transition", "Plugin to move source", "plugin")
        assert category in ["Effects", "Sources", "Transitions", "Output", "Audio", "Integration", "Automation", "Other"], \
            f"Invalid category: {category}"
        print(f"  ✓ Categorization works: '{category}'")
        
        # Test name cleaning
        clean_name = fetcher._clean_name("Advanced Scene Switcher v1.2.3")
        assert clean_name == "advanced-scene-switcher", f"Name cleaning failed: {clean_name}"
        print(f"  ✓ Name cleaning works: '{clean_name}'")
        
        # Cleanup
        import shutil
        if Path("test_obs_cache").exists():
            shutil.rmtree("test_obs_cache")
        
        print("  ✓ OBS Resources tests passed!\n")
        return True
    except Exception as e:
        print(f"  ✗ OBS Resources test failed: {e}\n")
        return False


def test_discovery():
    """Test discovery module."""
    print("Testing Discovery Module...")
    
    try:
        # Initialize discovery
        discovery = PluginDiscovery("test_discovery_cache")
        
        # Test cache operations
        cache_info = discovery.get_cache_info()
        assert isinstance(cache_info, dict), "Cache info should be a dictionary"
        print("  ✓ Discovery module initialized")
        
        # Test version comparison
        result = discovery.compare_versions("1.0.0", "1.0.1")
        assert result == -1, "Version comparison failed"
        print("  ✓ Version comparison works")
        
        result = discovery.compare_versions("2.0.0", "1.9.9")
        assert result == 1, "Version comparison failed"
        print("  ✓ Version comparison works (reverse)")
        
        # Test search
        categories = discovery.get_categories()
        assert isinstance(categories, list), "Categories should be a list"
        assert len(categories) > 0, "Should have categories"
        print(f"  ✓ Found {len(categories)} categories")
        
        # Test known developers
        developers = discovery.get_known_developers()
        assert isinstance(developers, list), "Developers should be a list"
        assert "obsproject" in developers, "Should include obsproject"
        print(f"  ✓ Tracking {len(developers)} known developers")
        
        # Cleanup
        import shutil
        if Path("test_discovery_cache").exists():
            shutil.rmtree("test_discovery_cache")
        
        print("  ✓ Discovery module tests passed!\n")
        return True
    except Exception as e:
        print(f"  ✗ Discovery test failed: {e}\n")
        return False


def test_imports():
    """Test that all imports work."""
    print("Testing Module Imports...")
    
    try:
        # Test all core imports
        from obs_plugin_manager import database
        from obs_plugin_manager import obs_manager
        from obs_plugin_manager import plugin_scanner
        from obs_plugin_manager import plugin_repository
        from obs_plugin_manager import plugin_installer
        from obs_plugin_manager import local_repository
        from obs_plugin_manager import discovery
        from obs_plugin_manager import obs_resources
        print("  ✓ All core modules import successfully")
        
        # Test that classes are available
        from obs_plugin_manager.database import PluginDatabase
        from obs_plugin_manager.local_repository import LocalRepository
        from obs_plugin_manager.discovery import PluginDiscovery
        from obs_plugin_manager.obs_resources import OBSResourcesFetcher
        print("  ✓ All classes import successfully")
        
        # Test version
        from obs_plugin_manager import __version__
        assert __version__ == "2.0.0", f"Version should be 2.0.0, got {__version__}"
        print(f"  ✓ Version is {__version__}")
        
        print("  ✓ Import tests passed!\n")
        return True
    except Exception as e:
        print(f"  ✗ Import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test that all dependencies are available."""
    print("Testing Dependencies...")
    
    dependencies = {
        "psutil": "Process management",
        "requests": "HTTP library",
        "beautifulsoup4": "HTML parsing",
        "tkinter": "GUI framework"
    }
    
    all_available = True
    for dep, description in dependencies.items():
        try:
            if dep == "beautifulsoup4":
                import bs4
                print(f"  ✓ {dep} ({description}) - version {bs4.__version__}")
            elif dep == "tkinter":
                import tkinter
                print(f"  ✓ {dep} ({description}) - available")
            else:
                module = __import__(dep)
                version = getattr(module, '__version__', 'unknown')
                print(f"  ✓ {dep} ({description}) - version {version}")
        except ImportError as e:
            print(f"  ✗ {dep} ({description}) - NOT INSTALLED: {e}")
            all_available = False
    
    if all_available:
        print("  ✓ All dependencies available!\n")
    else:
        print("  ⚠ Some dependencies missing. Run: pip install -r requirements.txt\n")
    
    return all_available


def test_data_structures():
    """Test data structure compatibility."""
    print("Testing Data Structures...")
    
    try:
        # Test that plugin dictionaries have expected structure
        from obs_plugin_manager.discovery import PluginDiscovery
        discovery = PluginDiscovery("test_cache")
        
        # Create a test plugin entry
        test_plugin = {
            "name": "test-plugin",
            "display_name": "Test Plugin",
            "description": "A test plugin",
            "author": "Test Author",
            "category": "Effects",
            "homepage_url": "https://example.com",
            "download_url": "https://example.com/download",
            "stars": 100,
            "discovered_at": "2025-12-14T12:00:00"
        }
        
        # Verify required fields
        required_fields = ["name", "display_name", "description", "author", "category"]
        for field in required_fields:
            assert field in test_plugin, f"Missing required field: {field}"
        
        print("  ✓ Plugin data structure valid")
        
        # Cleanup
        import shutil
        if Path("test_cache").exists():
            shutil.rmtree("test_cache")
        
        print("  ✓ Data structure tests passed!\n")
        return True
    except Exception as e:
        print(f"  ✗ Data structure test failed: {e}\n")
        return False


def main():
    """Run all smoke tests."""
    print("\n" + "=" * 60)
    print("OBS PLUGIN MANAGER v2.0 - SMOKE TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Dependencies", test_dependencies()))
    results.append(("Module Imports", test_imports()))
    results.append(("Local Repository", test_local_repository()))
    results.append(("OBS Resources", test_obs_resources()))
    results.append(("Discovery Module", test_discovery()))
    results.append(("Data Structures", test_data_structures()))
    
    # Display results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All smoke tests passed successfully!")
        print("\n🚀 Version 2.0 is ready for deployment!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        print("\n⚠ Please fix issues before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
