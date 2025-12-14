"""
Integration Tests - Verify that logging and validation are actually working
"""

import sys
from pathlib import Path
import shutil
import json

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_logging_integration():
    """Test that logging is working in integrated modules."""
    print("Testing logging integration...")
    
    # Clean up any existing logs
    log_dir = Path("logs")
    if log_dir.exists():
        shutil.rmtree(log_dir)
    
    try:
        # Import module (should initialize logger)
        from obs_plugin_manager.local_repository import LocalRepository
        from obs_plugin_manager.discovery import PluginDiscovery
        from obs_plugin_manager.obs_resources import OBSResourcesFetcher
        
        # Initialize modules (should log)
        repo = LocalRepository("test_integration_repo")
        discovery = PluginDiscovery("test_integration_discovery")
        obs = OBSResourcesFetcher("test_integration_obs")
        
        # Check if log file was created
        log_files = list(log_dir.glob("obs_plugin_manager_*.log"))
        
        if log_files:
            print(f"  ✓ Log file created: {log_files[0].name}")
            
            # Read log content
            log_content = log_files[0].read_text()
            
            # Check for expected log entries
            if "initialized" in log_content.lower():
                print(f"  ✓ Initialization logged")
            else:
                print(f"  ✗ No initialization log found")
                return False
            
            if "OBSPluginManager" in log_content:
                print(f"  ✓ Logger name correct")
            else:
                print(f"  ✗ Logger name not found")
                return False
            
            # Show sample log line
            lines = log_content.split('\n')
            for line in lines[:5]:
                if line.strip():
                    print(f"  Sample: {line[:100]}")
                    break
            
            return True
        else:
            print(f"  ✗ No log file created")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for test_dir in ["test_integration_repo", "test_integration_discovery", "test_integration_obs"]:
            if Path(test_dir).exists():
                shutil.rmtree(test_dir)


def test_validation_integration():
    """Test that input validation is working."""
    print("\nTesting input validation integration...")
    
    try:
        from obs_plugin_manager.local_repository import LocalRepository
        from obs_plugin_manager.validators import sanitize_plugin_name
        
        # Test cases
        test_cases = [
            ("valid-plugin", "valid-plugin", True),
            ("../../etc/passwd", "etcpasswd", True),  # Path traversal prevented (.. removed completely)
            ("my plugin", "my-plugin", True),  # Spaces replaced
            ("plugin<>name", "pluginname", True),  # Invalid chars removed
        ]
        
        passed = 0
        for input_name, expected, should_sanitize in test_cases:
            sanitized = sanitize_plugin_name(input_name)
            if sanitized == expected:
                print(f"  ✓ '{input_name}' → '{sanitized}'")
                passed += 1
            else:
                print(f"  ✗ '{input_name}' → '{sanitized}' (expected '{expected}')")
        
        print(f"\n  Validation: {passed}/{len(test_cases)} tests passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_atomic_operations():
    """Test that atomic file operations work."""
    print("\nTesting atomic file operations...")
    
    try:
        from obs_plugin_manager.local_repository import LocalRepository
        
        # Create test repository
        repo = LocalRepository("test_atomic_repo")
        
        # Save initial state
        repo._save_index()
        
        # Check if temp file is NOT left behind
        temp_files = list(Path("test_atomic_repo").glob("*.tmp"))
        
        if not temp_files:
            print(f"  ✓ No temp files left behind")
        else:
            print(f"  ✗ Temp files found: {temp_files}")
            return False
        
        # Check if actual file exists
        if repo.index_file.exists():
            print(f"  ✓ Index file created: {repo.index_file}")
        else:
            print(f"  ✗ Index file not created")
            return False
        
        # Verify it's valid JSON
        with open(repo.index_file, 'r') as f:
            data = json.load(f)
            print(f"  ✓ Valid JSON structure")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if Path("test_atomic_repo").exists():
            shutil.rmtree("test_atomic_repo")


def test_error_recovery():
    """Test that corrupted files are recovered gracefully."""
    print("\nTesting error recovery...")
    
    try:
        from obs_plugin_manager.local_repository import LocalRepository
        
        # Create repository
        test_dir = Path("test_recovery_repo")
        test_dir.mkdir(exist_ok=True)
        
        # Create corrupted index file
        index_file = test_dir / "repository_index.json"
        index_file.write_text("{ invalid json }")
        
        print(f"  Created corrupted file: {index_file}")
        
        # Try to load (should recover gracefully)
        repo = LocalRepository(str(test_dir))
        
        # Check if backup was created
        backup_files = list(test_dir.glob("*.corrupted"))
        
        if backup_files:
            print(f"  ✓ Backup created: {backup_files[0].name}")
        else:
            print(f"  ⚠ No backup created (might not have triggered)")
        
        # Check if repository still works
        if repo.index is not None and "plugins" in repo.index:
            print(f"  ✓ Repository recovered with default structure")
            return True
        else:
            print(f"  ✗ Repository not properly recovered")
            return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if Path("test_recovery_repo").exists():
            shutil.rmtree("test_recovery_repo")


def main():
    """Run all integration tests."""
    print("="*70)
    print("INTEGRATION TEST SUITE")
    print("="*70)
    print("\nVerifying that infrastructure is actually working...")
    print()
    
    results = []
    
    # Run tests
    results.append(("Logging Integration", test_logging_integration()))
    results.append(("Validation Integration", test_validation_integration()))
    results.append(("Atomic Operations", test_atomic_operations()))
    results.append(("Error Recovery", test_error_recovery()))
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST RESULTS")
    print("="*70)
    
    passed = 0
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(results)} integration tests passed")
    
    if passed == len(results):
        print("\n✅ All integration tests passed!")
        print("Infrastructure is properly integrated and working!")
        return 0
    else:
        print(f"\n⚠ {len(results) - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
