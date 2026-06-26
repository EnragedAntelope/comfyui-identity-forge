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
    merge_preset_documents,
    resolve_locked_fields,
    _is_absent,
    _parse_archetype_json,
    _CONTROL_FIELDS,
    _EXTRA_ABSENCE,
    _SET_ALL_OFF,
    _SET_ALL_NONE,
)
from nodes.identity_forge import _COSPLAY_LABEL_KEY, _COVERS_FACE_KEY, _MODIFIERS_KEY
from nodes.identity_forge_archetype import build_archetype_json
from nodes.identity_forge_cosplayer import (
    build_cosplayer_json, _MASK_DEFAULT, _MASK_OFF,
)
from nodes.identity_forge_modifier import build_modifier_json, _parse_modifier_text
from data.templates import ARCHETYPES
from data.cosplayers import COSPLAYERS, get_cosplayer_names
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

    def test_female_override_drops_male_archetype_beard(self):
        # Regression: a male archetype (Werewolf Hunter) locks facial_hair="short
        # beard"; forcing gender=Female downstream must NOT keep the beard. The
        # gender gate has to hold for locked/injected values, not just randomized
        # ones (the JS widget and the randomizer enforce it, the engine must too).
        flat = _parse_archetype_json(build_archetype_json("Werewolf Hunter", 0, "Essentials"))
        self.assertEqual(flat.get("facial_hair"), "short beard")  # archetype carries it
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(30):
            prose, js = generate_character(seed, "Female", locked)
            facial = json.loads(js).get("Hair", {}).get("facial_hair", "clean shaven")
            self.assertEqual(facial, "clean shaven", f"seed {seed}")
            self.assertNotIn("beard", prose, f"seed {seed}")

    def test_any_gender_keeps_locked_beard(self):
        # The gate is gender-specific: under "Any", facial hair stays valid and a
        # locked beard must survive (Any's pool is the union of both genders).
        _, js = generate_character(1, "Any", {"facial_hair": "full beard"})
        self.assertEqual(json.loads(js)["Hair"]["facial_hair"], "full beard")

    def test_male_makeup_leans_natural(self):
        for seed in range(40):
            _, js = generate_character(seed, "Male", {})
            self.assertNotIn(
                json.loads(js)["Makeup"]["makeup_style"],
                {"gothic dark makeup", "full glam", "bold glam", "heavy glam"},
            )

    # Feminine-coded values a randomly generated Male must never pick up.
    _MALE_FORBIDDEN = {
        "makeup_style": None,  # must be "no makeup" (bare-faced)
        "lips_makeup": None,   # cleared by the no-makeup cascade
        "lip_color": {"coral", "berry", "red", "mauve", "plum"},
        "nails": {"red polish", "pink polish", "coral polish", "mauve polish",
                  "french manicure", "stiletto nails", "coffin nails", "almond nails",
                  "chrome nails", "gel nails", "colorful nail art"},
        "earrings": {"chandelier earrings", "long drop earrings", "tassel earrings",
                     "pearl studs", "large bold gold hoops", "clip-on pearl earrings"},
        "necklace": {"pearl necklace", "pearl strand", "choker", "velvet choker",
                     "statement necklace", "collar necklace", "locket necklace"},
        "hair_style": {"space buns", "pigtails", "updo", "French twist",
                       "crown braid", "fishtail braid", "half up half down"},
        "hair_length": {"chin length bob", "waist length", "hip length"},
        "hair_highlights": {"subtle balayage", "face framing", "ombre", "sombre"},
        "eyebrows": {"thin and arched", "pencil thin", "feathered",
                     "well defined and arched", "bold statement brows", "laminated brows"},
        "lips": {"bow-shaped", "heart-shaped", "petite and defined"},
        "eye_size": {"doe-like"},
        "bust": {"large"},
    }

    def test_male_random_never_feminine(self):
        # Regression: a Male with default (Match gender) wardrobe must never get
        # random feminine makeup, lip colour, nail polish, jewellery, or hairstyle.
        for seed in range(60):
            doc = json.loads(generate_character(seed, "Male", {}, wardrobe="Match gender")[1])
            flat = {k: v for g in doc.values() if isinstance(g, dict) for k, v in g.items()}
            self.assertEqual(flat.get("makeup_style", "no makeup"), "no makeup", f"seed {seed}")
            for field, forbidden in self._MALE_FORBIDDEN.items():
                if forbidden and field in flat:
                    self.assertNotIn(flat[field], forbidden, f"{field} seed {seed}")

    def test_male_prose_has_no_makeup_or_polish(self):
        for seed in range(40):
            prose = generate_character(seed, "Male", {})[0].lower()
            # "polished" (e.g. "polished dress shoes") is an outfit word, not nail
            # polish — match "polish nails" so the check stays specific.
            for phrase in ("eyeshadow", "eyeliner", "mascara", "lipstick", "blush",
                           "polish nails"):
                self.assertNotIn(phrase, prose, f"'{phrase}' in male prose seed {seed}")

    def test_male_stays_bare_faced_even_when_locked(self):
        # makeup_style is gender-gated: a female-only value injected on a Male is
        # dropped, and the masculine default keeps him bare-faced.
        _, js = generate_character(1, "Male", {"makeup_style": "gothic dark makeup"})
        self.assertEqual(json.loads(js)["Makeup"]["makeup_style"], "no makeup")

    def test_male_archetype_makeup_dropped(self):
        # The Vampire Noble archetype (a gothic Male) renders bare-faced as a Male;
        # its makeup is intended for the Female crossplay rendering.
        flat = _parse_archetype_json(build_archetype_json("Vampire Noble", 0, "Full preset"))
        self.assertEqual(flat.get("makeup_style"), "gothic dark makeup")
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, "Male", locked)
        self.assertEqual(json.loads(js)["Makeup"]["makeup_style"], "no makeup")

    def test_male_locked_feminine_value_is_preserved(self):
        # The masculine defaults govern only the RANDOM fill: a value locked by a
        # user/archetype/cosplayer signature (same-pool fields like hair_style)
        # is respected, so faithful crossplay (a man cosplaying a pigtailed
        # character) still works.
        for field, value in (("hair_style", "pigtails"), ("necklace", "pearl necklace"),
                             ("nails", "red polish")):
            _, js = generate_character(2, "Male", {field: value})
            flat = {k: v for g in json.loads(js).values() if isinstance(g, dict)
                    for k, v in g.items()}
            self.assertEqual(flat.get(field), value, field)


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


class CosplayerTests(unittest.TestCase):
    def _locked_and_label(self, character, seed=0, look_level="Costume only"):
        flat = _parse_archetype_json(build_cosplayer_json(character, seed, look_level))
        label = flat.pop(_COSPLAY_LABEL_KEY, None)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        return locked, label, flat

    def test_none_returns_empty(self):
        self.assertEqual(build_cosplayer_json("None"), "{}")

    def test_unknown_returns_empty(self):
        self.assertEqual(build_cosplayer_json("Definitely Not A Character"), "{}")

    def test_deterministic_for_seed(self):
        self.assertEqual(
            build_cosplayer_json("2B", 5, "Costume only"),
            build_cosplayer_json("2B", 5, "Costume only"),
        )

    def test_costume_only_omits_physique(self):
        doc = json.loads(build_cosplayer_json("2B", 0, "Costume only"))
        for dropped in ("Demographics", "Body", "Face"):
            self.assertNotIn(dropped, doc)
        self.assertIn("Clothing", doc)  # the costume is kept
        self.assertIn("Hair", doc)      # signature look is kept

    def test_full_character_includes_physique(self):
        doc = json.loads(build_cosplayer_json("2B", 0, "Full character"))
        self.assertIn("Body", doc)
        self.assertEqual(doc["Body"]["skin_tone"], "porcelain")

    def test_costume_drives_outfit_description(self):
        doc = json.loads(build_cosplayer_json("2B", 0, "Costume only"))
        self.assertEqual(
            doc["Clothing"]["outfit_description"], COSPLAYERS["2B"]["costume"]
        )

    def test_meta_records_character_and_franchise(self):
        meta = json.loads(build_cosplayer_json("2B", 0))["_meta"]
        self.assertEqual(meta["cosplay_of"], "2B")
        self.assertEqual(meta["franchise"], "NieR: Automata")
        self.assertEqual(meta["look_level"], "Costume only")

    def test_random_any_is_seeded_and_valid(self):
        a = json.loads(build_cosplayer_json("Random — any", 5))["_meta"]["cosplay_of"]
        b = json.loads(build_cosplayer_json("Random — any", 5))["_meta"]["cosplay_of"]
        self.assertEqual(a, b)
        self.assertIn(a, COSPLAYERS)

    def test_random_female_scopes_to_female_sources(self):
        name = json.loads(build_cosplayer_json("Random — female", 3))["_meta"]["cosplay_of"]
        self.assertEqual(COSPLAYERS[name]["gender"], "Female")

    def test_random_male_scopes_to_male_sources(self):
        name = json.loads(build_cosplayer_json("Random — male", 3))["_meta"]["cosplay_of"]
        self.assertEqual(COSPLAYERS[name]["gender"], "Male")

    def test_random_scope_limits_to_category(self):
        from data.cosplayers import get_cosplayer_category
        for seed in range(8):
            name = json.loads(
                build_cosplayer_json("Random — any", seed, random_scope="Marvel")
            )["_meta"]["cosplay_of"]
            self.assertEqual(get_cosplayer_category(COSPLAYERS[name]["franchise"]), "Marvel")

    def test_random_scope_combines_with_gender(self):
        from data.cosplayers import get_cosplayer_category
        name = json.loads(
            build_cosplayer_json("Random — female", 3, random_scope="DC")
        )["_meta"]["cosplay_of"]
        self.assertEqual(COSPLAYERS[name]["gender"], "Female")
        self.assertEqual(get_cosplayer_category(COSPLAYERS[name]["franchise"]), "DC")

    def test_eyes_override_renders_free_text(self):
        # A canonical non-standard eye colour ("eyes" override) is voiced verbatim,
        # without being a selectable option on the main node's eye_color dropdown, and
        # the otherwise-random eye_shape word is suppressed so it reads clean.
        doc = json.loads(build_cosplayer_json("Sukuna", 0))
        self.assertEqual(doc["Face"]["eye_color"], "crimson")
        self.assertEqual(doc["Face"]["eye_shape"], "None")  # random shape locked out
        locked, label, _ = self._locked_and_label("Sukuna")
        for person_seed in range(5):
            prose, out = generate_character(person_seed, "Male", locked, cosplay_label=label)
            self.assertIn("crimson eyes", prose)   # no shape word between colour and "eyes"
            self.assertNotIn("eye_shape", out)     # locked-absent, dropped from the JSON

    def test_random_unknown_pool_returns_empty(self):
        # A Random pick over an empty pool must still degrade gracefully to "{}".
        from nodes.identity_forge_cosplayer import _resolve_character
        import random
        self.assertIsNone(_resolve_character("Random — nonexistent", random.Random(0)))

    def test_end_to_end_prose_has_cosplay_prefix(self):
        locked, label, _ = self._locked_and_label("2B")
        prose, js = generate_character(42, "Female", locked, cosplay_label=label)
        self.assertTrue(prose.startswith("Cosplaying as 2B (NieR: Automata): "))
        self.assertEqual(json.loads(js)["_meta"]["cosplay_of"], "2B (NieR: Automata)")

    def test_costume_only_randomizes_the_person(self):
        # Same character + different IdentityForge seeds = different people.
        locked, label, _ = self._locked_and_label("Ada Wong")
        a, _ = generate_character(10, "Female", locked, cosplay_label=label)
        b, _ = generate_character(20, "Female", locked, cosplay_label=label)
        self.assertNotEqual(a, b)

    def test_crossplay_male_wears_female_costume_without_contradiction(self):
        # A man cosplaying 2B: the costume + unisex signature survive the gender
        # gate, the prose uses "He", and no female-only trait leaks in.
        locked, label, _ = self._locked_and_label("2B")
        for seed in range(20):
            prose, js = generate_character(seed, "Male", locked, cosplay_label=label)
            doc = json.loads(js)
            self.assertEqual(doc["_meta"]["gender"], "Male")
            self.assertIn("He ", prose + " ")
            self.assertEqual(
                doc["Clothing"]["outfit_description"], COSPLAYERS["2B"]["costume"]
            )
            self.assertEqual(doc["Hair"]["hair_color"], "platinum blonde")

    def test_covers_face_meta_flag(self):
        # Masked character carries covers_face; an unmasked one does not.
        self.assertTrue(json.loads(build_cosplayer_json("Spider-Man", 0))["_meta"]["covers_face"])
        self.assertFalse(json.loads(build_cosplayer_json("2B", 0))["_meta"]["covers_face"])

    def test_covers_face_suppresses_face_hair_and_makeup(self):
        # A full-mask character: the randomized face/hair/makeup are dropped from
        # both prose and JSON so only the costume (with its mask) is described.
        flat = _parse_archetype_json(build_cosplayer_json("Spider-Man", 0))
        covers = bool(flat.pop(_COVERS_FACE_KEY, None))
        self.assertTrue(covers)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(10):
            prose, js = generate_character(seed, "Male", locked, covers_face=covers)
            doc = json.loads(js)
            for group in ("Face", "Hair", "Makeup"):
                self.assertNotIn(group, doc, f"{group} should be suppressed")
            self.assertNotIn("His face", prose)
            self.assertNotIn("His hair", prose)
            # The costume is present with the mask re-attached (default mode).
            entry = COSPLAYERS["Spider-Man"]
            self.assertEqual(
                doc["Clothing"]["outfit_description"],
                f"{entry['costume']}, {entry['mask']}",
            )

    def test_unmasked_character_keeps_face_and_hair(self):
        # Without covers_face the face/hair are described as usual.
        flat = _parse_archetype_json(build_cosplayer_json("Tony Stark", 0))
        self.assertNotIn(_COVERS_FACE_KEY, flat)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(1, "Male", locked, covers_face=False)
        self.assertIn("Hair", json.loads(js))

    def test_unmask_drops_mask_and_reveals_face(self):
        # 'Unmask' clears covers_face and omits the mask text so the randomized
        # head/hair show under the suit; 'Default' keeps the mask and suppresses.
        entry = COSPLAYERS["Spider-Man"]
        default = json.loads(build_cosplayer_json("Spider-Man", 0, mask_mode=_MASK_DEFAULT))
        unmasked = json.loads(build_cosplayer_json("Spider-Man", 0, mask_mode=_MASK_OFF))

        self.assertTrue(default["_meta"]["covers_face"])
        self.assertEqual(
            default["Clothing"]["outfit_description"],
            f"{entry['costume']}, {entry['mask']}",
        )

        self.assertFalse(unmasked["_meta"]["covers_face"])
        self.assertEqual(unmasked["Clothing"]["outfit_description"], entry["costume"])
        self.assertNotIn(entry["mask"], unmasked["Clothing"]["outfit_description"])

        # Run unmasked through the engine: face/hair are no longer suppressed.
        flat = _parse_archetype_json(json.dumps(unmasked))
        self.assertNotIn(_COVERS_FACE_KEY, flat)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(1, "Male", locked, covers_face=False)
        self.assertIn("Hair", json.loads(js))

    def test_unmask_is_noop_for_face_visible_character(self):
        # A character with no mask is identical in Default and Unmask modes.
        self.assertEqual(
            build_cosplayer_json("2B", 0, mask_mode=_MASK_DEFAULT),
            build_cosplayer_json("2B", 0, mask_mode=_MASK_OFF),
        )

    def test_every_covers_face_entry_has_a_mask(self):
        for name, entry in COSPLAYERS.items():
            if entry.get("covers_face"):
                self.assertTrue(entry.get("mask"), f"{name} missing mask")

    def test_all_cosplayer_fields_valid(self):
        valid = set(FIELD_DEFINITIONS)
        for name, entry in COSPLAYERS.items():
            for section in ("signature", "physique"):
                self.assertEqual(
                    set(entry.get(section, {})) - valid, set(), f"{name}.{section}"
                )

    def test_starter_set_size(self):
        self.assertGreaterEqual(len(get_cosplayer_names()), 50)


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


class PresetMergeTests(unittest.TestCase):
    def test_empty_own_passes_upstream_through(self):
        # A node set to "None" emits "{}"; the upstream must pass through unchanged.
        upstream = build_archetype_json("Knight", 0)
        self.assertEqual(
            json.loads(merge_preset_documents(upstream, "{}")), json.loads(upstream)
        )
        self.assertEqual(merge_preset_documents("", "{}"), "{}")

    def test_empty_upstream_returns_own(self):
        own = build_cosplayer_json("2B", 0)
        self.assertEqual(json.loads(merge_preset_documents("", own)), json.loads(own))

    def test_downstream_wins_on_overlap(self):
        upstream = json.dumps({
            "_meta": {"gender": "Male", "lock_level": "Essentials"},
            "Hair": {"hair_color": "dark brown", "hair_length": "long"},
        })
        own = json.dumps({
            "_meta": {"gender": "Female", "cosplay_of": "Hero"},
            "Hair": {"hair_color": "platinum blonde"},
        })
        merged = json.loads(merge_preset_documents(upstream, own))
        # Own (downstream) wins where keys overlap, in _meta and in groups...
        self.assertEqual(merged["_meta"]["gender"], "Female")
        self.assertEqual(merged["_meta"]["cosplay_of"], "Hero")
        self.assertEqual(merged["Hair"]["hair_color"], "platinum blonde")
        # ...but non-overlapping upstream values survive.
        self.assertEqual(merged["_meta"]["lock_level"], "Essentials")
        self.assertEqual(merged["Hair"]["hair_length"], "long")

    def test_merged_groups_follow_canonical_order(self):
        upstream = json.dumps({"Clothing": {"outfit_description": "x"}})
        own = json.dumps({"Hair": {"hair_color": "red"}})
        keys = list(json.loads(merge_preset_documents(upstream, own)))
        self.assertEqual(keys, ["Hair", "Clothing"])  # Hair precedes Clothing

    def test_malformed_inputs_yield_valid_json(self):
        self.assertEqual(merge_preset_documents("not json", "also not"), "{}")

    def test_chained_archetype_and_cosplayer(self):
        # Wire Archetype -> Cosplayer: the cosplayer (downstream) wins on overlap
        # and its cosplay label survives into the parsed character.
        upstream = build_archetype_json("Knight", 0, "Full preset")
        chained = build_cosplayer_json("2B", 0)
        merged = merge_preset_documents(upstream, chained)
        flat = _parse_archetype_json(merged)
        self.assertEqual(flat.get(_COSPLAY_LABEL_KEY), "2B (NieR: Automata)")
        self.assertEqual(flat.get("hair_color"), "platinum blonde")  # cosplayer's
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, "Female", locked)
        self.assertEqual(
            json.loads(js)["Clothing"]["outfit_description"], COSPLAYERS["2B"]["costume"]
        )

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


class UserPresetExtensionTests(unittest.TestCase):
    """user_options.json 'archetypes' / 'cosplayers' sections (survive git pull)."""

    def _write(self, payload):
        import json as _json, tempfile
        from pathlib import Path
        d = tempfile.mkdtemp()
        f = Path(d) / "user_options.json"
        f.write_text(_json.dumps(payload))
        return f

    def test_archetypes_merge_and_override(self):
        from data.user_options import apply_user_archetypes
        store = {"Existing Hero": {"gender": "Male", "hair_color": "jet black"}}
        f = self._write({"archetypes": {
            "Sky Pirate": {"gender": "Female", "hair_color": "copper", "bad": 5},  # non-str dropped
            "Existing Hero": {"gender": "Female"},   # overrides the built-in
            "Broken": "not a dict",                  # skipped
            "Empty": {},                             # skipped
        }})
        added = apply_user_archetypes(store, path=f)
        self.assertEqual(added, 2)
        self.assertEqual(store["Sky Pirate"], {"gender": "Female", "hair_color": "copper"})
        self.assertEqual(store["Existing Hero"], {"gender": "Female"})  # overridden
        self.assertNotIn("Broken", store)
        self.assertNotIn("Empty", store)

    def test_cosplayers_merge_requires_costume_and_defaults(self):
        from data.user_options import apply_user_cosplayers
        store = {}
        f = self._write({"cosplayers": {
            "My OC": {"costume": "a teal bodysuit with a star emblem",
                      "signature": {"hair_color": "electric blue", "bad": 1}},
            "No Costume": {"franchise": "X", "signature": {"hair_color": "white"}},  # skipped
            "Bad Gender": {"costume": "a plain robe", "gender": "Other"},  # gender -> Female
        }})
        added = apply_user_cosplayers(store, path=f)
        self.assertEqual(added, 2)
        oc = store["My OC"]
        self.assertEqual(oc["gender"], "Female")        # default
        self.assertEqual(oc["franchise"], "")           # default
        self.assertEqual(oc["signature"], {"hair_color": "electric blue"})  # non-str dropped
        self.assertEqual(oc["physique"], {})            # default
        self.assertNotIn("No Costume", store)
        self.assertEqual(store["Bad Gender"]["gender"], "Female")

    def test_cosplayer_male_entry_populates_random_male_scope(self):
        from data.user_options import apply_user_cosplayers
        from data.cosplayers import get_cosplayer_names_by_gender
        store = {}
        f = self._write({"cosplayers": {
            "Geralt": {"gender": "Male", "costume": "studded leather armor with twin scabbards"},
        }})
        apply_user_cosplayers(store, path=f)
        # The accessor scopes by the stored gender tag.
        males = sorted(n for n, e in store.items() if e.get("gender") == "Male")
        self.assertEqual(males, ["Geralt"])

    def test_missing_or_malformed_file_is_safe(self):
        from pathlib import Path
        from data.user_options import apply_user_archetypes, apply_user_cosplayers
        self.assertEqual(apply_user_archetypes({}, path=Path("/no/such.json")), 0)
        self.assertEqual(apply_user_cosplayers({}, path=Path("/no/such.json")), 0)
        f = self._write_raw("{ not valid json")
        self.assertEqual(apply_user_archetypes({}, path=f), 0)
        self.assertEqual(apply_user_cosplayers({}, path=f), 0)

    def _write_raw(self, text):
        import tempfile
        from pathlib import Path
        d = tempfile.mkdtemp()
        f = Path(d) / "user_options.json"
        f.write_text(text)
        return f


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

    def test_costume_override_suppresses_redundant_garment_fields(self):
        # A supplied costume is the whole outfit; the auto-randomized garment
        # fields must not appear alongside it (they only add JSON noise).
        costume = "a gothic black battle dress and thigh-high heeled boots"
        for seed in range(20):
            _, js = generate_character(seed, "Female", {"outfit_description": costume})
            clothing = json.loads(js)["Clothing"]
            self.assertEqual(clothing["outfit_description"], costume)
            for field in ("outfit_style", "footwear", "clothing_color", "clothing_pattern"):
                self.assertNotIn(field, clothing, f"seed {seed}: {field} leaked")

    def test_generated_outfit_keeps_garment_fields(self):
        # Without a costume, the normal garment fields are still emitted.
        _, js = generate_character(1, "Female", {})
        self.assertIn("footwear", json.loads(js)["Clothing"])

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


class SetAllFieldsTests(unittest.TestCase):
    """The 'set_all_fields' reset, resolved by ``resolve_locked_fields``."""

    def test_off_keeps_per_field_semantics(self):
        # Off: a Random field stays unset, a value locks, an explicit None omits.
        locked = resolve_locked_fields(
            {"eye_color": "emerald", "piercings": "None"}, {}, _SET_ALL_OFF
        )
        self.assertEqual(locked.get("eye_color"), "emerald")
        self.assertEqual(locked.get("piercings"), "None")
        self.assertNotIn("age", locked)  # untouched Random field is left to randomize

    def test_all_to_none_omits_untouched_fields(self):
        locked = resolve_locked_fields({"eye_color": "emerald"}, {}, _SET_ALL_NONE)
        self.assertEqual(locked.get("eye_color"), "emerald")  # explicit value kept
        self.assertEqual(locked.get("age"), "None")           # untouched -> omitted
        self.assertEqual(locked.get("location"), "None")

    def test_all_to_none_keeps_wired_character_signature(self):
        # A cosplayer's signature (supplied via the archetype dict) survives the
        # reset; only the random-person fields it didn't supply are blanked.
        archetype = {"hair_color": "platinum blonde", "eye_color": "emerald"}
        locked = resolve_locked_fields({}, archetype, _SET_ALL_NONE)
        self.assertEqual(locked["hair_color"], "platinum blonde")
        self.assertEqual(locked["eye_color"], "emerald")
        self.assertEqual(locked.get("age"), "None")  # non-signature field blanked

    def test_explicit_choice_overrides_archetype_under_reset(self):
        archetype = {"hair_color": "platinum blonde"}
        self.assertEqual(
            resolve_locked_fields({"hair_color": "None"}, archetype, _SET_ALL_NONE)["hair_color"],
            "None",
        )
        self.assertEqual(
            resolve_locked_fields({"hair_color": "jet black"}, archetype, _SET_ALL_NONE)["hair_color"],
            "jet black",
        )

    def test_all_to_none_end_to_end_keeps_costume_and_signature(self):
        # A She-Hulk cosplayer with the reset on: costume + signature hair show,
        # the random-person groups (Body / random Setting fields) are gone.
        flat = _parse_archetype_json(build_cosplayer_json("She-Hulk", 0, "Costume only"))
        archetype = {k: v for k, v in flat.items()
                     if k not in _CONTROL_FIELDS and v not in ("Random", "None")}
        locked = resolve_locked_fields({}, archetype, _SET_ALL_NONE)
        _, js = generate_character(7, "Female", locked, cosplay_label="She-Hulk")
        doc = json.loads(js)
        self.assertEqual(doc["Clothing"]["outfit_description"], COSPLAYERS["She-Hulk"]["costume"])
        self.assertEqual(doc["Hair"]["hair_color"], "emerald green")  # signature kept
        self.assertNotIn("Demographics", doc)  # random person blanked
        self.assertNotIn("Setting & Shot", doc)


class BodyPaintPhrasingTests(unittest.TestCase):
    """Non-natural skin reads as a single even coat, not patchy 'all-over' paint."""

    def test_she_hulk_uses_even_coat(self):
        costume = COSPLAYERS["She-Hulk"]["costume"]
        self.assertIn("an even, smooth coat of rich green body paint", costume)
        self.assertNotIn("all-over", costume)

    def test_body_paint_entries_avoid_bare_all_over(self):
        # "all-over" may survive only inside the textured "an even, all-over coat"
        # wording (scales/fur); a bare "all-over <colour> body paint" is the old,
        # patchy phrasing and must be gone.
        for name, entry in COSPLAYERS.items():
            costume = entry["costume"]
            if "body paint" in costume and "all-over" in costume:
                self.assertIn("an even, all-over coat", costume, name)


class ModifierTests(unittest.TestCase):
    """The Modifier node: parsing, payload, and prepend application."""

    def test_empty_or_comment_only_yields_empty(self):
        self.assertEqual(build_modifier_json(""), "{}")
        self.assertEqual(build_modifier_json("# just a comment\n\n   \n"), "{}")

    def test_parse_accepts_fields_and_groups_case_insensitively(self):
        mods = _parse_modifier_text(
            "Footwear: sci-fi chrome\nCLOTHING: weathered\nskin_tone: iridescent"
        )
        self.assertEqual(mods["footwear"], "sci-fi chrome")  # field, canonical case
        self.assertEqual(mods["Clothing"], "weathered")      # group, canonical case
        self.assertEqual(mods["skin_tone"], "iridescent")

    def test_parse_skips_unknown_and_malformed_keys(self):
        mods = _parse_modifier_text(
            "not_a_field: x\nNoColonHere\nfootwear: glowing\nhair_color:   "
        )
        self.assertEqual(dict(mods), {"footwear": "glowing"})  # only the valid line

    def test_payload_is_extracted_as_modifiers_not_locks(self):
        doc = build_modifier_json("footwear: sci-fi")
        flat = _parse_archetype_json(doc)
        self.assertEqual(flat.get(_MODIFIERS_KEY), {"footwear": "sci-fi"})
        self.assertNotIn("footwear", flat)  # never treated as a field lock

    def test_field_modifier_prepends_to_that_field_only(self):
        mods = {"skin_tone": "iridescent"}
        prose, js = generate_character(
            7, "Female", {"skin_tone": "porcelain", "eye_color": "emerald"}, modifiers=mods
        )
        doc = json.loads(js)
        self.assertEqual(doc["Body"]["skin_tone"], "iridescent porcelain")
        self.assertIn("iridescent porcelain skin", prose)
        self.assertEqual(doc["Face"]["eye_color"], "emerald")  # untouched

    def test_group_modifier_prepends_to_every_present_field(self):
        _, js = generate_character(
            7, "Female", {"skin_tone": "porcelain", "body_type": "athletic"},
            modifiers={"Body": "armored"},
        )
        body = json.loads(js)["Body"]
        self.assertEqual(body["skin_tone"], "armored porcelain")
        self.assertEqual(body["body_type"], "armored athletic")

    def test_field_modifier_beats_group_modifier(self):
        _, js = generate_character(
            7, "Female", {"skin_tone": "porcelain", "body_type": "athletic"},
            modifiers={"Body": "armored", "skin_tone": "iridescent"},
        )
        body = json.loads(js)["Body"]
        self.assertEqual(body["skin_tone"], "iridescent porcelain")  # field wins
        self.assertEqual(body["body_type"], "armored athletic")      # group fallback

    def test_modifier_does_not_resurrect_absent_field(self):
        _, js = generate_character(
            7, "Female", {"piercings": "None"}, modifiers={"piercings": "glowing"}
        )
        self.assertNotIn("piercings", json.loads(js).get("Jewelry & Nails", {}))

    def test_chains_after_cosplayer(self):
        chained = merge_preset_documents(
            build_cosplayer_json("2B", 0), build_modifier_json("hair_color: silver-chrome")
        )
        flat = _parse_archetype_json(chained)
        self.assertEqual(flat.get(_MODIFIERS_KEY), {"hair_color": "silver-chrome"})
        label = flat.pop(_COSPLAY_LABEL_KEY, None)
        mods = flat.pop(_MODIFIERS_KEY, None)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, "Female", locked, cosplay_label=label, modifiers=mods)
        # 2B's signature platinum blonde gets the chrome tilt; costume still intact.
        self.assertEqual(json.loads(js)["Hair"]["hair_color"], "silver-chrome platinum blonde")
        self.assertEqual(
            json.loads(js)["Clothing"]["outfit_description"], COSPLAYERS["2B"]["costume"]
        )


class GloveSuppressionTests(unittest.TestCase):
    """Gloved hands hide the fingers, so randomized nails/rings must not render
    on top of the glove -- except fingerless gloves (fingers exposed), an explicit
    user lock, and power rings written into the costume prose itself."""

    def _jewelry(self, doc):
        return doc.get("Jewelry & Nails", {})

    def test_gloves_suppress_nails_and_rings(self):
        costume = "a sleek black combat bodysuit with white gloves and boots"
        for seed in range(40):
            _, js = generate_character(seed, "Female", {"outfit_description": costume},
                                       accessory_density="Maximal")
            jewelry = self._jewelry(json.loads(js))
            self.assertNotIn("nails", jewelry, f"seed {seed}")
            self.assertNotIn("rings", jewelry, f"seed {seed}")

    def test_gauntlets_also_suppress(self):
        costume = "ornate silver plate armor with articulated gauntlets and a tabard"
        for seed in range(20):
            _, js = generate_character(seed, "Male", {"outfit_description": costume},
                                       accessory_density="Maximal")
            self.assertNotIn("nails", self._jewelry(json.loads(js)), f"seed {seed}")

    def test_fingerless_gloves_keep_nails(self):
        # Fingerless gloves expose the fingers, so nails should still appear.
        costume = "a leather jacket, ripped jeans, and fingerless gloves"
        seen_nails = any(
            "nails" in self._jewelry(json.loads(
                generate_character(s, "Female", {"outfit_description": costume},
                                   accessory_density="Maximal")[1]))
            for s in range(40)
        )
        self.assertTrue(seen_nails)

    def test_no_gloves_keep_nails(self):
        # A normal outfit (no gloves) leaves the nail field free to appear.
        costume = "a flowing red sundress with strappy sandals"
        seen_nails = any(
            "nails" in self._jewelry(json.loads(
                generate_character(s, "Female", {"outfit_description": costume},
                                   accessory_density="Maximal")[1]))
            for s in range(40)
        )
        self.assertTrue(seen_nails)

    def test_locked_nails_survive_gloves(self):
        # An explicit user lock beats the glove suppression.
        costume = "a sleek black combat bodysuit with white gloves and boots"
        _, js = generate_character(1, "Female",
                                   {"outfit_description": costume, "nails": "red polish"})
        self.assertEqual(self._jewelry(json.loads(js)).get("nails"), "red polish")

    def test_power_ring_in_costume_survives(self):
        # Green Lantern style: the power ring lives in the costume prose, not the
        # ``rings`` field, so suppressing the field never removes it.
        costume = ("a black-and-green bodysuit with a circular lantern emblem, green "
                   "gloves and boots, and a glowing green power ring worn on the finger")
        prose, js = generate_character(3, "Male", {"outfit_description": costume},
                                       accessory_density="Maximal")
        self.assertIn("power ring", prose)
        self.assertNotIn("rings", self._jewelry(json.loads(js)))

    def test_ringtyped_other_jewelry_dropped_under_gloves(self):
        costume = "a tailored suit with black leather gloves"
        for seed in range(60):
            _, js = generate_character(seed, "Female", {"outfit_description": costume},
                                       accessory_density="Maximal")
            other = self._jewelry(json.loads(js)).get("other_jewelry", "")
            self.assertNotIn("ring", other, f"seed {seed}")
            self.assertNotIn("finger", other, f"seed {seed}")


class GrammarAgreementTests(unittest.TestCase):
    """The 'Any' gender uses plural 'They' and must take plural verbs."""

    def test_they_takes_plural_wear(self):
        prose, _ = generate_character(
            7, "Any", {"outfit_style": "casual", "makeup_style": "soft glam"}
        )
        self.assertNotIn("They wears", prose)
        self.assertIn("They wear", prose)

    def test_gendered_subjects_keep_singular_wears(self):
        for gender in ("Female", "Male"):
            prose, _ = generate_character(7, gender, {"outfit_style": "casual"})
            self.assertNotIn(" wear ", prose)  # no plural verb for She/He


if __name__ == "__main__":
    unittest.main(verbosity=2)
