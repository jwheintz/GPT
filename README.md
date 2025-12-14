# OBS Plugin Manager

A comprehensive Windows-based OBS Studio Plugin Management Solution that provides a safe and user-friendly way to manage OBS plugins.

## Features

### Core Functionality
- **🔍 Plugin Detection**: Automatically scans your OBS installation to detect installed plugins and their versions
- **📦 Plugin Catalog**: Maintains a database of popular OBS plugins with version information
- **🔄 Update Checking**: Compares installed plugin versions with the latest available versions
- **📥 Plugin Installation**: Download and install plugins directly from the application
- **🗑️ Safe Removal**: Remove plugins with automatic backup creation
- **⏮️ Rollback Support**: Keep archives of the last 2 versions for easy rollback
- **🔐 OBS Process Management**: Prevents writes when OBS is running, can detect and terminate OBS

### Safety Features
- **OBS Status Monitoring**: Real-time detection of whether OBS is running
- **Write Protection**: Blocks all plugin installation/removal operations while OBS is active
- **Automatic Backups**: Creates backups before every plugin update or removal
- **Version Archives**: Maintains up to 2 previous versions of each plugin for rollback

### Plugin Repository
The application includes a built-in catalog of popular OBS plugins including:
- **OBS WebSocket** - Remote control via WebSocket
- **StreamFX** - Modern effects plugin
- **NDI Plugin** - Network Device Interface integration
- **Background Removal** - AI-powered background removal
- **Multiple RTMP Outputs** - Stream to multiple destinations
- And many more...

## Installation

### Prerequisites
- Windows 10 or later
- Python 3.8 or higher
- OBS Studio installed (optional for catalog-only usage)

### Setup Steps

1. **Clone or download this repository**
```bash
git clone <repository-url>
cd obs-plugin-manager
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python obs_plugin_manager.py
```

## Usage Guide

### First Launch
On first launch, the application will:
1. Detect your OBS Studio installation
2. Scan for installed plugins
3. Load the plugin catalog

### Main Interface

#### Installed Plugins Tab
- View all currently installed plugins
- See version, size, and location information
- Remove plugins with one click
- Rollback to previous versions

#### Available Plugins Tab
- Browse the catalog of popular OBS plugins
- Filter by category or search by name
- See if plugins are already installed
- Install new plugins directly
- View plugin descriptions and information

#### Updates Tab
- Check for available updates
- See current vs. latest versions
- Update individual plugins or all at once
- View update status

#### History Tab
- View installation history
- Track all plugin operations
- Monitor success/failure of operations

### Managing Plugins

#### Installing a Plugin
1. Go to the "Available Plugins" tab
2. Browse or search for the plugin you want
3. Select the plugin and click "Install Selected"
4. Ensure OBS is not running (the app will warn you)
5. Wait for download and installation to complete

#### Updating a Plugin
1. Click "Check for Updates" in the Updates tab
2. Select plugins with available updates
3. Click "Update Selected" or "Update All"
4. The app will backup the current version before updating

#### Removing a Plugin
1. Go to "Installed Plugins" tab
2. Select the plugin to remove
3. Click "Remove"
4. A backup will be created automatically

#### Rolling Back a Plugin
1. Select a plugin in "Installed Plugins"
2. Click "Rollback"
3. Choose from up to 2 previous versions
4. Click "Restore" to rollback

### OBS Process Management

#### Checking OBS Status
- Status is shown in real-time at the top of the window
- Green "Not Running" = Safe to make changes
- Red "Running" = Operations are blocked

#### Killing OBS
If you need to install/update plugins:
1. Click "Kill OBS" button in the toolbar
2. Confirm the action
3. OBS will be safely terminated

## Architecture

### Components

#### Database Module (`database.py`)
- SQLite database for plugin metadata
- Tracks installed plugins, catalog, archives, and history
- Manages version information and installation records

#### OBS Manager (`obs_manager.py`)
- Detects OBS installation location
- Monitors OBS process status
- Can terminate OBS processes
- Identifies plugin directories

#### Plugin Scanner (`plugin_scanner.py`)
- Scans OBS directories for installed plugins
- Extracts version information from DLL files
- Identifies plugin files and dependencies
- Calculates file hashes for verification

#### Plugin Repository (`plugin_repository.py`)
- Maintains catalog of popular plugins
- Fetches latest version information from GitHub
- Compares versions for update detection
- Caches plugin information

#### Plugin Installer (`plugin_installer.py`)
- Downloads plugins from URLs
- Extracts and installs plugin files
- Creates backups before operations
- Manages plugin archives for rollback
- Handles plugin removal

#### GUI (`gui.py`)
- Tkinter-based graphical interface
- Multi-tabbed interface for different operations
- Real-time OBS status monitoring
- Progress indicators for long operations

## Configuration

### Database Location
By default, the database is stored as `obs_plugins.db` in the application directory.

### Plugin Archives
Archives are stored in the `plugin_archives` directory. Each plugin's last 2 versions are maintained.

### Plugin Cache
Plugin information is cached in the `plugin_cache` directory to reduce API calls.

## Troubleshooting

### OBS Not Detected
If OBS is not detected:
1. Ensure OBS Studio is installed
2. Try running OBS once to create registry entries
3. Check that OBS is installed in a standard location
4. Use "Tools > Refresh" to re-scan

### Plugin Not Installing
If a plugin fails to install:
1. Ensure OBS is closed
2. Check that you have write permissions to the OBS directory
3. Verify the download URL is accessible
4. Check the installation history for error details

### Version Detection Issues
Some plugins may not have version information:
- The scanner tries multiple methods to extract versions
- "Unknown" version is shown if detection fails
- Manual verification may be needed

### Update Check Failures
If update checking fails:
- Ensure you have internet connectivity
- Check if GitHub API rate limits are reached
- Try refreshing the catalog manually

## Known Limitations

1. **Windows Only**: This application is designed specifically for Windows
2. **GitHub-based Plugins**: Update checking works best with GitHub-hosted plugins
3. **DLL Plugins**: Primarily supports DLL-based plugins (standard for Windows)
4. **Manual Plugin Configuration**: Some plugins may require manual configuration after installation

## Safety Considerations

- **Always backup your OBS settings** before making major plugin changes
- **Test plugins individually** to identify any compatibility issues
- **Keep rollback archives** - don't delete the plugin_archives folder
- **Close OBS before operations** - the app enforces this for safety

## Future Enhancements

Potential features for future versions:
- Plugin dependency management
- Automatic plugin recommendations based on use case
- Integration with more plugin repositories
- Plugin configuration management
- Batch operations and scheduling
- Plugin conflict detection

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## License

This project is provided as-is for managing OBS Studio plugins.

## Disclaimer

This application is not officially affiliated with OBS Studio. Use at your own risk. Always backup your OBS installation before making changes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the installation history for error messages
3. Ensure all prerequisites are met
4. Check that OBS is properly installed

---

**Note**: This tool manages plugins but does not modify OBS core files. It works by managing files in the OBS plugin directories only.
