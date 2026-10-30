"""IdentityForgeOutfitSheet node - one resolved character, a row of outfits.

The wardrobe-side sibling of :mod:`nodes.identity_forge_turnaround` and
:mod:`nodes.identity_forge_expression_sheet`, built the same way (read the Turnaround's
docstring first): it takes a **resolved** character (Identity Forge's ``prompt_json``),
re-runs the engine over it once per view and emits the prompts as a **list**.

**Ownership line.** This node owns only the clothes. Each view pins one
``outfit_style`` and *releases* every Clothing field from the document, so the engine
dresses the same person again under its own rules (season, place, age, body). The
other sheets pin fixed values instead; that cannot work here, because an outfit is a
dozen fields that have to agree with each other, and only the engine can draw them.

Each view replays on its own seed, derived from the style (not the position), so a
style dresses the person the same way in every sheet that contains it, and two views
do not share one colour draw.

A style a live rule refuses (``lock_clash``) is handled by what refuses it. Styling
that changes with the occasion (makeup, jewellery, hair styling, see
:data:`_RESTYLED`) is released and redrawn for that view. Anything else (edgy
alternative at 60+, resort wear in winter, a style the kept scene excludes) skips the
style rather than voicing a contradiction, and logs it. A cosplayer wears their costume, so
a cosplay or a body-covering character emits one view, as does one with no clothing.

Text-only, zero new dependencies.
"""
from __future__ import annotations

import json
import logging
from typing import Any

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover - exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

try:
    from ..data.constraints import lock_clash
    from .identity_forge import FIELD_DEFINITIONS
    from .identity_forge_turnaround import (
        _FRAMINGS, _KEEP_POSE, _NEUTRAL_POSES, _forge_class, _unwrap, document_fields,
        character_seed, document_meta, parse_document, release_fields, replay_base,
    )
except ImportError:  # pragma: no cover - standalone/test context
    from data.constraints import lock_clash
    from nodes.identity_forge import FIELD_DEFINITIONS
    from nodes.identity_forge_turnaround import (
        _FRAMINGS, _KEEP_POSE, _NEUTRAL_POSES, _forge_class, _unwrap, document_fields,
        character_seed, document_meta, parse_document, release_fields, replay_base,
    )

_LOG = logging.getLogger(__name__)

#: Every Clothing field, derived so a field added later is released too.
_CLOTHING: "frozenset[str]" = frozenset(
    name for name, field in FIELD_DEFINITIONS.items() if field.get("group") == "Clothing")

_STYLES: "list[str]" = list(FIELD_DEFINITIONS["outfit_style"]["female_options"])

#: The selectable sheets, in display order. Exact ``outfit_style`` pool values.
_SHEETS: "dict[str, tuple[str, ...]]" = {
    "Range (6)": ("casual", "smart casual", "business formal", "evening formal",
                  "athletic", "resort vacation"),
    "Everyday (4)": ("casual", "smart casual", "streetwear", "athletic"),
    "Work to evening (4)": ("business casual", "business formal", "cocktail semi-formal",
                            "evening formal"),
    "Every style (15)": tuple(_STYLES),
}

_KEEP_SCENE = "Keep the character's scene"

#: Backdrop label -> exact ``location`` pool value ("" keeps the scene). A plain
#: backdrop is the reference-sheet default: no place for a style to clash with.
_BACKDROPS: "dict[str, str]" = {
    "Grey studio backdrop": "seamless grey studio backdrop",
    "White studio backdrop": "solid white studio backdrop",
    "Black studio backdrop": "solid black studio backdrop",
    _KEEP_SCENE: "",
}

#: Scene fields drawn against the place; released with it when a backdrop replaces it
#: (studio light at a backdrop, not the park's afternoon sun; a backdrop has no season,
#: by the engine's own location -> season rule).
_SCENE: "frozenset[str]" = frozenset({"location", "lighting", "composition", "season"})

#: Styling a person changes with the occasion. The engine gates most of it on
#: ``outfit_style`` (mismatched earrings with business dress, a pearl necklace with
#: athletic wear, a scrunchie with evening dress); measured over 60 seeds, skipping
#: on these instead left most backdrop sheets with one or two views. So a style that
#: refuses one of them restyles it; a style refused by anything else (age, season,
#: the kept place) is skipped.
_RESTYLED: "frozenset[str]" = frozenset(
    name for name, field in FIELD_DEFINITIONS.items()
    if field.get("group") in ("Makeup", "Jewelry & Nails")
) | {"hair_accessory", "hair_style"}


def _single_view(meta: "dict[str, Any]") -> bool:
    """A character whose outfit is not the engine's to redraw."""
    suppressed_groups = meta.get("suppress_groups") or ()
    suppressed_fields = meta.get("suppress_fields") or ()
    return bool(meta.get("cosplay_of") or meta.get("covers_body")
                or "Clothing" in suppressed_groups or "outfit_description" in suppressed_fields)


def resolve_outfit_sheet(
    character_json: str, sheet_name: str, backdrop_name: str, framing_name: str,
    pose_name: str, outfit_seed: int = 0,
) -> "tuple[list[str], list[str]]":
    """Render one resolved character once per outfit style. Returns ``(prompts, labels)``."""
    forge = _forge_class()
    document = parse_document(character_json)
    meta = document_meta(document)
    base = replay_base(character_json)
    framing = _FRAMINGS.get(framing_name, "")
    if framing:
        base["shot_type"] = framing
    if pose_name != _KEEP_POSE:
        base["pose"] = pose_name

    if not document or _single_view(meta):
        _LOG.warning("This character's outfit is a costume or a body form, not a "
                     "wardrobe; emitting one view.")
        return [str(_unwrap(forge.execute(**base))[0])], ["1-as-resolved"]

    released = set(_CLOTHING)
    backdrop = _BACKDROPS.get(backdrop_name, "")
    if backdrop:
        released |= _SCENE
        base["location"] = backdrop
    if framing:
        released |= {name for name, value in document_fields(document).items()
                     if lock_clash("shot_type", framing, {name: value})}
    release_fields(document, released)
    base["archetype_json"] = json.dumps(document)
    # What the outfit must agree with: everything the replay keeps, plus the pins.
    context = document_fields(document)
    context.update({k: base[k] for k in ("location", "pose") if k in base
                    and base[k] not in ("Random", None)})

    names = _SHEETS.get(sheet_name, _SHEETS["Range (6)"])
    prompts: "list[str]" = []
    labels: "list[str]" = []
    for style in names:
        refused = {name for name, value in context.items()
                   if lock_clash("outfit_style", style, {name: value})}
        if refused - _RESTYLED:
            _LOG.info("Outfit sheet: skipping '%s', which this character's %s refuses.",
                      style, ", ".join(sorted(refused - _RESTYLED)))
            continue
        view = {**base, "outfit_style": style,
                "seed": character_seed(character_json, f"{outfit_seed}|{style}")}
        if refused:
            restyled = json.loads(json.dumps(document))
            release_fields(restyled, refused)
            view["archetype_json"] = json.dumps(restyled)
        prompts.append(str(_unwrap(forge.execute(**view))[0]))
        labels.append(f"{len(prompts)}-{style.replace(' ', '-')}")
    if not prompts:
        _LOG.warning("Every style in this sheet clashes with the character; "
                     "emitting one view as resolved.")
        return [str(_unwrap(forge.execute(**replay_base(character_json)))[0])], \
            ["1-as-resolved"]
    return prompts, labels


if _COMFY_AVAILABLE:

    class IdentityForgeOutfitSheet(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Emit one resolved character in several outfits, as a list."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeOutfitSheet",
                display_name="Identity Forge Outfit Sheet",
                category="conditioning/character",
                description=(
                    "One character, several outfits, from a single queue: a wardrobe "
                    "sheet. Wire Identity Forge's 'prompt_json' in; the 'prompt' "
                    "output is a LIST, so everything downstream runs once per outfit. "
                    "Only the clothes change - the person stays exactly as resolved."
                ),
                inputs=[
                    io.String.Input(
                        "character_json",
                        default="",
                        force_input=True,
                        tooltip="Connect Identity Forge's 'prompt_json' output. Every "
                                "view is the same person; each one is dressed again "
                                "in one outfit style. A cosplayer wears their costume, "
                                "so a cosplay character emits one view.",
                    ),
                    io.Combo.Input(
                        "sheet",
                        options=list(_SHEETS),
                        default="Range (6)",
                        tooltip="Which outfit styles to emit, and so how many images one "
                                "queue makes. Range (6) = casual, smart casual, business "
                                "formal, evening formal, athletic, resort vacation. A "
                                "style that clashes with the character (edgy "
                                "alternative at 60+, for example) is skipped.",
                    ),
                    io.Combo.Input(
                        "backdrop",
                        options=list(_BACKDROPS),
                        default="Grey studio backdrop",
                        tooltip="Where each outfit is shown. A plain studio backdrop "
                                "suits every style; 'Keep the character's scene' keeps "
                                "the place, lighting and composition, and skips any "
                                "style that place refuses (no evening gown on a hiking "
                                "trail).",
                    ),
                    io.Combo.Input(
                        "framing",
                        options=list(_FRAMINGS),
                        default="Full body",
                        tooltip="How much of the subject each view frames. 'Full body' "
                                "shows the whole outfit, shoes included. 'Unspecified' "
                                "keeps the character's own framing.",
                    ),
                    io.Combo.Input(
                        "pose",
                        options=list(_NEUTRAL_POSES) + [_KEEP_POSE],
                        default=_NEUTRAL_POSES[0],
                        tooltip="Pins a standing stance so every outfit is shown the "
                                "same way. Choose 'Keep the character's pose' to keep "
                                "it (a seated pose hides much of an outfit).",
                    ),
                    io.Int.Input(
                        "outfit_seed",
                        default=0,
                        min=0,
                        max=0xFFFFFFFFFFFFFFFF,
                        control_after_generate=True,
                        tooltip="Rolls a different outfit in every style for the same "
                                "character. Outfits already differ from one character "
                                "to the next; change this to re-dress the same person. "
                                "Set the control to 'randomize' for new outfits every "
                                "queue.",
                    ),
                ],
                outputs=[
                    io.String.Output(
                        display_name="prompt",
                        is_output_list=True,
                        tooltip="One prompt per outfit, as a list. Wire into "
                                "CLIPTextEncode.",
                    ),
                    io.String.Output(
                        display_name="view_label",
                        is_output_list=True,
                        tooltip="Matching list of sortable names ('1-casual', "
                                "'2-smart-casual', ...). Wire into Save Image's "
                                "filename_prefix.",
                    ),
                ],
            )

        # No fingerprint_inputs: every seed is derived, nothing auto-advances (see
        # Turnaround), so the node is a pure function of its inputs.

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompts, labels = resolve_outfit_sheet(
                kwargs.get("character_json", ""),
                kwargs.get("sheet", "Range (6)"),
                kwargs.get("backdrop", "Grey studio backdrop"),
                kwargs.get("framing", "Full body"),
                kwargs.get("pose", _NEUTRAL_POSES[0]),
                int(kwargs.get("outfit_seed", 0) or 0),
            )
            return io.NodeOutput(prompts, labels)
