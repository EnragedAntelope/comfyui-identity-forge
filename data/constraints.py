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

from collections import OrderedDict

# The location<->lighting rules below are generated from the option pools and the
# coherence buckets rather than restating ~166 location strings here, which would
# drift the moment a location is added. Dual import mirrors nodes/identity_forge.py:
# package-relative inside ComfyUI, absolute when run standalone for tests.
try:
    from .fields import (
        DEEP_SKIN_TONES, FIELD_DEFINITIONS, FIELD_FAMILIES, FIXTURE_LIGHTING,
        INDOOR_ONLY_LIGHTING, OUTDOOR_LOCATIONS, OUTDOOR_ONLY_LIGHTING,
        STUDIO_BACKDROPS, VOID_ALLOWED_LIGHTING,
    )
except ImportError:  # pragma: no cover -- standalone/test context
    from data.fields import (
        DEEP_SKIN_TONES, FIELD_DEFINITIONS, FIELD_FAMILIES, FIXTURE_LIGHTING,
        INDOOR_ONLY_LIGHTING, OUTDOOR_LOCATIONS, OUTDOOR_ONLY_LIGHTING,
        STUDIO_BACKDROPS, VOID_ALLOWED_LIGHTING,
    )

#: Hair styles that physically require enough length to braid, pin, or tie up.
#: ``cornrows`` and ``bantu knots`` joined at 0.72.0: both need hair long enough to
#: gather and section (cornrows want roughly two inches, a bantu knot is a coil), and
#: neither had ever been slotted into a length list, so they landed on buzz cuts --
#: 210 cornrow and 86 bantu-knot collisions in a 4000-seed sweep. They are texture-
#: free (they read on any curl pattern), which is why the texture gate below leaves
#: them alone; length is a separate axis.
_LONG_HAIR_STYLES: list[str] = [
    "side braid", "fishtail braid", "French braid", "dutch braids", "crown braid",
    "waterfall braid", "loose braids", "box braids", "locs", "updo", "French twist",
    "top knot", "chignon", "high ponytail", "low ponytail", "side ponytail",
    "braided ponytail", "messy bun", "sleek bun", "ballerina bun", "space buns",
    "pigtails", "high pigtails", "low pigtails", "curled pigtails", "braided pigtails",
    "half up half down", "twist-out", "afro", "cornrows", "bantu knots",
    # 0.83.0 additions. This slotting is MANDATORY, not optional -- it is the rule
    # `cornrows` and `bantu knots` escaped until 0.72.0. A milkmaid braid crosses the
    # crown, a rope braid twists two sections, a braided bun wraps a braid, twists
    # need sectionable length, and a bubble ponytail needs enough to tie repeatedly.
    # `hair puff` is here for a BIAS reason, not only a physical one. My first pass left
    # it out reasoning "a puff is a short-coil look like its family-mates afro and
    # twist-out" -- but both of those ARE in this list, so omitting the puff culled 2 of 3
    # in the `texture` family at buzz lengths and would have concentrated that family's
    # full frozen weight onto the puff alone. Caught by
    # HairStyleFamilyTests::test_impossible_length_style_pairs_are_whole_sub_families.
    # It is also true physically: gathering coils into a puff needs more than a buzz.
    # `micro bangs` is deliberately ABSENT -- it is handled by the bangs buzz rule
    # below, as a whole family, which is the same requirement satisfied a different way.
    "milkmaid braids", "rope braid", "braided bun", "two-strand twists",
    "bubble ponytail", "hair puff",
]

#: The four short barbered cuts (0.81.0). This list is EXACTLY the
#: ``barbered_short`` family in fields.py, and the rules below rely on that: they
#: exclude the whole family, so every other family keeps its share. If a fifth
#: short cut is ever added to that family it must be added here too, or the
#: exclusion becomes a partial cull and concentrates the family's frozen weight on
#: whatever is left. ``HairStyleFamilyTests`` pins the two lists together.
_BARBERED_SHORT_STYLES: list[str] = ["fade", "undercut", "pompadour", "quiff"]

#: The three short crops (0.83.0). EXACTLY the ``barbered_crop`` family in fields.py,
#: for the same reason the list above mirrors ``barbered_short``: the rules exclude the
#: WHOLE family, so a fourth crop added there must be added here or the exclusion
#: becomes a partial cull. ``HairStyleFamilyTests`` pins the two together.
#:
#: Their length gate is the MIRROR of the barbered_short one, which is precisely why
#: they could not join that family: a crop IS a very short cut, so it is legal at a buzz
#: and impossible from ear length up, where a fade or quiff is legal at a buzz-adjacent
#: length and only fails past the shoulders.
_BARBERED_CROP_STYLES: list[str] = ["crew cut", "textured crop", "high-top fade"]

#: Every length at which a crew cut / textured crop / high-top fade stops describing
#: the hair. Derived from the pool so a new length cannot silently escape the gate.
_CROP_IMPOSSIBLE_LENGTHS: tuple[str, ...] = (
    "ear length", "chin length bob", "jaw length", "shoulder length",
    "slightly past shoulders", "mid back", "lower back", "long", "very long",
    "waist length", "hip length",
)

#: Lengths at which a fade / undercut / pompadour / quiff no longer describes the
#: cut. Deliberately starts past the shoulders: an undercut or a quiff on
#: shoulder-length hair is an ordinary look, so shoulder lengths stay reachable.
_PAST_SHOULDER_LENGTHS: tuple[str, ...] = (
    "mid back", "lower back", "long", "very long", "waist length", "hip length",
)

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
     "excludes_field": "skin_finish", "excludes_values": ["full coverage matte", "matte finish", "dewy skin"],
     "reason": "these are foundation or cosmetic finishes, impossible bare-faced"},

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
    # 0.77.0: a buzz cut has no fringe to cut into bangs. A 12,000-sample sweep
    # put bangs on a buzz 267 times (~2.2% of all output) -- the same class as the
    # cornrows-on-a-buzz bug fixed at 0.72.0, and found the same way.
    # ``curtain bangs`` + ``blunt bangs`` are EXACTLY the ``bangs`` family in
    # HAIR_STYLE_FAMILIES, so excluding both drops a WHOLE family and the
    # remaining families stay exactly proportional -- the bias rule the lighting
    # buckets follow.
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style",
     # 0.83.0: `micro bangs` joined the family, so it MUST join this list -- the rule is
     # only safe while it drops the bangs family whole. 0.90.0: `side-swept bangs` and
     # `wispy bangs` joined for exactly the same reason, and the test caught their
     # absence immediately (3 of 5 culled instead of 5 of 5). This list must stay
     # EXACTLY the `bangs` family in fields.py.
     "excludes_values": ["curtain bangs", "blunt bangs", "micro bangs",
                         "side-swept bangs", "wispy bangs"],
     "reason": "a buzz cut has no fringe to cut into bangs"},
    # 0.78.0: the other half of the buzz-cut fix, unblocked by splitting the
    # ``loose`` family in fields.py. These five need length to hold a style and a
    # 12,000-sample sweep put them on a buzz cut 706 times (~5.9% of all output).
    # They are EXACTLY the ``loose_styled`` sub-family, so this drops a whole unit
    # and every other family stays proportional. Before the split they were 5 of 9
    # in one ``loose`` family, and excluding them would have handed that family's
    # full frozen weight to ``wet look`` + ``natural and unstyled``.
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style",
     "excludes_values": ['worn down', 'slicked back', 'windswept',
                         'freshly blown out', 'tousled bedhead'],
     "reason": "a buzz cut has no length to wear down, style, or blow out"},
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style", "excludes_values": ["mullet"],
     "reason": "a buzz cut has no back length for a mullet"},
    {"type": "exclusion", "field": "hair_length", "value": "very short",
     "excludes_field": "hair_style", "excludes_values": ["mullet"],
     "reason": "very short hair has no back length for a mullet"},
    {"type": "exclusion", "field": "hair_length", "value": "short pixie",
     "excludes_field": "hair_style", "excludes_values": ["mullet"],
     "reason": "a pixie cut has no back length for a mullet"},
    # Deliberately narrower than _LONG_HAIR_STYLES: a pixie IS long enough for the
    # short natural styles, so afro / twist-out (a pixie-length TWA is a real look),
    # locs (starter locs), cornrows and the small buns stay reachable. Only the
    # styles that need gatherable length are culled. ``box braids`` and ``bantu
    # knots`` joined at 0.72.0 -- both hang or coil well past a pixie's length.
    # ``dutch braids`` + ``crown braid`` joined at 0.78.0 (84 hits in a 12,000-sample
    # sweep): both need enough length to section and wrap. They could not be culled
    # before the ``braid`` family was split, because they would have left
    # ``cornrows`` and ``locs`` as the family's only pixie survivors, roughly
    # doubling both. With the split this rule now removes EXACTLY the ``braid_long``
    # sub-family, leaving ``braid_short`` intact -- a whole-unit drop.
    {"type": "exclusion", "field": "hair_length", "value": "short pixie",
     "excludes_field": "hair_style",
     "excludes_values": ["side braid", "fishtail braid", "French braid",
                         "waterfall braid", "loose braids", "updo", "French twist",
                         "space buns", "pigtails", "high pigtails", "low pigtails",
                         "curled pigtails", "braided pigtails",
                         "high ponytail", "low ponytail", "side ponytail",
                         "braided ponytail",
                         # 1.5.0 round 4: box braids and bantu knots left this list when
                         # they moved into braid_short / texture (whole families only);
                         # mini braids and knots on short natural hair are real looks.
                         "dutch braids", "crown braid",
                         # 0.83.0. `two-strand twists` is deliberately NOT here:
                         # like its family-mates `cornrows` and `locs` it is real at
                         # pixie length, and the pixie list stays narrower than
                         # _LONG_HAIR_STYLES on purpose. `hair puff` also stays
                         # legal -- a coil puff at pixie length is a real look.
                         "milkmaid braids", "rope braid", "braided bun",
                         "bubble ponytail"],
     "reason": "a pixie cut is too short to braid or tie back"},
    # 0.81.0: the barbered cuts. Both groups are excluded as WHOLE families
    # (`barbered_short` = these four, `barbered_shag` = shag), which is the only
    # reason they can be culled at all -- see the split note in fields.py.
    #
    # `buzzed very short` takes the whole short group rather than just the two that
    # are flatly impossible: a pompadour and a quiff need top length a buzz does not
    # have, and while "buzz fade" is a real barbershop order, the family cannot be
    # cut in half without handing its weight to the survivors. Losing a marginal
    # buzz-fade is the cheaper side of that trade.
    {"type": "exclusion", "field": "hair_length", "value": "buzzed very short",
     "excludes_field": "hair_style",
     "excludes_values": _BARBERED_SHORT_STYLES,
     "reason": "a buzz cut has no top length to fade into, sweep up, or undercut"},
    *[
        {"type": "exclusion", "field": "hair_length", "value": length,
         "excludes_field": "hair_style", "excludes_values": _BARBERED_SHORT_STYLES,
         "reason": f"{length} hair is far past the length these barbered cuts describe"}
        for length in _PAST_SHOULDER_LENGTHS
    ],
    # A shag is a layered MID-length cut; there is nothing to layer on a crop.
    *[
        {"type": "exclusion", "field": "hair_length", "value": length,
         "excludes_field": "hair_style", "excludes_values": ["shag", "wolf cut"],
         "reason": f"{length} hair is too short to cut into a shag's layers"}
        for length in ("buzzed very short", "very short", "short pixie")
    ],
    # 1.5.0: a hime cut is blunt sidelocks over long straight-hanging hair; below the
    # shoulders there is nothing for the sidelocks to frame. Single-variant family, so
    # a whole-family drop.
    *[
        {"type": "exclusion", "field": "hair_length", "value": length,
         "excludes_field": "hair_style", "excludes_values": ["hime cut"],
         "reason": f"{length} hair is too short for a hime cut"}
        for length in ("buzzed very short", "very short", "short pixie", "ear length",
                       "chin length bob", "jaw length")
    ],
    # 0.83.0: barbered_crop, excluded as a WHOLE family at every length from ear
    # length up. A crew cut is a very short cut by definition; a "chin length bob
    # crew cut" is not a haircut. Legal at buzzed very short / very short / short
    # pixie -- the three lengths the crops actually describe.
    *[
        {"type": "exclusion", "field": "hair_length", "value": length,
         "excludes_field": "hair_style", "excludes_values": _BARBERED_CROP_STYLES,
         "reason": f"{length} hair is far longer than a crew cut or crop describes"}
        for length in _CROP_IMPOSSIBLE_LENGTHS
    ],

    # Note: the "Natural only" hair scope is enforced during randomization (see
    # _build_option_pool), so randomized hair is always realistic. We do NOT add
    # a constraint for it: that would only fire on a *locked* fantasy colour
    # (e.g. an archetype's pink hair), which is an intentional choice to keep.

    # --- Outfit style drives bag, jewellery, accessories, footwear --------
    {"type": "requirement", "field": "outfit_style", "value": "athletic",
     "requires_field": "bag", "requires_value": "no bag",
     "reason": "you do not carry a handbag to a workout"},
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
     "excludes_values": ["baseball cap", "woven hat", "wide brim sun hat",
                         "earmuffs", "headphones worn around the neck",  # 1.5.0
                         "fingerless gloves", "bucket hat", "wool beanie",
                         "western belt"],  # 1.5.0 round 3
     "reason": "casual headwear clashes with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "watch_type", "excludes_values": ["smart watch"],
     "reason": "a sportwatch clashes with black-tie dress"},
    {"type": "exclusion", "field": "outfit_style", "value": "evening formal",
     "excludes_field": "bracelet", "excludes_values": ["leather wrap bracelet", "beaded bracelet"],
     "reason": "formal looks favour fine jewellery over everyday pieces"},

    {"type": "exclusion", "field": "outfit_style", "value": "business formal",
     "excludes_field": "accessories",
     "excludes_values": ["cat eye sunglasses", "round sunglasses",
                         "baseball cap", "beret",
                         "earmuffs", "headphones worn around the neck",  # 1.5.0
                         "fingerless gloves", "bucket hat", "wool beanie"],  # 1.5.0 r3
     "reason": "playful accessories undercut a formal suit"},
    {"type": "exclusion", "field": "outfit_style", "value": "cocktail semi-formal",
     "excludes_field": "accessories",
     "excludes_values": ["headphones worn around the neck", "baseball cap"],  # 1.5.0
     "reason": "everyday gear undercuts a cocktail look"},

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

    # 1.5.0: hands-on dress keeps rugged or practical pieces only.
    {"type": "exclusion", "field": "outfit_style", "value": "utility workwear",
     "excludes_field": "necklace",
     "excludes_values": ["pearl strand", "pearl necklace", "statement necklace",
                         "diamond pendant", "collar necklace", "velvet choker"],
     "reason": "fine or statement jewellery is out of place in workwear"},
    {"type": "exclusion", "field": "outfit_style", "value": "utility workwear",
     "excludes_field": "accessories",
     "excludes_values": ["long opera gloves", "silk neck scarf", "silk pocket square",
                         "belt cinching waist", "statement belt", "cat eye sunglasses",
                         "wide brim sun hat", "beret", "lapel pin"],
     "reason": "dress-up accessories clash with workwear"},

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

# Glam makeup styles require visible cosmetics on every axis -- bare or absent
# sub-field values contradict an intentionally dramatic look. The natural-makeup
# block above already gates fantasy/high-drama values out of natural styles;
# this gate does the reverse: it prevents bare cosmetics from landing under glam.
_GLAM_MAKEUP = [
    "full glam", "bold glam", "heavy glam",
    "editorial makeup", "gothic dark makeup", "club makeup",
    "vintage 1950s pin-up makeup", "mod 1960s eye makeup",
    "soft everyday glam", "soft glam",
]
_BARE_EYE_MAKEUP = ["no eyeshadow"]
_BARE_EYELINER = ["no eyeliner"]
_BARE_LASHES = ["natural bare"]
_BARE_LIPS = ["bare natural lips"]
_NO_BLUSH = ["no blush"]
_NO_CONTOUR = ["none"]
_NO_HIGHLIGHT = ["none"]
for _style in _GLAM_MAKEUP:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "eye_makeup", "excludes_values": _BARE_EYE_MAKEUP,
        "reason": f"'{_style}' requires visible eyeshadow; bare eyes contradicts it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "eyeliner", "excludes_values": _BARE_EYELINER,
        "reason": f"'{_style}' requires visible eyeliner; bare liner contradicts it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "lashes", "excludes_values": _BARE_LASHES,
        "reason": f"'{_style}' requires mascara or falsies; bare lashes contradict it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "lips_makeup", "excludes_values": _BARE_LIPS,
        "reason": f"'{_style}' requires visible lip colour; bare lips contradict it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "blush", "excludes_values": _NO_BLUSH,
        "reason": f"'{_style}' expects visible blush; bare cheeks contradict it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "contour", "excludes_values": _NO_CONTOUR,
        "reason": f"'{_style}' expects contouring; an untouched face contradicts it"})
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "makeup_style", "value": _style,
        "excludes_field": "highlight", "excludes_values": _NO_HIGHLIGHT,
        "reason": f"'{_style}' expects highlight; bare skin contradicts it"})


# Expression drives the mouth/smile state so the rendered smile_type never
# contradicts the face (smile_type is the single mouth field now -- teeth_visibility
# was merged out). Three buckets: a closed non-smiling mouth, a closed-lip soft
# smile, and an open toothy grin. Expressions left out of all three are genuinely
# ambiguous (playful, smirking, surprised, coy, ...) and keep a free smile_type draw.
_CLOSED_EXPRESSIONS = ["neutral", "serious", "stern", "intense gaze",
                       "pensive and thoughtful", "contemplative", "sultry",
                       "serene", "determined", "calm and composed", "at ease",
                       "steely", "focused", "brooding", "melancholic",
                       "lost in thought", "wistful", "skeptical", "daydreaming",
                       # 0.82.0 additions
                       "defiant", "solemn", "unimpressed",
                       # 1.5.0 additions
                       "weary", "mildly annoyed"]
_SOFT_SMILE_EXPRESSIONS = ["subtle soft smile", "warm smile", "bright smile",
                           "gentle smile",
                           # 0.82.0: "quietly content" is a closed-lip smile;
                           # "delighted" reads open-mouthed but is safest as a
                           # broad smile rather than a full toothy grin.
                           "quietly content", "delighted", "hopeful"]  # hopeful 1.5.0
_OPEN_EXPRESSIONS = ["wide toothy grin", "laughing", "candid mid-laugh", "beaming"]
# `sly` is deliberately left unbucketed, matching `smirking` -- a sly look works
# with a closed mouth or a one-sided smile, so the draw stays free.
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

# Hair texture gates the two styles that physically require coiled hair. An afro
# or twist-out on pin-straight/silky/wavy hair is a visible contradiction (the
# style IS the texture). Only these two styles are truly texture-bound — braids,
# locs, cornrows and bantu knots read fine on any texture, so they stay unpaired.
# Keyed on texture (the physical constraint) like the hair_length gate above:
# when a straight/wavy texture is drawn, afro/twist-out leave the style pool. If a
# preset instead LOCKS afro/twist-out, the engine's contrapositive repair re-rolls
# the randomized texture toward a coiled value, so an afro archetype stays coherent.
_TEXTURE_BOUND_STYLES = ["afro", "twist-out"]
_NON_COILED_TEXTURES = [
    "pin straight", "sleek straight", "silky and glossy", "slightly wavy",
    "loosely wavy", "wavy", "beachy waves",
]
for _texture in _NON_COILED_TEXTURES:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": _TEXTURE_BOUND_STYLES,
        "reason": f"{_texture} hair cannot form an afro or twist-out"})

# Masculine presentation defaults (gender == "Male").
# Many fields (nails, lip colour, jewellery, hairstyle) share one option pool
# across genders, so the random fill would otherwise hand a male character
# feminine-coded makeup, polish, pearls or pigtails. These rules govern ONLY the
# RANDOM fill: a value locked by the user, an archetype, or a cosplayer signature
# is in the engine's ``locked`` set, so the constraint warns and KEEPS it — which
# is exactly what faithful crossplay (a man cosplaying a pigtailed character)
# needs. "Any" is unaffected (it deliberately mixes both genders' pools).
# Makeup is a wardrobe *presentation* choice, not anatomy -- the same reasoning that
# gates the jewellery/nail trims below. Before 0.72.0 this rule was ungated, so a man
# with wardrobe="Feminine" drew feminine jewellery, nails and a skirt but was bare-
# faced in 300 of 300 seeds: the most visible half of the femme look was the one part
# the presentation switch could not reach. Gated, "Match gender" (the default) is
# unchanged -- only an explicit Feminine/"Any" wardrobe opens the field, and even then
# makeup_style's male pool is just "no makeup" plus the four natural styles, with
# male_weights already leaning 2x toward "no makeup" (~1 in 3 stays bare-faced).
# Bold/full glam still needs an explicit lock, which _GENDER_FLEXIBLE_GROUPS honours.
CONSTRAINT_RULES.append({
    "type": "requirement", "field": "gender", "value": "Male",
    "requires_field": "makeup_style", "requires_value": "no makeup",
    "presentation_gated": True,
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
        # 1.5.0 round 2: delicate / jewelled / layered pendants read feminine on men.
        "delicate gold chain", "diamond pendant", "gemstone pendant",
        "layered pendant necklaces", "layered gold chains",
    ],
    # 1.5.0 round 2: an upper-lip medusa is a feminine-coded placement.
    "piercings": ["medusa piercing"],
    # 1.4.0: `brooch` was missing from this list, so it stayed in the random male
    # pool -- MEASURED at 50 of 297 default male renders (17%) with
    # `wardrobe="Match gender"`, the most visible feminine-coded piece still landing
    # on men. `arm cuff` stays available, so the masculine pool is not just absence.
    "other_jewelry": ["anklet", "body chain", "waist chain", "brooch"],
    # 1.4.0. `accessories` was the last shared pool with NO masculine trim at all --
    # the same class of miss as the 0.83.0 `footwear` and 0.97.0 `bag` entries, and
    # found the same way (a measured sweep). MEASURED before the fix over 297 default
    # male renders: 18 drew long opera gloves or a waist-cinching belt. Unlike those
    # two fields `accessories` carries a `weights` map, but it covers only the nine
    # eyewear values and the field is absent from FIELD_FAMILIES, so the cull re-picks
    # proportionally among the survivors and concentrates no family weight.
    # Deliberately NOT trimmed, because a man wears them too: `wide brim sun hat`,
    # `beret`, `silk neck scarf`, `statement belt`.
    "accessories": [
        "long opera gloves", "belt cinching waist",
        "cat eye sunglasses", "cat-eye eyeglasses",
    ],
    "rings": ["stacked thin bands", "delicate gemstone", "midi ring"],
    "bracelet": ["tennis bracelet", "charm bracelet", "bangle stack"],
    # 0.83.0. `footwear` is a unisex pool, so feminine-coded shoes could always land on
    # a random man -- they simply never RENDERED before this revision, which is why the
    # trim was never needed. Caught in the preview pass: "a monochrome black tailored
    # suit with a fine-knit shirt and no tie, in kitten heels" on a male subject. Gated
    # on presentation like the jewellery trims, so a Feminine/"Any" wardrobe on a man
    # keeps them available -- the whole point of that mechanism. `wedges` / `mules` /
    # `heels` were in the pool before 0.83.0 and were already landing on men invisibly.
    "footwear": ["heels", "kitten heels", "wedges", "mules", "ballet flats",
                 "knee-high boots", "mary janes",  # mary janes 0.97.0
                 "flats", "platform boots"],  # 1.5.0 round 2
    # 0.97.0, and the same class of miss as the footwear trim above: `bag` shares one
    # pool across genders and was the last feminine-coded field with no trim at all.
    # MEASURED before the fix, over 1000 male renders at the default
    # wardrobe="Match gender": 137 (13.7%) carried a strictly feminine handbag --
    # "a fine-knit poplin shirt and a silk tie in a floral print, in loafers, carrying
    # an envelope clutch in gold". Presentation-gated like the other wardrobe trims,
    # so a Feminine/"Any" wardrobe on a man keeps the whole pool.
    #
    # Deliberately NOT trimmed: `canvas tote`, the leather totes, the crossbodies, the
    # saddlebags, the belt bags and the mini backpacks. Those are unisex carriers and
    # culling them would leave the masculine pool almost empty -- which is why the
    # three men's bags ship in the same revision (see data/fields.py).
    "bag": [
        "structured top handle bag in black", "structured top handle bag in cream",
        "structured top handle bag in tan", "envelope clutch in black",
        "envelope clutch in gold", "envelope clutch in nude", "woven rattan bag",
        "small quilted chain bag", "beaded evening clutch", "velvet evening bag",
        "straw beach tote", "printed silk scarf tied as bag accent",
        # 1.5.0 round 2: rendered as handbags on men in maintainer testing.
        "saddlebag in brown", "saddlebag in black", "saddlebag in cognac",
        "small black leather crossbody", "tan leather crossbody",
        "mini backpack in black", "mini backpack in tan",
        # 1.5.0 round 3: a leather tote on a man rendered as a purse.
        "leather tote in black", "leather tote in tan", "leather tote in cognac",
    ],
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
    # 1.5.0 -- the body half of the 1.4.0 "men with female body parts" report. These
    # four fields share ONE list across genders and had no trim, so feminine-coded
    # shape words landed on men. MEASURED over 1999 default male renders: 30% drew one
    # of these seven body types (petite and curvy 5.7%, voluptuous 5.3%, curvy 5.1%,
    # hourglass 4.9%, full figured 4.4%, softly curved 4.2%), and "petite" was in 35%
    # of male prose (body type, height and nose together). Anatomy, so NOT
    # presentation-gated. All four fields are flat, so the re-pick is bias-clean.
    "body_type": ["softly curved", "curvy", "full figured", "voluptuous", "hourglass",
                  "petite and slim", "petite and curvy"],
    "hips": ["full", "very full", "rounded"],
    "waist": ["very narrow"],
    "height": ["very petite", "petite", "statuesque"],
    "nose": ["petite"],
}
# Jewellery & nails are a wardrobe *presentation* choice, not anatomy: their trims
# are gated on the resolved presentation so a man with a Feminine/"Any" wardrobe can
# still draw feminine-coded pieces. The rest (hair, brows, lips, eye shape, bust) are
# structural/anatomical male defaults and always apply for a male character.
_PRESENTATION_GATED_FIELDS: frozenset[str] = frozenset({
    "nails", "earrings", "necklace", "other_jewelry", "rings", "bracelet",
    "footwear",     # 0.83.0 -- a wardrobe choice, not anatomy, so it gates like jewellery
    "bag",          # 0.97.0 -- likewise
    "accessories",  # 1.4.0 -- gloves, belts and frames are wardrobe, not anatomy
    "piercings",    # 1.5.0 -- adornment, not anatomy
})
for _field, _excluded in _MALE_EXCLUDED_VALUES.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "gender", "value": "Male",
        "excludes_field": _field, "excludes_values": _excluded,
        "presentation_gated": _field in _PRESENTATION_GATED_FIELDS,
        "reason": f"feminine-coded {_field} is not a male default"})

#: 1.5.0 round 2: feminine-coded HAIR, trimmed only for a MASCULINE presentation. The
#: 0.x `hair_style` trims above are structural (always on); these are styling, so a
#: man with a Feminine/"Any" wardrobe keeps them -- the maintainer's crossplay rule.
#: Partial culls of their families are deliberate and cheap here: the masculine
#: family weights (fields.py MASCULINE_FAMILY_WEIGHTS) already shrink those families.
_MASCULINE_EXCLUDED_VALUES: dict[str, list[str]] = {
    "hair_style": [
        "milkmaid braids", "waterfall braid", "braided bun", "side braid", "French braid",
        "loose braids", "rope braid", "chignon", "sleek bun", "freshly blown out",
        "blunt bangs", "micro bangs", "wispy bangs", "side ponytail", "bubble ponytail",
        "hair puff", "braided ponytail",  # braided ponytail 1.5.0 round 4
    ],
    "hair_length": ["short pixie"],
    "hair_part": ["zigzag part"],  # 1.5.0 round 4
    # 1.5.0 round 4: hoops and an ear cuff read as women's earrings on men (studs stay);
    # a thumb ring and a statement belt read feminine; a canvas tote reads as a purse;
    # "ankle boots" on a man rendered a heeled boot.
    "earrings": ["small gold hoops", "silver hoops", "ear cuff"],
    "rings": ["thumb ring"],
    "accessories": ["statement belt", "silk neck scarf"],
    # 1.5.0 round 4 QA: a thin headband rendered as a women's hairband on a man.
    "hair_accessory": ["thin headband"],
    "bag": ["canvas tote"],
    "footwear": ["ankle boots"],
    # 1.5.0 round 3: read as a feminine pose on men in the QA renders.
    "pose": ["posing with a hand on one hip", "kneeling gracefully"],
}
for _field, _excluded in _MASCULINE_EXCLUDED_VALUES.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "gender", "value": "Male",
        "excludes_field": _field, "excludes_values": _excluded,
        "presentation_gated": True,
        "reason": f"feminine-coded {_field} is not a masculine default"})

# --- Setting: a featureless backdrop has no environment ------------------
# Since 0.63.0 every shot_type describes the camera only, so shot choice is
# otherwise independent of where the shot happens -- no indoor/outdoor rules are
# needed. The one exception is the void backdrops: framings that promise to reveal
# or establish an environment contradict a seamless sweep with nothing in it.
#
# ``location`` is the TRIGGER (not the target), so the picked location always
# stands and the camera adapts to it. A user who *locks* one of these shots gets
# the engine's contrapositive repair instead: the randomized location re-rolls
# away from the void backdrops, which is the behaviour you want.
#
# "photography studio with backdrop" is deliberately absent: it is a real room
# (stands, lights, sweep) and reads fine in an establishing or environment shot.
#
# 0.65.0: this used to hand-duplicate the four backdrop strings; now that the
# module imports fields.py anyway, reuse STUDIO_BACKDROPS directly so the two
# lists can't drift on a future backdrop addition.
_VOID_BACKDROPS: list[str] = sorted(STUDIO_BACKDROPS)
_ENVIRONMENT_SHOTS: list[str] = [
    "extreme wide establishing shot", "full body shot with environment visible",
]
for _backdrop in _VOID_BACKDROPS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _backdrop,
        "excludes_field": "shot_type", "excludes_values": _ENVIRONMENT_SHOTS,
        "reason": f"a {_backdrop} is a featureless void with no environment to "
                  f"establish or reveal"})


# --- Setting: the light has to match where you are ---------------------------
# shot_type lost this class of incoherence in 0.63.0 by becoming camera-only, but
# lighting cannot follow: "golden hour sunlight" is inherently outdoors and there
# is no way to say it that isn't. Without these rules the engine happily produced
# "indoor spice market stall, under dappled sunlight through forest canopy".
#
# Same doctrine as the backdrop rule above: ``location`` is the TRIGGER, so the
# picked place always stands and the light adapts to it. Locking a light instead
# hands the engine its contrapositive repair -- the randomized location re-rolls
# to somewhere that light can exist.
#
# The buckets live in data/fields.py next to OUTDOOR_LOCATIONS (which the
# location_setting control already maintains) and are split along whole
# LIGHTING_FAMILIES boundaries wherever possible to keep the post-exclusion draw
# proportional. See the commentary there for why.
_ALL_LOCATIONS: list[str] = list(FIELD_DEFINITIONS["location"]["female_options"])
_ALL_FOOTWEAR: list[str] = list(FIELD_DEFINITIONS["footwear"]["female_options"])
_ALL_PATTERNS: list[str] = list(FIELD_DEFINITIONS["clothing_pattern"]["female_options"])
_ALL_LIGHTING: list[str] = list(FIELD_DEFINITIONS["lighting"]["female_options"])

# Void backdrops are indoor, but get the stricter studio-only rule below instead.
_INDOOR_LOCATIONS: list[str] = [
    _loc for _loc in _ALL_LOCATIONS
    if _loc not in OUTDOOR_LOCATIONS and _loc not in STUDIO_BACKDROPS
]
_VOID_EXCLUDED_LIGHTING: list[str] = sorted(
    _light for _light in _ALL_LIGHTING if _light not in VOID_ALLOWED_LIGHTING
)

for _loc in _INDOOR_LOCATIONS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "lighting", "excludes_values": sorted(OUTDOOR_ONLY_LIGHTING),
        "reason": f"'{_loc}' is indoors: open-sky light cannot reach it "
                  f"(indoor daylight is the 'window' family's job)"})

for _loc in sorted(OUTDOOR_LOCATIONS):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "lighting", "excludes_values": sorted(INDOOR_ONLY_LIGHTING),
        "reason": f"'{_loc}' is outdoors: no window, ceiling fixture, hearth, "
                  f"or television lights it"})

for _backdrop in _VOID_BACKDROPS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _backdrop,
        "excludes_field": "lighting", "excludes_values": _VOID_EXCLUDED_LIGHTING,
        "reason": f"a {_backdrop} is a studio sweep: only studio lighting exists "
                  f"there, and every other value implies a place"})

# Fixture lighting (0.82.0): indoors is necessary but not sufficient. A hearth, a
# television and a stained-glass window are objects, so the rule is per-location
# rather than per-bucket -- "a neighborhood pharmacy, under flickering firelight
# from a hearth" is what prompted it.
#
# One rule per location listing every fixture that location LACKS, rather than one
# rule per (location, fixture) pair: ~139 rules instead of ~380, and the engine
# already unions all firing exclusions on a target, so a single combined rule
# behaves identically. Each excluded value is its own single-variant LIGHTING
# family, so every one of these is a whole-family drop and the surviving families
# stay exactly proportional.
#
# Allowlist semantics mean a NEW location is excluded from all three fixtures
# until it is deliberately added to a set in fields.py -- the safe default.
# complexion <-> skin_tone (0.82.0). `peaches and cream` names a pink-white
# colouring, not a surface quality, so it contradicts a deep tone outright --
# real output read "deep ebony skin. ... Her skin shows a peaches and cream
# complexion." The field is FLAT (no FIELD_FAMILIES entry, no `weights`), so
# dropping one value re-picks flat-uniform over the other four and the
# whole-family rule does not apply. `clear` / `rosy` / `ruddy` / `sallow` are
# deliberately untouched: redness and pallor read on any skin tone.
for _tone in sorted(DEEP_SKIN_TONES):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "skin_tone", "value": _tone,
        "excludes_field": "complexion", "excludes_values": ["peaches and cream"],
        "reason": f"'peaches and cream' is a pink-white colouring, not a surface "
                  f"quality: it cannot describe {_tone} skin"})

# 0.83.0 widens this loop from _INDOOR_LOCATIONS to EVERY location, so the same
# mechanism can carry `stage spotlight from above` -- a fixture that has to be
# allowlisted at an OUTDOOR place (`outdoor amphitheater`) as well as excluded from
# indoor places with no rig. For the three indoor-only fixtures an outdoor rule is
# redundant with the bucket rule above; that is harmless, because the engine unions
# every firing exclusion on a target.
# =========================================================================
# The wardrobe axis (0.83.0): footwear x outfit_style, and palette x pattern
# =========================================================================
#
# `footwear` renders as of 0.83.0. Before that it was drawn and thrown away, so the
# three rules that existed (athletic / business formal / evening formal) were silently
# correct and invisible, and the other ELEVEN styles had no rule at all. Turning the
# field on would immediately have started rendering slippers with a business suit.
#
# Those three hand-written rules were replaced by the ALLOWLIST below -- what each
# style CAN wear rather than what it cannot. Two reasons. The old deny-lists were
# incomplete in a way that is invisible on inspection (`athletic` denied heels,
# loafers, oxfords, slippers and sandals but still permitted bare feet, wedges and
# mules), and a deny-list silently admits every value added later -- the 12 -> 20
# footwear growth in this same revision would have leaked `kitten heels` into
# sportswear. An allowlist fails safe: a NEW shoe is excluded from every style until
# it is deliberately listed, the same safety model as the fixture-lighting allowlists.
#
# BIAS: `footwear` is FLAT -- no FIELD_FAMILIES entry, no `weights` map -- so an
# exclusion re-picks flat-uniform over the survivors. This is the case the 0.82.0
# "a flat field is where a partial cull is FINE" note exists for; the whole-family
# rule does not apply.
FOOTWEAR_BY_STYLE: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ("casual", frozenset(['boat shoes', 'work boots', 'slides',  # 1.5.0
        'sneakers', 'loafers', 'boots', 'flats', 'sandals', 'ankle boots', 'mules',
        'chelsea boots', 'combat boots', 'ballet flats', 'high-top sneakers',
        'espadrilles', 'mary janes', 'cowboy boots',
        'hiking boots', 'clogs'])),  # 1.2.0
    ("smart casual", frozenset(['boat shoes',  # 1.5.0
        'sneakers', 'loafers', 'boots', 'heels', 'flats', 'oxfords', 'ankle boots',
        'wedges', 'mules', 'chelsea boots', 'knee-high boots', 'ballet flats',
        'derbies', 'kitten heels', 'mary janes'])),
    ("business casual", frozenset([
        'loafers', 'heels', 'flats', 'oxfords', 'ankle boots', 'wedges', 'mules',
        'chelsea boots', 'ballet flats', 'derbies', 'kitten heels'])),
    ("business formal", frozenset([
        'loafers', 'heels', 'oxfords', 'derbies', 'kitten heels', 'ankle boots'])),
    ("evening formal", frozenset(['heels', 'oxfords', 'derbies', 'kitten heels'])),
    ("cocktail semi-formal", frozenset([
        'heels', 'oxfords', 'loafers', 'ankle boots', 'mules', 'derbies',
        'kitten heels', 'knee-high boots'])),
    ("streetwear", frozenset(['work boots', 'slides',  # 1.5.0
        'sneakers', 'boots', 'ankle boots', 'combat boots', 'high-top sneakers',
        'chelsea boots', 'mules', 'cowboy boots',
        'platform boots'])),  # 1.2.0
    ("bohemian", frozenset([
        'sandals', 'boots', 'flats', 'ankle boots', 'wedges', 'mules', 'bare feet',
        'espadrilles', 'ballet flats', 'knee-high boots', 'cowboy boots',
        'clogs'])),  # 1.2.0
    ("athletic", frozenset(['slides', 'sneakers', 'high-top sneakers',
                             'hiking boots'])),  # 1.2.0
    ("resort vacation", frozenset(['boat shoes', 'slides',  # 1.5.0
        'sandals', 'flats', 'wedges', 'mules', 'bare feet', 'espadrilles',
        'sneakers', 'ballet flats'])),
    ("edgy alternative", frozenset(['work boots',  # 1.5.0
        'boots', 'combat boots', 'ankle boots', 'chelsea boots', 'knee-high boots',
        'heels', 'sneakers', 'high-top sneakers', 'cowboy boots', 'mary janes',
        'platform boots'])),  # 1.2.0
    ("preppy", frozenset(['boat shoes',  # 1.5.0
        'loafers', 'oxfords', 'sneakers', 'flats', 'ankle boots', 'chelsea boots',
        'ballet flats', 'derbies', 'espadrilles', 'kitten heels', 'mary janes'])),
    ("vintage retro", frozenset([
        'loafers', 'oxfords', 'heels', 'flats', 'ankle boots', 'wedges', 'mules',
        'derbies', 'kitten heels', 'ballet flats', 'chelsea boots', 'mary janes',
        'cowboy boots', 'platform boots'])),  # 1.2.0
    ("loungewear", frozenset(['slides', 'slippers', 'bare feet', 'flats', 'ballet flats',
                               'clogs'])),  # 1.2.0
    ("utility workwear", frozenset(['work boots',  # 1.5.0
        'boots', 'hiking boots', 'combat boots', 'chelsea boots', 'ankle boots',
        'sneakers', 'high-top sneakers', 'clogs', 'cowboy boots'])),  # 1.5.0
])

for _style, _allowed in FOOTWEAR_BY_STYLE.items():
    _banned = sorted(set(_ALL_FOOTWEAR) - _allowed)
    if _banned:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": "footwear", "excludes_values": _banned,
            "reason": f"these shoes do not belong with {_style} dress"})


# --- legwear x outfit_style (1.2.0) ------------------------------------------------
# Mirrors FOOTWEAR_BY_STYLE above exactly, including the allowlist-not-denylist safety
# model: a value absent from a style's set is excluded there, so a future men's legwear
# addition is excluded everywhere until it is deliberately listed. Without this,
# 'athletic crew socks' lands on `business formal`.
#
# SCOPE: the three MALE values added at 1.2.0, and nothing else. `_GATED_LEGWEAR`
# below is the entire universe this loop bans from, so every female value is
# untouched and women's draws stay byte-identical to 1.1.0 -- which is the point.
# Gating the female pool as well is genuinely missing ('fishnet tights' can still land
# on `business formal`), but it would move `legwear` prose across the shipped roster
# and `entry_hash` hashes the entry dict, not the resolved prose, so `--check` could
# not flag one invalidated gallery image. Logged in docs/suggested-additions.md
# "Still to consider" instead of done here.
#
# BIAS: `legwear` is FLAT -- no FIELD_FAMILIES entry -- so an exclusion re-picks
# uniform over the survivors, with the `male_weights` lean on 'no visible legwear'
# applied on top. 'no visible legwear' is in every style's set, so the pool can
# never empty.
#
# 1.5.0 round 4: the women's values joined -- "a one-shoulder chiffon gown with fishnet
# tights" and "a business-casual midi dress with patterned tights" were flagged renders,
# and the gallery-hash worry above does not apply to an unreleased minor.
_TIGHTS = ['sheer black tights', 'opaque black tights', 'sheer stockings']
LEGWEAR_BY_STYLE: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ("casual", frozenset(['ribbed crew socks', 'athletic crew socks', 'sheer black tights',
                          'opaque black tights', 'opaque cream tights',
                          'ribbed knee-high socks', 'slouchy ankle socks'])),
    ("smart casual", frozenset(['dark dress socks', 'opaque cream tights', *_TIGHTS])),
    ("business casual", frozenset(['dark dress socks', *_TIGHTS])),
    ("business formal", frozenset(['dark dress socks', *_TIGHTS])),
    ("evening formal", frozenset(['dark dress socks', 'sheer black tights', 'sheer stockings'])),
    ("cocktail semi-formal", frozenset(['dark dress socks', *_TIGHTS])),
    ("streetwear", frozenset(['ribbed crew socks', 'athletic crew socks', 'fishnet tights',
                              'opaque black tights', 'patterned tights', 'ribbed knee-high socks',
                              'over-the-knee socks', 'slouchy ankle socks'])),
    ("bohemian", frozenset(['opaque cream tights', 'patterned tights', 'opaque black tights',
                            'slouchy ankle socks', 'over-the-knee socks'])),
    ("athletic", frozenset(['athletic crew socks', 'slouchy ankle socks'])),
    ("resort vacation", frozenset()),
    ("edgy alternative", frozenset(['fishnet tights', 'opaque black tights', 'patterned tights',
                                    'sheer black tights', 'over-the-knee socks',
                                    'ribbed knee-high socks'])),
    ("preppy", frozenset(['ribbed crew socks', 'ribbed knee-high socks', 'opaque black tights',
                          'opaque cream tights', 'sheer black tights', 'over-the-knee socks'])),
    ("vintage retro", frozenset(['ribbed crew socks', 'dark dress socks', 'sheer stockings',
                                 'sheer black tights',
                                 'opaque black tights', 'slouchy ankle socks',
                                 'ribbed knee-high socks'])),
    ("loungewear", frozenset(['ribbed crew socks', 'slouchy ankle socks'])),
    ("utility workwear", frozenset(['ribbed crew socks', 'athletic crew socks',
                                    'slouchy ankle socks'])),
])
#: Every value LEGWEAR_BY_STYLE may exclude: the shipped pool (a user value passes).
_GATED_LEGWEAR: frozenset[str] = frozenset(
    v for g in ("female_options", "male_options") for v in FIELD_DEFINITIONS["legwear"][g]
    if v != "no visible legwear")

# NO CONSTRAINT_RULES LOOP HERE, and that is the whole point of this comment.
# `legwear` is a DEFERRED field (`nodes.identity_forge._DEFERRED_FIELDS`): it is drawn
# after the constraint-resolution loop has already finished, because it has to gate on
# the composed `outfit_description`, which does not exist while the loop runs. An
# `outfit_style` -> `legwear` exclusion rule is therefore structurally INERT -- measured,
# not assumed: the rule loop this replaced produced 132 violations over 400 seeds per
# style (socks on `bohemian`, `resort vacation` and `edgy alternative`, all of which
# allow none), while the identical FOOTWEAR_BY_STYLE loop produced 0, because `footwear`
# is an ordinary in-loop field.
#
# The map above is consumed instead by `nodes.identity_forge._style_appropriate_legwear`,
# a pool filter applied in `_resolve_deferred_fields` alongside `_wearable_legwear` --
# the mechanism that actually runs for a deferred field.

# `mixed prints` is a PATTERN claim living in the colour field (a pre-existing wart, and
# not worth a breaking rename), while `all black` / `all white` / `black monochrome` /
# `white and cream` are MONOCHROME claims. Either way, composing them with a second,
# multi-colour pattern renders a contradiction the preview caught immediately: "an
# all-white quilted field jacket ... in denim" and "a mixed-print gown ... in a floral
# print". Both fields are flat, so these culls re-pick flat-uniform.
#
# `stripes` and `subtle texture` are deliberately still allowed on a monochrome palette:
# tonal stripes and a self-coloured texture are real, and an all-black pinstripe is a
# staple. `solid` is allowed everywhere by construction.
_MULTICOLOUR_PATTERNS: list[str] = [
    'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim', 'plaid',
    # 0.97.0. Filed with 'plaid' rather than with the two-tone patterns the 0.90.0
    # batch deliberately left out ('houndstooth', 'gingham', 'pinstripe', 'polka dot'):
    # the classic argyle lattice is three colours plus a contrasting overstitch, so an
    # "all black" palette leaves it nothing to be.
    'argyle',
]
for _colour in ('all black', 'all white', 'black monochrome', 'white and cream'):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "clothing_color", "value": _colour,
        "excludes_field": "clothing_pattern", "excludes_values": _MULTICOLOUR_PATTERNS,
        "reason": f"'{_colour}' is a monochrome palette: a multi-colour print "
                  f"contradicts it outright"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "clothing_color", "value": 'mixed prints',
    "excludes_field": "clothing_pattern",
    "excludes_values": sorted(set(_ALL_PATTERNS) - {'solid'}),
    "reason": "'mixed prints' already states the pattern; naming a second one "
              "renders 'a mixed-print gown in a floral print'"})

for _loc in _ALL_LOCATIONS:
    _absent_fixtures = sorted(
        _light for _light, _places in FIXTURE_LIGHTING.items() if _loc not in _places
    )
    if _absent_fixtures:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "lighting", "excludes_values": _absent_fixtures,
            "reason": f"'{_loc}' has no such fixture: a hearth, a television, a "
                      f"stained-glass window or a stage rig has to actually be there"})

# --- composition <-> shot_type coherence (0.85.0) -----------------------------------
# `composition` is frame LAYOUT (where the subject sits), `shot_type` is camera distance
# / height / angle / lens. Both are flat fields (absent from FIELD_FAMILIES, no `weights`
# map), so every exclusion below re-picks uniform rather than concentrating weight on
# survivors -- the same reasoning that already governs shot_type's own exclusions.
_ENVIRONMENT_DEPENDENT_COMPOSITIONS = [
    'the subject small against open negative space',
    'leading lines drawing the eye to the subject',
    'a low horizon line and open sky above',
    'a high horizon line and a sliver of sky',
]
_TIGHT_SHOT_TYPES = [
    'extreme close-up on face', 'close-up portrait', 'medium close-up from chest up',
]
for _shot in _TIGHT_SHOT_TYPES:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "shot_type", "value": _shot,
        "excludes_field": "composition",
        "excludes_values": list(_ENVIRONMENT_DEPENDENT_COMPOSITIONS),
        "reason": "a tight shot leaves no environment in frame to compose"})

CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "shot_type", "value": "wide shot with subject at center",
    "excludes_field": "composition",
    "excludes_values": ["the subject on a rule-of-thirds line",
                         "the subject small against open negative space"],
    "reason": "the shot type already states the subject is centered"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "shot_type", "value": "wide shot with subject off-center",
    "excludes_field": "composition", "excludes_values": ["centered symmetry"],
    "reason": "the shot type already states the subject is off-center"})

_WIDE_ENVIRONMENT_SHOTS = ['full body shot with environment visible',
                           'extreme wide establishing shot']
for _shot in _WIDE_ENVIRONMENT_SHOTS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "shot_type", "value": _shot,
        "excludes_field": "composition",
        "excludes_values": ["a tight crop and little headroom",
                             "the subject filling most of the frame"],
        "reason": "a wide establishing shot cannot also be a tight crop"})

# A selfie is framed like the other tight shots -- little to no environment in view --
# so it shares the tight-shot exclusion above rather than a hand-rolled duplicate list.
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "shot_type", "value": "selfie framing at arm's length",
    "excludes_field": "composition",
    "excludes_values": list(_ENVIRONMENT_DEPENDENT_COMPOSITIONS),
    "reason": "an arm's-length selfie leaves no environment in frame to compose"})


# --- composition <-> location coherence (1.2.0) -------------------------------------
# The 0.85.0 block above gates composition against the CAMERA. This one gates it
# against the PLACE, which is the gap that was left: "a low horizon line and open sky
# above" asserts open sky, and an indoor location has none. Three sampled renders with
# an indoor location and a sky composition came back as tight close-ups instead of the
# requested framing, even with a correct locked shot_type -- the model resolved the
# contradiction by discarding the composition.
#
# The justification does not need the render theory. Both sky values ASSERT open sky as
# a fact about the frame; an interior contradicts that assertion outright. That is the
# same incoherence the 0.64.0 location -> lighting rules exist to remove, and the same
# doctrine applies: **location is the TRIGGER**, so the picked place stands and the
# composition adapts. Gating the other way round would hand a locked composition the
# engine's contrapositive repair and re-roll the location out from under the user.
#
# `composition` is FLAT (absent from FIELD_FAMILIES, no `weights` map), so each
# exclusion below re-picks uniform over the survivors and no weight concentrates --
# the same arithmetic stated in the 0.85.0 block above.
#
# Taken by name out of _ENVIRONMENT_DEPENDENT_COMPOSITIONS rather than retyped, so a
# future edit to that list cannot leave these two rules pointing at dead strings.
_SKY_COMPOSITIONS: list[str] = [
    _comp for _comp in _ENVIRONMENT_DEPENDENT_COMPOSITIONS if "sky" in _comp
]

for _loc in _INDOOR_LOCATIONS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "composition", "excludes_values": list(_SKY_COMPOSITIONS),
        "reason": f"'{_loc}' is indoors: there is no horizon line or open sky to place"})

# A void backdrop loses one more: a seamless sweep is a featureless void, so there is
# nothing in it to lead the eye with either. Deliberately KEPT is "the subject small
# against open negative space", which is precisely what a sweep does, along with the
# four camera-side values ("a tight crop and little headroom", "centered symmetry",
# "the subject filling most of the frame", "the subject on a rule-of-thirds line").
for _backdrop in _VOID_BACKDROPS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _backdrop,
        "excludes_field": "composition",
        "excludes_values": _SKY_COMPOSITIONS + [
            "leading lines drawing the eye to the subject"],
        "reason": f"a {_backdrop} is a seamless sweep: no horizon, no sky, and no "
                  f"lines in it to lead the eye"})


# --- outfit_style answers to the place (1.5.0) ------------------------------------
# Before 1.5.0 `outfit_style` was drawn with no reference to `location` at all:
# measured over 6000 default renders, evening gowns landed in an emergency room, a
# laundromat and a suburban basement, loungewear in a chemistry lab and a machine shop,
# resort wear in a prison visiting room. The base node exists to make a believable
# everyday person, so the place now decides what is plausible to wear there.
#
# Same doctrine as lighting and composition: `location` is the TRIGGER, so the place
# stands and the style adapts. Locking a style hands the engine its contrapositive
# repair (the random location re-rolls to somewhere that style is worn), and locking
# both keeps both. `outfit_style` is FLAT (no FIELD_FAMILIES entry, no `weights`), so
# every cull re-picks uniform over the survivors.
#
# Resolution per location: an explicit VENUE set if it has one, else its location
# family's set; then EXTRAS are added and REMOVALS taken away. A location the family
# map does not know (a user_options.json addition) gets no rule, so it allows every
# style -- custom places are never silently narrowed.
_EVERYDAY_STYLES: frozenset[str] = frozenset([
    "casual", "smart casual", "streetwear", "bohemian", "edgy alternative", "preppy",
    "vintage retro"])
_OUTDOORS_STYLES: frozenset[str] = frozenset([
    "casual", "streetwear", "bohemian", "edgy alternative", "preppy", "vintage retro",
    "athletic"])
#: SHIPPED styles only -- the keys of FOOTWEAR_BY_STYLE, which the validator requires to
#: be exactly the shipped set. A style added through user_options.json must never be
#: banned: measured in the 1.5.0 blast-radius pass, reading the live option list here put
#: a user style in every location's ban list and it drew 0 of 3000.
_ALL_STYLES: list[str] = list(FOOTWEAR_BY_STYLE)

OUTFIT_STYLES_BY_LOCATION_FAMILY: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ("domestic", _EVERYDAY_STYLES | {"business casual", "athletic", "loungewear"}),
    ("food_drink", _EVERYDAY_STYLES | {"business casual", "business formal", "athletic"}),
    ("retail_services", _EVERYDAY_STYLES | {"business casual", "athletic"}),
    ("leisure_fitness", _EVERYDAY_STYLES | {"athletic"}),
    ("civic_institutional", _EVERYDAY_STYLES | {
        "business casual", "business formal", "athletic"}),
    ("work_industrial", _EVERYDAY_STYLES | {"business casual", "business formal"}),
    ("transit_travel", _EVERYDAY_STYLES | {
        "business casual", "business formal", "athletic", "resort vacation"}),
    ("urban_outdoor", _EVERYDAY_STYLES | {
        "business casual", "business formal", "athletic", "utility workwear"}),
    ("urban_landmark", _EVERYDAY_STYLES | {
        "business casual", "business formal", "athletic", "resort vacation",
        "cocktail semi-formal"}),
    ("nature_outdoor", _OUTDOORS_STYLES),
    ("nature_landmark", _OUTDOORS_STYLES | {"smart casual", "resort vacation"}),
    ("studio", frozenset(_ALL_STYLES)),
])

_GYM: frozenset[str] = frozenset(["athletic", "casual", "streetwear"])
_SHOP_FLOOR: frozenset[str] = frozenset(["utility workwear", "casual", "streetwear"])
_MAKERS: frozenset[str] = frozenset([
    "utility workwear", "casual", "streetwear", "bohemian", "edgy alternative",
    "vintage retro"])
_WATERSIDE: frozenset[str] = frozenset([
    "resort vacation", "casual", "athletic", "bohemian", "streetwear", "vintage retro",
    "preppy"])
_FORMAL_WORK: frozenset[str] = frozenset([
    "business formal", "business casual", "smart casual", "preppy"])

#: Places whose plausible wardrobe is narrower than their family's.
OUTFIT_STYLE_VENUES: dict[str, frozenset[str]] = {
    **dict.fromkeys([
        "local gym weight room", "yoga studio with wood floors",
        "climbing gym with colorful holds", "dance studio with mirrors",
        "martial arts dojo", "boxing gym with hanging heavy bags",
        "high school gymnasium", "trampoline park with foam pits"], _GYM),
    "indoor swimming pool": frozenset(["athletic", "resort vacation", "casual"]),
    **dict.fromkeys([
        "factory floor", "warehouse interior", "auto repair shop service bay",
        "print shop with running presses", "machine shop with lathes",
        "brewery tank room", "blacksmith forge with an anvil",
        "glassblowing studio with a furnace", "fishing trawler wheelhouse",
        "woodworking workshop", "commercial kitchen", "working harbor dock"],
        _SHOP_FLOOR),
    "construction site with scaffolding": _SHOP_FLOOR | {"business casual"},
    **dict.fromkeys([
        "artist's painting studio", "ceramics studio with pottery wheels",
        "home garage workshop"], _MAKERS),
    **dict.fromkeys(["corner executive office", "hotel conference room"], _FORMAL_WORK),
    "courtroom": _FORMAL_WORK | {"casual"},
    **dict.fromkeys([
        "wide sandy beach", "volcanic black sand beach", "tide pools at low tide",
        "waterfall plunge pool", "steaming hot spring pool", "sea cave mouth",
        "lakeside pier"], _WATERSIDE),
    "poolside cabana": _WATERSIDE | {"smart casual", "cocktail semi-formal"},
    "photography studio with backdrop": frozenset(_ALL_STYLES),
}

_DRESSY = frozenset(["cocktail semi-formal", "evening formal"])
_WORKWEAR = frozenset(["utility workwear"])

#: Styles a place adds on top of its family/venue set.
OUTFIT_STYLE_EXTRAS: dict[str, frozenset[str]] = {}
for _places, _styles in (
    # Getting ready, dinner parties, galas and formal nights.
    (["formal dining room with chandelier", "upscale penthouse living room with city view",
      "fine dining restaurant interior", "elegant hotel dining room",
      "dimly lit cocktail lounge", "speakeasy-style basement bar",
      "casino floor with card tables", "backstage dressing room",
      "concert hall backstage", "empty theater stage with the curtain up",
      "art gallery opening night", "grand cathedral interior",
      "hotel lobby with marble floors", "grand hotel suite",
      "cruise ship interior corridor", "the back seat of a taxi", "rooftop cocktail bar",
      "rooftop terrace overlooking the skyline", "castle courtyard"], _DRESSY),
    (["walk-in closet with mirrors", "tiled bathroom with a large mirror",
      "tidy bedroom with a neatly made bed"], _DRESSY | {"business formal"}),
    # A night out, a date, a wedding guest -- cocktail but not black tie.
    (["neon-lit nightclub", "wine bar with exposed brick", "crowded bar and grill",
      "wood-paneled pub", "gastropub with an open kitchen",
      "French bistro with mirrored walls", "sushi bar counter", "dim sum restaurant",
      "upscale urban cafe", "karaoke room with song menus", "billiards hall",
      "movie theater lobby", "independent cinema auditorium",
      "community theatre auditorium", "luxury retail boutique",
      "department store perfume counter", "hair salon", "nail salon",
      "small chapel interior", "synagogue interior", "mosque interior",
      "city hall rotunda", "neon-lit city street", "outdoor amphitheater",
      "tree-lined boulevard", "cobblestone old-town street", "city fountain plaza",
      "pier with a Ferris wheel", "riverside boardwalk", "sunlit vineyard",
      "cherry blossom grove", "botanical garden path", "airport lounge"],
     frozenset(["cocktail semi-formal"])),
    (["home office with bookshelves", "bank lobby with teller windows",
      "luxury retail boutique", "department store perfume counter",
      "neighborhood dry cleaner counter", "old-school barbershop",
      "upscale grocery market deli counter", "shopping mall concourse",
      "casino floor with card tables"], frozenset(["business formal"])),
    (["grand hotel suite", "budget motel room", "university dormitory room",
      "laundromat", "corner bodega", "fire escape landing", "quiet suburban backyard",
      "hospital room", "airplane cabin aisle"], frozenset(["loungewear"])),
    # Holidaymakers: sights, promenades, markets, scenic nature.
    (["juice bar with a chrome counter", "old-fashioned ice cream parlor",
      "taqueria with a tiled counter", "indoor spice market stall",
      "natural history museum hall", "aquarium tunnel", "science museum atrium",
      "planetarium dome interior", "casino floor with card tables",
      "palm-lined promenade", "riverside boardwalk", "pier with a Ferris wheel",
      "harbor with moored boats", "open-air street food market",
      "cobblestone old-town street", "city fountain plaza",
      "rooftop terrace overlooking the skyline", "rooftop garden", "castle courtyard",
      "crumbling stone ruin", "pedestrian shopping street", "sunny city park",
      "stone bridge over a river", "canal towpath", "flower field in bloom",
      "lavender field", "sunlit vineyard", "cherry blossom grove",
      "botanical garden path", "mangrove boardwalk", "coastal lighthouse bluff",
      "rocky coastal cliff", "basalt column coastline", "bamboo forest path",
      "terraced rice paddies", "golden savanna with acacia trees",
      "rolling desert dune"], frozenset(["resort vacation"])),
    (["sunlit vineyard", "flower field in bloom", "lavender field",
      "botanical garden path", "cherry blossom grove"], frozenset(["smart casual"])),
    # Working people on a break, on the way, or at the counter.
    (["suburban basement", "mudroom entryway", "farmhouse kitchen with open shelving",
      "rustic log cabin interior", "small-town family diner", "old-school greasy spoon",
      "barbecue joint with paper-lined trays", "bustling food court",
      "taqueria with a tiled counter", "busy chain coffee shop", "crowded bar and grill",
      "wood-paneled pub", "hardware store aisle", "bicycle repair shop",
      "butcher shop counter", "garden centre greenhouse aisle",
      "big box store warehouse aisle", "shoe repair and key cutting counter",
      "farmers market indoor stall", "corner bodega", "small-town grocery store aisle",
      "laundromat", "parking garage", "budget motel room", "long-distance bus station",
      "subway car interior", "rolling wheat field", "apple orchard rows",
      "terraced rice paddies", "sunlit vineyard", "open meadow"], _WORKWEAR),
):
    for _place in _places:
        OUTFIT_STYLE_EXTRAS[_place] = OUTFIT_STYLE_EXTRAS.get(_place, frozenset()) | _styles

#: Styles a place rules out although its family allows them. Accumulated like the
#: extras, so a place named in two lists keeps BOTH removals (a dict literal with a
#: repeated key silently kept only the last -- the rooftop bar lost its athletic ban).
OUTFIT_STYLE_REMOVALS: dict[str, frozenset[str]] = {}
for _places, _styles in (
    (["fine dining restaurant interior", "elegant hotel dining room",
      "dimly lit cocktail lounge", "speakeasy-style basement bar",
      "wine bar with exposed brick", "rooftop cocktail bar",
      "luxury retail boutique", "department store perfume counter",
      "courtroom", "grand cathedral interior", "small chapel interior",
      "mosque interior", "synagogue interior", "Buddhist temple hall",
      "Shinto shrine interior", "art gallery opening night", "city hall rotunda"],
     frozenset(["athletic"])),
    (["neon-lit nightclub"], frozenset(["athletic", "business formal"])),
    # 1.5.0 round 2: a hoodie-and-cargo look at a formal dinner or in court.
    (["fine dining restaurant interior", "elegant hotel dining room",
      "dimly lit cocktail lounge", "courtroom", "art gallery opening night"],
     frozenset(["streetwear"])),
    (["university dormitory room"], frozenset(["business formal"])),
    (["graffiti-covered skate park", "outdoor basketball court with chain nets",
      "fire escape landing", "community garden allotment", "country dirt road",
      "quiet suburban backyard"], frozenset(["business formal"])),
    (["rooftop cocktail bar", "palm-lined promenade", "castle courtyard",
      "rooftop terrace overlooking the skyline"], _WORKWEAR),
):
    for _place in _places:
        OUTFIT_STYLE_REMOVALS[_place] = OUTFIT_STYLE_REMOVALS.get(_place, frozenset()) | _styles

#: location -> its FIELD_FAMILIES family, built-in locations only.
_LOCATION_FAMILY: dict[str, str] = {
    _v: _fam for _fam, _d in FIELD_FAMILIES["location"].items() for _v in _d["variants"]}


def outfit_styles_allowed_at(location: str) -> "frozenset[str] | None":
    """The outfit styles plausible at ``location``, or ``None`` for an unmapped place."""
    family = _LOCATION_FAMILY.get(location)
    if family is None:
        return None
    allowed = OUTFIT_STYLE_VENUES.get(location, OUTFIT_STYLES_BY_LOCATION_FAMILY[family])
    return ((allowed | OUTFIT_STYLE_EXTRAS.get(location, frozenset()))
            - OUTFIT_STYLE_REMOVALS.get(location, frozenset()))


for _loc in _LOCATION_FAMILY:
    _banned = sorted(set(_ALL_STYLES) - outfit_styles_allowed_at(_loc))
    if _banned:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "outfit_style", "excludes_values": _banned,
            "reason": f"nobody plausibly dresses like that at '{_loc}'"})


# --- season is an outdoor fact (1.5.0) ---------------------------------------------
# Before 1.5.0 `season` had no rule at all. Measured over 3000 default renders: winter
# with sandals or espadrilles 3.1%, winter with shorts / a crop top / swim shorts 2.4%,
# winter with a sun hat 1.1%, summer with a beanie or gloves 0.9%, and "cherry blossom
# grove during winter" / "snowy pine forest during summer" for every seasonal place.
#
# THREE LAYERS, in rule order (a pass applies rules in list order, so the indoor drop
# must come before anything season triggers):
#
# 1. Indoors and on a studio sweep the season is DROPPED ("None"), prose and JSON.
#    Weather does not reach an office, and "during winter" in a windowless room only
#    invites the model to paint snow on a wall. This is also what keeps every clothing
#    rule below outdoors-only for free: they trigger on a season value, and indoors
#    there is none. A locked season re-rolls a random location outdoors (the
#    requirement branch's contrapositive); locking both keeps both. Zero RNG cost --
#    season is still drawn, then blanked.
# 2. A seasonal PLACE pins its season. `location` is the trigger, so the place stands.
#    `season` is FLAT, so the re-pick is uniform over what survives. The two winter
#    lights follow the season, not the other way round (see _WINTER_LIGHTING).
# 3. The season then gates what is worn (footwear, accessories, bag, outfit_style) --
#    the season stands and the clothes adapt, the lighting/composition doctrine.
#    Every target here is flat or `weights`-only, so no family weight concentrates.
#    The generated garment phrase itself is season-filtered in
#    `nodes.identity_forge._resolve_outfit_description` (WARM_ONLY_GARMENT_RE /
#    COLD_ONLY_GARMENT_RE), because the outfit is drawn after this loop has finished.
_SEASONS: list[str] = list(FIELD_DEFINITIONS["season"]["female_options"])

for _loc in _LOCATION_FAMILY:
    if _loc not in OUTDOOR_LOCATIONS:
        CONSTRAINT_RULES.append({
            "type": "requirement", "field": "location", "value": _loc,
            "requires_field": "season", "requires_value": "None",
            "reason": f"'{_loc}' is indoors: the season does not show there"})

#: Outdoor places that only look like themselves in some seasons.
SEASONS_BY_LOCATION: dict[str, frozenset[str]] = {
    "snowy pine forest": frozenset(["winter"]),
    "frozen lake surface": frozenset(["winter"]),
    "autumn park with falling leaves": frozenset(["autumn"]),
    "cherry blossom grove": frozenset(["spring"]),
    "flower field in bloom": frozenset(["spring", "summer"]),
    "alpine meadow with wildflowers": frozenset(["spring", "summer"]),
    "lavender field": frozenset(["summer"]),
}
#: Lights that only exist in winter. The SEASON is the trigger (below), not the light:
#: pinning the season to the light skewed outdoor seasons to 29% winter / 21.5% summer
#: over 4000 renders, because two of the 17 daylight variants dragged it to winter.
#: This way round the season stays uniform and only a winter light drawn out of season
#: is re-picked, which re-draws the rejected value alone (the 0.64.0 mixture property).
_WINTER_LIGHTING: list[str] = ["hazy overcast winter light", "snow-reflected daylight"]

for _loc, _allowed in SEASONS_BY_LOCATION.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "season", "excludes_values": sorted(set(_SEASONS) - _allowed),
        "reason": f"'{_loc}' only looks like that in {', '.join(sorted(_allowed))}"})
for _season in ("spring", "summer", "autumn"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "season", "value": _season,
        "excludes_field": "lighting", "excludes_values": list(_WINTER_LIGHTING),
        "reason": f"winter light does not fall in {_season}"})

#: What each season rules out. Read only outdoors: indoors the season is "None".
SEASON_EXCLUSIONS: dict[str, dict[str, list[str]]] = {
    "spring": {
        "accessories": ["knit winter scarf", "earmuffs"],
    },
    "winter": {
        "footwear": ["sandals", "espadrilles", "bare feet", "slides", "boat shoes",
                     "mules", "wedges"],  # 1.5.0 round 4
        "accessories": ["wide brim sun hat", "woven hat"],
        "bag": ["straw beach tote", "woven rattan bag"],
        "outfit_style": ["resort vacation"],
    },
    "summer": {
        "accessories": ["wool beanie", "leather gloves", "knit winter scarf", "earmuffs",
                        "fingerless gloves"],  # 1.5.0 round 4
    },
}
#: Winter pieces are weather wear, so they also stay outdoors (the 0.97.0 decline these
#: were parked on). Keyed on each indoor LOCATION, not on season "None": a rule
#: triggered by the blank season would make a locked scarf re-roll a season that the
#: indoor requirement pins straight back, and the two repairs would ping-pong to the
#: iteration cap. On the location, the contrapositive moves the place outdoors instead.
_WINTER_ONLY_ACCESSORIES: list[str] = ["knit winter scarf", "earmuffs",
                                        # 1.5.0 round 2: sun hats stay outside too
                                        "wide brim sun hat", "woven hat"]
for _loc in _LOCATION_FAMILY:
    if _loc not in OUTDOOR_LOCATIONS:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "accessories", "excludes_values": list(_WINTER_ONLY_ACCESSORIES),
            "reason": f"'{_loc}' is indoors: winter outerwear comes off"})

for _season, _by_field in SEASON_EXCLUSIONS.items():
    for _field, _values in _by_field.items():
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "season", "value": _season,
            "excludes_field": _field, "excludes_values": list(_values),
            "reason": f"out of season outdoors in {_season}"})


# --- the face and the mood agree (1.5.0) --------------------------------------------
# `mood` is the picture's atmosphere and `expression` is the face in it; nothing tied
# them, and 5.4% of 4000 default renders contradicted themselves ("laughing" with a
# "somber" mood, "brooding" with a "lighthearted" one). The face is what a viewer reads
# first, so it stands and the mood adapts.
#
# Both fields are FIELD_FAMILIES fields, so every cull here drops a WHOLE mood family --
# `heavy` under a warm face, `positive` under a sad one -- and the surviving families
# stay exactly proportional (architecture.md -> the family weight rule). Taken from the
# family table by name so a regrouping cannot leave these pointing at dead strings.
_MOOD_HEAVY: list[str] = list(FIELD_FAMILIES["mood"]["heavy"]["variants"])
_MOOD_POSITIVE: list[str] = list(FIELD_FAMILIES["mood"]["positive"]["variants"])
_SAD_EXPRESSIONS: list[str] = ["melancholic", "solemn", "wistful", "brooding", "weary"]

for _expr in FIELD_FAMILIES["expression"]["warm"]["variants"]:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "expression", "value": _expr,
        "excludes_field": "mood", "excludes_values": list(_MOOD_HEAVY),
        "reason": f"a '{_expr}' face contradicts a heavy mood"})
for _expr in _SAD_EXPRESSIONS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "expression", "value": _expr,
        "excludes_field": "mood", "excludes_values": list(_MOOD_POSITIVE),
        "reason": f"a '{_expr}' face contradicts a buoyant mood"})


# --- outerwear (1.5.0) ----------------------------------------------------------------
# NO CONSTRAINT_RULES here, for the `legwear` reason: `outerwear` is a DEFERRED field
# (it gates on the finished garment), so a rule naming it would be inert. Both maps
# are consumed by `nodes.identity_forge._eligible_outerwear`, a pool filter.
#
# Which seasons each coat is worn in. Heavy coats are winter-only; mid-weight ones
# span the cold half; light jackets are the in-between seasons. Summer has none.
_HEAVY_COATS = frozenset(["wool overcoat", "parka", "puffer coat", "shearling coat",
                          "duffle coat", "faux fur coat"])
_MID_COATS = frozenset(["trench coat", "peacoat", "wrap coat", "leather jacket",
                        "quilted jacket", "waxed field jacket"])
_LIGHT_COATS = frozenset(["denim jacket", "bomber jacket", "rain jacket", "windbreaker"])
OUTERWEAR_SEASONS: dict[str, frozenset[str]] = {
    **dict.fromkeys(_HEAVY_COATS, frozenset(["winter"])),
    **dict.fromkeys(_MID_COATS, frozenset(["autumn", "winter", "spring"])),
    **dict.fromkeys(_LIGHT_COATS, frozenset(["autumn", "spring"])),
}

#: What each outfit_style plausibly throws on over the top. Allowlist, fail-safe like
#: FOOTWEAR_BY_STYLE: a coat not listed for a style is never drawn with it. An empty
#: set means the style never takes outerwear.
OUTERWEAR_BY_STYLE: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ("casual", frozenset([
        "denim jacket", "bomber jacket", "rain jacket", "quilted jacket", "parka",
        "puffer coat", "leather jacket", "waxed field jacket", "peacoat", "trench coat",
        "shearling coat", "duffle coat", "windbreaker"])),
    ("smart casual", frozenset([
        "trench coat", "wool overcoat", "peacoat", "leather jacket", "quilted jacket",
        "wrap coat", "shearling coat", "duffle coat"])),
    ("business casual", frozenset([
        "trench coat", "wool overcoat", "peacoat", "wrap coat", "quilted jacket",
        "rain jacket"])),
    ("business formal", frozenset(["wool overcoat", "trench coat", "peacoat", "wrap coat"])),
    ("evening formal", frozenset(["wool overcoat", "faux fur coat", "wrap coat"])),
    ("cocktail semi-formal", frozenset([
        "wool overcoat", "faux fur coat", "wrap coat", "trench coat", "leather jacket"])),
    ("streetwear", frozenset([
        "puffer coat", "parka", "bomber jacket", "denim jacket", "windbreaker",
        "leather jacket", "shearling coat"])),
    ("bohemian", frozenset(["shearling coat", "denim jacket", "wrap coat", "leather jacket"])),
    ("athletic", frozenset(["windbreaker", "rain jacket", "puffer coat"])),
    ("resort vacation", frozenset(["denim jacket"])),
    ("edgy alternative", frozenset([
        "leather jacket", "parka", "bomber jacket", "trench coat", "denim jacket",
        "faux fur coat"])),
    ("preppy", frozenset([
        "waxed field jacket", "quilted jacket", "peacoat", "duffle coat", "trench coat",
        "wool overcoat", "rain jacket"])),
    ("vintage retro", frozenset([
        "trench coat", "peacoat", "leather jacket", "wool overcoat", "duffle coat",
        "faux fur coat", "denim jacket"])),
    ("loungewear", frozenset()),
    ("utility workwear", frozenset([
        "parka", "quilted jacket", "waxed field jacket", "rain jacket", "puffer coat"])),
])


# =====================================================================================
# 1.5.0 ROUND 2 -- found by the maintainer's test renders
# =====================================================================================

# --- a pattern belongs to a style -----------------------------------------------------
# Patterns applied to the whole generated outfit with no reference to its style: tie-dye
# on a notch-lapel suit, camouflage on a preppy cable-knit, an abstract print on a
# tuxedo. Allowlist per style (fail-safe like FOOTWEAR_BY_STYLE). `clothing_pattern` is
# FLAT with a `weights` map and no family, so a cull re-picks proportionally. Every row
# keeps `solid`, so no style can run out.
_PLAIN = frozenset(["solid", "subtle texture"])
PATTERN_BY_STYLE: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ("casual", _PLAIN | {"stripes", "plaid", "floral", "geometric", "denim", "polka dot",
                         "gingham", "paisley", "tie-dye", "camouflage", "animal print",
                         "abstract", "argyle", "houndstooth"}),
    ("smart casual", _PLAIN | {"stripes", "plaid", "floral", "geometric", "houndstooth",
                               "pinstripe", "gingham", "polka dot", "paisley", "argyle"}),
    ("business casual", _PLAIN | {"stripes", "plaid", "pinstripe", "houndstooth",
                                  "gingham", "geometric", "polka dot", "floral"}),
    ("business formal", _PLAIN | {"pinstripe", "houndstooth", "plaid", "stripes"}),
    ("evening formal", _PLAIN | {"floral"}),
    ("cocktail semi-formal", _PLAIN | {"floral", "geometric", "polka dot", "abstract",
                                       "animal print", "stripes"}),
    ("streetwear", _PLAIN | {"stripes", "plaid", "camouflage", "tie-dye", "geometric",
                             "abstract", "denim", "animal print"}),
    ("bohemian", _PLAIN | {"floral", "paisley", "tie-dye", "geometric", "abstract",
                           "stripes", "plaid"}),
    ("athletic", _PLAIN | {"stripes", "camouflage", "geometric"}),
    ("resort vacation", _PLAIN | {"floral", "stripes", "gingham", "geometric",
                                  "polka dot", "paisley", "abstract"}),
    ("edgy alternative", _PLAIN | {"plaid", "animal print", "camouflage", "stripes",
                                   "abstract", "geometric", "denim"}),
    ("preppy", _PLAIN | {"stripes", "plaid", "gingham", "argyle", "houndstooth",
                         "pinstripe", "polka dot", "floral"}),
    ("vintage retro", _PLAIN | {"polka dot", "gingham", "houndstooth", "plaid", "paisley",
                                "floral", "stripes", "argyle", "geometric", "denim"}),
    ("loungewear", _PLAIN | {"stripes", "plaid", "gingham", "polka dot", "floral"}),
    ("utility workwear", _PLAIN | {"plaid", "denim", "camouflage", "stripes"}),
])
for _style, _allowed in PATTERN_BY_STYLE.items():
    _banned = sorted(set(_ALL_PATTERNS) - _allowed)
    if _banned:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": "clothing_pattern", "excludes_values": _banned,
            "reason": f"these patterns do not belong on {_style} clothing"})

# --- outdoors is lit by the sky, not a studio rig ------------------------------------
# The whole `studio_shape` family (Rembrandt, butterfly, split, soft-box, spotlights)
# was legal at every outdoor place: "a city fountain plaza, under Rembrandt lighting",
# "tide pools, under a harsh angled spotlight". Whole-family exclusion outdoors, so the
# surviving families keep their proportions. Indoors a portrait setup stays legal.
_STUDIO_SHAPE_LIGHTS: list[str] = list(FIELD_FAMILIES["lighting"]["studio_shape"]["variants"])
for _loc in sorted(OUTDOOR_LOCATIONS):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "lighting", "excludes_values": list(_STUDIO_SHAPE_LIGHTS),
        "reason": f"'{_loc}' is outdoors: no studio lighting rig"})

# --- nobody sits on the floor of a public or formal place ---------------------------
# `seated_floor` is a whole POSE_FAMILIES sub-family (the 1.5.0 split), so dropping it
# keeps `seated` (chairs) and every other family proportional.
_FLOOR_POSES: list[str] = list(FIELD_FAMILIES["pose"]["seated_floor"]["variants"])
_FLOOR_FREE_FAMILIES = ("food_drink", "retail_services", "civic_institutional",
                        "work_industrial", "transit_travel")
_FLOOR_FREE_PLACES = frozenset([
    "bowling alley", "billiards hall", "casino floor with card tables", "movie theater lobby",
    "independent cinema auditorium", "arcade with glowing cabinets", "indoor ice rink",
    "roller skating rink", "karaoke room with song menus", "busy city crosswalk",
    "neon-lit city street", "rainy street with umbrellas", "bus stop shelter",
    "pedestrian shopping street", "open-air street food market",
    "construction site with scaffolding", "working harbor dock", "Times Square",
    "Shibuya Crossing", "the Brooklyn Bridge pedestrian walkway", "Trafalgar Square",
    "rooftop cocktail bar",
])
for _loc, _fam in _LOCATION_FAMILY.items():
    if _fam in _FLOOR_FREE_FAMILIES or _loc in _FLOOR_FREE_PLACES:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "pose", "excludes_values": list(_FLOOR_POSES),
            "reason": f"nobody kneels, crouches or sits on the floor at '{_loc}'"})

# --- grey hair comes with age -------------------------------------------------------
# The DRAW is age-aware (nodes.identity_forge._GREY_BY_AGE), so a random character never
# needs a re-pick. This rule is the other direction, for a LOCKED age-grey: it moves a
# random age to 35+ (`age` is flat, so the re-pick is uniform). Only the three colours
# that ARE age -- white and silver are also stylistic (dye, and a great many white- or
# silver-haired young fictional characters lock them), so they never age anyone up.
AGE_GREY_HAIR: list[str] = ["salt and pepper", "gray-streaked dark hair", "charcoal gray"]
_YOUNG: list[str] = [a for a in FIELD_DEFINITIONS["age"]["female_options"]
                     if a.isdigit() and int(a) < 35]
for _grey in AGE_GREY_HAIR:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_color", "value": _grey,
        "excludes_field": "age", "excludes_values": list(_YOUNG),
        "reason": f"{_grey} hair is not a natural colour under 35"})

# --- a comb over needs short hair ---------------------------------------------------
for _length in ("shoulder length", "slightly past shoulders", "mid back", "lower back",
                "long", "very long", "waist length", "hip length"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_length", "value": _length,
        "excludes_field": "hair_style", "excludes_values": ["comb over"],
        "reason": f"a comb over is a short cut, not {_length} hair"})

# --- a hat covers the hair accessory -----------------------------------------------
# "a wool beanie" over "a bandana tied over his hair" -- two things on one head.
for _hat in ("wide brim sun hat", "baseball cap", "beret", "woven hat", "flat cap",
             "bucket hat", "wool beanie", "earmuffs"):
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "accessories", "value": _hat,
        "requires_field": "hair_accessory", "requires_value": "no hair accessory",
        "reason": f"a {_hat} leaves no room for a hair accessory"})

# --- a LOCKED coat makes the random scene fit it -------------------------------------
# A random coat is already gated by `_eligible_outerwear`. A LOCKED one wins by the
# lock rule, but nothing adapted around it: a parka in a museum atrium, a wool overcoat
# "during summer", a windbreaker over slides. `outerwear` is deferred, so these rules
# only ever fire on a lock (a random coat is not drawn until after the loop) -- which
# is exactly the case they are for. The place goes outdoors (every built-in interior
# is a whole location family, so the re-pick is proportional), the season, shoes and
# style follow the coat, and `_resolve_outfit_description` drops garments that bring
# their own outer layer.
_OPEN_FOOTWEAR: list[str] = ["bare feet", "sandals", "espadrilles", "slides", "slippers",
                              "mules", "wedges", "boat shoes"]  # last three 1.5.0 round 4
_INTERIORS: list[str] = [_loc for _loc in _LOCATION_FAMILY if _loc not in OUTDOOR_LOCATIONS]
_BATHING_PLACES: tuple[str, ...] = ("steaming hot spring pool", "waterfall plunge pool",
                                    "poolside cabana")
for _coat, _seasons in OUTERWEAR_SEASONS.items():
    # A seasonal place whose season the coat can never share (a parka in the autumn
    # park) would leave `season` with no legal value at all, so it goes too. Only on a
    # locked coat, and a few variants of one family -- a small, lock-only cull.
    _off_season = [_loc for _loc, _allowed in SEASONS_BY_LOCATION.items()
                   if not (_allowed & _seasons)]
    _rules = [
        ("season", sorted(set(_SEASONS) - _seasons), "is not worn then"),
        # 1.5.0 round 5: a wool overcoat and oxfords at a steaming hot spring pool.
        ("location", list(_INTERIORS) + _off_season + list(_BATHING_PLACES),
         "is not worn there"),
        ("footwear", list(_OPEN_FOOTWEAR), "does not go with open shoes"),
        ("outfit_style", sorted(_s for _s, _c in OUTERWEAR_BY_STYLE.items()
                                if _coat not in _c), "is not worn with that style"),
    ]
    for _target, _values, _why in _rules:
        if _values:
            CONSTRAINT_RULES.append({
                "type": "exclusion", "field": "outerwear", "value": _coat,
                "excludes_field": _target, "excludes_values": _values,
                "reason": f"a {_coat} {_why}"})

# --- a high-top fade needs coily hair ------------------------------------------------
# It is built by standing tightly coiled hair straight up; on straight or wavy hair it
# does not exist. Partial cull of `barbered_crop`: the crew cut and textured crop that
# absorb it are the generic everyday crops, which is the right place for the weight.
for _texture in ("pin straight", "sleek straight", "silky and glossy", "slightly wavy",
                 "loosely wavy", "wavy", "beachy waves"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": ["high-top fade"],
        "reason": f"a high-top fade needs coily hair, not {_texture}"})

# --- one watch -----------------------------------------------------------------------
# A cuff or a leather wrap bracelet beside a watch rendered as "a watch on both wrists"
# in maintainer testing. Both fields are flat, so the cull is uniform.
for _watch in ("minimal analog", "chronograph", "smart watch", "vintage leather", "metal link"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "watch_type", "value": _watch,
        # 1.5.0 round 4: every bracelet, not two -- a chain or charm bracelet beside
        # the watch stacked on the same wrist in 5 of 47 flagged renders.
        "excludes_field": "bracelet",
        "excludes_values": [b for b in FIELD_DEFINITIONS["bracelet"]["female_options"]
                            if b != "none"],
        "reason": "a bracelet beside a watch stacks on one wrist"})

# --- a palette belongs to a style too -------------------------------------------------
# The loud palettes read as costume on tailored or uniform-like dress: an ombre tuxedo,
# a mixed-print suit, a bold-primary business suit, pastel workwear. `clothing_color`
# is FLAT with a `weights` map, so these small denials re-pick proportionally.
PALETTE_DENIED_BY_STYLE: dict[str, list[str]] = {
    "smart casual": ["gradient ombre", "mixed prints"],
    "business casual": ["gradient ombre", "mixed prints", "all white", "white and cream",
                        "all black", "black monochrome"],  # last four 1.5.0 round 5
    "business formal": ["gradient ombre", "mixed prints", "bold primary colors", "pastels",
                        "jewel tones",  # 1.5.0 round 4: "a ruby two-piece suit"
                        # 1.5.0 round 5: an all-white suit, shirt and tie read as costume
                        "all white", "white and cream", "all black", "black monochrome"],
    "evening formal": ["gradient ombre", "mixed prints"],
    "cocktail semi-formal": ["mixed prints"],
    "preppy": ["gradient ombre", "mixed prints"],
    "utility workwear": ["gradient ombre", "mixed prints", "bold primary colors", "pastels",
                         "all white", "white and cream"],  # last two 1.5.0 round 5
    "edgy alternative": ["pastels"],  # 1.5.0 round 4: "a mint utility harness"
}
for _style, _denied in PALETTE_DENIED_BY_STYLE.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "outfit_style", "value": _style,
        "excludes_field": "clothing_color", "excludes_values": list(_denied),
        "reason": f"that palette reads as costume on {_style} clothing"})


# --- casual headwear stays out of formal rooms; freckles on deep skin ----------------
for _loc in ("fine dining restaurant interior", "elegant hotel dining room",
             "dimly lit cocktail lounge", "courtroom", "grand cathedral interior",
             "small chapel interior", "art gallery opening night", "formal dining room with chandelier"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "accessories",
        "excludes_values": ["baseball cap", "bucket hat", "wool beanie"],
        "reason": f"a casual cap comes off at '{_loc}'"})
# Dense freckling is a fair-skin trait; on deep skin tones it drew speckled faces in
# maintainer testing. `freckles_density` is flat, so the cull is uniform.
for _tone in sorted(DEEP_SKIN_TONES):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "skin_tone", "value": _tone,
        "excludes_field": "freckles_density", "excludes_values": ["heavy", "all-over"],
        "reason": f"dense freckling does not read on {_tone} skin"})

# --- a place named for its sun is not lit by night -------------------------------------
# "a sunny city park, under blue hour twilight". Three night lights at the three places
# whose NAME asserts daylight; a small partial cull of `daylight` at three places only.
for _loc in ("sunny city park", "sunlit vineyard", "sunlit sunroom"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "lighting",
        "excludes_values": ["blue hour twilight", "pre-dawn darkness with ambient glow",
                            "moonlight with cool blue tones", "fog-diffused streetlamp glow"],
        "reason": f"'{_loc}' is named for its sunlight"})


# --- bare feet and slippers stay where people take their shoes off --------------------
# "barefoot, set in a subway car interior". Bare feet belong at home, by water, on soft
# nature ground and in the studios where people train or pose barefoot; slippers only
# indoors at home or in a room you sleep in. `footwear` is flat, so the cull re-picks
# uniformly among the style's surviving shoes.
_BAREFOOT_FAMILIES = ("domestic", "nature_outdoor", "nature_landmark", "studio")
_BAREFOOT_PLACES = frozenset([
    "yoga studio with wood floors", "dance studio with mirrors", "martial arts dojo",
    "photography studio with backdrop", "indoor swimming pool", "poolside cabana",
    "quiet suburban backyard", "rooftop garden", "sunny city park", "community garden allotment",
    "grand hotel suite", "budget motel room", "university dormitory room",
])
_SLIPPER_FAMILIES = ("domestic",)
_SLIPPER_PLACES = frozenset(["grand hotel suite", "budget motel room",
                             "university dormitory room", "hospital room"])
for _loc, _fam in _LOCATION_FAMILY.items():
    _no = []
    if not (_fam in _BAREFOOT_FAMILIES or _loc in _BAREFOOT_PLACES):
        _no.append("bare feet")
    if not (_fam in _SLIPPER_FAMILIES or _loc in _SLIPPER_PLACES):
        _no.append("slippers")
    if _no:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "footwear", "excludes_values": _no,
            "reason": f"nobody goes {'barefoot or ' if 'bare feet' in _no else ''}in slippers at '{_loc}'"})

# --- dress-up accessories belong to dress-up styles -----------------------------------
# A pocket square needs a jacket's breast pocket; an evening clutch needs an evening.
# QA renders put "a silk pocket square" on a mesh dress and "a beaded evening clutch"
# on a boho maxi at home. Both fields are flat (accessories carries only the eyewear
# weights), so the culls re-pick proportionally.
_TAILORED = {"smart casual", "business casual", "business formal", "evening formal",
             "cocktail semi-formal", "preppy", "vintage retro"}
_EVENING = {"evening formal", "cocktail semi-formal"}
_DRESSY_BAGS = {"smart casual", "business casual", "business formal", "evening formal",
                "cocktail semi-formal", "vintage retro"}
for _style in FIELD_DEFINITIONS["outfit_style"]["female_options"]:
    if _style not in _TAILORED:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": "accessories", "excludes_values": ["silk pocket square"],
            "reason": f"{_style} clothing has no breast pocket for a pocket square"})
    _bags = []
    if _style not in _EVENING:
        _bags += ["beaded evening clutch", "velvet evening bag"]
    if _style not in _DRESSY_BAGS:
        _bags += ["envelope clutch in black", "envelope clutch in gold", "envelope clutch in nude"]
    if _bags:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": "bag", "excludes_values": _bags,
            "reason": f"an evening or dress clutch does not go with {_style} clothing"})


# =====================================================================================
# 1.5.0 round 4 -- the maintainer's 47 flagged renders. Every block below answers a
# class of contradiction seen there; docs/architecture.md "Round 4" has the list.
# =====================================================================================

# --- extras belong to a style ---------------------------------------------------------
# "a bucket hat" with a sequined cocktail top, "a flower crown" with an evening gown at
# a casino, "a leather briefcase" with coveralls, "a leather backpack" with a suit, "a
# belt bag" with a crewneck over a collared shirt, "a silk neck scarf" with a boxy tee.
# One table per style, denials only: a value not listed stays legal, so a user-added
# style or value is never banned. Every target is flat (accessories/skin weights only),
# so each cull re-picks proportionally, and every field keeps its absent value.
_CASUAL_HATS = ["baseball cap", "bucket hat", "wool beanie"]
_SUN_HATS = ["wide brim sun hat", "woven hat"]
_SUNGLASSES = ["classic black sunglasses", "cat eye sunglasses", "round sunglasses",
               "aviator sunglasses"]
_COLD_WEAR = ["knit winter scarf", "earmuffs"]
_ALL_BAGS = [b for b in FIELD_DEFINITIONS["bag"]["female_options"] if b != "no bag"]
_TOP_HANDLE = ["structured top handle bag in black", "structured top handle bag in cream",
               "structured top handle bag in tan"]
_CLUTCHES = ["envelope clutch in black", "envelope clutch in gold", "envelope clutch in nude",
             "beaded evening clutch", "velvet evening bag", "small quilted chain bag"]
_BELT_BAGS = ["belt bag in black", "belt bag in tan"]
_MINI_BACKPACKS = ["mini backpack in black", "mini backpack in tan"]
_SADDLEBAGS = ["saddlebag in brown", "saddlebag in black", "saddlebag in cognac"]
_LEATHER_TOTES = ["leather tote in black", "leather tote in tan", "leather tote in cognac"]
_BEACH_BAGS = ["straw beach tote", "woven rattan bag"]
_STATEMENT_EARRINGS = ["chandelier earrings", "long drop earrings", "tassel earrings",
                       "clip-on pearl earrings"]
_EDGY_PIERCINGS = ["snake bites", "bridge piercing", "eyebrow piercing", "labret stud",
                   "stretched lobes", "medusa piercing", "industrial earring",
                   "double nostril piercing", "small septum ring"]
_WORK_RINGS = ["statement ring", "delicate gemstone", "midi ring", "stacked thin bands"]


def _only(allowed: list[str]) -> list[str]:
    return [b for b in _ALL_BAGS if b not in allowed]


EXTRAS_DENIED_BY_STYLE: dict[str, dict[str, list[str]]] = {
    "casual": {
        "accessories": ["long opera gloves"],
        "bag": ["leather briefcase in black"],
        "hair_accessory": ["jeweled hair comb"],
        "earrings": ["chandelier earrings", "clip-on pearl earrings"],
    },
    "smart casual": {
        "accessories": ["bucket hat", "wool beanie", "headphones worn around the neck",
                        "fingerless gloves", "long opera gloves", "western belt"],
        "bag": ["canvas duffel bag", *_BEACH_BAGS[:1], *_BELT_BAGS],
        "hair_accessory": ["bandana tied over hair", "flower crown", "jeweled hair comb"],
        "necklace": ["beaded necklace", "pendant on a leather cord"],
    },
    "business casual": {
        "accessories": [*_CASUAL_HATS, *_SUN_HATS, "flat cap", "headphones worn around the neck",
                        "fingerless gloves", "long opera gloves", "western belt"],
        "bag": ["canvas duffel bag", *_BEACH_BAGS, *_BELT_BAGS, *_MINI_BACKPACKS],
        "hair_accessory": ["bandana tied over hair", "flower crown", "jeweled hair comb",
                           "oversized hair bow"],
        "necklace": ["beaded necklace", "pendant on a leather cord", "velvet choker",
                     "collar necklace"],
        "bracelet": ["beaded bracelet"],
        "rings": ["thumb ring"],
        "earrings": ["tassel earrings", "mismatched earrings", "chandelier earrings"],
        "piercings": list(_EDGY_PIERCINGS),
    },
    "business formal": {
        "accessories": [*_CASUAL_HATS, *_SUN_HATS, "flat cap", "beret",
                        "headphones worn around the neck", "fingerless gloves",
                        "long opera gloves", "western belt", "statement belt", "suspenders",
                        "reading glasses pushed up on head"],
        "bag": ["canvas tote", "canvas messenger bag", "canvas duffel bag", "canvas backpack",
                "leather backpack in brown", *_MINI_BACKPACKS, *_BELT_BAGS, *_BEACH_BAGS],
        "hair_accessory": ["scrunchie", "bandana tied over hair", "flower crown",
                           "oversized hair bow", "jeweled hair comb", "thin headband",
                           "thin scarf tied in hair", "knotted headband"],
        "necklace": ["beaded necklace", "pendant on a leather cord", "layered pendant necklaces",
                     "choker", "velvet choker"],
        "bracelet": ["beaded bracelet", "leather wrap bracelet", "charm bracelet", "bangle stack"],
        "rings": ["thumb ring", "midi ring"],
        "earrings": ["large bold gold hoops", "tassel earrings", "mismatched earrings",
                     "chandelier earrings", "ear cuff"],
        "piercings": list(_EDGY_PIERCINGS),
    },
    "evening formal": {
        "accessories": [*_CASUAL_HATS, *_SUN_HATS, *_SUNGLASSES, *_COLD_WEAR, "flat cap",
                        "beret", "headphones worn around the neck", "fingerless gloves",
                        "western belt", "statement belt", "suspenders",
                        "reading glasses pushed up on head"],
        "bag": _only(_CLUTCHES),
        "hair_accessory": ["scrunchie", "claw clip", "bandana tied over hair", "knotted headband",
                           "flower crown", "thin headband", "thin scarf tied in hair",
                           "padded headband"],
        "necklace": ["beaded necklace", "pendant on a leather cord", "layered pendant necklaces"],
        "bracelet": ["charm bracelet"],
        "watch_type": ["chronograph"],
        "rings": ["thumb ring"],
        "earrings": ["mismatched earrings"],
        "piercings": list(_EDGY_PIERCINGS),
    },
    "cocktail semi-formal": {
        "accessories": [*_CASUAL_HATS, *_SUN_HATS, *_COLD_WEAR, "flat cap",
                        "headphones worn around the neck", "fingerless gloves", "western belt",
                        "suspenders", "reading glasses pushed up on head"],
        "bag": _only(_CLUTCHES + _TOP_HANDLE + ["small black leather crossbody",
                                                  "tan leather crossbody"]),
        "hair_accessory": ["scrunchie", "bandana tied over hair", "flower crown", "thin headband",
                           "claw clip"],
        "necklace": ["beaded necklace", "pendant on a leather cord"],
        "bracelet": ["beaded bracelet", "leather wrap bracelet"],
        "watch_type": ["smart watch"],
    },
    "streetwear": {
        "accessories": [*_SUN_HATS, "silk neck scarf", "lapel pin", "long opera gloves",
                        "belt cinching waist"],
        "bag": ["leather briefcase in black", *_TOP_HANDLE, *_BEACH_BAGS,
                "small quilted chain bag", "printed silk scarf tied as bag accent"],
        "hair_accessory": ["jeweled hair comb", "flower crown", "satin ribbon tied in hair"],
        "earrings": ["clip-on pearl earrings", "chandelier earrings"],
    },
    "bohemian": {
        "accessories": ["baseball cap", "bucket hat", "headphones worn around the neck",
                        "long opera gloves", "suspenders", "lapel pin"],
        "bag": ["leather briefcase in black", *_BELT_BAGS, *_TOP_HANDLE,
                "small quilted chain bag"],
        "watch_type": ["smart watch"],
    },
    "athletic": {
        "accessories": [*_SUN_HATS, "beret", "flat cap", "silk neck scarf",
                        "belt cinching waist", "western belt", "statement belt", "lapel pin",
                        "long opera gloves", "leather gloves", "suspenders",
                        "reading glasses pushed up on head", "cat eye sunglasses"],
        "hair_accessory": ["flower crown", "jeweled hair comb", "satin ribbon tied in hair",
                           "oversized hair bow", "hair bow", "decorative hair pins",
                           "silk headband", "thin scarf tied in hair", "padded headband"],
        "necklace": ["collar necklace", "velvet choker", "choker", "layered gold chains",
                     "layered pendant necklaces", "locket necklace"],
        "bracelet": ["tennis bracelet", "charm bracelet", "bangle stack", "cuff"],
        "rings": list(_WORK_RINGS),
        "earrings": [*_STATEMENT_EARRINGS, "large bold gold hoops", "pearl studs",
                     "threader earrings"],
    },
    "resort vacation": {
        "accessories": ["suspenders", "leather gloves", "fingerless gloves", "long opera gloves",
                        "wool beanie", "lapel pin", *_COLD_WEAR],
        "bag": ["leather briefcase in black", "leather backpack in brown"],
        "necklace": ["velvet choker", "collar necklace", "pearl strand"],
    },
    "edgy alternative": {
        "accessories": [*_SUN_HATS, "silk neck scarf"],
        "bag": ["leather briefcase in black", *_BEACH_BAGS, "structured top handle bag in cream",
                "structured top handle bag in tan", "printed silk scarf tied as bag accent"],
    },
    "preppy": {
        "accessories": ["bucket hat", "headphones worn around the neck", "fingerless gloves",
                        "long opera gloves", "western belt"],
        "bag": list(_BELT_BAGS),
        "hair_accessory": ["bandana tied over hair", "flower crown", "jeweled hair comb"],
        "necklace": ["beaded necklace", "pendant on a leather cord", "velvet choker"],
        "piercings": list(_EDGY_PIERCINGS),
    },
    "vintage retro": {
        "accessories": ["headphones worn around the neck"],
        "bag": ["canvas duffel bag"],
        "watch_type": ["smart watch"],
    },
    "loungewear": {
        "accessories": [*_CASUAL_HATS, *_SUN_HATS, *_SUNGLASSES, *_COLD_WEAR, "flat cap",
                        "beret", "silk neck scarf", "belt cinching waist", "western belt",
                        "statement belt", "lapel pin", "long opera gloves", "leather gloves",
                        "fingerless gloves", "suspenders"],
        "bag": _only(["canvas tote", *_BELT_BAGS, *_MINI_BACKPACKS, "canvas backpack"]),
        "hair_accessory": ["jeweled hair comb", "flower crown", "decorative hair pins",
                           "satin ribbon tied in hair", "oversized hair bow"],
        "necklace": ["statement necklace", "collar necklace", "pearl strand", "pearl necklace",
                     "diamond pendant", "layered gold chains", "layered pendant necklaces",
                     "velvet choker", "choker"],
        "bracelet": ["tennis bracelet", "bangle stack", "cuff"],
        "earrings": list(_STATEMENT_EARRINGS),
    },
    "utility workwear": {
        "accessories": ["long opera gloves"],
        "bag": ["leather briefcase in black", *_TOP_HANDLE, "small quilted chain bag",
                *_SADDLEBAGS, *_LEATHER_TOTES, *_BEACH_BAGS, *_MINI_BACKPACKS,
                "printed silk scarf tied as bag accent"],
        "hair_accessory": ["flower crown", "jeweled hair comb", "satin ribbon tied in hair",
                           "oversized hair bow", "hair bow", "decorative hair pins",
                           "silk headband"],
        "bracelet": ["tennis bracelet", "charm bracelet", "bangle stack"],
        "rings": list(_WORK_RINGS),
        "earrings": [*_STATEMENT_EARRINGS, "large bold gold hoops"],
    },
}
#: Body jewellery is style-bound too: a brooch on a sweatshirt, a waist chain over a
#: hoodie. (The garment itself is checked after the outfit is composed, in
#: nodes.identity_forge._fit_extras_to_garment; this is the style half.)
_OTHER_JEWELRY_STYLES: dict[str, frozenset[str]] = {
    "brooch": frozenset(["smart casual", "business casual", "business formal", "evening formal",
                         "cocktail semi-formal", "preppy", "vintage retro"]),
    "arm cuff": frozenset(["bohemian", "resort vacation", "edgy alternative", "evening formal",
                           "cocktail semi-formal", "streetwear", "casual"]),
    "body chain": frozenset(["resort vacation", "bohemian", "edgy alternative",
                             "cocktail semi-formal"]),
    "waist chain": frozenset(["resort vacation", "bohemian", "edgy alternative", "streetwear",
                              "casual", "cocktail semi-formal"]),
    "anklet": frozenset(["resort vacation", "bohemian", "casual", "streetwear", "loungewear",
                         "cocktail semi-formal"]),
}
for _style in _ALL_STYLES:
    _by_field = {f: list(v) for f, v in EXTRAS_DENIED_BY_STYLE.get(_style, {}).items()}
    _jewels = [j for j, _ok in _OTHER_JEWELRY_STYLES.items() if _style not in _ok]
    if _jewels:
        _by_field["other_jewelry"] = _jewels
    for _field, _values in _by_field.items():
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": _field, "excludes_values": _values,
            "reason": f"that {_field.replace('_', ' ')} does not go with {_style} clothing"})

# Opera gloves reach past the wrist: a watch or bracelet would sit on top of the glove.
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "accessories", "value": "long opera gloves",
    "excludes_field": "watch_type",
    "excludes_values": [w for w in FIELD_DEFINITIONS["watch_type"]["female_options"] if w != "none"],
    "reason": "a watch does not go over an opera glove"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "accessories", "value": "long opera gloves",
    "excludes_field": "bracelet",
    "excludes_values": [b for b in FIELD_DEFINITIONS["bracelet"]["female_options"] if b != "none"],
    "reason": "a bracelet does not go over an opera glove"})

# --- where you are decides what you carry and wear ------------------------------------
# "carrying a saddlebag" in a dining room at home, "a canvas messenger bag" with a robe in
# the backyard; gloves, a beanie, a bucket hat and sunglasses indoors. Studio sweeps keep
# them (a styled shoot), every other interior drops them.
_AT_HOME: list[str] = [_loc for _loc, _fam in _LOCATION_FAMILY.items()
                       if _fam == "domestic" and _loc != "mudroom entryway"] + [
    "grand hotel suite", "budget motel room", "university dormitory room", "hospital room"]
for _loc in _AT_HOME:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "bag", "excludes_values": list(_ALL_BAGS),
        "reason": f"nobody carries a bag around '{_loc}'"})
_OUTDOOR_WEAR: list[str] = ["leather gloves", "fingerless gloves", "wool beanie", "bucket hat",
                            *_SUNGLASSES]
for _loc, _fam in _LOCATION_FAMILY.items():
    if _loc not in OUTDOOR_LOCATIONS and _fam != "studio":
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "location", "value": _loc,
            "excludes_field": "accessories", "excludes_values": list(_OUTDOOR_WEAR),
            "reason": f"'{_loc}' is indoors: gloves, sun hats and sunglasses come off"})
# Rough ground: "in slides" on a rocky coastal cliff.
_RUGGED_PLACES: list[str] = [
    "rocky coastal cliff", "forest trail", "mountain overlook", "rolling desert dune",
    "snowy pine forest", "misty moor", "alpine meadow with wildflowers", "bamboo forest path",
    "tide pools at low tide", "golden savanna with acacia trees", "red rock desert arch",
    "slot canyon with striated walls", "geothermal geyser basin",
    "redwood grove with towering trunks", "alpine glacier lake", "coastal lighthouse bluff",
    "waterfall plunge pool", "moss-draped rainforest trail", "frozen lake surface",
    "sea cave mouth", "basalt column coastline", "high desert with joshua trees",
    "the Grand Canyon south rim", "a Zion canyon riverbank", "the red desert plain below Uluru",
    "the Table Mountain plateau", "the Cliffs of Moher", "the Mount Fuji foothills",
    "construction site with scaffolding",
]
_DRESS_SHOES: list[str] = ["heels", "kitten heels", "wedges", "mules", "slides", "ballet flats",
                           "flats", "mary janes", "platform boots", "oxfords", "derbies",
                           "loafers"]
for _loc in _RUGGED_PLACES:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "footwear", "excludes_values": list(_DRESS_SHOES),
        "reason": f"'{_loc}' is rough ground for dress shoes"})

# --- lamps and candles need a room ----------------------------------------------------
# "warm candlelight" on a tree-lined boulevard, "warm incandescent lamp glow" in a cherry
# blossom grove. Wild places lose the whole `artificial_open` family (bias-clean); urban
# outdoor places keep the lantern and string lights (markets, patios) and lose the two
# that need a table or a lampshade, except where a table exists.
_PATIO_PLACES = frozenset(["rooftop cocktail bar", "rooftop terrace overlooking the skyline",
                           "poolside cabana", "open-air street food market",
                           "quiet suburban backyard"])
_OPEN_LIGHTS: list[str] = list(FIELD_FAMILIES["lighting"]["artificial_open"]["variants"])
for _loc, _fam in _LOCATION_FAMILY.items():
    if _loc not in OUTDOOR_LOCATIONS or _loc in _PATIO_PLACES:
        continue
    _dark = (list(_OPEN_LIGHTS) if _fam in ("nature_outdoor", "nature_landmark")
             else ["warm candlelight", "warm incandescent lamp glow"])
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "lighting", "excludes_values": _dark,
        "reason": f"'{_loc}' has no lamp or candle to light it"})

# --- hair: length, texture, parting, highlights, accessories ---------------------------
# Whole families only (the hair_style family rule). Ear length and a chin-length bob
# cannot be gathered into a ponytail, bun, updo, long braid or pigtails; jaw length
# still makes a stubby ponytail or a small bun, but not a French twist or braids.
_FAM = FIELD_FAMILIES["hair_style"]
_GATHERED = [v for f in ("ponytail", "bun_small", "bun_gathered", "braid_long", "pigtails")
             for v in _FAM[f]["variants"]]
_LONG_BRAIDS_UPDOS = [v for f in ("bun_gathered", "braid_long", "pigtails")
                      for v in _FAM[f]["variants"]]
for _length, _styles in (("ear length", _GATHERED + list(_FAM["half-up"]["variants"])),
                         ("chin length bob", _GATHERED),
                         ("jaw length", _LONG_BRAIDS_UPDOS)):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_length", "value": _length,
        "excludes_field": "hair_style", "excludes_values": _styles,
        "reason": f"{_length} hair is too short to gather into that style"})
# Texture on a buzz: waves and curls need length to show.
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "hair_length", "value": "buzzed very short",
    "excludes_field": "hair_texture",
    "excludes_values": ["slightly wavy", "loosely wavy", "wavy", "beachy waves",
                        "loosely curled", "softly curled", "fine and wispy", "silky and glossy"],
    "reason": "a buzz cut is too short to show a wave or a loose curl"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "hair_length", "value": "very short",
    "excludes_field": "hair_texture", "excludes_values": ["beachy waves", "loosely wavy"],
    "reason": "very short hair is too short for loose waves"})
# An afro is volume from coils; fine, wispy hair cannot hold one. A high-top fade is
# stood up from tight coils (thick straight or loose curls cannot hold it).
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "hair_texture", "value": "fine and wispy",
    "excludes_field": "hair_style", "excludes_values": list(_TEXTURE_BOUND_STYLES),
    "reason": "fine, wispy hair cannot form an afro or twist-out"})
for _texture in ("thick and voluminous", "fine and wispy", "loosely curled", "softly curled"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": ["high-top fade"],
        "reason": f"a high-top fade needs tight coils, not {_texture} hair"})
# Parting. A comb over IS a side part; bangs hide the part or dictate it; the crops,
# cornrows, locs and twists have no parting to describe; very short hair has no room
# for a centre or zigzag part.
for _style in ("blunt bangs", "micro bangs", "textured crop", "high-top fade", "cornrows",
               "locs", "two-strand twists", "hair puff", "box braids"):
    CONSTRAINT_RULES.append({
        "type": "requirement", "field": "hair_style", "value": _style,
        "requires_field": "hair_part", "requires_value": "no part",
        "reason": f"a {_style} style shows no parting"})
for _style, _parts in (("comb over", ["center part", "zigzag part", "diagonal"]),
                       ("side-swept bangs", ["center part", "zigzag part", "diagonal"]),
                       ("curtain bangs", ["side part", "deep side part", "zigzag part", "diagonal"]),
                       ("wispy bangs", ["deep side part", "zigzag part", "diagonal"])):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_style", "value": _style,
        "excludes_field": "hair_part", "excludes_values": _parts,
        "reason": f"a {_style} dictates its own parting"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "hair_length", "value": "very short",
    "excludes_field": "hair_part", "excludes_values": ["center part", "zigzag part", "diagonal"],
    "reason": "very short hair has no room for a centre or zigzag part"})
# Highlights need length to show, and grey or white hair is not highlighted.
_HIGHLIGHTS = [h for h in FIELD_DEFINITIONS["hair_highlights"]["female_options"] if h != "none"]
for _length, _keep in (("buzzed very short", []),
                       ("very short", ["frosted tips", "chunky highlights"])):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_length", "value": _length,
        "excludes_field": "hair_highlights",
        "excludes_values": [h for h in _HIGHLIGHTS if h not in _keep],
        "reason": f"{_length} hair is too short to carry those highlights"})
for _grey in FIELD_FAMILIES["hair_color"]["gray_white"]["variants"]:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_color", "value": _grey,
        "excludes_field": "hair_highlights", "excludes_values": list(_HIGHLIGHTS),
        "reason": f"{_grey} hair is not highlighted"})
# A headband on a buzz cut sits on bare scalp.
_HAIR_ACCESSORIES = [a for g in ("female_options", "male_options")
                     for a in FIELD_DEFINITIONS["hair_accessory"][g] if a != "no hair accessory"]
for _length, _keep in (
        ("buzzed very short", ["bandana tied over hair"]),
        ("very short", ["bandana tied over hair", "small hair clip", "decorative hair pins",
                        "silk headband", "knotted headband"]),
        ("short pixie", [a for a in _HAIR_ACCESSORIES
                         if a not in ("scrunchie", "claw clip", "oversized hair bow",
                                      "satin ribbon tied in hair")])):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_length", "value": _length,
        "excludes_field": "hair_accessory",
        "excludes_values": sorted({a for a in _HAIR_ACCESSORIES if a not in _keep}),
        "reason": f"{_length} hair has nothing for that accessory to hold"})
# Wind does not blow indoors ("long windswept hair" in a home office).
for _loc in _INDOOR_LOCATIONS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "hair_style", "excludes_values": ["windswept"],
        "reason": f"'{_loc}' is indoors: no wind"})

# --- one body --------------------------------------------------------------------------
# "a plus size build ... a very fit physique ... a narrow waist", "a slim build ... very
# broad shoulders, a muscular chest", "an hourglass build ... a very small bust ... narrow
# hips". The build is the headline word, so it stands and the parts follow it. Every
# target is flat, so each cull is uniform.
_SLIM = ["very slim", "slim", "slender", "petite and slim"]
_HEAVY = ["chubby", "plump", "plus size"]
_ATHLETIC = ["athletic", "toned", "fit"]
_CURVED = ["softly curved", "curvy", "voluptuous", "full figured", "petite and curvy", "hourglass"]
_BODY_RULES: list[tuple[list[str], str, list[str]]] = [
    (_SLIM + ["lean"], "waist", ["slightly wide", "wide", "full"]),
    (_SLIM + ["lean"], "hips", ["wide", "full", "very full"]),
    (_SLIM + ["lean"], "neck_length", ["thick"]),
    (_SLIM, "shoulder_width", ["very broad"]),
    (_SLIM, "bust", ["broad", "muscular", "very large", "generously proportioned"]),
    (_SLIM, "fitness_level", ["muscular"]),
    (_HEAVY, "waist", ["very narrow", "narrow", "defined"]),
    (_HEAVY, "fitness_level", ["very fit", "athletic", "muscular"]),
    (_HEAVY, "bust", ["flat", "very small"]),
    (_HEAVY, "hips", ["narrow", "slightly narrow"]),
    (_HEAVY, "neck_length", ["slender", "elegant"]),
    (_ATHLETIC, "waist", ["wide", "full"]),
    (_CURVED, "hips", ["narrow", "slightly narrow"]),
    (["hourglass", "voluptuous"], "bust", ["very small", "small"]),
    (["hourglass"], "waist", ["average", "slightly wide", "wide", "full"]),
    (["stocky"], "shoulder_width", ["narrow", "slightly narrow", "sloped"]),
    (["stocky"], "neck_length", ["slender", "elegant", "long"]),
    (["stocky"], "waist", ["very narrow"]),
    (["stocky"], "height", ["statuesque"]),
]
for _types, _target, _values in _BODY_RULES:
    for _type in _types:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "body_type", "value": _type,
            "excludes_field": _target, "excludes_values": list(_values),
            "reason": f"a {_type} build contradicts that {_target.replace('_', ' ')}"})
for _fit, _target, _values in (("sedentary", "bust", ["muscular"]),
                               ("muscular", "bust", ["flat"]),
                               ("very fit", "waist", ["wide", "full"]),
                               ("muscular", "waist", ["full"])):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "fitness_level", "value": _fit,
        "excludes_field": _target, "excludes_values": _values,
        "reason": f"a {_fit} physique contradicts that {_target}"})

# --- makeup: the look, the day and the place --------------------------------------------
# "vintage 1950s pin-up makeup, colorful bold eyeshadow, graphic editorial liner",
# "fresh-faced dewy look ... medium contour, glitter highlight", full glam in a cubicle
# farm and an auto repair shop, heavy glam in a mosque, club makeup at 65 in workwear.
_MAKEUP_DETAIL: dict[str, dict[str, list[str]]] = {
    "vintage 1950s pin-up makeup": {
        "eye_makeup": ["colorful bold eyeshadow", "glittery", "smoky black", "smoky gray",
                       "deep navy", "floating liner look"],
        "eyeliner": ["graphic editorial liner", "smudged kohl", "tight-lined waterline",
                     "barely there", "thin subtle liner"],
        "lips_makeup": ["tinted lip balm", "nude lipstick", "glossy clear", "brown nude",
                        "dark brown", "MLBB lipstick", "ombre lip", "high shine gloss"],
        "highlight": ["glitter highlight", "strobing"],
    },
    "mod 1960s eye makeup": {
        "eyeliner": ["smudged kohl", "barely there", "thin subtle liner", "tight-lined waterline"],
        "lips_makeup": ["deep red", "plum", "dark brown", "berry"],
        "eye_makeup": ["smoky black", "glittery"],
    },
    "gothic dark makeup": {
        "lips_makeup": ["coral", "pink", "glossy clear", "tinted lip balm", "nude lipstick",
                        "MLBB lipstick"],
        "blush": ["coral blush", "peach blush", "soft pink blush", "rosy blush",
                  "bronzed sun-kissed", "warm terra cotta"],
        "eye_makeup": ["rosy mauve", "warm earth tones", "copper and bronze", "warm bronze",
                       "colorful bold eyeshadow"],
        "skin_finish": ["sun-kissed glow"],
    },
}
for _look in ("soft everyday glam", "soft glam"):
    _MAKEUP_DETAIL[_look] = {
        "eyeliner": ["graphic editorial liner", "dramatic winged", "smudged kohl"],
        "eye_makeup": ["colorful bold eyeshadow", "smoky black", "smoky gray",
                       "floating liner look"],
        # (lash extensions stay: an everyday look, and banning them left a LOCKED
        # lash-extension face with no legal makeup style under workwear.)
        "lashes": ["dramatic falsies"],
        "contour": ["heavy"],
        "blush": ["heavy editorial blush"],
    }
for _look in _NATURAL_MAKEUP:
    _MAKEUP_DETAIL[_look] = {
        "eye_makeup": ["floating liner look"],
        "contour": ["heavy", "medium"],
        "highlight": ["glitter highlight", "strobing"],
        "blush": ["heavy editorial blush", "monochromatic blush and eyeshadow"],
        "lips_makeup": ["deep red", "plum", "dark brown", "ombre lip"],
        "eyebrow_makeup": ["bold sculpted"],
    }
for _look, _by_field in _MAKEUP_DETAIL.items():
    for _field, _values in _by_field.items():
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "makeup_style", "value": _look,
            "excludes_field": _field, "excludes_values": list(_values),
            "reason": f"'{_look}' does not wear that {_field.replace('_', ' ')}"})
_STAGE_MAKEUP = ["full glam", "bold glam", "heavy glam", "editorial makeup", "gothic dark makeup",
                 "club makeup", "vintage 1950s pin-up makeup", "mod 1960s eye makeup"]
for _style, _looks in (
        ("utility workwear", _STAGE_MAKEUP), ("loungewear", _STAGE_MAKEUP),
        ("athletic", _STAGE_MAKEUP),
        ("business casual", ["full glam", "bold glam", "heavy glam", "editorial makeup",
                             "gothic dark makeup", "club makeup"]),
        ("business formal", ["full glam", "bold glam", "heavy glam", "editorial makeup",
                             "gothic dark makeup", "club makeup"]),
        ("preppy", ["editorial makeup", "gothic dark makeup", "club makeup"]),
        ("resort vacation", ["editorial makeup", "gothic dark makeup", "club makeup"])):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "outfit_style", "value": _style,
        "excludes_field": "makeup_style", "excludes_values": list(_looks),
        "reason": f"that makeup is a costume with {_style} clothing"})
_SOBER_PLACES = ["grand cathedral interior", "small chapel interior", "mosque interior",
                 "synagogue interior", "Buddhist temple hall", "Shinto shrine interior",
                 "factory floor", "warehouse interior", "woodworking workshop",
                 "commercial kitchen", "auto repair shop service bay",
                 "print shop with running presses", "machine shop with lathes",
                 "brewery tank room", "blacksmith forge with an anvil",
                 "fishing trawler wheelhouse", "glassblowing studio with a furnace",
                 "construction site with scaffolding", "home garage workshop",
                 "courtroom"]
for _loc in _SOBER_PLACES:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "location", "value": _loc,
        "excludes_field": "makeup_style", "excludes_values": list(_STAGE_MAKEUP),
        "reason": f"stage makeup is out of place at '{_loc}'"})

# --- the pose has to fit the frame -------------------------------------------------------
# "extreme close-up on face" + "stretching both arms overhead"; "selfie framing" +
# "striding forward with purpose"; "view from directly behind" with a described face.
_POSE = FIELD_FAMILIES["pose"]
_BODY_POSES = [v for f in ("standing", "standing_hands_bound", "seated_floor", "motion",
                           "gesture_two_hands", "gesture_pockets") for v in _POSE[f]["variants"]]
for _shot in ("extreme close-up on face", "close-up portrait"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "shot_type", "value": _shot,
        "excludes_field": "pose",
        "excludes_values": list(_BODY_POSES) + ["posing with a hand on one hip"],
        "reason": f"a {_shot} does not show a full-body pose"})
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "shot_type", "value": "selfie framing at arm's length",
    "excludes_field": "pose",
    "excludes_values": list(_POSE["motion"]["variants"]) + [
        "in a confident power pose", "standing with feet planted wide",
        "in a relaxed contrapposto stance", "standing tall with shoulders back",
        "standing with arms relaxed at the sides"],
    "reason": "a selfie is held at arm's length, not struck as a full-body pose"})
_LOOK_BACK = ["looking over one shoulder", "glancing back", "turning toward the viewer mid-stride"]
_ALL_POSES = [v for f in _POSE.values() for v in f["variants"]]
for _shot in ("view from directly behind", "from behind and slightly below, looking up toward subject",
              "from above and behind, looking down toward subject"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "shot_type", "value": _shot,
        "excludes_field": "pose", "excludes_values": [p for p in _ALL_POSES if p not in _LOOK_BACK],
        "reason": "seen from behind, the face only shows if the head turns back"})

# --- the face and the mood agree, family by family ------------------------------------------
# Round 2 gated warm faces off heavy moods and sad faces off positive ones; the flagged
# renders still paired "solemn" with "triumphant", "mischievous" with "sorrowful",
# "defiant" with "dreamy", "at ease" with "uncanny". A whole-family matrix (bias-clean).
_MOODS_DENIED_BY_EXPRESSION: dict[str, list[str]] = {
    "warm": ["heavy", "bold_fierce", "enigmatic"],
    "calm": ["heavy", "bold_fierce", "bold_bright", "enigmatic"],
    "intense": ["positive", "calm"],
    "playful": ["heavy"],
    "pensive": ["positive", "bold_fierce", "bold_bright"],
    "reactive": ["bold_fierce", "bold_bright", "calm"],
}
for _efam, _mfams in _MOODS_DENIED_BY_EXPRESSION.items():
    _moods = [m for f in _mfams for m in FIELD_FAMILIES["mood"][f]["variants"]]
    for _expr in FIELD_FAMILIES["expression"][_efam]["variants"]:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "expression", "value": _expr,
            "excludes_field": "mood", "excludes_values": list(_moods),
            "reason": f"a '{_expr}' face contradicts that mood"})

# --- age --------------------------------------------------------------------------------
# Laugh lines at 18, "porcelain smooth" skin at 70, a velvet choker and a bridge piercing
# at 65, an industrial earring at 70, club makeup at 65.
_AGE_VALUES = [a for a in FIELD_DEFINITIONS["age"]["female_options"] if a.isdigit()]
_AGE_RULES: list[tuple[int, int, str, list[str]]] = [
    (0, 29, "skin_details", ["laugh lines"]),
    (50, 999, "skin_details", ["porcelain smooth"]),
    (55, 999, "piercings", list(_EDGY_PIERCINGS)),
    (55, 999, "necklace", ["choker", "velvet choker"]),
    (55, 999, "makeup_style", ["club makeup", "editorial makeup", "mod 1960s eye makeup",
                               "gothic dark makeup"]),
    # Pigtails and space buns read as a child's style from 45 ("braided pigtails" at 60).
    (45, 999, "hair_style", list(FIELD_FAMILIES["hair_style"]["pigtails"]["variants"])
     + list(FIELD_FAMILIES["hair_style"]["knots"]["variants"])),
    (55, 999, "eye_makeup", ["glittery", "colorful bold eyeshadow"]),
    (55, 999, "highlight", ["glitter highlight"]),
]
for _lo, _hi, _field, _values in _AGE_RULES:
    for _age in _AGE_VALUES:
        if _lo <= int(_age) <= _hi:
            CONSTRAINT_RULES.append({
                "type": "exclusion", "field": "age", "value": _age,
                "excludes_field": _field, "excludes_values": list(_values),
                "reason": f"that {_field.replace('_', ' ')} reads wrong at {_age}"})

# --- dense freckling reads on fair skin only ----------------------------------------------
for _tone in ("medium olive", "olive", "warm tan", "tan", "golden tan", "bronze", "caramel"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "skin_tone", "value": _tone,
        "excludes_field": "freckles_density", "excludes_values": ["heavy", "all-over"],
        "reason": f"dense freckling does not read on {_tone} skin"})


# --- round 4, second pass (the 47 seeds re-read after the first pass) --------------------
# A bird's-eye or high-angle camera sees ground, not a horizon.
for _shot in ("steep overhead bird's-eye view", "high angle looking down",
              "from above and behind, looking down toward subject"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "shot_type", "value": _shot,
        "excludes_field": "composition", "excludes_values": list(_SKY_COMPOSITIONS),
        "reason": f"a {_shot} shows no horizon or sky"})
# Afro-textured styles need textured hair. Whole families: `texture` (afro, twist-out,
# hair puff, bantu knots) and `braid_short` (cornrows, locs, two-strand twists). Box
# braids leave the 11-variant braid_long family. "Loosely wavy two-strand twists" on a
# German man, "sleek straight hair puff", "loosely wavy box braids".
_AFRO_TEXTURE = list(FIELD_FAMILIES["hair_style"]["texture"]["variants"])
_AFRO_BRAIDS = list(FIELD_FAMILIES["hair_style"]["braid_short"]["variants"])
for _texture in ("pin straight", "sleek straight", "silky and glossy", "fine and wispy",
                 "slightly wavy", "loosely wavy", "wavy", "beachy waves"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": _AFRO_TEXTURE + _AFRO_BRAIDS,
        "reason": f"{_texture} hair does not hold an Afro-textured style"})
for _texture in ("loosely curled", "softly curled"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": list(_AFRO_TEXTURE),
        "reason": f"{_texture} hair is too loose for an afro, twist-out, puff or knots"})
# A blowout straightens: not on tight coils, and not on very short hair; "worn down" says
# (A partial loose_styled cull at very short would break the whole-family rule.)
for _texture in ("tightly curled", "coily", "kinky coily"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": ["freshly blown out"],
        "reason": f"a blowout is not {_texture} hair"})
# A pixie has nothing to put in a bun or pull half up (whole families).
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "hair_length", "value": "short pixie",
    "excludes_field": "hair_style",
    "excludes_values": list(FIELD_FAMILIES["hair_style"]["bun_small"]["variants"])
    + list(FIELD_FAMILIES["hair_style"]["half-up"]["variants"]),
    "reason": "a pixie cut is too short for a bun, a top knot or a half-up"})
# A zigzag part is a young styling choice.
for _age in _AGE_VALUES:
    if int(_age) >= 50:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "age", "value": _age,
            "excludes_field": "hair_part", "excludes_values": ["zigzag part"],
            "reason": f"a zigzag part reads young at {_age}"})
# A shy face is not a fierce, commanding or triumphant picture.
for _expr in ("slightly bashful", "coy", "quiet amusement"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "expression", "value": _expr,
        "excludes_field": "mood",
        "excludes_values": list(FIELD_FAMILIES["mood"]["bold_fierce"]["variants"]
                                + FIELD_FAMILIES["mood"]["bold_bright"]["variants"]),
        "reason": f"a '{_expr}' face contradicts a bold mood"})

# Playful styles read as costume with business or evening dress ("milkmaid braids" with a
# pinstripe suit). Whole `pigtails` and `knots` families, two braid variants.
_PLAYFUL_HAIR = (list(FIELD_FAMILIES["hair_style"]["pigtails"]["variants"])
                 + list(FIELD_FAMILIES["hair_style"]["knots"]["variants"])
                 + ["milkmaid braids", "bubble ponytail"])
for _style in ("business formal", "business casual", "evening formal", "cocktail semi-formal"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "outfit_style", "value": _style,
        "excludes_field": "hair_style", "excludes_values": list(_PLAYFUL_HAIR),
        "reason": f"a playful hairstyle reads as costume with {_style} dress"})


# --- round 5 (the maintainer's test of the round-4 branch) -----------------------------
# An ombre palette already states the colouring; "an ombre-gradient plaid top" is two
# claims at once (same shape as the mixed-prints rule above).
CONSTRAINT_RULES.append({
    "type": "exclusion", "field": "clothing_color", "value": "gradient ombre",
    "excludes_field": "clothing_pattern",
    "excludes_values": sorted(set(_ALL_PATTERNS) - {"solid", "subtle texture"}),
    "reason": "an ombre palette already states the colouring; a print contradicts it"})
# Sunglasses at night ("classic black sunglasses ... under moonlight").
_NIGHT_LIGHTS = ["blue hour twilight", "pre-dawn darkness with ambient glow",
                 "moonlight with cool blue tones", "fog-diffused streetlamp glow",
                 "reflection off wet pavement", "neon sign glow in multiple colors",
                 "single neon light from one side", "purple and teal neon wash",
                 "club strobe lighting", "colored gel lighting", "warm candlelight",
                 "warm string lights bokeh background", "warm lantern light",
                 "golden bokeh lights in background", "fire and flame warm flicker",
                 "flickering firelight from a hearth", "flickering television glow in a dark room"]
for _light in _NIGHT_LIGHTS:
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "lighting", "value": _light,
        "excludes_field": "accessories", "excludes_values": list(_SUNGLASSES),
        "reason": f"nobody wears sunglasses under {_light}"})
# Cornrows, locs and twists on loose curls read as the same miss as on waves.
for _texture in ("loosely curled", "softly curled"):
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "hair_texture", "value": _texture,
        "excludes_field": "hair_style", "excludes_values": list(_AFRO_BRAIDS),
        "reason": f"{_texture} hair does not hold cornrows, locs or twists"})
# An undercut reads young from 55 ("an undercut" on a 70-year-old).
for _age in _AGE_VALUES:
    if int(_age) >= 55:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "age", "value": _age,
            "excludes_field": "hair_style", "excludes_values": ["undercut", "mullet"],
            "reason": f"an undercut or a mullet reads young at {_age}"})
