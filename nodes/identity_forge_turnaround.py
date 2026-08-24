"""IdentityForgeTurnaround node — one identity, N complementary camera views.

A reference-set builder for image models that accept multiple views of the same
character (a turnaround: front, three-quarters, profile, back). It renders ONE
seed-deterministic character through :class:`~nodes.identity_forge.IdentityForge`
once per run, pinning ``shot_type`` to the view selected by ``index`` and — by
default — ``pose`` to a neutral, symmetric stance from a small curated subset.

Why this shape and not a list output or a composited contact sheet:

* **Iteration.** ComfyUI has no first-class "run this graph N times". The
  ``index`` widget is a combo carrying ``control_after_generate="increment"``,
  so the frontend advances it automatically after every queue — set it to 0,
  queue N times (or use a batch count), and each run emits the next view.
* **Identity stability.** Every view runs with the same seed and the SAME set
  of locked fields (only the pinned VALUE of ``shot_type`` differs), so every
  field resolves identically across runs except the camera. That is also why
  no explicit scene lock is needed: location, lighting, mood and wardrobe come
  out identical for free.
* **Pose.** Most of the pose pool is wrong for a reference set (sitting,
  mid-stride, hand on hip reads differently from each side). The neutral
  subset holds only standing, symmetric, repeatable stances — the same shape
  as the engine's feral-pose subset.

Text-only, zero new dependencies, no IMAGE anywhere: wire ``prompt`` into a
CLIPTextEncode. The engine half is a pure call into IdentityForge.execute, so
constraints, masks, species payloads and modifiers all behave exactly as they
do on the main node.
"""
from __future__ import annotations

import random
from typing import Any

# merge_preset_documents is module-level in identity_forge (importable outside
# ComfyUI); the IdentityForge CLASS only exists when comfy_api is importable,
# so it is resolved lazily inside the functions that call it.
try:
    from .identity_forge import merge_preset_documents
except ImportError:  # pragma: no cover — standalone/test context
    from nodes.identity_forge import merge_preset_documents


def _forge_class() -> type:
    try:
        from .identity_forge import IdentityForge
    except ImportError:  # pragma: no cover — standalone/test context
        from nodes.identity_forge import IdentityForge
    return IdentityForge

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False


#: The complete turnaround, in rotation order. These are exact ``shot_type``
#: pool values — the node pins them through the engine's own widget-lock path,
#: so constraints treat them exactly like a user lock.
_TURNAROUND_VIEWS: tuple[str, ...] = (
    "straight-on eye level",
    "three-quarter angle facing left",
    "three-quarter angle facing right",
    "side profile",
    "from slightly behind and to the side",
    "view from directly behind",
)

_VIEW_PRESETS: dict[str, tuple[str, ...]] = {
    "Turnaround (6)": _TURNAROUND_VIEWS,
    "Portrait set (4)": _TURNAROUND_VIEWS[:4],
    "Front + profile (2)": (_TURNAROUND_VIEWS[0], _TURNAROUND_VIEWS[3]),
}

#: Short labels for filenames / batch collection — the string a user sorts a
#: reference set by.
_VIEW_LABELS: dict[str, str] = {
    "straight-on eye level": "front",
    "three-quarter angle facing left": "three-quarter left",
    "three-quarter angle facing right": "three-quarter right",
    "side profile": "profile",
    "from slightly behind and to the side": "rear three-quarter",
    "view from directly behind": "back",
}

#: Standing, symmetric, repeatable stances only. A reference set must differ
#: ONLY in camera; an asymmetric pose (hand on hip, contrapposto) reads as a
#: different body from each side. Same pattern as the engine's feral poses.
_NEUTRAL_POSES: tuple[str, ...] = (
    "standing naturally",
    "standing with arms relaxed at the sides",
    "standing tall with shoulders back",
    "standing with feet planted wide",
)

#: Steering widgets this node re-exposes, with their IdentityForge defaults.
_STEER_WIDGETS: dict[str, str] = {
    "gender": "Any",
    "wardrobe": "Match gender",
    "size_scale": "Auto",
    "hair_color_scope": "Natural only",
    "accessory_density": "Balanced",
    "location_setting": "Any indoor/outdoor",
}


def resolve_turnaround_prompt(
    upstream: str,
    seed: int,
    views_name: str,
    index_value: Any,
    neutral_pose: str,
    steer: dict[str, str],
) -> tuple[str, str, int]:
    """Run IdentityForge once for the view at ``index``; return (prompt, label, count).

    Pure function (no ComfyUI types) so tests can exercise the pinning logic
    without a running frontend.
    """
    views = _VIEW_PRESETS.get(views_name, _TURNAROUND_VIEWS)
    count = len(views)
    try:
        idx = int(index_value) % count
    except (TypeError, ValueError):
        idx = 0
    shot = views[idx]

    # One neutral pose per character, same across every view. Dedicated stream
    # so the choice never shifts the engine's RNG stream between views.
    pose = ""
    if neutral_pose == "On":
        rng = random.Random(seed ^ 0x5A17)
        pose = rng.choice(_NEUTRAL_POSES)

    forge_kwargs: dict[str, Any] = {
        "seed": seed,
        "archetype_json": merge_preset_documents(upstream, "{}"),
    }
    for spec in _forge_class().define_schema().inputs:
        if spec.id in forge_kwargs:
            continue
        if spec.id in steer:
            forge_kwargs[spec.id] = steer[spec.id]
        elif spec.id == "set_all_fields":
            forge_kwargs[spec.id] = "Off"
        else:
            forge_kwargs[spec.id] = "Random"
    # The pins. shot_type differs per view; pose (and every other resolved
    # field) is identical across views because the lock STRUCTURE is identical.
    forge_kwargs["shot_type"] = shot
    if pose:
        forge_kwargs["pose"] = pose

    prompt = _unwrap(_forge_class().execute(**forge_kwargs))[0]
    return str(prompt), _VIEW_LABELS.get(shot, shot), count


def _unwrap(output: Any) -> tuple:
    """Get the positional results out of a ``NodeOutput``.

    The stub stores them on ``.args``; the real ``comfy_api`` has carried both
    ``.args`` and ``.result`` across versions (same shape as the render
    script's unwrapper). Assume neither.
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
        """Emit one view of a seed-fixed character per run, for reference sets."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            return io.Schema(
                node_id="IdentityForgeTurnaround",
                display_name="Identity Forge Turnaround",
                category="conditioning/character",
                description=(
                    "One character, several camera angles: a turnaround / "
                    "reference set for models that accept multiple views of the "
                    "same person. Each run emits the view chosen by 'index' "
                    "(which auto-increments after every queue); keep 'seed' "
                    "fixed so the identity stays put while only the camera moves."
                ),
                inputs=[
                    io.Int.Input(
                        "seed",
                        default=0,
                        min=0,
                        max=0xFFFFFFFFFFFFFFFF,
                        control_after_generate="fixed",
                        tooltip="Identity seed. Deliberately FIXED across runs "
                                "(unlike the main node): every view must resolve "
                                "the same character. Change it to re-roll the "
                                "whole set.",
                    ),
                    io.Combo.Input(
                        "views",
                        options=list(_VIEW_PRESETS),
                        default="Turnaround (6)",
                        tooltip="Which ordered set of shots 'index' steps "
                                "through. Turnaround covers all six; Portrait "
                                "set drops the two rear views.",
                    ),
                    io.Combo.Input(
                        "index",
                        options=["0", "1", "2", "3", "4", "5"],
                        default="0",
                        control_after_generate="increment",
                        tooltip="Which view THIS run emits. The control below "
                                "the widget defaults to 'increment', so each "
                                "queued render automatically emits the next "
                                "angle: queue 6 runs (or set 'batch count' to "
                                "6) for the full set.",
                    ),
                    io.Combo.Input(
                        "neutral_pose",
                        options=["On", "Off"],
                        default="On",
                        tooltip="Pin the pose to a standing, symmetric stance "
                                "so the ONLY thing that changes between views "
                                "is the camera. 'Off' lets the pose randomize "
                                "(per seed) — useful for looser character "
                                "sheets, fatal for turnarounds.",
                    ),
                ]
                + [
                    io.Combo.Input(name, options=_options_for(name), default=default)
                    for name, default in _STEER_WIDGETS.items()
                ]
                + [
                    io.String.Input(
                        "upstream",
                        default="",
                        optional=True,
                        force_input=True,
                        tooltip="Optional: connect an Archetype / Cosplayer / "
                                "Creature (or Modifier / Vault Load) preset "
                                "here to turn THAT character around. Leave "
                                "unconnected for a random person.",
                    )
                ],
                outputs=[
                    io.String.Output(display_name="prompt"),
                    io.String.Output(display_name="view_label"),
                    io.Int.Output(display_name="view_count"),
                ],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            prompt, label, count = resolve_turnaround_prompt(
                kwargs.get("upstream", ""),
                int(kwargs.get("seed", 0)),
                kwargs.get("views", "Turnaround (6)"),
                kwargs.get("index", "0"),
                kwargs.get("neutral_pose", "On"),
                {name: kwargs.get(name, default) for name, default in _STEER_WIDGETS.items()},
            )
            return io.NodeOutput(prompt, label, count)


def _options_for(name: str) -> list[str]:
    """The option list for a steering widget, read off IdentityForge's schema."""
    for spec in _forge_class().define_schema().inputs:
        if spec.id == name:
            options = getattr(spec, "options", None)
            if options:
                return list(options)
    return []
