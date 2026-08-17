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
        FIELD_DEFINITIONS, FIELD_FAMILIES, FIELD_HELP, OUTFIT_DESCRIPTIONS,
        SKIN_TONE_BANDS, ETHNICITY_REGION, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS,
        HAIR_DEPENDENT_POSES, GARMENT_DEPENDENT_POSES, HAND_OCCUPIED_POSES,
        FURNITURE_DEPENDENT_POSES,
        PALETTE_ADJECTIVES, PATTERN_TAILS, WORN_ITEM_RES,
        SHOE_RE, COLOUR_WORD_RE, PATTERN_WORD_RE, LEADING_ARTICLE_RE,
    )
    from ..data.constraints import CONSTRAINT_RULES
except ImportError:  # pragma: no cover — standalone/test context
    from data.fields import (
        FIELD_DEFINITIONS, FIELD_FAMILIES, FIELD_HELP, OUTFIT_DESCRIPTIONS,
        SKIN_TONE_BANDS, ETHNICITY_REGION, OUTDOOR_LOCATIONS, STUDIO_BACKDROPS,
        HAIR_DEPENDENT_POSES, GARMENT_DEPENDENT_POSES, HAND_OCCUPIED_POSES,
        FURNITURE_DEPENDENT_POSES,
        PALETTE_ADJECTIVES, PATTERN_TAILS, WORN_ITEM_RES,
        SHOE_RE, COLOUR_WORD_RE, PATTERN_WORD_RE, LEADING_ARTICLE_RE,
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

#: Fields drawn AFTER the main randomization loop, because their pool depends on the
#: finished ``outfit_description`` -- and for a randomly generated character that
#: string does not exist yet while the loop is running. It is composed afterwards,
#: from ``outfit_style``, in :func:`generate_character`.
#:
#: This bit us for real: gating ``legwear`` and ``tattoo_placement`` inside the loop
#: read an empty outfit every time, so legwear never appeared at all (0 in 2,000) and
#: forearm tattoos rendered under blazers. The symptom looked like two bad regexes;
#: the cause was one ordering mistake. Note that :func:`_performable_poses` reads the
#: same key from inside the loop and therefore only ever sees a PRESET costume -- for
#: a randomly generated outfit its garment check is inert. That is pre-existing and
#: is left alone here, but it is the same trap.
#: ``tattoos`` is here for a different reason from the other two: it needs no outfit
#: at all, but drawing it inside the loop would consume RNG *before*
#: ``_resolve_outfit_description``, shifting the outfit -- and therefore the whole
#: character -- for every existing seed. Deferring all three puts every new draw
#: after the last pre-existing one, so an identical seed yields an identical
#: character plus the new clauses. Verified, not assumed: see the seed-stability
#: check in tests/test_engine.py.
_DEFERRED_FIELDS: frozenset[str] = frozenset({"tattoos", "legwear", "tattoo_placement"})

#: The one shot_type value that occupies a hand (holding the camera at arm's length),
#: same as a held prop. Read by _performable_poses so a selfie never draws a
#: both-hands pose.
_SELFIE_SHOT_TYPE: str = "selfie framing at arm's length"

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

#: Trailing "(...)" disambiguator on a roster key, e.g. "Blue Beetle (Ted Kord)".
_KEY_PARENTHETICAL_RE = re.compile(r"^(?P<base>.*?)\s*\((?P<paren>[^()]+)\)\s*$")


def _name_already_carries_franchise(name: str, franchise: str) -> bool:
    """True when appending ``(franchise)`` to ``name`` would stutter.

    The 0.77.0 rule ("a franchise-disambiguated key must not restate its franchise
    in the label") was enforced with an exact ``endswith("(<franchise>)")`` test,
    which only catches the case where the parenthetical *is* the franchise. Three
    shipped keys stuttered through that test for years -- "Ms. Marvel (Kamala Khan)
    (Marvel)", "Ms. Marvel (Sharon Ventura) (Marvel)" and "Duke Nukem (video game)
    (Duke Nukem)" -- and merging the Persona installments at 0.88.0 added a fourth,
    "Joker (Persona 5) (Persona)". Three shapes, one test:

    * the parenthetical IS the franchise -- "Jinx (League of Legends)";
    * either is a more specific form of the other -- "Mai (Avatar)" under
      "Avatar: The Last Airbender";
    * the base name already says it -- "Ms. Marvel", "Duke Nukem".

    The *narrower* direction of the second shape ("Joker (Persona 5)" under the
    series franchise "Persona") no longer occurs in the roster: 0.90.0 renamed that
    key to "Joker (Persona)" and added a ``validate_data.py`` rule forbidding a
    parenthetical that extends its franchise. The branch below still handles it, as
    defence in depth for data that has not been validated yet.

    Both the prefix test and the base-name test are word-bounded on purpose: a bare
    substring check would fire on any name that happened to contain a short
    franchise string, and a bare prefix check would let a one-letter parenthetical
    swallow a long franchise.

    **Scope, deliberately narrow.** Everything past the exact-match test applies only
    to keys that actually carry a "(...)" disambiguator -- which is what the 0.77.0
    rule is about. It does NOT touch an *eponymous* key whose franchise repeats it
    ("Shrek" under "Shrek", "Godzilla" under "Godzilla", "Sterling Archer" under
    "Archer"). Those render as "Shrek (Shrek)", which is redundant but has shipped
    that way for many releases, and broadening the rule to cover them would rewrite
    91 more entries' prose -- silently invalidating 91 published gallery images,
    since ``entry_hash`` hashes the entry dict and cannot see a prose-only change.
    That is a separate decision with a real re-render bill attached, not a
    side effect of this fix.

    Prose-only -- no RNG draw here, so no seed drift.
    """
    if name.endswith(f"({franchise})"):
        return True
    match = _KEY_PARENTHETICAL_RE.match(name)
    if not match:
        return False
    folded = franchise.casefold()
    paren = match.group("paren").casefold()
    # Whichever is shorter must be a whole-word prefix of the longer.
    short, long = sorted((paren, folded), key=len)
    if re.match(rf"{re.escape(short)}\b", long):
        return True
    base = match.group("base").casefold()
    return re.search(rf"\b{re.escape(folded)}\b", base) is not None

#: Reserved key carrying a cosplayer's ``covers_face`` flag (see below) through
#: the parsed-archetype dict, the same way the cosplay label travels.
_COVERS_FACE_KEY = "__covers_face__"

#: Reserved key carrying a masked character's HEAD description, kept out of the
#: costume string on purpose (0.90.0).
#:
#: It used to be comma-appended to the costume, so "a head wrapped entirely in
#: blood-soaked gauze bandages" arrived as the SIXTH item of a "He wears ..."
#: garment list -- and t2i models rendered the clothes and ignored the head. The
#: maintainer's render review caught it on six entries at once (Silent Hill Nurse,
#: The Ghoul, Figrin D'an, Ithorian, Larfleeze, Dexter Jettster), every one of them
#: reading as an ordinary person in a costume.
#:
#: Same failure and same remedy as the tattoo clause: a description that competes
#: with a long clothing list loses, so it gets its own sentence.
_MASK_KEY = "__mask__"

#: Reserved key carrying a cosplayer's ``covers_body`` flag through the parsed dict
#: (a full hard suit / armour / robot shell / exoskeleton — no skin for worn
#: jewellery to sit on).
_COVERS_BODY_KEY = "__covers_body__"

#: Reserved key carrying a cosplayer's ``covers_hair`` flag through the parsed dict
#: (a hood / cowl / helmet liner / replacing head-tails fully encloses the scalp,
#: but the face still shows — so hair is hidden while Face/Makeup stay).
_COVERS_HAIR_KEY = "__covers_hair__"

#: Reserved key carrying a cosplayer's ``size_scale`` tier ("giant" / "tiny")
#: through the parsed dict. The Cosplayer node already locks the entry's authored
#: ``scale_prose`` into the ``height`` slot, but that only states the scale in prose;
#: the engine needs the tier itself to keep the *scene* coherent with it (see
#: :func:`_scale_coherent_pool`). Travels exactly like the ``covers_*`` flags.
_SCALE_TIER_KEY = "__scale_tier__"

#: ``_meta`` keys that describe the *worn costume* rather than the document as a
#: whole, so a downstream node that supplies its own ``outfit_description`` makes
#: every one of them stale. Read by :func:`merge_preset_documents`, which is where
#: the "downstream wins" contract is enforced -- see its docstring for the leaks
#: this closes (Iron Man's faceplate rendering over a Hogwarts uniform, Godzilla's
#: scale on Hermione, a masked cosplayer suppressing an archetype's whole face).
_COSTUME_META_KEYS: tuple[str, ...] = (
    "covers_face", "covers_body", "covers_hair", "mask", "size_scale",
)

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
#:
#: **A WIDGET lock wins over this block; a preset lock does not (0.84.0).** Until
#: 0.84.0 the block dropped unconditionally, so on a masked character moving the
#: ``hair_color`` widget off ``Random`` did nothing, silently — the dead-widget failure
#: mode 0.83.0 closed for the wardrobe axis, and inconsistent with every other
#: suppression in this module (bald, full-shell skin, ``expression``), all of which
#: honour a lock.
#:
#: The fix keys off ``widget_locked``, **not** ``locked_clean``, and the distinction is
#: load-bearing rather than fussy. ``locked_clean`` merges three sources: the user's own
#: widget choices, a wired preset's authored ``signature`` / ``physique`` / ``eyes``
#: values, and the Cosplayer builder's injected ``"None"`` suppressions. Only the first
#: is a user decision. Measured on the shipped roster: **8 of 295** ``covers_face``
#: entries carry a ``signature`` pin in a concealed field (Princess Leia, The Atom,
#: Bo-Katan Kryze, Night Thrasher, Denji, Katana, Jane Foster Thor, Ermac) — and in every
#: one the mask is an *alternate* costume, so honouring the pin would render Leia's side
#: buns under the Boushh helmet. Honouring ``locked_clean`` here is therefore a
#: regression, not a fix; honouring ``widget_locked`` changes **no** shipped entry until
#: a user deliberately moves a widget.
_CONCEALED_FACE_GROUPS: frozenset[str] = frozenset({"Face", "Hair", "Makeup"})
#: Individual head-worn fields (outside the above groups) a full mask also hides.
_CONCEALED_FACE_FIELDS: frozenset[str] = frozenset({"earrings", "piercings"})

#: Fields a full mask hides that are dropped **only when not explicitly locked** (0.83.0).
#:
#: ``expression`` is the case this exists for. It lives in ``Setting & Shot``, not in
#: ``_CONCEALED_FACE_GROUPS``, so for every release a masked character has been rendering
#: "He wears a plush yordle suit. He is standing with arms crossed. **His expression is
#: steely.**" — a facial expression behind a moulded head. That was mechanical, never a
#: decision.
#:
#: **Why this is still a separate set from ``_CONCEALED_FACE_FIELDS``:** only the
#: membership differs now, not the semantics. Both blocks honour ``widget_locked`` as of
#: 0.84.0, but this one exists because ``expression`` lives in ``Setting & Shot`` — it is
#: not reachable by group, so it has to be named. Keeping it separate also keeps the
#: reason visible: these are fields a mask hides *incidentally*, not fields that describe
#: the head.
#:
#: 0.84.0 narrowed this from ``locked_clean`` to ``widget_locked`` so both blocks share
#: one rule — *the mask hides the face; only your own widget overrides it*. Verified a
#: no-op on shipped data: ``Harley Quinn`` is the only entry whose ``signature`` pins
#: ``expression`` and she is not ``covers_face``, and **no archetype sets
#: ``covers_face`` at all**. It is the future-proof half that matters — a masked entry
#: that pins an expression would otherwise reintroduce the exact bug this closed.
#:
#: ``mood`` deliberately stays: it describes the scene's atmosphere, not the face, and
#: reads fine over a mask. ``smile_type`` needs no entry — it is a Face field and the
#: group block already drops it.
_CONCEALED_FACE_SOFT_FIELDS: frozenset[str] = frozenset({"expression"})

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

#: Body/Demographics fields dropped when a character is BOTH fully masked
#: (``covers_face``) AND a full hard shell (``covers_body`` / ``_FULL_COVER_RE``):
#: the being is entirely encased, so a randomized human ``skin_tone`` would render as
#: a stray patch of bare skin under the armour/droid plating (Iron Man, 2-1B, 4-LOM).
#: ``covers_face`` already drops the other skin fields (complexion / skin_details /
#: freckles are Face group; skin_finish is Makeup); only ``skin_tone`` (Body) leaks.
#: ``ethnicity`` (Demographics) joins it as of 0.65.0: it describes the cosplayer under
#: the costume, which is a deliberate design elsewhere (see the Cosplayer node's
#: "Costume only" tooltip), but on an entirely-encased character (Iron Giant, Ultraman,
#: Salacious Crumb, 2-1B, ...) mentioning it only risks biasing the render toward a
#: visible human trait with nothing left to attach it to. An explicit user lock on
#: either field is respected, same as every other suppression in this module.
_CONCEALED_SHELL_SKIN_FIELDS: frozenset[str] = frozenset({"skin_tone", "ethnicity"})

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
    # 0.83.0 additions to the accessories pool. Keeping this in sync is mandatory --
    # the docstring above says so, and a missed entry means that hat can stack on a
    # hooded or helmeted outfit. ``AccessoryHatSyncTests`` now enforces it mechanically
    # rather than relying on someone reading the comment.
    "flat cap", "bucket hat", "wool beanie",
})

#: ``accessories`` values that cover the hands (0.83.0). ``_GLOVE_RE`` has always scanned
#: ``outfit_description``, but gloves became drawable from the ``accessories`` field in
#: 0.83.0, and a randomized glove there hides the fingers exactly the same way — so nails
#: and rings have to be dropped for it too, or polish renders on top of leather.
#: ``fingerless gloves`` is deliberately NOT here: it exposes the fingers, the same
#: carve-out ``_FINGERLESS_RE`` makes for costume text.
_GLOVE_ACCESSORY_VALUES: frozenset[str] = frozenset({
    "leather gloves", "long opera gloves",
})

#: Costume phrases that mean the whole body is encased in a hard shell — a robot /
#: droid / powered armour / full plate / exoskeleton / carapace — so there is no
#: bare skin for worn jewellery or nails to sit on. Detected on the resolved
#: outfit_description; when matched (or the ``covers_body`` flag is set) the engine
#: drops the Jewelry & Nails group so a random necklace/ring/polish can't render on
#: top of the shell. Kept conservative (terms that imply full hard coverage, never
#: a bare-chested gladiator's "breastplate" or a partial "cybernetic arm").
#: 0.78.0: every ``armor`` alternative accepts ``armour`` too. The pattern was
#: American-only while data/cosplayers.py carried 32 British-spelled values, so
#: those entries silently failed the full-shell test and drew necklaces and drop
#: earrings over plate armour. The data has been normalised to the majority
#: spelling (202 vs 32), but the regex stays spelling-agnostic because
#: user_options.json is free text and no validator can reach it.
_FULL_COVER_RE = re.compile(
    r"exoskeleton|carapace|\bdroid\b|\brobot\b|android|"
    r"power(?:ed)?[ -]armou?r|powered exosuit|\bexosuit\b|armou?red bodysuit|"
    r"plate armou?r|armou?r plating|beskar|mjolnir|bio-armou?r|"
    r"suit of .{0,40}?armou?r",
    re.IGNORECASE,
)

#: Random accessory "extras" dropped when a specific costume is provided
#: (``outfit_description`` locked by an archetype / cosplayer / a user-typed outfit).
#: A styled costume is a complete, intentional look; a random tote, a wristwatch, a
#: scrunchie or a pair of sunglasses bolted on top reads as anachronistic or just
#: noise (a designer bag on a samurai, a watch on a caped hero, a claw clip on a
#: knight). Explicit locks are respected -- a look that authored a signature scarf
#: (Parisian Chic), flower crown (Cottagecore) or hair comb (Regency) keeps it -- and
#: a plain no-costume run keeps them all (a random modern person may carry/wear them).
#: Jewellery/nails are NOT here: they sit on the body and are governed by the shell
#: rule (a full shell drops the whole Jewelry & Nails group), and a character may
#: coherently wear earrings or a ring over a costume.
#: ``legwear`` joins them at 0.90.0 for the doubling reason rather than the
#: anachronism one: an authored costume that already says "grey thigh-high stockings"
#: (Lucy) or "knee-high socks" (the school-uniform entries) would otherwise get a
#: second, contradicting pair randomized on top of it. Tattoos deliberately do NOT
#: join -- ink sits on the body under the costume, the same argument that keeps
#: jewellery out of this set.
_COSTUME_SUPPRESSED_EXTRAS: frozenset[str] = frozenset({
    "bag", "watch_type", "hair_accessory", "accessories", "legwear",
})

#: ``footwear`` values that need a whole replacement clause rather than the default
#: "in <value>" -- "in bare feet" is clumsy where "barefoot" is idiomatic, and it is an
#: adverb, so it takes no preposition at all. Keyed on the pool value so the option list
#: is untouched (removing a shipped combo value is a soft break).
_FOOTWEAR_CLAUSES: dict[str, str] = {"bare feet": "barefoot"}

#: Garments with neither pockets nor a collar -- swimwear, a leotard / bodysuit, a
#: gown, a toga. The three ``GARMENT_DEPENDENT_POSES`` ("hands in pockets", "touching
#: the collar", "adjusting one cuff") assume a shirt or jacket, so they are as
#: unperformable here as under
#: a full hard shell and get dropped the same way. Conservative: only garments that
#: clearly lack both (never a "suit"/"shirt"/"dress", which may have pockets).
_POCKETLESS_GARMENT_RE = re.compile(
    r"\b(?:swimsuit|swimwear|swim trunks|board shorts|trunks|bikini|monokini|"
    r"one-piece|speedo|wetsuit|leotard|unitard|bodysuit|catsuit|gown|toga|"
    r"loincloth|bedlah|tutu)s?\b",
    re.IGNORECASE,
)

#: Maximum constraint-propagation passes before giving up (cycle guard).
_MAX_CONSTRAINT_ITERATIONS: int = 12

#: The "Auto" sentinel for the manual-only ``size_scale`` control. It is not a tier
#: and is never selected by the randomizer -- ``Auto`` means "say nothing about
#: scale", which is why the field is bias-free by construction. Same contract as the
#: Creature node's ``integument_finish``: adding tiers cannot dilute anything,
#: because nothing is ever drawn from this pool.
_SIZE_SCALE_AUTO: str = "Auto"

#: Hand-authored scale phrases, one per tier, that REPLACE the ``height`` value.
#:
#: This reuses the proven Cosplayer ``size_scale`` / ``scale_prose`` machinery: the
#: phrase is locked into the ``height`` slot with override=True, so it renders in the
#: LEAD sentence ("a 34-year-old woman with a slim build, colossal and fifty feet
#: tall, and fair skin") rather than being prepended somewhere weaker. ``height``'s
#: two gender pools are identical, so ``_gender_permits`` short-circuits True and
#: passes the free text through -- the same route the body-paint skin anchor uses.
#:
#: Wording follows the doctrine established across 0.55.0/0.63.0 and must not be
#: "improved" casually:
#:   * CONCRETE MEASUREMENTS, never comparison objects. "beside a towering oak" or
#:     "the size of a mouse" makes t2i render the oak or the mouse.
#:   * Never "insect-sized" / "three apples high" for the same reason.
#:   * Giant tiers pair scale with mass ("hulking", "dwarfing"), because a plain
#:     "very tall" reads as a tall human rather than a change of scale.
_SIZE_SCALE_PHRASES: "OrderedDict[str, str]" = OrderedDict([
    ("tiny", "tiny and barely six inches tall"),
    ("miniature", "miniature and barely two feet tall"),
    ("short", "notably short and slight of frame"),
    ("large", "powerfully built and well over seven feet tall"),
    ("towering", "towering and hulking, easily twelve feet tall"),
    ("colossal", "colossal and fifty feet tall, dwarfing the scene"),
])

#: Tiers that change the subject's *scale* rather than merely their stature, keyed
#: by both vocabularies that reach this code: the widget's tier names above and the
#: Cosplayer entry's ``size_scale`` ("giant"/"tiny").
#:
#: ``short`` and ``large`` are deliberately in NEITHER set. "well over seven feet
#: tall" is a very tall *person*; the scene around them still works, so narrowing
#: their framing or location would cost variety for nothing.
_GIANT_TIERS: frozenset[str] = frozenset({"giant", "towering", "colossal"})
_TINY_TIERS: frozenset[str] = frozenset({"tiny", "miniature"})

#: Framings that can actually carry a change of scale. A subject is only legible as
#: fifty feet tall when the frame holds enough of the world to compare them against,
#: or looks up at them from ground level. Everything else in ``shot_type`` -- every
#: portrait, every medium shot, every profile -- crops the reference away and renders
#: an ordinary person, no matter how emphatic the scale phrase in the prose is.
#:
#: Measured before this existed: 71 giant entries x 30 seeds drew a framing from this
#: set 26.2% of the time and an outdoor location 25.9% of the time, so a giant render
#: that could read as giant was roughly a 1-in-14 event.
#:
#: BIAS: ``shot_type`` is not in FIELD_FAMILIES and carries no ``weights`` map, so the
#: pick is flat uniform and narrowing the pool cannot redistribute anything. Same
#: property the 0.63.0 camera-only rework relied on.
_SCALE_SHOWING_SHOTS: frozenset[str] = frozenset({
    "full body shot with environment visible",
    "wide shot with subject at center",
    "wide shot with subject off-center",
    "extreme wide establishing shot",
    "low angle looking up",
    "worm's-eye view from ground",
})

#: The mirror problem at the other end: a six-inch subject in an establishing shot is
#: a few pixels. Only the framings that cannot resolve them at all are dropped -- a
#: tiny subject still reads fine in a close-up or a medium shot, so the tiny tiers get
#: a far lighter touch than the giant ones (and no location rule at all; a doll-sized
#: person indoors beside ordinary furniture is *better* scale evidence, not worse).
_SHOTS_TOO_WIDE_FOR_TINY: frozenset[str] = frozenset({
    "extreme wide establishing shot",
    "wide shot with subject off-center",
})

#: The only two ``body_type`` values that state *stature* rather than *shape*. They
#: land in the lead sentence two words from the scale phrase -- "a petite and curvy
#: build, colossal and hundreds of feet tall" -- and a flat contradiction beside a
#: high-attention token is exactly the failure the 0.78.0 Krusty fix documented.
#:
#: Deliberately narrow: "very slim" / "slender" / "lean" describe build, not size, and
#: a slender fifty-foot figure is perfectly coherent. Culling those would trade a real
#: contradiction for lost variety. ``body_type`` is flat (no families, no weights), so
#: removing two of nineteen values is bias-free.
_STATURE_BODY_TYPES: frozenset[str] = frozenset({"petite and slim", "petite and curvy"})

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
#:
#: **The probability is a FLOOR, not the realized rate.** :func:`_maybe_absent` rolls
#: first, and when it declines the field still draws from a pool that *contains* the
#: absent value, so it can come up absent a second way. The realized rate is therefore
#: ``base + (1 - base) / len(pool)``, plus whatever the constraint engine's masculine
#: trims add on top: measured over 6,000 runs, ``other_jewelry`` 0.50 -> 0.63,
#: ``hair_highlights`` 0.45 -> 0.59, ``watch_type`` 0.60 -> 0.66. That is the intended
#: shape (these are floors below which an extra never falls) and the shipped rates are
#: the ones the roster was curated against, so the numbers are not being "corrected" --
#: but the table used to read as if the base *were* the outcome, which it never was.
#: ``ExtraAbsenceFloorTests`` pins the relationship so it stays true as pools grow.
_EXTRA_ABSENCE: dict[str, tuple[str, float]] = {
    # 0.90.0. Leans further absent than anything else here: tattoos should read as
    # a distinguishing feature on a minority of characters, not as a house style.
    # Routing rarity through this table rather than a `weights` map is deliberate --
    # it makes the accessory_density control govern tattoos for free ("None" strips
    # them, "Maximal" makes them common), which a weights map would not.
    # tattoo_placement is NOT listed: it is cascaded off `tattoos` by
    # _visible_tattoo_placements, so giving it an independent absence roll would
    # only desynchronise the pair.
    "tattoos": ("no tattoos", 0.85),
    # Whole-pool suppressed by _wearable_legwear whenever the outfit covers the leg,
    # so this probability only governs the bare-leg case.
    "legwear": ("no visible legwear", 0.55),
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


#: The article is chosen by the *sound* a word starts with, not its spelling, so a
#: bare vowel-letter test gets two classes wrong. Words opening on a "yoo" glide
#: ("university lecture hall", "uniform", "eucalyptus", "one-shoulder") take "a"
#: despite the vowel letter; words with a silent h ("hourglass", "honest") take
#: "an" despite the consonant. Both classes are live in the shipped pools --
#: ``body_type`` has "hourglass" and ``location`` has two "university …" values --
#: and free-text ``skin`` / ``eyes`` / ``scale_prose`` overrides route through here
#: too, so the exceptions are matched on the leading word rather than listed value
#: by value.
_CONSONANT_VOWEL_PREFIXES: tuple[str, ...] = (
    "uni", "use", "usu", "usa", "uti", "ubi", "eu", "ewe", "one", "once",
)
_VOWEL_CONSONANT_PREFIXES: tuple[str, ...] = ("hour", "honest", "honor", "heir")


def _a(word: str) -> str:
    """Return the indefinite article ("a"/"an") that fits ``word``.

    Vowel-letter test plus the two sound-based exception classes above, so
    "an hourglass build" and "a university lecture hall" both read correctly.
    """
    first = word.split(" ", 1)[0].lower() if word else ""
    if first.startswith(_VOWEL_CONSONANT_PREFIXES):
        return "an"
    if first.startswith(_CONSONANT_VOWEL_PREFIXES):
        return "a"
    # Numerals are read aloud, so the article follows the SPOKEN first sound, not
    # the digit: "an 18-year-old", "an 8-foot drop", "an 80s revival". Only a
    # leading 8 (eight / eighty / eight hundred) and the exact teens 11 and 18
    # (eleven / eighteen) take "an" -- 110 is "one hundred ten" and takes "a", so
    # this is deliberately not a blanket "starts with 1 or 8" test.
    leading_digits = re.match(r"\d+", first)
    if leading_digits:
        digits = leading_digits.group()
        return "an" if digits.startswith("8") or digits in ("11", "18") else "a"
    # `first[:1] in "aeiou"` is True for the EMPTY string (every string contains
    # ""), so an empty input returned "an". Guarded explicitly.
    return "an" if first[:1] and first[0] in "aeiou" else "a"


def _an(value: str, noun: str = "") -> str:
    """Render ``value`` (optionally with a trailing ``noun``) with its article."""
    tail = f" {noun}" if noun else ""
    return f"{_a(value)} {value}{tail}"


#: Locations voiced with NO article at all. A bare proper name reads wrong with
#: one ("set in a Trafalgar Square"), and unlike the self-articled landmarks it
#: cannot be detected from the string -- "Buddhist temple hall" and "French bistro
#: with mirrored walls" are also capitalised and DO want "a". Kept as an explicit
#: list because the distinction is semantic, not orthographic.
#: Locations that are bare proper nouns: they take NO article and supply none of their
#: own, so ``_location_clause`` must leave them alone ("set in Times Square").
#:
#: This has to be a hand-maintained list and cannot be derived. Four locations start with
#: a capital and they split two ways that no mechanical rule tells apart: these are
#: proper-noun PLACES, while `French bistro with mirrored walls`, `Buddhist temple hall`
#: and `Shinto shrine interior` open with a capitalised *adjective* and still need "a".
#: ``LocationArticleTests`` therefore asserts every capital-initial location is declared
#: in one bucket or the other, so a new one fails the suite until it is classified —
#: deliberate friction, the same device as ``PoseGrammarTests``' opener allowlist.
_NO_ARTICLE_LOCATIONS: frozenset[str] = frozenset([
    'Trafalgar Square', 'Times Square', 'Shibuya Crossing',
])


def _location_clause(value: str) -> str:
    """Render ``value`` for the "set in ..." slot, with the right article or none.

    The slot used to be a blind ``f"set in {_a(v)} {v}"``, which was correct for
    every common-noun location but broke on the named landmarks added later --
    they carry their own leading article, so the prompt shipped "set in **a the**
    Brooklyn Bridge pedestrian walkway", "set in **an a** Yosemite valley meadow"
    and "set in **a** Trafalgar Square".

    Same class of wart as the 0.72.0 ``outfit_description`` article sweep and
    ``_article_if_singular``: the slot's sentence frame is part of the field's
    contract. Fixed in the engine rather than by rewording the data, because
    "the Grand Canyon south rim" is the *correct* way to name that place and
    ``user_options.json`` is free text no validator can reach.

    A second, older breakage shares the slot: the pool mixes singular and plural
    heads ("neighborhood pharmacy" beside "cracked salt flats", "tide pools at low
    tide", "terraced rice paddies"), so the blind article also shipped "set in a
    cracked salt flats". ``_article_if_singular`` already solves exactly this for
    the worn-item pools, head-noun split and all -- reused here rather than
    reimplemented, so "a public library with tall bookshelves" still articles on
    ``library`` and not on the trailing ``bookshelves``.

    Prose-only: no pool change, no RNG draw, no seed drift.
    """
    if value in _NO_ARTICLE_LOCATIONS:
        return value
    if value.split(" ", 1)[0].lower() in ("a", "an", "the"):
        return value  # the value supplies its own article
    return _article_if_singular(value)


def _prepend_descriptor(phrase: str, descriptor: str) -> str:
    """Prepend ``descriptor`` to ``phrase``, relocating the article ("a"/"an").

    "a segmented exoskeleton" + "emerald" -> "an emerald segmented exoskeleton".
    A phrase without a leading article (a plural / mass noun) just gets the
    descriptor in front: "compound eyes" + "glowing" -> "glowing compound eyes".

    Lives here (rather than in the creature node, where it started) because the
    Modifier path needs exactly the same fix: costume prose starts with an article
    by convention -- 1107 of the shipped cosplayer costumes do -- so a blind
    prepend rendered "wears weathered a gothic black dress". The creature node
    imports it from here.
    """
    if not descriptor or not phrase:
        return phrase
    for article in ("a ", "an ", "A ", "An "):
        if phrase.startswith(article):
            return f"{_a(descriptor)} {descriptor} {phrase[len(article):]}"
    return f"{descriptor} {phrase}"


#: Splits a worn-item phrase at the preposition / participle that starts a
#: post-modifier, so the *head* noun can be inspected: "reading glasses pushed up
#: on head" heads on "reading glasses" (plural), not on the trailing "head", and
#: "belt cinching waist" heads on "belt" (singular), not on "waist". Without this
#: the naive last-word test gets both backwards.
_ITEM_TAIL_RE = re.compile(
    r"\s+(?:on|in|over|at|with|as|under|across|tied|worn|pushed|cinching|"
    r"bearing|falling|framing)\b"
)

#: A free-text ``eyes`` override (a cosplayer's non-standard eye description) may
#: already name the eye part it describes -- "green with vertical cat-slit pupils",
#: "red on black sclera", "warm brown behind thick round goggle lenses". The prose
#: normally appends " eyes" to the colour, which turns those into "...pupils eyes".
#: When the value already ends in an eye part, the noun is dropped. Mirrors the
#: material-noun guard the skin_tone anchor uses ("dark blue scaled-skin").
_EYE_PART_RE = re.compile(r"\b(?:eyes?|pupils?|irises|iris|sclerae?|lenses|lens)$",
                          re.IGNORECASE)


def _article_if_singular(value: str) -> str:
    """Return ``value`` with an indefinite article when its head noun is singular.

    The worn-item pools mix singular and plural entries in the same slot — "brooch",
    "thumb ring" and "canvas tote" sit beside "pearl studs", "layered gold chains"
    and "classic black sunglasses". The prose voices them in one list, so a blanket
    article would give "a pearl studs" and no article gives "He has brooch, thumb
    ring, nose stud" (while the neighbouring watch, which does use ``_an``, reads
    correctly). Articling only the singular heads makes the whole list agree.

    Plural is detected on the head noun's final ``s`` (ignoring ``ss``, so "dress"
    and "sunglasses" are handled correctly by the head split above).
    """
    if not value:
        return value
    head = _ITEM_TAIL_RE.split(value, 1)[0]
    last = head.split()[-1].lower() if head.split() else ""
    if last.endswith("s") and not last.endswith("ss"):
        return value
    return _an(value)


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
    both the initial random fill and (via ``_repick``) the constraint engine's
    re-picks, so a down-weighted value stays rare even after an exclusion re-roll.
    """
    weights_map = field_def.get("weights")
    male_weights = field_def.get("male_weights") if gender == "Male" else None
    if weights_map or male_weights:
        combined = {**(weights_map or {}), **(male_weights or {})}
        weights = [combined.get(value, 1) for value in pool]
        return rng.choices(pool, weights=weights)[0]
    return rng.choice(pool)


def _repick(
    field_name: str, field_def: dict, pool: list[str], gender: str, rng: random.Random
) -> str:
    """Draw a replacement value for ``field_name`` from an already-filtered ``pool``.

    Routes to the same picker the initial fill would have used: the two-tier
    weighted pick for fields registered in :data:`FIELD_FAMILIES`, the draw-weight
    pick otherwise. Constraint re-picks went straight to ``_weighted_choice``
    before 0.64.0, which silently dropped family weighting on the way through --
    a re-rolled hair_style or lighting came out flat-uniform over the survivors
    instead of keeping each family's share. Both pickers intersect with ``pool``,
    so any exclusion the caller already applied still holds.
    """
    if field_name in FIELD_FAMILIES:
        return _pick_family_weighted(field_name, pool, rng)
    return _weighted_choice(field_def, pool, gender, rng)


def _performable_poses(
    pool: list[str],
    resolved: dict[str, str],
    covers_face: bool,
    covers_body: bool,
    covers_hair: bool,
) -> list[str]:
    """Drop poses that reach for something this character does not have.

    The ``pose`` field is written as a gesture a *person* performs, which quietly
    assumes a person's parts: "running one hand through the hair" needs scalp hair,
    "posing with hands in pockets" and "touching the collar with one hand" need a
    worn garment *with pockets and a collar*. A fully masked / hooded / bald character
    has no hair to touch; a full hard shell or non-skin body (fur, plating, flame) has
    no pockets or collar (the Moogle-with-a-hairstyle-gesture bug); and a pocketless,
    collarless garment — swimwear, a leotard, a gown, a toga — has neither either, so
    the garment gestures are dropped for it the same way (hands-in-pockets on a bikini).

    A third assumption joined at 0.84.0: a pose that occupies **both hands** assumes the
    hands are empty. With the Cosplayer node's signature prop switched on, the prose
    rendered *"She is posing with hands in pockets, holding Mjolnir"* — measured at
    **14.37%** of prop-enabled renders, across 468 of 1,732 cosplayers that carry a
    ``prop``. One-handed poses are deliberately kept: the free hand holds the prop, which
    is the natural reading, so only :data:`HAND_OCCUPIED_POSES` goes.

    A fourth, 0.85.0: ``shot_type`` locked to the selfie framing assumes the same thing
    a held prop does — one hand is occupied holding the camera at arm's length, so
    :data:`HAND_OCCUPIED_POSES` drops for the same reason, reusing the existing set
    rather than hand-listing a selfie-specific subset.

    Reads ``hair_length``, ``outfit_description`` and ``held_item`` straight out of
    ``resolved`` rather than taking more parameters: ``pose`` is drawn after all three
    (field indices 24/46 vs 67, and ``held_item`` is a preset-only lock present from the
    first line of :func:`_randomize_fields`), so their final values — locked *or*
    randomized — are already in hand. That also means an auto-detected shell (a randomly
    drawn plate-armour outfit) is caught without the caller having to flag it.

    Both bald routes count: the engine's own "bald" ``hair_length``, and the
    Cosplayer node's ``_BALD_SUPPRESS``, which locks the scalp fields to an *absent*
    value instead (never to "bald" — that option is male-only and would be
    gender-gated). Absent hair means no hair is described at all, so a hair gesture
    is unsupported either way.

    Whole families are removed, never single values, so the remaining families keep
    their proportional shares (see POSE_FAMILIES). Returns ``pool`` unchanged when
    nothing applies, and never returns empty.
    """
    hair_length = resolved.get("hair_length")
    hair_hidden = (
        covers_face or covers_hair
        or hair_length == "bald" or _is_absent(hair_length)
    )
    outfit = resolved.get("outfit_description") or ""
    # A hard shell OR a pocketless/collarless garment (swimwear, leotard, gown, toga)
    # leaves nothing for the garment gestures to reach for.
    garmentless = (
        covers_body
        or bool(_FULL_COVER_RE.search(outfit))
        or bool(_POCKETLESS_GARMENT_RE.search(outfit))
    )
    held = resolved.get("held_item")
    excluded: set[str] = set()
    if hair_hidden:
        excluded |= HAIR_DEPENDENT_POSES
    if garmentless:
        excluded |= GARMENT_DEPENDENT_POSES
    if (held and not _is_absent(held)) or resolved.get("shot_type") == _SELFIE_SHOT_TYPE:
        excluded |= HAND_OCCUPIED_POSES
    if not excluded:
        return pool
    return [p for p in pool if p not in excluded] or pool


#: Garments that leave the leg bare or mostly bare, so legwear and leg tattoos can
#: actually be seen. Matched against the resolved ``outfit_description`` text, the
#: same technique ``_POCKETLESS_GARMENT_RE`` already uses to gate poses -- the engine
#: has no structured garment model, and inventing one for two fields would cost far
#: more than it returns. Conservative by construction: anything not matched here is
#: treated as covering the leg, so the failure mode is a missing option rather than
#: tights rendered under a pair of jeans.
_BARE_LEG_RE = re.compile(
    r"\b(?:skirt|skort|dress|gown|shorts|playsuit|romper|leotard|unitard|bodysuit|"
    r"swimsuit|swimwear|bikini|monokini|kaftan|caftan|sundress|tunic|toga|"
    r"pinafore|kilt|sarong)s?\b",
    re.IGNORECASE,
)

#: Sleeves that reach the wrist, hiding a forearm / wrist / hand tattoo. Same
#: conservative posture as ``_BARE_LEG_RE``, but inverted: here a MATCH removes
#: options, so over-matching costs variety while under-matching would print ink
#: onto a covered arm. Listed garments are ones that are long-sleeved by
#: definition; ambiguous words ("shirt", "top") are deliberately absent because
#: they are as often short-sleeved.
_LONG_SLEEVE_RE = re.compile(
    r"\b(?:blazer|suit|tuxedo|coat|jacket|cardigan|sweater|sweatshirt|hoodie|"
    r"jumper|turtleneck|roll-neck|pullover|anorak|windbreaker|parka|robe|"
    r"long sleeve|long-sleeve|long-sleeved|bell sleeves|wide sleeves|"
    # Added after a sample render put a forearm tattoo under "a quarter-zip base
    # layer": these are long-sleeved by definition and the first pass missed them.
    r"quarter-zip|half-zip|zip-up|zip-through|base layer|thermal|henley|"
    r"flannel|overshirt|fleece|crewneck|poncho|duster|trench|kaftan|caftan)s?\b",
    re.IGNORECASE,
)

#: Hems that reach past the thigh (and, for the longest, past the calf too), so a
#: leg tattoo under them is covered even though the garment technically "shows leg".
#: Split from ``_BARE_LEG_RE`` rather than folded into it because the two answer
#: different questions: a maxi skirt still takes tights (they are seen when it
#: moves), but it does hide a thigh tattoo completely.
_LONG_HEM_RE = re.compile(
    r"\b(?:maxi|floor-length|ankle-length|full-length|midi|long skirt|"
    r"broomstick|tiered maxi)\b",
    re.IGNORECASE,
)

#: Necklines that sit high enough to cover a collarbone tattoo.
_HIGH_NECK_RE = re.compile(
    r"\b(?:turtleneck|roll-neck|high-neck|high neck|mock neck|crewneck|"
    r"high collar|standing collar|halter)s?\b",
    re.IGNORECASE,
)

#: Legwear opaque enough to hide a thigh or calf tattoo underneath it.
_OPAQUE_LEGWEAR_RE = re.compile(r"\b(?:opaque|patterned|ribbed|over-the-knee)\b",
                                re.IGNORECASE)

#: Footwear that already covers the calf, so knee-high / over-the-knee legwear
#: would be layered invisibly underneath it.
_TALL_BOOT_RE = re.compile(r"\b(?:knee-high|thigh-high|over-the-knee)\b", re.IGNORECASE)


def _wearable_legwear(pool: list[str], resolved: dict[str, str]) -> list[str]:
    """Drop legwear the outfit would hide, or the footwear would swallow.

    Two independent gates:

    * **The outfit has to show leg at all.** Trousers, jeans and chinos hide tights
      completely, and naming a hidden garment in a t2i prompt does not add detail --
      it adds a contradiction the model has to resolve, usually by inventing a
      visible pair. When the leg is covered the whole pool goes, not part of it, so
      no share is concentrated on survivors (the partial-cull trap that
      ``FIELD_FAMILIES`` weights make dangerous elsewhere; ``legwear`` has no family
      entry, but whole-pool suppression is the honest shape regardless).
    * **Tall boots already cover the calf.** Knee-high socks under knee-high boots
      is not wrong so much as invisible, so those two values drop when the footwear
      reaches the knee.

    Returns ``[]`` when nothing is wearable; the caller's ``optional`` branch turns
    that into ``"None"``.
    """
    outfit = resolved.get("outfit_description") or ""
    if not _BARE_LEG_RE.search(outfit):
        return []
    footwear = resolved.get("footwear") or ""
    if _TALL_BOOT_RE.search(footwear):
        pool = [v for v in pool if not _TALL_BOOT_RE.search(v) and "knee" not in v.lower()]
    return pool


def _visible_tattoo_placements(pool: list[str], resolved: dict[str, str]) -> list[str]:
    """Drop tattoo placements the character's clothing would cover.

    A tattoo the viewer cannot see is worse than no tattoo: the phrase still steers
    the image, so "a floral tattoo down one thigh" on a character in jeans pushes the
    model toward showing a thigh. This is the concrete failure the field was gated
    for from the start, rather than a refinement bolted on afterwards.

    Cascades off ``tattoos`` first -- a placement with nothing to place is dropped
    entirely. ``tattoos`` is drawn earlier (it is appended above ``legwear`` and
    ``tattoo_placement`` in ``FIELD_DEFINITIONS``), so its value is already settled.

    Neck, behind-ear, upper-arm and shoulder-blade placements are never dropped, so
    the pool cannot empty while a tattoo exists. Flat field, no family weight, so
    culling re-picks uniformly among the survivors.
    """
    tattoo = resolved.get("tattoos")
    if not tattoo or _is_absent(tattoo):
        return []
    outfit = resolved.get("outfit_description") or ""
    legwear = resolved.get("legwear") or ""
    excluded: set[str] = set()
    if _LONG_SLEEVE_RE.search(outfit):
        excluded |= {"on one forearm", "across the back of one hand", "on the inner wrist"}
    # Three ways a leg tattoo ends up invisible: the garment covers the leg, the
    # garment shows leg but its hem still reaches past the thigh (a maxi skirt --
    # caught in a sample render), or opaque legwear covers what the hem does not.
    leg_bare = bool(_BARE_LEG_RE.search(outfit)) and not _LONG_HEM_RE.search(outfit)
    leg_covered_by_legwear = bool(legwear) and not _is_absent(legwear) and \
        bool(_OPAQUE_LEGWEAR_RE.search(legwear))
    if not leg_bare or leg_covered_by_legwear:
        excluded |= {"down one thigh", "on one calf"}
    if _HIGH_NECK_RE.search(outfit):
        excluded.add("across the collarbone")
    if not excluded:
        return pool
    return [p for p in pool if p not in excluded]


def _resolve_deferred_fields(
    resolved: dict[str, str], gender: str, accessory_density: str, rng: random.Random
) -> None:
    """Draw :data:`_DEFERRED_FIELDS` now that ``outfit_description`` is final.

    Mirrors the main loop's tail exactly -- same pool build, same
    :func:`_maybe_absent` density roll, same ``optional`` fallback -- so these two
    fields behave like every other field except for *when* they are drawn.

    Called after the outfit clause is composed, so it runs at the very end of the
    draw order. Nothing is drawn after it, which is why adding these fields cannot
    shift any pre-existing field's random values: an identical seed produces an
    identical character, plus or minus the new clauses.
    """
    for field_name in FIELD_DEFINITIONS:
        if field_name not in _DEFERRED_FIELDS or field_name in resolved:
            continue
        field_def = FIELD_DEFINITIONS[field_name]
        pool = _build_option_pool(field_name, field_def, gender, resolved)
        if field_name == "legwear":
            pool = _wearable_legwear(pool, resolved)
        elif field_name == "tattoo_placement":
            pool = _visible_tattoo_placements(pool, resolved)
        forced_absent = _maybe_absent(field_name, pool, accessory_density, rng)
        if forced_absent is not None:
            resolved[field_name] = forced_absent
        elif pool:
            resolved[field_name] = _weighted_choice(field_def, pool, gender, rng)
        elif field_def["optional"]:
            resolved[field_name] = "None"


def _repair_pose(
    resolved: dict[str, str],
    gender: str,
    locked: set[str],
    covers_face: bool,
    covers_body: bool,
    covers_hair: bool,
    scale_class: str,
    rng: random.Random,
) -> None:
    """Re-pick ``pose`` if the finished outfit made the drawn one unperformable.

    :func:`_performable_poses` runs inside the randomize loop, where ``pose`` (field
    index 67) is drawn long before a *generated* ``outfit_description`` exists — it is
    composed after the loop ends. So its garment tests read an empty string, and the
    whole ``GARMENT_DEPENDENT_POSES`` gate was inert for every randomly generated
    outfit. The ``_DEFERRED_FIELDS`` note has named this trap for two releases; this
    closes it. Measured before the fix: of 324 random outfits matching
    ``_POCKETLESS_GARMENT_RE`` in 6,000 runs, **26 (8.0%)** drew a pockets/collar
    gesture -- "a pastel off-shoulder mermaid gown with long satin gloves" while
    "posing with hands in pockets".

    **Why a repair rather than deferral.** Moving ``pose`` into
    :data:`_DEFERRED_FIELDS` is the obvious fix and the wrong one: it relocates a draw
    that sits in the middle of the stream, so every existing seed would resolve to a
    different pose *and* different tattoos/legwear -- silently invalidating every
    published gallery image, exactly as the 0.90.0 prose change did, and
    ``entry_hash`` could not flag it. Repairing after the fact costs nothing instead.
    This runs at the very end of the draw order (after
    :func:`_resolve_deferred_fields`, and nothing is drawn later), and **consumes no
    RNG at all unless the pose is genuinely unperformable** -- the pool membership
    test is free. So a seed only changes when its pose was already wrong, and even
    then nothing downstream shifts, because nothing downstream draws.

    A preset costume was already in ``resolved`` during the loop, so its poses were
    filtered correctly the first time and this is a no-op for the whole cosplayer and
    archetype roster. An explicit lock is skipped, as everywhere else.
    """
    if "pose" in locked:
        return
    current = resolved.get("pose")
    if not current or _is_absent(current):
        return
    field_def = FIELD_DEFINITIONS["pose"]
    pool = _performable_poses(
        _build_option_pool("pose", field_def, gender, resolved),
        resolved, covers_face, covers_body, covers_hair,
    )
    if scale_class:
        pool = _scale_coherent_pool("pose", pool, scale_class)
    if current in pool or not pool:
        return  # still performable (or nothing better on offer) -- no RNG spent
    resolved["pose"] = _repick("pose", field_def, pool, gender, rng)


def _scale_class(widget_tier: str, character_tier: str | None) -> str:
    """Resolve the active scale class: ``"giant"``, ``"tiny"`` or ``""`` (none).

    Two sources feed this. ``widget_tier`` is the manual ``size_scale`` control on the
    Identity Forge node; ``character_tier`` is a wired Cosplayer entry's own
    ``size_scale``. **The widget wins**, which is the node's precedence rule
    everywhere else and matches the height override the widget already performs -- a
    user who picks ``tiny`` for a colossal character gets a tiny scene to go with the
    tiny body, not a contradiction.

    Returns ``""`` for ``Auto`` with no wired character, and for the human-plausible
    ``short`` / ``large`` tiers, so ordinary output is untouched.
    """
    for tier in (widget_tier, character_tier):
        if not tier:
            continue
        if tier in _GIANT_TIERS:
            return "giant"
        if tier in _TINY_TIERS:
            return "tiny"
    return ""


def _scale_coherent_pool(field_name: str, pool: list[str], scale_class: str) -> list[str]:
    """Narrow a scene/build pool so the render can actually show the subject's scale.

    An extreme change of scale is the one thing the prose cannot establish on its own.
    "Colossal and fifty feet tall" is a claim about the *relationship* between the
    subject and everything around them, so it only survives into the image when the
    frame contains something to measure against. Three fields decide that:

    * ``shot_type`` -- must hold a framing that keeps the world in shot, or looks up
      from ground level (:data:`_SCALE_SHOWING_SHOTS`).
    * ``location`` -- must be outdoors. A fifty-foot figure in a nail salon has no
      room to be fifty feet, and the interior sets the ceiling height that the model
      then draws the subject inside.
    * ``body_type`` -- must not simultaneously call the subject petite
      (:data:`_STATURE_BODY_TYPES`).
    * ``pose`` -- must not require furniture (:data:`FURNITURE_DEPENDENT_POSES`). This
      is a *consequence* of the location rule rather than an independent one: forcing
      the scene outdoors leaves no seat to perch on the edge of. Added 0.84.0; an audit
      of all 38 poses at giant scale found this to be the only genuinely impossible one
      (`leaning against a wall` reads better at scale, not worse -- the wall becomes a
      building).

    Only the giant class takes all four; ``tiny`` takes the framing rule alone, in
    its own lighter form (see :data:`_SHOTS_TOO_WIDE_FOR_TINY`). A three-foot subject
    perched on the edge of a seat is fine, so the pose rule is giant-only.

    **This is called from the randomize loop, which has already skipped every locked
    field, so an explicit user lock is never narrowed** -- lock ``location`` to a
    kitchen and you get the kitchen. An empty result also falls back to ``pool``
    rather than failing: ``location_setting: Indoor`` plus a giant is a contradiction
    the user asked for, and the 0.63.0 empty-studio-pool precedent is to keep the
    value rather than raise.

    **BIAS.** All four fields are safe, each for its own reason. ``shot_type`` and
    ``body_type`` are flat -- no ``FIELD_FAMILIES`` entry, no ``weights`` map -- so a
    narrowed pool stays uniform over the survivors. ``pose`` is family-weighted and
    passes because ``FURNITURE_DEPENDENT_POSES`` is exactly the ``seated_perch`` family,
    split out at 0.84.0 for this rule -- a WHOLE family, so the other eleven stay
    proportional. ``location`` *is* family-weighted,
    and it passes because its twelve families bucket perfectly: ``domestic``,
    ``food_drink``, ``retail_services``, ``leisure_fitness``, ``civic_institutional``,
    ``work_industrial`` and ``transit_travel`` are entirely indoor; ``urban_outdoor``,
    ``urban_landmark``, ``nature_outdoor`` and ``nature_landmark`` are entirely
    outdoor; ``studio`` is neither and is already excluded by every
    ``location_setting`` except its own. Filtering to outdoors therefore drops eight
    WHOLE families and leaves the surviving four proportional to each other -- the
    whole-unit drop the family-weight rule requires, never the partial cull that
    concentrates a frozen weight. This is also why the shipped
    ``location_setting: Outdoor`` control has never skewed anything.

    (The family list above was written when there were nine and went stale as the
    roster grew; it is re-verified mechanically by ``LocationFamilyBucketTests``, so
    a future family that straddles the boundary fails the suite rather than quietly
    skewing a giant's scenery.)
    """
    if scale_class == "giant":
        if field_name == "shot_type":
            return [v for v in pool if v in _SCALE_SHOWING_SHOTS] or pool
        if field_name == "location":
            return [v for v in pool if v in OUTDOOR_LOCATIONS] or pool
        if field_name == "body_type":
            return [v for v in pool if v not in _STATURE_BODY_TYPES] or pool
        if field_name == "pose":
            return [v for v in pool if v not in FURNITURE_DEPENDENT_POSES] or pool
    elif scale_class == "tiny":
        if field_name == "shot_type":
            return [v for v in pool if v not in _SHOTS_TOO_WIDE_FOR_TINY] or pool
    return pool


def _randomize_fields(
    locked: dict[str, str],
    gender: str,
    hair_color_scope: str,
    accessory_density: str,
    location_setting: str,
    rng: random.Random,
    covers_face: bool = False,
    covers_body: bool = False,
    covers_hair: bool = False,
    scale_class: str = "",
) -> dict[str, str]:
    """Fill every unlocked, non-control field from its option pool.

    ``locked`` maps field_name → user-chosen value (already excludes control
    and hidden fields). The returned dict contains every field.

    The ``covers_*`` flags are the cosplayer coverage flags; they only narrow the
    ``pose`` pool (see :func:`_performable_poses`). Every other suppression they
    drive happens after the fill, in :func:`generate_character`.

    ``scale_class`` is ``"giant"`` / ``"tiny"`` / ``""`` and narrows the scene and
    build pools so the render can show the scale (see :func:`_scale_coherent_pool`).
    It is applied inside this loop precisely because the loop has already skipped
    every locked field, so a user's explicit choice is never narrowed.
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
        if field_name in _DEFERRED_FIELDS:
            continue  # needs the finished outfit; drawn by _resolve_deferred_fields
        if field_name in resolved:  # locked
            continue

        pool = _build_option_pool(field_name, field_def, gender, resolved)
        if field_name == "skin_tone":
            pool = _bias_skin_tone(pool, resolved.get("ethnicity"), rng)
        elif field_name == "pose":
            pool = _performable_poses(pool, resolved, covers_face, covers_body, covers_hair)
        if scale_class:
            pool = _scale_coherent_pool(field_name, pool, scale_class)
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


def _requirement_pins(
    field: str, resolved: dict[str, str], presentation: str
) -> bool:
    """Is ``field`` currently pinned to a value by another live requirement rule?

    The guard on the requirement-side contrapositive repair (0.82.0). Re-rolling a
    trigger only helps when the trigger is free to move; if some *other* firing rule
    pins it, the next iteration forces it straight back and the loop ping-pongs to
    the iteration cap.

    The concrete case is the makeup chain: ``gender=Male`` requires
    ``makeup_style="no makeup"``, which in turn requires bare lashes/lips. With a
    lash lock, repairing ``makeup_style`` would be undone on every pass. Note the
    check is presentation-aware, so a ``Feminine``/``Any`` wardrobe -- where the
    male-makeup rule is gated off and ``makeup_style`` genuinely randomizes -- does
    allow the repair.
    """
    for rule in CONSTRAINT_RULES:
        if rule["type"] != "requirement" or rule.get("requires_field") != field:
            continue
        if rule.get("presentation_gated") and presentation != "Masculine":
            continue
        if resolved.get(rule["field"]) == rule["value"]:
            return True
    return False


def _conflicting_trigger_values(
    trigger: str, resolved: dict[str, str], locked: set[str], presentation: str
) -> set[str]:
    """Values of ``trigger`` that contradict a LOCKED field — across BOTH rule types.

    Shared by both halves of the contrapositive repair, and that sharing is the whole
    point. Each branch used to build this set from its *own* rule type only: the
    exclusion branch collected exclusion rules, the requirement branch collected
    requirement rules. Neither saw the other's bans on the same trigger, so each
    repair handed the other a value it would immediately reject — and for a male
    character with a bold eyeliner locked the two sets partition the whole five-value
    ``makeup_style`` pool between them:

        exclusion branch bans the four naturals  -> leaves only "no makeup"
        requirement branch bans "no makeup"      -> leaves only the four naturals

    That is a closed cycle, not a near miss. The loop ping-ponged to
    ``_MAX_CONSTRAINT_ITERATIONS`` and emitted whichever half of the cycle the 12th
    pass happened to hold, which is how a character came out wearing "no makeup"
    beside nude lipstick, lash extensions, laminated brows and dewy skin. Measured at
    **40 of 40 seeds** for each of 14 lock values (the bold ``eye_makeup`` /
    ``eyeliner`` / ``lashes`` entries) under gender ``Male`` with wardrobe
    ``Feminine`` or ``Any`` — i.e. squarely on the deliberately-femme male look the
    wardrobe control exists to serve.

    With one union the cycle cannot form: when every candidate is banned the pool
    comes back empty, the repair is correctly abandoned, and control falls through to
    the caller's ``warn()`` — the lock wins, the trigger keeps a value that is
    coherent with everything *else*, and the user is told about the conflict. This is
    the same union-of-every-live-rule argument the 0.78.0 comment makes for the
    forward direction, finally applied across rule types as well.

    Strictly a superset of what each branch computed before, so a repair that already
    converged is untouched: :func:`_repick` consumes the same RNG regardless of pool
    contents, so no seed drifts except where the broader ban actually removes the
    candidate that was about to be (wrongly) chosen.
    """
    conflicting: set[str] = set()
    for rule in CONSTRAINT_RULES:
        if rule["field"] != trigger:
            continue
        if rule.get("presentation_gated") and presentation != "Masculine":
            continue
        if rule["type"] == "exclusion":
            target = rule["excludes_field"]
            if target in locked and resolved.get(target) in set(rule["excludes_values"]):
                conflicting.add(rule["value"])
        else:
            target = rule["requires_field"]
            if target not in locked:
                continue
            want, have = rule["requires_value"], resolved.get(target)
            # Two absent-but-different values (e.g. "None" vs "no eyeshadow") both
            # render nothing, so they are not a contradiction — same equivalence the
            # requirement branch already applies before warning.
            if want == have or (_is_absent(want) and _is_absent(have)):
                continue
            conflicting.add(rule["value"])
    return conflicting


def _apply_constraints(
    resolved: dict[str, str],
    gender: str,
    locked: set[str],
    rng: random.Random,
    presentation: str = "Masculine",
    scale_class: str = "",
) -> list[str]:
    """Apply :data:`CONSTRAINT_RULES` until stable. Returns warning messages.

    Locked fields are never silently overwritten: when a constraint would
    change a locked field, the lock wins and a warning is recorded instead.

    ``presentation`` is the resolved wardrobe presentation. Rules flagged
    ``presentation_gated`` (the masculine-default jewellery/nail trims) apply only
    when a man reads ``"Masculine"``; a Feminine/"Any" wardrobe skips them so a
    deliberately femme male look keeps feminine-coded pieces available. The default
    is ``"Masculine"`` so a caller that omits it keeps the historical male defaults.

    ``scale_class`` narrows every re-pick pool the same way the initial fill was
    narrowed (see :func:`_scale_coherent_pool`). Without it a constraint could hand a
    giant an indoor location right back: the lighting rules use ``location`` as their
    trigger, so a *locked* indoor light drives the contrapositive repair to re-roll
    ``location`` -- straight past the filter the randomizer applied.
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
                        # Every value that contradicts ANY locked field, of EITHER
                        # rule type. Scoping this to exclusion rules on this one
                        # target is what let the two repairs deadlock — see
                        # _conflicting_trigger_values.
                        conflicting = _conflicting_trigger_values(
                            trigger, resolved, locked, presentation)
                        pool = [v for v in _scale_coherent_pool(
                            trigger,
                            _build_option_pool(trigger, trig_def, gender, resolved),
                            scale_class,
                        ) if v not in conflicting]
                        if pool:
                            resolved[trigger] = _repick(trigger, trig_def, pool, gender, rng)
                            changed = True
                            continue
                    warn(target, f"'{rule['field']}={rule['value']}' conflicts with "
                                 f"locked '{target}={resolved[target]}'; keeping lock.")
                    continue
                field_def = FIELD_DEFINITIONS.get(target)
                if field_def is None:
                    continue
                # Re-pick against the union of EVERY exclusion currently firing on
                # this target, not just this rule's values.
                #
                # 0.78.0 bug fix (latent since the multi-rule constraints landed):
                # filtering only ``excluded`` left the re-pick pool full of values
                # some *other* live rule forbids, so the loop ping-ponged -- rule A
                # re-picks a value rule B bans, rule B re-picks a value rule A bans
                # -- and whatever the 12th pass happened to hold was emitted. It
                # mostly went unnoticed because convergence was likely while few
                # values were banned. Splitting the ``loose`` family took the legal
                # hair_style set on a buzz cut from 7 of 33 down to 2 of 33, which
                # made the cap bite constantly and surfaced it: buzz cuts came out
                # with high ponytails, and afros landed on pin-straight hair.
                #
                # Collecting the union converges in a single pass and is strictly
                # more correct. The contrapositive branch above already builds its
                # ``conflicting`` set the same way, so this only brings the forward
                # direction in line with it.
                forbidden = set(excluded)
                for other in CONSTRAINT_RULES:
                    if (other["type"] != "exclusion"
                            or other.get("excludes_field") != target):
                        continue
                    if (other.get("presentation_gated")
                            and presentation != "Masculine"):
                        continue
                    if resolved.get(other["field"]) != other["value"]:
                        continue
                    forbidden.update(other["excludes_values"])
                pool = [v for v in _scale_coherent_pool(
                    target,
                    _build_option_pool(target, field_def, gender, resolved),
                    scale_class,
                ) if v not in forbidden]
                if pool:
                    resolved[target] = _repick(target, field_def, pool, gender, rng)
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
                    # Contrapositive repair, requirement side (0.82.0). The exclusion
                    # branch above has re-rolled the randomized *trigger* since 0.50.0,
                    # but the requirement branch only ever warned -- so a deliberate
                    # lock lost to a random draw and said so twice per run:
                    #
                    #   'makeup_style=no makeup' wants 'lashes=natural bare' but
                    #   'lashes' is locked to 'lash extension look'; keeping lock.
                    #
                    # The lock did win, so the message described the engine doing the
                    # right thing -- while leaving the *output* incoherent (a bare-face
                    # style beside lash extensions). Re-rolling the trigger instead
                    # produces a makeup style that actually wants those lashes, and the
                    # warning disappears because the conflict does. Same shape for a
                    # locked smile_type against a contradicting random expression, and
                    # a locked hair_part against 'slicked back'.
                    trigger = rule["field"]
                    trig_def = FIELD_DEFINITIONS.get(trigger)
                    if (trig_def is not None and trigger not in locked
                            and not trig_def.get("control")
                            and not _requirement_pins(trigger, resolved, presentation)):
                        # Union of every trigger value that would contradict ANY
                        # locked target -- not just this rule's target, and not just
                        # this rule's TYPE. Filtering on one rule alone is the 0.78.0
                        # exclusion bug in the other branch; filtering on one rule
                        # type is the deadlock documented in
                        # _conflicting_trigger_values. The union converges in a
                        # single pass, or abandons the repair and warns.
                        conflicting = _conflicting_trigger_values(
                            trigger, resolved, locked, presentation)
                        pool = [v for v in _scale_coherent_pool(
                            trigger,
                            _build_option_pool(trigger, trig_def, gender, resolved),
                            scale_class,
                        ) if v not in conflicting]
                        if pool:
                            resolved[trigger] = _repick(trigger, trig_def, pool, gender, rng)
                            changed = True
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


def _compose_outfit_clause(
    garment: str, resolved: dict[str, str], locked_clean: set[str]
) -> str:
    """Compose the generated outfit with its palette, pattern and footwear (0.83.0).

    ``garment`` is a garment phrase from ``OUTFIT_DESCRIPTIONS`` — garments and fabrics
    only, no leading article. Returns the finished clause for the "wears ..." slot, e.g.
    ``"a jewel-toned satin slip gown with delicate straps, in strappy heels"``.

    **Mutates ``resolved``**: any axis suppressed by a guard is popped, so ``prompt_json``
    can never disagree with ``prompt_text`` again — that mismatch is the defect this
    whole phase exists to fix. An explicitly locked field is never popped.

    Order matters. The palette adjective is prefixed and the phrase articled *before* the
    pattern tail is appended, so ``_article_if_singular`` reads the garment's head noun
    ("gown") rather than the tail's ("print").

    Called only for an outfit the ENGINE generated. A supplied costume (cosplayer /
    archetype / user-typed) drops all three fields instead — that boundary is what keeps
    this change non-breaking for the whole roster.
    """
    def _wanted(field: str, guard_fired: bool) -> str | None:
        """The value to voice for ``field``, or ``None`` after suppressing it.

        **A lock beats a guard.** Everywhere else in this engine an explicit lock survives
        suppression, and here the alternative is not merely inconsistent — skipping the
        clause while leaving the locked value in ``resolved`` would put the JSON back in
        disagreement with the prose, which is the exact defect this phase removes. So a
        locked field is voiced even when the garment already states that axis (striped
        denim is a real fabric), and only an UNLOCKED value yields to the garment.
        """
        value = resolved.get(field)
        if field in locked_clean:
            return value if value and not _is_absent(value) else None
        if guard_fired:
            resolved.pop(field, None)
            return None
        return value if value and not _is_absent(value) else None

    phrase = LEADING_ARTICLE_RE.sub("", garment).strip() or garment

    # --- palette ------------------------------------------------------------------
    colour = _wanted("clothing_color", bool(COLOUR_WORD_RE.search(phrase)))
    if colour:
        adjective = PALETTE_ADJECTIVES.get(colour)
        if adjective:
            phrase = f"{adjective} {phrase}"
        else:                    # unmapped value: say nothing rather than guess
            resolved.pop("clothing_color", None)

    phrase = _article_if_singular(phrase)

    # --- pattern ------------------------------------------------------------------
    pattern = _wanted("clothing_pattern", bool(PATTERN_WORD_RE.search(phrase)))
    if pattern:
        tail = PATTERN_TAILS.get(pattern)
        if tail:
            phrase += tail
        elif tail is None:       # unmapped value
            resolved.pop("clothing_pattern", None)
        # A mapped-but-EMPTY tail ("solid") is deliberate silence and the field stays:
        # "solid" is true of the garment, it just does not need saying.

    # --- legwear ------------------------------------------------------------------
    # Sits between the garment and the shoes because that is the order it is worn in,
    # and reads as "a pleated skirt ..., with opaque black tights, in ankle boots".
    # No guard is passed: _wearable_legwear has already forced the absent token for
    # any outfit that covers the leg, so by the time the clause is built there is
    # nothing left to suppress -- and a lock still wins, exactly as it does above.
    hose = _wanted("legwear", False)
    if hose:
        phrase += f", with {hose}"

    # --- footwear -----------------------------------------------------------------
    shoes = _wanted("footwear", bool(SHOE_RE.search(phrase)))
    if shoes:
        override = _FOOTWEAR_CLAUSES.get(shoes)
        phrase += f", {override}" if override else f", in {shoes}"

    return phrase


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
    mask_text: str | None = None,
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
    # Both branches now pick the article from the text. The human branch used to
    # hardcode "A " to avoid disturbing existing output, which shipped "A Armenian
    # woman" (18 of 92 ethnicities start with a vowel, and they lead whenever age is
    # omitted) and "a 18-year-old". Prose-only: no RNG draw moves, so no seed drift,
    # and entry_hash covers the entry dict rather than the prose, so no gallery
    # image is invalidated by this.
    lead = f"{_a(lead_tail).capitalize()} {lead_tail}"
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
        # Normally "{colour} {shape} eyes". A free-text ``eyes`` override may already
        # end in the eye part it describes ("green with vertical cat-slit pupils",
        # "red on black sclera") -- appending the noun there gives "...pupils eyes".
        # Same guard, and same reasoning, as the skin_tone material-noun check above.
        eye_desc = _words(g("eye_color"), g("eye_shape"))
        features.append(eye_desc if _EYE_PART_RE.search(eye_desc) else f"{eye_desc} eyes")
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

    # --- Tattoos --------------------------------------------------------
    # Its OWN sentence, deliberately, rather than another item on the end of the
    # clothing list. A marking appended to a long garment list is the failure that
    # made Judy Alvarez's face tattoo and the Kabuki Actor's kumadori fail to
    # render -- by the time the model reaches it, sixty tokens of clothing have
    # already claimed the pixels. It also has to stand apart from the skin sentence
    # above because that sentence is Face-group and disappears behind a mask, while
    # body ink does not.
    if g("tattoos"):
        placement = g("tattoo_placement")
        sentences.append(f"{subj} {has} {g('tattoos')}"
                         + (f" {placement}" if placement else ""))

    # --- Hair -----------------------------------------------------------
    # "bald" is a head state, not a hair description — voice it as its own
    # sentence ("his head is bald", never "his hair is bald"). The engine has
    # already dropped the other scalp-hair fields for a bald head.
    if g("hair_length") == "bald":
        sentences.append(f"{poss} head is bald")
    is_bald = g("hair_length") == "bald"
    hair_desc = ("" if is_bald
                 else _words(g("hair_length"), g("hair_texture"), g("hair_color")))
    if hair_desc:
        s = f"{poss} hair is {hair_desc}"
        if g("hair_style"):
            s += f", {g('hair_style')}"
        sentences.append(s)
    elif g("hair_style") and not is_bald:
        sentences.append(f"{poss} hair is {g('hair_style')}")
    hair_extra = []
    if g("hair_part") and not is_bald:
        part = g("hair_part")
        hair_extra.append(_an(part, "" if "part" in part else "part"))
    if g("hair_highlights") and not is_bald:
        hl = g("hair_highlights")
        hair_extra.append(hl if "highlight" in hl else f"{hl} highlights")
    if g("facial_hair"):
        fh = g("facial_hair")
        # Mass/plural values ("stubble", "mutton chops") read naturally bare;
        # the singular pieces ("full beard", "mustache") take an article.
        hair_extra.append(fh if fh in ("stubble", "mutton chops") else _an(fh))
    if g("hair_accessory") and not is_bald:
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
            # Singular pieces take an article ("a brooch", "a nose stud"); plural ones
            # ("pearl studs", "layered gold chains") stay bare, so the list agrees with
            # the watch below, which has always been articled.
            jewelry.append(_article_if_singular(g(field)))
    if g("watch_type"):
        watch = g("watch_type")
        jewelry.append(_an(watch, "" if "watch" in watch else "watch"))
    if g("nails"):
        jewelry.append(f"{g('nails')} nails" if "nail" not in g("nails") else g("nails"))
    if jewelry:
        sentences.append(f"{subj} {has} " + _join(_dedupe(jewelry)))

    # --- The head, for a masked character -------------------------------
    # BEFORE the clothing, and in its own sentence. Until 0.90.0 the mask was
    # comma-appended to the costume string, so it arrived as the last item of a
    # "He wears ..." garment list -- and the model rendered the garments and
    # ignored the head. Six entries were reported at once from a render review
    # (Silent Hill Nurse, The Ghoul, Figrin D'an, Ithorian, Larfleeze, Dexter
    # Jettster), each rendering as an ordinary person wearing a costume.
    #
    # Position is the fix, not wording: leading the description with the head
    # gives it its own weight instead of making it compete with five garments.
    # "has" rather than "wears" because a mask slot describes what the head IS
    # (an alien skull, a bandaged stump), not something worn on top of it.
    if mask_text:
        sentences.append(f"{subj} {has} {mask_text}")

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
        clothing.append(f"carrying {_article_if_singular(g('bag'))}")
    if g("accessories"):
        clothing.append(f"accessorized with {_article_if_singular(g('accessories'))}")
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
        scene.append(f"set in {_location_clause(g('location'))}")
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
    if g("composition"):
        scene.append(f"composed with {g('composition')}")
    # Skip mood when it merely restates the expression (e.g. expression "confident"
    # + "confident mood"); expression is the face, mood the scene -- only redundant
    # when identical.
    if g("mood") and g("mood") != g("expression"):
        scene.append(f"with {_a(g('mood'))} {g('mood')} mood")
    if scene:
        sentences.append(_join(scene) if len(scene) > 1 else scene[0])

    # Capitalize each sentence's first letter (0.83.0). The join has always been a plain
    # ". " and relied on every sentence opening with a pronoun or possessive -- which held
    # only by luck. Each scene element after the first is a lowercase fragment ("set in",
    # "under", "during", "the framing is", "composed with", "with a ... mood"), so
    # whenever `expression` was absent the whole scene sentence rendered lowercase:
    #
    #     "He is standing with feet planted wide. set in a retro diner-style kitchen, ..."
    #
    # This is LATENT AND PRE-0.83.0 -- locking `expression` to "None" reproduces it in
    # every prior release. Suppressing `expression` under a full mask merely made it
    # common (~200 masked entries) instead of rare, and the preview pass caught it.
    # Fixed at the join so the whole CLASS is closed rather than the one instance: any
    # future field that opens a sentence is covered. Prose-only, no RNG, and a no-op for
    # every sentence that already began with a capital.
    text = ". ".join(
        (s[0].upper() + s[1:]) for s in (s.strip() for s in sentences) if s
    )
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


def _document_fields(document: dict) -> set[str]:
    """Every field name a preset document sets across its group sub-dicts."""
    fields: set[str] = set()
    for key, value in document.items():
        if key in ("_meta", _MODIFIERS_DOC_KEY) or not isinstance(value, dict):
            continue
        fields.update(name for name, val in value.items() if isinstance(val, str))
    return fields


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

    **"Own wins" has to hold for the reserved ``_meta`` keys too, not just fields.**
    A plain key-by-key merge honours it only for keys the downstream node actually
    writes, and two classes of key escaped that:

    * :data:`_COSTUME_META_KEYS` describe the *worn costume*, and the Cosplayer node
      writes ``covers_face`` / ``covers_body`` / ``covers_hair`` unconditionally
      (even when false) precisely so a downstream node overrides an upstream one --
      but ``mask`` and ``size_scale`` were only written when present, so they
      survived. Chaining Cosplayer "Iron Man" -> Cosplayer "Hermione Granger"
      correctly reset ``covers_face`` to false and still rendered "She has a
      faceplate with narrow glowing eye slits" over the Hogwarts uniform; via
      Godzilla it also leaked ``size_scale: giant`` and its authored ``height``.
      The Archetype / Creature / Modifier nodes write *none* of the five, so
      Cosplayer -> Archetype leaked all of them at once -- a ballerina in a tutu
      with Iron Man's faceplate, no face, no hair and no jewellery.
    * ``_meta.variants`` carries a per-gender archetype's two look blocks, and
      :func:`generate_character` folds the matching one in *after* the merged locks,
      so it beat everything downstream of it. Archetype "Battle Bard" -> Cosplayer
      "Hermione Granger" merged the Hogwarts uniform correctly into ``Clothing`` and
      then rendered the Bard's velvet doublet, speakeasy, string lights and cheerful
      mood over it, still labelled "Cosplaying as Hermione Granger". 34 archetypes
      carry variants.

    Both are fixed here rather than downstream because this is where the precedence
    contract lives -- and fixing it here covers every node pairing at once, including
    hand-authored documents, instead of patching each emitter. The rule for the
    costume keys is that a document supplying its own ``outfit_description`` replaces
    the *look*, so the upstream's costume-derived state is stale; the rule for
    variants is plain field-level precedence.
    """
    upstream = _load_document(upstream_json)
    own = _load_document(own_json)
    if not own:  # this node is inactive ("None") -> pass the upstream through
        return json.dumps(upstream, indent=2) if upstream else "{}"
    if not upstream:
        return json.dumps(own, indent=2)

    merged: "OrderedDict[str, Any]" = OrderedDict()
    own_meta = _as_dict(own.get("_meta"))
    meta = {**_as_dict(upstream.get("_meta")), **own_meta}
    own_fields = _document_fields(own)

    # The downstream document supplies its own costume, so the upstream's
    # costume-derived flags no longer describe anything that is being worn.
    dropped_scale = False
    if "outfit_description" in own_fields:
        for key in _COSTUME_META_KEYS:
            if key not in own_meta and key in meta:
                del meta[key]
                dropped_scale = dropped_scale or key == "size_scale"

    # A ``size_scale`` entry always ships with an authored ``scale_prose`` locked into
    # ``height`` (validator-enforced), so dropping the tier has to drop that phrase
    # too -- otherwise the scene stops being narrowed for a giant while the lead
    # sentence still calls the character "colossal and hundreds of feet tall".
    stale_height = dropped_scale and "height" not in own_fields

    # Field-level precedence for an upstream archetype's variant look blocks: a
    # variant may only fill fields the downstream document leaves open.
    variants = meta.get("variants")
    if "variants" not in own_meta and isinstance(variants, dict) and own_fields:
        pruned = {
            variant_gender: {
                field: value for field, value in look.items()
                if field not in own_fields
            }
            for variant_gender, look in variants.items()
            if isinstance(look, dict)
        }
        pruned = {g: look for g, look in pruned.items() if look}
        if pruned:
            meta["variants"] = pruned
        else:
            del meta["variants"]

    if meta:
        merged["_meta"] = OrderedDict(meta)
    # Canonical groups first, then any unexpected extras; own fields win on overlap.
    keys = [k for k in _GROUP_ORDER if k in upstream or k in own]
    keys += [
        k for k in (*upstream, *own)
        if k != "_meta" and k not in _GROUP_ORDER and k not in keys
    ]
    height_group = FIELD_DEFINITIONS.get("height", {}).get("group", "Body")
    for key in keys:
        section = {**_as_dict(upstream.get(key)), **_as_dict(own.get(key))}
        if stale_height and key == height_group:
            section.pop("height", None)
        if section:
            merged[key] = section
    return json.dumps(merged, indent=2)


def _format_json(
    resolved: dict[str, str], gender: str, hair_color_scope: str, wardrobe: str,
    cosplay_label: str | None = None, species: dict | None = None,
    # APPENDED, not inserted -- generate_character calls this positionally, the same
    # rule the engine entry point documents for its own signature.
    covers_face: bool = False, covers_body: bool = False, covers_hair: bool = False,
    mask_text: str | None = None, size_scale: str = "",
    omitted: "list[str] | None" = None,
) -> str:
    """Build a JSON document: ``_meta`` plus fields nested by group.

    The seed is intentionally excluded — it is run-control noise, not part of
    the character description. A connected creature's ``Species & Anatomy`` group
    is re-emitted (in canonical order) alongside its identifying ``_meta``.

    **The document has to be self-describing, because the vault round-trips it.**
    ``prompt_json`` is exactly what Vault Save writes to disk, and Vault Load feeds it
    straight back into ``archetype_json`` — the node's stated promise being that "a
    single saved document captures the whole character regardless of how the graph was
    wired". It did not. Two omissions compounded:

    * The concealment state (``covers_face`` / ``covers_body`` / ``covers_hair`` /
      ``mask`` / ``size_scale``) lived only on the Cosplayer node's document, never on
      this one. So recall restored Iron Man's costume but not the *reasons* it hid
      anything: the faceplate sentence vanished and a full randomized face, hair and
      makeup were generated under the armour, with a stray ethnicity and skin tone on
      a fully-encased character.
    * :func:`group_fields` strips ``"None"``, which is precisely the token the
      Cosplayer builder injects to suppress a field. She-Hulk's ``ethnicity: "None"``
      therefore did not survive, and a randomized ethnicity reappeared under the body
      paint — the exact failure 0.78.0 added that suppression to fix.

    Both are recorded here, so recall needs no changes on the load side:
    :func:`_parse_archetype_json` already reads the five costume keys, and now reads
    ``omitted`` as well. ``omitted`` lists only *explicitly locked* absences, never a
    field that merely randomized to nothing, so a plain run records an empty list and
    is unchanged.
    """
    species = species or {}
    slots = species.get("slots") or {}

    meta: "OrderedDict[str, Any]" = OrderedDict()
    if cosplay_label:
        meta["cosplay_of"] = cosplay_label
    if slots:
        for key in ("creature_of", "creature_class", "form"):
            if species.get(key):
                meta[key] = species[key]
    meta["gender"] = gender
    meta["hair_color_scope"] = hair_color_scope
    meta["wardrobe"] = wardrobe
    # Only emitted when actually in play, so an ordinary character's document is
    # byte-identical to previous releases.
    if covers_face:
        meta["covers_face"] = True
    if covers_body:
        meta["covers_body"] = True
    if covers_hair:
        meta["covers_hair"] = True
    if mask_text:
        meta["mask"] = mask_text
    if size_scale:
        meta["size_scale"] = size_scale
    if omitted:
        meta["omitted"] = sorted(omitted)

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

    Goes through :func:`_prepend_descriptor` so an article-led value keeps its
    article in front: a costume reads "a gothic black dress" by convention, and a
    blind prepend produced "wears weathered a gothic black dress". Values with a
    plural / mass head ("robes", "plate armor") just take the descriptor in front.
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
            resolved[field] = _prepend_descriptor(value, descriptor)


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
    size_scale: str = _SIZE_SCALE_AUTO,
    character_scale: str = "",
    widget_locked: frozenset[str] | None = None,
    # APPENDED, not inserted mid-signature. `execute` calls this positionally, so a
    # parameter added in the middle silently shifts every argument after it -- it put
    # a string into `gender_variants` and crashed on `.get`. The same shape as the
    # widgets_values shift fixed twice already this release: positional interfaces
    # tolerate appends and nothing else.
    mask_text: str | None = None,
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

    ``widget_locked`` names the fields whose **widget on this node** the user moved off
    ``"Random"``. It is deliberately narrower than ``locked``: see
    :data:`_CONCEALED_FACE_GROUPS` for why the concealment blocks need to tell a user's
    own choice apart from a wired preset's authored look. ``None`` (the default) means
    "no widget locks", so every caller that does not pass it is unaffected.

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

    ``size_scale`` is a MANUAL-ONLY override. ``"Auto"`` (the default) leaves scale
    unstated and is never chosen by the randomizer, so the control cannot bias any
    distribution. Any other tier replaces the ``height`` value with a hand-authored
    scale phrase, letting a perfectly ordinary randomized person be rendered
    towering or doll-sized. A cosplayer's own ``size_scale`` wins, so selecting a
    tier cannot shrink a canonically giant character.

    ``character_scale`` is a wired Cosplayer entry's own ``size_scale`` tier. It does
    not set the height (the Cosplayer node already locked its authored ``scale_prose``
    into that slot); it tells the engine which scale is in play so the framing,
    location and build stay coherent with it.
    """
    rng = random.Random(seed)
    widget_locked = widget_locked or frozenset()
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
    # Manual size-scale override. Replaces `height` outright rather than prepending,
    # so the lead sentence reads "with a slim build, towering and hulking, easily
    # twelve feet tall, and fair skin" instead of stacking two contradictory height
    # words. Free text survives the gender gate because `height`'s two pools are
    # identical (`_gender_permits` short-circuits) -- the same route the Cosplayer
    # node's `scale_prose` and the body-paint skin anchor already take.
    #
    # PRECEDENCE: the widget wins, including over a wired character's own scale.
    # That is the node's rule everywhere else ("explicit non-Random widgets still
    # override" a preset), and a user who deliberately picks a tier expects it to
    # apply. The alternative -- silently ignoring the tier whenever a cosplayer is
    # connected -- looks like a broken control. `Auto` is never picked by the
    # randomizer, so this whole path is inert unless a human chooses a tier.
    if size_scale != _SIZE_SCALE_AUTO:
        phrase = _SIZE_SCALE_PHRASES.get(size_scale)
        if phrase:
            locked_clean["height"] = phrase
        else:
            print(f"[IdentityForge] Unknown size_scale {size_scale!r}; ignoring. "
                  f"Expected 'Auto' or one of: "
                  f"{', '.join(_SIZE_SCALE_PHRASES)}.")

    # Which scale, if any, the scene has to be able to show. Empty for ordinary
    # output, so every pool below is untouched unless a scale is genuinely in play.
    scale_class = _scale_class(
        size_scale if size_scale != _SIZE_SCALE_AUTO else "", character_scale
    )

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
        locked_clean, gender, hair_color_scope, accessory_density, location_setting, rng,
        covers_face=covers_face, covers_body=covers_body, covers_hair=covers_hair,
        scale_class=scale_class,
    )

    # Wardrobe presentation gates the masculine-default trims: a man reads Masculine
    # under "Match gender", but a Feminine/"Any" wardrobe keeps feminine-coded
    # jewellery/nails available so a deliberately femme male look still works.
    presentation = _presentation_mode(gender, wardrobe)
    warnings = _apply_constraints(
        resolved, gender, set(locked_clean), rng, presentation, scale_class
    )
    for message in warnings:
        print(message)

    # A costume override (outfit_description supplied by an archetype/cosplayer)
    # is already a complete outfit, so the separately-randomized garment fields
    # (outfit_style, footwear, colour, pattern) would only add noise — and
    # sometimes contradiction ("barefoot" beside heeled boots) — to the JSON.
    # Drop them when a costume is set; the prose already omits them in that case.
    # When no costume is supplied, generate one from the random outfit_style.
    if _is_absent(resolved.get("outfit_description")):
        # 0.83.0: the generated outfit is a GARMENT phrase, so the palette, pattern and
        # footwear compose onto it instead of being drawn and thrown away. Mutates
        # `resolved`, popping any axis a guard suppressed, so the JSON matches the prose.
        garment = _resolve_outfit_description(resolved, gender, wardrobe, rng)
        # Three-step, and the order is forced. `legwear` gates on the garment, and
        # the composed clause then VOICES legwear -- so it has to be drawn between
        # picking the garment and composing around it. Parking the raw garment in
        # `resolved` first is what lets the deferred draw see it.
        resolved["outfit_description"] = garment or ""
        _resolve_deferred_fields(resolved, gender, accessory_density, rng)
        resolved["outfit_description"] = (
            _compose_outfit_clause(garment, resolved, set(locked_clean))
            if garment else garment
        )
    else:
        for field in ("outfit_style", "footwear", "clothing_color", "clothing_pattern"):
            resolved.pop(field, None)
        # A preset costume is already a finished outfit string, so the deferred
        # fields can gate on it directly. legwear is suppressed for costumes further
        # down (_COSTUME_SUPPRESSED_EXTRAS); tattoo_placement still resolves, because
        # ink under a costume is coherent.
        _resolve_deferred_fields(resolved, gender, accessory_density, rng)

    # The outfit is final at last, so the pose gate can finally see it -- inside the
    # randomize loop a *generated* costume does not exist yet. Free unless the drawn
    # pose is genuinely unperformable in the finished garment, and nothing is drawn
    # after this point, so no seed drifts except the ones that were already wrong.
    # See _repair_pose for why this is a repair rather than a deferral.
    _repair_pose(resolved, gender, set(locked_clean), covers_face, covers_body,
                 covers_hair, scale_class, rng)

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

    # An outfit that already includes headwear can't stack a second hat from the
    # randomized ``accessories`` field ("a top hat … accessorized with wide brim
    # sun hat"). Drop a hat-valued draw when the outfit reads as headwear — this
    # covers cosplayer costumes, archetype outfits and random outfits alike, and
    # costs no RNG. Non-hat accessories still show; a user lock is respected.
    if (_HAT_RE.search(outfit_text)
            and resolved.get("accessories") in _HAT_ACCESSORY_VALUES
            and "accessories" not in locked_clean):
        resolved.pop("accessories", None)

    # The same rule, generalized to every other worn item the costume can already name
    # (0.83.0). See ``WORN_ITEM_RES``: a costume that spells out a pendant, earrings, a
    # ring, a bangle, a brooch or a bag must not have a second one bolted on by the
    # randomizer. Costs no RNG (the field is dropped after the fill) and respects an
    # explicit lock, so a user who deliberately locks a necklace still gets it. Only the
    # NAMED field is dropped — this is not the 0.66.0 group-level question.
    for field, pattern in WORN_ITEM_RES.items():
        if (field in resolved
                and field not in locked_clean
                and not _is_absent(resolved.get(field))
                and pattern.search(outfit_text)):
            resolved.pop(field, None)

    # A provided costume (archetype / cosplayer / a user-typed outfit) is a complete,
    # intentional look, so the engine should not bolt a random accessory *extra* onto
    # it — a designer tote or wristwatch on a samurai, a scrunchie or sunglasses on a
    # knight (anachronistic or just noise). When an outfit_description was locked, drop
    # the random bag / watch / hair accessory / accessory unless the look explicitly set
    # one (an authored scarf, flower crown or hair comb survives). A plain no-costume run
    # has no locked outfit, so a random modern person still gets them. No RNG; respects
    # explicit locks. (The hat-stacking rule above still guards plain runs whose auto
    # outfit rolls headwear; jewellery stays, governed by the full-shell rule below.)
    if "outfit_description" in locked_clean:
        for field in _COSTUME_SUPPRESSED_EXTRAS:
            if field not in locked_clean:
                resolved.pop(field, None)

    # Gloved/gauntleted hands hide the fingers, so a randomized fingernail polish or ring
    # would render on top of the glove (the reported bug). Two sources: the resolved
    # outfit text, and -- since 0.83.0, when gloves joined the pool -- the `accessories`
    # field. ``_FINGERLESS_RE`` opts out: fingerless gloves expose the fingers, so
    # nails/rings should still show. A power ring worn OVER the glove (Green Lantern,
    # Sinestro) is written into the costume prose, not the ``rings`` field, so it survives.
    # ``other_jewelry`` holds only body pieces (anklet, arm cuff, body chain, ...), none of
    # which sit on the fingers, so gloves suppress nails + the dedicated rings field only.
    #
    # Deliberately placed AFTER the costume-extras suppression above: a locked costume
    # drops the random `accessories` draw entirely, and suppressing nails for a glove that
    # was itself just dropped would be over-suppression from a value that never renders.
    if ((_GLOVE_RE.search(outfit_text) and not _FINGERLESS_RE.search(outfit_text))
            or resolved.get("accessories") in _GLOVE_ACCESSORY_VALUES):
        for field in ("nails", "rings"):
            if field not in locked_clean:
                resolved.pop(field, None)

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
    # here. ethnicity (Demographics) joins it: with no visible skin or face left,
    # mentioning it only risks nudging the render toward a human trait that has
    # nothing to attach to. An explicit user lock on either field is respected.
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
    #
    # 0.84.0: a WIDGET lock wins. Deliberately `widget_locked`, not `locked_clean` --
    # see _CONCEALED_FACE_GROUPS for the eight entries that measurement caught.
    if covers_face:
        for field in list(resolved):
            if ((FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_FACE_GROUPS
                    or field in _CONCEALED_FACE_FIELDS)
                    and field not in widget_locked):
                resolved.pop(field, None)
        # 0.83.0: a facial expression behind a moulded head. Separate block because
        # `expression` is in Setting & Shot and so cannot be reached by group -- but the
        # same widget-lock rule (0.84.0). See _CONCEALED_FACE_SOFT_FIELDS.
        for field in _CONCEALED_FACE_SOFT_FIELDS:
            if field not in widget_locked:
                resolved.pop(field, None)

    # A hood / cowl / lekku covers only the scalp while the face shows: drop the Hair
    # group so no randomized hair contradicts the covering, but keep Face and Makeup.
    # (A character with both covers_face and covers_hair has its hair dropped by the
    # covers_face block above already; this just handles the face-visible case.)
    # Widget locks win here for the same reason, and on the same evidence.
    if covers_hair:
        for field in list(resolved):
            if (FIELD_DEFINITIONS.get(field, {}).get("group") in _CONCEALED_HAIR_GROUPS
                    and field not in widget_locked):
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
    ) or resolved.get("accessories") in _GLOVE_ACCESSORY_VALUES
    prose = _format_prose(resolved, gender, cosplay_label, species,
                          hands_visible=not hands_covered, mask_text=mask_text)
    # Fields a preset or a widget deliberately locked ABSENT. They are stripped from
    # the group output (``group_fields`` drops "None"), so without recording them the
    # document cannot round-trip through the vault -- a recalled She-Hulk grew a
    # randomized ethnicity back under her body paint. Only explicit locks qualify; a
    # field that merely randomized to nothing is not a decision worth restoring.
    omitted = sorted(name for name, value in locked_clean.items() if value == "None")
    json_output = _format_json(
        resolved, gender, hair_color_scope, wardrobe, cosplay_label, species,
        covers_face=covers_face, covers_body=covers_body, covers_hair=covers_hair,
        mask_text=mask_text,
        # The tier actually in force: the widget overrides a wired character's own,
        # which is the precedence _scale_class applies a few lines above.
        size_scale=(size_scale if size_scale != _SIZE_SCALE_AUTO else character_scale),
        omitted=omitted,
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
            # `gender` is the one control a preset may set: the widget's "Any"
            # is an explicit defer-to-the-preset sentinel, and `execute` reads it
            # back out of the parsed document by name.
            #
            # `hair_color_scope` was copied here too until 0.91.1 and never
            # arrived: `execute` builds `archetype_locked` with `name not in
            # _CONTROL_FIELDS`, which drops it before the engine sees it (measured:
            # an upstream "Full spectrum" left 0/200 seeds with a fantasy shade).
            # It is deliberately NOT wired up. The scope widget has no defer
            # sentinel -- its default "Natural only" is indistinguishable from a
            # deliberate user choice -- and the main node writes the resolved scope
            # into its own prompt_json `_meta`, which is exactly what the vault
            # stores, so honouring it would make every recalled character silently
            # override the user's widget. Adding it back needs an explicit
            # "Auto (preset)" option on the widget first.
            if isinstance(meta.get("gender"), str):
                flat["gender"] = meta["gender"]
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
                # A key disambiguated *by its franchise* already carries it
                # ("Red (Pokemon)", "Zero (Code Geass)"), so appending again
                # stuttered -- "Cosplaying as Red (Pokemon) (Pokemon)". 29 shipped
                # entries did this. Prose-only, no RNG draw, no seed drift.
                named = isinstance(franchise, str) and bool(franchise)
                flat[_COSPLAY_LABEL_KEY] = (
                    f"{cosplay_of} ({franchise})"
                    if named and not _name_already_carries_franchise(cosplay_of, franchise)
                    else cosplay_of
                )
            if meta.get("covers_face"):
                flat[_COVERS_FACE_KEY] = "1"
            # Gated on ``covers_face`` on purpose. The mask describes a HEAD that is
            # hidden; voicing it on a face-visible character renders a helmet over a
            # perfectly good face. merge_preset_documents now drops a stale mask at
            # the source, so this is defence in depth -- but it is the half that also
            # covers a hand-authored document, and the cost is one boolean.
            head = meta.get("mask")
            if meta.get("covers_face") and isinstance(head, str) and head:
                flat[_MASK_KEY] = head
            # Fields a saved document records as deliberately absent (see
            # _format_json). Re-injected as "None" locks so a recalled character keeps
            # its suppressions instead of re-randomizing them. ``setdefault`` never
            # beats a real value: the group loop below overwrites, and group_fields
            # has already stripped "None" from the groups, so there is no collision.
            omitted = meta.get("omitted")
            if isinstance(omitted, list):
                for name in omitted:
                    if isinstance(name, str) and name in FIELD_DEFINITIONS:
                        flat.setdefault(name, "None")
            if meta.get("covers_body"):
                flat[_COVERS_BODY_KEY] = "1"
            if meta.get("covers_hair"):
                flat[_COVERS_HAIR_KEY] = "1"
            tier = meta.get("size_scale")
            if isinstance(tier, str) and tier:
                flat[_SCALE_TIER_KEY] = tier
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
                    raw_list = meta.get(list_key)
                    if isinstance(raw_list, list):
                        species[list_key] = [v for v in raw_list if isinstance(v, str)]
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
                    tooltip="Which outfit wardrobe to draw from -- and how the character "
                            "presents. 'Match gender' keeps outfits typical for the chosen "
                            "gender; 'Feminine' / 'Masculine' force a wardrobe (e.g. a man "
                            "in feminine outfits). 'Any' mixes outfits -- and, when gender "
                            "is also 'Any', unlocks fully mixed-gender features too. On a "
                            "man, 'Feminine' / 'Any' also lift the masculine defaults for "
                            "jewellery, nails and makeup so a full femme look is reachable.",
                ),
                io.Combo.Input(
                    "size_scale",
                    options=[_SIZE_SCALE_AUTO] + list(_SIZE_SCALE_PHRASES),
                    default=_SIZE_SCALE_AUTO,
                    tooltip="Force an unrealistic body scale on an otherwise ordinary "
                            "person -- a doll-sized office worker, a fifty-foot "
                            "commuter.\n"
                            "'Auto' (the default) says nothing about scale and is "
                            "NEVER chosen at random, so this control only ever does "
                            "something when you pick a tier yourself -- it cannot "
                            "affect normal randomized output.\n"
                            "A tier replaces the height description in the opening "
                            "sentence, and overrides a connected Cosplayer's own "
                            "scale, so you can make any character giant or tiny.",
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
                # Per-field help first, then the shared mechanic line. Before 0.78.0
                # every field carried only the mechanic sentence, which explained the
                # widget but never the field itself.
                help_text = FIELD_HELP.get(field_name)
                mechanic = (f"{field_def['group']} · 'Random' = randomize, "
                            f"a value = lock, 'None' = omit from the output.")
                inputs.append(
                    io.Combo.Input(
                        field_name,
                        options=options,
                        default="Random",
                        tooltip=f"{help_text}\n{mechanic}" if help_text else mechanic,
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
            mask_text = archetype.pop(_MASK_KEY, None)
            covers_body = bool(archetype.pop(_COVERS_BODY_KEY, None))
            covers_hair = bool(archetype.pop(_COVERS_HAIR_KEY, None))
            character_scale = archetype.pop(_SCALE_TIER_KEY, "") or ""
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

            # Which locks are the USER's own widget choices, as opposed to the wired
            # character's authored look. `locked` above deliberately merges the two, but
            # the concealment blocks need to tell them apart: a mask must hide a
            # cosplayer's signature hair while still obeying a user who deliberately
            # moved the hair_color widget. See _CONCEALED_FACE_GROUPS. Read straight
            # from kwargs, so a `set_all_fields` reset (which writes "None" into fields
            # the user never touched) correctly does not count as a widget lock.
            widget_locked = frozenset(
                name for name in FIELD_DEFINITIONS
                if name not in _HIDDEN_FIELDS
                and name not in _CONTROL_FIELDS
                and kwargs.get(name, "Random") != "Random"
            )

            prose, json_output = generate_character(
                seed, gender, locked, hair_color_scope, wardrobe,
                accessory_density, location_setting, cosplay_label, covers_face,
                covers_body, covers_hair, modifiers, species, gender_variants,
                kwargs.get("size_scale", _SIZE_SCALE_AUTO),
                character_scale,
                widget_locked=widget_locked,
                mask_text=mask_text,
            )
            return io.NodeOutput(prose, json_output)
