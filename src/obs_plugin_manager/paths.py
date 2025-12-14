from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ObsPaths:
    """Resolved OBS paths used by the manager.

    obs_root: Installation root (e.g. C:\\Program Files\\obs-studio)
    user_config_root: %APPDATA%\\obs-studio

    Global plugin locations (under obs_root):
      - bin plugins: obs-plugins\\64bit
      - data plugins: data\\obs-plugins

    User plugin locations (under user_config_root):
      - plugins\\<plugin>\\bin\\64bit
      - plugins\\<plugin>\\data
    """

    obs_root: Path | None
    user_config_root: Path | None

    @property
    def global_bin_64(self) -> Path | None:
        if not self.obs_root:
            return None
        return self.obs_root / "obs-plugins" / "64bit"

    @property
    def global_data(self) -> Path | None:
        if not self.obs_root:
            return None
        return self.obs_root / "data" / "obs-plugins"

    @property
    def user_plugins_root(self) -> Path | None:
        if not self.user_config_root:
            return None
        return self.user_config_root / "plugins"


def _windows_env_path(var: str) -> Path | None:
    v = os.environ.get(var)
    return Path(v) if v else None


def detect_obs_paths(obs_root_hint: str | None = None) -> ObsPaths:
    """Best-effort OBS path detection for Windows.

    This is heuristic-based (no OBS integration). Users can override obs_root_hint.
    """

    obs_root: Path | None = Path(obs_root_hint) if obs_root_hint else None

    # Common Windows installer path
    if obs_root is None:
        pf = _windows_env_path("ProgramFiles")
        if pf:
            cand = pf / "obs-studio"
            if (cand / "bin" / "64bit" / "obs64.exe").exists():
                obs_root = cand

    # Portable mode: if launched from a folder with obs64.exe, obs_root is that parent.
    # (Only relevant when running from within a portable OBS directory.)
    if obs_root is None:
        cwd = Path.cwd()
        if (cwd / "bin" / "64bit" / "obs64.exe").exists():
            obs_root = cwd

    user_config_root: Path | None = None
    appdata = _windows_env_path("APPDATA")
    if appdata:
        cand = appdata / "obs-studio"
        if cand.exists():
            user_config_root = cand

    return ObsPaths(obs_root=obs_root, user_config_root=user_config_root)
