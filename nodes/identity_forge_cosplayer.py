"""IdentityForgeCosplayer node — fictional characters as a worn cosplay look.

Pick (or randomize) a fictional character and emit a JSON document of overrides.
Wire its ``character_json`` output into the ``archetype_json`` input of an
:class:`~nodes.identity_forge.IdentityForge` node. The character's costume defines
the *look* and IdentityForge randomizes the person underneath, so every run is a
different individual cosplaying the same character.

Presets chain: connect another preset's ``character_json`` into the optional
``upstream`` input and they stack into one document (this node wins on overlap),
so Archetype and Cosplayer nodes can all stay wired at once. Set a node to
``None`` and it simply passes its upstream through.

Two look levels:

* **Costume only** (default) — only the costume and a few signature look traits
  (hair, eyes) are sent, so body, face, and demographics stay free to randomize.
  This is the "a random person cosplaying X" mode.
* **Full character** — also locks the character's physique (body type, height,
  skin tone, …) for a faithful reproduction; the scene still randomizes.

Full-mask characters (``covers_face``) carry their head covering in a separate
``mask`` field. The node's ``mask`` widget defaults to keeping it on (face/hair
suppressed); ``"Unmask (show face)"`` drops it so the randomized head shows under
the suit — a helmet-off look. It is a no-op for face-visible characters.

Characters with a signature held prop (Thor's hammer, Captain America's shield)
carry it in an optional ``prop`` field. The ``props`` widget is **off by default**
("worn, not held" stays the norm); ``"Include signature prop"`` emits the prop as
the hidden ``held_item`` lock, voiced downstream as "holding …". It is a no-op for
characters without a ``prop``.

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
import re
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
try:
    from ..data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_names_by_gender, get_cosplayer_categories,
    )
    from ..data.fields import FIELD_DEFINITIONS
    from .identity_forge import group_fields, merge_preset_documents
except ImportError:  # pragma: no cover — standalone/test context
    from data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_names_by_gender, get_cosplayer_categories,
    )
    from data.fields import FIELD_DEFINITIONS
    from nodes.identity_forge import group_fields, merge_preset_documents

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

#: Mask options (only affect ``covers_face`` characters).
_MASK_DEFAULT = "Default"
_MASK_OFF = "Unmask (show face)"

#: Signature-prop options (only affect characters that carry a ``prop``).
_PROP_OFF = "No prop"
_PROP_ON = "Include signature prop"

#: Random-scope sentinel: no franchise/category limit on the Random picks.
_SCOPE_ANY = "Any"

#: A face-visible character whose colour covers the whole body (and therefore the
#: face) — She-Hulk's green, Mystique's blue, a Nightsister's chalk-white — is
#: written with the canonical "an even … coat of <colour> …" phrasing (see the
#: cosplayer conventions in docs/architecture.md). When that paint/skin/fur coat
#: is present the engine must NOT also randomize a human skin tone, complexion,
#: skin marks, or skin-toned makeup underneath: those describe a natural-coloured
#: face that t2i models then render *under* the paint, leaving the face pale while
#: the body is coloured. This regex detects the marker so the contradicting fields
#: can be locked absent (the costume's own colour becomes the only skin descriptor).
_BODY_PAINT_RE = re.compile(r"\ban even\b.*?\bcoat of\b", re.IGNORECASE)

#: Skin / makeup fields force-locked absent for body-paint characters, each mapped
#: to the absent token the engine expects. ``makeup_style`` is locked to "no makeup"
#: (which the constraints in data/constraints.py cascade to clear every cosmetic
#: sub-field, and which _is_absent() treats as omitted so the whole makeup sentence
#: drops): the umbrella style word ("soft glam", "dewy look", ...) implies a face
#: foundation that t2i models render as a pale base *under* the paint, leaving the
#: face light while the body is coloured (the She-Hulk / Satana pale-face bug). With
#: the style suppressed the costume's own paint colour becomes the only skin/face
#: descriptor. ``"None"`` is the universal absent sentinel for the skin fields, which
#: carry no such constraint; "no blush"/"none" match the makeup absent tokens.
_BODY_PAINT_SUPPRESS: dict[str, str] = {
    "skin_tone": "None",
    "complexion": "None",
    "skin_details": "None",
    "freckles_density": "None",
    "skin_finish": "None",
    "makeup_style": "no makeup",
    "blush": "no blush",
    "contour": "none",
    "highlight": "none",
}


def _is_body_paint(entry: dict, costume: str) -> bool:
    """Whether the character's colour covers the face (so human skin must be hid).

    Defaults to auto-detecting the canonical body-paint phrase in the costume; an
    explicit ``body_paint`` key on the entry forces it on or off.
    """
    override = entry.get("body_paint")
    if override is not None:
        return bool(override)
    return bool(_BODY_PAINT_RE.search(costume))


def _resolve_character(
    character: str, rng: random.Random, category: str = _SCOPE_ANY
) -> str | None:
    """Resolve a combo selection to a concrete character name.

    Returns ``None`` for "None", an unknown name, or a Random pick over an empty
    pool (e.g. "Random — male" before any male characters are added). ``category``
    limits the Random picks to one franchise/category ("Any" = no limit). A specific
    character selection ignores ``category``.
    """
    if character in _RANDOM_POOLS:
        gender = _RANDOM_POOLS[character]
        pool = get_cosplayer_names(gender=gender, category=category)
        if not pool:  # empty (gender, category) combo -> fall back to the full gender pool
            pool = get_cosplayer_names(gender=gender)
        if not pool:
            print(f"[IdentityForgeCosplayer] No characters available for '{character}'.")
            return None
        return rng.choice(pool)
    if character == _NONE or character not in COSPLAYERS:
        return None
    return character


def build_cosplayer_json(
    character: str,
    seed: int = 0,
    look_level: str = _COSTUME_ONLY,
    mask_mode: str = _MASK_DEFAULT,
    include_prop: bool = False,
    random_scope: str = _SCOPE_ANY,
) -> str:
    """Return the cosplay preset as a grouped JSON string.

    ``character`` may be a name, ``"None"`` (→ ``"{}"``), or one of the
    ``"Random — …"`` scoping picks. In ``"Costume only"`` mode the costume plus
    signature look is emitted; ``"Full character"`` also locks the physique.

    ``mask_mode`` only affects full-mask characters (those with ``covers_face``
    and a ``mask`` clause). ``"Default"`` attaches the mask to the costume and
    keeps ``covers_face`` set so IdentityForge drops the randomized face/hair.
    ``"Unmask (show face)"`` omits the mask clause and clears ``covers_face`` so
    the randomized head/hair shows (a "helmet-off" look). It is a no-op for
    face-visible characters.

    ``include_prop`` (default ``False``) adds the character's signature held prop
    (e.g. Thor's hammer) as the hidden ``held_item`` lock, voiced downstream as
    "holding …". It is a no-op for characters without a ``prop``.

    ``random_scope`` (default ``"Any"``) limits the ``"Random — …"`` picks to one
    franchise/category; it is ignored when a specific character is selected.
    """
    rng = random.Random(seed)
    name = _resolve_character(character, rng, random_scope)
    if name is None:
        return "{}"

    entry = get_cosplayer(name)

    covers = bool(entry.get("covers_face", False))
    unmask = covers and mask_mode == _MASK_OFF
    # The mask clause lives apart from the costume so it can be dropped on unmask.
    costume = entry["costume"]
    if covers and not unmask and entry.get("mask"):
        costume = f"{costume}, {entry['mask']}"

    # The costume drives IdentityForge's hidden outfit_description override; the
    # signature look (hair/eyes) is always applied; physique only in Full mode.
    fields: dict[str, str] = {"outfit_description": costume}
    fields.update(entry.get("signature", {}))
    # Free-text canonical eye-colour override for characters whose eyes fall outside
    # the believable-people eye_color pool (e.g. "crimson", "golden cat-slit pupils").
    # eye_color has identical gender pools, so the downstream gender gate passes the
    # free-text value straight to the prose. Applied in both look levels.
    if entry.get("eyes"):
        fields["eye_color"] = entry["eyes"]
    if look_level == _FULL:
        fields.update(entry.get("physique", {}))
    # Signature held prop → hidden held_item lock (opt-in; off by default).
    if include_prop and entry.get("prop"):
        fields["held_item"] = entry["prop"]

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = OrderedDict([
        ("cosplay_of", name),
        ("franchise", entry.get("franchise", "")),
        ("gender", entry.get("gender", "Any")),
        ("look_level", look_level),
        ("covers_face", covers and not unmask),
    ])
    document.update(group_fields(fields))
    # When an eye-colour override is in play, lock eye_shape to absent so the override
    # reads clean downstream ("crimson eyes", not "crimson deep-set eyes"). Injected
    # here, after group_fields (which strips "None" on the build side), because the
    # engine keeps a locked "None" as the absent state and omits it from its own prose
    # and JSON. setdefault preserves an explicit signature eye_shape if one was set.
    if entry.get("eyes"):
        for group_values in document.values():
            if isinstance(group_values, dict) and "eye_color" in group_values:
                group_values.setdefault("eye_shape", "None")
                # A free-text eye description already encodes size; lock eye_size
                # off too so a random size doesn't contradict it in the JSON.
                group_values.setdefault("eye_size", "None")
                break
    # Body-paint characters (face shows but the colour covers it): force the human
    # skin tone / complexion / skin marks / skin-toned makeup absent so only the
    # costume's paint colour describes the skin — otherwise the face renders pale
    # under the paint. Skipped when the face is masked away (those fields are hidden
    # already). Injected here for the same reason as the eye locks above: group_fields
    # strips "None", but the engine keeps a locked "None" as the absent state.
    if not (covers and not unmask) and _is_body_paint(entry, costume):
        for field_name, absent in _BODY_PAINT_SUPPRESS.items():
            group = FIELD_DEFINITIONS.get(field_name, {}).get("group", "Other")
            document.setdefault(group, OrderedDict())[field_name] = absent
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
                            "gender) person cosplaying that character. Chain presets via "
                            "the 'upstream' input so Archetype and Cosplayer nodes can "
                            "all stay wired at once.",
                inputs=[
                    io.Combo.Input(
                        "character",
                        options=[_NONE, _RANDOM_ANY, _RANDOM_FEMALE, _RANDOM_MALE]
                                + get_cosplayer_names(),
                        default=_NONE,
                        tooltip="Character to cosplay. 'None' emits nothing; the "
                                "'Random — …' entries pick one using the seed, scoped by "
                                "the source character's gender (and by 'random_scope' "
                                "below). Type to filter the list.",
                    ),
                    io.Combo.Input(
                        "random_scope",
                        options=[_SCOPE_ANY] + get_cosplayer_categories(),
                        default=_SCOPE_ANY,
                        tooltip="Limits the 'Random — …' picks to one franchise/category "
                                "(e.g. only Anime & Manga, only Marvel). 'Any' = no limit. "
                                "Combines with the gender scope; no effect when a specific "
                                "character is picked.",
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
                    io.Combo.Input(
                        "mask",
                        options=[_MASK_DEFAULT, _MASK_OFF],
                        default=_MASK_DEFAULT,
                        tooltip="Only affects full-mask characters (Spider-Man, Iron "
                                "Man, …). 'Default' keeps the mask on and hides the "
                                "randomized face/hair. 'Unmask (show face)' drops the "
                                "mask so the randomized head/hair shows under the suit "
                                "(a helmet-off look). No effect on face-visible "
                                "characters.",
                    ),
                    io.Combo.Input(
                        "props",
                        options=[_PROP_OFF, _PROP_ON],
                        default=_PROP_OFF,
                        tooltip="Off by default. 'Include signature prop' adds the "
                                "character's iconic held prop (e.g. Thor's hammer, "
                                "Captain America's shield), voiced as 'holding …'. No "
                                "effect on characters without a signature prop. Note: "
                                "held objects can stress hand rendering in some models.",
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
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            own = build_cosplayer_json(
                kwargs.get("character", _NONE),
                int(kwargs.get("seed", 0)),
                kwargs.get("look_level", _COSTUME_ONLY),
                kwargs.get("mask", _MASK_DEFAULT),
                kwargs.get("props", _PROP_OFF) == _PROP_ON,
                kwargs.get("random_scope", _SCOPE_ANY),
            )
            character_json = merge_preset_documents(kwargs.get("upstream", ""), own)
            return io.NodeOutput(character_json)
