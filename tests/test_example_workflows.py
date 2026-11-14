"""Example workflows stay loadable against the current node schemas (2.6.0).

``widgets_values`` is positional: a widget added, removed or reordered in a node's
``define_schema()`` shifts every later value in a saved workflow, and a combo option
that was renamed loads as an invalid value. Nothing caught that for the shipped
``example_workflows/`` until this test, which checks every pack node in them against
the committed frontend fixture (``tests/frontend/fixtures/nodes.json``, itself gated
against the live schemas by ``scripts/dump_frontend_fixtures.py --check``).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / "example_workflows").glob("*.json"))
FIXTURE = json.loads((ROOT / "tests" / "frontend" / "fixtures" / "nodes.json")
                     .read_text(encoding="utf-8"))

#: The Vault Load combo lists the user's own saved characters, so any name is valid.
_FREE_COMBOS = {("IdentityForgeVaultLoad", "character")}


class ExampleWorkflowWidgetTests(unittest.TestCase):
    def test_there_are_example_workflows(self):
        self.assertTrue(WORKFLOWS)

    def test_pack_nodes_match_the_schema(self):
        for path in WORKFLOWS:
            workflow = json.loads(path.read_text(encoding="utf-8"))
            for node in workflow["nodes"]:
                widgets = FIXTURE.get(node["type"])
                if widgets is None:
                    self.assertFalse(node["type"].startswith("IdentityForge"),
                                     f"{path.name}: {node['type']} missing from the fixture")
                    continue
                values = node.get("widgets_values") or []
                with self.subTest(workflow=path.name, node=node["id"]):
                    self.assertEqual(len(values), len(widgets),
                                     f"{node['type']}: widget count changed")
                    for widget, value in zip(widgets, values):
                        if widget["type"] != "combo" or (node["type"], widget["name"]) in _FREE_COMBOS:
                            continue
                        self.assertIn(value, widget["options"],
                                      f"{node['type']}.{widget['name']}")


if __name__ == "__main__":
    unittest.main()
