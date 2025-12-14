"""OBS Plugin Manager (Windows-first).

This tool does NOT integrate with OBS APIs.
It manages plugins by:
- maintaining a local catalog of known plugins
- scanning standard OBS plugin folders
- downloading and installing plugin packages safely

Safety: writes to OBS plugin directories are blocked while OBS is running.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
