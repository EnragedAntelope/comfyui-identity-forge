"""Registers the comfy_api stub before pytest collects any test module.

``python -m unittest discover -s tests -t .`` gets this ordering from
``tests/__init__.py``, because ``-t .`` makes ``tests`` a genuine subpackage
whose ``__init__`` Python must run first. pytest has no equivalent guarantee,
so it could import a node module with ``_COMFY_AVAILABLE`` permanently
``False`` -- a contributor running the natural-feeling command got a silently
different suite. A rootdir ``conftest.py`` is imported before collection
begins, which is the same guarantee by a different route.

**Real-first, stub-fallback**, identical to ``tests/__init__.py``: with ComfyUI
installed the real ``comfy_api`` wins and the stub is never touched. Both files
are kept because they cover different runners, not because either is redundant.

``python -m unittest discover -s tests -t .`` remains the documented command
and the CI entry point -- it is what guarantees the pack stays dependency-free.
This file makes ``pytest`` *correct*; it does not make it *the* command.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent

# The repo root must be importable for `data.*` / `nodes.*` to resolve, and for
# pytest's own import of the root package (which is what surfaced the missing
# `ComfyExtension` in the stub).
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:  # pragma: no cover -- taken on a machine with ComfyUI installed
    import comfy_api.latest.io  # noqa: F401
except ImportError:
    sys.path.insert(0, str(_ROOT / "tests" / "comfy_stub"))
