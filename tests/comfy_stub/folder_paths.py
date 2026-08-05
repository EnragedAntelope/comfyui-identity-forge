"""Minimal stand-in for ComfyUI's ``folder_paths`` module — used only when
the real ComfyUI is not installed (see ``tests/__init__.py``, which puts this
directory on ``sys.path`` only after the real ``comfy_api`` fails to import,
so a real ``folder_paths`` always wins when one is actually present).

Scope: just ``get_user_directory()``, the one function
``nodes/identity_forge_vault_load.py``'s ``_vault_root()`` calls. Returns a
fresh, empty temp directory on every call, so a script that builds a
Vault Load schema off of it (``scripts/dump_frontend_fixtures.py``) can never
read — or bake into a committed fixture — a real local vault's saved
character names. The ``character`` widget fixture always comes out as the
same clean "no characters saved" default a fresh install would show.
"""
from __future__ import annotations

import tempfile


def get_user_directory() -> str:
    return tempfile.mkdtemp(prefix="identity_forge_stub_user_")
