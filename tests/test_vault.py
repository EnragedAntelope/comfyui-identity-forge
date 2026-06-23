"""Unit tests for the Identity Forge character vault (save / load / manage).

Pure-stdlib ``unittest`` so it runs without ComfyUI, torch or PIL installed:

    python -m unittest discover -s tests -v

The storage engine takes an explicit ``vault_root`` and an already-decoded
thumbnail, so these tests drive it against a throwaway temp directory with a tiny
PIL-like stub standing in for a real image.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nodes.identity_forge_vault_save import (
    _OVERWRITE, _KEEP_BOTH, _SKIP, _entry_dir, auto_name, describe_character,
    sanitize_name, save_character,
)
from nodes.identity_forge_vault_load import (
    delete_characters, list_character_names, list_characters, load_character,
    rename_character,
)

#: A resolved document like IdentityForge emits — cosplay label in _meta.
SAMPLE_JSON = json.dumps({
    "_meta": {"cosplay_of": "2B (NieR: Automata)", "gender": "Female"},
    "Body": {"body_type": "slender"},
    "_modifiers": {"footwear": "sci-fi"},
}, indent=2)

#: A random (non-cosplay) character with describable traits.
RICH_JSON = json.dumps({
    "_meta": {"gender": "Female"},
    "Demographics": {"age": "25"},
    "Hair": {"hair_color": "auburn"},
}, indent=2)


class _FakeImage:
    """Minimal stand-in for a PIL image (copy/thumbnail/save)."""

    def copy(self):
        return self

    def thumbnail(self, size):
        self.size = size

    def save(self, path):
        Path(path).write_bytes(b"\x89PNG\r\n")


class SanitizeTests(unittest.TestCase):
    def test_strips_illegal_and_separators(self):
        self.assertEqual(sanitize_name("a/b:c*?"), "a b c")

    def test_collapses_whitespace_and_trims_dots(self):
        self.assertEqual(sanitize_name("  hi   there.. "), "hi there")

    def test_rejects_traversal_and_empty(self):
        self.assertEqual(sanitize_name(".."), "")
        self.assertEqual(sanitize_name("///"), "")
        self.assertEqual(sanitize_name(""), "")


class DescribeTests(unittest.TestCase):
    def test_describe_from_traits(self):
        self.assertEqual(describe_character(RICH_JSON), "Woman, 25, auburn hair")

    def test_describe_too_sparse_returns_empty(self):
        only_gender = json.dumps({"_meta": {"gender": "Female"}})
        self.assertEqual(describe_character(only_gender), "")
        self.assertEqual(describe_character("not json"), "")


class AutoNameTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_label_wins(self):
        self.assertEqual(auto_name(self.root, SAMPLE_JSON), "2B (NieR Automata)")

    def test_description_when_no_label(self):
        self.assertEqual(auto_name(self.root, RICH_JSON), "Woman, 25, auburn hair")

    def test_sequential_fallback_counts_up(self):
        self.assertEqual(auto_name(self.root, "{}"), "Character 1")
        save_character(self.root, "Character 1", "{}")
        self.assertEqual(auto_name(self.root, "{}"), "Character 2")


class PathSafetyTests(unittest.TestCase):
    def test_traversal_is_neutralized_inside_root(self):
        # Separators/dots are stripped, so a traversal attempt collapses to a
        # plain name that stays a direct child of the vault root.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            entry = _entry_dir(root, "../evil")
            self.assertEqual(entry.parent, root)
            self.assertEqual(entry.name, "evil")

    def test_unusable_name_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                _entry_dir(Path(d), "..")


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_list_load_roundtrip_pristine(self):
        name = save_character(self.root, "2B", SAMPLE_JSON, "She wears…",
                              thumbnail=_FakeImage())
        self.assertEqual(name, "2B")
        self.assertEqual(list_character_names(self.root), ["2B"])

        loaded_json, prompt = load_character(self.root, "2B")
        self.assertEqual(loaded_json, SAMPLE_JSON)  # byte-for-byte pristine
        self.assertEqual(prompt, "She wears…")

        # Sidecar + preview were written, kept out of character.json.
        entry = self.root / "2B"
        self.assertTrue((entry / "preview.png").is_file())
        meta = json.loads((entry / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["source_label"], "2B (NieR: Automata)")

    def test_prompt_file_skipped_when_empty(self):
        save_character(self.root, "NoProse", SAMPLE_JSON)
        self.assertFalse((self.root / "NoProse" / "prompt.txt").exists())
        self.assertEqual(load_character(self.root, "NoProse")[1], "")

    def test_list_characters_metadata(self):
        save_character(self.root, "2B", SAMPLE_JSON)
        info = list_characters(self.root)
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]["name"], "2B")
        self.assertEqual(info[0]["source_label"], "2B (NieR: Automata)")
        self.assertFalse(info[0]["has_preview"])

    def test_on_existing_overwrite(self):
        save_character(self.root, "X", json.dumps({"a": 1}))
        save_character(self.root, "X", SAMPLE_JSON, on_existing=_OVERWRITE)
        self.assertEqual(list_character_names(self.root), ["X"])
        loaded, _ = load_character(self.root, "X")
        self.assertEqual(loaded, SAMPLE_JSON)

    def test_on_existing_keep_both_suffixes(self):
        save_character(self.root, "X", "{}")
        second = save_character(self.root, "X", "{}", on_existing=_KEEP_BOTH)
        self.assertEqual(second, "X-2")
        self.assertEqual(sorted(list_character_names(self.root)), ["X", "X-2"])

    def test_on_existing_skip(self):
        save_character(self.root, "X", json.dumps({"keep": True}))
        result = save_character(self.root, "X", "{}", on_existing=_SKIP)
        self.assertEqual(result, "X")
        loaded, _ = load_character(self.root, "X")
        self.assertEqual(json.loads(loaded), {"keep": True})

    def test_missing_load_is_noop(self):
        self.assertEqual(load_character(self.root, "ghost"), ("{}", ""))
        self.assertEqual(load_character(self.root, "../escape"), ("{}", ""))

    def test_delete(self):
        save_character(self.root, "A", "{}")
        save_character(self.root, "B", "{}")
        save_character(self.root, "C", "{}")
        survivors = delete_characters(self.root, ["A", "C", "missing"])
        self.assertEqual(survivors, ["B"])

    def test_rename(self):
        save_character(self.root, "Old", SAMPLE_JSON)
        final = rename_character(self.root, "Old", "New Name")
        self.assertEqual(final, "New Name")
        self.assertEqual(list_character_names(self.root), ["New Name"])
        meta = json.loads((self.root / "New Name" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["display_name"], "New Name")

    def test_rename_collision_and_missing(self):
        save_character(self.root, "A", "{}")
        save_character(self.root, "B", "{}")
        with self.assertRaises(ValueError):
            rename_character(self.root, "A", "B")
        with self.assertRaises(ValueError):
            rename_character(self.root, "ghost", "C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
