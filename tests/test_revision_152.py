"""1.5.2: regressions from the maintainer's idforge-928-concern renders."""
import json
import unittest

from data.templates import ARCHETYPES, _COSTUMES
from nodes.identity_forge import _fit_extras_to_garment, generate_character


def _flat(js):
    return {k: v for g in json.loads(js).values() if isinstance(g, dict) for k, v in g.items()}


class SumoBodyTests(unittest.TestCase):
    """ "a sumo wrestler's body" drew a second person behind every woman (#00921-00959)."""

    def test_no_possessive_person_names_the_body(self):
        for gender, look in ARCHETYPES["Sumo Wrestler"]["variants"].items():
            self.assertNotIn("wrestler's", look["outfit_description"], gender)
            self.assertIn("enormously large", look["outfit_description"], gender)


class ObjectTokenTests(unittest.TestCase):
    """Value words that drew objects: banknotes (#00973), feathers (#01033, #01057)."""

    def test_voicing_avoids_the_object_words(self):
        locks = {"hair_highlights": "money piece", "eyebrow_makeup": "feathered",
                 "skin_details": "birthmark on neck", "makeup_style": "soft glam",
                 "hair_length": "long"}
        for seed in range(5):
            prose, js = generate_character(seed, "Female", dict(locks))
            self.assertNotIn("money", prose.lower())
            self.assertNotIn("feathered brows", prose)
            self.assertIn("light-brown birthmark", prose)
            flat = _flat(js)
            self.assertEqual(flat["hair_highlights"], "money piece")  # the value is unchanged
            self.assertEqual(flat["eyebrow_makeup"], "feathered")

    def test_no_costume_leaves_a_glove_loose(self):
        """One glove tucked in a pocket rendered one glove (#00998)."""
        for name, costume in _COSTUMES.items():
            for text in costume if isinstance(costume, list) else [costume]:
                self.assertNotRegex(text, r"gloves? (?:tucked|hanging|clipped|stuffed)", name)

    def test_named_masks_have_a_place(self):
        """An unplaced mask landed on the bodice or at the chest (#01176, gallery)."""
        looks = [ARCHETYPES["Masquerade Guest"]["variants"][g]["outfit_description"]
                 for g in ("Female", "Male")]
        looks += ARCHETYPES["Mardi Gras Reveler"]["variants"]["Female"]["outfit_description"]
        for text in looks:
            self.assertIn("worn over the eyes", text)
        # The full beaked mask hung on a cane (#01210); worn over the face it still sat
        # beside the head, so it is pushed up.
        for text in _COSTUMES["Plague Doctor"]:
            self.assertIn("pushed up onto the top of the head", text)
            self.assertNotIn("cane", text)

    def test_netrunner_names_what_is_under_the_jacket(self):
        """With only a jacket named, the gallery sample came back bare under it."""
        for text in _COSTUMES["Cyberpunk Netrunner"]:
            self.assertRegex(text, r"\bover a black [a-z -]+ and slim black")
            self.assertNotIn("utility straps", text)  # rendered as suspenders (#01082)

    def test_robes_take_one_colour(self):
        """ "white and brass robes" rendered a white robe beside a brown one (#01049, #01050)."""
        for name in ("Angelic Being", "Celestial Cleric"):
            self.assertNotIn("white and {metal}", _COSTUMES[name], name)


class GarmentBoundExtraTests(unittest.TestCase):
    """A pocket square needs a tailored jacket; opera gloves need an evening garment."""

    def _accessory(self, accessory, outfit, style="cocktail semi-formal"):
        resolved = {"accessories": accessory, "outfit_description": outfit,
                    "outfit_style": style}
        _fit_extras_to_garment(resolved, set())
        return resolved["accessories"]

    def test_pocket_square(self):
        dropped = ["a wrap coat over a camel velvet wrap dress",
                   "an all-black harrington jacket over a henley with jeans",
                   "a slate-grey collarless jacket over a camisole with trousers"]
        kept = ["a navy double-breasted flannel suit with a white shirt",
                "a beige ponte blazer over a crewneck with tailored trousers",
                "a burgundy peak-lapel jacket with a pencil skirt"]
        for outfit in dropped:
            self.assertEqual(self._accessory("silk pocket square", outfit), "no accessories")
        for outfit in kept:
            self.assertEqual(self._accessory("silk pocket square", outfit), "silk pocket square")

    def test_opera_gloves(self):
        self.assertEqual(self._accessory("long opera gloves",
                                         "a cream puff-sleeve smocked mini sundress",
                                         "vintage retro"), "no accessories")
        self.assertEqual(self._accessory("long opera gloves", "a black mermaid gown",
                                         "vintage retro"), "long opera gloves")
        self.assertEqual(self._accessory("long opera gloves", "a velvet wrap dress"),
                         "long opera gloves")


class GogglesNecklaceTests(unittest.TestCase):
    """Goggles plus a statement necklace drew a second pair at the neck (#01166)."""

    def test_goggles_drop_an_unlocked_necklace_only(self):
        outfit = "a stained white lab coat with cracked goggles pushed up on the forehead"
        resolved = {"outfit_description": outfit, "necklace": "statement necklace"}
        _fit_extras_to_garment(resolved, set())
        self.assertEqual(resolved["necklace"], "no necklace")
        resolved = {"outfit_description": outfit, "necklace": "statement necklace"}
        _fit_extras_to_garment(resolved, {"necklace"})
        self.assertEqual(resolved["necklace"], "statement necklace")


class MenswearEarringTests(unittest.TestCase):
    """Men drew earrings 15.5% of the time, a third of them diamond (#00989, #00990)."""

    def test_default_men_rarely_wear_studs_and_never_diamonds(self):
        worn = 0
        for seed in range(400):
            _, js = generate_character(seed, "Male", {})
            earrings = _flat(js).get("earrings", "no earrings")
            self.assertNotEqual(earrings, "diamond studs", seed)
            worn += earrings != "no earrings"
        self.assertLess(worn / 400, 0.10)


if __name__ == "__main__":
    unittest.main()
