import { app } from "../../scripts/app.js";

/*
 * Identity Forge roster picker — Phase 4b (1.1.0).
 *
 * A searchable modal over the whole roster (cosplayers, archetypes, creatures),
 * attached to the three preset nodes' primary combo: IdentityForgeCosplayer's
 * `character`, IdentityForgeArchetype's `archetype`, IdentityForgeCreature's
 * `creature`. Ported from comfyui-stylebook's js/stylebook_gallery.js (the
 * picker dialog shape, the debounced search input, the focus trap, the
 * bulk-data lazy-fetch pattern) with everything sprite/atlas-related dropped:
 * this pack ships text-first cards, with images an explicit opt-in.
 *
 * Data comes from js/identity_forge_roster.json (scripts/generate_js_data.py),
 * a flat array of ~2481 entries tagged by `kind`. It is fetched lazily as
 * `.json`, never imported as `.js` -- ComfyUI globs **\/*.js under a pack's web
 * directory and imports every hit at app start, so a ~1MB module here would be
 * a startup tax on every user regardless of whether they use this pack's
 * character-name nodes at all.
 *
 * Search: case-insensitive substring over the precomputed `haystack`, with
 * every whitespace-split query token required (AND, order-independent) --
 * the one deliberate improvement over stylebook's single-substring match.
 * A query searches every kind regardless of the active tab; tabs only narrow
 * the view when the search box is empty.
 *
 * Scope note (also destined for the docs, by a later task): this searches
 * *roster entries* -- named cosplayers, archetypes, creatures -- not the
 * randomizable field pools on the main IdentityForge node. Said in the
 * modal's footer, which is visible in every state including the empty one.
 *
 * The trigger button is a floating DOM element positioned over the node's
 * canvas rect, tracked by a single shared requestAnimationFrame loop. It is
 * never added to `node.widgets`, so it can never occupy a `widgets_values`
 * slot -- unlike a `serialize: false` widget, which the 0.89.0 franchise_filter
 * incident (see WIDGETS_ADDED_BY_RELEASE in identity_forge_cosplayer.js) showed
 * still consumes one on *read*, forcing every existing node to be recreated.
 * random_pool (Task 2, 1.1.0) already occupies the trailing slot that scheme
 * would need next; this button deliberately never enters that bookkeeping at
 * all, so it adds no row to any repair table.
 *
 * Every failure here is caught so the node still works with no picker at all.
 */

// --- roster data (lazy .json fetch) -----------------------------------------

const ROSTER_FILE = "identity_forge_roster.json";

function assetURL(relative) {
  try {
    return new URL(relative, import.meta.url).href;
  } catch (_) {
    return relative;
  }
}

let roster = null; // sorted array, once loaded
let rosterPromise = null;

/**
 * Compare two roster names the way a person browsing alphabetically expects
 * (numeric-aware, accent/case-insensitive), falling back to code-point order
 * if Intl is unavailable -- a frontend failure here must degrade, not break.
 */
const compareNames = (() => {
  try {
    const collator = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });
    return (a, b) => collator.compare(a.name, b.name) || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
  } catch (_) {
    return (a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
  }
})();

/**
 * Fetch the roster index, once. Copies loadBulkData's retry semantics from
 * stylebook_gallery.js: the promise is nulled on failure so a later retry
 * (the placeholder's "Try again" button) actually re-fetches instead of
 * re-resolving the same rejection for the rest of the session.
 */
function loadRoster() {
  if (roster) return Promise.resolve(roster);
  if (!rosterPromise) {
    rosterPromise = fetch(assetURL("./" + ROSTER_FILE))
      .then((response) => {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data)) throw new Error("roster is not an array");
        roster = data.slice().sort(compareNames);
        return roster;
      })
      .catch((error) => {
        rosterPromise = null;
        throw error;
      });
  }
  return rosterPromise;
}

// --- kinds -------------------------------------------------------------------

const KIND_LABEL = { cosplayer: "Cosplayers", archetype: "Archetypes", creature: "Creatures" };
//: Gallery folder names differ from the roster's `kind` strings (the cosplay
//: gallery folder is "cosplay", not "cosplayer") -- see gallery/cosplay/publish.py's
//: GALLERY_KIND / REL_DIR.
const KIND_GALLERY_FOLDER = { cosplayer: "cosplay", archetype: "archetypes", creature: "creatures" };
const TAB_ALL = "__all__";
const TABS = [TAB_ALL, "cosplayer", "archetype", "creature"];

function tabLabel(tab) {
  return tab === TAB_ALL ? "All" : KIND_LABEL[tab] || tab;
}

// --- search: substring, multi-token AND, case-insensitive -------------------

function tokenize(query) {
  return String(query || "").trim().toLowerCase().split(/\s+/).filter(Boolean);
}

function matchesQuery(entry, tokens) {
  if (!tokens.length) return true;
  return tokens.every((token) => entry.haystack.includes(token));
}

// --- trait facets -------------------------------------------------------------
//
// Mirrors nodes/identity_forge_cosplayer.py's _SPECIAL_SCOPES keys and Task 2's
// three random_pool values verbatim, so browsing here and randomizing on the
// Cosplayer node share one vocabulary. Do not rename any of these strings.
//
// There is no per-entry boolean flag in the roster index for any of this --
// only the precomputed `haystack` string. scripts/generate_js_data.py folds
// six literal trait words into a cosplayer's haystack for exactly this reason
// (_cosplayer_trait_words: "masked"/"mascot" from covers_face/covers_body,
// "feral"/"beast" from body_plan, "giant"/"tiny" from size_scale), so five of
// the six scopes below are simple substring checks against those words.
//
// "Non-human / colored" (_scope_is_nonhuman) has no such folded keyword --
// the backend detects it with a regex over the costume prose instead. Rather
// than reproduce that regex against a haystack that only carries a *lowercased*
// copy of the costume text (the "naive regex over prose" trap this repo has
// already paid for twice; see architecture.md), this checks for the two
// literal, non-wildcard phrases the regex requires ("smooth, flawless", or
// "uniform, all-over") as plain substrings. That is narrower than the backend
// predicate (it misses the legacy "an even ... coat of" wording and the
// free-text `skin` override, neither of which is in the haystack at all) --
// a deliberate, documented approximation for a browse-time facet, not a data
// integrity assertion.
const FACET_ALL = "All characters";
const FACET_GIANT = "Giant characters";
const FACET_TINY = "Tiny characters";
const FACET_NONHUMAN = "Non-human / colored";
const FACET_MASKED = "Masked";
const FACET_MASCOT = "Mascot / full-suit";
const FACET_BEAST = "Beast / non-humanoid";
const FACET_PEOPLE = "People only — no mascot suits or beasts";
const FACET_MASCOT_POOL = "Mascot suits and beasts only";

const FACETS = [
  FACET_ALL, FACET_GIANT, FACET_TINY, FACET_NONHUMAN, FACET_MASKED,
  FACET_MASCOT, FACET_BEAST, FACET_PEOPLE, FACET_MASCOT_POOL,
];

function hasAny(haystack, words) {
  return words.some((w) => haystack.includes(w));
}

const FACET_PREDICATES = {
  [FACET_ALL]: () => true,
  [FACET_GIANT]: (e) => e.haystack.includes("giant"),
  [FACET_TINY]: (e) => e.haystack.includes("tiny"),
  [FACET_MASKED]: (e) => e.haystack.includes("masked"),
  [FACET_MASCOT]: (e) => e.haystack.includes("mascot"),
  [FACET_BEAST]: (e) => hasAny(e.haystack, ["feral", "beast"]),
  [FACET_NONHUMAN]: (e) => hasAny(e.haystack, ["smooth, flawless", "uniform, all-over"]),
  [FACET_PEOPLE]: (e) => !hasAny(e.haystack, ["mascot", "feral", "beast"]),
  [FACET_MASCOT_POOL]: (e) => hasAny(e.haystack, ["mascot", "feral", "beast"]),
};

/** Trait chips shown on a card. "mascot" implies "masked" in the haystack -- show the more specific one only. */
function traitChips(entry) {
  const chips = [];
  if (entry.haystack.includes("mascot")) chips.push("mascot");
  else if (entry.haystack.includes("masked")) chips.push("masked");
  if (hasAny(entry.haystack, ["feral", "beast"])) chips.push("beast");
  if (entry.haystack.includes("giant")) chips.push("giant");
  if (entry.haystack.includes("tiny")) chips.push("tiny");
  return chips;
}

// --- opt-in thumbnails --------------------------------------------------------
//
// Text-first, zero image payload by default. Enabling "Show preview images"
// fetches the LIVE gh-pages gallery manifest for a kind with a plain, absolute
// `fetch` -- explicitly not `api.fetchApi`, which targets the ComfyUI server,
// not GitHub Pages -- and lazy-loads <img> tags via IntersectionObserver. Any
// copy of a manifest.json committed under gallery/ on `main` is a stale
// snapshot and must never be read for URLs; only the published gh-pages file
// is ever fetched here.

const GH_PAGES_GALLERY_ROOT = "https://enragedantelope.github.io/comfyui-identity-forge/gallery/";
const PREVIEW_PREF_KEY = "identity_forge.picker.show_previews";

function galleryFolderURL(kind) {
  return GH_PAGES_GALLERY_ROOT + KIND_GALLERY_FOLDER[kind] + "/";
}

function loadPreviewPref() {
  try {
    return window.localStorage.getItem(PREVIEW_PREF_KEY) === "1";
  } catch (_) {
    return false;
  }
}

function savePreviewPref(value) {
  try {
    window.localStorage.setItem(PREVIEW_PREF_KEY, value ? "1" : "0");
  } catch (_) {
    /* best-effort; the toggle simply resets next session */
  }
}

//: kind -> Map<name, image-relative-path> | Promise<that Map>. Never surfaces
//: an error: a failed or offline fetch resolves to an empty Map so cards
//: silently stay text-only, and the cache entry is dropped so a later attempt
//: (toggle off/on, or back online) can retry.
const manifestCache = new Map();

function loadManifest(kind) {
  if (manifestCache.has(kind)) return manifestCache.get(kind);
  const promise = fetch(galleryFolderURL(kind) + "manifest.json")
    .then((response) => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then((data) => {
      const map = new Map();
      for (const entry of (data && data.entries) || []) {
        if (entry && entry.has_image && entry.image) map.set(entry.name, entry.image);
      }
      manifestCache.set(kind, map);
      return map;
    })
    .catch(() => {
      manifestCache.delete(kind);
      return new Map();
    });
  manifestCache.set(kind, promise);
  return promise;
}

// --- widget plumbing (same pattern as every other js/*.js file here) --------

function findWidget(node, name) {
  return (node.widgets || []).find((w) => w.name === name);
}

function setWidgetValue(node, widget, value) {
  if (!widget) return;
  widget.value = value;
  if (typeof widget.callback === "function") {
    try {
      widget.callback(value, app.canvas, node);
    } catch (error) {
      console.error("[IdentityForgePicker] widget callback failed", error);
    }
  }
}

// --- the dialog ---------------------------------------------------------------

const CSS_MARKER = "data-identity-forge-picker-css";

function injectCSS() {
  if (document.querySelector("[" + CSS_MARKER + "]")) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = assetURL("./identity_forge_picker.css");
  link.setAttribute(CSS_MARKER, "1");
  document.head.appendChild(link);
}

class IdentityForgePicker {
  /**
   * @param {object} config
   *   title                 dialog heading
   *   kind                  "cosplayer" | "archetype" | "creature" -- the only
   *                          kind selectable from this attachment point
   *   node                  the node this picker is attached to
   *   targetWidgetName      the combo widget the picker writes into
   *   franchiseFilterWidgetName  optional -- re-synced after a pick so the
   *                          "current selection is always reachable" rule holds
   */
  constructor(config) {
    this.config = config;
    this.query = "";
    this.activeTab = config.kind;
    this.facet = FACET_ALL;
    this.showPreviews = loadPreviewPref();
    this.focusIndex = 0;
    this.visible = [];
    this.overlay = null;
    this.previousFocus = null;
    this.imageObserver = null;
  }

  open() {
    if (this.overlay) return;
    this.previousFocus = document.activeElement;
    try {
      this.build();
      document.body.appendChild(this.overlay);
    } catch (error) {
      console.error("[IdentityForgePicker] failed to open", error);
      this.close();
      return;
    }
    requestAnimationFrame(() => {
      try {
        if (this.searchInput) this.searchInput.focus();
      } catch (_) { /* ignore */ }
    });
    // The dialog appears immediately; the fetch happens inside a frame that
    // already exists, rather than behind an unresponsive button.
    this.ensureData();
  }

  ensureData() {
    if (roster) {
      this.renderGrid();
      return;
    }
    this.showPlaceholder("Loading roster…");
    const opened = this.overlay;
    loadRoster().then(
      () => {
        if (this.overlay !== opened) return;
        this.renderGrid();
      },
      (error) => {
        if (this.overlay !== opened) return;
        console.error("[IdentityForgePicker] could not load the roster index", error);
        this.showPlaceholder(
          "Could not load the roster index. Check that the pack's js/ folder is complete, then try again.",
          () => this.ensureData(),
        );
      },
    );
  }

  showPlaceholder(message, onRetry) {
    if (!this.grid) return;
    this.grid.replaceChildren();
    this._focused = null;
    const box = document.createElement("div");
    box.className = "if-picker-empty";
    box.textContent = message;
    if (onRetry) {
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "if-picker-btn";
      retry.textContent = "Try again";
      retry.addEventListener("click", onRetry);
      box.append(document.createElement("br"), retry);
    }
    this.grid.appendChild(box);
    if (this.count) this.count.textContent = "";
    this.visible = [];
  }

  close() {
    if (this.imageObserver) {
      this.imageObserver.disconnect();
      this.imageObserver = null;
    }
    if (this.overlay && this.overlay.parentNode) {
      this.overlay.parentNode.removeChild(this.overlay);
    }
    this.overlay = null;
    this.grid = null;
    this.tabs = null;
    this.count = null;
    this.searchInput = null;
    this._focused = null;
    if (this._searchTimer) {
      clearTimeout(this._searchTimer);
      this._searchTimer = null;
    }
    try {
      if (this.previousFocus && this.previousFocus.focus) this.previousFocus.focus();
    } catch (_) { /* ignore */ }
  }

  build() {
    const overlay = document.createElement("div");
    overlay.className = "if-picker-overlay";

    const dialog = document.createElement("div");
    dialog.className = "if-picker-dialog";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", this.config.title);

    const header = document.createElement("div");
    header.className = "if-picker-header";

    const search = document.createElement("input");
    search.type = "search";
    search.className = "if-picker-search";
    search.placeholder = "Search by name, franchise, trait…";
    search.spellcheck = false;
    search.autocomplete = "off";
    search.setAttribute("aria-label", "Search the roster by name, franchise, or trait");
    search.addEventListener("input", (event) => {
      this.query = event.target.value || "";
      this.focusIndex = 0;
      if (this._searchTimer) clearTimeout(this._searchTimer);
      this._searchTimer = setTimeout(() => {
        this._searchTimer = null;
        this.renderGrid();
      }, 80);
    });
    this.searchInput = search;

    const count = document.createElement("span");
    count.className = "if-picker-count";
    count.setAttribute("aria-live", "polite");
    this.count = count;

    const facet = document.createElement("select");
    facet.className = "if-picker-facet";
    facet.setAttribute("aria-label", "Filter by trait");
    for (const value of FACETS) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      facet.appendChild(option);
    }
    facet.value = this.facet;
    facet.addEventListener("change", () => {
      this.facet = facet.value;
      this.focusIndex = 0;
      this.renderGrid();
    });
    this.facetSelect = facet;

    const previewLabel = document.createElement("label");
    previewLabel.className = "if-picker-preview-toggle";
    const previewCheckbox = document.createElement("input");
    previewCheckbox.type = "checkbox";
    previewCheckbox.checked = this.showPreviews;
    previewCheckbox.addEventListener("change", () => {
      this.showPreviews = previewCheckbox.checked;
      savePreviewPref(this.showPreviews);
      this.renderGrid();
    });
    previewLabel.append(previewCheckbox, document.createTextNode(" Show preview images"));
    this.previewCheckbox = previewCheckbox;

    const close = document.createElement("button");
    close.type = "button";
    close.className = "if-picker-btn if-picker-close";
    close.textContent = "Close";
    close.setAttribute("aria-label", "Close (" + this.config.title + ")");
    close.addEventListener("click", () => this.close());

    header.append(search, facet, count, previewLabel, close);

    const notice = document.createElement("div");
    notice.className = "if-picker-notice";
    notice.textContent =
      "Enabling previews fetches images from this project's GitHub Pages site (enragedantelope.github.io) — nothing else phones home.";

    const links = document.createElement("div");
    links.className = "if-picker-links";
    for (const kind of ["cosplayer", "archetype", "creature"]) {
      const a = document.createElement("a");
      a.href = galleryFolderURL(kind);
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = "Open the full " + KIND_LABEL[kind].toLowerCase() + " gallery ↗";
      links.appendChild(a);
    }

    const tabs = document.createElement("div");
    tabs.className = "if-picker-tabs";
    tabs.setAttribute("role", "tablist");
    this.tabs = tabs;

    const grid = document.createElement("div");
    grid.className = "if-picker-grid";
    grid.setAttribute("role", "listbox");
    grid.tabIndex = 0;
    this.grid = grid;

    const footer = document.createElement("div");
    footer.className = "if-picker-footer";
    footer.textContent =
      "Searches roster entries (cosplayers, archetypes, creatures) — not the randomizable "
      + "field pools on the main node. Arrow keys move, Enter selects, Escape closes.";

    dialog.append(header, notice, links, tabs, grid, footer);
    overlay.appendChild(dialog);

    overlay.addEventListener("mousedown", (event) => {
      if (event.target === overlay) this.close();
    });
    overlay.addEventListener("click", (event) => event.stopPropagation());
    overlay.addEventListener("keydown", (event) => this.onKeyDown(event), true);

    this.overlay = overlay;
    this.renderTabs();
    this.renderGrid();
  }

  focusableElements() {
    if (!this.overlay) return [];
    return Array.from(
      this.overlay.querySelectorAll('input, select, a[href], button, [tabindex]:not([tabindex="-1"])'),
    ).filter((el) => !el.disabled);
  }

  onKeyDown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      this.close();
      return;
    }

    if (event.key === "Tab") {
      const focusable = this.focusableElements();
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;
      const outside = !this.overlay.contains(active);
      if (event.shiftKey && (active === first || outside)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || outside)) {
        event.preventDefault();
        first.focus();
      }
      return;
    }

    const columns = this.columnCount();
    const lastIndex = this.visible.length - 1;
    let next = null;

    if (event.key === "ArrowRight") next = this.focusIndex + 1;
    else if (event.key === "ArrowLeft") next = this.focusIndex - 1;
    else if (event.key === "ArrowDown") next = this.focusIndex + columns;
    else if (event.key === "ArrowUp") next = this.focusIndex - columns;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = lastIndex;
    else if (event.key === "Enter") {
      const entry = this.visible[this.focusIndex];
      if (entry) {
        event.preventDefault();
        event.stopPropagation();
        this.select(entry);
      }
      return;
    } else {
      return;
    }

    if (next === null || lastIndex < 0) return;
    event.preventDefault();
    event.stopPropagation();
    this.focusIndex = Math.min(Math.max(next, 0), lastIndex);
    this.highlight();
  }

  columnCount() {
    if (!this.grid) return 1;
    const width = this.grid.clientWidth || 220;
    return Math.max(1, Math.floor(width / 210));
  }

  highlight() {
    if (!this.grid) return;
    const next = this.visible.length ? this.grid.children[this.focusIndex] || null : null;
    if (this._focused === next) {
      if (next && next.scrollIntoView) next.scrollIntoView({ block: "nearest" });
      return;
    }
    if (this._focused) {
      this._focused.classList.remove("focused");
      this._focused.setAttribute("aria-selected", "false");
    }
    this._focused = next;
    if (next) {
      next.classList.add("focused");
      next.setAttribute("aria-selected", "true");
      if (next.scrollIntoView) next.scrollIntoView({ block: "nearest" });
    }
  }

  renderTabs() {
    if (!this.tabs) return;
    this.tabs.replaceChildren();
    for (const tab of TABS) {
      const button = document.createElement("div");
      button.tabIndex = 0;
      const active = tab === this.activeTab && !this.query;
      button.className = "if-picker-tab" + (active ? " active" : "");
      button.textContent = tabLabel(tab);
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", active ? "true" : "false");
      button.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          button.click();
        }
      });
      button.addEventListener("click", () => {
        this.activeTab = tab;
        this.query = "";
        this.focusIndex = 0;
        if (this.searchInput) this.searchInput.value = "";
        this.renderTabs();
        this.renderGrid();
      });
      this.tabs.appendChild(button);
    }
  }

  visibleEntries() {
    if (!roster) return [];
    const tokens = tokenize(this.query);
    // A query spans every tab; only the empty query is tab-scoped.
    let list = tokens.length
      ? roster.filter((entry) => matchesQuery(entry, tokens))
      : this.activeTab === TAB_ALL
        ? roster
        : roster.filter((entry) => entry.kind === this.activeTab);
    if (this.facet !== FACET_ALL) {
      const predicate = FACET_PREDICATES[this.facet] || FACET_PREDICATES[FACET_ALL];
      list = list.filter(predicate);
    }
    return list;
  }

  renderGrid() {
    if (!this.grid) return;
    if (!roster) return; // ensureData() is showing the placeholder
    this.grid.replaceChildren();
    this._focused = null;

    this.visible = this.visibleEntries();
    this.renderTabs();

    // Kind badges only matter where the tab strip does not already say it.
    this._showKind = this.activeTab === TAB_ALL || Boolean(this.query);

    if (this.count) {
      this.count.textContent = this.visible.length + (this.visible.length === 1 ? " result" : " results");
    }

    if (!this.visible.length) {
      const empty = document.createElement("div");
      empty.className = "if-picker-empty";
      empty.textContent = this.query
        ? 'Nothing matches "' + this.query + '".'
        : "Nothing in this category.";
      this.grid.appendChild(empty);
      return;
    }

    if (this.imageObserver) {
      this.imageObserver.disconnect();
      this.imageObserver = null;
    }
    if (this.showPreviews && typeof IntersectionObserver !== "undefined") {
      this.imageObserver = new IntersectionObserver(
        (entries) => {
          for (const observed of entries) {
            if (!observed.isIntersecting) continue;
            const img = observed.target;
            const src = img.getAttribute("data-src");
            if (src) {
              img.src = src;
              img.removeAttribute("data-src");
            }
            this.imageObserver.unobserve(img);
          }
        },
        { rootMargin: "200px 0px", threshold: 0.01 },
      );
    }

    const fragment = document.createDocumentFragment();
    this.visible.forEach((entry, index) => {
      fragment.appendChild(this.buildTile(entry, index));
    });
    this.grid.appendChild(fragment);
    this.highlight();

    if (this.showPreviews) {
      // One manifest fetch per kind actually shown, not per card.
      const kindsShown = new Set(this.visible.map((e) => e.kind));
      for (const kind of kindsShown) {
        loadManifest(kind).then((map) => {
          if (!this.overlay || !map.size) return;
          this.applyManifest(kind, map);
        });
      }
    }
  }

  /** Wire up <img data-src> once a kind's manifest resolves, for cards already on screen. */
  applyManifest(kind, map) {
    if (!this.grid) return;
    for (const el of this.grid.querySelectorAll('[data-if-kind="' + kind + '"] .if-picker-art')) {
      const name = el.getAttribute("data-if-name");
      const relative = map.get(name);
      if (!relative || el.querySelector("img")) continue;
      const img = document.createElement("img");
      img.alt = "";
      img.setAttribute("data-src", galleryFolderURL(kind) + relative);
      img.loading = "lazy";
      el.replaceChildren(img);
      if (this.imageObserver) this.imageObserver.observe(img);
      else img.src = img.getAttribute("data-src"); // no IO support: load eagerly rather than never
    }
  }

  buildTile(entry, index) {
    const selectable = entry.kind === this.config.kind;
    const tile = document.createElement("div");
    tile.className = "if-picker-tile" + (selectable ? "" : " if-picker-tile-disabled");
    tile.setAttribute("role", "option");
    tile.setAttribute("aria-selected", "false");
    tile.setAttribute("aria-disabled", selectable ? "false" : "true");
    tile.tabIndex = -1;
    tile.dataset.ifKind = entry.kind;
    tile.dataset.ifName = entry.name;

    const art = document.createElement("div");
    art.className = "if-picker-art";
    art.dataset.ifName = entry.name;
    art.setAttribute("aria-hidden", "true");
    const glyph = document.createElement("span");
    glyph.className = "if-picker-glyph";
    glyph.textContent = (entry.name || "?").charAt(0).toUpperCase();
    art.appendChild(glyph);

    const name = document.createElement("div");
    name.className = "if-picker-name";
    name.textContent = entry.name;

    const sub = document.createElement("div");
    sub.className = "if-picker-sub";
    const bits = [entry.franchise ?? "", entry.category ?? ""].filter(Boolean);
    if (this._showKind) bits.unshift(KIND_LABEL[entry.kind]);
    sub.textContent = bits.join(" · ");

    const chips = document.createElement("div");
    chips.className = "if-picker-chips";
    for (const chip of traitChips(entry)) {
      const span = document.createElement("span");
      span.className = "if-picker-chip";
      span.textContent = chip;
      chips.appendChild(span);
    }

    tile.append(art, name, sub, chips);

    if (!selectable) {
      tile.title = "Browsing only — open the " + KIND_LABEL[entry.kind].slice(0, -1)
        + " node to pick this entry.";
    }

    tile.addEventListener("click", () => this.select(entry));
    tile.addEventListener("mouseenter", () => {
      this.focusIndex = index;
      this.highlight();
    });
    return tile;
  }

  select(entry) {
    if (entry.kind !== this.config.kind) return; // not valid for this node's combo
    try {
      const node = this.config.node;
      const widget = findWidget(node, this.config.targetWidgetName);
      setWidgetValue(node, widget, entry.name);
      // Respect franchise_filter: a pick made outside the active filter must
      // stay reachable afterward (filteredOptions' "current selection is
      // always reachable" rule). Re-invoking the filter's own callback with
      // its own current value recomputes that rule with the new selection,
      // reusing the exact logic in identity_forge_cosplayer.js rather than
      // duplicating it.
      if (this.config.franchiseFilterWidgetName) {
        const filterWidget = findWidget(node, this.config.franchiseFilterWidgetName);
        if (filterWidget && typeof filterWidget.callback === "function") {
          filterWidget.callback(filterWidget.value);
        }
      }
      if (typeof node.setDirtyCanvas === "function") node.setDirtyCanvas(true, true);
    } catch (error) {
      console.error("[IdentityForgePicker] selection failed", error);
    }
    this.close();
  }
}

// --- trigger button: a DOM overlay, never in node.widgets --------------------
//
// A shared requestAnimationFrame loop tracks every attached button's screen
// position from its node's canvas rect (node.pos/size against app.canvas's
// pan/zoom), so it stays visually anchored to the node without ever touching
// node.widgets or widgets_values. If app.canvas does not expose the expected
// shape (older/unknown frontend, or a headless test harness), the button is
// still created and clickable -- it simply is not position-tracked.

const activeButtons = [];
let tickingButtons = false;

function updateButtonPosition(node, button) {
  const canvas = app.canvas;
  if (!canvas || !canvas.canvas || typeof canvas.canvas.getBoundingClientRect !== "function") return;
  if (!node.pos || !node.size || (node.flags && node.flags.collapsed)) {
    button.style.display = "none";
    return;
  }
  const rect = canvas.canvas.getBoundingClientRect();
  const scale = (canvas.ds && canvas.ds.scale) || 1;
  const offset = (canvas.ds && canvas.ds.offset) || [0, 0];
  const left = rect.left + (node.pos[0] + offset[0]) * scale;
  const bottom = rect.top + (node.pos[1] + node.size[1] + offset[1]) * scale;
  button.style.display = "block";
  button.style.left = left + "px";
  button.style.top = bottom + 4 + "px";
  button.style.width = Math.max(80, node.size[0] * scale) + "px";
}

function ensureButtonTicking() {
  if (tickingButtons) return;
  tickingButtons = true;
  const tick = () => {
    for (let i = activeButtons.length - 1; i >= 0; i--) {
      const entry = activeButtons[i];
      if (!entry.button.isConnected) {
        activeButtons.splice(i, 1);
        continue;
      }
      try {
        updateButtonPosition(entry.node, entry.button);
      } catch (_) { /* ignore -- the button just stops tracking */ }
    }
    if (activeButtons.length) requestAnimationFrame(tick);
    else tickingButtons = false;
  };
  requestAnimationFrame(tick);
}

/** Node-instance re-entry guard: onNodeCreated can fire again for the same node. */
function alreadyAttached(node) {
  return Boolean(node.__identityForgePickerAttached);
}

const NODE_CONFIG = {
  IdentityForgeCosplayer: {
    kind: "cosplayer",
    targetWidgetName: "character",
    franchiseFilterWidgetName: "franchise_filter",
    title: "Identity Forge — browse cosplay roster",
    buttonLabel: "🔍 Browse roster…",
  },
  IdentityForgeArchetype: {
    kind: "archetype",
    targetWidgetName: "archetype",
    title: "Identity Forge — browse archetypes",
    buttonLabel: "🔍 Browse archetypes…",
  },
  IdentityForgeCreature: {
    kind: "creature",
    targetWidgetName: "creature",
    title: "Identity Forge — browse creatures",
    buttonLabel: "🔍 Browse creatures…",
  },
};

function setupPickerButton(node, config) {
  if (alreadyAttached(node)) return;
  if (!findWidget(node, config.targetWidgetName)) return; // schema doesn't match; nothing to attach to
  node.__identityForgePickerAttached = true;

  try {
    injectCSS();
  } catch (error) {
    console.error("[IdentityForgePicker] stylesheet injection failed", error);
  }

  const picker = new IdentityForgePicker({ ...config, node });

  const button = document.createElement("button");
  button.type = "button";
  button.className = "if-picker-trigger-btn";
  button.textContent = config.buttonLabel;
  button.setAttribute("aria-haspopup", "dialog");
  button.style.position = "fixed";
  button.style.zIndex = "9999";
  button.style.display = "none";
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    picker.open();
  });
  // Never dragged onto the canvas as a node-move gesture.
  button.addEventListener("pointerdown", (event) => event.stopPropagation());
  button.addEventListener("mousedown", (event) => event.stopPropagation());

  document.body.appendChild(button);
  node.__identityForgePickerButton = button;

  if (app.canvas && app.canvas.canvas && typeof app.canvas.canvas.getBoundingClientRect === "function") {
    activeButtons.push({ node, button });
    ensureButtonTicking();
  }

  const previousRemoved = node.onRemoved;
  node.onRemoved = function () {
    try {
      button.remove();
    } catch (_) { /* ignore */ }
    const idx = activeButtons.findIndex((entry) => entry.node === node);
    if (idx > -1) activeButtons.splice(idx, 1);
    return previousRemoved ? previousRemoved.apply(this, arguments) : undefined;
  };
}

app.registerExtension({
  name: "identity_forge.picker.ui",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const config = NODE_CONFIG[nodeData?.name];
    if (!config) return;
    const onCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onCreated ? onCreated.apply(this, arguments) : undefined;
      try {
        setupPickerButton(this, config);
      } catch (error) {
        console.error("[IdentityForgePicker] frontend setup failed", error);
      }
      return result;
    };
  },
});

// Exported for tests only -- not used by the extension itself. The reset
// helpers clear this module's singleton caches (roster data, gallery
// manifests) between test cases, since a jsdom test file imports this module
// once and would otherwise leak state -- e.g. a later "failed fetch" test
// silently passing because an earlier test already populated `roster`.
export const __testing = {
  IdentityForgePicker,
  tokenize,
  matchesQuery,
  FACET_PREDICATES,
  FACETS,
  loadRoster,
  loadManifest,
  setWidgetValue,
  galleryFolderURL,
  ROSTER_FILE,
  __resetForTests() {
    roster = null;
    rosterPromise = null;
    manifestCache.clear();
  },
};
