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
        DEEP_SKIN_TONES, FIELD_DEFINITIONS, FIXTURE_LIGHTING,
        INDOOR_ONLY_LIGHTING, OUTDOOR_LOCATIONS, OUTDOOR_ONLY_LIGHTING,
        STUDIO_BACKDROPS, VOID_ALLOWED_LIGHTING,
    )
except ImportError:  # pragma: no cover -- standalone/test context
    from data.fields import (
        DEEP_SKIN_TONES, FIELD_DEFINITIONS, FIXTURE_LIGHTING,
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
                         "braided ponytail", "box braids", "bantu knots",
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
         "excludes_field": "hair_style", "excludes_values": ["shag"],
         "reason": f"{length} hair is too short to cut into a shag's layers"}
        for length in ("buzzed very short", "very short", "short pixie")
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
     "excludes_values": ["baseball cap", "woven hat", "wide brim sun hat"],
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
                         "baseball cap", "beret"],
     "reason": "playful accessories undercut a formal suit"},

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
                       "defiant", "solemn", "unimpressed"]
_SOFT_SMILE_EXPRESSIONS = ["subtle soft smile", "warm smile", "bright smile",
                           "gentle smile",
                           # 0.82.0: "quietly content" is a closed-lip smile;
                           # "delighted" reads open-mouthed but is safest as a
                           # broad smile rather than a full toothy grin.
                           "quietly content", "delighted"]
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
    ],
    "other_jewelry": ["anklet", "body chain", "waist chain"],
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
                 "knee-high boots", "mary janes"],  # mary janes 0.97.0
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
}
# Jewellery & nails are a wardrobe *presentation* choice, not anatomy: their trims
# are gated on the resolved presentation so a man with a Feminine/"Any" wardrobe can
# still draw feminine-coded pieces. The rest (hair, brows, lips, eye shape, bust) are
# structural/anatomical male defaults and always apply for a male character.
_PRESENTATION_GATED_FIELDS: frozenset[str] = frozenset({
    "nails", "earrings", "necklace", "other_jewelry", "rings", "bracelet",
    "footwear",   # 0.83.0 -- a wardrobe choice, not anatomy, so it gates like jewellery
    "bag",        # 0.97.0 -- likewise
})
for _field, _excluded in _MALE_EXCLUDED_VALUES.items():
    CONSTRAINT_RULES.append({
        "type": "exclusion", "field": "gender", "value": "Male",
        "excludes_field": _field, "excludes_values": _excluded,
        "presentation_gated": _field in _PRESENTATION_GATED_FIELDS,
        "reason": f"feminine-coded {_field} is not a male default"})

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
    ("casual", frozenset([
        'sneakers', 'loafers', 'boots', 'flats', 'sandals', 'ankle boots', 'mules',
        'chelsea boots', 'combat boots', 'ballet flats', 'high-top sneakers',
        'espadrilles', 'mary janes', 'cowboy boots'])),
    ("smart casual", frozenset([
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
    ("streetwear", frozenset([
        'sneakers', 'boots', 'ankle boots', 'combat boots', 'high-top sneakers',
        'chelsea boots', 'mules', 'cowboy boots'])),
    ("bohemian", frozenset([
        'sandals', 'boots', 'flats', 'ankle boots', 'wedges', 'mules', 'bare feet',
        'espadrilles', 'ballet flats', 'knee-high boots', 'cowboy boots'])),
    ("athletic", frozenset(['sneakers', 'high-top sneakers'])),
    ("resort vacation", frozenset([
        'sandals', 'flats', 'wedges', 'mules', 'bare feet', 'espadrilles',
        'sneakers', 'ballet flats'])),
    ("edgy alternative", frozenset([
        'boots', 'combat boots', 'ankle boots', 'chelsea boots', 'knee-high boots',
        'heels', 'sneakers', 'high-top sneakers', 'cowboy boots', 'mary janes'])),
    ("preppy", frozenset([
        'loafers', 'oxfords', 'sneakers', 'flats', 'ankle boots', 'chelsea boots',
        'ballet flats', 'derbies', 'espadrilles', 'kitten heels', 'mary janes'])),
    ("vintage retro", frozenset([
        'loafers', 'oxfords', 'heels', 'flats', 'ankle boots', 'wedges', 'mules',
        'derbies', 'kitten heels', 'ballet flats', 'chelsea boots', 'mary janes',
        'cowboy boots'])),
    ("loungewear", frozenset(['slippers', 'bare feet', 'flats', 'ballet flats'])),
])

for _style, _allowed in FOOTWEAR_BY_STYLE.items():
    _banned = sorted(set(_ALL_FOOTWEAR) - _allowed)
    if _banned:
        CONSTRAINT_RULES.append({
            "type": "exclusion", "field": "outfit_style", "value": _style,
            "excludes_field": "footwear", "excludes_values": _banned,
            "reason": f"these shoes do not belong with {_style} dress"})

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
