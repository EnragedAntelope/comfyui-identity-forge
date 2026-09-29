"""1.5.1: regressions from the maintainer's 33 flagged renders (idforge-927-concern)."""
import json
import re
import unittest

from data.constraints import lock_clash
from data.fields import ETHNICITY_REGION, OUTFIT_DESCRIPTIONS, PATTERN_ADJECTIVES, SKIN_TONE_BANDS
from data.templates import ARCHETYPES
from nodes.identity_forge import _NEAR_BAND, generate_character
from nodes.identity_forge_archetype import build_archetype_json
from tests.preview_cosplayer import render


def _flat(js):
    return {k: v for g in json.loads(js).values() if isinstance(g, dict) for k, v in g.items()}


class EncasedBodyTests(unittest.TestCase):
    """A masked, fully shelled character voices no randomized human body (#00687, #00690)."""

    def test_robots_carry_no_human_body(self):
        for name in ("Megatron", "Chopper", "R2-D2", "Iron Man"):
            for seed in (0, 3, 7):
                prose, js = render(name, "", "Costume only", seed)
                flat = _flat(js)
                for field in ("age", "ethnicity", "skin_tone", "fitness_level", "bust",
                              "waist", "hips", "shoulder_width", "nails"):
                    self.assertNotIn(field, flat, f"{name}@{seed}: {field}")
                self.assertNotRegex(prose, r"year-old|physique|skin\b", f"{name}@{seed}")

    def test_scale_phrase_is_an_appositive(self):
        prose, _ = render("Megatron", "", "Full character", 3)
        self.assertIn("a man, colossal and over thirty feet tall, with a stocky build.", prose)
        prose, _ = render("Megatron", "", "Costume only", 3)
        self.assertIn("a man, colossal and over thirty feet tall.", prose)


class ArchetypeLockClashTests(unittest.TestCase):
    """List picks agree with each other; the validator gates fixed values (#00669, #00790)."""

    def test_clash_helper_reads_both_directions(self):
        self.assertTrue(lock_clash("lighting", "golden hour sunlight",
                                   {"location": "farmers market indoor stall"}))
        self.assertTrue(lock_clash("location", "farmers market indoor stall",
                                   {"lighting": "golden hour sunlight"}))
        self.assertFalse(lock_clash("lighting", "warm incandescent lamp glow",
                                    {"location": "farmers market indoor stall"}))

    def test_list_picks_never_pair_a_forbidden_scene(self):
        for name in ("Astronomer", "1980s Action Star", "Rude Boy", "Kabuki Actor", "Volcanologist"):
            for seed in range(120):
                doc = json.loads(build_archetype_json(name, seed, "Full preset"))
                scene = doc.get("Setting & Shot", {})
                looks = [scene]
                for variant in (doc["_meta"].get("variants") or {}).values():
                    looks.append({**scene, **variant})
                for look in looks:
                    if "location" in look and "lighting" in look:
                        self.assertFalse(
                            lock_clash("lighting", look["lighting"], {"location": look["location"]}),
                            f"{name}@{seed}: {look['location']} x {look['lighting']}")


class SkinEthnicityTests(unittest.TestCase):
    """No tone outside the ethnicity's near band, locked or not (#00537, #00653, #00780)."""

    def test_no_draw_crosses_the_spectrum(self):
        for locks in ({}, {"skin_tone": "pale"}, {"skin_tone": "ebony"}):
            for seed in range(300):
                flat = _flat(generate_character(seed, "Any", dict(locks))[1])
                band = ETHNICITY_REGION.get(flat.get("ethnicity", ""))
                if band and flat.get("skin_tone") in SKIN_TONE_BANDS["fair"] + SKIN_TONE_BANDS["dark"]:
                    self.assertIn(flat["skin_tone"], _NEAR_BAND[band],
                                  f"{locks}@{seed}: {flat['ethnicity']} / {flat['skin_tone']}")


class RenderWordingTests(unittest.TestCase):
    """Words the model misreads stay out of the generated wardrobe (#00636, #00816)."""

    def test_no_stray_tie_token(self):
        allowed = re.compile(r"\b(?:bow|silk|slim|knitted|grenadine|wool|skinny)? ?tie\b")
        for style, buckets in OUTFIT_DESCRIPTIONS.items():
            for phrases in buckets.values():
                for p in phrases:
                    self.assertNotRegex(p, r"tie-|tie (?:waist|back)|\bno tie\b", p)
                    if re.search(r"\btie\b", p):
                        self.assertRegex(p, allowed, p)
        self.assertNotIn("tie", PATTERN_ADJECTIVES["tie-dye"])

    def test_behind_the_ear_and_bleached_brows_are_not_drawn_at_random(self):
        for seed in range(600):
            flat = _flat(generate_character(seed, "Any", {})[1])
            self.assertNotEqual(flat.get("tattoo_placement"), "behind one ear", seed)
            self.assertNotEqual(flat.get("eyebrows"), "bleached", seed)


class OutfitNoneTests(unittest.TestCase):
    """outfit_style None mentions no clothing at all (#00525, #00542)."""

    def test_none_voices_no_clothing(self):
        for seed in range(200):
            prose, js = generate_character(seed, "Any", {"outfit_style": "None"})
            self.assertNotRegex(prose, r"\b(?:Carrying|carrying|accessorized)\b", seed)
            flat = _flat(js)
            for field in ("bag", "accessories", "legwear", "footwear", "outerwear",
                          "clothing_color", "clothing_pattern", "outfit_description"):
                self.assertIn(flat.get(field, "None"),
                              ("None", "", "no bag", "no accessories", "no visible legwear",
                               "no outerwear"), f"{seed}: {field}={flat.get(field)}")
            placement = flat.get("tattoo_placement")
            self.assertIn(placement, (None, "across the back of one hand", "on the inner wrist",
                                      "on the side of the neck"), seed)


class CoinFlipTests(unittest.TestCase):
    """Gender-neutral roles draw either gender under "Any" (maintainer, 1.5.1)."""

    def test_a_variant_archetype_has_both_looks(self):
        for name, a in ARCHETYPES.items():
            if a.get("variants"):
                self.assertEqual(set(a["variants"]), {"Female", "Male"}, name)

    def test_neutral_roles_render_both_genders(self):
        from nodes import identity_forge as IF
        for name in ("Firefighter", "Teacher", "Lifeguard", "Samurai", "Scientist",
                     "Gondolier", "Aso-Ebi with Gele"):
            self.assertEqual(ARCHETYPES[name].get("gender", "Any"), "Any", name)
            seen = set()
            for seed in range(40):
                doc = build_archetype_json(name, seed, "Essentials")
                out = IF.IdentityForge.execute(seed=seed, gender="Any", archetype_json=doc)
                seen.add(json.loads(out.args[1])["_meta"]["gender"])
            self.assertEqual(seen, {"Female", "Male"}, name)


class GenderedCostumeTests(unittest.TestCase):
    """A costume with no top has a Female look beside it (#00769)."""

    def test_bare_chested_archetypes_dress_a_woman(self):
        for name in ("Lifeguard", "Surfer", "Boxer", "Pro Wrestler", "Sumo Wrestler",
                     "Berserker Barbarian"):
            variants = ARCHETYPES[name].get("variants") or {}
            self.assertIn("outfit_description", variants.get("Female", {}), name)
            self.assertNotEqual(variants["Female"]["outfit_description"],
                                variants["Male"]["outfit_description"], name)


class HandPropPoseTests(unittest.TestCase):
    """A costume that holds something takes no both-hands pose (floating clipboard, 1.5.1)."""

    def test_costume_prop_occupies_a_hand(self):
        from data.fields import HAND_OCCUPIED_POSES
        from nodes.identity_forge import _HAND_PROP_RE
        for text in ("a clipboard in one hand", "a helmet held under one arm",
                     "smart clothing, holding a rolled diploma", "honeycomb held up"):
            self.assertRegex(text, _HAND_PROP_RE)
        for text in ("trousers held up by braces", "a belt carrying a sword",
                     "a clip holding the hair", "a bamboo muzzle held across the mouth"):
            self.assertNotRegex(text, _HAND_PROP_RE)
        from nodes import identity_forge as IF
        for seed in range(30):
            doc = build_archetype_json("Personal Trainer", seed, "Essentials")
            out = IF.IdentityForge.execute(seed=seed, archetype_json=doc)
            pose = _flat(out.args[1]).get("pose")
            self.assertNotIn(pose, HAND_OCCUPIED_POSES, seed)


class BodyIsTheLookTests(unittest.TestCase):
    """Essentials keeps the build when the costume states it (a slim sumo wrestler)."""

    def test_essentials_keeps_a_stated_build(self):
        from data.templates import BODY_IS_THE_LOOK
        for name in BODY_IS_THE_LOOK:
            self.assertIn("body_type", ARCHETYPES[name], name)
            flat = _flat(build_archetype_json(name, 0, "Essentials"))
            self.assertEqual(flat.get("body_type"), ARCHETYPES[name]["body_type"], name)
        self.assertNotIn("body_type", _flat(build_archetype_json("Chef", 0, "Essentials")))


if __name__ == "__main__":
    unittest.main()
