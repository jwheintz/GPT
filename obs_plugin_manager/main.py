#!/usr/bin/env python3
"""
OBS Plugin Manager - Main Entry Point

A Windows-based OBS Studio plugin management solution.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                Path.home() / "AppData" / "Local" / "OBSPluginManager" / "app.log",
                mode='a',
                encoding='utf-8'
            )
        ]
    )


def run_gui():
    """Run the GUI application."""
    from src.gui import main
    main()


def run_cli(args):
    """Run CLI commands."""
    from src.config import get_config
    from src.database import PluginDatabase
    from src.obs_scanner import OBSScanner
    from src.process_manager import ProcessManager
    from src.plugin_manager import PluginManager
    from src.catalog_refresh import CatalogRefresher
    
    config = get_config()
    db = PluginDatabase()
    scanner = OBSScanner(config)
    pm = ProcessManager()
    plugin_mgr = PluginManager(config)
    catalog = CatalogRefresher(db)
    
    if args.command == 'scan':
        print("Scanning OBS installation...")
        obs_info = scanner.scan_obs_installation()
        
        if obs_info:
            print(f"\nOBS Installation Found:")
            print(f"  Path: {obs_info.install_path}")
            print(f"  Version: {obs_info.version}")
            print(f"  64-bit: {obs_info.is_64bit}")
            print(f"  Plugins: {obs_info.plugins_path}")
        else:
            print("OBS installation not found.")
            return
        
        print("\nInstalled Plugins:")
        plugins = scanner.scan_plugins()
        
        if not plugins:
            print("  No third-party plugins found.")
        else:
            for plugin in plugins:
                status = ""
                if plugin.matched_catalog_id:
                    catalog_plugin = db.get_plugin(plugin.matched_catalog_id)
                    if catalog_plugin:
                        if plugin.version != catalog_plugin.latest_version:
                            status = f" (Update available: {catalog_plugin.latest_version})"
                
                print(f"  - {plugin.name} v{plugin.version}{status}")
    
    elif args.command == 'list':
        print("Plugin Catalog:")
        print("-" * 60)
        
        if args.category:
            plugins = db.get_plugins_by_category(args.category)
        elif args.popular:
            plugins = db.get_popular_plugins()
        elif args.recommended:
            plugins = db.get_recommended_plugins()
        else:
            plugins = db.get_all_plugins()
        
        for plugin in plugins:
            badges = []
            if plugin.is_recommended:
                badges.append("⭐")
            if plugin.is_popular:
                badges.append("🔥")
            
            badge_str = " ".join(badges) + " " if badges else ""
            print(f"{badge_str}{plugin.name}")
            print(f"    by {plugin.author} | v{plugin.latest_version} | {plugin.category}")
            print(f"    {plugin.description[:80]}...")
            print()
    
    elif args.command == 'updates':
        print("Checking for updates...")
        updates = scanner.check_updates()
        
        if not updates:
            print("All plugins are up to date!")
        else:
            print(f"\n{len(updates)} updates available:")
            for update in updates:
                print(f"  - {update['plugin_name']}: {update['current_version']} -> {update['latest_version']}")
    
    elif args.command == 'status':
        info = pm.get_process_info()
        print(f"OBS Status: {'Running' if info['running'] else 'Not Running'}")
        
        if info['running']:
            print(f"  PID: {info['pid']}")
            print(f"  Memory: {info['memory_mb']} MB")
            print(f"  Uptime: {info['uptime']}")
    
    elif args.command == 'kill':
        if pm.is_obs_running():
            print("Killing OBS...")
            if pm.kill_obs(force=args.force):
                print("OBS terminated successfully.")
            else:
                print("Failed to terminate OBS.")
        else:
            print("OBS is not running.")
    
    elif args.command == 'refresh':
        print("Refreshing plugin catalog from GitHub...")
        
        def progress(current, total, msg):
            print(f"  [{current}/{total}] {msg}")
        
        result = catalog.refresh_all(progress_callback=progress)
        print(f"\nCatalog updated:")
        print(f"  Added: {result.plugins_added}")
        print(f"  Updated: {result.plugins_updated}")
        print(f"  Total: {result.plugins_total}")
    
    elif args.command == 'install':
        if pm.is_obs_running():
            print("ERROR: Cannot install plugins while OBS is running.")
            print("Use 'obs-plugin-manager kill' to stop OBS first.")
            return
        
        plugin = db.get_plugin(args.plugin_id)
        if not plugin:
            # Search by name
            results = db.search_plugins(args.plugin_id)
            if results:
                plugin = results[0]
                print(f"Found plugin: {plugin.name}")
            else:
                print(f"Plugin '{args.plugin_id}' not found in catalog.")
                return
        
        print(f"Installing {plugin.name} v{plugin.latest_version}...")
        
        def progress(p):
            print(f"  Downloading: {p.percent:.1f}%")
        
        result = plugin_mgr.download_and_install(
            plugin.id,
            plugin.download_url,
            plugin.latest_version,
            progress_callback=progress
        )
        
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ {result.message}")
    
    elif args.command == 'uninstall':
        if pm.is_obs_running():
            print("ERROR: Cannot uninstall plugins while OBS is running.")
            return
        
        result = plugin_mgr.uninstall_plugin(args.plugin_id)
        
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ {result.message}")
    
    elif args.command == 'rollback':
        if pm.is_obs_running():
            print("ERROR: Cannot rollback plugins while OBS is running.")
            return
        
        archives = plugin_mgr.get_archive_info(args.plugin_id)
        
        if not archives:
            print(f"No archived versions found for '{args.plugin_id}'")
            return
        
        if args.version:
            version = args.version
        else:
            print("Available versions for rollback:")
            for i, archive in enumerate(archives):
                print(f"  {i+1}. v{archive['version']} ({archive['archive_date'][:10]})")
            
            choice = input("\nSelect version number: ")
            try:
                idx = int(choice) - 1
                version = archives[idx]['version']
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        print(f"Rolling back to v{version}...")
        result = plugin_mgr.rollback_plugin(args.plugin_id, version)
        
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ {result.message}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OBS Plugin Manager - Manage OBS Studio plugins on Windows"
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # GUI (default)
    gui_parser = subparsers.add_parser('gui', help='Launch GUI application')
    
    # Scan
    scan_parser = subparsers.add_parser('scan', help='Scan installed plugins')
    
    # List catalog
    list_parser = subparsers.add_parser('list', help='List plugins in catalog')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--popular', action='store_true', help='Show popular plugins')
    list_parser.add_argument('--recommended', action='store_true', help='Show recommended plugins')
    
    # Check updates
    updates_parser = subparsers.add_parser('updates', help='Check for plugin updates')
    
    # OBS status
    status_parser = subparsers.add_parser('status', help='Check OBS running status')
    
    # Kill OBS
    kill_parser = subparsers.add_parser('kill', help='Kill OBS process')
    kill_parser.add_argument('-f', '--force', action='store_true', help='Force kill')
    
    # Refresh catalog
    refresh_parser = subparsers.add_parser('refresh', help='Refresh plugin catalog')
    
    # Install
    install_parser = subparsers.add_parser('install', help='Install a plugin')
    install_parser.add_argument('plugin_id', help='Plugin ID or name')
    
    # Uninstall
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a plugin')
    uninstall_parser.add_argument('plugin_id', help='Plugin ID')
    
    # Rollback
    rollback_parser = subparsers.add_parser('rollback', help='Rollback plugin to previous version')
    rollback_parser.add_argument('plugin_id', help='Plugin ID')
    rollback_parser.add_argument('--version', help='Specific version to rollback to')
    
    args = parser.parse_args()
    
    # Ensure log directory exists
    log_dir = Path.home() / "AppData" / "Local" / "OBSPluginManager"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    setup_logging(args.verbose)
    
    if args.command is None or args.command == 'gui':
        run_gui()
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
