# OBS Plugin Manager

A Windows-based management tool for OBS Studio plugins. This tool helps you manage, install, update, and backup your OBS plugins without integrating directly into OBS.

## Features

- **Database of Plugins**: Maintains a local database of plugins.
- **Scanning**: Detects installed plugins in your OBS directory.
- **Safety**: Prevents installation if OBS is currently running.
- **Process Management**: Can check status and kill OBS process.
- **Backups**: Automatically backs up plugin files before installation/update.
- **Rollback**: Easily rollback to previous versions of a plugin.

## Installation

1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The tool is a command-line interface. Run `python main.py` to see available commands.

### Commands

- **Scan for plugins**:
  ```bash
  python main.py scan
  ```
  Optionally specify OBS path if not standard:
  ```bash
  python main.py --obs-path "D:\OBS Studio" scan
  ```

- **List available plugins**:
  ```bash
  python main.py list
  ```

- **Install a plugin**:
  ```bash
  python main.py install <plugin_name>
  ```
  Example: `python main.py install obs-websocket`

- **Rollback a plugin**:
  ```bash
  python main.py rollback <plugin_name>
  ```

- **Check OBS Status**:
  ```bash
  python main.py status
  ```

- **Kill OBS Process**:
  ```bash
  python main.py kill
  ```

- **Update Plugin Database**:
  ```bash
  python main.py refresh
  ```

## Configuration

The tool defaults to `C:\Program Files\obs-studio` for the OBS path on Windows. You can override this with the `--obs-path` argument.

## Data

- Plugin database is stored in `obs_manager/data/plugins.json`.
- Backups are stored in `obs_manager/backups/`.
