"""Constraint rules for IdentityForge randomization.

Each rule is a plain dict consumed by the engine in ``nodes/identity_forge.py``.

Schema
------
Exclusion rule (remove impossible values from a field's pool)::

    {
        "type": "exclusion",
        "field": <trigger field>,
        "value": <trigger value>,
        "excludes_field": <target field>,
        "excludes_values": [<value>, ...],
        "reason": <human-readable note>,   # optional, documentation only
    }

Requirement rule (force a field to a specific value)::

    {
        "type": "requirement",
        "field": <trigger field>,
        "value": <trigger value>,
        "requires_field": <target field>,
        "requires_value": <value>,
        "reason": <human-readable note>,   # optional, documentation only
    }

Conventions
-----------
* ``value`` and every excluded/required value MUST be a real option of the
  referenced field (enforced by ``tests/validate_data.py``).
* A value that means "absent" (e.g. ``"None"``) never triggers a rule and is
  never produced by a requirement.
* Rules cascade: the engine re-applies the whole set until it reaches a fixed
  point, so a requirement that changes field B can in turn trigger a rule on B.
"""
from __future__ import annotations

#: Hair styles that physically require enough length to braid, pin, or tie up.
_LONG_HAIR_STYLES: list[str] = [
    "side braid", "fishtail braid", "French braid", "dutch braids", "crown braid",
    "loose braids", "box braids", "locs", "updo", "French twist", "top knot",
    "high ponytail", "low ponytail", "messy bun", "sleek bun", "space buns",
    "pigtails", "half up half down", "twist-out", "afro",
]

CONSTRAINT_RULES: list[dict] = [
    # --- "no makeup" zeroes out every cosmetic sub-field -------------------
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "eye_makeup", "requires_value": "no eyeshadow",
     "reason": "bare face has no eyeshadow"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "eyeliner", "requires_value": "no eyeliner",
     "reason": "bare face has no eyeliner"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "lashes", "requires_value": "natural bare",
     "reason": "bare face has no mascara or falsies"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "lips_makeup", "requires_value": "bare natural lips",
     "reason": "bare face has no lip product"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "blush", "requires_value": "no blush",
     "reason": "bare face has no blush"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "eyebrow_makeup", "requires_value": "none",
     "reason": "bare face has untouched brows"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "contour", "requires_value": "none",
     "reason": "bare face has no contour"},
    {"type": "requirement", "field": "makeup_style", "value": "no makeup",
     "requires_field": "highlight", "requires_value": "none",
     "reason": "bare face has no highlighter"},
    {"type": "exclusion", "field": "makeup_style", "value": "no makeup",
     "excludes_field": "skin_finish", "excludes_values": ["full coverage matte"],
     "reason": "full-coverage matte is a foundation finish, impossible bare-faced"},

    # --- Hair length gates which styles are physically possible -----------
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style", "excludes_values": _LONG_HAIR_STYLES,
     "reason": "a buzz cut cannot be braided, tied, or pinned"},
    {"type": "exclusion", "field": "hair_length", "value": "very short",
     "excludes_field": "hair_style", "excludes_values": _LONG_HAIR_STYLES,
     "reason": "very short hair cannot be braided, tied, or pinned"},
    {"type": "exclusion", "field": "hair_length", "value": "short pixie",
     "excludes_field": "hair_style",
     "excludes_values": ["side braid", "fishtail braid", "French braid",
                         "loose braids", "updo", "French twist", "space buns",
                         "pigtails", "high ponytail", "low ponytail"],
     "reason": "a pixie cut is too short to braid or tie back"},
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_volume", "excludes_values": ["voluminous", "big hair"],
     "reason": "a buzz cut cannot have voluminous body"},
    {"type": "exclusion", "field": "hair_length", "value": "very short",
     "excludes_field": "hair_volume", "excludes_values": ["big hair"],
     "reason": "very short hair cannot be teased into big hair"},

    # --- Body coherence: fitness drives plausible muscle definition -------
    {"type": "exclusion", "field": "fitness_level", "value": "sedentary",
     "excludes_field": "muscle_definition",
     "excludes_values": ["defined", "cut", "very muscular"],
     "reason": "a sedentary build is not chiselled"},
    {"type": "exclusion", "field": "fitness_level", "value": "lightly active",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "light activity does not produce competition-level definition"},

    # Note: the "Natural only" hair scope is enforced during randomization (see
    # _build_option_pool), so randomized hair is always realistic. We do NOT add
    # a constraint for it: that would only fire on a *locked* fantasy colour
    # (e.g. an archetype's pink hair), which is an intentional choice to keep.

    # --- Outfit style drives bag, jewellery, accessories, footwear --------
    {"type": "requirement", "field": "outfit_style", "value": "athletic",
     "requires_field": "bag", "requires_value": "no bag",
     "reason": "you do not carry a handbag to a workout"},
    {"type": "exclusion", "field": "outfit_style", "value": "athletic",
     "excludes_field": "footwear",
     "excludes_values": ["heels", "loafers", "oxfords", "slippers", "sandals"],
     "reason": "athletic wear pairs with trainers, not dress shoes"},
    {"type": "exclusion", "field": "outfit_style", "value": "athletic",
     "excludes_field": "necklace",
     "excludes_values": ["pearl strand", "statement necklace", "diamond pendant",
                         "pearl necklace"],
     "reason": "fine jewellery is out of place in sportswear"},

    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "bag",
     "excludes_values": ["canvas tote", "straw beach tote",
                         "mini backpack in black", "mini backpack in tan"],
     "reason": "casual carryalls clash with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "accessories",
     "excludes_values": ["baseball cap", "woven hat", "smart watch",
                         "wide brim sun hat"],
     "reason": "casual headwear and sportswatches clash with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "footwear",
     "excludes_values": ["sneakers", "slippers", "barefoot", "sandals"],
     "reason": "black-tie dress calls for heels or oxfords"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "other_jewelry", "excludes_values": ["stacked bracelets", "watch"],
     "reason": "formal looks favour fine jewellery over everyday pieces"},

    {"type": "exclusion", "field": "outfit_style", "value": "business formal",
     "excludes_field": "accessories",
     "excludes_values": ["cat eye sunglasses", "round sunglasses",
                         "baseball cap", "beret"],
     "reason": "playful accessories undercut a formal suit"},
    {"type": "exclusion", "field": "outfit_style", "value": "business formal",
     "excludes_field": "footwear",
     "excludes_values": ["sneakers", "slippers", "barefoot", "sandals"],
     "reason": "a formal suit calls for dress shoes"},

    {"type": "exclusion", "field": "outfit_style", "value": "edgy alternative",
     "excludes_field": "necklace",
     "excludes_values": ["pearl strand", "delicate gold chain", "pearl necklace"],
     "reason": "demure jewellery clashes with an edgy look"},

    {"type": "exclusion", "field": "outfit_style", "value": "streetwear",
     "excludes_field": "necklace",
     "excludes_values": ["pearl strand", "pearl necklace"],
     "reason": "pearls clash with streetwear"},

    {"type": "exclusion", "field": "outfit_style", "value": "resort vacation",
     "excludes_field": "accessories",
     "excludes_values": ["western belt", "smart watch"],
     "reason": "office and western accessories clash with resort wear"},

    # --- Hair: a buzz cut has no parting ----------------------------------
    {"type": "requirement", "field": "hair_length", "value": "buzzed very short",
     "requires_field": "hair_part", "requires_value": "no part",
     "reason": "a buzz cut has no visible parting"},

    # --- Body: very slim / plus-size builds vs muscle definition ----------
    {"type": "exclusion", "field": "body_type", "value": "very slim",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "a very slim frame lacks heavy muscle mass"},
    {"type": "exclusion", "field": "body_type", "value": "petite and slim",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "a petite slim frame lacks heavy muscle mass"},
    {"type": "exclusion", "field": "body_type", "value": "plus size",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "a plus-size build reads as soft, not shredded"},
    {"type": "exclusion", "field": "body_type", "value": "chubby",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "a chubby build reads as soft, not shredded"},
    {"type": "exclusion", "field": "body_type", "value": "plump",
     "excludes_field": "muscle_definition", "excludes_values": ["cut", "very muscular"],
     "reason": "a plump build reads as soft, not shredded"},
]


# --- Generated coherence rules ------------------------------------------------
# Built in loops to avoid repetition; appended to CONSTRAINT_RULES above.

# Natural makeup styles never carry dramatic eye looks.
_NATURAL_MAKEUP = [
    "barely there natural makeup", "soft natural makeup",
    "classic no-makeup makeup", "fresh-faced dewy look",
]
_HEAVY_EYESHADOW = ["smoky black", "smoky gray", "deep navy",
                    "colorful bold eyeshadow", "glittery", "cut crease"]
_HEAVY_EYELINER = ["bold cat eye", "dramatic winged", "smudged kohl",
                   "graphic editorial liner"]
_HEAVY_LASHES = ["bold thick mascara", "wispy false lashes",
                 "dramatic falsies", "lash extension look"]
for _style in _NATURAL_MAKEUP:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "eye_makeup", "excludes_values": list(_HEAVY_EYESHADOW),
        "reason": f"'{_style}' excludes dramatic eyeshadow"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "eyeliner", "excludes_values": list(_HEAVY_EYELINER),
        "reason": f"'{_style}' excludes dramatic eyeliner"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "lashes", "excludes_values": list(_HEAVY_LASHES),
        "reason": f"'{_style}' excludes false/heavy lashes"})

# Expression drives whether teeth show (keeps the smile coherent).
_CLOSED_EXPRESSIONS = ["neutral", "serious", "stern", "intense gaze",
                       "pensive and thoughtful", "contemplative", "sultry"]
_OPEN_EXPRESSIONS = ["wide toothy grin", "laughing", "candid mid-laugh"]
for _expr in _CLOSED_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "teeth_visibility", "requires_value": "closed lips",
        "reason": f"a {_expr} expression keeps the mouth closed"})
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "smile_type", "requires_value": "closed mouth",
        "reason": f"a {_expr} expression is not a smile"})
for _expr in _OPEN_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "teeth_visibility", "requires_value": "broad smile showing teeth",
        "reason": f"a {_expr} expression shows teeth"})
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "smile_type", "requires_value": "toothy grin",
        "reason": f"a {_expr} expression is a broad toothy smile"})
