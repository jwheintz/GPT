# Troubleshooting Guide

This guide helps you resolve common issues with OBS Plugin Manager.

## Installation Issues

### Python Not Found

**Problem**: When running `launch.bat`, you see "Python is not installed or not in PATH"

**Solutions**:
1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. If already installed, add Python to PATH manually:
   - Search for "Environment Variables" in Windows
   - Edit "Path" variable
   - Add Python installation directory (e.g., `C:\Python310\`)
4. Restart command prompt after changing PATH

### Dependency Installation Fails

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
1. Update pip first:
   ```bash
   python -m pip install --upgrade pip
   ```

2. If you get SSL errors:
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

3. Install packages individually:
   ```bash
   pip install psutil
   pip install requests
   pip install pywin32
   ```

4. Check Python version:
   ```bash
   python --version
   ```
   Must be 3.8 or higher

### Module Import Errors

**Problem**: "ModuleNotFoundError: No module named 'obs_plugin_manager'"

**Solutions**:
1. Ensure you're running from the project root directory
2. Check that `obs_plugin_manager/` folder exists
3. Verify `__init__.py` exists in `obs_plugin_manager/`
4. Try running with full path:
   ```bash
   python C:\full\path\to\obs_plugin_manager.py
   ```

## OBS Detection Issues

### OBS Not Detected

**Problem**: Application shows "Installation: Not found" (red)

**Possible Causes & Solutions**:

1. **OBS Not Installed**
   - Install OBS Studio from [obsproject.com](https://obsproject.com/)

2. **Non-Standard Installation Location**
   - The app checks these locations:
     - `C:\Program Files\obs-studio`
     - `C:\Program Files (x86)\obs-studio`
     - Registry keys
   - If installed elsewhere, the app may not find it

3. **Registry Not Set**
   - Run OBS Studio at least once to create registry entries
   - Restart the Plugin Manager

4. **Permissions Issue**
   - Try running Plugin Manager as Administrator
   - Right-click `launch.bat` → "Run as administrator"

### Plugin Directories Not Found

**Problem**: Plugin scanning finds no plugins

**Solutions**:
1. Verify OBS installation is complete
2. Check these directories exist:
   - `[OBS Install]\obs-plugins\64bit\`
   - `%APPDATA%\obs-studio\obs-plugins\64bit\`
3. Run OBS once to create directories
4. Click "Tools → Refresh" in Plugin Manager

## Plugin Management Issues

### Cannot Install Plugin - OBS Running

**Problem**: "Cannot install plugins while OBS is running"

**Solutions**:
1. Close OBS normally
2. If OBS won't close, use "Kill OBS" button
3. Wait a few seconds after closing
4. Verify status shows "Not Running ✓"
5. Try installation again

### Plugin Download Fails

**Problem**: Plugin download fails or times out

**Solutions**:
1. **Check Internet Connection**
   - Verify you can access GitHub
   - Try visiting plugin's homepage URL

2. **GitHub Rate Limiting**
   - GitHub API has rate limits
   - Wait 10-15 minutes and try again
   - Or visit the plugin's page manually

3. **Plugin No Longer Available**
   - Check if plugin still exists
   - Look for alternative download link
   - Manual download and install may be needed

4. **Antivirus Blocking**
   - Temporarily disable antivirus
   - Add exception for plugin manager
   - Check antivirus logs

### Plugin Installation Fails

**Problem**: Download succeeds but installation fails

**Solutions**:
1. **Verify OBS is Closed**
   - Use Task Manager to verify no OBS processes
   - Kill any remaining obs64.exe/obs32.exe

2. **Permission Denied**
   - Run as Administrator
   - Check OBS folder isn't read-only
   - Verify user has write access

3. **Archive Extraction Issues**
   - Try re-downloading the plugin
   - Check available disk space
   - Verify temp folder is writable

4. **Invalid Plugin Archive**
   - Some downloads may be invalid
   - Try downloading manually from GitHub
   - Check if plugin is Windows-compatible

### Plugin Not Appearing in OBS

**Problem**: Plugin installs successfully but doesn't show in OBS

**Solutions**:
1. **Restart OBS**
   - OBS only loads plugins on startup
   - Close and reopen OBS

2. **Check OBS Version Compatibility**
   - Plugin may require specific OBS version
   - Check plugin documentation
   - Update OBS if needed

3. **Plugin Dependencies Missing**
   - Some plugins need additional files
   - Check plugin's installation instructions
   - Install Visual C++ Redistributables if needed

4. **Check OBS Logs**
   - In OBS: Help → Log Files → View Current Log
   - Look for plugin load errors
   - Search for the plugin name

5. **Wrong Architecture**
   - Ensure 64-bit plugin for 64-bit OBS
   - Check plugin file is in `64bit` folder

### Version Detection Shows "Unknown"

**Problem**: Plugin appears but version shows "Unknown"

**This is Normal**:
- Not all plugins include version information
- The plugin will still work
- Version detection is informational only

**Optional Fix**:
- Check plugin's documentation for version
- Manually track version if needed
- Update checking may not work for this plugin

## Update Issues

### Update Check Fails

**Problem**: "Check for Updates" doesn't find any updates

**Solutions**:
1. **First Time Check**
   - Initial check takes longer
   - Be patient (up to 30 seconds)

2. **GitHub API Issues**
   - API might be temporarily unavailable
   - Wait and try again later

3. **No Updates Available**
   - "All plugins are up to date!" is success
   - This is the expected message if current

4. **Plugin Not in Catalog**
   - Only catalog plugins support update checking
   - Custom/manual plugins won't show updates

### Update Installation Fails

**Problem**: Update download/install fails

**Same as installation issues above, plus**:
- Verify current version is backed up
- Check rollback archives exist
- Try removing and reinstalling fresh

## Rollback Issues

### No Archives Available

**Problem**: "No backup archives available for this plugin"

**Causes**:
- Plugin was never updated (no backups created)
- Archives were manually deleted
- Plugin was installed before archiving feature

**Solutions**:
- Backups only created during updates
- Remove and reinstall to start fresh
- Future updates will create archives

### Rollback Fails

**Problem**: Restore from archive fails

**Solutions**:
1. **Verify OBS is Closed**
   - Must not be running during rollback

2. **Check Archive Exists**
   - Navigate to `plugin_archives/` folder
   - Verify archive directory exists
   - Check files are present

3. **Permission Issues**
   - Run as Administrator
   - Verify write access to OBS directory

4. **Manual Rollback**
   - Go to `plugin_archives/[plugin]/`
   - Manually copy files to OBS plugin directory
   - Replace current version

## GUI Issues

### Application Won't Start

**Problem**: Double-clicking launch.bat does nothing or crashes

**Solutions**:
1. **Run from Command Prompt**
   ```bash
   cd path\to\obs-plugin-manager
   python obs_plugin_manager.py
   ```
   - See actual error messages

2. **Check for Errors**
   - Look for error messages in console
   - Common: missing dependencies

3. **Tkinter Not Available**
   - Usually included with Python
   - Reinstall Python with tcl/tk option

4. **Try Basic Test**
   ```bash
   python test_basic.py
   ```
   - Tests core functionality without GUI

### Window Display Issues

**Problem**: Window appears corrupted or elements misaligned

**Solutions**:
1. **Screen Scaling**
   - Windows display scaling affects Tkinter
   - Try 100% scaling temporarily
   - Or adjust in Python compatibility settings

2. **DPI Awareness**
   - Right-click launch.bat
   - Properties → Compatibility
   - Check "Override high DPI scaling"

3. **Old Windows Version**
   - Requires Windows 10 or later
   - Earlier versions may have display issues

### TreeView Not Populating

**Problem**: Plugin lists are empty

**Solutions**:
1. Click "Refresh" or "Scan Plugins"
2. Check status bar for error messages
3. Verify OBS is detected
4. Look at History tab for errors

## Database Issues

### Database Locked

**Problem**: "Database is locked" error

**Solutions**:
1. Close other instances of Plugin Manager
2. Delete `obs_plugins.db-journal` if it exists
3. Restart the application

### Corrupted Database

**Problem**: Persistent database errors

**Solution - Reset Database**:
```bash
# Backup first!
copy obs_plugins.db obs_plugins.db.backup

# Delete database
del obs_plugins.db

# Restart application (creates new database)
python obs_plugin_manager.py
```

**Note**: This loses installation history but not actual plugins

## Performance Issues

### Slow Plugin Scanning

**Problem**: Scanning takes very long

**This is Normal If**:
- First scan of large OBS installation
- Many plugins installed
- Antivirus scanning files

**Solutions**:
1. Be patient (can take 30-60 seconds)
2. Add exception in antivirus for OBS folder
3. Close other applications

### Slow Download

**Problem**: Plugin downloads are very slow

**Causes**:
- Slow internet connection
- Large plugin file
- GitHub server load

**No Real Solution**:
- Just wait for completion
- Cancel and retry if stalled

## Advanced Troubleshooting

### Enable Debug Mode

Run with Python directly to see full errors:
```bash
python obs_plugin_manager.py
```

All errors will appear in console window.

### Check File Permissions

Verify access to OBS folder:
```bash
icacls "C:\Program Files\obs-studio\obs-plugins"
```

Should show read/write access.

### Manual Plugin Installation

If manager fails, install manually:
1. Download plugin from source
2. Extract ZIP file
3. Copy DLL files to: `[OBS]\obs-plugins\64bit\`
4. Copy data folders if included
5. Restart OBS

### View Database Contents

Use any SQLite browser:
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `obs_plugins.db`
3. View tables and data
4. Can manually edit if needed

### Clean Reinstall

Complete reset:
```bash
# 1. Backup your OBS settings!

# 2. Close everything
# - Close Plugin Manager
# - Close OBS

# 3. Delete app data
del obs_plugins.db
rmdir /s plugin_archives
rmdir /s plugin_cache

# 4. Restart application
python obs_plugin_manager.py
```

## Getting Further Help

### Gather Information

Before requesting help, collect:
1. Python version: `python --version`
2. Windows version: Run `winver`
3. OBS version: Check in OBS Help → About
4. Error messages (screenshot or copy/paste)
5. Installation history from History tab

### Check Existing Resources

1. Read README.md thoroughly
2. Review GETTING_STARTED.md
3. Check ARCHITECTURE.md for technical details
4. Look at test_basic.py for examples

### Report Issues

If you found a bug:
1. Check if already reported
2. Provide detailed steps to reproduce
3. Include system information
4. Attach relevant error messages
5. Describe expected vs actual behavior

## Common Error Messages

### "Access Denied"
- Run as Administrator
- Check folder permissions
- Antivirus may be blocking

### "File not found"
- Check paths are correct
- OBS installation path may have changed
- Plugin may have been manually deleted

### "Connection timed out"
- Check internet connection
- GitHub may be down
- Firewall may be blocking

### "Invalid archive"
- Plugin download corrupted
- Re-download the plugin
- Check plugin is still available

### "Plugin already installed"
- Remove existing version first
- Or use Update function instead

## Prevention Tips

### Regular Maintenance

1. **Backup Archives**
   - Copy `plugin_archives/` folder regularly
   - Keep before major OBS updates

2. **Keep Plugin Manager Updated**
   - Check for new versions
   - Update when available

3. **Document Changes**
   - History tab tracks all operations
   - Export/screenshot for records

4. **Test Plugins**
   - Test in OBS after installation
   - Remove if causing issues
   - Use rollback if needed

### Best Practices

1. **Close OBS Before Changes**
   - Always close OBS first
   - Verify "Not Running" status
   - Wait a few seconds after closing

2. **One Change at a Time**
   - Install one plugin at a time
   - Test before installing more
   - Easier to identify issues

3. **Read Plugin Documentation**
   - Check requirements
   - Review installation notes
   - Understand what plugin does

4. **Keep Backups**
   - Don't delete archive folders
   - Backup OBS scenes/settings
   - Export important configurations

---

**Still Having Issues?**

If this guide didn't help:
1. Try test_basic.py to verify core functionality
2. Check Python and dependency versions
3. Consider clean reinstall
4. Report the issue with details

Remember: Most issues are related to OBS being open, permissions, or network connectivity!
