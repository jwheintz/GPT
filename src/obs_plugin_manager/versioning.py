from __future__ import annotations

import os
import subprocess
from pathlib import Path


def get_file_version(path: Path) -> str | None:
    """Return Windows file version for a DLL/EXE, if available.

    Uses PowerShell VersionInfo on Windows. Returns None if unavailable.
    """

    if not path.exists():
        return None

    if os.name != "nt":
        return None

    # Use PowerShell to access file version info reliably.
    # Example: (Get-Item 'C:\path\file.dll').VersionInfo.FileVersion
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"(Get-Item '{str(path)}').VersionInfo.FileVersion",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, errors="replace")
        v = out.strip()
        return v or None
    except Exception:
        return None
