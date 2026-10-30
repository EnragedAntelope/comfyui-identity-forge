"""Tests for the IdentityForgeAgeProgression node (2.3.0).

Contract: one resolved character at several adult ages; hair greys forward, never back;
nothing an age refuses is voiced.
"""
from __future__ import annotations

import json
import logging
import unittest

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge_age_progression import (
    _STAGES, IdentityForgeAgeProgression, _stage_hair, resolve_age_progression,
)
from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
from tests.test_outfit_sheet import _Conflicts, _forge


class VocabularyTests(unittest.TestCase):
    def test_every_stage_is_an_adult_pool_age(self):
        for name, stages in _STAGES.items():
            self.assertEqual(list(stages), sorted(stages, key=int), name)
            for stage in stages:
                self.assertIn(stage, FIELD_DEFINITIONS["age"]["female_options"])
                self.assertIn(stage, FIELD_DEFINITIONS["age"]["male_options"])
                self.assertGreaterEqual(int(stage), 18)


class HairTests(unittest.TestCase):
    def test_greys_forward(self):
        self.assertEqual(_stage_hair("jet black", 30, 50, ""), "jet black")
        self.assertEqual(_stage_hair("jet black", 30, 60, ""), "salt and pepper")
        self.assertEqual(_stage_hair("jet black", 30, 70, ""), "silver")
        self.assertEqual(_stage_hair("golden blonde", 30, 60, ""), "silver")
        # Younger than the character: the colour they have now.
        self.assertEqual(_stage_hair("jet black", 50, 20, ""), "jet black")

    def test_never_back(self):
        # Grey at 45 stays grey at 50 even though most 50-year-olds are not.
        self.assertEqual(_stage_hair("silver", 45, 50, "dark brown"), "silver")
        self.assertEqual(_stage_hair("silver", 45, 40, "dark brown"), "dark brown")
        self.assertEqual(_stage_hair("salt and pepper", 70, 60, "dark brown"),
                         "salt and pepper")
        self.assertEqual(_stage_hair("salt and pepper", 70, 20, "dark brown"), "dark brown")

    def test_stage_colours_are_live_options(self):
        for colour in ("salt and pepper", "silver"):
            self.assertIn(colour, FIELD_DEFINITIONS["hair_color"]["female_options"])
            self.assertIn(colour, FIELD_DEFINITIONS["hair_color"]["male_options"])


class ProgressionTests(unittest.TestCase):
    def test_same_person_at_each_age(self):
        document = _forge(23)
        prompts, labels = resolve_age_progression(document, "Decades (6)", "Unspecified")
        self.assertEqual(labels, [f"{i}-age-{a}" for i, a in
                                  enumerate(_STAGES["Decades (6)"], start=1)])
        for prompt, stage in zip(prompts, _STAGES["Decades (6)"]):
            self.assertIn(f"{stage}-year-old", prompt)
        # Only the age moves in the identity sentence.
        heads = {p.split(". ")[0].replace(f"{a}-year-old", "AGE")
                 for p, a in zip(prompts, _STAGES["Decades (6)"])}
        self.assertEqual(len(heads), 1, heads)

    def test_no_stage_voices_a_contradiction(self):
        handler = _Conflicts()
        root = logging.getLogger()
        old_level = root.level
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        try:
            for seed in range(30):
                document = _forge(seed)
                handler.messages.clear()
                resolve_age_progression(document, "Decades (6)", "Head and shoulders")
                self.assertEqual(handler.messages, [], f"seed {seed}")
        finally:
            root.removeHandler(handler)
            root.setLevel(old_level)

    def test_a_masked_character_emits_one_view(self):
        kwargs = {spec.id: getattr(spec, "default", None)
                  for spec in IdentityForgeCosplayer.define_schema().inputs}
        kwargs.update(character="Grimace", seed=7, upstream="")
        document = _forge(7, IdentityForgeCosplayer.execute(**kwargs).args[0])
        self.assertTrue(json.loads(document)["_meta"].get("covers_face"))
        prompts, labels = resolve_age_progression(document, "Decades (6)", "Unspecified")
        self.assertEqual((len(prompts), labels), (1, ["1-as-resolved"]))


class SchemaTests(unittest.TestCase):
    def test_outputs_are_lists(self):
        schema = IdentityForgeAgeProgression.define_schema()
        self.assertEqual(schema.node_id, "IdentityForgeAgeProgression")
        self.assertEqual(schema.category, "conditioning/character")
        self.assertTrue(all(output.is_output_list for output in schema.outputs))


if __name__ == "__main__":
    unittest.main()
