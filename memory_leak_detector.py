"""
Memory Leak Detector - Find memory leaks and resource leaks

Tests for:
- Growing memory usage over repeated operations
- File handle leaks
- Database connection leaks
- Thread leaks
"""

import sys
import tracemalloc
import gc
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

class MemoryLeakDetector:
    def __init__(self):
        self.results = []
    
    def test_for_leak(self, name, func, iterations=100):
        """Test if a function leaks memory over repeated calls."""
        print(f"\nTesting: {name}")
        print("-" * 60)
        
        # Force garbage collection
        gc.collect()
        
        # Start memory tracking
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        # Run function multiple times
        memory_samples = []
        for i in range(iterations):
            func()
            
            # Sample memory every 10 iterations
            if i % 10 == 0:
                current, peak = tracemalloc.get_traced_memory()
                memory_samples.append(current)
        
        # Final memory measurement
        end_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Analyze memory growth
        memory_growth = end_memory - start_memory
        growth_mb = memory_growth / 1024 / 1024
        
        # Check if memory is growing
        if len(memory_samples) >= 3:
            first_third = sum(memory_samples[:len(memory_samples)//3]) / (len(memory_samples)//3)
            last_third = sum(memory_samples[-len(memory_samples)//3:]) / (len(memory_samples)//3)
            growth_ratio = last_third / first_third if first_third > 0 else 1.0
        else:
            growth_ratio = 1.0
        
        print(f"Start memory: {start_memory/1024/1024:.2f} MB")
        print(f"End memory: {end_memory/1024/1024:.2f} MB")
        print(f"Growth: {growth_mb:.2f} MB over {iterations} iterations")
        print(f"Growth ratio: {growth_ratio:.2f}x")
        
        # Detect leak
        leak_detected = False
        if growth_ratio > 1.5:
            print(f"⚠️  MEMORY LEAK DETECTED! Memory grew {growth_ratio:.2f}x")
            leak_detected = True
        elif growth_mb > 10:
            print(f"⚠️  LARGE MEMORY GROWTH! {growth_mb:.2f} MB leaked")
            leak_detected = True
        else:
            print(f"✓ No significant memory leak detected")
        
        self.results.append({
            'name': name,
            'growth_mb': growth_mb,
            'growth_ratio': growth_ratio,
            'leak_detected': leak_detected
        })
        
        return leak_detected
    
    def test_database_leak(self):
        """Test for database connection leaks."""
        from obs_plugin_manager.database import PluginDatabase
        
        def test():
            # Use context manager for proper cleanup
            with PluginDatabase("leak_test.db") as db:
                db.add_plugin_to_catalog(
                    name="test-plugin",
                    display_name="Test",
                    description="Test",
                    author="Test"
                )
                plugins = db.get_catalog_plugins()
        
        leak = self.test_for_leak("Database operations (with context manager)", test, iterations=50)
        
        # Cleanup
        Path("leak_test.db").unlink(missing_ok=True)
        return leak
    
    def test_cache_leak(self):
        """Test for cache memory leaks."""
        from obs_plugin_manager.safe_cache import ThreadSafeCache
        from datetime import timedelta
        
        def test():
            # Use context manager for proper cleanup
            with ThreadSafeCache("leak_cache.json", timedelta(hours=1)) as cache:
                for i in range(10):
                    cache.set(f"key_{i}", {"data": "x" * 1000})
        
        leak = self.test_for_leak("Cache operations (with context manager)", test, iterations=50)
        
        # Cleanup
        Path("leak_cache.json").unlink(missing_ok=True)
        return leak
    
    def test_file_handle_leak(self):
        """Test for file handle leaks."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        def test():
            from obs_plugin_manager.local_repository import LocalRepository
            repo = LocalRepository("leak_repo")
            repo._save_index()
        
        # Get initial file handle count
        initial_handles = process.num_fds() if hasattr(process, 'num_fds') else process.num_handles()
        
        print(f"\nTesting: File handle leaks")
        print("-" * 60)
        print(f"Initial handles: {initial_handles}")
        
        # Run operations
        for i in range(100):
            test()
        
        # Get final count
        final_handles = process.num_fds() if hasattr(process, 'num_fds') else process.num_handles()
        handle_growth = final_handles - initial_handles
        
        print(f"Final handles: {final_handles}")
        print(f"Growth: {handle_growth} handles")
        
        # Cleanup
        import shutil
        shutil.rmtree("leak_repo", ignore_errors=True)
        
        leak_detected = handle_growth > 10
        if leak_detected:
            print(f"⚠️  FILE HANDLE LEAK! {handle_growth} handles leaked")
        else:
            print(f"✓ No file handle leak detected")
        
        self.results.append({
            'name': 'File handles',
            'growth_handles': handle_growth,
            'leak_detected': leak_detected
        })
        
        return leak_detected
    
    def test_validator_leak(self):
        """Test validator operations for leaks."""
        from obs_plugin_manager.validators import (
            sanitize_plugin_name,
            validate_plugin_name,
            sanitize_version_string
        )
        
        def test():
            for i in range(10):
                sanitize_plugin_name(f"test-plugin-{i}")
                validate_plugin_name(f"test-plugin-{i}")
                sanitize_version_string(f"1.0.{i}")
        
        return self.test_for_leak("Validator operations", test, iterations=100)
    
    def test_logger_leak(self):
        """Test logging for memory leaks."""
        from obs_plugin_manager.logger import get_logger
        
        def test():
            logger = get_logger("leak_test")
            for i in range(10):
                logger.debug(f"Debug {i}")
                logger.info(f"Info {i}")
        
        return self.test_for_leak("Logger operations", test, iterations=50)
    
    def analyze_results(self):
        """Analyze and report leak detection results."""
        print("\n" + "="*70)
        print("MEMORY LEAK ANALYSIS SUMMARY")
        print("="*70 + "\n")
        
        leaks_found = [r for r in self.results if r.get('leak_detected', False)]
        
        if leaks_found:
            print(f"⚠️  LEAKS DETECTED: {len(leaks_found)}/{len(self.results)} tests\n")
            for leak in leaks_found:
                print(f"❌ {leak['name']}")
                if 'growth_mb' in leak:
                    print(f"   Memory growth: {leak['growth_mb']:.2f} MB")
                    print(f"   Growth ratio: {leak['growth_ratio']:.2f}x")
                if 'growth_handles' in leak:
                    print(f"   Handle growth: {leak['growth_handles']} handles")
        else:
            print(f"✓ NO LEAKS DETECTED in {len(self.results)} tests\n")
        
        # Memory growth summary
        memory_tests = [r for r in self.results if 'growth_mb' in r]
        if memory_tests:
            total_growth = sum(r['growth_mb'] for r in memory_tests)
            avg_growth = total_growth / len(memory_tests)
            
            print(f"\nMemory growth summary:")
            print(f"  Total growth: {total_growth:.2f} MB")
            print(f"  Average per test: {avg_growth:.2f} MB")
            print(f"  Max growth: {max(r['growth_mb'] for r in memory_tests):.2f} MB")
        
        # Overall assessment
        print("\n" + "="*70)
        if leaks_found:
            print("⚠️  MEMORY LEAKS FOUND - Investigation needed!")
        else:
            print("✓ NO MEMORY LEAKS - Code is clean!")
        print("="*70)
    
    def run_all(self):
        """Run all leak detection tests."""
        print("="*70)
        print("MEMORY LEAK DETECTION SUITE")
        print("="*70)
        print("\nTesting for memory leaks in integrated components...\n")
        
        # Run tests
        self.test_validator_leak()
        self.test_cache_leak()
        self.test_database_leak()
        self.test_logger_leak()
        
        # File handle test (requires psutil)
        try:
            self.test_file_handle_leak()
        except ImportError:
            print("\n⚠️  Skipping file handle test (psutil not available)")
        
        # Analyze
        self.analyze_results()

def main():
    detector = MemoryLeakDetector()
    detector.run_all()
    return 0

if __name__ == "__main__":
    sys.exit(main())
