"""
Comprehensive Smoke Test - Tests ALL components together

This is the REAL test - does everything actually work together?
"""

import sys
from pathlib import Path
import shutil
import json
import time

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def section(title):
    """Print section header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

class SmokeTest:
    def __init__(self):
        self.results = []
        self.test_dir = Path("smoke_test_temp")
        
    def test(self, name, func):
        """Run a test and record result."""
        try:
            print(f"Testing {name}...", end=" ")
            result = func()
            if result:
                print(f"{GREEN}✓ PASSED{RESET}")
                self.results.append((name, True, None))
            else:
                print(f"{RED}✗ FAILED{RESET}")
                self.results.append((name, False, "Test returned False"))
        except Exception as e:
            print(f"{RED}✗ ERROR: {e}{RESET}")
            self.results.append((name, False, str(e)))
    
    def cleanup(self):
        """Cleanup test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Clean up other test dirs
        for test_dir in Path(".").glob("test_*"):
            if test_dir.is_dir():
                shutil.rmtree(test_dir)
    
    def test_logging_system(self):
        """Test that logging system works."""
        section("LOGGING SYSTEM")
        
        def test():
            from obs_plugin_manager.logger import get_logger
            logger = get_logger("smoke_test")
            
            # Log at different levels
            logger.debug("Debug message from smoke test")
            logger.info("Info message from smoke test")
            logger.warning("Warning message from smoke test")
            logger.error("Error message from smoke test")
            
            # Check log file exists
            log_files = list(Path("logs").glob("*.log"))
            if not log_files:
                return False
            
            # Check log contains our messages
            log_content = log_files[0].read_text()
            return "smoke_test" in log_content
        
        self.test("Logging system", test)
    
    def test_input_validation(self):
        """Test input validation works."""
        section("INPUT VALIDATION")
        
        def test():
            from obs_plugin_manager.validators import (
                sanitize_plugin_name,
                sanitize_version_string,
                validate_plugin_name,
                validate_url
            )
            
            # Test sanitization
            safe_name = sanitize_plugin_name("../../etc/passwd")
            if ".." in safe_name or "/" in safe_name:
                return False
            
            # Test validation
            valid, _ = validate_plugin_name("valid-plugin")
            if not valid:
                return False
            
            invalid, _ = validate_plugin_name("../../bad")
            if invalid:
                return False
            
            # Test URL validation
            valid_url, _ = validate_url("https://github.com/test")
            if not valid_url:
                return False
            
            bad_url, _ = validate_url("file:///etc/passwd")
            if bad_url:
                return False
            
            return True
        
        self.test("Input validation", test)
    
    def test_local_repository(self):
        """Test local repository works."""
        section("LOCAL REPOSITORY")
        
        def test():
            from obs_plugin_manager.local_repository import LocalRepository
            
            # Create test repo
            repo = LocalRepository(str(self.test_dir / "repo"))
            
            # Test stats
            stats = repo.get_repository_stats()
            if not isinstance(stats, dict):
                return False
            
            # Test list operations
            plugins = repo.list_all_plugins()
            scripts = repo.list_all_scripts()
            
            if not isinstance(plugins, list) or not isinstance(scripts, list):
                return False
            
            return True
        
        self.test("Local repository", test)
    
    def test_database(self):
        """Test database operations."""
        section("DATABASE OPERATIONS")
        
        def test():
            from obs_plugin_manager.database import PluginDatabase
            
            # Create test DB
            db = PluginDatabase(str(self.test_dir / "test.db"))
            
            # Test catalog operations
            success = db.add_plugin_to_catalog(
                name="test-plugin",
                display_name="Test Plugin",
                description="Test",
                author="Test Author"
            )
            
            if not success:
                return False
            
            # Retrieve catalog
            plugins = db.get_catalog_plugins()
            if not plugins:
                return False
            
            # Check our plugin is there
            found = any(p['name'] == 'test-plugin' for p in plugins)
            
            db.close()
            return found
        
        self.test("Database operations", test)
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        section("THREAD SAFETY")
        
        def test():
            from obs_plugin_manager.safe_cache import ThreadSafeCache
            from datetime import timedelta
            from concurrent.futures import ThreadPoolExecutor
            
            cache = ThreadSafeCache(
                self.test_dir / "thread_test.json",
                expiry=timedelta(hours=1)
            )
            
            # Test concurrent writes
            def write_value(i):
                cache.set(f"key_{i}", f"value_{i}")
                return True
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(write_value, range(10)))
            
            if not all(results):
                return False
            
            # Verify all values written
            for i in range(10):
                value = cache.get(f"key_{i}")
                if value != f"value_{i}":
                    return False
            
            return True
        
        self.test("Thread-safe cache", test)
    
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        section("ERROR RECOVERY")
        
        def test():
            from obs_plugin_manager.local_repository import LocalRepository
            
            # Create corrupted index
            repo_dir = self.test_dir / "corrupted_repo"
            repo_dir.mkdir(parents=True, exist_ok=True)
            
            index_file = repo_dir / "repository_index.json"
            index_file.write_text("{ invalid json }")
            
            # Try to load - should recover
            repo = LocalRepository(str(repo_dir))
            
            # Should have valid structure despite corruption
            if not isinstance(repo.index, dict):
                return False
            
            if "plugins" not in repo.index or "scripts" not in repo.index:
                return False
            
            # Check backup was created
            backup_files = list(repo_dir.glob("*.corrupted"))
            return len(backup_files) > 0
        
        self.test("Error recovery", test)
    
    def test_atomic_operations(self):
        """Test atomic file operations."""
        section("ATOMIC OPERATIONS")
        
        def test():
            from obs_plugin_manager.local_repository import LocalRepository
            
            repo = LocalRepository(str(self.test_dir / "atomic_test"))
            
            # Save multiple times rapidly
            for i in range(5):
                repo._save_index()
            
            # Check no temp files left
            temp_files = list((self.test_dir / "atomic_test").glob("*.tmp"))
            if temp_files:
                return False
            
            # Check index is valid JSON
            with open(repo.index_file, 'r') as f:
                data = json.load(f)
            
            return isinstance(data, dict)
        
        self.test("Atomic file operations", test)
    
    def test_integration(self):
        """Test components work together."""
        section("INTEGRATION TEST")
        
        def test():
            from obs_plugin_manager.database import PluginDatabase
            from obs_plugin_manager.local_repository import LocalRepository
            from obs_plugin_manager.validators import sanitize_plugin_name
            
            # Create components
            db = PluginDatabase(str(self.test_dir / "integration.db"))
            repo = LocalRepository(str(self.test_dir / "integration_repo"))
            
            # Simulate workflow
            plugin_name = "test-plugin-123"
            safe_name = sanitize_plugin_name(plugin_name)
            
            # Add to catalog
            db.add_plugin_to_catalog(
                name=safe_name,
                display_name="Test Plugin",
                description="Integration test"
            )
            
            # Verify in database
            plugins = db.get_catalog_plugins()
            found = any(p['name'] == safe_name for p in plugins)
            
            db.close()
            return found
        
        self.test("Component integration", test)
    
    def test_log_file_rotation(self):
        """Test log file is properly formatted."""
        section("LOG FILE VALIDATION")
        
        def test():
            log_files = list(Path("logs").glob("*.log"))
            if not log_files:
                return False
            
            # Check log format
            log_content = log_files[0].read_text()
            
            # Should have timestamps
            if "2025-12-14" not in log_content:
                return False
            
            # Should have module names
            if "OBSPluginManager" not in log_content:
                return False
            
            # Should have file names
            if ".py:" not in log_content:
                return False
            
            return True
        
        self.test("Log file format", test)
    
    def run_all(self):
        """Run all smoke tests."""
        print(f"\n{BOLD}COMPREHENSIVE SMOKE TEST SUITE{RESET}")
        print(f"{BOLD}Testing ALL components together...{RESET}\n")
        
        # Setup
        self.test_dir.mkdir(exist_ok=True)
        
        try:
            # Run all tests
            self.test_logging_system()
            self.test_input_validation()
            self.test_local_repository()
            self.test_database()
            self.test_thread_safety()
            self.test_error_recovery()
            self.test_atomic_operations()
            self.test_integration()
            self.test_log_file_rotation()
            
        finally:
            # Cleanup
            self.cleanup()
        
        # Summary
        section("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for _, result, _ in self.results if result)
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"Success rate: {passed/total*100:.1f}%\n")
        
        # Details
        if failed > 0:
            print(f"{RED}Failed tests:{RESET}")
            for name, result, error in self.results:
                if not result:
                    print(f"  {RED}✗{RESET} {name}: {error}")
        
        print()
        
        if passed == total:
            print(f"{GREEN}{BOLD}✅ ALL SMOKE TESTS PASSED!{RESET}")
            print(f"{GREEN}The integrated components are working correctly.{RESET}")
            return 0
        else:
            print(f"{YELLOW}{BOLD}⚠ {failed} TEST(S) FAILED{RESET}")
            print(f"{YELLOW}Some components need attention.{RESET}")
            return 1

def main():
    """Main entry point."""
    tester = SmokeTest()
    return tester.run_all()

if __name__ == "__main__":
    sys.exit(main())
