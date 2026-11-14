"""Contracts every node class in ``nodes/`` keeps (2.6.0).

These were per-node tests (the Turnaround's tooltip check) or memory-only rules, and
the Outfit Sheet shipped in 2.3.0 with an auto-advancing ``outfit_seed`` and no cache
buster. Walking every module means a new node is covered without anyone listing it.
"""
from __future__ import annotations

import importlib
import inspect
import math
import pkgutil
import unittest

import nodes


def _node_classes():
    found = {}
    for info in pkgutil.iter_modules(nodes.__path__):
        module = importlib.import_module(f"nodes.{info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and "define_schema" in cls.__dict__:
                found[cls.__name__] = cls
    return found


class NodeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classes = _node_classes()

    def test_every_node_is_found(self):
        self.assertIn("IdentityForgeSceneSheet", self.classes)
        self.assertGreaterEqual(len(self.classes), 12)

    def test_every_input_and_output_carries_a_tooltip(self):
        for name, cls in self.classes.items():
            schema = cls.define_schema()
            for spec in schema.inputs:
                self.assertTrue((spec.tooltip or "").strip(), f"{name}.{spec.id}")
            for output in schema.outputs:
                self.assertTrue((output.tooltip or "").strip(),
                                f"{name} output {output.display_name}")

    def test_an_auto_advancing_widget_busts_the_cache(self):
        """ComfyUI#11905 can serve a cached result after a control_after_generate
        widget advances; such a node must define fingerprint_inputs (NaN when it
        matters, see the seeded nodes and Vault Load's random pick)."""
        for name, cls in self.classes.items():
            if any(getattr(spec, "control_after_generate", None)
                   for spec in cls.define_schema().inputs):
                self.assertIn("fingerprint_inputs", cls.__dict__, name)

    def test_outfit_sheet_and_a_random_vault_pick_always_rerun(self):
        self.assertTrue(math.isnan(
            self.classes["IdentityForgeOutfitSheet"].fingerprint_inputs(outfit_seed=3)))
        self.assertTrue(math.isnan(self.classes["IdentityForgeVaultLoad"].fingerprint_inputs(
            character="(random saved character)", seed=3)))


if __name__ == "__main__":
    unittest.main()
