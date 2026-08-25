"""Guard against drift between ``tests/frontend/fixtures/nodes.json`` and the
live ``define_schema()`` output it's generated from.

Mirrors ``tests/test_js_sync.py``'s job for the other generated frontend data
block. A generated file that only gets checked by regenerating and diffing
against itself (``--check``) is a real guard, but it only runs when someone
remembers to invoke it directly; wiring the same rebuild-and-diff into a
regular test means it runs on every plain ``unittest discover`` too, so a
schema change that forgets to regenerate the fixture fails the suite, not
just a separate CI step someone could skip locally.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_SCRIPT_PATH = ROOT / "scripts" / "dump_frontend_fixtures.py"
_FIXTURE_PATH = ROOT / "tests" / "frontend" / "fixtures" / "nodes.json"

_spec = importlib.util.spec_from_file_location("dump_frontend_fixtures", _SCRIPT_PATH)
_dump_frontend_fixtures = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dump_frontend_fixtures)


class FrontendFixtureInSync(unittest.TestCase):
    def test_fixture_matches_live_schema(self) -> None:
        live = _dump_frontend_fixtures.build_fixture()
        # The fixture is defined against an EMPTY vault, because that is what CI
        # (dependency-free, stub `folder_paths`) sees. Run on a maintainer's box
        # with a real ComfyUI on sys.path, `IdentityForgeVaultLoad` instead lists
        # their actual saved characters, so this test failed and told them to
        # "regenerate" -- which would have committed those private names. Skip
        # instead: the fixture is not stale, the vault is simply not empty.
        try:
            _dump_frontend_fixtures._assert_no_private_data(live)
        except SystemExit:
            self.skipTest(
                "a populated local vault is on sys.path, so live define_schema() "
                "output is machine-specific; the committed fixture is generated "
                "against an empty vault (see dump_frontend_fixtures guard)"
            )
        expected = json.dumps(live, indent=2) + "\n"
        actual = _FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertEqual(
            actual, expected,
            "tests/frontend/fixtures/nodes.json is out of sync with live "
            "define_schema() output — regenerate with "
            "`python scripts/dump_frontend_fixtures.py`.",
        )


if __name__ == "__main__":
    unittest.main()
