from __future__ import annotations

import subprocess

OBS_PROCESS_NAMES = ("obs64.exe", "obs32.exe")


def is_obs_running() -> bool:
    """Return True if OBS appears to be running (Windows tasklist).

    On non-Windows platforms, falls back to checking for typical process names via `ps`.
    """

    try:
        # Windows
        out = subprocess.check_output(["tasklist"], text=True, errors="replace")
        out_lower = out.lower()
        return any(name.lower() in out_lower for name in OBS_PROCESS_NAMES)
    except Exception:
        # Non-Windows fallback (best-effort)
        try:
            out = subprocess.check_output(["ps", "-A"], text=True, errors="replace")
            out_lower = out.lower()
            return any(name.lower().replace(".exe", "") in out_lower for name in OBS_PROCESS_NAMES)
        except Exception:
            return False


def kill_obs(force: bool = True) -> None:
    """Kill OBS if running.

    Uses taskkill on Windows. No-op if processes not present.
    """

    # Windows-first
    for name in OBS_PROCESS_NAMES:
        try:
            args = ["taskkill", "/IM", name]
            if force:
                args.append("/F")
            subprocess.run(args, check=False, capture_output=True, text=True)
        except Exception:
            # Best-effort; ignore failures
            pass
