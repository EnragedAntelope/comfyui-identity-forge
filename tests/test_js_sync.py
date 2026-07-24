"""Guard against drift between the frontend JS data and ``data/fields.py``.

``js/identity_forge.js`` embeds two data blocks transcribed from the Python field
definitions: ``FIELD_TO_GROUP`` (which group each widget belongs to) and
``GENDER_POOLS`` (the per-gender option lists the UI swaps in when the gender toggle
changes). They are hand-maintained, so they can silently fall out of step with
``data/fields.py`` — exactly what happened when ``hair_length`` and ``hair_style``
gained gender-divergent options that never reached ``GENDER_POOLS``.

These tests reconstruct the expected blocks from ``data/fields.py`` using the same
rules the node's ``define_schema`` widget builder applies, and assert the JS matches.
Both JS blocks are strict JSON object literals, so they parse directly.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge import _CONTROL_FIELDS, _HIDDEN_FIELDS, _dedupe, _is_absent

_JS_PATH = ROOT / "js" / "identity_forge.js"
_GENDERS = ("Female", "Male", "Any")


def _extract_object(source: str, name: str, open_ch: str, close_ch: str):
    """Parse the ``const <name> = { ... };`` (or ``[ ... ]``) literal out of the JS.

    The two data blocks are plain JSON (double-quoted keys/values, no comments or
    trailing commas), so a balanced-delimiter scan + ``json.loads`` is sufficient.
    """
    marker = f"const {name} = "
    start = source.index(marker) + len(marker)
    depth = 0
    i = start
    while i < len(source):
        ch = source[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return json.loads(source[start:i + 1])
        i += 1
    raise AssertionError(f"Unbalanced {name!r} literal in {_JS_PATH.name}")


def _visible(values) -> list[str]:
    """Options the widget shows: real values only (absence sentinels are hidden)."""
    return [v for v in values if not _is_absent(v)]


def _expected_field_to_group() -> dict[str, str]:
    return {
        name: meta["group"]
        for name, meta in FIELD_DEFINITIONS.items()
        if name not in _HIDDEN_FIELDS and name not in _CONTROL_FIELDS
    }


def _expected_gender_pools() -> dict[str, dict[str, list[str]]]:
    """Per-gender option lists for every gender-divergent, widget-visible field.

    Mirrors the JS convention: each list is ``["Random", *visible options, "None"]``;
    the ``Any`` pool is the deduped union (female order first, male-only appended),
    exactly as ``define_schema`` builds the combined widget options.
    """
    pools: dict[str, dict[str, list[str]]] = {}
    for name, meta in FIELD_DEFINITIONS.items():
        if name in _HIDDEN_FIELDS or name in _CONTROL_FIELDS:
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


class JsDataInSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = _JS_PATH.read_text(encoding="utf-8")

    def test_field_to_group_matches_fields_py(self) -> None:
        js_map = _extract_object(self.source, "FIELD_TO_GROUP", "{", "}")
        self.assertEqual(
            js_map, _expected_field_to_group(),
            "js/identity_forge.js FIELD_TO_GROUP is out of sync with data/fields.py — "
            "regenerate it from the current field definitions.",
        )

    def test_gender_pools_cover_every_divergent_field(self) -> None:
        js_pools = _extract_object(self.source, "GENDER_POOLS", "{", "}")
        self.assertEqual(
            set(js_pools), set(_expected_gender_pools()),
            "js/identity_forge.js GENDER_POOLS is missing (or has extra) gender-"
            "divergent fields relative to data/fields.py.",
        )

    def test_gender_pools_option_lists_match(self) -> None:
        js_pools = _extract_object(self.source, "GENDER_POOLS", "{", "}")
        expected = _expected_gender_pools()
        for field, by_gender in expected.items():
            for gender in _GENDERS:
                self.assertEqual(
                    js_pools.get(field, {}).get(gender), by_gender[gender],
                    f"GENDER_POOLS[{field!r}][{gender!r}] in the JS does not match "
                    f"data/fields.py.",
                )


if __name__ == "__main__":
    unittest.main()
