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
    "waterfall braid", "loose braids", "box braids", "locs", "updo", "French twist",
    "top knot", "chignon", "high ponytail", "low ponytail", "side ponytail",
    "braided ponytail", "messy bun", "sleek bun", "ballerina bun", "space buns",
    "pigtails", "high pigtails", "low pigtails", "curled pigtails", "braided pigtails",
    "half up half down", "twist-out", "afro",
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
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style", "excludes_values": ["comb over"],
     "reason": "a buzz cut has no length on top to comb over"},
    {"type": "exclusion", "field": "hair_length", "value": "short pixie",
     "excludes_field": "hair_style",
     "excludes_values": ["side braid", "fishtail braid", "French braid",
                         "waterfall braid", "loose braids", "updo", "French twist",
                         "space buns", "pigtails", "high pigtails", "low pigtails",
                         "curled pigtails", "braided pigtails",
                         "high ponytail", "low ponytail", "side ponytail",
                         "braided ponytail"],
     "reason": "a pixie cut is too short to braid or tie back"},

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
     "excludes_values": ["baseball cap", "woven hat", "wide brim sun hat"],
     "reason": "casual headwear clashes with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "watch_type", "excludes_values": ["smart watch"],
     "reason": "a sportwatch clashes with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "footwear",
     "excludes_values": ["sneakers", "slippers", "barefoot", "sandals"],
     "reason": "black-tie dress calls for heels or oxfords"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "bracelet", "excludes_values": ["leather wrap bracelet", "beaded bracelet"],
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
     "excludes_values": ["western belt"],
     "reason": "western office accessories clash with resort wear"},

    # --- Hair: a buzz cut has no parting ----------------------------------
    {"type": "requirement", "field": "hair_length", "value": "buzzed very short",
     "requires_field": "hair_part", "requires_value": "no part",
     "reason": "a buzz cut has no visible parting"},

    # --- Body: very slim / plus-size builds vs fitness level --------------
    # fitness_level is now the sole muscularity/conditioning axis (muscle_definition
    # was merged out), so keep it plausible for the body_type silhouette: a
    # "plus size, muscular" contradiction can never be rolled.
    {"type": "exclusion", "field": "body_type", "value": "very slim",
     "excludes_field": "fitness_level", "excludes_values": ["muscular"],
     "reason": "a very slim frame lacks heavy muscle mass"},
    {"type": "exclusion", "field": "body_type", "value": "petite and slim",
     "excludes_field": "fitness_level", "excludes_values": ["muscular"],
     "reason": "a petite slim frame lacks heavy muscle mass"},
    {"type": "exclusion", "field": "body_type", "value": "plus size",
     "excludes_field": "fitness_level", "excludes_values": ["athletic", "muscular"],
     "reason": "a plus-size build reads as soft, not athletic"},
    {"type": "exclusion", "field": "body_type", "value": "chubby",
     "excludes_field": "fitness_level", "excludes_values": ["athletic", "muscular"],
     "reason": "a chubby build reads as soft, not athletic"},
    {"type": "exclusion", "field": "body_type", "value": "plump",
     "excludes_field": "fitness_level", "excludes_values": ["athletic", "muscular"],
     "reason": "a plump build reads as soft, not athletic"},
    # Soft-curved silhouettes contradict heavy muscle mass (but stay compatible
    # with "athletic"/"very fit" — strong curvy bodies exist; only the extreme
    # is excluded). Conversely, a build *named* for conditioning can't be
    # sedentary. These govern only the random fill: locked values (cosplayer
    # physique, archetype, user) win with a warning, as with every rule here.
    {"type": "exclusion", "field": "body_type", "value": "softly curved",
     "excludes_field": "fitness_level", "excludes_values": ["muscular"],
     "reason": "a softly curved build reads as soft, not heavily muscled"},
    {"type": "exclusion", "field": "body_type", "value": "full figured",
     "excludes_field": "fitness_level", "excludes_values": ["muscular"],
     "reason": "a full-figured build reads as soft, not heavily muscled"},
    {"type": "exclusion", "field": "body_type", "value": "voluptuous",
     "excludes_field": "fitness_level", "excludes_values": ["muscular"],
     "reason": "a voluptuous build reads as soft, not heavily muscled"},
    {"type": "exclusion", "field": "body_type", "value": "athletic",
     "excludes_field": "fitness_level", "excludes_values": ["sedentary"],
     "reason": "an athletic build implies regular training"},
    {"type": "exclusion", "field": "body_type", "value": "toned",
     "excludes_field": "fitness_level", "excludes_values": ["sedentary"],
     "reason": "a toned build implies regular training"},
    {"type": "exclusion", "field": "body_type", "value": "fit",
     "excludes_field": "fitness_level", "excludes_values": ["sedentary"],
     "reason": "a fit build implies regular training"},
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

# "fresh-faced dewy look" names its own finish: a matte skin_finish contradicts
# it, and "dewy skin" doubles the word in one sentence. The luminous/glass/
# natural finishes remain compatible.
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "makeup_style", "value": "fresh-faced dewy look",
    "excludes_field": "skin_finish",
    "excludes_values": ["matte finish", "full coverage matte", "dewy skin"],
    "reason": "dewy makeup style conflicts with matte finishes and doubles 'dewy skin'"})

# Expression drives the mouth/smile state so the rendered smile_type never
# contradicts the face (smile_type is the single mouth field now -- teeth_visibility
# was merged out). Three buckets: a closed non-smiling mouth, a closed-lip soft
# smile, and an open toothy grin. Expressions left out of all three are genuinely
# ambiguous (playful, smirking, surprised, coy, ...) and keep a free smile_type draw.
_CLOSED_EXPRESSIONS = ["neutral", "serious", "stern", "intense gaze",
                       "pensive and thoughtful", "contemplative", "sultry",
                       "serene", "determined", "calm and composed", "at ease",
                       "steely", "focused", "brooding", "melancholic",
                       "lost in thought", "wistful", "skeptical", "daydreaming"]
_SOFT_SMILE_EXPRESSIONS = ["subtle soft smile", "warm smile", "bright smile",
                           "gentle smile"]
_OPEN_EXPRESSIONS = ["wide toothy grin", "laughing", "candid mid-laugh", "beaming"]
for _expr in _CLOSED_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "smile_type", "requires_value": "closed mouth",
        "reason": f"a {_expr} expression is not a smile"})
for _expr in _SOFT_SMILE_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "smile_type", "requires_value": "soft smile",
        "reason": f"a {_expr} is a gentle closed-lip smile"})
for _expr in _OPEN_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "expression", "value": _expr,
        "requires_field": "smile_type", "requires_value": "toothy grin",
        "reason": f"a {_expr} expression is a broad toothy smile"})

# Hairstyles with no visible parting force hair_part to "no part" (treated as absent
# in prose), resolving the slicked-back/centre-part style conflict.
_NO_PART_STYLES = ["slicked back", "wet look", "afro", "twist-out",
                   "bantu knots", "space buns"]
for _style in _NO_PART_STYLES:
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "hair_style", "value": _style,
        "requires_field": "hair_part", "requires_value": "no part",
        "reason": f"a {_style} style shows no visible parting"})

# Masculine presentation defaults (gender == "Male").
# Many fields (nails, lip colour, jewellery, hairstyle) share one option pool
# across genders, so the random fill would otherwise hand a male character
# feminine-coded makeup, polish, pearls or pigtails. These rules govern ONLY the
# RANDOM fill: a value locked by the user, an archetype, or a cosplayer signature
# is in the engine's ``locked`` set, so the constraint warns and KEEPS it — which
# is exactly what faithful crossplay (a man cosplaying a pigtailed character)
# needs. "Any" is unaffected (it deliberately mixes both genders' pools).
CONSTRAINT_RULES.append({
    "type": "requirement", "field": "gender", "value": "Male",
    "requires_field": "makeup_style", "requires_value": "no makeup",
    "reason": "a male character is bare-faced by default (cascades to clear all cosmetics)"})

#: field -> feminine-coded values a random Male should not pick up. The remaining
#: (masculine / neutral) options stay available for the random re-pick.
_MALE_EXCLUDED_VALUES: dict[str, list[str]] = {
    "nails": [
        "long nails", "almond nails", "coffin nails", "stiletto nails",
        "french manicure", "nude polish", "red polish", "coral polish",
        "pink polish", "mauve polish", "deep burgundy", "black polish",
        "navy polish", "colorful nail art", "minimalist nail art",
        "chrome nails", "gel nails",
    ],
    "earrings": [
        "pearl studs", "medium gold hoops", "large bold gold hoops",
        "chandelier earrings", "long drop earrings", "tassel earrings",
        "mismatched earrings", "clip-on pearl earrings", "huggie hoops",
        "threader earrings",
    ],
    "necklace": [
        "pearl necklace", "pearl strand", "locket necklace", "choker",
        "velvet choker", "statement necklace", "collar necklace",
    ],
    "other_jewelry": ["anklet", "body chain", "waist chain"],
    "rings": ["stacked thin bands", "delicate gemstone", "midi ring"],
    "bracelet": ["tennis bracelet", "charm bracelet", "bangle stack"],
    "hair_style": [
        "space buns", "pigtails", "high pigtails", "low pigtails", "curled pigtails",
        "braided pigtails", "updo", "French twist",
        "crown braid", "fishtail braid", "half up half down", "ballerina bun",
    ],
    "hair_length": ["chin length bob", "waist length", "hip length"],
    "hair_highlights": ["subtle balayage", "face framing", "ombre", "sombre",
                        "money piece", "peekaboo highlights"],
    "eyebrows": ["thin and arched", "pencil thin", "well defined and arched"],
    "lips": ["bow-shaped", "heart-shaped", "petite and defined"],
    "eye_shape": ["doe-like"],
    "bust": ["large"],
}
# Jewellery & nails are a wardrobe *presentation* choice, not anatomy: their trims
# are gated on the resolved presentation so a man with a Feminine/"Any" wardrobe can
# still draw feminine-coded pieces. The rest (hair, brows, lips, eye shape, bust) are
# structural/anatomical male defaults and always apply for a male character.
_PRESENTATION_GATED_FIELDS: frozenset[str] = frozenset({
    "nails", "earrings", "necklace", "other_jewelry", "rings", "bracelet",
})
for _field, _excluded in _MALE_EXCLUDED_VALUES.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "gender", "value": "Male",
        "excludes_field": _field, "excludes_values": _excluded,
        "presentation_gated": _field in _PRESENTATION_GATED_FIELDS,
        "reason": f"feminine-coded {_field} is not a male default"})
