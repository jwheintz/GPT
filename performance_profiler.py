"""
Performance Profiler - Find bottlenecks and optimization opportunities

This tests PERFORMANCE, not just correctness.
"""

import sys
import time
import tracemalloc
from pathlib import Path
import cProfile
import pstats
import io

sys.path.insert(0, str(Path(__file__).parent))

class PerformanceProfiler:
    def __init__(self):
        self.results = []
    
    def profile_function(self, name, func, *args, **kwargs):
        """Profile a function's performance."""
        print(f"\nProfiling: {name}")
        print("-" * 60)
        
        # Memory profiling
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        # Time profiling
        start_time = time.time()
        
        # CPU profiling
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
            
            profiler.disable()
            elapsed = time.time() - start_time
            
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            memory_used = (current_memory - start_memory) / 1024 / 1024  # MB
            peak_used = peak_memory / 1024 / 1024  # MB
            
            tracemalloc.stop()
            
            # Get CPU profile stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Top 10 functions
            
            print(f"⏱️  Time: {elapsed:.3f}s")
            print(f"💾 Memory: {memory_used:.2f} MB used, {peak_used:.2f} MB peak")
            
            # Check if slow
            if elapsed > 1.0:
                print(f"⚠️  SLOW: Takes more than 1 second!")
            elif elapsed > 0.1:
                print(f"⚠️  Moderate: Takes more than 100ms")
            else:
                print(f"✓ Fast: Under 100ms")
            
            # Check if memory hungry
            if peak_used > 100:
                print(f"⚠️  MEMORY HOG: Uses more than 100MB!")
            elif peak_used > 10:
                print(f"⚠️  Memory intensive: Uses more than 10MB")
            else:
                print(f"✓ Memory efficient: Under 10MB")
            
            self.results.append({
                'name': name,
                'time': elapsed,
                'memory': memory_used,
                'peak_memory': peak_used,
                'status': 'success'
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append({
                'name': name,
                'time': 0,
                'memory': 0,
                'peak_memory': 0,
                'status': 'error',
                'error': str(e)
            })
            return None
    
    def test_database_performance(self):
        """Test database operation performance."""
        from obs_plugin_manager.database import PluginDatabase
        
        def test():
            db = PluginDatabase("perf_test.db")
            
            # Test bulk insert performance
            for i in range(100):
                db.add_plugin_to_catalog(
                    name=f"plugin-{i}",
                    display_name=f"Plugin {i}",
                    description=f"Test plugin {i}",
                    author="Test"
                )
            
            # Test query performance
            for _ in range(10):
                plugins = db.get_catalog_plugins()
            
            db.close()
            Path("perf_test.db").unlink()
            return len(plugins)
        
        return self.profile_function("Database: 100 inserts + 10 queries", test)
    
    def test_file_operations(self):
        """Test file operation performance."""
        from obs_plugin_manager.local_repository import LocalRepository
        
        def test():
            repo = LocalRepository("perf_repo")
            
            # Test repeated saves (atomic operations)
            for i in range(50):
                repo._save_index()
            
            import shutil
            shutil.rmtree("perf_repo")
            return 50
        
        return self.profile_function("File ops: 50 atomic saves", test)
    
    def test_logging_performance(self):
        """Test logging overhead."""
        from obs_plugin_manager.logger import get_logger
        
        def test():
            logger = get_logger("perf_test")
            
            # Test logging overhead
            for i in range(1000):
                logger.debug(f"Debug message {i}")
                logger.info(f"Info message {i}")
            
            return 1000
        
        return self.profile_function("Logging: 2000 log calls", test)
    
    def test_validation_performance(self):
        """Test input validation overhead."""
        from obs_plugin_manager.validators import (
            sanitize_plugin_name,
            validate_plugin_name,
            sanitize_version_string
        )
        
        def test():
            # Test validation overhead
            for i in range(1000):
                sanitize_plugin_name(f"test-plugin-{i}")
                validate_plugin_name(f"test-plugin-{i}")
                sanitize_version_string(f"1.0.{i}")
            
            return 1000
        
        return self.profile_function("Validation: 3000 validations", test)
    
    def test_cache_performance(self):
        """Test cache operation performance."""
        from obs_plugin_manager.safe_cache import ThreadSafeCache
        from datetime import timedelta
        
        def test():
            cache = ThreadSafeCache("perf_cache.json", timedelta(hours=1))
            
            # Test write performance
            for i in range(100):
                cache.set(f"key_{i}", {"data": f"value_{i}" * 10})
            
            # Test read performance
            for i in range(100):
                cache.get(f"key_{i}")
            
            Path("perf_cache.json").unlink()
            return 100
        
        return self.profile_function("Cache: 100 writes + 100 reads", test)
    
    def analyze_results(self):
        """Analyze and report performance results."""
        print("\n" + "="*70)
        print("PERFORMANCE ANALYSIS SUMMARY")
        print("="*70 + "\n")
        
        total_time = sum(r['time'] for r in self.results if r['status'] == 'success')
        total_memory = sum(r['peak_memory'] for r in self.results if r['status'] == 'success')
        
        print(f"Total execution time: {total_time:.3f}s")
        print(f"Total peak memory: {total_memory:.2f} MB\n")
        
        # Find slowest operations
        slow_ops = sorted(
            [r for r in self.results if r['status'] == 'success'],
            key=lambda x: x['time'],
            reverse=True
        )
        
        print("Slowest operations:")
        for i, op in enumerate(slow_ops[:3], 1):
            print(f"  {i}. {op['name']}: {op['time']:.3f}s")
        
        # Find memory hogs
        memory_ops = sorted(
            [r for r in self.results if r['status'] == 'success'],
            key=lambda x: x['peak_memory'],
            reverse=True
        )
        
        print("\nMemory intensive operations:")
        for i, op in enumerate(memory_ops[:3], 1):
            print(f"  {i}. {op['name']}: {op['peak_memory']:.2f} MB")
        
        # Performance recommendations
        print("\n" + "="*70)
        print("OPTIMIZATION RECOMMENDATIONS")
        print("="*70 + "\n")
        
        recommendations = []
        
        for r in self.results:
            if r['status'] != 'success':
                continue
            
            if r['time'] > 1.0:
                recommendations.append(
                    f"⚠️  {r['name']} is slow ({r['time']:.3f}s) - consider optimization"
                )
            
            if r['peak_memory'] > 10:
                recommendations.append(
                    f"⚠️  {r['name']} uses significant memory ({r['peak_memory']:.2f} MB)"
                )
        
        if recommendations:
            for rec in recommendations:
                print(rec)
        else:
            print("✓ All operations are reasonably fast and memory-efficient!")
        
        # Calculate performance score
        fast_ops = sum(1 for r in self.results if r['status'] == 'success' and r['time'] < 0.1)
        efficient_ops = sum(1 for r in self.results if r['status'] == 'success' and r['peak_memory'] < 10)
        total_ops = sum(1 for r in self.results if r['status'] == 'success')
        
        if total_ops > 0:
            speed_score = (fast_ops / total_ops) * 100
            memory_score = (efficient_ops / total_ops) * 100
            overall_score = (speed_score + memory_score) / 2
            
            print(f"\nPerformance Scores:")
            print(f"  Speed: {speed_score:.1f}% operations under 100ms")
            print(f"  Memory: {memory_score:.1f}% operations under 10MB")
            print(f"  Overall: {overall_score:.1f}%")
            
            if overall_score >= 80:
                print(f"\n✓ Excellent performance!")
            elif overall_score >= 60:
                print(f"\n⚠️  Good performance, some optimization possible")
            else:
                print(f"\n⚠️  Performance needs improvement")
    
    def run_all(self):
        """Run all performance tests."""
        print("="*70)
        print("PERFORMANCE PROFILING SUITE")
        print("="*70)
        print("\nTesting performance of integrated components...\n")
        
        # Run tests
        self.test_logging_performance()
        self.test_validation_performance()
        self.test_database_performance()
        self.test_file_operations()
        self.test_cache_performance()
        
        # Analyze
        self.analyze_results()

def main():
    profiler = PerformanceProfiler()
    profiler.run_all()
    return 0

if __name__ == "__main__":
    sys.exit(main())
