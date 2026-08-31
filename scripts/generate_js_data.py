#!/usr/bin/env python
"""Generate the frontend data block embedded in ``js/identity_forge.js``.

``js/identity_forge.js`` needs three lookups that are *derived from* the Python
field definitions: ``GROUP_ORDER`` (widget group order), ``FIELD_TO_GROUP`` (which
group each widget belongs to) and ``GENDER_POOLS`` (the per-gender option lists the
UI swaps in when the gender toggle changes). Hand-transcribing them let the JS drift
from ``data/fields.py`` — the missing ``hair_length`` / ``hair_style`` pools were
exactly that. This script regenerates the block from ``data/fields.py`` so the two
can never disagree.

The block lives between two marker comments inside ``js/identity_forge.js`` (the
surrounding UI logic is hand-written and untouched):

    // >>> GENERATED DATA ... >>>
    const GROUP_ORDER = ...;
    const FIELD_TO_GROUP = ...;
    const GENDER_POOLS = ...;
    // <<< GENERATED DATA <<<

Usage (from the repo root)::

    python scripts/generate_js_data.py            # rewrite the block in place
    python scripts/generate_js_data.py --check    # fail if out of date (CI)

The option-list conventions mirror the node's ``define_schema`` widget builder:
each list is ``["Random", *visible options, "None"]`` and the ``Any`` pool is the
deduped union (female order first, male-only appended).
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.fields import FIELD_DEFINITIONS  # noqa: E402
from nodes.identity_forge import (  # noqa: E402
    _CONTROL_FIELDS, _GROUP_ORDER, _HIDDEN_FIELDS, _SPECIES_GROUP, _dedupe, _is_absent,
)

_JS_PATH = ROOT / "js" / "identity_forge.js"
_COSPLAYER_JS_PATH = ROOT / "js" / "identity_forge_cosplayer.js"
_ROSTER_JSON_PATH = ROOT / "js" / "identity_forge_roster.json"
_START = "// >>> GENERATED DATA"
_END = "// <<< GENERATED DATA <<<"
_HEADER = (
    "// >>> GENERATED DATA — do not edit by hand. "
    "Regenerate: python scripts/generate_js_data.py >>>"
)


def _is_widget_field(name: str) -> bool:
    """A field that gets a user-facing widget (so the frontend cares about it)."""
    return name not in _HIDDEN_FIELDS and name not in _CONTROL_FIELDS


def _visible(values) -> list[str]:
    """Options the widget shows — real values only (absence sentinels are hidden)."""
    return [v for v in values if not _is_absent(v)]


def _group_order() -> list[str]:
    """Widget group order: the engine's group order minus the non-widget species group."""
    return [g for g in _GROUP_ORDER if g != _SPECIES_GROUP]


def _field_to_group() -> dict[str, str]:
    return {
        name: meta["group"]
        for name, meta in FIELD_DEFINITIONS.items()
        if _is_widget_field(name)
    }


def _gender_pools() -> dict[str, dict[str, list[str]]]:
    pools: dict[str, dict[str, list[str]]] = {}
    for name, meta in FIELD_DEFINITIONS.items():
        if not _is_widget_field(name):
            continue
        female = meta.get("female_options")
        male = meta.get("male_options")
        if female is None or male is None or female == male:
            continue  # not gender-divergent — the UI never swaps it
        pools[name] = {
            "Female": ["Random", *_visible(female), "None"],
            "Male": ["Random", *_visible(male), "None"],
            "Any": ["Random", *_visible(_dedupe(list(female) + list(male))), "None"],
        }
    return pools


def render_block() -> str:
    """The full marker-delimited generated block (markers included)."""
    return "\n".join([
        _HEADER,
        f"const GROUP_ORDER = {json.dumps(_group_order())};",
        f"const FIELD_TO_GROUP = {json.dumps(_field_to_group(), indent=2)};",
        f"const GENDER_POOLS = {json.dumps(_gender_pools(), indent=2)};",
        _END,
    ])


def _builtin_cosplayer_franchises() -> dict[str, list[str]]:
    """``{franchise: [character names]}`` for the BUILT-IN roster only.

    Read by parsing the ``COSPLAYERS`` literal out of ``data/cosplayers.py`` with
    ``ast`` rather than importing it. That is deliberate and load-bearing: importing
    the module runs ``apply_user_cosplayers(COSPLAYERS)`` at the bottom of it, which
    merges the local ``user_options.json`` in place — so an import-based generator
    would bake a maintainer's private characters into a committed, published file.
    The AST sees only what is written in the source.

    User-added characters are therefore absent from this map, which is the right
    failure mode: the frontend treats an unknown name as unfiltered and always shows
    it, so a user entry can never be hidden by the filter.
    """
    source = (ROOT / "data" / "cosplayers.py").read_text(encoding="utf-8")
    by_franchise: dict[str, list[str]] = {}
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.AnnAssign)
                and getattr(node.target, "id", "") == "COSPLAYERS"):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            franchise = ""
            for entry_key, entry_value in zip(value.keys, value.values):
                if (isinstance(entry_key, ast.Constant) and entry_key.value == "franchise"
                        and isinstance(entry_value, ast.Constant)):
                    franchise = entry_value.value
            if franchise:
                by_franchise.setdefault(franchise, []).append(key.value)
    return {f: sorted(names) for f, names in sorted(by_franchise.items())}


def render_cosplayer_block() -> str:
    """The generated block for ``js/identity_forge_cosplayer.js``."""
    return "\n".join([
        _HEADER,
        "const COSPLAYER_FRANCHISES = "
        f"{json.dumps(_builtin_cosplayer_franchises(), indent=2, ensure_ascii=False)};",
        _END,
    ])


# --- js/identity_forge_roster.json: the picker modal's bulk search index -------
#
# A separate, later task builds the frontend search/picker modal
# (js/identity_forge_picker.js) that fetches this file lazily (mirroring how
# comfyui-stylebook's picker fetches stylebook_data.json rather than paying for a
# multi-hundred-KB corpus on every ComfyUI page load). This generator only produces
# the data side.
#
# Read via ``ast`` only, exactly like ``_builtin_cosplayer_franchises`` above and for
# the same reason: importing data/cosplayers.py, data/templates.py or
# data/creatures.py runs their ``apply_user_*`` merge at module bottom, which would
# bake a maintainer's private roster additions into this committed, published file.
# Every dataset in those three modules is built from plain literals (strings,
# numbers, lists, tuples, dicts, bools, None) with no function calls, so
# ``ast.literal_eval`` on the parsed assignment node reproduces the true committed
# data with no import and no merge.


def _module_literal(path: Path, name: str):
    """Return the literal value of the top-level ``name = ...`` in ``path``.

    ``name`` may be annotated (``NAME: T = {...}``) or plain (``NAME = {...}``).
    Raises if no such literal assignment exists — a silent empty-dict fallback
    would make a renamed source constant look like an empty (but valid) roster.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            target = names[0] if len(names) == 1 else None
        else:
            continue
        if target == name:
            return ast.literal_eval(node.value)
    raise ValueError(f"{name!r} not found as a top-level literal assignment in {path}")


def _cosplayer_franchise_categories() -> tuple[dict[str, str], str]:
    """``{franchise: broad category}`` plus the fallback, mirroring
    ``data.cosplayers.get_cosplayer_category`` without importing the module."""
    path = ROOT / "data" / "cosplayers.py"
    by_category = _module_literal(path, "_CATEGORY_FRANCHISES")
    default_category = _module_literal(path, "_DEFAULT_CATEGORY")
    franchise_categories = {
        franchise: category
        for category, franchises in by_category.items()
        for franchise in franchises
    }
    return franchise_categories, default_category


def _cosplayer_trait_words(entry: dict) -> list[str]:
    """Trait words derived from ``covers_face``/``covers_body``/``body_plan``/
    ``size_scale``, mirroring the ``_scope_is_*`` predicates in
    ``nodes/identity_forge_cosplayer.py`` (not imported — same reason as above;
    those predicates are pure and cheap enough to restate here)."""
    words: list[str] = []
    if entry.get("body_plan") == "feral":
        words += ["feral", "beast"]
    else:
        covers_face = bool(entry.get("covers_face"))
        covers_body = bool(entry.get("covers_body"))
        if covers_face:
            words.append("masked")
        if covers_face and covers_body:
            words.append("mascot")
    size_scale = entry.get("size_scale")
    if size_scale == "giant":
        words.append("giant")
    elif size_scale == "tiny":
        words.append("tiny")
    return words


def _cosplayer_roster_entry(
    name: str, entry: dict, franchise_categories: dict[str, str], default_category: str,
) -> dict:
    franchise = entry.get("franchise", "")
    gender = entry.get("gender", "")
    category = franchise_categories.get(franchise, default_category)
    haystack_parts = [name, franchise, category, gender, entry.get("costume", "")]
    mask = entry.get("mask")
    if mask:
        haystack_parts.append(mask)
    prop = entry.get("prop")
    if prop:
        haystack_parts.append(prop)
    for section in ("signature", "physique"):
        haystack_parts.extend(str(v) for v in entry.get(section, {}).values())
    haystack_parts.extend(_cosplayer_trait_words(entry))
    aliases = entry.get("aliases")
    if aliases:
        haystack_parts.extend(aliases)
    return {
        "kind": "cosplayer",
        "name": name,
        "franchise": franchise,
        "category": category,
        "gender": gender,
        "haystack": " ".join(haystack_parts).lower(),
    }


def _flatten_field_values(fields: dict) -> list[str]:
    """String-ify every value in an archetype field map, skipping ``variants``
    (the caller recurses into it separately). A value may be a plain string or a
    curated list of alternatives (``eye_color``, ``outfit_description``, ...)."""
    values: list[str] = []
    for key, value in fields.items():
        if key == "variants":
            continue
        if isinstance(value, list):
            values.extend(str(v) for v in value)
        else:
            values.append(str(value))
    return values


def _archetype_roster_entry(name: str, template: dict) -> dict:
    values = _flatten_field_values(template)
    for look in (template.get("variants") or {}).values():
        if isinstance(look, dict):
            values.extend(_flatten_field_values(look))
    entry = {
        "kind": "archetype",
        "name": name,
        "haystack": " ".join([name, *values]).lower(),
    }
    gender = template.get("gender")
    if gender:
        entry["gender"] = gender
    return entry


def _creature_roster_entry(name: str, entry: dict, slots: tuple[str, ...]) -> dict:
    creature_class = entry.get("class", "")
    haystack_parts = [name, creature_class]
    for slot in slots:
        text = entry.get(slot)
        if text:
            haystack_parts.append(text)
    return {
        "kind": "creature",
        "name": name,
        "category": creature_class,
        "haystack": " ".join(haystack_parts).lower(),
    }


def _roster_entries() -> list[dict]:
    """Every cosplayer, archetype and creature as one flat, ``kind``-tagged list.

    See the module-level comment above for why this reads the three data modules
    with ``ast`` rather than importing them.
    """
    cosplayers = _module_literal(ROOT / "data" / "cosplayers.py", "COSPLAYERS")
    franchise_categories, default_category = _cosplayer_franchise_categories()
    archetypes = _module_literal(ROOT / "data" / "templates.py", "ARCHETYPES")
    creatures = _module_literal(ROOT / "data" / "creatures.py", "CREATURES")
    creature_slots = _module_literal(ROOT / "data" / "creatures.py", "CREATURE_SLOTS")

    entries: list[dict] = []
    for name, entry in cosplayers.items():
        entries.append(_cosplayer_roster_entry(name, entry, franchise_categories, default_category))
    for name, template in archetypes.items():
        entries.append(_archetype_roster_entry(name, template))
    for name, entry in creatures.items():
        entries.append(_creature_roster_entry(name, entry, creature_slots))
    return entries


def render_roster_json() -> str:
    """The full ``js/identity_forge_roster.json`` contents (compact — this is a
    fetched bulk data file, not hand-read source)."""
    return json.dumps(_roster_entries(), ensure_ascii=False, sort_keys=True)


def _splice(source: str, block: str) -> str:
    """Replace the existing marker region in ``source`` with ``block``."""
    start = source.index(_START)
    end = source.index(_END, start) + len(_END)
    return source[:start] + block + source[end:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Verify the committed JS matches data/fields.py (exit 1 if stale).")
    args = parser.parse_args(argv)

    targets = (
        (_JS_PATH, render_block, "data/fields.py"),
        (_COSPLAYER_JS_PATH, render_cosplayer_block, "data/cosplayers.py"),
    )
    stale = False
    for path, render, origin in targets:
        source = path.read_text(encoding="utf-8")
        if _START not in source or _END not in source:
            print(f"ERROR: marker comments not found in {path.name}; "
                  f"expected a region delimited by {_START!r} … {_END!r}.")
            return 2

        updated = _splice(source, render())
        rel = path.relative_to(ROOT)
        if args.check:
            if updated != source:
                print(f"{rel} is STALE relative to {origin}.")
                print("Regenerate with: python scripts/generate_js_data.py")
                stale = True
            else:
                print(f"{rel} generated data is up to date.")
        elif updated != source:
            path.write_text(updated, encoding="utf-8")
            print(f"wrote {rel}")
        else:
            print(f"{rel} already up to date")

    # js/identity_forge_roster.json is a standalone generated file (not a marker
    # region spliced into hand-written JS), so it is compared/written directly.
    roster_json = render_roster_json()
    roster_rel = _ROSTER_JSON_PATH.relative_to(ROOT)
    existing_roster = (
        _ROSTER_JSON_PATH.read_text(encoding="utf-8") if _ROSTER_JSON_PATH.is_file() else None
    )
    if args.check:
        if existing_roster != roster_json:
            print(f"{roster_rel} is STALE relative to data/cosplayers.py, "
                  f"data/templates.py and data/creatures.py.")
            print("Regenerate with: python scripts/generate_js_data.py")
            stale = True
        else:
            print(f"{roster_rel} generated data is up to date.")
    elif existing_roster != roster_json:
        _ROSTER_JSON_PATH.write_text(roster_json, encoding="utf-8")
        print(f"wrote {roster_rel}")
    else:
        print(f"{roster_rel} already up to date")

    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
