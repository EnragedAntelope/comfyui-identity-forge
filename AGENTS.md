# AGENTS.md — comfyui-identity-forge

A character creator and person generator for ComfyUI. Builds coherent, seed-reproducible people from dropdown menus with a constraint engine that prevents clashing traits. Zero dependencies, fully offline — no LLM, no API keys. Built on ComfyUI V3 API (`comfy_api.latest`), category: `conditioning/character`.

**Docs: `docs/architecture.md` (deep reference — read it before engine/data changes)**

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
| `js/` | ComfyUI frontend extensions (widgets, preview, vault UI) |
| `tests/` | Data validation, engine/creature/vault/gallery tests, a `comfy_api` stub (`comfy_stub/`) so node classes define outside ComfyUI, and a jsdom frontend suite (`frontend/`) |
| `scripts/` | Reference doc generator, JS data sync generator, frontend schema fixture generator |
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

# Regenerate JS data block (GROUP_ORDER/FIELD_TO_GROUP/GENDER_POOLS)
python scripts/generate_js_data.py

# Regenerate the frontend test fixture after a node schema change
python scripts/dump_frontend_fixtures.py

# Check reference docs / JS data / frontend fixture are in sync (CI/pre-commit)
python scripts/generate_reference_docs.py --check
python scripts/generate_js_data.py --check
python scripts/dump_frontend_fixtures.py --check
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
