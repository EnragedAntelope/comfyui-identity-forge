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

from collections import OrderedDict
import json
import random
import re
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
try:
    from ..data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_categories,
    )
    from ..data.fields import FIELD_DEFINITIONS
    from .identity_forge import group_fields, merge_preset_documents
except ImportError:  # pragma: no cover — standalone/test context
    from data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_categories,
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

#: Special Random scopes that filter the pool by a character *attribute* instead of
#: its franchise category. They are offered ahead of the franchise categories in the
#: node's ``random_scope`` dropdown and combine with the gender scope. Each maps to a
#: predicate over a cosplayer entry. "Non-human / colored" reuses the body-paint
#: detector (an all-over non-natural skin/fur/scale colour) plus the explicit
#: ``skin``/``body_paint`` overrides; "Masked" keys off ``covers_face``. Kept in the
#: node (not the data layer) so ``get_cosplayer_names`` stays a pure franchise filter.
def _scope_is_giant(entry: dict) -> bool:
    return entry.get("size_scale") == "giant"


def _scope_is_tiny(entry: dict) -> bool:
    return entry.get("size_scale") == "tiny"


def _scope_is_masked(entry: dict) -> bool:
    return bool(entry.get("covers_face"))


def _scope_is_nonhuman(entry: dict) -> bool:
    override = entry.get("body_paint")
    if override is not None:
        return bool(override)
    if entry.get("skin"):
        return True
    return bool(_BODY_PAINT_RE.search(entry.get("costume", "")))


_SPECIAL_SCOPES: "dict[str, Any]" = {
    "Giant characters": _scope_is_giant,
    "Tiny characters": _scope_is_tiny,
    "Non-human / colored": _scope_is_nonhuman,
    "Masked": _scope_is_masked,
}

#: A face-visible character whose colour covers the whole body (and therefore the
#: face) — She-Hulk's green, Mystique's blue, a Nightsister's chalk-white — is
#: written with a canonical skin-native phrasing: "smooth, flawless <colour> skin"
#: for even colour, or "uniform, all-over <colour> <material>" when the surface is
#: textured (scaled/craggy/pebbled…). Live A/B testing (0.52) showed skin-native
#: wording renders a uniform colour, while "body paint"/"dye" wording made models
#: layer a streaky coat OVER a human tone — so the paint word was swept out. The
#: older "an even … coat of <colour> …" anchor is still recognised (fur/feather/
#: flame entries and user_options presets may use it). When any marker is present
#: the engine must NOT also randomize a human skin tone, complexion, skin marks, or
#: skin-toned makeup underneath: those describe a natural-coloured face that t2i
#: models then render *under* the colour, leaving the face pale while the body is
#: coloured. This regex detects the marker so the contradicting fields can be
#: locked absent (the costume's own colour becomes the only skin descriptor).
_BODY_PAINT_RE = re.compile(
    r"\ban even\b.*?\bcoat of\b|\bsmooth, flawless\b|\buniform, all-over\b",
    re.IGNORECASE,
)

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


#: Pulls the colour descriptor out of the canonical body-paint phrase so it can be
#: planted in the (otherwise empty) ``skin_tone`` slot as a *colour anchor*. Body
#: paint suppresses the human ``skin_tone``/``complexion``, which leaves the opening
#: prose with no skin colour at all ("...with a slim build and tall.") — the costume
#: clause is the only mention, so t2i routinely defaults the high-attention *face* to
#: a human tone (the Poison Ivy white-face / TMNT pale-face bug). Re-injecting the
#: colour ("...and vivid green skin") anchors face + body. Captures the words between
#: the canonical marker and the material noun: "smooth, flawless <rich green> skin",
#: "uniform, all-over <dark blue scaled> skin", or the legacy
#: "an even, smooth coat of <vivid green> body paint".
_BODY_PAINT_COLOR_RE = re.compile(
    r"\b(?:coat of|smooth, flawless|uniform, all-over)\s+(.+?)\s+"
    r"(?:body\s+paint|skin|fur|scales?|hide|carapace|exoskeleton|plating|paint|coat)\b",
    re.IGNORECASE,
)


def _body_paint_skin_color(entry: dict, costume: str) -> str | None:
    """The colour string to anchor in ``skin_tone`` for a body-paint character.

    An explicit ``skin`` entry key wins (free-text, for phrasings the regex misses or
    where a cleaner word is wanted); otherwise the colour is auto-derived from the
    canonical "coat of <colour> <material>" clause. Returns ``None`` when neither is
    available (the field then stays suppressed, as before).
    """
    explicit = entry.get("skin")
    if explicit:
        return str(explicit)
    match = _BODY_PAINT_COLOR_RE.search(costume)
    return match.group(1).strip() if match else None


#: A bald character states it in the costume by convention ("a bald head", "a
#: clean-shaven bald scalp"). ``\bbald\b`` matches that without catching "baldric"
#: (the 'r' after 'd' breaks the word boundary). When present the builder locks the
#: scalp-hair fields absent so a randomized "His hair is ..." line cannot contradict
#: the bald head (the Doctor Manhattan / Voldemort bald-but-random-hair bug). An
#: explicit ``bald`` entry key overrides the auto-detection. ``facial_hair`` is left
#: alone (bald + beard is natural); "clean-shaven" handles that separately below.
_BALD_RE = re.compile(r"\bbald\b", re.IGNORECASE)
_BALD_SUPPRESS: dict[str, str] = {
    "hair_color": "None",
    "hair_length": "None",
    "hair_texture": "None",
    "hair_style": "None",
    "hair_part": "None",
    "hair_highlights": "None",
    "hair_accessory": "None",
}

#: "clean-shaven" / "clean shaven" in the costume locks ``facial_hair`` absent so a
#: random beard does not sprout on a face the costume explicitly calls bare.
_CLEAN_SHAVEN_RE = re.compile(r"clean[ -]?shaven", re.IGNORECASE)
_CLEAN_SHAVEN_SUPPRESS: dict[str, str] = {"facial_hair": "clean shaven"}

# Size-scale entries ("giant"/"tiny") pair with a hand-authored ``scale_prose``
# phrase that REPLACES the human ``height`` value (applied in build_cosplayer_json).
# ``height``'s gender pools are identical, so the engine's gender gate passes any
# free text and the lead sentence renders it verbatim ("… with an athletic build,
# colossal and fifty feet tall, and warm tan skin") — the same free-text-lock route
# the body-paint skin_tone anchor uses. Early placement is deliberate: T2I models
# weight lead tokens, so the scale lands up front and the costume prose reinforces
# it later.


#: Per-look keys an alternate costume may override (everything else stays shared at
#: entry level). Deliberately excludes ``size_scale``/``scale_prose``/``physique``/
#: ``franchise``/``gender`` so a giant stays giant (and the same person-underneath) no
#: matter which costume is rolled -- the alternates vary only the *worn look*.
_LOOK_OVERRIDE_KEYS = (
    "costume", "signature", "mask", "covers_face", "covers_body",
    "covers_hair", "prop", "body_paint", "skin", "eyes",
)


def _pick_look(entry: dict, rng: random.Random) -> dict:
    """Return ``entry`` with one costume from its ``costumes`` pool applied.

    An entry may carry an optional ``costumes`` list of *alternate looks*, each a
    plain costume string or a dict overlay of :data:`_LOOK_OVERRIDE_KEYS`. The pool is
    the canonical ``costume`` followed by those alternates; one is ``rng``-picked per
    seed, so a specific OR Random character rotates looks deterministically. Shared
    keys (size_scale, physique, franchise, gender) are never per-look, so scale and
    the person underneath are stable across costumes.

    Returns ``entry`` unchanged (and consumes no RNG) when there are no alternates, so
    the 900+ single-costume entries reproduce their existing seeds exactly.
    """
    alternates = entry.get("costumes")
    if not alternates:
        return entry
    pool: list[dict] = [{"costume": entry["costume"]}]
    pool += [alt if isinstance(alt, dict) else {"costume": alt} for alt in alternates]
    chosen = rng.choice(pool)
    merged = dict(entry)
    merged.pop("costumes", None)
    # Overlay only the keys the chosen look actually sets; absent keys fall back to the
    # entry-level value already in ``merged`` (a plain-string alternate sets only
    # ``costume``). A face-visible alternate of a masked character sets
    # ``covers_face: False``; the stale entry-level ``mask`` is then ignored downstream
    # because the mask clause is only attached when ``covers_face`` is truthy.
    for key in _LOOK_OVERRIDE_KEYS:
        if key in chosen:
            merged[key] = chosen[key]
    return merged


def _is_bald(entry: dict, costume: str) -> bool:
    """Whether the costume describes a bald head (so scalp hair must be hidden)."""
    override = entry.get("bald")
    if override is not None:
        return bool(override)
    return bool(_BALD_RE.search(costume))


def _apply_suppress(
    document: "OrderedDict[str, Any]", suppress: dict[str, str], *, override: bool
) -> None:
    """Lock each field in ``suppress`` to its absent token in ``document``.

    ``override`` replaces an existing locked value (used by body paint, which must
    beat an explicit physique skin tone); otherwise an explicit signature/physique
    lock is preserved (used by bald / clean-shaven, which only fill randomized gaps).
    """
    for field_name, absent in suppress.items():
        group = FIELD_DEFINITIONS.get(field_name, {}).get("group", "Other")
        bucket = document.setdefault(group, OrderedDict())
        if override or field_name not in bucket:
            bucket[field_name] = absent


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
        predicate = _SPECIAL_SCOPES.get(category)
        if predicate is not None:
            # Attribute scope (Giant/Tiny/Non-human/Masked): filter the gender pool
            # by the predicate instead of by franchise category.
            pool = [n for n in get_cosplayer_names(gender=gender)
                    if predicate(get_cosplayer(n))]
        else:
            pool = get_cosplayer_names(gender=gender, category=category)
        if not pool:  # empty (gender, scope) combo -> fall back to the full gender pool
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
    franchise/category, or to one of the attribute scopes (Giant / Tiny / Non-human /
    Masked); it is ignored when a specific character is selected.
    """
    rng = random.Random(seed)
    name = _resolve_character(character, rng, random_scope)
    if name is None:
        return "{}"

    # Resolve the character, then roll one of its costumes (a no-op for the common
    # single-costume entry). Rebinding ``entry`` to the merged look means every read
    # below transparently sees the chosen costume and its per-look overrides.
    entry = _pick_look(get_cosplayer(name), rng)

    covers = bool(entry.get("covers_face", False))
    # A full hard suit / armour / robot shell / exoskeleton hides the body's skin,
    # so worn jewellery and nails don't belong. Independent of the mask: unmasking
    # reveals the head, but the body stays encased.
    covers_body = bool(entry.get("covers_body", False))
    # A hood / cowl / lekku encloses the scalp while the face shows: hides the
    # randomized hair only (the engine drops the Hair group). Independent of the mask.
    covers_hair = bool(entry.get("covers_hair", False))
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
        ("covers_body", covers_body),
        ("covers_hair", covers_hair),
    ])
    size_scale = entry.get("size_scale", "")
    if size_scale:
        document["_meta"]["size_scale"] = size_scale
    document.update(group_fields(fields))
    # When an eye-colour override is in play, lock eye_shape to absent so the override
    # reads clean downstream ("crimson eyes", not "crimson deep-set eyes"). Injected
    # here, after group_fields (which strips "None" on the build side), because the
    # engine keeps a locked "None" as the absent state and omits it from its own prose
    # and JSON. setdefault preserves an explicit signature eye_shape if one was set.
    if entry.get("eyes"):
        for group_values in document.values():
            if isinstance(group_values, dict) and "eye_color" in group_values:
                # eye_shape is the single eye-structure field (it also encodes size),
                # so locking it absent is enough for the free-text override to read clean.
                group_values.setdefault("eye_shape", "None")
                break
    # Costume-driven suppressions: lock fields absent that the costume prose has
    # already settled, so the engine's randomizer can't add a value that contradicts
    # the look. Injected here for the same reason as the eye locks above: group_fields
    # strips "None" on the build side, but the engine keeps a locked "None"/absent
    # token as the absent state and omits it from prose and JSON.
    #
    # Body paint runs even for a masked face: covers_face hides the Face/Hair/Makeup
    # groups but NOT the Body-group skin_tone, so an all-over coat ("flame", "scaled
    # skin") would otherwise still report a stray human skin tone under it.
    if _is_body_paint(entry, costume):
        _apply_suppress(document, _BODY_PAINT_SUPPRESS, override=True)
        # Re-plant the paint colour in the (now-suppressed) skin_tone slot so the
        # opening prose anchors it ("...and vivid green skin") instead of leaving the
        # face uncoloured for t2i to default to a human tone. Free-text value, voiced
        # verbatim like the ``eyes`` override; the demographics formatter guards the
        # trailing " skin" so "...scaled-skin" / "...fur" don't read doubled.
        skin_color = _body_paint_skin_color(entry, costume)
        if skin_color:
            group = FIELD_DEFINITIONS.get("skin_tone", {}).get("group", "Body")
            document.setdefault(group, OrderedDict())["skin_tone"] = skin_color
    # Bald / clean-shaven only fill randomized gaps (override=False) so an entry can
    # still lock a deliberate topknot or stray hairs via its signature. Auto-detected
    # "bald" in the prose suppresses scalp hair only (a bald man may keep a beard); an
    # explicit ``bald: True`` is the stronger "fully hairless head" assertion used for
    # creatures/aliens, so it also clears facial hair.
    if _is_bald(entry, costume):
        _apply_suppress(document, _BALD_SUPPRESS, override=False)
        if entry.get("bald") is True:
            _apply_suppress(document, _CLEAN_SHAVEN_SUPPRESS, override=False)
    if _CLEAN_SHAVEN_RE.search(costume):
        _apply_suppress(document, _CLEAN_SHAVEN_SUPPRESS, override=False)
    # Size-scale: replace the human height with the entry's authored scale_prose so
    # the scale reads in the lead sentence (strongest T2I position) instead of a
    # contradictory "very tall"/"petite". override=True beats any physique.height
    # lock. Validator guarantees scale_prose accompanies size_scale.
    if entry.get("size_scale"):
        _apply_suppress(document, {"height": entry["scale_prose"]}, override=True)
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
                        options=[_SCOPE_ANY] + list(_SPECIAL_SCOPES) + get_cosplayer_categories(),
                        default=_SCOPE_ANY,
                        tooltip="Limits the 'Random — …' picks. Attribute scopes come "
                                "first (Giant / Tiny characters, Non-human / colored, "
                                "Masked), then one franchise/category (only Anime & Manga, "
                                "only Marvel, …). 'Any' = no limit. Combines with the gender "
                                "scope; no effect when a specific character is picked.",
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
