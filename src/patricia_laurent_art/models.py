from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LocalizedText:
    fr: str = ""
    en: str = ""

    @classmethod
    def from_raw(cls, value: Any) -> "LocalizedText":
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(fr=str(value.get("fr", "") or "").strip(), en=str(value.get("en", "") or "").strip())
        if value is None:
            return cls()
        text = str(value).strip()
        return cls(fr=text, en=text)

    def to_dict(self) -> dict[str, str]:
        return {"fr": self.fr, "en": self.en}

    def get(self, lang: str, fallback: str = "fr") -> str:
        if lang == "fr":
            return self.fr or self.en
        if lang == "en":
            return self.en or self.fr
        return self.fr or self.en


@dataclass
class LocalizedList:
    fr: list[str] = field(default_factory=list)
    en: list[str] = field(default_factory=list)

    @classmethod
    def from_raw(cls, value: Any) -> "LocalizedList":
        def normalize(items: Any) -> list[str]:
            if not isinstance(items, list):
                return []
            return [str(item).strip() for item in items if str(item).strip()]

        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(fr=normalize(value.get("fr", [])), en=normalize(value.get("en", [])))
        if isinstance(value, list):
            normalized = normalize(value)
            return cls(fr=normalized.copy(), en=normalized.copy())
        return cls()

    def to_dict(self) -> dict[str, list[str]]:
        return {"fr": self.fr, "en": self.en}

    def get(self, lang: str, fallback: str = "fr") -> list[str]:
        if lang == "fr":
            return self.fr or self.en
        if lang == "en":
            return self.en or self.fr
        return self.fr or self.en


@dataclass
class HomePageContent:
    image: str = "images/patricia.jpg"
    title: LocalizedText = field(default_factory=LocalizedText)
    lead: LocalizedText = field(default_factory=LocalizedText)
    hero_text: LocalizedText = field(default_factory=LocalizedText)
    hero_cta: LocalizedText = field(default_factory=LocalizedText)
    intro_title: LocalizedText = field(default_factory=LocalizedText)
    intro_text: LocalizedText = field(default_factory=LocalizedText)
    admin_button_enabled: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HomePageContent":
        return cls(
            image=str(data.get("image", "images/patricia.jpg")),
            title=LocalizedText.from_raw(data.get("title")),
            lead=LocalizedText.from_raw(data.get("lead")),
            hero_text=LocalizedText.from_raw(data.get("hero_text")),
            hero_cta=LocalizedText.from_raw(data.get("hero_cta")),
            intro_title=LocalizedText.from_raw(data.get("intro_title")),
            intro_text=LocalizedText.from_raw(data.get("intro_text")),
            admin_button_enabled=bool(data.get("admin_button_enabled", False)),
            extra=dict(data.get("extra", {})) if isinstance(data.get("extra", {}), dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "image": self.image,
            "title": self.title.to_dict(),
            "lead": self.lead.to_dict(),
            "hero_text": self.hero_text.to_dict(),
            "hero_cta": self.hero_cta.to_dict(),
            "intro_title": self.intro_title.to_dict(),
            "intro_text": self.intro_text.to_dict(),
            "admin_button_enabled": self.admin_button_enabled,
            "extra": self.extra,
        }


@dataclass
class SiteConfig:
    site_title: str = "Patricia Laurent"
    email: str = ""
    default_theme: str = "gallery"
    default_locale: str = "fr"
    home: HomePageContent = field(default_factory=HomePageContent)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SiteConfig":
        return cls(
            site_title=str(data.get("site_title", "Patricia Laurent")).strip() or "Patricia Laurent",
            email=str(data.get("email", "")).strip(),
            default_theme=str(data.get("default_theme", "gallery")).strip() or "gallery",
            default_locale=str(data.get("default_locale", "fr")).strip() or "fr",
            home=HomePageContent.from_dict(data.get("home", {})),
            extra=dict(data.get("extra", {})) if isinstance(data.get("extra", {}), dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "site_title": self.site_title,
            "email": self.email,
            "default_theme": self.default_theme,
            "default_locale": self.default_locale,
            "home": self.home.to_dict(),
            "extra": self.extra,
        }


@dataclass
class Artwork:
    id: str
    title: LocalizedText = field(default_factory=LocalizedText)
    description: LocalizedText = field(default_factory=LocalizedText)
    type: LocalizedText = field(default_factory=LocalizedText)
    dimensions: str = ""
    date: str = ""
    price: str = ""
    keywords: LocalizedList = field(default_factory=LocalizedList)
    notes: LocalizedText = field(default_factory=LocalizedText)
    pictures: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Artwork":
        return cls(
            id=str(data.get("id", "")).strip(),
            title=LocalizedText.from_raw(data.get("title") or data.get("name")),
            description=LocalizedText.from_raw(data.get("description")),
            type=LocalizedText.from_raw(data.get("type")),
            dimensions=str(data.get("dimensions", "") or "").strip(),
            date=str(data.get("date", "") or "").strip(),
            price=str(data.get("price", "") or "").strip(),
            keywords=LocalizedList.from_raw(data.get("keywords")),
            notes=LocalizedText.from_raw(data.get("notes")),
            pictures=[str(p).replace('\\', '/').strip() for p in data.get("pictures", []) if str(p).strip()],
            extra=dict(data.get("extra", {})) if isinstance(data.get("extra", {}), dict) else {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title.to_dict(),
            "description": self.description.to_dict(),
            "type": self.type.to_dict(),
            "dimensions": self.dimensions,
            "date": self.date,
            "price": self.price,
            "keywords": self.keywords.to_dict(),
            "notes": self.notes.to_dict(),
            "pictures": self.pictures,
            "extra": self.extra,
        }

    def title_for(self, lang: str) -> str:
        return self.title.get(lang) or self.id
