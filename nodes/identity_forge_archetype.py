"""IdentityForgeArchetype node — themed character presets for IdentityForge.

Pick (or randomize) an archetype and emit a JSON document of overrides. Wire its
``character_json`` output into the ``archetype_json`` input of an
:class:`~nodes.identity_forge.IdentityForge` node: the archetype defines the
*look* (costume, signature hair/makeup, setting) and IdentityForge randomizes the
rest of the person, so every run is a different individual in the same getup.

Presets chain: connect another preset's ``character_json`` into the optional
``upstream`` input and they stack into one document (this node wins on overlap),
so Archetype and Cosplayer nodes can all stay wired at once. Set a node to
``None`` and it simply passes its upstream through.

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
    from .identity_forge import group_fields, merge_preset_documents
except ImportError:  # pragma: no cover — standalone/test context
    from data.templates import (
        ARCHETYPES, get_archetype_names, get_archetype_preset, fill_costume,
    )
    from data.fields import FIELD_DEFINITIONS
    from nodes.identity_forge import group_fields, merge_preset_documents

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


def _fill_look_costume(look: "dict[str, Any]", rng: "random.Random") -> None:
    """Resolve a look's ``outfit_description`` in place.

    A list value is a set of alternative costume templates — one is seed-picked
    (uniformly, so no template is overweighted) *immediately before* its slots
    are filled, keeping each costume's draws adjacent and deterministic.
    """
    outfit = look.get("outfit_description")
    if isinstance(outfit, list):
        outfit = rng.choice(outfit)
    if outfit is not None:
        look["outfit_description"] = fill_costume(outfit, rng)


def _resolve_list_values(look: "dict[str, Any]", rng: "random.Random") -> None:
    """Seed-pick every remaining list value in ``look``, in place.

    An archetype field may hold a list of curated alternatives (e.g. three
    coherent hair colours); a uniform pick keeps the look while varying the
    detail, with no distribution bias by construction. Runs on the *unfiltered*
    look so the draw count is identical across lock levels (Essentials/Full
    parity for a given seed). Empty lists are dropped (defensive: built-ins are
    validator-checked, user_options.json entries are not).
    """
    for field, value in list(look.items()):
        if isinstance(value, list):
            if value:
                look[field] = rng.choice(value)
            else:
                del look[field]


def build_archetype_json(archetype: str, seed: int = 0, lock_level: str = _ESSENTIALS) -> str:
    """Return the archetype preset as a grouped JSON string.

    ``archetype`` may be a name, ``"None"`` (→ ``"{}"``), or ``"Random"`` (a
    seeded random pick). Costume placeholders are filled from the seed. In
    ``"Essentials"`` mode only look-defining fields are emitted.

    Any field value may be a ``list`` of alternatives — one is seed-picked so a
    single archetype yields a curated range of looks. Draw order (append-only,
    so existing seeds keep their picks when data merely *adds* lists): random
    archetype pick → base costume template pick + slot fills → each variant's
    costume template pick + slot fills → one scalar list pass (base fields in
    template order, then Female/Male variants). Emitted values are always
    strings; ``gender`` must never be a list (validator-enforced).
    """
    rng = random.Random(seed)

    if archetype == _RANDOM:
        archetype = rng.choice(get_archetype_names())
    if archetype == _NONE or archetype not in ARCHETYPES:
        return "{}"

    preset = get_archetype_preset(archetype)

    # A per-gender archetype carries its two divergent looks under "variants"; pull
    # them out of the flat preset (not FIELD_DEFINITIONS fields) and process each the
    # same way as the base — fill costume slots, then Essentials-filter to the look.
    variants = preset.pop("variants", None)

    # Fill costume slots (e.g. "{color}") with seeded picks.
    _fill_look_costume(preset, rng)

    resolved_variants: "dict[str, dict[str, Any]]" = {}
    if isinstance(variants, dict):
        for variant_gender, look in variants.items():
            if variant_gender not in ("Female", "Male") or not isinstance(look, dict):
                continue
            look = dict(look)
            _fill_look_costume(look, rng)
            resolved_variants[variant_gender] = look

    # Scalar list picks happen in one pass after every costume fill and before
    # the Essentials filter, so switching lock level never shifts the draws.
    _resolve_list_values(preset, rng)
    for variant_gender in ("Female", "Male"):
        if variant_gender in resolved_variants:
            _resolve_list_values(resolved_variants[variant_gender], rng)

    filtered_variants: "dict[str, dict[str, Any]]" = resolved_variants
    if lock_level == _ESSENTIALS:
        preset = {f: v for f, v in preset.items() if _is_essential(f)}
        filtered_variants = {
            variant_gender: {f: v for f, v in look.items() if _is_essential(f)}
            for variant_gender, look in resolved_variants.items()
        }

    document: "OrderedDict[str, Any]" = OrderedDict()
    meta: "OrderedDict[str, Any]" = OrderedDict([
        ("archetype", archetype),
        ("gender", get_archetype_preset(archetype).get("gender", "Any")),
        ("lock_level", lock_level),
    ])
    if filtered_variants:
        meta["variants"] = filtered_variants
    document["_meta"] = meta
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
                            "IdentityForge node. Costume colours vary by seed. Chain "
                            "presets via the 'upstream' input — they stack instead of "
                            "fighting over IdentityForge's single socket.",
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
                    io.String.Input(
                        "upstream",
                        default="",
                        optional=True,
                        force_input=True,
                        tooltip="Optional: connect another preset's character_json here "
                                "to stack presets. This node's values win where they "
                                "overlap; set this node to 'None' to pass the upstream "
                                "through unchanged.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def fingerprint_inputs(cls, **kwargs: Any) -> float:
            # Force a fresh roll on every queue. ComfyUI can serve a stale cached
            # result when control_after_generate auto-advances the seed (ComfyUI
            # #11905); returning a never-equal value (NaN) makes this node's cache
            # signature always differ, so it re-executes and reads the new seed.
            # Pure cache control -- no RNG here, so a fixed seed still reproduces
            # exactly and nothing biases the randomization.
            return float("nan")

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            own = build_archetype_json(
                kwargs.get("archetype", _NONE),
                int(kwargs.get("seed", 0)),
                kwargs.get("lock_level", _ESSENTIALS),
            )
            character_json = merge_preset_documents(kwargs.get("upstream", ""), own)
            return io.NodeOutput(character_json)
