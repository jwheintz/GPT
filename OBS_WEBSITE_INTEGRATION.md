# OBS Website Integration - Complete Guide

## Overview

Version 2.0 now queries **BOTH** GitHub **AND** the official OBS Project website (obsproject.com) for plugin discovery!

This addresses the key point that GitHub isn't the main discussion spot - the **OBS forums and resources page** are where the community actually discusses and shares plugins.

## What's New

### Dual-Source Discovery

The Discovery tab now pulls from:
1. **GitHub** - Open source repositories with star counts
2. **OBS Resources** - Official OBS Project website (obsproject.com/forum/resources/)

You can choose:
- **Combined** - Best of both worlds
- **GitHub** - GitHub repositories only
- **OBS Site** - OBS Resources page only

## OBS Resources Integration

### What We Query

**Official OBS Resources Page**:
- https://obsproject.com/forum/resources/
- Categories: Plugins, Scripts, Themes, Overlays
- Community-approved and discussed resources

### Information Extracted

From each OBS resource:
- **Title** - Plugin/script name
- **Author** - Creator username
- **Version** - Current version
- **Description** - What it does
- **Rating** - User ratings (out of 5)
- **Downloads** - Download count
- **Last Update** - When last updated
- **Resource URL** - Link to discussion and download

### Why This Matters

The OBS Resources page shows:
- **Community-vetted plugins** - Discussed in forums
- **Official support** - Developers respond to issues
- **Download counts** - See what's actually used
- **User ratings** - Community feedback
- **Version history** - Track updates

## Using the New Discovery

### Source Selection

In the Discovery tab toolbar:

**Source**: `(o) Combined  (o) GitHub  (o) OBS Site`

- **Combined** - Queries both, merges results, removes duplicates
- **GitHub** - GitHub API only (open source repos)
- **OBS Site** - OBS Resources page only (community-approved)

### Mode Selection

**Mode**: `(o) Popular  (o) New  (o) Trending  (o) Scripts`

How modes work with sources:
- **GitHub + Popular** = Most-starred GitHub repos
- **OBS Site + Popular** = Highest-rated OBS resources
- **Combined + Popular** = Best from both!

## Features by Source

### GitHub Source

**Advantages**:
- Open source code visible
- Star count shows popularity
- Fork count shows usage
- Recent activity visible
- Direct repo access

**Data Shown**:
- Stars (⭐)
- Forks
- Language (C, C++, Python, Lua)
- GitHub username
- Last commit date

### OBS Site Source

**Advantages**:
- Community discussion threads
- Official forum support
- User ratings (1-5 stars)
- Download statistics
- Version history
- Installation guides

**Data Shown**:
- Rating (X.X/5.0)
- Downloads count
- User comments/support
- OBS forum username
- Last update date

### Combined Source

**Best of Both**:
- GitHub repos + OBS resources
- Deduplicated (same plugin from both = one entry)
- Sorted by popularity (stars + ratings)
- Shows source for each: `[GitHub]` or `[OBS Resources]`

## How It Works

### Web Scraping

**OBS Resources uses**:
- BeautifulSoup4 for HTML parsing
- Requests for HTTP

**What we extract**:
```python
# From each resource item
- Title and link
- Author username
- Version number
- Description/tagline
- Rating (X/5)
- Download count
- Last update date
- Category
```

### Caching Strategy

**GitHub**: 6-hour cache
**OBS Resources**: 24-hour cache (less frequent changes)

Why longer cache for OBS:
- OBS resources don't update as frequently
- Reduces load on OBS servers
- Community ratings don't change rapidly

### Rate Limiting

**GitHub API**: 60 requests/hour (no auth)
**OBS Website**: No official limits, but we're polite

Our approach:
- Cache aggressively
- Manual refresh only
- Respectful query intervals
- User-Agent identifies us

## Example Workflows

### Find Community Favorites

1. Select **Source: OBS Site**
2. Select **Mode: Popular**
3. Click **Refresh Live Data**
4. See highest-rated plugins from community
5. Click plugin to see ratings and downloads
6. Click **Open Homepage** to read discussions

### Compare Sources

1. Select **Source: Combined**
2. Select **Mode: Popular**
3. Refresh for latest data
4. Look at source tags: `[GitHub]` vs `[OBS Resources]`
5. GitHub plugins show stars
6. OBS plugins show ratings + downloads
7. Choose based on your preference

### Find New Releases

1. Select **Source: GitHub**
2. Select **Mode: New**
3. See recently updated repos
4. Fresh code, active development
5. Switch to **Source: OBS Site**
6. See recently posted resources
7. Community discussion available

## Data Display

### In Plugin List

**GitHub Plugins**:
```
[GitHub] StreamFX  | Xaymar | 2150 | Effects | 2025-12-10
```

**OBS Resources**:
```
[OBS Resources] Move Transition | Exeldro | 4.8⭐ (15k dl) | Transitions | 2025-12-08
```

### In Details Panel

**GitHub Plugin**:
```
StreamFX
============================================================

Source: GitHub
Repository: Xaymar/obs-StreamFX
Author: Xaymar
Category: Effects
Stars: ⭐ 2150
Forks: 180
Language: C++
Type: OBS Plugin

Last Updated: 2025-12-10

Description:
Modern effects plugin for OBS Studio...

Homepage: https://github.com/Xaymar/obs-StreamFX
Download: https://github.com/Xaymar/obs-StreamFX/releases/latest
```

**OBS Resource**:
```
Move Transition
============================================================

Source: OBS Resources
Author: Exeldro
Category: Transitions
Rating: 4.8/5.0
Downloads: 15,234
Version: 2.9.0
Type: OBS Plugin

Last Updated: 2025-12-08

Description:
Plugin to move source to a new position during scene transition...

Homepage: https://obsproject.com/forum/resources/move-transition.913/
Download: https://obsproject.com/forum/resources/move-transition.913/
```

## Benefits of Dual-Source

### Complete Coverage

- **GitHub**: Developer-focused, open source
- **OBS Site**: User-focused, community support

### Different Perspectives

- **Stars** (GitHub): Developer interest
- **Ratings** (OBS): User satisfaction
- **Forks** (GitHub): Code reuse
- **Downloads** (OBS): Actual usage

### Community Connection

- **GitHub Issues**: Technical problems
- **OBS Forum**: User discussion, tips, help

### Discovery Variety

- Some plugins only on GitHub
- Some only on OBS Resources
- Combined gives complete picture

## Technical Details

### HTML Parsing

OBS Resources page structure:
```html
<div class="resourceListItem">
  <a class="resourceTitle">Plugin Name</a>
  <a class="username">Author</a>
  <span class="version">1.0.0</span>
  <div class="resourceTagLine">Description</div>
  <dl class="resourceStats">
    <dt>Downloads</dt><dd>1,234</dd>
  </dl>
</div>
```

We extract all metadata and parse into our standard format.

### Auto-Categorization

Categories determined by keywords in title/description:
- **Effects**: filter, blur, shader, color
- **Sources**: source, capture, browser
- **Transitions**: transition, move, slide
- **Output**: stream, rtmp, record
- **Audio**: audio, sound, volume
- **Integration**: websocket, api, midi, ndi
- **Automation**: scene, switch, auto
- **Scripts**: lua, python

### Error Handling

If OBS website query fails:
- Falls back to cached data
- Shows cache age
- User can try again later
- GitHub still works independently

## Configuration

### Cache Directories

```
obs-plugin-manager/
├── discovery_cache/           (GitHub cache - 6 hours)
│   └── discovery_cache.json
└── obs_resources_cache/       (OBS cache - 24 hours)
    └── obs_resources_cache.json
```

### Dependencies

Added to requirements.txt:
```
beautifulsoup4>=4.12.0  # HTML parsing for OBS website
```

Install with:
```bash
pip install beautifulsoup4
```

## Tips & Best Practices

### When to Use Each Source

**Use GitHub when**:
- Want to see source code
- Checking development activity
- Looking for forks/variations
- Need technical details

**Use OBS Site when**:
- Want community feedback
- Need installation help
- Looking for support threads
- Checking compatibility reports

**Use Combined when**:
- Want everything
- Discovering new plugins
- Comparing options
- Not sure what you need

### Reading the Data

**High GitHub stars** = Developer interest, technical merit
**High OBS rating** = User satisfaction, ease of use
**High OBS downloads** = Proven, widely used
**Recent updates** = Active development, maintained

### Community Research

For any plugin of interest:
1. Check GitHub for code quality
2. Check OBS forums for user experiences
3. Read ratings and comments
4. Look for recent updates
5. Verify Windows compatibility

## Troubleshooting

### OBS Website Query Fails

**Error**: "Error querying OBS Resources"

**Solutions**:
1. Check internet connection
2. Verify obsproject.com is accessible
3. Use cached data (if available)
4. Switch to GitHub source
5. Try again later

### Missing Plugins

**Some plugins don't appear**:
- May not be on OBS Resources page
- May be GitHub-only
- May be in different category
- Try searching both sources

### Duplicate Entries

**Same plugin appears twice**:
- Use "Combined" source
- Automatically deduplicates
- Shows one entry with source tag
- Prefers GitHub data (more metadata)

## Future Enhancements

Planned improvements:
- Parse forum discussion threads
- Extract user reviews/comments
- Show compatibility reports
- Track update frequency
- Alert on new releases

## Privacy & Ethics

### Respectful Scraping

- Caches aggressively (24 hours)
- Identifies as OBS Plugin Manager
- Only queries when user requests
- No automated polling
- Respects server load

### Data Usage

- Only public data
- No personal info collected
- No authentication needed
- Read-only access
- Links back to original sources

## Summary

**Version 2.0 now gives you the complete picture**:

✅ **GitHub** - Developer community  
✅ **OBS Resources** - User community  
✅ **Combined** - Best of both worlds  

**Discover plugins from where they're actually discussed!**

---

**See also**:
- [DISCOVERY_GUIDE.md](DISCOVERY_GUIDE.md) - Full discovery documentation
- [VERSION_2_UPDATES.md](VERSION_2_UPDATES.md) - Technical changelog
- [WHATS_NEW_V2.md](WHATS_NEW_V2.md) - User-friendly updates

---

**Now you can explore the full OBS plugin ecosystem!** 🔍✨
