from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
IMAGES_DIR = ROOT / 'images'
TEMPLATES_DIR = ROOT / 'templates'
ASSETS_DIR = ROOT / 'assets'
SITE_DIR = ROOT / 'docs'

SITE_TITLE = 'Patricia Laurent'
SITE_EMAIL = 'patricia.laurent.12@gmail.com'
DEFAULT_THEME = 'gallery'
DEFAULT_BASE_URL = 'https://michelbierlaire.github.io/patricia_laurent_art'
DEFAULT_LOCALE = 'fr'
SUPPORTED_LANGS = ('fr', 'en')

UI = {
    'fr': {
        'lang_name': 'Français',
        'other_lang': 'English',
        'home': 'Accueil',
        'collection': 'Collection',
        'search': 'Rechercher',
        'search_placeholder': 'Titre, description, mots-clés…',
        'filter_type': 'Type',
        'filter_year': 'Date',
        'filter_keyword': 'Mot-clé',
        'all_types': 'Tous les types',
        'all_years': 'Toutes les dates',
        'all_keywords': 'Tous les mots-clés',
        'sort': 'Tri',
        'sort_title_asc': 'Titre A → Z',
        'sort_title_desc': 'Titre Z → A',
        'sort_date_desc': 'Date décroissante',
        'sort_date_asc': 'Date croissante',
        'sort_recent': 'Plus récentes d’abord',
        'sort_oldest': 'Plus anciennes d’abord',
        'unknown': 'Non renseigné',
        'view_details': 'Voir l’œuvre',
        'discover_collection': 'Découvrir la collection',
        'back_to_collection': 'Retour à la collection',
        'previous_artwork': 'Œuvre précédente',
        'next_artwork': 'Œuvre suivante',
        'contact': 'Contact',
        'description': 'Description',
        'details': 'Informations',
        'notes': 'Notes et commentaires',
        'price': 'Prix',
        'date': 'Date',
        'dimensions': 'Dimensions',
        'type': 'Type',
        'keywords': 'Mots-clés',
        'qr_code': 'QR code de la page',
        'no_image': 'Image indisponible',
        'hero_title': 'Patricia Laurent',
        'hero_text': 'Patricia Laurent est une artiste suisse spécialisée dans la céramique et la peinture. Son univers associe sensibilité, matière et lumière dans une démarche à la fois contemporaine et profondément personnelle.',
        'hero_cta': 'Voir les œuvres',
        'intro_title': 'Une collection vivante',
        'intro_text': 'Cette galerie présente une sélection d’œuvres de Patricia Laurent. Chaque pièce possède sa propre page, avec ses images, ses informations disponibles et ses notes éventuelles.',
        'footer_text': 'Site de présentation de la collection artistique de Patricia Laurent.',
        'language_switch': 'EN',
        'gallery_heading': 'Collection',
        'results_count_one': 'œuvre',
        'results_count_many': 'œuvres',
        'home_lead': 'Artiste suisse — céramique et peinture',
    },
    'en': {
        'lang_name': 'English',
        'other_lang': 'Français',
        'home': 'Home',
        'collection': 'Collection',
        'search': 'Search',
        'search_placeholder': 'Title, description, keywords…',
        'filter_type': 'Type',
        'filter_year': 'Date',
        'filter_keyword': 'Keyword',
        'all_types': 'All types',
        'all_years': 'All dates',
        'all_keywords': 'All keywords',
        'sort': 'Sort',
        'sort_title_asc': 'Title A → Z',
        'sort_title_desc': 'Title Z → A',
        'sort_date_desc': 'Date descending',
        'sort_date_asc': 'Date ascending',
        'sort_recent': 'Most recent first',
        'sort_oldest': 'Oldest first',
        'unknown': 'Not specified',
        'view_details': 'View artwork',
        'discover_collection': 'Explore the collection',
        'back_to_collection': 'Back to collection',
        'previous_artwork': 'Previous artwork',
        'next_artwork': 'Next artwork',
        'contact': 'Contact',
        'description': 'Description',
        'details': 'Details',
        'notes': 'Notes and comments',
        'price': 'Price',
        'date': 'Date',
        'dimensions': 'Dimensions',
        'type': 'Type',
        'keywords': 'Keywords',
        'qr_code': 'Page QR code',
        'no_image': 'No image available',
        'hero_title': 'Patricia Laurent',
        'hero_text': 'Patricia Laurent is a Swiss artist specializing in ceramics and painting. Her work combines sensitivity, materiality, and light in an approach that is both contemporary and deeply personal.',
        'hero_cta': 'View the artworks',
        'intro_title': 'A living collection',
        'intro_text': 'This gallery presents a selection of artworks by Patricia Laurent. Each piece has its own page with images, available information, and optional notes.',
        'footer_text': 'Presentation website for the art collection of Patricia Laurent.',
        'language_switch': 'FR',
        'gallery_heading': 'Collection',
        'results_count_one': 'artwork',
        'results_count_many': 'artworks',
        'home_lead': 'Swiss artist — ceramics and painting',
    },
}

THEMES = {
    'contemporary': {
        'body_class': 'theme-contemporary',
        'theme_label': 'Contemporary',
    },
    'museum': {
        'body_class': 'theme-museum',
        'theme_label': 'Museum',
    },
    'gallery': {
        'body_class': 'theme-gallery',
        'theme_label': 'Gallery',
    },
}


@dataclass
class ArtworkView:
    raw: dict[str, Any]
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
        return str(self.raw.get('id', ''))

    @property
    def title(self) -> str:
        return localized_value(self.raw.get('title') or self.raw.get('name'), self.lang) or self.id

    @property
    def description(self) -> str:
        return localized_value(self.raw.get('description'), self.lang)

    @property
    def type_label(self) -> str:
        return localized_value(self.raw.get('type'), self.lang)

    @property
    def dimensions(self) -> str:
        return scalar_value(self.raw.get('dimensions'))

    @property
    def date(self) -> str:
        return scalar_value(self.raw.get('date'))

    @property
    def price(self) -> str:
        return scalar_value(self.raw.get('price'))

    @property
    def notes(self) -> str:
        return localized_value(self.raw.get('notes'), self.lang)

    @property
    def keywords(self) -> list[str]:
        value = self.raw.get('keywords', [])
        if isinstance(value, dict):
            selected = value.get(self.lang, [])
            return [str(v) for v in selected if str(v).strip()]
        if isinstance(value, list):
            return [str(v) for v in value if str(v).strip()]
        return []

    @property
    def pictures(self) -> list[str]:
        pics = self.raw.get('pictures') or []
        return [normalize_asset_path(str(p)) for p in pics if str(p).strip()]

    @property
    def cover_picture(self) -> str | None:
        return self.pictures[0] if self.pictures else None

    @property
    def excerpt(self) -> str:
        text = self.description.strip()
        if not text:
            return ''
        return text[:160].rstrip() + ('…' if len(text) > 160 else '')

    @property
    def year_sort(self) -> int:
        return extract_year(self.date)

    @property
    def search_blob(self) -> str:
        parts = [self.title, self.description, self.type_label, self.date, self.dimensions, ' '.join(self.keywords)]
        return ' '.join(part for part in parts if part).lower()


def localized_value(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        candidate = value.get(lang)
        if candidate is None:
            candidate = value.get(DEFAULT_LOCALE) or next((v for v in value.values() if v), '')
        return scalar_value(candidate)
    return scalar_value(value)


def scalar_value(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return ''
    return str(value).strip()


def normalize_asset_path(path_str: str) -> str:
    path = path_str.replace('\\', '/').lstrip('./')
    if path.startswith('images/'):
        return '../../' + path
    if path.startswith('assets/'):
        return '../../' + path
    return path


def extract_year(date_str: str) -> int:
    digits = ''.join(ch if ch.isdigit() else ' ' for ch in date_str)
    parts = [p for p in digits.split() if len(p) == 4]
    if not parts:
        return -1
    try:
        return int(parts[0])
    except ValueError:
        return -1


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def load_artworks(json_path: Path) -> list[dict[str, Any]]:
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError('The JSON database must contain a list of artworks.')
    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue
        normalized.append(item)
    normalized.sort(key=lambda x: localized_value(x.get('title') or x.get('name'), DEFAULT_LOCALE).lower())
    return normalized


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def make_qr_code(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = qrcode.make(url)
    img.save(output_path)


def make_artwork_views(artworks: list[dict[str, Any]], lang: str, base_url: str) -> list[ArtworkView]:
    views: list[ArtworkView] = []
    folder = 'oeuvres' if lang == 'fr' else 'artworks'
    other_folder = 'artworks' if lang == 'fr' else 'oeuvres'
    for index, art in enumerate(artworks):
        slug = art['id']
        page_path = f'../{folder}/{slug}.html'
        gallery_path = '../collection/index.html'
        home_path = '../index.html'
        lang_switch_path = f'../../{'en' if lang == 'fr' else 'fr'}/{other_folder}/{slug}.html'
        qr_file = SITE_DIR / 'assets' / 'qrcodes' / lang / f'{slug}.png'
        public_url = f"{base_url.rstrip('/')}/{lang}/{folder}/{slug}.html"
        make_qr_code(public_url, qr_file)
        prev_path = prev_title = next_path = next_title = None
        if index > 0:
            prev_slug = artworks[index - 1]['id']
            prev_path = f'{prev_slug}.html'
            prev_title = localized_value(artworks[index - 1].get('title') or artworks[index - 1].get('name'), lang)
        if index < len(artworks) - 1:
            next_slug = artworks[index + 1]['id']
            next_path = f'{artworks[index + 1]["id"]}.html'
            next_title = localized_value(artworks[index + 1].get('title') or artworks[index + 1].get('name'), lang)
        views.append(
            ArtworkView(
                raw=art,
                lang=lang,
                page_path=page_path,
                gallery_path=gallery_path,
                home_path=home_path,
                lang_switch_path=lang_switch_path,
                qr_code_path=f'../../assets/qrcodes/{lang}/{slug}.png',
                prev_path=prev_path,
                prev_title=prev_title,
                next_path=next_path,
                next_title=next_title,
            )
        )
    return views


def gallery_item_json(view: ArtworkView) -> dict[str, Any]:
    return {
        'id': view.id,
        'title': view.title,
        'type': view.type_label,
        'date': view.date,
        'year': view.year_sort,
        'dimensions': view.dimensions,
        'price': view.price,
        'keywords': view.keywords,
        'description': view.description,
        'excerpt': view.excerpt,
        'cover': view.cover_picture,
        'link': view.page_path,
        'search_blob': view.search_blob,
    }


def build_site(json_filename: str, theme: str, base_url: str) -> None:
    json_path = DATA_DIR / json_filename
    artworks = load_artworks(json_path)
    env = make_env()

    ensure_clean_dir(SITE_DIR)
    (SITE_DIR / 'fr' / 'collection').mkdir(parents=True, exist_ok=True)
    (SITE_DIR / 'fr' / 'oeuvres').mkdir(parents=True, exist_ok=True)
    (SITE_DIR / 'en' / 'collection').mkdir(parents=True, exist_ok=True)
    (SITE_DIR / 'en' / 'artworks').mkdir(parents=True, exist_ok=True)

    copy_tree(ASSETS_DIR, SITE_DIR / 'assets')
    copy_tree(IMAGES_DIR, SITE_DIR / 'images')

    root_index = env.get_template('root_index_template.html')
    (SITE_DIR / 'index.html').write_text(root_index.render(default_lang=DEFAULT_LOCALE), encoding='utf-8')

    theme_info = THEMES[theme]

    for lang in SUPPORTED_LANGS:
        ui = UI[lang]
        other_lang = 'en' if lang == 'fr' else 'fr'
        views = make_artwork_views(artworks, lang, base_url)
        gallery_json = [gallery_item_json(v) for v in views]

        home_template = env.get_template('home_template.html')
        gallery_template = env.get_template('gallery_template.html')
        artwork_template = env.get_template('artwork_template.html')

        home_html = home_template.render(
            lang=lang,
            ui=ui,
            site_title=SITE_TITLE,
            site_email=SITE_EMAIL,
            theme=theme_info,
            body_class=theme_info['body_class'],
            collection_href='collection/index.html',
            lang_switch_href=f'../{other_lang}/index.html',
            patricia_image='../images/patricia.jpg',
        )
        (SITE_DIR / lang / 'index.html').write_text(home_html, encoding='utf-8')

        gallery_folder = SITE_DIR / lang / 'collection'
        gallery_html = gallery_template.render(
            lang=lang,
            ui=ui,
            site_title=SITE_TITLE,
            theme=theme_info,
            body_class=theme_info['body_class'],
            home_href='../index.html',
            lang_switch_href=f'../../{other_lang}/collection/index.html',
            gallery_items=gallery_json,
        )
        (gallery_folder / 'index.html').write_text(gallery_html, encoding='utf-8')

        artwork_folder = SITE_DIR / lang / ('oeuvres' if lang == 'fr' else 'artworks')
        for view in views:
            html = artwork_template.render(
                lang=lang,
                ui=ui,
                site_title=SITE_TITLE,
                theme=theme_info,
                body_class=theme_info['body_class'],
                artwork=view,
                home_href=view.home_path,
                collection_href=view.gallery_path,
                lang_switch_href=view.lang_switch_path,
            )
            (artwork_folder / f'{view.id}.html').write_text(html, encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate the Patricia Laurent bilingual static website.')
    parser.add_argument('--json', default='oeuvres.json', help='JSON file inside data/.')
    parser.add_argument('--theme', default=DEFAULT_THEME, choices=sorted(THEMES), help='Visual theme.')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL, help='Public base URL used for QR codes.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    build_site(json_filename=args.json, theme=args.theme, base_url=args.base_url)
    print(f'Site generated in {SITE_DIR}')
