#!/usr/bin/env python
"""Generate ``tests/frontend/fixtures/nodes.json`` from live ``define_schema()``.

The jsdom frontend tests (``tests/frontend/*.test.mjs``) need to know, for each
node, the widgets a real ComfyUI would build and the order they'd appear in —
without that, a test asserting "every field lands in the right group" would be
checking a hand-typed list against another hand-typed list, proving nothing
about the actual Python schema. This script derives that list from the real
``io.ComfyNode.define_schema()`` output (using the ``comfy_api`` stub in
``tests/comfy_stub`` when no real ComfyUI is installed — see
``tests/__init__.py``), so a Python schema change that isn't matched on the
JS side shows up as a stale fixture, not a passing test that means nothing.

Widget vs. link-only socket: an ``Input`` with no ``default`` attribute (only
``Image.Input`` in this pack) is a pure socket, never a widget. A
``WidgetInput`` whose ``force_input`` is set is *also* a pure socket — that's
how ``archetype_json`` / ``upstream`` / ``prompt_json`` become connectable
sockets instead of text boxes on the node face (see each node's own comment
at the call site). Everything else becomes one ``widgets_values`` entry, in
schema-list order; an ``Int.Input`` with a truthy ``control_after_generate``
contributes a second, synthetic sibling widget of that name, exactly as
ComfyUI's own frontend auto-adds one next to a seed.

Usage (from the repo root)::

    python scripts/dump_frontend_fixtures.py            # write the fixture
    python scripts/dump_frontend_fixtures.py --check    # fail if out of date (CI)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests  # noqa: E402,F401 — side effect only: registers the comfy_api stub

from nodes.identity_forge import IdentityForge  # noqa: E402
from nodes.identity_forge_archetype import IdentityForgeArchetype  # noqa: E402
from nodes.identity_forge_cosplayer import IdentityForgeCosplayer  # noqa: E402
from nodes.identity_forge_creature import IdentityForgeCreature  # noqa: E402
from nodes.identity_forge_modifier import IdentityForgeModifier  # noqa: E402
from nodes.identity_forge_turnaround import IdentityForgeTurnaround  # noqa: E402
from nodes.identity_forge_vault_load import IdentityForgeVaultLoad  # noqa: E402
from nodes.identity_forge_vault_save import IdentityForgeVaultSave  # noqa: E402

_FIXTURE_PATH = ROOT / "tests" / "frontend" / "fixtures" / "nodes.json"

# Order matches the seven node_id values used across nodes/*.py.
_NODE_CLASSES = {
    "IdentityForge": IdentityForge,
    "IdentityForgeArchetype": IdentityForgeArchetype,
    "IdentityForgeCosplayer": IdentityForgeCosplayer,
    "IdentityForgeCreature": IdentityForgeCreature,
    "IdentityForgeModifier": IdentityForgeModifier,
    "IdentityForgeTurnaround": IdentityForgeTurnaround,
    "IdentityForgeVaultLoad": IdentityForgeVaultLoad,
    "IdentityForgeVaultSave": IdentityForgeVaultSave,
}

# ComfyUI's standard control_after_generate combo, auto-added by the real
# frontend next to any widget (Int OR Combo) that set a truthy value here. Not
# part of this pack's own schema (no io.* construction produces it), so it
# can't be derived from define_schema() output — this is the one fixed
# convention the generator has to know about, not discover.
_CONTROL_AFTER_GENERATE_OPTIONS = ["fixed", "increment", "decrement", "randomize"]

#: What the sibling combo starts on when the input asked for a bare ``True``
#: rather than naming a mode.
_CONTROL_AFTER_GENERATE_FALLBACK = "randomize"


def _widgets_for(node_cls: Any) -> list[dict[str, Any]]:
    schema = node_cls.define_schema()
    widgets: list[dict[str, Any]] = []
    for inp in schema.inputs:
        if not hasattr(inp, "default"):
            continue  # socket-only Input (e.g. Image.Input) — never a widget
        if getattr(inp, "force_input", False):
            continue  # WidgetInput demoted to a pure socket by force_input

        entry: dict[str, Any] = {"name": inp.id, "default": inp.default}
        if hasattr(inp, "options"):
            entry["type"] = "combo"
            entry["options"] = list(inp.options)
        elif hasattr(inp, "min") and hasattr(inp, "max"):
            entry["type"] = "INT"
        else:
            entry["type"] = "STRING"
        widgets.append(entry)

        control = getattr(inp, "control_after_generate", None)
        if control:
            # A string names the mode the sibling combo starts on ("fixed" on
            # the Turnaround's seed, "increment" on its index); a bare True
            # leaves it on ComfyUI's own default. Hard-coding "randomize" here
            # made the fixture claim every control started there, which is only
            # true of the four randomizers' seeds.
            widgets.append({
                "name": "control_after_generate",
                "type": "combo",
                "default": (control if isinstance(control, str)
                            else _CONTROL_AFTER_GENERATE_FALLBACK),
                "options": list(_CONTROL_AFTER_GENERATE_OPTIONS),
            })
    return widgets


def build_fixture() -> dict[str, list[dict[str, Any]]]:
    return {node_id: _widgets_for(cls) for node_id, cls in _NODE_CLASSES.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Verify the committed fixture matches define_schema() "
                             "output (exit 1 if stale).")
    args = parser.parse_args(argv)

    content = json.dumps(build_fixture(), indent=2) + "\n"
    rel = _FIXTURE_PATH.relative_to(ROOT)

    if args.check:
        existing = _FIXTURE_PATH.read_text(encoding="utf-8") if _FIXTURE_PATH.exists() else ""
        if existing != content:
            print(f"{rel} is STALE relative to live define_schema() output.")
            print("Regenerate with: python scripts/dump_frontend_fixtures.py")
            return 1
        print(f"{rel} is up to date.")
        return 0

    _FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FIXTURE_PATH.write_text(content, encoding="utf-8")
    print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
