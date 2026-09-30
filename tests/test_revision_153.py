"""1.5.3: regressions from the maintainer's idforge-929-concern renders."""
import re
import unittest

from nodes.identity_forge import (
    _GATHERED_HAIR_STYLES, _LOWER_FACE_COVER_RE, _MASCULINE_NECK_CLAUSES, _OBJECT_TOKEN_CLAUSES,
    generate_character,
)
from nodes.identity_forge_cosplayer import _MASK_OFF
from tests.preview_cosplayer import render

_JEWELRY_WORDS = re.compile(r"\b(?:ring|earrings?|studs?|necklace|bracelet|chain|pendant|hoops?)\b", re.I)


class LowerFaceMaskTests(unittest.TestCase):
    """Kitana's mask was pulled under her chin: the prose still described her mouth."""

    def test_regex_matches_lower_face_masks_only(self):
        for text in ("a blue face mask covering the mouth and nose",
                     "a scarf drawn up over the nose to mask the lower face",
                     "a bamboo muzzle held across the mouth by a red cord",
                     "a black cloth mask across the nose and mouth leaving the eyes bare"):
            self.assertRegex(text, _LOWER_FACE_COVER_RE)
        for text in ("a green ninja outfit with a face mask pulled down around the neck",
                     "a white half-mask covering the right side of the face",
                     "a visored half mask covering the upper face",
                     "glasses over the nose"):
            self.assertNotRegex(text, _LOWER_FACE_COVER_RE)

    def test_kitana_never_voices_the_mouth(self):
        for seed in range(12):
            prose, _ = render("Kitana", "", "Costume only", seed)
            self.assertNotRegex(prose, r"\blips\b|\bsmile\b|lip colour|expression is", prose)

    def test_a_widget_lock_still_voices_the_expression(self):
        _, js = generate_character(1, "Female", {"outfit_description": "a mask covering the mouth"})
        self.assertNotIn("expression", js)
        prose, _ = generate_character(1, "Female", {"outfit_description": "a mask covering the mouth",
                                                    "expression": "solemn"},
                                      widget_locked=frozenset({"expression"}))
        self.assertIn("expression is solemn", prose)


class CosplayJewelryTests(unittest.TestCase):
    """Chewbacca's ring, Kitana's bracelet, a stud on a 1940s detective (#01430-#01466)."""

    def test_full_character_adds_no_random_jewelry_or_nails(self):
        for name in ("Detective Frank Harris", "Kitana", "Chewbacca", "Daredevil"):
            for seed in range(8):
                prose, _ = render(name, "", "Full character", seed)
                self.assertNotRegex(prose, _JEWELRY_WORDS, f"{name} {seed}")
                self.assertNotIn(" nails", prose, f"{name} {seed}")

    def test_costume_only_keeps_jewelry_unmasked_and_drops_it_masked(self):
        unmasked = sum(bool(_JEWELRY_WORDS.search(render("Detective Frank Harris", "Female", "Costume only", s)[0]))
                       for s in range(30))
        self.assertGreater(unmasked, 0)
        for seed in range(30):
            prose, _ = render("Shao Kahn", "", "Costume only", seed)
            self.assertNotRegex(prose, _JEWELRY_WORDS, seed)
        revealed = sum(bool(_JEWELRY_WORDS.search(render("Shao Kahn", "Female", "Costume only", s, _MASK_OFF)[0]))
                       for s in range(30))
        self.assertGreater(revealed, 0)

    def test_chewbacca_is_a_furred_shell_not_a_person(self):
        for seed in range(8):
            prose, _ = render("Chewbacca", "", "Costume only", seed)
            self.assertNotRegex(prose, r"year-old|physique|broad shoulders|posture", seed)
            self.assertIn("long shaggy brown fur", prose)

    def test_muscular_costume_pins_the_physique(self):
        for seed in range(8):
            prose, _ = render("Shao Kahn", "", "Costume only", seed)
            self.assertIn("muscular physique", prose, seed)

    def test_masculine_earring_rate(self):
        worn = 0
        for seed in range(600):
            _, js = generate_character(seed, "Male", {})
            worn += '"no earrings"' not in js and '"earrings"' in js
        self.assertLess(worn / 600, 0.075)


class VoiceTests(unittest.TestCase):
    def test_noun_less_values_get_a_noun(self):
        self.assertEqual(_OBJECT_TOKEN_CLAUSES[("rings", "delicate gemstone")], "a delicate gemstone ring")
        prose, _ = generate_character(3, "Female", {"rings": "delicate gemstone", "forehead": "prominent brow ridge"})
        self.assertIn("a delicate gemstone ring", prose)
        self.assertNotIn("brow ridge forehead", prose)

    def test_gathered_hair_is_worn_in_not_a_second_hairdo(self):
        self.assertIn("ballerina bun", _GATHERED_HAIR_STYLES)
        prose, _ = generate_character(2, "Female", {"hair_length": "long", "hair_style": "ballerina bun"})
        self.assertRegex(prose, r"hair is [^.]*, worn in a ballerina bun")
        prose, _ = generate_character(2, "Female", {"hair_length": "long", "hair_style": "half up half down"})
        self.assertIn(", worn half up half down", prose)
        prose, _ = generate_character(2, "Female", {"hair_length": "long", "hair_style": "worn down"})
        self.assertNotIn("worn in", prose)

    def test_masculine_neck_is_not_elegant(self):
        self.assertIn("elegant", _MASCULINE_NECK_CLAUSES)
        for seed in range(60):
            prose, _ = generate_character(seed, "Male", {"neck_length": "elegant"})
            self.assertNotIn("an elegant neck", prose, seed)

    def test_petite_is_said_once(self):
        for seed in range(40):
            prose, _ = generate_character(seed, "Female", {"height": "petite", "body_type": "petite and slim"})
            self.assertNotIn("petite and slim", prose, seed)
            self.assertEqual(prose.split(".")[0].lower().count("petite"), 1, seed)


if __name__ == "__main__":
    unittest.main()
