# Patricia Laurent Art

Projet complet pour gérer et publier la collection artistique de Patricia Laurent.

Le projet contient trois acteurs clairement séparés :

- **gestionnaire de contenu** : modèle de données, persistance JSON, logique métier, import d'images ;
- **générateur de site** : production du site statique bilingue dans `docs/` ;
- **éditeur local** : interface web locale en français pour modifier les œuvres et la configuration du site.

## Structure

```text
patricia_laurent_art/
├── data/
│   ├── oeuvres.json
│   └── site_config.json
├── images/
├── assets/
├── templates/
│   ├── public/
│   └── editor/
├── docs/               # site généré
├── scripts/
│   ├── generate_site.py
│   └── run_editor.py
└── src/patricia_laurent_art/
```

## Installation

```bash
pip install -r requirements.txt
```

ou

```bash
pip install .
```

## Lancer l'éditeur local

```bash
python scripts/run_editor.py
```

Puis ouvrir l'adresse affichée dans le terminal, en général :

```text
http://127.0.0.1:5000
```

## Régénérer le site statique

```bash
python scripts/generate_site.py --base-url "https://username.github.io/patricia_laurent_art"
```

Le site est généré dans `docs/`.

## Règles importantes

- l'import d'image **refuse** un nom de fichier déjà présent dans `images/` ;
- l'image n'est jamais renommée automatiquement ;
- le contenu éditorial global est stocké dans `data/site_config.json` ;
- les œuvres sont stockées dans `data/oeuvres.json` ;
- le code de rendu public n'accède pas directement au JSON brut.
