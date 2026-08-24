# AGENTS.md — comfyui-identity-forge

A character creator and person generator for ComfyUI. Builds coherent, seed-reproducible people from dropdown menus with a constraint engine that prevents clashing traits. Zero dependencies, fully offline — no LLM, no API keys. Built on ComfyUI V3 API (`comfy_api.latest`), category: `conditioning/character`.

**Docs: `docs/architecture.md` (deep reference — read it before engine/data changes)**

## Current state

_Last verified: 2026-08-24 (0.98.0)_

- **Status:** in active development, released at v0.98.0 (`pyproject.toml`). Published to the Comfy Registry via `.github/workflows/publish_action.yml`, which fires on a `pyproject.toml` version change on `main` — bump the version on every functional commit or the release never ships. CI (`.github/workflows/ci.yml`) is deliberately dependency-free.
- **Works:** the constraint engine resolving dropdowns into coherent prose plus structured JSON, seed-reproducible; the four preset layer nodes (Archetype, Creature, Modifier, Cosplayer); searchable dropdown widgets, live preview, the `franchise_filter`, and the save/load vault in `js/`; Stylebook interop, the composition axis, and the **Turnaround** reference-set node; a jsdom frontend suite alongside the Python one; generated reference docs and JS data with `--check` modes wired into the gate. A cosplay entry may render as a **person in a costume**, as a **mascot suit** (`covers_face` + `covers_body` + `mask`), or — since 0.95.0 — as the **beast itself** (`body_plan: "feral"`, which emits the Creature node's Species & Anatomy payload instead of a costume); see architecture.md → "Animal characters split four ways". `scripts/render_gallery.py` renders a roster entry's gallery image by driving a running ComfyUI over HTTP and publishes it to `gh-pages`, and `gallery/render_manifest.json` + `--check` fail CI when an entry's text changes without a re-render (architecture.md → "The gallery render pipeline"). Since 0.97.0 every roster entry also carries a **release stamp** (`data/versions.py`, written by `scripts/stamp_versions.py`, gated in CI), which is what lets the three sample gallery pages offer **A–Z / Newest first** and a **New in `<version>`** filter.
- **In progress:** roster and coherence curation is the ongoing work, not a milestone — each release adds characters/creatures/archetypes and closes coherence bugs found by rendering them. `docs/suggested-additions.md` is the live backlog (under consideration / decided against / still to consider).
- **Recent releases** — one line each. **This list is a pointer, not a changelog:** the reasoning for every item is in `docs/architecture.md` (the sections are named there per release) and the full messages are in `git log`. Keep roughly the last eight and let older ones drop off; do not let an entry grow into a paragraph.
  - **0.98.0** — 8 cosplayers (`Amara`, unblocked from the 0.97.0 decline by `anatomy_note`'s six-arm case; the core `Looney Tunes` cast `Porky Pig`, `Sylvester`, `Tweety`, `Wile E. Coyote`, `Road Runner`, `Foghorn Leghorn`, `Speedy Gonzales` — that franchise to 14). Three render-review rewrites: `Greez Dritus` onto the Dexter mask pattern (his published render had come back two-armed), `Grogu` to the mascot treatment, mosquito proboscis re-led with body-relative scale. New **Turnaround** node — one seed-fixed identity, N auto-indexed camera views for reference sheets. Gallery: shots pinned front-facing (the pin initially shipped dead to a duplicate execute), re-renders now overwrite via a staging dir, favicons on all three sample pages. See architecture.md → "Front-facing shots and overwrite publishing".
  - **0.97.0** — 9 cosplayers (`Mizora`; `Zer0` + `Sir Hammerlock`; `The Invisible Man`; `Ash Williams`; `Immortan Joe`; `Mega Man`; `Sherlock Holmes`; `The Knight (Hollow Knight)`) across four new franchises, which takes **Universal Monsters to 8 and therefore adds a `Franchise: Universal Monsters` random_scope option**. Five engine changes, three of them long-open and all measured: the bare-adjective `height` now leads the phrase instead of trailing it (**CLOSED**, open since 0.84.0); `composition` joins the giant/tiny scale gate (**CLOSED**); a species `hands` slot suppresses the human `nails` field (**CLOSED**); `anatomy_note` gives a maskless entry the early body sentence the 0.96.0 limb fix needed (**CLOSED**, applied to the four multi-armed entries); and **`bag` gained the masculine trim it never had — 13.7% of default male renders were carrying a handbag**, measured over 1000 seeds. Field options: `mary janes`, `cowboy boots`, `argyle` (which repriced the whole patterned set to hold plain at 2/10), `split dye`, `stretched lobes`, three men's bags. Gallery: sort + "New in" filter, and two dead controls fixed. Frontend: re-entry guards on the four setups that lacked one, and four vault/creature audit findings. See architecture.md → the five 0.97.0 sections.
  - **0.96.0** — 3 cosplayers (Minthara, Captain Mizuki, The Martyr) and a new `The Citadel` franchise; 11 archetypes (Tuareg, Maasai, Sami Gakti, Ukrainian Vyshyvanka, Mongolian Deel, Korean Hanbok, Vietnamese Ao Dai, Visual Kei, Cybergoth, Rude Boy, Teddy Boy); Marika and Ragyo refined; arm counts stated as numerals on the four multi-armed entries that hid them behind arithmetic or a trailing list item; Desert Nomad's tagelmust alternate retired into the new Tuareg entry; `creature_class` now required on a feral entry. Two render-review findings closed: **nine negated clauses across six feral entries** (`Falkor` "with no wings at all" drew wings) rewritten as positive statements, and **limb counts moved out of the costume sentence** — see architecture.md → "Limb and part counts: position beats repetition" and "Never negate in prompt data".
  - **0.95.0** — `body_plan: "feral"` on the Cosplayer node, 22 named beasts + 6 retrofits, and three engine fixes (shell drops `tattoos`, `QUADRUPED_UNPERFORMABLE_POSES`, species vault round-trip).
  - **0.94.0** — 6 insect creatures (Diptera, Hemiptera, and the first larval body plans).
  - **0.93.0** — 10 creatures sifted from a ~600-name animal list, on an *anatomy, not species* bar.
  - **0.92.0** — five audit fixes: the contrapositive constraint deadlock, `_meta` leaks across chained presets, variant override precedence, a self-describing `prompt_json`, and the pose garment gate.
  - **0.91.1** — hair-scope cleanup; `natural_hair_colors` pinned by the validator (the filter fails OPEN without it).
- **Known gaps / next steps:** **~308 masked entries still carry gallery images rendered from the pre-0.90.0 buried-mask prose** — deliberately not re-rendered (maintainer call), and `--check` cannot flag them because the change was prose-only. **`pytest` does not work here** — it imports `comfy_api` before the stub can register, so use `python -m unittest discover -s tests -t . -v` (the `-t .` is load-bearing); gallery images live only on `gh-pages`, so a `main`-only checkout cannot preview them; **editing an entry's text while ComfyUI is off turns CI red** until `render_gallery.py` re-renders it — that is the gate working as intended. **The render gate is currently GREEN** (cosplay 1869 / archetypes 249 / creatures 249, all rendered and published). `docs/suggested-additions.md` "Under consideration" holds three `hair_style` values (`hime cut`, `wolf cut`, `victory rolls`) blocked on family-weight arithmetic, not taste; "Decided against" is not to be re-litigated, and it gained a **"Field options — declined"** table at 0.97.0 (chiefly: no `ethnicity` additions — they are not visually distinguishable in a render *and* would take Europe from ~30% to ~35% of a flat field). **Three of the four measured open questions were closed at 0.97.0** — the `composition` scale gate, the `hands`→`nails` suppression, and the four multi-armed maskless entries (via `anatomy_note`) — at the cost that was priced when they were deferred: the published images for the affected entries are no longer literal reproductions of current output, and `--check` cannot see prose-only drift. **Two remain open, both deliberate:** (1) `_POCKETLESS_GARMENT_RE` is an allowlist, so a pocketless costume it does not name still draws a pockets gesture; (2) **costume text that asserts a body trait against an unpinned random field** ("on a hulking frame" beside "a very slim build") — 33 entries, and the `signature`/`physique` split that causes it is *deliberate*; **if it is ever taken up, measure it again from scratch — the naive regex reported 171 and was wrong.**
- **Deep docs:** `docs/architecture.md` (deep reference — read before engine or data changes), `docs/usage.md`, `docs/cosplayer-notes.md`, `docs/creature-notes.md`, `docs/suggested-additions.md` (backlog), `docs/reference/*.md` (generated).

## Architecture in 60 seconds

- **Data-driven constraint engine.** `data/` modules define cosplayers, creatures, templates, and constraints. `nodes/identity_forge.py` is the engine that resolves dropdowns into coherent natural-language prose + structured JSON.
- **Preset layer nodes.** Optional nodes stack in front of Identity Forge: Archetype (themed looks), Creature (animal/monster/alien), Modifier (field tweaks), Cosplayer (fictional character costumes with canon-checked visual descriptions).
- **ComfyUI frontend extensions.** `js/` modules provide searchable dropdown widgets, live preview, and the vault (save/load characters).
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

# Run all tests (pytest does NOT work here -- it imports comfy_api before the
# stub in tests/__init__.py can register; -t . is required, see Conventions)
python -m unittest discover -s tests -t . -v

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
- After a node schema change (`define_schema()` in `nodes/*.py`): also run `python scripts/dump_frontend_fixtures.py` and commit the refreshed `tests/frontend/fixtures/nodes.json`.

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
