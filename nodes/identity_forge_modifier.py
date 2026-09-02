"""IdentityForgeModifier node — prepend a custom descriptor to single elements.

Sometimes you want *one* element to get a stylistic tilt — sci-fi shoes, glowing
earrings, iridescent skin — without theming the whole image. This node lets you
prepend a free-text descriptor in front of a chosen field's (or whole group's)
randomized value. The descriptor lands right before the noun, which is exactly how
text-to-image models pick up textures / genres (great for alien / sci-fi looks).

Wire its ``character_json`` output into the ``archetype_json`` input of an
:class:`~nodes.identity_forge.IdentityForge` node (or chain it after an Archetype /
Cosplayer node via the optional ``upstream`` input — presets stack, this node only
adds modifiers and never fights over field locks).

Usage — one ``key: descriptor`` per line in the ``style_modifiers`` box::

    footwear: sci-fi chrome      # a FIELD -> only the shoes change
    earrings: glowing            # a FIELD -> only the earrings
    skin_tone: iridescent        # a FIELD -> only the skin tone
    Clothing: weathered          # a GROUP -> every clothing item

``key`` is either a **field name** (the same labels shown on the Identity Forge node:
``footwear``, ``skin_tone``, ``hair_color``, ``earrings`` …) for pin-point control,
or a **group header** (``Demographics``, ``Body``, ``Face``, ``Hair``, ``Makeup``,
``Jewelry & Nails``, ``Clothing``, ``Setting & Shot``) to tilt the whole group. Keys
are case-insensitive; a field key beats a group key when both touch the same field.
Blank lines and ``#`` comments are ignored, and unknown keys are skipped with a note.

Modifiers only **decorate values that are present** — they style an element, they do
not force an absent / ``None`` element to appear. Clearing the box (or muting the
node) disables it entirely.

The engine half (:func:`build_modifier_json`) is a pure function, testable without
ComfyUI.
"""
from __future__ import annotations

import logging

import json
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
#: 1.2.0: runtime messages go to the logger, not stdout. ComfyUI owns root
#: logging configuration, so there is deliberately no handler and no
#: logging.basicConfig() call here. The logger NAME carries what the old
#: '[NodeName]' message prefix used to say, so those prefixes went with them.
_LOG = logging.getLogger(__name__)

try:
    from ..data.fields import FIELD_DEFINITIONS
    from .identity_forge import merge_preset_documents, _GROUP_ORDER, _MODIFIERS_DOC_KEY
except ImportError:  # pragma: no cover — standalone/test context
    from data.fields import FIELD_DEFINITIONS
    from nodes.identity_forge import merge_preset_documents, _GROUP_ORDER, _MODIFIERS_DOC_KEY

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False


#: Pre-filled, self-documenting help shown right inside the node's text box. Every
#: line is a comment or blank, so an untouched node emits nothing (passes upstream
#: through). Users delete a ``#`` to switch a line on.
_HELP_DEFAULT = (
    "# Prepend a descriptor to ONE element (or a whole group).\n"
    "# One per line ->  key: descriptor      (delete the # to use a line)\n"
    "# key = a FIELD (footwear, skin_tone, hair_color, earrings, eye_color, ...)\n"
    "#    or a GROUP (Body, Face, Hair, Makeup, Jewelry & Nails, Clothing, Setting & Shot)\n"
    "# Field names are the same labels shown on the Identity Forge node.\n"
    "#\n"
    "# THE ONE RULE: the descriptor goes IN FRONT of the value, it does not\n"
    "# replace it. So keep it to a 1-3 word adjective that reads naturally there.\n"
    "#   good ->  hair_color: living-flame   (becomes 'living-flame auburn')\n"
    "#   bad  ->  hair_style: nest of vipers (becomes 'nest of vipers messy bun')\n"
    "#\n"
    "# --- materials -------------------------------------------------------\n"
    "# skin_tone: iridescent\n"
    "# skin_tone: cracked molten\n"
    "# skin_tone: carved marble\n"
    "# skin_tone: moss-and-lichen\n"
    "# hair_color: living-flame\n"
    "# eye_color: glowing\n"
    "#\n"
    "# --- genres (a whole group at once) ----------------------------------\n"
    "# Clothing: cyberpunk neon\n"
    "# Clothing: baroque gilded\n"
    "# Clothing: post-apocalyptic weathered\n"
    "# footwear: anti-gravity hover\n"
    "#\n"
    "# --- whimsy ----------------------------------------------------------\n"
    "# Makeup: galaxy-glitter\n"
    "# earrings: tiny caged\n"
    "# Setting & Shot: storm-lit\n"
)


def _parse_modifier_text(text: str) -> "OrderedDict[str, str]":
    """Parse the ``key: descriptor`` box into a ``{canonical_key: descriptor}`` map.

    ``key`` matches a :data:`FIELD_DEFINITIONS` field name or a group header from
    :data:`~nodes.identity_forge._GROUP_ORDER`, case-insensitively, and is stored in
    its canonical casing. Blank / ``#`` lines and lines without a ``key: value`` pair
    are skipped; unknown keys are reported and dropped so the emitted payload is clean.
    """
    field_by_lc = {name.lower(): name for name in FIELD_DEFINITIONS}
    group_by_lc = {group.lower(): group for group in _GROUP_ORDER}

    mods: "OrderedDict[str, str]" = OrderedDict()
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            _LOG.warning("Skipping line without 'key: descriptor' -> %r", raw)
            continue
        key, _, descriptor = line.partition(":")
        key, descriptor = key.strip(), descriptor.strip()
        if not key or not descriptor:
            continue
        canonical = field_by_lc.get(key.lower()) or group_by_lc.get(key.lower())
        if canonical is None:
            _LOG.warning(f"Unknown key {key!r}; use a field name or a "
                  f"group header. Skipping.")
            continue
        mods[canonical] = descriptor  # a later line for the same key wins
    return mods


def build_modifier_json(text: str = "") -> str:
    """Return a preset document carrying only a ``_modifiers`` section.

    Empty / all-comment input yields ``"{}"`` so an inactive node simply passes its
    ``upstream`` through (mirrors the other preset nodes' "None" behaviour).
    """
    mods = _parse_modifier_text(text)
    if not mods:
        return "{}"
    document: "OrderedDict[str, Any]" = OrderedDict()
    document[_MODIFIERS_DOC_KEY] = mods
    return json.dumps(document, indent=2)


if _COMFY_AVAILABLE:

    class IdentityForgeModifier(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Prepend custom descriptors to individual fields / groups of IdentityForge."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeModifier",
                display_name="Identity Forge Modifier",
                category="conditioning/character",
                description=(
                    "Give ONE element a stylistic tilt (sci-fi shoes, glowing earrings, "
                    "iridescent skin) without theming the whole image. Type 'key: "
                    "descriptor' lines; the descriptor is prepended to that field's (or "
                    "group's) randomized value. Wire 'character_json' into Identity "
                    "Forge's 'archetype_json', or chain after an Archetype / Cosplayer "
                    "via 'upstream'. Clear the box (or mute the node) to disable."
                ),
                inputs=[
                    io.String.Input(
                        "style_modifiers",
                        multiline=True,
                        default=_HELP_DEFAULT,
                        tooltip=(
                            "One 'key: descriptor' per line. The descriptor is prepended "
                            "to the randomized value of that element.\n"
                            "  key = a FIELD (footwear, skin_tone, hair_color, earrings, "
                            "eye_color, lips, nails, …) to change just that item,\n"
                            "      or a GROUP (Demographics, Body, Face, Hair, Makeup, "
                            "Jewelry & Nails, Clothing, Setting & Shot) to tilt the whole "
                            "group.\n"
                            "Field names are exactly the labels on the Identity Forge "
                            "node. Keys are case-insensitive; a field key wins over a "
                            "group key. '#' lines and blanks are ignored; unknown keys "
                            "are skipped.\n"
                            "The descriptor is PREPENDED, never substituted, so keep "
                            "it to a 1-3 word adjective that reads naturally in front "
                            "of the value: 'hair_color: living-flame' becomes "
                            "'living-flame auburn', but 'hair_style: nest of vipers' "
                            "becomes 'nest of vipers messy bun'.\n"
                            "Example:  footwear: sci-fi chrome\n"
                            "The text box ships with a curated set of ideas, all "
                            "commented out — delete a '#' to switch one on.\n"
                            "Modifiers only decorate elements that are present — they do "
                            "not force an absent item to appear."
                        ),
                    ),
                    io.String.Input(
                        "upstream",
                        default="",
                        optional=True,
                        force_input=True,
                        tooltip="Optional: connect an Archetype / Cosplayer (or another "
                                "Modifier) character_json here to stack presets. This "
                                "node only adds modifiers, so it never overrides their "
                                "field locks.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            own = build_modifier_json(kwargs.get("style_modifiers", ""))
            character_json = merge_preset_documents(kwargs.get("upstream", ""), own)
            return io.NodeOutput(character_json)
