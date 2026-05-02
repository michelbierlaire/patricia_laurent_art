from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .content_manager import ContentManager
from .models import Announcement, Artwork, PressArticle, SiteConfig
from .settings import (
    ASSETS_DIR,
    DEFAULT_BASE_URL,
    DEFAULT_LOCALE,
    DOCS_DIR,
    DOCUMENTS_DIR,
    IMAGES_DIR,
    PUBLIC_UI,
    SUPPORTED_LANGS,
    TEMPLATES_DIR,
    THEMES,
    CUSTOM_DOMAIN,
)


@dataclass
class ArtworkView:
    raw: Artwork
    lang: str
    page_path: str
    gallery_path: str
    home_path: str
    lang_switch_path: str
    qr_code_path: str
    prev_path: str | None
    prev_title: str | None
    next_path: str | None
    next_title: str | None

    @property
    def id(self) -> str:
        return self.raw.id

    @property
    def title(self) -> str:
        return self.raw.title.get(self.lang) or self.raw.id

    @property
    def description(self) -> str:
        return self.raw.description.get(self.lang)

    @property
    def type_label(self) -> str:
        return self.raw.type.get(self.lang)

    @property
    def dimensions(self) -> str:
        return self.raw.dimensions

    @property
    def date(self) -> str:
        return self.raw.date

    @property
    def price(self) -> str:
        return self.raw.price

    @property
    def notes(self) -> str:
        return self.raw.notes.get(self.lang)

    @property
    def keywords(self) -> list[str]:
        return self.raw.keywords.get(self.lang)

    @property
    def pictures(self) -> list[str]:
        return [self._normalize_asset_path(picture) for picture in self.raw.pictures]

    @property
    def cover_picture(self) -> str | None:
        return self.pictures[0] if self.pictures else None

    @property
    def excerpt(self) -> str:
        text = self.description.strip()
        return text[:160].rstrip() + ("…" if len(text) > 160 else "") if text else ""

    @property
    def year_sort(self) -> int:
        return extract_year(self.date)

    @property
    def search_blob(self) -> str:
        parts = [
            self.title,
            self.description,
            self.type_label,
            self.date,
            self.dimensions,
            " ".join(self.keywords),
        ]
        return " ".join(part for part in parts if part).lower()

    @staticmethod
    def _normalize_asset_path(path_str: str) -> str:
        path = path_str.replace("\\", "/").lstrip("./")
        if path.startswith("images/"):
            return "../../" + path
        if path.startswith("assets/"):
            return "../../" + path
        return path


@dataclass
class PressArticleView:
    raw: PressArticle
    lang: str

    @property
    def id(self) -> str:
        return self.raw.id

    @property
    def title(self) -> str:
        return self.raw.title_for(self.lang)

    @property
    def newspaper(self) -> str:
        return self.raw.newspaper

    @property
    def date(self) -> str:
        return self.raw.date

    @property
    def pdf(self) -> str:
        return self._normalize_document_path(self.raw.pdf)

    @property
    def url(self) -> str:
        return self.raw.url

    @property
    def note(self) -> str:
        return self.raw.note_for(self.lang)

    @staticmethod
    def _normalize_document_path(path_str: str) -> str:
        path = path_str.replace("\\", "/").lstrip("./")
        if not path:
            return ""
        if path.startswith("documents/"):
            return "../../" + path
        if path.startswith("/documents/"):
            return path
        return path


def extract_year(date_str: str) -> int:
    digits = "".join(ch if ch.isdigit() else " " for ch in date_str)
    parts = [part for part in digits.split() if len(part) == 4]
    if not parts:
        return -1
    try:
        return int(parts[0])
    except ValueError:
        return -1


class SiteGenerator:
    def __init__(
        self, manager: ContentManager | None = None, docs_dir: Path | None = None
    ) -> None:
        self.manager = manager or ContentManager()
        self.docs_dir = docs_dir or DOCS_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR / "public")),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(
        self, *, base_url: str | None = None, theme: str | None = None
    ) -> Path:
        config = self.manager.get_site_config()
        artworks = self.manager.get_artworks()
        press_articles = self.manager.get_press_articles()
        active_announcements = config.active_announcements()
        selected_theme = theme or config.default_theme or "gallery"
        theme_info = THEMES[selected_theme]
        public_base_url = base_url or DEFAULT_BASE_URL
        self._ensure_clean_dir(self.docs_dir)
        (self.docs_dir / "fr" / "collection").mkdir(parents=True, exist_ok=True)
        (self.docs_dir / "fr" / "oeuvres").mkdir(parents=True, exist_ok=True)
        (self.docs_dir / "en" / "collection").mkdir(parents=True, exist_ok=True)
        (self.docs_dir / "en" / "artworks").mkdir(parents=True, exist_ok=True)
        (self.docs_dir / "fr" / "presse").mkdir(parents=True, exist_ok=True)
        (self.docs_dir / "en" / "press").mkdir(parents=True, exist_ok=True)

        self._copy_tree(ASSETS_DIR, self.docs_dir / "assets")
        self._copy_tree(IMAGES_DIR, self.docs_dir / "images")
        self._copy_tree(DOCUMENTS_DIR, self.docs_dir / "documents")

        root_index = self.env.get_template("root_index_template.html")
        (self.docs_dir / "index.html").write_text(
            root_index.render(default_lang=config.default_locale or DEFAULT_LOCALE),
            encoding="utf-8",
        )
        (self.docs_dir / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")

        for lang in SUPPORTED_LANGS:
            ui = PUBLIC_UI[lang]
            other_lang = "en" if lang == "fr" else "fr"
            press_folder_name = "presse" if lang == "fr" else "press"
            other_press_folder_name = "press" if lang == "fr" else "presse"
            views = self._make_artwork_views(artworks, lang, public_base_url)
            press_views = self._make_press_article_views(press_articles, lang)
            gallery_json = [self._gallery_item_json(view) for view in views]
            announcement_payloads = [
                self._announcement_payload(announcement, lang)
                for announcement in active_announcements
            ]
            home_template = self.env.get_template("home_template.html")
            gallery_template = self.env.get_template("gallery_template.html")
            artwork_template = self.env.get_template("artwork_template.html")
            press_template = self.env.get_template("press_template.html")

            home_html = home_template.render(
                lang=lang,
                ui=ui,
                site_title=config.site_title,
                site_email=config.email,
                goatcounter_url=config.goatcounter_url,
                theme=theme_info,
                body_class=theme_info["body_class"],
                collection_href="collection/index.html",
                press_href=f"{press_folder_name}/index.html",
                lang_switch_href=f"../{other_lang}/index.html",
                patricia_image="../"
                + config.home.image.replace("\\", "/").lstrip("./"),
                home=config.home,
                announcements=announcement_payloads,
            )
            (self.docs_dir / lang / "index.html").write_text(
                home_html, encoding="utf-8"
            )

            gallery_folder = self.docs_dir / lang / "collection"
            gallery_html = gallery_template.render(
                lang=lang,
                ui=ui,
                site_title=config.site_title,
                site_email=config.email,
                goatcounter_url=config.goatcounter_url,
                theme=theme_info,
                body_class=theme_info["body_class"],
                home_href="../index.html",
                collection_href="index.html",
                press_href=f"../{press_folder_name}/index.html",
                lang_switch_href=f"../../{other_lang}/collection/index.html",
                gallery_items=gallery_json,
                announcements=announcement_payloads,
            )
            (gallery_folder / "index.html").write_text(gallery_html, encoding="utf-8")

            press_folder = self.docs_dir / lang / press_folder_name
            press_html = press_template.render(
                lang=lang,
                ui=ui,
                site_title=config.site_title,
                site_email=config.email,
                goatcounter_url=config.goatcounter_url,
                theme=theme_info,
                body_class=theme_info["body_class"],
                home_href="../index.html",
                collection_href="../collection/index.html",
                press_href="index.html",
                lang_switch_href=f"../../{other_lang}/{other_press_folder_name}/index.html",
                articles=press_views,
                announcements=announcement_payloads,
            )
            (press_folder / "index.html").write_text(press_html, encoding="utf-8")

            artwork_folder = (
                self.docs_dir / lang / ("oeuvres" if lang == "fr" else "artworks")
            )
            for view in views:
                html = artwork_template.render(
                    lang=lang,
                    ui=ui,
                    site_title=config.site_title,
                    site_email=config.email,
                    goatcounter_url=config.goatcounter_url,
                    theme=theme_info,
                    body_class=theme_info["body_class"],
                    artwork=view,
                    home_href=view.home_path,
                    collection_href=view.gallery_path,
                    press_href=f"../{press_folder_name}/index.html",
                    lang_switch_href=view.lang_switch_path,
                    announcements=announcement_payloads,
                )
                (artwork_folder / f"{view.id}.html").write_text(html, encoding="utf-8")
        return self.docs_dir

    def _make_artwork_views(
        self, artworks: list[Artwork], lang: str, base_url: str
    ) -> list[ArtworkView]:
        views: list[ArtworkView] = []
        folder = "oeuvres" if lang == "fr" else "artworks"
        other_folder = "artworks" if lang == "fr" else "oeuvres"
        other_lang = "en" if lang == "fr" else "fr"
        for index, artwork in enumerate(artworks):
            slug = artwork.id
            qr_file = self.docs_dir / "assets" / "qrcodes" / lang / f"{slug}.png"
            public_url = f"{base_url.rstrip('/')}/{lang}/{folder}/{slug}.html"
            self._make_qr_code(public_url, qr_file)
            prev_path = prev_title = next_path = next_title = None
            if index > 0:
                prev_path = f"{artworks[index - 1].id}.html"
                prev_title = artworks[index - 1].title.get(lang)
            if index < len(artworks) - 1:
                next_path = f"{artworks[index + 1].id}.html"
                next_title = artworks[index + 1].title.get(lang)
            views.append(
                ArtworkView(
                    raw=artwork,
                    lang=lang,
                    page_path=f"../{folder}/{slug}.html",
                    gallery_path="../collection/index.html",
                    home_path="../index.html",
                    lang_switch_path=f"../../{other_lang}/{other_folder}/{slug}.html",
                    qr_code_path=f"../../assets/qrcodes/{lang}/{slug}.png",
                    prev_path=prev_path,
                    prev_title=prev_title,
                    next_path=next_path,
                    next_title=next_title,
                )
            )
        return views

    @staticmethod
    def _make_press_article_views(
        articles: list[PressArticle], lang: str
    ) -> list[PressArticleView]:
        return [PressArticleView(raw=article, lang=lang) for article in articles]

    @staticmethod
    def _announcement_payload(announcement: Announcement, lang: str) -> dict[str, Any]:
        return {
            "id": announcement.id,
            "title": announcement.title.get(lang),
            "text": announcement.text.get(lang),
            "starts_on": announcement.starts_on,
            "expires_on": announcement.expires_on,
            "links": [
                {
                    "url": link.url,
                    "label": link.label.get(lang),
                }
                for link in announcement.links
                if link.url and link.label.get(lang)
            ],
            "variant": announcement.variant,
        }

    @staticmethod
    def _gallery_item_json(view: ArtworkView) -> dict[str, Any]:
        return {
            "id": view.id,
            "title": view.title,
            "type": view.type_label,
            "date": view.date,
            "year": view.year_sort,
            "dimensions": view.dimensions,
            "price": view.price,
            "keywords": view.keywords,
            "description": view.description,
            "excerpt": view.excerpt,
            "cover": view.cover_picture,
            "link": view.page_path,
            "search_blob": view.search_blob,
        }

    @staticmethod
    def _make_qr_code(url: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        qrcode.make(url).save(output_path)

    @staticmethod
    def _ensure_clean_dir(path: Path) -> None:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _copy_tree(src: Path, dst: Path) -> None:
        if not src.exists():
            return
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
