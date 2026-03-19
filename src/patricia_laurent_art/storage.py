from __future__ import annotations

import json
from pathlib import Path

from .models import Artwork, SiteConfig
from .settings import DATA_DIR


class Storage:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self.artworks_path = self.data_dir / "oeuvres.json"
        self.site_config_path = self.data_dir / "site_config.json"

    def load_artworks(self) -> list[Artwork]:
        if not self.artworks_path.exists():
            return []

        raw = json.loads(self.artworks_path.read_text(encoding="utf-8"))

        if not isinstance(raw, list):
            raise ValueError("oeuvres.json must contain a list.")

        artworks = [Artwork.from_dict(item) for item in raw if isinstance(item, dict)]
        return artworks

    def save_artworks(self, artworks: list[Artwork]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        data = [artwork.to_dict() for artwork in artworks]
        self.artworks_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def load_site_config(self) -> SiteConfig:
        if not self.site_config_path.exists():
            return SiteConfig()

        raw = json.loads(self.site_config_path.read_text(encoding="utf-8"))

        if not isinstance(raw, dict):
            raise ValueError("site_config.json must contain an object.")

        return SiteConfig.from_dict(raw)

    def save_site_config(self, config: SiteConfig) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.site_config_path.write_text(
            json.dumps(config.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
