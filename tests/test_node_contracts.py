"""Contracts every node class in ``nodes/`` keeps (2.6.0).

These were per-node tests (the Turnaround's tooltip check) or memory-only rules.
Walking every module means a new node is covered without anyone listing it.
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

    def test_no_node_returns_a_nan_fingerprint(self):
        """2.7.1: NaN never equals itself, and ComfyUI folds every ancestor's
        fingerprint into a node's cache key, so one NaN re-runs the whole graph
        downstream (sampler included) every queue. A seed is already in the key."""
        for name, cls in self.classes.items():
            if "fingerprint_inputs" in cls.__dict__:
                value = cls.fingerprint_inputs(character="(random saved character)", seed=3)
                self.assertFalse(isinstance(value, float) and math.isnan(value), name)


if __name__ == "__main__":
    unittest.main()
