"""Runs before every ``tests/test_*.py`` module — but only under
``python -m unittest discover -s tests -t . -v`` (the ``-t .`` makes
``tests`` a genuine subpackage of the repo root, which is what makes
Python's import system guarantee this file runs before its children;
without it, ``discover`` imports test files as bare top-level modules and
this package ``__init__`` never runs first).

Registers the ``comfy_api.latest.io`` stub *before* any test module can
import a node module — a module runs its top-level code once per process,
so if ``nodes.identity_forge`` (or any other node module) were imported
first, its own ``_COMFY_AVAILABLE`` would be permanently ``False`` for the
rest of the run and registering the stub afterward could not undo it.

Real-first, stub-fallback: on a machine with ComfyUI installed, the real
``comfy_api`` wins and this stub is never touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import comfy_api.latest.io  # noqa: F401
except ImportError:
    _STUB_ROOT = Path(__file__).resolve().parent / "comfy_stub"
    sys.path.insert(0, str(_STUB_ROOT))
