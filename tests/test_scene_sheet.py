"""Scene Sheet (2.6.0): one resolved character, a row of places."""
from __future__ import annotations

import json
import logging
import unittest
from unittest import mock

from data.constraints import lock_clash
from nodes import identity_forge_scene_sheet as scene
from nodes.identity_forge import FIELD_DEFINITIONS, run_identity_forge
from nodes.identity_forge_turnaround import _forge_class, _unwrap, document_fields, parse_document

_FACE = {name for name, field in FIELD_DEFINITIONS.items() if field.get("group") == "Face"}


class _Spy:
    """Records the resolved document of every view the sheet renders."""

    def __init__(self):
        self.forge = _forge_class()
        self.views: "list[tuple[str | None, dict]]" = []

    def execute(self, **kwargs):
        out = self.forge.execute(**kwargs)
        self.views.append((kwargs.get("location"),
                           document_fields(parse_document(_unwrap(out)[1]))))
        return out


def _run(document, sheet="Everyday (6)", clothes=scene._DRESS):
    spy = _Spy()
    with mock.patch.object(scene, "_forge_class", lambda: spy):
        prompts, labels = scene.resolve_scene_sheet(
            document, sheet, "Cowboy (mid-thigh up)", clothes)
    return prompts, labels, spy.views


class SceneSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)
        cls.characters = [run_identity_forge({"seed": seed})[1] for seed in range(8)]

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def _assert_coherent(self, views):
        for place, fields in views:
            self.assertEqual(fields["location"], place)
            for name, value in fields.items():
                if name != "location":
                    self.assertFalse(lock_clash("location", place, {name: value}),
                                     f"{place} vs {name}={value}")

    def test_dress_for_each_place(self):
        for document in self.characters:
            prompts, labels, views = _run(document)
            self.assertEqual(len(prompts), len(scene._SHEETS["Everyday (6)"]))
            self.assertEqual(labels[0], "1-sunny-city-park")
            self._assert_coherent(views)
            self.assertEqual(len({f.get("outfit_description") for _, f in views}), len(views))
            original = document_fields(parse_document(document))
            for _, fields in views:
                self.assertEqual({k: fields.get(k) for k in _FACE},
                                 {k: original.get(k) for k in _FACE})

    def test_keep_the_outfit_skips_places_that_refuse_it(self):
        skipped = 0
        for document in self.characters:
            outfit = document_fields(parse_document(document))["outfit_description"]
            prompts, _, views = _run(document, clothes=scene._KEEP_OUTFIT)
            if views and views[0][0] is not None:
                self._assert_coherent(views)
                self.assertEqual({f["outfit_description"] for _, f in views}, {outfit})
            skipped += len(scene._SHEETS["Everyday (6)"]) - len(prompts)
        self.assertGreater(skipped, 0, "no place refused any kept outfit")

    def test_a_cosplayer_keeps_the_costume(self):
        doc = json.loads(self.characters[0])
        doc["_meta"]["cosplay_of"] = "Test Hero"
        outfit = document_fields(doc)["outfit_description"]
        _, _, views = _run(json.dumps(doc))
        self.assertTrue(views)
        for place, fields in views:
            if place is not None:
                self.assertEqual(fields["outfit_description"], outfit)

    def test_malformed_input_emits_one_view(self):
        prompts, labels, _ = _run("not json")
        self.assertEqual(labels, ["1-as-resolved"])
        self.assertEqual(len(prompts), 1)

    def test_every_sheet_names_real_places(self):
        pool = set(FIELD_DEFINITIONS["location"]["female_options"])
        for name, places in scene._SHEETS.items():
            self.assertTrue(set(places) <= pool, name)
            self.assertIn(f"({len(places)})", name)


if __name__ == "__main__":
    unittest.main()
