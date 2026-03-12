from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .models import Announcement, Artwork, LocalizedList, LocalizedText, SiteConfig
from .storage import Storage


class ContentManager:
    def __init__(self, storage: Storage | None = None) -> None:
        self.storage = storage or Storage()

    def get_artworks(self) -> list[Artwork]:
        artworks = self.storage.load_artworks()
        artworks.sort(key=lambda artwork: artwork.title_for("fr").lower())
        return artworks

    def save_artworks(self, artworks: list[Artwork]) -> None:
        self._validate_unique_ids(artworks)
        self.storage.save_artworks(artworks)

    def get_artwork(self, artwork_id: str) -> Artwork | None:
        for artwork in self.get_artworks():
            if artwork.id == artwork_id:
                return artwork
        return None

    def add_artwork(self, artwork: Artwork) -> None:
        artworks = self.get_artworks()
        if any(existing.id == artwork.id for existing in artworks):
            raise ValueError(f"Une œuvre avec l'identifiant '{artwork.id}' existe déjà.")
        artworks.append(artwork)
        self.save_artworks(artworks)

    def update_artwork(self, artwork_id: str, updated: Artwork) -> None:
        artworks = self.get_artworks()
        replaced = False
        for index, artwork in enumerate(artworks):
            if artwork.id == artwork_id:
                artworks[index] = updated
                replaced = True
                break
        if not replaced:
            raise ValueError(f"Œuvre introuvable: {artwork_id}")
        self.save_artworks(artworks)

    def delete_artwork(self, artwork_id: str) -> None:
        artworks = [artwork for artwork in self.get_artworks() if artwork.id != artwork_id]
        self.save_artworks(artworks)

    def duplicate_artwork(self, artwork_id: str) -> Artwork:
        artwork = self.get_artwork(artwork_id)
        if artwork is None:
            raise ValueError(f"Œuvre introuvable: {artwork_id}")
        new_id = self._generate_copy_id(artwork.id)
        duplicate = replace(artwork, id=new_id)
        duplicate.title = LocalizedText(
            fr=f"{artwork.title.fr} (copie)".strip(),
            en=f"{artwork.title.en} (copy)".strip(),
        )
        self.add_artwork(duplicate)
        return duplicate

    def get_site_config(self) -> SiteConfig:
        return self.storage.load_site_config()

    def save_site_config(self, config: SiteConfig) -> None:
        self.storage.save_site_config(config)

    def get_active_announcements(self) -> list[Announcement]:
        config = self.get_site_config()
        return config.active_announcements()

    def save_announcements(self, announcements: list[Announcement]) -> None:
        config = self.get_site_config()
        config.announcements = announcements
        self.save_site_config(config)

    def create_empty_artwork(self, artwork_id: str) -> Artwork:
        return Artwork(
            id=artwork_id,
            title=LocalizedText(),
            description=LocalizedText(),
            type=LocalizedText(),
            keywords=LocalizedList(),
            notes=LocalizedText(),
            pictures=[],
        )

    def reorder_pictures(self, artwork_id: str, pictures: Iterable[str]) -> None:
        artwork = self.get_artwork(artwork_id)
        if artwork is None:
            raise ValueError(f"Œuvre introuvable: {artwork_id}")
        artwork.pictures = [picture for picture in pictures if picture]
        self.update_artwork(artwork_id, artwork)

    def _validate_unique_ids(self, artworks: list[Artwork]) -> None:
        ids = [artwork.id for artwork in artworks]
        if any(not artwork_id for artwork_id in ids):
            raise ValueError("Chaque œuvre doit avoir un identifiant non vide.")
        if len(set(ids)) != len(ids):
            raise ValueError("Les identifiants des œuvres doivent être uniques.")

    def _generate_copy_id(self, base_id: str) -> str:
        artworks = self.get_artworks()
        existing_ids = {artwork.id for artwork in artworks}
        suffix = 2
        candidate = f"{base_id}-copie"
        while candidate in existing_ids:
            suffix += 1
            candidate = f"{base_id}-copie-{suffix}"
        return candidate
