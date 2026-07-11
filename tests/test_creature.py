"""Unit tests for the IdentityForgeCreature node and the species engine path.

Pure-stdlib ``unittest`` so it runs without ComfyUI installed:

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.creatures import (
    CREATURES, CREATURE_CLASSES, get_creature, get_creature_names_by_class,
)
from nodes.identity_forge_creature import (
    build_creature_json, _NONE, _RANDOM_ANY, _FOLLOW, _RANDOM_SLOT,
    _FORM_LABEL_ANTHRO, _FORM_LABEL_FERAL, _FORM_LABEL_SUBTLE, _FORM_LABEL_RANDOM,
)
from nodes.identity_forge import (
    generate_character, merge_preset_documents, _parse_archetype_json,
    _SPECIES_KEY, _SPECIES_GROUP, _COSPLAY_LABEL_KEY, _GROUP_ORDER,
    _FORM_ANTHRO, _FORM_FERAL, _FORM_SUBTLE,
)
from nodes.identity_forge_cosplayer import build_cosplayer_json
from data.cosplayers import get_cosplayer_names


def _doc(raw: str) -> dict:
    return json.loads(raw)


def _render(character_json: str, gender: str = "Any", seed: int = 7):
    """Run a creature/merged document through IdentityForge; return (prose, json)."""
    flat = _parse_archetype_json(character_json)
    species = flat.pop(_SPECIES_KEY, None)
    cosplay_label = flat.pop(_COSPLAY_LABEL_KEY, None)
    locked = {k: v for k, v in flat.items() if not k.startswith("__") and k != "gender"}
    return generate_character(seed, gender, locked, cosplay_label=cosplay_label, species=species)


class BuildBasicsTests(unittest.TestCase):
    def test_none_is_inactive(self):
        self.assertEqual(build_creature_json(_NONE), "{}")

    def test_unknown_name_is_inactive(self):
        self.assertEqual(build_creature_json("definitely-not-a-creature"), "{}")

    def test_none_ignores_slot_and_freetext_overrides(self):
        # The 'creature' dropdown is the master on/off switch: 'None' emits nothing
        # even when hybrid slots or the free-text box still carry leftover overrides.
        self.assertEqual(build_creature_json(_NONE, head="sloth"), "{}")
        self.assertEqual(build_creature_json(_NONE, head=_RANDOM_SLOT, seed=5), "{}")
        self.assertEqual(
            build_creature_json(_NONE, more_features="a crown of bone spurs"), "{}"
        )

    def test_specific_creature_fills_core_slots(self):
        doc = _doc(build_creature_json("praying mantis", seed=1))
        anatomy = doc[_SPECIES_GROUP]
        for slot in ("head", "eyes", "integument"):
            self.assertIn(slot, anatomy)
        self.assertEqual(doc["_meta"]["creature_of"], "praying mantis")
        self.assertEqual(doc["_meta"]["creature_class"], "Insects & Arachnids")
        self.assertEqual(doc["_meta"]["form"], _FORM_ANTHRO)

    def test_reproducible(self):
        self.assertEqual(
            build_creature_json(_RANDOM_ANY, seed=99),
            build_creature_json(_RANDOM_ANY, seed=99),
        )


class RandomScopingTests(unittest.TestCase):
    def test_random_any_picks_known_creature(self):
        doc = _doc(build_creature_json(_RANDOM_ANY, seed=5))
        self.assertIn(doc["_meta"]["creature_of"], CREATURES)

    def test_random_class_stays_in_class(self):
        for creature_class in CREATURE_CLASSES:
            if not get_creature_names_by_class(creature_class):
                continue
            for seed in range(8):  # a few seeds to exercise the pick
                doc = _doc(build_creature_json(f"Random - {creature_class}", seed=seed))
                self.assertEqual(doc["_meta"]["creature_class"], creature_class)


class HybridTests(unittest.TestCase):
    def test_head_override_grafts_other_creature(self):
        doc = _doc(build_creature_json("praying mantis", seed=1, head="sloth"))
        anatomy = doc[_SPECIES_GROUP]
        self.assertEqual(anatomy["head"], get_creature("sloth")["head"])
        # the rest still comes from the mantis base
        self.assertEqual(anatomy["arms"], get_creature("praying mantis")["arms"])

    def test_more_features_overrides_slot_and_adds_extras(self):
        doc = _doc(build_creature_json(
            "wolf", seed=2, more_features="eyes: six glowing ocelli\na crown of bone spurs",
        ))
        anatomy = doc[_SPECIES_GROUP]
        self.assertEqual(anatomy["eyes"], "six glowing ocelli")
        self.assertIn("a crown of bone spurs", anatomy["extras"])

    def test_palette_and_finish_recolour_integument(self):
        doc = _doc(build_creature_json(
            "octopus", seed=3, palette="crimson", integument_finish="glossy",
        ))
        integ = doc[_SPECIES_GROUP]["integument"]
        self.assertIn("crimson", integ)
        self.assertIn("glossy", integ)

    def test_auto_palette_draws_from_pool_and_varies(self):
        # 0.38 gave colour-variable species a palette_pool: 'Auto' must land in
        # the pool every time and actually vary across seeds.
        pool = CREATURES["dragon"]["palette_pool"]
        seen = set()
        for seed in range(40):
            integ = _doc(build_creature_json("dragon", seed=seed))[_SPECIES_GROUP]["integument"]
            # a mass/plural integument carries no article ("crimson overlapping
            # armored scales"); a singular one does ("a crimson hide").
            hits = [hue for hue in pool
                    if integ.startswith((f"{hue} ", f"a {hue} ", f"an {hue} "))]
            self.assertEqual(len(hits), 1, integ)
            seen.add(hits[0])
        self.assertGreater(len(seen), 1)  # not stuck on one hue

    def test_pool_palette_does_not_shift_creature_or_slot_picks(self):
        # The palette draw is last, so seed->anatomy mapping is colour-independent:
        # everything except the recoloured integument matches an explicit-palette build.
        for seed in range(10):
            auto = _doc(build_creature_json("wolf", seed=seed))[_SPECIES_GROUP]
            fixed = _doc(build_creature_json("wolf", seed=seed, palette="crimson"))[_SPECIES_GROUP]
            auto.pop("integument"), fixed.pop("integument")
            self.assertEqual(auto, fixed, f"seed {seed}")

    def test_multiword_pattern_palette_keeps_article_agreement(self):
        # Pattern-bearing pool entries ("orange-spotted cream") ride the same
        # descriptor path; the leading article must agree with the first word.
        integ = _doc(build_creature_json(
            "wolf", seed=1, palette="orange-spotted cream",
        ))[_SPECIES_GROUP]["integument"]
        self.assertTrue(integ.startswith("an orange-spotted cream "), integ)
        integ = _doc(build_creature_json(
            "wolf", seed=1, palette="russet brown",
        ))[_SPECIES_GROUP]["integument"]
        self.assertTrue(integ.startswith("a russet brown "), integ)


class SuppressionTests(unittest.TestCase):
    def test_anthro_suppresses_demographics_and_head_hides_face(self):
        meta = _doc(build_creature_json("praying mantis", seed=1))["_meta"]
        self.assertIn("Demographics", meta["suppress_groups"])
        self.assertIn("Face", meta["suppress_groups"])  # head slot present
        self.assertIn("skin_tone", meta["suppress_fields"])  # integument present

    def test_feral_suppresses_clothing_and_proportions(self):
        meta = _doc(build_creature_json("dragon", seed=3, form=_FORM_LABEL_FERAL))["_meta"]
        self.assertEqual(meta["form"], _FORM_FERAL)
        self.assertIn("Clothing", meta["suppress_groups"])
        self.assertIn("bust", meta["suppress_fields"])

    def test_subtle_drops_replacers_and_keeps_human(self):
        doc = _doc(build_creature_json("owl", seed=4, form=_FORM_LABEL_SUBTLE))
        anatomy = doc[_SPECIES_GROUP]
        for dropped in ("head", "eyes", "integument"):
            self.assertNotIn(dropped, anatomy)
        self.assertIn("wings", anatomy)  # additive accents survive
        self.assertEqual(doc["_meta"]["suppress_groups"], [])
        self.assertEqual(doc["_meta"]["suppress_fields"], [])

    def test_random_form_is_one_of_the_three(self):
        meta = _doc(build_creature_json("wolf", seed=11, form=_FORM_LABEL_RANDOM))["_meta"]
        self.assertIn(meta["form"], (_FORM_ANTHRO, _FORM_FERAL, _FORM_SUBTLE))


class EnginePathTests(unittest.TestCase):
    def test_species_group_in_json_and_canonical_position(self):
        own = build_creature_json("praying mantis", seed=1)
        _, js = _render(own)
        doc = json.loads(js)
        self.assertIn(_SPECIES_GROUP, doc)
        # Species & Anatomy must sit right after _meta / Demographics by group order.
        keys = [k for k in doc if k != "_meta"]
        self.assertEqual(keys[0], _SPECIES_GROUP)  # Demographics is suppressed under anthro

    def test_suppressed_fields_absent_from_outputs(self):
        own = build_creature_json("praying mantis", seed=1)
        prose, js = _render(own, gender="Female", seed=20)
        doc = json.loads(js)
        self.assertNotIn("Face", doc)   # head slot suppresses the face
        self.assertNotIn("Demographics", doc)
        self.assertIn("anthropomorphic praying mantis hybrid", prose)

    def test_anatomy_woven_into_prose(self):
        own = build_creature_json("praying mantis", seed=1, head="sloth")
        prose, _ = _render(own, gender="Male", seed=20)
        self.assertIn("sloth", prose)
        self.assertIn("raptorial spiked forelimbs", prose)

    def test_cosplayer_costume_survives_creature(self):
        names = get_cosplayer_names()
        cosplayer = "Superman" if "Superman" in names else names[0]
        cos = build_cosplayer_json(cosplayer, seed=2)
        own = build_creature_json("praying mantis", seed=1)
        merged = merge_preset_documents(cos, own)
        doc = json.loads(merged)
        # costume (Clothing) from the upstream cosplayer survives the creature
        self.assertIn("Clothing", doc)
        # creature (downstream) wins the species group
        self.assertIn(_SPECIES_GROUP, doc)
        prose, _ = _render(merged, gender="Male", seed=2)
        self.assertIn("Cosplaying as", prose)
        self.assertIn("hybrid", prose)

    def test_inactive_creature_passes_upstream_through(self):
        cos = build_cosplayer_json(get_cosplayer_names()[0], seed=1)
        merged = merge_preset_documents(cos, build_creature_json(_NONE))
        self.assertEqual(json.loads(merged), json.loads(cos))

    def test_many_seeds_never_crash(self):
        names = list(CREATURES)
        for seed in range(60):
            creature = names[seed % len(names)]
            form = (_FORM_LABEL_ANTHRO, _FORM_LABEL_FERAL, _FORM_LABEL_SUBTLE)[seed % 3]
            own = build_creature_json(creature, seed=seed, form=form)
            prose, js = _render(own, gender=("Any", "Female", "Male")[seed % 3], seed=seed)
            self.assertIsInstance(prose, str)
            json.loads(js)


if __name__ == "__main__":
    unittest.main()
