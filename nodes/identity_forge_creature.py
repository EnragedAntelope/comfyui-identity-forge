"""IdentityForgeCreature node — a non-human *form* layer (animal / monster / alien).

Pick (or randomize) a creature and emit a ``Species & Anatomy`` JSON document that
seeds an :class:`~nodes.identity_forge.IdentityForge` node: a creature head, eyes,
integument (skin / fur / scales / chitin / shell) and optional limbs, tail and wings.
IdentityForge renders the chosen *form* and **suppresses** the human fields it
replaces (a creature head hides the face/hair, a creature integument hides the skin),
while everything not replaced — a wired costume, the surviving body, the scene — still
composes. Wire ``character_json`` into IdentityForge's ``archetype_json`` (or chain it
after an Archetype / Cosplayer via the optional ``upstream`` input; the node closest to
IdentityForge wins on overlap).

**Only-one vs mix-everything.** The ``creature`` widget answers it in one dropdown:
``None`` (off), ``Random - any`` (across every class), ``Random - <class>`` (only
monsters / only insects / only aliens / …), or a specific creature.

**Hybrids / chimeras.** Each anatomy slot (``head``, ``eyes``, ``integument``, ``arms``,
``hands``, ``legs_feet``, ``tail``, ``wings``) can override the base creature — set it to
``Follow base``, ``Random``, or a specific creature. So a praying-mantis body with a
sloth's head is ``creature = praying mantis`` + ``head = sloth``. The free-text
``more_features`` box (``slot: phrase`` lines, or bare extra features) adds unlimited
detail without a wall of widgets.

**Form.** ``Anthropomorphic`` (default) keeps a humanoid silhouette so costumes stay
compatible; ``Feral / full creature`` drops the human clothing/makeup/jewellery for a
true beast; ``Subtle hybrid`` keeps the human and adds the creature as accents. ``Random``
rolls one with the seed.

The engine half (:func:`build_creature_json`) is a pure function, testable without
ComfyUI.
"""
from __future__ import annotations

import json
import random
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
try:
    from ..data.creatures import (
        CREATURES, CREATURE_CLASSES, CREATURE_SLOTS,
        get_creature, get_creature_names, get_creature_names_by_class,
    )
    from .identity_forge import (
        merge_preset_documents, _a, _SPECIES_GROUP,
        _FORM_ANTHRO, _FORM_FERAL, _FORM_SUBTLE,
    )
except ImportError:  # pragma: no cover — standalone/test context
    from data.creatures import (
        CREATURES, CREATURE_CLASSES, CREATURE_SLOTS,
        get_creature, get_creature_names, get_creature_names_by_class,
    )
    from nodes.identity_forge import (
        merge_preset_documents, _a, _SPECIES_GROUP,
        _FORM_ANTHRO, _FORM_FERAL, _FORM_SUBTLE,
    )

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

# --- creature combo sentinels ----------------------------------------------
_NONE = "None"
_RANDOM_ANY = "Random - any"
#: "Random - <class>" -> class, for the only-a-monster / only-an-insect scoping.
_RANDOM_CLASS_LABELS: dict[str, str] = {f"Random - {c}": c for c in CREATURE_CLASSES}

# --- per-slot override sentinels -------------------------------------------
_FOLLOW = "Follow base"
_RANDOM_SLOT = "Random"

# --- detail sentinels ------------------------------------------------------
_AUTO = "Auto"
_FINISHES = ["matte", "glossy", "iridescent", "slimy", "bioluminescent",
             "translucent", "metallic", "wet", "fuzzy"]
_PALETTES = ["emerald", "crimson", "sapphire blue", "royal violet", "gold", "obsidian black",
             "bone white", "ash grey", "blood red", "electric blue", "toxic green",
             "iridescent", "chrome", "deep purple", "amber", "teal", "rose pink"]
_SIZES = ["tiny", "small", "human-sized", "large", "towering"]

# --- form labels (UI) -> canonical tokens (the engine's vocabulary) --------
_FORM_LABEL_ANTHRO = "Anthropomorphic"
_FORM_LABEL_FERAL = "Feral / full creature"
_FORM_LABEL_SUBTLE = "Subtle hybrid"
_FORM_LABEL_RANDOM = "Random"
_FORM_LABEL_TO_TOKEN: dict[str, str] = {
    _FORM_LABEL_ANTHRO: _FORM_ANTHRO,
    _FORM_LABEL_FERAL: _FORM_FERAL,
    _FORM_LABEL_SUBTLE: _FORM_SUBTLE,
}

#: Which human groups/fields a form (and its filled slots) suppress. Mirrors and
#: generalizes IdentityForge's covers_face behaviour: the creature replaces them.
_FORM_SUPPRESS_GROUPS: dict[str, set[str]] = {
    _FORM_ANTHRO: {"Demographics"},
    _FORM_FERAL: {"Demographics", "Makeup", "Jewelry & Nails", "Clothing"},
    _FORM_SUBTLE: set(),
}
#: A feral (non-humanoid) form also drops the humanoid body proportions — a beast has
#: no bust / waist / hips / shoulders. Build / height / fitness stay (a "powerful,
#: towering" creature reads fine). Anthro keeps them (it is humanoid).
_FORM_SUPPRESS_FIELDS: dict[str, set[str]] = {
    _FORM_ANTHRO: set(),
    _FORM_FERAL: {"bust", "waist", "hips", "shoulder_width", "neck_length", "posture"},
    _FORM_SUBTLE: set(),
}
#: A creature head hides the human face/hair/makeup; an integument hides the skin.
#: arms/hands/legs map to no human field (the body is humanoid), so they add only text.
_SLOT_CONCEAL_GROUPS: dict[str, set[str]] = {"head": {"Face", "Hair", "Makeup"}}
_SLOT_CONCEAL_FIELDS: dict[str, set[str]] = {
    "integument": {"skin_tone", "skin_details", "complexion", "skin_finish", "freckles_density"},
}
#: The Subtle form keeps the human and only *adds* what humans lack (limbs read as
#: creature, plus wings / tail / extras); the conflicting replacers (head, eyes,
#: integument) are dropped so it never co-describes a human and a creature face.
_SUBTLE_DROP_SLOTS: frozenset[str] = frozenset({"head", "eyes", "integument"})

#: The eight anatomy slots exposed as override dropdowns (``extras`` is base-only,
#: plus whatever the free-text box adds).
_OVERRIDE_SLOTS: tuple[str, ...] = (
    "head", "eyes", "integument", "arms", "hands", "legs_feet", "tail", "wings",
)

_MORE_HELP = (
    "# Add or override anatomy with free text (optional).\n"
    "# 'slot: phrase' overrides a slot; a line with no ':' is an extra feature.\n"
    "# slots: head, eyes, integument, arms, hands, legs_feet, tail, wings, extras\n"
    "#\n"
    "# eyes: six glowing ocelli\n"
    "# wings: feathered angel wings\n"
    "# a crown of bone spurs\n"
)


def _prepend_descriptor(phrase: str, descriptor: str) -> str:
    """Prepend ``descriptor`` to ``phrase``, fixing the article ("a"/"an").

    "a segmented exoskeleton" + "emerald" -> "an emerald segmented exoskeleton".
    A phrase without a leading article (a plural / mass noun) just gets the
    descriptor in front: "compound eyes" + "glowing" -> "glowing compound eyes".
    """
    if not descriptor or not phrase:
        return phrase
    for article in ("a ", "an ", "A ", "An "):
        if phrase.startswith(article):
            return f"{_a(descriptor)} {descriptor} {phrase[len(article):]}"
    return f"{descriptor} {phrase}"


def _resolve_creature(creature: str, rng: random.Random) -> str | None:
    """Resolve the ``creature`` combo to a concrete name (or ``None``)."""
    if creature == _RANDOM_ANY:
        pool = get_creature_names()
        return rng.choice(pool) if pool else None
    if creature in _RANDOM_CLASS_LABELS:
        pool = get_creature_names_by_class(_RANDOM_CLASS_LABELS[creature])
        if not pool:
            print(f"[IdentityForgeCreature] No creatures available for '{creature}'.")
            return None
        return rng.choice(pool)
    if creature == _NONE or creature not in CREATURES:
        return None
    return creature


def _resolve_slot(
    slot: str, base_name: str | None, selection: str, rng: random.Random
) -> tuple[str | None, str | None]:
    """Resolve one slot to ``(value, source_creature)``.

    ``Follow base`` uses the base creature; ``Random`` picks any creature for that
    slot; a name uses that creature. Returns ``(None, None)`` when nothing applies
    (e.g. the source creature does not fill that slot).
    """
    if selection == _FOLLOW:
        source = base_name
    elif selection == _RANDOM_SLOT:
        pool = get_creature_names()
        source = rng.choice(pool) if pool else None
    elif selection in CREATURES:
        source = selection
    else:
        source = None
    if not source:
        return None, None
    value = get_creature(source).get(slot)
    return (value if isinstance(value, str) and value else None), source


def _parse_more_features(text: str, slots: "OrderedDict[str, str]") -> list[str]:
    """Apply ``more_features`` overrides in place; return loose extra features.

    A ``slot: phrase`` line whose key is a known slot overrides that slot verbatim
    (so the user wins over palette/finish). Any other ``key: phrase`` line or a bare
    line becomes an extra feature appended to ``extras``.
    """
    extras: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key, value = key.strip().lower(), value.strip()
            if not value:
                continue
            if key in CREATURE_SLOTS:
                slots[key] = value
                continue
            extras.append(value)
        else:
            extras.append(line)
    return extras


def _suppression(form_token: str, slots: "OrderedDict[str, str]") -> tuple[list[str], list[str]]:
    """Return ``(suppress_groups, suppress_fields)`` for the form and filled slots."""
    groups = set(_FORM_SUPPRESS_GROUPS.get(form_token, set()))
    fields = set(_FORM_SUPPRESS_FIELDS.get(form_token, set()))
    if form_token != _FORM_SUBTLE:  # Subtle keeps the human; its creature bits are accents
        for slot in slots:
            groups |= _SLOT_CONCEAL_GROUPS.get(slot, set())
            fields |= _SLOT_CONCEAL_FIELDS.get(slot, set())
    return sorted(groups), sorted(fields)


def build_creature_json(
    creature: str,
    seed: int = 0,
    form: str = _FORM_LABEL_ANTHRO,
    head: str = _FOLLOW,
    eyes: str = _FOLLOW,
    integument: str = _FOLLOW,
    arms: str = _FOLLOW,
    hands: str = _FOLLOW,
    legs_feet: str = _FOLLOW,
    tail: str = _FOLLOW,
    wings: str = _FOLLOW,
    integument_finish: str = _AUTO,
    palette: str = _AUTO,
    size_scale: str = _AUTO,
    more_features: str = "",
) -> str:
    """Return the creature preset as a ``Species & Anatomy`` JSON string.

    ``creature`` may be a name, ``"None"`` (→ ``"{}"``), ``"Random - any"`` or
    ``"Random - <class>"``. Each slot override is ``Follow base`` / ``Random`` / a
    name. ``palette`` (default = the integument source's colour) and
    ``integument_finish`` recolour/retexture the integument; ``size_scale`` scales the
    subject; ``more_features`` adds free-text slots/extras. Emits ``"{}"`` when nothing
    is selected, so an inactive node passes its upstream through.
    """
    rng = random.Random(seed)

    form_token = _FORM_LABEL_TO_TOKEN.get(form)
    if form_token is None:  # "Random" (or anything unexpected) -> seed-pick a form
        form_token = rng.choice([_FORM_ANTHRO, _FORM_FERAL, _FORM_SUBTLE])

    base_name = _resolve_creature(creature, rng)

    overrides = {
        "head": head, "eyes": eyes, "integument": integument, "arms": arms,
        "hands": hands, "legs_feet": legs_feet, "tail": tail, "wings": wings,
    }
    slots: "OrderedDict[str, str]" = OrderedDict()
    integument_source = base_name
    for slot in CREATURE_SLOTS:
        if slot in _OVERRIDE_SLOTS:
            value, source = _resolve_slot(slot, base_name, overrides[slot], rng)
            if slot == "integument" and source:
                integument_source = source
        elif base_name:  # base-only slots (extras)
            raw = get_creature(base_name).get(slot)
            value = raw if isinstance(raw, str) and raw else None
        else:
            value = None
        if value:
            slots[slot] = value

    # Subtle form keeps the human face/skin: drop the conflicting replacer slots so
    # the result is a human with creature limbs/wings/tail, not two faces.
    if form_token == _FORM_SUBTLE:
        for drop in _SUBTLE_DROP_SLOTS:
            slots.pop(drop, None)

    # Recolour / retexture the integument: palette (override, else the source
    # creature's own colour) goes on first, then the finish sits outermost.
    if slots.get("integument"):
        palette_value = palette if palette != _AUTO else (
            get_creature(integument_source).get("palette") if integument_source else None
        )
        if palette_value:
            slots["integument"] = _prepend_descriptor(slots["integument"], palette_value)
        if integument_finish != _AUTO:
            slots["integument"] = _prepend_descriptor(slots["integument"], integument_finish)

    # Free-text overrides win verbatim; loose lines accrue onto extras.
    extras = _parse_more_features(more_features, slots)
    if extras:
        existing = slots.get("extras")
        slots["extras"] = f"{existing}, {', '.join(extras)}" if existing else ", ".join(extras)

    if not slots:  # nothing to render -> inactive, pass upstream through
        return "{}"

    size = size_scale if size_scale != _AUTO else None
    meta: "OrderedDict[str, Any]" = OrderedDict()
    if base_name:
        meta["creature_of"] = base_name
    meta["creature_class"] = get_creature(base_name).get("class", "") if base_name else ""
    meta["form"] = form_token
    if size:
        meta["size"] = size
    suppress_groups, suppress_fields = _suppression(form_token, slots)
    meta["suppress_groups"] = suppress_groups
    meta["suppress_fields"] = suppress_fields

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = meta
    document[_SPECIES_GROUP] = OrderedDict(
        (slot, slots[slot]) for slot in CREATURE_SLOTS if slots.get(slot)
    )
    return json.dumps(document, indent=2)


if _COMFY_AVAILABLE:

    class IdentityForgeCreature(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Render a character as a non-human creature / monster / alien form."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            names = get_creature_names()
            slot_options = [_FOLLOW, _RANDOM_SLOT] + names
            return io.Schema(
                node_id="IdentityForgeCreature",
                display_name="Identity Forge Creature",
                category="conditioning/character",
                description=(
                    "Render a character as a creature / monster / alien. Pick one "
                    "('Random - <class>' scopes to only animals / insects / monsters / "
                    "aliens / …), then override individual anatomy slots to build a "
                    "hybrid (a mantis body with a sloth's head). Wire 'character_json' "
                    "into Identity Forge's 'archetype_json', or chain after an Archetype "
                    "/ Cosplayer via 'upstream'."
                ),
                inputs=[
                    io.Combo.Input(
                        "creature",
                        options=[_NONE, _RANDOM_ANY] + list(_RANDOM_CLASS_LABELS) + names,
                        default=_NONE,
                        tooltip="The base creature. 'None' emits nothing; 'Random - any' "
                                "picks across every class; 'Random - <class>' stays within "
                                "one (only a monster / only an insect / …). Type to filter.",
                    ),
                    io.Combo.Input(
                        "form",
                        options=[_FORM_LABEL_ANTHRO, _FORM_LABEL_FERAL, _FORM_LABEL_SUBTLE,
                                 _FORM_LABEL_RANDOM],
                        default=_FORM_LABEL_ANTHRO,
                        tooltip="'Anthropomorphic' keeps a humanoid body (costumes still "
                                "fit); 'Feral / full creature' drops human clothing/makeup "
                                "for a true beast; 'Subtle hybrid' keeps the human and adds "
                                "creature accents. 'Random' rolls one with the seed.",
                    ),
                    io.Int.Input(
                        "seed",
                        default=0,
                        min=0,
                        max=0xFFFFFFFFFFFFFFFF,
                        control_after_generate="randomize",
                        tooltip="Seed for the random creature / slot / form picks. The "
                                "control below defaults to 'randomize'.",
                    ),
                    # --- hybrid slots (collapsed by default in the UI) ---------
                    io.Combo.Input("head", options=slot_options, default=_FOLLOW,
                                   tooltip="Head slot. 'Follow base' uses the chosen "
                                           "creature; 'Random' picks any; or pick a creature "
                                           "to graft its head (a sloth head on a mantis)."),
                    io.Combo.Input("eyes", options=slot_options, default=_FOLLOW,
                                   tooltip="Eyes slot. Follow base / Random / a creature."),
                    io.Combo.Input("integument", options=slot_options, default=_FOLLOW,
                                   tooltip="Skin / fur / scales / chitin / shell. Follow "
                                           "base / Random / a creature."),
                    io.Combo.Input("arms", options=slot_options, default=_FOLLOW,
                                   tooltip="Arms slot. Follow base / Random / a creature."),
                    io.Combo.Input("hands", options=slot_options, default=_FOLLOW,
                                   tooltip="Hands / claws slot. Follow base / Random / a "
                                           "creature."),
                    io.Combo.Input("legs_feet", options=slot_options, default=_FOLLOW,
                                   tooltip="Legs / feet slot. Follow base / Random / a "
                                           "creature."),
                    io.Combo.Input("tail", options=slot_options, default=_FOLLOW,
                                   tooltip="Tail slot. Follow base / Random / a creature "
                                           "(many creatures have none)."),
                    io.Combo.Input("wings", options=slot_options, default=_FOLLOW,
                                   tooltip="Wings slot. Follow base / Random / a creature "
                                           "(many creatures have none)."),
                    # --- detail (collapsed by default in the UI) ---------------
                    io.Combo.Input("integument_finish", options=[_AUTO] + _FINISHES,
                                   default=_AUTO,
                                   tooltip="Surface finish on the skin/hide (matte, glossy, "
                                           "iridescent, slimy, bioluminescent, …)."),
                    io.Combo.Input("palette", options=[_AUTO] + _PALETTES, default=_AUTO,
                                   tooltip="Recolour the integument. 'Auto' uses the "
                                           "creature's own colour."),
                    io.Combo.Input("size_scale", options=[_AUTO] + _SIZES, default=_AUTO,
                                   tooltip="Scale of the subject (tiny … towering). "
                                           "'Auto' leaves it unstated."),
                    io.String.Input(
                        "more_features",
                        multiline=True,
                        default=_MORE_HELP,
                        tooltip="Optional free text. 'slot: phrase' overrides a slot "
                                "(head, eyes, integument, arms, hands, legs_feet, tail, "
                                "wings, extras); a line with no ':' is an extra feature. "
                                "Unlimited detail without more widgets.",
                    ),
                    io.String.Input(
                        "upstream",
                        default="",
                        optional=True,
                        force_input=True,
                        tooltip="Optional: connect another preset's character_json here to "
                                "stack presets (Cosplayer -> Creature -> Identity Forge). "
                                "This node wins where they overlap; set 'None' to pass the "
                                "upstream through unchanged.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            own = build_creature_json(
                kwargs.get("creature", _NONE),
                int(kwargs.get("seed", 0)),
                kwargs.get("form", _FORM_LABEL_ANTHRO),
                kwargs.get("head", _FOLLOW),
                kwargs.get("eyes", _FOLLOW),
                kwargs.get("integument", _FOLLOW),
                kwargs.get("arms", _FOLLOW),
                kwargs.get("hands", _FOLLOW),
                kwargs.get("legs_feet", _FOLLOW),
                kwargs.get("tail", _FOLLOW),
                kwargs.get("wings", _FOLLOW),
                kwargs.get("integument_finish", _AUTO),
                kwargs.get("palette", _AUTO),
                kwargs.get("size_scale", _AUTO),
                kwargs.get("more_features", ""),
            )
            character_json = merge_preset_documents(kwargs.get("upstream", ""), own)
            return io.NodeOutput(character_json)
