from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

Location = Literal["user", "global"]


@dataclass(frozen=True)
class InstalledPlugin:
    plugin_id: str
    name: str
    location: Location
    bin_path: Path | None
    data_path: Path | None
    installed_version: str | None
    version_source: str | None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["bin_path"] = str(self.bin_path) if self.bin_path else None
        d["data_path"] = str(self.data_path) if self.data_path else None
        return d


@dataclass(frozen=True)
class UpdateAvailable:
    plugin_id: str
    name: str
    installed_version: str | None
    latest_version: str
    download_url: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
