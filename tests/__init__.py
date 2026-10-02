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
    # 1.5.5: purge any partial `comfy_api` import before inserting the stub
    # path. A real (but broken/Pillow-less, or otherwise partially-imported)
    # `comfy_api` package reachable on sys.path from outside this repo -- a
    # stray editable install, a leftover venv, an earlier process in the same
    # interpreter -- lands in sys.modules on the failed `import` above and
    # Python then resolves `comfy_api.latest.io` from THAT cached partial
    # package for the rest of the process, never reaching the stub inserted
    # below. Every node class then silently fails to define (_COMFY_AVAILABLE
    # stays False), and every test that imports one fails with "cannot import
    # name 'IdentityForge'" -- a local-environment artifact that looks like a
    # severe regression but isn't one (real CI installs nothing, so there is
    # no real comfy_api to poison there). See docs/history.md -> the 1.1.0 CI
    # investigation for how this was found and confirmed to need this fix.
    for _name in [m for m in sys.modules if m == "comfy_api" or m.startswith("comfy_api.")]:
        del sys.modules[_name]
    _STUB_ROOT = Path(__file__).resolve().parent / "comfy_stub"
    sys.path.insert(0, str(_STUB_ROOT))
