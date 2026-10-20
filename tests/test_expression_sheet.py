"""Tests for the IdentityForgeExpressionSheet node (1.10.0).

Contract: one resolved character, several expressions, and nothing but the face's
emotion moving between them.
"""
from __future__ import annotations

import json
import unittest

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge import IdentityForge, _live_exclusions
from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
from nodes.identity_forge_expression_sheet import (
    _SHEETS, _VIEWS, IdentityForgeExpressionSheet, resolve_expression_sheet,
)

_OWNED = ("expression", "mood", "smile_type")


def _forge(seed: int) -> tuple[str, str]:
    kwargs: dict = {spec.id: "Random" for spec in IdentityForge.define_schema().inputs}
    kwargs.update(
        seed=seed, archetype_json="", set_all_fields="Off", gender="Any",
        wardrobe="Match gender", size_scale="Auto", hair_color_scope="Natural only",
        accessory_density="Balanced", location_setting="Any indoor/outdoor",
    )
    return IdentityForge.execute(**kwargs).args[:2]


class VocabularyTests(unittest.TestCase):
    def test_every_triple_value_is_a_live_option(self):
        for name, triple in _VIEWS.items():
            for field, value in zip(_OWNED, triple):
                if value == "None":
                    continue
                with self.subTest(view=name, field=field):
                    self.assertIn(value, FIELD_DEFINITIONS[field]["female_options"])
                    self.assertIn(value, FIELD_DEFINITIONS[field]["male_options"])

    def test_no_triple_pairs_values_the_engine_excludes(self):
        # A lock beats a rule, so the engine would voice a contradictory pair. Catch
        # it here instead (coherence checklist 5: expression vs mood must agree).
        for name, triple in _VIEWS.items():
            resolved = {f: v for f, v in zip(_OWNED, triple) if v != "None"}
            for field, value in resolved.items():
                with self.subTest(view=name, field=field):
                    self.assertNotIn(value, _live_exclusions(field, resolved))

    def test_every_sheet_names_known_views_without_repeats(self):
        for sheet, names in _SHEETS.items():
            self.assertEqual(len(names), len(set(names)), sheet)
            self.assertLessEqual(set(names), set(_VIEWS), sheet)
        self.assertEqual(len(_SHEETS["Full (10)"]), 10)


class SheetTests(unittest.TestCase):
    def test_same_person_only_the_face_moves(self):
        _, document = _forge(11)
        prompts, labels = resolve_expression_sheet(document, "Basic (6)", "Unspecified")
        self.assertEqual(len(prompts), 6)
        self.assertEqual(labels[0], "1-neutral")
        self.assertEqual(len(set(prompts)), 6, "every view must differ")
        # The person is the same: the identity sentence leads every prompt unchanged.
        heads = {prompt.split(". ")[0] for prompt in prompts}
        self.assertEqual(len(heads), 1, heads)
        self.assertIn("laughing", prompts[2])

    def test_framing_replaces_the_shot(self):
        _, document = _forge(3)
        prompts, _ = resolve_expression_sheet(document, "Smiles (3)", "Head and shoulders")
        for prompt in prompts:
            self.assertIn("close-up portrait", prompt)

    def test_a_masked_character_emits_one_view(self):
        kwargs = {spec.id: getattr(spec, "default", None)
                  for spec in IdentityForgeCosplayer.define_schema().inputs}
        kwargs.update(character="Grimace", seed=7, upstream="")
        cosplay = IdentityForgeCosplayer.execute(**kwargs).args[0]
        forge_kwargs = {spec.id: "Random" for spec in IdentityForge.define_schema().inputs}
        forge_kwargs.update(seed=7, archetype_json=cosplay, set_all_fields="Off",
                            gender="Any", wardrobe="Match gender", size_scale="Auto",
                            hair_color_scope="Natural only", accessory_density="Balanced",
                            location_setting="Any indoor/outdoor")
        document = IdentityForge.execute(**forge_kwargs).args[1]
        self.assertTrue(json.loads(document)["_meta"].get("covers_face"))
        prompts, labels = resolve_expression_sheet(document, "Full (10)", "Head and shoulders")
        self.assertEqual(labels, ["1-masked"])
        self.assertEqual(len(prompts), 1)


class SchemaTests(unittest.TestCase):
    def test_outputs_are_lists(self):
        schema = IdentityForgeExpressionSheet.define_schema()
        self.assertEqual(schema.node_id, "IdentityForgeExpressionSheet")
        self.assertEqual(schema.category, "conditioning/character")
        self.assertTrue(all(output.is_output_list for output in schema.outputs))


if __name__ == "__main__":
    unittest.main()
