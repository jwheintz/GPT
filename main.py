import argparse
import sys
import os
from obs_manager.database import PluginDatabase
from obs_manager.scanner import OBSScanner
from obs_manager.manager import PluginManager
from obs_manager.process import ProcessManager

def main():
    parser = argparse.ArgumentParser(description="Windows-Based OBS Plugin Management Solution")
    
    # Global arguments
    parser.add_argument("--obs-path", help="Path to OBS Studio installation", default=r"C:\Program Files\obs-studio")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Subcommands
    subparsers.add_parser("scan", help="Scan local OBS installation for plugins")
    subparsers.add_parser("list", help="List available plugins in database")
    
    install_parser = subparsers.add_parser("install", help="Install or update a plugin")
    install_parser.add_argument("plugin_name", help="Name of the plugin to install")
    
    rollback_parser = subparsers.add_parser("rollback", help="Rollback a plugin to previous version")
    rollback_parser.add_argument("plugin_name", help="Name of the plugin to rollback")
    
    subparsers.add_parser("status", help="Check if OBS is running")
    subparsers.add_parser("kill", help="Kill OBS process")
    subparsers.add_parser("refresh", help="Refresh plugin database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize components
    db = PluginDatabase()
    process_manager = ProcessManager()
    
    # Ensure we use a valid path or default
    obs_path = args.obs_path
    if os.name != 'nt' and not os.path.exists(obs_path):
        # Fallback for non-windows testing if path doesn't exist
        print(f"Warning: Path {obs_path} does not exist. Using current directory as mock OBS root.")
        obs_path = os.path.join(os.getcwd(), "mock_obs")
        os.makedirs(obs_path, exist_ok=True)

    scanner = OBSScanner(obs_path, db)
    manager = PluginManager(obs_path, db)

    if args.command == "scan":
        print(f"Scanning OBS at: {obs_path}")
        results = scanner.scan_plugins()
        print("\nInstalled Plugins:")
        for name, info in results.items():
            status = "Installed" if info["installed"] else "Not Found"
            ver = info.get("version")
            print(f"- {name}: {status} {f'({ver})' if ver else ''}")
            
            # Check for updates
            db_plugin = db.get_plugin(name)
            if db_plugin and info["installed"]:
                # Simple check: if db version is different and we detected *something* (we don't have real local version extraction yet)
                # In a real app, we'd compare versions.
                print(f"  Available Version: {db_plugin['version']}")

    elif args.command == "list":
        print("\nAvailable Plugins in Database:")
        for name in db.list_plugins():
            p = db.get_plugin(name)
            print(f"- {name} (v{p['version']}): {p['description']}")

    elif args.command == "install":
        print(f"Attempting to install {args.plugin_name}...")
        try:
            manager.install_plugin(args.plugin_name)
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "rollback":
        print(f"Attempting to rollback {args.plugin_name}...")
        try:
            manager.rollback_plugin(args.plugin_name)
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "status":
        if process_manager.is_obs_running():
            print("OBS is currently RUNNING.")
        else:
            print("OBS is NOT running.")

    elif args.command == "kill":
        try:
            manager.process_manager.ensure_obs_closed()
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "refresh":
        print("Refreshing database...")
        db.refresh_from_remote()
        print("Database updated.")

if __name__ == "__main__":
    main()
