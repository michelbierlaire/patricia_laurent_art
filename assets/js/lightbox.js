(function () {
  const mainImage = document.getElementById('mainArtworkImage');
  const thumbButtons = document.querySelectorAll('.thumb-button');
  const lightbox = document.getElementById('lightbox');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxClose = document.getElementById('lightboxClose');
  const artworkPage = document.getElementById('artwork-page');

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
    if (!lightbox || !lightboxImage) return;
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

  if (!artworkPage) return;

  const prevUrl = artworkPage.dataset.prevUrl || '';
  const nextUrl = artworkPage.dataset.nextUrl || '';
  const swipeThreshold = 60;
  const horizontalRatio = 1.2;
  let touchStartX = null;
  let touchStartY = null;

  function shouldIgnoreSwipeStart(target) {
    return Boolean(target.closest('a, button, input, textarea, select, label'));
  }

  artworkPage.addEventListener(
    'touchstart',
    (event) => {
      if (!event.changedTouches.length) return;
      if (lightbox && !lightbox.hidden) return;
      if (shouldIgnoreSwipeStart(event.target)) return;

      const touch = event.changedTouches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
    },
    { passive: true }
  );

  artworkPage.addEventListener(
    'touchend',
    (event) => {
      if (touchStartX === null || touchStartY === null) return;
      if (!event.changedTouches.length) {
        touchStartX = null;
        touchStartY = null;
        return;
      }
      if (lightbox && !lightbox.hidden) {
        touchStartX = null;
        touchStartY = null;
        return;
      }

      const touch = event.changedTouches[0];
      const deltaX = touch.clientX - touchStartX;
      const deltaY = touch.clientY - touchStartY;
      const absDeltaX = Math.abs(deltaX);
      const absDeltaY = Math.abs(deltaY);

      touchStartX = null;
      touchStartY = null;

      if (absDeltaX < swipeThreshold) return;
      if (absDeltaX <= absDeltaY * horizontalRatio) return;

      if (deltaX < 0 && nextUrl) {
        window.location.href = nextUrl;
      } else if (deltaX > 0 && prevUrl) {
        window.location.href = prevUrl;
      }
    },
    { passive: true }
  );
})();
