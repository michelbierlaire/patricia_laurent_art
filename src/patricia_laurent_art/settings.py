from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PACKAGE_ROOT / "data"
IMAGES_DIR = PACKAGE_ROOT / "images"
ASSETS_DIR = PACKAGE_ROOT / "assets"
TEMPLATES_DIR = PACKAGE_ROOT / "templates"
DOCS_DIR = PACKAGE_ROOT / "docs"

DEFAULT_THEME = "gallery"
CUSTOM_DOMAIN = "patricialaurent.art"
DEFAULT_BASE_URL = f"https://{CUSTOM_DOMAIN}"
DEFAULT_LOCALE = "fr"
SUPPORTED_LANGS = ("fr", "en")
THEMES = {
    "contemporary": {"body_class": "theme-contemporary", "theme_label": "Contemporary"},
    "museum": {"body_class": "theme-museum", "theme_label": "Museum"},
    "gallery": {"body_class": "theme-gallery", "theme_label": "Gallery"},
}

PUBLIC_UI = {
    "fr": {
        "lang_name": "Français",
        "other_lang": "English",
        "home": "Accueil",
        "collection": "Collection",
        "search": "Rechercher",
        "search_placeholder": "Titre, description, mots-clés…",
        "filter_type": "Type",
        "filter_year": "Date",
        "filter_keyword": "Mot-clé",
        "all_types": "Tous les types",
        "all_years": "Toutes les dates",
        "all_keywords": "Tous les mots-clés",
        "sort": "Tri",
        "sort_title_asc": "Titre A → Z",
        "sort_title_desc": "Titre Z → A",
        "sort_date_desc": "Date décroissante",
        "sort_date_asc": "Date croissante",
        "unknown": "Non renseigné",
        "view_details": "Voir l’œuvre",
        "discover_collection": "Découvrir la collection",
        "back_to_collection": "Retour à la collection",
        "previous_artwork": "Œuvre précédente",
        "next_artwork": "Œuvre suivante",
        "contact": "Contact",
        "description": "Description",
        "details": "Informations",
        "notes": "Notes et commentaires",
        "price": "Prix",
        "date": "Date",
        "dimensions": "Dimensions",
        "type": "Type",
        "keywords": "Mots-clés",
        "qr_code": "QR code de la page",
        "no_image": "Image indisponible",
        "footer_text": "Site de présentation de la collection artistique de Patricia Laurent.",
        "language_switch": "EN",
        "gallery_heading": "Collection",
        "results_count_one": "œuvre",
        "results_count_many": "œuvres",
    },
    "en": {
        "lang_name": "English",
        "other_lang": "Français",
        "home": "Home",
        "collection": "Collection",
        "search": "Search",
        "search_placeholder": "Title, description, keywords…",
        "filter_type": "Type",
        "filter_year": "Date",
        "filter_keyword": "Keyword",
        "all_types": "All types",
        "all_years": "All dates",
        "all_keywords": "All keywords",
        "sort": "Sort",
        "sort_title_asc": "Title A → Z",
        "sort_title_desc": "Title Z → A",
        "sort_date_desc": "Date descending",
        "sort_date_asc": "Date ascending",
        "unknown": "Not specified",
        "view_details": "View artwork",
        "discover_collection": "Explore the collection",
        "back_to_collection": "Back to collection",
        "previous_artwork": "Previous artwork",
        "next_artwork": "Next artwork",
        "contact": "Contact",
        "description": "Description",
        "details": "Details",
        "notes": "Notes and comments",
        "price": "Price",
        "date": "Date",
        "dimensions": "Dimensions",
        "type": "Type",
        "keywords": "Keywords",
        "qr_code": "Page QR code",
        "no_image": "No image available",
        "footer_text": "Presentation website for the art collection of Patricia Laurent.",
        "language_switch": "FR",
        "gallery_heading": "Collection",
        "results_count_one": "artwork",
        "results_count_many": "artworks",
    },
}
