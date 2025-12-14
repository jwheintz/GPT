# OBS Plugin Manager - Architecture Documentation

## Overview

OBS Plugin Manager is a Windows-based desktop application built in Python that provides safe and user-friendly management of OBS Studio plugins. The application follows a modular architecture with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (GUI)                     │
│                      tkinter-based UI                        │
└───────────────┬─────────────────────────────────┬───────────┘
                │                                 │
        ┌───────▼────────┐              ┌────────▼──────────┐
        │ OBS Manager    │              │ Plugin Repository │
        │ - Detect OBS   │              │ - Plugin Catalog  │
        │ - Kill Process │              │ - Update Check    │
        │ - Status Check │              │ - Version Compare │
        └───────┬────────┘              └────────┬──────────┘
                │                                │
        ┌───────▼────────┐              ┌────────▼──────────┐
        │ Plugin Scanner │              │ Plugin Installer  │
        │ - Scan Plugins │              │ - Download        │
        │ - Extract Ver. │              │ - Install         │
        │ - Get Files    │              │ - Remove          │
        └───────┬────────┘              │ - Rollback        │
                │                       └────────┬──────────┘
                │                                │
                └────────┬──────────┬────────────┘
                         │          │
                    ┌────▼──────────▼─────┐
                    │   SQLite Database   │
                    │ - Plugin Catalog    │
                    │ - Installed Plugins │
                    │ - Archives          │
                    │ - History           │
                    └─────────────────────┘
```

## Module Descriptions

### 1. Database Module (`database.py`)

**Purpose**: Persistent storage and retrieval of plugin data

**Key Components**:
- `PluginDatabase` class: Main database interface

**Database Tables**:
- `plugin_catalog`: Known plugins and their metadata
- `installed_plugins`: Currently installed plugins
- `plugin_archives`: Backup archives for rollback
- `installation_history`: Log of all operations

**Key Methods**:
- `add_plugin_to_catalog()`: Add/update plugin in catalog
- `get_catalog_plugins()`: Retrieve available plugins
- `add_installed_plugin()`: Record plugin installation
- `get_installed_plugins()`: Get list of installed plugins
- `add_archive()`: Record backup archive
- `add_history_entry()`: Log installation event

**Data Flow**:
```
User Action → GUI → Database → SQLite File
                      ↓
              Query Results ← SQLite File
```

### 2. OBS Manager Module (`obs_manager.py`)

**Purpose**: Interface with OBS Studio installation and process

**Key Components**:
- `OBSManager` class: Handles all OBS-related operations

**Capabilities**:
1. **Installation Detection**
   - Registry scanning (HKCU, HKLM)
   - Common directory checking
   - Running process detection

2. **Process Management**
   - Check if OBS is running
   - Terminate OBS processes
   - Get process information

3. **Directory Detection**
   - Find OBS installation path
   - Locate plugin directories
   - Identify data directories

**Key Methods**:
- `_detect_obs_installation()`: Find OBS on system
- `is_obs_running()`: Check OBS process status
- `kill_obs()`: Terminate OBS processes
- `get_plugin_directories()`: Get plugin folder paths

**Safety Features**:
- Non-destructive detection
- Safe process termination (terminate before kill)
- Multiple location fallbacks

### 3. Plugin Scanner Module (`plugin_scanner.py`)

**Purpose**: Scan and analyze installed plugins

**Key Components**:
- `PluginScanner` class: Analyzes OBS plugin directory

**Scanning Process**:
1. Walk through plugin directories
2. Find DLL files (plugin binaries)
3. Extract version information
4. Calculate file hashes
5. Detect related files
6. Deduplicate results

**Version Detection Methods**:
1. PowerShell file version query (primary)
2. Binary content scanning (fallback)
3. Pattern matching for version strings

**Key Methods**:
- `scan_plugins()`: Main scanning operation
- `_analyze_plugin_file()`: Extract plugin info
- `_extract_version_from_file()`: Get version number
- `get_plugin_files()`: Find all related files

**Data Structure**:
```python
{
    'name': 'plugin-name',
    'filename': 'plugin.dll',
    'path': 'C:\\path\\to\\plugin.dll',
    'version': '1.2.3',
    'size': 123456,
    'modified': 1234567890.0,
    'hash': 'md5hash',
    'directory': 'C:\\path\\to'
}
```

### 4. Plugin Repository Module (`plugin_repository.py`)

**Purpose**: Manage plugin catalog and check for updates

**Key Components**:
- `PluginRepository` class: Plugin catalog management
- `POPULAR_PLUGINS`: Built-in plugin database

**Features**:
1. **Plugin Catalog**
   - 15+ pre-configured popular plugins
   - Categories and metadata
   - Recommended plugins marked

2. **Update Checking**
   - GitHub API integration
   - Latest release detection
   - Version comparison

3. **Search and Filter**
   - Text search
   - Category filtering
   - Recommendation filtering

**Key Methods**:
- `get_popular_plugins()`: Get catalog
- `refresh_plugin_info()`: Update from GitHub
- `check_for_updates()`: Compare versions
- `compare_versions()`: Version string comparison
- `search_plugins()`: Find plugins by query

**GitHub Integration**:
```
User Requests Update Check
         ↓
Plugin Repository
         ↓
GitHub API Request (releases/latest)
         ↓
Parse Response (version, download URL)
         ↓
Compare with Installed Version
         ↓
Return Update Information
```

### 5. Plugin Installer Module (`plugin_installer.py`)

**Purpose**: Download, install, backup, and rollback plugins

**Key Components**:
- `PluginInstaller` class: Main installation manager

**Operations**:

#### Installation Flow
```
1. Download Plugin
   ├─ Stream from URL
   ├─ Save to temp directory
   └─ Progress callback
   
2. Extract Archive
   ├─ Unzip to temp
   └─ Verify contents
   
3. Backup Current Version
   ├─ Create archive directory
   ├─ Copy existing files
   └─ Store metadata
   
4. Install New Files
   ├─ Copy DLLs to plugin dir
   ├─ Copy data directories
   └─ Record in database
   
5. Cleanup
   ├─ Delete temp files
   └─ Cleanup old archives (keep 2)
```

#### Rollback Flow
```
1. Select Archive
   ↓
2. Remove Current Version
   ↓
3. Restore Files from Archive
   ↓
4. Update Database
   ↓
5. Verify Restoration
```

**Key Methods**:
- `download_plugin()`: Download from URL
- `extract_plugin()`: Unzip archive
- `install_plugin_files()`: Copy to OBS
- `remove_plugin()`: Uninstall plugin
- `create_archive()`: Backup for rollback
- `restore_from_archive()`: Rollback operation

**Archive Structure**:
```
plugin_archives/
├─ pluginname_version_timestamp/
│  ├─ plugin.dll
│  ├─ data/
│  └─ archive_metadata.json
└─ pluginname_version2_timestamp/
   └─ ...
```

### 6. GUI Module (`gui.py`)

**Purpose**: User interface and application orchestration

**Key Components**:
- `OBSPluginManagerGUI` class: Main application window

**UI Structure**:
```
┌─────────────────────────────────────────┐
│           Menu Bar                      │
├─────────────────────────────────────────┤
│  Status Bar (OBS Status, Path, Kill)   │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Notebook (Tabs)                │   │
│  │  ┌───┬───┬───┬───┐             │   │
│  │  │ I │ A │ U │ H │             │   │
│  │  └───┴───┴───┴───┘             │   │
│  │                                 │   │
│  │  Tab Content Area               │   │
│  │  - TreeView (list)              │   │
│  │  - Details Panel                │   │
│  │  - Action Buttons               │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│  Bottom Status Bar                      │
└─────────────────────────────────────────┘

Legend:
I = Installed Plugins
A = Available Plugins
U = Updates
H = History
```

**Tabs**:

1. **Installed Plugins**
   - TreeView with plugin list
   - Details panel
   - Remove button
   - Rollback button

2. **Available Plugins**
   - Category filter
   - Search box
   - TreeView with catalog
   - Details panel
   - Install button

3. **Updates**
   - Check for updates button
   - TreeView with available updates
   - Update selected button
   - Update all button

4. **History**
   - TreeView with operation log
   - Timestamps and status
   - Clear history button

**Threading**:
Long-running operations use threads:
- Plugin scanning
- Update checking
- Downloads and installations
- Catalog refreshing

**Key Methods**:
- `_setup_ui()`: Create interface
- `_check_obs_installation()`: Initialize OBS detection
- `_scan_plugins()`: Trigger plugin scan
- `_install_selected_plugin()`: Install workflow
- `_check_updates()`: Update check workflow
- `_update_obs_status()`: Real-time status monitoring

## Data Flow Examples

### Plugin Installation Flow
```
1. User selects plugin in Available Plugins tab
2. User clicks "Install Selected"
3. GUI checks OBS status (must not be running)
4. GUI shows progress dialog
5. Installer downloads plugin
6. Installer extracts archive
7. Installer creates backup of existing version (if any)
8. Installer copies files to OBS directory
9. Database records installation
10. Database adds history entry
11. GUI refreshes installed plugins list
12. GUI shows success message
```

### Update Check Flow
```
1. User clicks "Check for Updates"
2. GUI retrieves installed plugins from Scanner
3. GUI passes list to Repository
4. Repository fetches latest versions from GitHub
5. Repository compares versions
6. Repository returns list of available updates
7. GUI displays updates in TreeView
8. User can select and install updates
```

### Rollback Flow
```
1. User selects plugin in Installed tab
2. User clicks "Rollback"
3. GUI queries database for archives
4. GUI shows archive selection dialog
5. User selects version to restore
6. Installer removes current version
7. Installer restores files from archive
8. Database updates installed plugin record
9. Database adds history entry
10. GUI refreshes plugin list
```

## Safety Mechanisms

### 1. OBS Running Check
```
Before ANY write operation:
    if obs_manager.is_obs_running():
        show_error("OBS must be closed")
        return
    proceed_with_operation()
```

### 2. Backup Before Modification
```
Before installing/updating:
    existing_files = find_existing_plugin()
    if existing_files:
        create_archive(existing_files)
    install_new_version()
```

### 3. Archive Rotation
```
After creating archive:
    archives = get_archives_for_plugin()
    if len(archives) > 2:
        delete_oldest_archives()
```

### 4. Error Handling
```
try:
    perform_operation()
    database.add_history(success=True)
    show_success_message()
except Exception as e:
    database.add_history(success=False, error=str(e))
    show_error_message()
    rollback_if_needed()
```

## Extension Points

### Adding New Plugin Sources
Extend `PluginRepository`:
```python
def fetch_from_custom_source(self):
    # Implement custom API/RSS/etc
    return plugin_list
```

### Custom Version Detection
Extend `PluginScanner`:
```python
def _extract_version_custom(self, file_path):
    # Custom version extraction logic
    return version_string
```

### Additional Operations
Extend `PluginInstaller`:
```python
def migrate_plugin(self, old_name, new_name):
    # Custom migration logic
    pass
```

## Performance Considerations

1. **Threading**: Long operations run in background threads
2. **Caching**: Plugin info cached to reduce API calls
3. **Lazy Loading**: UI elements loaded on-demand
4. **Batch Operations**: Multiple plugins processed efficiently

## Security Considerations

1. **No Admin Required**: Operates on user-level directories
2. **Safe Downloads**: HTTPS only for downloads
3. **Hash Verification**: MD5 hashes stored for verification
4. **Process Safety**: Graceful OBS termination before forced kill

## Future Architecture Enhancements

1. **Plugin System**: Allow third-party extensions
2. **Web Service**: Optional cloud sync of settings
3. **CLI Interface**: Command-line management option
4. **Config Management**: Manage plugin configurations
5. **Conflict Detection**: Detect incompatible plugins

---

This architecture provides a solid foundation for safe and reliable OBS plugin management while remaining maintainable and extensible.
