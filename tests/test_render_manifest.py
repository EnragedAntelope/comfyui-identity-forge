"""Guard the gallery render gate in ``scripts/render_gallery.py``.

The gate's whole value rests on three properties, and each one has a way of
quietly breaking:

* ``--check`` passes on the committed tree. If it does not, either somebody
  edited an entry without re-rendering (which is the gate doing its job) or the
  manifest was seeded at the wrong moment (which is the gate lying).
* ``entry_hash`` is deterministic across processes and actually reacts to the
  text it claims to cover. A hash over the wrong thing still produces a stable
  hex string and looks entirely healthy.
* Importing the module is inert. It is imported by CI, which installs nothing
  and has no ComfyUI and no network, so any HTTP or node import at module scope
  would turn every CI run into a network call.
"""
from __future__ import annotations

import importlib
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import render_gallery  # noqa: E402


class CheckPassesTests(unittest.TestCase):
    def test_check_is_clean_on_the_committed_tree(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = render_gallery.main(["--check"])
        self.assertEqual(
            code, 0,
            "scripts/render_gallery.py --check is failing on the committed "
            "tree:\n" + buffer.getvalue(),
        )

    def test_the_manifest_covers_every_kind(self) -> None:
        manifest = render_gallery.load_manifest()
        self.assertEqual(manifest["schema_version"], render_gallery.MANIFEST_VERSION)
        for kind in render_gallery.KINDS:
            self.assertTrue(
                manifest["entries"].get(kind),
                f"the manifest has no entries recorded for {kind}",
            )

    def test_the_render_block_is_not_part_of_any_entry_record(self) -> None:
        # Deliberate: ~2,150 images predate this pipeline and were rendered
        # under settings nobody recorded, so folding render settings into the
        # per-entry hash would mark every one of them stale. If this ever
        # starts failing, read the note on entry_hash before "fixing" it.
        manifest = render_gallery.load_manifest()
        for kind, records in manifest["entries"].items():
            for name, record in records.items():
                self.assertEqual(
                    set(record) - {"hash", "rendered"}, set(),
                    f"{kind}/{name} records more than a hash and a date",
                )


class EntryHashTests(unittest.TestCase):
    def test_hash_is_stable_across_calls(self) -> None:
        first = render_gallery.entry_hash("cosplay", "2B")
        second = render_gallery.entry_hash("cosplay", "2B")
        self.assertEqual(first, second)

    def test_hash_changes_when_a_costume_string_changes(self) -> None:
        from data.cosplayers import COSPLAYERS

        name = "2B"
        before = render_gallery.entry_hash("cosplay", name)
        original = COSPLAYERS[name]["costume"]
        try:
            COSPLAYERS[name]["costume"] = original + " and a scarf"
            self.assertNotEqual(before, render_gallery.entry_hash("cosplay", name))
        finally:
            COSPLAYERS[name]["costume"] = original
        self.assertEqual(before, render_gallery.entry_hash("cosplay", name))

    def test_hash_covers_the_merged_archetype_costume(self) -> None:
        from data.templates import ARCHETYPES

        name = next(iter(ARCHETYPES))
        before = render_gallery.entry_hash("archetypes", name)
        entry = ARCHETYPES[name]
        entry["__probe__"] = "x"
        try:
            self.assertNotEqual(before, render_gallery.entry_hash("archetypes", name))
        finally:
            entry.pop("__probe__")

    def test_seed_is_deterministic_and_matches_the_recorded_formula(self) -> None:
        import hashlib

        name = "Jack Skellington"
        expected = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:15], 16)
        self.assertEqual(render_gallery.entry_seed(name), expected)
        self.assertEqual(
            render_gallery.load_manifest()["seed_formula"],
            render_gallery.SEED_FORMULA,
        )


class ImportIsInertTests(unittest.TestCase):
    """The module must import with no ComfyUI, no network and no side effects."""

    def test_importing_opens_no_socket(self) -> None:
        # A subprocess, because render_gallery is already imported in this one:
        # a module runs its top-level code once per process, so patching sockets
        # here would prove nothing about import time.
        probe = (
            "import socket, sys\n"
            "class Blocked(socket.socket):\n"
            "    def connect(self, *a, **k):\n"
            "        raise AssertionError('render_gallery opened a socket at import')\n"
            "socket.socket = Blocked\n"
            f"sys.path.insert(0, {str(ROOT)!r})\n"
            f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
            "import render_gallery\n"
            "assert 'comfy_api' not in sys.modules, 'ComfyUI imported at import time'\n"
            "print('ok')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok", result.stdout)

    def test_check_needs_no_comfyui(self) -> None:
        # survey() reads the data layer only. If a node module ever creeps into
        # that path, CI (which has no ComfyUI at all) is where it would surface.
        importlib.reload(render_gallery)
        results = render_gallery.survey()
        self.assertEqual(set(results), set(render_gallery.KINDS))

    def test_the_manifest_file_is_valid_json_with_a_trailing_newline(self) -> None:
        raw = render_gallery.MANIFEST.read_text(encoding="utf-8")
        self.assertTrue(raw.endswith("\n"))
        json.loads(raw)


if __name__ == "__main__":
    unittest.main()
