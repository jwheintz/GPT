from __future__ import annotations

import json
import sqlite3
import time
from importlib import resources
from pathlib import Path
from typing import Any

from packaging.version import InvalidVersion, Version

from obs_plugin_manager.errors import CatalogError
from obs_plugin_manager.models import InstalledPlugin, UpdateAvailable
from obs_plugin_manager.providers.github_release import fetch_latest_release

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS plugins (
  plugin_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  homepage TEXT,
  suggested INTEGER NOT NULL DEFAULT 0,
  primary_dll TEXT,
  default_scope TEXT NOT NULL DEFAULT 'global',
  provider_json TEXT NOT NULL,
  latest_version TEXT,
  download_url TEXT,
  updated_at INTEGER
);
"""


class Catalog:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.db_path = state_dir / "catalog.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript(SCHEMA_SQL)

    def upsert_plugins(self, plugins: list[dict[str, Any]]) -> int:
        """Upsert plugin definitions into the catalog.

        Expected schema per item:
          - plugin_id (str, required)
          - name (str, required)
          - description (str, optional)
          - homepage (str, optional)
          - suggested (bool, optional)
          - primary_dll (str, optional)
          - default_scope ('global'|'user', optional)
          - provider (dict, optional)
        """

        now = int(time.time())
        upserted = 0
        with self._connect() as con:
            for p in plugins:
                if not isinstance(p, dict):
                    continue
                plugin_id = str(p.get("plugin_id") or "").strip()
                name = str(p.get("name") or "").strip()
                if not plugin_id or not name:
                    continue

                con.execute(
                    """
                    INSERT INTO plugins (
                      plugin_id,
                      name,
                      description,
                      homepage,
                      suggested,
                      primary_dll,
                      default_scope,
                      provider_json,
                      updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(plugin_id) DO UPDATE SET
                      name=excluded.name,
                      description=excluded.description,
                      homepage=excluded.homepage,
                      suggested=excluded.suggested,
                      primary_dll=excluded.primary_dll,
                      default_scope=excluded.default_scope,
                      provider_json=excluded.provider_json,
                      updated_at=excluded.updated_at
                    """,
                    (
                        plugin_id,
                        name,
                        p.get("description"),
                        p.get("homepage"),
                        1 if p.get("suggested") else 0,
                        p.get("primary_dll"),
                        p.get("default_scope") or "global",
                        json.dumps(p.get("provider") or {}),
                        now,
                    ),
                )
                upserted += 1
        return upserted

    def seed_builtin(self) -> int:
        """Upsert built-in seed plugin definitions."""

        try:
            seed_text = (
                resources.files("obs_plugin_manager.data")
                .joinpath("catalog_seed.json")
                .read_text(encoding="utf-8")
            )
            seed = json.loads(seed_text)
        except Exception as e:
            raise CatalogError(f"Failed to load built-in seed: {e}") from e

        if not isinstance(seed, list):
            raise CatalogError("Seed JSON must be a list")

        return self.upsert_plugins(seed)

    def list_plugins(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM plugins ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def get_plugin(self, plugin_id: str) -> dict[str, Any] | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM plugins WHERE plugin_id=?", (plugin_id,)).fetchone()
        return dict(row) if row else None

    def refresh_versions(self) -> int:
        """Refresh latest_version + download_url for each plugin based on provider_json."""

        plugins = self.list_plugins()
        now = int(time.time())
        updated = 0

        with self._connect() as con:
            for p in plugins:
                provider = json.loads(p.get("provider_json") or "{}")
                if provider.get("type") != "github_release":
                    continue
                repo = provider.get("repo")
                if not repo:
                    continue
                asset_regex = provider.get("asset_regex")

                try:
                    rel = fetch_latest_release(repo=repo, asset_regex=asset_regex)
                except Exception:
                    continue

                con.execute(
                    "UPDATE plugins SET latest_version=?, download_url=?, updated_at=? "
                    "WHERE plugin_id=?",
                    (rel.version, rel.asset_url, now, p["plugin_id"]),
                )
                updated += 1

        return updated

    def compute_updates(self, installed: list[InstalledPlugin]) -> list[UpdateAvailable]:
        out: list[UpdateAvailable] = []
        for inst in installed:
            meta = self.get_plugin(inst.plugin_id)
            if not meta:
                continue
            latest_version = meta.get("latest_version")
            download_url = meta.get("download_url")
            if not latest_version or not download_url:
                continue

            if inst.installed_version is None:
                # If unknown installed version, still report as "update" (actionable download).
                out.append(
                    UpdateAvailable(
                        plugin_id=inst.plugin_id,
                        name=inst.name,
                        installed_version=None,
                        latest_version=str(latest_version),
                        download_url=str(download_url),
                    )
                )
                continue

            try:
                if Version(str(inst.installed_version)) < Version(str(latest_version)):
                    out.append(
                        UpdateAvailable(
                            plugin_id=inst.plugin_id,
                            name=inst.name,
                            installed_version=inst.installed_version,
                            latest_version=str(latest_version),
                            download_url=str(download_url),
                        )
                    )
            except InvalidVersion:
                # If versions are non-semver, compare as strings (fallback)
                if str(inst.installed_version) != str(latest_version):
                    out.append(
                        UpdateAvailable(
                            plugin_id=inst.plugin_id,
                            name=inst.name,
                            installed_version=inst.installed_version,
                            latest_version=str(latest_version),
                            download_url=str(download_url),
                        )
                    )

        return out

    def recommend(self, installed: list[InstalledPlugin]) -> list[dict[str, Any]]:
        installed_ids = {p.plugin_id for p in installed}
        with self._connect() as con:
            rows = con.execute(
                "SELECT plugin_id, name, description, homepage "
                "FROM plugins WHERE suggested=1 ORDER BY name"
            ).fetchall()
        recs: list[dict[str, Any]] = []
        for r in rows:
            if r["plugin_id"] in installed_ids:
                continue
            recs.append(
                {
                    "plugin_id": r["plugin_id"],
                    "name": r["name"],
                    "description": r["description"],
                    "homepage": r["homepage"],
                }
            )
        return recs
