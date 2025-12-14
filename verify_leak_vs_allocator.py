"""
Verify if memory leaks are real or just Python's allocator behavior

Test with MANY more iterations to see if memory grows linearly (leak)
or stabilizes (allocator keeping pages).
"""

import sys
import tracemalloc
import gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_cache_extended():
    """Test cache with many iterations to detect true leak."""
    from obs_plugin_manager.safe_cache import ThreadSafeCache
    from datetime import timedelta
    
    print("Testing Cache with 200 iterations...")
    print("-" * 60)
    
    gc.collect()
    tracemalloc.start()
    
    memory_samples = []
    
    for i in range(200):
        with ThreadSafeCache("leak_cache.json", timedelta(hours=1)) as cache:
            for j in range(10):
                cache.set(f"key_{j}", {"data": "x" * 1000})
        
        # Sample memory every 20 iterations
        if i % 20 == 0:
            current, peak = tracemalloc.get_traced_memory()
            memory_samples.append(current / 1024 / 1024)
            print(f"Iteration {i:3d}: {current/1024/1024:.3f} MB")
    
    tracemalloc.stop()
    
    # Analyze growth pattern
    print(f"\nMemory samples: {memory_samples}")
    
    if len(memory_samples) >= 3:
        first_half = memory_samples[:len(memory_samples)//2]
        second_half = memory_samples[len(memory_samples)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        print(f"\nFirst half average: {avg_first:.3f} MB")
        print(f"Second half average: {avg_second:.3f} MB")
        
        growth_rate = (avg_second - avg_first) / avg_first * 100
        print(f"Growth rate: {growth_rate:.1f}%")
        
        if growth_rate < 10:
            print("\n✓ Memory STABLE - This is normal Python allocator behavior")
            print("  (Python keeps memory pages for reuse, not a real leak)")
            return False  # No leak
        else:
            print(f"\n❌ Memory GROWING {growth_rate:.1f}% - Real leak detected!")
            return True  # Real leak
    
    # Cleanup
    Path("leak_cache.json").unlink(missing_ok=True)

def test_database_extended():
    """Test database with many iterations."""
    from obs_plugin_manager.database import PluginDatabase
    
    print("\n\nTesting Database with 200 iterations...")
    print("-" * 60)
    
    gc.collect()
    tracemalloc.start()
    
    memory_samples = []
    
    for i in range(200):
        with PluginDatabase("leak_test.db") as db:
            db.add_plugin_to_catalog(
                name=f"test-plugin-{i}",
                display_name="Test",
                description="Test",
                author="Test"
            )
            plugins = db.get_catalog_plugins()
        
        if i % 20 == 0:
            current, peak = tracemalloc.get_traced_memory()
            memory_samples.append(current / 1024 / 1024)
            print(f"Iteration {i:3d}: {current/1024/1024:.3f} MB")
    
    tracemalloc.stop()
    
    # Analyze
    print(f"\nMemory samples: {memory_samples}")
    
    if len(memory_samples) >= 3:
        first_half = memory_samples[:len(memory_samples)//2]
        second_half = memory_samples[len(memory_samples)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        print(f"\nFirst half average: {avg_first:.3f} MB")
        print(f"Second half average: {avg_second:.3f} MB")
        
        growth_rate = (avg_second - avg_first) / avg_first * 100
        print(f"Growth rate: {growth_rate:.1f}%")
        
        if growth_rate < 10:
            print("\n✓ Memory STABLE - Normal allocator behavior")
            return False
        else:
            print(f"\n❌ Memory GROWING {growth_rate:.1f}% - Real leak!")
            return True
    
    # Cleanup
    Path("leak_test.db").unlink(missing_ok=True)

def main():
    print("="*70)
    print("EXTENDED MEMORY LEAK VERIFICATION")
    print("="*70)
    print("\nTesting with 200 iterations to distinguish:")
    print("  - Real leak: Memory grows linearly")
    print("  - Allocator: Memory stabilizes after initial growth")
    print()
    
    cache_leak = test_cache_extended()
    db_leak = test_database_extended()
    
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    
    if cache_leak:
        print("❌ Cache: REAL LEAK DETECTED")
    else:
        print("✓ Cache: Normal behavior (allocator keeping pages)")
    
    if db_leak:
        print("❌ Database: REAL LEAK DETECTED")
    else:
        print("✓ Database: Normal behavior (allocator keeping pages)")
    
    if not cache_leak and not db_leak:
        print("\n🎉 NO REAL LEAKS! Memory growth is just Python's allocator.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
