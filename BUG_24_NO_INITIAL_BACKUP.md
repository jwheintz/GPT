# 🐛 Bug #24: No Initial Backup of Existing Plugins

**Date**: December 14, 2025  
**Reported by**: User  
**Severity**: **HIGH** ⚠️  
**Status**: ❌ **CONFIRMED - NOT FIXED YET**

---

## 🎯 The Problem

**User's Question**:
> "If it hasn't ever been updated, it is gathering the current plugin from the obs directory and saving it so that there is always a prior version unless it is a fresh new install, right?"

**Answer**: ❌ **NO - This is NOT happening!**

### Current Behavior

When the app first scans existing OBS plugins:

1. ✅ Detects plugins in OBS directory
2. ✅ Records them in database
3. ✅ Displays them in GUI
4. ❌ **Does NOT create initial backup/archive**

**Result**: If user tries to rollback a plugin that was never updated through this tool, **there's no archive to rollback to!**

---

## 📊 Impact Analysis

### Scenario 1: Fresh OBS Install
**User has**: OBS with no plugins  
**App does**: Scans, finds nothing  
**Impact**: ✅ **No issue** (nothing to backup)

### Scenario 2: Existing OBS with Plugins (MOST COMMON)
**User has**: OBS with 5 existing plugins installed manually  
**App does**: Scans, detects them, records in database  
**Archive created**: ❌ **NONE**  

**What happens if user wants to rollback?**
```
User clicks "Rollback" → No archives available → Can't rollback!
```

**Impact**: ❌ **USER CAN'T ROLLBACK EXISTING PLUGINS**

### Scenario 3: Plugin Updated Through Tool
**User has**: Existing plugin  
**App does**: Update plugin → Creates archive of old version  
**Archive created**: ✅ **YES** (during update)

**What happens if user wants to rollback?**
```
User clicks "Rollback" → 1 archive available → ✅ Can rollback to pre-update version
```

**But**: Can't rollback further than first update!

---

## 🔍 Code Analysis

### Where Backups ARE Created

**1. During plugin installation** (`plugin_installer.py:228`):
```python
if backup:
    existing_files = []
    for dll in plugin_files['dlls']:
        target = self.primary_plugin_dir / dll.name
        if target.exists():
            existing_files.append(target)
    
    if existing_files:
        archive_path = self.create_archive(plugin_name, existing_version, existing_files)
```

**When**: Installing/updating a plugin  
**Condition**: `backup=True` AND existing files found  
**Result**: ✅ Archives created

**2. During plugin removal** (`plugin_installer.py:276`):
```python
archive_path = self.create_archive(
    plugin_info['name'],
    plugin_info.get('version', 'unknown'),
    files_to_backup
)
```

**When**: Removing a plugin  
**Result**: ✅ Archive created before removal

### Where Backups ARE NOT Created

**During initial scan** (`gui.py:519`):
```python
def scan_thread():
    plugins = self.plugin_scanner.scan_plugins()  # Just scans
    self.installed_plugins = plugins
    
    # Update database
    for plugin in plugins:
        self.database.add_installed_plugin(...)  # Just records
    
    # ❌ NO ARCHIVE CREATION!
```

**Result**: ❌ **No initial backup of existing plugins!**

---

## 🚨 Real-World Scenarios

### Case 1: User Wants to Test Rollback

**Timeline**:
1. User installs OBS Plugin Manager (first time)
2. App scans existing plugins (5 plugins found)
3. User doesn't like a plugin, wants to remove it
4. User clicks "Remove" → Plugin removed, archive created ✅
5. User regrets it, clicks "Rollback" → ✅ Can restore (archive from step 4)

**Works**: ✅ (because removal created archive)

### Case 2: User Wants to Revert to Original

**Timeline**:
1. User has OBS with plugins installed manually (original versions)
2. User installs OBS Plugin Manager
3. App scans plugins (NO archives created) ❌
4. User updates plugin through app → New version installed, old archived ✅
5. Update has bugs, user clicks "Rollback" → Reverts to pre-update version ✅
6. Still has issues, user wants ORIGINAL version → ❌ **NO ARCHIVE!**

**Problem**: ❌ Can't rollback to original version (no initial backup)

### Case 3: Accidental Update

**Timeline**:
1. User has working plugin (v1.0 - manually installed)
2. App scans (no backup created) ❌
3. User accidentally clicks "Update" → v2.0 installed, v1.0 archived ✅
4. v2.0 breaks everything
5. User clicks "Rollback" → ✅ Reverts to v1.0
6. But what if v1.0 is also broken? → ❌ **Can't go back to original!**

**Problem**: ❌ Only 1 rollback level available (should be 2+)

---

## 📈 Expected vs Actual Behavior

### User Expectation ✅
"The app will backup my existing plugins when it first sees them, so I can always restore to original state."

### Actual Behavior ❌
"The app only creates backups when I update/remove plugins. No initial backup means I can't restore to original versions."

### Promised Feature (from requirements)
> "It keeps an archive of the last two versions for rollback"

**Current**: Only archives versions touched by the app  
**Expected**: Archives ALL versions, including pre-existing ones  
**Gap**: ❌ Initial backup missing

---

## 🔧 Recommended Fix

### Option 1: Create Initial Backups During First Scan (RECOMMENDED)

**When**: First time a plugin is scanned  
**What**: Create archive of current state  
**How**:

```python
def _scan_plugins(self):
    """Scan for installed plugins."""
    plugins = self.plugin_scanner.scan_plugins()
    
    for plugin in plugins:
        # Check if this is first time seeing this plugin
        existing_record = self.database.get_installed_plugin(plugin['name'])
        
        if not existing_record:
            # First time seeing this plugin - create initial backup
            plugin_files = [Path(plugin['path'])]
            
            archive_path = self.plugin_installer.create_archive(
                plugin_name=plugin['name'],
                version=plugin.get('version', 'initial'),
                files=plugin_files
            )
            
            if archive_path:
                # Record in database
                self.database.add_archive_record(
                    plugin['name'],
                    plugin.get('version', 'initial'),
                    archive_path
                )
```

**Pros**:
- ✅ Always have original version to rollback to
- ✅ Meets user expectations
- ✅ Fulfills "last two versions" promise
- ✅ No data loss

**Cons**:
- ⚠️ Extra disk space (but that's the point!)
- ⚠️ Slightly slower first scan (one-time cost)

### Option 2: Prompt User on First Scan

**When**: First scan detects existing plugins  
**What**: Ask user if they want initial backups  
**How**:

```python
if plugins and not previously_scanned:
    result = messagebox.askyesno(
        "Create Initial Backups?",
        f"Found {len(plugins)} existing plugins.\n\n"
        "Create backup archives for rollback protection?\n\n"
        "(Recommended for safety, uses ~50-100MB disk space)"
    )
    
    if result:
        # Create initial backups
```

**Pros**:
- ✅ User has control
- ✅ Can skip if disk space is concern
- ✅ Clear communication

**Cons**:
- ⚠️ Extra UI interaction
- ⚠️ Some users may skip (then regret)

### Option 3: Lazy Backup (On Demand)

**When**: User tries to update/remove a plugin  
**What**: If no archive exists, create one FIRST  
**How**: Already partially implemented (backup=True in install_plugin)

**Pros**:
- ✅ No upfront cost
- ✅ Minimal implementation

**Cons**:
- ❌ Too late if already updated
- ❌ Doesn't protect original versions
- ❌ Not a true fix

**Verdict**: ❌ **Not recommended** (doesn't solve the problem)

---

## 💡 Recommended Implementation

### Phase 1: Add Initial Backup Function

```python
def create_initial_backups(self, plugins: List[Dict]) -> Dict[str, bool]:
    """
    Create initial backups of existing plugins.
    
    Args:
        plugins: List of detected plugins
        
    Returns:
        Dict mapping plugin names to backup success status
    """
    results = {}
    
    for plugin in plugins:
        try:
            # Check if already has archive
            existing_archives = self.database.get_archives(plugin['name'])
            if existing_archives:
                results[plugin['name']] = True  # Already backed up
                continue
            
            # Create initial backup
            plugin_path = Path(plugin['path'])
            files_to_backup = []
            
            # If path is a directory, backup all files
            if plugin_path.is_dir():
                files_to_backup = [plugin_path]
            else:
                # Single file
                files_to_backup = [plugin_path]
            
            archive_path = self.create_archive(
                plugin_name=plugin['name'],
                version=plugin.get('version', 'initial_backup'),
                files=files_to_backup
            )
            
            if archive_path:
                # Record in database
                self.database.add_archive_record(
                    plugin_name=plugin['name'],
                    version=plugin.get('version', 'initial_backup'),
                    archive_path=str(archive_path),
                    file_count=len(files_to_backup),
                    total_size=sum(f.stat().st_size for f in files_to_backup if f.exists())
                )
                results[plugin['name']] = True
            else:
                results[plugin['name']] = False
                
        except Exception as e:
            self.logger.error(f"Failed to create initial backup for {plugin['name']}: {e}")
            results[plugin['name']] = False
    
    return results
```

### Phase 2: Call During First Scan

```python
def _scan_plugins(self):
    """Scan for installed plugins."""
    self.set_status("Scanning plugins...")
    
    def scan_thread():
        plugins = self.plugin_scanner.scan_plugins()
        self.installed_plugins = plugins
        
        # Check if this is first scan (no previous records)
        is_first_scan = len(self.database.get_installed_plugins()) == 0
        
        # Update database
        for plugin in plugins:
            self.database.add_installed_plugin(
                plugin['name'],
                plugin.get('version', 'Unknown'),
                plugin['path']
            )
        
        # Create initial backups if first scan
        if is_first_scan and plugins:
            self.set_status(f"Creating initial backups of {len(plugins)} plugins...")
            results = self.plugin_installer.create_initial_backups(plugins)
            
            success_count = sum(1 for v in results.values() if v)
            self.set_status(f"Initial backups created: {success_count}/{len(plugins)}")
        
        # Update GUI
        self.root.after(0, self._update_installed_list)
        self.root.after(0, lambda: self.set_status("Scan complete"))
    
    threading.Thread(target=scan_thread, daemon=True).start()
```

### Phase 3: Add Database Method

```python
def add_archive_record(self, plugin_name: str, version: str, archive_path: str, 
                      file_count: int = 0, total_size: int = 0):
    """Add archive record to database."""
    self.cursor.execute("""
        INSERT INTO plugin_archives 
        (plugin_name, version, archive_path, archived_date, file_count, total_size)
        VALUES (?, ?, ?, datetime('now'), ?, ?)
    """, (plugin_name, version, archive_path, file_count, total_size))
    self.conn.commit()
```

---

## 🧪 Testing Plan

### Test Case 1: Fresh Install (No Existing Plugins)
**Setup**: Clean OBS with no plugins  
**Action**: Run plugin manager, scan  
**Expected**: No backups created (nothing to backup)  
**Result**: ✅ Should pass (no plugins to backup)

### Test Case 2: Existing Plugins (First Scan)
**Setup**: OBS with 3 manually installed plugins  
**Action**: Run plugin manager for first time, scan  
**Expected**: 
- ✅ 3 plugins detected
- ✅ 3 initial backups created
- ✅ Archives in database
- ✅ Can view archives in GUI

### Test Case 3: Second Scan (Plugins Already Backed Up)
**Setup**: Already scanned and backed up  
**Action**: Scan again  
**Expected**:
- ✅ No duplicate backups created
- ✅ Original archives preserved
- ✅ Fast scan (no backup overhead)

### Test Case 4: Rollback to Initial Backup
**Setup**: Plugin backed up initially, then updated twice  
**Action**: Rollback → Rollback → Rollback  
**Expected**:
- ✅ First rollback → version before last update
- ✅ Second rollback → version before first update  
- ✅ Third rollback → **original/initial version** ✅
- ✅ All 3 rollbacks succeed

### Test Case 5: Disk Space Check
**Setup**: 10 large plugins (100MB each)  
**Action**: Initial scan with backups  
**Expected**:
- ✅ ~1GB disk space used for backups
- ⚠️ User notified of disk usage
- ✅ All backups complete successfully

---

## 📊 Impact of Fix

### Before Fix ❌

**Rollback capability**:
- Existing plugins: ❌ Can't rollback (no archives)
- After 1 update: ✅ Can rollback 1 level
- After 2 updates: ✅ Can rollback 2 levels

**User trust**: ⚠️ "Rollback doesn't work for my plugins!"

### After Fix ✅

**Rollback capability**:
- Existing plugins: ✅ Can rollback to original
- After 1 update: ✅ Can rollback 2 levels (original + updated)
- After 2 updates: ✅ Can rollback 2 levels (keep last 2)

**User trust**: ✅ "Rollback always works!"

---

## 🎯 Priority

**Severity**: HIGH ⚠️  
**User impact**: Can't rollback existing plugins  
**Frequency**: Affects ALL users with existing plugins (most common case)  
**Fix effort**: 2-3 hours  

**Recommendation**: **FIX BEFORE PRODUCTION RELEASE**

This violates user expectations and the documented feature ("last two versions").

---

## 📋 Summary

### The Bug

✅ User's assumption: "App backs up my plugins when it first sees them"  
❌ Actual behavior: "App only backs up when updating/removing"  
❌ Impact: Can't rollback to original versions  

### The Fix

1. Add `create_initial_backups()` method
2. Call during first scan
3. Store archives in database
4. Allow rollback to original state

### Why It Matters

**Without fix**: Users can't trust rollback feature  
**With fix**: Full rollback protection from day one  

---

**Status**: ❌ **NOT FIXED - NEEDS IMPLEMENTATION**  
**Priority**: ⚠️ **HIGH - Fix before production**  
**Effort**: 2-3 hours  
**User Impact**: **CRITICAL** (most users affected)

---

*"The best backup is the one you made before you needed it."*
