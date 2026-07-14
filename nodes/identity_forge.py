"""IdentityForge node — character description randomizer with constraint engine.

This module is split in two halves:

* **Engine** — pure functions (``generate_character`` and helpers) with no
  ComfyUI dependency, so they can be unit-tested without a ComfyUI install.
* **Node** — the V3 ``io.ComfyNode`` wrapper, only defined when ``comfy_api``
  is importable.

Design notes
------------
* ``gender`` and ``hair_color_scope`` are *control* fields (``"control": True``
  in :data:`data.fields.FIELD_DEFINITIONS`). They are read straight from their
  widgets, never randomized, and never emitted as descriptive text — they steer
  the option pools instead.
* A value that means "absent" (``"None"``, ``"no bag"``, ``"clean shaven"`` …)
  is skipped in the prose for readability but kept in the JSON for fidelity.
* The prose summarizes; the JSON is the complete, structured record.
"""
from __future__ import annotations

from collections import OrderedDict
import json
import random
import re
from typing import Any

# Dual import: package-relative inside ComfyUI (avoids polluting sys.path with
# the generic "data"/"nodes" names), absolute when run standalone for tests.
try:
    from ..data.fields import (
        FIELD_DEFINITIONS, FIELD_FAMILIES, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS,
        ETHNICITY_REGION, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS,
    )
    from ..data.constraints import CONSTRAINT_RULES
except ImportError:  # pragma: no cover — standalone/test context
    from data.fields import (
        FIELD_DEFINITIONS, FIELD_FAMILIES, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS,
        ETHNICITY_REGION, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS,
    )
    from data.constraints import CONSTRAINT_RULES

# ---------------------------------------------------------------------------
# ComfyUI V3 API import — guarded so the engine helpers remain importable
# in environments where comfy_api is not installed (tests, CI).
# ---------------------------------------------------------------------------
try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

# ---------------------------------------------------------------------------
# Derived constants
# ---------------------------------------------------------------------------

#: Fields that never get a user-facing widget (engine-generated).
_HIDDEN_FIELDS: frozenset[str] = frozenset({"outfit_description", "held_item"})

#: Hidden fields that are nonetheless honoured as preset-supplied locks (a costume
#: override and a cosplayer's signature prop). Everything else hidden is engine-only.
_PRESET_HIDDEN_FIELDS: frozenset[str] = frozenset({"outfit_description", "held_item"})

#: Field groups that are cosmetic and anatomically gender-neutral: an *explicitly
#: locked* value here (from an archetype/cosplayer preset) survives a downstream
#: gender override, because a man can wear bold glam just as a woman can. This lets
#: a forced-Male drag performer keep its glam makeup while *random* men still default
#: to the natural male pool. Only fields whose pools actually differ by gender (e.g.
#: makeup_style) are affected; identical-pool fields already pass the gate.
_GENDER_FLEXIBLE_GROUPS: frozenset[str] = frozenset({"Makeup"})

#: ``set_all_fields`` control values. "All to None" omits every field still on
#: "Random" (a blank-slate baseline) so only locked fields appear; a wired
#: character's signature look is exempt (see :func:`resolve_locked_fields`).
_SET_ALL_OFF = "Off"
_SET_ALL_NONE = "All to None"

#: Reserved key (not a real field) carrying a cosplay character label from a
#: connected Cosplayer node's ``_meta`` through the parsed-archetype dict.
_COSPLAY_LABEL_KEY = "__cosplay_label__"

#: Reserved key carrying a cosplayer's ``covers_face`` flag (see below) through
#: the parsed-archetype dict, the same way the cosplay label travels.
_COVERS_FACE_KEY = "__covers_face__"

#: Reserved key carrying a cosplayer's ``covers_body`` flag through the parsed dict
#: (a full hard suit / armour / robot shell / exoskeleton — no skin for worn
#: jewellery to sit on).
_COVERS_BODY_KEY = "__covers_body__"

#: Reserved key carrying a cosplayer's ``covers_hair`` flag through the parsed dict
#: (a hood / cowl / helmet liner / replacing head-tails fully encloses the scalp,
#: but the face still shows — so hair is hidden while Face/Makeup stay).
_COVERS_HAIR_KEY = "__covers_hair__"

#: Top-level section name a Modifier node adds to the chained preset document,
#: holding ``{field_or_group: descriptor}`` style modifiers.
_MODIFIERS_DOC_KEY = "_modifiers"

#: Reserved key carrying the parsed modifiers dict through the flattened
#: parsed-archetype dict (double-underscored so it never collides with a field).
_MODIFIERS_KEY = "__modifiers__"

#: JSON group a Creature node adds, holding ``{slot: prose}`` anatomy (a creature
#: head, integument, limbs …). Rendered by a dedicated species path, not the human
#: field engine, so its keys are *not* :data:`FIELD_DEFINITIONS` fields.
_SPECIES_GROUP = "Species & Anatomy"

#: Reserved key carrying the parsed species payload (slots + form + suppression)
#: through the flattened parsed-archetype dict.
_SPECIES_KEY = "__species__"

#: Reserved key carrying an archetype's per-gender variant look blocks
#: (``{"Female": {...}, "Male": {...}}``) through the flattened parsed-archetype
#: dict. Folded into the locks *after* the gender coin-flip so one archetype
#: selection yields either a coherent male or female look.
_VARIANTS_KEY = "__variants__"

#: Canonical transformation-form tokens emitted in a creature document's ``_meta``
#: (the node maps its friendlier widget labels onto these). ``Anthropomorphic`` and
#: ``Feral`` lead the prose with the creature; ``Subtle`` keeps the human subject and
#: appends the creature features as accents.
_FORM_ANTHRO = "Anthropomorphic"
_FORM_FERAL = "Feral"
_FORM_SUBTLE = "Subtle"

#: Order anatomy slots are voiced / serialized in.
_SPECIES_SLOT_ORDER: tuple[str, ...] = (
    "head", "eyes", "integument", "arms", "hands", "legs_feet", "wings", "tail", "extras",
)

#: Field groups suppressed when a cosplayer sets ``covers_face`` — a full mask /
#: helmet / featureless head hides the randomized face, hair and makeup, so
#: describing them would only fight the costume at render time. Body and
#: demographics stay (the person under the mask is still a real body).
_CONCEALED_FACE_GROUPS: frozenset[str] = frozenset({"Face", "Hair", "Makeup"})
#: Individual head-worn fields (outside the above groups) a full mask also hides.
_CONCEALED_FACE_FIELDS: frozenset[str] = frozenset({"earrings", "piercings"})

#: Field groups suppressed when a cosplayer sets ``covers_body`` — a full hard
#: suit / armour / robot shell / exoskeleton leaves no bare skin for worn
#: jewellery or nails, so a randomized necklace/bracelet/ring/polish would only
#: render on top of the shell. Body and demographics stay (there is still a body,
#: and the silhouette has a height/build).
_CONCEALED_BODY_GROUPS: frozenset[str] = frozenset({"Jewelry & Nails"})

#: Individual fields dropped alongside ``_CONCEALED_BODY_GROUPS`` for a full shell:
#: ``accessories`` and ``bag`` (Clothing group) are worn/carried *on* the person —
#: sunglasses, a belt, a rattan bag — so a randomized draw would only render on top
#: of a mascot suit / armour shell (the sunglasses-on-Michelin-Man bug). The rest of
#: the Clothing group stays (the costume itself lives there via outfit_description).
_CONCEALED_BODY_FIELDS: frozenset[str] = frozenset({"accessories", "bag"})

#: Field groups suppressed when a cosplayer sets ``covers_hair`` — a hood / cowl /
#: helmet-liner (or alien head-tails) fully encloses the scalp while the face still
#: shows, so a randomized "Her hair is ..." line would only contradict the covering.
#: Narrower than ``covers_face`` (which also drops Face + Makeup): here the face is
#: visible, so only the Hair group goes.
_CONCEALED_HAIR_GROUPS: frozenset[str] = frozenset({"Hair"})

#: Scalp-hair fields dropped when ``hair_length`` resolves to "bald" — there is no
#: hair for a colour/texture/style/part/highlight/accessory to describe, so any of
#: them would only contradict the bald head. ``hair_length`` itself stays (it is
#: what voices the bald head) and ``facial_hair`` stays (bald + beard is natural).
#: Mirrors the Cosplayer node's ``_BALD_SUPPRESS`` for costume-declared bald heads.
_BALD_SCALP_FIELDS: tuple[str, ...] = (
    "hair_color", "hair_texture", "hair_style", "hair_part",
    "hair_highlights", "hair_accessory",
)

#: Body-group skin fields dropped when a character is BOTH fully masked
#: (``covers_face``) AND a full hard shell (``covers_body`` / ``_FULL_COVER_RE``):
#: the being is entirely encased, so a randomized human ``skin_tone`` would render as
#: a stray patch of bare skin under the armour/droid plating (Iron Man, 2-1B, 4-LOM).
#: ``covers_face`` already drops the other skin fields (complexion / skin_details /
#: freckles are Face group; skin_finish is Makeup); only ``skin_tone`` (Body) leaks.
_CONCEALED_SHELL_SKIN_FIELDS: frozenset[str] = frozenset({"skin_tone"})

#: Control fields: read from their toggle, never randomized, never described.
_CONTROL_FIELDS: frozenset[str] = frozenset(
    name for name, meta in FIELD_DEFINITIONS.items() if meta.get("control")
)

#: Canonical group ordering for prose and JSON output. ``Species & Anatomy`` sits
#: right after Demographics — it sets the substrate the rest is rendered on, and a
#: Modifier node can target the whole group by this name (it reads ``_GROUP_ORDER``).
_GROUP_ORDER: tuple[str, ...] = (
    "Demographics", _SPECIES_GROUP, "Body", "Face", "Hair", "Makeup",
    "Jewelry & Nails", "Clothing", "Setting & Shot",
)

#: Pronoun maps keyed by gender.
_SUBJ = {"Female": "She", "Male": "He", "Any": "They"}
_POSS = {"Female": "Her", "Male": "His", "Any": "Their"}
_GENDER_NOUN = {"Female": "woman", "Male": "man", "Any": "person"}

#: Values that read as "absent" and are skipped in prose.
_ABSENCE_EXACT: frozenset[str] = frozenset({
    "natural bare", "bare natural lips", "bare nails", "clean shaven", "none",
})

#: Gloved/gauntleted hands cover the fingers, so a randomized fingernail polish or
#: ring would render *on top of* the glove (a reported t2i bug). When the resolved
#: outfit covers the hands the engine forces the finger fields (nails, rings, and
#: ring-typed other_jewelry) absent — see ``generate_character``. ``_FINGERLESS_RE``
#: opts out: fingerless gloves expose the fingers, so nails/rings should still show.
#: Iconic power rings worn *over* the glove (Green Lantern, Sinestro) live in the
#: costume prose (outfit_description), not the ``rings`` field, so they are untouched.
_GLOVE_RE = re.compile(r"\b(?:glove|gauntlet|mitten)s?\b", re.IGNORECASE)
_FINGERLESS_RE = re.compile(r"fingerless", re.IGNORECASE)

#: An outfit that already includes headwear (a top hat, a helmet, a hood) can't
#: also wear a randomized hat from the ``accessories`` field — "a top hat …
#: accessorized with wide brim sun hat" stacks two hats (the reported quirk).
#: When the resolved outfit_description reads as headwear, the engine drops a
#: hat-valued ``accessories`` draw (non-hat accessories — sunglasses, belts,
#: scarves — still show; an explicit user lock is respected, as with gloves).
#: ``_HAT_ACCESSORY_VALUES`` mirrors the hat entries of the ``accessories``
#: pool in ``data/fields.py`` — keep the two in sync when editing that field.
_HAT_RE = re.compile(
    r"\b(?:hat|cap|beret|hood(?:ed)?|helm(?:et)?|cowl|crown|tiara|beanie|fedora|"
    r"turban|headdress|headpiece|headscarf|bonnet|sombrero|circlet|diadem|veil|"
    r"visor)s?\b",
    re.IGNORECASE,
)
_HAT_ACCESSORY_VALUES: frozenset[str] = frozenset({
    "wide brim sun hat", "baseball cap", "beret", "woven hat",
})

#: Costume phrases that mean the whole body is encased in a hard shell — a robot /
#: droid / powered armour / full plate / exoskeleton / carapace — so there is no
#: bare skin for worn jewellery or nails to sit on. Detected on the resolved
#: outfit_description; when matched (or the ``covers_body`` flag is set) the engine
#: drops the Jewelry & Nails group so a random necklace/ring/polish can't render on
#: top of the shell. Kept conservative (terms that imply full hard coverage, never
#: a bare-chested gladiator's "breastplate" or a partial "cybernetic arm").
_FULL_COVER_RE = re.compile(
    r"exoskeleton|carapace|\bdroid\b|\brobot\b|android|"
    r"power(?:ed)?[ -]armor|powered exosuit|\bexosuit\b|armored bodysuit|"
    r"plate armor|armor plating|beskar|mjolnir|bio-armor|suit of .{0,40}?armor",
    re.IGNORECASE,
)

#: Maximum constraint-propagation passes before giving up (cycle guard).
_MAX_CONSTRAINT_ITERATIONS: int = 12

#: Probability that a randomized skin tone is drawn from the ethnicity's
#: plausible band rather than the full spectrum. < 1.0 keeps real-world
#: diversity possible (and locking skin_tone bypasses the bias entirely).
SKIN_TONE_INBAND_PROBABILITY: float = 0.8

#: The believable human skin tones. A resolved ``skin_tone`` *outside* this set is a
#: non-human colour: a body-paint colour anchor (She-Hulk green, Mystique blue) or a
#: free-text ``skin`` override planted by the cosplayer builder. Such a colour must be
#: restated on the face (see _format_prose), because the opening sentence anchors it on
#: the body only and t2i otherwise renders the high-attention face from the (colourless)
#: facial-feature tokens, leaving it pale under the paint -- the green-body/white-face
#: bug. ``skin_tone``'s female/male pools are identical, so either list defines the set.
_STANDARD_SKIN_TONES: frozenset[str] = frozenset(
    FIELD_DEFINITIONS["skin_tone"]["female_options"]
)

#: Wardrobe modes: how the outfit picker maps to the gendered outfit buckets.
_WARDROBE_BY_GENDER: dict[str, str] = {
    "Female": "Feminine", "Male": "Masculine", "Any": "Any",
}

#: "Extra" fields (bags, jewellery, accessories) plus the two "sometimes" skin
#: features (freckles, distinguishing marks) whose single "absent" option is
#: otherwise drowned out by its present options — leaving ~90% of characters
#: over-accessorised / over-freckled. Each maps to (absent value, P(absent) at
#: "Balanced"); the accessory_density control scales that probability. Portrait-
#: rare items (bag, accessories) lean more absent than everyday jewellery
#: (necklace, earrings). Freckles/marks lean mostly-absent so they read as a
#: distinguishing feature, not a default.
_EXTRA_ABSENCE: dict[str, tuple[str, float]] = {
    "freckles_density": ("none", 0.72),
    "skin_details": ("no notable marks", 0.60),
    "bag": ("no bag", 0.65),
    "accessories": ("no accessories", 0.55),
    "hair_accessory": ("no hair accessory", 0.55),
    "watch_type": ("none", 0.60),
    "piercings": ("no piercings beyond ears", 0.60),
    "other_jewelry": ("no other jewelry", 0.50),
    "rings": ("none", 0.50),
    "bracelet": ("none", 0.50),
    "hair_highlights": ("none", 0.45),
    "necklace": ("no necklace", 0.40),
    "earrings": ("no earrings", 0.35),
}

#: Multiplier applied to each extra's base absence probability. ``None`` forces
#: absence; "Maximal" reproduces the old fully-accessorised behaviour.
_DENSITY_SCALE: dict[str, float | None] = {
    "None": None, "Minimal": 1.5, "Balanced": 1.0, "Maximal": 0.2,
}


def _maybe_absent(
    field_name: str, pool: list[str], density: str, rng: random.Random
) -> str | None:
    """Return the field's "absent" value if accessory density says to drop it.

    Returns ``None`` to mean "randomize normally". Only applies to the
    :data:`_EXTRA_ABSENCE` fields.
    """
    info = _EXTRA_ABSENCE.get(field_name)
    if info is None:
        return None
    absent_value, base = info
    if absent_value not in pool:
        return None
    scale = _DENSITY_SCALE.get(density, 1.0)
    if scale is None:  # "None" — always drop
        return absent_value
    return absent_value if rng.random() < min(base * scale, 0.95) else None


# ===========================================================================
# Small text helpers
# ===========================================================================

def _is_absent(value: str | None) -> bool:
    """True when a value means "nothing to describe" and should be skipped."""
    if not value or value in ("None", "Random"):
        return True
    if value == "none" or value.startswith("no "):
        return True
    return value in _ABSENCE_EXACT


def _a(word: str) -> str:
    """Return the indefinite article ("a"/"an") that fits ``word``."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def _an(value: str, noun: str = "") -> str:
    """Render ``value`` (optionally with a trailing ``noun``) with its article."""
    tail = f" {noun}" if noun else ""
    return f"{_a(value)} {value}{tail}"


def _join(items: list[str]) -> str:
    """Comma-join with an Oxford "and" before the final item."""
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _words(*items: str) -> str:
    """Space-join the non-empty arguments."""
    return " ".join(i for i in items if i)


def _dedupe(items: list[str]) -> list[str]:
    """Remove duplicates while preserving first-occurrence order."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# ===========================================================================
# Randomization engine (pure functions)
# ===========================================================================

def _presentation_mode(gender: str, wardrobe: str) -> str:
    """Resolve the wardrobe *presentation* — ``"Feminine"`` / ``"Masculine"`` / ``"Any"``.

    "Match gender" follows the character's gender (Female→Feminine, Male→Masculine,
    Any→Any); every other wardrobe value is an explicit presentation the user chose
    to mix. Drives both the outfit pool and the masculine jewellery trim so a man's
    accessories match the wardrobe he is actually wearing.
    """
    return _WARDROBE_BY_GENDER.get(gender, "Any") if wardrobe == "Match gender" else wardrobe


def _build_option_pool(
    field_name: str,
    field_def: dict,
    gender: str,
    resolved: dict[str, str],
) -> list[str]:
    """Return the valid randomization options for a field under ``gender``.

    Handles the ``hair_color`` / ``hair_color_scope`` interaction.
    """
    if gender == "Female":
        base = list(field_def["female_options"])
    elif gender == "Male":
        base = list(field_def["male_options"])
    else:  # "Any" — union of both genders' pools
        base = _dedupe(field_def["female_options"] + field_def["male_options"])

    if field_name == "hair_color" and resolved.get("hair_color_scope") == "Natural only":
        natural = set(field_def.get("natural_hair_colors", base))
        base = [c for c in base if c in natural]

    # An already-present hair_style (a lock — styles randomize after lengths)
    # implies scalp hair exists, so never draw a bald head under it: the bald
    # scrub spares locked styles, which would leave "bald ... high ponytail".
    if field_name == "hair_length" and resolved.get("hair_style"):
        base = [v for v in base if v != "bald"]

    if field_name == "location":
        setting = resolved.get("location_setting", "Any indoor/outdoor")
        if setting == "Studio / solid backdrop":
            base = [loc for loc in base if loc in STUDIO_BACKDROPS]
        elif setting == "Indoor":
            # Indoor real locations only — never an outdoor scene or a studio sweep.
            base = [loc for loc in base if loc not in OUTDOOR_LOCATIONS
                    and loc not in STUDIO_BACKDROPS]
        elif setting == "Outdoor":
            base = [loc for loc in base if loc in OUTDOOR_LOCATIONS]
        else:  # "Any indoor/outdoor" (default): every real location, never a studio
            base = [loc for loc in base if loc not in STUDIO_BACKDROPS]

    return base


def _gender_permits(field_def: dict, gender: str, value: str) -> bool:
    """Whether ``value`` is allowed for ``gender`` by the field's gender pools.

    Only the *gender* dimension is checked (the raw ``female_options`` /
    ``male_options`` lists), never scope/location coherence — so an intentionally
    locked fantasy hair colour under a "Natural only" scope is left untouched.
    A field whose two pools are identical is not gender-gated and always passes.
    """
    female = field_def.get("female_options")
    male = field_def.get("male_options")
    if female is None or male is None or female == male:
        return True
    if gender == "Female":
        return value in female
    if gender == "Male":
        return value in male
    return value in female or value in male  # "Any" — union of both pools


def _gender_from_locks(locked: dict[str, str]) -> str | None:
    """Infer a concrete gender from anatomically gender-specific locks.

    Used to resolve a "Any" gender widget into a coherent man/woman: an explicit
    lock on a single-gender anatomical field (``facial_hair`` beard -> Male, a
    feminine ``bust`` -> Female) decides the gender so the user's choice is honored
    instead of coin-flipped away. Cosmetic/stylable fields are deliberately ignored
    (they are gender-flexible). Returns ``"Female"``/``"Male"`` when exactly one
    gender is implied, else ``None`` (nothing implied, or contradictory locks).
    """
    implied: set[str] = set()
    for field in ("facial_hair", "bust"):
        value = locked.get(field)
        if not value or value in ("Random", "None") or _is_absent(value):
            continue
        field_def = FIELD_DEFINITIONS[field]
        in_female = value in field_def["female_options"]
        in_male = value in field_def["male_options"]
        if in_male and not in_female:
            implied.add("Male")
        elif in_female and not in_male:
            implied.add("Female")
    return implied.pop() if len(implied) == 1 else None


def _bias_skin_tone(pool: list[str], ethnicity: str | None, rng: random.Random) -> list[str]:
    """Optionally narrow the skin-tone pool to the ethnicity's plausible band.

    A soft bias: with probability :data:`SKIN_TONE_INBAND_PROBABILITY` the pool
    is restricted to the band; otherwise the full pool is kept, so any tone
    remains possible. Returns ``pool`` unchanged when the ethnicity is unmapped.
    """
    band = ETHNICITY_REGION.get(ethnicity or "")
    if not band or rng.random() >= SKIN_TONE_INBAND_PROBABILITY:
        return pool
    in_band = [tone for tone in pool if tone in set(SKIN_TONE_BANDS.get(band, ()))]
    return in_band or pool


def _pick_family_weighted(field_name: str, pool: list[str], rng: random.Random) -> str:
    """Weighted two-tier pick for any field registered in :data:`FIELD_FAMILIES`:
    choose a family (weighted by its frozen original size), then a variant
    uniformly within it.

    This keeps each family's overall share independent of how many variants it
    holds, so adding variants subdivides a family's slice instead of inflating it
    (the bias-safe channel for growing a flat field). Because each family's weight
    equals its original variant count, the pick reproduces a flat uniform draw
    until new variants are added. Variants are intersected with ``pool`` (and
    empty families dropped) so any upstream filtering -- e.g. the location_setting
    indoor/outdoor/studio scope or a hair-length constraint -- still applies;
    falls back to a flat pick if the field has no families or nothing maps.
    """
    field_families = FIELD_FAMILIES.get(field_name)
    if not field_families:
        return rng.choice(pool)
    families = [
        (fam["weight"], [v for v in fam["variants"] if v in pool])
        for fam in field_families.values()
    ]
    families = [(weight, variants) for weight, variants in families if variants]
    # Pool values outside every family are user_options.json additions (shipped
    # options always partition exactly — validator-enforced). Give them an
    # implicit leftover family weighted by its size: each such value then draws
    # at exactly the flat 1-in-N share the frozen family weights reproduce, so
    # user additions are reachable without disturbing the built-in distribution.
    # With no user file the leftover is empty and this is a no-op.
    covered = {v for fam in field_families.values() for v in fam["variants"]}
    leftover = [v for v in pool if v not in covered]
    if leftover:
        families.append((len(leftover), leftover))
    if not families:
        return rng.choice(pool)
    chosen = rng.choices(families, weights=[weight for weight, _ in families])[0]
    return rng.choice(chosen[1])


def _weighted_choice(
    field_def: dict, pool: list[str], gender: str, rng: random.Random
) -> str:
    """Pick from ``pool`` honoring a field's draw-weight maps.

    A field may carry draw-weight maps ({value: weight}) to lean the random draw
    without duplicating pool entries (the validator rejects duplicates). Two maps
    compose: ``weights`` applies to every gender (e.g. bleached eyebrows are rare
    for all), ``male_weights`` is a male-only overlay that wins on key collision
    (e.g. men lean toward 'no makeup' and away from silky-glossy hair). Weights may
    be floats so a single value can sit below its peers' implicit weight of 1.
    Missing values weigh 1; a single ``rng.choices`` call keeps the RNG stream
    shape identical to ``rng.choice``. Unweighted fields stay flat-uniform. Used by
    both the initial random fill and the constraint engine's re-picks so a
    down-weighted value stays rare even after an exclusion re-roll.
    """
    weights_map = field_def.get("weights")
    male_weights = field_def.get("male_weights") if gender == "Male" else None
    if weights_map or male_weights:
        combined = {**(weights_map or {}), **(male_weights or {})}
        weights = [combined.get(value, 1) for value in pool]
        return rng.choices(pool, weights=weights)[0]
    return rng.choice(pool)


def _randomize_fields(
    locked: dict[str, str],
    gender: str,
    hair_color_scope: str,
    accessory_density: str,
    location_setting: str,
    rng: random.Random,
) -> dict[str, str]:
    """Fill every unlocked, non-control field from its option pool.

    ``locked`` maps field_name → user-chosen value (already excludes control
    and hidden fields). The returned dict contains every field.
    """
    resolved: dict[str, str] = {
        "gender": gender,
        "hair_color_scope": hair_color_scope,
        "location_setting": location_setting,
    }
    resolved.update(locked)

    for field_name, field_def in FIELD_DEFINITIONS.items():
        if field_name in _HIDDEN_FIELDS or field_name in _CONTROL_FIELDS:
            continue
        if field_name in resolved:  # locked
            continue

        pool = _build_option_pool(field_name, field_def, gender, resolved)
        if field_name == "skin_tone":
            pool = _bias_skin_tone(pool, resolved.get("ethnicity"), rng)
        forced_absent = _maybe_absent(field_name, pool, accessory_density, rng)
        if forced_absent is not None:
            resolved[field_name] = forced_absent
        elif field_name in FIELD_FAMILIES and pool:
            # Bias-safe weighted pick for grown fields (hair_style, expression,
            # pose, mood, lighting, location). _maybe_absent is RNG-neutral for
            # these (none are density-gated), so seeds stay stable for the field.
            resolved[field_name] = _pick_family_weighted(field_name, pool, rng)
        elif pool:
            resolved[field_name] = _weighted_choice(field_def, pool, gender, rng)
        elif field_def["optional"]:
            resolved[field_name] = "None"
        else:  # non-optional field with an empty pool — fall back to raw list
            raw = field_def["male_options"] if gender == "Male" else field_def["female_options"]
            resolved[field_name] = raw[0] if raw else "None"

    return resolved


def _apply_constraints(
    resolved: dict[str, str],
    gender: str,
    locked: set[str],
    rng: random.Random,
    presentation: str = "Masculine",
) -> list[str]:
    """Apply :data:`CONSTRAINT_RULES` until stable. Returns warning messages.

    Locked fields are never silently overwritten: when a constraint would
    change a locked field, the lock wins and a warning is recorded instead.

    ``presentation`` is the resolved wardrobe presentation. Rules flagged
    ``presentation_gated`` (the masculine-default jewellery/nail trims) apply only
    when a man reads ``"Masculine"``; a Feminine/"Any" wardrobe skips them so a
    deliberately femme male look keeps feminine-coded pieces available. The default
    is ``"Masculine"`` so a caller that omits it keeps the historical male defaults.
    """
    warnings: list[str] = []
    warned: set[tuple[str, str]] = set()

    def warn(field: str, detail: str) -> None:
        key = (field, detail)
        if key not in warned:
            warned.add(key)
            warnings.append(f"[IdentityForge] {detail}")

    for _ in range(_MAX_CONSTRAINT_ITERATIONS):
        changed = False

        for rule in CONSTRAINT_RULES:
            # A masculine-default trim only fires when the man reads Masculine; a
            # Feminine/"Any" wardrobe leaves the feminine-coded pool intact.
            if rule.get("presentation_gated") and presentation != "Masculine":
                continue
            # Trigger values are concrete option values (e.g. "no makeup",
            # "Natural only"); match exactly. The "absence" notion applies only
            # to prose rendering, never to whether a rule fires.
            if resolved.get(rule["field"]) != rule["value"]:
                continue

            if rule["type"] == "exclusion":
                target = rule["excludes_field"]
                excluded = set(rule["excludes_values"])
                if resolved.get(target) not in excluded:
                    continue
                if target in locked:
                    # Contrapositive repair: the locked target keeps its value, so
                    # re-roll the randomized *trigger* away from every value that
                    # excludes it (a locked "sleek bun" re-rolls a random "buzzed
                    # very short" length). Only a real, unlocked, non-control
                    # trigger can move; otherwise (both locked, or a gender /
                    # scope trigger) fall back to warn-and-keep as before.
                    trigger = rule["field"]
                    trig_def = FIELD_DEFINITIONS.get(trigger)
                    if (trig_def is not None and trigger not in locked
                            and not trig_def.get("control")):
                        conflicting = {
                            r["value"] for r in CONSTRAINT_RULES
                            if r["type"] == "exclusion" and r["field"] == trigger
                            and r["excludes_field"] == target
                            and resolved[target] in set(r["excludes_values"])
                        }
                        pool = [v for v in _build_option_pool(trigger, trig_def, gender, resolved)
                                if v not in conflicting]
                        if pool:
                            resolved[trigger] = _weighted_choice(trig_def, pool, gender, rng)
                            changed = True
                            continue
                    warn(target, f"'{rule['field']}={rule['value']}' conflicts with "
                                 f"locked '{target}={resolved[target]}'; keeping lock.")
                    continue
                field_def = FIELD_DEFINITIONS.get(target)
                if field_def is None:
                    continue
                pool = [v for v in _build_option_pool(target, field_def, gender, resolved)
                        if v not in excluded]
                if pool:
                    resolved[target] = _weighted_choice(field_def, pool, gender, rng)
                    changed = True
                elif field_def["optional"]:
                    resolved[target] = "None"
                    changed = True
                else:
                    # Non-optional field with no allowed option left: the value is
                    # stuck at an excluded one. Don't flag a change (a no-op flag
                    # would churn iterations and mask the contradiction) -- surface
                    # it so the offending constraint/pool can be fixed.
                    warn(target, f"'{rule['field']}={rule['value']}' excludes every "
                                 f"option for required field '{target}'; left at "
                                 f"'{resolved.get(target)}'.")

            else:  # requirement
                target = rule["requires_field"]
                required = rule["requires_value"]
                if resolved.get(target) == required:
                    continue
                if target in locked:
                    # An absence-requiring rule (e.g. "no makeup" wants
                    # eye_makeup="no eyeshadow") is already satisfied when the lock
                    # holds a *different but equally absent* value ("None"): both
                    # render nothing, so warning is pure noise. Stay silent for that
                    # case; only a lock that holds a real, present value (e.g.
                    # lips_makeup="classic red" vs. "bare natural lips") is a genuine
                    # contradiction worth surfacing.
                    if _is_absent(required) and _is_absent(resolved.get(target)):
                        continue
                    warn(target, f"'{rule['field']}={rule['value']}' wants "
                                 f"'{target}={required}' but '{target}' is locked to "
                                 f"'{resolved.get(target)}'; keeping lock.")
                    continue
                resolved[target] = required
                changed = True

        if not changed:
            break

    return warnings


def _resolve_outfit_description(
    resolved: dict[str, str], gender: str, wardrobe: str, rng: random.Random
) -> str:
    """Pick an outfit matching ``outfit_style`` and the wardrobe mode.

    The pool is the style's ``unisex`` bucket plus the gendered bucket selected
    by ``wardrobe``: "Match gender" follows the character's gender, while
    "Feminine"/"Masculine"/"Any" let a user deliberately mix wardrobes.
    """
    buckets = OUTFIT_DESCRIPTIONS.get(resolved.get("outfit_style", "casual"))
    if not buckets:
        return ""
    mode = _presentation_mode(gender, wardrobe)
    pool = list(buckets.get("unisex", []))
    if mode == "Feminine":
        pool += buckets.get("female", [])
    elif mode == "Masculine":
        pool += buckets.get("male", [])
    else:  # "Any" — mix every wardrobe
        pool += buckets.get("female", []) + buckets.get("male", [])
    return rng.choice(pool) if pool else ""


# ===========================================================================
# Output formatting
# ===========================================================================

def _species_subject(species: dict, gender: str) -> str:
    """Return the lead noun for an Anthropomorphic / Feral creature subject.

    e.g. ``"anthropomorphic praying-mantis hybrid"`` or ``"monstrous dragon"``,
    optionally prefixed by a ``size`` ("towering …"). Falls back to the plain
    gender noun for the Subtle form (handled by the caller).
    """
    base = species.get("creature_of") or "creature"
    form = species.get("form", "")
    if form == _FORM_ANTHRO:
        noun = f"anthropomorphic {base} hybrid"
    elif form == _FORM_FERAL:
        creature_class = species.get("creature_class", "")
        noun = f"monstrous {base}" if creature_class in ("Monsters", "Aliens") else base
    else:
        return _GENDER_NOUN.get(gender, "person")
    size = species.get("size")
    return f"{size} {noun}" if size else noun


def _format_prose(
    resolved: dict[str, str], gender: str, cosplay_label: str | None = None,
    species: dict | None = None, hands_visible: bool = True,
) -> str:
    """Build a natural-language description from resolved field values.

    When ``cosplay_label`` is set, the prose is prefixed ``Cosplaying as <label>:``.
    When ``species`` carries anatomy slots, an Anthropomorphic / Feral form leads
    with the creature subject and weaves its features in; a Subtle form keeps the
    human subject and appends the creature features as accents.
    """
    r = resolved
    subj = _SUBJ.get(gender, "They")
    poss = _POSS.get(gender, "Their")
    has = "have" if gender == "Any" else "has"
    is_v = "are" if gender == "Any" else "is"
    wears = "wear" if gender == "Any" else "wears"
    bust_noun = "chest" if gender == "Male" else "bust"

    def g(field: str) -> str:
        """Value for ``field`` or '' when absent."""
        v = r.get(field, "")
        return "" if _is_absent(v) else v

    species = species or {}
    slots = species.get("slots") or {}
    form = species.get("form", "")
    species_lead = bool(slots) and form in (_FORM_ANTHRO, _FORM_FERAL)
    subject_noun = _species_subject(species, gender) if species_lead \
        else _GENDER_NOUN.get(gender, "person")
    # Anatomy phrases in reading order, plus any extras keyed outside the canon.
    anatomy = [slots[s] for s in _SPECIES_SLOT_ORDER if slots.get(s)]
    anatomy += [v for k, v in slots.items() if k not in _SPECIES_SLOT_ORDER and v]

    sentences: list[str] = []

    # --- Demographics + body core --------------------------------------
    lead_bits = [b for b in (f"{g('age')}-year-old" if g("age") else "", g("ethnicity")) if b]
    lead_tail = _words(*lead_bits, subject_noun)
    # Creature subjects pick their article ("An anthropomorphic …"); the human
    # default keeps the original literal "A " to avoid disturbing existing output.
    lead = f"{_a(lead_tail).capitalize()} {lead_tail}" if species_lead else "A " + lead_tail
    core = []
    if g("body_type"):
        core.append(_an(g("body_type"), "build"))
    if g("height"):
        core.append(g("height"))
    if g("skin_tone"):
        # Normally "{tone} skin" ("bronze skin"). A body-paint colour anchor may be a
        # free-text value that already ends in its own material noun ("dark blue
        # scaled-skin", "golden cheetah-fur") — don't double the noun in that case.
        tone = g("skin_tone")
        core.append(tone if re.search(r"\b(?:skin|fur|scales?|hide)$", tone) else f"{tone} skin")
    sentences.append(lead + (" with " + _join(core) if core else ""))

    # --- Creature anatomy ----------------------------------------------
    # Lead forms put the creature features right after the subject; the Subtle
    # form folds them in as accents on the otherwise-human description.
    if anatomy:
        connector = f"{subj} {has} " if species_lead else f"{subj} also {has} "
        sentences.append(connector + _join(anatomy))

    # --- Physique + body proportions -----------------------------------
    # Drop the fitness word when it merely restates the body_type silhouette
    # (e.g. "athletic build ... athletic physique"); body_type already carries it.
    physique = g("fitness_level")
    if physique and physique == g("body_type"):
        physique = ""
    body_detail = []
    if g("shoulder_width"):
        body_detail.append(f"{g('shoulder_width')} shoulders")
    if g("bust"):
        body_detail.append(_an(g("bust"), bust_noun))
    if g("waist"):
        body_detail.append(_an(g("waist"), "waist"))
    if g("hips"):
        body_detail.append(f"{g('hips')} hips")
    if g("neck_length"):
        body_detail.append(_an(g("neck_length"), "neck"))
    if g("posture"):
        body_detail.append(f"{g('posture')} posture")
    if physique:
        s = f"{subj} {has} {_an(physique, 'physique')}"
        if body_detail:
            s += " with " + _join(body_detail)
        sentences.append(s)
    elif body_detail:
        sentences.append(f"{subj} {has} " + _join(body_detail))

    # --- Face structure -------------------------------------------------
    face_struct = []
    if g("forehead"):
        face_struct.append(_an(g("forehead"), "forehead"))
    if g("cheekbones"):
        face_struct.append(f"{g('cheekbones')} cheekbones")
    if g("jawline"):
        face_struct.append(_an(g("jawline"), "jawline"))
    if g("chin"):
        face_struct.append(_an(g("chin"), "chin"))
    if g("face_shape"):
        s = f"{poss} face is {g('face_shape')}"
        if face_struct:
            s += " with " + _join(face_struct)
        sentences.append(s)
    elif face_struct:
        sentences.append(f"{poss} face has " + _join(face_struct))

    # --- Eyes / nose / lips / brows ------------------------------------
    features = []
    if g("eye_color") or g("eye_shape"):
        features.append(_words(g("eye_color"), g("eye_shape")) + " eyes")
    if g("nose"):
        features.append(_an(g("nose"), "nose"))
    if g("lips"):
        features.append(g("lips") + " lips")
    if g("eyebrows"):
        brows = g("eyebrows")
        features.append(brows if "brow" in brows else f"{brows} eyebrows")
    if g("smile_type"):
        # Mouth/smile state (kept coherent with expression by constraints.py). Named
        # smiles read as-is; the bare modifiers (asymmetric / broad / subtle dimpled)
        # qualify "smile"; "closed mouth" voices the no-smile state.
        smile = g("smile_type")
        if smile == "closed mouth":
            features.append("a closed mouth")
        elif smile in ("soft smile", "toothy grin"):
            features.append(_an(smile))
        else:
            features.append(_an(f"{smile} smile"))
    if features:
        sentences.append(f"{subj} {has} " + _join(features))

    # --- Face colour reinforcement (body-paint / exotic skin) ----------
    # The opening sentence anchors a non-human skin colour on the body only; the face
    # is otherwise described purely by colourless feature tokens, so t2i defaults it to
    # a human tone (the green-body / white-face bug). When skin_tone is a non-standard
    # colour AND the face is actually being described, restate the colour on the face so
    # the face region renders coloured too. A masked (covers_face) or creature-replaced
    # face has its Face-group fields popped before render, so face_struct/features are
    # empty there and this correctly does not fire (the head is the mask/creature).
    skin_color = g("skin_tone")
    if skin_color and skin_color not in _STANDARD_SKIN_TONES and (face_struct or features):
        face_color = (skin_color if re.search(r"\b(?:skin|fur|scales?|hide)$", skin_color)
                      else f"{skin_color} skin")
        sentences.append(f"{poss} face has the same {face_color}")

    # --- Hand colour reinforcement (body-paint / exotic skin) ----------
    # The same restatement as the face, for the hands: t2i renders bare hands (and
    # any nail polish) in a default human tone unless the body-paint colour is
    # restated there too -- the green-body / white-hands bug. Fires only when the
    # hands actually show as skin; gloves or a full shell hide them (their nails
    # were already dropped upstream), so neither hand colour nor nails are voiced
    # under a covering. Prose-only -- no RNG draws, so no randomization bias.
    if hands_visible and skin_color and skin_color not in _STANDARD_SKIN_TONES:
        hand_color = (skin_color if re.search(r"\b(?:skin|fur|scales?|hide)$", skin_color)
                      else f"{skin_color} skin")
        sentences.append(f"{poss} hands have the same {hand_color}")

    # --- Complexion / skin details -------------------------------------
    skin = []
    if g("complexion"):
        skin.append(_an(g("complexion"), "complexion"))
    if g("skin_details"):
        skin.append(g("skin_details"))
    if g("freckles_density") and "freckle" not in g("skin_details"):
        skin.append(f"{g('freckles_density')} freckles")
    if skin:
        sentences.append(f"{poss} skin shows " + _join(skin))

    # --- Hair -----------------------------------------------------------
    # "bald" is a head state, not a hair description — voice it as its own
    # sentence ("his head is bald", never "his hair is bald"). The engine has
    # already dropped the other scalp-hair fields for a bald head.
    if g("hair_length") == "bald":
        sentences.append(f"{poss} head is bald")
    hair_desc = ("" if g("hair_length") == "bald"
                 else _words(g("hair_length"), g("hair_texture"), g("hair_color")))
    if hair_desc:
        s = f"{poss} hair is {hair_desc}"
        if g("hair_style"):
            s += f", {g('hair_style')}"
        sentences.append(s)
    elif g("hair_style"):
        sentences.append(f"{poss} hair is {g('hair_style')}")
    hair_extra = []
    if g("hair_part"):
        part = g("hair_part")
        hair_extra.append(_an(part, "" if "part" in part else "part"))
    if g("hair_highlights"):
        hl = g("hair_highlights")
        hair_extra.append(hl if "highlight" in hl else f"{hl} highlights")
    if g("facial_hair"):
        fh = g("facial_hair")
        # Mass/plural values ("stubble", "mutton chops") read naturally bare;
        # the singular pieces ("full beard", "mustache") take an article.
        hair_extra.append(fh if fh in ("stubble", "mutton chops") else _an(fh))
    if g("hair_accessory"):
        acc = g("hair_accessory")
        # "... in/over hair" values are placement phrases; voice them with the
        # possessive ("tied in her hair") so they don't read as a bare "tied in
        # hair" stacked against the hair sentence. Option values stay untouched
        # (they are locked by archetypes/cosplayers) -- render-layer only.
        acc = re.sub(r"\b(in|over) hair$", rf"\1 {poss.lower()} hair", acc)
        # Plural pieces ("decorative hair pins") read naturally bare; singular
        # pieces take an article.
        hair_extra.append(acc if acc.endswith("s") else _an(acc))
    if hair_extra:
        sentences.append(f"{subj} {has} " + _join(hair_extra))

    # --- Makeup (skipped entirely when bare-faced) ---------------------
    # (field, noun, stem) — append " noun" only when the value doesn't already
    # carry the category (stem), avoiding "ombre lip lip colour" / "… liner
    # eyeliner" style doubling.
    if g("makeup_style"):
        makeup = [g("makeup_style")]
        for field, noun, stem in (
            ("eye_makeup", "eyeshadow", "shadow"), ("eyeliner", "eyeliner", "liner"),
            ("lashes", "lashes", "lash"), ("lips_makeup", "lip colour", "lip"),
            ("blush", "blush", "blush"), ("eyebrow_makeup", "brows", "brow"),
            ("contour", "contour", "contour"), ("highlight", "highlighter", "highlight"),
            ("skin_finish", "finish", "finish"),
        ):
            val = g(field)
            if val:
                makeup.append(val if stem in val else f"{val} {noun}")
        sentences.append(f"{subj} {wears} " + _join(makeup))

    # --- Jewellery & nails ---------------------------------------------
    jewelry = []
    for field in ("earrings", "necklace", "other_jewelry", "rings", "bracelet", "piercings"):
        if g(field):
            jewelry.append(g(field))
    if g("watch_type"):
        watch = g("watch_type")
        jewelry.append(_an(watch, "" if "watch" in watch else "watch"))
    if g("nails"):
        jewelry.append(f"{g('nails')} nails" if "nail" not in g("nails") else g("nails"))
    if jewelry:
        sentences.append(f"{subj} {has} " + _join(_dedupe(jewelry)))

    # --- Clothing -------------------------------------------------------
    # outfit_description already includes shoes/colour/pattern, so the separate
    # footwear/colour/pattern fields are only voiced when there is no full outfit.
    clothing = []
    outfit = g("outfit_description")
    if outfit:
        clothing.append(f"{subj} {wears} {outfit}")
    else:
        pattern_color = _words(g("clothing_color"), g("clothing_pattern"))
        if pattern_color:
            clothing.append(f"{subj} {wears} {pattern_color} clothing")
        if g("footwear"):
            clothing.append(f"in {g('footwear')}")
    if g("bag"):
        clothing.append(f"carrying {g('bag')}")
    if g("accessories"):
        clothing.append(f"accessorized with {g('accessories')}")
    if clothing:
        sentences.append(", ".join(clothing))

    # --- Pose & held item ----------------------------------------------
    # held_item is a hidden, preset-only field (a cosplayer's signature prop);
    # voiced here as "holding <value>", folded into the pose sentence when present.
    pose, held = g("pose"), g("held_item")
    if pose and held:
        sentences.append(f"{subj} {is_v} {pose}, holding {held}")
    elif pose:
        sentences.append(f"{subj} {is_v} {pose}")
    elif held:
        sentences.append(f"{subj} {is_v} holding {held}")

    # --- Setting & shot -------------------------------------------------
    scene = []
    if g("expression"):
        scene.append(f"{poss} expression is {g('expression')}")
    if g("location"):
        scene.append(f"set in {_a(g('location'))} {g('location')}")
    if g("lighting"):
        # lighting encodes time-of-day (golden hour / moonlight / midday sun), so the
        # separate time_of_day field was removed to avoid contradictions; season stands.
        scene.append(f"under {g('lighting')}")
    if g("season"):
        scene.append(f"during {g('season')}")
    if g("shot_type"):
        # No article: shot_type values vary wildly ("close-up portrait",
        # "from slightly behind…", "shot through a doorway") and "a/an" + value
        # reads badly or doubles "shot".
        scene.append(f"the framing is {g('shot_type')}")
    # Skip mood when it merely restates the expression (e.g. expression "confident"
    # + "confident mood"); expression is the face, mood the scene -- only redundant
    # when identical.
    if g("mood") and g("mood") != g("expression"):
        scene.append(f"with {_a(g('mood'))} {g('mood')} mood")
    if scene:
        sentences.append(_join(scene) if len(scene) > 1 else scene[0])

    text = ". ".join(s.strip() for s in sentences if s.strip())
    text = (text + ".") if text else ""
    if cosplay_label and text:
        return f"Cosplaying as {cosplay_label}: {text[0].lower() + text[1:]}"
    if cosplay_label:
        return f"Cosplaying as {cosplay_label}."
    return text


def group_fields(field_values: dict[str, str]) -> "OrderedDict[str, dict[str, str]]":
    """Nest ``{field: value}`` by group, in canonical group order.

    Control fields and absent sentinels (``"None"`` / ``"Random"``) are dropped.
    Shared by the JSON formatter and the archetype node so both emit the same
    shape.
    """
    grouped: "OrderedDict[str, dict[str, str]]" = OrderedDict(
        (group, {}) for group in _GROUP_ORDER
    )
    for field_name, value in field_values.items():
        if field_name in _CONTROL_FIELDS or value in ("None", "Random"):
            continue
        group = FIELD_DEFINITIONS.get(field_name, {}).get("group", "Other")
        grouped.setdefault(group, {})[field_name] = value
    return OrderedDict((group, fields) for group, fields in grouped.items() if fields)


def _as_dict(value: Any) -> dict:
    """Return ``value`` if it is a dict, else an empty dict."""
    return value if isinstance(value, dict) else {}


def _load_document(raw: str) -> dict:
    """Parse a preset JSON string into a dict; ``{}`` on empty/malformed input."""
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        print("[IdentityForge] Ignoring malformed preset JSON during merge.")
        return {}
    return data if isinstance(data, dict) else {}


def merge_preset_documents(upstream_json: str, own_json: str) -> str:
    """Merge two preset JSON documents, with ``own`` (downstream) winning.

    Lets the preset nodes chain: an upstream preset's ``character_json`` is merged
    *under* this node's own output, so wiring ``Archetype -> Cosplayer ->
    IdentityForge`` keeps both connected. A node set to ``"None"`` emits ``"{}"``,
    which here passes the upstream through unchanged. On overlap the downstream
    (own) document wins, field by field, including ``_meta`` keys. ``_meta`` is
    emitted first and groups follow :data:`_GROUP_ORDER` for readable output.

    Either input may be empty, ``"{}"`` or malformed; the result is always a
    valid JSON object string.
    """
    upstream = _load_document(upstream_json)
    own = _load_document(own_json)
    if not own:  # this node is inactive ("None") -> pass the upstream through
        return json.dumps(upstream, indent=2) if upstream else "{}"
    if not upstream:
        return json.dumps(own, indent=2)

    merged: "OrderedDict[str, Any]" = OrderedDict()
    meta = {**_as_dict(upstream.get("_meta")), **_as_dict(own.get("_meta"))}
    if meta:
        merged["_meta"] = OrderedDict(meta)
    # Canonical groups first, then any unexpected extras; own fields win on overlap.
    keys = [k for k in _GROUP_ORDER if k in upstream or k in own]
    keys += [
        k for k in (*upstream, *own)
        if k != "_meta" and k not in _GROUP_ORDER and k not in keys
    ]
    for key in keys:
        section = {**_as_dict(upstream.get(key)), **_as_dict(own.get(key))}
        if section:
            merged[key] = section
    return json.dumps(merged, indent=2)


def _format_json(
    resolved: dict[str, str], gender: str, hair_color_scope: str, wardrobe: str,
    cosplay_label: str | None = None, species: dict | None = None,
) -> str:
    """Build a JSON document: ``_meta`` plus fields nested by group.

    The seed is intentionally excluded — it is run-control noise, not part of
    the character description. A connected creature's ``Species & Anatomy`` group
    is re-emitted (in canonical order) alongside its identifying ``_meta``.
    """
    species = species or {}
    slots = species.get("slots") or {}

    meta: "OrderedDict[str, str]" = OrderedDict()
    if cosplay_label:
        meta["cosplay_of"] = cosplay_label
    if slots:
        for key in ("creature_of", "creature_class", "form"):
            if species.get(key):
                meta[key] = species[key]
    meta["gender"] = gender
    meta["hair_color_scope"] = hair_color_scope
    meta["wardrobe"] = wardrobe

    grouped = group_fields(resolved)
    if slots:
        anatomy: "OrderedDict[str, str]" = OrderedDict(
            (s, slots[s]) for s in _SPECIES_SLOT_ORDER if slots.get(s)
        )
        for slot, value in slots.items():  # any extras keyed outside the canon
            if slot not in anatomy and value:
                anatomy[slot] = value
        grouped[_SPECIES_GROUP] = anatomy

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = meta
    # Re-order so the (manually added) species group lands in canonical position.
    for group in _GROUP_ORDER:
        if group in grouped:
            document[group] = grouped[group]
    for group, fields in grouped.items():
        if group not in document:
            document[group] = fields
    return json.dumps(document, indent=2)


def _apply_modifiers(resolved: dict[str, str], modifiers: dict[str, str] | None) -> None:
    """Prepend style descriptors onto ``resolved`` values, in place.

    ``modifiers`` keys are either a field name (applies to that field only) or a
    group header (applies to every field in the group). A field key wins over a
    group key for the same field. Only *present* values are decorated — absent /
    ``"None"`` / suppressed fields are left untouched so a modifier styles an
    element without forcing one to appear.
    """
    if not modifiers:
        return
    for field, value in list(resolved.items()):
        if _is_absent(value):
            continue
        descriptor = modifiers.get(field)
        if descriptor is None:
            group = FIELD_DEFINITIONS.get(field, {}).get("group")
            descriptor = modifiers.get(group) if group else None
        if descriptor:
            resolved[field] = f"{descriptor} {value}"


def generate_character(
    seed: int,
    gender: str,
    locked: dict[str, str],
    hair_color_scope: str = "Natural only",
    wardrobe: str = "Match gender",
    accessory_density: str = "Balanced",
    location_setting: str = "Any indoor/outdoor",
    cosplay_label: str | None = None,
    covers_face: bool = False,
    covers_body: bool = False,
    covers_hair: bool = False,
    modifiers: dict[str, str] | None = None,
    species: dict | None = None,
    gender_variants: dict[str, dict[str, str]] | None = None,
) -> tuple[str, str]:
    """Engine entry point. Returns ``(prose, json_output)``.

    ``locked`` maps field_name → chosen value for every user-locked field
    (control fields excluded). A locked ``outfit_description`` is honoured as a
    costume, overriding the generated outfit (used by costume archetypes).

    ``cosplay_label`` (e.g. ``"2B (NieR: Automata)"``), when set by a connected
    Cosplayer node, prefixes the prose and is recorded in the JSON ``_meta``.

    ``covers_face`` (set by a full-mask cosplayer) drops the randomized face,
    hair and makeup so only the costume's mask/helmet is described.

    ``covers_body`` (set by a full hard-suit / armour / robot / exoskeleton
    cosplayer) drops the randomized Jewelry & Nails group so no necklace, ring or
    nail polish renders on top of the shell. When a character is both ``covers_face``
    and a full shell it is entirely encased, so the leaking Body ``skin_tone`` is
    dropped too (no bare skin shows under the armour/droid plating).

    ``covers_hair`` (set by a hooded / cowled / lekku cosplayer whose face still
    shows) drops only the randomized Hair group, so no "Her hair is ..." line
    contradicts the head covering while the face is still described.

    ``modifiers`` (set by a connected Modifier node) maps a field name or group
    header to a descriptor that is prepended to the matching resolved value(s),
    e.g. ``{"footwear": "sci-fi"}`` → "sci-fi white sneakers".

    ``species`` (set by a connected Creature node) carries non-human anatomy: a
    ``slots`` map of ``{slot: prose}``, a ``form`` token and ``suppress_groups`` /
    ``suppress_fields`` lists. The suppressed human fields are dropped (a creature
    head hides the face/hair, a creature integument hides the skin) and the slots
    are woven into both outputs by the species-aware formatters.

    ``gender_variants`` (set by a per-gender archetype) maps ``"Female"`` /
    ``"Male"`` to a look block; once the gender is settled the matching block is
    folded into the locks, so one archetype selection yields a coherent male or
    female look (e.g. a housewife dress vs a suburban-dad sweater-vest).
    """
    rng = random.Random(seed)
    # "None" locks the *absent* state (optional fields only); keep it. Only
    # "Random" means "engine, choose". ``outfit_description`` is hidden but may
    # be supplied as a costume override, so it is allowed through.
    locked_clean = {
        name: value
        for name, value in locked.items()
        if name in FIELD_DEFINITIONS
        and name not in _CONTROL_FIELDS
        and value != "Random"
        and (name not in _HIDDEN_FIELDS or name in _PRESET_HIDDEN_FIELDS)
    }
    # "Any" gender resolves to a concrete man or woman per seed so the person is
    # coherent: the gender gate and randomizer below then draw from a single
    # gender's pools (no beard on a bust, no "they/them" mix). An anatomically
    # gender-specific *lock* (a beard, a feminine bust) decides the gender so the
    # explicit choice is honored; otherwise it is an unbiased 50/50 coin-flip. The
    # deliberate full-mix "anything goes" mode -- both pools unioned, neutral
    # pronouns -- is preserved only when the user also sets wardrobe to "Any".
    if gender == "Any" and wardrobe != "Any":
        gender = _gender_from_locks(locked_clean) or rng.choice(["Female", "Male"])

    # A per-gender-variant archetype ships two look blocks; now that the gender is
    # settled, fold the matching block into the locks (the variant's look wins). This
    # lets one archetype selection render either a coherent male or female look. When
    # the gender is the neutral "Any" (the wardrobe="Any" escape hatch), coin-flip a
    # block so the outfit still reads coherent rather than half-mixed.
    if gender_variants:
        variant = gender_variants.get(gender)
        if variant is None and gender_variants:
            variant = gender_variants[rng.choice(sorted(gender_variants))]
        for name, value in (variant or {}).items():
            if (
                name in FIELD_DEFINITIONS
                and name not in _CONTROL_FIELDS
                and value != "Random"
                and (name not in _HIDDEN_FIELDS or name in _PRESET_HIDDEN_FIELDS)
            ):
                locked_clean[name] = value

    # The gender gate must hold for *injected* locks too. An archetype emits
    # look-defining fields (incl. facial_hair) and its own gender; when the
    # downstream gender widget overrides that gender, a value that is invalid for
    # the new gender — e.g. a male archetype's beard on a forced-Female character —
    # would otherwise be kept verbatim, bypassing the randomizer's gender pools and
    # the JS widget filter. Drop such values so the field re-randomizes within the
    # correct gender pool. "None" (an explicit omit) is gender-neutral and stays.
    for name, value in list(locked_clean.items()):
        if value == "None":
            continue
        field_def = FIELD_DEFINITIONS[name]
        if _gender_permits(field_def, gender, value):
            continue
        # A cosmetic field (makeup) that a preset explicitly locked is anatomically
        # gender-neutral; keep it when it's a real option for *some* gender so a
        # styled look (e.g. drag glam on a forced-Male subject) survives intact.
        if field_def.get("group") in _GENDER_FLEXIBLE_GROUPS and _gender_permits(
            field_def, "Any", value
        ):
            continue
        del locked_clean[name]
        print(f"[IdentityForge] '{name}={value}' is not valid for gender "
              f"'{gender}'; re-randomizing within the {gender} pool.")

    resolved = _randomize_fields(
        locked_clean, gender, hair_color_scope, accessory_density, location_setting, rng
    )

    # Wardrobe presentation gates the masculine-default trims: a man reads Masculine
    # under "Match gender", but a Feminine/"Any" wardrobe keeps feminine-coded
    # jewellery/nails available so a deliberately femme male look still works.
    presentation = _presentation_mode(gender, wardrobe)
    warnings = _apply_constraints(resolved, gender, set(locked_clean), rng, presentation)
    for message in warnings:
        print(message)

    # A costume override (outfit_description supplied by an archetype/cosplayer)
    # is already a complete outfit, so the separately-randomized garment fields
    # (outfit_style, footwear, colour, pattern) would only add noise — and
    # sometimes contradiction ("barefoot" beside heeled boots) — to the JSON.
    # Drop them when a costume is set; the prose already omits them in that case.
    # When no costume is supplied, generate one from the random outfit_style.
    if _is_absent(resolved.get("outfit_description")):
        resolved["outfit_description"] = _resolve_outfit_description(
            resolved, gender, wardrobe, rng
        )
    else:
        for field in ("outfit_style", "footwear", "clothing_color", "clothing_pattern"):
            resolved.pop(field, None)

    # Gloved/gauntleted hands hide the fingers, so a randomized fingernail polish or
    # ring would render on top of the glove (the reported bug). Force the finger
    # fields absent when the resolved outfit covers the hands -- unless they expose
    # the fingers ("fingerless") or the user explicitly locked the field. A power
    # ring worn over the glove (Green Lantern, Sinestro) is written into the costume
    # prose itself, not the ``rings`` field, so it survives this suppression.
    # ``other_jewelry`` now holds only body pieces (anklet, arm cuff, body chain, …),
    # none of which sit on the fingers, so gloves only suppress nails + the dedicated
    # rings field.
    outfit_text = resolved.get("outfit_description") or ""
    if _GLOVE_RE.search(outfit_text) and not _FINGERLESS_RE.search(outfit_text):
        for field in ("nails", "rings"):
            if field not in locked_clean:
                resolved.pop(field, None)

    # An outfit that already includes headwear can't stack a second hat from the
    # randomized ``accessories`` field ("a top hat … accessorized with wide brim
    # sun hat"). Drop a hat-valued draw when the outfit reads as headwear — this
    # covers cosplayer costumes, archetype outfits and random outfits alike, and
    # costs no RNG. Non-hat accessories still show; a user lock is respected.
    if (_HAT_RE.search(outfit_text)
            and resolved.get("accessories") in _HAT_ACCESSORY_VALUES
            and "accessories" not in locked_clean):
        resolved.pop("accessories", None)

    # A full hard shell -- robot / droid / powered armour / full plate / exoskeleton
    # -- leaves no bare skin for worn jewellery or nails, so a randomized necklace,
    # ring or polish would only render on top of the shell. Drop the whole Jewelry &
    # Nails group when the costume reads as full coverage (or the cosplayer set the
    # ``covers_body`` flag for a case the prose doesn't spell out). Auto-detection
    # here also covers full-plate archetypes (Holy Paladin, Human Knight). Explicit
    # user locks are respected, as with the glove rule above.
    full_shell = covers_body or bool(_FULL_COVER_RE.search(outfit_text))
    if full_shell:
        for field in list(resolved):
            if ((FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_BODY_GROUPS
                    or field in _CONCEALED_BODY_FIELDS)
                    and field not in locked_clean):
                resolved.pop(field, None)

    # A character that is BOTH fully masked and a full hard shell is entirely
    # encased: a randomized human skin_tone would render as a stray patch of bare
    # skin under the armour/droid plating (Iron Man, 2-1B). covers_face already drops
    # the Face/Makeup skin fields; only the Body-group skin_tone leaks, so drop it
    # here. An explicit user skin_tone lock is respected, as elsewhere.
    if covers_face and full_shell:
        for field in _CONCEALED_SHELL_SKIN_FIELDS:
            if field not in locked_clean:
                resolved.pop(field, None)

    # A studio / solid backdrop wants clean, even studio light — a scene-specific
    # value ("neon-lit street", "dappled forest canopy") on a green screen reads
    # wrong and defeats the easy-masking intent. When the resolved location is a
    # backdrop and lighting was not explicitly locked, neutralize it. Scope is kept
    # to lighting (the one strong scene-tell); an explicit lighting lock still wins.
    if (resolved.get("location") in STUDIO_BACKDROPS
            and "lighting" not in locked_clean
            and not _is_absent(resolved.get("lighting"))):
        resolved["lighting"] = "soft studio three-point lighting"

    # A full mask / helmet hides the face: drop the now-irrelevant face, hair and
    # makeup fields so neither prose nor JSON describes a face that contradicts
    # the costume. Done after constraints so nothing downstream expects them.
    if covers_face:
        for field in list(resolved):
            if (FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_FACE_GROUPS
                    or field in _CONCEALED_FACE_FIELDS):
                resolved.pop(field, None)

    # A hood / cowl / lekku covers only the scalp while the face shows: drop the Hair
    # group so no randomized hair contradicts the covering, but keep Face and Makeup.
    # (A character with both covers_face and covers_hair has its hair dropped by the
    # covers_face block above already; this just handles the face-visible case.)
    if covers_hair:
        for field in list(resolved):
            if FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_HAIR_GROUPS:
                resolved.pop(field, None)

    # A "bald" hair_length (locked or randomly drawn from the male pool) is
    # scalp-only: drop the randomized scalp-hair fields so no "bald wavy auburn
    # hair, high ponytail" contradiction renders. An explicitly locked scalp
    # field survives with the usual locked-wins semantics (like constraints).
    # facial_hair is untouched either way (bald + beard is natural).
    if resolved.get("hair_length") == "bald":
        for field in _BALD_SCALP_FIELDS:
            if field not in locked_clean:
                resolved.pop(field, None)

    # A creature form suppresses the human fields it replaces — generalizing the
    # covers_face mechanism. The two unions naturally: a masked cosplayer + an
    # integument-only creature drop both the face and the skin.
    if species:
        suppress_groups = set(species.get("suppress_groups", []))
        suppress_fields = set(species.get("suppress_fields", []))
        if suppress_groups or suppress_fields:
            for field in list(resolved):
                if (FIELD_DEFINITIONS.get(field, {}).get("group") in suppress_groups
                        or field in suppress_fields):
                    resolved.pop(field, None)

    # Style modifiers: prepend a descriptor to the surviving values. Applied last so
    # it decorates exactly what prose and JSON will show (and never an item that was
    # pruned above). Both outputs read from the same modified ``resolved``.
    _apply_modifiers(resolved, modifiers)
    # The same modifiers can tilt the whole species group (e.g. "Species & Anatomy:
    # bioluminescent"); a per-slot key wins over the group key if a future Modifier
    # node exposes slot names.
    if species and species.get("slots") and modifiers:
        group_descriptor = modifiers.get(_SPECIES_GROUP)
        for slot, value in list(species["slots"].items()):
            descriptor = modifiers.get(slot) or group_descriptor
            if descriptor and value:
                species["slots"][slot] = f"{descriptor} {value}"

    # Restate the body-paint / exotic skin colour on the hands too (see
    # _format_prose), but only when the hands show as bare skin -- gloves or a
    # full shell hide them, and their nails were already dropped above.
    hands_covered = full_shell or bool(
        _GLOVE_RE.search(outfit_text) and not _FINGERLESS_RE.search(outfit_text)
    )
    prose = _format_prose(resolved, gender, cosplay_label, species,
                          hands_visible=not hands_covered)
    json_output = _format_json(
        resolved, gender, hair_color_scope, wardrobe, cosplay_label, species
    )
    return prose, json_output


def resolve_locked_fields(
    field_values: dict[str, str],
    archetype_locked: dict[str, str],
    set_all: str = _SET_ALL_OFF,
) -> dict[str, str]:
    """Combine a wired character's locks with the per-field widget choices.

    ``archetype_locked`` holds the concrete field values supplied by a connected
    Archetype/Cosplayer node (its signature look / physique). ``field_values``
    maps each randomizable field to its widget value (``"Random"`` / a concrete
    value / ``"None"``).

    With ``set_all == _SET_ALL_NONE`` every field left on ``"Random"`` is omitted
    (set to ``"None"``) *unless* the wired character supplied it — so a cosplayer's
    iconic hair/eyes survive the reset while the random-person noise is stripped.
    Explicit widget choices (a concrete value or ``"None"``) always win, matching
    the per-field behaviour when the reset is ``"Off"``.
    """
    locked = dict(archetype_locked)
    for field_name in FIELD_DEFINITIONS:
        if field_name in _HIDDEN_FIELDS or field_name in _CONTROL_FIELDS:
            continue
        value = field_values.get(field_name, "Random")
        if (value == "Random" and set_all == _SET_ALL_NONE
                and field_name not in archetype_locked):
            value = "None"
        if value == "None":
            locked[field_name] = "None"  # explicit omit, overrides any archetype value
        elif value != "Random":
            locked[field_name] = value
    return locked


def _parse_archetype_json(raw: str) -> dict[str, str]:
    """Parse an optional archetype JSON string into a field→value dict.

    Accepts either a flat ``{field: value}`` mapping or the grouped document
    produced by :class:`IdentityForge` / the archetype node (``_meta`` plus
    per-group sub-dicts). Returns ``{}`` on empty or malformed input.
    """
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        print("[IdentityForge] Ignoring malformed archetype_json input.")
        return {}
    if not isinstance(data, dict):
        return {}

    flat: dict[str, Any] = {}
    for key, value in data.items():
        if key == "_meta":
            meta = value if isinstance(value, dict) else {}
            for control in ("gender", "hair_color_scope"):
                if isinstance(meta.get(control), str):
                    flat[control] = meta[control]
            # Per-gender variant look blocks from a merged archetype. Kept under a
            # reserved key (not real fields) so the locked-field loops never treat
            # them as locks; applied in generate_character after the gender is fixed.
            variants = meta.get("variants")
            if isinstance(variants, dict):
                clean = {
                    g: {k: v for k, v in look.items() if isinstance(v, str)}
                    for g, look in variants.items()
                    if g in ("Female", "Male") and isinstance(look, dict)
                }
                if clean:
                    flat[_VARIANTS_KEY] = clean
            # A cosplay preset names its character; surface a display label under
            # a reserved key (not a real field, so the locked-field loops ignore
            # it) for the prose prefix / JSON _meta.
            cosplay_of = meta.get("cosplay_of")
            if isinstance(cosplay_of, str) and cosplay_of:
                franchise = meta.get("franchise")
                flat[_COSPLAY_LABEL_KEY] = (
                    f"{cosplay_of} ({franchise})"
                    if isinstance(franchise, str) and franchise else cosplay_of
                )
            if meta.get("covers_face"):
                flat[_COVERS_FACE_KEY] = "1"
            if meta.get("covers_body"):
                flat[_COVERS_BODY_KEY] = "1"
            if meta.get("covers_hair"):
                flat[_COVERS_HAIR_KEY] = "1"
            # A creature preset carries its form + suppression here. ``form`` is
            # the marker that species data is present; slots arrive in the group.
            form = meta.get("form")
            if isinstance(form, str) and form:
                species = flat.setdefault(_SPECIES_KEY, {})
                species["form"] = form
                for str_key in ("creature_of", "creature_class", "size"):
                    if isinstance(meta.get(str_key), str):
                        species[str_key] = meta[str_key]
                for list_key in ("suppress_groups", "suppress_fields"):
                    raw = meta.get(list_key)
                    if isinstance(raw, list):
                        species[list_key] = [v for v in raw if isinstance(v, str)]
            continue
        if key == _SPECIES_GROUP:
            # Anatomy slots: capture the whole group verbatim under the reserved
            # species key (its slot names are not FIELD_DEFINITIONS fields, so the
            # generic group-flatten below would otherwise scatter and drop them).
            if isinstance(value, dict):
                slots = {k: v for k, v in value.items() if isinstance(v, str) and v}
                if slots:
                    species = flat.setdefault(_SPECIES_KEY, {})
                    species["slots"] = {**species.get("slots", {}), **slots}
            continue
        if key == _MODIFIERS_DOC_KEY:
            # Style modifiers from a Modifier node: a {field_or_group: descriptor}
            # map. Kept under a reserved key so the locked-field loops never treat
            # its entries as field locks; merged across chained Modifier nodes.
            if isinstance(value, dict):
                mods = {k: v for k, v in value.items() if isinstance(v, str)}
                if mods:
                    flat[_MODIFIERS_KEY] = {**flat.get(_MODIFIERS_KEY, {}), **mods}
            continue
        if isinstance(value, dict):  # a group sub-dict
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    flat[sub_key] = sub_value
        elif isinstance(value, str):  # flat mapping
            flat[key] = value
    return flat


# ===========================================================================
# ComfyUI V3 node
# ===========================================================================

if _COMFY_AVAILABLE:

    class IdentityForge(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Randomize a detailed character description with a constraint engine."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            inputs: list[Any] = [
                io.Int.Input(
                    "seed",
                    default=0,
                    min=0,
                    max=0xFFFFFFFFFFFFFFFF,
                    # A string value sets the control_after_generate widget's
                    # default mode; "randomize" makes every queue produce a new
                    # character (switch it to "fixed" to reproduce one). A bare
                    # True would default the control to "fixed" instead.
                    control_after_generate="randomize",
                    tooltip="Seed for reproducible randomization. The control below "
                            "defaults to 'randomize' so every run differs; set it to "
                            "'fixed' to reproduce a character.",
                ),
                io.Combo.Input(
                    "gender",
                    options=["Any", "Female", "Male"],
                    default="Any",
                    tooltip="Steers gender-specific presentation and pronouns: "
                            "'Male' keeps the random fill masculine (no makeup, "
                            "polish, feminine jewellery or hairstyles), 'Female' "
                            "allows them. 'Any' rolls a coherent man OR woman each "
                            "run (set wardrobe to 'Any' to instead unlock every "
                            "mixed-gender combination). Locked / archetype / "
                            "cosplayer values are always respected; 'Any' defers to "
                            "a connected archetype's gender.",
                ),
                io.Combo.Input(
                    "wardrobe",
                    options=["Match gender", "Feminine", "Masculine", "Any"],
                    default="Match gender",
                    tooltip="Which outfit wardrobe to draw from. 'Match gender' keeps "
                            "outfits typical for the chosen gender; 'Feminine' / "
                            "'Masculine' force a wardrobe (e.g. a man in feminine "
                            "outfits). 'Any' mixes outfits -- and, when gender is also "
                            "'Any', unlocks fully mixed-gender features too.",
                ),
                io.Combo.Input(
                    "hair_color_scope",
                    options=["Natural only", "Full spectrum"],
                    default="Natural only",
                    tooltip="Defaults to realistic hair colours; choose 'Full spectrum' "
                            "to allow fantasy shades (pink, blue, …).",
                ),
                io.Combo.Input(
                    "accessory_density",
                    options=["Balanced", "Minimal", "Maximal", "None"],
                    default="Balanced",
                    tooltip="How often random characters carry bags / jewellery / "
                            "accessories. 'Balanced' keeps it tasteful, 'None' strips "
                            "them, 'Maximal' decks everyone out. (Fields you lock are "
                            "unaffected.)",
                ),
                io.Combo.Input(
                    "location_setting",
                    options=["Any indoor/outdoor", "Indoor", "Outdoor", "Studio / solid backdrop"],
                    default="Any indoor/outdoor",
                    tooltip="Restrict the random location. 'Any indoor/outdoor' (default) "
                            "picks any real scene but never a studio. 'Studio / solid "
                            "backdrop' forces a plain, easily-maskable background (grey, "
                            "white, black, or chroma-key green screen) and a clean studio "
                            "light. A locked location overrides this.",
                ),
                io.Combo.Input(
                    "set_all_fields",
                    options=[_SET_ALL_OFF, _SET_ALL_NONE],
                    default=_SET_ALL_OFF,
                    tooltip="Quick reset for the fields below. 'All to None' omits "
                            "every field left on 'Random', so only the fields you "
                            "lock to a specific value appear in the output. A wired "
                            "costume and the character's signature look (hair, eyes, "
                            "physique) are kept. Handy for tweaking a cosplay: blank "
                            "the random-person noise, then enable just the fields you "
                            "want.",
                ),
            ]

            # One COMBO per randomizable field, in group order. Every field
            # offers a single "None" so any of them — including scene fields like
            # location / lighting / framing — can be omitted from the output
            # entirely (e.g. to describe a character only and add your own scene).
            # In-pool "absent" values ("no earrings", "none", "bare nails", "clean
            # shaven", …) are hidden from the widget: the engine already treats them
            # identically to "None" (see _is_absent), so showing them would be a
            # redundant second "nothing" entry. They stay in the pools below for
            # randomization / accessory_density, which read the pools, not the widget.
            for field_name, field_def in FIELD_DEFINITIONS.items():
                if field_name in _HIDDEN_FIELDS or field_name in _CONTROL_FIELDS:
                    continue
                visible = [
                    v for v in _dedupe(field_def["female_options"] + field_def["male_options"])
                    if not _is_absent(v)
                ]
                options = ["Random"] + visible + ["None"]
                inputs.append(
                    io.Combo.Input(
                        field_name,
                        options=options,
                        default="Random",
                        tooltip=f"{field_def['group']} · 'Random' = randomize, "
                                f"a value = lock, 'None' = omit from the output.",
                    )
                )

            # Optional archetype JSON input socket (wire IdentityForgeArchetype's
            # character_json here). force_input makes it a connectable socket
            # rather than a text widget.
            inputs.append(
                io.String.Input(
                    "archetype_json",
                    default="",
                    optional=True,
                    force_input=True,
                    tooltip="Connect an IdentityForgeArchetype, IdentityForgeCosplayer or "
                            "IdentityForgeCreature here (chain several via their 'upstream' "
                            "inputs). Its fields seed the character; explicit non-'Random' "
                            "widgets still override it. Leave unconnected (or use 'None') "
                            "for no override.",
                )
            )

            return io.Schema(
                node_id="IdentityForge",
                display_name="Identity Forge",
                category="conditioning/character",
                description="Randomize a detailed character description across many "
                            "lockable fields with a constraint engine, producing "
                            "natural-language prose and structured JSON.",
                inputs=inputs,
                outputs=[
                    io.String.Output(display_name="prompt_text"),
                    io.String.Output(display_name="prompt_json"),
                ],
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
            seed = int(kwargs.get("seed", 0))

            archetype = _parse_archetype_json(kwargs.get("archetype_json", ""))
            cosplay_label = archetype.pop(_COSPLAY_LABEL_KEY, None)
            covers_face = bool(archetype.pop(_COVERS_FACE_KEY, None))
            covers_body = bool(archetype.pop(_COVERS_BODY_KEY, None))
            covers_hair = bool(archetype.pop(_COVERS_HAIR_KEY, None))
            modifiers = archetype.pop(_MODIFIERS_KEY, None)
            species = archetype.pop(_SPECIES_KEY, None)
            gender_variants = archetype.pop(_VARIANTS_KEY, None)
            if species is not None and not species.get("slots"):
                species = None  # form without anatomy → nothing to render

            # Gender: an explicit widget choice wins; "Any" defers to the archetype.
            widget_gender = kwargs.get("gender", "Any")
            gender = widget_gender if widget_gender != "Any" else archetype.get("gender", "Any")
            if gender not in _SUBJ:
                gender = "Any"

            hair_color_scope = kwargs.get("hair_color_scope", "Natural only")
            wardrobe = kwargs.get("wardrobe", "Match gender")
            accessory_density = kwargs.get("accessory_density", "Balanced")
            location_setting = kwargs.get("location_setting", "Any indoor/outdoor")

            # Locked fields: the wired character's values, overridden by explicit
            # widgets. The 'set_all_fields' reset turns every untouched field into
            # an omit, while leaving the wired character's signature look intact.
            #
            # A wired "None" is an *explicit omit* the character chose -- the
            # cosplayer builder injects them to suppress fields the costume already
            # settles: skin_tone/complexion under body paint, scalp hair on a bald
            # head, eye_shape/size under a free-text eye colour. They MUST survive to
            # the engine; excluding them let a default "Random" widget re-randomize a
            # human skin tone under She-Hulk's green or hair on Voldemort's bald head.
            # Kept here so a deliberate concrete widget choice still overrides (handled
            # in resolve_locked_fields), but an untouched "Random" widget preserves the
            # omit. "Random" itself carries no information and stays excluded.
            archetype_locked: dict[str, str] = {
                name: value
                for name, value in archetype.items()
                if name in FIELD_DEFINITIONS
                and name not in _CONTROL_FIELDS
                and value != "Random"
            }
            set_all = kwargs.get("set_all_fields", _SET_ALL_OFF)
            locked = resolve_locked_fields(kwargs, archetype_locked, set_all)

            prose, json_output = generate_character(
                seed, gender, locked, hair_color_scope, wardrobe,
                accessory_density, location_setting, cosplay_label, covers_face,
                covers_body, covers_hair, modifiers, species, gender_variants,
            )
            return io.NodeOutput(prose, json_output)
