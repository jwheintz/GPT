"""
Test if the "database leak" is actually just the database file growing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_db_file_size():
    """Check if database 'leak' is actually file growth."""
    from obs_plugin_manager.database import PluginDatabase
    import os
    
    db_file = Path("leak_test.db")
    db_file.unlink(missing_ok=True)
    
    print("Testing database file growth...")
    print("-" * 60)
    
    # Add 200 plugins
    for i in range(200):
        with PluginDatabase("leak_test.db") as db:
            db.add_plugin_to_catalog(
                name=f"test-plugin-{i}",  # Unique name
                display_name="Test",
                description="Test plugin description here",
                author="Test Author"
            )
        
        if i % 50 == 0:
            file_size = db_file.stat().st_size / 1024
            print(f"After {i:3d} plugins: {file_size:.2f} KB")
    
    final_size = db_file.stat().st_size / 1024
    print(f"\nFinal database file size: {final_size:.2f} KB")
    print(f"Per plugin: {final_size / 200:.3f} KB")
    
    # Now test with SAME plugin (update, not insert)
    print("\n" + "-" * 60)
    print("Testing with SAME plugin (should not grow)...")
    
    db_file2 = Path("leak_test2.db")
    db_file2.unlink(missing_ok=True)
    
    for i in range(200):
        with PluginDatabase("leak_test2.db") as db:
            db.add_plugin_to_catalog(
                name="test-plugin",  # SAME name
                display_name="Test",
                description="Test",
                author="Test"
            )
        
        if i % 50 == 0:
            file_size2 = db_file2.stat().st_size / 1024
            print(f"After {i:3d} updates: {file_size2:.2f} KB")
    
    final_size2 = db_file2.stat().st_size / 1024
    print(f"\nFinal size (200 updates of same plugin): {final_size2:.2f} KB")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print(f"200 unique plugins: {final_size:.2f} KB")
    print(f"200 updates of same: {final_size2:.2f} KB")
    
    if final_size > final_size2 * 10:
        print("\n✓ The 'leak' is DATABASE FILE GROWTH, not a memory leak!")
        print("  (Adding 200 plugins naturally increases file size)")
    else:
        print("\n⚠️  Hmm, file sizes are similar. Might be real leak.")
    
    # Cleanup
    db_file.unlink(missing_ok=True)
    db_file2.unlink(missing_ok=True)

if __name__ == "__main__":
    test_db_file_size()
