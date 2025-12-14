from __future__ import annotations

import time
from pathlib import Path

import requests

from obs_plugin_manager.errors import InstallError


def download_to_cache(*, url: str, state_dir: Path, filename_prefix: str) -> Path:
    downloads = state_dir / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = downloads / f"{filename_prefix}-{ts}.zip"

    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        raise InstallError(f"Download failed: {e}") from e

    return dest
