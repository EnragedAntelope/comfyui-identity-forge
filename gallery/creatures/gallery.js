/* =============================================================
   Identity Forge — Creature Gallery Script
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
  };

  // ── DOM refs ───────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const grid = $('#gallery-grid');
  const searchInput = $('#search');
  const searchClear = $('#search-clear');
  const countVisible = $('#count-visible');
  const countTotal = $('#count-total');
  const statsMissing = $('#stats-missing');
  const loadingEl = $('#loading');
  const noResults = $('#no-results');
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

    if (state.filtered.length === 0 && state.searchTerm) {
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
        btn.addEventListener('click', showMissing);
        btn.addEventListener('keydown', (e) => { if (e.key === 'Enter') showMissing(); });
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

    const nameEl = document.createElement('div');
    nameEl.className = 'card-name';
    nameEl.textContent = entry.name;
    nameEl.title = entry.name;

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

  function doSearch(term) {
    state.searchTerm = term.trim().toLowerCase();

    if (!state.searchTerm) {
      state.filtered = [...state.entries];
    } else {
      state.filtered = state.entries.filter((entry) =>
        entry.name.toLowerCase().includes(state.searchTerm)
      );
    }

    searchClear.classList.toggle('hidden', !state.searchTerm);
    render();
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

  // ── Show missing ───────────────────────────────────────
  function showMissing() {
    state.filtered = state.entries.filter((e) => !e.has_image);
    state.searchTerm = '';
    searchInput.value = 'missing entries';
    searchClear.classList.remove('hidden');
    render();
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

  // ── Init ───────────────────────────────────────────────
  async function init() {
    try {
      const manifest = await loadManifest();
      loadingEl.classList.add('hidden');

      // Update stats
      countTotal.textContent = manifest.total_entries || state.entries.length;

      render();

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
