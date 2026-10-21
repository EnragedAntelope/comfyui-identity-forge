"""The 2.0.0 seed-epoch changes: each one moves seeds or gallery prose on purpose.

Measured numbers for every item are in docs/history.md -> "2.0.0".
"""
from __future__ import annotations

import json
import unittest

from data.constraints import _LOCATION_FAMILY, _STUDIO_LIT_INTERIORS
from data.fields import FIELD_DEFINITIONS, FIELD_FAMILIES, OUTDOOR_LOCATIONS
from nodes.identity_forge import _format_prose, _live_exclusions, generate_character

N = 1500


def _flat(js: str) -> dict:
    out = {}
    for group, fields in json.loads(js).items():
        if group != "_meta" and isinstance(fields, dict):
            out.update(fields)
    return out


class ExpressionArticleTests(unittest.TestCase):
    """A noun expression reads "a bright smile", never "is bright smile"."""

    def _scene(self, expression: str) -> str:
        return _format_prose({"expression": expression}, "Male", None, None)

    def test_noun_expressions_take_an_article(self):
        self.assertIn("His expression is a bright smile", self._scene("bright smile"))
        self.assertIn("His expression is an intense gaze", self._scene("intense gaze"))
        self.assertIn("His expression is a wide toothy grin", self._scene("wide toothy grin"))

    def test_adjectives_and_mass_nouns_stay_bare(self):
        self.assertIn("His expression is confident", self._scene("confident"))
        self.assertIn("His expression is quiet amusement", self._scene("quiet amusement"))

    def test_an_article_already_present_is_not_doubled(self):
        self.assertIn("His expression is a warm smile", self._scene("a warm smile"))


class DrawWeightTests(unittest.TestCase):
    """Women's short hair near 10% and age 60+ near 16% with 75 and 80 added."""

    @classmethod
    def setUpClass(cls):
        cls.rows = {g: [_flat(generate_character(s, g, {})[1]) for s in range(N)]
                    for g in ("Female", "Male")}

    def _share(self, gender, field, values):
        rows = self.rows[gender]
        return sum(r.get(field) in values for r in rows) / len(rows)

    def test_womens_shortest_lengths_are_near_ten_percent(self):
        share = self._share("Female", "hair_length",
                            {"buzzed very short", "very short", "short pixie"})
        self.assertTrue(0.06 < share < 0.14, share)

    def test_age_sixty_plus_holds_near_sixteen_percent(self):
        for gender in ("Female", "Male"):
            share = self._share(gender, "age", {"60", "65", "70", "75", "80"})
            self.assertTrue(0.12 < share < 0.20, (gender, share))

    def test_seventy_five_and_eighty_draw(self):
        self.assertGreater(self._share("Female", "age", {"75"}), 0)
        self.assertGreater(self._share("Male", "age", {"80"}), 0)


class IndoorStudioLightingTests(unittest.TestCase):
    """A portrait rig only lights a place that owns one (2.0.0)."""

    def test_no_rig_at_an_everyday_interior(self):
        rig = set(FIELD_FAMILIES["lighting"]["studio_shape"]["variants"])
        for seed in range(N):
            for gender in ("Female", "Male"):
                d = _flat(generate_character(seed, gender, {})[1])
                loc = d.get("location") or ""
                if (loc in OUTDOOR_LOCATIONS or _LOCATION_FAMILY.get(loc) == "studio"
                        or loc in _STUDIO_LIT_INTERIORS):
                    continue
                self.assertNotIn(d.get("lighting"), rig, (seed, gender, loc))

    def test_the_mood_family_stays_legal_indoors(self):
        mood = set(FIELD_FAMILIES["lighting"]["studio_mood"]["variants"])
        hits = sum(_flat(generate_character(s, "Female", {})[1]).get("lighting") in mood
                   for s in range(N))
        self.assertGreater(hits, 0)

    def test_a_locked_rig_moves_the_place_not_the_light(self):
        for seed in range(40):
            d = _flat(generate_character(seed, "Female", {"lighting": "Rembrandt lighting"})[1])
            self.assertEqual(d["lighting"], "Rembrandt lighting")
            loc = d.get("location") or ""
            self.assertTrue(loc in _STUDIO_LIT_INTERIORS
                            or _LOCATION_FAMILY.get(loc) == "studio", (seed, loc))


class GazeFieldTests(unittest.TestCase):
    """2.0.0: the `looking` poses became their own field, drawn after the pose."""

    @classmethod
    def setUpClass(cls):
        cls.rows = [_flat(generate_character(s, g, {})[1])
                    for s in range(600) for g in ("Female", "Male")]

    def test_pose_and_gaze_are_disjoint(self):
        pose = set(FIELD_DEFINITIONS["pose"]["female_options"])
        gaze = set(FIELD_DEFINITIONS["gaze"]["female_options"])
        self.assertFalse(pose & gaze)

    def test_gaze_is_voiced_after_the_pose(self):
        prose, _ = generate_character(11, "Female", {"pose": "standing naturally",
                                                      "gaze": "looking off past the camera"})
        self.assertIn("She is standing naturally, looking off past the camera.", prose)

    def test_every_drawn_pose_and_gaze_obeys_the_live_rules(self):
        for d in self.rows:
            presentation = "Masculine" if d.get("gender") == "Male" else "Feminine"
            for field in ("pose", "gaze"):
                self.assertNotIn(d.get(field), _live_exclusions(field, d, presentation),
                                 (field, d.get(field), d.get("shot_type")))

    def test_a_selfie_looks_at_the_lens(self):
        for seed in range(60):
            d = _flat(generate_character(seed, "Female",
                                         {"shot_type": "selfie framing at arm's length"})[1])
            self.assertNotIn(d.get("gaze"), {"looking off past the camera",
                                             "looking over one shoulder", "glancing back",
                                             "looking down thoughtfully"}, seed)

    def test_a_locked_gaze_steers_the_pose_drawn_before_it(self):
        for seed in range(60):
            d = _flat(generate_character(seed, "Male", {"gaze": "glancing back"})[1])
            self.assertNotEqual(d.get("pose"), "walking toward the camera", seed)
            self.assertNotIn(d.get("pose"), {"flashing a peace sign", "giving a thumbs up",
                                             "waving at the camera", "making a finger heart"})

    def test_an_old_looking_pose_lock_becomes_a_gaze(self):
        d = _flat(generate_character(5, "Female",
                                     {"pose": "looking directly into the camera"})[1])
        self.assertEqual(d.get("gaze"), "looking directly into the camera")
        self.assertIn(d.get("pose"), FIELD_DEFINITIONS["pose"]["female_options"])

    def test_a_turnaround_with_a_pinned_stance_states_no_gaze(self):
        from nodes.identity_forge_turnaround import resolve_turnaround
        _, js = generate_character(3, "Female", {"gaze": "glancing back"})
        prompts, _ = resolve_turnaround(js, "Front + back (2)", "Full body",
                                        "standing naturally")
        for prompt in prompts:
            self.assertNotIn("glancing back", prompt)

    def test_the_expression_sheet_can_hold_one_gaze(self):
        from nodes.identity_forge_expression_sheet import resolve_expression_sheet
        _, js = generate_character(3, "Female", {})
        prompts, _ = resolve_expression_sheet(js, "Smiles (3)", "Head and shoulders",
                                              "looking directly into the camera")
        for prompt in prompts:
            self.assertIn("looking directly into the camera", prompt)


class CostumeBackTests(unittest.TestCase):
    """2.0.0: a back view draws the entry's `costume_back`, not the chest emblem."""

    def _turnaround(self, name, views="Turnaround (6)"):
        import tests  # noqa: F401  (comfy_api stub)
        from nodes.identity_forge import IdentityForge
        from nodes.identity_forge_cosplayer import build_cosplayer_json
        from nodes.identity_forge_turnaround import _unwrap, resolve_turnaround
        defaults = {s.id: getattr(s, "default", None)
                    for s in IdentityForge.define_schema().inputs}
        kwargs = dict(defaults, seed=1, archetype_json=build_cosplayer_json(name, 1))
        doc = _unwrap(IdentityForge.execute(**kwargs))[1]
        return resolve_turnaround(doc, views, "Full body", "standing naturally")

    def test_back_views_swap_the_costume(self):
        from data.cosplayers import COSPLAYERS
        prompts, labels = self._turnaround("Superman")
        back = COSPLAYERS["Superman"]["costume_back"]
        for prompt, label in zip(prompts, labels):
            swapped = label.endswith(("back", "rear-three-quarter"))
            self.assertEqual(back in prompt, swapped, label)
            self.assertEqual("S shield" in prompt, not swapped, label)

    def test_an_entry_without_one_is_unchanged(self):
        prompts, _ = self._turnaround("Iron Man", "Front + back (2)")
        from data.cosplayers import COSPLAYERS
        self.assertIn(COSPLAYERS["Iron Man"]["costume"], prompts[1])


class GarmentSlotTests(unittest.TestCase):
    """2.0.0: corpus phrases carry {slot} words drawn from their own seed stream."""

    def test_slots_always_fill(self):
        for seed in range(400):
            for gender in ("Female", "Male"):
                prose, js = generate_character(seed, gender, {"outfit_style": "preppy"})
                outfit = _flat(js).get("outfit_description") or ""
                self.assertNotIn("{", prose + outfit, (seed, gender))

    def test_the_slot_stream_moves_no_other_field(self):
        import random
        from unittest import mock
        import nodes.identity_forge as engine
        real = engine.fill_costume

        def other_stream(template, rng, keep=None):
            return real(template, random.Random("another stream"), keep)

        for seed in range(150):
            base = _flat(generate_character(seed, "Male", {"outfit_style": "utility workwear"})[1])
            with mock.patch.object(engine, "fill_costume", other_stream):
                moved = _flat(generate_character(seed, "Male",
                                                 {"outfit_style": "utility workwear"})[1])
            base.pop("outfit_description", None)
            moved.pop("outfit_description", None)
            self.assertEqual(base, moved, seed)

    def test_a_leg_cropping_shot_drops_the_skirt_length_from_the_prose(self):
        from data.templates import COSTUME_SLOTS
        lengths = COSTUME_SLOTS["skirt_length"]
        locks = {"outfit_style": "business casual", "shot_type": "medium shot from waist up"}
        seen = 0
        for seed in range(400):
            prose, js = generate_character(seed, "Female", locks)
            outfit = _flat(js).get("outfit_description") or ""
            if "A-line" not in outfit:
                continue
            seen += 1
            self.assertTrue(any(f"{w} skirt" in outfit for w in lengths), outfit)
            self.assertFalse(any(f"{w} skirt" in prose for w in lengths), prose)
        self.assertGreater(seen, 0)

    def test_an_older_woman_draws_no_mini(self):
        for seed in range(300):
            out = _flat(generate_character(seed, "Female", {"outfit_style": "preppy",
                                                            "age": "55"})[1])
            self.assertNotIn("mini skirt", out.get("outfit_description") or "", seed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
