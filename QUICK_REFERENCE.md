# OBS Plugin Manager - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
1. install.bat          # First time only
2. launch.bat           # Every time
3. Browse → Install → Done!
```

## 📋 Essential Commands

### Windows
```bash
# Install dependencies (first time)
install.bat

# Launch application
launch.bat

# Or launch directly
python obs_plugin_manager.py

# Run tests
python test_basic.py
```

## 🎯 Main Features

| Feature | Location | Shortcut |
|---------|----------|----------|
| Scan Plugins | Installed Tab | Tools → Scan Plugins |
| Install Plugin | Available Tab | Select + Install |
| Check Updates | Updates Tab | Check for Updates |
| Rollback | Installed Tab | Select + Rollback |
| Kill OBS | Top Bar | Kill OBS Button |
| View History | History Tab | - |

## 🔴 Critical Rules

### ⚠️ NEVER while OBS is running:
- ❌ Install plugins
- ❌ Remove plugins
- ❌ Update plugins
- ❌ Rollback plugins

### ✅ ALWAYS:
- ✓ Close OBS first
- ✓ Verify "Not Running ✓" status
- ✓ Let backups complete
- ✓ Wait for operations to finish

## 📱 Status Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| 🟢 Not Running ✓ | Safe to proceed | Can install/update |
| 🔴 Running ⚠️ | OBS is active | Close OBS first |
| ⭐ | Recommended | Safe to install |
| [INSTALLED] | Already have it | Can update |

## 🎨 Plugin Categories

| Category | Examples |
|----------|----------|
| **Integration** | WebSocket, NDI, MIDI |
| **Effects** | StreamFX, Blur, Shader |
| **Sources** | Browser, Replay |
| **Output** | Multiple RTMP, Virtual Cam |
| **Audio** | Audio Monitor |
| **Automation** | Scene Switcher |
| **Transitions** | Move Transition |

## 🔧 Common Operations

### Install a Plugin
```
1. Available Plugins tab
2. Search or filter
3. Select plugin
4. Click "Install Selected"
5. Wait for completion
6. Restart OBS
```

### Update Plugins
```
1. Updates tab
2. Click "Check for Updates"
3. Wait for scan
4. Select plugin(s)
5. Click "Update Selected"
6. Restart OBS
```

### Rollback Plugin
```
1. Installed Plugins tab
2. Select plugin
3. Click "Rollback"
4. Choose version
5. Click "Restore"
6. Restart OBS
```

### Remove Plugin
```
1. Installed Plugins tab
2. Select plugin
3. Click "Remove"
4. Confirm
5. Backup created automatically
```

## 🔍 Search & Filter

### Available Plugins
- **Search box**: Type plugin name
- **Category dropdown**: Filter by type
- **⭐**: Shows recommended only

### Results
- Shows matching plugins instantly
- [INSTALLED] = already have it
- ⭐ = recommended by community

## 📊 Understanding the Interface

### Top Status Bar
```
OBS Status: [●] Not Running ✓    Installation: C:\Program Files\obs-studio    [Kill OBS]
```
- Left: OBS running status (updates every 2 seconds)
- Center: OBS installation path
- Right: Force-kill OBS button

### Bottom Status Bar
```
Status: Ready
```
Shows current operation or "Ready"

### Plugin List Columns

**Installed Plugins**:
- Plugin | Name | Version | Size | Path

**Available Plugins**:
- Plugin | Author | Category | Latest Version

**Updates**:
- Plugin | Current | Latest | Status

**History**:
- Plugin | Action | Version | Timestamp | Status

## ⚡ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F5 | Refresh current tab |
| Ctrl+F | Focus search box |
| Ctrl+Q | Quit application |
| Delete | Remove selected plugin |

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| OBS not detected | Run OBS once, then restart app |
| Can't install | Close OBS completely |
| Download fails | Check internet connection |
| Plugin missing in OBS | Restart OBS |
| Version shows "Unknown" | Normal, plugin still works |
| No updates found | All plugins up to date! |

## 📁 Important Paths

```
Application Files:
├─ obs_plugin_manager.py      # Main program
├─ obs_plugins.db             # Database (auto-created)
├─ plugin_archives/           # Backups (keep this!)
└─ plugin_cache/              # Cache (safe to delete)

OBS Plugins:
├─ C:\Program Files\obs-studio\obs-plugins\64bit\
└─ %APPDATA%\obs-studio\obs-plugins\64bit\
```

## 🔐 Safety Features

| Feature | Benefit |
|---------|---------|
| OBS Status Check | Prevents corruption |
| Auto Backup | Enables rollback |
| Archive System | Keeps 2 versions |
| History Log | Track all changes |
| Error Recovery | Safe failure handling |

## 📞 Quick Help

| Issue | See |
|-------|-----|
| First time setup | GETTING_STARTED.md |
| Something broke | TROUBLESHOOTING.md |
| Want to understand | ARCHITECTURE.md |
| Want to contribute | CONTRIBUTING.md |

## 💡 Pro Tips

1. **Test First**: Install one plugin at a time
2. **Check History**: Review History tab regularly
3. **Keep Archives**: Don't delete plugin_archives folder
4. **Update Regularly**: Check for updates weekly
5. **Read Descriptions**: Know what plugins do
6. **Restart OBS**: Always restart OBS after changes
7. **Use Rollback**: Don't be afraid to rollback
8. **Report Issues**: Help improve the tool

## 🎓 Best Practices

### Before Installing
- ✓ Close OBS
- ✓ Read plugin description
- ✓ Check if recommended
- ✓ Note the version

### After Installing
- ✓ Restart OBS
- ✓ Test basic functionality
- ✓ Check OBS logs if issues
- ✓ Rollback if problems

### Regular Maintenance
- Weekly: Check for updates
- Monthly: Review installed plugins
- Quarterly: Clean up unused plugins
- Always: Keep backups of OBS scenes

## 🌟 Recommended First Plugins

Start with these safe, popular plugins:

1. **⭐ OBS WebSocket** - Essential for advanced setups
2. **⭐ Background Removal** - AI-powered backgrounds
3. **⭐ StreamFX** - Beautiful effects
4. **⭐ NDI Plugin** - Network video sources
5. **⭐ Multiple RTMP** - Multi-platform streaming

## 📝 Quick Checklist

### Before Any Operation
- [ ] OBS is closed
- [ ] Status shows "Not Running ✓"
- [ ] Waited 5 seconds after closing
- [ ] Internet connected (for downloads)
- [ ] Enough disk space

### After Installation
- [ ] Success message appeared
- [ ] Plugin in Installed list
- [ ] Restart OBS
- [ ] Plugin appears in OBS
- [ ] Test basic functionality

### If Something Goes Wrong
- [ ] Check History tab for errors
- [ ] Try rollback if available
- [ ] Close and restart app
- [ ] Kill OBS and try again
- [ ] Check TROUBLESHOOTING.md

## 🔢 By The Numbers

- **15** popular plugins included
- **7** plugin categories
- **2** versions kept for rollback
- **4** main tabs in interface
- **2** seconds between status updates
- **0** admin rights needed
- **0** accounts or logins required

## 🎬 Typical Session

```
1. Double-click launch.bat
   ↓
2. App opens, detects OBS
   ↓
3. Browse Available Plugins
   ↓
4. Select "StreamFX"
   ↓
5. Click Install
   ↓
6. Wait 30 seconds
   ↓
7. Success!
   ↓
8. Close app
   ↓
9. Open OBS
   ↓
10. Use new plugin!
```

## 📚 Learn More

| Document | For |
|----------|-----|
| README.md | Overview & features |
| GETTING_STARTED.md | Beginners |
| TROUBLESHOOTING.md | Problems |
| ARCHITECTURE.md | Developers |
| PROJECT_SUMMARY.md | Everything |

## 🆘 Emergency Procedures

### OBS Won't Start After Plugin Install
```
1. Click Rollback on the plugin
2. Or remove the plugin
3. Restart OBS
4. Report the issue
```

### App Won't Start
```
1. Open command prompt
2. cd to application folder
3. Run: python obs_plugin_manager.py
4. Read error message
5. Check TROUBLESHOOTING.md
```

### Database Corrupted
```
1. Close application
2. Rename obs_plugins.db to obs_plugins.db.old
3. Restart application
4. Rescan plugins
```

---

## 🎯 Remember

**The Golden Rule**: ALWAYS close OBS before making changes!

**The Silver Rule**: Backups are your friend - don't delete archives!

**The Bronze Rule**: When in doubt, check the documentation!

---

**Need More Help?**
- 📖 Read GETTING_STARTED.md for detailed guides
- 🔧 Check TROUBLESHOOTING.md for solutions
- 💬 All documentation in same folder

**Happy Streaming!** 🎥✨
