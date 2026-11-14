"""IdentityForgeSceneSheet node - one resolved character, a row of places (2.6.0).

The location-side sibling of :mod:`nodes.identity_forge_outfit_sheet`, built the same
way (read the Turnaround's docstring first): it takes a **resolved** character
(Identity Forge's ``prompt_json``), re-runs the engine over it once per place and
emits the prompts as a **list**.

**Ownership line.** This node owns the place. Each view pins one ``location`` and
releases the scene drawn against the old one (lighting, composition, season), so the
engine lights and dates the new place itself. The person never changes.

A place a live rule refuses (``lock_clash``) is handled by what refuses it, as in the
Outfit Sheet: stance and styling a person changes with the setting (pose, gaze,
framing, makeup, jewellery, hair styling, see :data:`_RESTAGED`) are released and
redrawn for that view; anything else (age, body, a locked held item) skips the place
and logs it. Clothing follows the ``clothes`` input: by default every place dresses
the person again (beach clothes on the beach, office clothes in the office); "Keep the
outfit" keeps it and skips a place that refuses it. A cosplayer or a body-covering
character always keeps their costume.

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
    from .identity_forge_outfit_sheet import _CLOTHING, _RESTYLED, _single_view
    from .identity_forge_turnaround import (
        _FRAMINGS, _forge_class, _unwrap, character_seed, document_fields, document_meta,
        parse_document, release_fields, replay_base,
    )
except ImportError:  # pragma: no cover - standalone/test context
    from data.constraints import lock_clash
    from nodes.identity_forge_outfit_sheet import _CLOTHING, _RESTYLED, _single_view
    from nodes.identity_forge_turnaround import (
        _FRAMINGS, _forge_class, _unwrap, character_seed, document_fields, document_meta,
        parse_document, release_fields, replay_base,
    )

_LOG = logging.getLogger(__name__)

#: The selectable sheets, in display order. Exact ``location`` pool values.
_SHEETS: "dict[str, tuple[str, ...]]" = {
    "Everyday (6)": ("sunny city park", "cozy corner coffee shop",
                     "modern open-concept living room", "corporate open office",
                     "wide sandy beach", "forest trail"),
    "Indoors (4)": ("cozy corner coffee shop", "modern open-concept living room",
                    "cozy bookstore with reading nooks", "dimly lit cocktail lounge"),
    "Outdoors (4)": ("sunny city park", "wide sandy beach", "forest trail",
                     "neon-lit city street"),
    "Studio backdrops (3)": ("seamless grey studio backdrop", "solid white studio backdrop",
                             "solid black studio backdrop"),
}

_DRESS = "Dress for each place"
_KEEP_OUTFIT = "Keep the outfit (skip places that refuse it)"

#: Drawn against the place, so released with it (``location_setting`` too: a recorded
#: "Indoor" must not fight a pinned beach).
_SCENE: "frozenset[str]" = frozenset(
    {"location", "location_setting", "lighting", "composition", "season"})

#: What a person changes with the setting; a place that refuses one of these redraws
#: it for that view instead of being skipped.
_RESTAGED: "frozenset[str]" = _RESTYLED | {"pose", "gaze", "shot_type"}


def resolve_scene_sheet(
    character_json: str, sheet_name: str, framing_name: str, clothes: str = _DRESS,
) -> "tuple[list[str], list[str]]":
    """Render one resolved character once per place. Returns ``(prompts, labels)``."""
    forge = _forge_class()
    document = parse_document(character_json)
    base = replay_base(character_json)
    if not document:
        return [str(_unwrap(forge.execute(**base))[0])], ["1-as-resolved"]

    framing = _FRAMINGS.get(framing_name, "")
    if framing:
        base["shot_type"] = framing
    redress = clothes != _KEEP_OUTFIT and not _single_view(document_meta(document))
    release_fields(document, set(_SCENE) | (set(_CLOTHING) if redress else set()))
    # What the place must agree with: everything the replay keeps, plus the framing pin.
    context = document_fields(document)
    pinned = {"shot_type": framing} if framing else {}
    context.update(pinned)

    prompts: "list[str]" = []
    labels: "list[str]" = []
    for place in _SHEETS.get(sheet_name, _SHEETS["Everyday (6)"]):
        refused = {name for name, value in context.items()
                   if lock_clash("location", place, {name: value})}
        blocked = (refused - _RESTAGED) | (refused & set(pinned))
        if blocked:
            _LOG.info("Scene sheet: skipping '%s', which this character's %s refuses.",
                      place, ", ".join(sorted(blocked)))
            continue
        view_document = json.loads(json.dumps(document))
        release_fields(view_document, refused)
        view = {**base, "location": place, "archetype_json": json.dumps(view_document),
                "seed": character_seed(character_json, f"scene|{place}")}
        prompts.append(str(_unwrap(forge.execute(**view))[0]))
        labels.append(f"{len(prompts)}-{place.replace(' ', '-')}")
    if not prompts:
        _LOG.warning("Every place in this sheet clashes with the character; "
                     "emitting one view as resolved.")
        return [str(_unwrap(forge.execute(**replay_base(character_json)))[0])], \
            ["1-as-resolved"]
    return prompts, labels


if _COMFY_AVAILABLE:

    class IdentityForgeSceneSheet(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Emit one resolved character in several places, as a list."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeSceneSheet",
                display_name="Identity Forge Scene Sheet",
                category="conditioning/character",
                description=(
                    "One character, several places, from a single queue. Wire Identity "
                    "Forge's 'prompt_json' in; the 'prompt' output is a LIST, so "
                    "everything downstream runs once per place. The person stays "
                    "exactly as resolved; the place, its light and season change, and "
                    "by default the clothes are chosen again to suit each place."
                ),
                inputs=[
                    io.String.Input(
                        "character_json",
                        default="",
                        force_input=True,
                        tooltip="Connect Identity Forge's 'prompt_json' output. Every "
                                "view is the same person, shown in a different place.",
                    ),
                    io.Combo.Input(
                        "sheet",
                        options=list(_SHEETS),
                        default="Everyday (6)",
                        tooltip="Which places to emit, and so how many images one queue "
                                "makes. Everyday (6) = city park, coffee shop, living "
                                "room, office, beach, forest trail. A place that clashes "
                                "with the character is skipped.",
                    ),
                    io.Combo.Input(
                        "framing",
                        options=list(_FRAMINGS),
                        default="Cowboy (mid-thigh up)",
                        tooltip="How much of the subject each view frames. A wider "
                                "shot shows more of the place. 'Unspecified' keeps the "
                                "character's own framing (redrawn where a place "
                                "refuses it).",
                    ),
                    io.Combo.Input(
                        "clothes",
                        options=[_DRESS, _KEEP_OUTFIT],
                        default=_DRESS,
                        tooltip="'Dress for each place' picks a new outfit that suits "
                                "every place. 'Keep the outfit' keeps the character's "
                                "clothes and skips any place they do not fit (no "
                                "evening gown on a forest trail). A cosplayer always "
                                "keeps their costume.",
                    ),
                ],
                outputs=[
                    io.String.Output(
                        display_name="prompt",
                        is_output_list=True,
                        tooltip="One prompt per place, as a list. Wire into "
                                "CLIPTextEncode.",
                    ),
                    io.String.Output(
                        display_name="view_label",
                        is_output_list=True,
                        tooltip="Matching list of sortable names ('1-sunny-city-park', "
                                "...). Wire into Save Image's filename_prefix.",
                    ),
                ],
            )

        # No fingerprint_inputs: every seed is derived, nothing auto-advances (see
        # Turnaround), so the node is a pure function of its inputs.

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompts, labels = resolve_scene_sheet(
                kwargs.get("character_json", ""),
                kwargs.get("sheet", "Everyday (6)"),
                kwargs.get("framing", "Cowboy (mid-thigh up)"),
                kwargs.get("clothes", _DRESS),
            )
            return io.NodeOutput(prompts, labels)
