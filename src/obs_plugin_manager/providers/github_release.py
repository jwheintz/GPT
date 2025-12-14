from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class GitHubReleaseResult:
    version: str
    asset_url: str
    asset_name: str


def _strip_v(tag: str) -> str:
    return tag[1:] if tag.lower().startswith("v") else tag


def fetch_latest_release(
    repo: str, asset_regex: str | None = None, timeout_s: int = 30
) -> GitHubReleaseResult:
    """Fetch latest GitHub release info for a repo.

    repo: "owner/name"
    asset_regex: regex used to choose the best asset to download.
    """

    url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(url, timeout=timeout_s)
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()

    tag = str(data.get("tag_name") or data.get("name") or "").strip()
    if not tag:
        raise RuntimeError(f"No tag_name found for {repo}")
    version = _strip_v(tag)

    assets = data.get("assets") or []
    if not isinstance(assets, list) or not assets:
        raise RuntimeError(f"No release assets found for {repo} latest release")

    rx = re.compile(asset_regex) if asset_regex else None

    chosen = None
    for a in assets:
        name = str(a.get("name") or "")
        if not name:
            continue
        if rx and not rx.search(name):
            continue
        chosen = a
        break

    if chosen is None:
        # fall back to first asset
        chosen = assets[0]

    asset_url = str(chosen.get("browser_download_url") or "")
    asset_name = str(chosen.get("name") or "")
    if not asset_url:
        raise RuntimeError(f"No browser_download_url for chosen asset in {repo}")

    return GitHubReleaseResult(version=version, asset_url=asset_url, asset_name=asset_name)
