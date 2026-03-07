from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from jinja2 import ChoiceLoader, FileSystemLoader

from .content_manager import ContentManager
from .image_service import ImageService
from .models import Artwork, LocalizedList, LocalizedText, SiteConfig
from .settings import DOCS_DIR, IMAGES_DIR, THEMES, TEMPLATES_DIR
from .site_generator import SiteGenerator


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = 'patricia-laurent-art-local-editor'
    app.jinja_loader = ChoiceLoader([app.jinja_loader, FileSystemLoader(str(TEMPLATES_DIR / 'editor'))])
    manager = ContentManager()
    image_service = ImageService(IMAGES_DIR)
    generator = SiteGenerator(manager)

    @app.route('/')
    def dashboard() -> str:
        artworks = manager.get_artworks()
        config = manager.get_site_config()
        return render_template('dashboard.html', artworks=artworks, config=config)

    @app.route('/site-config', methods=['GET', 'POST'])
    def site_config() -> str:
        config = manager.get_site_config()
        if request.method == 'POST':
            config = SiteConfig(
                site_title=request.form.get('site_title', '').strip() or 'Patricia Laurent',
                email=request.form.get('email', '').strip(),
                default_theme=request.form.get('default_theme', 'gallery').strip() or 'gallery',
                default_locale=request.form.get('default_locale', 'fr').strip() or 'fr',
                home=config.home,
                extra=config.extra,
            )
            config.home.image = request.form.get('home_image', config.home.image).strip() or config.home.image
            config.home.title = LocalizedText(request.form.get('home_title_fr', '').strip(), request.form.get('home_title_en', '').strip())
            config.home.lead = LocalizedText(request.form.get('home_lead_fr', '').strip(), request.form.get('home_lead_en', '').strip())
            config.home.hero_text = LocalizedText(request.form.get('hero_text_fr', '').strip(), request.form.get('hero_text_en', '').strip())
            config.home.hero_cta = LocalizedText(request.form.get('hero_cta_fr', '').strip(), request.form.get('hero_cta_en', '').strip())
            config.home.intro_title = LocalizedText(request.form.get('intro_title_fr', '').strip(), request.form.get('intro_title_en', '').strip())
            config.home.intro_text = LocalizedText(request.form.get('intro_text_fr', '').strip(), request.form.get('intro_text_en', '').strip())
            manager.save_site_config(config)
            flash('Configuration du site enregistrée.', 'success')
            return redirect(url_for('site_config'))
        return render_template('site_config_form.html', config=config, themes=THEMES)

    @app.route('/artworks/new', methods=['GET', 'POST'])
    def new_artwork() -> str:
        if request.method == 'POST':
            artwork = _build_artwork_from_form(request, allow_id_change=True)
            try:
                manager.add_artwork(artwork)
                flash('Œuvre créée.', 'success')
                return redirect(url_for('edit_artwork', artwork_id=artwork.id))
            except ValueError as exc:
                flash(str(exc), 'danger')
                return render_template('artwork_form.html', artwork=artwork, is_new=True, available_images=image_service.list_images())
        draft = manager.create_empty_artwork('')
        return render_template('artwork_form.html', artwork=draft, is_new=True, available_images=image_service.list_images())

    @app.route('/artworks/<artwork_id>/edit', methods=['GET', 'POST'])
    def edit_artwork(artwork_id: str) -> str:
        artwork = manager.get_artwork(artwork_id)
        if artwork is None:
            flash('Œuvre introuvable.', 'danger')
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            updated = _build_artwork_from_form(request, allow_id_change=False, artwork_id=artwork_id)
            try:
                manager.update_artwork(artwork_id, updated)
                flash('Œuvre enregistrée.', 'success')
                return redirect(url_for('edit_artwork', artwork_id=artwork_id))
            except ValueError as exc:
                flash(str(exc), 'danger')
                return render_template('artwork_form.html', artwork=updated, is_new=False, available_images=image_service.list_images())
        return render_template('artwork_form.html', artwork=artwork, is_new=False, available_images=image_service.list_images())

    @app.post('/artworks/<artwork_id>/delete')
    def delete_artwork(artwork_id: str):
        manager.delete_artwork(artwork_id)
        flash('Œuvre supprimée.', 'success')
        return redirect(url_for('dashboard'))

    @app.post('/artworks/<artwork_id>/duplicate')
    def duplicate_artwork(artwork_id: str):
        duplicate = manager.duplicate_artwork(artwork_id)
        flash('Œuvre dupliquée.', 'success')
        return redirect(url_for('edit_artwork', artwork_id=duplicate.id))

    @app.post('/artworks/<artwork_id>/upload-image')
    def upload_image(artwork_id: str):
        artwork = manager.get_artwork(artwork_id)
        if artwork is None:
            flash('Œuvre introuvable.', 'danger')
            return redirect(url_for('dashboard'))
        upload = request.files.get('image_file')
        if upload is None:
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(url_for('edit_artwork', artwork_id=artwork_id))
        try:
            relative_path = image_service.import_upload(upload)
            if relative_path not in artwork.pictures:
                artwork.pictures.append(relative_path)
                manager.update_artwork(artwork_id, artwork)
            flash('Image importée.', 'success')
        except ValueError as exc:
            flash(str(exc), 'danger')
        return redirect(url_for('edit_artwork', artwork_id=artwork_id))

    @app.post('/generate-site')
    def generate_site():
        docs_path = generator.generate()
        flash(f'Site régénéré dans {docs_path}.', 'success')
        return redirect(url_for('dashboard'))

    @app.get('/open-site')
    def open_site():
        target = (DOCS_DIR / 'index.html').resolve().as_uri()
        webbrowser.open(target)
        flash('Le site généré a été ouvert dans le navigateur.', 'success')
        return redirect(url_for('dashboard'))

    def _build_artwork_from_form(req, *, allow_id_change: bool, artwork_id: str | None = None) -> Artwork:
        final_id = req.form.get('id', '').strip() if allow_id_change else (artwork_id or '')
        pictures = [value.strip() for value in req.form.getlist('pictures') if value.strip()]
        return Artwork(
            id=final_id,
            title=LocalizedText(req.form.get('title_fr', '').strip(), req.form.get('title_en', '').strip()),
            description=LocalizedText(req.form.get('description_fr', '').strip(), req.form.get('description_en', '').strip()),
            type=LocalizedText(req.form.get('type_fr', '').strip(), req.form.get('type_en', '').strip()),
            dimensions=req.form.get('dimensions', '').strip(),
            date=req.form.get('date', '').strip(),
            price=req.form.get('price', '').strip(),
            keywords=LocalizedList(
                [item.strip() for item in req.form.get('keywords_fr', '').split(',') if item.strip()],
                [item.strip() for item in req.form.get('keywords_en', '').split(',') if item.strip()],
            ),
            notes=LocalizedText(req.form.get('notes_fr', '').strip(), req.form.get('notes_en', '').strip()),
            pictures=pictures,
        )

    return app


def main() -> None:
    app = create_app()
    app.run(debug=True)


if __name__ == '__main__':
    main()
