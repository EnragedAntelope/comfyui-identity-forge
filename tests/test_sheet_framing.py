"""2.6.0: a sheet that pins a framing releases what the framing refuses.

Before 2.6.0 the Expression Sheet pinned a close-up and kept "standing with arms crossed",
and the one-view paths of the Age Progression and Outfit Sheet did the same. Every path
now goes through ``pin_framing``.
"""
from __future__ import annotations

import json
import logging
import unittest

from data.constraints import lock_clash
from nodes.identity_forge import run_identity_forge
from nodes.identity_forge_age_progression import resolve_age_progression
from nodes.identity_forge_expression_sheet import resolve_expression_sheet
from nodes.identity_forge_outfit_sheet import resolve_outfit_sheet
from nodes.identity_forge_turnaround import _FRAMINGS, document_fields, parse_document

_CLOSE_UP = "Head and shoulders"


def _clashing_characters(count: int):
    """Documents whose own values include something a close-up refuses."""
    framing = _FRAMINGS[_CLOSE_UP]
    found = []
    for seed in range(200):
        _, document, _ = run_identity_forge({"seed": seed, "shot_type": "full body shot"})
        fields = document_fields(parse_document(document))
        refused = {value for name, value in fields.items()
                   if lock_clash("shot_type", framing, {name: value})}
        if refused:
            found.append((seed, document, refused))
        if len(found) == count:
            return found
    raise AssertionError("no seed draws a value a close-up refuses")


def _with_meta(document: str, **meta) -> str:
    doc = json.loads(document)
    doc["_meta"].update(meta)
    return json.dumps(doc)


class SheetFramingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)
        cls.characters = _clashing_characters(6)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def _assert_released(self, prompts, refused, seed):
        for prompt in prompts:
            for value in refused:
                self.assertNotIn(value, prompt, f"seed {seed}")

    def test_expression_sheet(self):
        for seed, document, refused in self.characters:
            prompts, _ = resolve_expression_sheet(document, "Smiles (3)", _CLOSE_UP)
            self._assert_released(prompts, refused, seed)

    def test_age_progression_one_view_path(self):
        for seed, document, refused in self.characters:
            prompts, labels = resolve_age_progression(
                _with_meta(document, covers_face=True), "Life stages (4)", _CLOSE_UP)
            self.assertEqual(labels, ["1-as-resolved"])
            self._assert_released(prompts, refused, seed)

    def test_outfit_sheet_one_view_path(self):
        for seed, document, refused in self.characters:
            prompts, labels = resolve_outfit_sheet(
                _with_meta(document, covers_body=True), "Range (6)",
                "Keep the character's scene", _CLOSE_UP, "Keep the character's pose")
            self.assertEqual(labels, ["1-as-resolved"])
            self._assert_released(prompts, refused, seed)

    def test_released_pose_differs_between_characters(self):
        # The replacement is drawn per character, not from one shared replay seed.
        poses = set()
        for _, document, _ in self.characters:
            prompts, _ = resolve_expression_sheet(document, "Smiles (3)", _CLOSE_UP)
            poses.add(prompts[0].split(". Set in")[0][-80:])
        self.assertGreater(len(poses), 1)


if __name__ == "__main__":
    unittest.main()
