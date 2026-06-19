"""IdentityForgeCosplayer node — fictional characters as a worn cosplay look.

Pick (or randomize) a fictional character and emit a JSON document of overrides.
Wire its ``character_json`` output into the ``archetype_json`` input of an
:class:`~nodes.identity_forge.IdentityForge` node (it shares that socket with the
Archetype node — use one or the other). The character's costume defines the
*look* and IdentityForge randomizes the person underneath, so every run is a
different individual cosplaying the same character.

Two look levels:

* **Costume only** (default) — only the costume and a few signature look traits
  (hair, eyes) are sent, so body, face, and demographics stay free to randomize.
  This is the "a random person cosplaying X" mode.
* **Full character** — also locks the character's physique (body type, height,
  skin tone, …) for a faithful reproduction; the scene still randomizes.

The *person's* gender is chosen on the IdentityForge node, independent of the
character's, so crossplay (e.g. a man cosplaying a female character) works: the
downstream gender gate drops any value invalid for the chosen gender. The source
character's gender here only scopes the "Random — female / male" picks.

The engine half (:func:`build_cosplayer_json`) is a pure function, testable
without ComfyUI.
"""
from __future__ import annotations

import json
import random
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
try:
    from ..data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_names_by_gender,
    )
    from .identity_forge import group_fields
except ImportError:  # pragma: no cover — standalone/test context
    from data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_names_by_gender,
    )
    from nodes.identity_forge import group_fields

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

#: Sentinels for the character combo.
_NONE = "None"
_RANDOM_ANY = "Random — any"
_RANDOM_FEMALE = "Random — female"
_RANDOM_MALE = "Random — male"
_RANDOM_POOLS: dict[str, str | None] = {
    _RANDOM_ANY: None,        # any source gender
    _RANDOM_FEMALE: "Female",
    _RANDOM_MALE: "Male",
}

#: Look-level options.
_COSTUME_ONLY = "Costume only"
_FULL = "Full character"


def _resolve_character(character: str, rng: random.Random) -> str | None:
    """Resolve a combo selection to a concrete character name.

    Returns ``None`` for "None", an unknown name, or a Random pick over an empty
    pool (e.g. "Random — male" before any male characters are added).
    """
    if character in _RANDOM_POOLS:
        gender = _RANDOM_POOLS[character]
        pool = get_cosplayer_names() if gender is None else get_cosplayer_names_by_gender(gender)
        if not pool:
            print(f"[IdentityForgeCosplayer] No characters available for '{character}'.")
            return None
        return rng.choice(pool)
    if character == _NONE or character not in COSPLAYERS:
        return None
    return character


def build_cosplayer_json(
    character: str, seed: int = 0, look_level: str = _COSTUME_ONLY
) -> str:
    """Return the cosplay preset as a grouped JSON string.

    ``character`` may be a name, ``"None"`` (→ ``"{}"``), or one of the
    ``"Random — …"`` scoping picks. In ``"Costume only"`` mode the costume plus
    signature look is emitted; ``"Full character"`` also locks the physique.
    """
    rng = random.Random(seed)
    name = _resolve_character(character, rng)
    if name is None:
        return "{}"

    entry = get_cosplayer(name)

    # The costume drives IdentityForge's hidden outfit_description override; the
    # signature look (hair/eyes) is always applied; physique only in Full mode.
    fields: dict[str, str] = {"outfit_description": entry["costume"]}
    fields.update(entry.get("signature", {}))
    if look_level == _FULL:
        fields.update(entry.get("physique", {}))

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = OrderedDict([
        ("cosplay_of", name),
        ("franchise", entry.get("franchise", "")),
        ("gender", entry.get("gender", "Any")),
        ("look_level", look_level),
    ])
    document.update(group_fields(fields))
    return json.dumps(document, indent=2)


if _COMFY_AVAILABLE:

    class IdentityForgeCosplayer(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Fictional-character cosplay presets that feed IdentityForge."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeCosplayer",
                display_name="Identity Forge Cosplayer",
                category="conditioning/character",
                description="Pick or randomize a fictional character and emit JSON to "
                            "seed an IdentityForge node — a random (optionally cross-"
                            "gender) person cosplaying that character. Shares the "
                            "archetype_json socket with the Archetype node.",
                inputs=[
                    io.Combo.Input(
                        "character",
                        options=[_NONE, _RANDOM_ANY, _RANDOM_FEMALE, _RANDOM_MALE]
                                + get_cosplayer_names(),
                        default=_NONE,
                        tooltip="Character to cosplay. 'None' emits nothing; the "
                                "'Random — …' entries pick one using the seed, scoped by "
                                "the source character's gender. Type to filter the list.",
                    ),
                    io.Combo.Input(
                        "look_level",
                        options=[_COSTUME_ONLY, _FULL],
                        default=_COSTUME_ONLY,
                        tooltip="'Costume only' sends the costume + signature hair/eyes so "
                                "the person (body, face, ethnicity) randomizes freely. "
                                "'Full character' also locks the physique for a faithful "
                                "look. Set the IdentityForge 'gender' widget to mix for "
                                "crossplay.",
                    ),
                    io.Int.Input(
                        "seed",
                        default=0,
                        min=0,
                        max=0xFFFFFFFFFFFFFFFF,
                        # String value sets the control widget's default mode to
                        # randomize (a bare True would default it to "fixed").
                        control_after_generate="randomize",
                        tooltip="Seed for the random character pick. The control below "
                                "defaults to 'randomize'.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            character_json = build_cosplayer_json(
                kwargs.get("character", _NONE),
                int(kwargs.get("seed", 0)),
                kwargs.get("look_level", _COSTUME_ONLY),
            )
            return io.NodeOutput(character_json)
