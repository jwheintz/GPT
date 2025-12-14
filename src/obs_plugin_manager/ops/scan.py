from __future__ import annotations

from pathlib import Path

from obs_plugin_manager.catalog import Catalog
from obs_plugin_manager.models import InstalledPlugin
from obs_plugin_manager.paths import ObsPaths
from obs_plugin_manager.versioning import get_file_version


def _guess_primary_dll(bin_dir: Path, preferred: str | None) -> Path | None:
    if preferred:
        p = bin_dir / preferred
        if p.exists():
            return p

    dlls = sorted(bin_dir.glob("*.dll"))
    return dlls[0] if dlls else None


def _scan_user_plugins(plugins_root: Path, catalog: Catalog) -> list[InstalledPlugin]:
    out: list[InstalledPlugin] = []
    if not plugins_root.exists():
        return out

    for plugin_dir in sorted([p for p in plugins_root.iterdir() if p.is_dir()]):
        plugin_id = plugin_dir.name
        meta = catalog.get_plugin(plugin_id)
        name = meta.get("name") if meta else plugin_id
        primary = meta.get("primary_dll") if meta else None

        bin_dir = plugin_dir / "bin" / "64bit"
        data_dir = plugin_dir / "data"

        installed_version = None
        version_source = None
        if bin_dir.exists():
            dll = _guess_primary_dll(bin_dir, primary)
            if dll:
                installed_version = get_file_version(dll)
                version_source = str(dll)

        out.append(
            InstalledPlugin(
                plugin_id=plugin_id,
                name=str(name),
                location="user",
                bin_path=bin_dir if bin_dir.exists() else None,
                data_path=data_dir if data_dir.exists() else None,
                installed_version=installed_version,
                version_source=version_source,
            )
        )

    return out


def _scan_global_plugins(
    global_bin_64: Path, global_data: Path | None, catalog: Catalog
) -> list[InstalledPlugin]:
    out: list[InstalledPlugin] = []
    if not global_bin_64.exists():
        return out

    # Global bin folder is flat; plugin DLL names vary. We use catalog primary_dll mapping.
    plugins = catalog.list_plugins()
    for meta in plugins:
        primary = meta.get("primary_dll")
        if not primary:
            continue
        dll = global_bin_64 / primary
        if not dll.exists():
            continue

        installed_version = get_file_version(dll)
        data_path = None
        if global_data and global_data.exists():
            cand = global_data / meta["plugin_id"]
            if cand.exists():
                data_path = cand

        out.append(
            InstalledPlugin(
                plugin_id=str(meta["plugin_id"]),
                name=str(meta.get("name") or meta["plugin_id"]),
                location="global",
                bin_path=global_bin_64,
                data_path=data_path,
                installed_version=installed_version,
                version_source=str(dll),
            )
        )

    return out


def scan_installed(obs_paths: ObsPaths, catalog: Catalog) -> list[InstalledPlugin]:
    """Scan common OBS plugin locations and return best-effort installed list."""

    out: list[InstalledPlugin] = []

    if obs_paths.user_plugins_root:
        out.extend(_scan_user_plugins(obs_paths.user_plugins_root, catalog=catalog))

    if obs_paths.global_bin_64:
        out.extend(
            _scan_global_plugins(
                global_bin_64=obs_paths.global_bin_64,
                global_data=obs_paths.global_data,
                catalog=catalog,
            )
        )

    # De-dupe: prefer user location over global if same plugin_id
    by_id: dict[str, InstalledPlugin] = {}
    for p in out:
        existing = by_id.get(p.plugin_id)
        if not existing:
            by_id[p.plugin_id] = p
            continue
        if existing.location == "global" and p.location == "user":
            by_id[p.plugin_id] = p

    return sorted(by_id.values(), key=lambda x: x.plugin_id)
