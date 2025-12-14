#!/usr/bin/env python3
"""
Setup script for OBS Plugin Manager.
Handles first-time setup and creates shortcuts.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version is 3.8+."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path(__file__).parent / ".venv"
    
    if venv_path.exists():
        print("✓ Virtual environment exists")
        return True
    
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install required packages."""
    venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    requirements = Path(__file__).parent / "requirements.txt"
    
    if not venv_python.exists():
        venv_python = sys.executable
    
    print("Installing dependencies...")
    try:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
            check=True
        )
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def create_shortcut():
    """Create desktop shortcut (Windows)."""
    if sys.platform != 'win32':
        print("Shortcut creation is only supported on Windows")
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "OBS Plugin Manager.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # Use pythonw for no console window
        venv_pythonw = Path(__file__).parent / ".venv" / "Scripts" / "pythonw.exe"
        main_py = Path(__file__).parent / "main.py"
        
        shortcut.Targetpath = str(venv_pythonw)
        shortcut.Arguments = str(main_py)
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.Description = "OBS Plugin Manager"
        shortcut.save()
        
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        return True
    except ImportError:
        print("Note: Install 'winshell' and 'pywin32' for desktop shortcut creation")
        return False
    except Exception as e:
        print(f"✗ Failed to create shortcut: {e}")
        return False


def setup_app_directory():
    """Create application data directories."""
    app_dir = Path.home() / "AppData" / "Local" / "OBSPluginManager"
    
    directories = [
        app_dir,
        app_dir / "archives",
        app_dir / "temp",
    ]
    
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
    
    print(f"✓ App data directory: {app_dir}")
    return True


def main():
    """Run setup."""
    print("=" * 50)
    print("OBS Plugin Manager - Setup")
    print("=" * 50)
    print()
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up app directory", setup_app_directory),
        ("Creating desktop shortcut", create_shortcut),
    ]
    
    success = True
    for name, func in steps:
        print(f"\n[{name}]")
        if not func():
            success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("✓ Setup complete!")
        print()
        print("To start the application:")
        print("  - Double-click 'run.bat'")
        print("  - Or run: python main.py")
        print("  - Or use the desktop shortcut")
    else:
        print("⚠ Setup completed with warnings")
        print("The application may still work.")
    
    print("=" * 50)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
