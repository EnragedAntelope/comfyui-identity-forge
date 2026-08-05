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
        expected = json.dumps(_dump_frontend_fixtures.build_fixture(), indent=2) + "\n"
        actual = _FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertEqual(
            actual, expected,
            "tests/frontend/fixtures/nodes.json is out of sync with live "
            "define_schema() output — regenerate with "
            "`python scripts/dump_frontend_fixtures.py`.",
        )


if __name__ == "__main__":
    unittest.main()
