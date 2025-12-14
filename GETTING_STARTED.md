# Getting Started with OBS Plugin Manager

## Quick Start Guide

### Step 1: Installation

1. **Install Python** (if not already installed)
   - Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Download OBS Plugin Manager**
   - Clone or download this repository
   - Extract to a folder of your choice

3. **Install Dependencies**
   ```bash
   cd path/to/obs-plugin-manager
   pip install -r requirements.txt
   ```

### Step 2: First Run

1. **Launch the Application**
   ```bash
   python obs_plugin_manager.py
   ```

2. **Initial Setup**
   - The app will automatically detect your OBS installation
   - If OBS is found, you'll see a green status indicator
   - The app will scan for currently installed plugins

### Step 3: Explore the Interface

#### Understanding the Status Bar
At the top of the window:
- **OBS Status**: Shows if OBS is running (updates every 2 seconds)
- **Installation Path**: Shows where OBS is installed
- **Kill OBS Button**: Terminates OBS if needed

#### The Four Main Tabs

**1. Installed Plugins**
- Shows all plugins currently in your OBS installation
- Displays version, size, and location
- Actions: Remove, Rollback

**2. Available Plugins**
- Browse 15+ popular OBS plugins
- Filter by category or search by name
- ⭐ indicates recommended plugins
- [INSTALLED] shows plugins you already have
- Actions: Install, View Details

**3. Updates**
- Check which plugins have updates available
- See current vs. latest versions
- Actions: Update Selected, Update All

**4. History**
- View log of all plugin operations
- See timestamps and success/failure status
- Useful for troubleshooting

### Step 4: Common Tasks

#### Installing Your First Plugin

Let's install **StreamFX**, a popular effects plugin:

1. Go to the **Available Plugins** tab
2. Look for "⭐ StreamFX" in the list
3. Click on it to see details in the bottom panel
4. Click **Install Selected**
5. If OBS is running, you'll be prompted to close it
6. Wait for download and installation (progress bar shows status)
7. Done! The plugin will appear in **Installed Plugins**

#### Checking for Updates

1. Go to the **Updates** tab
2. Click **Check for Updates**
3. Wait while the app checks GitHub for latest versions
4. If updates are available, they'll appear in the list
5. Select a plugin and click **Update Selected**
6. Or click **Update All** to update everything

#### Removing a Plugin

1. Go to **Installed Plugins** tab
2. Select the plugin you want to remove
3. Click **Remove**
4. Confirm the removal
5. A backup is automatically created for rollback

#### Rolling Back a Plugin

If a plugin update causes issues:

1. Select the plugin in **Installed Plugins**
2. Click **Rollback**
3. A window shows available previous versions (up to 2)
4. Select the version to restore
5. Click **Restore**
6. The plugin will be reverted to that version

### Step 5: Safety Features

#### Why OBS Must Be Closed

The app **prevents all write operations** when OBS is running because:
- OBS locks plugin DLL files while running
- Changes could cause OBS to crash
- Plugins might not load correctly

**Always close OBS before:**
- Installing plugins
- Updating plugins
- Removing plugins
- Rolling back plugins

#### Using the "Kill OBS" Feature

If you need to close OBS quickly:
1. Click the **Kill OBS** button at the top
2. Confirm the termination
3. OBS will close immediately
4. Status will change to "Not Running ✓"
5. Now you can safely manage plugins

### Step 6: Understanding Plugin Information

#### In the Installed Plugins Tab

When you select a plugin, details show:
- **Name**: Plugin identifier
- **Filename**: DLL file name
- **Version**: Detected version number
- **Path**: Full path to plugin file
- **Size**: File size in KB
- **Hash**: MD5 hash for verification

#### In the Available Plugins Tab

Plugin details include:
- **Display Name**: User-friendly name
- **Author**: Plugin creator
- **Category**: Type of plugin (Effects, Integration, etc.)
- **Latest Version**: Most recent release
- **Description**: What the plugin does
- **Homepage**: Link to plugin's website

### Step 7: Advanced Features

#### Searching and Filtering

In **Available Plugins**:
- Use the **Search** box to find plugins by name
- Use the **Category** dropdown to filter:
  - Integration
  - Effects
  - Sources
  - Output
  - Audio
  - Automation
  - Transitions

#### Refreshing the Catalog

Click **Refresh Catalog** to:
- Fetch latest version information from GitHub
- Update plugin descriptions
- Get new download links

This is useful if:
- Plugins show "Check online" for version
- You want to ensure latest information
- A plugin was recently updated

#### Using the History Tab

The history log shows:
- **Plugin**: Which plugin was affected
- **Action**: install, remove, update, rollback
- **Version**: Version involved
- **Timestamp**: When it happened
- **Status**: ✓ (success) or ✗ (failure)

Use this to:
- Track what changes you've made
- Troubleshoot failed operations
- Verify successful installations

### Step 8: Tips and Best Practices

#### Before Installing Plugins

1. ✅ Close OBS completely
2. ✅ Read the plugin description
3. ✅ Check if it's recommended (⭐)
4. ✅ Note the version being installed
5. ✅ Ensure you have enough disk space

#### After Installing Plugins

1. ✅ Restart OBS
2. ✅ Check if plugin appears in OBS
3. ✅ Test basic functionality
4. ✅ If issues occur, use rollback

#### Regular Maintenance

- **Weekly**: Check for updates
- **Monthly**: Review installed plugins (remove unused ones)
- **Before OBS Updates**: Backup your plugin archives folder
- **After OBS Updates**: Verify plugins still work

### Step 9: Troubleshooting

#### "OBS Not Found" Error

If you see "Installation: Not found" (red):
1. Ensure OBS Studio is actually installed
2. Try running OBS once to create registry entries
3. Restart the Plugin Manager
4. If still not found, reinstall OBS

#### Plugin Download Failed

If download fails:
1. Check your internet connection
2. Try clicking **Refresh Catalog** first
3. Visit the plugin's homepage to verify it still exists
4. Some plugins require manual download

#### Plugin Not Appearing in OBS

If installed plugin doesn't show in OBS:
1. Ensure OBS was completely closed during installation
2. Restart OBS after installation
3. Check OBS logs for plugin load errors
4. Some plugins need additional configuration

#### "Access Denied" Errors

If you get permission errors:
1. Run the Plugin Manager as Administrator
2. Check that OBS folder isn't read-only
3. Disable antivirus temporarily (it might block DLL writes)

### Step 10: Next Steps

Now that you're familiar with the basics:

1. **Browse Available Plugins**: Explore the catalog to find plugins that enhance your streams
2. **Join the Community**: Many plugins have Discord servers or forums
3. **Experiment Safely**: Thanks to rollback support, you can try plugins risk-free
4. **Share Knowledge**: Help others learn about useful plugins

### Recommended Plugins for Beginners

Start with these highly-rated, stable plugins:

1. **⭐ OBS WebSocket** - Remote control (essential for advanced setups)
2. **⭐ Background Removal** - AI-powered green screen effect
3. **⭐ StreamFX** - Beautiful effects and filters
4. **⭐ NDI Plugin** - Network video sources
5. **⭐ Multiple RTMP Outputs** - Stream to multiple platforms

### Getting Help

If you encounter issues:

1. Check the **History** tab for error messages
2. Read the README.md for detailed information
3. Verify OBS is properly installed and working
4. Ensure Python and dependencies are correctly installed

---

**Congratulations!** You're now ready to use OBS Plugin Manager effectively. Happy streaming! 🎥
