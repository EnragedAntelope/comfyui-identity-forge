"""Tests for the IdentityForgeOutfitSheet node (2.3.0).

Contract: one resolved character, several outfits, and nothing but the clothes (and the
styling that goes with them) moving between them.
"""
from __future__ import annotations

import json
import logging
import unittest

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge import IdentityForge
from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
from nodes.identity_forge_outfit_sheet import (
    _BACKDROPS, _CLOTHING, _RESTYLED, _SHEETS, IdentityForgeOutfitSheet,
    resolve_outfit_sheet,
)

_POSE = "standing naturally"


def _forge(seed: int, archetype_json: str = "") -> str:
    kwargs: dict = {spec.id: "Random" for spec in IdentityForge.define_schema().inputs}
    kwargs.update(
        seed=seed, archetype_json=archetype_json, set_all_fields="Off", gender="Any",
        wardrobe="Match gender", size_scale="Auto", hair_color_scope="Natural only",
        accessory_density="Balanced", location_setting="Any indoor/outdoor",
    )
    return IdentityForge.execute(**kwargs).args[1]


class _Conflicts(logging.Handler):
    """Collects the engine's lock-vs-lock reports: a lock it had to keep against a rule."""

    def __init__(self) -> None:
        super().__init__(logging.INFO)
        self.messages: "list[str]" = []

    def emit(self, record: logging.LogRecord) -> None:
        if "keeping lock" in record.getMessage():
            self.messages.append(record.getMessage())


class VocabularyTests(unittest.TestCase):
    def test_every_sheet_style_is_a_live_option(self):
        for sheet, styles in _SHEETS.items():
            self.assertEqual(len(styles), len(set(styles)), sheet)
            for style in styles:
                self.assertIn(style, FIELD_DEFINITIONS["outfit_style"]["female_options"])
                self.assertIn(style, FIELD_DEFINITIONS["outfit_style"]["male_options"])

    def test_every_backdrop_is_a_live_location(self):
        for label, location in _BACKDROPS.items():
            if location:
                self.assertIn(location, FIELD_DEFINITIONS["location"]["female_options"], label)
                self.assertIn(location, FIELD_DEFINITIONS["location"]["male_options"], label)

    def test_restyling_never_touches_the_person(self):
        groups = {FIELD_DEFINITIONS[name]["group"] for name in _RESTYLED}
        self.assertNotIn("Face", groups)
        self.assertNotIn("Body", groups)
        self.assertNotIn("Demographics", groups)
        self.assertFalse({"hair_color", "hair_length", "hair_texture"} & _RESTYLED)
        self.assertIn("outfit_description", _CLOTHING)


class SheetTests(unittest.TestCase):
    def test_same_person_each_view_in_its_style(self):
        document = _forge(11)
        prompts, labels = resolve_outfit_sheet(
            document, "Range (6)", "Grey studio backdrop", "Full body", _POSE)
        self.assertEqual(len(prompts), 6)
        self.assertEqual(labels[2], "3-business-formal")
        self.assertEqual(len(set(prompts)), 6, "every view must differ")
        heads = {prompt.split(". ")[0] for prompt in prompts}
        self.assertEqual(len(heads), 1, heads)
        for prompt in prompts:
            self.assertIn("seamless grey studio backdrop", prompt)

    def test_deterministic_and_stable_across_sheets(self):
        document = _forge(4)
        first = resolve_outfit_sheet(document, "Range (6)", "Grey studio backdrop",
                                     "Full body", _POSE)
        again = resolve_outfit_sheet(document, "Range (6)", "Grey studio backdrop",
                                     "Full body", _POSE)
        self.assertEqual(first, again)
        everyday, _ = resolve_outfit_sheet(document, "Everyday (4)", "Grey studio backdrop",
                                           "Full body", _POSE)
        # The seed follows the style, not the position: casual dresses the same way.
        self.assertEqual(first[0][0], everyday[0])

    def test_outfits_differ_between_characters_and_by_outfit_seed(self):
        # 2.3.0: a fixed per-style seed gave 40 characters four casual outfits.
        def outfit(prompt: str) -> str:
            return prompt.split(" wears ", 2)[-1].split(". ")[0]

        casual = {outfit(resolve_outfit_sheet(_forge(seed), "Everyday (4)",
                                              "Grey studio backdrop", "Full body",
                                              _POSE)[0][0])
                  for seed in range(12)}
        self.assertGreaterEqual(len(casual), 10, casual)
        document = _forge(4)
        rolls = {tuple(outfit(p) for p in resolve_outfit_sheet(
                    document, "Everyday (4)", "Grey studio backdrop", "Full body", _POSE,
                    outfit_seed=n)[0])
                 for n in range(4)}
        self.assertEqual(len(rolls), 4, "each outfit_seed must re-dress the person")

    def test_no_view_voices_a_contradiction(self):
        # Every lock this node adds must agree with what it keeps: the engine reports
        # a lock it had to keep against a rule, and no view may produce one.
        handler = _Conflicts()
        root = logging.getLogger()
        old_level = root.level
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        try:
            for seed in range(25):
                document = _forge(seed)
                handler.messages.clear()
                for backdrop in ("Grey studio backdrop", "Keep the character's scene"):
                    resolve_outfit_sheet(document, "Every style (15)", backdrop,
                                         "Full body", _POSE)
                self.assertEqual(handler.messages, [], f"seed {seed}")
        finally:
            root.removeHandler(handler)
            root.setLevel(old_level)

    def test_a_cosplayer_wears_their_costume(self):
        kwargs = {spec.id: getattr(spec, "default", None)
                  for spec in IdentityForgeCosplayer.define_schema().inputs}
        kwargs.update(character="Grimace", seed=7, upstream="")
        document = _forge(7, IdentityForgeCosplayer.execute(**kwargs).args[0])
        prompts, labels = resolve_outfit_sheet(
            document, "Range (6)", "Grey studio backdrop", "Full body", _POSE)
        self.assertEqual(labels, ["1-as-resolved"])
        self.assertEqual(len(prompts), 1)

    def test_malformed_input_degrades_to_one_view(self):
        prompts, labels = resolve_outfit_sheet(
            "not json", "Range (6)", "Grey studio backdrop", "Full body", _POSE)
        self.assertEqual((len(prompts), labels), (1, ["1-as-resolved"]))
        self.assertTrue(json.dumps(prompts))


class SchemaTests(unittest.TestCase):
    def test_outputs_are_lists(self):
        schema = IdentityForgeOutfitSheet.define_schema()
        self.assertEqual(schema.node_id, "IdentityForgeOutfitSheet")
        self.assertEqual(schema.category, "conditioning/character")
        self.assertTrue(all(output.is_output_list for output in schema.outputs))


if __name__ == "__main__":
    unittest.main()
