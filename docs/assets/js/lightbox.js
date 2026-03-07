(function () {
  const mainImage = document.getElementById('mainArtworkImage');
  const thumbButtons = document.querySelectorAll('.thumb-button');
  const lightbox = document.getElementById('lightbox');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxClose = document.getElementById('lightboxClose');

  if (thumbButtons.length && mainImage) {
    thumbButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const src = button.getAttribute('data-fullsrc');
        if (src) {
          mainImage.src = src;
        }
      });
    });
  }

  function openLightbox(src, alt) {
    if (!lightbox || !lightboxImage) return;
    lightboxImage.src = src;
    lightboxImage.alt = alt || '';
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    lightboxImage.src = '';
    document.body.style.overflow = '';
  }

  if (mainImage) {
    mainImage.addEventListener('click', () => openLightbox(mainImage.src, mainImage.alt));
  }

  if (lightboxClose) {
    lightboxClose.addEventListener('click', closeLightbox);
  }

  if (lightbox) {
    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox) closeLightbox();
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeLightbox();
  });
})();
