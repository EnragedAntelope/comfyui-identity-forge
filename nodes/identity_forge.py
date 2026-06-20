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

import json
import random
from collections import OrderedDict
from typing import Any

# Dual import: package-relative inside ComfyUI (avoids polluting sys.path with
# the generic "data"/"nodes" names), absolute when run standalone for tests.
try:
    from ..data.fields import (
        FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS, ETHNICITY_REGION,
        OUTDOOR_LOCATIONS,
    )
    from ..data.constraints import CONSTRAINT_RULES
except ImportError:  # pragma: no cover — standalone/test context
    from data.fields import (
        FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS, ETHNICITY_REGION,
        OUTDOOR_LOCATIONS,
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
_HIDDEN_FIELDS: frozenset[str] = frozenset({"outfit_description"})

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

#: Field groups suppressed when a cosplayer sets ``covers_face`` — a full mask /
#: helmet / featureless head hides the randomized face, hair and makeup, so
#: describing them would only fight the costume at render time. Body and
#: demographics stay (the person under the mask is still a real body).
_CONCEALED_FACE_GROUPS: frozenset[str] = frozenset({"Face", "Hair", "Makeup"})
#: Individual head-worn fields (outside the above groups) a full mask also hides.
_CONCEALED_FACE_FIELDS: frozenset[str] = frozenset({"earrings", "piercings"})

#: Control fields: read from their toggle, never randomized, never described.
_CONTROL_FIELDS: frozenset[str] = frozenset(
    name for name, meta in FIELD_DEFINITIONS.items() if meta.get("control")
)

#: Canonical group ordering for prose and JSON output.
_GROUP_ORDER: tuple[str, ...] = (
    "Demographics", "Body", "Face", "Hair", "Makeup",
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

#: Maximum constraint-propagation passes before giving up (cycle guard).
_MAX_CONSTRAINT_ITERATIONS: int = 12

#: Probability that a randomized skin tone is drawn from the ethnicity's
#: plausible band rather than the full spectrum. < 1.0 keeps real-world
#: diversity possible (and locking skin_tone bypasses the bias entirely).
SKIN_TONE_INBAND_PROBABILITY: float = 0.8

#: Wardrobe modes: how the outfit picker maps to the gendered outfit buckets.
_WARDROBE_BY_GENDER: dict[str, str] = {
    "Female": "Feminine", "Male": "Masculine", "Any": "Any",
}

#: "Extra" fields (bags, jewellery, accessories) whose single "absent" option is
#: otherwise drowned out by 10-26 present options — leaving ~90% of characters
#: over-accessorised. Each maps to (absent value, P(absent) at "Balanced"); the
#: accessory_density control scales that probability. Portrait-rare items (bag,
#: accessories) lean more absent than everyday jewellery (necklace, earrings).
_EXTRA_ABSENCE: dict[str, tuple[str, float]] = {
    "bag": ("no bag", 0.65),
    "accessories": ("no accessories", 0.55),
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

    if field_name == "location":
        setting = resolved.get("location_setting", "Any")
        if setting == "Indoor":
            base = [loc for loc in base if loc not in OUTDOOR_LOCATIONS]
        elif setting == "Outdoor":
            base = [loc for loc in base if loc in OUTDOOR_LOCATIONS]

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
        elif pool:
            resolved[field_name] = rng.choice(pool)
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
) -> list[str]:
    """Apply :data:`CONSTRAINT_RULES` until stable. Returns warning messages.

    Locked fields are never silently overwritten: when a constraint would
    change a locked field, the lock wins and a warning is recorded instead.
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
                    warn(target, f"'{rule['field']}={rule['value']}' conflicts with "
                                 f"locked '{target}={resolved[target]}'; keeping lock.")
                    continue
                field_def = FIELD_DEFINITIONS.get(target)
                if field_def is None:
                    continue
                pool = [v for v in _build_option_pool(target, field_def, gender, resolved)
                        if v not in excluded]
                if pool:
                    resolved[target] = rng.choice(pool)
                elif field_def["optional"]:
                    resolved[target] = "None"
                changed = True

            else:  # requirement
                target = rule["requires_field"]
                required = rule["requires_value"]
                if resolved.get(target) == required:
                    continue
                if target in locked:
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
    mode = _WARDROBE_BY_GENDER.get(gender, "Any") if wardrobe == "Match gender" else wardrobe
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

def _format_prose(
    resolved: dict[str, str], gender: str, cosplay_label: str | None = None
) -> str:
    """Build a natural-language description from resolved field values.

    When ``cosplay_label`` is set, the prose is prefixed ``Cosplaying as <label>:``.
    """
    r = resolved
    subj = _SUBJ.get(gender, "They")
    poss = _POSS.get(gender, "Their")
    has = "have" if gender == "Any" else "has"
    is_v = "are" if gender == "Any" else "is"
    bust_noun = "chest" if gender == "Male" else "bust"

    def g(field: str) -> str:
        """Value for ``field`` or '' when absent."""
        v = r.get(field, "")
        return "" if _is_absent(v) else v

    sentences: list[str] = []

    # --- Demographics + body core --------------------------------------
    lead_bits = [b for b in (f"{g('age')}-year-old" if g("age") else "", g("ethnicity")) if b]
    lead = "A " + _words(*lead_bits, _GENDER_NOUN.get(gender, "person"))
    core = []
    if g("body_type"):
        core.append(_an(g("body_type"), "build"))
    if g("height"):
        core.append(g("height"))
    if g("skin_tone"):
        core.append(f"{g('skin_tone')} skin")
    sentences.append(lead + (" with " + _join(core) if core else ""))

    # --- Physique + body proportions -----------------------------------
    physique = " and ".join(x for x in (g("fitness_level"), g("muscle_definition")) if x)
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
    if g("lips") or g("lip_color"):
        features.append(_words(g("lip_color"), g("lips")) + " lips")
    if g("eyebrows"):
        brows = g("eyebrows")
        features.append(brows if "brow" in brows else f"{brows} eyebrows")
    if features:
        sentences.append(f"{subj} {has} " + _join(features))

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
    # hair_volume is recorded in the JSON but folded out of the prose: it
    # overlaps with hair_texture ("thick and voluminous") and reads redundantly.
    hair_desc = _words(g("hair_length"), g("hair_texture"), g("hair_color"))
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
        hair_extra.append(g("facial_hair"))
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
        sentences.append(f"{subj} wears " + _join(makeup))

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
        clothing.append(f"{subj} wears {outfit}")
    else:
        pattern_color = _words(g("clothing_color"), g("clothing_pattern"))
        if pattern_color:
            clothing.append(f"{subj} wears {pattern_color} clothing")
        if g("footwear"):
            clothing.append(f"in {g('footwear')}")
    if g("bag"):
        clothing.append(f"carrying {g('bag')}")
    if g("accessories"):
        clothing.append(f"accessorized with {g('accessories')}")
    if clothing:
        sentences.append(", ".join(clothing))

    # --- Pose -----------------------------------------------------------
    if g("pose"):
        sentences.append(f"{subj} {is_v} {g('pose')}")

    # --- Setting & shot -------------------------------------------------
    scene = []
    if g("expression"):
        scene.append(f"{poss} expression is {g('expression')}")
    if g("location"):
        scene.append(f"set in {_a(g('location'))} {g('location')}")
    if g("lighting"):
        scene.append(f"under {g('lighting')}")
    time_season = _join([g("time_of_day"), g("season")])
    if time_season:
        scene.append(f"during {time_season}")
    if g("shot_type"):
        # No article: shot_type values vary wildly ("close-up portrait",
        # "from slightly behind…", "shot through a doorway") and "a/an" + value
        # reads badly or doubles "shot".
        scene.append(f"the framing is {g('shot_type')}")
    if g("mood"):
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
    cosplay_label: str | None = None,
) -> str:
    """Build a JSON document: ``_meta`` plus fields nested by group.

    The seed is intentionally excluded — it is run-control noise, not part of
    the character description.
    """
    meta: "OrderedDict[str, str]" = OrderedDict()
    if cosplay_label:
        meta["cosplay_of"] = cosplay_label
    meta["gender"] = gender
    meta["hair_color_scope"] = hair_color_scope
    meta["wardrobe"] = wardrobe

    document: "OrderedDict[str, Any]" = OrderedDict()
    document["_meta"] = meta
    document.update(group_fields(resolved))
    return json.dumps(document, indent=2)


def generate_character(
    seed: int,
    gender: str,
    locked: dict[str, str],
    hair_color_scope: str = "Natural only",
    wardrobe: str = "Match gender",
    accessory_density: str = "Balanced",
    location_setting: str = "Any",
    cosplay_label: str | None = None,
    covers_face: bool = False,
) -> tuple[str, str]:
    """Engine entry point. Returns ``(prose, json_output)``.

    ``locked`` maps field_name → chosen value for every user-locked field
    (control fields excluded). A locked ``outfit_description`` is honoured as a
    costume, overriding the generated outfit (used by costume archetypes).

    ``cosplay_label`` (e.g. ``"2B (NieR: Automata)"``), when set by a connected
    Cosplayer node, prefixes the prose and is recorded in the JSON ``_meta``.

    ``covers_face`` (set by a full-mask cosplayer) drops the randomized face,
    hair and makeup so only the costume's mask/helmet is described.
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
        and (name not in _HIDDEN_FIELDS or name == "outfit_description")
    }

    # The gender gate must hold for *injected* locks too. An archetype emits
    # look-defining fields (incl. facial_hair) and its own gender; when the
    # downstream gender widget overrides that gender, a value that is invalid for
    # the new gender — e.g. a male archetype's beard on a forced-Female character —
    # would otherwise be kept verbatim, bypassing the randomizer's gender pools and
    # the JS widget filter. Drop such values so the field re-randomizes within the
    # correct gender pool. "None" (an explicit omit) is gender-neutral and stays.
    for name, value in list(locked_clean.items()):
        if value != "None" and not _gender_permits(FIELD_DEFINITIONS[name], gender, value):
            del locked_clean[name]
            print(f"[IdentityForge] '{name}={value}' is not valid for gender "
                  f"'{gender}'; re-randomizing within the {gender} pool.")

    resolved = _randomize_fields(
        locked_clean, gender, hair_color_scope, accessory_density, location_setting, rng
    )

    warnings = _apply_constraints(resolved, gender, set(locked_clean), rng)
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

    # A full mask / helmet hides the face: drop the now-irrelevant face, hair and
    # makeup fields so neither prose nor JSON describes a face that contradicts
    # the costume. Done after constraints so nothing downstream expects them.
    if covers_face:
        for field in list(resolved):
            if (FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_FACE_GROUPS
                    or field in _CONCEALED_FACE_FIELDS):
                resolved.pop(field, None)

    prose = _format_prose(resolved, gender, cosplay_label)
    json_output = _format_json(resolved, gender, hair_color_scope, wardrobe, cosplay_label)
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

    flat: dict[str, str] = {}
    for key, value in data.items():
        if key == "_meta":
            meta = value if isinstance(value, dict) else {}
            for control in ("gender", "hair_color_scope"):
                if isinstance(meta.get(control), str):
                    flat[control] = meta[control]
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
                            "allows them, 'Any' mixes. Locked / archetype / cosplayer "
                            "values are always respected. 'Any' defers to a connected "
                            "archetype's gender.",
                ),
                io.Combo.Input(
                    "wardrobe",
                    options=["Match gender", "Feminine", "Masculine", "Any"],
                    default="Match gender",
                    tooltip="Which outfit wardrobe to draw from. 'Match gender' keeps "
                            "outfits typical for the chosen gender; the others let you "
                            "mix wardrobes (e.g. a man in feminine outfits).",
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
                    options=["Any", "Indoor", "Outdoor"],
                    default="Any",
                    tooltip="Restrict the random location to indoor or outdoor scenes "
                            "(or leave 'Any'). A locked location overrides this.",
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
            # offers "None" so any of them — including scene fields like
            # location / lighting / framing — can be omitted from the output
            # entirely (e.g. to describe a character only and add your own scene).
            for field_name, field_def in FIELD_DEFINITIONS.items():
                if field_name in _HIDDEN_FIELDS or field_name in _CONTROL_FIELDS:
                    continue
                options = ["Random"] + _dedupe(
                    field_def["female_options"] + field_def["male_options"]
                ) + ["None"]
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
                    tooltip="Connect an IdentityForgeArchetype or IdentityForgeCosplayer "
                            "here (use one or the other). Its fields seed the character; "
                            "explicit non-'Random' widgets still override it. Leave "
                            "unconnected (or use 'None') for no override.",
                )
            )

            return io.Schema(
                node_id="IdentityForge",
                display_name="Identity Forge",
                category="conditioning/character",
                description="Randomize a detailed character description across 70+ "
                            "lockable fields with a constraint engine, producing "
                            "natural-language prose and structured JSON.",
                inputs=inputs,
                outputs=[
                    io.String.Output(display_name="prompt_text"),
                    io.String.Output(display_name="prompt_json"),
                ],
            )

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            seed = int(kwargs.get("seed", 0))

            archetype = _parse_archetype_json(kwargs.get("archetype_json", ""))
            cosplay_label = archetype.pop(_COSPLAY_LABEL_KEY, None)
            covers_face = bool(archetype.pop(_COVERS_FACE_KEY, None))

            # Gender: an explicit widget choice wins; "Any" defers to the archetype.
            widget_gender = kwargs.get("gender", "Any")
            gender = widget_gender if widget_gender != "Any" else archetype.get("gender", "Any")
            if gender not in _SUBJ:
                gender = "Any"

            hair_color_scope = kwargs.get("hair_color_scope", "Natural only")
            wardrobe = kwargs.get("wardrobe", "Match gender")
            accessory_density = kwargs.get("accessory_density", "Balanced")
            location_setting = kwargs.get("location_setting", "Any")

            # Locked fields: the wired character's values, overridden by explicit
            # widgets. The 'set_all_fields' reset turns every untouched field into
            # an omit, while leaving the wired character's signature look intact.
            archetype_locked: dict[str, str] = {
                name: value
                for name, value in archetype.items()
                if name in FIELD_DEFINITIONS
                and name not in _CONTROL_FIELDS
                and value not in ("Random", "None")
            }
            set_all = kwargs.get("set_all_fields", _SET_ALL_OFF)
            locked = resolve_locked_fields(kwargs, archetype_locked, set_all)

            prose, json_output = generate_character(
                seed, gender, locked, hair_color_scope, wardrobe,
                accessory_density, location_setting, cosplay_label, covers_face,
            )
            return io.NodeOutput(prose, json_output)
