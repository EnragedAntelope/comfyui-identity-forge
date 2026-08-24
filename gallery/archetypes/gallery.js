/* =============================================================
   Identity Forge — Archetype Gallery Script
   Lazy-loading image grid with search, lightbox, keyboard nav.
   ============================================================= */

(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────
  const state = {
    entries: [],           // Full list from manifest
    filtered: [],          // Currently filtered subset
    lightboxIndex: -1,     // Current lightbox position in filtered[]
    observer: null,        // IntersectionObserver for lazy loading
    searchTerm: '',
    sort: 'az',            // 'az' | 'new'
    onlyMissing: false,    // "N missing images" toggle
    onlyNew: false,        // "New in <version>" toggle
    version: '',           // Pack version this manifest was built from
    rank: new Map(),       // release -> position in the release list
  };

  // Sorting by name is locale-aware and numeric-aware, so "Spider-Man 2" lands
  // after "Spider-Man" rather than between "Spider-Man 1" and "Spider-Man 10".
  const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' });

  // Remembering the sort is a per-viewer convenience, not state anyone else sees,
  // so it lives in localStorage -- which throws outright in some privacy modes,
  // hence the try/catch on BOTH sides.
  const SORT_KEY = 'if-gallery-sort';
  function loadSort() {
    try {
      const saved = localStorage.getItem(SORT_KEY);
      if (saved === 'az' || saved === 'new') return saved;
    } catch (e) { /* private mode, blocked site data - fall through */ }
    return 'az';
  }
  function saveSort(value) {
    try { localStorage.setItem(SORT_KEY, value); } catch (e) { /* ignore */ }
  }

  /* An entry's release, ranked by POSITION in the manifest's release list rather
     than by comparing the version strings -- "0.10.0" sorts before "0.9.0" as
     text. An unstamped entry (a user-added one) ranks -1, i.e. oldest. */
  function rankOf(entry) {
    const r = state.rank.get(entry.added);
    return r === undefined ? -1 : r;
  }

  function isNew(entry) {
    return Boolean(state.version) && entry.added === state.version;
  }

  // ── DOM refs ───────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const grid = $('#gallery-grid');
  const searchInput = $('#search');
  const searchClear = $('#search-clear');
  const sortSelect = $('#sort');
  const sortGroup = $('#sort-group');
  const newFilterBtn = $('#filter-new');
  const countVisible = $('#count-visible');
  const countTotal = $('#count-total');
  const statsMissing = $('#stats-missing');
  const loadingEl = $('#loading');
  const noResults = $('#no-results');
  const clearFiltersBtn = $('#clear-search-btn');
  const lightbox = $('#lightbox');
  const lightboxImg = $('#lightbox-img');
  const lightboxName = $('#lightbox-name');
  const lightboxClose = $('#lightbox-close');
  const lightboxPrev = $('#lightbox-prev');
  const lightboxNext = $('#lightbox-next');

  // ── Load manifest ──────────────────────────────────────
  async function loadManifest() {
    try {
      const resp = await fetch('manifest.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      state.entries = data.entries || [];
      state.version = data.version || '';
      // schema_version 1 manifests carry neither field. Everything below then
      // sees every entry as unstamped, the sort control stays hidden, and the
      // page behaves exactly as it did before -- no error, no empty control.
      (data.releases || []).forEach((release, i) => state.rank.set(release, i));
      state.filtered = [...state.entries];
      return data;
    } catch (err) {
      console.error('Failed to load manifest:', err);
      loadingEl.innerHTML = '<p style="color:#e06060">⚠ Failed to load gallery data. Please try refreshing.</p>';
      throw err;
    }
  }

  // ── Render ─────────────────────────────────────────────
  function render() {
    // Clear grid
    grid.innerHTML = '';

    // Fires for ANY active narrowing, not just a search. Before 0.97.0 only a
    // search could empty the grid; the two toggles can too, and an empty grid with
    // no explanation reads as a broken page.
    if (state.filtered.length === 0 && isNarrowed()) {
      noResults.classList.remove('hidden');
    } else {
      noResults.classList.add('hidden');
    }

    // Build cards
    const fragment = document.createDocumentFragment();
    state.filtered.forEach((entry, idx) => {
      const card = createCard(entry, idx);
      fragment.appendChild(card);
    });
    grid.appendChild(fragment);

    // Update stats
    countVisible.textContent = state.filtered.length;
    countTotal.textContent = state.entries.length;

    // Update missing count
    const missingCount = state.entries.filter(e => !e.has_image).length;
    if (missingCount > 0) {
      statsMissing.innerHTML = `<span role="button" tabindex="0" title="Show missing entries" id="show-missing-btn">${missingCount} missing image${missingCount !== 1 ? 's' : ''}</span>`;
      const btn = $('#show-missing-btn');
      if (btn) {
        btn.setAttribute('aria-pressed', String(state.onlyMissing));
        btn.classList.toggle('is-active', state.onlyMissing);
        btn.addEventListener('click', toggleMissing);
        btn.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleMissing(); }
        });
      }
    } else {
      statsMissing.textContent = '';
    }

    // Re-observe lazy images
    observeNewImages();
  }

  function createCard(entry) {
    const card = document.createElement('div');
    card.className = 'gallery-card' + (entry.has_image ? '' : ' missing');
    card.setAttribute('role', 'listitem');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', entry.name + (entry.has_image ? '' : ' (no image)'));

    const wrapper = document.createElement('div');
    wrapper.className = 'card-image-wrapper';

    if (entry.has_image) {
      const img = document.createElement('img');
      img.setAttribute('data-src', entry.image);
      img.alt = entry.name;
      img.loading = 'lazy';
      // Inline tiny placeholder color to avoid layout shift
      img.style.backgroundColor = '#1a2a3a';
      wrapper.appendChild(img);
    } else {
      wrapper.classList.add('placeholder');
      wrapper.innerHTML = '<span class="placeholder-icon" aria-hidden="true">📷</span>';
      const badge = document.createElement('span');
      badge.className = 'missing-badge';
      badge.textContent = 'no image';
      card.appendChild(badge);
    }

    if (isNew(entry)) {
      const tag = document.createElement('span');
      tag.className = 'new-badge';
      tag.textContent = 'new';
      tag.title = 'Added in ' + entry.added;
      card.appendChild(tag);
    }

    const nameEl = document.createElement('div');
    nameEl.className = 'card-name';
    nameEl.textContent = entry.name;
    nameEl.title = entry.name + (entry.added ? ' - added in ' + entry.added : '');

    card.appendChild(wrapper);
    card.appendChild(nameEl);

    // Click handler
    if (entry.has_image) {
      card.addEventListener('click', () => openLightbox(entry.name));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(entry.name);
        }
      });
    }

    return card;
  }

  // ── Lazy Loading ───────────────────────────────────────
  function observeNewImages() {
    // Disconnect previous observer
    if (state.observer) state.observer.disconnect();

    state.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target;
            const src = img.getAttribute('data-src');
            if (src) {
              img.src = src;
              img.removeAttribute('data-src');
              img.addEventListener('load', () => img.classList.add('loaded'));
              img.addEventListener('error', () => {
                // On error, show placeholder
                img.parentElement.classList.add('placeholder');
                img.remove();
              });
            }
            state.observer.unobserve(img);
          }
        });
      },
      {
        rootMargin: '200px 0px',
        threshold: 0.01,
      }
    );

    // Observe all images with data-src
    grid.querySelectorAll('img[data-src]').forEach((img) => {
      state.observer.observe(img);
    });
  }

  // ── Search ─────────────────────────────────────────────
  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  /* The single place `state.filtered` is computed. Search, the two toggles and
     the sort all funnel through here, so they compose instead of overwriting one
     another -- searching used to clear a "missing images" view, and vice versa. */
  function applyView() {
    let list = state.entries;
    if (state.onlyMissing) list = list.filter((e) => !e.has_image);
    if (state.onlyNew) list = list.filter(isNew);
    if (state.searchTerm) {
      list = list.filter((e) => e.name.toLowerCase().includes(state.searchTerm));
    }

    // The manifest is already name-sorted, so A-Z needs no work; sorting a copy
    // matters only for 'new', but both branches copy so `filtered` is never an
    // alias of `entries`.
    list = [...list];
    if (state.sort === 'new') {
      list.sort((a, b) => rankOf(b) - rankOf(a) || collator.compare(a.name, b.name));
    }
    state.filtered = list;

    searchClear.classList.toggle('hidden', !state.searchTerm);
    if (newFilterBtn) newFilterBtn.setAttribute('aria-pressed', String(state.onlyNew));
    render();
  }

  function doSearch(term) {
    state.searchTerm = term.trim().toLowerCase();
    applyView();
  }

  function isNarrowed() {
    return Boolean(state.searchTerm) || state.onlyMissing || state.onlyNew;
  }

  /* Resets every narrowing at once. The button for this shipped in the markup from
     the start but was never wired to anything -- a dead control, and the only exit
     from a filtered empty state that does not require guessing which control caused
     it. The sort is deliberately NOT reset: it is a view preference, not a filter. */
  function clearFilters() {
    state.searchTerm = '';
    state.onlyMissing = false;
    state.onlyNew = false;
    searchInput.value = '';
    if (newFilterBtn) newFilterBtn.classList.remove('is-active');
    applyView();
  }

  const debouncedSearch = debounce(doSearch, 150);

  searchInput.addEventListener('input', () => {
    debouncedSearch(searchInput.value);
  });

  searchClear.addEventListener('click', () => {
    searchInput.value = '';
    doSearch('');
    searchInput.focus();
  });

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', () => {
      clearFilters();
      searchInput.focus();
    });
  }

  // ── Show missing ───────────────────────────────────────
  /* Was: it planted the literal text "missing entries" in the search box, which
     looked like a query the viewer had typed and could not be un-typed without
     clearing a real search. It is a toggle now, and it composes with the rest. */
  function toggleMissing() {
    state.onlyMissing = !state.onlyMissing;
    applyView();
  }

  // ── Lightbox ───────────────────────────────────────────
  function openLightbox(name) {
    // Find entry index in filtered list
    state.lightboxIndex = state.filtered.findIndex(
      (e) => e.name === name && e.has_image
    );
    if (state.lightboxIndex === -1) return;
    updateLightbox();
    lightbox.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    lightboxClose.focus();
    window.addEventListener('keydown', handleLightboxKey);
  }

  function closeLightbox() {
    lightbox.classList.add('hidden');
    document.body.style.overflow = '';
    state.lightboxIndex = -1;
    window.removeEventListener('keydown', handleLightboxKey);

    // Refocus the card that was open
    const name = lightboxName.textContent;
    const cards = grid.querySelectorAll('.gallery-card');
    cards.forEach((card) => {
      if (card.querySelector('.card-name')?.textContent === name) {
        card.focus();
      }
    });
  }

  function updateLightbox() {
    const entry = state.filtered[state.lightboxIndex];
    if (!entry) return;

    lightboxImg.src = entry.image;
    lightboxImg.alt = entry.name;
    lightboxName.textContent = entry.name;

    // Update nav button states
    lightboxPrev.disabled = state.lightboxIndex <= 0;
    lightboxNext.disabled = state.lightboxIndex >= state.filtered.length - 1;
  }

  function lightboxPrevImage() {
    // Find previous entry with an image
    let idx = state.lightboxIndex - 1;
    while (idx >= 0) {
      if (state.filtered[idx].has_image) {
        state.lightboxIndex = idx;
        updateLightbox();
        return;
      }
      idx--;
    }
  }

  function lightboxNextImage() {
    let idx = state.lightboxIndex + 1;
    while (idx < state.filtered.length) {
      if (state.filtered[idx].has_image) {
        state.lightboxIndex = idx;
        updateLightbox();
        return;
      }
      idx++;
    }
  }

  function handleLightboxKey(e) {
    switch (e.key) {
      case 'Escape':
        closeLightbox();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        lightboxPrevImage();
        break;
      case 'ArrowRight':
        e.preventDefault();
        lightboxNextImage();
        break;
    }
  }

  lightboxClose.addEventListener('click', closeLightbox);
  lightboxPrev.addEventListener('click', lightboxPrevImage);
  lightboxNext.addEventListener('click', lightboxNextImage);

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  // ── Keyboard shortcut hint ─────────────────────────────
  document.addEventListener('keydown', (e) => {
    // Ctrl+K or / to focus search
    if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && document.activeElement !== searchInput)) {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
  });

  // ── Sort & filter controls ─────────────────────────────
  /* Both controls are HIDDEN unless the manifest actually supports them: a sort
     with nothing to sort by, or a "New in ..." filter that is always present and
     sometimes empty, only teaches a viewer to ignore the control row. */
  function setupSortControls() {
    const stamped = state.rank.size > 0
      && state.entries.some((e) => e.added);

    if (sortGroup) sortGroup.hidden = !stamped;
    if (sortSelect) {
      if (stamped) {
        state.sort = loadSort();
        sortSelect.value = state.sort;
        sortSelect.addEventListener('change', () => {
          state.sort = sortSelect.value === 'new' ? 'new' : 'az';
          saveSort(state.sort);
          applyView();
        });
      }
    }

    if (newFilterBtn) {
      const anyNew = stamped && state.entries.some(isNew);
      newFilterBtn.hidden = !anyNew;
      if (anyNew) {
        newFilterBtn.textContent = 'New in ' + state.version;
        newFilterBtn.addEventListener('click', () => {
          state.onlyNew = !state.onlyNew;
          newFilterBtn.classList.toggle('is-active', state.onlyNew);
          applyView();
        });
      }
    }
  }

  // ── Init ───────────────────────────────────────────────
  async function init() {
    try {
      const manifest = await loadManifest();
      loadingEl.classList.add('hidden');

      // Update stats
      countTotal.textContent = manifest.total_entries || state.entries.length;

      setupSortControls();
      applyView();

      // Focus search on load if no hash
      if (!window.location.hash) {
        // Don't auto-focus on mobile to avoid keyboard popup
        if (window.innerWidth > 768) {
          searchInput.focus();
        }
      }
    } catch (err) {
      loadingEl.innerHTML = '<p style="color:#e06060">⚠ Failed to load gallery.</p>';
    }
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
