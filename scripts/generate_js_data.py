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

    source = _JS_PATH.read_text(encoding="utf-8")
    if _START not in source or _END not in source:
        print(f"ERROR: marker comments not found in {_JS_PATH.name}; "
              f"expected a region delimited by {_START!r} … {_END!r}.")
        return 2

    updated = _splice(source, render_block())
    rel = _JS_PATH.relative_to(ROOT)
    if args.check:
        if updated != source:
            print(f"{rel} is STALE relative to data/fields.py.")
            print("Regenerate with: python scripts/generate_js_data.py")
            return 1
        print(f"{rel} generated data is up to date.")
        return 0
    if updated != source:
        _JS_PATH.write_text(updated, encoding="utf-8")
        print(f"wrote {rel}")
    else:
        print(f"{rel} already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
