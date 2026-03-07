(function () {
  const dataEl = document.getElementById('gallery-data');
  if (!dataEl) return;

  const items = JSON.parse(dataEl.textContent);
  const grid = document.getElementById('artworksGrid');
  const searchInput = document.getElementById('searchInput');
  const typeFilter = document.getElementById('typeFilter');
  const yearFilter = document.getElementById('yearFilter');
  const keywordFilter = document.getElementById('keywordFilter');
  const sortSelect = document.getElementById('sortSelect');
  const resultsCount = document.getElementById('resultsCount');
  const i18n = window.GALLERY_I18N || {};

  function uniq(values) {
    return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
  }

  function populateSelect(select, values) {
    values.forEach((value) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  populateSelect(typeFilter, uniq(items.map((item) => item.type)));
  populateSelect(yearFilter, uniq(items.map((item) => item.date)));
  populateSelect(keywordFilter, uniq(items.flatMap((item) => item.keywords || [])));

  function cardTemplate(item) {
    const media = item.cover
      ? `<img src="${item.cover}" alt="${item.title}" class="card-img-top artwork-image">`
      : `<div class="artwork-placeholder d-flex align-items-center justify-content-center">${i18n.no_image || 'No image available'}</div>`;

    const metaParts = [item.type, item.date, item.dimensions].filter(Boolean);
    const meta = metaParts.join(' · ');
    const excerpt = item.excerpt ? `<p class="artwork-excerpt">${item.excerpt}</p>` : '';

    return `
      <article class="col-12 col-sm-6 col-xl-4 col-xxl-3 artwork-item">
        <a href="${item.link}" class="card artwork-card h-100 text-decoration-none">
          <div class="artwork-media">${media}</div>
          <div class="card-body d-flex flex-column">
            <h3 class="artwork-title">${item.title}</h3>
            ${meta ? `<p class="artwork-meta mb-2">${meta}</p>` : ''}
            ${excerpt}
            <div class="mt-auto artwork-link">${i18n.view_details || 'View artwork'}</div>
          </div>
        </a>
      </article>`;
  }

  function sortItems(list) {
    const [field, direction] = sortSelect.value.split('-');
    const factor = direction === 'desc' ? -1 : 1;
    return [...list].sort((a, b) => {
      if (field === 'date') {
        return ((a.year || -1) - (b.year || -1)) * factor;
      }
      return a.title.localeCompare(b.title) * factor;
    });
  }

  function filterItems() {
    const query = searchInput.value.trim().toLowerCase();
    const typeValue = typeFilter.value;
    const yearValue = yearFilter.value;
    const keywordValue = keywordFilter.value;

    const filtered = items.filter((item) => {
      const matchesQuery = !query || item.search_blob.includes(query);
      const matchesType = !typeValue || item.type === typeValue;
      const matchesYear = !yearValue || item.date === yearValue;
      const matchesKeyword = !keywordValue || (item.keywords || []).includes(keywordValue);
      return matchesQuery && matchesType && matchesYear && matchesKeyword;
    });

    return sortItems(filtered);
  }

  function render() {
    const filtered = filterItems();
    grid.innerHTML = filtered.map(cardTemplate).join('');
    const suffix = filtered.length === 1 ? i18n.results_count_one : i18n.results_count_many;
    resultsCount.textContent = `${filtered.length} ${suffix}`;
  }

  [searchInput, typeFilter, yearFilter, keywordFilter, sortSelect].forEach((el) => {
    el.addEventListener('input', render);
    el.addEventListener('change', render);
  });

  render();
})();
