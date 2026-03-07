from __future__ import annotations

from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .settings import IMAGES_DIR


class ImageService:
    def __init__(self, images_dir: Path | None = None) -> None:
        self.images_dir = images_dir or IMAGES_DIR
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def import_upload(self, upload: FileStorage) -> str:
        filename = secure_filename(upload.filename or "")
        if not filename:
            raise ValueError("Aucun fichier image sélectionné.")
        target = self.images_dir / filename
        if target.exists():
            raise ValueError(f"Le fichier '{filename}' existe déjà dans images/. Renommez-le avant l'import.")
        upload.save(target)
        return f"images/{filename}"

    def list_images(self) -> list[str]:
        allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".JPG", ".JPEG"}
        images = [f"images/{path.name}" for path in sorted(self.images_dir.iterdir()) if path.is_file() and path.suffix in allowed]
        return images
