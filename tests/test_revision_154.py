"""1.5.4: regressions from the second idforge-929-concern render batch."""
import unittest

from data.cosplayers import COSPLAYERS
from nodes.identity_forge import _LOWER_FACE_COVER_RE, generate_character
from nodes.identity_forge_cosplayer import _body_paint_skin_color
from tests.preview_cosplayer import render

_MASKED_COSTUMES = ("Sub-Zero", "Kakashi Hatake", "Ibuki", "Ken Kaneki", "Nezuko Kamado", "Kitana")


class LowerFaceMaskHidesTheJawTests(unittest.TestCase):
    """The jaw and chin were still voiced under a mask, so the model drew a bare jaw."""

    def test_no_jaw_or_chin_under_a_lower_face_mask(self):
        for name in _MASKED_COSTUMES:
            for seed in range(6):
                prose, _ = render(name, "", "Costume only", seed)
                # The face-structure sentence only: poses ("resting chin on one hand") and
                # makeup ("jawline contour") legitimately mention the chin or jaw.
                face = next((s for s in prose.split(". ") if " face is " in s or " face has " in s), "")
                self.assertNotRegex(face, r"\bjawline\b|\bchin\b", f"{name} {seed}")

    def test_a_widget_lock_still_voices_the_chin(self):
        prose, _ = generate_character(1, "Male", {"outfit_description": "a mask covering the mouth",
                                                  "chin": "cleft chin"},
                                      widget_locked=frozenset({"chin"}))
        self.assertIn("chin", prose)

    def test_every_reworded_mask_costume_matches_the_regex(self):
        for name in _MASKED_COSTUMES:
            entry = COSPLAYERS[name]
            looks = [entry["costume"]] + [a if isinstance(a, str) else a["costume"]
                                          for a in entry.get("costumes", [])]
            self.assertTrue(any(_LOWER_FACE_COVER_RE.search(t) for t in looks), name)
        silk = COSPLAYERS["Silk"]["costumes"][0]
        self.assertRegex(silk, _LOWER_FACE_COVER_RE)


class MaterialAnchorTests(unittest.TestCase):
    """Beast was blue SKIN under a blue fur COAT; the anchor now keeps the material."""

    def test_anchor_keeps_fur_scale_and_hide(self):
        for name, expect in (("Beast (X-Men)", "blue fur"), ("Sonic the Hedgehog", "bright blue fur")):
            entry = COSPLAYERS[name]
            self.assertEqual(_body_paint_skin_color(entry, entry["costume"]), expect)

    def test_anchor_still_drops_a_skin_noun(self):
        hulk = COSPLAYERS["Hulk"]
        self.assertEqual(_body_paint_skin_color(hulk, hulk["costume"]), "rich green")

    def test_beast_prose_says_fur_not_skin(self):
        for seed in range(6):
            prose, _ = render("Beast (X-Men)", "", "Costume only", seed)
            self.assertIn("blue fur", prose)
            self.assertNotIn("blue skin", prose)

    def test_hulk_still_says_skin(self):
        prose, _ = render("Hulk", "", "Costume only", 1)
        self.assertIn("rich green skin", prose)


class MaskWordingTests(unittest.TestCase):
    def test_daredevil_cowl_has_no_lenses(self):
        entry = COSPLAYERS["Daredevil"]
        self.assertNotIn("lens", entry["mask"].lower())
        self.assertNotIn("lens", entry["costume"].lower())

    def test_masks_lead_the_costume(self):
        for name in ("Sub-Zero", "Kakashi Hatake", "Ibuki", "Ken Kaneki", "Nezuko Kamado"):
            self.assertRegex(COSPLAYERS[name]["costume"].split(",")[0], r"mask|muzzle", name)

    def test_ewoks_are_named_ewoks(self):
        self.assertIn("Ewok", COSPLAYERS["Chief Chirpa"]["mask"])
        self.assertIn("Ewok", COSPLAYERS["Wicket the Ewok"]["mask"])


if __name__ == "__main__":
    unittest.main()
