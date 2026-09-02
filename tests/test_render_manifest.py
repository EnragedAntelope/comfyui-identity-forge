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
import re
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
                    set(record) - {"hash", "rendered", "seed"}, set(),
                    f"{kind}/{name} records more than a hash, a date and an "
                    f"optional re-rolled seed",
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


class GalleryShotPoolTests(unittest.TestCase):
    """Regression: ``_gallery_shot`` must always pin a real camera angle.

    ``shot_type``'s option list carries "Random" (its control value) and
    "None" (its omit sentinel) alongside actual framings. The pool filter
    excluded "Random" but not "None" -- so on the seeds that landed on it,
    the gallery render passed shot_type="None" into IdentityForge.execute,
    which (a non-Random widget value always beats a preset lock) silently
    discarded whatever shot_type the archetype/cosplayer itself locked,
    with no framing at all. Caught via ``Kendo Practitioner`` (locked to
    "full body shot") rendering as an extreme close-up twice in a row.
    """

    def test_never_returns_the_omit_sentinel_or_control_value(self) -> None:
        for seed in range(500):
            shot = render_gallery._gallery_shot(seed)
            self.assertNotEqual(shot, "None", f"seed {seed} picked the omit sentinel")
            self.assertNotEqual(shot, "Random", f"seed {seed} picked the control value")
            self.assertNotIn(shot, render_gallery._BACK_FACING_SHOTS,
                              f"seed {seed} picked a back-facing shot")


class RuntimeLoggingTests(unittest.TestCase):
    """1.2.0: node runtime messages go to `logging`, not stdout.

    Only the RUNTIME modules were converted (`nodes/*.py` and the entrypoint,
    18 call sites). `scripts/` and `gallery/` are CLI tools where `print` IS the
    output, and `data/user_options.py` prints at import time on behalf of those
    same CLIs -- both deliberately left alone, so this test is scoped to the
    runtime tree rather than the whole repo.

    No handler and no `basicConfig()` is configured anywhere in the pack:
    ComfyUI owns root logging, and a library that grabs it is a library that
    fights its host.
    """

    _RUNTIME = ("nodes", "__init__.py")

    def _runtime_files(self):
        root = Path(__file__).resolve().parents[1]
        files = [root / "__init__.py"]
        files += sorted((root / "nodes").glob("*.py"))
        return files

    def test_no_print_remains_in_the_runtime_tree(self):
        offenders = []
        for path in self._runtime_files():
            for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"(?<![\w.])print\s*\(", line):
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [], "use _LOG.<level>(...) in runtime code; "
                                        "print is for the scripts/ CLIs")

    def test_every_runtime_module_that_logs_has_its_own_logger(self):
        for path in self._runtime_files():
            text = path.read_text(encoding="utf-8")
            if "_LOG." not in text:
                continue
            with self.subTest(module=path.name):
                self.assertIn("_LOG = logging.getLogger(__name__)", text)
                self.assertIn("\nimport logging\n", text)

    def test_the_pack_never_configures_root_logging(self):
        # ComfyUI owns it; a handler or a basicConfig() call here hijacks the
        # host. COMMENTS ARE STRIPPED FIRST: every module carries a comment
        # explaining that it makes no such call, and a naive substring scan
        # matches that explanation -- the check has to read code, not prose.
        for path in self._runtime_files():
            code = "\n".join(
                line for line in path.read_text(encoding="utf-8").splitlines()
                if not line.lstrip().startswith(("#", "#:")))
            with self.subTest(module=path.name):
                self.assertNotIn("basicConfig", code)
                self.assertNotIn("addHandler", code)
                self.assertNotIn("logging.getLogger()", code)  # never the root

    def test_messages_dropped_the_bracket_prefix(self):
        # The logger name carries it now; keeping both double-prints it.
        for path in self._runtime_files():
            text = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertNotIn("[IdentityForge]", text)
                self.assertNotIn("[IdentityForgeCosplayer]", text)


class StubRegistrationTests(unittest.TestCase):
    """1.2.0: `pytest` works, and the stub covers the entrypoint too.

    Two independent things had to be true and only the first was:

    * the stub has to be registered before any node module is imported --
      `tests/__init__.py` gets that from `-t .` under unittest, and the rootdir
      `conftest.py` gets it under pytest; and
    * the stub has to export everything the pack imports from `comfy_api`.
      It did not. The repo-root `__init__.py` does
      `from comfy_api.latest import ComfyExtension, io`, and the stub package
      was empty, so `pytest` failed all 772 tests with
      `ImportError: cannot import name 'ComfyExtension'`. unittest never
      imported the root package, so the gap was invisible there.
    """

    def test_comfy_api_resolves(self):
        import comfy_api.latest  # noqa: F401
        from comfy_api.latest import io  # noqa: F401
        self.assertTrue(hasattr(io, "ComfyNode"))

    def test_the_entrypoints_import_surface_exists(self):
        # Exactly the import the repo-root __init__.py performs.
        from comfy_api.latest import ComfyExtension, io  # noqa: F401
        self.assertTrue(callable(getattr(ComfyExtension, "get_node_list", None)))

    def test_node_modules_saw_the_api(self):
        # The ordering guarantee itself: if the stub had been registered late,
        # this would be False for the rest of the process.
        from nodes.identity_forge import _COMFY_AVAILABLE
        self.assertTrue(_COMFY_AVAILABLE,
                        "a node module was imported before the comfy_api stub "
                        "was registered -- check conftest.py / tests/__init__.py")

    def test_a_rootdir_conftest_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "conftest.py").is_file(),
                        "the rootdir conftest.py is what makes pytest correct")


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
