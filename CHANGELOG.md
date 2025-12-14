# Changelog

All notable changes to OBS Plugin Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-14

### Added
- Initial release of OBS Plugin Manager
- Automatic OBS installation detection
- Plugin scanning and version detection
- Built-in catalog of 15+ popular OBS plugins
- Plugin installation from URLs
- Safe plugin removal with automatic backups
- Rollback support (keeps last 2 versions)
- Update checking via GitHub API
- OBS process status monitoring
- Ability to terminate OBS processes
- Write protection when OBS is running
- SQLite database for plugin tracking
- Installation history logging
- GUI with tabbed interface:
  - Installed Plugins tab
  - Available Plugins tab
  - Updates tab
  - History tab
- Search and filter functionality
- Category-based plugin organization
- Progress indicators for downloads
- Detailed plugin information display
- Archive management system

### Features

#### Safety Features
- Real-time OBS status monitoring
- Blocks all write operations when OBS is running
- Automatic backup before all modifications
- Version archiving (up to 2 previous versions)
- Rollback capability

#### Plugin Management
- Download and install plugins from GitHub
- Remove plugins with backup
- Update plugins while preserving old versions
- Scan OBS directory for installed plugins
- Extract version information from DLL files
- Calculate file hashes for verification

#### User Interface
- Clean, intuitive Tkinter GUI
- Real-time status updates
- Progress bars for long operations
- Detailed plugin information panels
- Context-sensitive actions
- Error handling with user-friendly messages

#### Plugin Catalog
- Pre-configured with 15+ popular plugins:
  - OBS WebSocket
  - StreamFX
  - NDI Plugin
  - Background Removal
  - Multiple RTMP Outputs
  - Move Transition
  - Replay Source
  - Shader Filter
  - Composite Blur
  - Advanced Scene Switcher
  - MIDI Controller
  - Audio Monitor
  - And more...

### Technical Details
- Python 3.8+ compatible
- Windows-specific implementation
- Uses psutil for process management
- Requests library for downloads
- SQLite for data persistence
- Tkinter for cross-platform GUI
- GitHub API integration for updates

### Documentation
- Comprehensive README.md
- Step-by-step GETTING_STARTED.md
- Contributing guidelines (CONTRIBUTING.md)
- Installation scripts (install.bat)
- Launch script (launch.bat)
- MIT License

### Known Limitations
- Windows-only (by design)
- Requires OBS Studio to be installed
- GitHub-hosted plugins work best for updates
- Some plugins may not report version information
- Manual configuration may be needed for some plugins

## [Unreleased]

### Planned Features
- Plugin dependency resolution
- Configuration file management
- Batch operations
- Scheduled update checks
- Plugin conflict detection
- Custom plugin repository support
- Enhanced logging system
- Plugin usage analytics
- Import/export plugin profiles
- Command-line interface option

---

For detailed changes, see the commit history on GitHub.
