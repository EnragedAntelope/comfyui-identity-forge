"""IdentityForgeAgeProgression node - one resolved character at several ages.

A sibling of :mod:`nodes.identity_forge_turnaround` (read its docstring first): it
takes a **resolved** character (Identity Forge's ``prompt_json``), re-runs the engine
over it once per life stage and emits the prompts as a **list**.

**Ownership line.** This node owns ``age``, and only what age forces:

* **Fields a live rule refuses at that age** are released and redrawn by the engine
  (``lock_clash``): laugh lines at 20, "porcelain smooth" skin at 70, pigtails from
  45, an undercut from 55. When the refused field is ``outfit_style`` the whole
  outfit goes with it, because the outfit text was written for that style.
* **Hair greys forward, never back.** Under "Natural only" hair, a stage at 55 or
  older than the character turns natural colour grey (salt and pepper for dark hair,
  silver otherwise, silver for everyone from 70); a stage younger than a grey-haired
  character, and under 55, gets one natural colour drawn once for the whole sheet, so
  the person does not change hair colour between their twenties and forties. Dye
  (Full spectrum), a cosplayer's canon hair and covered hair are left alone.

Everything else (face, build, outfit, scene) is the document's, unchanged.
Every stage is an exact ``age`` pool value, so the youngest is 18 by construction.
A face-covering character, or a form with no age, emits one view.

Text-only, zero new dependencies, no RNG of its own.
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
    from ..data.constraints import FIELD_FAMILIES, lock_clash
    from .identity_forge import FIELD_DEFINITIONS
    from .identity_forge_turnaround import (
        _FRAMINGS, _forge_class, _unwrap, document_fields, document_meta,
        character_seed, parse_document, release_fields, replay_base,
    )
except ImportError:  # pragma: no cover - standalone/test context
    from data.constraints import FIELD_FAMILIES, lock_clash
    from nodes.identity_forge import FIELD_DEFINITIONS
    from nodes.identity_forge_turnaround import (
        _FRAMINGS, _forge_class, _unwrap, document_fields, document_meta,
        character_seed, parse_document, release_fields, replay_base,
    )

_LOG = logging.getLogger(__name__)

#: The selectable progressions, in display order. Exact ``age`` pool values.
_STAGES: "dict[str, tuple[str, ...]]" = {
    "Life stages (4)": ("20", "35", "50", "70"),
    "Decades (6)": ("20", "30", "40", "50", "60", "70"),
    "Young and old (2)": ("25", "70"),
}

_CLOTHING: "frozenset[str]" = frozenset(
    name for name, field in FIELD_DEFINITIONS.items() if field.get("group") == "Clothing")

_GREY: "frozenset[str]" = frozenset(FIELD_FAMILIES["hair_color"]["gray_white"]["variants"])
_DARK: "frozenset[str]" = frozenset(
    FIELD_FAMILIES["hair_color"]["black"]["variants"]
    + FIELD_FAMILIES["hair_color"]["brunette"]["variants"])

#: From this age natural hair is grey more often than not (the engine's own
#: ``_GREY_BY_AGE`` crosses one half at 55), so a progression shows it grey.
_GREYS_AT = 55
_SILVER_AT = 70


def _stage_hair(original: str, character_age: int, stage: int, natural: str) -> str:
    """The hair colour at ``stage``: greying forward from the character, never back."""
    if original in _GREY:
        return original if stage >= min(character_age, _GREYS_AT) else natural
    if stage > character_age and stage >= _GREYS_AT:
        return "salt and pepper" if original in _DARK and stage < _SILVER_AT else "silver"
    return original


def _aged_view(
    document: "dict[str, Any]", base: "dict[str, Any]", pins: "dict[str, str]",
    also: "frozenset[str]" = frozenset(),
) -> "dict[str, Any]":
    """Replay kwargs with ``pins`` locked, and everything they refuse (laugh lines at
    20, highlights in grey hair) released, plus ``also``, for the engine to redraw."""
    fields = document_fields(document)
    refused = set(also) | {
        name for name, value in fields.items() if name not in pins
        and any(lock_clash(pin, pinned, {name: value}) for pin, pinned in pins.items())}
    if "outfit_style" in refused:
        refused |= _CLOTHING
    view_document = json.loads(json.dumps(document))
    release_fields(view_document, refused)
    return {**base, **pins, "archetype_json": json.dumps(view_document)}


def _natural_colour(document: "dict[str, Any]", base: "dict[str, Any]") -> str:
    """The colour a grey-haired character had young: one engine draw at age 20."""
    kwargs = _aged_view(document, base, {"age": "20"}, frozenset({"hair_color"}))
    resolved = parse_document(str(_unwrap(_forge_class().execute(**kwargs))[1]))
    return document_fields(resolved).get("hair_color", "")


def resolve_age_progression(
    character_json: str, stages_name: str, framing_name: str,
) -> "tuple[list[str], list[str]]":
    """Render one resolved character once per age. Returns ``(prompts, labels)``."""
    forge = _forge_class()
    document = parse_document(character_json)
    meta = document_meta(document)
    fields = document_fields(document)
    base = replay_base(character_json)
    # Released fields (skin detail at 70, say) redraw per character, not one shared draw.
    base["seed"] = character_seed(character_json, "age")
    framing = _FRAMINGS.get(framing_name, "")
    if framing:
        base["shot_type"] = framing
        # A close-up refuses a horizon-line composition and a full-standing pose.
        release_fields(document, {name for name, value in fields.items()
                                  if lock_clash("shot_type", framing, {name: value})})

    character_age = fields.get("age", "")
    if meta.get("covers_face") or not character_age.isdigit():
        _LOG.warning("This character shows no age (a covered face, or a form without "
                     "one); emitting one view.")
        return [str(_unwrap(forge.execute(**base))[0])], ["1-as-resolved"]

    hair = fields.get("hair_color", "")
    greys = bool(hair and base.get("hair_color_scope") == "Natural only"
                 and not meta.get("cosplay_of") and not meta.get("covers_hair"))
    natural = ""
    if greys and hair in _GREY:
        natural = _natural_colour(document, base) or hair

    prompts: "list[str]" = []
    labels: "list[str]" = []
    for position, stage in enumerate(_STAGES.get(stages_name, _STAGES["Life stages (4)"]),
                                     start=1):
        pins = {"age": stage}
        if greys:
            pins["hair_color"] = _stage_hair(hair, int(character_age), int(stage), natural)
        view = _aged_view(document, base, pins)
        prompts.append(str(_unwrap(forge.execute(**view))[0]))
        labels.append(f"{position}-age-{stage}")
    return prompts, labels


if _COMFY_AVAILABLE:

    class IdentityForgeAgeProgression(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Emit one resolved character at several ages, as a list."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeAgeProgression",
                display_name="Identity Forge Age Progression",
                category="conditioning/character",
                description=(
                    "One character at several ages, from a single queue. Wire Identity "
                    "Forge's 'prompt_json' in; the 'prompt' output is a LIST, so "
                    "everything downstream runs once per age. The face, build, outfit "
                    "and scene stay as resolved; hair greys with age, and anything "
                    "that reads wrong at an age (laugh lines at 20, pigtails at 70) is "
                    "redrawn."
                ),
                inputs=[
                    io.String.Input(
                        "character_json",
                        default="",
                        force_input=True,
                        tooltip="Connect Identity Forge's 'prompt_json' output. Every "
                                "view is the same person at a different age. A "
                                "face-covering character (mascot head, full helmet) "
                                "emits one view.",
                    ),
                    io.Combo.Input(
                        "stages",
                        options=list(_STAGES),
                        default="Life stages (4)",
                        tooltip="Which ages to emit, and so how many images one queue "
                                "makes. Life stages (4) = 20, 35, 50, 70; Decades (6) = "
                                "20 to 70 in tens; Young and old (2) = 25 and 70.",
                    ),
                    io.Combo.Input(
                        "framing",
                        options=list(_FRAMINGS),
                        default="Head and shoulders",
                        tooltip="How much of the subject each view frames. 'Head and "
                                "shoulders' keeps the face, where age shows, large. "
                                "'Unspecified' keeps the character's own framing.",
                    ),
                ],
                outputs=[
                    io.String.Output(
                        display_name="prompt",
                        is_output_list=True,
                        tooltip="One prompt per age, as a list. Wire into "
                                "CLIPTextEncode.",
                    ),
                    io.String.Output(
                        display_name="view_label",
                        is_output_list=True,
                        tooltip="Matching list of sortable names ('1-age-20', "
                                "'2-age-35', ...). Wire into Save Image's "
                                "filename_prefix.",
                    ),
                ],
            )

        # No fingerprint_inputs: no RNG and no auto-advancing widget (see Turnaround).

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompts, labels = resolve_age_progression(
                kwargs.get("character_json", ""),
                kwargs.get("stages", "Life stages (4)"),
                kwargs.get("framing", "Head and shoulders"),
            )
            return io.NodeOutput(prompts, labels)
