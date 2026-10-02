"""Unit tests for the Identity Forge character vault (save / load / manage).

Pure-stdlib ``unittest`` so it runs without ComfyUI, torch or PIL installed:

    python -m unittest discover -s tests -t . -v

The storage engine takes an explicit ``vault_root`` and an already-decoded
thumbnail, so these tests drive it against a throwaway temp directory with a tiny
PIL-like stub standing in for a real image.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nodes.identity_forge_vault_save import (
    _OVERWRITE, _KEEP_BOTH, _SKIP, _entry_dir, auto_name, describe_character,
    sanitize_name, save_character,
)
from nodes.identity_forge_vault_load import (
    _character_fingerprint, _NO_FINGERPRINT, delete_characters,
    list_character_names, list_characters, load_character, rename_character,
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

#: A non-blank placeholder for tests that don't care about content, only that a
#: save succeeds. 1.5.5: save_character refuses a literal "{}" (blank), so these
#: fixtures need SOMETHING in the document.
BLANK_OK_JSON = '{"Body": {}}'


class _FakeImage:
    """Minimal stand-in for a PIL image (copy/thumbnail/save)."""

    def copy(self):
        return self

    def thumbnail(self, size):
        self.size = size

    def save(self, path):
        Path(path).write_bytes(b"\x89PNG\r\n")


class _FailingImage(_FakeImage):
    """Fails partway through a save, to test the overwrite-failure path."""

    def save(self, path):
        raise OSError("disk full (simulated)")


class SanitizeTests(unittest.TestCase):
    def test_strips_illegal_and_separators(self):
        self.assertEqual(sanitize_name("a/b:c*?"), "a b c")

    def test_collapses_whitespace_and_trims_dots(self):
        self.assertEqual(sanitize_name("  hi   there.. "), "hi there")

    def test_rejects_traversal_and_empty(self):
        self.assertEqual(sanitize_name(".."), "")
        self.assertEqual(sanitize_name("///"), "")
        self.assertEqual(sanitize_name(""), "")

    def test_windows_reserved_device_names_are_suffixed(self):
        # 1.5.5: a folder named exactly one of these targets a special Windows
        # device file, not an ordinary folder -- confirmed on a Windows dev box.
        # Reserved regardless of case or any extension that follows.
        self.assertEqual(sanitize_name("NUL"), "NUL_")
        self.assertEqual(sanitize_name("nul"), "nul_")
        self.assertEqual(sanitize_name("CON"), "CON_")
        self.assertEqual(sanitize_name("com1"), "com1_")
        self.assertEqual(sanitize_name("lpt9"), "lpt9_")
        self.assertEqual(sanitize_name("NUL.txt"), "NUL.txt_")
        # Not reserved: a prefix/suffix match, or a non-reserved device number.
        self.assertEqual(sanitize_name("NULL"), "NULL")
        self.assertEqual(sanitize_name("COM10"), "COM10")
        self.assertEqual(sanitize_name("My CON Report"), "My CON Report")


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
        save_character(self.root, "Character 1", BLANK_OK_JSON)
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

    def test_blank_character_json_is_refused(self):
        with self.assertRaises(ValueError):
            save_character(self.root, "X", "{}")
        with self.assertRaises(ValueError):
            save_character(self.root, "X", "")
        with self.assertRaises(ValueError):
            save_character(self.root, "X", "  {}  ")
        self.assertEqual(list_character_names(self.root), [])

    def test_a_failed_overwrite_leaves_the_old_save_intact(self):
        # 1.5.5: overwriting used to rmtree the old entry BEFORE writing the new
        # one, so a write failure partway through silently lost the old save.
        # Uses its own private vault_root (a subdir of self.root) so the staging
        # dir -- built as a SIBLING of vault_root -- stays inside the test's own
        # temp dir rather than the shared OS temp dir.
        vault_parent = self.root
        root = vault_parent / "characters"
        root.mkdir()
        save_character(root, "X", SAMPLE_JSON)
        with self.assertRaises(OSError):
            save_character(root, "X", RICH_JSON, on_existing=_OVERWRITE,
                           thumbnail=_FailingImage())
        self.assertEqual(list_character_names(root), ["X"])
        loaded, _ = load_character(root, "X")
        self.assertEqual(loaded, SAMPLE_JSON, "the old save should survive the failure")
        # No leftover staging dir (sibling of root) or backup dir (inside root).
        self.assertEqual([p.name for p in vault_parent.iterdir()], ["characters"])
        self.assertEqual([p.name for p in root.iterdir()], ["X"])

    def test_on_existing_keep_both_suffixes(self):
        save_character(self.root, "X", BLANK_OK_JSON)
        second = save_character(self.root, "X", BLANK_OK_JSON, on_existing=_KEEP_BOTH)
        self.assertEqual(second, "X-2")
        self.assertEqual(sorted(list_character_names(self.root)), ["X", "X-2"])

    def test_on_existing_skip(self):
        save_character(self.root, "X", json.dumps({"keep": True}))
        result = save_character(self.root, "X", BLANK_OK_JSON, on_existing=_SKIP)
        self.assertEqual(result, "X")
        loaded, _ = load_character(self.root, "X")
        self.assertEqual(json.loads(loaded), {"keep": True})

    def test_missing_load_is_noop(self):
        self.assertEqual(load_character(self.root, "ghost"), ("{}", ""))
        self.assertEqual(load_character(self.root, "../escape"), ("{}", ""))

    def test_delete(self):
        save_character(self.root, "A", BLANK_OK_JSON)
        save_character(self.root, "B", BLANK_OK_JSON)
        save_character(self.root, "C", BLANK_OK_JSON)
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
        save_character(self.root, "A", BLANK_OK_JSON)
        save_character(self.root, "B", BLANK_OK_JSON)
        with self.assertRaises(ValueError):
            rename_character(self.root, "A", "B")
        with self.assertRaises(ValueError):
            rename_character(self.root, "ghost", "C")



class VaultRecallControlDeferralTests(unittest.TestCase):
    """Regression for the 0.99.0 wardrobe/hair_color_scope recall hole.

    A character saved with wardrobe='Any' (and/or a full-spectrum hair colour)
    rebuilt a *different* person on Vault Load, because IdentityForge read the
    control values from its own widgets (default 'Match gender' / 'Natural only')
    and ignored the saved _meta. The fix adds an 'Auto (preset)' sentinel to
    both widgets: set it and recall honours the saved controls.
    """

    def _generate(self, seed, gender, wardrobe, hair_color_scope):
        from nodes.identity_forge import IdentityForge
        out = IdentityForge.execute(
            seed=seed, gender=gender, wardrobe=wardrobe,
            hair_color_scope=hair_color_scope,
        )
        return out.args[1]

    def _recall(self, saved_json, seed, wardrobe, hair_color_scope, gender="Any"):
        from nodes.identity_forge import IdentityForge
        out = IdentityForge.execute(
            seed=seed, archetype_json=saved_json, gender=gender,
            wardrobe=wardrobe, hair_color_scope=hair_color_scope,
        )
        return out.args[1]

    def test_recall_with_auto_preset_is_faithful(self):
        original = self._generate(12345, "Any", "Any", "Full spectrum")
        recalled = self._recall(original, 12345, "Auto (preset)", "Auto (preset)")
        orig = json.loads(original)
        rec = json.loads(recalled)
        # The saved control values are honoured: the recalled _meta matches.
        self.assertEqual(rec["_meta"], orig["_meta"])
        # The composed outfit (the authoritative description of the person)
        # is identical, so the recalled character is the same person.
        self.assertEqual(
            rec["Clothing"]["outfit_description"],
            orig["Clothing"]["outfit_description"],
        )
        # The whole document matches once the four raw garment fields that the
        # engine intentionally supersedes with outfit_description are ignored
        # (a pre-existing, wardrobe-orthogonal round-trip detail: on generation
        # outfit_description starts absent so they are kept; on recall it is
        # locked so they are popped). The person is otherwise identical.
        _GARMENT_FIELDS = ("outfit_style", "footwear", "clothing_color",
                           "clothing_pattern")
        def _drop_garment(doc):
            return {
                g: {k: v for k, v in fields.items() if k not in _GARMENT_FIELDS}
                for g, fields in doc.items()
            }
        self.assertEqual(_drop_garment(rec), _drop_garment(orig))

    def test_recall_with_default_widgets_diverges(self):
        original = self._generate(12345, "Any", "Any", "Full spectrum")
        recalled = self._recall(original, 12345, "Match gender", "Natural only")
        self.assertNotEqual(json.loads(recalled), json.loads(original))

    def test_parse_archetype_exposes_control_meta(self):
        from nodes.identity_forge import (
            _parse_archetype_json, _WARDROBE_KEY, _HAIR_COLOR_SCOPE_KEY,
        )
        doc = json.dumps({
            "_meta": {"gender": "Any", "wardrobe": "Any",
                      "hair_color_scope": "Full spectrum"},
            "Hair": {"hair_color": "hot pink"},
        })
        parsed = _parse_archetype_json(doc)
        self.assertEqual(parsed.get(_WARDROBE_KEY), "Any")
        self.assertEqual(parsed.get(_HAIR_COLOR_SCOPE_KEY), "Full spectrum")

    def test_auto_preset_without_archetype_falls_back(self):
        # No wired character: 'Auto (preset)' must not leak the sentinel into
        # the engine, and must fall back to the widget defaults.
        from nodes.identity_forge import IdentityForge
        out = IdentityForge.execute(
            seed=7, gender="Female", wardrobe="Auto (preset)",
            hair_color_scope="Auto (preset)",
        )
        recalled = json.loads(out.args[1])
        self.assertEqual(recalled["_meta"]["wardrobe"], "Match gender")
        self.assertEqual(recalled["_meta"]["hair_color_scope"], "Natural only")


class MalformedEntryTests(unittest.TestCase):
    """1.5.5: a hand-edited or racily-written entry must degrade, never crash."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_non_dict_meta_json_does_not_crash_listing(self):
        save_character(self.root, "X", SAMPLE_JSON)
        (self.root / "X" / "meta.json").write_text("null", encoding="utf-8")
        info = list_characters(self.root)  # used to raise AttributeError
        self.assertEqual(info[0]["name"], "X")
        self.assertEqual(info[0]["source_label"], "2B (NieR: Automata)",
                         "should fall back to character.json's own _meta")

    def test_non_dict_top_level_meta_in_character_json(self):
        # _source_label: the top-level document IS a dict, but its "_meta"
        # VALUE is not. The `.get("_meta", {})` lookup is inside the try either
        # way; this exercises the branch that used to be outside it.
        from nodes.identity_forge_vault_save import _source_label
        self.assertEqual(_source_label(json.dumps({"_meta": "oops"})), "")

    def test_unreadable_character_json_is_a_noop_not_a_crash(self):
        save_character(self.root, "X", SAMPLE_JSON)
        (self.root / "X" / "character.json").write_bytes(b"\xff\xfe\x00\xff")
        self.assertEqual(load_character(self.root, "X"), ("{}", ""))

    def test_delete_only_removes_a_real_entry(self):
        # A directory that sanitizes to a requested name but holds no
        # character.json (never a real save) must survive a delete call.
        decoy = self.root / "decoy"
        decoy.mkdir()
        (decoy / "not_a_character.txt").write_text("x", encoding="utf-8")
        save_character(self.root, "real", SAMPLE_JSON)
        survivors = delete_characters(self.root, ["decoy", "real"])
        self.assertEqual(survivors, [])  # "real" deleted as asked
        self.assertTrue(decoy.is_dir(), "the non-entry directory must survive")


class FingerprintTests(unittest.TestCase):
    """1.5.5: Vault Load's cache key must track the FILE, not just the widget."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_no_selection_or_missing_entry_is_the_stable_sentinel(self):
        self.assertEqual(_character_fingerprint(self.root, "(no characters saved)"),
                         _NO_FINGERPRINT)
        self.assertEqual(_character_fingerprint(self.root, "ghost"), _NO_FINGERPRINT)

    def test_unchanged_file_gives_the_same_fingerprint(self):
        save_character(self.root, "X", SAMPLE_JSON)
        self.assertEqual(_character_fingerprint(self.root, "X"),
                         _character_fingerprint(self.root, "X"))

    def test_an_overwrite_changes_the_fingerprint(self):
        save_character(self.root, "X", SAMPLE_JSON)
        before = _character_fingerprint(self.root, "X")
        save_character(self.root, "X", RICH_JSON, on_existing=_OVERWRITE)
        after = _character_fingerprint(self.root, "X")
        self.assertNotEqual(before, after,
                            "an overwritten entry must invalidate the node's cache")

    def test_a_delete_changes_the_fingerprint(self):
        save_character(self.root, "X", SAMPLE_JSON)
        before = _character_fingerprint(self.root, "X")
        delete_characters(self.root, ["X"])
        after = _character_fingerprint(self.root, "X")
        self.assertNotEqual(before, after)
        self.assertEqual(after, _NO_FINGERPRINT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
