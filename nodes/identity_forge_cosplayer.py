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

When the signature object is *worn* in the costume rather than held (a bullwhip
coiled on a belt, swords sheathed at a hip), the entry also carries an optional
``prop_costume``: the identical look with that object removed. Switching the prop
on swaps it in, so the item moves from the belt to the hand instead of rendering
twice. See ``build_cosplayer_json``.

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
    from .identity_forge import (
        group_fields, merge_preset_documents, _SPECIES_GROUP, _FORM_FERAL,
    )
    from .identity_forge_creature import _suppression
except ImportError:  # pragma: no cover — standalone/test context
    from data.cosplayers import (
        COSPLAYERS, get_cosplayer, get_cosplayer_names,
        get_cosplayer_categories,
    )
    from data.fields import FIELD_DEFINITIONS
    from nodes.identity_forge import (
        group_fields, merge_preset_documents, _SPECIES_GROUP, _FORM_FERAL,
    )
    from nodes.identity_forge_creature import _suppression

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

#: The one ``body_plan`` value. A named fictional beast whose canonical form is a body
#: **a person cannot occupy** -- a quadruped, a serpent, a six-legged sky bison -- so
#: the mascot-suit reading ("a person inside a Pikachu suit") is not available and the
#: whole ``covers_face`` + ``mask`` + body-as-costume idiom renders it wrong: as a
#: human in a fur suit, with human demographics, human proportions, jewellery and a
#: "He *wears* a ... body" verb.
#:
#: Such an entry emits the Creature node's ``Species & Anatomy`` payload instead of a
#: costume, so the engine's existing species prose path and Feral suppression handle
#: it. There is deliberately no second value: ``body_plan`` is a switch onto that
#: path, not a taxonomy. Which characters qualify is settled in
#: docs/architecture.md -> "Animal characters split four ways".
_FERAL = "feral"

#: Entry keys carrying anatomy for a feral entry. ``mask`` -> the ``head`` slot and
#: ``costume`` -> the ``integument`` slot are REUSED rather than renamed, so
#: ``_pick_look``, ``entry_hash``, the Masked / Mascot / Non-human scopes and the
#: gallery keep working on a feral entry untouched. Everything else goes in
#: ``anatomy``, keyed by the Creature node's own slot names.
_FERAL_HEAD_SLOT = "head"
_FERAL_INTEGUMENT_SLOT = "integument"

#: Default ``pose`` pool for a feral subject, drawn per seed and locked.
#:
#: :data:`~data.fields.QUADRUPED_UNPERFORMABLE_POSES` removes the gestures that reach
#: for arms and hips, but the survivors still include human *stances* -- "in a relaxed
#: contrapposto stance", "sitting cross-legged", "kneeling gracefully". Culling those
#: would mean splitting the two largest pose families and repricing them, which is the
#: expensive kind of change the backlog warns about; authoring a replacement is the
#: cheap kind, and it is the pattern the pack already uses for exactly this shape of
#: problem (``scale_prose`` replaces ``height``, a body-paint colour replaces
#: ``skin_tone``, ``eyes`` replaces ``eye_color``).
#:
#: **Bias-free by construction**: nothing is ever drawn from the global ``pose`` pool
#: for a feral entry, so no family weight moves and no other entry is affected. The
#: values are body-plan neutral on purpose -- they read on a quadruped, a serpent or a
#: winged beast alike -- and an entry with an unusual plan overrides them with its own
#: ``poses`` list.
#: Every value must complete "He/She/They is ..." -- the pose clause is a bare
#: ``{subject} is {pose}``, so a noun-absolute ("head lowered and turned toward the
#: viewer") renders as "He is head lowered ...". Participles only. They also avoid a
#: possessive: "with the head raised", never "with its head raised", because the
#: sentence subject is a gendered pronoun and "its" fights it.
_FERAL_POSES: tuple[str, ...] = (
    "standing still with the head raised",
    "standing in full profile with the whole body in frame",
    "moving forward at an easy pace",
    "standing with the head lowered and turned toward the viewer",
    "at rest on the ground with the body settled",
    "standing square with the head turned to one side",
)

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
    # A feral entry sets covers_face (that is what drops the human head), but it is
    # not *masked* -- there is no person wearing anything. It has its own scope, and
    # docs/reference/cosplayers.md already makes the same distinction (`beast`, not
    # `masked`), so the scopes must agree with it. Same for the mascot scope below.
    return bool(entry.get("covers_face")) and entry.get("body_plan") != _FERAL


def _scope_is_nonhuman(entry: dict) -> bool:
    override = entry.get("body_paint")
    if override is not None:
        return bool(override)
    if entry.get("skin"):
        return True
    return bool(_BODY_PAINT_RE.search(entry.get("costume", "")))


def _scope_is_mascot(entry: dict) -> bool:
    """A full head-and-body covering: a person inside a mascot/creature suit.

    0.82.0, proposed in docs/suggested-additions.md and finally built. Derived
    from the two flags rather than a new schema key, so it counts
    ``user_options.json`` additions and self-maintains as the roster grows -- and
    because it is a *filter over the existing pool* it adds no entries and cannot
    shift any field's distribution. Bias-free by construction.

    It earns its place on discoverability: ~120 entries carry both flags (Pikachu,
    the TMNT, Bugs Bunny, Godzilla, Moogle, Teemo, ...) and there was no way to
    find them short of luck.

    Feral entries are excluded (0.95.0). They carry both flags too, but the scope means
    *a person inside a suit*, which is precisely what a feral entry is not -- and the
    two scopes would otherwise overlap completely, so picking "Mascot / full-suit"
    could hand you a bantha.
    """
    return (bool(entry.get("covers_body")) and bool(entry.get("covers_face"))
            and entry.get("body_plan") != _FERAL)


def _scope_is_feral(entry: dict) -> bool:
    """A named beast rendered as itself -- see :data:`_FERAL` and ``body_plan``.

    Derived from the schema key rather than hand-listed, exactly like
    :func:`_scope_is_mascot`: it is a *filter over the existing pool*, so it adds no
    entries, cannot shift any field's distribution, and counts ``user_options.json``
    additions for free.
    """
    return entry.get("body_plan") == _FERAL


_SPECIAL_SCOPES: "dict[str, Any]" = {
    "Giant characters": _scope_is_giant,
    "Tiny characters": _scope_is_tiny,
    "Non-human / colored": _scope_is_nonhuman,
    "Masked": _scope_is_masked,
    "Mascot / full-suit": _scope_is_mascot,
    "Beast / non-humanoid": _scope_is_feral,
}

#: Minimum roster size for a franchise to earn its own Random scope. The nine
#: broad categories leave the biggest ones unbrowsable (Video Games alone is 268
#: characters), but exposing all 263 franchises does not work either: 135 of them
#: are singletons and would each return one fixed character forever -- the reason
#: franchise scoping was scoped and rejected once before. A threshold keeps only
#: the franchises deep enough for a Random pick to feel random.
_FRANCHISE_SCOPE_MINIMUM: int = 8

#: Prefix so franchise scopes read as one family in the dropdown, sorted together
#: and visibly distinct from the attribute scopes and the broad categories.
_FRANCHISE_SCOPE_PREFIX = "Franchise: "


def _build_franchise_scopes() -> "dict[str, Any]":
    """Derive ``{"Franchise: X": predicate}`` for every franchise big enough to browse.

    Built from :data:`COSPLAYERS` at import, so it picks up ``user_options.json``
    additions and self-maintains as the roster grows -- no hand-kept list to drift.
    Franchises whose name is already a broad category (Marvel, DC, Star Wars) are
    skipped: they would be an exact duplicate of the category entry.
    """
    counts: dict[str, int] = {}
    for entry in COSPLAYERS.values():
        franchise = entry.get("franchise", "")
        if franchise:
            counts[franchise] = counts.get(franchise, 0) + 1
    categories = set(get_cosplayer_categories())
    scopes: "dict[str, Any]" = {}
    for franchise in sorted(counts):
        if counts[franchise] < _FRANCHISE_SCOPE_MINIMUM or franchise in categories:
            continue
        # Bind the franchise per iteration; a closure over the loop variable would
        # leave every predicate matching the last franchise only.
        scopes[f"{_FRANCHISE_SCOPE_PREFIX}{franchise}"] = (
            lambda entry, _f=franchise: entry.get("franchise") == _f
        )
    return scopes


#: Franchise scopes, offered after the broad categories in ``random_scope``.
_FRANCHISE_SCOPES: "dict[str, Any]" = _build_franchise_scopes()

#: Every predicate-driven scope (attribute + franchise), which is what
#: ``_resolve_character`` looks a scope up in. The two are kept apart above only so
#: the dropdown can order them: attributes first, then categories, then franchises.
_PREDICATE_SCOPES: "dict[str, Any]" = {**_SPECIAL_SCOPES, **_FRANCHISE_SCOPES}

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
#:
#: ``ethnicity`` joined at 0.78.0 for the same reason the rest of this map exists.
#: It had been the one skin-describing field left randomizing under a full-body
#: colour, and it is the *loudest* of them: the lead sentence opened "a 19-year-old
#: Chilean man ... with chalk-white skin", and t2i resolves the high-attention face
#: token to the ethnicity, rendering an ordinary human face above a coloured body.
#: That is the Lobo report ("a hispanic guy wearing Lobo's clothes but not his
#: face") and it reproduces at every seed. Same argument, same verdict as 0.65.0,
#: which added ``ethnicity`` to ``_CONCEALED_SHELL_SKIN_FIELDS`` for fully-encased
#: characters: when no natural skin is visible there is nothing for an ethnicity to
#: attach to, so naming one only fights the colour the costume just established.
#:
#: **Seeds drift for body-paint characters** (only). Locking a field makes the
#: randomizer skip it, so ``ethnicity``'s draw leaves the RNG stream and every
#: field resolved after it shifts. Scope is exactly the entries where
#: ``_is_body_paint`` is true; plain runs, archetypes and unpainted cosplayers are
#: byte-identical. Verified by previewing Lobo at seeds 0/2 before and after.
_BODY_PAINT_SUPPRESS: dict[str, str] = {
    "skin_tone": "None",
    "ethnicity": "None",
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
    "costume", "signature", "mask", "anatomy_note", "covers_face", "covers_body",
    "covers_hair", "prop", "prop_costume", "body_paint", "skin", "eyes",
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
    # ``prop_costume`` is the same look as ``costume`` minus the worn prop, so it is
    # only ever valid for the costume it ships with. An alternate that changes the
    # costume without supplying its own drops it rather than pairing the base
    # entry's prop-less look with a different alternate's costume.
    if "costume" in chosen and "prop_costume" not in chosen:
        merged.pop("prop_costume", None)
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


#: (character, scope) combos whose pool size has already been announced this
#: session, so the info line below prints at most once per combo (not per seed).
_SCOPE_NOTICE_SEEN: set[tuple[str, str]] = set()


#: Outcomes of narrowing the Random pool, reported by :func:`_announce_scope`.
_SCOPE_OK = "ok"                    # the (gender, scope) combo had characters
_SCOPE_GENDER_RELAXED = "gender"    # scope kept, gender dropped to fill it
_SCOPE_ABANDONED = "abandoned"      # scope itself matched nothing (result out of scope)


def _announce_scope(
    character: str, category: str, gender: str | None, count: int, outcome: str
) -> None:
    """Print a one-time console note of the in-scope pool size for a Random combo.

    A franchise/attribute scope narrows the Random pool. A *small* pool (e.g.
    ``Masked`` + ``female`` = 8) then repeats characters across seeds, which reads
    like the scope was ignored even though it is working. Printing the pool size
    once per (character, scope) combo makes the scope legible without spamming the
    console every generation.

    ``outcome`` distinguishes the two degraded cases, which are very different for
    the user: :data:`_SCOPE_GENDER_RELAXED` still honours the franchise they asked
    for (only the *source* gender was dropped, which crossplay makes harmless),
    while :data:`_SCOPE_ABANDONED` means the scope matched nothing at all and the
    result really is out of scope.
    """
    key = (character, category)
    if key in _SCOPE_NOTICE_SEEN:
        return
    _SCOPE_NOTICE_SEEN.add(key)
    gender_word = gender.lower() if gender else "any-gender"
    plural = "s" if count != 1 else ""
    if outcome == _SCOPE_GENDER_RELAXED:
        print(f"[IdentityForgeCosplayer] scope '{category}' has no {gender_word} "
              f"characters; keeping the scope and picking from all {count} "
              f"character{plural} in it instead. Set the person's gender on the "
              f"IdentityForge node for crossplay.")
    elif outcome == _SCOPE_ABANDONED:
        print(f"[IdentityForgeCosplayer] '{character}' + scope '{category}' matched no "
              f"characters; falling back to the full {gender_word} pool "
              f"({count} characters). The result will be OUT OF SCOPE.")
    else:
        print(f"[IdentityForgeCosplayer] '{character}' + scope '{category}': "
              f"{count} character{plural} in scope.")


def _resolve_character(
    character: str, rng: random.Random, category: str = _SCOPE_ANY
) -> str | None:
    """Resolve a combo selection to a concrete character name.

    Returns ``None`` for "None", an unknown name, or a Random pick over an empty
    pool (e.g. "Random — male" before any male characters are added). ``category``
    limits the Random picks to one franchise/category ("Any" = no limit). A specific
    character selection ignores ``category``.

    When a (gender, scope) combo is empty the **scope wins and the gender is
    relaxed**: asking for "Random — male" + "Franchise: Date A Live" (an all-female
    cast) returns a Date A Live character rather than an out-of-scope one from the
    whole roster. The scope is the deliberate, visible choice; the source gender
    only pre-filters the pool, and the *person* cosplaying is gendered separately on
    the IdentityForge node, so crossplay already makes the relaxed pick valid.
    Only a scope that matches nothing at all falls back to the full roster, loudly.
    """
    if character in _RANDOM_POOLS:
        gender = _RANDOM_POOLS[character]
        scoped = category != _SCOPE_ANY
        predicate = _PREDICATE_SCOPES.get(category)

        def in_scope(for_gender: str | None) -> list[str]:
            names = get_cosplayer_names(gender=for_gender)
            if predicate is not None:
                # Attribute scope (Giant/Tiny/Non-human/Masked) or a single-franchise
                # scope: filter the gender pool by the predicate instead of by category.
                return [n for n in names if predicate(get_cosplayer(n))]
            return get_cosplayer_names(gender=for_gender, category=category)

        pool = in_scope(gender)
        outcome = _SCOPE_OK
        if not pool and scoped and gender is not None:
            # Keep the scope the user picked; drop only the source-gender filter.
            pool = in_scope(None)
            outcome = _SCOPE_GENDER_RELAXED
        if not pool:
            # The scope itself is empty (only reachable via user_options.json).
            outcome = _SCOPE_ABANDONED if scoped else _SCOPE_OK
            pool = get_cosplayer_names(gender=gender)
        if not pool:
            print(f"[IdentityForgeCosplayer] No characters available for '{character}'.")
            return None
        if scoped:
            _announce_scope(character, category, gender, len(pool), outcome)
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
    "holding …". It is a no-op for characters without a ``prop``. When the entry
    also defines ``prop_costume`` — the same look with a *worn* signature object
    removed — that costume is swapped in, so Indiana Jones' whip leaves his belt
    when it reaches his hand rather than being rendered twice.

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
    # A character whose signature object is *worn* rather than held (Indiana Jones'
    # bullwhip is coiled on his belt, Zoro's three swords are sheathed at his hip)
    # describes it in the costume, so emitting the prop as well renders the object
    # twice -- 0.63.0 caught a real double-whip render this way. Such an entry may
    # carry ``prop_costume``: the same look with the object removed, used only when
    # the prop is switched on, so the item moves from the belt to the hand instead of
    # appearing in both. Entries without one are unaffected (worn stays worn).
    if include_prop and entry.get("prop") and entry.get("prop_costume"):
        costume = entry["prop_costume"]
    # The head travels in `_meta` rather than being glued onto the costume, so the
    # engine can give it its own sentence ahead of the clothing. Appending it here
    # made it the last item of a "He wears ..." list, where t2i models reliably
    # ignored it -- see the note on `_MASK_KEY` in identity_forge.py.
    head_text = entry["mask"] if (covers and not unmask and entry.get("mask")) else None
    # A feral entry's ``mask`` IS its head slot, voiced by the species path, so the
    # separate mask sentence would describe the same head twice. Unmasking is a no-op
    # for the same reason there is no mascot reading: there is no person underneath a
    # bantha to reveal.
    feral = entry.get("body_plan") == _FERAL
    if feral:
        head_text = None
        # ...and unmasking must not clear ``covers_face`` either. It normally does, to
        # reveal the randomized head under a helmet; on a beast that head does not
        # exist, and clearing the flag let the human Face group back in ("His
        # expression is warm smile" on a bantha). Caught by
        # FeralBodyPlanTests.test_unmask_is_a_no_op_for_a_beast.
        unmask = False

    # The costume drives IdentityForge's hidden outfit_description override; the
    # signature look (hair/eyes) is always applied; physique only in Full mode.
    # A feral entry has no costume: its ``costume`` is the integument slot and goes to
    # the species group below, so nothing locks ``outfit_description`` (the Feral form
    # suppresses the whole Clothing group anyway).
    fields: dict[str, str] = {} if feral else {"outfit_description": costume}
    fields.update(entry.get("signature", {}))
    # Free-text canonical eye-colour override for characters whose eyes fall outside
    # the believable-people eye_color pool (e.g. "crimson", "golden cat-slit pupils").
    # eye_color has identical gender pools, so the downstream gender gate passes the
    # free-text value straight to the prose. Applied in both look levels.
    if entry.get("eyes"):
        fields["eye_color"] = entry["eyes"]
    # ``physique`` is normally Full-character-only, because Costume-only deliberately
    # randomizes *the person wearing the costume*. A feral entry has no person
    # underneath -- the physique IS the animal -- so it applies in both look levels.
    # This is also what keeps a costume-asserted body trait from contradicting an
    # unpinned random field (docs/suggested-additions.md "Still to consider" #2).
    if feral or look_level == _FULL:
        fields.update(entry.get("physique", {}))
    # Signature held prop → hidden held_item lock (opt-in; off by default).
    if include_prop and entry.get("prop"):
        fields["held_item"] = entry["prop"]
    # Feral pose: authored, seed-picked and locked, so the global pose pool is never
    # drawn from and no family weight moves (see _FERAL_POSES). An entry may pin its
    # own ``poses`` for an unusual body plan (a serpent cannot walk, a phoenix flies),
    # and an explicit signature ``pose`` still wins over both.
    if feral and "pose" not in fields:
        fields["pose"] = rng.choice(tuple(entry.get("poses") or _FERAL_POSES))

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
    if head_text:
        document["_meta"]["mask"] = head_text
    # One sentence about the BODY, voiced ahead of the clothing exactly as the mask
    # is -- the only route a maskless entry has to state a limb count where the
    # render will act on it (see ``_ANATOMY_NOTE_KEY`` in identity_forge.py).
    # Feral entries are excluded at the data layer: they carry a per-slot ``anatomy``
    # dict instead, and voicing both would describe the body twice. Unmasking does
    # NOT clear it -- it is not part of the head.
    if not feral and entry.get("anatomy_note"):
        document["_meta"]["anatomy_note"] = entry["anatomy_note"]
    size_scale = entry.get("size_scale", "")
    if size_scale:
        document["_meta"]["size_scale"] = size_scale
    # A feral entry emits the Creature node's document shape: the Feral form token, the
    # species noun the prose leads with, and the suppression the form implies. The
    # suppression is computed by the Creature node's own ``_suppression`` rather than
    # restated here, so the two producers cannot drift -- a beast and a Feral creature
    # drop exactly the same human fields, and any future change to the form lands on
    # both at once.
    if feral:
        slots: "OrderedDict[str, str]" = OrderedDict()
        if entry.get("mask"):
            slots[_FERAL_HEAD_SLOT] = entry["mask"]
        slots[_FERAL_INTEGUMENT_SLOT] = costume
        for slot, text in (entry.get("anatomy") or {}).items():
            slots[slot] = text
        document["_meta"]["creature_of"] = entry.get("creature_of", "") or name
        document["_meta"]["creature_class"] = entry.get("creature_class", "Mammals")
        document["_meta"]["form"] = _FORM_FERAL
        suppress_groups, suppress_fields = _suppression(_FORM_FERAL, slots)
        document["_meta"]["suppress_groups"] = suppress_groups
        document["_meta"]["suppress_fields"] = suppress_fields
    document.update(group_fields(fields))
    if feral:
        document[_SPECIES_GROUP] = slots
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
    if not feral and _is_body_paint(entry, costume):
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
    if not feral and _is_bald(entry, costume):
        _apply_suppress(document, _BALD_SUPPRESS, override=False)
        if entry.get("bald") is True:
            _apply_suppress(document, _CLEAN_SHAVEN_SUPPRESS, override=False)
    if not feral and _CLEAN_SHAVEN_RE.search(costume):
        _apply_suppress(document, _CLEAN_SHAVEN_SUPPRESS, override=False)
    # Size-scale: replace the human height with the entry's authored scale_prose so
    # the scale reads in the lead sentence (strongest T2I position) instead of a
    # contradictory "very tall"/"petite". override=True beats any physique.height
    # lock. Validator guarantees scale_prose accompanies size_scale.
    # 0.95.0: gated on ``scale_prose`` rather than ``size_scale``, so a FERAL entry can
    # state a concrete size without claiming a giant/tiny *tier*. The tier is a scene
    # control (it forces the framing and location that can show the scale); most beasts
    # -- a tauntaun, a chocobo, a direwolf -- are simply an animal-sized animal, and
    # "very tall" from the human height pool says nothing useful about one. The
    # validator allows the pairing only for a feral entry; every tiered entry still
    # ships both, and the size_scale-requires-scale_prose rule is unchanged.
    #
    # Feral ``scale_prose`` is worded as an APPOSITIVE ("small, about two feet long"),
    # not as the conjunction the other 101 entries use ("tiny and barely a foot tall").
    # That is deliberate: a human entry has three core items (build, height, skin tone)
    # so ``_join`` commas them, but a feral entry has two -- no skin tone -- and the
    # conjunctive form renders "with a stocky build and tiny and barely two feet long".
    # Do not align the two forms.
    if entry.get("scale_prose"):
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
                                "below). Type to filter the list.\n"
                                "Many characters ship several canonical outfits (Leia's "
                                "white gown / Hoth / Boushh, Harley's classic and Arkham "
                                "looks). One is chosen per seed, so re-rolling the seed "
                                "on a fixed character cycles their wardrobe.",
                    ),
                    io.Combo.Input(
                        "random_scope",
                        options=([_SCOPE_ANY] + list(_SPECIAL_SCOPES)
                                 + get_cosplayer_categories() + list(_FRANCHISE_SCOPES)),
                        default=_SCOPE_ANY,
                        tooltip="Limits the 'Random — …' picks. Attribute scopes come "
                                "first (Giant / Tiny characters, Non-human / colored, "
                                "Masked, Mascot / full-suit), then the broad "
                                "categories (only Anime & Manga, "
                                "only Marvel, …), then 'Franchise: …' entries for single "
                                "franchises with enough characters to browse (Pokemon, "
                                "Final Fantasy, Mortal Kombat, …). 'Any' = no limit. "
                                "Combines with the gender scope; no effect when a specific "
                                "character is picked. The console prints the in-scope pool "
                                "size the first time you use a combo.",
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
