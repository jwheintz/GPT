# Installation & Verification Checklist

Use this checklist to verify your OBS Plugin Manager installation is complete and working correctly.

## Pre-Installation Checklist

### System Requirements
- [ ] Running Windows 10 or later
- [ ] Have administrator access (for Python installation)
- [ ] At least 100 MB free disk space
- [ ] Internet connection available

### Software Prerequisites
- [ ] Python 3.8+ installed ([Download](https://www.python.org/downloads/))
  - During Python install, checked "Add Python to PATH"
- [ ] OBS Studio installed (optional but recommended)

## Installation Steps

### 1. Verify Python Installation
```bash
python --version
```
- [ ] Shows Python 3.8.0 or higher
- [ ] No "command not found" error

### 2. Download/Extract Project
- [ ] Downloaded OBS Plugin Manager
- [ ] Extracted to a folder (e.g., `C:\OBS-Plugin-Manager\`)
- [ ] Can see all project files

### 3. Install Dependencies
```bash
cd path\to\obs-plugin-manager
install.bat
```
- [ ] Script runs without errors
- [ ] Shows "Installation Complete!"
- [ ] All packages installed successfully

### 4. Verify File Structure
Check these files exist:
- [ ] `obs_plugin_manager.py`
- [ ] `launch.bat`
- [ ] `requirements.txt`
- [ ] `README.md`
- [ ] `obs_plugin_manager/` folder with 7 Python files

## First Launch Checklist

### 1. Launch Application
```bash
launch.bat
```
Or:
```bash
python obs_plugin_manager.py
```

- [ ] Application window opens
- [ ] No error messages in console
- [ ] GUI displays properly

### 2. Verify OBS Detection
Check top status bar:
- [ ] Shows OBS installation path (green) -OR-
- [ ] Shows "Not found" (red) - if OBS not installed

**If OBS is installed but not detected:**
- [ ] Run OBS Studio once
- [ ] Click "Tools → Refresh" in Plugin Manager
- [ ] Check TROUBLESHOOTING.md

### 3. Verify Tabs Are Working
Click each tab and verify it displays:
- [ ] **Installed Plugins** tab shows (may be empty)
- [ ] **Available Plugins** tab shows 15+ plugins
- [ ] **Updates** tab shows (empty until first check)
- [ ] **History** tab shows (empty initially)

### 4. Test Basic Features

#### Test Plugin Catalog
- [ ] Go to Available Plugins tab
- [ ] See list of plugins (15+)
- [ ] Can search plugins (type in search box)
- [ ] Can filter by category (use dropdown)
- [ ] Clicking plugin shows details below

#### Test OBS Status (if OBS installed)
- [ ] Status shows "Running" when OBS is open
- [ ] Status shows "Not Running" when OBS is closed
- [ ] "Kill OBS" button is visible
- [ ] Status updates automatically (within 2 seconds)

#### Test Scanning (if OBS installed)
- [ ] Click "Tools → Scan Plugins"
- [ ] Status bar shows "Scanning plugins..."
- [ ] After scan, shows count of found plugins
- [ ] Installed Plugins tab populates with results

## Feature Verification

### Database
- [ ] `obs_plugins.db` file created in app directory
- [ ] Can add entry to history (install/scan operation)
- [ ] History tab shows recorded operations

### Plugin Repository
- [ ] Available Plugins tab shows plugins
- [ ] Recommended plugins marked with ⭐
- [ ] Can search for specific plugins
- [ ] Can filter by category

### OBS Manager (if OBS installed)
- [ ] OBS path detected correctly
- [ ] OBS status updates in real-time
- [ ] Can detect when OBS is running
- [ ] "Kill OBS" button works (if OBS running)

### Plugin Operations (if OBS installed)
- [ ] Can scan installed plugins
- [ ] Installed plugins show in list
- [ ] Can view plugin details
- [ ] Can check for updates

### Safety Features
- [ ] Cannot install while OBS running (shows error)
- [ ] Cannot remove while OBS running (shows error)
- [ ] Status bar shows current operation
- [ ] Error messages are user-friendly

## Advanced Verification

### Test Installation (if comfortable)
**Note**: Only do this if you want to install a plugin

1. **Setup**:
   - [ ] Close OBS completely
   - [ ] Verify status shows "Not Running ✓"

2. **Select Plugin**:
   - [ ] Go to Available Plugins
   - [ ] Choose a safe plugin (e.g., "Move Transition")
   - [ ] Read description

3. **Install**:
   - [ ] Click "Install Selected"
   - [ ] Progress dialog appears
   - [ ] Download completes
   - [ ] Installation succeeds
   - [ ] Success message shown

4. **Verify**:
   - [ ] Plugin appears in Installed Plugins
   - [ ] History shows installation
   - [ ] `plugin_archives/` folder created

5. **Test in OBS**:
   - [ ] Open OBS
   - [ ] Plugin appears in OBS
   - [ ] Plugin functions correctly

6. **Test Rollback** (optional):
   - [ ] Close OBS
   - [ ] Select plugin in Installed tab
   - [ ] Click "Rollback"
   - [ ] Archive list appears
   - [ ] Can restore previous version

### Test Update Check
- [ ] Click "Check for Updates" in Updates tab
- [ ] Status shows "Checking for updates..."
- [ ] Completes without errors
- [ ] Shows available updates OR "All up to date"

## Documentation Verification

Verify these documents exist and open correctly:
- [ ] README.md - Main documentation
- [ ] GETTING_STARTED.md - Beginner's guide
- [ ] TROUBLESHOOTING.md - Problem solving
- [ ] ARCHITECTURE.md - Technical docs
- [ ] CONTRIBUTING.md - For contributors
- [ ] QUICK_REFERENCE.md - Quick reference
- [ ] PROJECT_SUMMARY.md - Complete overview
- [ ] CHANGELOG.md - Version history
- [ ] LICENSE - MIT License

## Common Issues During Verification

### Issue: Python not found
**Solution**: Install Python 3.8+ and add to PATH

### Issue: Dependencies won't install
**Solution**: 
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: GUI doesn't appear
**Solution**: Check console for errors, verify tkinter installed

### Issue: OBS not detected
**Solution**: Run OBS once, click Tools → Refresh

### Issue: "Module not found" errors
**Solution**: Ensure running from correct directory

## Performance Benchmarks

Expected performance on typical system:

- [ ] App starts in < 2 seconds
- [ ] Plugin scan completes in < 30 seconds
- [ ] Update check completes in < 15 seconds
- [ ] GUI responds immediately to clicks
- [ ] No lag or freezing during normal use

## Final Verification

- [ ] All core features working
- [ ] No critical errors
- [ ] Documentation accessible
- [ ] Ready for daily use

## Sign-Off

Once all items are checked:

✅ **INSTALLATION VERIFIED**

Date: _______________

Notes:
_________________________________
_________________________________
_________________________________

## Next Steps

After verification:

1. **Read GETTING_STARTED.md** for detailed usage guide
2. **Bookmark QUICK_REFERENCE.md** for quick help
3. **Keep TROUBLESHOOTING.md** handy for issues
4. **Start using the application!**

## Support

If any checklist item fails:

1. **Check TROUBLESHOOTING.md** for solutions
2. **Review error messages** carefully
3. **Verify all prerequisites** are met
4. **Try clean reinstall** if needed

## Uninstallation (if needed)

To completely remove:

1. Close the application
2. Delete the application folder
3. Delete `obs_plugins.db` if you want fresh start
4. Plugins installed to OBS remain (remove via app or manually)

---

**Congratulations!** 🎉

If all items are checked, your OBS Plugin Manager is ready to use!

**Happy plugin managing!** 🎥✨
