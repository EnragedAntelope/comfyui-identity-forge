# AGENTS.md — comfyui-identity-forge

A character creator and person generator for ComfyUI. Builds coherent, seed-reproducible people from dropdown menus with a constraint engine that prevents clashing traits. Zero dependencies, fully offline — no LLM, no API keys. Built on ComfyUI V3 API (`comfy_api.latest`), category: `conditioning/character`.

**Docs: `docs/architecture.md` (deep reference: working principles, data schemas, conventions,
gotchas cheat-sheet — read before engine/data changes) and `docs/history.md` (per-release
investigation notes, 1.5.0+ — the reasoning for every item in the release list below)**

## Current state

_Last verified: 2026-10-20 (2.0.0)_

- **Status:** in active development; main is v2.0.0 (`pyproject.toml`), the seed-epoch release: every seed resolves differently from 1.x, by design. Published to the Comfy Registry via `.github/workflows/publish_action.yml`, which fires on a `pyproject.toml` version change on `main` - bump the version on every functional commit or the release never ships. CI (`.github/workflows/ci.yml`) is deliberately dependency-free, has a Windows leg, and `publish-node` needs it (1.8.0).
- **Works:** the constraint engine resolving dropdowns into coherent prose plus structured JSON, seed-reproducible; the four preset layer nodes (Archetype, Creature, Modifier, Cosplayer); searchable dropdown widgets, live preview, the `franchise_filter`, the `random_pool` scope-composing filter, and the save/load vault in `js/` (an atomic overwrite, a disk-change-aware cache fingerprint, and Windows-reserved-name handling as of 1.5.5); a searchable **in-node roster picker** (`js/identity_forge_picker.js`) on the Cosplayer/Archetype/Creature nodes — trait facets, cross-tab search, opt-in gallery thumbnails, backed by a generated `js/identity_forge_roster.json` search index; Stylebook interop, the composition axis, and the **Turnaround** reference-set node (which emits every camera view of one resolved character as a list, so one queue renders the set) and its face-side sibling the **Expression Sheet** (1.10.0: one view per curated expression/mood/smile triple); a free-text `held_item` on the Modifier node; a jsdom frontend suite alongside the Python one; generated reference docs and JS data, and a committed field-marginals baseline (`scripts/sweep_marginals.py`, 1.5.5 — catches a value drawing far more or less often than intended), plus a reachability gate (`--unreachable`, 1.8.0: every pool value some gender can draw, or a reasoned exception in `tests/fixtures/unreachable_by_design.json`), all with `--check` modes wired into the gate. A cosplay entry may render as a **person in a costume**, as a **mascot suit** (`covers_face` + `covers_body` + `mask`), or — since 0.95.0 — as the **beast itself** (`body_plan: "feral"`, which emits the Creature node's Species & Anatomy payload instead of a costume); see architecture.md → "Animal characters split four ways". `scripts/render_gallery.py` renders a roster entry's gallery image by driving a running ComfyUI over HTTP and publishes it to `gh-pages`, and `gallery/render_manifest.json` + `--check` fail CI when an entry's text changes without a re-render (architecture.md → "The gallery render pipeline"). Since 0.97.0 every roster entry also carries a **release stamp** (`data/versions.py`, written by `scripts/stamp_versions.py`, gated in CI), which is what lets the three sample gallery pages offer **A–Z / Newest first** and a **New in `<version>`** filter. Since 2.0.0: a **`gaze`** field drawn last with `pose` (both with live constraint rules; architecture.md -> "pose and gaze draw last"), opt-in **`costume_back`** for Turnaround back views, **per-garment `{slot}` variation** in the outfit corpus on its own seed stream, and a gallery hash over **resolved prose** so an engine change marks images stale.
- **In progress:** roster and coherence curation is the ongoing work, not a milestone - each release adds characters/creatures/archetypes and closes coherence bugs found by rendering them. `docs/suggested-additions.md` is the live backlog (under consideration / decided against / still to consider). Next: more `costume_back` entries (start with caped or back-emblem heroes) and more slotted corpus phrases; both are seed-safe additions now (a slot draws from its own stream; a back text touches only back views).
- **Recent releases** — one line each. **This list is a pointer, not a changelog:** the reasoning for every item is in `docs/history.md` (the sections are named there per release) and the full messages are in `git log`. Keep roughly the last eight and let older ones drop off; do not let an entry grow into a paragraph.
  - **2.0.0** - Seed epoch: a `gaze` field (the old `looking` poses) drawn last with a deferred `pose` (`_repair_pose` retired), women's hair-length and 75/80 age weights, a portrait rig gated out of everyday interiors (`studio_shape` / `studio_mood` split), per-garment `{slot}` variation, opt-in `costume_back` for Turnaround back views, no "Name (Name)" label, an article for noun expressions, and a prose-based gallery hash (existing tiles accepted with `--rehash`, no full re-render). See docs/history.md -> "2.0.0".
  - **1.11.0** - Roster release: new cosplayers (incl. Birdie, Vecna on the mascot route), retro archetypes (Carhop at a new drive-in location, Zoot Suit men's only), four creatures, a `_GALLERY_SHOT` framing pin, Lola Bunny's paws, Tellarite's canon text (snout still unrendered). Random characters move only through the new location (about 5% of seeds, those drawing an urban outdoor place). Corinthian, Feyd-Rautha, barreleye, vampire squid and the pachuca variant declined on the render bar. See docs/history.md -> "1.11.0".
  - **1.10.0** - Expression Sheet node, free-text `held_item` on the Modifier, legwear dropped from prose in leg-cropping shots, "a coat of fur" no longer read as a pocketed garment, an overload drift test, and a gallery gate that fails on rendered-but-unpublished images (`--publish-pending`). Random characters unchanged; Bartok (now feral), Lola Bunny and Tasmanian Devil repaired and re-rendered (Tellarite deferred to 1.11.0). See docs/history.md -> "1.10.0".
  - **1.9.0** - Sandman and independent-comics curation, Savage Dragon likeness repair, a Morris Dancer archetype, deployment-only gallery manifests, and accurate engine/preset typing. See docs/history.md -> "1.9.0".
  - **1.8.0** — Picker trait facets read structured `traits` (Poison Ivy is no longer "Tiny"); ethnicity and skin tone lock only in Full character / Full preset; a seventh `subject_text` output (person and outfit, no scene); colour and pattern modifiers reach a generated outfit; widgets_values saved in schema order for headless tools; `--unreachable` gate; publish depends on CI with a Windows leg; new cosplayers (incl. The Invisibles), three archetypes and a stegosaurus; the duplicate Julia Carpenter entry folded into one. See docs/history.md → "1.8.0".
  - **1.7.0** — Engine and UX fixes from the 1.6.0 review: "Roll + lock all" locks one engine roll (a new read-only `POST /identity_forge/roll` route) instead of uniform per-dropdown picks; a framing that crops the feet no longer names the shoes in the prose (the JSON keeps them); hair styles and noun lengths are voiced as prose, not a tag list; a footwear or legwear modifier now reaches a generated outfit; the Modifier help example decorates single fields; `generate_character` is keyword-only from `widget_locked`. See docs/history.md → "1.7.0".
  - **1.6.0** — Content only, mined from third-party wildcard packs: weather as two `lighting` families (rain/drizzle/fog, falling snow) gated outdoors and by season; a `troubled` expression family for the heavy mood; social hand gestures; mohawk, faux hawk and three braid styles; new hair colours and highlights (skunk stripe weighted rare); new outfit-corpus entries weighted to the thin menswear/unisex cells, pyjamas under `loungewear`; new archetypes (Wedding Groom, Lehenga & Sherwani, Yukata, Hanfu, Kebaya, Metalhead and others) and alternate bridal gowns; three cultural archetypes no longer pin a pale skin tone in Full preset. Engine/UX findings are queued for 1.7.0. See docs/history.md → "1.6.0".
  - **1.5.5** — Audit pass: `vitiligo patches`, three golden `eye_color` values and two tattoo placements were drawing far more than their peers (flat weight against a visually louder or near-always-survivable value) — weighted down; a buzz cut no longer draws "wet look" (the `loose_natural` family split so the exclusion drops a whole unit instead of a partial cull). A committed marginals sweep (`scripts/sweep_marginals.py --check`) joined the CI gate so a future weight/pool change that moves a share unintentionally is caught automatically. Vault hardening: an atomic overwrite (the old save survives a write failure), a disk-change-aware cache fingerprint on Vault Load, Windows-reserved-name handling, and several crash-on-malformed-entry fixes. `docs/history.md` split out of `docs/architecture.md` (the 1.5.0–1.5.4 sections, about half that file). See docs/history.md → "1.5.5".
- **Known gaps / next steps:** two deliberate, open items — not to be re-litigated without a fresh case (the old pockets-allowlist gap was measured and closed in 1.10.0): (1) the Turnaround node's back view still draws a costume's front-facing detail (e.g. a chest emblem) on the back for any entry without a `costume_back` (opt-in since 2.0.0, so far only a handful of flagship heroes); never parse the front text for back clauses (the regex-over-prose trap), add `costume_back` to the entry instead. (2) Costume text that asserts a body trait against an unpinned random field (e.g. "on a hulking frame" beside a random, unlocked `build`) — the `signature`/`physique` split that causes it is deliberate; measure again from scratch before touching it, a naive regex sweep has reported a wrong count here before. `docs/suggested-additions.md` is the live backlog for roster/field-option candidates.
- **Deep docs:** `docs/architecture.md` (deep reference — read before engine or data changes), `docs/history.md` (per-release investigation notes, 1.5.0+), `docs/usage.md`, `docs/cosplayer-notes.md`, `docs/creature-notes.md`, `docs/suggested-additions.md` (backlog), `docs/reference/*.md` (generated).

## Architecture in 60 seconds

- **Data-driven constraint engine.** `data/` modules define cosplayers, creatures, templates, and constraints. `nodes/identity_forge.py` is the engine that resolves dropdowns into coherent natural-language prose + structured JSON.
- **Preset layer nodes.** Optional nodes stack in front of Identity Forge: Archetype (themed looks), Creature (animal/monster/alien), Modifier (field tweaks), Cosplayer (fictional character costumes with canon-checked visual descriptions).
- **ComfyUI frontend extensions.** `js/` modules provide searchable dropdown widgets, live preview, the vault (save/load characters), and a searchable roster picker modal.
- **Generated reference docs.** `docs/reference/*.md` are regenerated from data by `scripts/generate_reference_docs.py` — commit them after data changes.
- **Gallery on `gh-pages`.** Sample renders and deployment manifests live on `gh-pages`; `gallery/.gitignore` keeps them off `main`. See `gallery/README.md` for local previews.

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

# Every pool value no gender can draw must be a listed exception (1.8.0)
python scripts/sweep_marginals.py --unreachable

# Check every roster entry's gallery image matches its current text (CI).
# Network-free. Rendering the ones it reports needs a running ComfyUI:
#   python scripts/render_gallery.py --missing --save-originals --publish
# It also fails on an image rendered but never published (1.10.0); fix with:
#   python scripts/render_gallery.py --publish-pending
# A deliberate prose-only change across the roster (2.0.0) is accepted, without
# re-rendering, by: python scripts/render_gallery.py --rehash
python scripts/render_gallery.py --check
```

## Conventions & gotchas

- Zero dependencies. Python ≥3.10. No pip installs required — pack drops into ComfyUI's `custom_nodes/`.
- Working principles (from `docs/architecture.md`): no bloat, no duplication, docs stay accurate, tooltips stay current, curate don't hoard.
- **Coherence checklist — run it BEFORE shipping any new value, phrase or rule** (each line is a class the maintainer found in renders; details in docs/history.md → "Round 2" / "Round 4"):
  1. *Hidden items get exposed.* Anything named must be visible in the finished garment (tattoo placement, legwear, belts, suspenders, body jewellery, necklace under a tie) — check it in `_fit_extras_to_garment` / `_visible_tattoo_placements` / `_wearable_legwear`, never before the outfit exists.
  2. *One named colour spreads to the whole outfit.* A garment phrase with several pieces must let `_colour_the_rest` colour the others; sets and suits stay matched; a pattern goes on the lead garment only, never on a set.
  3. *Men's defaults must read masculine.* New jewellery/hair/accessory values get a masculine trim or plain wording (`_MASCULINE_EXCLUDED_VALUES`, `_MASCULINE_JEWELRY_CLAUSES`); a man's single long braid, hoops, a thin headband and a neck scarf all rendered feminine.
  4. *Every value needs a place, a season, an age, a style and a body it fits* — gate it (style/place/season/age tables in `data/constraints.py`), and keep culls whole-family.
  5. *Framing vs pose, expression vs mood, look vs makeup detail* must agree.
  6. **Measure, don't eyeball:** `RoundFourQaTests` (incl. the final-state invariant: no unlocked field holds a value a live rule excludes), plus a before/after sweep of every field's marginals over a few thousand seeds per gender (no share moves you did not intend, nothing newly unreachable), then render the maintainer's flagged seeds again.
- After data changes: run `python scripts/generate_reference_docs.py` and commit the refreshed `docs/reference/*.md`.
- After adding a roster entry: also run `python scripts/stamp_versions.py --stamp` and commit `data/versions.py`. An unstamped entry sorts as though it had always shipped, and CI rejects it.
- **Release tags.** After a release PR merges, tag the merge commit (`git tag -a vX.Y.Z <sha> -m "X.Y.Z"`) and push that tag **by name** (`git push origin vX.Y.Z`). Never `git push --tags` — local-only backup tags exist and must not be published. Tags are for humans (compare links, `git checkout vX.Y.Z`); the Registry publish is driven by the `pyproject.toml` version, not by tags. First tags: `v1.2.0`, `v1.3.0`, `v1.4.0`.
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
