# Discovery & Local Repository Guide

## Overview

OBS Plugin Manager now includes **Discovery** and **Local Repository** features that expand your plugin management capabilities with live GitHub queries and local file storage.

## 🔍 Discovery Tab

### What It Does

The Discovery tab queries GitHub in real-time to find:
- **New** - Recently updated OBS plugins (last 30 days)
- **Popular** - Most-starred OBS plugins (100+ stars)
- **Trending** - Recently created plugins gaining popularity fast
- **Scripts** - OBS Lua and Python scripts

### How It Works

1. **Live Queries**: Searches GitHub API for OBS-related repositories
2. **Smart Filtering**: Focuses on C/C++ plugins and Lua/Python scripts
3. **Caching**: Caches results for 6 hours to avoid API rate limits
4. **Auto-Categorization**: Automatically categorizes plugins by type

### Using Discovery

#### Browse Modes

Click the radio buttons to switch between:
- **New**: Plugins updated in the last 30 days
- **Popular**: Plugins with the most GitHub stars
- **Trending**: New plugins (< 180 days) with good star growth
- **Scripts**: OBS Lua and Python scripts

#### Refresh Live Data

Click **"Refresh Live Data"** to query GitHub API freshly:
- Forces new query ignoring cache
- Shows last update time
- Takes 5-15 seconds
- Limited to avoid GitHub API rate limits

#### View Details

Click any plugin/script to see:
- Full repository name
- Author information
- Star count and forks
- Programming language
- Description
- Homepage and download links
- Trending score (for trending mode)

#### Take Action

**Open Homepage**: Opens the GitHub repository in your browser

**Add to Catalog**: Adds the plugin to your Available Plugins catalog for easy access

### Discovery Features

#### Smart Search Queries

Searches for:
- `obs-studio plugin`
- `obs plugin`
- `obs-websocket`
- `obs filter/source/transition`

#### Known Developers

Tracks popular OBS plugin developers:
- obsproject (official)
- Exeldro (many popular plugins)
- royshil (AI plugins)
- FiniteSingularity (effects)
- WarmUpTill (scene switcher)
- And more...

#### Auto-Categorization

Automatically categorizes by keywords:
- **Effects**: filter, blur, shader, color
- **Sources**: source, input, capture
- **Transitions**: transition, move, slide
- **Output**: stream, rtmp, record
- **Audio**: audio, sound, volume
- **Integration**: websocket, api, midi, ndi
- **Automation**: scene, switch, auto
- **Scripts**: lua, python

### Cache System

**Cache Duration**: 6 hours

**Cache Benefits**:
- Reduces GitHub API calls
- Faster browsing
- Avoids rate limiting

**Cache Status**: Shows age of cached data at bottom right

**Clear Cache**: Use "Refresh Live Data" to force new query

### Trending Score

For trending plugins, calculates:
```
Score = (Stars / Days Old) * 10 + (Forks / Days Old) * 5
```

Higher score = more rapidly gaining popularity

## 📦 Local Repository Tab

### What It Does

Maintains a local storage of downloaded plugins and scripts with version tracking:
- Stores downloaded files locally
- Keeps last 2 versions of each plugin
- Tracks file sizes and dates
- Provides repository statistics

### Repository Structure

```
local_repository/
├── plugins/
│   └── plugin-name/
│       ├── 1.0.0/
│       │   └── plugin.dll
│       └── 1.1.0/
│           └── plugin.dll
├── scripts/
│   └── script-name/
│       ├── 1.0.0/
│       │   └── script.lua
│       └── 1.1.0/
│           └── script.lua
├── metadata/
└── repository_index.json
```

### Repository Features

#### Version Tracking

- Stores last 2 versions automatically
- Older versions automatically deleted
- SHA256 hash verification
- File size tracking
- Date tracking

#### Statistics Dashboard

Shows at a glance:
- Total plugins stored
- Total scripts stored
- Total versions
- Total disk space used

#### Two Tabs

**Plugins Tab**: Lists all stored plugins
- Plugin name
- Latest version
- Number of versions stored
- File size
- Date added

**Scripts Tab**: Lists all stored scripts
- Same information as plugins
- Separate from plugins for clarity

### Using Local Repository

#### Auto-Storage

When you download/install plugins:
- Automatically added to local repository
- Version tracked
- Metadata stored

#### Manual Operations

**Refresh**: Updates the view with current repository state

**Cleanup Orphaned Files**: Removes files not in index
- Finds files not referenced
- Frees disk space
- Safe operation

#### Repository Benefits

1. **Fast Reinstalls**: Don't need to re-download
2. **Version History**: Keep previous versions
3. **Offline Access**: Files available offline
4. **Backup**: Local backup of your plugins

## Integration Features

### Discovery → Catalog

From Discovery tab:
1. Find interesting plugin
2. Click "Add to Catalog"
3. Plugin appears in Available Plugins
4. Can install like any other plugin

### Discovery → Local Repo

When installing discovered plugins:
1. Downloads automatically
2. Stores in local repository
3. Keeps last 2 versions
4. Available for reinstall anytime

### Local Repo → Installation

Files in local repository:
- Can be installed directly
- No re-download needed
- Fast installation
- Version selection available

## Live Data Updates

### What "Live" Means

- Queries GitHub API in real-time
- Gets latest repository data
- Fresh star counts
- Recent update times
- Current descriptions

### Update Frequency

**Cached Data**: 6 hours
**Manual Refresh**: Anytime via button
**Automatic**: On first load (if no cache)

### Rate Limiting

**GitHub API Limits**:
- 60 requests/hour (unauthenticated)
- Shared across all queries

**Best Practices**:
- Use cached data when possible
- Refresh only when needed
- Wait a few minutes between refreshes
- Avoid rapid clicking

**If Rate Limited**:
- Wait 10-15 minutes
- Use cached data
- Check cache status indicator

## Advanced Features

### Metadata Storage

Each stored file includes:
- Plugin/script name
- Version string
- File path
- File size
- SHA256 hash
- Date added
- Custom metadata

### Index File

`repository_index.json` contains:
- All stored plugins
- All stored scripts
- Version information
- Metadata
- Timestamps

**Safe to backup**: Copy this file for backup

**Recovery**: Keep this file to rebuild index

### Export/Import

**Export Index**:
```python
local_repository.export_index(Path("backup_index.json"))
```

**Benefits**:
- Backup repository state
- Share with other installs
- Recovery tool

## Tips & Best Practices

### Discovery

1. **Start with Popular**: See what community uses
2. **Check Stars**: High stars = well-maintained
3. **Read Descriptions**: Understand what it does
4. **Visit Homepage**: Check documentation
5. **Add to Catalog**: Bookmark interesting plugins

### Local Repository

1. **Let It Auto-Store**: Don't manually manage
2. **Cleanup Occasionally**: Remove orphaned files
3. **Monitor Size**: Check disk usage
4. **Keep Index Safe**: Backup repository_index.json

### Combined Usage

1. Discover new plugins
2. Add to catalog
3. Install when ready
4. Auto-stores in local repo
5. Update as new versions release
6. Old versions kept for rollback

## Troubleshooting

### Discovery Issues

**"Error querying API"**
- Check internet connection
- Wait if rate limited
- Try again in 10 minutes

**"No results found"**
- Try different mode
- Refresh live data
- Check GitHub is accessible

**"Cache expired"**
- Normal after 6 hours
- Click "Refresh Live Data"
- Will query fresh data

### Repository Issues

**"Repository stats not loading"**
- Click "Refresh" button
- Check repository folder exists
- Verify permissions

**"Files missing"**
- Run "Cleanup Orphaned Files"
- Re-download plugins
- Check disk space

**"Index corrupted"**
- Backup `repository_index.json`
- Delete and let rebuild
- Re-scan plugins

## Performance

### Discovery Performance

- Initial query: 10-15 seconds
- Cached browsing: Instant
- Mode switching: < 1 second
- Refresh: 10-15 seconds

### Repository Performance

- File storage: Instant
- Index updates: < 1 second
- Cleanup: 2-5 seconds
- Stats calculation: < 1 second

### Disk Usage

**Typical Sizes**:
- Plugin: 1-10 MB each
- Script: < 1 MB each
- 2 versions: 2-20 MB per plugin
- 10 plugins: 20-200 MB total

**Cleanup Helps**:
- Removes orphaned files
- Keeps only 2 versions
- Maintains index

## Privacy & Security

### GitHub API

- Public API only
- No authentication needed
- No personal data sent
- Rate limited for protection

### Local Storage

- All files stored locally
- No cloud sync
- Your data stays private
- Standard file permissions

### Safety

- SHA256 hash verification
- Version tracking
- Auto-backup before overwrites
- Safe cleanup operations

## Future Enhancements

Planned features:
- Custom search queries
- Developer profiles
- Plugin ratings
- Community recommendations
- Dependency detection
- Auto-update notifications

---

## Quick Reference

| Feature | Location | Action |
|---------|----------|--------|
| Discover new plugins | Discovery → New | Browse + Add to Catalog |
| Find popular plugins | Discovery → Popular | Sort by stars |
| Find trending plugins | Discovery → Trending | Check trending score |
| Find scripts | Discovery → Scripts | Lua/Python scripts |
| Refresh live | Discovery | "Refresh Live Data" button |
| View repository | Local Repo tab | See all stored files |
| Cleanup files | Local Repo tab | "Cleanup Orphaned Files" |
| Check stats | Local Repo tab | Stats panel at top |

---

**Enjoy discovering new OBS plugins and keeping them organized!** 🔍📦
