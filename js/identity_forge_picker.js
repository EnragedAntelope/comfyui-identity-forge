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
 * The tab and the query compose: a query is filtered *within* the active tab,
 * and the "All" tab is what searches every kind at once. This replaced the
 * original "a query spans every tab, tabs only apply to an empty box"
 * behaviour, which silently threw away the category the user had chosen the
 * moment they typed -- there was no way to search inside one kind at all.
 * Discoverability of the other kinds is kept by two additions rather than by
 * overriding the tab: while filtering, each tab shows its own match count
 * (so "Creatures (7)" is visible from the Cosplayers tab), and a tab whose
 * count is zero under the current query/facet renders dimmed. When the active
 * tab has no matches but another does, the empty state says so and offers a
 * one-click switch to "All".
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
// already paid for twice; see architecture.md), this checks for the three
// literal, non-wildcard phrases the regex's three alternatives require:
// "smooth, flawless", "uniform, all-over", and "coat of" (the stable,
// non-wildcard tail of `\ban even\b.*?\bcoat of\b` -- the leading "an even"
// is dropped only because plain substring matching cannot express the `.*?`
// gap between the two words, not because it doesn't matter). Fixed in the
// 1.1.0 fix round: the first revision checked only the first two phrases,
// which missed 97 of ~301 backend-flagged entries that use the "coat of"
// wording (e.g. Maui) -- verified against the real roster after the fix.
// Still narrower than the backend predicate in one respect (the free-text
// `skin` override is never in the haystack at all) -- a deliberate,
// documented approximation for a browse-time facet, not a data integrity
// assertion.
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
  [FACET_NONHUMAN]: (e) => hasAny(e.haystack, ["smooth, flawless", "uniform, all-over", "coat of"]),
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

//: kind -> Promise<Map<name, image-relative-path>>, held ONLY while a fetch
//: for that kind is in flight -- cleared the instant it settles, success or
//: failure, via `.finally()`. This is deliberately NOT a cache of the
//: resolved value (an earlier revision was, and that had two problems: (1)
//: it overwrote itself with the bare Map once the fetch resolved, so every
//: *second* call to loadManifest() for an already-loaded kind returned a
//: non-Promise -- the sole call site unconditionally chains `.then()` on the
//: result, so that threw `TypeError: ...then is not a function` inside
//: open()'s try/catch, silently breaking the dialog open for that kind until
//: a full page reload reset the module-level cache; (2) even fixed to always
//: return a Promise, an indefinite JS-level cache never expires for the life
//: of the tab, defeating GitHub Pages' own freshness contract for this file
//: -- confirmed via `curl -I` on the live manifest: `Cache-Control:
//: max-age=600` plus an `ETag`. A long-lived ComfyUI tab could show a stale
//: manifest forever with no way to force a refresh short of reloading the
//: whole page. Letting every call past the in-flight window issue a plain
//: `fetch()` again hands both problems to the browser's own HTTP cache,
//: which already does this correctly: within the 10-minute window it serves
//: the response from cache with no network round trip; past it, the
//: `ETag` lets the server answer 304 instead of re-sending the body. The
//: in-flight Promise is still cached (not skipped entirely) so that
//: `renderGrid()` firing once per currently-visible kind -- on open, every
//: tab switch, every debounced keystroke, every facet change -- can't fire
//: duplicate concurrent requests for the same kind while one is already on
//: the wire. See the 1.1.0 fix-round report (bug 3) for the full history.
//: Never surfaces an error: a failed or offline fetch resolves (not rejects)
//: to an empty Map so cards silently stay text-only, and (per the above) the
//: very next call retries on its own -- no separate retry bookkeeping needed.
const manifestFetches = new Map();

function loadManifest(kind) {
  if (manifestFetches.has(kind)) return manifestFetches.get(kind);
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
      return map;
    })
    .catch(() => new Map())
    .finally(() => {
      manifestFetches.delete(kind);
    });
  manifestFetches.set(kind, promise);
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
    // Reset filtering state to the clean default view (1.1.0 fix round: this
    // used to reset only the DOM -- a fresh <input> always starts empty, but
    // `this.query`/`this.facet` survived close() untouched, so reopening
    // showed an empty search box next to a grid still narrowed by whatever
    // was typed or picked last time. Not just cosmetic: `query` and `facet`
    // are read by visibleEntries() on every render, so the mismatch was
    // between what the box *showed* and what the grid actually *used*.
    // `showPreviews` is deliberately excluded -- that is a persisted user
    // preference (localStorage-backed), not per-open scratch state.
    this.query = "";
    this.activeTab = this.config.kind;
    this.facet = FACET_ALL;
    this.focusIndex = 0;
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
      // stopImmediatePropagation, not just stopPropagation: defense in depth
      // against any other capture-phase listener attached to this same
      // overlay element. (The reported "Escape deletes the node" bug traced
      // to something this handler cannot reach at all -- LiteGraph's own
      // ghost-node-placement cancel, which fires at the window/document level
      // strictly before an overlay-level listener ever runs, so no amount of
      // stopping propagation *here* could have prevented it. The actual fix
      // is gating the trigger button on `node.flags.ghost`, see
      // setupPickerButton/updateButtonPosition. This still stands on its own
      // merits for the dialog's normal, non-ghost operation.)
      event.stopImmediatePropagation();
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

  renderTabs(matching) {
    if (!this.tabs) return;
    this.tabs.replaceChildren();
    // Counts are shown only while a query or facet is narrowing the roster:
    // with nothing typed they would just restate each kind's total, and the
    // information the user actually lost when tabs started scoping the search
    // is "how many matches are in the tab I'm not looking at".
    const filtering = this.isFiltering();
    const counts = filtering ? this.tabCounts(matching || this.matchingEntries()) : null;
    for (const tab of TABS) {
      const button = document.createElement("div");
      button.tabIndex = 0;
      const active = tab === this.activeTab;
      const count = counts ? counts[tab] : null;
      button.className = "if-picker-tab" + (active ? " active" : "") + (count === 0 ? " empty" : "");
      button.dataset.tab = tab;
      button.textContent = tabLabel(tab) + (counts ? " (" + count + ")" : "");
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", active ? "true" : "false");
      button.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          button.click();
        }
      });
      button.addEventListener("click", () => {
        // The query is deliberately left untouched -- clearing it here was a
        // bug (1.1.0 fix round). Tab and query compose, so a tab click while
        // searching re-scopes the same search to another category rather
        // than discarding what was typed.
        this.activeTab = tab;
        this.focusIndex = 0;
        this.renderTabs();
        this.renderGrid();
      });
      this.tabs.appendChild(button);
    }
  }

  /**
   * Everything matching the current query + facet, across every kind --
   * deliberately NOT tab-scoped. This is what feeds the per-tab counts, so
   * the Cosplayers tab can still say how many creatures the same query hits.
   */
  matchingEntries() {
    if (!roster) return [];
    const tokens = tokenize(this.query);
    let list = tokens.length ? roster.filter((entry) => matchesQuery(entry, tokens)) : roster;
    if (this.facet !== FACET_ALL) {
      const predicate = FACET_PREDICATES[this.facet] || FACET_PREDICATES[FACET_ALL];
      list = list.filter(predicate);
    }
    return list;
  }

  /** The grid's contents: the query/facet matches, narrowed to the active tab. */
  visibleEntries(matching) {
    const list = matching || this.matchingEntries();
    return this.activeTab === TAB_ALL ? list : list.filter((entry) => entry.kind === this.activeTab);
  }

  /** Match count per tab under the current query + facet, TAB_ALL being the total. */
  tabCounts(matching) {
    const counts = { [TAB_ALL]: 0, cosplayer: 0, archetype: 0, creature: 0 };
    for (const entry of matching || []) {
      counts[TAB_ALL] += 1;
      if (counts[entry.kind] !== undefined) counts[entry.kind] += 1;
    }
    return counts;
  }

  /** True while anything is narrowing the roster -- when the counts are worth showing. */
  isFiltering() {
    return Boolean(tokenize(this.query).length) || this.facet !== FACET_ALL;
  }

  renderGrid() {
    if (!this.grid) return;
    if (!roster) return; // ensureData() is showing the placeholder
    this.grid.replaceChildren();
    this._focused = null;

    const matching = this.matchingEntries();
    this.visible = this.visibleEntries(matching);
    this.renderTabs(matching);

    // Kind badges only matter where the tab strip does not already say it.
    // Any tab other than "All" now scopes the grid to a single kind, query or
    // not, so the badge is redundant there.
    this._showKind = this.activeTab === TAB_ALL;

    if (this.count) {
      this.count.textContent = this.visible.length + (this.visible.length === 1 ? " result" : " results");
    }

    if (!this.visible.length) {
      const empty = document.createElement("div");
      empty.className = "if-picker-empty";
      // The tab now scopes the search, so "nothing here" is only half the
      // answer -- say whether the same query hits another category, and make
      // getting there one click rather than a hunt across the tab strip.
      const elsewhere = this.activeTab === TAB_ALL ? 0 : matching.length;
      if (this.query && this.activeTab === TAB_ALL) {
        empty.textContent = 'Nothing matches "' + this.query + '".';
      } else if (this.query) {
        empty.textContent = 'No ' + tabLabel(this.activeTab).toLowerCase()
          + ' match "' + this.query + '"'
          + (elsewhere ? ' — ' + elsewhere + ' match' + (elsewhere === 1 ? "" : "es")
            + ' in other categories.' : ".");
      } else {
        empty.textContent = "Nothing in this category"
          + (elsewhere ? " — " + elsewhere + " match" + (elsewhere === 1 ? "" : "es")
            + " in other categories." : ".");
      }
      if (elsewhere) {
        const showAll = document.createElement("button");
        showAll.type = "button";
        showAll.className = "if-picker-btn";
        showAll.textContent = "Search all categories";
        showAll.addEventListener("click", () => {
          this.activeTab = TAB_ALL;
          this.focusIndex = 0;
          this.renderGrid();
        });
        empty.append(document.createElement("br"), showAll);
      }
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
//
// Anchored to the node's TITLE BAR (fix round 2), not below the node's
// bottom edge (the original placement). The bottom edge is exactly where the
// LAST widget's dropdown expands, and a native combo's own popup lives in a
// separate, high stacking context this button's z-index cannot reliably
// out-rank -- confirmed live with "Nodes 2.0 BETA" toggled on in a real
// ComfyUI instance: opening `random_pool`'s dropdown put this button's
// z-index-100 box directly over the dropdown's own z-index-3000 popup at the
// exact click target, so a real click there opened the picker instead of
// selecting the dropdown option. That is misdirected input, not a cosmetic
// glitch, and no z-index this button could plausibly claim is guaranteed to
// beat every native popup's own stacking context in every ComfyUI frontend
// version. Moving the button to the title bar removes the collision class
// entirely, because no widget's dropdown ever expands upward into the title
// bar -- there is nowhere left for the two to overlap.

const TRIGGER_BUTTON_SIZE = 22; // fixed CSS px; never scaled with zoom, so it stays legible at any zoom level
const TRIGGER_BUTTON_MARGIN = 4;

const activeButtons = [];
let tickingButtons = false;

function updateButtonPosition(node, button) {
  const canvas = app.canvas;
  if (!canvas || !canvas.canvas || typeof canvas.canvas.getBoundingClientRect !== "function") return;
  if (!node.pos || !node.size || (node.flags && (node.flags.collapsed || node.flags.ghost))) {
    // `flags.ghost`: LiteGraph's own "still following the mouse, not yet
    // placed" state for a node just spawned from the node-search palette
    // (double-click canvas -> type a name -> Enter, with no click yet to
    // commit it). Hiding the button here is the real fix for a critical
    // 1.1.0 bug: a DOM overlay button is clickable even while the node
    // underneath is still a ghost, and if a user opened the picker from
    // that state and then pressed Escape, LiteGraph's OWN "cancel node
    // placement" handler (bound at the window/document level, ahead of
    // this dialog's own overlay-level Escape handler in the capture order,
    // so nothing this file does to its own keydown listener can outrun it)
    // deleted the still-ghost node -- confirmed live via Playwright: the
    // dialog stayed open (this file's handler never even ran) and the node
    // vanished. Making the trigger unusable during ghost mode closes the
    // actual hole rather than trying to win an unwinnable propagation race
    // against a framework-level shortcut. The click handler in
    // setupPickerButton carries the same `node.flags.ghost` guard directly
    // (belt-and-suspenders, and the only guard at all on a frontend where
    // this position-tracking loop never starts in the first place).
    button.style.display = "none";
    return;
  }
  const rect = canvas.canvas.getBoundingClientRect();
  const scale = (canvas.ds && canvas.ds.scale) || 1;
  const offset = (canvas.ds && canvas.ds.offset) || [0, 0];
  // node.pos is the top-left of the node's BODY, i.e. the boundary between
  // the title bar (above it) and the widget area (below it) -- the title
  // bar itself occupies the titleHeight graph-units immediately above
  // node.pos[1]. Read LiteGraph's own constant defensively (a bare
  // `LiteGraph` global reference would throw in this ES module if the
  // frontend ever stops exposing it) with the long-standing 30 default as
  // the fallback.
  const titleHeight = (typeof window !== "undefined" && window.LiteGraph && window.LiteGraph.NODE_TITLE_HEIGHT) || 30;
  const nodeScreenRight = rect.left + (node.pos[0] + node.size[0] + offset[0]) * scale;
  const bodyScreenTop = rect.top + (node.pos[1] + offset[1]) * scale;
  const titleBarScreenTop = bodyScreenTop - titleHeight * scale;
  const titleBarScreenHeight = titleHeight * scale;
  button.style.display = "flex";
  button.style.left = (nodeScreenRight - TRIGGER_BUTTON_SIZE - TRIGGER_BUTTON_MARGIN) + "px";
  button.style.top = (titleBarScreenTop + (titleBarScreenHeight - TRIGGER_BUTTON_SIZE) / 2) + "px";
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
  // Icon-only: the button now lives in the node's title bar (fix round 2),
  // which has no room for the full "🔍 Browse roster…" label the original
  // bottom-anchored placement could afford. The full text survives as the
  // accessible name (aria-label) and the native hover tooltip (title).
  button.textContent = "🔍";
  button.setAttribute("aria-label", config.buttonLabel);
  button.title = config.buttonLabel;
  button.setAttribute("aria-haspopup", "dialog");
  button.style.position = "fixed";
  button.style.width = TRIGGER_BUTTON_SIZE + "px";
  button.style.height = TRIGGER_BUTTON_SIZE + "px";
  button.style.alignItems = "center";
  button.style.justifyContent = "center";
  // Deliberately modest, not the overlay dialog's own 10000: a full modal
  // legitimately belongs above everything, but this is just a trigger sitting
  // on the node's title bar. Kept modest even after the fix-round-2
  // repositioning (which is the real fix for the confirmed "Nodes 2.0"
  // click-misdirection collision -- see updateButtonPosition's comment) as
  // continued defense in depth, since no title bar is guaranteed collision-free
  // in every current or future ComfyUI frontend.
  button.style.zIndex = "100";
  button.style.display = "none";
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    // Belt-and-suspenders alongside the ghost check in updateButtonPosition:
    // that check hides the button once the position-tracking loop's next
    // frame runs, but a click landing in the same frame the node became a
    // ghost (or on a frontend where the loop never starts at all -- see the
    // guard around `activeButtons.push` below) would still reach here.
    if (node.flags && node.flags.ghost) return;
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
  updateButtonPosition,
  TRIGGER_BUTTON_SIZE,
  __resetForTests() {
    roster = null;
    rosterPromise = null;
    manifestFetches.clear();
  },
};
