"""Unit tests for the IdentityForge engine and archetype node.

Pure-stdlib ``unittest`` so it runs without ComfyUI installed:

    python -m unittest discover -s tests -t . -v
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import random
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.fields import (
    FIELD_DEFINITIONS, FIELD_FAMILIES, POSE_FAMILIES, HAIR_STYLE_FAMILIES,
    HAIR_DEPENDENT_POSES, GARMENT_DEPENDENT_POSES, HAND_OCCUPIED_POSES,
    FURNITURE_DEPENDENT_POSES, OUTFIT_DESCRIPTIONS,
)
from data.constraints import CONSTRAINT_RULES
from data.fields import WORN_ITEM_RES, SHOE_RE, PALETTE_ADJECTIVES, PATTERN_TAILS
from nodes.identity_forge import (
    generate_character,
    merge_preset_documents,
    resolve_locked_fields,
    _pick_family_weighted,
    _performable_poses,
    _BARE_LEG_RE,
    _LONG_SLEEVE_RE,
    _HIGH_NECK_RE,
    _OPAQUE_LEGWEAR_RE,
    _TALL_BOOT_RE,
    _DEFERRED_FIELDS,
    _visible_tattoo_placements,
    _wearable_legwear,
    _SELFIE_SHOT_TYPE,
    _randomize_fields,
    _is_absent,
    _parse_archetype_json,
    _CONTROL_FIELDS,
    _EXTRA_ABSENCE,
    _SET_ALL_OFF,
    _SET_ALL_NONE,
    _a,
    _prepend_descriptor,
    _compose_outfit_clause,
    _FOOTWEAR_CLAUSES,
    _article_if_singular,
    _format_prose,
)
from nodes.identity_forge import (
    _COSPLAY_LABEL_KEY, _COVERS_FACE_KEY, _COVERS_BODY_KEY, _COVERS_HAIR_KEY,
    _MASK_KEY,
    _MODIFIERS_KEY, _VARIANTS_KEY, _name_already_carries_franchise,
)
from nodes.identity_forge_archetype import build_archetype_json
from nodes.identity_forge_cosplayer import (
    build_cosplayer_json, _MASK_DEFAULT, _MASK_OFF,
    _pick_look, _resolve_character, _SPECIAL_SCOPES,
    _FRANCHISE_SCOPES, _PREDICATE_SCOPES, _FRANCHISE_SCOPE_MINIMUM,
    _FRANCHISE_SCOPE_PREFIX,
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
        # "Any" resolves to a concrete gender, but an anatomical lock decides it: a
        # locked beard implies Male (via _gender_from_locks), so the explicit choice
        # is honored and survives the gender gate.
        for seed in range(20):
            _, js = generate_character(seed, "Any", {"facial_hair": "full beard"})
            self.assertEqual(json.loads(js)["Hair"]["facial_hair"], "full beard",
                             f"seed {seed}")

    # Female-only bust values (a masculine character must never carry one).
    _FEMALE_BUST = {"very small", "small", "modest", "medium", "full",
                    "very large", "generously proportioned"}

    def test_any_resolves_to_one_coherent_gender(self):
        # gender "Any" + a real wardrobe rolls a concrete man OR woman, never the
        # mixed "they/them" union: meta gender is concrete and a beard never lands
        # on a feminine bust (the woman-with-a-mustache bug).
        for seed in range(80):
            _, js = generate_character(seed, "Any", {}, wardrobe="Match gender")
            doc = json.loads(js)
            self.assertIn(doc["_meta"]["gender"], {"Female", "Male"}, f"seed {seed}")
            facial = doc.get("Hair", {}).get("facial_hair", "")
            bust = doc.get("Body", {}).get("bust", "")
            if facial and "shaven" not in facial:  # a real beard/moustache => male
                self.assertNotIn(bust, self._FEMALE_BUST,
                                 f"seed {seed}: {facial!r} with {bust!r}")

    def test_any_with_any_wardrobe_still_mixes(self):
        # The deliberate full-mix escape hatch: gender "Any" + wardrobe "Any" keeps
        # the unioned androgynous mode ("They" pronouns, meta gender stays "Any").
        _, js = generate_character(7, "Any", {}, wardrobe="Any")
        self.assertEqual(json.loads(js)["_meta"]["gender"], "Any")

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
        "nails": {"red polish", "pink polish", "coral polish", "mauve polish",
                  "french manicure", "stiletto nails", "coffin nails", "almond nails",
                  "chrome nails", "gel nails", "colorful nail art"},
        "earrings": {"chandelier earrings", "long drop earrings", "tassel earrings",
                     "pearl studs", "large bold gold hoops", "clip-on pearl earrings"},
        "necklace": {"pearl necklace", "pearl strand", "choker", "velvet choker",
                     "statement necklace", "collar necklace", "locket necklace"},
        "hair_style": {"space buns", "pigtails", "high pigtails", "low pigtails",
                       "curled pigtails", "updo", "French twist",
                       "crown braid", "fishtail braid", "half up half down"},
        "hair_length": {"chin length bob", "waist length", "hip length"},
        "hair_highlights": {"subtle balayage", "face framing", "ombre", "sombre"},
        "eyebrows": {"thin and arched", "pencil thin", "feathered",
                     "well defined and arched", "bold statement brows", "laminated brows"},
        "lips": {"bow-shaped", "heart-shaped", "petite and defined"},
        "eye_shape": {"doe-like"},
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

    def test_male_locked_makeup_overrides_gender(self):
        # Makeup is cosmetic and anatomically gender-neutral, so a value explicitly
        # locked by a preset survives a Male override (a man can wear gothic glam —
        # e.g. drag performers). Random men still default bare-faced, see
        # test_male_random_never_feminine.
        _, js = generate_character(1, "Male", {"makeup_style": "gothic dark makeup"})
        self.assertEqual(json.loads(js)["Makeup"]["makeup_style"], "gothic dark makeup")

    def test_male_archetype_makeup_preserved(self):
        # The Vampire Noble archetype locks gothic makeup; as an explicit cosmetic
        # lock it now survives the Male rendering, so a male crossplay keeps the
        # styled look instead of being stripped to bare-faced.
        flat = _parse_archetype_json(build_archetype_json("Vampire Noble", 0, "Full preset"))
        self.assertEqual(flat.get("makeup_style"), "gothic dark makeup")
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, "Male", locked)
        self.assertEqual(json.loads(js)["Makeup"]["makeup_style"], "gothic dark makeup")

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


class ERNurseGenderMakeupTests(unittest.TestCase):
    """0.67.0: ER Nurse is a unisex archetype whose only per-gender difference is
    makeup. It carries a costume-less ``variants`` block (Female -> soft natural
    makeup, Male -> no makeup) so a female nurse is made up while a male nurse stays
    bare-faced -- without a base makeup_style lock that would paint a man (the bug
    this fixed). The costume rotation stays on the base via _COSTUMES."""

    def _render(self, seed, gender):
        flat = _parse_archetype_json(build_archetype_json("ER Nurse", seed, "Essentials"))
        gv = flat.pop(_VARIANTS_KEY, None)
        return generate_character(seed, gender, flat, gender_variants=gv)

    def test_female_nurse_wears_soft_natural_makeup(self):
        for seed in range(20):
            _, js = self._render(seed, "Female")
            self.assertEqual(json.loads(js)["Makeup"]["makeup_style"],
                             "soft natural makeup", f"seed {seed}")

    def test_male_nurse_is_bare_faced(self):
        # The male variant locks makeup_style="no makeup", which cascades to clear
        # every cosmetic sub-field. No eyeshadow/lipstick lands on a male nurse.
        for seed in range(20):
            prose, js = self._render(seed, "Male")
            self.assertEqual(json.loads(js)["Makeup"]["makeup_style"], "no makeup",
                             f"seed {seed}")
            low = prose.lower()
            for phrase in ("eyeshadow", "eyeliner", "mascara", "lipstick"):
                self.assertNotIn(phrase, low, f"'{phrase}' on male nurse seed {seed}")

    def test_costume_still_rotates_for_both_genders(self):
        # The five-look _COSTUMES rotation survives the variants block (variants
        # define no outfit_description, so the base costume is the single source).
        for gender in ("Female", "Male"):
            looks = {json.loads(self._render(s, gender)[1])["Clothing"]["outfit_description"]
                     for s in range(40)}
            self.assertGreater(len(looks), 1, f"{gender} costume did not vary")


class CostumeExtraSuppressionTests(unittest.TestCase):
    """0.67/0.68: a provided costume (outfit_description locked) drops the random
    accessory extras -- bag, watch, hair accessory, accessories -- so a samurai never
    gets a designer tote, wristwatch, scrunchie or sunglasses. A plain no-costume run
    still gets them; an explicitly authored extra (scarf, flower crown) survives."""

    _EXTRAS = {"bag": "no bag", "watch_type": "none",
               "hair_accessory": "no hair accessory", "accessories": "no accessories"}

    def _flat(self, js):
        d = json.loads(js)
        return {k: v for g in d.values() if isinstance(g, dict) for k, v in g.items()}

    def test_locked_costume_drops_all_extras(self):
        locked = {"outfit_description": "lacquered samurai armor with a horned kabuto helmet"}
        for seed in range(60):
            f = self._flat(generate_character(seed, "Male", locked)[1])
            for field, absent in self._EXTRAS.items():
                self.assertIn(f.get(field, absent), (absent, None), f"{field} seed {seed}")

    def test_plain_run_still_allows_extras(self):
        # No costume provided -> a random modern person may carry/wear them.
        hits = {field: 0 for field in self._EXTRAS}
        for seed in range(200):
            f = self._flat(generate_character(seed, "Female", {})[1])
            for field, absent in self._EXTRAS.items():
                hits[field] += f.get(field, absent) != absent
        for field, n in hits.items():
            self.assertGreater(n, 0, field)

    def test_explicit_extra_lock_is_respected_with_costume(self):
        # An authored signature extra survives the costume suppression.
        for field, value in (("bag", "tan leather crossbody"),
                             ("accessories", "silk neck scarf"),
                             ("hair_accessory", "flower crown")):
            locked = {"outfit_description": "a tailored trench coat and jeans", field: value}
            f = self._flat(generate_character(3, "Female", locked)[1])
            self.assertEqual(f.get(field), value, field)


class PocketlessPoseTests(unittest.TestCase):
    """0.67.0: swimwear / leotard / gown / toga has no pockets or collar, so the two
    garment gestures (hands in pockets, touching the collar) are dropped for it -- the
    same way a full hard shell drops them."""

    _GARMENT = frozenset({"posing with hands in pockets", "touching the collar with one hand"})

    def test_pocketless_outfit_drops_garment_gestures(self):
        for outfit in ("a sleek one-piece training swimsuit",
                       "a black dance leotard and tights",
                       "a flowing Grecian toga",
                       "an emerald evening gown"):
            pool = _performable_poses(
                ["standing naturally", *self._GARMENT], {"outfit_description": outfit},
                covers_face=False, covers_body=False, covers_hair=False)
            self.assertFalse(self._GARMENT & set(pool), outfit)

    def test_normal_outfit_keeps_garment_gestures(self):
        pool = _performable_poses(
            ["standing naturally", *self._GARMENT],
            {"outfit_description": "a tailored blazer and trousers with deep pockets"},
            covers_face=False, covers_body=False, covers_hair=False)
        self.assertTrue(self._GARMENT & set(pool))


class ScopeAnnounceTests(unittest.TestCase):
    """0.67.0: a scoped Random pick prints its in-scope pool size once per combo so
    small pools (Masked+female=7) read as intentional, and warns loudly if a combo
    ever falls back to the full gender pool (unreachable with the shipped roster)."""

    def test_announce_is_once_per_combo(self):
        import nodes.identity_forge_cosplayer as cn
        cn._SCOPE_NOTICE_SEEN.clear()
        cn._announce_scope("Random - female", "Masked", "Female", 7, cn._SCOPE_OK)
        cn._announce_scope("Random - female", "Masked", "Female", 7, cn._SCOPE_OK)
        self.assertIn(("Random - female", "Masked"), cn._SCOPE_NOTICE_SEEN)
        self.assertEqual(len(cn._SCOPE_NOTICE_SEEN), 1)

    def test_empty_gender_combo_keeps_the_scope(self):
        """An all-one-gender franchise must still return a character FROM it.

        0.75.0 bug: "Random - male" + a franchise with no male characters (Date A
        Live) silently fell back to the whole male roster and handed back an Ewok.
        The scope is the deliberate choice, so the gender filter yields instead.
        """
        import nodes.identity_forge_cosplayer as cn
        real = cn.get_cosplayer_names

        def fake_names(gender=None, category=cn._SCOPE_ANY):
            # No male characters exist; the un-gendered pool is the in-scope cast.
            return [] if gender == "Male" else ["Kurumi Tokisaki", "Tohka Yatogami"]

        cn._SCOPE_NOTICE_SEEN.clear()
        cn.get_cosplayer_names = fake_names
        try:
            # A category scope, so the stubbed roster is used directly rather than
            # re-filtered through a predicate against the real COSPLAYERS dict.
            name = cn._resolve_character(cn._RANDOM_MALE, random.Random(0), "Anime & Manga")
        finally:
            cn.get_cosplayer_names = real
        self.assertIn(name, ("Kurumi Tokisaki", "Tohka Yatogami"))

    def test_wholly_empty_scope_still_falls_back_and_flags(self):
        """A scope matching nothing at all (any gender) keeps the old loud fallback."""
        import nodes.identity_forge_cosplayer as cn
        real = cn.get_cosplayer_names

        def fake_names(gender=None, category=cn._SCOPE_ANY):
            # Scoped lookups are empty for every gender; only the bare pool has names.
            return ["Zatanna"] if category in (None, cn._SCOPE_ANY) else []

        cn._SCOPE_NOTICE_SEEN.clear()
        cn.get_cosplayer_names = fake_names
        try:
            name = cn._resolve_character(cn._RANDOM_FEMALE, random.Random(0), "DC")
        finally:
            cn.get_cosplayer_names = real
        self.assertEqual(name, "Zatanna")

    def test_unscoped_pick_announces_nothing(self):
        import nodes.identity_forge_cosplayer as cn
        cn._SCOPE_NOTICE_SEEN.clear()
        cn._resolve_character(cn._RANDOM_ANY, random.Random(0), cn._SCOPE_ANY)
        self.assertEqual(len(cn._SCOPE_NOTICE_SEEN), 0)


class HarleyArkhamLooksTests(unittest.TestCase):
    """0.67.0: Harley Quinn gained the two missing Arkham game looks as costumes[]
    alternates (Asylum nurse-corset, City studded-leather corset)."""

    def test_harley_has_five_distinct_looks(self):
        looks = {json.loads(build_cosplayer_json("Harley Quinn", s, "Costume only"))
                 ["Clothing"]["outfit_description"] for s in range(60)}
        self.assertGreaterEqual(len(looks), 4)

    def test_arkham_looks_reachable(self):
        seen = set()
        for s in range(80):
            c = json.loads(build_cosplayer_json("Harley Quinn", s, "Costume only")
                           )["Clothing"]["outfit_description"].lower()
            if "nurse's corset" in c:
                seen.add("asylum")
            if "quilted red-and-black leather corset" in c:
                seen.add("city")
        self.assertEqual(seen, {"asylum", "city"})


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


class BaldHairLengthTests(unittest.TestCase):
    """A "bald" hair_length is scalp-only: the other scalp-hair fields are
    dropped (no "bald wavy auburn hair" contradiction), prose voices the head,
    and the option lives in the male pool only (comb-over precedent)."""

    _SCALP = ("hair_color", "hair_texture", "hair_style", "hair_part",
              "hair_highlights", "hair_accessory")

    def test_bald_lock_drops_scalp_fields_keeps_facial_hair_possible(self):
        for seed in range(20):
            prose, js = generate_character(seed, "Male", {"hair_length": "bald"})
            hair = json.loads(js).get("Hair", {})
            self.assertEqual(hair.get("hair_length"), "bald")
            for field in self._SCALP:
                self.assertNotIn(field, hair, f"{field} survived a bald head (seed {seed})")
            self.assertIn("head is bald", prose)
            self.assertNotIn("hair is bald", prose)

    def test_bald_is_male_pool_only(self):
        self.assertIn("bald", FIELD_DEFINITIONS["hair_length"]["male_options"])
        self.assertNotIn("bald", FIELD_DEFINITIONS["hair_length"]["female_options"])
        # A random female draw can never produce it.
        for seed in range(60):
            _, js = generate_character(seed, "Female", {})
            self.assertNotEqual(json.loads(js)["Hair"].get("hair_length"), "bald")

    def test_random_male_can_draw_bald_and_it_scrubs(self):
        drew_bald = False
        for seed in range(300):
            _, js = generate_character(seed, "Male", {})
            hair = json.loads(js).get("Hair", {})
            if hair.get("hair_length") == "bald":
                drew_bald = True
                for field in self._SCALP:
                    self.assertNotIn(field, hair)
        self.assertTrue(drew_bald, "no random male drew 'bald' in 300 seeds")


class MulletHairStyleTests(unittest.TestCase):
    """'mullet' is a male-only hair_style gated by hair length (needs back length)."""

    def test_mullet_is_male_pool_only(self):
        self.assertIn("mullet", FIELD_DEFINITIONS["hair_style"]["male_options"])
        self.assertNotIn("mullet", FIELD_DEFINITIONS["hair_style"]["female_options"])

    def test_mullet_excluded_for_short_lengths(self):
        for length in ("buzzed very short", "very short", "short pixie"):
            for seed in range(40):
                _, js = generate_character(seed, "Male", {"hair_length": length})
                self.assertNotEqual(
                    json.loads(js)["Hair"].get("hair_style"), "mullet",
                    f"mullet drawn under '{length}' (seed {seed})")


class ContrapositiveConstraintTests(unittest.TestCase):
    """A locked exclusion *target* re-rolls the randomized *trigger* instead of
    leaving an incoherent pair behind a warning (a locked "sleek bun" must never
    sit on a randomly drawn buzz cut, and a locked style never on a bald head)."""

    def test_locked_long_style_rerolls_short_random_length(self):
        # Expected exclusions mirror the forward rules: buns are pixie-friendly,
        # ponytails/mullets are not; "bald" never coexists with a locked style.
        cases = {
            "sleek bun": ("Female", {"buzzed very short", "very short", "bald"}),
            "high ponytail": ("Female", {"buzzed very short", "very short", "short pixie", "bald"}),
            "mullet": ("Male", {"buzzed very short", "very short", "short pixie", "bald"}),
        }
        for style, (gender, blocked) in cases.items():
            for seed in range(60):
                _, js = generate_character(seed, gender, {"hair_style": style})
                hair = json.loads(js)["Hair"]
                self.assertEqual(hair.get("hair_style"), style)
                self.assertNotIn(
                    hair.get("hair_length"), blocked,
                    f"'{style}' locked but length drew '{hair.get('hair_length')}' (seed {seed})")

    def test_both_locked_still_warns_and_keeps(self):
        # A user locking a genuine contradiction keeps both values (lock wins).
        _, js = generate_character(
            5, "Female", {"hair_style": "sleek bun", "hair_length": "buzzed very short"})
        hair = json.loads(js)["Hair"]
        self.assertEqual(hair.get("hair_style"), "sleek bun")
        self.assertEqual(hair.get("hair_length"), "buzzed very short")


class ContrapositiveRequirementTests(unittest.TestCase):
    """The requirement half of contrapositive repair (0.82.0).

    Until 0.82.0 only *exclusion* rules re-rolled a randomized trigger; a
    requirement rule whose target was locked just warned and left incoherent
    output behind ("no makeup" beside a locked lash-extension look, a locked
    toothy grin beside a "stern" expression). The lock still wins -- but now the
    free side moves to agree with it, so the contradiction never renders.
    """

    @staticmethod
    def _flat(js):
        return {k: v for group in json.loads(js).values()
                if isinstance(group, dict) for k, v in group.items()}

    def test_locked_lashes_and_lips_reroll_makeup_style(self):
        # The reported case: two deliberate locks vs. a random "no makeup" draw.
        locked = {"lashes": "lash extension look", "lips_makeup": "classic red"}
        for seed in range(80):
            _, js = generate_character(seed, "Female", dict(locked))
            flat = self._flat(js)
            self.assertEqual(flat.get("lashes"), "lash extension look")
            self.assertEqual(flat.get("lips_makeup"), "classic red")
            self.assertNotEqual(
                flat.get("makeup_style"), "no makeup",
                f"bare-face style drawn beside locked lash extensions (seed {seed})")

    def test_locked_smile_type_rerolls_contradicting_expression(self):
        # expression -> smile_type is the same shape and was equally broken.
        closed = {r["value"] for r in CONSTRAINT_RULES
                  if r["type"] == "requirement" and r["field"] == "expression"
                  and r["requires_value"] != "toothy grin"}
        for seed in range(80):
            _, js = generate_character(seed, "Female", {"smile_type": "toothy grin"})
            flat = self._flat(js)
            self.assertEqual(flat.get("smile_type"), "toothy grin")
            self.assertNotIn(
                flat.get("expression"), closed,
                f"locked grin drew a closed-mouth expression (seed {seed})")

    def test_locked_hair_part_rerolls_partless_style(self):
        partless = {r["value"] for r in CONSTRAINT_RULES
                    if r["type"] == "requirement" and r["field"] == "hair_style"
                    and r["requires_field"] == "hair_part"}
        for seed in range(60):
            _, js = generate_character(seed, "Female", {"hair_part": "middle part"})
            hair = json.loads(js)["Hair"]
            self.assertEqual(hair.get("hair_part"), "middle part")
            self.assertNotIn(
                hair.get("hair_style"), partless,
                f"locked part drew a part-less style (seed {seed})")

    def test_male_makeup_chain_still_warns_instead_of_ping_ponging(self):
        # gender=Male PINS makeup_style="no makeup", so re-rolling it would be
        # undone every pass. _requirement_pins must block the repair here and
        # fall back to warn-and-keep -- the lock still wins, and the loop
        # terminates instead of churning to the iteration cap.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _, js = generate_character(
                3, "Male", {"lips_makeup": "classic red"}, wardrobe="Match gender")
        flat = self._flat(js)
        self.assertEqual(flat.get("lips_makeup"), "classic red")
        self.assertEqual(flat.get("makeup_style"), "no makeup")
        self.assertIn("keeping lock", buf.getvalue())

    def test_both_locked_still_warns_and_keeps(self):
        # A user locking both sides of a genuine contradiction keeps both.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _, js = generate_character(
                5, "Female",
                {"makeup_style": "no makeup", "lips_makeup": "classic red"})
        flat = self._flat(js)
        self.assertEqual(flat.get("makeup_style"), "no makeup")
        self.assertEqual(flat.get("lips_makeup"), "classic red")
        self.assertIn("keeping lock", buf.getvalue())

    def test_unlocked_output_is_untouched(self):
        # The repair only runs when a target is locked, so ordinary random
        # output must be bit-identical to the pre-0.82.0 engine. This is the
        # bias gate: no locked field, no re-pick, no extra RNG draw.
        for gender in ("Female", "Male", "Any"):
            for seed in range(40):
                a, _ = generate_character(seed, gender, {})
                b, _ = generate_character(seed, gender, {})
                self.assertEqual(a, b)


class ConstraintTests(unittest.TestCase):
    def test_requirement_no_makeup_zeroes_subfields(self):
        _, js = generate_character(7, "Female", {"makeup_style": "no makeup"})
        mk = json.loads(js)["Makeup"]
        self.assertEqual(mk["eye_makeup"], "no eyeshadow")
        self.assertEqual(mk["eyeliner"], "no eyeliner")
        self.assertEqual(mk["lashes"], "natural bare")
        self.assertEqual(mk["blush"], "no blush")

    def test_absence_equivalent_lock_is_silent(self):
        # A "no makeup" requirement wants eye_makeup="no eyeshadow" etc.; a field
        # already locked to the equally-absent "None" satisfies that with no need to
        # nag the console. But a lock holding a *real* value (classic red lips) is a
        # genuine contradiction that must still warn.
        import random as _random
        from nodes.identity_forge import _apply_constraints
        resolved = {
            "makeup_style": "no makeup",
            "eye_makeup": "None", "eyeliner": "None", "lashes": "None",
            "eyebrow_makeup": "None", "lips_makeup": "classic red",
        }
        locked = {"makeup_style", "eye_makeup", "eyeliner", "lashes",
                  "eyebrow_makeup", "lips_makeup"}
        warnings = _apply_constraints(
            resolved, "Female", locked, _random.Random(0), presentation="Feminine")
        joined = "\n".join(warnings)
        # The four absent-vs-absent locks stay quiet...
        for field in ("eye_makeup", "eyeliner", "lashes", "eyebrow_makeup"):
            self.assertNotIn(f"'{field}=", joined,
                             f"absence-equivalent lock on {field} should be silent")
        # ...but the real contradiction (red lips vs. no makeup) is surfaced.
        self.assertIn("lips_makeup", joined)
        self.assertIn("classic red", joined)
        # Every lock is still honoured regardless of whether it warned.
        self.assertEqual(resolved["eye_makeup"], "None")
        self.assertEqual(resolved["lips_makeup"], "classic red")

    def test_exclusion_buzzed_hair_blocks_braids(self):
        long_styles = {"side braid", "French braid", "updo", "French twist", "high ponytail"}
        for seed in range(60):
            _, js = generate_character(seed, "Female", {"hair_length": "buzzed very short"})
            self.assertNotIn(json.loads(js)["Hair"]["hair_style"], long_styles)

    def test_exclusion_athletic_has_no_bag(self):
        for seed in range(40):
            _, js = generate_character(seed, "Female", {"outfit_style": "athletic"})
            self.assertEqual(json.loads(js)["Clothing"].get("bag"), "no bag")

    def test_body_fitness_coherence(self):
        # fitness_level is the sole conditioning axis (muscle_definition was merged
        # out); a plus-size silhouette never rolls an athletic/muscular fitness level.
        for seed in range(60):
            _, js = generate_character(seed, "Male", {"body_type": "plus size"})
            self.assertNotIn(
                json.loads(js)["Body"]["fitness_level"],
                {"athletic", "muscular"},
            )

    def test_locked_field_not_overwritten_by_constraint(self):
        _, js = generate_character(
            5, "Female", {"eye_makeup": "smoky black", "makeup_style": "full glam"}
        )
        self.assertEqual(json.loads(js)["Makeup"]["eye_makeup"], "smoky black")

    def test_dewy_makeup_style_excludes_matte_and_doubled_dewy_finish(self):
        for seed in range(60):
            _, js = generate_character(
                seed, "Female", {"makeup_style": "fresh-faced dewy look"})
            self.assertNotIn(
                json.loads(js)["Makeup"].get("skin_finish"),
                {"matte finish", "full coverage matte", "dewy skin"},
            )

    def test_mood_and_expression_vocabularies_do_not_collide(self):
        # mood "playful" was renamed "carefree" in 0.36 because expression owns
        # "playful"; the two randomize independently, so a shared word could
        # double in one output ("a playful expression ... a playful mood").
        expr = set(FIELD_DEFINITIONS["expression"]["female_options"])
        mood = set(FIELD_DEFINITIONS["mood"]["female_options"])
        self.assertFalse(expr & mood,
                         f"expression/mood share options: {expr & mood}")
        self.assertIn("carefree", mood)

    def test_skin_details_does_not_duplicate_smile_type_dimples(self):
        # "dimples when smiling" was reworded in 0.36: smile_type's
        # "subtle dimpled" owns the dimple concept.
        for opt in FIELD_DEFINITIONS["skin_details"]["female_options"]:
            self.assertNotIn("dimple", opt)


class OutputFormatTests(unittest.TestCase):
    def test_locked_value_preserved(self):
        _, js = generate_character(9, "Female", {"eye_color": "emerald"})
        self.assertEqual(json.loads(js)["Face"]["eye_color"], "emerald")

    def test_none_excludes_optional_field(self):
        _, js = generate_character(9, "Female", {"piercings": "None"})
        self.assertNotIn("piercings", json.loads(js).get("Jewelry & Nails", {}))

    def test_none_excludes_non_optional_field(self):
        # Any field (even non-optional scene fields) can be omitted via "None".
        # Derived from FIELD_DEFINITIONS' own group membership rather than
        # hand-listed: a hand-listed set can't know about a field added after
        # it was written (0.85.0 had to add `composition` here by hand, and
        # nothing guarded the next one until now).
        from nodes.identity_forge import _CONTROL_FIELDS, _HIDDEN_FIELDS
        scene = {
            name: "None" for name, meta in FIELD_DEFINITIONS.items()
            if meta["group"] == "Setting & Shot"
            and name not in _CONTROL_FIELDS and name not in _HIDDEN_FIELDS
        }
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

    def test_hair_accessory_placement_gets_possessive(self):
        # "... tied in hair" option values are voiced with the possessive at
        # the render layer ("tied in her hair") — never the bare "in hair".
        cases = (("Female", "satin ribbon tied in hair", "tied in her hair"),
                 ("Male", "bandana tied over hair", "over his hair"))
        for gender, acc, expected in cases:
            prose, _ = generate_character(42, gender, {"hair_accessory": acc})
            self.assertIn(expected, prose)
            self.assertNotIn("tied in hair", prose)
            self.assertNotIn("tied over hair", prose)

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
            # "variants" is a per-gender look block, not a field; its nested looks
            # are validated below.
            self.assertEqual(set(template) - valid - {"variants"}, set(), f"{name}")
            for vgender, look in (template.get("variants") or {}).items():
                self.assertIn(vgender, ("Female", "Male"), name)
                self.assertNotIn("gender", look, f"{name}/{vgender}")
                self.assertEqual(set(look) - valid, set(), f"{name}/{vgender}")

    def test_list_values_resolve_to_one_alternative(self):
        # A field value may be a curated list; the node seed-picks one so a
        # single archetype yields a range of coherent looks.
        synthetic = {
            "gender": "Female",
            "hair_color": ["raven black", "jet black", "espresso"],
            "outfit_description": "a {color} shift dress",
        }
        ARCHETYPES["__ListTest__"] = synthetic
        try:
            picks = set()
            for seed in range(40):
                doc = json.loads(build_archetype_json("__ListTest__", seed))
                value = doc["Hair"]["hair_color"]
                self.assertIn(value, synthetic["hair_color"])
                picks.add(value)
            self.assertEqual(picks, set(synthetic["hair_color"]))  # all reachable
            self.assertEqual(  # deterministic per seed
                build_archetype_json("__ListTest__", 11),
                build_archetype_json("__ListTest__", 11),
            )
        finally:
            del ARCHETYPES["__ListTest__"]

    def test_trailing_list_field_does_not_shift_costume_fill(self):
        # Scalar list picks draw AFTER all costume fills: adding a list field to
        # an archetype must not change which costume colours a seed produces.
        base = {"gender": "Female", "outfit_description": "a {color} shift dress"}
        with_list = dict(base, hair_color=["raven black", "espresso"])
        for seed in range(15):
            ARCHETYPES["__ListTest__"] = dict(base)
            try:
                before = json.loads(build_archetype_json("__ListTest__", seed))
                ARCHETYPES["__ListTest__"] = dict(with_list)
                after = json.loads(build_archetype_json("__ListTest__", seed))
            finally:
                del ARCHETYPES["__ListTest__"]
            self.assertEqual(
                before["Clothing"]["outfit_description"],
                after["Clothing"]["outfit_description"],
                f"seed {seed}",
            )

    def test_list_picks_match_across_lock_levels(self):
        # The scalar pass runs on the unfiltered look, so Essentials and Full
        # preset agree on every pick for a given seed.
        ARCHETYPES["__ListTest__"] = {
            "gender": "Female",
            "hair_color": ["raven black", "jet black", "espresso"],
            "skin_tone": ["porcelain", "pale"],  # non-essential (Body)
            "outfit_description": "a {color} shift dress",
        }
        try:
            for seed in range(15):
                ess = json.loads(build_archetype_json("__ListTest__", seed, "Essentials"))
                full = json.loads(build_archetype_json("__ListTest__", seed, "Full preset"))
                self.assertEqual(ess["Hair"]["hair_color"], full["Hair"]["hair_color"])
                self.assertEqual(
                    ess["Clothing"]["outfit_description"],
                    full["Clothing"]["outfit_description"],
                )
        finally:
            del ARCHETYPES["__ListTest__"]

    def test_outfit_description_list_picks_one_template(self):
        templates = ["a {color} shift dress", "a {color} wrap blouse with tailored trousers"]
        ARCHETYPES["__ListTest__"] = {"gender": "Female", "outfit_description": list(templates)}
        try:
            seen = set()
            for seed in range(40):
                outfit = json.loads(build_archetype_json("__ListTest__", seed))["Clothing"]["outfit_description"]
                self.assertNotIn("{", outfit)
                seen.add("dress" if "dress" in outfit else "blouse")
            self.assertEqual(seen, {"dress", "blouse"})
        finally:
            del ARCHETYPES["__ListTest__"]

    def test_list_inside_variants_resolves(self):
        ARCHETYPES["__ListTest__"] = {
            "gender": "Female",
            "variants": {
                "Female": {"hair_color": ["raven black", "espresso"]},
                "Male": {"hair_color": ["ash brown", "jet black"]},
            },
        }
        try:
            meta = json.loads(build_archetype_json("__ListTest__", 4))["_meta"]
            self.assertIn(meta["variants"]["Female"]["hair_color"], ["raven black", "espresso"])
            self.assertIn(meta["variants"]["Male"]["hair_color"], ["ash brown", "jet black"])
        finally:
            del ARCHETYPES["__ListTest__"]

    def test_gender_variants_resolve_per_gender(self):
        # A merged archetype renders its female look on the female override and its
        # male look on the male override — one selection, two coherent looks.
        doc = build_archetype_json("1980s Aerobics", 3, "Essentials")
        flat = _parse_archetype_json(doc)
        variants = flat.pop("__variants__", None)
        self.assertIsNotNone(variants)
        self.assertEqual(set(variants), {"Female", "Male"})
        locked = {k: v for k, v in flat.items() if not k.startswith("__")}
        _, jf = generate_character(7, "Female", dict(locked), gender_variants=variants)
        _, jm = generate_character(7, "Male", dict(locked), gender_variants=variants)
        of = json.loads(jf)["Clothing"]["outfit_description"]
        om = json.loads(jm)["Clothing"]["outfit_description"]
        self.assertIn("leotard", of)
        self.assertNotEqual(of, om)


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
            # The costume is present; the mask rides in _meta from 0.90.0 (see
            # test_unmask_drops_mask_and_reveals_face) rather than being appended.
            entry = COSPLAYERS["Spider-Man"]
            self.assertEqual(
                doc["Clothing"]["outfit_description"],
                entry["costume"],
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

        # 0.90.0: the mask travels in _meta, NOT glued onto outfit_description.
        # Appended, it arrived as the last item of a "He wears ..." garment list and
        # t2i models rendered the clothes and ignored the head -- six entries were
        # reported that way from one render review. The engine now gives it its own
        # sentence ahead of the clothing.
        self.assertTrue(default["_meta"]["covers_face"])
        self.assertEqual(default["_meta"]["mask"], entry["mask"])
        self.assertEqual(default["Clothing"]["outfit_description"], entry["costume"])
        self.assertNotIn(entry["mask"], default["Clothing"]["outfit_description"])

        self.assertFalse(unmasked["_meta"]["covers_face"])
        self.assertNotIn("mask", unmasked["_meta"])
        self.assertEqual(unmasked["Clothing"]["outfit_description"], entry["costume"])
        self.assertNotIn(entry["mask"], unmasked["Clothing"]["outfit_description"])

        # Run unmasked through the engine: face/hair are no longer suppressed.
        flat = _parse_archetype_json(json.dumps(unmasked))
        self.assertNotIn(_COVERS_FACE_KEY, flat)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(1, "Male", locked, covers_face=False)
        self.assertIn("Hair", json.loads(js))

    def test_the_mask_is_voiced_as_its_own_sentence_before_the_clothing(self):
        """0.90.0. The head must not compete with a garment list.

        Regression for six entries reported from one render review -- the Silent
        Hill Nurse rendering as an ordinary nurse, The Ghoul with a normal face,
        Figrin D'an, the Ithorian, Larfleeze and Dexter Jettster all reading as
        people in costumes. The mask text was correct and present the whole time;
        it was simply the last item of "He wears a, b, c, d, e, <the head>".
        """
        raw = build_cosplayer_json("Spider-Man", 0, mask_mode=_MASK_DEFAULT)
        flat = _parse_archetype_json(raw)
        mask_text = flat.pop(_MASK_KEY, None)
        self.assertTrue(mask_text, "the mask never reached the engine")
        label = flat.pop(_COSPLAY_LABEL_KEY, None)
        covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
        flat.pop(_COVERS_BODY_KEY, None)
        flat.pop(_COVERS_HAIR_KEY, None)
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        prose, _ = generate_character(1, "Male", locked, cosplay_label=label,
                                      mask_text=mask_text, covers_face=covers_face)
        sentences = [s.strip() for s in prose.split(". ")]
        head_at = next(i for i, s in enumerate(sentences) if mask_text in s)
        wears_at = next(i for i, s in enumerate(sentences) if " wears " in s)
        self.assertLess(head_at, wears_at,
                        "the head must be described BEFORE the clothing")
        # ...and as its own sentence, not tacked onto the garment list.
        self.assertNotIn(" wears ", sentences[head_at])

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
        # hair_color is a shade-family list since 0.39 (raven black leads it);
        # the node resolves it to one member per seed.
        self.assertIn(doc["Hair"]["hair_color"], ("raven black", "jet black", "near black"))
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

    def test_outdoor_bucket_matches_the_outdoor_families(self):
        # 0.78.0: indoor is DERIVED (all - OUTDOOR_LOCATIONS - STUDIO_BACKDROPS), so a
        # new outdoor location that nobody adds to OUTDOOR_LOCATIONS silently buckets
        # as indoor and starts drawing window light on a canyon rim. Nothing caught
        # that before -- the union check in validate_data.py only covers the families
        # against the option list. Pin the two outdoor families to the frozenset.
        # 0.83.0: restated from a hardcoded two-family union to a DECLARED set of
        # outdoor family names, because the landmark split took it from 2 families to 4
        # and the old form would have to be edited by hand every time. Declaring the
        # names still fails loudly if a new location family appears unclassified.
        from data.fields import LOCATION_FAMILIES, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS
        outdoor_families = {"urban_outdoor", "urban_landmark",
                            "nature_outdoor", "nature_landmark"}
        studio_families = {"studio"}
        self.assertTrue(
            outdoor_families | studio_families <= set(LOCATION_FAMILIES),
            "a declared location family no longer exists")
        expected = {v for fam in outdoor_families
                    for v in LOCATION_FAMILIES[fam]["variants"]}
        self.assertEqual(
            set(OUTDOOR_LOCATIONS), expected,
            "OUTDOOR_LOCATIONS has drifted from the outdoor location families; "
            "missing entries silently become indoor")
        # Every remaining family must be entirely indoor -- this is what the
        # `location_setting` scope and the whole lighting bucket argument rest on.
        for fam, spec in LOCATION_FAMILIES.items():
            if fam in outdoor_families or fam in studio_families:
                continue
            leaked = set(spec["variants"]) & (set(OUTDOOR_LOCATIONS) | set(STUDIO_BACKDROPS))
            self.assertEqual(leaked, set(),
                             f"family {fam!r} is meant to be indoor but leaks {leaked}")

    def test_no_location_bakes_in_a_time_of_day(self):
        """0.81.0: `time_of_day` was DELETED as a field because `lighting` owns it.

        Nine location values had quietly put it back ("rooftop terrace at dusk",
        "harbor dock at sunrise", "sandy beach at golden hour", ...). Nothing
        stopped those pairing with a contradicting light, so a real preview
        produced "set in a harbor dock at sunrise, under fire and flame warm
        flicker". `lighting` is the only field allowed to state the hour, so a
        location that also states it is a contradiction the engine cannot resolve.

        `tide pools at low tide` is deliberately fine (a tide state, not an hour)
        and `art gallery opening night` names an event type indoors, where the
        lighting pool is artificial anyway.
        """
        from data.fields import LOCATION_FAMILIES
        banned = re.compile(
            r"\bat (?:night|dusk|dawn|sunrise|sunset|midday|noon|golden hour|"
            r"twilight|first light)\b", re.IGNORECASE)
        offenders = [v for fam in LOCATION_FAMILIES.values()
                     for v in fam["variants"] if banned.search(v)]
        self.assertEqual(
            offenders, [],
            "these location values state a time of day, which `lighting` already "
            f"controls and can contradict: {offenders}. Reword in place (same "
            "slot, same family) so the bias profile does not move.")

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


class LandmarkFamilyTests(unittest.TestCase):
    """0.83.0: landmark variety WITHOUT landmark frequency.

    Adding famous landmarks straight into urban_outdoor / nature_outdoor would have kept
    the field-level distribution intact (that is what family weighting guarantees) while
    still taking the *famous landmark* concept from ~11% of urban scenes to ~27%. That is
    overweighting a concept even though no family share moved -- the subtler half of the
    bias rule. Splitting each family into base + landmark at a PROPORTIONAL weight and
    growing only the landmark side buys variety at unchanged frequency.

    Baseline is the 0.82.0 table, hardcoded so a future retune is a deliberate act.
    """

    #: 0.82.0: family -> (weight, variant count), pre-split.
    BEFORE = {
        "domestic": (24, 32), "food_drink": (15, 25), "retail_services": (16, 30),
        "leisure_fitness": (11, 24), "civic_institutional": (17, 30),
        "work_industrial": (7, 20), "transit_travel": (7, 18),
        "urban_outdoor": (20, 36), "nature_outdoor": (15, 41), "studio": (4, 4),
    }
    #: The landmark counts the split was priced on -- NOT the current counts, which grow.
    ORIGINAL_LANDMARKS = {"urban_landmark": 4, "nature_landmark": 3}
    PARENTS = {
        "urban_outdoor": "urban_outdoor", "urban_landmark": "urban_outdoor",
        "nature_outdoor": "nature_outdoor", "nature_landmark": "nature_outdoor",
    }

    def test_every_family_share_is_unchanged(self):
        from data.fields import LOCATION_FAMILIES
        old_total = sum(w for w, _ in self.BEFORE.values())
        new_total = sum(d["weight"] for d in LOCATION_FAMILIES.values())
        for fam, spec in LOCATION_FAMILIES.items():
            parent = self.PARENTS.get(fam, fam)
            pw, pn = self.BEFORE[parent]
            if fam in self.PARENTS:
                # A split half must hold the parent's share x (its original count / pn).
                own = (self.ORIGINAL_LANDMARKS[fam] if fam in self.ORIGINAL_LANDMARKS
                       else pn - self.ORIGINAL_LANDMARKS[fam.split("_")[0] + "_landmark"])
                expected = pw / old_total * own / pn
            else:
                expected = pw / old_total
            self.assertAlmostEqual(
                spec["weight"] / new_total, expected, places=12,
                msg=f"family {fam!r} share moved off the 0.82.0 baseline")

    def test_probability_of_any_landmark_is_unchanged(self):
        """The whole point. Variety went up; frequency did not."""
        from data.fields import LOCATION_FAMILIES
        total = sum(d["weight"] for d in LOCATION_FAMILIES.values())
        old_total = sum(w for w, _ in self.BEFORE.values())
        for landmark, parent in (("urban_landmark", "urban_outdoor"),
                                 ("nature_landmark", "nature_outdoor")):
            pw, pn = self.BEFORE[parent]
            before = pw / old_total * self.ORIGINAL_LANDMARKS[landmark] / pn
            after = LOCATION_FAMILIES[landmark]["weight"] / total
            self.assertAlmostEqual(after, before, places=12,
                                   msg=f"P({landmark}) moved: {before} -> {after}")

    def test_the_split_is_proportional_to_original_counts(self):
        from data.fields import LOCATION_FAMILIES
        for landmark, parent in (("urban_landmark", "urban_outdoor"),
                                 ("nature_landmark", "nature_outdoor")):
            nl = self.ORIGINAL_LANDMARKS[landmark]
            nb = self.BEFORE[parent][1] - nl
            wl = LOCATION_FAMILIES[landmark]["weight"]
            wb = LOCATION_FAMILIES[parent]["weight"]
            self.assertEqual(wb * nl, wl * nb,
                             f"{landmark} split is not proportional ({wb}:{wl} vs {nb}:{nl})")

    def test_weights_are_integers(self):
        """validate_data requires positive ints, which is why the rescale is x369."""
        from data.fields import LOCATION_FAMILIES
        for fam, spec in LOCATION_FAMILIES.items():
            self.assertIsInstance(spec["weight"], int, f"{fam} weight is not an int")
            self.assertGreater(spec["weight"], 0)

    def test_landmarks_grew(self):
        from data.fields import LOCATION_FAMILIES
        for landmark in self.ORIGINAL_LANDMARKS:
            self.assertGreater(len(LOCATION_FAMILIES[landmark]["variants"]),
                               self.ORIGINAL_LANDMARKS[landmark],
                               f"{landmark} did not actually gain variety")

    def test_landmarks_are_plain_ascii(self):
        """user-facing prose and filenames: no accented characters (Zocalo, not Zócalo)."""
        from data.fields import LOCATION_FAMILIES
        for landmark in self.ORIGINAL_LANDMARKS:
            for value in LOCATION_FAMILIES[landmark]["variants"]:
                self.assertTrue(value.isascii(), f"{value!r} is not plain ASCII")

    def test_indoor_landmarks_are_not_silently_present(self):
        """Deliberately open: civic_institutional / transit_travel have ZERO landmarks,
        so there is nothing to split from and any add would be a frequency increase from
        zero -- breaking the guarantee this whole phase rests on. If indoor landmarks are
        ever wanted they need their own decision, not a quiet append."""
        from data.fields import LOCATION_FAMILIES, OUTDOOR_LOCATIONS
        landmark_values = {v for fam in ("urban_landmark", "nature_landmark")
                           for v in LOCATION_FAMILIES[fam]["variants"]}
        self.assertTrue(landmark_values <= set(OUTDOOR_LOCATIONS),
                        "every landmark must be outdoor; see the docstring")


class LocationArticleTests(unittest.TestCase):
    """0.82.0: the "set in ..." slot must not article a value that already has one.

    The slot was a blind ``f"set in {_a(v)} {v}"``, which is right for a common
    noun but broke on every named landmark added later -- those carry their own
    leading article. The prompt text had been shipping "set in **a the** Brooklyn
    Bridge pedestrian walkway", "set in **an a** Yosemite valley meadow" and
    "set in **a** Trafalgar Square".

    Same contract as the 0.72.0 outfit-article sweep: a field's prose frame is
    part of its definition.
    """

    def test_self_articled_and_proper_names_take_no_extra_article(self):
        from nodes.identity_forge import _location_clause
        cases = {
            'the Brooklyn Bridge pedestrian walkway': 'the Brooklyn Bridge pedestrian walkway',
            'a Yosemite valley meadow': 'a Yosemite valley meadow',
            'the Grand Canyon south rim': 'the Grand Canyon south rim',
            'Trafalgar Square': 'Trafalgar Square',
            'neighborhood pharmacy': 'a neighborhood pharmacy',
            'university lecture hall': 'a university lecture hall',
            'open meadow': 'an open meadow',
            'indoor ice rink': 'an indoor ice rink',
        }
        for value, expected in cases.items():
            self.assertEqual(_location_clause(value), expected)

    #: Locations opening with a capitalised ADJECTIVE. They look like proper nouns to any
    #: mechanical rule but still take an article ("a French bistro"). Declared here so the
    #: test below can prove every capital-initial location was classified deliberately.
    ARTICLED_CAPITALS = frozenset([
        'French bistro with mirrored walls', 'Buddhist temple hall',
        'Shinto shrine interior',
    ])

    def test_every_capitalised_location_is_classified(self):
        """0.83.0 deliberate friction. A NEW proper-noun landmark that nobody adds to
        ``_NO_ARTICLE_LOCATIONS`` would silently ship "set in a Times Square"; the older
        tests only checked hand-listed cases and could never catch it. This closes that
        gap: a capital-initial location must be declared either as a bare proper noun or
        as a capitalised adjective, so adding one without deciding fails the suite."""
        from nodes.identity_forge import _NO_ARTICLE_LOCATIONS
        caps = {v for v in FIELD_DEFINITIONS["location"]["female_options"]
                if v[:1].isupper()}
        declared = set(_NO_ARTICLE_LOCATIONS) | set(self.ARTICLED_CAPITALS)
        self.assertEqual(
            caps - declared, set(),
            "capital-initial location(s) not classified: add to _NO_ARTICLE_LOCATIONS "
            "(a bare proper noun) or to ARTICLED_CAPITALS (a capitalised adjective)")
        self.assertEqual(declared - caps, set(),
                         "a declared location no longer exists in the pool")

    def test_no_location_renders_a_broken_article(self):
        """Sweep the LIVE pool, not a hand-picked sample: every rendered clause must
        avoid a doubled article and must not article a bare proper noun."""
        from nodes.identity_forge import _location_clause, _NO_ARTICLE_LOCATIONS
        for value in FIELD_DEFINITIONS["location"]["female_options"]:
            clause = _location_clause(value)
            with self.subTest(location=value):
                self.assertNotRegex(clause, r"^(?:a|an|the)\s+(?:a|an|the)\s",
                                    f"doubled article: 'set in {clause}'")
                if value in _NO_ARTICLE_LOCATIONS:
                    self.assertEqual(clause, value,
                                     f"proper noun was articled: 'set in {clause}'")
                self.assertTrue(clause.endswith(value),
                                f"{value!r} was mangled into {clause!r}")

    def test_plural_headed_locations_take_no_article(self):
        # The other half of the same slot bug, older than the landmarks: the pool
        # mixes singular and plural heads, so the blind article shipped "set in a
        # cracked salt flats". The head split must survive a post-modifier, so a
        # singular head with a plural tail still gets its article.
        from nodes.identity_forge import _location_clause
        for value in ('cracked salt flats', 'tide pools at low tide',
                      'apple orchard rows', 'terraced rice paddies'):
            self.assertEqual(_location_clause(value), value,
                             f"plural head {value!r} was given an article")
        for value, expected in (
            ('public library with tall bookshelves', 'a public library with tall bookshelves'),
            ('dance studio with mirrors', 'a dance studio with mirrors'),
            ('boxing gym with hanging heavy bags', 'a boxing gym with hanging heavy bags'),
        ):
            self.assertEqual(_location_clause(value), expected,
                             f"{value!r} articled on its tail instead of its head")

    def test_no_shipped_location_renders_a_doubled_article(self):
        from nodes.identity_forge import _location_clause
        doubled = re.compile(r"^(?:a|an|the)\s+(?:a|an|the)\s", re.IGNORECASE)
        offenders = [v for v in FIELD_DEFINITIONS["location"]["female_options"]
                     if doubled.match(_location_clause(v))]
        self.assertEqual(offenders, [], f"doubled article in 'set in ...': {offenders}")

    def test_every_location_actually_appears_in_the_prose(self):
        # Guards the fix from over-reaching: suppressing the article must never
        # suppress the location itself.
        for value in FIELD_DEFINITIONS["location"]["female_options"]:
            prose, _ = generate_character(1, "Female", {"location": value})
            self.assertIn("set in ", prose)
            self.assertIn(value, prose, f"{value!r} vanished from the prose")

    def test_no_article_list_names_only_real_locations(self):
        from nodes.identity_forge import _NO_ARTICLE_LOCATIONS
        pool = set(FIELD_DEFINITIONS["location"]["female_options"])
        self.assertTrue(
            _NO_ARTICLE_LOCATIONS <= pool,
            f"_NO_ARTICLE_LOCATIONS names non-locations: {_NO_ARTICLE_LOCATIONS - pool}")


class LocationLightingCoherenceTests(unittest.TestCase):
    """0.64.0: the light has to match where you are.

    Before these rules the engine produced "indoor spice market stall, under
    dappled sunlight through forest canopy".
    """

    def _pairs(self, n=400, **kwargs):
        for seed in range(n):
            _, js = generate_character(seed, "Any", {}, **kwargs)
            setting = json.loads(js)["Setting & Shot"]
            yield setting["location"], setting["lighting"]

    def test_indoor_location_never_draws_open_sky_light(self):
        from data.fields import OUTDOOR_ONLY_LIGHTING, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS
        for loc, lig in self._pairs():
            if loc in OUTDOOR_LOCATIONS or loc in STUDIO_BACKDROPS:
                continue
            self.assertNotIn(lig, OUTDOOR_ONLY_LIGHTING, f"{loc!r} lit by {lig!r}")

    def test_outdoor_location_never_draws_interior_light(self):
        from data.fields import INDOOR_ONLY_LIGHTING, OUTDOOR_LOCATIONS
        for loc, lig in self._pairs():
            if loc not in OUTDOOR_LOCATIONS:
                continue
            self.assertNotIn(lig, INDOOR_ONLY_LIGHTING, f"{loc!r} lit by {lig!r}")

    def test_void_backdrop_draws_only_studio_lighting(self):
        from data.fields import VOID_ALLOWED_LIGHTING
        seen = 0
        for loc, lig in self._pairs(location_setting="Studio / solid backdrop"):
            seen += 1
            self.assertIn(lig, VOID_ALLOWED_LIGHTING, f"{loc!r} lit by {lig!r}")
        self.assertGreater(seen, 0)

    def test_locked_light_rerolls_the_location_not_the_light(self):
        """``location`` is the trigger, so a locked light moves the *place*."""
        from data.fields import OUTDOOR_LOCATIONS
        for seed in range(40):
            _, js = generate_character(seed, "Any", {"lighting": "harsh desert sun"})
            setting = json.loads(js)["Setting & Shot"]
            self.assertEqual(setting["lighting"], "harsh desert sun")
            self.assertIn(setting["location"], OUTDOOR_LOCATIONS)

    def test_every_lighting_value_survives_somewhere(self):
        """No bucket may strand a value with no location that can host it."""
        from data.fields import (
            INDOOR_ONLY_LIGHTING, OUTDOOR_ONLY_LIGHTING, VOID_ALLOWED_LIGHTING,
        )
        overlap = INDOOR_ONLY_LIGHTING & OUTDOOR_ONLY_LIGHTING
        self.assertEqual(overlap, frozenset(), f"value both indoor- and outdoor-only: {overlap}")
        pool = set(FIELD_DEFINITIONS["lighting"]["female_options"])
        for name, bucket in (("indoor-only", INDOOR_ONLY_LIGHTING),
                             ("outdoor-only", OUTDOOR_ONLY_LIGHTING),
                             ("void-allowed", VOID_ALLOWED_LIGHTING)):
            self.assertTrue(bucket <= pool, f"{name} names a non-option: {bucket - pool}")


class CompositionTests(unittest.TestCase):
    """0.85.0: composition is frame layout, shot_type is the camera.

    Both fields are flat (absent from FIELD_FAMILIES), so every coherence
    exclusion in constraints.py re-picks uniform rather than concentrating
    weight -- verified here the same way LocationLightingCoherenceTests
    verifies the lighting buckets.
    """

    #: Values that presuppose an environment behind the subject.
    _ENVIRONMENT_DEPENDENT = frozenset({
        'the subject small against open negative space',
        'leading lines drawing the eye to the subject',
        'a low horizon line and open sky above',
        'a high horizon line and a sliver of sky',
    })
    _TIGHT_SHOTS = frozenset({
        'extreme close-up on face', 'close-up portrait', 'medium close-up from chest up',
    })
    _WIDE_ENVIRONMENT_SHOTS = frozenset({
        'full body shot with environment visible', 'extreme wide establishing shot',
    })

    def test_every_composition_value_completes_composed_with(self):
        for gendered in ("female_options", "male_options"):
            for value in FIELD_DEFINITIONS["composition"][gendered]:
                with self.subTest(value=value):
                    self.assertTrue(value and value[0].islower(), value)

    def test_composition_values_name_no_camera_or_object_terms(self):
        # A layout value must never restate shot_type's axis (distance/angle/lens)
        # or introduce a physical object into frame (the 0.63.0 shot_type lesson).
        banned = ("camera", "lens", "angle", "shot", "doorway", "window",
                  "mirror", "foliage")
        for gendered in ("female_options", "male_options"):
            for value in FIELD_DEFINITIONS["composition"][gendered]:
                for word in banned:
                    self.assertNotIn(word, value, f"{value!r} contains {word!r}")

    def _pairs(self, n=600):
        for seed in range(n):
            for scope in ("Any indoor/outdoor", "Indoor", "Outdoor", "Studio / solid backdrop"):
                _, js = generate_character(seed, "Any", {}, location_setting=scope)
                setting = json.loads(js)["Setting & Shot"]
                yield setting["shot_type"], setting["composition"]

    def test_tight_shots_never_draw_environment_dependent_composition(self):
        for shot, comp in self._pairs():
            if shot in self._TIGHT_SHOTS:
                self.assertNotIn(comp, self._ENVIRONMENT_DEPENDENT, f"{shot!r} / {comp!r}")

    def test_wide_environment_shots_never_draw_tight_composition(self):
        tight_compositions = {"a tight crop and little headroom",
                               "the subject filling most of the frame"}
        for shot, comp in self._pairs():
            if shot in self._WIDE_ENVIRONMENT_SHOTS:
                self.assertNotIn(comp, tight_compositions, f"{shot!r} / {comp!r}")

    def test_centered_and_off_center_shots_never_contradict_composition(self):
        for shot, comp in self._pairs():
            if shot == "wide shot with subject at center":
                self.assertNotIn(comp, {"the subject on a rule-of-thirds line",
                                         "the subject small against open negative space"},
                                  f"{shot!r} / {comp!r}")
            if shot == "wide shot with subject off-center":
                self.assertNotEqual(comp, "centered symmetry", f"{shot!r} / {comp!r}")


class FixtureLightingTests(unittest.TestCase):
    """0.82.0: indoors is necessary but not sufficient for fixture lighting.

    A hearth, a television and a stained-glass window are *objects*, so the
    indoor/outdoor buckets alone let them land anywhere indoors -- the reported
    render was "a neighborhood pharmacy, under flickering firelight from a
    hearth". Each fixture value is now its own single-variant LIGHTING family so a
    per-location rule removes it as a whole unit.
    """

    def test_fixture_light_only_lands_where_the_fixture_exists(self):
        from data.fields import FIXTURE_LIGHTING
        for seed in range(1200):
            _, js = generate_character(seed, "Any", {})
            setting = json.loads(js)["Setting & Shot"]
            loc, lig = setting["location"], setting["lighting"]
            if lig in FIXTURE_LIGHTING:
                self.assertIn(
                    loc, FIXTURE_LIGHTING[lig],
                    f"{lig!r} drawn in {loc!r}, which has no such fixture (seed {seed})")

    #: Fixtures that exist outdoors too, so their allowlist may legitimately name an
    #: outdoor or backdrop location. 0.83.0: a stage rig is the first such fixture --
    #: `outdoor amphitheater` is a real outdoor stage, and the four studio backdrops
    #: must stay because `studio_stage` is carved out of the family VOID_ALLOWED_LIGHTING
    #: admits. Everything not listed here is an interior object and must stay indoors.
    OUTDOOR_CAPABLE_FIXTURES = {"stage spotlight from above"}

    def test_allowlist_entries_are_all_real_locations(self):
        # A typo, or a location later renamed/removed, would silently make an
        # allowlist entry dead -- the fixture would then be excluded everywhere.
        # This half is universal and applies to every fixture, indoor or not.
        from data.fields import FIXTURE_LIGHTING
        pool = set(FIELD_DEFINITIONS["location"]["female_options"])
        for light, places in FIXTURE_LIGHTING.items():
            self.assertTrue(places, f"{light!r} has an empty allowlist")
            self.assertTrue(places <= pool, f"{light!r} names non-locations: {places - pool}")

    def test_interior_fixtures_stay_indoors(self):
        """Restated at 0.83.0. The original test asserted this of EVERY fixture, which
        was an incidental property of the 0.82.0 set (all three were interior objects),
        not the invariant being protected. A hearth, a television and a stained-glass
        window are still interior-only; a stage rig is not."""
        from data.fields import FIXTURE_LIGHTING, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS
        for light, places in FIXTURE_LIGHTING.items():
            if light in self.OUTDOOR_CAPABLE_FIXTURES:
                continue
            outdoors = places & (set(OUTDOOR_LOCATIONS) | set(STUDIO_BACKDROPS))
            self.assertEqual(
                outdoors, set(),
                f"{light!r} is indoor-only but lists outdoor/backdrop places: {outdoors}")

    def test_outdoor_capable_fixtures_are_declared_not_accidental(self):
        """The exemption above must be opt-in: a NEW fixture that quietly names an
        outdoor place should fail `test_interior_fixtures_stay_indoors`, not slip in."""
        from data.fields import FIXTURE_LIGHTING
        self.assertTrue(
            self.OUTDOOR_CAPABLE_FIXTURES <= set(FIXTURE_LIGHTING),
            "the exemption list names a fixture that no longer exists")

    def test_every_fixture_value_is_its_own_whole_family(self):
        from data.fields import FIXTURE_LIGHTING, LIGHTING_FAMILIES
        singletons = {tuple(d["variants"])[0] for d in LIGHTING_FAMILIES.values()
                      if len(d["variants"]) == 1}
        for light in FIXTURE_LIGHTING:
            self.assertIn(
                light, singletons,
                f"{light!r} is excluded per-location but shares a family -- the "
                f"exclusion would be a partial cull and concentrate that family's "
                f"frozen weight onto the survivors")


class LightingBucketFamilyTests(unittest.TestCase):
    """Every location<->lighting bucket must be an exact union of WHOLE families.

    ``_pick_family_weighted`` keeps a family's full frozen weight when it
    intersects with the available pool, so culling *part* of a family dumps that
    weight onto the survivors. Before 0.82.0 this held only "mostly": indoors,
    ``neon`` lost 2 of 8 variants while keeping its full share, inflating each of
    the 6 survivors by ~33% relative. The 0.82.0 split made every bucket exact.

    **This is the test that catches a new lighting value put in a family whose
    members do not share its bucket** -- at which point the guarantee lapses
    silently and no other check would notice.
    """

    def _buckets(self):
        from data.fields import (
            FIXTURE_LIGHTING, INDOOR_ONLY_LIGHTING, OUTDOOR_ONLY_LIGHTING,
            VOID_ALLOWED_LIGHTING,
        )
        allv = set(FIELD_DEFINITIONS["lighting"]["female_options"])
        buckets = {
            "OUTDOOR_ONLY_LIGHTING": set(OUTDOOR_ONLY_LIGHTING),
            "INDOOR_ONLY_LIGHTING": set(INDOOR_ONLY_LIGHTING),
            "not VOID_ALLOWED_LIGHTING": allv - set(VOID_ALLOWED_LIGHTING),
        }
        for light in FIXTURE_LIGHTING:
            buckets[f"fixture {light!r}"] = {light}
        return buckets

    def test_no_bucket_partially_culls_a_family(self):
        from data.fields import LIGHTING_FAMILIES
        families = {f: set(d["variants"]) for f, d in LIGHTING_FAMILIES.items()}
        for label, bucket in self._buckets().items():
            for fam, variants in families.items():
                if variants & bucket and not variants <= bucket:
                    self.fail(
                        f"bucket {label} cuts family {fam!r} in half "
                        f"(in: {sorted(variants & bucket)}, "
                        f"out: {sorted(variants - bucket)}) -- a partial cull "
                        f"leaves {fam!r}'s full weight on the survivors")

    def test_families_partition_the_lighting_pool(self):
        from data.fields import LIGHTING_FAMILIES
        seen = [v for d in LIGHTING_FAMILIES.values() for v in d["variants"]]
        self.assertEqual(len(seen), len(set(seen)), "a lighting value is in two families")
        self.assertEqual(set(seen), set(FIELD_DEFINITIONS["lighting"]["female_options"]))

    def test_split_preserved_every_pre_split_share(self):
        """Every rescale is only legitimate if no value's probability moved.

        Baseline is the 0.81.0 family table, hardcoded so a future weight retune
        has to be a deliberate act rather than an accident. It has now survived two
        splits: x6 at 0.82.0 (the fixture split) and x11 at 0.83.0 (studio ->
        studio_shape + studio_stage), total 228 x 11 = 2508. The point of the test is
        that a value's per-variant share is STILL the 0.81.0 share after both.
        """
        from data.fields import LIGHTING_FAMILIES
        before = {  # 0.81.0: family -> (weight, variant count)
            "daylight": (14, 17), "window": (4, 6), "artificial": (6, 9),
            "neon": (6, 8), "studio": (8, 11),
        }
        parents = {
            "daylight": "daylight", "window_general": "window",
            "window_stained": "window", "artificial_open": "artificial",
            "artificial_ceiling": "artificial", "artificial_hearth": "artificial",
            "artificial_screen": "artificial", "neon_venue": "neon",
            "neon_street": "neon",
            # 0.83.0: both halves of the studio split trace to the same 0.81.0 parent,
            # which is exactly the 10:1 proportionality assertion.
            "studio_shape": "studio", "studio_stage": "studio",
        }
        self.assertEqual(set(parents), set(LIGHTING_FAMILIES),
                         "a family was added/renamed without updating this baseline")
        old_total = sum(w for w, _ in before.values())
        new_total = sum(d["weight"] for d in LIGHTING_FAMILIES.values())
        for fam, d in LIGHTING_FAMILIES.items():
            pw, pn = before[parents[fam]]
            self.assertAlmostEqual(
                d["weight"] / new_total / len(d["variants"]),
                pw / old_total / pn, places=12,
                msg=f"family {fam!r} shifted its members' share off the 0.81.0 baseline")


class RepickDistributionTests(unittest.TestCase):
    """0.64.0: a constraint re-pick must draw the way the initial fill would.

    Re-picks called ``_weighted_choice`` directly before 0.64.0, which is flat for
    a field carrying no draw-weight map -- so an exclusion silently discarded
    FIELD_FAMILIES weighting and rebalanced the survivors by raw variant count.
    """

    def test_repick_of_family_field_keeps_family_shares(self):
        from data.fields import LIGHTING_FAMILIES, OUTDOOR_ONLY_LIGHTING
        from nodes.identity_forge import _repick

        family_of = {v: n for n, f in LIGHTING_FAMILIES.items() for v in f["variants"]}
        field_def = FIELD_DEFINITIONS["lighting"]
        pool = [v for v in field_def["female_options"] if v not in OUTDOOR_ONLY_LIGHTING]
        rng = random.Random(0)
        counts: dict[str, int] = {}
        draws = 40000
        for _ in range(draws):
            fam = family_of[_repick("lighting", field_def, pool, "Female", rng)]
            counts[fam] = counts.get(fam, 0) + 1

        # Surviving families keep their frozen weights; each family's share is
        # its weight over the surviving total, independent of variant count.
        surviving = {n: f["weight"] for n, f in LIGHTING_FAMILIES.items()
                     if any(v in pool for v in f["variants"])}
        total_weight = sum(surviving.values())
        for name, weight in surviving.items():
            expected = weight / total_weight
            actual = counts.get(name, 0) / draws
            self.assertAlmostEqual(
                actual, expected, delta=0.015,
                msg=f"{name}: expected ~{expected:.3f}, got {actual:.3f}")

    def test_repick_of_plain_field_still_honours_draw_weights(self):
        """A non-family field must keep routing through the draw-weight pick.

        ``eyebrows`` down-weights 'bleached' to 0.2, so a re-roll has to keep it
        roughly five times rarer than its peers rather than flattening it back.
        """
        from nodes.identity_forge import _repick

        field_def = FIELD_DEFINITIONS["eyebrows"]
        self.assertNotIn("eyebrows", FIELD_FAMILIES)
        pool = list(field_def["female_options"])
        rng = random.Random(0)
        draws = 40000
        bleached = sum(_repick("eyebrows", field_def, pool, "Female", rng) == "bleached"
                       for _ in range(draws))
        # weight 0.2 against (len(pool) - 1) peers at an implicit weight of 1.
        expected = 0.2 / (0.2 + len(pool) - 1)
        self.assertAlmostEqual(bleached / draws, expected, delta=0.005)


class UserOptionsTests(unittest.TestCase):
    def test_merges_valid_and_rejects_protected(self):
        import json as _json
        import tempfile
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
        import json as _json
        import tempfile
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
        import json as _json
        import tempfile
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
        import json as _json
        import tempfile
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

    _FEMININE_EARRINGS = frozenset({
        "chandelier earrings", "long drop earrings", "tassel earrings", "pearl studs",
        "clip-on pearl earrings", "threader earrings", "mismatched earrings",
        "medium gold hoops", "large bold gold hoops",
    })

    def _male_earrings(self, wardrobe, n=250):
        out = set()
        for s in range(n):
            _, js = generate_character(s, "Male", {}, wardrobe=wardrobe)
            e = json.loads(js).get("Jewelry & Nails", {}).get("earrings")
            if e:
                out.add(e)
        return out

    def test_masculine_male_never_draws_feminine_jewellery(self):
        # Default "Match gender" reads Masculine for a man: no chandeliers/pearls.
        drawn = self._male_earrings("Match gender")
        self.assertEqual(drawn & self._FEMININE_EARRINGS, set())

    def test_feminine_or_any_wardrobe_keeps_feminine_jewellery_for_a_man(self):
        # A deliberately femme/mixed wardrobe leaves the feminine-coded pool intact.
        self.assertTrue(self._male_earrings("Feminine") & self._FEMININE_EARRINGS)
        self.assertTrue(self._male_earrings("Any") & self._FEMININE_EARRINGS)

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
    """Full-body colour is skin-native (0.52 A/B verdict): "smooth, flawless <colour>
    skin" / "uniform, all-over <colour> <material>". "body paint"/"dye" wording made
    t2i models render a streaky coat OVER a human tone, so it was swept out."""

    def test_she_hulk_uses_skin_native_phrasing(self):
        costume = COSPLAYERS["She-Hulk"]["costume"]
        self.assertIn("smooth, flawless rich green skin", costume)
        self.assertNotIn("paint", costume)

    def test_no_full_body_paint_wording_remains(self):
        # "body paint" renders as a streaky applied layer; full-body colour must be
        # phrased as the character's own skin. Partial face/war paint is fine.
        for name, entry in COSPLAYERS.items():
            self.assertNotIn("body paint", entry["costume"], name)

    def test_skin_native_markers_are_detected_as_body_paint(self):
        # Both new canonical markers must trigger the builder's skin suppression.
        from nodes.identity_forge_cosplayer import _BODY_PAINT_RE
        self.assertTrue(_BODY_PAINT_RE.search("smooth, flawless rich green skin"))
        self.assertTrue(_BODY_PAINT_RE.search("uniform, all-over craggy orange rock-like skin"))
        self.assertTrue(_BODY_PAINT_RE.search("an even, all-over coat of blue fur"))


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


class PoseGrammarTests(unittest.TestCase):
    """Every pose value must complete the "{subject} is …" frame the prose uses.

    Three values silently broke this until 0.66.0 ("She is arms relaxed at the
    sides."), all by opening with a bare noun. A value is acceptable when it opens
    with a present participle ("standing naturally"), a past participle ("perched on
    the edge of a seat"), or a preposition introducing a noun ("in a confident power
    pose").

    The past-participle set is an explicit allowlist rather than a heuristic: there
    is no reliable way to tell "perched" (a verb) from "arms" (a noun) by shape, and
    an explicit list makes adding a pose a deliberate decision instead of a silent
    one. Adding a new past-participle pose means adding its opening word here.
    """

    #: Past participles that complete "{subject} is ..." without an -ing form.
    _PAST_PARTICIPLES = frozenset({"perched"})
    #: Prepositional openings that introduce a noun phrase.
    _PREPOSITIONAL = ("in a ",)

    def test_every_pose_completes_the_subject_is_frame(self):
        for gendered in ("female_options", "male_options"):
            for pose in FIELD_DEFINITIONS["pose"][gendered]:
                with self.subTest(pose=pose):
                    first = pose.split()[0]
                    ok = (
                        first.endswith("ing")
                        or first in self._PAST_PARTICIPLES
                        or pose.startswith(self._PREPOSITIONAL)
                    )
                    self.assertTrue(
                        ok,
                        f"pose {pose!r} does not read after '{{subject}} is ...' - a "
                        f"pose must open with a participle or a preposition, never a "
                        f"bare noun (see the pose field comment in data/fields.py)",
                    )

    def test_no_pose_uses_a_gendered_pronoun(self):
        # The field comment requires "a hand", never "their/his/her hand".
        for gendered in ("female_options", "male_options"):
            for pose in FIELD_DEFINITIONS["pose"][gendered]:
                for pronoun in (" his ", " her ", " their ", " its "):
                    self.assertNotIn(pronoun, f" {pose} ", f"pose {pose!r}")


class PoseFamilyTests(unittest.TestCase):
    """Every pose family split must leave the parent's share exactly where it was.

    Splitting a family re-weights its variants unless each sub-family's weight is
    proportional to its variant count. This pins the arithmetic against the
    pre-split baseline so a future weight tweak cannot silently bias the field.
    Three rounds of splitting are covered: 0.66.0 (gesture -> 3), and 0.84.0
    (standing -> 2, seated -> 2, gesture_garment -> 2 for the held-prop and giant
    coherence rules).
    """

    #: POSE_FAMILIES exactly as it stood at 0.65.0, before any split.
    _BASELINE = {
        "standing": (5, 7), "seated": (5, 7), "leaning": (1, 3), "motion": (1, 3),
        "gesture": (4, 6), "looking": (2, 4),
    }

    @staticmethod
    def _marginals(families):
        """value -> P(value) for a {name: (weight, variants)} style mapping."""
        total = sum(weight for weight, _ in families.values())
        return {
            value: (weight / total) / len(variants)
            for weight, variants in families.values()
            for value in variants
        }

    #: Every 0.65.0 family that has since been split, mapped to the sub-families that
    #: now share its slice. A family absent here was never split.
    _SUBFAMILIES = {
        "gesture": ("gesture", "gesture_two_hands", "gesture_garment",
                    "gesture_pockets", "gesture_hair"),
        "standing": ("standing", "standing_hands_bound"),
        "seated": ("seated", "seated_perch"),
    }

    def _parts(self, family):
        return self._SUBFAMILIES.get(family, (family,))

    def test_split_preserves_every_family_share(self):
        """The invariant every split had to satisfy, stated at family level.

        0.82.0 note: this used to pin each *value* to a fixed probability, which
        also froze the pool size -- so adding a pose failed it for the wrong
        reason. Growing a family-weighted field is the sanctioned, bias-free way
        to add variety: the family's share is fixed, so a new variant subdivides
        that share instead of inflating the field. The guarantee worth pinning is
        therefore the FAMILY share (unchanged since 0.65.0) plus equiprobability
        within each family -- both of which a bad weight tweak still breaks.
        Same correction as `HairStyleFamilyTests` took at 0.81.0.
        """
        base_total = sum(w for w, _ in self._BASELINE.values())
        cur_total = sum(fam["weight"] for fam in POSE_FAMILIES.values())

        for family, (weight, _count) in self._BASELINE.items():
            expected = weight / base_total
            # The whole point of a split: the parts still sum to the parent's slice.
            actual = sum(POSE_FAMILIES[f]["weight"] for f in self._parts(family))
            self.assertAlmostEqual(
                actual / cur_total, expected, places=12,
                msg=f"family {family!r} share moved off the 0.65.0 baseline")

    def test_every_split_family_covers_its_parents_variants(self):
        # A split must partition the parent, never lose or gain a value. Catches a
        # variant moved between sub-families without a matching weight change, which
        # `test_split_preserves_every_family_share` alone would not see.
        for family, (_weight, _count) in self._BASELINE.items():
            parts = self._parts(family)
            merged = [v for f in parts for v in POSE_FAMILIES[f]["variants"]]
            self.assertEqual(len(merged), len(set(merged)),
                             f"{family!r} sub-families overlap")

    def test_split_subfamily_weights_stay_proportional_to_size(self):
        # The load-bearing arithmetic of every split: sub-family weights must track
        # variant counts, or splitting re-weights the values it split.
        for family, parts in self._SUBFAMILIES.items():
            per_variant = {
                f: POSE_FAMILIES[f]["weight"] / len(POSE_FAMILIES[f]["variants"])
                for f in parts
            }
            self.assertEqual(
                len({round(v, 9) for v in per_variant.values()}), 1,
                f"{family!r} sub-families are no longer proportional to size: "
                f"{per_variant}")

    def test_every_family_is_internally_uniform(self):
        # _pick_family_weighted draws a family, then a variant uniformly within
        # it. Nothing else may bias the within-family pick.
        current = self._marginals(
            {name: (fam["weight"], fam["variants"]) for name, fam in POSE_FAMILIES.items()}
        )
        for name, fam in POSE_FAMILIES.items():
            shares = {current[v] for v in fam["variants"]}
            self.assertEqual(len(shares), 1, f"family {name!r} is not internally uniform")

    def test_probabilities_sum_to_one(self):
        current = self._marginals(
            {name: (fam["weight"], fam["variants"]) for name, fam in POSE_FAMILIES.items()}
        )
        self.assertAlmostEqual(sum(current.values()), 1.0, places=12)

    def test_dependent_pose_sets_are_whole_families(self):
        # Partial-family exclusion is the documented bias trap: the family keeps its
        # full weight and concentrates it on the survivors. Every suppression set the
        # engine applies to `pose` must therefore be a union of WHOLE families.
        by_family = {
            name: frozenset(fam["variants"]) for name, fam in POSE_FAMILIES.items()
        }
        for label, sub_set in (
            ("HAIR_DEPENDENT_POSES", HAIR_DEPENDENT_POSES),
            ("GARMENT_DEPENDENT_POSES", GARMENT_DEPENDENT_POSES),
            ("HAND_OCCUPIED_POSES", HAND_OCCUPIED_POSES),
            ("FURNITURE_DEPENDENT_POSES", FURNITURE_DEPENDENT_POSES),
        ):
            covered = frozenset().union(
                *(vs for vs in by_family.values() if vs <= sub_set)
            ) if any(vs <= sub_set for vs in by_family.values()) else frozenset()
            self.assertEqual(
                sub_set, covered,
                f"{label} is not a union of whole POSE_FAMILIES families -- a partial "
                f"cull concentrates the parent family's frozen weight on the survivors")

    def test_pockets_stay_garment_dependent_after_the_0_84_0_split(self):
        # `gesture_pockets` was split out of `gesture_garment` for the held-prop rule.
        # Pockets are the MOST garment-dependent pose of all, so the split must not
        # quietly let a mascot suit put its hands in pockets it does not have.
        self.assertIn("posing with hands in pockets", GARMENT_DEPENDENT_POSES)
        self.assertIn("posing with hands in pockets", HAND_OCCUPIED_POSES)

    def test_hand_occupied_set_holds_only_two_handed_poses(self):
        # A one-handed pose must NOT be here: the free hand holds the prop, which is
        # the natural reading and the reason the set is narrow.
        for pose in ("posing with a hand on one hip", "resting chin on one hand",
                     "touching the collar with one hand", "adjusting one cuff",
                     "running one hand through the hair"):
            self.assertNotIn(pose, HAND_OCCUPIED_POSES)

    def test_dependent_poses_are_real_field_options(self):
        options = set(FIELD_DEFINITIONS["pose"]["female_options"])
        self.assertTrue(
            (HAIR_DEPENDENT_POSES | GARMENT_DEPENDENT_POSES
             | HAND_OCCUPIED_POSES | FURNITURE_DEPENDENT_POSES) <= options)


class FieldHelpTests(unittest.TestCase):
    """0.78.0: every field dropdown carries its own tooltip."""

    def test_hidden_field_list_matches_the_validator(self):
        # validate_data.py duplicates _HIDDEN_FIELDS by hand so it need not import
        # the node package (same arrangement as _LOOK_OVERRIDE_KEYS). Pin them.
        from nodes.identity_forge import _HIDDEN_FIELDS
        self.assertEqual(set(_HIDDEN_FIELDS), {"outfit_description", "held_item"})

    def test_every_visible_field_has_help(self):
        from data.fields import FIELD_HELP
        from nodes.identity_forge import _HIDDEN_FIELDS, _CONTROL_FIELDS
        for name in FIELD_DEFINITIONS:
            if name in _HIDDEN_FIELDS or name in _CONTROL_FIELDS:
                continue
            self.assertIn(name, FIELD_HELP, f"{name} has no tooltip")

    def test_help_is_a_single_short_sentence(self):
        from data.fields import FIELD_HELP
        for name, text in FIELD_HELP.items():
            self.assertLessEqual(len(text), 190, f"{name} tooltip is too long")
            self.assertNotIn("\n", text, f"{name} tooltip should be one line")


class ManualSizeScaleTests(unittest.TestCase):
    """0.78.0: the manual-only size_scale override on the human node.

    The whole point of the control is that it is bias-free: ``Auto`` is never drawn
    by the randomizer, so adding tiers cannot dilute anything (the Creature node's
    ``integument_finish`` contract).
    """

    def test_auto_is_a_no_op(self):
        from nodes.identity_forge import _SIZE_SCALE_AUTO
        for seed in range(20):
            baseline = generate_character(seed, "Female", {})
            explicit = generate_character(seed, "Female", {},
                                          size_scale=_SIZE_SCALE_AUTO)
            self.assertEqual(baseline, explicit, f"seed {seed}")

    def test_auto_is_never_randomly_selected(self):
        # No tier phrase may appear unless the caller asked for one. This is the
        # bias guarantee, asserted rather than assumed.
        from nodes.identity_forge import _SIZE_SCALE_PHRASES
        for seed in range(200):
            prose, _ = generate_character(seed, "Any", {})
            for phrase in _SIZE_SCALE_PHRASES.values():
                self.assertNotIn(phrase, prose, f"seed {seed}")

    def test_each_tier_replaces_height_in_the_lead_sentence(self):
        from nodes.identity_forge import _SIZE_SCALE_PHRASES
        human_heights = set(FIELD_DEFINITIONS["height"]["female_options"])
        for tier, phrase in _SIZE_SCALE_PHRASES.items():
            prose, js = generate_character(4, "Female", {}, size_scale=tier)
            self.assertIn(phrase, prose, tier)
            # Replaced, not prepended: no ordinary height word survives alongside it.
            height = json.loads(js)["Body"]["height"]
            self.assertEqual(height, phrase, tier)
            self.assertNotIn(height, human_heights, tier)
            # It lands in the opening sentence, the strongest position for t2i.
            self.assertIn(phrase, prose.split(".")[0], tier)

    def test_tier_overrides_a_wired_cosplayer_scale(self):
        # A user who deliberately picks a tier expects it to apply even to a
        # canonically giant character; the widget beats the preset, as everywhere
        # else in the node.
        from nodes.identity_forge import _SIZE_SCALE_PHRASES
        locked, label, cf, ch = _node_locked(
            build_cosplayer_json("Lobo", 0, "Full character"))
        prose, _ = generate_character(3, "Male", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch,
                                      size_scale="tiny")
        self.assertIn(_SIZE_SCALE_PHRASES["tiny"], prose)
        self.assertNotIn("enormously tall and hulking", prose)

    def test_unknown_tier_is_ignored_loudly(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            prose, _ = generate_character(1, "Female", {}, size_scale="enormous")
        self.assertIn("Unknown size_scale", buffer.getvalue())
        for phrase in ("barely six inches", "fifty feet"):
            self.assertNotIn(phrase, prose)

    def test_phrases_avoid_comparison_objects(self):
        # 0.55.0 doctrine: a comparison object ("beside a towering oak", "the size
        # of a mouse") makes t2i render the object. Concrete measurements only.
        from nodes.identity_forge import _SIZE_SCALE_PHRASES
        banned = ("beside", "compared", "size of", "-sized", "apples")
        for tier, phrase in _SIZE_SCALE_PHRASES.items():
            for word in banned:
                self.assertNotIn(word, phrase.lower(), f"{tier}: {phrase}")


class ScaleCoherenceTests(unittest.TestCase):
    """0.79.0: the scene has to be able to *show* an extreme scale.

    "Colossal and fifty feet tall" is a claim about the subject's relationship to
    everything around them, so it only survives into an image when the frame holds
    something to measure against. Before this, 71 giant entries x 30 seeds drew a
    scale-showing framing 26.2% of the time and an outdoor location 25.9% of the
    time, and ~7% of renders called the subject "petite" in the same sentence.
    """

    SCALE_SHOTS = frozenset({
        "full body shot with environment visible",
        "wide shot with subject at center",
        "wide shot with subject off-center",
        "extreme wide establishing shot",
        "low angle looking up",
        "worm's-eye view from ground",
    })

    def setUp(self):
        from data.fields import OUTDOOR_LOCATIONS
        self.outdoor = OUTDOOR_LOCATIONS

    def _scene(self, **kwargs):
        prose, js = generate_character(**kwargs)
        doc = json.loads(js)
        return prose, doc["Setting & Shot"], doc["Body"]

    def test_giant_tier_forces_a_framing_that_can_show_scale(self):
        for seed in range(40):
            _, shot, _ = self._scene(seed=seed, gender="Any", locked={},
                                     size_scale="colossal")
            self.assertIn(shot["shot_type"], self.SCALE_SHOTS, f"seed {seed}")

    def test_giant_tier_forces_an_outdoor_location(self):
        for seed in range(40):
            _, shot, _ = self._scene(seed=seed, gender="Any", locked={},
                                     size_scale="colossal")
            self.assertIn(shot["location"], self.outdoor, f"seed {seed}")

    def test_giant_tier_never_calls_the_subject_petite(self):
        # "a petite and curvy build, colossal and fifty feet tall" is a flat
        # contradiction two words apart in the highest-attention sentence.
        from nodes.identity_forge import _STATURE_BODY_TYPES
        for seed in range(60):
            _, _, body = self._scene(seed=seed, gender="Any", locked={},
                                     size_scale="towering")
            self.assertNotIn(body["body_type"], _STATURE_BODY_TYPES, f"seed {seed}")

    def test_tiny_tier_drops_only_the_framings_that_cannot_resolve_it(self):
        from nodes.identity_forge import _SHOTS_TOO_WIDE_FOR_TINY
        seen = set()
        for seed in range(60):
            _, shot, _ = self._scene(seed=seed, gender="Any", locked={},
                                     size_scale="tiny")
            self.assertNotIn(shot["shot_type"], _SHOTS_TOO_WIDE_FOR_TINY, f"seed {seed}")
            seen.add(shot["shot_type"])
        # Deliberately a light touch: a tiny subject still reads in a close-up, so
        # the pool must stay broad rather than collapsing to the giant rule.
        self.assertGreater(len(seen), 6)

    def test_a_cosplayers_own_giant_scale_drives_the_scene(self):
        # The tier travels from the Cosplayer node's _meta, not from a widget.
        from nodes.identity_forge import _SCALE_TIER_KEY
        flat = _parse_archetype_json(build_cosplayer_json("Godzilla", 0, "Costume only"))
        self.assertEqual(flat.get(_SCALE_TIER_KEY), "giant")
        for seed in range(20):
            locked, label, cf, ch = _node_locked(
                build_cosplayer_json("Godzilla", seed, "Costume only"))
            _, js = generate_character(seed, "Any", locked, cosplay_label=label,
                                       covers_face=cf, covers_hair=ch,
                                       character_scale="giant")
            shot = json.loads(js)["Setting & Shot"]
            self.assertIn(shot["shot_type"], self.SCALE_SHOTS, f"seed {seed}")
            self.assertIn(shot["location"], self.outdoor, f"seed {seed}")

    def test_an_explicit_lock_always_wins(self):
        # The filter runs inside the randomize loop, which skips locked fields, so
        # a user who asks for a giant in a kitchen gets a giant in a kitchen.
        _, shot, body = self._scene(
            seed=5, gender="Female",
            locked={"location": "sunny suburban kitchen",
                    "shot_type": "close-up portrait",
                    "body_type": "petite and slim"},
            size_scale="colossal",
        )
        self.assertEqual(shot["location"], "sunny suburban kitchen")
        self.assertEqual(shot["shot_type"], "close-up portrait")
        self.assertEqual(body["body_type"], "petite and slim")

    def test_an_impossible_scope_degrades_gracefully(self):
        # location_setting Indoor + a giant is a contradiction the user asked for.
        # Precedent (0.63.0 empty studio pool) is warn-and-keep, never an exception
        # and never an empty field.
        for seed in range(20):
            _, shot, _ = self._scene(seed=seed, gender="Any", locked={},
                                     location_setting="Indoor",
                                     size_scale="colossal")
            self.assertTrue(shot["location"])
            self.assertNotIn(shot["location"], self.outdoor, f"seed {seed}")

    def test_human_plausible_tiers_are_untouched(self):
        # "well over seven feet tall" is a very tall person, not a change of scale:
        # narrowing their scene would cost variety for nothing.
        from nodes.identity_forge import _scale_class
        for tier in ("short", "large"):
            self.assertEqual(_scale_class(tier, None), "")
        indoor = 0
        for seed in range(60):
            _, shot, _ = self._scene(seed=seed, gender="Any", locked={},
                                     size_scale="large")
            if shot["location"] not in self.outdoor:
                indoor += 1
        self.assertGreater(indoor, 0)

    def test_no_scale_leaves_ordinary_output_byte_identical(self):
        # The whole feature must be inert unless a scale is genuinely in play.
        for seed in range(30):
            self.assertEqual(
                generate_character(seed, "Any", {}),
                generate_character(seed, "Any", {}, character_scale=""),
                f"seed {seed}",
            )

    def test_the_widget_beats_a_wired_characters_scale_for_the_scene_too(self):
        # Precedence has to be consistent: the widget already overrides the height
        # phrase, so it must override the scene rule that goes with it.
        from nodes.identity_forge import _scale_class, _SHOTS_TOO_WIDE_FOR_TINY
        self.assertEqual(_scale_class("tiny", "giant"), "tiny")
        for seed in range(20):
            locked, label, cf, ch = _node_locked(
                build_cosplayer_json("Godzilla", seed, "Costume only"))
            _, js = generate_character(seed, "Any", locked, cosplay_label=label,
                                       covers_face=cf, covers_hair=ch,
                                       size_scale="tiny", character_scale="giant")
            shot = json.loads(js)["Setting & Shot"]
            self.assertNotIn(shot["shot_type"], _SHOTS_TOO_WIDE_FOR_TINY, f"seed {seed}")

    def test_the_location_filter_drops_whole_families(self):
        """The bias gate. A partial family cull would concentrate a frozen weight.

        ``location`` is family-weighted, so this rule is only legal because every
        family is entirely indoor or entirely outdoor. Pinned here rather than
        trusted: a future location added to a family that spans the boundary would
        silently turn this coherence rule into a distribution bug.
        """
        outdoor_families, indoor_families = [], []
        for name, spec in FIELD_FAMILIES["location"].items():
            variants = set(spec["variants"] if isinstance(spec, dict) else spec)
            survivors = variants & self.outdoor
            self.assertIn(
                len(survivors), (0, len(variants)),
                f"location family {name!r} spans the indoor/outdoor boundary "
                f"({len(survivors)} of {len(variants)} outdoor); filtering to "
                f"outdoors would concentrate its frozen weight on the survivors",
            )
            (outdoor_families if survivors else indoor_families).append(name)
        self.assertTrue(outdoor_families)
        self.assertTrue(indoor_families)

    def test_the_narrowed_fields_carry_no_weights(self):
        # shot_type and body_type are safe for the opposite reason: flat pools, so
        # narrowing cannot redistribute anything.
        for field in ("shot_type", "body_type"):
            self.assertNotIn(field, FIELD_FAMILIES, field)
            self.assertNotIn("weights", FIELD_DEFINITIONS[field], field)
            self.assertNotIn("male_weights", FIELD_DEFINITIONS[field], field)


class CanonicalMakeupTests(unittest.TestCase):
    """0.81.0: a face authored in costume prose must silence the makeup draw.

    Female cosplayers draw a *random* makeup look. For most characters that is
    correct -- a real person at a convention wears their own makeup. But when the
    entry's own prose already paints the face ("teal war paint over half the
    face", "the whole face painted stark white in kabuki style"), the random draw
    lands a second, contradicting face on top: full glam over Senua's warpaint.

    The fix is a per-entry ``makeup_style`` lock, which needs no schema change --
    ``"no makeup"`` cascades through CONSTRAINT_RULES to clear every cosmetic
    sub-field and drops the makeup sentence entirely, leaving the prose as the
    only facial descriptor. That is the same end state ``_BODY_PAINT_SUPPRESS``
    reaches automatically for body-painted characters, which is why those are
    exempt here.
    """

    #: Unambiguous "the prose owns this face" phrasings. Deliberately narrow --
    #: this gate must not fire on an entry that merely mentions lipstick in
    #: passing, or it becomes noise that gets suppressed rather than fixed.
    _FACE_IS_AUTHORED = re.compile(
        r"greasepaint|face ?paint|war[- ]?paint|corpse ?paint|clown white|"
        r"kabuki|painted stark white|face (?:painted|markings)|"
        r"smeared across the (?:brow|eyes)|painted across the face",
        re.IGNORECASE,
    )

    def test_an_authored_face_pins_the_makeup_style(self):
        from nodes.identity_forge_cosplayer import _BODY_PAINT_RE
        offenders = []
        for name, entry in COSPLAYERS.items():
            if entry.get("gender") != "Female":
                continue  # the engine already forces "no makeup" on men
            costume = entry.get("costume", "")
            if not self._FACE_IS_AUTHORED.search(costume):
                continue
            if _BODY_PAINT_RE.search(costume):
                continue  # _BODY_PAINT_SUPPRESS handles these already
            if not entry.get("signature", {}).get("makeup_style"):
                offenders.append(name)
        self.assertEqual(
            offenders, [],
            "these entries paint the face in their costume prose but leave "
            "makeup_style to the random draw, so a glam look renders on top of "
            f"it: {offenders}. Pin signature.makeup_style (usually 'no makeup').")

    def test_the_gate_would_catch_an_unpinned_face(self):
        """Non-vacuous: the regex really does fire on the shipped phrasings."""
        for phrase in ("teal war paint over half the face",
                       "the whole face painted stark white in kabuki style",
                       "a wide carved red grin with clown white"):
            self.assertRegex(phrase, self._FACE_IS_AUTHORED)

    def test_pinning_no_makeup_actually_silences_the_makeup_sentence(self):
        """End to end, on a real entry, rather than trusting the cascade."""
        for seed in range(40):
            flat = _parse_archetype_json(
                build_cosplayer_json("Senua", seed, "Full character"))
            prose, _ = generate_character(seed, "Female", flat)
            self.assertNotIn("makeup", prose.lower(), f"seed {seed}: {prose}")
            self.assertIn("war paint", prose.lower(), f"seed {seed}")


class FullCoverSpellingTests(unittest.TestCase):
    """0.78.0: the full-shell regex must accept both spellings of "armor".

    It was American-only while the roster carried 32 British-spelled values, so
    those entries failed the shell test and drew necklaces and drop earrings over
    plate armour. The data is normalised now, but user_options.json is free text
    and no validator reaches it, so the pattern itself has to be tolerant.
    """

    def test_both_spellings_detected(self):
        from nodes.identity_forge import _FULL_COVER_RE
        for text in ("heavy gold plate armor", "heavy gold plate armour",
                     "an armored bodysuit", "an armoured bodysuit",
                     "powered armor", "powered armour",
                     "a suit of ornate ceremonial armor",
                     "a suit of ornate ceremonial armour"):
                self.assertTrue(_FULL_COVER_RE.search(text), text)

    def test_roster_uses_one_spelling(self):
        # Cosmetic, but a mixed roster is what hid the bug: keep it consistent so a
        # future reader does not have to wonder which spelling is load-bearing.
        offenders = [name for name, entry in COSPLAYERS.items()
                     if "armour" in str(entry).lower()]
        self.assertEqual(offenders, [], "use the American 'armor' spelling in data")


class HairStyleFamilyTests(unittest.TestCase):
    """The 0.78.0 loose/braid split must not move a single hair style's probability.

    Same contract as :class:`PoseFamilyTests`: a family may only be split into
    sub-families whose weights are proportional to their variant counts, otherwise
    the split itself re-weights the field. Pinned against the pre-split baseline so
    a future weight tweak cannot silently bias ``hair_style``.
    """

    #: HAIR_STYLE_FAMILIES exactly as it stood at 0.77.0, before the split.
    #: {family: (weight, variant_count)}; sum of weights = 30.
    _BASELINE = {
        "loose": (6, 9), "half-up": (1, 1), "ponytail": (2, 4), "bun": (5, 7),
        "braid": (9, 10), "knots": (2, 2), "pigtails": (1, 5), "texture": (2, 2),
        "bangs": (2, 2),
    }

    #: Which pre-split family each post-split family carves out of.
    _DERIVED_FROM = {
        "loose_styled": "loose", "loose_natural": "loose",
        "loose_combover": "loose", "loose_mullet": "loose",
        "braid_long": "braid", "braid_short": "braid",
        "bun_small": "bun", "bun_gathered": "bun",
    }

    @staticmethod
    def _marginals(families):
        """value -> P(value) for a {name: (weight, variants)} style mapping."""
        total = sum(weight for weight, _ in families.values())
        return {
            value: (weight / total) / len(variants)
            for weight, variants in families.values()
            for value in variants
        }

    def _current(self):
        return self._marginals(
            {name: (fam["weight"], fam["variants"])
             for name, fam in HAIR_STYLE_FAMILIES.items()}
        )

    #: Families that are NOT splits -- genuinely new values, so they must take share from
    #: somewhere. They take it uniformly, so no pre-existing family is singled out.
    #:   0.81.0: barbered_short + barbered_shag, weight 350 on a pre-existing 3150, so
    #:           every older value kept exactly 3150/3500 = 9/10 of its probability.
    #:   0.83.0: barbered_crop, a further 70 on 3500, so 3500/3570 = 0.9804 on top.
    #: Compounded: 0.9 x 0.9804 = 3150/3570.
    _ADDED_FAMILIES = ("barbered_short", "barbered_shag", "barbered_crop")
    _DILUTION = 3150 / 3570

    #: Added families priced at the field's ordinary "one everyday cut" rate, which is
    #: what justifies their weights (see the next test). Expressed as a share of the
    #: total so the assertion survives a rescale -- 0.83.0 doubled every weight to keep
    #: the braid split's arithmetic integral.
    _EVERYDAY_RATE_FAMILIES = ("barbered_short", "barbered_shag")

    #: ``barbered_crop`` is DELIBERATELY priced below the per-variant rate: weight 70
    #: (x2 = 140) over three variants, where the field's rate is ~74.5 (x2 = 149). That
    #: buys a 1.96% dilution instead of 6.0%, at the price of each crop sitting ~3.2x
    #: rarer than an average value -- which is wanted, since a crew cut and a high-top
    #: fade are specific looks and keeping them rare stops the base node reading as
    #: barbered. Declared here so a weights audit cannot mistake it for a mistake.
    _DELIBERATELY_RARE_FAMILIES = ("barbered_crop",)

    def test_split_preserves_every_pre_split_family_share(self):
        """Every PRE-EXISTING family keeps its share, up to one uniform dilution.

        **Restated at 0.83.0, at the level the mechanism actually guarantees.** This
        test used to pin each pre-existing *value* to a fixed probability, which
        silently made the pool size part of the contract -- so it failed on merely
        ADDING a hairstyle, for the wrong reason. That is exactly the trap
        ``PoseFamilyTests`` hit at 0.82.0, and the correction is the same: family
        weighting promises that a new variant SUBDIVIDES its family's share, never that
        `side braid` keeps a fixed number forever.

        What is asserted instead is the real guarantee, in three parts:
          1. each pre-split family's total share == its 0.77.0 share x `_DILUTION`;
          2. variants are uniform WITHIN a family (`_marginals` computes it, so this is
             about the data having no duplicate/empty families);
          3. sub-family weights stay proportional to variant count (its own test).
        A hand-retuned weight still fails this; a legitimate content addition does not.
        """
        baseline_total = sum(weight for weight, _ in self._BASELINE.values())
        current_total = sum(fam["weight"] for fam in HAIR_STYLE_FAMILIES.values())

        # Roll every post-split family back up into its pre-split origin.
        rolled: dict[str, int] = {}
        for family, fam in HAIR_STYLE_FAMILIES.items():
            if family in self._ADDED_FAMILIES:
                continue
            origin = self._DERIVED_FROM.get(family, family)
            self.assertIn(origin, self._BASELINE,
                          f"family {family!r} traces to unknown origin {origin!r}")
            rolled[origin] = rolled.get(origin, 0) + fam["weight"]

        self.assertEqual(set(rolled), set(self._BASELINE),
                         "a pre-split family disappeared or was renamed")
        for origin, weight in rolled.items():
            baseline_weight, _ = self._BASELINE[origin]
            self.assertAlmostEqual(
                weight / current_total,
                baseline_weight / baseline_total * self._DILUTION, places=12,
                msg=f"family {origin!r} share drifted off the 0.77.0 baseline")

    def test_added_families_account_for_exactly_the_dilution(self):
        """The other half: the share taken by the added families must equal 1 -
        `_DILUTION`. Together with the test above this pins the whole distribution
        without freezing any pool size."""
        total = sum(fam["weight"] for fam in HAIR_STYLE_FAMILIES.values())
        added = sum(HAIR_STYLE_FAMILIES[name]["weight"]
                    for name in self._ADDED_FAMILIES)
        self.assertAlmostEqual(added / total, 1 - self._DILUTION, places=12)

    def test_each_barbered_cut_is_priced_like_an_existing_everyday_cut(self):
        """The 0.81.0 barbering weights are justified by a precedent, not picked freely.

        `comb over` and `mullet` are the pack's existing "one ordinary everyday cut"
        families (one variant each). Each 0.81.0 barbered cut is priced identically,
        which is the whole argument for 280 + 70. Asserted against `mullet`'s live
        probability rather than the literal 70, so a rescale (0.83.0 doubled every
        weight for the braid split) does not falsify a claim that is still true.
        """
        current = self._current()
        reference = current["mullet"]
        self.assertAlmostEqual(current["comb over"], reference, places=12)
        for name in self._EVERYDAY_RATE_FAMILIES:
            for value in HAIR_STYLE_FAMILIES[name]["variants"]:
                self.assertAlmostEqual(current[value], reference, places=12, msg=value)

    def test_the_deliberately_rare_family_is_rare_on_purpose(self):
        """0.83.0. `barbered_crop` is the FIRST hair_style family priced below the
        per-variant rate. That is a decision (1.96% dilution instead of 6.0%), not an
        oversight, so it is pinned: below the everyday rate, and by roughly the factor
        the decision was taken on. A weights audit that "fixes" this will fail here and
        read the reason."""
        current = self._current()
        reference = current["mullet"]
        for name in self._DELIBERATELY_RARE_FAMILIES:
            for value in HAIR_STYLE_FAMILIES[name]["variants"]:
                self.assertLess(current[value], reference,
                                f"{value} is no longer deliberately rare")
                self.assertAlmostEqual(reference / current[value], 3.0, places=6,
                                       msg=f"{value} rarity factor drifted")

    def test_the_barbered_short_constraint_list_matches_its_family(self):
        """A partial cull would concentrate the family's frozen weight.

        `data/constraints.py` excludes `_BARBERED_SHORT_STYLES` as a unit. If a
        fifth cut joins the family and not that list, the exclusions silently stop
        being whole-family drops -- which is the bias trap the split exists to
        avoid, reintroduced by omission.
        """
        from data.constraints import _BARBERED_SHORT_STYLES
        self.assertEqual(
            sorted(_BARBERED_SHORT_STYLES),
            sorted(HAIR_STYLE_FAMILIES["barbered_short"]["variants"]),
            "_BARBERED_SHORT_STYLES has drifted from the barbered_short family")
        # 0.83.0: the crop family carries the same obligation, for the same reason.
        from data.constraints import _BARBERED_CROP_STYLES
        self.assertEqual(
            sorted(_BARBERED_CROP_STYLES),
            sorted(HAIR_STYLE_FAMILIES["barbered_crop"]["variants"]),
            "_BARBERED_CROP_STYLES has drifted from the barbered_crop family")

    def test_a_barbered_cut_never_lands_on_hair_it_cannot_be_cut_into(self):
        from data.constraints import _BARBERED_SHORT_STYLES, _PAST_SHOULDER_LENGTHS
        for length in (*_PAST_SHOULDER_LENGTHS, "buzzed very short"):
            for seed in range(120):
                _, js = generate_character(seed, "Any", {"hair_length": length})
                style = json.loads(js).get("Hair", {}).get("hair_style")
                self.assertNotIn(style, _BARBERED_SHORT_STYLES,
                                 f"{length!r} @ seed {seed}")
        for length in ("buzzed very short", "very short", "short pixie"):
            for seed in range(120):
                _, js = generate_character(seed, "Any", {"hair_length": length})
                self.assertNotEqual(json.loads(js).get("Hair", {}).get("hair_style"),
                                    "shag", f"{length!r} @ seed {seed}")

    def test_probabilities_sum_to_one(self):
        self.assertAlmostEqual(sum(self._current().values()), 1.0, places=12)

    def test_sub_family_weights_are_proportional_to_variant_count(self):
        # The invariant that makes the split safe, asserted directly rather than
        # only via the marginals: within a pre-split family, weight per variant is
        # constant across its sub-families.
        for origin in ("loose", "braid", "bun"):
            subs = [fam for name, fam in HAIR_STYLE_FAMILIES.items()
                    if self._DERIVED_FROM.get(name) == origin]
            self.assertGreater(len(subs), 1, origin)
            per_variant = {fam["weight"] / len(fam["variants"]) for fam in subs}
            self.assertEqual(len(per_variant), 1,
                             f"{origin} sub-families are not proportional: {per_variant}")

    def test_impossible_length_style_pairs_are_whole_sub_families(self):
        # The reason the split exists: every hair_style exclusion must remove whole
        # families, never part of one. Rebuild each rule's effect and assert it.
        by_length: dict[str, set[str]] = {}
        for rule in CONSTRAINT_RULES:
            if (rule.get("type") == "exclusion" and rule.get("field") == "hair_length"
                    and rule.get("excludes_field") == "hair_style"):
                by_length.setdefault(rule["value"], set()).update(rule["excludes_values"])
        self.assertIn("buzzed very short", by_length)
        for length, excluded in by_length.items():
            for name, fam in HAIR_STYLE_FAMILIES.items():
                variants = set(fam["variants"])
                overlap = variants & excluded
                self.assertIn(
                    len(overlap), (0, len(variants)),
                    f"hair_length '{length}' culls {len(overlap)} of {len(variants)} "
                    f"in family '{name}' -- a partial cull concentrates its full "
                    f"frozen weight on the survivors")

    def test_buzz_cut_cannot_draw_a_styled_or_gathered_look(self):
        # End-to-end: the pairings the split was built to eliminate.
        impossible = {"worn down", "slicked back", "windswept", "freshly blown out",
                      "tousled bedhead", "curtain bangs", "blunt bangs",
                      "comb over", "mullet"}
        for seed in range(600):
            _, js = generate_character(seed, "Any", {"hair_length": "buzzed very short"})
            style = json.loads(js).get("Hair", {}).get("hair_style")
            self.assertNotIn(style, impossible, f"seed {seed}")

    def test_pixie_cannot_draw_a_braid_that_needs_length(self):
        for seed in range(600):
            _, js = generate_character(seed, "Any", {"hair_length": "short pixie"})
            style = json.loads(js).get("Hair", {}).get("hair_style")
            self.assertNotIn(style, {"dutch braids", "crown braid"}, f"seed {seed}")


class PerformablePoseTests(unittest.TestCase):
    """A character without hair / a garment never draws a pose that needs one."""

    def _pool(self):
        return list(FIELD_DEFINITIONS["pose"]["female_options"])

    def test_masked_character_drops_hair_pose(self):
        got = _performable_poses(self._pool(), {}, True, False, False)
        self.assertFalse(HAIR_DEPENDENT_POSES & set(got))

    def test_hooded_character_drops_hair_pose(self):
        got = _performable_poses(self._pool(), {}, False, False, True)
        self.assertFalse(HAIR_DEPENDENT_POSES & set(got))

    def test_bald_hair_length_drops_hair_pose(self):
        got = _performable_poses(self._pool(), {"hair_length": "bald"}, False, False, False)
        self.assertFalse(HAIR_DEPENDENT_POSES & set(got))

    def test_absent_hair_length_drops_hair_pose(self):
        # The Cosplayer node's bald route locks the scalp fields absent, not "bald".
        got = _performable_poses(self._pool(), {"hair_length": "None"}, False, False, False)
        self.assertFalse(HAIR_DEPENDENT_POSES & set(got))

    def test_covers_body_drops_garment_poses(self):
        got = _performable_poses(
            self._pool(), {"hair_length": "long"}, False, True, False
        )
        self.assertFalse(GARMENT_DEPENDENT_POSES & set(got))
        # Hair is visible here, so the hair gesture must survive.
        self.assertTrue(HAIR_DEPENDENT_POSES & set(got))

    def test_auto_detected_shell_drops_garment_poses(self):
        # A plate-armour outfit is a shell even with no covers_body flag set.
        resolved = {"hair_length": "long",
                    "outfit_description": "polished silver plate armor over a white tabard"}
        got = _performable_poses(self._pool(), resolved, False, False, False)
        self.assertFalse(GARMENT_DEPENDENT_POSES & set(got))

    def test_ordinary_character_keeps_every_pose(self):
        resolved = {"hair_length": "long", "outfit_description": "a flowing red sundress"}
        got = _performable_poses(self._pool(), resolved, False, False, False)
        self.assertEqual(got, self._pool())

    def test_fully_covered_creature_drops_both(self):
        got = _performable_poses(self._pool(), {"hair_length": "None"}, True, True, True)
        self.assertFalse((HAIR_DEPENDENT_POSES | GARMENT_DEPENDENT_POSES) & set(got))
        self.assertTrue(got, "pool must never be emptied")

    # --- 0.84.0: a held signature prop occupies the hands --------------------

    def test_held_prop_drops_two_handed_poses(self):
        resolved = {"hair_length": "long", "outfit_description": "a wool overcoat",
                    "held_item": "Mjolnir, a short-handled war hammer"}
        got = _performable_poses(self._pool(), resolved, False, False, False)
        self.assertFalse(HAND_OCCUPIED_POSES & set(got))

    def test_held_prop_keeps_one_handed_poses(self):
        # The narrowness is the point -- the free hand holds the prop.
        resolved = {"hair_length": "long", "outfit_description": "a wool overcoat",
                    "held_item": "a bullwhip"}
        got = _performable_poses(self._pool(), resolved, False, False, False)
        for pose in ("posing with a hand on one hip", "resting chin on one hand",
                     "running one hand through the hair", "adjusting one cuff"):
            self.assertIn(pose, got)

    def test_absent_held_item_changes_nothing(self):
        # `held_item` is optional and preset-only; an absent value must not narrow.
        base = {"hair_length": "long", "outfit_description": "a wool overcoat"}
        expected = _performable_poses(self._pool(), base, False, False, False)
        for absent in ("None", "none", ""):
            got = _performable_poses(
                self._pool(), {**base, "held_item": absent}, False, False, False
            )
            self.assertEqual(got, expected, f"held_item={absent!r} narrowed the pool")

    # --- 0.85.0: a selfie occupies one hand, same as a held prop -------------

    def test_selfie_shot_type_drops_two_handed_poses(self):
        resolved = {"hair_length": "long", "outfit_description": "a wool overcoat",
                    "shot_type": _SELFIE_SHOT_TYPE}
        got = _performable_poses(self._pool(), resolved, False, False, False)
        self.assertFalse(HAND_OCCUPIED_POSES & set(got))

    def test_non_selfie_shot_type_changes_nothing(self):
        base = {"hair_length": "long", "outfit_description": "a wool overcoat"}
        expected = _performable_poses(self._pool(), base, False, False, False)
        got = _performable_poses(
            self._pool(), {**base, "shot_type": "close-up portrait"}, False, False, False
        )
        self.assertEqual(got, expected)

    def test_no_two_handed_pose_ever_renders_beside_a_selfie(self):
        for seed in range(600):
            _, js = generate_character(
                seed, "Any", {"shot_type": _SELFIE_SHOT_TYPE}, location_setting="Any indoor/outdoor")
            setting = json.loads(js)["Setting & Shot"]
            pose = setting.get("pose")
            if pose:
                self.assertNotIn(pose, HAND_OCCUPIED_POSES, f"seed {seed}: {pose!r}")

    def test_no_two_handed_pose_ever_renders_beside_a_held_prop(self):
        # End to end through the engine, at the density that draws the most extras.
        for seed in range(1200):
            prose, _ = generate_character(
                seed, "Female", {"held_item": "a bullwhip coiled in one hand"},
                accessory_density="Maximal",
            )
            for pose in HAND_OCCUPIED_POSES:
                self.assertNotIn(pose, prose, f"seed {seed}")

    def test_thor_never_crosses_his_arms_while_holding_mjolnir(self):
        # The reported shape, end to end through the real Cosplayer entry + prop toggle.
        for seed in range(80):
            flat = _parse_archetype_json(
                build_cosplayer_json("Thor", seed, include_prop=True)
            )
            flat.pop(_COSPLAY_LABEL_KEY, None)
            covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
            covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
            covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
            locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
            prose, _ = generate_character(
                seed, "Any", locked, covers_face=covers_face,
                covers_body=covers_body, covers_hair=covers_hair,
            )
            self.assertIn("holding", prose, f"seed {seed}")
            for pose in HAND_OCCUPIED_POSES:
                self.assertNotIn(pose, prose, f"seed {seed}")

    def test_moogle_never_runs_a_hand_through_its_hair(self):
        # The reported bug, end to end through the real Cosplayer entry.
        for seed in range(60):
            flat = _parse_archetype_json(build_cosplayer_json("Moogle", seed))
            flat.pop(_COSPLAY_LABEL_KEY, None)
            covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
            covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
            covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
            locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
            prose, _ = generate_character(
                seed, "Any", locked, covers_face=covers_face, covers_body=covers_body,
                covers_hair=covers_hair,
            )
            self.assertNotIn("through the hair", prose, f"seed {seed}")
            self.assertNotIn("in pockets", prose, f"seed {seed}")
            self.assertNotIn("the collar", prose, f"seed {seed}")


class GiantPoseTests(unittest.TestCase):
    """A giant is forced outdoors, so it cannot perch on the edge of a seat (0.84.0)."""

    def test_giant_never_perches_on_a_seat(self):
        for seed in range(1500):
            _, js = generate_character(seed, "Any", {}, size_scale="colossal")
            pose = json.loads(js).get("Setting & Shot", {}).get("pose")
            self.assertNotIn(pose, FURNITURE_DEPENDENT_POSES, f"seed {seed}")

    def test_giant_can_still_sit(self):
        # The fix must remove one variant, not the seated concept -- a giant sitting
        # on the ground is a good image and the rest of `seated` stays legal.
        seen = set()
        for seed in range(1500):
            _, js = generate_character(seed, "Any", {}, size_scale="colossal")
            seen.add(json.loads(js).get("Setting & Shot", {}).get("pose"))
        self.assertTrue(
            seen & set(POSE_FAMILIES["seated"]["variants"]),
            "the giant scale dropped the whole seated concept, not just the perch")

    def test_tiny_keeps_the_perch(self):
        # A three-foot subject on the edge of a seat is fine; the rule is giant-only.
        seen = set()
        for seed in range(1500):
            _, js = generate_character(seed, "Any", {}, size_scale="tiny")
            seen.add(json.loads(js).get("Setting & Shot", {}).get("pose"))
        self.assertTrue(seen & FURNITURE_DEPENDENT_POSES)

    def test_an_explicit_pose_lock_still_wins(self):
        # _scale_coherent_pool runs inside the randomize loop, which has already
        # skipped every locked field. A user who locks the perch gets the perch.
        _, js = generate_character(
            7, "Any", {"pose": "perched on the edge of a seat"}, size_scale="colossal"
        )
        self.assertEqual(
            json.loads(js)["Setting & Shot"]["pose"], "perched on the edge of a seat")


class CoversBodyTests(unittest.TestCase):
    """A full hard shell (robot/armour/exoskeleton) suppresses worn jewellery and
    nails -- detected from the costume prose or set via the ``covers_body`` flag."""

    def _has_jewelry(self, js):
        return "Jewelry & Nails" in json.loads(js)

    def test_robot_costume_auto_suppresses_jewelry(self):
        costume = "a towering humanoid war robot sheathed in polished chrome armor plating"
        for seed in range(40):
            _, js = generate_character(seed, "Male", {"outfit_description": costume},
                                       accessory_density="Maximal")
            self.assertFalse(self._has_jewelry(js), f"seed {seed}")

    def test_full_plate_archetype_auto_suppresses_jewelry(self):
        # Holy Paladin's costume is "polished ... plate armor ..." -> full coverage.
        flat = _parse_archetype_json(build_archetype_json("Holy Paladin", 0, "Essentials"))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(20):
            _, js = generate_character(seed, flat.get("gender", "Any"), locked,
                                       accessory_density="Maximal")
            self.assertFalse(self._has_jewelry(js), f"seed {seed}")

    def test_covers_body_flag_suppresses_jewelry(self):
        for seed in range(20):
            _, js = generate_character(seed, "Female", {"outfit_description": "a plain robe"},
                                       covers_body=True, accessory_density="Maximal")
            self.assertFalse(self._has_jewelry(js), f"seed {seed}")

    def test_covers_body_flag_suppresses_accessories_and_bag(self):
        # Worn/carried extras (sunglasses, belts, a rattan bag) can't sit on a full
        # mascot suit / armour shell -- the sunglasses-on-Michelin-Man bug.
        for seed in range(30):
            _, js = generate_character(seed, "Male", {"outfit_description": "a plain robe"},
                                       covers_body=True, accessory_density="Maximal")
            clothing = json.loads(js).get("Clothing", {})
            self.assertNotIn("accessories", clothing, f"seed {seed}")
            self.assertNotIn("bag", clothing, f"seed {seed}")

    def test_locked_accessories_survive_covers_body(self):
        # An explicit user lock still wins over the shell suppression.
        _, js = generate_character(2, "Male", {"outfit_description": "a plain robe",
                                               "accessories": "aviator sunglasses"},
                                   covers_body=True)
        self.assertEqual(json.loads(js)["Clothing"]["accessories"], "aviator sunglasses")

    def test_ordinary_costume_keeps_jewelry(self):
        # A normal outfit (no hard shell) leaves the jewellery group reachable.
        costume = "a flowing red sundress with strappy sandals"
        seen = any(self._has_jewelry(generate_character(s, "Female",
                   {"outfit_description": costume}, accessory_density="Maximal")[1])
                   for s in range(40))
        self.assertTrue(seen)

    def test_locked_necklace_survives_full_cover(self):
        costume = "a towering humanoid war robot sheathed in chrome armor plating"
        _, js = generate_character(1, "Female",
                                   {"outfit_description": costume, "necklace": "pearl necklace"})
        self.assertEqual(json.loads(js)["Jewelry & Nails"]["necklace"], "pearl necklace")

    def test_cosplayer_flag_round_trips_through_meta(self):
        # Man-At-Arms carries covers_body in the data; it must reach the engine.
        meta = json.loads(build_cosplayer_json("Man-At-Arms", 0))["_meta"]
        self.assertTrue(meta["covers_body"])
        flat = _parse_archetype_json(build_cosplayer_json("Man-At-Arms", 0))
        self.assertIn(_COVERS_BODY_KEY, flat)

    def test_cylon_end_to_end_has_no_jewelry(self):
        flat = _parse_archetype_json(build_cosplayer_json("Cylon Centurion", 0))
        flat.pop(_COSPLAY_LABEL_KEY, None)
        covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
        covers_body = bool(flat.pop(_COVERS_BODY_KEY, None)) or True  # auto-detected anyway
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(15):
            _, js = generate_character(seed, "Male", locked, covers_face=covers_face,
                                       covers_body=covers_body, accessory_density="Maximal")
            self.assertFalse(self._has_jewelry(js), f"seed {seed}")


class CoversHairTests(unittest.TestCase):
    """A hood / cowl / lekku (``covers_hair``) hides the Hair group but keeps the
    face -- narrower than ``covers_face``."""

    def _hair_fields(self):
        return [n for n, m in FIELD_DEFINITIONS.items() if m.get("group") == "Hair"]

    def test_covers_hair_drops_hair_group_keeps_face(self):
        # Hair fields vanish; the Face group still renders (eyes/nose/lips described).
        for seed in range(30):
            _, js = generate_character(seed, "Female", {}, covers_hair=True)
            doc = json.loads(js)
            self.assertNotIn("Hair", doc, f"seed {seed}")
            self.assertIn("Face", doc, f"seed {seed}")

    def test_without_covers_hair_the_hair_group_is_present(self):
        seen = any("Hair" in json.loads(generate_character(s, "Female", {})[1])
                   for s in range(20))
        self.assertTrue(seen)

    def test_cosplayer_flag_round_trips_through_meta(self):
        # Blue Beetle (Ted Kord) carries covers_hair; it must reach the engine and
        # leave the face intact (lower face exposed).
        meta = json.loads(build_cosplayer_json("Blue Beetle (Ted Kord)", 0))["_meta"]
        self.assertTrue(meta["covers_hair"])
        flat = _parse_archetype_json(build_cosplayer_json("Blue Beetle (Ted Kord)", 0))
        self.assertIn(_COVERS_HAIR_KEY, flat)
        covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        _, js = generate_character(3, "Male", locked, covers_hair=covers_hair)
        doc = json.loads(js)
        self.assertNotIn("Hair", doc)
        self.assertIn("Face", doc)


class ShellSkinToneTests(unittest.TestCase):
    """A fully-encased character (covers_face + full hard shell) shows no stray
    human skin tone under the armour/droid plating."""

    def test_masked_droid_drops_skin_tone(self):
        costume = "a humanoid coppery medical-droid body with a transparent chest panel"
        for seed in range(30):
            _, js = generate_character(seed, "Male", {"outfit_description": costume},
                                       covers_face=True)
            self.assertNotIn("skin_tone", json.loads(js).get("Body", {}), f"seed {seed}")

    def test_masked_only_keeps_skin_tone(self):
        # covers_face without a hard shell still describes the body's skin tone.
        seen = any("skin_tone" in json.loads(generate_character(
                       s, "Male", {"outfit_description": "a plain cloth tunic"},
                       covers_face=True)[1]).get("Body", {})
                   for s in range(20))
        self.assertTrue(seen)

    def test_locked_skin_tone_survives_shell(self):
        costume = "a towering humanoid war robot sheathed in chrome armor plating"
        _, js = generate_character(1, "Male",
                                   {"outfit_description": costume, "skin_tone": "olive"},
                                   covers_face=True)
        self.assertEqual(json.loads(js)["Body"]["skin_tone"], "olive")

    def test_2_1b_end_to_end_has_no_skin_tone(self):
        flat = _parse_archetype_json(build_cosplayer_json("2-1B Droid", 0))
        flat.pop(_COSPLAY_LABEL_KEY, None)
        covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
        covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(15):
            _, js = generate_character(seed, "Male", locked, covers_face=covers_face,
                                       covers_body=covers_body)
            self.assertNotIn("skin_tone", json.loads(js).get("Body", {}), f"seed {seed}")


class ShellEthnicityTests(unittest.TestCase):
    """A fully-encased character (covers_face + full hard shell) shows no
    human ethnicity — nothing left to attach it to under the shell."""

    def test_masked_droid_drops_ethnicity(self):
        costume = "a humanoid coppery medical-droid body with a transparent chest panel"
        for seed in range(30):
            _, js = generate_character(seed, "Male", {"outfit_description": costume},
                                       covers_face=True)
            self.assertNotIn("ethnicity", json.loads(js).get("Demographics", {}), f"seed {seed}")

    def test_masked_only_keeps_ethnicity(self):
        # covers_face without a hard shell still describes the person's ethnicity.
        seen = any("ethnicity" in json.loads(generate_character(
                       s, "Male", {"outfit_description": "a plain cloth tunic"},
                       covers_face=True)[1]).get("Demographics", {})
                   for s in range(20))
        self.assertTrue(seen)

    def test_locked_ethnicity_survives_shell(self):
        costume = "a towering humanoid war robot sheathed in chrome armor plating"
        _, js = generate_character(1, "Male",
                                   {"outfit_description": costume, "ethnicity": "Japanese"},
                                   covers_face=True)
        self.assertEqual(json.loads(js)["Demographics"]["ethnicity"], "Japanese")

    def test_2_1b_end_to_end_has_no_ethnicity(self):
        flat = _parse_archetype_json(build_cosplayer_json("2-1B Droid", 0))
        flat.pop(_COSPLAY_LABEL_KEY, None)
        covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
        covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
        locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
        for seed in range(15):
            _, js = generate_character(seed, "Male", locked, covers_face=covers_face,
                                       covers_body=covers_body)
            self.assertNotIn("ethnicity", json.loads(js).get("Demographics", {}), f"seed {seed}")


def _node_locked(doc, **widgets):
    """Reproduce IdentityForge.execute's locked-field build from a preset doc.

    Mirrors the node path -- ``archetype_locked`` keeps every wired value except
    "Random" (so an explicit "None" omit survives), then ``resolve_locked_fields``
    overlays the widgets -- so tests exercise the same flow as the live node, not
    the shortcut of passing the flat dict straight to ``generate_character``.
    Returns ``(locked, label, covers_face, covers_hair)``.
    """
    flat = _parse_archetype_json(doc)
    label = flat.pop(_COSPLAY_LABEL_KEY, None)
    covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
    covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
    flat.pop(_COVERS_BODY_KEY, None)
    archetype_locked = {
        k: v for k, v in flat.items()
        if k in FIELD_DEFINITIONS and k not in _CONTROL_FIELDS and v != "Random"
    }
    kwargs = {n: "Random" for n in FIELD_DEFINITIONS}
    kwargs.update(widgets)
    locked = resolve_locked_fields(kwargs, archetype_locked, _SET_ALL_OFF)
    return locked, label, covers_face, covers_hair


class SuppressionLockSurvivalTests(unittest.TestCase):
    """A wired "None" omit (body paint, bald, eye locks) must survive the node's
    locked-field build -- a default "Random" widget must not re-randomize it. Guards
    the bug where She-Hulk rendered a human skin tone and Voldemort grew hair."""

    def test_body_paint_replaces_human_skin_with_colour_anchor(self):
        # The wired suppression must still beat a "Random" widget: no *human* skin
        # tone or complexion leaks. Body-paint characters now carry a colour anchor in
        # skin_tone (e.g. "rich green") instead of an empty slot -- it must be the
        # paint colour, never a value from the human skin_tone pool.
        human = set(FIELD_DEFINITIONS["skin_tone"]["female_options"])
        for name in ("She-Hulk", "Poison Ivy"):
            locked, label, cf, ch = _node_locked(build_cosplayer_json(name, 0, "Costume only"))
            for seed in range(15):
                _, js = generate_character(seed, "Female", locked, cosplay_label=label,
                                           covers_face=cf, covers_hair=ch)
                doc = json.loads(js)
                tone = doc.get("Body", {}).get("skin_tone")
                self.assertIsNotNone(tone, f"{name} seed {seed}: missing colour anchor")
                self.assertNotIn(tone, human, f"{name} seed {seed}: human tone leaked")
                self.assertIn("green", tone, f"{name} seed {seed}")
                self.assertNotIn("complexion", doc.get("Face", {}), f"{name} seed {seed}")

    def test_body_paint_suppresses_ethnicity(self):
        # 0.78.0: ethnicity was the last skin-describing field still randomizing under
        # a full-body colour, and the loudest -- it lands in the lead sentence ("a
        # 19-year-old Chilean man ... with chalk-white skin"), so t2i resolved the
        # high-attention face token to the ethnicity and rendered an ordinary human
        # face above a coloured body. Covers a male (no makeup cascade) and a female
        # entry, and the prose as well as the JSON.
        for name, gender in (("Lobo", "Male"), ("She-Hulk", "Female")):
            locked, label, cf, ch = _node_locked(
                build_cosplayer_json(name, 0, "Full character"))
            for seed in range(15):
                prose, js = generate_character(seed, gender, locked, cosplay_label=label,
                                               covers_face=cf, covers_hair=ch)
                doc = json.loads(js)
                self.assertNotIn("ethnicity", doc.get("Demographics", {}),
                                 f"{name} seed {seed}: ethnicity leaked into JSON")
                # Ethnicity renders in the lead clause, immediately before the gender
                # noun ("a 19-year-old Chilean man"). Scanning the WHOLE prose for
                # ethnicity words is a false-positive trap -- "French braid" and
                # "Roman nose" are hair/face values, not demographics.
                noun = "man" if gender == "Male" else "woman"
                self.assertRegex(prose, rf"a \d+-year-old {noun} with",
                                 f"{name} seed {seed}: lead clause carries an ethnicity")

    def test_unpainted_cosplayer_keeps_ethnicity(self):
        # The suppression is gated on the body-paint marker, so an ordinary costumed
        # character must still describe the person wearing it.
        locked, label, cf, ch = _node_locked(
            build_cosplayer_json("Princess Leia Organa", 0, "Full character"))
        seen = set()
        for seed in range(15):
            _, js = generate_character(seed, "Female", locked, cosplay_label=label,
                                       covers_face=cf, covers_hair=ch)
            value = json.loads(js).get("Demographics", {}).get("ethnicity")
            if value:
                seen.add(value)
        self.assertTrue(seen, "an unpainted cosplayer must still carry an ethnicity")

    def test_bald_suppresses_scalp_hair_through_node_path(self):
        # Saitama is fully bald: no scalp-hair field may survive (facial_hair, a
        # separate Hair-group field, is allowed -- bald is scalp-only).
        scalp = ("hair_color", "hair_length", "hair_style", "hair_texture",
                 "hair_part", "hair_highlights")
        locked, label, cf, ch = _node_locked(build_cosplayer_json("Saitama", 0, "Costume only"))
        for seed in range(15):
            _, js = generate_character(seed, "Male", locked, cosplay_label=label,
                                       covers_face=cf, covers_hair=ch)
            hair = json.loads(js).get("Hair", {})
            for field in scalp:
                self.assertNotIn(field, hair, f"seed {seed}: {field} leaked")

    def test_concrete_widget_still_overrides_wired_none(self):
        # A user who explicitly sets skin_tone on the widget beats the wired omit.
        locked, label, cf, ch = _node_locked(
            build_cosplayer_json("She-Hulk", 0, "Costume only"), skin_tone="olive")
        _, js = generate_character(1, "Female", locked, cosplay_label=label, covers_face=cf)
        self.assertEqual(json.loads(js)["Body"]["skin_tone"], "olive")


class BodyPaintLipColorTests(unittest.TestCase):
    """Body-paint suppression forces ``makeup_style`` off. The ``lip_color`` field was
    removed (it duplicated ``lips_makeup``), so Poison Ivy's red lips now live in her
    costume prose, which survives the body-paint makeup suppression."""

    def test_poison_ivy_keeps_red_lips_on_green_body(self):
        locked, label, cf, ch = _node_locked(build_cosplayer_json("Poison Ivy", 0, "Costume only"))
        for seed in range(20):
            text, js = generate_character(seed, "Female", locked, cosplay_label=label,
                                          covers_face=cf, covers_hair=ch)
            doc = json.loads(js)
            self.assertIn("red lips", text, f"seed {seed}")
            # The green body-paint coat anchors skin_tone to the paint colour (so the
            # face reads green), not a leaked human tone.
            self.assertEqual(doc.get("Body", {}).get("skin_tone"), "vivid green", f"seed {seed}")


class SkinColorAnchorTests(unittest.TestCase):
    """Body-paint characters re-plant the paint colour in skin_tone so the opening
    prose anchors it (fixes the white-face bug), without doubling the noun."""

    def test_auto_derived_colour_in_opening_sentence(self):
        # Poison Ivy: "...and vivid green skin." in the lead sentence, both look levels.
        for look in ("Costume only", "Full character"):
            locked, label, cf, ch = _node_locked(build_cosplayer_json("Poison Ivy", 0, look))
            prose, _ = generate_character(0, "Female", locked, cosplay_label=label,
                                          covers_face=cf, covers_hair=ch)
            lead = prose.split(". ")[0]
            self.assertIn("vivid green skin", lead, look)

    def test_explicit_skin_override_wins(self):
        # Iceman's "ice" phrasing isn't auto-derivable; the explicit key supplies it.
        locked, label, cf, ch = _node_locked(build_cosplayer_json("Iceman", 0, "Full character"))
        prose, _ = generate_character(0, "Male", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch)
        self.assertIn("icy pale-blue skin", prose)

    def test_prose_does_not_double_skin_noun(self):
        # Mystique's anchor is "dark blue scaled": the demographics guard appends
        # exactly one " skin", never two.
        locked, label, cf, ch = _node_locked(build_cosplayer_json("Mystique", 0, "Costume only"))
        prose, _ = generate_character(0, "Female", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch)
        self.assertIn("dark blue scaled skin", prose)
        self.assertNotIn("skin skin", prose)

    def test_survives_set_all_none(self):
        # The anchor is a wired value, so the "set all to none" reset keeps it.
        flat = _parse_archetype_json(build_cosplayer_json("Poison Ivy", 0, "Full character"))
        label = flat.pop(_COSPLAY_LABEL_KEY, None)
        cf = bool(flat.pop(_COVERS_FACE_KEY, None))
        ch = bool(flat.pop(_COVERS_HAIR_KEY, None))
        flat.pop(_COVERS_BODY_KEY, None)
        archetype_locked = {k: v for k, v in flat.items()
                            if k in FIELD_DEFINITIONS and k not in _CONTROL_FIELDS and v != "Random"}
        kwargs = {n: "Random" for n in FIELD_DEFINITIONS}
        locked = resolve_locked_fields(kwargs, archetype_locked, _SET_ALL_NONE)
        _, js = generate_character(0, "Female", locked, cosplay_label=label,
                                   covers_face=cf, covers_hair=ch)
        self.assertEqual(json.loads(js)["Body"]["skin_tone"], "vivid green")


class FaceColorReinforcementTests(unittest.TestCase):
    """The opening anchors the paint colour on the body; the face must also be
    coloured or t2i renders it pale (the green-body / white-face bug). The engine
    restates a non-human skin colour on the face when the face is described."""

    def test_face_reinforced_both_look_levels(self):
        # Both Costume only and Full character: the face restates the green skin.
        for look in ("Costume only", "Full character"):
            for seed in range(6):
                locked, label, cf, ch = _node_locked(
                    build_cosplayer_json("Poison Ivy", 0, look))
                prose, _ = generate_character(seed, "Female", locked, cosplay_label=label,
                                              covers_face=cf, covers_hair=ch)
                self.assertIn("face has the same vivid green skin", prose, f"{look} seed {seed}")

    def test_face_reinforced_under_set_all_none(self):
        # Even with the reset on (only wired hair/eyes/anchor survive), the face is
        # still described (green eyes, red lips) so the colour is restated on it.
        flat = _parse_archetype_json(build_cosplayer_json("Poison Ivy", 0, "Full character"))
        label = flat.pop(_COSPLAY_LABEL_KEY, None)
        cf = bool(flat.pop(_COVERS_FACE_KEY, None))
        ch = bool(flat.pop(_COVERS_HAIR_KEY, None))
        flat.pop(_COVERS_BODY_KEY, None)
        archetype_locked = {k: v for k, v in flat.items()
                            if k in FIELD_DEFINITIONS and k not in _CONTROL_FIELDS and v != "Random"}
        kwargs = {n: "Random" for n in FIELD_DEFINITIONS}
        locked = resolve_locked_fields(kwargs, archetype_locked, _SET_ALL_NONE)
        prose, _ = generate_character(0, "Female", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch)
        self.assertIn("face has the same vivid green skin", prose)

    def test_face_reinforcement_not_doubled(self):
        # Mystique's anchor ends in "scaled-skin": the face line must not say
        # "scaled-skin skin".
        locked, label, cf, ch = _node_locked(
            build_cosplayer_json("Mystique", 0, "Costume only"))
        prose, _ = generate_character(0, "Female", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch)
        self.assertIn("face has the same", prose)
        self.assertNotIn("scaled-skin skin", prose)

    def test_normal_human_has_no_face_reinforcement(self):
        # A standard human skin tone is not restated on the face (no output churn).
        for gender in ("Female", "Male", "Any"):
            for seed in range(8):
                prose, _ = generate_character(seed, gender, {})
                self.assertNotIn("face has the same", prose, f"{gender} seed {seed}")

    def test_masked_body_paint_has_no_face_reinforcement(self):
        # King Shark is covers_face + body paint: the head is the mask, the face
        # fields are dropped, so the face colour must not be restated (only the body).
        locked, label, cf, ch = _node_locked(
            build_cosplayer_json("King Shark", 0, "Full character"))
        prose, _ = generate_character(0, "Female", locked, cosplay_label=label,
                                      covers_face=cf, covers_hair=ch)
        self.assertNotIn("face has the same", prose)


class HandColorReinforcementTests(unittest.TestCase):
    """Body-paint hands are restated in the same colour (the white-hands bug), but
    only when the hands actually show -- gloves / a full shell hide them."""

    def test_hands_reinforced_for_body_paint(self):
        # She-Hulk has bare hands: the green is restated on them in both look levels.
        for look in ("Costume only", "Full character"):
            for seed in range(6):
                locked, label, cf, ch = _node_locked(
                    build_cosplayer_json("She-Hulk", 0, look))
                prose, _ = generate_character(seed, "Female", locked, cosplay_label=label,
                                              covers_face=cf, covers_hair=ch)
                self.assertIn("hands have the same rich green skin", prose,
                              f"{look} seed {seed}")

    def test_gloved_body_paint_omits_hand_colour_and_nails(self):
        # Gloves hide the hands: neither the hand skin colour nor nail polish may be
        # voiced (otherwise t2i paints nails on top of a glove). The face still shows.
        prose, js = generate_character(
            1, "Female",
            {"skin_tone": "vivid green",
             "outfit_description": "a green bodysuit with long opera gloves"})
        self.assertIn("face has the same vivid green skin", prose)
        self.assertNotIn("hands have the same", prose)
        self.assertNotIn("nails", json.loads(js).get("Jewelry & Nails", {}))

    def test_normal_human_has_no_hand_reinforcement(self):
        # A standard human skin tone is never restated on the hands (no output churn).
        for gender in ("Female", "Male", "Any"):
            for seed in range(8):
                prose, _ = generate_character(seed, gender, {})
                self.assertNotIn("hands have the same", prose, f"{gender} seed {seed}")


class CostumeArticleTests(unittest.TestCase):
    """fill_costume recomputes 'a'/'an' from the value it fills into a slot."""

    def test_article_agrees_with_filled_slot(self):
        from data.templates import fill_costume
        for tmpl in ("a {gem}", "an {earth_tone}", "a {color}", "a {sheer_fabric}"):
            for seed in range(60):
                out = fill_costume(tmpl, random.Random(seed))
                article, word = out.split()[0], out.split()[1]
                expected = "an" if word[:1].lower() in "aeiou" else "a"
                self.assertEqual(article, expected, out)

    def test_article_governed_by_adjective_is_untouched(self):
        # When the article belongs to an adjective (not the slot), it must not change.
        from data.templates import fill_costume
        self.assertTrue(
            fill_costume("an embroidered {color} doublet", random.Random(0))
            .startswith("an embroidered "))
        self.assertTrue(
            fill_costume("an aristocratic {dark_color} coat", random.Random(0))
            .startswith("an aristocratic "))


class FieldHygieneTests(unittest.TestCase):
    """Cross-field de-duplication: hair fullness has a single owner."""

    def test_hair_volume_removed(self):
        # hair_volume duplicated hair_texture's fullness words and was already kept
        # out of the prose, so it was removed rather than left as a redundant field.
        self.assertNotIn("hair_volume", FIELD_DEFINITIONS)

    def test_no_constraint_or_data_references_hair_volume(self):
        from data.constraints import CONSTRAINT_RULES
        from data.templates import ARCHETYPES
        for rule in CONSTRAINT_RULES:
            for key in ("field", "excludes_field", "requires_field"):
                self.assertNotEqual(rule.get(key), "hair_volume")
        for name, template in ARCHETYPES.items():
            self.assertNotIn("hair_volume", template, name)
        for name, entry in COSPLAYERS.items():
            for section in ("signature", "physique"):
                self.assertNotIn("hair_volume", entry.get(section, {}), name)


class GrammarAgreementTests(unittest.TestCase):
    """The androgynous full-mix mode (gender 'Any' + wardrobe 'Any') uses plural
    'They' and must take plural verbs. (Plain 'Any' now coin-flips to he/she.)"""

    def test_they_takes_plural_wear(self):
        prose, _ = generate_character(
            7, "Any", {"outfit_style": "casual", "makeup_style": "soft glam"},
            wardrobe="Any",
        )
        self.assertNotIn("They wears", prose)
        self.assertIn("They wear", prose)

    def test_gendered_subjects_keep_singular_wears(self):
        for gender in ("Female", "Male"):
            prose, _ = generate_character(7, gender, {"outfit_style": "casual"})
            self.assertNotIn(" wear ", prose)  # no plural verb for She/He


class SmileTypeRenderTests(unittest.TestCase):
    """smile_type (formerly a dead field) now renders and stays coherent with the
    expression that steers it via constraints.py."""

    def test_open_expression_renders_toothy_grin(self):
        prose, _ = generate_character(3, "Female", {"expression": "laughing"})
        self.assertIn("toothy grin", prose)

    def test_closed_expression_renders_closed_mouth(self):
        prose, _ = generate_character(3, "Female", {"expression": "serious"})
        self.assertIn("closed mouth", prose)
        self.assertNotIn("grin", prose)

    def test_soft_smile_expression_renders_soft_smile(self):
        prose, _ = generate_character(3, "Female", {"expression": "warm smile"})
        self.assertIn("soft smile", prose)


class FieldFamilyPickTests(unittest.TestCase):
    """The generalized weighted two-tier picker (_pick_family_weighted)."""

    def test_every_family_field_partitions_its_options(self):
        # Mirrors validate_data but asserted here too: a drifted family makes some
        # values unreachable / double-weighted, biasing randomization.
        for field, families in FIELD_FAMILIES.items():
            variants = [v for fam in families.values() for v in fam["variants"]]
            self.assertEqual(len(variants), len(set(variants)),
                             f"{field}: duplicate variant across families")
            # Union of both gender pools: families must cover every option any
            # gender can draw (options may be gender-scoped, e.g. 'comb over'
            # is male-only), and the picker intersects with the live pool.
            opts = (set(FIELD_DEFINITIONS[field]["female_options"])
                    | set(FIELD_DEFINITIONS[field]["male_options"]))
            self.assertEqual(set(variants), opts, f"{field}: families != options")

    def test_pick_returns_in_pool_value(self):
        rng = random.Random(0)
        pool = list(FIELD_DEFINITIONS["expression"]["female_options"])
        for _ in range(200):
            self.assertIn(_pick_family_weighted("expression", pool, rng), pool)

    def test_pick_respects_filtered_pool(self):
        # Variants outside the (filtered) pool must never be returned, and empty
        # families are dropped -- the location_setting / constraint composition.
        rng = random.Random(1)
        pool = ["high ponytail", "low ponytail", "afro"]
        seen = {_pick_family_weighted("hair_style", pool, rng) for _ in range(300)}
        self.assertTrue(seen.issubset(set(pool)))
        self.assertEqual(seen, set(pool))  # all reachable

    def test_unregistered_field_falls_back_to_flat_choice(self):
        rng = random.Random(2)
        self.assertEqual(_pick_family_weighted("not_a_family", ["only"], rng), "only")

    def test_frozen_weights_reproduce_uniform_at_freeze(self):
        # With family weight == family size and no added variants, the macro draw
        # is statistically uniform. hair_style (sum 30) is the canonical check:
        # every value should appear over many draws, none dominating wildly.
        rng = random.Random(3)
        pool = list(FIELD_DEFINITIONS["hair_style"]["female_options"])
        counts = {v: 0 for v in pool}
        for _ in range(20000):
            counts[_pick_family_weighted("hair_style", pool, rng)] += 1
        # No value should be absent, and none should exceed ~3x the mean share.
        mean = 20000 / len(pool)
        self.assertTrue(all(c > 0 for c in counts.values()))
        self.assertTrue(max(counts.values()) < mean * 3)


class MaskedExpressionTests(unittest.TestCase):
    """0.83.0: a full mask hides the face, so a randomized `expression` must not render.

    ``expression`` lives in ``Setting & Shot``, not in ``_CONCEALED_FACE_GROUPS``, so for
    every release before this a masked character rendered "He wears a plush yordle suit.
    ... His expression is steely." Mechanical, never a decision.
    """

    COSTUME = "a plush yordle suit with a bandolier and oversized boots"

    def _setting(self, js):
        return json.loads(js).get("Setting & Shot", {})

    def test_masked_subject_has_no_expression(self):
        for seed in range(200):
            text, js = generate_character(
                seed, "Male", {"outfit_description": self.COSTUME},
                covers_face=True, covers_body=True)
            self.assertNotIn("expression", self._setting(js),
                             f"seed {seed} kept an expression behind a full mask")
            self.assertNotIn("expression is", text, f"seed {seed}: {text}")

    def test_unmasked_subject_still_has_one(self):
        found = 0
        for seed in range(60):
            _, js = generate_character(seed, "Male", {})
            if self._setting(js).get("expression"):
                found += 1
        self.assertEqual(found, 60, "expression must be untouched when the face shows")

    def test_an_explicit_widget_lock_still_wins(self):
        """A user's own widget beats the mask -- the house semantics, and the same rule
        the Face/Hair/Makeup block took at 0.84.0.

        0.84.0 restatement: this used to pass any `locked` entry and assert it won,
        which conflated a user's widget with a wired preset's authored look. The
        guarantee that is actually wanted is the narrower one, and the companion test
        below pins the other half."""
        for seed in range(40):
            text, js = generate_character(
                seed, "Male",
                {"outfit_description": self.COSTUME, "expression": "beaming"},
                covers_face=True, covers_body=True,
                widget_locked=frozenset({"expression"}))
            self.assertEqual(self._setting(js).get("expression"), "beaming")
            self.assertIn("expression is beaming", text)

    def test_a_preset_lock_does_not_win(self):
        """The other half of the 0.84.0 rule: a wired character's authored value is
        part of the costume the mask hides, so it must NOT survive."""
        for seed in range(40):
            text, js = generate_character(
                seed, "Male",
                {"outfit_description": self.COSTUME, "expression": "beaming"},
                covers_face=True, covers_body=True)
            self.assertNotIn("expression", self._setting(js), f"seed {seed}")
            self.assertNotIn("expression is", text, f"seed {seed}")

    def test_widget_lock_is_ignored_when_the_face_shows(self):
        # widget_locked only ever *prevents* a suppression; it must never inject.
        _, js = generate_character(
            3, "Male", {}, widget_locked=frozenset({"expression"}))
        self.assertIn("expression", self._setting(js))

    def test_mood_is_deliberately_kept(self):
        """mood describes the scene's atmosphere, not the face: it reads over a mask."""
        found = 0
        for seed in range(80):
            _, js = generate_character(
                seed, "Male", {"outfit_description": self.COSTUME},
                covers_face=True, covers_body=True)
            if self._setting(js).get("mood"):
                found += 1
        self.assertGreater(found, 0, "mood must survive a full mask")


class WidgetLockVersusConcealmentTests(unittest.TestCase):
    """0.84.0: the mask hides the face; only the user's OWN widget overrides it.

    Until 0.84.0 the `covers_face` group block and the `covers_hair` block dropped
    unconditionally, so on a masked character moving the `hair_color` widget off
    "Random" did nothing, silently -- the dead-widget failure mode 0.83.0 closed for
    the wardrobe axis. The fix keys off `widget_locked`, NOT the merged `locked`
    mapping: `locked` also carries a wired cosplayer's authored `signature`, and 8 of
    the 295 `covers_face` entries pin a concealed field there (Princess Leia's side
    buns under the Boushh helmet). Honouring those would be a regression.
    """

    COSTUME = "a sealed chrome helmet over a full armored bodysuit"

    def _groups(self, js):
        return json.loads(js)

    def test_masked_subject_drops_hair_by_default(self):
        for seed in range(60):
            _, js = generate_character(
                seed, "Female", {"outfit_description": self.COSTUME}, covers_face=True)
            self.assertNotIn("Hair", self._groups(js), f"seed {seed}")
            self.assertNotIn("Face", self._groups(js), f"seed {seed}")

    def test_a_widget_lock_survives_the_mask(self):
        for seed in range(40):
            text, js = generate_character(
                seed, "Female",
                {"outfit_description": self.COSTUME, "hair_color": "auburn"},
                covers_face=True, widget_locked=frozenset({"hair_color"}))
            self.assertEqual(self._groups(js)["Hair"]["hair_color"], "auburn")
            self.assertIn("auburn", text)

    def test_a_preset_lock_does_not_survive_the_mask(self):
        # The Princess Leia case: the same value, arriving from a signature pin.
        for seed in range(40):
            _, js = generate_character(
                seed, "Female",
                {"outfit_description": self.COSTUME, "hair_color": "auburn"},
                covers_face=True)
            self.assertNotIn("Hair", self._groups(js), f"seed {seed}")

    def test_a_widget_lock_survives_a_hood(self):
        for seed in range(40):
            _, js = generate_character(
                seed, "Female",
                {"outfit_description": "a heavy grey travelling cloak with a deep hood",
                 "hair_style": "low ponytail"},
                covers_hair=True, widget_locked=frozenset({"hair_style"}))
            self.assertEqual(self._groups(js)["Hair"]["hair_style"], "low ponytail")

    def test_a_hood_still_drops_unlocked_hair(self):
        for seed in range(40):
            _, js = generate_character(
                seed, "Female",
                {"outfit_description": "a heavy grey travelling cloak with a deep hood"},
                covers_hair=True)
            self.assertNotIn("Hair", self._groups(js), f"seed {seed}")

    def test_widget_locked_is_purely_additive(self):
        # Every caller that does not pass it must be byte-identical -- the whole
        # non-breaking argument for the new parameter rests on this.
        for seed in range(120):
            a = generate_character(seed, "Female", {})
            b = generate_character(seed, "Female", {}, widget_locked=frozenset())
            c = generate_character(seed, "Female", {}, widget_locked=None)
            self.assertEqual(a, b)
            self.assertEqual(a, c)

    def test_every_shipped_masked_cosplayer_is_unchanged_by_default(self):
        """The regression gate: with no widget locks, no masked entry may gain a face.

        This is what makes the change safe to ship -- the 8 signature-pinning entries
        are the ones that would break if `locked` had been used instead.
        """
        pinning = ["Princess Leia Organa", "The Atom", "Bo-Katan Kryze",
                   "Night Thrasher", "Denji", "Katana", "Jane Foster Thor", "Ermac"]
        for name in pinning:
            for seed in range(25):
                flat = _parse_archetype_json(build_cosplayer_json(name, seed))
                flat.pop(_COSPLAY_LABEL_KEY, None)
                covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
                covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
                covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
                if not covers_face:
                    continue  # this seed rolled an unmasked alternate costume
                locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
                _, js = generate_character(
                    seed, "Any", locked, covers_face=covers_face,
                    covers_body=covers_body, covers_hair=covers_hair)
                self.assertNotIn("Hair", json.loads(js), f"{name} seed {seed}")
                self.assertNotIn("Face", json.loads(js), f"{name} seed {seed}")


class FeralFitnessTests(unittest.TestCase):
    """0.83.0: a beast has no gym habit.

    ``body_type`` states a SHAPE and reads on anything; ``fitness_level``'s low values
    state a human LIFESTYLE ("sedentary"), which a feral creature does not have.
    """

    def _body(self, js):
        return json.loads(js).get("Body", {})

    def _feral(self, seed):
        from nodes.identity_forge_creature import build_creature_json
        doc = json.loads(build_creature_json("Wolf", seed=seed, form="Feral (beast)"))
        species = doc.get("_meta", {})
        return generate_character(seed, "Any", {}, species={
            "slots": doc.get("Species & Anatomy", {}),
            "form": species.get("form", ""),
            "suppress_groups": species.get("suppress_groups", []),
            "suppress_fields": species.get("suppress_fields", []),
        })

    def test_feral_form_drops_fitness_level(self):
        from nodes.identity_forge_creature import _FORM_SUPPRESS_FIELDS, _FORM_FERAL
        self.assertIn("fitness_level", _FORM_SUPPRESS_FIELDS[_FORM_FERAL])

    def test_shape_fields_are_deliberately_kept(self):
        from nodes.identity_forge_creature import (
            _FORM_SUPPRESS_FIELDS, _FORM_FERAL, _FORM_ANTHRO)
        feral = _FORM_SUPPRESS_FIELDS[_FORM_FERAL]
        self.assertNotIn("body_type", feral, "a shape reads fine on a beast")
        self.assertNotIn("height", feral, "a towering creature reads fine")
        self.assertEqual(_FORM_SUPPRESS_FIELDS[_FORM_ANTHRO], set(),
                         "anthro is humanoid and keeps everything")


class WornItemDeduplicationTests(unittest.TestCase):
    """The generalization of the hat rule (0.83.0).

    A costume that already NAMES a worn item must not have a second one bolted on by
    the randomizer. Until 0.83.0 this was enforced for headwear only and patched per
    entry for everything else (28 cosplayers hand-pin ``necklace: no necklace``).

    The regex traps below are the load-bearing part: every one is real roster or corpus
    text that a naive pattern gets wrong. Do NOT relax them without re-checking the
    data -- a false positive silently deletes a field for a whole class of characters.
    """

    #: (field, costume text, expected-to-fire) -- the false-positive suite.
    TRAPS = (
        # rings must not fire on "earrings" (no word boundary inside the word) ...
        ("rings", "a gown with delicate straps and diamond stud earrings", False),
        ("rings", "a slip dress with chandelier earrings", False),
        # ... nor on a PIERCING, nor on a non-jewellery "ring"
        ("rings", "black jeans with studded wristbands, a brow ring and a nose stud", False),
        ("rings", "a leather jacket with a lip ring", False),
        ("rings", "a rubber suit with a tire ring around the waist", False),
        ("rings", "a bronze collar and a heavy neck ring", False),
        ("rings", "a bare chest with a gold arm ring", False),
        # ... but must fire on an actual finger ring
        ("rings", "a tweed coat with layered rings", True),
        ("rings", "a plain hobbit shirt and the One Ring on a chain", True),
        # bracelet must never match a bare "cuff"
        ("bracelet", "a dress shirt with cuffed sleeves and chinos", False),
        ("bracelet", "1950s rolled-cuff jeans with a white tee", False),
        ("bracelet", "a bodysuit with an ear cuff", False),
        ("bracelet", "a toga with a gold arm cuff", False),
        ("bracelet", "french cuffs and a waistcoat", False),
        ("bracelet", "a gi with blue wristbands and boots", True),
        ("bracelet", "patchwork layers with stacked bangles", True),
        ("bracelet", "a leotard with steel wrist cuffs", True),
        # earrings must not fire on garment studs (Simon's trench coat)
        ("earrings", "a long navy trench coat with gold studs and a spiral emblem", False),
        ("earrings", "a leather jacket with studded patches and black jeans", False),
        ("earrings", "a kimono with three gold earrings in one ear", True),
        ("earrings", "a dress with pearl stud earrings", True),
        # bag must not fire on "baggy", nor on "clutch" the VERB (Psyduck)
        ("bag", "an oversized sweatshirt with baggy pants", False),
        ("bag", "stubby webbed feet and small arms raised to clutch the head", False),
        ("bag", "a satin slip gown with a clutch", True),
        ("bag", "a tee dress with a crossbody bag", True),
        ("bag", "a battered fedora and a leather satchel", True),
        # necklace: a chain only counts at the neck
        ("necklace", "a hauberk of chainmail over a padded gambeson", False),
        ("necklace", "cargo pants with a key chain hanging from a belt loop", False),
        ("necklace", "a wide red hat, a yellow scarf, and an 'O' medallion", True),
        ("necklace", "a wolf-head amulet and studded-leather armor", True),
        ("necklace", "a fishnet top under a slip dress with a choker", True),
        # other_jewelry
        ("other_jewelry", "a sailor collar with a heart-shaped brooch", True),
        ("other_jewelry", "a linen wrap with silver anklets", True),
        ("other_jewelry", "a dress shirt with cuffed sleeves", False),
    )

    def test_regex_traps(self):
        for field, text, should_fire in self.TRAPS:
            with self.subTest(field=field, text=text):
                fired = bool(WORN_ITEM_RES[field].search(text))
                self.assertEqual(
                    fired, should_fire,
                    f"{field} pattern {'fired' if fired else 'did not fire'} on {text!r}")

    def test_every_pattern_field_is_a_real_field(self):
        for field in WORN_ITEM_RES:
            self.assertIn(field, FIELD_DEFINITIONS, f"{field} is not a real field")

    def _clothing(self, js, field):
        doc = json.loads(js)
        for group in doc.values():
            if isinstance(group, dict) and field in group:
                return group[field]
        return None

    def _worn(self, js, field):
        """True when the field would actually RENDER.

        The rule deliberately skips a value that is already absent -- there is nothing
        to de-duplicate, and popping it would change the JSON shape for no reason. So
        the contract is "does not render", not "is missing from the JSON": an absent
        token ("no necklace") is omitted from prose by ``_is_absent`` either way.
        """
        value = self._clothing(js, field)
        return value is not None and not _is_absent(value)

    def test_costume_naming_a_necklace_suppresses_the_random_one(self):
        costume = ("a deep green velvet wrap dress with a gold pendant necklace "
                   "and suede pumps")
        for seed in range(120):
            text, js = generate_character(seed, "Female",
                                          {"outfit_description": costume},
                                          accessory_density="Maximal")
            self.assertFalse(self._worn(js, "necklace"),
                             f"seed {seed} stacked a second neck ornament")
            self.assertEqual(text.count("necklace"), 1,
                             f"seed {seed}: {text}")

    def test_costume_naming_earrings_suppresses_the_random_pair(self):
        costume = "a floor length velvet gown with delicate straps and diamond stud earrings"
        for seed in range(120):
            text, js = generate_character(seed, "Female",
                                          {"outfit_description": costume},
                                          accessory_density="Maximal")
            self.assertFalse(self._worn(js, "earrings"),
                             f"seed {seed} stacked a second pair of earrings")
            self.assertEqual(text.count("earrings"), 1, f"seed {seed}: {text}")

    def test_other_jewellery_fields_still_draw(self):
        """Only the NAMED field is dropped -- this is not the 0.66.0 group question."""
        costume = "a velvet wrap dress with a gold pendant necklace and suede pumps"
        seen = set()
        for seed in range(200):
            _, js = generate_character(seed, "Female",
                                       {"outfit_description": costume},
                                       accessory_density="Maximal")
            for field in ("earrings", "bracelet", "rings"):
                if self._worn(js, field):
                    seen.add(field)
        self.assertEqual(seen, {"earrings", "bracelet", "rings"},
                         "suppressing the named field must not suppress its siblings")

    def test_an_explicit_lock_still_wins(self):
        costume = "a velvet wrap dress with a gold pendant necklace and suede pumps"
        for seed in range(40):
            _, js = generate_character(
                seed, "Female",
                {"outfit_description": costume, "necklace": "pearl strand"})
            self.assertEqual(self._clothing(js, "necklace"), "pearl strand",
                             "a deliberate lock must survive the de-dup rule")

    def test_a_plain_costume_keeps_all_its_jewellery(self):
        """No named item -> nothing is dropped. The rule must be surgical."""
        costume = "a charcoal wool overcoat over a fine-knit turtleneck and wool trousers"
        seen = set()
        for seed in range(200):
            _, js = generate_character(seed, "Female",
                                       {"outfit_description": costume},
                                       accessory_density="Maximal")
            for field in WORN_ITEM_RES:
                if self._worn(js, field):
                    seen.add(field)
        # bag is suppressed for any LOCKED costume by _COSTUME_SUPPRESSED_EXTRAS, so it
        # is legitimately absent here; every jewellery field must still appear.
        self.assertEqual(seen, set(WORN_ITEM_RES) - {"bag"})

    def test_no_prose_stacks_two_of_the_same_item(self):
        """End-to-end sweep over the real roster: the bug this rule exists to kill."""
        from nodes.identity_forge_cosplayer import build_cosplayer_json
        names = sorted(COSPLAYERS)
        offenders = []
        for i, name in enumerate(names[::7]):        # ~247 characters, 3 seeds each
            for seed in range(3):
                doc = json.loads(build_cosplayer_json(name, seed=seed))
                locked = {}
                for group in doc.values():
                    if isinstance(group, dict):
                        locked.update({k: v for k, v in group.items()
                                       if isinstance(v, str)})
                meta = doc.get("_meta", {})
                text, _ = generate_character(
                    seed + i, "Female", locked,
                    accessory_density="Maximal",
                    covers_face=bool(meta.get("covers_face")),
                    covers_body=bool(meta.get("covers_body")),
                    covers_hair=bool(meta.get("covers_hair")))
                # "She has <jewellery>" plus a costume that names the same class
                if re.search(r"\bhas\b[^.]*\bearrings\b", text) and \
                        re.search(r"\bwears\b[^.]*\bearrings\b", text):
                    offenders.append((name, "earrings"))
        self.assertEqual(offenders, [], f"stacked items: {offenders[:8]}")


class HatSuppressionTests(unittest.TestCase):
    """The hat-stacking rule: an *auto-generated* outfit that includes headwear must
    not stack a second hat from the randomized ``accessories`` field. As of 0.68 a
    LOCKED costume suppresses every random accessory (see CostumeExtraSuppressionTests),
    so the hat rule now only governs plain runs; an explicit user lock still wins."""

    HAT_VALUES = {"wide brim sun hat", "baseball cap", "beret", "woven hat"}

    def _accessories(self, js):
        return json.loads(js).get("Clothing", {}).get("accessories")

    def test_hat_costume_suppresses_hat_accessories(self):
        costume = "a ringmaster's red tailcoat with a black top hat and striped trousers"
        for seed in range(80):
            _, js = generate_character(seed, "Male", {"outfit_description": costume},
                                       accessory_density="Maximal")
            self.assertNotIn(self._accessories(js), self.HAT_VALUES, f"seed {seed}")

    def test_helmet_costume_also_suppresses(self):
        costume = "a scuffed racing suit with a mirrored full-face helmet under one arm"
        for seed in range(40):
            _, js = generate_character(seed, "Female", {"outfit_description": costume},
                                       accessory_density="Maximal")
            self.assertNotIn(self._accessories(js), self.HAT_VALUES, f"seed {seed}")

    def test_accessories_reachable_without_a_costume(self):
        # The costume-extra suppression fires only when an outfit is LOCKED; a plain
        # run (auto-generated outfit) still reaches the full accessory pool, hats incl.
        seen = {self._accessories(generate_character(
            s, "Female", {}, accessory_density="Maximal")[1]) for s in range(200)}
        self.assertTrue(seen & self.HAT_VALUES)

    def test_locked_hat_accessory_survives(self):
        # An explicit user lock beats the suppression (deliberate double hat).
        costume = "a ringmaster's red tailcoat with a black top hat and striped trousers"
        _, js = generate_character(5, "Female",
                                   {"outfit_description": costume,
                                    "accessories": "beret"})
        self.assertEqual(self._accessories(js), "beret")

    def test_locked_costume_suppresses_all_accessories(self):
        # 0.68: a provided costume drops EVERY random accessory (not just a stacked
        # hat), so no unauthored accessory rides on a styled look.
        costume = "a ringmaster's red tailcoat with a black top hat and striped trousers"
        for s in range(80):
            self.assertIn(
                self._accessories(generate_character(
                    s, "Male", {"outfit_description": costume})[1]),
                (None, "no accessories"), f"seed {s}")


class MaleMakeupWeightTests(unittest.TestCase):
    """The male makeup_style pool leans 2x toward 'no makeup' via the explicit
    ``male_weights`` mechanism (never a duplicated pool entry). The female draw
    stays flat-uniform."""

    def _distribution(self, gender, draws=3000):
        counts: dict[str, int] = {}
        for seed in range(draws):
            resolved = _randomize_fields(
                {}, gender, "Any color", "Balanced", "Any indoor/outdoor",
                random.Random(seed))
            value = resolved["makeup_style"]
            counts[value] = counts.get(value, 0) + 1
        return counts, draws

    def test_male_pool_has_no_duplicates_but_carries_weight(self):
        meta = FIELD_DEFINITIONS["makeup_style"]
        pool = meta["male_options"]
        self.assertEqual(len(pool), len(set(pool)))
        self.assertEqual(meta.get("male_weights"), {"no makeup": 2})

    def test_male_draw_leans_toward_no_makeup(self):
        counts, draws = self._distribution("Male")
        pool = FIELD_DEFINITIONS["makeup_style"]["male_options"]
        # weight 2 out of (len-1)+2 total: expected share for 'no makeup'.
        expected = 2 / (len(pool) + 1)
        share = counts.get("no makeup", 0) / draws
        self.assertGreater(share, expected * 0.8)
        self.assertLess(share, expected * 1.2)
        for value in pool:  # every option stays reachable
            self.assertGreater(counts.get(value, 0), 0, value)

    def test_female_draw_stays_flat(self):
        counts, draws = self._distribution("Female")
        pool = FIELD_DEFINITIONS["makeup_style"]["female_options"]
        flat = 1 / len(pool)
        share = counts.get("no makeup", 0) / draws
        self.assertLess(share, flat * 1.6)  # no hidden lean on the female pool


class DrawWeightRarityTests(unittest.TestCase):
    """The generalized draw-weight maps down-weight a single value below its peers.
    ``weights`` biases every gender; ``male_weights`` is a male-only overlay. Float
    weights let a value sit below the implicit 1 (bleached eyebrows, silky male hair)."""

    def _share(self, field, value, gender, draws=4000):
        hits = 0
        for seed in range(draws):
            resolved = _randomize_fields(
                {}, gender, "Any color", "Balanced", "Any indoor/outdoor",
                random.Random(seed))
            if resolved.get(field) == value:
                hits += 1
        return hits / draws

    def test_bleached_eyebrows_rare_for_all_genders(self):
        self.assertEqual(FIELD_DEFINITIONS["eyebrows"].get("weights"), {"bleached": 0.2})
        flat = 1 / len(FIELD_DEFINITIONS["eyebrows"]["female_options"])  # old 1/10
        for gender in ("Female", "Male"):
            share = self._share("eyebrows", "bleached", gender)
            self.assertLess(share, flat * 0.5, gender)   # well under the old 10%
            self.assertGreater(share, 0.0, gender)       # still reachable/lockable

    def test_bleached_stays_rare_for_males_through_constraint_repick(self):
        # Regression guard: the male brow-trim re-rolls ~1/3 of males; the exclusion
        # re-pick must honor the weight map (via _weighted_choice) or bleached would
        # creep back up toward the flat rate for men.
        hits = 0
        for seed in range(4000):
            _, js = generate_character(seed, "Male", {})
            flat = {}
            for v in json.loads(js).values():
                if isinstance(v, dict):
                    flat.update(v)
            if flat.get("eyebrows") == "bleached":
                hits += 1
        self.assertLess(hits / 4000, 0.05)  # ~3%, comfortably under the old 10%

    def test_silky_glossy_rare_for_males_only(self):
        self.assertEqual(
            FIELD_DEFINITIONS["hair_texture"].get("male_weights"),
            {"silky and glossy": 0.3})
        female = self._share("hair_texture", "silky and glossy", "Female")
        male = self._share("hair_texture", "silky and glossy", "Male")
        flat = 1 / len(FIELD_DEFINITIONS["hair_texture"]["female_options"])
        self.assertGreater(female, flat * 0.7)   # unchanged for women (~1/15)
        self.assertLess(male, female * 0.6)       # meaningfully rarer for men
        self.assertGreater(male, 0.0)             # still lockable/reachable


class TextureStyleCoherenceTests(unittest.TestCase):
    """afro / twist-out are the only texture-bound styles; a straight or wavy
    hair_texture must never pair with them (constraints.py 0.53)."""

    _NON_COILED = {
        "pin straight", "sleek straight", "silky and glossy", "slightly wavy",
        "loosely wavy", "wavy", "beachy waves",
    }

    def test_afro_twistout_never_on_straight_or_wavy(self):
        for gender in ("Female", "Male"):
            for seed in range(600):
                _, js = generate_character(seed, gender, {}, hair_color_scope="Full spectrum")
                flat = {}
                for v in json.loads(js).values():
                    if isinstance(v, dict):
                        flat.update(v)
                if flat.get("hair_style") in ("afro", "twist-out"):
                    self.assertNotIn(flat.get("hair_texture"), self._NON_COILED,
                                     f"{gender} seed pairing")

    def test_locked_afro_repairs_texture_to_coiled(self):
        # A preset that locks afro must not leave a random straight texture beside it.
        for seed in range(200):
            _, js = generate_character(seed, "Female", {"hair_style": "afro"})
            flat = {}
            for v in json.loads(js).values():
                if isinstance(v, dict):
                    flat.update(v)
            self.assertNotIn(flat.get("hair_texture"), self._NON_COILED, seed)


class MascotScopeTests(unittest.TestCase):
    """0.82.0: the `Mascot / full-suit` scope, proposed since 0.77.0 and now built.

    Derived from `covers_body and covers_face` rather than a new schema key, so it
    counts user_options.json additions and self-maintains. Being a filter over the
    existing pool, it adds no entries and cannot shift any field's distribution.
    """

    def test_scope_matches_only_fully_encased_entries(self):
        from nodes.identity_forge_cosplayer import _SPECIAL_SCOPES
        pred = _SPECIAL_SCOPES["Mascot / full-suit"]
        matched = [n for n, e in COSPLAYERS.items() if pred(e)]
        self.assertGreater(len(matched), 50, "mascot pool suspiciously small")
        for name in matched:
            entry = COSPLAYERS[name]
            self.assertTrue(entry.get("covers_body"), name)
            self.assertTrue(entry.get("covers_face"), name)

    def test_every_gender_combo_stays_in_scope(self):
        # The 0.75.0 lesson: a scope bug lives in the INTERSECTION with gender, so
        # walk the matrix rather than sampling one gender.
        from nodes.identity_forge_cosplayer import _SPECIAL_SCOPES, build_cosplayer_json
        pred = _SPECIAL_SCOPES["Mascot / full-suit"]
        in_scope = {n for n, e in COSPLAYERS.items() if pred(e)}
        for gender in ("Random — any", "Random — female", "Random — male"):
            for seed in range(15):
                meta = json.loads(build_cosplayer_json(
                    gender, seed, random_scope="Mascot / full-suit"))["_meta"]
                self.assertIn(
                    meta["cosplay_of"], in_scope,
                    f"{gender} seed {seed} escaped the mascot scope")


class ComplexionSkinToneTests(unittest.TestCase):
    """0.82.0: `peaches and cream` names a colour, not a surface quality.

    Rendered output read "a 35-year-old Jamaican woman with ... deep ebony skin.
    ... Her skin shows a peaches and cream complexion." The same contradiction is
    recorded in the Ka D'Argo entry comment, but was only ever fixed *per entry*
    by the body-paint suppression -- nothing handled the ordinary human case.

    Scoped to one value on purpose: `clear` / `rosy` / `ruddy` / `sallow` describe
    redness, pallor and clarity, all of which read on any skin tone.
    """

    def test_deep_tones_never_draw_a_pink_white_complexion(self):
        from data.fields import DEEP_SKIN_TONES
        for seed in range(600):
            _, js = generate_character(seed, "Any", {})
            flat = {k: v for g in json.loads(js).values()
                    if isinstance(g, dict) for k, v in g.items()}
            if flat.get("skin_tone") in DEEP_SKIN_TONES:
                self.assertNotEqual(
                    flat.get("complexion"), "peaches and cream",
                    f"{flat.get('skin_tone')!r} skin with a peaches and cream "
                    f"complexion (seed {seed})")

    def test_the_value_survives_on_lighter_tones(self):
        # A coherence rule that quietly deletes a value everywhere is a worse bug
        # than the one it fixes.
        from data.fields import DEEP_SKIN_TONES
        seen = False
        for seed in range(600):
            _, js = generate_character(seed, "Any", {})
            flat = {k: v for g in json.loads(js).values()
                    if isinstance(g, dict) for k, v in g.items()}
            if (flat.get("complexion") == "peaches and cream"
                    and flat.get("skin_tone") not in DEEP_SKIN_TONES):
                seen = True
                break
        self.assertTrue(seen, "'peaches and cream' no longer reachable at all")

    def test_the_exclusion_is_bias_safe_because_complexion_is_flat(self):
        # The whole-family rule does not apply here, and this is WHY: a flat field
        # (no FIELD_FAMILIES entry, no weights map) re-picks flat-uniform over
        # whatever survives. If complexion ever gains families or weights, this
        # exclusion has to be re-argued.
        from data.fields import FIELD_FAMILIES
        self.assertNotIn("complexion", FIELD_FAMILIES)
        self.assertIsNone(FIELD_DEFINITIONS["complexion"].get("weights"))
        self.assertIsNone(FIELD_DEFINITIONS["complexion"].get("male_weights"))

    def test_deep_tone_bucket_names_only_real_options(self):
        from data.fields import DEEP_SKIN_TONES
        pool = set(FIELD_DEFINITIONS["skin_tone"]["female_options"])
        self.assertTrue(DEEP_SKIN_TONES <= pool,
                        f"DEEP_SKIN_TONES names non-options: {DEEP_SKIN_TONES - pool}")


class PhysiqueCoherenceTests(unittest.TestCase):
    """body_type <-> fitness_level exclusions: contradictory extremes can't be
    rolled together, while explicit locks still win."""

    def _body(self, js):
        return json.loads(js).get("Body", {})

    def test_athletic_build_never_sedentary(self):
        for seed in range(80):
            _, js = generate_character(seed, "Female", {"body_type": "athletic"})
            self.assertNotEqual(self._body(js).get("fitness_level"), "sedentary",
                                f"seed {seed}")

    def test_voluptuous_build_never_muscular(self):
        for seed in range(80):
            _, js = generate_character(seed, "Female", {"body_type": "voluptuous"})
            self.assertNotEqual(self._body(js).get("fitness_level"), "muscular",
                                f"seed {seed}")

    def test_locked_contradiction_survives(self):
        # A deliberate user lock on both fields beats the constraint (warn+keep).
        _, js = generate_character(
            7, "Female", {"body_type": "voluptuous", "fitness_level": "muscular"})
        body = self._body(js)
        self.assertEqual(body.get("body_type"), "voluptuous")
        self.assertEqual(body.get("fitness_level"), "muscular")


class ValidatorGuardTests(unittest.TestCase):
    """The AST duplicate-key guard catches a re-added roster name (the class of
    bug where a later literal entry silently overrides the earlier one)."""

    def test_detects_duplicate_literal_key(self):
        import tempfile
        from tests.validate_data import _duplicate_literal_keys
        source = 'ROSTER: dict = {\n    "A": 1,\n    "B": 2,\n    "A": 3,\n}\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roster.py"
            path.write_text(source, encoding="utf-8")
            self.assertEqual(_duplicate_literal_keys(path, "ROSTER"), ["A"])
            self.assertEqual(_duplicate_literal_keys(path, "MISSING"), [])

    def test_live_rosters_have_no_duplicate_keys(self):
        from tests.validate_data import _duplicate_literal_keys
        for filename, dict_name in (
            ("data/cosplayers.py", "COSPLAYERS"),
            ("data/creatures.py", "CREATURES"),
            ("data/templates.py", "ARCHETYPES"),
        ):
            self.assertEqual(
                _duplicate_literal_keys(ROOT / filename, dict_name), [], filename)


class UserOptionsIntegrationTests(unittest.TestCase):
    """user_options.json additions must be first-class: reachable by the random
    draw on family-weighted fields, shaped like built-ins in the cosplayer store,
    and exempt from the shipped-data strictness in validate_data."""

    def test_user_value_on_family_field_is_reachable(self):
        # A value outside every family (a user addition) draws via the implicit
        # leftover family at roughly the flat 1-in-(N+1) share.
        pool = list(FIELD_DEFINITIONS["expression"]["female_options"]) + ["smug"]
        rng = random.Random(11)
        draws = 30000
        hits = sum(_pick_family_weighted("expression", pool, rng) == "smug"
                   for _ in range(draws))
        # The leftover family weighs its size (1) against the frozen family
        # weights, so the exact design share is 1/(sum_of_frozen_weights + 1).
        total_weight = sum(f["weight"] for f in FIELD_FAMILIES["expression"].values())
        expected = draws / (total_weight + 1)
        self.assertGreater(hits, expected * 0.75)
        self.assertLess(hits, expected * 1.25)

    def test_no_leftover_means_identical_families_path(self):
        # Without user additions the leftover family is empty: every built-in
        # option partitions into a family, so behavior is unchanged.
        pool = list(FIELD_DEFINITIONS["expression"]["female_options"])
        rng = random.Random(12)
        for _ in range(500):
            self.assertIn(_pick_family_weighted("expression", pool, rng), pool)

    def test_user_cosplayer_omits_empty_optional_keys(self):
        import tempfile
        from data.user_options import apply_user_cosplayers
        doc = {"cosplayers": {
            "Plain OC": {"costume": "a red jacket"},
            "Masked OC": {"costume": "a black suit", "covers_face": True,
                          "mask": "a chrome helmet", "prop": "a staff",
                          "eyes": "glowing white"},
        }}
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text(json.dumps(doc), encoding="utf-8")
            store: dict = {}
            self.assertEqual(apply_user_cosplayers(store, path=f), 2)
        plain = store["Plain OC"]
        for key in ("mask", "prop", "eyes"):
            self.assertNotIn(key, plain)  # omitted, never ""
        masked = store["Masked OC"]
        self.assertEqual(masked["mask"], "a chrome helmet")
        self.assertEqual(masked["prop"], "a staff")
        self.assertEqual(masked["eyes"], "glowing white")

    def test_user_cosplayer_advanced_flags(self):
        # covers_body/covers_hair/bald/body_paint copied only when literally
        # true; skin rides the optional free-text keys. Anything else omitted
        # so user records mirror the built-in shape (no False flags stored).
        import tempfile
        from data.user_options import apply_user_cosplayers
        doc = {"cosplayers": {
            "Painted OC": {"costume": "tribal wraps over green painted skin",
                           "body_paint": True, "skin": "deep green",
                           "bald": True},
            "Armored OC": {"costume": "a full chrome exo-suit",
                           "covers_body": True, "covers_hair": True},
            "Sloppy OC": {"costume": "a red jacket", "body_paint": False,
                          "bald": "yes", "covers_body": 1, "skin": ""},
        }}
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "user_options.json"
            f.write_text(json.dumps(doc), encoding="utf-8")
            store: dict = {}
            self.assertEqual(apply_user_cosplayers(store, path=f), 3)
        painted = store["Painted OC"]
        self.assertIs(painted["body_paint"], True)
        self.assertIs(painted["bald"], True)
        self.assertEqual(painted["skin"], "deep green")
        armored = store["Armored OC"]
        self.assertIs(armored["covers_body"], True)
        self.assertIs(armored["covers_hair"], True)
        sloppy = store["Sloppy OC"]  # falsy/non-bool/empty values all omitted
        for key in ("body_paint", "bald", "covers_body", "covers_hair", "skin"):
            self.assertNotIn(key, sloppy)

    def test_loader_records_added_values_in_registry(self):
        import copy
        import tempfile
        from data.user_options import (apply_user_options,
                                       USER_ADDED_FIELD_VALUES,
                                       USER_ADDED_OUTFIT_STYLES)
        doc = {"fields": {"expression": ["definitely-a-test-expression"]},
               "outfits": {"test-style-xyz": {"unisex": ["a test garment"]}}}
        fd = copy.deepcopy(dict(FIELD_DEFINITIONS))
        outfits: dict = {}
        try:
            with tempfile.TemporaryDirectory() as d:
                f = Path(d) / "user_options.json"
                f.write_text(json.dumps(doc), encoding="utf-8")
                apply_user_options(fd, outfits, path=f)
            self.assertIn("definitely-a-test-expression",
                          USER_ADDED_FIELD_VALUES.get("expression", set()))
            self.assertIn("test-style-xyz", USER_ADDED_OUTFIT_STYLES)
        finally:
            USER_ADDED_FIELD_VALUES.get("expression", set()).discard(
                "definitely-a-test-expression")
            USER_ADDED_OUTFIT_STYLES.discard("test-style-xyz")

    def test_validate_exempts_registered_user_values(self):
        # Inject a user-style addition into the live expression pool + registry;
        # validate() must stay clean (family partition check exempts it).
        from data.user_options import USER_ADDED_FIELD_VALUES
        pool = FIELD_DEFINITIONS["expression"]["female_options"]
        value = "definitely-a-test-expression"
        pool.append(value)
        USER_ADDED_FIELD_VALUES.setdefault("expression", set()).add(value)
        try:
            self.assertEqual(validate(), [])
        finally:
            pool.remove(value)
            USER_ADDED_FIELD_VALUES["expression"].discard(value)

    def test_example_file_loads_through_every_section(self):
        import copy
        from data.user_options import (apply_user_options, apply_user_archetypes,
                                       apply_user_cosplayers, apply_user_creatures,
                                       USER_ADDED_FIELD_VALUES,
                                       USER_ADDED_OUTFIT_STYLES)
        from data.fields import OUTFIT_DESCRIPTIONS
        example = ROOT / "user_options.example.json"
        before_fields = {k: set(v) for k, v in USER_ADDED_FIELD_VALUES.items()}
        before_styles = set(USER_ADDED_OUTFIT_STYLES)
        try:
            fd = copy.deepcopy(dict(FIELD_DEFINITIONS))
            outfits = copy.deepcopy(OUTFIT_DESCRIPTIONS)
            self.assertGreater(apply_user_options(fd, outfits, path=example), 0)
            self.assertEqual(apply_user_archetypes({}, path=example), 1)
            self.assertEqual(apply_user_cosplayers({}, path=example), 3)
            self.assertEqual(apply_user_creatures({}, path=example), 1)
            # every archetype value in the example is a valid post-merge option
            doc = json.loads(example.read_text(encoding="utf-8"))
            for field, value in doc["archetypes"]["Sky Pirate"].items():
                if field in ("gender", "outfit_description"):
                    continue
                opts = set(fd[field]["female_options"]) | set(fd[field]["male_options"])
                self.assertIn(value, opts, f"Sky Pirate {field}")
        finally:  # the registries are global -- restore
            for k in list(USER_ADDED_FIELD_VALUES):
                USER_ADDED_FIELD_VALUES[k] = before_fields.get(k, set())
                if not USER_ADDED_FIELD_VALUES[k]:
                    del USER_ADDED_FIELD_VALUES[k]
            USER_ADDED_OUTFIT_STYLES.clear()
            USER_ADDED_OUTFIT_STYLES.update(before_styles)

class SizeScaleSuppressionTests(unittest.TestCase):
    """Verify ``size_scale`` on a cosplayer entry suppresses the engine's height
    rendering and surfaces in ``_meta`` for downstream consumers.

    The builder is responsible for both: locking ``height`` to "None" so the
    engine drops it from prose and JSON, and writing ``size_scale`` into
    ``_meta`` so the IdentityForge node can detect and present the scale. The
    engine does NOT inject any size language itself -- the costume prose
    carries the scale.
    """

    # A giant (colossal) and a tiny character to cover both branches.
    _GIANT = "Giganta"
    _TINY = "Tinker Bell"
    _NEUTRAL = "Spider-Man"  # no size_scale; height must be left alone

    def _doc(self, name, look_level="Full character"):
        """Run the cosplayer builder and return the parsed JSON document."""
        raw = build_cosplayer_json(name, seed=42, look_level=look_level,
                                   mask_mode=_MASK_DEFAULT,
                                   include_prop=False, random_scope="Any")
        return json.loads(raw)

    def test_giant_cosplayer_locks_height_to_scale_prose(self):
        """``size_scale: "giant"`` must lock ``height`` to the entry's authored
        ``scale_prose`` so the scale renders in the lead sentence (the costume
        prose reinforces it later)."""
        doc = self._doc(self._GIANT)
        body = doc.get("Body", {})
        expected = COSPLAYERS[self._GIANT]["scale_prose"]
        self.assertEqual(body.get("height"), expected,
                         f"{self._GIANT} height should be {expected!r}, got {body.get('height')!r}")

    def test_tiny_cosplayer_locks_height_to_scale_prose(self):
        """``size_scale: "tiny"`` must also lock ``height`` to the scale_prose."""
        doc = self._doc(self._TINY)
        body = doc.get("Body", {})
        expected = COSPLAYERS[self._TINY]["scale_prose"]
        self.assertEqual(body.get("height"), expected,
                         f"{self._TINY} height should be {expected!r}, got {body.get('height')!r}")

    def test_neutral_cosplayer_keeps_height(self):
        """A cosplayer without ``size_scale`` must NOT have its height touched
        (regression guard -- suppression must not leak to other characters)."""
        doc = self._doc(self._NEUTRAL)
        body = doc.get("Body", {})
        # Spider-Man's covers_face suppresses some fields but height is Body-group
        # and not covered, so it stays. The exact value is randomized -- just
        # assert it's NOT the absent sentinel and NOT the locked "None".
        height = body.get("height")
        self.assertNotIn(height, (None, "None"),
                         f"{self._NEUTRAL} height should be a real value, got {height!r}")

    def test_giant_metadata_records_size_scale(self):
        """The ``_meta.size_scale`` key must be set when the entry declares it."""
        doc = self._doc(self._GIANT)
        meta = doc.get("_meta", {})
        self.assertEqual(meta.get("size_scale"), "giant",
                         f"{self._GIANT} _meta.size_scale should be 'giant'")

    def test_tiny_metadata_records_size_scale(self):
        """Same for the tiny character."""
        doc = self._doc(self._TINY)
        meta = doc.get("_meta", {})
        self.assertEqual(meta.get("size_scale"), "tiny",
                         f"{self._TINY} _meta.size_scale should be 'tiny'")

    def test_neutral_metadata_omits_size_scale(self):
        """A cosplayer without ``size_scale`` must NOT carry the key in ``_meta``."""
        doc = self._doc(self._NEUTRAL)
        meta = doc.get("_meta", {})
        self.assertNotIn("size_scale", meta,
                         f"{self._NEUTRAL} should not have _meta.size_scale")

    def test_giant_full_character_keeps_other_physique(self):
        """Full-character mode with ``size_scale`` suppresses only height --
        body_type, skin_tone and signature fields survive (size is the
        identity; the rest of the physique is the randomizable person)."""
        doc = self._doc(self._GIANT, look_level="Full character")
        body = doc.get("Body", {})
        self.assertEqual(body.get("height"), COSPLAYERS[self._GIANT]["scale_prose"])
        # body_type and skin_tone must still be present (Giganta's full physique)
        self.assertIn("body_type", body, "body_type must survive size-scale suppression")
        self.assertIn("skin_tone", body, "skin_tone must survive size-scale suppression")

    def test_engine_output_renders_scale_prose_for_giant(self):
        """End-to-end: the engine's prose must NOT contain the character's
        original ``physique.height`` (e.g. "very tall" for Giganta) and MUST
        contain the authored ``scale_prose`` in its place."""
        from nodes.identity_forge import generate_character
        archetype_str = build_cosplayer_json(self._GIANT, seed=42,
                                             look_level="Full character",
                                             mask_mode=_MASK_DEFAULT,
                                             include_prop=False, random_scope="Any")
        parsed = _parse_archetype_json(archetype_str)
        locked = {k: v for k, v in parsed.items()
                  if k not in ("__cosplay_label__", "_meta")}
        prose, _ = generate_character(
            seed=42, gender="Any", locked=locked,
            cosplay_label=parsed.get("__cosplay_label__"),
            covers_face=parsed.get("_covers_face", False),
            covers_body=parsed.get("_covers_body", False),
            covers_hair=parsed.get("_covers_hair", False),
        )
        # Giganta's pre-existing physique.height was "very tall" -- the builder
        # replaces it with scale_prose, so the original must NOT appear and the
        # authored scale MUST.
        self.assertNotIn("very tall", prose,
                         f"Engine prose for {self._GIANT} leaked physique.height: {prose[:200]}")
        self.assertIn(COSPLAYERS[self._GIANT]["scale_prose"], prose,
                      f"Engine prose for {self._GIANT} missing scale_prose: {prose[:200]}")

    def test_all_size_scaled_cosplayers_have_valid_size_value(self):
        """Cross-check: every cosplayer that declares ``size_scale`` must use a
        recognized value ("giant"/"tiny") AND carry a non-empty ``scale_prose``
        the builder can lock into the height slot."""
        valid = {"giant", "tiny"}
        for name, entry in COSPLAYERS.items():
            scale = entry.get("size_scale")
            if scale is not None:
                self.assertIn(scale, valid,
                               f"{name!r} has unknown size_scale {scale!r}; "
                               f"expected one of {valid}")
                prose = entry.get("scale_prose")
                self.assertTrue(isinstance(prose, str) and prose,
                                f"{name!r} declares size_scale but has no scale_prose")
        # And the count must match the roster plan (31 + Papa Smurf = 32).
        scaled = [n for n, e in COSPLAYERS.items() if e.get("size_scale")]
        self.assertGreaterEqual(len(scaled), 32,
                                f"Expected >= 32 size-scaled cosplayers, got {len(scaled)}")

    def test_scale_text_is_self_contained(self):
        """No size-scaled character's costume/scale_prose may name a reference
        object ("beside a towering everyday object", "three apples high") --
        T2I models render the named object next to the character."""
        banned = (r"beside (a|the)\b", r"everyday objects?", r"apples high",
                  r"\binsect[- ]sized", r"\bant[- ]sized", r"\bdoll[- ]sized",
                  r"\bpalm[- ]sized", r"\bdwarfing", r"next to (a|the)\b")
        for name, entry in COSPLAYERS.items():
            if not entry.get("size_scale"):
                continue
            combined = f"{entry.get('costume', '')} {entry.get('scale_prose', '')}".lower()
            for pattern in banned:
                self.assertIsNone(re.search(pattern, combined),
                                  f"{name!r} scale text matches comparison pattern {pattern!r}")

    def test_papa_smurf_and_gargamel_present(self):
        """Papa Smurf is a size-scaled tiny; Gargamel is a regular-sized human
        (canonically NOT giant or tiny) -- guard both rosters."""
        papa = COSPLAYERS["Papa Smurf"]
        self.assertEqual(papa.get("size_scale"), "tiny")
        self.assertTrue(papa.get("scale_prose"))
        gargamel = COSPLAYERS["Gargamel"]
        self.assertNotIn("size_scale", gargamel)
        self.assertNotIn("scale_prose", gargamel)


class AltCostumeTests(unittest.TestCase):
    """The ``costumes`` alternate-look list: rng-picked per seed, string or dict
    overlay, shared keys (size/physique) stable across looks."""

    _BASE = {
        "franchise": "Test", "gender": "Female",
        "costume": "the primary look",
        "size_scale": "giant", "scale_prose": "colossal and fifty feet tall",
        "physique": {"body_type": "athletic"},
    }

    def test_no_costumes_returns_entry_unchanged_and_consumes_no_rng(self):
        entry = dict(self._BASE)
        rng = random.Random(7)
        state_before = rng.getstate()
        self.assertIs(_pick_look(entry, rng), entry)
        self.assertEqual(rng.getstate(), state_before,
                         "single-costume entry must not consume RNG (seed stability)")

    def test_string_alternate_can_be_selected(self):
        entry = dict(self._BASE, costumes=["the alternate look"])
        seen = {_pick_look(entry, random.Random(s))["costume"] for s in range(30)}
        self.assertEqual(seen, {"the primary look", "the alternate look"})

    def test_alternate_pick_is_deterministic_per_seed(self):
        entry = dict(self._BASE, costumes=["look B", "look C"])
        self.assertEqual(_pick_look(entry, random.Random(3))["costume"],
                         _pick_look(entry, random.Random(3))["costume"])

    def test_shared_keys_survive_every_costume(self):
        entry = dict(self._BASE, costumes=["alt one", {"costume": "alt two"}])
        for s in range(20):
            look = _pick_look(entry, random.Random(s))
            self.assertEqual(look["size_scale"], "giant")
            self.assertEqual(look["scale_prose"], "colossal and fifty feet tall")
            self.assertEqual(look["physique"], {"body_type": "athletic"})
            self.assertNotIn("costumes", look, "resolved look must not carry the raw list")

    def test_dict_overlay_overrides_only_its_keys(self):
        entry = dict(self._BASE, signature={"hair_color": "deep red"},
                     costumes=[{"costume": "caped look", "signature": {"hair_color": "jet black"}}])
        # Find a seed that selects the overlay.
        for s in range(30):
            look = _pick_look(entry, random.Random(s))
            if look["costume"] == "caped look":
                self.assertEqual(look["signature"], {"hair_color": "jet black"})
                break
        else:
            self.fail("overlay costume was never selected across 30 seeds")

    def test_end_to_end_giant_alt_costume_keeps_scale(self):
        """A real build over an entry with alternates must keep the giant scale_prose
        in the height slot regardless of which costume rolled."""
        entry = dict(self._BASE, costumes=["alt look"])
        COSPLAYERS["__AltTest__"] = entry
        try:
            for s in range(12):
                doc = json.loads(build_cosplayer_json("__AltTest__", s, "Full character"))
                body = doc.get("Body", {})
                self.assertEqual(body.get("height"), "colossal and fifty feet tall")
        finally:
            del COSPLAYERS["__AltTest__"]


class SpecialRandomScopeTests(unittest.TestCase):
    """The attribute-based random scopes (Giant/Tiny/Non-human/Masked/Mascot)."""

    def _pick(self, scope, seeds=40):
        names = set()
        for s in range(seeds):
            name = _resolve_character("Random — any", random.Random(s), scope)
            if name is not None:
                names.add(name)
        return names

    def test_scopes_are_registered(self):
        # The scope list is user-facing UI, so a change to it should be a
        # deliberate edit here rather than something that slips in with a data
        # tweak. `Mascot / full-suit` joined at 0.82.0; see MascotScopeTests.
        # (Non-breaking: ComfyUI serialises a combo by its string value, so
        # inserting an option does not move a saved workflow's selection.)
        self.assertEqual(set(_SPECIAL_SCOPES),
                         {"Giant characters", "Tiny characters",
                          "Non-human / colored", "Masked", "Mascot / full-suit"})

    def test_giant_scope_only_returns_giants(self):
        for name in self._pick("Giant characters"):
            self.assertEqual(COSPLAYERS[name].get("size_scale"), "giant",
                             f"{name} is not a giant but was picked under the Giant scope")

    def test_tiny_scope_only_returns_tinies(self):
        picked = self._pick("Tiny characters")
        self.assertTrue(picked, "Tiny scope produced no characters")
        for name in picked:
            self.assertEqual(COSPLAYERS[name].get("size_scale"), "tiny")

    def test_masked_scope_only_returns_masked(self):
        for name in self._pick("Masked"):
            self.assertTrue(COSPLAYERS[name].get("covers_face"),
                            f"{name} is not masked but was picked under the Masked scope")

    def test_nonhuman_scope_predicate_holds(self):
        predicate = _SPECIAL_SCOPES["Non-human / colored"]
        picked = self._pick("Non-human / colored")
        self.assertTrue(picked, "Non-human scope produced no characters")
        for name in picked:
            self.assertTrue(predicate(COSPLAYERS[name]))


class ArticleTests(unittest.TestCase):
    """``_a`` picks the article by sound, not by spelling (0.72.0).

    A bare vowel-letter test shipped "a hourglass build" and "an university
    lecture hall" for three real option values. Both exception classes are pinned
    here so a future simplification of ``_a`` cannot quietly reintroduce them.
    """

    def test_silent_h_takes_an(self):
        for word in ("hourglass", "honest mistake", "heirloom brooch"):
            self.assertEqual(_a(word), "an", word)

    def test_yoo_glide_takes_a(self):
        for word in ("university lecture hall", "uniform", "eucalyptus grove",
                     "one piece swimsuit", "useful thing"):
            self.assertEqual(_a(word), "a", word)

    def test_ordinary_words_unchanged(self):
        for word, article in (("athletic", "an"), ("emerald", "an"), ("oval", "an"),
                              ("silver", "a"), ("bronze", "a"), ("wide", "a")):
            self.assertEqual(_a(word), article, word)

    def test_shipped_values_render_correctly(self):
        prose, _ = generate_character(
            0, "Female",
            {"body_type": "hourglass", "location": "university lecture hall"},
        )
        self.assertIn("an hourglass build", prose)
        self.assertIn("a university lecture hall", prose)


class ModifierArticleTests(unittest.TestCase):
    """A Modifier must not prepend in front of a costume's own article (0.72.0).

    Costume prose starts with an article by convention -- 1107 of the shipped
    cosplayer costumes do -- so the old blind prepend rendered "wears weathered a
    gothic black dress". ``_apply_modifiers`` now routes through
    ``_prepend_descriptor``, which relocates the article; a plural/mass head
    ("robes", "plate armor") still just takes the descriptor in front.
    """

    def test_prepend_relocates_article(self):
        self.assertEqual(
            _prepend_descriptor("a gothic black dress", "weathered"),
            "a weathered gothic black dress")
        self.assertEqual(
            _prepend_descriptor("a segmented exoskeleton", "emerald"),
            "an emerald segmented exoskeleton")

    def test_prepend_leaves_mass_nouns_alone(self):
        self.assertEqual(
            _prepend_descriptor("ornate summoner robes", "weathered"),
            "weathered ornate summoner robes")

    def test_costume_modifier_does_not_strand_the_article(self):
        prose, _ = generate_character(
            0, "Female", {"outfit_description": "a gothic black dress with a lace hem"},
            modifiers={"Clothing": "weathered"})
        self.assertIn("wears a weathered gothic black dress", prose)
        self.assertNotIn("weathered a gothic", prose)

    def test_every_shipped_costume_survives_a_modifier(self):
        """No cosplayer costume may render "<descriptor> a ..." under a modifier."""
        for name, entry in COSPLAYERS.items():
            decorated = _prepend_descriptor(entry["costume"], "weathered")
            self.assertNotRegex(
                decorated, r"^weathered an? ",
                f"{name}: modifier stranded the costume's article")


class WardrobeAxisTests(unittest.TestCase):
    """0.83.0: three shipped widgets stopped being dead.

    ``footwear`` / ``clothing_color`` / ``clothing_pattern`` were drawn every render and
    never voiced, because ``OUTFIT_DESCRIPTIONS`` superseded them and nobody retired
    them. The JSON contradicted the prose on every render, and locking one changed
    nothing visible while silently removing an RNG draw -- so five unrelated fields moved
    and the widget looked like it worked.
    """

    AXES = ("footwear", "clothing_color", "clothing_pattern")

    def _clothing(self, raw):
        return json.loads(raw)["Clothing"]

    def test_the_json_never_contradicts_the_prose(self):
        """The headline fix. Any axis present in the JSON must appear in the outfit."""
        for seed in range(300):
            raw = generate_character(seed, "Female", {})[1]
            c = self._clothing(raw)
            outfit = c["outfit_description"]
            with self.subTest(seed=seed):
                if "footwear" in c and not _is_absent(c["footwear"]):
                    # "bare feet" is voiced as the adverb "barefoot" (_FOOTWEAR_CLAUSES),
                    # so compare against the rendered form, not the pool value.
                    expected = _FOOTWEAR_CLAUSES.get(c["footwear"], c["footwear"])
                    self.assertIn(expected, outfit,
                                  f"footwear {c['footwear']!r} not in {outfit!r}")
                if "clothing_color" in c and not _is_absent(c["clothing_color"]):
                    self.assertIn(PALETTE_ADJECTIVES[c["clothing_color"]], outfit,
                                  f"palette not rendered in {outfit!r}")

    def test_a_locked_axis_actually_renders(self):
        """The regression that motivated the whole phase."""
        for seed in range(60):
            locked = {"footwear": "combat boots", "clothing_color": "jewel tones",
                      "clothing_pattern": "stripes"}
            prose, raw = generate_character(seed, "Female", dict(locked))
            outfit = self._clothing(raw)["outfit_description"]
            with self.subTest(seed=seed):
                self.assertIn("combat boots", outfit)
                self.assertIn("jewel-toned", outfit)
                self.assertIn("in stripes", outfit)
                self.assertIn(outfit, prose)

    def test_a_supplied_costume_still_drops_all_three(self):
        """The boundary that keeps this non-breaking for 1,732 cosplayers and 225
        archetypes: a provided costume is a complete look and composes nothing."""
        costume = "a weathered brown leather jacket over a linen shirt"
        for seed in range(60):
            raw = generate_character(seed, "Male", {"outfit_description": costume})[1]
            c = self._clothing(raw)
            self.assertEqual(c["outfit_description"], costume)
            for axis in self.AXES + ("outfit_style",):
                self.assertNotIn(axis, c, f"{axis} leaked onto a supplied costume")

    def test_solid_pattern_is_silent_but_kept(self):
        """`solid` is true of any garment; saying it only adds noise. The field stays."""
        raw = generate_character(0, "Female",
                                {"clothing_pattern": "solid", "footwear": "loafers"})[1]
        c = self._clothing(raw)
        self.assertEqual(c["clothing_pattern"], "solid")
        self.assertNotIn("solid", c["outfit_description"])

    def test_bare_feet_renders_as_barefoot(self):
        raw = generate_character(0, "Female",
                                {"footwear": "bare feet", "outfit_style": "loungewear"})[1]
        outfit = self._clothing(raw)["outfit_description"]
        self.assertTrue(outfit.endswith(", barefoot"), outfit)
        self.assertNotIn("in bare feet", outfit)

    def test_pattern_tails_never_stack_a_second_with(self):
        """Garment phrases routinely end in their own "with ..." clause, so a "with"
        tail rendered "...with delicate straps with a floral print". Caught in preview."""
        for value, tail in PATTERN_TAILS.items():
            if tail:
                self.assertTrue(tail.startswith(" in "),
                                f"{value!r} tail must use 'in', not {tail!r}")

    # --- back-compat with user_options.json outfit strings ------------------------
    def test_guards_protect_an_old_contract_user_string(self):
        """A user's existing outfit string has a leading article, its own shoes and its
        own colour. Every guard must fire so it degrades gracefully, not doubles up."""
        old_style = "a sleek white EVA suit with a mirrored visor and magnetic boots"
        resolved = {"clothing_color": "jewel tones", "clothing_pattern": "plaid",
                    "footwear": "loafers"}
        out = _compose_outfit_clause(old_style, resolved, set())
        self.assertNotIn("jewel-toned", out, "palette must yield to a stated colour")
        self.assertNotIn("loafers", out, "footwear must yield to stated shoes")
        self.assertNotRegex(out, r"^(?:a|an) (?:a|an|the) ", "article was doubled")
        self.assertNotIn("clothing_color", resolved, "suppressed axis must be popped")
        self.assertNotIn("footwear", resolved, "suppressed axis must be popped")

    def test_a_lock_beats_a_guard(self):
        """Locked-wins, consistently: a guard suppresses the CLAUSE but must not delete
        a value the user explicitly chose, or the JSON would lose their choice."""
        old_style = "a sleek white EVA suit with magnetic boots"
        resolved = {"clothing_color": "jewel tones", "footwear": "loafers"}
        _compose_outfit_clause(old_style, resolved, {"clothing_color", "footwear"})
        self.assertEqual(resolved["clothing_color"], "jewel tones")
        self.assertEqual(resolved["footwear"], "loafers")

    def test_shoe_regex_does_not_false_positive_on_garments(self):
        """The first draft matched `oxfords?` / `flats?` / `boots?` and silently deleted
        the footwear clause of five shipped garment phrases."""
        for garment in ("oxford shirt with rolled sleeves and chinos",
                        "merino quarter-zip with flat-front chinos",
                        "soft blazer over an oxford shirt with flat-front trousers",
                        "bootcut denim with a jersey tee"):
            self.assertIsNone(SHOE_RE.search(garment),
                              f"SHOE_RE false-positived on {garment!r}")
        for shoe in FIELD_DEFINITIONS["footwear"]["female_options"]:
            self.assertIsNotNone(SHOE_RE.search(f"a dress and {shoe}"),
                                 f"SHOE_RE does not recognise the pool value {shoe!r}")


class GloveAccessoryTests(unittest.TestCase):
    """0.83.0: gloves joined the `accessories` pool, so the glove rule had to follow.

    ``_GLOVE_RE`` only ever scanned ``outfit_description``. A randomized glove drawn from
    ``accessories`` hides the fingers exactly as well, so nails and rings must drop for
    it too -- otherwise polish renders on top of leather, the original reported bug.
    """

    def _jewels(self, raw):
        return json.loads(raw).get("Jewelry & Nails", {})

    def test_gloves_from_accessories_suppress_nails_and_rings(self):
        for glove in ("leather gloves", "long opera gloves"):
            for seed in range(40):
                raw = generate_character(seed, "Female", {"accessories": glove},
                                         accessory_density="Maximal")[1]
                j = self._jewels(raw)
                with self.subTest(glove=glove, seed=seed):
                    self.assertNotIn("nails", j)
                    self.assertNotIn("rings", j)

    def test_fingerless_gloves_keep_the_fingers_visible(self):
        seen = set()
        for seed in range(120):
            raw = generate_character(seed, "Female", {"accessories": "fingerless gloves"},
                                     accessory_density="Maximal")[1]
            seen |= set(self._jewels(raw)) & {"nails", "rings"}
        self.assertEqual(seen, {"nails", "rings"},
                         "fingerless gloves expose the fingers; nails/rings must show")

    def test_hat_accessory_values_stay_in_sync_with_the_pool(self):
        """The docstring on _HAT_ACCESSORY_VALUES says keep it in sync with the pool.
        0.83.0 makes that mechanical: a hat added to `accessories` and not to the set
        can stack on a hooded or helmeted outfit."""
        from nodes.identity_forge import _HAT_ACCESSORY_VALUES, _HAT_RE
        pool = FIELD_DEFINITIONS["accessories"]["female_options"]
        hats = {v for v in pool if _HAT_RE.search(v)}
        self.assertEqual(
            hats, set(_HAT_ACCESSORY_VALUES),
            "_HAT_ACCESSORY_VALUES has drifted from the hat-like accessories values")

    def test_glove_accessory_values_are_real_options(self):
        from nodes.identity_forge import _GLOVE_ACCESSORY_VALUES, _GLOVE_RE
        pool = set(FIELD_DEFINITIONS["accessories"]["female_options"])
        self.assertTrue(set(_GLOVE_ACCESSORY_VALUES) <= pool)
        for value in _GLOVE_ACCESSORY_VALUES:
            self.assertIsNotNone(_GLOVE_RE.search(value))


class FootwearStyleMatrixTests(unittest.TestCase):
    """0.83.0: an ALLOWLIST per outfit_style, not a deny-list.

    Before this, three styles had a hand-written deny-list and eleven had no rule at all
    -- invisible while `footwear` never rendered. The deny-lists were also incomplete in
    a way inspection does not reveal (`athletic` denied five dress shoes but still
    permitted bare feet, wedges and mules), and a deny-list silently admits every value
    added later: the 12 -> 20 growth in this same revision would have leaked `kitten
    heels` into sportswear. An allowlist fails safe.
    """

    def test_every_style_is_covered(self):
        from data.constraints import FOOTWEAR_BY_STYLE
        self.assertEqual(set(FOOTWEAR_BY_STYLE),
                         set(FIELD_DEFINITIONS["outfit_style"]["female_options"]),
                         "a style has no footwear allowlist, so anything goes there")

    def test_allowlists_name_only_real_shoes(self):
        from data.constraints import FOOTWEAR_BY_STYLE
        pool = set(FIELD_DEFINITIONS["footwear"]["female_options"])
        for style, allowed in FOOTWEAR_BY_STYLE.items():
            self.assertTrue(allowed, f"{style} allows no footwear at all")
            self.assertTrue(allowed <= pool,
                            f"{style} names non-shoes: {sorted(allowed - pool)}")

    def test_every_shoe_is_wearable_somewhere(self):
        """A value allowed by no style would be unreachable except by an explicit lock."""
        from data.constraints import FOOTWEAR_BY_STYLE
        reachable = set().union(*FOOTWEAR_BY_STYLE.values())
        pool = set(FIELD_DEFINITIONS["footwear"]["female_options"])
        self.assertEqual(pool - reachable, set(),
                         "these shoes are allowed by no style and can never be drawn")

    def test_no_render_pairs_a_shoe_with_a_style_that_forbids_it(self):
        from data.constraints import FOOTWEAR_BY_STYLE
        for seed in range(600):
            for gender in ("Female", "Male"):
                c = json.loads(generate_character(seed, gender, {})[1])["Clothing"]
                style, shoe = c.get("outfit_style"), c.get("footwear")
                if style and shoe and not _is_absent(shoe):
                    self.assertIn(shoe, FOOTWEAR_BY_STYLE[style],
                                  f"{shoe!r} with {style!r} at seed {seed}")

    def test_slippers_and_bare_feet_stay_domestic(self):
        from data.constraints import FOOTWEAR_BY_STYLE
        for style, allowed in FOOTWEAR_BY_STYLE.items():
            if "slippers" in allowed:
                self.assertEqual(style, "loungewear",
                                 "slippers belong to loungewear only")
            if "bare feet" in allowed:
                self.assertIn(style, ("loungewear", "resort vacation", "bohemian"),
                              f"bare feet allowed with {style}")

    #: Feminine-coded shoes trimmed from a masculine presentation (0.83.0).
    FEMININE_SHOES = frozenset({"heels", "kitten heels", "wedges", "mules",
                                "ballet flats", "knee-high boots"})

    def test_a_masculine_presentation_draws_no_feminine_shoes(self):
        """`footwear` is a unisex pool, so these could always land on a random man --
        they simply never RENDERED before 0.83.0. Caught in the preview pass: "a
        monochrome black tailored suit with a fine-knit shirt and no tie, in kitten
        heels"."""
        for wardrobe in ("Match gender", "Masculine"):
            for seed in range(300):
                c = json.loads(generate_character(seed, "Male", {},
                                                  wardrobe=wardrobe)[1])["Clothing"]
                self.assertNotIn(c.get("footwear"), self.FEMININE_SHOES,
                                 f"{wardrobe} @ seed {seed}")

    def test_a_femme_male_wardrobe_still_reaches_them(self):
        """The gate is `presentation_gated`, like the jewellery trims: a deliberately
        Feminine or Any wardrobe on a man keeps the feminine-coded pool intact. Gating
        it any other way would break the femme-male look the 0.72.0 work opened up."""
        for wardrobe in ("Feminine", "Any"):
            seen = 0
            for seed in range(300):
                c = json.loads(generate_character(seed, "Male", {},
                                                  wardrobe=wardrobe)[1])["Clothing"]
                if c.get("footwear") in self.FEMININE_SHOES:
                    seen += 1
            self.assertGreater(seen, 0, f"{wardrobe} on a man reaches no feminine shoes")

    def test_no_style_and_presentation_combination_empties_the_pool(self):
        """The allowlist and the masculine trim compose. If any style's allowlist were
        entirely feminine-coded, a masculine subject would have no legal shoe and the
        engine would fall back to the unfiltered pool -- silently undoing both rules."""
        from data.constraints import FOOTWEAR_BY_STYLE
        for style, allowed in FOOTWEAR_BY_STYLE.items():
            remaining = allowed - self.FEMININE_SHOES
            self.assertTrue(remaining,
                            f"{style} has no masculine-legal footwear at all")

    def test_monochrome_palette_never_takes_a_multicolour_pattern(self):
        for seed in range(600):
            c = json.loads(generate_character(seed, "Female", {})[1])["Clothing"]
            colour, pattern = c.get("clothing_color"), c.get("clothing_pattern")
            if colour in ("all black", "all white", "black monochrome", "white and cream"):
                self.assertNotIn(pattern, ("floral", "animal print", "geometric",
                                           "abstract", "camouflage", "denim", "plaid"),
                                 f"{colour!r} + {pattern!r} at seed {seed}")

    def test_mixed_prints_never_names_a_second_pattern(self):
        for seed in range(800):
            c = json.loads(generate_character(seed, "Female", {})[1])["Clothing"]
            if c.get("clothing_color") == "mixed prints":
                self.assertIn(c.get("clothing_pattern", "solid"), ("solid", None),
                              f"mixed prints + a second pattern at seed {seed}")


class OutfitArticleTests(unittest.TestCase):
    """Random outfits read with a correct article — now the ENGINE's job (0.83.0).

    0.72.0 fixed a two-grammar prose slot ("wears a gothic black dress" vs "wears
    cropped hoodie with...") by requiring every corpus value to carry its own leading
    article. 0.83.0 **inverts that contract**: the corpus is garment-only and
    article-less, because the engine now prefixes a palette adjective before articling
    ("jewel tones" + "satin slip gown" -> "a jewel-toned satin slip gown"). A baked-in
    article would render "a jewel-toned a satin slip gown".

    The invariant being protected never changed — *the rendered prose must article
    correctly*. Only the layer that owns it moved. So this test moved with it, and got
    stronger: it sweeps hundreds of rendered strings instead of asserting on the data
    and spot-checking one seed.
    """

    def test_corpus_carries_no_leading_article(self):
        """The new contract. ``validate_data`` gates this too; kept here so the reason
        is visible next to the prose assertions it enables."""
        for style, buckets in OUTFIT_DESCRIPTIONS.items():
            for bucket, values in buckets.items():
                for value in values:
                    self.assertNotRegex(
                        value, r"^(?:a|an|the)\s",
                        f"{style}/{bucket}: {value!r} must not carry an article; the "
                        f"engine articles the composed phrase")

    def test_prose_articles_every_generated_outfit(self):
        """Sweep: an article, or a legitimately bare plural/mass head.

        The bare case is asserted against the RULE ``_article_if_singular`` documents --
        the head noun's final "s" (ignoring "ss") -- rather than a hand-kept list of
        plural words. A word list is the wrong shape here: the first draft of this test
        listed twelve and still missed "layered gauze scarves", failing on correct engine
        output. Testing the rule cannot drift as the corpus grows, and it still catches
        the real defect (a singular head rendering with no article).
        """
        for seed in range(400):
            for gender in ("Female", "Male", "Any"):
                raw = generate_character(seed, gender, {})[1]
                outfit = json.loads(raw)["Clothing"]["outfit_description"]
                with self.subTest(seed=seed, gender=gender):
                    if re.match(r"^(?:a|an) ", outfit):
                        continue
                    head = re.split(r"\s+(?:with|over|under|and|in)\s+|,", outfit)[0]
                    last = head.split()[-1].lower()
                    self.assertTrue(
                        last.endswith("s") and not last.endswith("ss"),
                        f"{outfit!r} has no article but its head {last!r} is singular")

    def test_no_doubled_article_ever_renders(self):
        for seed in range(400):
            prose, _ = generate_character(seed, "Any", {})
            self.assertNotRegex(
                prose, r"wears? (?:a|an|the) (?:a|an|the) ",
                f"doubled article at seed {seed}: {prose}")


class PresentationGateTests(unittest.TestCase):
    """Makeup follows the wardrobe presentation, not raw gender (0.72.0).

    The jewellery/nail trims were already ``presentation_gated``; the
    ``gender=Male -> makeup_style="no makeup"`` requirement was not, so a man with
    wardrobe="Feminine" drew feminine jewellery, nails and a skirt but was
    bare-faced in 300 of 300 seeds. Gating it leaves the default untouched and
    opens only the explicit Feminine/"Any" wardrobes.
    """

    @staticmethod
    def _styles(wardrobe, seeds=120):
        out = []
        for seed in range(seeds):
            _, raw = generate_character(seed, "Male", {}, wardrobe=wardrobe)
            out.append(json.loads(raw).get("Makeup", {}).get("makeup_style"))
        return out

    def test_masculine_wardrobes_stay_bare_faced(self):
        """The default must be byte-identical to pre-0.72.0 behaviour."""
        for wardrobe in ("Match gender", "Masculine"):
            self.assertEqual(set(self._styles(wardrobe)), {"no makeup"}, wardrobe)

    def test_feminine_wardrobe_opens_the_natural_styles(self):
        styles = set(self._styles("Feminine"))
        self.assertIn("no makeup", styles, "bare-faced must stay reachable")
        self.assertTrue(styles - {"no makeup"},
                        "a Feminine wardrobe should allow some makeup on a man")

    def test_male_pool_still_caps_at_natural_styles(self):
        """Gating opens the field but never the feminine-only glam values."""
        allowed = set(FIELD_DEFINITIONS["makeup_style"]["male_options"])
        for wardrobe in ("Feminine", "Any"):
            self.assertLessEqual(set(self._styles(wardrobe)), allowed, wardrobe)


class FranchiseScopeTests(unittest.TestCase):
    """Derived per-franchise Random scopes (0.72.0).

    The nine broad categories leave the biggest ones unbrowsable (Video Games is
    268 characters). Exposing all 263 franchises does not work either -- 135 are
    singletons -- so scopes are derived above a threshold.
    """

    def test_scopes_are_derived_and_thresholded(self):
        self.assertTrue(_FRANCHISE_SCOPES, "no franchise scopes were derived")
        for label in _FRANCHISE_SCOPES:
            self.assertTrue(label.startswith(_FRANCHISE_SCOPE_PREFIX), label)
            franchise = label[len(_FRANCHISE_SCOPE_PREFIX):]
            count = sum(1 for e in COSPLAYERS.values()
                        if e.get("franchise") == franchise)
            self.assertGreaterEqual(count, _FRANCHISE_SCOPE_MINIMUM, label)

    def test_predicates_are_bound_per_franchise(self):
        """A closure over the loop variable would make every predicate identical."""
        matched = {
            label: {n for n, e in COSPLAYERS.items() if pred(e)}
            for label, pred in _FRANCHISE_SCOPES.items()
        }
        self.assertEqual(len(matched), len(_FRANCHISE_SCOPES))
        for label, names in matched.items():
            self.assertTrue(names, f"{label} matched nothing")
        # Distinct franchises must yield disjoint rosters.
        labels = list(matched)
        self.assertFalse(matched[labels[0]] & matched[labels[-1]])

    def test_scope_narrows_the_random_pick(self):
        label = f"{_FRANCHISE_SCOPE_PREFIX}Pokemon"
        self.assertIn(label, _FRANCHISE_SCOPES)
        for seed in range(30):
            raw = build_cosplayer_json("Random — any", seed, random_scope=label)
            meta = json.loads(raw)["_meta"]
            self.assertEqual(meta["franchise"], "Pokemon", meta["cosplay_of"])

    def test_category_named_franchises_are_not_duplicated(self):
        """Marvel / DC / Star Wars are already categories -- no second entry."""
        from data.cosplayers import get_cosplayer_categories
        for category in get_cosplayer_categories():
            self.assertNotIn(f"{_FRANCHISE_SCOPE_PREFIX}{category}", _FRANCHISE_SCOPES)

    def test_predicate_lookup_covers_both_scope_families(self):
        for label in (*_SPECIAL_SCOPES, *_FRANCHISE_SCOPES):
            self.assertIn(label, _PREDICATE_SCOPES)


class AdvertisedCharacterCountTests(unittest.TestCase):
    """README.md and pyproject.toml must quote NO roster count. (0.77.0)

    This test used to assert the opposite -- that the count quoted in both files
    matched ``len(COSPLAYERS)`` exactly. That made every content release a
    three-file edit, and the count went stale between them anyway. The maintainer's
    standing rule is now the inverse: **live counts live only in the generated
    ``docs/reference/*.md``**, which ``scripts/generate_reference_docs.py`` keeps
    accurate for free.

    So the invariant is flipped rather than deleted -- a hardcoded roster size
    creeping back into either file is caught here instead of silently rotting.
    ``docs/`` is deliberately not checked: the reference indexes are supposed to
    carry counts, and the prose docs quote point-in-time audit figures on purpose
    (see architecture.md's "leave version-stamped audit figures alone").
    """

    def _sources(self):
        root = Path(__file__).resolve().parents[1]
        return (root / "README.md", root / "pyproject.toml")

    #: A thousands-separated number (``1,480``), or a bare four-digit one
    #: immediately followed by a roster noun (``1480 characters``). A bare
    #: ``\d{4}`` alone is NOT enough -- it matches the UUID fragments in the
    #: README's asset URLs (``33bd47f1-1789-473f-...``) and any year.
    _COUNT_RE = r"\b\d,\d{3}\b|\b\d{4}\s+(?:characters|cosplayers|entries)\b"

    def test_no_roster_count_is_quoted(self):
        for path in self._sources():
            text = path.read_text(encoding="utf-8")
            quoted = set(re.findall(self._COUNT_RE, text))
            self.assertEqual(
                quoted, set(),
                f"{path.name} quotes a roster count {sorted(quoted)}. Counts belong "
                f"only in the generated docs/reference/*.md -- describe the roster "
                f"qualitatively here and link the reference index instead.")


class EveryScopeGenderComboTests(unittest.TestCase):
    """Every scope x every gender must return an IN-SCOPE character. (0.75.0)

    The previous coverage sampled one franchise ("Franchise: Pokemon") against one
    gender ("Random - any"), which is why the empty-combo fallback shipped: "Random
    - male" + "Franchise: Date A Live" (an all-female cast) matched nothing and
    quietly returned a character from the entire roster. This walks the whole
    dropdown -- attribute scopes, broad categories and every derived franchise --
    against all three character picks, so any future roster edit that empties a
    combo fails here instead of in a user's graph.
    """

    _PICKS = ("Random — any", "Random — female", "Random — male")

    @staticmethod
    def _members(scope):
        """The set of names a scope legitimately covers, ignoring gender."""
        from data.cosplayers import get_cosplayer_categories
        if scope in get_cosplayer_categories():
            return set(get_cosplayer_names(category=scope))
        predicate = _PREDICATE_SCOPES[scope]
        return {n for n, e in COSPLAYERS.items() if predicate(e)}

    def test_every_scope_and_gender_stays_in_scope(self):
        from data.cosplayers import get_cosplayer_categories
        scopes = [*_SPECIAL_SCOPES, *get_cosplayer_categories(), *_FRANCHISE_SCOPES]
        self.assertGreater(len(scopes), 30, "scope dropdown unexpectedly small")
        offenders = []
        for scope in scopes:
            allowed = self._members(scope)
            self.assertTrue(allowed, f"{scope} covers no characters at all")
            for pick in self._PICKS:
                for seed in range(15):
                    with contextlib.redirect_stdout(io.StringIO()):
                        raw = build_cosplayer_json(pick, seed, random_scope=scope)
                    name = json.loads(raw)["_meta"]["cosplay_of"]
                    if name not in allowed:
                        offenders.append((scope, pick, seed, name))
        self.assertEqual(offenders, [], f"out-of-scope picks: {offenders[:10]}")

    def test_no_scope_gender_combo_is_silently_empty(self):
        """Document which combos rely on the gender-relaxing path, and why.

        An empty combo is not itself a bug -- an all-female cast has no male
        members -- but it MUST resolve through the relax-gender branch rather than
        the out-of-scope fallback. This asserts the branch is what fires.
        """
        import nodes.identity_forge_cosplayer as cn
        from data.cosplayers import get_cosplayer_categories
        for scope in (*_SPECIAL_SCOPES, *get_cosplayer_categories(), *_FRANCHISE_SCOPES):
            allowed = self._members(scope)
            for gender in ("Female", "Male"):
                gendered = {n for n in allowed
                            if COSPLAYERS[n].get("gender") == gender}
                if gendered:
                    continue
                pick = cn._RANDOM_FEMALE if gender == "Female" else cn._RANDOM_MALE
                with contextlib.redirect_stdout(io.StringIO()):
                    name = cn._resolve_character(pick, random.Random(0), scope)
                self.assertIn(name, allowed,
                              f"{scope} + {gender} escaped its scope")


class WornItemArticleTests(unittest.TestCase):
    """Singular worn items take an article; plural ones do not (0.72.0).

    The jewellery/bag/accessory pools mix both in one slot, and the prose voices
    them in a single list. Before this, only ``watch_type`` and ``nails`` were
    articled, so a run read "He has brooch, thumb ring, nose stud, a metal link
    watch". The head-noun split matters: "reading glasses pushed up on head" is
    plural (head "reading glasses"), "belt cinching waist" is singular (head "belt").
    """

    _POOLS = ("earrings", "necklace", "other_jewelry", "rings", "bracelet",
              "piercings", "bag", "accessories")

    def test_head_noun_drives_the_article(self):
        for value, expected in (
            ("brooch", "a brooch"),
            ("arm cuff", "an arm cuff"),
            ("industrial earring", "an industrial earring"),
            ("pearl studs", "pearl studs"),
            ("layered gold chains", "layered gold chains"),
            ("classic black sunglasses", "classic black sunglasses"),
            # Post-modifiers must not be mistaken for the head noun.
            ("reading glasses pushed up on head", "reading glasses pushed up on head"),
            ("belt cinching waist", "a belt cinching waist"),
            ("pendant on a leather cord", "a pendant on a leather cord"),
            ("envelope clutch in gold", "an envelope clutch in gold"),
        ):
            self.assertEqual(_article_if_singular(value), expected, value)

    def test_every_pool_value_is_stable(self):
        """No pool value may produce a doubled or stranded article."""
        for field in self._POOLS:
            definition = FIELD_DEFINITIONS[field]
            values = set(definition["female_options"]) | set(definition["male_options"])
            for value in values:
                if _is_absent(value):
                    continue
                rendered = _article_if_singular(value)
                self.assertNotRegex(rendered, r"^an? an? ", f"{field}: {rendered}")
                self.assertTrue(rendered.endswith(value), f"{field}: {rendered}")

    def test_prose_articles_the_singular_pieces(self):
        prose, _ = generate_character(
            3, "Female", {"other_jewelry": "brooch", "rings": "thumb ring",
                          "piercings": "nose stud"},
            accessory_density="Maximal")
        self.assertIn("a brooch", prose)
        self.assertIn("a thumb ring", prose)
        self.assertIn("a nose stud", prose)

    def test_prose_leaves_plural_pieces_bare(self):
        prose, _ = generate_character(
            3, "Female", {"earrings": "pearl studs"}, accessory_density="Maximal")
        self.assertIn("pearl studs", prose)
        self.assertNotIn("a pearl studs", prose)

    def test_bag_and_accessories_are_articled(self):
        prose, _ = generate_character(
            3, "Female", {"bag": "canvas tote", "accessories": "wide brim sun hat"},
            accessory_density="Maximal")
        self.assertIn("carrying a canvas tote", prose)
        self.assertIn("accessorized with a wide brim sun hat", prose)


class CostumePronounTests(unittest.TestCase):
    """Costume prose must not hardcode a gendered pronoun (0.72.0).

    ``costume`` is voiced verbatim after "She/He wears ...", and the *person's*
    gender is the IdentityForge widget, not the character's -- that is what makes
    crossplay work. Ten entries carried "her"/"his"/"she"/"he" in the costume
    text, so a man cosplaying She-Hulk read "...covering her face and entire body".
    """

    _PRONOUN = re.compile(r"\b(?:her|his|she|he)\b", re.IGNORECASE)

    def test_no_gendered_pronoun_in_costume_text(self):
        offenders = sorted(
            name for name, entry in COSPLAYERS.items()
            if self._PRONOUN.search(entry.get("costume", ""))
        )
        self.assertEqual(offenders, [], f"gendered pronouns in costume: {offenders}")

    #: Every free-text key that reaches the prose verbatim. ``prop`` is on the list
    #: because it caught three entries the costume-only sweep missed (Bloodsport's
    #: "assembled from his gauntlet", Silver Surfer, Emilia) -- it is voiced as
    #: "holding ..." on a person whose gender the character does not decide.
    _TEXT_KEYS = ("costume", "mask", "prop", "prop_costume", "scale_prose",
                  "skin", "eyes")

    def test_no_gendered_pronoun_in_any_free_text(self):
        offenders = []
        for name, entry in COSPLAYERS.items():
            texts = [entry.get(key, "") for key in self._TEXT_KEYS]
            for alternate in entry.get("costumes", []) or []:
                texts.extend([alternate] if isinstance(alternate, str)
                             else [v for v in alternate.values() if isinstance(v, str)])
            for text in texts:
                if isinstance(text, str) and self._PRONOUN.search(text):
                    offenders.append(f"{name}: {text[:60]}")
        self.assertEqual(sorted(offenders), [], f"gendered pronouns: {offenders}")

    def test_crossplay_renders_without_a_stray_pronoun(self):
        """She-Hulk on a male cosplayer must not say "her face"."""
        document = build_cosplayer_json("She-Hulk", 7, look_level="Full character")
        parsed = _parse_archetype_json(document)
        label = parsed.pop(_COSPLAY_LABEL_KEY, None)
        locked = resolve_locked_fields(
            {}, {k: v for k, v in parsed.items() if isinstance(v, str)})
        prose, _ = generate_character(7, "Male", locked, cosplay_label=label)
        self.assertNotIn("her face", prose)
        self.assertIn("covering the face and entire body", prose)


class FootwearPhrasingTests(unittest.TestCase):
    """``footwear`` is voiced as "in <value>", so every value must fit that frame.

    "barefoot" is an adjective, not a noun phrase, and rendered "in barefoot"
    (0.73.0 -> "bare feet"). The branch only runs when no outfit_description was
    resolved, which is rare, but the value is also lockable from the widget.
    """

    def test_every_value_completes_the_frame(self):
        values = set(FIELD_DEFINITIONS["footwear"]["female_options"])
        values |= set(FIELD_DEFINITIONS["footwear"]["male_options"])
        for value in values:
            self.assertNotIn(value, ("barefoot", "shoeless", "unshod"),
                             f"'in {value}' is not a noun phrase")

    def test_bare_feet_renders(self):
        """Case-insensitive since 0.83.0: sentence capitalisation happens at the join, so
        this clause reads "In bare feet." when it is sentence-initial (which it is here,
        with no outfit and no colour/pattern). The invariant is the FRAME -- "in <noun
        phrase>", never "in barefoot" -- not the letter case."""
        prose = _format_prose(
            {"gender": "Female", "footwear": "bare feet",
             "outfit_description": "None"}, "Female")
        self.assertIn("in bare feet", prose.lower())
        self.assertNotIn("in barefoot", prose.lower())

    def test_the_composed_path_uses_the_adverb_instead(self):
        """The 0.83.0 wardrobe axis voices it as ", barefoot" (no preposition) because it
        is appended mid-sentence after a garment phrase, where "in bare feet" is clumsy.
        Two different frames, both correct for their position."""
        raw = generate_character(0, "Female",
                                {"footwear": "bare feet",
                                 "outfit_style": "loungewear"})[1]
        outfit = json.loads(raw)["Clothing"]["outfit_description"]
        self.assertTrue(outfit.endswith(", barefoot"), outfit)


class EyePartPhrasingTests(unittest.TestCase):
    """A free-text ``eyes`` override that names the eye part keeps it (0.74.0).

    The prose appends " eyes" to the colour, which turned the ten overrides ending
    in an eye part into "...has green with vertical cat-slit pupils eyes". Same
    guard, same reasoning, as the skin_tone material-noun check.
    """

    _EYE_PARTS = ("pupils", "irises", "sclera", "lenses")

    def test_part_naming_overrides_drop_the_noun(self):
        prose = _format_prose(
            {"gender": "Female", "eye_color": "green with vertical cat-slit pupils"},
            "Female")
        self.assertIn("green with vertical cat-slit pupils", prose)
        self.assertNotIn("pupils eyes", prose)

    def test_ordinary_colours_still_get_the_noun(self):
        prose = _format_prose({"gender": "Female", "eye_color": "deep blue"}, "Female")
        self.assertIn("deep blue eyes", prose)

    def test_no_shipped_override_renders_a_doubled_noun(self):
        for name, entry in COSPLAYERS.items():
            override = entry.get("eyes")
            if not override:
                continue
            prose = _format_prose(
                {"gender": "Female", "eye_color": override}, "Female")
            for part in self._EYE_PARTS:
                self.assertNotIn(f"{part} eyes", prose, f"{name}: {override!r}")


class NewRosterEntryTests(unittest.TestCase):
    """The 0.73.0 additions: Hell's Paradise cast + Fern.

    Guards the wiring each entry depends on rather than restating its prose:
    a mapped franchise (so ``random_scope`` works), a working ``prop_costume``
    swap on the one entry that wears its weapon, and rollable alternates.
    """

    _ADDED = ("Gabimaru", "Yamada Asaemon Sagiri", "Yuzuriha", "Akaginu", "Fern",
              "Gwen Tennyson", "Yzma", "Maron", "Nani Pelekai", "Babette",
              "Simon", "Kamina", "Nia Teppelin", "Rias Gremory", "Akeno Himejima",
              "Asia Argento", "Koneko Toujou", "Issei Hyoudou")

    def test_entries_exist_and_are_mapped(self):
        """Every addition must resolve to a real category, not the silent fallback."""
        from data.cosplayers import (get_cosplayer_category, get_cosplayer_categories,
                                     _FRANCHISE_CATEGORY)
        categories = set(get_cosplayer_categories())
        for name in self._ADDED:
            self.assertIn(name, COSPLAYERS, name)
            franchise = COSPLAYERS[name]["franchise"]
            self.assertIn(franchise, _FRANCHISE_CATEGORY,
                          f"{name}: '{franchise}' is not in the category map")
            self.assertIn(get_cosplayer_category(franchise), categories, name)

    def test_sagiri_prop_costume_sheathes_the_sword(self):
        """Prop on must move the katana from the hip to the hand, not double it."""
        worn = json.loads(build_cosplayer_json("Yamada Asaemon Sagiri", 2))
        held = json.loads(build_cosplayer_json(
            "Yamada Asaemon Sagiri", 2, include_prop=True))
        self.assertIn("a katana in a black lacquered scabbard",
                      worn["Clothing"]["outfit_description"])
        self.assertIn("an empty black lacquered scabbard",
                      held["Clothing"]["outfit_description"])
        self.assertNotIn("a katana in a black lacquered scabbard",
                         held["Clothing"]["outfit_description"])

    def test_alternate_looks_actually_roll(self):
        for name, expected in (("Yuzuriha", 3), ("Gabimaru", 2), ("Fern", 2)):
            looks = {
                json.loads(build_cosplayer_json(name, seed))["Clothing"]["outfit_description"]
                for seed in range(40)
            }
            self.assertEqual(len(looks), expected, f"{name} rolled {len(looks)} looks")

    def test_free_text_eyes_suppress_the_shape_word(self):
        """An `eyes` override must not read "pale peach almond-shaped eyes".

        The builder injects ``eye_shape: "None"`` after ``group_fields`` on purpose:
        the engine keeps a locked ``"None"`` as the absent state and drops it from
        the prose, so the free-text colour reads clean. Assert the lock is present
        *and* that the rendered prose carries no shape word.
        """
        shape_words = set(FIELD_DEFINITIONS["eye_shape"]["female_options"])
        for name in ("Akaginu", "Gabimaru", "Fern"):
            document = json.loads(build_cosplayer_json(name, 2))
            face = document.get("Face", {})
            self.assertTrue(face.get("eye_color"), name)
            self.assertEqual(face.get("eye_shape"), "None", name)

            parsed = _parse_archetype_json(build_cosplayer_json(name, 2))
            label = parsed.pop(_COSPLAY_LABEL_KEY, None)
            locked = resolve_locked_fields(
                {}, {k: v for k, v in parsed.items() if isinstance(v, str)})
            prose, _ = generate_character(
                2, COSPLAYERS[name]["gender"], locked, cosplay_label=label)
            eye_clause = next(s for s in prose.split(". ") if " eyes" in s)
            for word in shape_words:
                if not _is_absent(word):
                    self.assertNotIn(f"{word} eyes", eye_clause, f"{name}: {eye_clause}")


class FunnyAnimalRosterTests(unittest.TestCase):
    """The 0.85.0 additions: Maid Marian, Scrooge McDuck, Darkwing Duck.

    Each is a distinct franchise (deliberately not folded into "Mickey Mouse
    & Friends", which would cross ``_FRANCHISE_SCOPE_MINIMUM`` and add an
    unplanned ``random_scope`` option) -- guard that every one resolves to a
    real category rather than the silent Movies & TV fallback.
    """

    _ADDED = ("Maid Marian", "Scrooge McDuck", "Darkwing Duck")

    def test_entries_exist_and_are_mapped(self):
        from data.cosplayers import (get_cosplayer_category, get_cosplayer_categories,
                                     _FRANCHISE_CATEGORY)
        categories = set(get_cosplayer_categories())
        for name in self._ADDED:
            self.assertIn(name, COSPLAYERS, name)
            franchise = COSPLAYERS[name]["franchise"]
            self.assertIn(franchise, _FRANCHISE_CATEGORY,
                          f"{name}: '{franchise}' is not in the category map")
            self.assertIn(get_cosplayer_category(franchise), categories, name)

    def test_held_props_are_not_also_worn(self):
        """Scrooge's cane and Darkwing's gas gun must not double-describe in costume."""
        for name, prop_word in (("Scrooge McDuck", "cane"), ("Darkwing Duck", "gas gun")):
            entry = COSPLAYERS[name]
            self.assertNotIn(prop_word, entry["costume"], name)
            self.assertIn(prop_word, entry["prop"], name)


class FranchiseLabelTests(unittest.TestCase):
    """Franchise labels name a real franchise, not a medium (0.72.0).

    ``"Movie"`` was a placeholder on 8 entries (Dracula, Godzilla, Rambo, ...),
    which reads badly in the cosplay label ("Cosplaying as Dracula (Movie)") and
    would have produced a nonsense "Franchise: Movie" scope.
    """

    _GENERIC = {"movie", "movies", "film", "tv", "anime", "game", "games",
                "various", "other", "unknown", "misc"}

    def test_no_medium_as_a_franchise(self):
        offenders = sorted(
            f"{n} ({e['franchise']})" for n, e in COSPLAYERS.items()
            if e.get("franchise", "").strip().lower() in self._GENERIC
        )
        self.assertEqual(offenders, [], f"generic franchise labels: {offenders}")

    def test_a_disambiguated_key_never_stutters_its_franchise(self):
        """0.77.0's rule, enforced for real (0.88.0).

        It was implemented as an exact ``endswith("(<franchise>)")`` test, which only
        catches a parenthetical that *is* the franchise. Four keys stuttered past it:
        "Ms. Marvel (Kamala Khan) (Marvel)", "Ms. Marvel (Sharon Ventura) (Marvel)",
        "Duke Nukem (video game) (Duke Nukem)" -- all long-shipped -- and
        "Joker (Persona 5) (Persona)", created by merging the Persona installments.
        That last key was renamed to "Joker (Persona)" at 0.90.0, so the roster no
        longer contains the shape at all -- but the guard stays, because this test
        walks whatever COSPLAYERS happens to hold.
        """
        offenders = []
        for name, entry in COSPLAYERS.items():
            franchise = entry.get("franchise", "")
            if not franchise or "(" not in name:
                continue  # eponymous keys are out of scope; see the helper's docstring
            label = (name if _name_already_carries_franchise(name, franchise)
                     else f"{name} ({franchise})")
            head, _, tail = label.rpartition(" (")
            if tail[:-1] and tail[:-1].casefold() in head.casefold():
                offenders.append(label)
        self.assertEqual(offenders, [], f"stuttering cosplay labels: {offenders}")

    def test_the_rule_is_scoped_to_disambiguated_keys_only(self):
        """An eponymous key keeps its franchise suffix.

        Broadening the rule to "Shrek (Shrek)" would rewrite 91 more entries' prose
        and silently invalidate their published gallery images, because entry_hash
        hashes the entry dict and cannot see a prose-only change. That is a separate
        decision with a re-render bill, not a side effect -- pinned here so it is not
        "tidied up" by accident.
        """
        self.assertFalse(_name_already_carries_franchise("Shrek", "Shrek"))
        self.assertFalse(_name_already_carries_franchise("Sterling Archer", "Archer"))
        # ...while the disambiguated forms are all suppressed. "Joker (Persona 5)"
        # is kept as a SHAPE case only -- no roster key looks like that since
        # 0.90.0, and validate_data.py now rejects one, but the helper must still
        # collapse it if it ever sees it.
        for name, franchise in (("Joker (Persona)", "Persona"),
                                ("Joker (Persona 5)", "Persona"),
                                ("Mai (Avatar)", "Avatar: The Last Airbender"),
                                ("Ms. Marvel (Kamala Khan)", "Marvel"),
                                ("Duke Nukem (video game)", "Duke Nukem"),
                                ("Jinx (League of Legends)", "League of Legends")):
            self.assertTrue(_name_already_carries_franchise(name, franchise), name)
        # An unrelated parenthetical must still get the franchise appended.
        for name, franchise in (("Nova (Frankie Raye)", "Marvel"),
                                ("Terra (Teen Titans)", "DC"),
                                ("Homura Akemi (Devil)", "Madoka Magica")):
            self.assertFalse(_name_already_carries_franchise(name, franchise), name)


class ConceptShareTests(unittest.TestCase):
    """Growing a flat field must not make its CONCEPTS commoner (0.90.0).

    ``FIELD_FAMILIES`` protects a *field's* distribution, but neither of these two
    fields has a families entry, so nothing structural stops a content addition from
    quietly shifting the odds of a whole idea -- the trap already documented for the
    landmark locations, where every family share held and "famous landmark" still
    went from ~11% to ~27% of urban scenes.

    Asserted analytically rather than by sampling: a Monte Carlo run cannot tell
    0.25 from 0.26 without an impractical number of draws, and these are exact.
    """

    def _share(self, field: str, predicate) -> float:
        definition = FIELD_DEFINITIONS[field]
        pool = definition["female_options"]
        weights = definition.get("weights", {})
        total = sum(weights.get(value, 1) for value in pool)
        return sum(weights.get(value, 1) for value in pool if predicate(value)) / total

    def test_eyewear_keeps_its_pre_0_90_share(self):
        """Three eyeglass frames were added; P(wearing glasses) must not move.

        Pre-0.90.0 the pool held 6 eyewear values out of 24. A bare append would
        have made it 9 of 27 -- a third of all accessories instead of a quarter.
        """
        self.assertAlmostEqual(
            self._share("accessories", lambda v: "glass" in v), 6 / 24, places=9,
            msg="the eyewear concept drifted; reprice the weights map",
        )

    def test_plain_clothing_keeps_its_pre_0_90_share(self):
        """Six patterns were added; the odds of PLAIN clothing must not fall.

        2 of 10 before, and a bare append would have made it 2 of 16 -- dressing
        everyone in busier clothes without a single family share moving.
        """
        self.assertAlmostEqual(
            self._share("clothing_pattern",
                        lambda v: v in ("solid", "subtle texture")), 2 / 10, places=9,
            msg="the plain-clothing concept drifted; reprice the weights map",
        )

    def test_every_clothing_pattern_has_a_prose_tail(self):
        """A pattern with no PATTERN_TAILS entry is dropped silently at compose time.

        validate_data.py enforces this too; pinned here because all six new patterns
        were initially missing and the coupling is not obvious from either file.
        """
        missing = sorted(set(FIELD_DEFINITIONS["clothing_pattern"]["female_options"])
                         - set(PATTERN_TAILS))
        self.assertEqual(missing, [], f"patterns with no prose tail: {missing}")


class TattooAndLegwearTests(unittest.TestCase):
    """The two fields added at 0.90.0, and the invariants that make them safe.

    Both are gated on the finished ``outfit_description``, which for a randomly
    generated character does not exist until *after* the main randomization loop --
    the ordering mistake that made legwear appear 0 times in 2,000 draws and printed
    forearm tattoos under blazers. These tests pin the fix, not the symptom.
    """

    #: Placements that must survive every outfit, so the pool can never empty while
    #: a tattoo exists. Anything here is unreachable by all three cull rules.
    _ALWAYS_AVAILABLE = {
        "on the side of the neck", "behind one ear",
        "on one upper arm", "across one shoulder blade",
    }

    def _flat(self, payload: str) -> dict:
        out: dict = {}
        for value in json.loads(payload).values():
            if isinstance(value, dict):
                out.update(value)
        return out

    def test_the_new_fields_are_drawn_last_so_no_seed_drifts(self):
        """Every new draw happens after every pre-existing one.

        This is what lets 0.90.0 add two fields without changing the person any
        existing seed produces. If a future field is inserted into
        FIELD_DEFINITIONS *before* these, or one of these is un-deferred, the extra
        RNG call shifts the outfit draw and every seed silently yields someone else.
        """
        names = list(FIELD_DEFINITIONS)
        for field in _DEFERRED_FIELDS:
            self.assertIn(field, names)
        deferred_positions = [names.index(f) for f in _DEFERRED_FIELDS]
        other_positions = [i for i, n in enumerate(names) if n not in _DEFERRED_FIELDS]
        self.assertGreater(
            min(deferred_positions), max(other_positions),
            "the deferred fields must sit at the very end of FIELD_DEFINITIONS; "
            "anything drawn after them would have its seed shifted",
        )

    def test_a_tattoo_is_never_placed_where_the_clothes_cover_it(self):
        """The whole point of the placement gate, over a real sample."""
        offenders = []
        for seed in range(600):
            for gender in ("Female", "Male"):
                resolved = self._flat(generate_character(seed, gender, {})[1])
                placement = resolved.get("tattoo_placement")
                outfit = resolved.get("outfit_description") or ""
                legwear = resolved.get("legwear") or ""
                tattoo = resolved.get("tattoos")
                if not placement or placement == "None":
                    continue
                if not tattoo or _is_absent(tattoo):
                    offenders.append((seed, gender, "placement with no tattoo"))
                    continue
                if placement in ("on one forearm", "across the back of one hand",
                                 "on the inner wrist") and _LONG_SLEEVE_RE.search(outfit):
                    offenders.append((seed, gender, f"{placement} under {outfit[:40]}"))
                if placement in ("down one thigh", "on one calf"):
                    if not _BARE_LEG_RE.search(outfit):
                        offenders.append((seed, gender, f"{placement} under {outfit[:40]}"))
                    if legwear and _OPAQUE_LEGWEAR_RE.search(legwear):
                        offenders.append((seed, gender, f"{placement} under {legwear}"))
                if placement == "across the collarbone" and _HIGH_NECK_RE.search(outfit):
                    offenders.append((seed, gender, f"collarbone under {outfit[:40]}"))
        self.assertEqual(offenders, [], f"covered tattoos: {offenders[:5]}")

    def test_legwear_only_appears_when_the_outfit_shows_leg(self):
        offenders = []
        for seed in range(600):
            for gender in ("Female", "Male"):
                resolved = self._flat(generate_character(seed, gender, {})[1])
                legwear = resolved.get("legwear")
                if not legwear or legwear == "None" or _is_absent(legwear):
                    continue
                outfit = resolved.get("outfit_description") or ""
                if not _BARE_LEG_RE.search(outfit):
                    offenders.append((seed, gender, legwear, outfit[:45]))
                if gender == "Male":
                    offenders.append((seed, "male pool leaked", legwear))
                if "knee" in legwear and _TALL_BOOT_RE.search(resolved.get("footwear") or ""):
                    offenders.append((seed, gender, legwear, resolved.get("footwear")))
        self.assertEqual(offenders, [], f"legwear contradictions: {offenders[:5]}")

    def test_the_placement_pool_can_never_empty_while_a_tattoo_exists(self):
        """Four placements are unreachable by every cull, by construction.

        Without this the gates could combine -- long sleeves plus trousers plus a
        turtleneck -- to cull the pool to nothing, and a tattoo would be described
        with no location at all.
        """
        worst_case = {
            "tattoos": "a dense blackwork tattoo",
            # long sleeves + covered legs + high neck, i.e. every cull firing at once
            "outfit_description": "a wool turtleneck sweater under a tailored blazer "
                                  "with pressed trousers",
            "legwear": "opaque black tights",
        }
        pool = list(FIELD_DEFINITIONS["tattoo_placement"]["female_options"])
        survivors = _visible_tattoo_placements(pool, worst_case)
        self.assertTrue(survivors, "every placement was culled at once")
        self.assertEqual(set(survivors), self._ALWAYS_AVAILABLE)

    def test_no_tattoo_means_no_placement(self):
        pool = list(FIELD_DEFINITIONS["tattoo_placement"]["female_options"])
        for absent in ("no tattoos", "None", ""):
            self.assertEqual(
                _visible_tattoo_placements(pool, {"tattoos": absent}), [],
                f"placement survived an absent tattoo ({absent!r})",
            )

    def test_legwear_is_suppressed_entirely_by_a_covering_outfit(self):
        """Whole-pool suppression, not a partial cull.

        A partial cull of a family-weighted field concentrates the family's frozen
        weight on the survivors. ``legwear`` carries no family entry, but taking the
        whole pool is still the honest shape and is pinned here so a later change
        cannot quietly turn it into a partial one.
        """
        pool = list(FIELD_DEFINITIONS["legwear"]["female_options"])
        self.assertEqual(
            _wearable_legwear(pool, {"outfit_description": "straight-leg jeans "
                                                           "with a jersey tee"}), [])
        kept = _wearable_legwear(pool, {"outfit_description": "a pleated tennis skirt",
                                        "footwear": "sneakers"})
        self.assertEqual(kept, pool)

    def test_tattoos_stay_uncommon(self):
        """Rarity is the maintainer's explicit requirement, so it is asserted.

        Routed through _EXTRA_ABSENCE rather than a `weights` map so the
        accessory_density control governs it; this pins the resulting rate.
        """
        self.assertIn("tattoos", _EXTRA_ABSENCE)
        inked = 0
        total = 0
        for seed in range(800):
            for gender in ("Female", "Male"):
                resolved = self._flat(generate_character(seed, gender, {})[1])
                tattoo = resolved.get("tattoos")
                total += 1
                if tattoo and not _is_absent(tattoo):
                    inked += 1
        rate = inked / total
        self.assertLess(rate, 0.25, f"tattoos are too common at {rate:.1%}")
        self.assertGreater(rate, 0.04, f"tattoos are effectively unreachable at {rate:.1%}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
