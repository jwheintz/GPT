# Developer Guide - OBS Plugin Manager v2.0

## For Developers Who Want to Extend or Modify

### Quick Start for Developers

```bash
# 1. Clone/download the project
cd obs-plugin-manager

# 2. Install in development mode
pip install -e .

# 3. Install dev dependencies
pip install -r requirements.txt

# 4. Run tests
python test_basic.py
python test_v2_features.py

# 5. Launch
python obs_plugin_manager.py
```

## Project Architecture

### Module Dependency Graph

```
obs_plugin_manager.py (entry point)
         ↓
    gui.py (main application)
         ↓
    ┌────┴────┬────────┬─────────┬──────────┐
    ↓         ↓        ↓         ↓          ↓
database   obs_mgr  scanner  installer  discovery
    ↓                              ↓          ↓
    └──────────────────────────────┴─────→ local_repo
                                      ↓
                                 obs_resources
```

### Data Flow

```
User Action (GUI)
    ↓
Business Logic (Core Modules)
    ↓
Data Layer (Database, Files)
    ↓
External APIs (GitHub, OBS Site)
    ↓
Cache Layer
    ↓
Display (GUI Update)
```

## Module Deep Dive

### 1. database.py - Data Persistence

**Purpose**: SQLite database for plugin metadata

**Key Classes**:
- `PluginDatabase` - Main database interface

**Tables**:
```sql
plugin_catalog        -- Known plugins
installed_plugins     -- Currently installed
plugin_archives      -- Backup versions
installation_history -- Operation log
```

**Adding a New Table**:
```python
def _create_tables(self):
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS my_new_table (
            id INTEGER PRIMARY KEY,
            field1 TEXT,
            field2 INTEGER
        )
    """)
    self.conn.commit()
```

### 2. obs_manager.py - OBS Control

**Purpose**: Detect and control OBS process

**Key Methods**:
- `is_obs_installed()` - Check if OBS exists
- `is_obs_running()` - Check if OBS is active
- `kill_obs()` - Terminate OBS safely
- `get_plugin_directories()` - Find plugin folders

**Adding OBS Detection Method**:
```python
def _detect_obs_custom(self):
    # Add your custom detection logic
    custom_path = Path(r"C:\My\Custom\Path")
    if custom_path.exists():
        self.obs_path = custom_path
        return True
    return False
```

### 3. plugin_scanner.py - Plugin Detection

**Purpose**: Scan OBS directories for plugins

**Key Methods**:
- `scan_plugins()` - Main scan operation
- `_analyze_plugin_file()` - Extract plugin info
- `_extract_version_from_file()` - Get version
- `get_plugin_files()` - Find related files

**Adding Version Detection Method**:
```python
def _extract_version_custom(self, file_path):
    # Your custom version extraction
    # Return version string or None
    return version_string
```

### 4. plugin_repository.py - Plugin Catalog

**Purpose**: Maintain list of known plugins

**Adding a Plugin to Catalog**:
```python
POPULAR_PLUGINS.append({
    "name": "my-new-plugin",
    "display_name": "My New Plugin",
    "description": "What it does",
    "author": "Author Name",
    "category": "Effects",  # Or Sources, Integration, etc.
    "homepage_url": "https://github.com/author/plugin",
    "download_url": "https://github.com/author/plugin/releases/latest",
    "is_recommended": False  # True for highly trusted plugins
})
```

### 5. plugin_installer.py - Installation Manager

**Purpose**: Install, remove, and rollback plugins

**Key Operations**:
```python
# Download
download_plugin(url, name)

# Install
install_plugin_files(files, name, backup=True)

# Remove
remove_plugin(plugin_info, create_backup=True)

# Rollback
restore_from_archive(archive_path, name)
```

**Adding Pre-Install Hook**:
```python
def install_plugin_files(self, ...):
    # Add your pre-install logic here
    self._pre_install_hook(plugin_files)
    
    # Existing install logic
    ...
```

### 6. local_repository.py - Local Storage

**Purpose**: Store downloaded plugins locally

**Key Methods**:
- `add_plugin_file()` - Store a plugin file
- `get_plugin_versions()` - List stored versions
- `cleanup_orphaned_files()` - Remove unused files

**Extending Storage**:
```python
def add_custom_metadata(self, plugin_name, metadata):
    # Add custom metadata to repository
    if plugin_name in self.index["plugins"]:
        self.index["plugins"][plugin_name]["custom"] = metadata
        self._save_index()
```

### 7. discovery.py - Multi-Source Discovery

**Purpose**: Find plugins from GitHub and OBS site

**Key Methods**:
- `discover_new_plugins()` - Recently updated (GitHub)
- `discover_popular_plugins()` - Most starred (GitHub)
- `discover_trending_plugins()` - Fast-growing (GitHub)
- `discover_obs_website_plugins()` - From OBS Resources
- `discover_combined_popular()` - Both sources

**Adding Custom Discovery Source**:
```python
def discover_custom_source(self, max_results=20):
    cache_key = "custom_source"
    
    if not self._is_cache_valid(cache_key):
        # Query your custom source
        plugins = self._fetch_from_custom_source()
        
        # Cache results
        self.cache[cache_key] = {
            "cached_at": datetime.now().isoformat(),
            "results": plugins
        }
        self._save_cache()
    
    return self.cache[cache_key]["results"][:max_results]
```

### 8. obs_resources.py - OBS Website Scraping

**Purpose**: Parse OBS Resources page

**Key Methods**:
- `fetch_obs_plugins()` - Get plugins from OBS site
- `fetch_obs_scripts()` - Get scripts from OBS site
- `_parse_resource_item()` - Parse HTML item

**Updating Parser** (if OBS site changes):
```python
def _parse_resource_item(self, item, resource_type):
    # Update selectors if OBS changes HTML structure
    title_elem = item.find('a', class_='NEW_CLASS_NAME')
    # ... update other selectors as needed
```

### 9. gui.py - User Interface

**Purpose**: Tkinter-based GUI application

**Adding a New Tab**:
```python
def _setup_ui(self):
    # ... existing code ...
    self._create_my_new_tab()

def _create_my_new_tab(self):
    frame = ttk.Frame(self.notebook)
    self.notebook.add(frame, text="My Tab")
    
    # Add widgets to frame
    ttk.Label(frame, text="My Content").pack()
```

**Adding a Menu Item**:
```python
def _setup_ui(self):
    # ... existing menu setup ...
    
    my_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="My Menu", menu=my_menu)
    my_menu.add_command(label="My Action", command=self._my_action)

def _my_action(self):
    # Your action here
    messagebox.showinfo("My Action", "Action executed!")
```

## Testing

### Unit Tests

```python
# test_my_feature.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from obs_plugin_manager.my_module import MyClass

def test_my_feature():
    obj = MyClass()
    result = obj.my_method()
    assert result == expected_value
    print("✓ Test passed")

if __name__ == "__main__":
    test_my_feature()
```

### Integration Tests

```python
def test_full_workflow():
    # Initialize components
    db = PluginDatabase("test.db")
    repo = LocalRepository("test_repo")
    
    # Test workflow
    # ...
    
    # Cleanup
    Path("test.db").unlink()
    shutil.rmtree("test_repo")
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message here")
```

### Common Issues

**Import Errors**:
```bash
# Make sure you're using relative imports
from .module import Class  # Correct
from module import Class   # Wrong (in package)
```

**GUI Not Updating**:
```python
# Use root.after() to update from threads
self.root.after(0, self._update_ui)
```

**Database Locked**:
```python
# Ensure connections are closed
try:
    # database operations
finally:
    db.close()
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    my_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 slowest
```

### Optimization Tips

1. **Cache Aggressively**: Don't query APIs repeatedly
2. **Use Threading**: Long operations should be threaded
3. **Lazy Loading**: Don't load data until needed
4. **Batch Operations**: Group database operations
5. **Stream Large Files**: Don't load entirely into memory

## Security Best Practices

### Input Validation

```python
def validate_plugin_name(name):
    # Only allow alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError("Invalid plugin name")
    return name
```

### SQL Injection Prevention

```python
# NEVER do this:
cursor.execute(f"SELECT * FROM plugins WHERE name = '{name}'")

# ALWAYS do this:
cursor.execute("SELECT * FROM plugins WHERE name = ?", (name,))
```

### File Path Safety

```python
# Use Path objects
from pathlib import Path

plugin_path = Path(base_dir) / user_input
# Path automatically handles traversal attempts
```

## Extending Functionality

### Adding a New Discovery Source

1. Create new fetcher in `discovery.py`:
```python
def discover_my_source(self, max_results=20):
    # Implementation
    pass
```

2. Add to GUI in `gui.py`:
```python
# Add radio button
ttk.Radiobutton(toolbar, text="My Source", 
                variable=self.discovery_source, 
                value="my_source").pack()

# Update refresh logic
if source == "my_source":
    plugins = self.discovery.discover_my_source()
```

### Adding a New Plugin Category

1. Update `plugin_repository.py`:
```python
def _determine_category(self, name, description):
    # ... existing categories ...
    elif any(word in text for word in ["my", "keywords"]):
        return "My Category"
```

2. Update GUI filters if needed

### Custom Plugin Parser

```python
class MyPluginParser:
    def parse(self, file_path):
        # Your parsing logic
        return {
            'name': name,
            'version': version,
            'metadata': metadata
        }

# Use in scanner
from my_parser import MyPluginParser

parser = MyPluginParser()
plugin_info = parser.parse(plugin_file)
```

## Code Style Guide

### Naming Conventions

```python
# Classes: PascalCase
class PluginManager:
    pass

# Functions/Methods: snake_case
def get_plugin_list():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_PLUGINS = 100

# Private methods: leading underscore
def _internal_method(self):
    pass
```

### Docstring Format

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is invalid
    """
    pass
```

### Type Hints

```python
from typing import List, Dict, Optional

def process_plugins(
    plugins: List[Dict], 
    options: Optional[Dict] = None
) -> List[str]:
    # Implementation
    pass
```

## Contributing

### Before Submitting Changes

1. **Test Thoroughly**:
   ```bash
   python test_basic.py
   python test_v2_features.py
   ```

2. **Check Code Style**:
   - Follow PEP 8
   - Add docstrings
   - Use type hints

3. **Update Documentation**:
   - Update relevant .md files
   - Add examples if needed
   - Update CHANGELOG.md

4. **Test on Clean System**:
   - Fresh Python environment
   - Install from requirements.txt
   - Verify functionality

### Pull Request Checklist

- [ ] Code tested and working
- [ ] No new dependencies (or justified)
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows project code style
- [ ] Commit messages clear

## Useful Resources

### Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete overview
- [CODE_REVIEW.md](CODE_REVIEW.md) - Quality assessment

### External APIs
- [GitHub API](https://docs.github.com/en/rest)
- [OBS Resources](https://obsproject.com/forum/resources/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### Python Libraries
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [requests](https://docs.python-requests.org/)
- [psutil](https://psutil.readthedocs.io/)

## FAQ for Developers

**Q: How do I add a new plugin to the built-in catalog?**  
A: Edit `plugin_repository.py`, add to `POPULAR_PLUGINS` list

**Q: How do I change cache duration?**  
A: Edit `discovery.py`, modify `self.cache_expiry` value

**Q: Can I add more than 3 discovery sources?**  
A: Yes! Add methods in `discovery.py` and update GUI radio buttons

**Q: How do I customize the GUI theme?**  
A: Tkinter supports ttk themes. Look into `ttk.Style()` configuration

**Q: Can this work on Linux/Mac?**  
A: Not currently. Would need to adapt:
   - OBS detection (different paths)
   - Process management (different system calls)
   - Registry access (not available)

**Q: How do I optimize database queries?**  
A: Add indexes, use WHERE clauses, batch operations

**Q: Can I add more archive versions (not just 2)?**  
A: Yes! Edit `local_repository.py`, change cleanup logic

## Quick Reference Commands

```bash
# Development
pip install -e .                # Editable install
python -m obs_plugin_manager    # Run as module

# Testing  
python test_basic.py           # Basic tests
python test_v2_features.py     # v2.0 tests

# Code Quality
pylint obs_plugin_manager      # Linting (if installed)
black obs_plugin_manager       # Formatting (if installed)

# Distribution
python setup.py sdist          # Source distribution
python setup.py bdist_wheel    # Wheel distribution

# Cleanup
rm -rf obs_plugins.db         # Remove database
rm -rf plugin_*               # Remove caches
rm -rf __pycache__            # Remove Python cache
```

---

**Happy Coding!** 🚀

For questions or improvements, see [CONTRIBUTING.md](CONTRIBUTING.md)
