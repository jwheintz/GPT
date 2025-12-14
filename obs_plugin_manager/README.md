# OBS Plugin Manager

A comprehensive **Windows-based OBS Studio Plugin Management Solution** that helps you discover, install, update, and manage OBS plugins without directly integrating with OBS.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 🗄️ Plugin Catalog Database
- Pre-populated database of 25+ popular OBS plugins
- Plugins from popular authors like **Exeldro**, **BarRaider**, **Xaymar**, and more
- Categories: Streaming, Recording, Sources, Filters, Audio, Video, Automation, Integration, Utility
- **Refresh catalog** from GitHub to discover new plugins and updates
- Import/Export catalog as JSON for backup and sharing

### 🔍 OBS Installation Scanner
- Automatically detects OBS Studio installation paths
- Scans for installed third-party plugins
- Detects plugin versions via file properties
- Identifies plugins in both installation directory and AppData

### 🔄 Update Management
- Compare installed plugins against catalog versions
- One-click updates with automatic archiving
- Smart version comparison

### 💡 Plugin Suggestions
- Recommends popular plugins you haven't installed
- Categories: Recommended (⭐) and Popular (🔥)
- Based on community usage and author reputation

### 🛡️ Safety Features
- **Never writes when OBS is running** - All modifications blocked while OBS is active
- Real-time OBS process monitoring
- Can query OBS status at any time
- **Kill OBS** button for quick shutdown before modifications
- Confirmation dialogs for destructive operations

### 📦 Archive & Rollback System
- Automatically archives old versions before updates
- Keeps last **2 versions** (configurable) for each plugin
- One-click rollback to any archived version
- Archive cleanup to manage disk space

### 📥 Download Manager
- Downloads plugins directly from GitHub releases
- Supports ZIP, 7Z, RAR archives
- Progress tracking with speed and ETA
- Automatic extraction and installation

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (64-bit recommended)
- **Python 3.8+**
- **OBS Studio 28.0+** installed

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/obs-plugin-manager.git
   cd obs-plugin-manager
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 Usage

### GUI Application

Launch the graphical interface:
```bash
python main.py
# or
python main.py gui
```

#### Main Features:

1. **📦 Installed Plugins** - View and manage currently installed plugins
2. **📚 Plugin Catalog** - Browse available plugins with search and filters
3. **🔄 Updates** - Check for and apply plugin updates
4. **💡 Suggestions** - Discover recommended plugins
5. **⚙️ Settings** - Configure paths and preferences

### Command Line Interface

The application also supports CLI commands:

```bash
# Scan installed plugins
python main.py scan

# List all plugins in catalog
python main.py list

# List popular plugins
python main.py list --popular

# List recommended plugins
python main.py list --recommended

# List by category
python main.py list --category filters

# Check for updates
python main.py updates

# Check OBS status
python main.py status

# Kill OBS (if running)
python main.py kill
python main.py kill --force

# Refresh catalog from GitHub
python main.py refresh

# Install a plugin
python main.py install obs-shaderfilter

# Uninstall a plugin
python main.py uninstall obs-shaderfilter

# Rollback to previous version
python main.py rollback obs-shaderfilter
python main.py rollback obs-shaderfilter --version 2.2.0
```

## 📁 Project Structure

```
obs_plugin_manager/
├── main.py                 # Entry point (GUI & CLI)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── config.py          # Configuration management
    ├── database.py        # Plugin catalog database
    ├── obs_scanner.py     # OBS installation scanner
    ├── process_manager.py # OBS process management
    ├── plugin_manager.py  # Plugin download/install/rollback
    ├── catalog_refresh.py # Online catalog updates
    └── gui.py             # GUI application
```

## 🔌 Included Plugin Catalog

The default catalog includes popular plugins:

| Plugin | Author | Category | Description |
|--------|--------|----------|-------------|
| OBS WebSocket | OBS Project | Integration | Remote control via WebSockets |
| OBS NDI | Palakis | Video | NDI integration |
| StreamFX | Xaymar | Filters | Advanced filters and sources |
| Advanced Scene Switcher | WarmUpTill | Automation | Automatic scene switching |
| Background Removal | occ-ai | Filters | AI-powered background removal |
| Audio Monitor | Exeldro | Audio | Independent audio monitoring |
| Move Transition | Exeldro | Filters | Animated source transitions |
| Shader Filter | Exeldro | Filters | Custom HLSL/GLSL shaders |
| Multi RTMP | sorayuki | Streaming | Stream to multiple destinations |
| Input Overlay | univrsal | Sources | Show keyboard/mouse/gamepad |
| ... and 15+ more | | | |

## ⚙️ Configuration

Configuration is stored in:
```
%LOCALAPPDATA%\OBSPluginManager\config.json
```

### Settings:

- **OBS Installation Path** - Auto-detected or manually set
- **Plugin Archive Path** - Where backups are stored
- **Max Archive Versions** - Number of versions to keep (default: 2)
- **Auto-check Updates** - Check for updates on startup

## 🔒 Safety Mechanisms

### Write Protection
The application **prevents all modifications** when OBS is running:
- Plugin installations
- Plugin updates
- Plugin uninstallations
- Rollbacks

You must either:
1. Close OBS manually
2. Use the "Kill OBS" button in the app

### Archive Before Modify
Before any plugin modification:
1. Current version is automatically archived
2. Archive includes DLL + data folder
3. Old archives are cleaned up based on retention policy

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Adding New Plugins to Catalog

Edit `src/database.py` and add to `_get_default_plugins()`:

```python
PluginInfo(
    id="my-plugin",
    name="My Plugin",
    description="Description here",
    author="Author Name",
    category=PluginCategory.FILTERS.value,
    latest_version="1.0.0",
    release_date="2024-01-01",
    download_url="https://github.com/.../releases/latest",
    github_url="https://github.com/...",
    homepage_url="https://...",
    dll_name="my-plugin.dll",
    additional_files='["data/obs-plugins/my-plugin"]',
    is_popular=True,
    is_recommended=False,
    added_date=now,
    updated_date=now
)
```

Or import from JSON:
```bash
python main.py import-catalog plugins.json
```

## 📝 Troubleshooting

### OBS Not Detected
1. Ensure OBS is installed in default location
2. Use Settings > Browse to manually set path
3. OBS must have `bin/64bit/obs64.exe`

### Plugin Not Installing
1. Ensure OBS is not running (`python main.py status`)
2. Check download URL is valid
3. Verify archive format is supported (ZIP/7Z/RAR)

### Permission Errors
1. Run as Administrator if installing to Program Files
2. Or install plugins to AppData location

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🙏 Acknowledgments

- **OBS Project** - For the amazing streaming software
- **Exeldro** - For numerous essential plugins
- **BarRaider** - For Stream Deck integration
- **Xaymar** - For StreamFX
- All plugin authors in our catalog

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/obs-plugin-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/obs-plugin-manager/discussions)

---

Made with ❤️ for the OBS community
