# AGENTS.md — comfyui-identity-forge

A character creator and person generator for ComfyUI. Builds coherent, seed-reproducible people from dropdown menus with a constraint engine that prevents clashing traits. Zero dependencies, fully offline — no LLM, no API keys. Built on ComfyUI V3 API (`comfy_api.latest`), category: `conditioning/character`.

**Docs: `docs/architecture.md` (deep reference — read it before engine/data changes)**

## Current state

_Last verified: 2026-08-17 (0.91.1)_

- **Status:** in active development, released at v0.90.1 (`pyproject.toml`). Published to the Comfy Registry via `.github/workflows/publish_action.yml`, which fires on a `pyproject.toml` version change on `main` — bump the version on every functional commit or the release never ships. CI (`.github/workflows/ci.yml`) is deliberately dependency-free.
- **Works:** the constraint engine resolving dropdowns into coherent prose plus structured JSON, seed-reproducible; the four preset layer nodes (Archetype, Creature, Modifier, Cosplayer); searchable dropdown widgets, live preview and the save/load vault in `js/`; Stylebook interop and the composition axis; a jsdom frontend suite alongside the Python one; generated reference docs and JS data with `--check` modes wired into the gate. `scripts/render_gallery.py` renders a roster entry's gallery image by driving a running ComfyUI over HTTP and publishes it, and `gallery/render_manifest.json` + `--check` fail CI when an entry's text changes without a re-render (see architecture.md → "The gallery render pipeline"). **New at 0.88.0:** 46 cosplayer entries across 13 new franchises (Guilty Gear, Team Fortress 2, Warhammer 40,000, Castlevania, Encanto, Fallout, Hellsing, Inuyasha, Ranma 1/2, Yu Yu Hakusho, Back to the Future, The Big Lebowski, plus Persona consolidated from `Persona 5`), and two new `random_scope` franchise options (Guilty Gear, Persona). Also fixes the cosplay label stutter that 0.77.0's exact-match guard missed on seven disambiguated keys (`Joker (Persona 5) (Persona)`, both `Ms. Marvel` variants, …). **New at 0.89.0:** a `franchise_filter` on the Cosplayer node that narrows the ~1,800-name character dropdown by franchise — a `serialize: false` view-only widget added in `js/identity_forge_cosplayer.js`. **That widget was believed non-breaking and was not** — `serialize: false` is honoured when *writing* `widgets_values` and ignored when *reading* it back, so pre-0.89.0 Cosplayer nodes reloaded with every widget after `character` shifted one slot, and had to be recreated by hand. Repaired at 0.90.0 by the same `configure` wrapper the main node uses. **New at 0.90.0:** two new randomizable axes — a `tattoos` cascade (`tattoos` + `tattoo_placement`, Body group) and `legwear` (Clothing group) — plus 14 cosplayers (Fallout ×3 incl. The Ghoul, Game of Thrones ×5, and Dark Magician/Dark Magician Girl, Nurse (Silent Hill), Splicer, Samus Aran (Power Suit), Eleven), one new franchise (`Stranger Things`), six `clothing_pattern` values, three eyeglass frames in `accessories`, and two `bangs` variants. Both new fields are **appended at the end of `FIELD_DEFINITIONS` on purpose** so `widgets_values` stays positional-compatible with pre-0.90.0 saved workflows (verified against a live pre-0.90.0 instance: its 74 widgets keep their exact indices) while `FIELD_TO_GROUP` still places them in the right UI section — see architecture.md → "Adding a field without breaking saved workflows". Also 25 creatures (209 → 233) and 7 archetypes (231 → 238, incl. Matador, Sumo Wrestler, Buddhist Monk, Andean Cholita). **A masked character's head is now voiced as its own sentence ahead of the clothing** (`_MASK_KEY`): it used to be comma-appended to the costume, arriving as the last item of a "He wears …" garment list, and t2i models rendered the garments and ignored the head — six entries were reported that way from one render review. 316 entries carry a mask, so their prose changed; `entry_hash` covers the entry dict rather than the prose, so `--check` cannot see it and only the re-rendered ones are current (see architecture.md → "Gating a field on what the clothes actually show" and the note on `_MASK_KEY`). Also: the cosplay key `Joker (Persona 5)` → `Joker (Persona)` with a `validate_data.py` rule forbidding a parenthetical that names something narrower than its franchise; likeness rewrites for `Dexter Jettster`, `Figrin D'an`, `Ithorian`, `Kilowog` and `Larfleeze` (all were rendering a randomized **human** face or build over an alien); and an article fix so the lead sentence reads "an 18-year-old" / "an Armenian woman" rather than "a 18-year-old" / "A Armenian woman".
- **In progress:** roster and coherence curation is the ongoing work, not a milestone — each release adds characters/creatures/archetypes and closes coherence bugs found by rendering them. `docs/suggested-additions.md` is the live backlog (under consideration / decided against / still to consider).
- **New at 0.90.1:** two Joker (DC) variants (Heath Ledger and Joaquin Phoenix); glam makeup styles now require visible cosmetics on every axis; no-makeup now also excludes matte finish and dewy skin from skin_finish; hands_covered now includes glove accessories; bald prose path guards hair_style and hair_extra branches against locked leaks; removed dead legwear/tattoo_placement branches in _randomize_fields.
- **New at 0.91.0:** `Silk` (Cindy Moon, Marvel) joins the roster — `covers_hair` with the red hood and the gaiter over the lower face written into the costume (eyes and brow show, so NOT `covers_face`), plus her debut all-webbing look as an alternate. The `Joker` (DC) entry grows from 3 looks to 9: Batman (1989), The Killing Joke's carnival "tourist" (with the camera as its prop) and its Red Hood origin (the entry's only `covers_face` look, set per-costume), the Arkham games, Suicide Squad (2016) and Batman (1966) join the existing classic/Ledger/Phoenix looks. Also fixes `tests/preview_cosplayer.py`, which never forwarded `_MASK_KEY` to `generate_character` — every masked character previewed bare-headed while the real node was correct.
- **New at 0.91.1:** hair-scope cleanup after an audit flagged the Natural-only/Full-spectrum control as a no-op. **It is not** — measured through `IdentityForge.execute`, Natural only gives 0/200 fantasy shades and Full spectrum ~45%, in every gender. What was dead: a `full_spectrum_hair_colors` list on the `hair_color` field that nothing read (the full spectrum *is* the option pool), now deleted, and `_parse_archetype_json` copying `_meta.hair_color_scope` off a preset only for `execute`'s `_CONTROL_FIELDS` filter to drop it — control fields are widget-owned and it is deliberately not wired up (see architecture.md → "Control fields"). `validate_data.py` now pins `natural_hair_colors` (present, and a subset of the pool: the filter fails OPEN without it) and rejects a dead `*_hair_colors` lookalike. Also documents that a `user_options.json` hair colour is randomizable only under Full spectrum.
- **Known gaps / next steps:** **~308 masked entries still carry gallery images rendered from the pre-0.90.0 buried-mask prose** — deliberately not re-rendered (maintainer call), and `--check` cannot flag them because the change was prose-only. `docs/suggested-additions.md` "Under consideration" holds two `hair_style` values (`hime cut`, `wolf cut`) blocked on family-weight arithmetic, not taste — new candidates need a written case, and "Decided against" is not to be re-litigated; the one open question is "Still to consider" #1 (re-examining the roster's softest shipped entries). **`pytest` does not work here** — it imports `comfy_api` before the stub can register, so use `python -m unittest discover -s tests -t . -v` (the `-t .` is load-bearing); gallery images live only on `gh-pages`, so a `main`-only checkout cannot preview them; **editing an entry's text while ComfyUI is off turns CI red** until `render_gallery.py` re-renders it — that is the gate working as intended, not a bug.
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
| `scripts/` | Reference doc generator, JS data sync generator, frontend schema fixture generator, gallery renderer + hash gate |
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

# Check reference docs / JS data / frontend fixture are in sync (CI/pre-commit)
python scripts/generate_reference_docs.py --check
python scripts/generate_js_data.py --check
python scripts/dump_frontend_fixtures.py --check

# Check every roster entry's gallery image matches its current text (CI).
# Network-free. Rendering the ones it reports needs a running ComfyUI:
#   python scripts/render_gallery.py --missing --save-originals --publish
python scripts/render_gallery.py --check
```

## Conventions & gotchas

- Zero dependencies. Python ≥3.10. No pip installs required — pack drops into ComfyUI's `custom_nodes/`.
- Working principles (from `docs/architecture.md`): no bloat, no duplication, docs stay accurate, tooltips stay current, curate don't hoard.
- After data changes: run `python scripts/generate_reference_docs.py` and commit the refreshed `docs/reference/*.md`.
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
