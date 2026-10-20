"""IdentityForgeExpressionSheet node - one resolved character, a row of expressions.

The face-side sibling of :mod:`nodes.identity_forge_turnaround`, built the same way and
for the same reasons (read that module's docstring first): it takes a **resolved**
character (Identity Forge's ``prompt_json``), re-runs the engine over it once per view
and emits the prompts as a **list**, so one queue renders the whole sheet from one
identity.

**Ownership line.** The Turnaround owns only the camera; this node owns only the
face's emotion: ``expression``, ``mood`` and ``smile_type``. Everything else - the
person, the outfit, the scene, the pose - is the document's, unchanged.

Each view pins an explicit (expression, mood, smile_type) triple from
:data:`_SHEETS` rather than "releasing" the three fields for the engine to re-roll.
A re-roll would need a seed per view and could land two views on the same face; a
fixed triple is deterministic, and ``ExpressionSheetTests`` checks every triple
against the live exclusion rules, so a pairing the engine would refuse cannot ship.

A ``covers_face`` character (a mascot head, a full helmet) has no visible
expression, so the sheet degrades to a single view of the character as resolved.

Text-only, zero new dependencies, no RNG.
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
    from .identity_forge_turnaround import (
        _FRAMINGS, _REPLAY_SEED, _forge_class, _unwrap, replay_steering,
    )
except ImportError:  # pragma: no cover - standalone/test context
    from nodes.identity_forge_turnaround import (
        _FRAMINGS, _REPLAY_SEED, _forge_class, _unwrap, replay_steering,
    )

_LOG = logging.getLogger(__name__)

#: Label -> (expression, mood, smile_type). Exact pool values; "None" omits a field.
#: Labels are filename-safe because they become Save Image prefixes.
_VIEWS: "dict[str, tuple[str, str, str]]" = {
    "neutral": ("neutral", "tranquil", "closed mouth"),
    "smile": ("warm smile", "cheerful", "soft smile"),
    "laughing": ("laughing", "joyful", "toothy grin"),
    "surprised": ("surprised", "None", "None"),
    "serious": ("serious", "intense", "closed mouth"),
    "sad": ("teary-eyed", "sorrowful", "closed mouth"),
    "angry": ("defiant", "fierce", "closed mouth"),
    "smirk": ("smirking", "mysterious", "asymmetric"),
    "thoughtful": ("contemplative", "dreamy", "closed mouth"),
    "worried": ("worried", "tense", "closed mouth"),
}

#: The selectable sheets, in display order.
_SHEETS: "dict[str, tuple[str, ...]]" = {
    "Basic (6)": ("neutral", "smile", "laughing", "surprised", "serious", "sad"),
    "Full (10)": tuple(_VIEWS),
    "Smiles (3)": ("smile", "laughing", "smirk"),
}

_DEFAULT_FRAMING = "Head and shoulders"


def _covers_face(character_json: str) -> bool:
    try:
        document = json.loads(character_json or "{}")
    except (ValueError, TypeError):
        return False
    meta = document.get("_meta") if isinstance(document, dict) else None
    return isinstance(meta, dict) and bool(meta.get("covers_face"))


def resolve_expression_sheet(
    character_json: str, sheet_name: str, framing_name: str,
) -> "tuple[list[str], list[str]]":
    """Render one resolved character once per expression. Returns ``(prompts, labels)``."""
    forge = _forge_class()
    # Schema defaults for every input, then the document: the Turnaround's recipe, and
    # its long note on why defaults (not "Random" everywhere) are load-bearing.
    base: "dict[str, Any]" = {
        spec.id: getattr(spec, "default", None) for spec in forge.define_schema().inputs
    }
    base["seed"] = _REPLAY_SEED
    base["archetype_json"] = character_json or ""
    base.update(replay_steering(character_json))
    framing = _FRAMINGS.get(framing_name, "")
    if framing:
        base["shot_type"] = framing

    if _covers_face(character_json):
        _LOG.warning("A face-covering character has no visible expression; "
                     "emitting one view.")
        return [str(_unwrap(forge.execute(**base))[0])], ["1-masked"]

    names = _SHEETS.get(sheet_name, _SHEETS["Basic (6)"])
    prompts: "list[str]" = []
    labels: "list[str]" = []
    for position, name in enumerate(names, start=1):
        expression, mood, smile = _VIEWS[name]
        view = {**base, "expression": expression, "mood": mood, "smile_type": smile}
        prompts.append(str(_unwrap(forge.execute(**view))[0]))
        labels.append(f"{position}-{name}")
    return prompts, labels


if _COMFY_AVAILABLE:

    class IdentityForgeExpressionSheet(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Emit one resolved character with several expressions, as a list."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeExpressionSheet",
                display_name="Identity Forge Expression Sheet",
                category="conditioning/character",
                description=(
                    "One character, several expressions, from a single queue: an "
                    "expression sheet. Wire Identity Forge's 'prompt_json' in; the "
                    "'prompt' output is a LIST, so everything downstream runs once "
                    "per expression. Only the expression, mood and smile change - "
                    "the person, outfit and scene stay exactly as resolved."
                ),
                inputs=[
                    io.String.Input(
                        "character_json",
                        default="",
                        force_input=True,
                        tooltip="Connect Identity Forge's 'prompt_json' output. It "
                                "is a fully resolved character, so every view is the "
                                "same person; only the face's emotion changes.",
                    ),
                    io.Combo.Input(
                        "sheet",
                        options=list(_SHEETS),
                        default="Basic (6)",
                        tooltip="Which expressions to emit, and so how many images "
                                "one queue makes. Basic (6) = neutral, smile, "
                                "laughing, surprised, serious, sad; Full (10) adds "
                                "angry, smirk, thoughtful, worried. A face-covering "
                                "character (mascot head, full helmet) emits one view.",
                    ),
                    io.Combo.Input(
                        "framing",
                        options=list(_FRAMINGS),
                        default=_DEFAULT_FRAMING,
                        tooltip="How much of the subject each view frames, replacing "
                                "the character's own framing. 'Head and shoulders' "
                                "keeps the face large enough to read. 'Unspecified' "
                                "keeps the character's own framing.",
                    ),
                ],
                outputs=[
                    io.String.Output(
                        display_name="prompt",
                        is_output_list=True,
                        tooltip="One prompt per expression, as a list. Wire into "
                                "CLIPTextEncode.",
                    ),
                    io.String.Output(
                        display_name="view_label",
                        is_output_list=True,
                        tooltip="Matching list of sortable names ('1-neutral', "
                                "'2-smile', ...). Wire into Save Image's "
                                "filename_prefix.",
                    ),
                ],
            )

        # No fingerprint_inputs: no RNG and no auto-advancing widget (see Turnaround).

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompts, labels = resolve_expression_sheet(
                kwargs.get("character_json", ""),
                kwargs.get("sheet", "Basic (6)"),
                kwargs.get("framing", _DEFAULT_FRAMING),
            )
            return io.NodeOutput(prompts, labels)
