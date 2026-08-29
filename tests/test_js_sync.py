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


class CosplayerFranchisesInSync(unittest.TestCase):
    """``COSPLAYER_FRANCHISES`` in the Cosplayer JS matches the roster (0.97.0).

    Closes a coverage gap an audit found: the two blocks in ``identity_forge.js``
    were pinned by a unit test AND by ``generate_js_data.py --check`` in CI, but
    this third generated block was pinned by the CI check alone. A contributor
    adding a character and running only the unit suite got a green run with a
    stale franchise filter -- the filter is what the dropdown searches, so a new
    entry would simply be unreachable through it.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "js" / "identity_forge_cosplayer.js").read_text(
            encoding="utf-8")

    def _expected(self):
        # Reuses the GENERATOR's own reader rather than importing COSPLAYERS.
        # Importing runs ``apply_user_cosplayers`` at the bottom of the data module,
        # which merges the maintainer's local ``user_options.json`` -- so an
        # import-based expectation would fail on any machine that has one, and would
        # be asserting that a private character IS in a committed file.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_gen_js_data", ROOT / "scripts" / "generate_js_data.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module._builtin_cosplayer_franchises()

    def test_the_block_matches_the_roster(self):
        js_map = _extract_object(self.source, "COSPLAYER_FRANCHISES", "{", "}")
        expected = self._expected()
        self.assertEqual(
            {f: sorted(v) for f, v in js_map.items()}, expected,
            "js/identity_forge_cosplayer.js COSPLAYER_FRANCHISES is out of sync with "
            "data/cosplayers.py -- run `python scripts/generate_js_data.py`.",
        )

    def test_every_builtin_entry_is_reachable_through_the_filter(self):
        # User-added characters are deliberately absent from the map (the frontend
        # treats an unknown name as unfiltered and always shows it), so this checks
        # the BUILT-IN roster only -- same reader, same reason as above.
        js_map = _extract_object(self.source, "COSPLAYER_FRANCHISES", "{", "}")
        listed = {n for names in js_map.values() for n in names}
        expected = {n for names in self._expected().values() for n in names}
        self.assertEqual(sorted(expected - listed), [],
                         "built-in entries unreachable through franchise_filter")


class RosterJsonSizeTests(unittest.TestCase):
    """``js/identity_forge_roster.json`` is the picker modal's bulk search index
    (a separate, later task builds the modal that fetches it). It is regenerated
    from the full roster on every release, so nothing pins its *content* here
    beyond this size ceiling -- ``scripts/generate_js_data.py --check`` is what
    catches it going stale relative to the data layer. This just stops a future
    roster pass from quietly ballooning the file every ComfyUI picker has to fetch.
    """

    #: ~1.5 MB ceiling (0.97 MB at introduction across 1977 cosplayers, 251
    #: archetypes, 253 creatures) -- generous headroom for roster growth, tight
    #: enough to fail loudly on an accidental per-entry bloat (e.g. a stray raw
    #: field dump instead of just the haystack).
    _MAX_BYTES = 1_500_000

    def test_roster_json_stays_under_the_size_ceiling(self):
        path = ROOT / "js" / "identity_forge_roster.json"
        self.assertTrue(path.is_file(), f"{path} does not exist -- run "
                        f"`python scripts/generate_js_data.py`")
        size = path.stat().st_size
        self.assertLess(
            size, self._MAX_BYTES,
            f"js/identity_forge_roster.json is {size:,} bytes, over the "
            f"{self._MAX_BYTES:,}-byte ceiling -- a roster pass has bloated the "
            f"picker's search index; trim what each entry's haystack carries.",
        )


class SpeciesSlotListsInSync(unittest.TestCase):
    """The species slot tuple is maintained by hand in three places (0.97.0).

    ``data/creatures.py::CREATURE_SLOTS``,
    ``data/user_options.py::_CREATURE_SLOTS`` and
    ``nodes/identity_forge.py::_SPECIES_SLOT_ORDER`` are the same nine slots, and
    ``nodes/identity_forge_creature.py::_OVERRIDE_SLOTS`` is a hand-written subset.

    The duplication is deliberate -- it is what keeps the data modules importable
    without the nodes package -- but nothing pinned them together, so a tenth slot
    could be added in one place and silently ignored in the other two. An audit
    flagged it; this is the mechanical pin rather than the refactor, because
    collapsing them would re-introduce the import edge the split exists to avoid.
    """

    def test_all_three_copies_are_identical(self):
        from data.creatures import CREATURE_SLOTS
        from data.user_options import _CREATURE_SLOTS
        from nodes.identity_forge import _SPECIES_SLOT_ORDER
        self.assertEqual(tuple(CREATURE_SLOTS), tuple(_SPECIES_SLOT_ORDER))
        self.assertEqual(tuple(CREATURE_SLOTS), tuple(_CREATURE_SLOTS))

    def test_the_override_subset_names_only_real_slots(self):
        from data.creatures import CREATURE_SLOTS
        from nodes.identity_forge_creature import _OVERRIDE_SLOTS
        extra = set(_OVERRIDE_SLOTS) - set(CREATURE_SLOTS)
        self.assertEqual(extra, set(), f"not creature slots: {sorted(extra)}")

    def test_the_order_is_the_reading_order_the_prose_relies_on(self):
        # _SPECIES_SLOT_ORDER is what the anatomy sentence is built from, so the
        # tuple ORDER is load-bearing, not just its membership.
        from data.creatures import CREATURE_SLOTS
        self.assertEqual(
            tuple(CREATURE_SLOTS),
            ("head", "eyes", "integument", "arms", "hands", "legs_feet", "wings",
             "tail", "extras"),
        )

if __name__ == "__main__":
    unittest.main()
