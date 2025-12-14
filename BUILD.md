# Building OBS Plugin Manager

## Prerequisites

- Windows 10/11
- .NET 8.0 SDK (download from https://dotnet.microsoft.com/download)
- Visual Studio 2022 (optional, for IDE support)

## Building from Command Line

### Using .NET CLI

```bash
# Restore dependencies
dotnet restore OBSPluginManager.sln

# Build the solution
dotnet build OBSPluginManager.sln --configuration Release

# Run the application
dotnet run --project OBSPluginManager/OBSPluginManager.csproj --configuration Release
```

### Using MSBuild

```bash
# Build Release version
msbuild OBSPluginManager.sln /p:Configuration=Release /p:Platform="Any CPU"

# Output will be in: OBSPluginManager\bin\Release\net8.0-windows\
```

## Building from Visual Studio

1. Open `OBSPluginManager.sln` in Visual Studio 2022
2. Select "Release" configuration
3. Build → Build Solution (Ctrl+Shift+B)
4. Run → Start Without Debugging (Ctrl+F5)

## Output

The compiled executable will be located at:
```
OBSPluginManager\bin\Release\net8.0-windows\OBSPluginManager.exe
```

## Dependencies

The project uses the following NuGet packages:
- Microsoft.Data.Sqlite (8.0.0) - SQLite database support
- Newtonsoft.Json (13.0.3) - JSON serialization
- System.Management (8.0.0) - Windows process management

These are automatically restored during build.

## Troubleshooting

### Build Errors

If you encounter build errors:
1. Ensure .NET 8.0 SDK is installed: `dotnet --version`
2. Restore packages: `dotnet restore`
3. Clean and rebuild: `dotnet clean && dotnet build`

### Runtime Errors

If the application fails to run:
1. Ensure .NET 8.0 Runtime is installed
2. Check Windows compatibility
3. Verify OBS Studio is installed (for plugin scanning)

## Creating a Standalone Executable

To create a self-contained executable:

```bash
dotnet publish OBSPluginManager/OBSPluginManager.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

This will create a single executable file that includes the .NET runtime.
