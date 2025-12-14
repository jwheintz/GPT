from __future__ import annotations

import shutil
import time
import zipfile
from pathlib import Path

import requests

from obs_plugin_manager.catalog import Catalog
from obs_plugin_manager.errors import InstallError, ObsRunningError
from obs_plugin_manager.paths import ObsPaths
from obs_plugin_manager.process import is_obs_running, kill_obs


def _ensure_obs_not_running(allow_kill_obs: bool) -> None:
    if not is_obs_running():
        return
    if not allow_kill_obs:
        raise ObsRunningError("OBS is running; refusing to write to OBS plugin folders")

    kill_obs(force=True)
    # Wait briefly for process to terminate
    for _ in range(30):
        if not is_obs_running():
            return
        time.sleep(0.25)

    raise ObsRunningError("OBS still appears to be running after kill attempt")


def _downloads_dir(state_dir: Path) -> Path:
    d = state_dir / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _archives_dir(state_dir: Path, plugin_id: str) -> Path:
    d = state_dir / "archives" / plugin_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download(url: str, dest: Path, timeout_s: int = 60) -> None:
    with requests.get(url, stream=True, timeout=timeout_s) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def _extract_zip(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)


def _find_layout(root: Path) -> tuple[Path | None, Path | None]:
    """Return (bin_root, data_root) within extracted directory.

    Supports common layouts:
    - obs-plugins/64bit/*.dll and data/obs-plugins/<plugin>
    - bin/64bit and data
    """

    # Layout A: OBS packaging
    bin_a = root / "obs-plugins" / "64bit"
    data_a = root / "data" / "obs-plugins"
    if bin_a.exists():
        return bin_a, data_a if data_a.exists() else None

    # Layout B: per-user plugin folder
    bin_b = root / "bin" / "64bit"
    data_b = root / "data"
    if bin_b.exists() or data_b.exists():
        return bin_b if bin_b.exists() else None, data_b if data_b.exists() else None

    # Sometimes everything is nested one level deep
    for child in [p for p in root.iterdir() if p.is_dir()]:
        b, d = _find_layout(child)
        if b or d:
            return b, d

    return None, None


def _archive_existing(
    *,
    state_dir: Path,
    plugin_id: str,
    obs_paths: ObsPaths,
    scope: str,
    meta: dict,
) -> None:
    arch_root = _archives_dir(state_dir, plugin_id)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    dest = arch_root / timestamp
    dest.mkdir(parents=True, exist_ok=True)

    primary_dll = meta.get("primary_dll")

    if scope == "global":
        if not obs_paths.global_bin_64:
            return
        if primary_dll:
            dll = obs_paths.global_bin_64 / primary_dll
            if dll.exists():
                shutil.copy2(dll, dest / primary_dll)
        if obs_paths.global_data:
            data_dir = obs_paths.global_data / plugin_id
            if data_dir.exists():
                shutil.copytree(data_dir, dest / "data", dirs_exist_ok=True)

    else:
        if not obs_paths.user_plugins_root:
            return
        plugin_dir = obs_paths.user_plugins_root / plugin_id
        if plugin_dir.exists():
            shutil.copytree(plugin_dir, dest / plugin_id, dirs_exist_ok=True)

    # Keep only last 2 archives
    backups = sorted([p for p in arch_root.iterdir() if p.is_dir()], reverse=True)
    for old in backups[2:]:
        shutil.rmtree(old, ignore_errors=True)


def install_or_update(
    *,
    plugin_id: str,
    catalog: Catalog,
    obs_paths: ObsPaths,
    state_dir: Path,
    allow_kill_obs: bool,
) -> dict:
    _ensure_obs_not_running(allow_kill_obs=allow_kill_obs)

    meta = catalog.get_plugin(plugin_id)
    if not meta:
        raise InstallError(f"Unknown plugin_id '{plugin_id}'. Seed catalog first.")

    download_url = meta.get("download_url")
    if not download_url:
        raise InstallError(f"No download_url in catalog for '{plugin_id}'. Run catalog refresh.")

    scope = str(meta.get("default_scope") or "global")
    if scope not in ("global", "user"):
        scope = "global"

    # Always archive before overwrite
    _archive_existing(
        state_dir=state_dir,
        plugin_id=plugin_id,
        obs_paths=obs_paths,
        scope=scope,
        meta=meta,
    )

    downloads = _downloads_dir(state_dir)
    ts = time.strftime("%Y%m%d-%H%M%S")
    zip_path = downloads / f"{plugin_id}-{ts}.zip"

    _download(str(download_url), zip_path)

    work_dir = state_dir / "work" / f"{plugin_id}-{ts}"
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    _extract_zip(zip_path, work_dir)
    bin_root, data_root = _find_layout(work_dir)

    if scope == "global":
        if not obs_paths.global_bin_64 or not obs_paths.global_bin_64.exists():
            raise InstallError("Could not locate global OBS plugin directory. Provide --obs-root.")

        if bin_root:
            for dll in bin_root.glob("*.dll"):
                shutil.copy2(dll, obs_paths.global_bin_64 / dll.name)

        if data_root and obs_paths.global_data:
            # If data_root points to data/obs-plugins, copy plugin folder if present
            src_plugin_data = data_root / plugin_id if data_root.name == "obs-plugins" else None
            if src_plugin_data and src_plugin_data.exists():
                dest_plugin_data = obs_paths.global_data / plugin_id
                dest_plugin_data.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_plugin_data, dest_plugin_data, dirs_exist_ok=True)

    else:
        if not obs_paths.user_plugins_root or not obs_paths.user_plugins_root.exists():
            raise InstallError("Could not locate user OBS plugins directory. Is %APPDATA% set?")

        plugin_dir = obs_paths.user_plugins_root / plugin_id
        plugin_dir.mkdir(parents=True, exist_ok=True)

        if bin_root:
            dest_bin = plugin_dir / "bin" / "64bit"
            dest_bin.mkdir(parents=True, exist_ok=True)
            for dll in bin_root.glob("*.dll"):
                shutil.copy2(dll, dest_bin / dll.name)

        if data_root:
            dest_data = plugin_dir / "data"
            dest_data.mkdir(parents=True, exist_ok=True)
            if data_root.name == "obs-plugins":
                src_plugin_data = data_root / plugin_id
                if src_plugin_data.exists():
                    shutil.copytree(src_plugin_data, dest_data, dirs_exist_ok=True)
            else:
                shutil.copytree(data_root, dest_data, dirs_exist_ok=True)

    return {
        "plugin_id": plugin_id,
        "installed": True,
        "scope": scope,
        "downloaded": str(zip_path),
        "archived": True,
    }


def rollback(
    *,
    plugin_id: str,
    obs_paths: ObsPaths,
    state_dir: Path,
    backup_index: int,
    allow_kill_obs: bool,
) -> dict:
    _ensure_obs_not_running(allow_kill_obs=allow_kill_obs)

    arch_root = _archives_dir(state_dir, plugin_id)
    backups = sorted([p for p in arch_root.iterdir() if p.is_dir()], reverse=True)
    if not backups:
        raise InstallError(f"No backups available for '{plugin_id}'")

    idx = backup_index - 1
    if idx < 0 or idx >= len(backups):
        raise InstallError(f"Invalid backup index {backup_index}. Available: 1..{len(backups)}")

    chosen = backups[idx]

    # Restore as user-plugin folder if present in backup; else restore global dll/data
    user_snapshot = chosen / plugin_id
    if user_snapshot.exists() and obs_paths.user_plugins_root:
        dest = obs_paths.user_plugins_root / plugin_id
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(user_snapshot, dest, dirs_exist_ok=True)
        return {"plugin_id": plugin_id, "rolled_back": True, "scope": "user", "backup": str(chosen)}

    # Global snapshot
    if obs_paths.global_bin_64:
        for dll in chosen.glob("*.dll"):
            shutil.copy2(dll, obs_paths.global_bin_64 / dll.name)

    data_snapshot = chosen / "data"
    if data_snapshot.exists() and obs_paths.global_data:
        dest_data = obs_paths.global_data / plugin_id
        if dest_data.exists():
            shutil.rmtree(dest_data, ignore_errors=True)
        shutil.copytree(data_snapshot, dest_data, dirs_exist_ok=True)

    return {"plugin_id": plugin_id, "rolled_back": True, "scope": "global", "backup": str(chosen)}
