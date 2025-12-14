# OBS Plugin Manager (Windows, file-based)

This repository provides a **Windows-based OBS Plugin Management solution** that **does not integrate with OBS** (no OBS API usage). Instead it:

- **Maintains a local catalog** of popular plugins (seeded JSON + SQLite database)
- **Refreshes the catalog** by querying online sources (currently GitHub Releases)
- **Scans your OBS install + user plugin folders** to detect what plugins you have
- **Compares installed vs latest** and reports available updates
- **Downloads and installs updates** (only via filesystem operations)
- **Never writes to OBS plugin folders while OBS is running**
  - It can **detect** OBS running, and can **kill OBS** if you allow it
- **Archives the last two versions** before overwrite so you can **rollback**

## Quickstart (Windows)

Prereqs: **Python 3.10+**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# seed local catalog
obs-plugin-manager catalog seed

# fetch latest versions/download URLs
obs-plugin-manager catalog refresh

# (optional) merge additional plugin definitions (JSON list) from file or URL
obs-plugin-manager catalog import plugins.json
obs-plugin-manager catalog import https://example.com/obs-plugin-catalog.json

# show detected OBS paths + running state
obs-plugin-manager status

# scan installed plugins
obs-plugin-manager scan

# show updates available
obs-plugin-manager updates

# download a plugin package to cache (no install)
obs-plugin-manager download obs-websocket

# install/update one plugin (will refuse if OBS is running unless you allow kill)
obs-plugin-manager install obs-websocket --allow-kill-obs

# rollback using archived backups (1 = most recent)
obs-plugin-manager rollback obs-websocket --index 1 --allow-kill-obs
```

Notes:
- If OBS isn’t in the default install location, pass `--obs-root "C:\\Program Files\\obs-studio"` (or your path).
- The tool stores its state (catalog, downloads, archives) under `%USERPROFILE%\\.obs_plugin_manager` by default.

## Links

- Getting started: `GETTING_STARTED.md`
- Contributing: `CONTRIBUTING.md`
