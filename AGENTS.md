# AGENTS.md — comfyui-identity-forge

A character creator and person generator for ComfyUI. Builds coherent, seed-reproducible people from dropdown menus with a constraint engine that prevents clashing traits. Zero dependencies, fully offline — no LLM, no API keys. Built on ComfyUI V3 API (`comfy_api.latest`), category: `conditioning/character`.

**Docs: `docs/architecture.md` (deep reference — read it before engine/data changes)**

## Current state

_Last verified: 2026-09-01 (1.2.0)_

- **Status:** in active development, released at v1.2.0 (`pyproject.toml`). Published to the Comfy Registry via `.github/workflows/publish_action.yml`, which fires on a `pyproject.toml` version change on `main` — bump the version on every functional commit or the release never ships. CI (`.github/workflows/ci.yml`) is deliberately dependency-free.
- **Works:** the constraint engine resolving dropdowns into coherent prose plus structured JSON, seed-reproducible; the four preset layer nodes (Archetype, Creature, Modifier, Cosplayer); searchable dropdown widgets, live preview, the `franchise_filter`, the `random_pool` scope-composing filter, and the save/load vault in `js/`; a searchable **in-node roster picker** (`js/identity_forge_picker.js`) on the Cosplayer/Archetype/Creature nodes — trait facets, cross-tab search, opt-in gallery thumbnails, backed by a generated `js/identity_forge_roster.json` search index; Stylebook interop, the composition axis, and the **Turnaround** reference-set node (which emits every camera view of one resolved character as a list, so one queue renders the set); a jsdom frontend suite alongside the Python one; generated reference docs and JS data with `--check` modes wired into the gate. A cosplay entry may render as a **person in a costume**, as a **mascot suit** (`covers_face` + `covers_body` + `mask`), or — since 0.95.0 — as the **beast itself** (`body_plan: "feral"`, which emits the Creature node's Species & Anatomy payload instead of a costume); see architecture.md → "Animal characters split four ways". `scripts/render_gallery.py` renders a roster entry's gallery image by driving a running ComfyUI over HTTP and publishes it to `gh-pages`, and `gallery/render_manifest.json` + `--check` fail CI when an entry's text changes without a re-render (architecture.md → "The gallery render pipeline"). Since 0.97.0 every roster entry also carries a **release stamp** (`data/versions.py`, written by `scripts/stamp_versions.py`, gated in CI), which is what lets the three sample gallery pages offer **A–Z / Newest first** and a **New in `<version>`** filter.
- **In progress:** roster and coherence curation is the ongoing work, not a milestone — each release adds characters/creatures/archetypes and closes coherence bugs found by rendering them. `docs/suggested-additions.md` is the live backlog (under consideration / decided against / still to consider).
- **Recent releases** — one line each. **This list is a pointer, not a changelog:** the reasoning for every item is in `docs/architecture.md` (the sections are named there per release) and the full messages are in `git log`. Keep roughly the last eight and let older ones drop off; do not let an entry grow into a paragraph.
  - **1.2.0** — **`_CATEGORY_FRANCHISES` had 21 defects, not the two typos 1.1.0 logged**: nine mapped names no entry used and twelve live franchises unmapped, so 13 shipped entries fell through to `_DEFAULT_CATEGORY` and were unreachable under their own `random_scope` category (`Maomao` could never be drawn by an "Anime & Manga" scope). Fixed, plus a **bidirectional** `validate_data.py` gate that reads the source with `ast` so a private `user_options.json` cannot fail it. **`composition` gained its `location` gate** (backlog row 4, closed): the two sky values are excluded at every indoor location and a void backdrop also loses `leading lines`, with `location` as the trigger so the place stands. Field options: `footwear` 22→25, `piercings` 12→14, `composition` 8→9 — and **`legwear` stopped being silent for men** (male pool 1→4, leaned 2x to `no visible legwear`, gated by a new `LEGWEAR_BY_STYLE`). That gate had to be a **deferred-field pool filter, not a `CONSTRAINT_RULES` exclusion**, which is inert on a deferred field — measured at 132 violations before the fix, 0 after. 15 roster entries: 5 cosplayers (`Mara Sov`, `Jayne Cobb`, `Cyberman`, `Dr. Mrs. The Monarch` + `The Monarch`), 6 creatures (`tardigrade`, `ocean sunfish`, `saiga antelope`, `markhor`, `secretary bird`, `proboscis monkey`) and 4 archetypes (`Filipiniana Terno`, `Aso-Ebi with Gele`, `Gondolier`, `Chimney Sweep`). Hygiene: **`pytest` works** (the stub was missing `ComfyExtension`, not mis-ordered), the 18 runtime `print()` calls became `logging`, and `SECURITY.md`, `dependabot.yml` and a contributor-runnable `scripts/check_public_safety.py` landed. See architecture.md → the four 1.2.0 sections.
  - **1.1.0** — Neon/signage lighting coherence: `neon_venue` split into `neon_signage` / `venue_rig` / `bokeh` (proportional weight rescale, zero share drift) plus `NEON_SIGNAGE_VENUE_LOCATIONS` / `NEON_STREET_LOCATIONS` allowlists, closing the marginal-vs-conditional bias a flat exclusion would have caused. `random_pool` widget on Cosplayer (People only / Mascot suits and beasts only), composing with `random_scope` instead of becoming a seventh special scope. A searchable in-node **roster picker** modal on all three preset nodes (trait facets, opt-in thumbnails, cross-tab search) — two fix rounds closed two Critical bugs found in live testing (Escape deleting an unplaced ghost node; `random_pool` silently dropped on reload by a ComfyUI-core `migrateWidgetsValues` bug) and a Nodes-2.0 click-collision; `random_pool`'s visual position was also reordered, but only for the classic canvas widget renderer — confirmed inert under Nodes 2.0/VueNodes, a documented, parked limitation (no non-invasive hook exists there without touching the widget-safety invariant). 17 cosplayers across 8 new franchises — Mayor McCheese, Barbarella + The Great Tyrant, The Rocketeer, Robby the Robot, Princess Ardala + Twiki, The Martian Ambassador, Lady Penelope, The Toxic Avenger, and The Venture Bros' Triana Orpheus — plus five new Flash Gordon entries and Heavy Metal's second (Julie); Princess Aura refined onto maintainer-verified 1980-film canon. See architecture.md → the three named 1.1.0 sections.
  - **1.0.0** — Roster pass: 8 cosplayers across Chrono Trigger and Clair Obscur: Expedition 33, plus 91 more across 50 new franchises in four waves — video games (`Pyra`, `Panam Palmer`, `Quiet`, `Fran`, `Mirko`, `Lucina`, `Megaera`, `Selvaria Bles`, `Liliana Vess`, mascot-route `Rivet`/`Amy Rose`/`Rouge the Bat`/`Elora`, and 14 more), anime (`Lum Invader`, `Fujiko Mine`, helmet-route `Celty Sturluson`, the Inuyasha trio, Chainsaw Man's `Reze`/`Himeno`/`Quanxi`, and 12 more), comics (`Dejah Thoris`, `Tank Girl`, `Aeon Flux`, `Taarna`, `Ramona Flowers`, `Michonne`, duck-route `Magica De Spell`, gem-skin `Spinel`/`Rose Quartz`, and 9 more), screen (`Sarah Williams`, `Tauriel`, `River Tam`, bald-route `Ilia`, `Vanessa Ives`, `Eda Clawthorne`, and 12 more). 2 new creatures (`naked mole rat`, `goblin shark` off its 0.98.0 backlog case) and 2 new archetypes (`Kendo Practitioner`, `Tavern Wench`); the `mole`'s head rewritten onto positive statements — its "no visible ears" clause drew ears, the Never-negate rule catching a shipped generic. **Vault recall fixed:** `IdentityForgeVaultLoad` recall of a `wardrobe: "Any"` / full-spectrum `hair_color_scope` character no longer rebuilds a different person — both widgets gained an `"Auto (preset)"` defer sentinel, so a saved character loaded with both set to it replays its exact saved controls. See architecture.md → "Vault recall and the control sentinels". **Gallery render bug fixed:** `scripts/render_gallery.py`'s `_gallery_shot()` picked a random `shot_type` for every gallery render but its exclusion filter forgot the field's `"None"` omit-sentinel alongside `"Random"` — on the seeds that landed on it, the gallery render silently discarded whatever `shot_type` the archetype/cosplayer itself locked (a non-`Random` widget value always beats a preset), with no framing at all. Caught via `Kendo Practitioner` (locked to `"full body shot"`) rendering as an extreme close-up. `tests/test_render_manifest.py::GalleryShotPoolTests` pins it.
  - **0.99.0** — **Turnaround rewritten.** It was a second Identity Forge (six duplicated steering widgets, ~75 fields silently forced to Random, a third competing `seed`, and an auto-incrementing `index` whose N-queue set let an upstream `randomize` re-roll the character between views). It now takes a **resolved** character (`IdentityForge.prompt_json`) and emits every view as a **list output** — one queue, the whole set, four camera-only controls, no seed, no `fingerprint_inputs`. Two silent engine traps found and pinned: `"Random"` is not `"Any"` to the `gender` control, and `_meta.wardrobe` is recorded but not replayed. The straight-back view now **omits the face** (Face + Makeup groups, `facial_hair`, `expression`) — a live render turned the head to show the eyes and lipstick the prose named; the omission never negates. Also found by running the suite against the *real* `comfy_api` rather than the stub: `dump_frontend_fixtures.py` would commit the maintainer's private vault entries (now guarded), and `RELEASES` legitimately omits an engine-only release (test corrected). See architecture.md → "The Turnaround owns only the camera".
  - **0.98.0** — 16 cosplayers: `Amara` (unblocked from the 0.97.0 decline by `anatomy_note`'s six-arm case); the core `Looney Tunes` cast (`Porky Pig`, `Sylvester`, `Tweety`, `Wile E. Coyote`, `Road Runner`, `Foghorn Leghorn`, `Speedy Gonzales` — that franchise to 14); and six new-franchise entries (`Sans` + `Papyrus`, `Cuphead`, `Isabelle`, `Bill Cipher`, `Kaneda`, `Ai Hoshino`, `Maomao`) that left the 0.88.0 skip list via characters whose look reads without the name doing the work. Three render-review rewrites: `Greez Dritus` onto the Dexter mask pattern (his published render had come back two-armed), `Grogu` to the mascot treatment, mosquito proboscis re-led with body-relative scale. New **Turnaround** node — one seed-fixed identity, N auto-indexed camera views for reference sheets. Gallery: shots pinned front-facing (the pin initially shipped dead to a duplicate execute, and the pool let the `Random` control value through), re-renders now overwrite via a staging dir, favicons on all three sample pages. Pre-merge review closed seven more: the Turnaround was missing `fingerprint_inputs` (its whole point is an auto-advancing widget — the ComfyUI#11905 case), its six steering widgets shipped with no tooltips at all and now read them off `IdentityForge.define_schema()`, it was absent from `dump_frontend_fixtures.py`'s node map, and canon fixes landed on `Kaneda` (the film look is red head to foot), `Maomao` (blue eyes, the bandaged forearm, the burgundy skirt), `Ai Hoshino` (indigo star-pupils, and the free-text `eyes` value now obeys the `_EYE_PART_RE` rule) and `Cuphead` / `Bill Cipher` / `Porky Pig` / `Grogu`. See architecture.md → "Front-facing shots and overwrite publishing".
  - **0.97.0** — 9 cosplayers (`Mizora`; `Zer0` + `Sir Hammerlock`; `The Invisible Man`; `Ash Williams`; `Immortan Joe`; `Mega Man`; `Sherlock Holmes`; `The Knight (Hollow Knight)`) across four new franchises, which takes **Universal Monsters to 8 and therefore adds a `Franchise: Universal Monsters` random_scope option**. Five engine changes, three of them long-open and all measured: the bare-adjective `height` now leads the phrase instead of trailing it (**CLOSED**, open since 0.84.0); `composition` joins the giant/tiny scale gate (**CLOSED**); a species `hands` slot suppresses the human `nails` field (**CLOSED**); `anatomy_note` gives a maskless entry the early body sentence the 0.96.0 limb fix needed (**CLOSED**, applied to the four multi-armed entries); and **`bag` gained the masculine trim it never had — 13.7% of default male renders were carrying a handbag**, measured over 1000 seeds. Field options: `mary janes`, `cowboy boots`, `argyle` (which repriced the whole patterned set to hold plain at 2/10), `split dye`, `stretched lobes`, three men's bags. Gallery: sort + "New in" filter, and two dead controls fixed. Frontend: re-entry guards on the four setups that lacked one, and four vault/creature audit findings. See architecture.md → the five 0.97.0 sections.
- **Known gaps / next steps:** **~308 masked entries still carry gallery images rendered from the pre-0.90.0 buried-mask prose** — deliberately not re-rendered (maintainer call), and `--check` cannot flag them because the change was prose-only. **`python -m unittest discover -s tests -t . -v` is THE command** (the `-t .` is load-bearing) and the CI gate — it is what guarantees the pack stays dependency-free. `pytest` also works as of 1.2.0: it used to fail every test with `ImportError: cannot import name 'ComfyExtension'` because the stub package was empty and only the repo-root `__init__.py` imports that name, which unittest never loads. Fixed by exporting it from the stub plus a rootdir `conftest.py`; gallery images live only on `gh-pages`, so a `main`-only checkout cannot preview them; **editing an entry's text while ComfyUI is off turns CI red** until `render_gallery.py` re-renders it — that is the gate working as intended. **The render gate is GREEN**, verified via `python scripts/render_gallery.py --check` (roster counts drift release to release; see `python tests/validate_data.py` for the current ones). **CLOSED at 1.2.0:** `composition` now has its indoor/outdoor coherence gate against `location`. Both sky values assert open sky and an interior has none, so they are excluded at every indoor location; a void backdrop also loses `leading lines drawing the eye to the subject`. `location` is the trigger, so the place stands and the composition adapts. See architecture.md → "Composition answers to the place, not only the camera". `docs/suggested-additions.md` "Under consideration" holds three `hair_style` values (`hime cut`, `wolf cut`, `victory rolls`) blocked on family-weight arithmetic, not taste; "Decided against" is not to be re-litigated, and it gained a **"Field options — declined"** table at 0.97.0 (chiefly: no `ethnicity` additions — they are not visually distinguishable in a render *and* would take Europe from ~30% to ~35% of a flat field). **Three of the four measured open questions were closed at 0.97.0** — the `composition` scale gate, the `hands`→`nails` suppression, and the four multi-armed maskless entries (via `anatomy_note`) — at the cost that was priced when they were deferred: the published images for the affected entries are no longer literal reproductions of current output, and `--check` cannot see prose-only drift. **A third opened at 0.99.0 and fixed at 0.102.0:** `IdentityForgeVaultLoad` recall of a character generated with `wardrobe: "Any"` used to rebuild a *different person* — `_meta.wardrobe` was written into the document but never honoured on the `archetype_json` path (150/150 sampled seeds). Fixed by adding an "Auto (preset)" sentinel to the `wardrobe` / `hair_color_scope` widgets: when set, recall replays the saved `_meta` values instead of the widget defaults. See architecture.md → "Vault recall and the control sentinels". **A fourth is deliberate and closed to re-litigation:** the Turnaround's back view still draws a costume's chest-front detail on the back (a Supergirl S-shield, measured live) because a costume is one authored free-text string; parsing it to find front-facing clauses is the regex-over-prose trap, and the only correct fix is structured front/back costume data across the roster. **Two remain open, both deliberate:** (1) `_POCKETLESS_GARMENT_RE` is an allowlist, so a pocketless costume it does not name still draws a pockets gesture; (2) **costume text that asserts a body trait against an unpinned random field** ("on a hulking frame" beside "a very slim build") — 33 entries, and the `signature`/`physique` split that causes it is *deliberate*; **if it is ever taken up, measure it again from scratch — the naive regex reported 171 and was wrong.** **Found at 1.1.0, FIXED at 1.2.0 and far worse than reported:** `_CATEGORY_FRANCHISES` held **21 defects**, not two typos — nine mapped names no entry used (two of them created by the missing commas) and twelve live franchises unmapped, so **13 shipped entries** fell through to `_DEFAULT_CATEGORY` and were unreachable under their own `random_scope` category. The map is a hand-maintained mirror of the roster's `franchise` strings and nothing checked it. `tests/validate_data.py` now gates it **bidirectionally**, reading the source with `ast` so a maintainer's private `user_options.json` cannot fail it.
- **Deep docs:** `docs/architecture.md` (deep reference — read before engine or data changes), `docs/usage.md`, `docs/cosplayer-notes.md`, `docs/creature-notes.md`, `docs/suggested-additions.md` (backlog), `docs/reference/*.md` (generated).

## Architecture in 60 seconds

- **Data-driven constraint engine.** `data/` modules define cosplayers, creatures, templates, and constraints. `nodes/identity_forge.py` is the engine that resolves dropdowns into coherent natural-language prose + structured JSON.
- **Preset layer nodes.** Optional nodes stack in front of Identity Forge: Archetype (themed looks), Creature (animal/monster/alien), Modifier (field tweaks), Cosplayer (fictional character costumes with canon-checked visual descriptions).
- **ComfyUI frontend extensions.** `js/` modules provide searchable dropdown widgets, live preview, the vault (save/load characters), and a searchable roster picker modal.
- **Generated reference docs.** `docs/reference/*.md` are regenerated from data by `scripts/generate_reference_docs.py` — commit them after data changes.
- **Gallery on `gh-pages`.** Sample renders live on the `gh-pages` branch only; `gallery/.gitignore` blocks images from `main`.

## Layout

| Directory | Purpose |
|-----------|---------|
| `data/` | Cosplayers, creatures, templates, constraints, fields, user options |
| `nodes/` | Engine + main node, cosplayer/creature/archetype/modifier nodes, vault save/load |
| `js/` | ComfyUI frontend extensions (widgets, preview, vault UI, cosplayer franchise filter) |
| `tests/` | Data validation, engine/creature/vault/gallery tests, a `comfy_api` stub (`comfy_stub/`) so node classes define outside ComfyUI, and a jsdom frontend suite (`frontend/`) |
| `scripts/` | Reference doc generator, JS data sync generator, frontend schema fixture generator, release stamper, gallery renderer + hash gate |
| `docs/` | Usage, architecture (deep reference), cosplayer/creature notes |
| `gallery/` | Sample render manifests and build scripts (images on `gh-pages` only) |

## Build / test / run

```bash
# Validate data integrity
python tests/validate_data.py

# Run all tests. THIS is the command and the CI gate: -t . makes `tests` a real
# subpackage, which is what guarantees tests/__init__.py registers the comfy_api
# stub before any test imports a node module.
python -m unittest discover -s tests -t . -v

# `pytest tests` also works as of 1.2.0 (rootdir conftest.py + a ComfyExtension
# export on the stub) and is a convenience, not the gate.

# Scan tracked markdown for categorical leaks (paths, private IPs, secrets).
# NOT the maintainer's denylist checker, which lives outside this repo.
python scripts/check_public_safety.py

# Frontend jsdom suite (separate toolchain: npm ci once, then this)
npm run test:frontend

# Regenerate reference docs after data changes
python scripts/generate_reference_docs.py

# Regenerate the JS data blocks (GROUP_ORDER/FIELD_TO_GROUP/GENDER_POOLS in
# identity_forge.js, COSPLAYER_FRANCHISES in identity_forge_cosplayer.js)
python scripts/generate_js_data.py

# Regenerate the frontend test fixture after a node schema change
python scripts/dump_frontend_fixtures.py

# Stamp new roster entries with the current release (galleries sort by it)
python scripts/stamp_versions.py --stamp

# Check reference docs / JS data / frontend fixture / release stamps (CI/pre-commit)
python scripts/generate_reference_docs.py --check
python scripts/generate_js_data.py --check
python scripts/dump_frontend_fixtures.py --check
python scripts/stamp_versions.py --check

# Check every roster entry's gallery image matches its current text (CI).
# Network-free. Rendering the ones it reports needs a running ComfyUI:
#   python scripts/render_gallery.py --missing --save-originals --publish
python scripts/render_gallery.py --check
```

## Conventions & gotchas

- Zero dependencies. Python ≥3.10. No pip installs required — pack drops into ComfyUI's `custom_nodes/`.
- Working principles (from `docs/architecture.md`): no bloat, no duplication, docs stay accurate, tooltips stay current, curate don't hoard.
- After data changes: run `python scripts/generate_reference_docs.py` and commit the refreshed `docs/reference/*.md`.
- After adding a roster entry: also run `python scripts/stamp_versions.py --stamp` and commit `data/versions.py`. An unstamped entry sorts as though it had always shipped, and CI rejects it.
- **Never read the data layer by importing it in a build script.** Importing runs `apply_user_*` at the bottom of each data module, which merges the maintainer's local `user_options.json` — an import-based generator bakes private entries into a committed, published file. `scripts/generate_js_data.py` and `scripts/stamp_versions.py` both parse the source with `ast` instead.
- The data modules are large — always grep existing keys before adding a character/creature/archetype.
- Test fake keys in secret-scan must be realistic but contain "EXAMPLE" to hit the allowlist.
- Gallery images live ONLY on `gh-pages`; the manifest is rebuilt from published files (never deletes).
- Always run tests with `-t .` (`unittest discover -s tests -t . -v`). Without it, `tests/__init__.py` — which registers the `comfy_api` stub before any node module can import it — never runs first, and node-class-dependent tests silently behave as if ComfyUI were unavailable.
- After a node schema change (`define_schema()` in `nodes/*.py`): also run `python scripts/dump_frontend_fixtures.py` and commit the refreshed `tests/frontend/fixtures/nodes.json`. **Run it with plain `python`, never with a real ComfyUI on `sys.path`** — `IdentityForgeVaultLoad` would then list your own saved characters and commit them. The script refuses to run in that case; see architecture.md → the release-stamp/generator traps.

## Security

This file is **public-safe by default**. Never add local paths, credentials, personal data, infrastructure details, or subscription info.

Before pushing: run the maintainer's AGENTS.md denylist checker (kept outside this repo,
not a tracked file here) against `AGENTS.md` and `CLAUDE.md` — it must exit 0.

Deep design rationale, working principles, and data schemas: `docs/architecture.md`.

## Maintenance

**Update rule:** When you change the architecture, build/test commands, or conventions, update this AGENTS.md in the same commit. Keep under 200 lines. Link to `docs/architecture.md` for detail.

**CLAUDE.md:** One-line shim: `@AGENTS.md`.

**New-repo rule:** Create AGENTS.md in the first session a new repo is worked on.

**No-overlap rule:** Explanatory prose lives in one file. AGENTS.md = agent-facing summary; `docs/architecture.md` = deep reference. Identical build/test commands may be restated verbatim. Explanatory prose must not be duplicated — link instead.
