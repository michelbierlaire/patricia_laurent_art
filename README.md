# Patricia Laurent — Static bilingual art website

This repository contains a bilingual static website generator for the art collection of Patricia Laurent.

## Features

- French and English versions
- Static HTML generation from `data/oeuvres.json`
- One page per artwork
- Responsive gallery built with Bootstrap
- Search, filters, and sorting in the gallery
- Multiple visual themes selected at generation time
- Artwork QR codes based on a configurable public base URL
- Lightbox image viewer
- GitHub Pages friendly output in `site/`

## Repository structure

```text
patricia-laurent-art/
├── data/
│   └── oeuvres.json
├── images/
│   ├── patricia.jpg
│   └── ...
├── templates/
├── scripts/
│   └── generate_site.py
├── assets/
│   ├── css/
│   ├── js/
│   └── icons/
├── site/
├── README.md
└── requirements.txt
```

## JSON format

The generator accepts either:

1. the original simple structure:

```json
{
  "id": "accordeon-orbe",
  "name": "L’Accordéon d’Orbe",
  "pictures": ["images/accordeon_orbe.JPG"],
  "description": "",
  "type": "",
  "dimensions": "",
  "date": "",
  "price": "",
  "keywords": [],
  "notes": ""
}
```

2. a bilingual structure:

```json
{
  "id": "accordeon-orbe",
  "title": {
    "fr": "L’Accordéon d’Orbe",
    "en": "The Accordion of Orbe"
  },
  "pictures": ["images/accordeon_orbe.JPG"],
  "description": {
    "fr": "",
    "en": ""
  },
  "type": {
    "fr": "Céramique",
    "en": "Ceramic"
  },
  "dimensions": "",
  "date": "",
  "price": "",
  "keywords": {
    "fr": ["musique"],
    "en": ["music"]
  },
  "notes": {
    "fr": "",
    "en": ""
  }
}
```

All fields are optional except `id`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate the site

Default generation:

```bash
python scripts/generate_site.py
```

Choose a theme:

```bash
python scripts/generate_site.py --theme gallery
python scripts/generate_site.py --theme contemporary
python scripts/generate_site.py --theme museum
```

Set the public base URL for QR codes:

```bash
python scripts/generate_site.py --base-url "https://username.github.io/patricia-laurent-art"
```

Use another JSON file inside `data/`:

```bash
python scripts/generate_site.py --json oeuvres.json
```

## Output

Generated files are written to `site/`:

- `site/index.html` redirects to French by default
- `site/fr/index.html` is the French home page
- `site/fr/collection/index.html` is the French gallery
- `site/fr/oeuvres/*.html` are French artwork pages
- `site/en/index.html` is the English home page
- `site/en/collection/index.html` is the English gallery
- `site/en/artworks/*.html` are English artwork pages

## Notes

- Put all artwork images in `images/`
- Put `patricia.jpg` in `images/`
- The script copies `images/` and `assets/` into `site/`
- If a field is missing, it is not displayed
- If an artwork has no picture, a placeholder block is shown instead

## GitHub Pages

A straightforward setup is to publish the content of `site/`.
