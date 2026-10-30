"""IdentityForgeTurnaround node — one resolved character, every camera view at once.

A reference-set builder for image models that accept several views of the same
character (a turnaround: front, three-quarters, profile, back). It takes a
**resolved** character — the ``prompt_json`` output of
:class:`~nodes.identity_forge.IdentityForge` — and emits the whole set of views
as a **list**, so a single queue renders all of them.

Wiring::

    Cosplayer/Archetype -> Identity Forge -(prompt_json)-> Turnaround
                                                              |
                                              (prompt x N) ---+--> CLIPTextEncode -> ...

**One ownership line, and it is the whole design.** Identity Forge owns the
character and the scene; this node owns *only* the camera. That is why it
re-exposes none of the main node's ~80 widgets: the first draft (0.98.0) carried
copies of six steering controls, which meant a user of the Turnaround silently
lost the other seventy-odd, could not tell which node's copy won, and had a third
``seed`` competing with the one on every upstream preset. Taking a resolved
document instead deletes the question rather than documenting an answer.

Why a list output rather than an auto-incrementing ``index`` widget:

* **Identity stability.** The upstream nodes run ONCE per queue, so all N views
  come from the same resolution. With an index widget, an upstream node left on
  ``control_after_generate="randomize"`` re-rolled the character between queues
  and the "turnaround" was six angles on six different people. That is the
  failure this rewrite exists to remove.
* **One queue, N renders.** ``is_output_list=True`` makes ComfyUI run everything
  downstream once per element (``execution.py`` -> ``merge_result_data``), and
  shorter inputs — the negative prompt, the model, the latent — broadcast off
  their last element, so an ordinary graph needs no rewiring.
* **No cache hack.** With no auto-advancing widget and no RNG this node is a pure
  function of its inputs, so it needs no ``fingerprint_inputs`` (contrast the
  four seeded nodes — architecture.md -> "Seeded nodes re-roll every queue").

Why the resolved document is enough to re-render from: ``prompt_json`` is
self-describing by contract — it is exactly what Vault Save writes and Vault Load
feeds back through ``archetype_json``, with every field concrete. Re-running the
engine over it with only ``shot_type`` (and optionally ``pose``) overridden
therefore reproduces the character exactly; the seed cannot move anything,
because nothing is left to randomize.

Text-only, zero new dependencies, no IMAGE anywhere.
"""
from __future__ import annotations

import json
import zlib
from typing import Any

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False


try:
    from ..data.cosplayers import COSPLAYERS
    from .identity_forge import FIELD_DEFINITIONS
except ImportError:  # pragma: no cover — standalone/test context
    from data.cosplayers import COSPLAYERS
    from nodes.identity_forge import FIELD_DEFINITIONS


def _forge_class() -> type:
    """The IdentityForge CLASS, resolved lazily.

    It only exists when ``comfy_api`` is importable, so importing it at module
    scope would make this module unimportable outside ComfyUI.
    """
    try:
        from .identity_forge import IdentityForge
    except ImportError:  # pragma: no cover — standalone/test context
        from nodes.identity_forge import IdentityForge
    return IdentityForge


#: The six rotations, as exact ``shot_type`` pool values. Each describes the
#: subject's ORIENTATION to the camera and nothing else — the distance half comes
#: from :data:`_FRAMINGS`. They are pinned through the engine's own lock path, so
#: constraints treat them exactly like a user lock.
_FRONT = "straight-on eye level"
_THREE_QUARTER_LEFT = "three-quarter angle facing left"
_THREE_QUARTER_RIGHT = "three-quarter angle facing right"
_PROFILE = "side profile"
_REAR_THREE_QUARTER = "from slightly behind and to the side"
_BACK = "view from directly behind"

#: Rotation -> the short, filename-safe name it is labelled with.
_ROTATION_LABELS: "dict[str, str]" = {
    _FRONT: "front",
    _THREE_QUARTER_LEFT: "three-quarter-left",
    _THREE_QUARTER_RIGHT: "three-quarter-right",
    _PROFILE: "profile",
    _REAR_THREE_QUARTER: "rear-three-quarter",
    _BACK: "back",
}

#: The selectable sets, each a sensible rotation in its own right rather than a
#: truncation of the six — a four-view character sheet is front / three-quarter /
#: profile / back, not "the first four of the list".
_VIEW_SETS: "dict[str, tuple[str, ...]]" = {
    "Turnaround (6)": (_FRONT, _THREE_QUARTER_LEFT, _THREE_QUARTER_RIGHT,
                       _PROFILE, _REAR_THREE_QUARTER, _BACK),
    "Turnaround (4)": (_FRONT, _THREE_QUARTER_LEFT, _PROFILE, _BACK),
    "Front + back (2)": (_FRONT, _BACK),
    "Front + profile (2)": (_FRONT, _PROFILE),
}

#: Framing label -> the distance clause prepended to the rotation. Every phrase is
#: an exact ``shot_type`` pool value, so the composed string stays inside the
#: field's own vocabulary (``TurnaroundVocabularyTests`` pins this).
_FRAMINGS: "dict[str, str]" = {
    "Full body": "full body shot",
    "Cowboy (mid-thigh up)": "cowboy shot from mid-thigh up",
    "Waist up": "medium shot from waist up",
    "Chest up": "medium close-up from chest up",
    "Head and shoulders": "close-up portrait",
    "Unspecified": "",
}

#: Keep whatever pose the character resolved to, instead of pinning one.
_KEEP_POSE = "Keep the character's pose"

#: Standing, symmetric, repeatable stances only — all exact ``pose`` pool values.
#: A reference set must differ ONLY in camera, and an asymmetric pose (a hand on
#: one hip, contrapposto) reads as a different body from each side.
_NEUTRAL_POSES: "tuple[str, ...]" = (
    "standing with arms relaxed at the sides",
    "standing naturally",
    "standing tall with shoulders back",
    "standing with feet planted wide",
)

#: Steering the engine reads from kwargs rather than from the document, mapped to
#: the ``_meta`` key that records it, with the widget default as the fallback.
#:
#: These two are the whole reason this node reads ``_meta`` at all. Both are
#: recorded in a resolved document but deliberately NOT honoured on the main
#: node's ``archetype_json`` path — see
#: :func:`~nodes.identity_forge._parse_archetype_json`, where the reasoning is
#: that neither widget has a "defer to the preset" sentinel, so honouring them
#: would let a recalled character silently override a user's live widget. That
#: reasoning is about *steering a new run*. This node is **replaying a finished
#: one** and has no such widgets to override, so it must restore them or the
#: replay is not the same character: measured before the fix, a run made with
#: ``wardrobe: "Any"`` (which unlocks mixed-gender features) came back through the
#: turnaround rebuilt under "Match gender" — a different person in all 150 sampled
#: seeds. ``hair_color_scope`` is restored for the same reason, though it is
#: currently unobservable, since a resolved document always pins ``hair_color``.
_REPLAYED_STEERING: "dict[str, str]" = {
    "wardrobe": "Match gender",
    "hair_color_scope": "Natural only",
}

#: Rotations where the camera is behind the subject's head, so the face is not in
#: frame at all. Only the straight-back view qualifies: "from slightly behind and
#: to the side" still shows a cheek and jaw, and stripping its face detail would
#: lose description a viewer can actually see.
_FACE_OUT_OF_FRAME: "frozenset[str]" = frozenset({_BACK})

#: Field groups that describe nothing but the face.
_FACE_ONLY_GROUPS: "frozenset[str]" = frozenset({"Face", "Makeup"})

#: Face-only fields filed under some other group: a beard reads only from the
#: front, and ``expression`` and ``gaze`` (2.0.0) live with the scene. Ear and neck jewellery are
#: deliberately NOT here -- earrings read perfectly well from behind.
_FACE_ONLY_EXTRA: "frozenset[str]" = frozenset({"facial_hair", "expression", "gaze"})

#: Everything omitted from a view whose camera is behind the subject.
#:
#: Derived from ``FIELD_DEFINITIONS`` rather than hand-listed, so a Face or Makeup
#: field added later is covered without anyone remembering this exists.
#:
#: This is an OMISSION, never a denial. Nothing here ever writes "the face is not
#: visible" -- naming a feature in order to negate it is precisely what makes a
#: t2i model draw it (architecture.md -> "Never negate in prompt data", where nine
#: shipped clauses did exactly that). The character's mask, hair and costume are
#: untouched, because all three read from behind: a helmeted cosplayer keeps their
#: helmet.
_FACE_ONLY_FIELDS: "frozenset[str]" = frozenset(
    name for name, field in FIELD_DEFINITIONS.items()
    if field.get("group") in _FACE_ONLY_GROUPS
) | _FACE_ONLY_EXTRA

#: Seed for the replay call. Held constant, and its value cannot matter: the
#: resolved document locks every field, so the randomizer has nothing left to draw
#: and the RNG stream is never consumed differently between views. It is fixed
#: rather than derived precisely so that if a future field ever escapes the
#: document, it escapes IDENTICALLY into all N views instead of making one of them
#: the odd one out.
_REPLAY_SEED = 0


def compose_shot(framing_name: str, rotation: str) -> str:
    """The ``shot_type`` value for one view: distance clause, then rotation.

    ``shot_type`` is a single field that mixes distance ("full body shot"),
    orientation ("side profile") and lens, so a turnaround cannot express both
    halves by picking one pool value. It composes them instead — free text is safe
    here because ``shot_type``'s two gender pools are identical, which makes
    :func:`~nodes.identity_forge._gender_permits` pass any value. Renders as
    "the framing is full body shot, three-quarter angle facing left".
    """
    distance = _FRAMINGS.get(framing_name, "")
    return f"{distance}, {rotation}" if distance else rotation


def replay_steering(character_json: str) -> "dict[str, str]":
    """Recover the steering controls a resolved document records in ``_meta``.

    Falls back to the widget defaults for anything missing or malformed, so a
    hand-written or truncated document degrades to an ordinary run rather than
    raising. See :data:`_REPLAYED_STEERING`.
    """
    try:
        document = json.loads(character_json or "{}")
    except (ValueError, TypeError):
        document = None
    # Well-formed JSON that is not an object (a bare list) parses fine and then
    # has no .get -- the same shape _parse_archetype_json guards against.
    meta = document.get("_meta") if isinstance(document, dict) else None
    if not isinstance(meta, dict):
        return dict(_REPLAYED_STEERING)
    return {
        name: meta[name] if isinstance(meta.get(name), str) else default
        for name, default in _REPLAYED_STEERING.items()
    }


def replay_base(character_json: str) -> "dict[str, Any]":
    """Main-node kwargs that replay ``character_json`` unchanged: every input on its
    schema default, the replay seed, the document, and its recorded steering. See
    :func:`resolve_turnaround` for why the defaults (not "Random") are load-bearing."""
    forge = _forge_class()
    base: "dict[str, Any]" = {
        spec.id: getattr(spec, "default", None) for spec in forge.define_schema().inputs
    }
    base["seed"] = _REPLAY_SEED
    base["archetype_json"] = character_json or ""
    base.update(replay_steering(character_json))
    return base


def character_seed(character_json: str, salt: str = "") -> int:
    """A replay seed for sheets that RELEASE fields (Outfit Sheet, Age Progression).

    The fixed :data:`_REPLAY_SEED` is right for a replay that redraws nothing, but a
    released field redrawn from it lands on the same value for every character (2.3.0:
    40 characters' casual views shared four outfits). Hashing the document makes the
    redraw differ between characters and repeat for the same one.
    """
    return zlib.crc32(f"{salt}|{character_json or ''}".encode("utf-8"))


def parse_document(character_json: str) -> "dict[str, Any]":
    """The resolved document as a dict, or ``{}`` for anything malformed."""
    try:
        document = json.loads(character_json or "{}")
    except (ValueError, TypeError):
        return {}
    return document if isinstance(document, dict) else {}


def document_meta(document: "dict[str, Any]") -> "dict[str, Any]":
    meta = document.get("_meta")
    return meta if isinstance(meta, dict) else {}


def document_fields(document: "dict[str, Any]") -> "dict[str, str]":
    """Every concrete field value in the document, flattened out of its groups."""
    return {
        name: value
        for key, group in document.items() if key != "_meta" and isinstance(group, dict)
        for name, value in group.items()
        if name in FIELD_DEFINITIONS and isinstance(value, str)
    }


def release_fields(document: "dict[str, Any]", names: "set[str]") -> None:
    """Unlock ``names`` in place, so a replay draws them again under the engine's rules.

    A field is locked twice over in a resolved document: by its value in a group, and,
    when it was deliberately absent, by ``_meta.omitted`` (re-injected as a "None"
    lock). Both have to go or the field stays pinned.
    """
    for key, group in document.items():
        if key != "_meta" and isinstance(group, dict):
            for name in names:
                group.pop(name, None)
    meta = document_meta(document)
    if isinstance(meta.get("omitted"), list):
        meta["omitted"] = [n for n in meta["omitted"] if n not in names]


#: Rotations that show the costume's back, where a roster entry's ``costume_back``
#: replaces its front-facing costume text (2.0.0).
_BACK_OF_COSTUME: "frozenset[str]" = frozenset({_BACK, _REAR_THREE_QUARTER})


def back_costume_document(character_json: str) -> "str | None":
    """The document with its cosplayer's ``costume_back`` swapped in, or None.

    A costume is one free-text string, so a back view used to draw the chest emblem on
    the back. An entry may carry an opt-in ``costume_back``: the same costume as seen
    from behind. The resolved document names its cosplayer in ``_meta.cosplay_of``
    (the key, or "key (franchise)"). The swap replaces the entry's front costume where
    it appears verbatim in the resolved outfit, so a rolled alternate costume or a
    downstream outfit that replaced it is left alone.
    """
    try:
        document = json.loads(character_json or "{}")
    except (ValueError, TypeError):
        return None
    meta = document.get("_meta") if isinstance(document, dict) else None
    label = meta.get("cosplay_of") if isinstance(meta, dict) else None
    if not isinstance(label, str):
        return None
    entry = COSPLAYERS.get(label) or COSPLAYERS.get(label.rsplit(" (", 1)[0]) or {}
    front, back = entry.get("costume"), entry.get("costume_back")
    group = document.get(FIELD_DEFINITIONS["outfit_description"]["group"])
    if not isinstance(group, dict):
        return None
    outfit = group.get("outfit_description")
    if not (front and back and isinstance(outfit, str) and front in outfit):
        return None
    group["outfit_description"] = outfit.replace(front, back)
    return json.dumps(document)


def resolve_turnaround(
    character_json: str,
    views_name: str,
    framing_name: str,
    pose_name: str,
) -> "tuple[list[str], list[str]]":
    """Render one resolved character from every view in the chosen set.

    Returns ``(prompts, labels)``, both the same length and in rotation order.
    Pure function (no ComfyUI types) so the whole behaviour is testable without a
    running frontend.
    """
    rotations = _VIEW_SETS.get(views_name, _VIEW_SETS["Turnaround (6)"])
    forge = _forge_class()

    # Call the main node with ITS OWN schema defaults. That is every randomizable
    # field on "Random" — so the document's values pass straight through, an
    # explicit widget value having overridden them (resolve_locked_fields) — and
    # every *control* on the value that means "defer": `gender: "Any"` reads the
    # document's `_meta.gender`, `size_scale: "Auto"` its `_meta.size_scale`.
    #
    # Reading the defaults rather than writing "Random" everywhere is load-bearing,
    # not tidiness. The controls do not share the fields' vocabulary: "Random" is a
    # nonsense value to `size_scale` (which logs and ignores it) and, worse, is not
    # "Any" to `gender` — so the document's recorded gender was discarded and the
    # engine re-rolled it, turning a woman into a man between the main node and the
    # turnaround. Defaults also mean a control added to the main node later is
    # deferred to correctly here without this node knowing it exists.
    base = replay_base(character_json)
    if pose_name != _KEEP_POSE:
        base["pose"] = pose_name
        # A neutral stance faces the way the camera says; a gaze ("looking over one
        # shoulder") would turn the head differently in every view. Until 2.0.0 the gaze
        # was part of the pose, so pinning the pose replaced it too.
        base["gaze"] = "None"

    back_document = back_costume_document(character_json)

    prompts: "list[str]" = []
    labels: "list[str]" = []
    for position, rotation in enumerate(rotations, start=1):
        view = dict(base)
        if back_document and rotation in _BACK_OF_COSTUME:
            view["archetype_json"] = back_document
        # shot_type is already in `base` (as "Random"), so it is overwritten
        # rather than passed alongside — the one field this node owns.
        view["shot_type"] = compose_shot(framing_name, rotation)
        if rotation in _FACE_OUT_OF_FRAME:
            # "None" is the engine's explicit-omit token and it beats the wired
            # character's own value (resolve_locked_fields), which is what makes
            # this work on a cosplayer whose costume authored those fields.
            view.update(dict.fromkeys(_FACE_ONLY_FIELDS, "None"))
        prompts.append(str(_unwrap(forge.execute(**view))[0]))
        # Numbered so a reference set sorts in rotation order when the label is
        # wired into Save Image's filename_prefix, which is what it is for.
        labels.append(f"{position}-{_ROTATION_LABELS[rotation]}")
    return prompts, labels


def _unwrap(output: Any) -> tuple:
    """Get the positional results out of a ``NodeOutput``.

    The stub stores them on ``.args``; the real ``comfy_api`` has carried both
    ``.args`` and ``.result`` across versions (same shape as the render script's
    unwrapper). Assume neither.
    """
    for attribute in ("args", "result"):
        values = getattr(output, attribute, None)
        if isinstance(values, (tuple, list)):
            return tuple(values)
    if isinstance(output, (tuple, list)):
        return tuple(output)
    raise TypeError(f"Cannot read node output of type {type(output).__name__}")


if _COMFY_AVAILABLE:

    class IdentityForgeTurnaround(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Emit every camera view of one resolved character, as a list."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeTurnaround",
                display_name="Identity Forge Turnaround",
                category="conditioning/character",
                description=(
                    "One character, every camera angle, from a single queue: a "
                    "turnaround / reference set for models that accept several "
                    "views of the same person. Wire Identity Forge's "
                    "'prompt_json' in; the 'prompt' output is a LIST, so "
                    "everything downstream runs once per view. Set the character "
                    "and the scene on Identity Forge itself — this node only "
                    "moves the camera."
                ),
                inputs=[
                    io.String.Input(
                        "character_json",
                        default="",
                        force_input=True,
                        tooltip="The character to turn around: connect Identity "
                                "Forge's 'prompt_json' output here. It is a "
                                "fully resolved character, so every view "
                                "reproduces it exactly — nothing is re-rolled "
                                "between angles. Build the person, the outfit "
                                "and the scene on that node (chain a Cosplayer / "
                                "Archetype / Creature into it as usual); this "
                                "node changes only the camera.",
                    ),
                    io.Combo.Input(
                        "views",
                        options=list(_VIEW_SETS),
                        default="Turnaround (6)",
                        tooltip="Which set of angles to emit — and therefore how "
                                "many images one queue produces. Turnaround (6) "
                                "= front, both three-quarters, profile, rear "
                                "three-quarter and back; Turnaround (4) = front, "
                                "three-quarter, profile, back; the two pairs are "
                                "the quick checks. Every angle is emitted at "
                                "once as a list, so the graph below runs once "
                                "per view.\n"
                                "The straight-back view drops the face "
                                "description (eyes, lips, makeup, expression) "
                                "so the model renders a back and does not turn "
                                "the head to show them; hair, costume and any "
                                "mask are kept.",
                    ),
                    io.Combo.Input(
                        "framing",
                        options=list(_FRAMINGS),
                        default="Full body",
                        tooltip="How much of the subject each view frames. It is "
                                "combined with the angle into the shot "
                                "description, replacing whatever framing the "
                                "character resolved to — 'Full body' is the "
                                "reference-sheet default. 'Unspecified' states "
                                "the angle only and lets the model choose the "
                                "distance.",
                    ),
                    io.Combo.Input(
                        "pose",
                        options=list(_NEUTRAL_POSES) + [_KEEP_POSE],
                        default=_NEUTRAL_POSES[0],
                        tooltip="Pins a standing, symmetric stance so the ONLY "
                                "thing changing between views is the camera. An "
                                "asymmetric pose (a hand on one hip, "
                                "contrapposto) reads as a different body from "
                                "each side, which is why the character's own "
                                "pose (and gaze) is replaced by default. Choose "
                                "'Keep the character's pose' for a looser "
                                "character sheet.",
                    ),
                ],
                outputs=[
                    # Both are lists: ComfyUI runs everything downstream once per
                    # element, and single-valued inputs elsewhere in the graph
                    # (negative prompt, model, latent) broadcast across them.
                    io.String.Output(
                        display_name="prompt",
                        is_output_list=True,
                        tooltip="One prompt per view, as a list. Wire into "
                                "CLIPTextEncode: the whole graph below then runs "
                                "once per angle from a single queue.",
                    ),
                    io.String.Output(
                        display_name="view_label",
                        is_output_list=True,
                        tooltip="Matching list of short, sortable names "
                                "('1-front', '2-three-quarter-left', …). Wire "
                                "into Save Image's filename_prefix to keep a "
                                "reference set in rotation order on disk.",
                    ),
                ],
            )

        # No fingerprint_inputs on purpose. The four seeded nodes need one because
        # control_after_generate silently advances a widget between queues
        # (ComfyUI#11905); this node has no such widget and no RNG, so it is a
        # pure function of its inputs and ComfyUI's normal caching is correct.

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompts, labels = resolve_turnaround(
                kwargs.get("character_json", ""),
                kwargs.get("views", "Turnaround (6)"),
                kwargs.get("framing", "Full body"),
                kwargs.get("pose", _NEUTRAL_POSES[0]),
            )
            return io.NodeOutput(prompts, labels)
