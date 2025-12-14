#!/usr/bin/env python3
"""
OBS Plugin Manager - Main Entry Point
Windows-based OBS Plugin Management Solution
"""

import sys
from pathlib import Path

# Add the obs_plugin_manager directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from obs_plugin_manager.gui import main

if __name__ == "__main__":
    main()
