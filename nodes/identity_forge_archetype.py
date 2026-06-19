"""IdentityForgeArchetype node — themed character presets for IdentityForge.

Pick (or randomize) an archetype and emit a JSON document of overrides. Wire its
``character_json`` output into the ``archetype_json`` input of an
:class:`~nodes.identity_forge.IdentityForge` node: the archetype defines the
*look* (costume, signature hair/makeup, setting) and IdentityForge randomizes the
rest of the person, so every run is a different individual in the same getup.

Two lock levels:

* **Essentials** (default) — only the look-defining fields are sent, so body,
  face, and demographics stay free to randomize downstream. Best for variety.
* **Full preset** — every field the template specifies is locked, for a fixed,
  reproducible character.

Costume strings may contain ``{slot}`` placeholders (see
:data:`data.templates.COSTUME_SLOTS`); they are filled with seeded random picks
so the same costume varies in colour, fabric, metal, etc.

The engine half (:func:`build_archetype_json`) is a pure function, testable
without ComfyUI.
"""
from __future__ import annotations

import json
import random
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
try:
    from ..data.templates import (
        ARCHETYPES, get_archetype_names, get_archetype_preset, fill_costume,
    )
    from ..data.fields import FIELD_DEFINITIONS
    from .identity_forge import group_fields
except ImportError:  # pragma: no cover — standalone/test context
    from data.templates import (
        ARCHETYPES, get_archetype_names, get_archetype_preset, fill_costume,
    )
    from data.fields import FIELD_DEFINITIONS
    from nodes.identity_forge import group_fields

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

#: Sentinels for the archetype combo.
_NONE = "None"
_RANDOM = "Random"

#: Lock-level options.
_ESSENTIALS = "Essentials"
_FULL = "Full preset"

#: In "Essentials" mode only fields from these groups (plus gender) are sent —
#: the styled "look". Demographics / Body / Face are dropped so the person
#: underneath randomizes freely.
_ESSENTIAL_GROUPS: frozenset[str] = frozenset({
    "Hair", "Makeup", "Jewelry & Nails", "Clothing", "Setting & Shot",
})


def _is_essential(field: str) -> bool:
    if field == "gender":
        return True
    return FIELD_DEFINITIONS.get(field, {}).get("group") in _ESSENTIAL_GROUPS


def build_archetype_json(archetype: str, seed: int = 0, lock_level: str = _ESSENTIALS) -> str:
    """Return the archetype preset as a grouped JSON string.

    ``archetype`` may be a name, ``"None"`` (→ ``"{}"``), or ``"Random"`` (a
    seeded random pick). Costume placeholders are filled from the seed. In
    ``"Essentials"`` mode only look-defining fields are emitted.
    """
    rng = random.Random(seed)

    if archetype == _RANDOM:
        archetype = rng.choice(get_archetype_names())
    if archetype == _NONE or archetype not in ARCHETYPES:
        return "{}"

    preset = get_archetype_preset(archetype)

    # Fill costume slots (e.g. "{color}") with seeded picks.
    if "outfit_description" in preset:
        preset["outfit_description"] = fill_costume(preset["outfit_description"], rng)

    if lock_level == _ESSENTIALS:
        preset = {f: v for f, v in preset.items() if _is_essential(f)}

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = OrderedDict([
        ("archetype", archetype),
        ("gender", get_archetype_preset(archetype).get("gender", "Any")),
        ("lock_level", lock_level),
    ])
    document.update(group_fields(preset))
    return json.dumps(document, indent=2)


if _COMFY_AVAILABLE:

    class IdentityForgeArchetype(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Themed character presets that feed IdentityForge."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeArchetype",
                display_name="Identity Forge Archetype",
                category="conditioning/character",
                description="Pick or randomize a themed character archetype (knight, "
                            "sorceress, pirate, pop star, …) and emit JSON to seed an "
                            "IdentityForge node. Costume colours vary by seed.",
                inputs=[
                    io.Combo.Input(
                        "archetype",
                        options=[_NONE, _RANDOM] + get_archetype_names(),
                        default=_NONE,
                        tooltip="Character archetype. 'None' emits nothing; 'Random' "
                                "picks one using the seed.",
                    ),
                    io.Combo.Input(
                        "lock_level",
                        options=[_ESSENTIALS, _FULL],
                        default=_ESSENTIALS,
                        tooltip="'Essentials' sends only the look (costume, hair, makeup, "
                                "setting) so the person randomizes freely downstream. "
                                "'Full preset' locks every field the archetype defines.",
                    ),
                    io.Int.Input(
                        "seed",
                        default=0,
                        min=0,
                        max=0xFFFFFFFFFFFFFFFF,
                        # String value sets the control widget's default mode to
                        # randomize (a bare True would default it to "fixed").
                        control_after_generate="randomize",
                        tooltip="Seed for the random archetype pick and costume colour "
                                "variation. The control below defaults to 'randomize'.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            character_json = build_archetype_json(
                kwargs.get("archetype", _NONE),
                int(kwargs.get("seed", 0)),
                kwargs.get("lock_level", _ESSENTIALS),
            )
            return io.NodeOutput(character_json)
