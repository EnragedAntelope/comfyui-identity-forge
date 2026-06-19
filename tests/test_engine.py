"""Unit tests for the IdentityForge engine and archetype node.

Pure-stdlib ``unittest`` so it runs without ComfyUI installed:

    python -m unittest discover -s tests -v
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
from nodes.identity_forge import (
    generate_character,
    _is_absent,
    _parse_archetype_json,
    _CONTROL_FIELDS,
    _EXTRA_ABSENCE,
)
from nodes.identity_forge_archetype import build_archetype_json
from data.templates import ARCHETYPES
from tests.validate_data import validate


class DataLayerTests(unittest.TestCase):
    def test_data_layer_valid(self):
        self.assertEqual(validate(), [])


class ReproducibilityTests(unittest.TestCase):
    def test_same_seed_same_output(self):
        self.assertEqual(
            generate_character(42, "Female", {}),
            generate_character(42, "Female", {}),
        )

    def test_different_seed_differs(self):
        a, _ = generate_character(42, "Female", {})
        b, _ = generate_character(43, "Female", {})
        self.assertNotEqual(a, b)

    def test_hundred_seeds_never_crash(self):
        for seed in range(100):
            prose, js = generate_character(seed, "Any", {})
            self.assertTrue(prose.endswith("."))
            json.loads(js)  # must always be valid JSON


class GenderTests(unittest.TestCase):
    def test_female_uses_she(self):
        prose, _ = generate_character(1, "Female", {})
        self.assertIn("She ", prose)
        self.assertNotIn("They ", prose)

    def test_male_uses_he(self):
        prose, _ = generate_character(1, "Male", {})
        self.assertIn("He ", prose + " ")

    def test_gender_not_randomized_away(self):
        for seed in range(20):
            _, js = generate_character(seed, "Female", {})
            self.assertEqual(json.loads(js)["_meta"]["gender"], "Female")

    def test_female_never_grows_beard(self):
        for seed in range(50):
            prose, js = generate_character(seed, "Female", {})
            facial = json.loads(js).get("Hair", {}).get("facial_hair", "clean shaven")
            self.assertEqual(facial, "clean shaven")
            self.assertNotIn("beard", prose)

    def test_male_makeup_leans_natural(self):
        for seed in range(40):
            _, js = generate_character(seed, "Male", {})
            self.assertNotIn(
                json.loads(js)["Makeup"]["makeup_style"],
                {"gothic dark makeup", "full glam", "bold glam", "heavy glam"},
            )


class ControlFieldTests(unittest.TestCase):
    def test_control_fields_absent_from_groups(self):
        _, js = generate_character(3, "Female", {})
        doc = json.loads(js)
        for group, fields in doc.items():
            if group == "_meta":
                continue
            for control in _CONTROL_FIELDS:
                self.assertNotIn(control, fields)

    def test_control_values_not_in_prose(self):
        prose, _ = generate_character(3, "Female", {}, "Natural only")
        self.assertNotIn("Natural only", prose)
        self.assertNotIn("Full spectrum", prose)


class HairScopeTests(unittest.TestCase):
    def test_natural_only_excludes_fantasy_colors(self):
        natural = set(FIELD_DEFINITIONS["hair_color"]["natural_hair_colors"])
        for seed in range(60):
            _, js = generate_character(seed, "Female", {}, "Natural only")
            self.assertIn(json.loads(js)["Hair"]["hair_color"], natural)

    def test_full_spectrum_meta_recorded(self):
        _, js = generate_character(1, "Female", {}, "Full spectrum")
        self.assertEqual(json.loads(js)["_meta"]["hair_color_scope"], "Full spectrum")

    def test_default_scope_is_natural_only(self):
        # generate_character defaults to Natural only, so random hair stays realistic.
        natural = set(FIELD_DEFINITIONS["hair_color"]["natural_hair_colors"])
        for seed in range(40):
            _, js = generate_character(seed, "Female", {})
            self.assertIn(json.loads(js)["Hair"]["hair_color"], natural)
        self.assertEqual(json.loads(js)["_meta"]["hair_color_scope"], "Natural only")


class ConstraintTests(unittest.TestCase):
    def test_requirement_no_makeup_zeroes_subfields(self):
        _, js = generate_character(7, "Female", {"makeup_style": "no makeup"})
        mk = json.loads(js)["Makeup"]
        self.assertEqual(mk["eye_makeup"], "no eyeshadow")
        self.assertEqual(mk["eyeliner"], "no eyeliner")
        self.assertEqual(mk["lashes"], "natural bare")
        self.assertEqual(mk["blush"], "no blush")

    def test_exclusion_buzzed_hair_blocks_braids(self):
        long_styles = {"side braid", "French braid", "updo", "French twist", "high ponytail"}
        for seed in range(60):
            _, js = generate_character(seed, "Female", {"hair_length": "buzzed very short"})
            self.assertNotIn(json.loads(js)["Hair"]["hair_style"], long_styles)

    def test_exclusion_athletic_has_no_bag(self):
        for seed in range(40):
            _, js = generate_character(seed, "Female", {"outfit_style": "athletic"})
            self.assertEqual(json.loads(js)["Clothing"].get("bag"), "no bag")

    def test_fitness_muscle_coherence(self):
        for seed in range(60):
            _, js = generate_character(seed, "Male", {"fitness_level": "sedentary"})
            self.assertNotIn(
                json.loads(js)["Body"]["muscle_definition"],
                {"defined", "cut", "very muscular"},
            )

    def test_locked_field_not_overwritten_by_constraint(self):
        _, js = generate_character(
            5, "Female", {"eye_makeup": "smoky black", "makeup_style": "full glam"}
        )
        self.assertEqual(json.loads(js)["Makeup"]["eye_makeup"], "smoky black")


class OutputFormatTests(unittest.TestCase):
    def test_locked_value_preserved(self):
        _, js = generate_character(9, "Female", {"eye_color": "emerald"})
        self.assertEqual(json.loads(js)["Face"]["eye_color"], "emerald")

    def test_none_excludes_optional_field(self):
        _, js = generate_character(9, "Female", {"piercings": "None"})
        self.assertNotIn("piercings", json.loads(js).get("Jewelry & Nails", {}))

    def test_none_excludes_non_optional_field(self):
        # Any field (even non-optional scene fields) can be omitted via "None".
        scene = {f: "None" for f in ("location", "lighting", "shot_type",
                                     "time_of_day", "season", "mood", "expression", "pose")}
        prose, js = generate_character(9, "Female", scene)
        self.assertNotIn("Setting & Shot", json.loads(js))
        for word in ("set in", "the framing is", "mood", "expression is"):
            self.assertNotIn(word, prose)

    def test_every_field_offers_none_in_schema(self):
        # Mirror the schema rule: each randomizable field's option list ends with None.
        from nodes.identity_forge import _CONTROL_FIELDS, _HIDDEN_FIELDS
        for name, meta in FIELD_DEFINITIONS.items():
            if name in _CONTROL_FIELDS or name in _HIDDEN_FIELDS:
                continue
            _, js = generate_character(1, "Female", {name: "None"})
            flat = {k for grp in json.loads(js).values()
                    if isinstance(grp, dict) for k in grp}
            self.assertNotIn(name, flat, f"{name} should be omittable")

    def test_json_has_meta_and_groups(self):
        _, js = generate_character(9, "Female", {})
        doc = json.loads(js)
        self.assertIn("_meta", doc)
        self.assertIn("Demographics", doc)

    def test_prose_starts_capital_ends_period(self):
        prose, _ = generate_character(9, "Female", {})
        self.assertTrue(prose[0].isupper())
        self.assertTrue(prose.endswith("."))

    def test_absence_helper(self):
        for absent in ("None", "Random", "none", "no bag", "clean shaven", "natural bare", ""):
            self.assertTrue(_is_absent(absent))
        for present in ("emerald", "side braid", "natural and unstyled", "barely there"):
            self.assertFalse(_is_absent(present))

    def test_grammar_no_they_is(self):
        prose, _ = generate_character(11, "Any", {})
        self.assertNotIn("They is", prose)
        self.assertNotIn("They has", prose)

    def test_no_doubled_article_or_noun(self):
        prose, _ = generate_character(11, "Female", {})
        self.assertNotIn(" a a ", prose)
        self.assertNotIn("salon salon", prose)

    def test_no_adjacent_word_doubling(self):
        # Scan many outputs for "word word" repeats. The only legitimate one is
        # the beauty term "no-makeup makeup".
        import re
        pat = re.compile(r"\b(\w+)\s+\1\b", re.I)
        for seed in range(150):
            gender = ("Female", "Male", "Any")[seed % 3]
            prose, _ = generate_character(seed, gender, {}, "Full spectrum")
            hits = [m.group(0).lower() for m in pat.finditer(prose)
                    if m.group(0).lower() != "makeup makeup"]
            self.assertEqual(hits, [], f"seed {seed} ({gender}): {hits}")

    def test_no_double_shot_phrasing(self):
        for seed in range(120):
            prose, _ = generate_character(seed, "Female", {})
            self.assertNotIn("shot as a shot", prose)
            self.assertNotIn("a from ", prose)


class ArchetypeTests(unittest.TestCase):
    def test_none_returns_empty(self):
        self.assertEqual(build_archetype_json("None"), "{}")

    def test_unknown_returns_empty(self):
        self.assertEqual(build_archetype_json("Nonexistent Hero"), "{}")

    def test_deterministic_for_seed(self):
        self.assertEqual(
            build_archetype_json("Dark Sorceress", 5, "Essentials"),
            build_archetype_json("Dark Sorceress", 5, "Essentials"),
        )

    def test_random_selection_is_seeded(self):
        a = json.loads(build_archetype_json("Random", 5))["_meta"]["archetype"]
        b = json.loads(build_archetype_json("Random", 5))["_meta"]["archetype"]
        self.assertEqual(a, b)
        self.assertIn(a, ARCHETYPES)

    def test_essentials_drops_person_groups(self):
        doc = json.loads(build_archetype_json("Fairy Princess", 3, "Essentials"))
        for dropped in ("Demographics", "Body", "Face"):
            self.assertNotIn(dropped, doc)
        self.assertIn("Clothing", doc)  # the look is kept

    def test_full_preset_keeps_person_groups(self):
        doc = json.loads(build_archetype_json("Fairy Princess", 3, "Full preset"))
        self.assertIn("Body", doc)
        self.assertIn("Face", doc)

    def test_costume_slots_filled_and_vary(self):
        c1 = json.loads(build_archetype_json("Fairy Princess", 1))["Clothing"]["outfit_description"]
        c2 = json.loads(build_archetype_json("Fairy Princess", 2))["Clothing"]["outfit_description"]
        self.assertNotIn("{", c1)          # every slot resolved
        self.assertNotEqual(c1, c2)        # colour/fabric varies by seed

    def test_seed_not_in_meta(self):
        self.assertNotIn("seed", json.loads(build_archetype_json("Fairy Princess", 7))["_meta"])

    def test_all_archetype_fields_valid(self):
        valid = set(FIELD_DEFINITIONS)
        for name, template in ARCHETYPES.items():
            self.assertEqual(set(template) - valid, set(), f"{name}")


class IntegrationTests(unittest.TestCase):
    def test_archetype_seeds_identity_forge(self):
        flat = _parse_archetype_json(build_archetype_json("Dark Sorceress", 0, "Full preset"))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(7, flat.get("gender", "Any"), locked)
        doc = json.loads(js)
        self.assertEqual(doc["_meta"]["gender"], "Female")
        self.assertEqual(doc["Hair"]["hair_color"], "raven black")
        self.assertEqual(doc["Makeup"]["makeup_style"], "gothic dark makeup")
        self.assertIn("age", doc["Demographics"])

    def test_essentials_archetype_randomizes_the_person(self):
        # Same archetype + different IdentityForge seeds = different people.
        flat = _parse_archetype_json(build_archetype_json("Fairy Princess", 1, "Essentials"))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        a, _ = generate_character(10, flat.get("gender", "Any"), locked)
        b, _ = generate_character(20, flat.get("gender", "Any"), locked)
        self.assertNotEqual(a, b)

    def test_archetype_changes_output(self):
        plain, _ = generate_character(7, "Female", {})
        flat = _parse_archetype_json(build_archetype_json("Fairy Princess", 0, "Full preset"))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        themed, _ = generate_character(7, flat.get("gender", "Any"), locked)
        self.assertNotEqual(plain, themed)

    def test_parser_accepts_grouped_and_flat(self):
        flat = _parse_archetype_json('{"eye_color": "emerald", "_meta": {"gender": "Male"}}')
        self.assertEqual((flat["eye_color"], flat["gender"]), ("emerald", "Male"))
        grouped = _parse_archetype_json('{"Face": {"nose": "Roman"}, "_meta": {"gender": "Male"}}')
        self.assertEqual((grouped["nose"], grouped["gender"]), ("Roman", "Male"))

    def test_parser_handles_garbage(self):
        self.assertEqual(_parse_archetype_json("not json {{"), {})
        self.assertEqual(_parse_archetype_json(""), {})
        self.assertEqual(_parse_archetype_json("[1,2,3]"), {})

    def test_round_trip_identity_forge_json(self):
        _, js = generate_character(3, "Male", {"eye_color": "amber"})
        flat = _parse_archetype_json(js)
        self.assertEqual((flat["eye_color"], flat["gender"]), ("amber", "Male"))


class AccessoryDensityTests(unittest.TestCase):
    def _present_counts(self, density, n=300):
        present = {f: 0 for f in _EXTRA_ABSENCE}
        for seed in range(n):
            gender = ("Female", "Male", "Any")[seed % 3]
            _, js = generate_character(seed, gender, {}, "Full spectrum",
                                       accessory_density=density)
            flat = {k: v for grp in json.loads(js).values()
                    if isinstance(grp, dict) for k, v in grp.items()}
            for field, (absent, _) in _EXTRA_ABSENCE.items():
                if not _is_absent(flat.get(field, absent)):
                    present[field] += 1
        return present

    def test_absence_values_are_valid_options(self):
        for field, (absent, _) in _EXTRA_ABSENCE.items():
            opts = set(FIELD_DEFINITIONS[field]["female_options"]) | set(
                FIELD_DEFINITIONS[field]["male_options"])
            self.assertIn(absent, opts, field)
            self.assertTrue(_is_absent(absent), f"{field}={absent!r} should read as absent")

    def test_none_strips_all_extras(self):
        self.assertEqual(sum(self._present_counts("None", 120).values()), 0)

    def test_density_is_monotonic(self):
        # More "stuff" as density rises.
        total = {d: sum(self._present_counts(d).values())
                 for d in ("Minimal", "Balanced", "Maximal")}
        self.assertLess(total["Minimal"], total["Balanced"])
        self.assertLess(total["Balanced"], total["Maximal"])

    def test_balanced_tames_the_bag(self):
        # The original complaint: ~90% of characters had a bag. Balanced << that.
        present = self._present_counts("Balanced", 300)
        self.assertLess(present["bag"], 150)  # < 50%

    def test_locked_extra_survives_density(self):
        _, js = generate_character(1, "Female", {"bag": "canvas tote"},
                                   accessory_density="None")
        self.assertEqual(json.loads(js)["Clothing"]["bag"], "canvas tote")


class LocationAndPoseTests(unittest.TestCase):
    def test_indoor_setting_excludes_outdoor(self):
        from data.fields import OUTDOOR_LOCATIONS
        for seed in range(60):
            _, js = generate_character(seed, "Female", {}, location_setting="Indoor")
            self.assertNotIn(json.loads(js)["Setting & Shot"]["location"], OUTDOOR_LOCATIONS)

    def test_outdoor_setting_only_outdoor(self):
        from data.fields import OUTDOOR_LOCATIONS
        for seed in range(60):
            _, js = generate_character(seed, "Female", {}, location_setting="Outdoor")
            self.assertIn(json.loads(js)["Setting & Shot"]["location"], OUTDOOR_LOCATIONS)

    def test_location_setting_not_in_json(self):
        d = json.loads(generate_character(1, "Female", {})[1])
        for group, fields in d.items():
            if isinstance(fields, dict):
                self.assertNotIn("location_setting", fields)

    def test_pose_in_output(self):
        _, js = generate_character(3, "Female", {})
        self.assertIn("pose", json.loads(js)["Setting & Shot"])

    def test_pose_grammar_for_they(self):
        for seed in range(60):
            prose, _ = generate_character(seed, "Any", {})
            self.assertNotIn("They is ", prose)


class UserOptionsTests(unittest.TestCase):
    def test_merges_valid_and_rejects_protected(self):
        import copy, json as _json, tempfile
        from pathlib import Path
        from data.user_options import apply_user_options
        fd = {k: {"female_options": list(v["female_options"]),
                  "male_options": list(v["male_options"])}
              for k, v in FIELD_DEFINITIONS.items()}
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text(_json.dumps({"fields": {
                "ethnicity": ["Atlantean"],
                "outfit_style": ["rejected"],     # protected
                "gender": ["rejected"],           # protected
            }}))
            apply_user_options(fd, path=f)
        self.assertIn("Atlantean", fd["ethnicity"]["female_options"])
        self.assertNotIn("rejected", fd["outfit_style"]["female_options"])
        self.assertNotIn("rejected", fd["gender"]["female_options"])

    def test_missing_or_malformed_file_is_safe(self):
        import tempfile
        from pathlib import Path
        from data.user_options import apply_user_options
        self.assertEqual(apply_user_options({}, path=Path("/no/such/file.json")), 0)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text("{ not valid json")
            self.assertEqual(apply_user_options({}, path=f), 0)

    def test_outfits_section_registers_style_and_text(self):
        import json as _json, tempfile
        from pathlib import Path
        from data.user_options import apply_user_options
        fd = {"outfit_style": {"female_options": ["casual"], "male_options": ["casual"]}}
        outfits = {}  # stand-in for OUTFIT_DESCRIPTIONS
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text(_json.dumps({"outfits": {
                "spacesuit": {"unisex": ["a white EVA suit"], "male": ["a bulky exosuit"]},
                "empty style": {"unisex": []},        # no usable text — must be skipped
            }}))
            added = apply_user_options(fd, outfits, path=f)
        # New style registered in the dropdown (both gender pools) with its text.
        self.assertIn("spacesuit", fd["outfit_style"]["female_options"])
        self.assertIn("spacesuit", fd["outfit_style"]["male_options"])
        self.assertEqual(outfits["spacesuit"]["unisex"], ["a white EVA suit"])
        self.assertEqual(outfits["spacesuit"]["male"], ["a bulky exosuit"])
        self.assertEqual(added, 2)
        # A style with no garment text never reaches the dropdown.
        self.assertNotIn("empty style", fd["outfit_style"]["female_options"])
        self.assertNotIn("empty style", outfits)

    def test_outfits_ignored_without_descriptions_map(self):
        # Called the old way (no OUTFIT_DESCRIPTIONS), the outfits section is a no-op.
        import json as _json, tempfile
        from pathlib import Path
        from data.user_options import apply_user_options
        fd = {"outfit_style": {"female_options": ["casual"], "male_options": ["casual"]}}
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text(_json.dumps({"outfits": {"spacesuit": {"unisex": ["a suit"]}}}))
            self.assertEqual(apply_user_options(fd, path=f), 0)
        self.assertNotIn("spacesuit", fd["outfit_style"]["female_options"])


class WardrobeAndCostumeTests(unittest.TestCase):
    _FEMININE = ("gown", "sundress", "pencil skirt", "ball gown", "cocktail dress",
                 "maxi dress", "swing dress", "shirt dress", "sweater dress")

    def test_male_outfits_match_gender_by_default(self):
        for seed in range(120):
            _, js = generate_character(seed, "Male", {})
            outfit = json.loads(js)["Clothing"]["outfit_description"]
            self.assertFalse(any(w in outfit for w in self._FEMININE), outfit)

    def test_feminine_wardrobe_lets_a_man_wear_a_gown(self):
        seen_gown = any(
            "gown" in json.loads(generate_character(s, "Male", {"outfit_style": "evening formal"},
                                                     wardrobe="Feminine")[1])["Clothing"]["outfit_description"]
            for s in range(40)
        )
        self.assertTrue(seen_gown)

    def test_costume_outfit_description_is_preserved(self):
        costume = "frilly French maid uniform with a lace apron"
        _, js = generate_character(1, "Female", {"outfit_description": costume,
                                                 "outfit_style": "smart casual"})
        self.assertEqual(json.loads(js)["Clothing"]["outfit_description"], costume)

    def test_wardrobe_recorded_in_meta(self):
        _, js = generate_character(1, "Female", {}, wardrobe="Any")
        self.assertEqual(json.loads(js)["_meta"]["wardrobe"], "Any")


class SkinToneBiasTests(unittest.TestCase):
    def test_irish_skews_fair_but_stays_diverse(self):
        from data.fields import SKIN_TONE_BANDS
        fair = set(SKIN_TONE_BANDS["fair"])
        in_band = sum(
            json.loads(generate_character(s, "Female", {"ethnicity": "Irish"})[1])["Body"]["skin_tone"] in fair
            for s in range(200)
        )
        self.assertGreater(in_band, 140)   # strong bias
        self.assertLess(in_band, 200)      # but not absolute — diversity preserved

    def test_locked_skin_tone_overrides_bias(self):
        _, js = generate_character(1, "Female", {"ethnicity": "Irish", "skin_tone": "deep ebony"})
        self.assertEqual(json.loads(js)["Body"]["skin_tone"], "deep ebony")


class CostumeArchetypeTests(unittest.TestCase):
    def test_costume_archetype_keeps_its_outfit(self):
        flat = _parse_archetype_json(build_archetype_json("French Maid", 0, "Essentials"))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, flat.get("gender", "Any"), locked)
        outfit = json.loads(js)["Clothing"]["outfit_description"]
        self.assertIn("maid", outfit)

    def test_at_least_50_archetypes(self):
        self.assertGreaterEqual(len(ARCHETYPES), 50)

    def test_identity_forge_json_has_no_seed(self):
        _, js = generate_character(5, "Female", {})
        self.assertNotIn("seed", json.loads(js)["_meta"])


class NewOptionTests(unittest.TestCase):
    def test_eighteen_is_an_age_option(self):
        self.assertIn("18", FIELD_DEFINITIONS["age"]["female_options"])

    def test_new_outfit_styles_present(self):
        styles = set(FIELD_DEFINITIONS["outfit_style"]["female_options"])
        self.assertTrue({"preppy", "vintage retro", "loungewear"} <= styles)


if __name__ == "__main__":
    unittest.main(verbosity=2)
