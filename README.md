# OBS Plugin Manager

A Windows-based OBS Plugin Management Solution that helps you discover, install, update, and manage OBS Studio plugins safely and efficiently.

## Features

- **Plugin Catalog**: Maintains a database of popular OBS plugins that can be refreshed and updated (e.g., from BarRaider or other sources)
- **Plugin Scanning**: Automatically scans your OBS installation to detect installed plugins and their versions
- **Version Comparison**: Compares installed plugins with available versions and identifies updates
- **Suggested Plugins**: Highlights recommended plugins to enhance your OBS setup
- **Safe Operations**: Never allows writes to OBS plugin directories while OBS is running
- **OBS Process Management**: 
  - Check if OBS is running
  - Kill OBS process when needed
  - Query OBS status
- **Plugin Management**:
  - Download and install plugins
  - Update existing plugins
  - Rollback to previous versions (keeps archive of last 2 versions)
- **Version Archive**: Automatically maintains rollback archives for safe plugin management

## Requirements

- Windows 10/11
- .NET 8.0 Runtime
- OBS Studio installed

## Installation

1. Clone this repository
2. Open the solution in Visual Studio 2022 or later
3. Build the solution (Ctrl+Shift+B)
4. Run the application

## Usage

### Getting Started

1. **Check OBS Status**: The application will show whether OBS is currently running
2. **Scan for Plugins**: Click "Scan for Plugins" to detect installed plugins in your OBS installation
3. **Browse Catalog**: View available plugins in the catalog, including suggested plugins
4. **Install/Update**: Select a plugin and click "Install" or "Update"

### Safety Features

- The application will **never** write to OBS plugin directories while OBS is running
- If OBS is running and you attempt to install/update, you'll be prompted to close OBS first
- Use the "Kill OBS" button to safely close OBS before performing plugin operations

### Plugin Operations

- **Install**: Download and install a new plugin from the catalog
- **Update**: Update an existing plugin to the latest version
- **Rollback**: Restore a previous version of a plugin (last 2 versions are kept)

### Refreshing the Catalog

The plugin catalog can be refreshed to get the latest plugin information. In a production environment, this would connect to APIs like BarRaider's plugin repository or GitHub releases.

## Project Structure

```
OBSPluginManager/
├── Models/              # Data models (Plugin, InstalledPlugin)
├── Services/            # Core services
│   ├── OBSProcessManager.cs    # OBS process detection and management
│   ├── PluginDatabase.cs       # SQLite database for plugin catalog
│   ├── PluginScanner.cs        # Scans OBS installation for plugins
│   ├── VersionComparer.cs      # Version comparison logic
│   ├── PluginInstaller.cs     # Plugin download, install, and rollback
│   └── PluginCatalogSeeder.cs # Initial catalog data seeding
├── ViewModels/          # MVVM view models
├── Converters/          # WPF value converters
├── MainWindow.xaml      # Main UI
└── App.xaml             # Application entry point
```

## Technical Details

### OBS Detection

The application detects OBS installation through:
1. Running process detection (`obs64.exe` or `obs32.exe`)
2. Common installation paths (Program Files, AppData)
3. Windows Registry lookup

### Plugin Scanning

Scans the following OBS directories:
- `obs-plugins/` - 64-bit plugins
- `data/obs-plugins/` - 32-bit/data plugins

Extracts version information from:
- DLL file version info
- Version.txt files
- Directory names

### Version Archive

When updating a plugin, the previous version is automatically archived to:
`PluginArchives/{PluginName}/{Version}_{Timestamp}/`

The system maintains the last 2 versions for rollback purposes.

## Development

### Building

```bash
dotnet build OBSPluginManager.sln
```

### Running

```bash
dotnet run --project OBSPluginManager/OBSPluginManager.csproj
```

### Adding New Plugin Sources

To add support for new plugin sources (e.g., BarRaider API):

1. Create a service that implements `IPluginSource`
2. Update `PluginCatalogSeeder` to fetch from the new source
3. The database will automatically update with new plugin information

## Safety Considerations

- **Never writes while OBS is running**: All write operations check OBS status first
- **Rollback support**: Previous versions are archived before updates
- **Process management**: Can safely terminate OBS when needed
- **Error handling**: Comprehensive error handling prevents data loss

## Future Enhancements

- Integration with BarRaider API for automatic catalog updates
- Plugin dependency management
- Batch install/update operations
- Plugin search and filtering
- Export/import plugin configurations
- Plugin ratings and reviews

## License

[Specify your license here]

## Contributing

See CONTRIBUTING.md for guidelines on contributing to this project.

## Support

For issues and feature requests, please open an issue on the GitHub repository.
