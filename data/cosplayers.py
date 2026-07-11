"""Cosplayer dataset for IdentityForge — fictional characters as a *worn look*.

Each entry describes a character the way a **cosplayer** wears them: the costume
(and any signature non-human features rendered as body paint / prosthetics /
headpieces) is captured as text, while the person underneath is free to
randomize. This is what lets the Cosplayer node put "2B's outfit" on an
ever-changing — and optionally cross-gender — person.

Schema per entry (keyed by character name)::

    "2B": {
        "franchise": "NieR: Automata",   # shown in the cosplay label
        "gender":    "Female",            # SOURCE character gender — for Random scoping only
        "covers_face": True,              # OPTIONAL — full mask/helmet: drop the randomized
                                          #   face/hair/makeup so only the costume shows
        "mask":      "a full face mask ...",# REQUIRED when covers_face — the head covering,
                                          #   kept apart from costume so the node's "Unmask"
                                          #   toggle can drop it and reveal the random head
        "costume":   "a gothic black ...",# → IdentityForge's hidden outfit_description
        "signature": {                    # iconic, field-mappable look — applied in BOTH modes
            "hair_color": "platinum blonde", "hair_length": "chin length bob",
            "hair_style": "blunt bangs",
        },
        "physique":  {                    # body/skin/height — applied ONLY in "Full character" mode
            "body_type": "slender", "height": "average height", "skin_tone": "porcelain",
        },
    }

Curation rules (so the data stays coherent with the engine):

* **Worn, not held.** ``costume`` lists only *worn* items — clothing, footwear,
  gloves, masks/cowls, headwear, hair bows, jewellery, belts, empty holsters,
  body paint, markings, capes. Held / wielded props (swords, staves, bows, guns,
  shields, wands) stay *out* of ``costume``.
* **Signature props (optional, opt-in).** A character with a *truly iconic* held
  prop may carry it in an optional ``"prop"`` key — a free-text phrase that reads
  naturally after "holding …" (e.g. ``"Mjolnir, a short-handled rectangular war
  hammer with a worn leather grip"``). It is emitted only when the Cosplayer node's
  prop toggle is on (off by default), as the hidden ``held_item`` lock. Describe it
  richly and distinctively like a costume — shape, colours, materials, markings —
  not as a bare noun, and keep the same plain-ASCII style. Most characters have no
  signature prop: omit the key entirely rather than inventing one.
* ``costume`` reads naturally after "She/He wears …" (it is voiced verbatim as
  the outfit), so it starts lowercase with an article.
* ``signature`` / ``physique`` keys must be real :data:`data.fields.FIELD_DEFINITIONS`
  fields and every value must be a valid option for that field. Prefer unisex
  fields (hair, eyes, body) so the look survives the downstream gender gate for
  crossplay. ``tests/validate_data.py`` enforces this.
* Non-human characters are included: their non-mappable features (green/blue/
  orange skin, montrals, antennae, wings, scales) live in ``costume`` as worn
  cosplay elements, and ``skin_tone`` is left out so the person underneath
  randomizes.
* **Non-natural skin colour is skin-native (0.52 A/B verdict).** A solid colour is
  worded ``"smooth, flawless <colour> skin"`` — never "body paint"/"dye", which
  live testing showed t2i models render as a streaky coat OVER a human tone.
  Textured surfaces (scaled/craggy/pebbled/rubbery…) use
  ``"uniform, all-over <colour> <material>"`` and keep the texture word;
  markings, tattoos and plating follow as ``"… with <pattern>"``. Fur / feathers /
  flame / ice / hard plating keep the legacy ``"an even, all-over coat of …"``
  wording. All three markers auto-trigger the builder's skin suppression.
* **Full masks/helmets** (Spider-Man, a Mandalorian helmet, a ninja hood) set
  ``"covers_face": True`` so IdentityForge drops the randomized face, hair and
  makeup that would otherwise be described fighting the mask. Omit it whenever
  the face is visible (an open cowl, body-painted-but-visible face, domino mask).
  Every ``covers_face`` entry also puts its head covering in a separate ``mask``
  string (kept *out* of ``costume``): in the default mode the node re-attaches it
  to the costume, but the Cosplayer node's ``Unmask`` toggle drops it and clears
  ``covers_face`` so the randomized head/hair shows under the suit. ``mask`` reads
  naturally as one more worn item appended after the costume (lowercase, with an
  article); face-visible characters have no ``mask``.
* **Plain ASCII only.** Costume text and the character name reach the prompt, so
  avoid em/en dashes, smart quotes and ellipses (use ``-``, ``'``, ``...``);
  some text-to-image tokenizers mangle them.

This is a curated starter set; new characters can be added incrementally — just
follow the schema and keep values valid against ``data/fields.py``.
"""
from __future__ import annotations

#: Character name → cosplay record. See module docstring for the schema.
COSPLAYERS: dict[str, dict] = {
    # --- Anime / JRPG -----------------------------------------------------
    "2B": {
        "franchise": "NieR: Automata",
        "gender": "Female",
        "costume": "a gothic black battle dress with a high thigh slit and white trim, "
                   "a black silk blindfold, thigh-high heeled boots, and white gloves",
        "signature": {"hair_color": "platinum blonde", "hair_length": "chin length bob",
                      "hair_style": "blunt bangs"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "porcelain"},
    },
    "Aerith Gainsborough": {
        "franchise": "Final Fantasy VII",
        "gender": "Female",
        "costume": "a long pink button-up dress with a fitted bodice and short puffed "
                   "sleeves, a red bolero jacket, a pink hair ribbon, brown gloves, and "
                   "brown knee-high laced boots",
        "signature": {"hair_color": "light chestnut", "hair_length": "long",
                      "hair_style": "French braid", "eye_color": "bright green"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
    },
    "Tifa Lockhart": {
        "franchise": "Final Fantasy VII",
        "gender": "Female",
        "costume": "a black sleeveless crop top, a short black miniskirt with suspenders, "
                   "black mid-calf combat boots, brown leather gloves, and a pink arm ribbon",
        "signature": {"hair_color": "dark brown", "hair_length": "waist length",
                      "hair_style": "low ponytail", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
    },
    "Yuffie Kisaragi": {
        "franchise": "Final Fantasy VII",
        "gender": "Female",
        "costume": "a green sleeveless top and shorts ensemble, brown arm guards and leg "
                   "protectors, a green headband, and brown climbing boots",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "petite", "skin_tone": "fair"},
    },
    "Lightning": {
        "franchise": "Final Fantasy XIII",
        "gender": "Female",
        "costume": "a modified Guardian Corps uniform in white and brown with a white "
                   "half-cape, brown leather armor pieces, and tall brown boots",
        "signature": {"hair_color": "rose gold", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Yuna": {
        "franchise": "Final Fantasy X",
        "gender": "Female",
        "costume": "ornate white and blue summoner robes with intricate patterns, white "
                   "boots, prayer beads, and ceremonial ornaments",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "loose braids"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
    },
    "Asuka Langley Soryu": {
        "franchise": "Neon Genesis Evangelion",
        "gender": "Female",
        "costume": "a red plugsuit with white and black accents and technological "
                   "components, with red A10 neural-connector interface headgear",
        "signature": {"hair_color": "copper", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "very petite", "skin_tone": "fair",
                     "age": "18"},
    },
    "Rei Ayanami": {
        "franchise": "Neon Genesis Evangelion",
        "gender": "Female",
        "costume": "a white and blue school uniform with a white short-sleeve shirt, a "
                   "blue skirt, white socks, brown shoes, and a red hair clip",
        "signature": {"hair_color": "electric blue", "hair_length": "chin length bob",
                      "hair_style": "blunt bangs"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "very pale"},
    },
    "Motoko Kusanagi": {
        "franchise": "Ghost in the Shell",
        "gender": "Female",
        "costume": "a high-cut purple leotard with minimal coverage, black gloves past "
                   "the elbows, and black thigh-high boots",
        "signature": {"hair_color": "purple", "hair_length": "chin length bob",
                      "hair_style": "worn down"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Sailor Moon": {
        "franchise": "Sailor Moon",
        "gender": "Female",
        "costume": "a blue-and-white sailor uniform with a white blouse, blue collar, red "
                   "bow, blue pleated miniskirt, white knee-high socks, red shoes, red "
                   "odango hair ribbons, and a crescent moon brooch",
        "signature": {"hair_color": "golden blonde", "hair_length": "hip length",
                      "hair_style": "space buns", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "porcelain"},
    },
    "Hatsune Miku": {
        "franchise": "Vocaloid",
        "gender": "Female",
        "costume": "a silver sleeveless blouse with a turquoise tie, a black pleated "
                   "skirt, detached black sleeves with turquoise trim, thigh-high socks, "
                   "and turquoise-soled loafers",
        "signature": {"hair_color": "teal", "hair_length": "hip length",
                      "hair_style": "pigtails"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "fair", "age": "18"},
    },
    "Android 18": {
        "franchise": "Dragon Ball",
        "gender": "Female",
        "costume": "a blue denim vest over a black-and-white striped long-sleeve shirt, "
                   "blue jeans, brown boots, and gold hoop earrings",
        "signature": {"hair_color": "light blonde", "hair_length": "chin length bob",
                      "hair_style": "blunt bangs", "eye_color": "ice blue",
                      "earrings": "large bold gold hoops"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Bulma": {
        "franchise": "Dragon Ball",
        "gender": "Female",
        "costume": "a casual pink sleeveless top with the word logo, denim shorts, and "
                   "white sneakers, with a red hair band",
        "signature": {"hair_color": "teal", "hair_length": "shoulder length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Hinata Hyuga": {
        "franchise": "Naruto",
        "gender": "Female",
        "costume": "a cream-colored hooded jacket with lavender trim, dark blue pants, "
                   "and blue shinobi sandals",
        "signature": {"hair_color": "navy blue", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "pale"},
    },
    "Sakura Haruno": {
        "franchise": "Naruto",
        "gender": "Female",
        "costume": "a red qipao-style dress with white circular patterns, black shorts "
                   "underneath, blue shinobi sandals, pink elbow guards, and a red "
                   "headband with a metal plate",
        "signature": {"hair_color": "baby pink", "hair_length": "chin length bob",
                      "hair_style": "blunt bangs", "eye_color": "bright green"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
    },
    "Tsunade": {
        "franchise": "Naruto",
        "gender": "Female",
        "costume": "a grey kimono-style top with a deep neckline, dark blue pants, blue "
                   "sandals, and a green haori jacket",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "pigtails", "eye_color": "light brown"},
        "physique": {"body_type": "voluptuous", "height": "short", "skin_tone": "fair"},
    },
    "Nami": {
        "franchise": "One Piece",
        "gender": "Female",
        "costume": "a blue-and-white striped shirt tied to show the midriff, an orange "
                   "mini-skirt, brown high-heeled sandals, and gold bracelets",
        "signature": {"hair_color": "orange", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "warm tan"},
    },
    "Nico Robin": {
        "franchise": "One Piece",
        "gender": "Female",
        "costume": "a purple cowboy hat, a pink midriff-showing shirt, purple chaps over "
                   "dark pants, and black high-heeled boots",
        "signature": {"hair_color": "jet black", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "deep blue"},
        "physique": {"body_type": "hourglass", "height": "very tall", "skin_tone": "olive"},
    },
    "Mikasa Ackerman": {
        "franchise": "Attack on Titan",
        "gender": "Female",
        "costume": "a brown Survey Corps jacket with the Wings of Freedom emblem, an "
                   "omni-directional maneuver gear harness, white pants, brown mid-calf "
                   "boots, and a red scarf",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "dark gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
    },

    # --- Fighting games ---------------------------------------------------
    "Chun-Li": {
        "franchise": "Street Fighter",
        "gender": "Female",
        "costume": "a blue qipao dress with gold trim and puffed short sleeves modified "
                   "for combat, brown tights, white cross-laced combat boots with blue "
                   "accents, and spiked bracelets",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_style": "space buns", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
    },
    "Cammy White": {
        "franchise": "Street Fighter",
        "gender": "Female",
        "costume": "a green high-cut leotard with long sleeves and red accents, a red "
                   "beret, red mid-calf combat boots, brown gloves, brown leg warmers, "
                   "and red camo face paint",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_style": "loose braids", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Mai Shiranui": {
        "franchise": "The King of Fighters",
        "gender": "Female",
        "costume": "a revealing red kunoichi outfit tied behind the neck, very short "
                   "shorts, red leg warmers, white tabi socks, and red ninja shoes",
        "signature": {"hair_color": "warm brown", "hair_length": "waist length",
                      "hair_style": "high ponytail", "eye_color": "medium brown"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "fair"},
        "prop": "a pair of folding paper fans painted with red flowers, one open "
                "in each hand",
    },
    "Kitana": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a blue form-fitting leotard with thigh-high boots, matching long "
                   "gloves, and a blue face mask covering the mouth and nose",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
        "prop": "a pair of bladed steel war fans, fanned open to bare their razor "
                "edges, one in each hand",
    },
    "Skarlet": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a form-fitting red leather bodysuit with strategic cutouts, a red "
                   "hooded cloak, a blood-red face mask, crimson arm guards, and black "
                   "boots with red accents",
        "eyes": "glowing red",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "loose braids"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "pale"},
    },

    # --- Overwatch --------------------------------------------------------
    "D.Va": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a blue and pink bodysuit with technological elements, white and pink "
                   "gloves and boots, pink-accented headphones, and a bunny logo, with "
                   "pink hair highlights",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "fair",
                     "ethnicity": "Korean"},
    },
    "Tracer": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a bright orange and blue bodysuit with technological components, "
                   "orange goggles, white and orange gloves, orange boots, and a chest "
                   "chronal accelerator device",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
    },
    "Mercy": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a white and gold Valkyrie suit with medical cross symbols, white "
                   "boots, and mechanical halo wings",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
        "prop": "the Caduceus staff, a slender golden rod topped with a glowing "
                "winged medical emblem",
    },
    "Widowmaker": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a form-fitting dark purple bodysuit with technological enhancements, a high "
                   "collar, integrated armor, a visor, stealth boots, and smooth, flawless "
                   "blue-violet skin",
        "eyes": "glowing yellow",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "low ponytail"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Pharah": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "blue and gold Raptora combat armor with wing-like jets, a bird-like "
                   "visor helmet, and an Eye of Horus tattoo under the right eye",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "warm brown",
                     "ethnicity": "Egyptian"},
    },

    # --- League of Legends / Arcane --------------------------------------
    "Ahri": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a white and blue Korean-inspired dress with gold accents, blue "
                   "thigh-high stockings, blue boots, a fox-ear headband, and nine "
                   "white-tipped fox tails",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Jinx": {
        "franchise": "Arcane",
        "gender": "Female",
        "costume": "a purple crop top, blue shorts, pink-and-blue striped stockings, "
                   "purple boots, and blue arm tattoos in a punk-anarchist style",
        "eyes": "glowing pink",
        "signature": {"hair_color": "electric blue", "hair_length": "hip length",
                      "hair_style": "loose braids"},
        "physique": {"body_type": "very slim", "height": "short", "skin_tone": "pale"},
    },

    # --- Star Wars --------------------------------------------------------
    "Ahsoka Tano": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a practical grey-and-blue tunic with leggings and armored pieces, a "
                   "blue-and-white striped montral-and-lekku headpiece, and smooth, flawless "
                   "orange skin with white Togruta facial markings",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a pair of ignited lightsabers, a long white energy blade in one "
                "hand and a shorter white shoto blade in the other",
    },
    "Princess Leia Organa": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a floor-length long-sleeved white gown with a high collar and a "
                   "silver belt",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "space buns", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "fair"},
    },
    "Padme Amidala": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "the white Geonosis battle outfit with a form-fitting white top, "
                   "white pants, a utility belt, and beige boots",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_style": "updo", "eye_color": "warm hazel"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Padme Amidala (Regal Outfit)": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "an opulent floor-length Naboo throne-room gown of deep crimson "
                   "and gold brocade with enormous flared sleeves, ceremonial chalk-white "
                   "face paint with a red lower-lip mark and red dots on each cheek, and a "
                   "towering golden fan-shaped headdress with hanging gold ornaments",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_style": "updo", "eye_color": "warm hazel"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Rey": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "practical wrapped gray-and-brown fabric clothing strips, arm guards, "
                   "and sturdy boots",
        "signature": {"hair_color": "warm brown", "hair_length": "shoulder length",
                      "hair_style": "space buns", "eye_color": "warm hazel"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "warm tan"},
        "prop": "a long worn quarterstaff of weathered metal and wrapped leather",
    },

    # --- Nintendo / Zelda -------------------------------------------------
    "Zelda": {
        "franchise": "The Legend of Zelda: Breath of the Wild",
        "gender": "Female",
        "costume": "a blue ceremonial dress with intricate gold embroidery, a white "
                   "underdress, a brown corset-style belt, brown boots, and a blue cape",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "loose braids", "eye_color": "bright green"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
    },
    "Princess Peach": {
        "franchise": "Super Mario",
        "gender": "Female",
        "costume": "an elegant pink ballgown with puffy sleeves, a jeweled bodice, a full "
                   "floor-length skirt, white gloves past the elbows, a jeweled crown, "
                   "and pink high heels",
        "signature": {"hair_color": "golden blonde", "hair_length": "waist length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Zero Suit Samus": {
        "franchise": "Metroid",
        "gender": "Female",
        "costume": "a blue form-fitting Zero Suit bodysuit with orange accents and "
                   "technological components, and blue boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },

    # --- Resident Evil / Tomb Raider / survival --------------------------
    "Ada Wong": {
        "franchise": "Resident Evil",
        "gender": "Female",
        "costume": "a fitted red qipao dress with a high collar and side slits, black "
                   "stockings, and black high heels",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair",
                     "ethnicity": "Chinese"},
    },
    "Jill Valentine": {
        "franchise": "Resident Evil",
        "gender": "Female",
        "costume": "a blue tube top showing a toned midriff, a white miniskirt, brown "
                   "mid-calf combat boots, a black tactical vest, and brown gloves",
        "signature": {"hair_color": "dark brown", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Claire Redfield": {
        "franchise": "Resident Evil",
        "gender": "Female",
        "costume": "a distinctive red leather vest with an angel design over a black top, "
                   "blue jeans, and sturdy boots",
        "signature": {"hair_color": "auburn", "hair_length": "slightly past shoulders",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Lara Croft": {
        "franchise": "Tomb Raider",
        "gender": "Female",
        "costume": "a fitted brown tank top revealing a toned midriff, khaki cargo "
                   "shorts, brown mid-calf combat boots, a utility belt, fingerless "
                   "gloves, and knee pads",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "warm tan"},
        "prop": "a pair of matte-black semi-automatic pistols, one in each hand",
    },
    "Aloy": {
        "franchise": "Horizon",
        "gender": "Female",
        "costume": "layered leather and techno-tribal armor of scavenged machine plating "
                   "in earthy tones with blue and red accents, Nora tribal face paint, "
                   "and a glowing blue Focus device at the temple",
        "signature": {"hair_color": "copper", "hair_length": "long",
                      "hair_style": "dutch braids", "eye_color": "bright green",
                      "freckles_density": "scattered"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a drawn wood-and-sinew tribal hunting bow, an arrow nocked",
    },

    # --- Avatar: The Last Airbender / Korra ------------------------------
    "Azula": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Female",
        "costume": "a fitted sleeveless red-and-black Fire Nation outfit with gold trim, "
                   "matching pants, black boots, golden arm guards, and a red cape",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "top knot", "eye_color": "amber"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Katara": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Female",
        "costume": "a blue tunic with white trim and Water Tribe designs, blue pants, "
                   "brown boots, blue arm guards, and a white undershirt",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_texture": "silky and glossy",
                      "hair_style": "loose braids", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "olive"},
    },
    "Toph Beifong": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Female",
        "costume": "a simple green tunic with Earth Kingdom designs, beige pants, a "
                   "yellow arm guard, and bare feet",
        "signature": {"hair_color": "jet black", "hair_length": "jaw length",
                      "hair_style": "messy bun", "eye_color": "bright green"},
        "physique": {"body_type": "stocky", "height": "petite", "skin_tone": "warm tan"},
    },
    "Ty Lee": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Female",
        "costume": "a pink sleeveless midriff-exposing top, matching pink shorts, pink "
                   "leg warmers, arm bands, and simple sandals",
        "signature": {"hair_color": "warm brown", "hair_length": "waist length",
                      "hair_style": "low ponytail", "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "warm tan"},
    },
    "Korra": {
        "franchise": "The Legend of Korra",
        "gender": "Female",
        "costume": "a light blue sleeveless asymmetrical Water Tribe tunic, dark blue "
                   "baggy pants tucked into fur-trimmed brown boots, and dark blue "
                   "armbands",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "high ponytail"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "warm brown"},
    },

    # --- DC ---------------------------------------------------------------
    "Wonder Woman": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "an iconic red bustier with a golden eagle chest emblem, blue "
                   "star-spangled briefs, red mid-calf boots, golden forearm bracers, "
                   "and a golden tiara with a red star",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "statuesque", "skin_tone": "warm tan"},
        "prop": "the Lasso of Truth, a coil of glowing golden rope at the hip",
    },
    "Harley Quinn": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a tight white crop top, very short tattered "
                   "red-and-blue sequined shorts over ripped fishnet stockings, a black "
                   "studded choker, fingerless gloves and studded accessories, with a "
                   "pale powdered whitish face and high blonde pigtails dip-dyed pink at "
                   "the tips on one side and blue on the other",
        "signature": {"hair_color": "platinum blonde", "hair_length": "shoulder length",
                      "hair_style": "pigtails", "eye_color": "bright blue",
                      "makeup_style": "club makeup", "eye_makeup": "colorful bold eyeshadow",
                      "eyeliner": "dramatic winged", "lashes": "dramatic falsies",
                      "lips_makeup": "deep red", "expression": "wide toothy grin"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a wooden baseball bat covered in colorful spray-painted graffiti, "
                "resting on one shoulder",
    },
    "Harley Quinn (Classic Jester)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a red-and-black harlequin jester catsuit split down the middle, a "
                   "white ruffled collar, a two-pointed red-and-black jester hood with "
                   "small bells framing the face, a black domino eye mask, a chalk-white "
                   "painted face with a wide red-lipped grin, white gloves, and pointed "
                   "jester boots",
        "signature": {"lips_makeup": "classic red", "expression": "wide toothy grin"},
        "covers_hair": True,  # two-pointed jester hood fully encloses the scalp; face shows
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "an oversized cartoonish wooden mallet with a rounded head, slung over "
                "one shoulder",
    },
    "Deadshot": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red-and-grey tactical combat suit with body armor, arm gauntlets, "
                   "and a targeting monocle over the right eye",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "brown"},
        "prop": "a long-barreled sniper rifle held ready at the shoulder",
    },
    "Peacemaker": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a white-and-silver armored bodysuit with red trim and a polished "
                   "chrome dove-of-peace helmet",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a pair of large silver pistols, one in each hand",
    },
    "Captain Boomerang": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a blue-and-white costume with a boomerang-laden bandolier and "
                   "harness over a long coat",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "fair"},
        "prop": "a razor-edged metal boomerang held in each hand",
    },
    "Bloodsport": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black-and-silver high-tech armored combat suit with weaponized "
                   "gauntlets and a sleek open-face helmet",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
        "prop": "a modular rifle assembled from his gauntlet, leveled forward",
    },
    "Rick Flag": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "military tactical gear with a black load-bearing vest, fatigues, and "
                   "a holstered sidearm",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "an assault rifle held across the chest",
    },
    "King Shark": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "covers_face": True,
        "costume": "only torn cargo shorts, with uniform, all-over grey-and-white shark skin and "
                   "a dorsal fin down the back, on an enormously tall hulking figure of immense proportions",
        "mask": "a massive great-white shark head with rows of jagged teeth and small "
                "solid black eyes",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Polka-Dot Man": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a grey bodysuit and snug helmet covered in rows of bright "
                   "multicolored polka dots, with dot-projecting wrist devices",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "pale blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "pale"},
    },
    "Ratcatcher 2": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a worn brown hooded trench coat over layered scavenged clothing, "
                   "with round tinted goggles pushed up on the forehead",
        "signature": {"hair_color": "near black", "hair_length": "mid back",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "tan"},
        "prop": "a small brown pet rat perched on one shoulder",
    },
    "Despero": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "covers_face": True,
        "costume": "a minimal warrior harness with gold trim, over smooth, flawless pink-red "
                   "alien skin, on a towering figure of overwhelming size and proportion",
        "mask": "a pink-red alien face with a large third eye set in the forehead, a "
                "tall white finned crest over the head, and glowing red eyes",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Starro": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a full-body giant blue-and-purple starfish costume with five thick "
                   "textured arms and bumpy ridged skin",
        "mask": "a starfish head-piece dominated by a single huge central eye",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Starro Spore": {
        "franchise": "DC",
        "gender": "Female",
        "covers_face": True,
        "costume": "ordinary everyday streetwear, the body standing rigid and slack "
                   "under mind control",
        "mask": "a small blue-and-white Starro spore clamped over the face, with a "
                "single central eye and probing tendrils",
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Poison Ivy": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting bodysuit of overlapping leaves and vines, smooth, flawless "
                   "vivid green skin from head to toe including the face, with bold red lips "
                   "and tiny leaves entwined in the hair",
        "signature": {"hair_color": "bright red", "hair_length": "waist length",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "voluptuous", "height": "tall"},
    },
    "Catwoman": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a tight black leather catsuit with a pointed cat-eared cowl, a "
                   "utility belt, and black thigh-high heeled boots",
        "signature": {"hair_color": "near black", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "olive"},
    },
    "Zatanna Zatara": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black tuxedo tailcoat, a white dress shirt with a black bow tie, a "
                   "red vest, fishnet stockings, black high-heeled shoes, and a black top "
                   "hat",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "fair"},
    },
    "Batgirl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting dark purple-and-black batsuit with a yellow bat symbol "
                   "on the chest, a yellow utility belt, a pointed bat-eared cowl, and a "
                   "scalloped cape",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Starfire": {
        "franchise": "DC (Teen Titans)",
        "gender": "Female",
        "costume": "a purple crop top, a purple miniskirt, purple thigh-high boots, silver arm "
                   "guards, and smooth, flawless warm golden-orange skin",
        "eyes": "solid glowing green",
        "signature": {"hair_color": "bright red", "hair_length": "hip length",
                      "hair_style": "worn down"},
        "physique": {"body_type": "curvy", "height": "very tall"},
    },
    "Raven": {
        "franchise": "DC (Teen Titans)",
        "gender": "Female",
        "costume": "a dark blue hooded cloak over a blue bodysuit with a mystical symbol "
                   "belt, and dark blue boots",
        "eyes": "violet",
        "signature": {"hair_color": "deep purple", "hair_length": "chin length bob",
                      "hair_style": "blunt bangs"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "very pale"},
    },

    # --- Marvel -----------------------------------------------------------
    "Black Widow": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting black tactical bodysuit with subtle armor plating, a "
                   "red hourglass belt emblem, and black combat boots",
        "signature": {"hair_color": "deep red", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "porcelain"},
    },
    "Scarlet Witch": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a red corset and a flowing red cape over dark pants, with fingerless "
                   "gloves and a red headpiece",
        "signature": {"hair_color": "auburn", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Mystique": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "nothing but uniform, all-over dark blue scaled skin with natural scale "
                   "coverage",
        "eyes": "solid yellow",
        "signature": {"hair_color": "bright red", "hair_length": "shoulder length",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Storm": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting black leather bodysuit with silver accents and "
                   "lightning-bolt patterns, a dramatic flowing cape, and black boots "
                   "and gloves",
        "signature": {"hair_color": "white", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
    },

    # --- Disney / animation ----------------------------------------------
    "Ariel": {
        "franchise": "The Little Mermaid",
        "gender": "Female",
        "costume": "a purple seashell bikini top with small pearls and a shimmering "
                   "green mermaid tail",
        "signature": {"hair_color": "bright red", "hair_length": "waist length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
    },
    "Elsa": {
        "franchise": "Frozen",
        "gender": "Female",
        "costume": "an elegant ice-blue gown with long sleeves, a fitted bodice with "
                   "snowflake patterns, a flowing shimmering skirt, and blue high heels",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very long",
                      "hair_style": "side braid", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "pale"},
    },
    "Anna": {
        "franchise": "Frozen",
        "gender": "Female",
        "costume": "a teal dress with black trim and floral embroidery, puffy sleeves, a "
                   "full skirt, a magenta cape, and brown boots",
        "signature": {"hair_color": "auburn", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "bright blue",
                      "freckles_density": "few"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
    },
    "Belle": {
        "franchise": "Beauty and the Beast",
        "gender": "Female",
        "costume": "a simple blue dress with a white apron, brown flat shoes, and a blue "
                   "hair ribbon",
        "signature": {"hair_color": "chestnut", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Aurora": {
        "franchise": "Sleeping Beauty",
        "gender": "Female",
        "costume": "a blue gown with a fitted bodice and a flowing floor-length skirt, a "
                   "simple gold tiara, and delicate slippers",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "deep blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Cinderella": {
        "franchise": "Cinderella",
        "gender": "Female",
        "costume": "a shimmering blue ballgown with off-shoulder sleeves and a fitted "
                   "bodice, a full floor-length skirt, long white gloves, and glass "
                   "slippers",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "updo", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Snow White": {
        "franchise": "Snow White",
        "gender": "Female",
        "costume": "a blue bodice with puffy yellow sleeves, a yellow ankle-length "
                   "skirt, a red cape, a white collar and cuffs, and brown shoes",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "silky and glossy",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "porcelain"},
    },
    "Jasmine": {
        "franchise": "Aladdin",
        "gender": "Female",
        "costume": "a blue midriff-baring crop top, flowing blue ankle-gathered pants, "
                   "gold jewelry on the arms and neck, a jeweled headband, and gold "
                   "slippers",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "silky and glossy",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "warm tan"},
    },
    "Mulan": {
        "franchise": "Mulan",
        "gender": "Female",
        "costume": "a traditional Chinese red wrap-style top with gold trim, matching "
                   "red pants, black boots, a red waist sash, and subtle armor pieces",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "silky and glossy",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "warm tan",
                     "ethnicity": "Chinese"},
    },
    "Moana": {
        "franchise": "Moana",
        "gender": "Female",
        "costume": "a red bandeau top with traditional patterns, a cream grass skirt "
                   "reaching the knees, shell and bead jewelry, tropical flowers in the "
                   "hair, and bare feet",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "warm tan"},
    },
    "Rapunzel": {
        "franchise": "Tangled",
        "gender": "Female",
        "costume": "a purple dress with pink laces and white puffy sleeves, an "
                   "ankle-length skirt, and brown boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "hip length",
                      "hair_style": "crown braid", "eye_color": "bright green"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "fair"},
    },
    "Tiana": {
        "franchise": "The Princess and the Frog",
        "gender": "Female",
        "costume": "a green ballgown with golden accents and lily-pad designs, "
                   "off-shoulder sleeves, and a full skirt",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_style": "French twist", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "warm brown"},
    },
    "Merida": {
        "franchise": "Brave",
        "gender": "Female",
        "costume": "a dark teal dress with Celtic designs, and a brown leather quiver and "
                   "belt",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_texture": "curly", "eye_color": "bright blue",
                      "freckles_density": "moderate"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
        "prop": "a drawn wooden longbow worn smooth with use, an arrow nocked",
    },
    "Pocahontas": {
        "franchise": "Pocahontas",
        "gender": "Female",
        "costume": "a tan fringed buckskin dress reaching mid-thigh with geometric "
                   "patterns, a turquoise necklace, and brown moccasins",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "silky and glossy",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "bronze"},
    },
    "Jessica Rabbit": {
        "franchise": "Who Framed Roger Rabbit",
        "gender": "Female",
        "costume": "a strapless form-fitting red sequined gown with a high side slit, "
                   "long purple gloves past the elbows, and red high heels",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "porcelain"},
    },

    # --- Live-action / literary ------------------------------------------
    "Hermione Granger": {
        "franchise": "Harry Potter",
        "gender": "Female",
        "costume": "a Hogwarts uniform with a white shirt, grey sweater vest, black robes "
                   "with Gryffindor colors, a red-and-gold striped tie, a black skirt, "
                   "white knee-high socks, and black school shoes",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "thick and voluminous", "eye_color": "warm hazel"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Katniss Everdeen": {
        "franchise": "The Hunger Games",
        "gender": "Female",
        "costume": "a practical dark brown leather jacket, black pants, sturdy brown "
                   "boots, and a mockingjay pin on the jacket",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "side braid", "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "olive"},
        "prop": "a drawn recurve bow of black-and-silver composite limbs, an "
                "arrow nocked",
    },
    "Daenerys Targaryen": {
        "franchise": "Game of Thrones",
        "gender": "Female",
        "costume": "a flowing blue-grey gown with dragon-scale motifs and metallic "
                   "elements",
        "eyes": "violet",
        "signature": {"hair_color": "platinum white", "hair_length": "waist length",
                      "hair_style": "dutch braids"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "fair"},
    },
    "Xena": {
        "franchise": "Xena: Warrior Princess",
        "gender": "Female",
        "costume": "a brown tooled-leather armored corset with bronze accents, a short "
                   "segmented leather skirt, matching shoulder pauldrons, leather "
                   "armbands, and knee-high leather boots",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "curtain bangs", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "the chakram, a round flat steel throwing disc edged with a blade "
                "and etched in gold",
    },
    "Yennefer of Vengerberg": {
        "franchise": "The Witcher",
        "gender": "Female",
        "costume": "a high-collared black-and-white blouse with intricate lace details "
                   "and elegant trousers, with a black obsidian star pendant on a black "
                   "velvet choker",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "violet-gray"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "very pale"},
    },
    "Morticia Addams": {
        "franchise": "The Addams Family",
        "gender": "Female",
        "costume": "a form-fitting floor-length black gown with trailing sleeves and a "
                   "subtle cobweb motif",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "silky and glossy", "eye_color": "dark brown"},
        "physique": {"body_type": "hourglass", "height": "statuesque", "skin_tone": "porcelain"},
    },
    "Wednesday Addams": {
        "franchise": "The Addams Family",
        "gender": "Female",
        "costume": "a simple black dress with a white collar and cuffs, black stockings, "
                   "and black shoes",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "silky and glossy",
                      "hair_style": "pigtails", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "very pale"},
    },

    # --- More Marvel ------------------------------------------------------
    "She-Hulk": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a purple-and-white athletic leotard, with smooth, flawless rich green skin "
                   "covering her face and entire body, on an enormously tall figure of immense towering proportions",
        "signature": {"hair_color": "emerald green", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely wavy", "eye_color": "emerald"},
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Captain Marvel": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a red, blue, and gold Kree flight suit with a gold eight-pointed "
                   "starburst chest emblem, red gloves, and red boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Captain Carter": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a navy Union Jack-emblazoned super-soldier suit with red and white "
                   "contour lines, brown tactical boots, and brown gloves",
        "signature": {"hair_color": "chestnut", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "statuesque", "skin_tone": "fair"},
        "prop": "a round shield emblazoned with the red, white, and blue Union "
                "Jack, the crossed-bar flag framed by a polished metal rim",
    },
    "Jean Grey": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a green and gold Phoenix costume with a bird-emblem sash and gold "
                   "boots",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Rogue": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting yellow and green bodysuit, a brown leather jacket, "
                   "gloves covering all skin, and white face-framing hair streaks",
        "signature": {"hair_color": "dark brown", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "fair"},
    },
    "Psylocke": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting purple bodysuit covering neck to toe with "
                   "Japanese-inspired designs, a utility belt, purple boots, and arm "
                   "guards",
        "signature": {"hair_color": "purple", "hair_length": "long", "hair_style": "worn down"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "olive"},
        "prop": "a glowing pink psychic energy katana projected from one fist",
    },
    "Gamora": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "tactical dark leather armor in black and deep teal with a long coat, fitted "
                   "pants, boots, smooth, flawless green skin, and magenta hair tips",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Nebula": {
        "bald": True,
        "covers_body": True,  # fully armoured cybernetic combat suit, no bare skin
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a fitted dark combat suit with armored segments, boots, gauntlets, smooth, "
                   "flawless blue metallic skin with intricate plating, and purple biomechanical "
                   "lines over a shaved head",
        "signature": {},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Spider-Gwen": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a white and pink spider suit with a black spider chest emblem, a "
                   "white hood, pink and blue accents, and white boots with pink soles",
        "signature": {"hair_color": "light blonde", "hair_length": "jaw length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
    },
    "Wasp": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting yellow and black insect-themed costume with functional "
                   "wings, matching boots, and an antennae headpiece, on a figure shrunk to impossibly "
                   "tiny miniature proportions",
        "signature": {"hair_color": "warm brown", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "size_scale": "tiny",
        "physique": {"body_type": "petite and slim", "height": "short", "skin_tone": "fair"},
    },
    "Elektra": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a scarlet wrap-style costume with asymmetric bands across the torso "
                   "and hips, matching red arm and leg wraps, and a crimson headband",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "olive",
                     "ethnicity": "Greek"},
        "prop": "a pair of steel three-pronged sai, one spun in each hand",
    },
    "Invisible Woman": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a blue Fantastic Four uniform with a '4' chest emblem, and matching "
                   "blue gloves and boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },

    # --- More DC ----------------------------------------------------------
    "Supergirl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a blue crop top with the Superman S-shield, a red miniskirt, a red "
                   "cape, and red mid-thigh boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Power Girl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a white bodysuit with a circular chest cutout, a blue cape, blue "
                   "gloves and boots, and a red belt",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "fair"},
    },
    "Batwoman": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a fitted black bodysuit with a bold red bat symbol across the chest, "
                   "a long black cape lined bright red, red gloves, a red utility belt, "
                   "red boots, and a sleek black mask",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Black Canary": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black leather jacket over a black bodysuit, fishnet stockings, "
                   "black combat boots, and a blue domino mask",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Hawkgirl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a gold-and-green Egyptian-inspired costume, a winged hawk helmet, and "
                   "large feathered wings",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "loose braids", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "golden tan"},
    },
    "Vampirella": {
        "franchise": "Vampirella",
        "gender": "Female",
        "costume": "an iconic red sling-style costume with white trim joined by a "
                   "circular clasp, white boots, and a red cape with bat-wing accents",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "voluptuous", "height": "tall", "skin_tone": "porcelain"},
    },

    # --- More Star Wars ---------------------------------------------------
    "Hera Syndulla": {
        "bald": True,
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a practical brown and orange flight suit with a utility belt, brown boots, "
                   "smooth, flawless green Twi'lek skin, and two long head-tails (lekku)",
        "signature": {"eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height"},
    },
    "Mara Jade": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a fitted dark gray bodysuit, a utility belt with pouches, dark "
                   "gloves, dark boots, and a dark cloak",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "low ponytail"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "an ignited lightsaber with a glowing magenta-purple blade",
    },

    # --- More Disney / animation -----------------------------------------
    "Tinker Bell": {
        "franchise": "Peter Pan",
        "gender": "Female",
        "costume": "a strapless green leaf dress, tiny green slippers, translucent "
                   "iridescent fairy wings, and a dusting of pixie dust, on a fairy-sized figure of "
                   "miniature proportions",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "messy bun", "eye_color": "bright blue"},
        "size_scale": "tiny",
        "physique": {"body_type": "petite and slim", "height": "very petite",
                     "skin_tone": "golden tan"},
    },
    "Alice": {
        "franchise": "Alice in Wonderland",
        "gender": "Female",
        "costume": "a blue dress with a white pinafore apron, white stockings, black "
                   "Mary Jane shoes, and a black hair-bow headband",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "porcelain"},
    },
    "Maleficent": {
        "franchise": "Sleeping Beauty",
        "gender": "Female",
        "costume": "a long flowing black robe with a high collar, wide sleeves, and "
                   "purple lining, a dramatic black horned headdress, and pale green "
                   "skin",
        "signature": {},
        "physique": {"body_type": "slender", "height": "tall"},
        "prop": "a tall slender black staff topped with a glowing green orb",
    },
    "Ursula": {
        "franchise": "The Little Mermaid",
        "gender": "Female",
        "costume": "a black strapless dress, golden shell earrings, a nautilus necklace, a white "
                   "bouffant wig, smooth, flawless purple-gray skin, and eight large purple "
                   "octopus tentacles",
        "signature": {},
        "physique": {"body_type": "voluptuous", "height": "statuesque"},
    },
    "Cruella de Vil": {
        "franchise": "101 Dalmatians",
        "gender": "Female",
        "costume": "an elaborate floor-length black fur coat with white trim, a "
                   "high-fashion black-and-white outfit, long black gloves, dramatic "
                   "jewelry, extremely high heels, and dramatically split black-and-"
                   "white hair",
        "signature": {"eye_color": "green"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "pale"},
    },
    "Marceline the Vampire Queen": {
        "franchise": "Adventure Time",
        "gender": "Female",
        "costume": "a grey tank top, ripped jeans, sturdy boots, and smooth, flawless pale "
                   "greyish-blue skin with two small neck bite marks",
        "signature": {"hair_color": "jet black", "hair_length": "hip length",
                      "hair_style": "worn down"},
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Daphne Blake": {
        "franchise": "Scooby-Doo",
        "gender": "Female",
        "costume": "a purple dress with long sleeves and a short skirt, a pink neck "
                   "scarf, and purple heeled shoes",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Velma Dinkley": {
        "franchise": "Scooby-Doo",
        "gender": "Female",
        "costume": "an orange turtleneck sweater, a red pleated skirt, orange knee-high "
                   "socks, brown oxford shoes, and thick orange-framed glasses",
        "signature": {"hair_color": "auburn", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "medium brown"},
        "physique": {"body_type": "softly curved", "height": "short", "skin_tone": "fair"},
    },
    "Elvira": {
        "franchise": "Mistress of the Dark",
        "gender": "Female",
        "costume": "a skintight black gown with a plunging neckline and a thigh-high "
                   "slit, a dagger-shaped belt, and stiletto heels",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "hair_texture": "thick and voluminous", "eye_color": "dark brown"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "porcelain"},
    },

    # --- More games -------------------------------------------------------
    "Ciri": {
        "franchise": "The Witcher",
        "gender": "Female",
        "costume": "a loose cream linen V-neck shirt, a brown leather corset, dark tight "
                   "trousers, sturdy leather boots, fingerless gloves, and a pale scar "
                   "over the left eye",
        "signature": {"hair_color": "dirty blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "low ponytail", "eye_color": "emerald"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Triss Merigold": {
        "franchise": "The Witcher",
        "gender": "Female",
        "costume": "an elegant dress in deep blue and autumnal tones with a plunging "
                   "neckline and floral embroidery, an amulet, and leather boots",
        "signature": {"hair_color": "auburn", "hair_length": "long",
                      "hair_texture": "loosely curled", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Mei": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a bulky padded blue-and-white winter outfit with fur trim, heavy "
                   "boots, round glasses, and a large hairpin",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_style": "messy bun", "eye_color": "dark brown"},
        "physique": {"body_type": "softly curved", "height": "short", "skin_tone": "fair",
                     "ethnicity": "Chinese"},
    },
    "Bayonetta": {
        "franchise": "Bayonetta",
        "gender": "Female",
        "costume": "a skin-tight black bodysuit embroidered with arcane sigils, chic "
                   "angular glasses, gunmetal gloves, and black heeled boots",
        "signature": {"hair_color": "raven black", "hair_length": "hip length",
                      "hair_style": "updo", "eye_color": "blue-gray"},
        "physique": {"body_type": "slender", "height": "very tall", "skin_tone": "fair"},
    },
    "Morrigan Aensland": {
        "franchise": "Darkstalkers",
        "gender": "Female",
        "costume": "a black bat-themed leotard with a heart-shaped chest cutout, sheer "
                   "purple tights with bat silhouettes, and bat wings from the back and "
                   "the sides of the head",
        "signature": {"hair_color": "emerald green", "hair_length": "long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "voluptuous", "height": "tall", "skin_tone": "fair"},
    },
    "Chell": {
        "franchise": "Portal",
        "gender": "Female",
        "costume": "an orange Aperture Science jumpsuit tied at the waist over a white "
                   "tank top, with white-and-orange long-fall heel boots",
        "signature": {"hair_color": "dark brown", "hair_length": "slightly past shoulders",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
    },

    # --- Additional Marvel / DC women -------------------------------------
    "Black Cat": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a sleek black catsuit with a white fur collar and cuffs, a black "
                   "domino mask, and black gloves and boots",
        "signature": {"hair_color": "platinum blonde", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "fair"},
    },
    "X-23": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "tight black and gray combat gear, fingerless gloves, reinforced "
                   "boots, and metal claws extending from the knuckles of each hand",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_texture": "sleek straight", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "very petite", "skin_tone": "tan"},
    },
    "Emma Frost": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a white form-fitting bodysuit with a white cape, white gloves, and "
                   "white thigh-high boots",
        "signature": {"hair_color": "platinum blonde", "hair_length": "slightly past shoulders",
                      "hair_texture": "wavy", "eye_color": "ice blue"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "porcelain"},
    },
    "Jubilee": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a bright yellow trench coat over a casual outfit, yellow gloves, pink "
                   "sunglasses, sneakers, and yellow-streaked hair",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "light medium"},
    },
    "Ms. Marvel (Kamala Khan)": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a blue tunic-style costume with a gold lightning-bolt emblem, a long red "
                   "scarf trailing from the neck, a small blue domino mask, red gloves, blue "
                   "leggings, and blue boots",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "petite", "skin_tone": "caramel"},
    },
    "Spider-Woman": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a red and yellow bodysuit with a black spider-web pattern across the "
                   "chest and arms, red gloves, and red boots",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "olive"},
    },
    "Hela": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a sleek form-fitting black and deep green bodysuit with swirling "
                   "patterns, a dark flowing cape, and a black antler-like headdress",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "slicked back", "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
    },
    "Domino": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black leather bodysuit with minimal white accents, black boots, and "
                   "black gloves, with a black circular marking painted around the left eye",
        "signature": {"hair_color": "jet black", "hair_length": "ear length",
                      "hair_style": "worn down", "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "very pale"},
    },
    "Dazzler": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a silver disco outfit with a metallic halter top and shorts, silver "
                   "gloves, and silver roller skates",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Polaris": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting green bodysuit with metallic accents, green gloves, and "
                   "green boots",
        "signature": {"hair_color": "emerald green", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Big Barda": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "metallic blue and gold high-tech armor with massive golden shoulder "
                   "pauldrons, armored boots, and a cape with cosmic designs",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Cheetah": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a spotted bikini-style outfit, with smooth, flawless golden spotted cheetah "
                   "fur, pointed ears, and sharp fangs",
        "eyes": "green with vertical cat-slit pupils",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Mera": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting green bodysuit with scale patterns, golden armor "
                   "pieces, and royal golden accessories",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "emerald"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "fair"},
    },

    # --- Additional women (other franchises) ------------------------------
    "Rainbow Brite": {
        "franchise": "Rainbow Brite",
        "gender": "Female",
        "costume": "a blue dress with rainbow-striped sleeves and skirt trim, a yellow "
                   "star emblem, a rainbow belt, puffy boots, and a rainbow ribbon in "
                   "the hair",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Smurfette": {
        "franchise": "The Smurfs",
        "gender": "Female",
        "costume": "a white dress and white high-heeled shoes, with smooth, flawless light blue "
                   "Smurf skin, on a tiny diminutive figure of miniature proportions",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "size_scale": "tiny",
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Liara T'Soni": {
        "bald": True,
        "franchise": "Mass Effect",
        "gender": "Female",
        "costume": "a white and blue sleeveless top with a high collar, dark fitted pants, and "
                   "practical boots, with smooth, flawless light blue Asari skin and a smooth "
                   "cartilage head crest",
        "signature": {"eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height"},
    },

    # ======================================================================
    # MALE CHARACTERS
    # Worn items only (held props/weapons dropped); non-human skin as body
    # paint with skin_tone omitted; full-mask characters carry no signature
    # hair/eyes. Iconic facial hair uses the gendered `facial_hair` field, so
    # it applies to a male person and is dropped for crossplay to a female.
    # ======================================================================

    # --- Marvel (male) ----------------------------------------------------
    "Spider-Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a skintight red and blue bodysuit with black webbing lines across the "
                   "red, a large black spider emblem on the chest, red gloves, and red boots",
        "mask": "a full face mask with large white teardrop eye lenses",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Iron Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full powered exosuit, no bare skin for jewellery
        "costume": "a glossy hot-rod red and gold plated powered exosuit with a glowing "
                   "circular arc reactor in the chest and articulated armored gauntlets "
                   "and boots",
        "mask": "a faceplate with narrow glowing eye slits",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Tony Stark": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a tailored dark suit with tinted aviator sunglasses and a faint blue "
                   "arc reactor glow at the chest",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "goatee", "eye_color": "medium brown"},
        "physique": {"body_type": "fit", "height": "average height", "skin_tone": "fair"},
    },
    "Captain America": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue scale-textured uniform with a white star on the chest, red and "
                   "white horizontal stripes across the midsection, a snug blue cowl with "
                   "a white A, red gloves, and red boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a round shield with concentric red and white rings and a white "
                "five-pointed star on a blue center",
    },
    "Thor": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "sleeveless silver and black armor with rows of circular silver chest "
                   "discs, a flowing red cape, and engraved bracers",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "facial_hair": "short beard", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "Mjolnir, a short-handled rectangular war hammer with a worn "
                "leather-wrapped grip",
    },
    "Hulk": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "only torn purple trousers, with smooth, flawless rich green skin over "
                   "enormous muscles, on an enormously tall hulking figure of immense towering proportions",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "green"},
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Wolverine": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a yellow and blue tactical suit with black side panels, a yellow mask "
                   "with pointed peaks, and metal claws extending between the knuckles of "
                   "each fist",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "mutton chops", "eye_color": "hazel"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "Deadpool": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a skintight red and black bodysuit with black side panels, leg "
                   "holsters, and ammo pouches and belts",
        "mask": "a full red and black mask with white teardrop eye patches",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "twin steel katanas, one gripped in each hand",
    },
    "Black Panther": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a sleek matte-black vibranium catsuit with a faint raised silver "
                   "triangular weave and a silver vibranium necklace",
        "mask": "a panther mask with small rounded ears",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Doctor Strange": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a dark blue tunic with a wide sash and high collar, a flowing red "
                   "Cloak of Levitation with a tall collar, and a golden Eye of Agamotto "
                   "amulet at the throat",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "very short",
                      "facial_hair": "goatee", "eye_color": "gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Star-Lord": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a long weathered red leather coat over a grey jacket, and a retro "
                   "metal helmet with glowing orange eyes",
        "signature": {"hair_color": "dark blonde", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a pair of retro chrome-and-orange element blasters, one in each hand",
    },
    "Loki": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "green and black layered armor with gold accents, a long flowing green "
                   "cape, and a tall golden helmet with two long curving horns",
        "signature": {"hair_color": "jet black", "hair_length": "jaw length",
                      "hair_style": "slicked back", "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
    },
    "Thanos": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "gold and blue armored battle plate, blue greaves, and the golden Infinity "
                   "Gauntlet, with uniform, all-over deeply ridged purple skin, on an enormously "
                   "tall figure of immense towering proportions",
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Venom": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hulking glossy pitch-black symbiote bodysuit on an imposingly large figure of "
                   "immense proportions, with a white spider emblem across the chest and clawed hands",
        "mask": "a featureless symbiote head with huge jagged white eye patches",
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Daredevil": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "deep red textured leather armor from neck to toe with a double-D "
                   "emblem on the chest",
        "mask": "a small mask with two short devil horns",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Punisher": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a black long-sleeve shirt with a large stylized white skull spanning "
                   "the chest, a tactical vest with ammo, and fingerless gloves",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Magneto": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a deep crimson armored bodysuit with purple gloves and boots, a "
                   "purple flowing cape, and a tall purple crested helmet",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Doctor Doom": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hooded green cloak over silver metallic plate armor, a wide brown "
                   "belt, and gauntlets",
        "mask": "a riveted steel mask with narrow eye slits",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Gambit": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a long brown trench coat over pink and blue armor with a chest sash",
        "signature": {"hair_color": "auburn", "hair_length": "shoulder length",
                      "hair_style": "worn down"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "a fanned hand of playing cards crackling with charged "
                "pink-and-violet kinetic energy",
    },
    "Nightcrawler": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a red and black bodysuit, with smooth, flawless indigo-blue skin, pointed "
                   "ears, and a long spaded tail",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Silver Surfer": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a seamless mirror-chrome silver bodysuit with smooth, flawless reflective "
                   "silver skin",
        "mask": "a featureless chrome head with blank silver eyes",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a sleek mirror-chrome cosmic surfboard, held upright at his side",
    },
    "Winter Soldier": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a black tactical vest with straps over dark combat gear, and a "
                   "gleaming silver metal left arm bearing a red star",
        "signature": {"hair_color": "dark brown", "hair_length": "jaw length",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Ghost Rider": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black studded leather jacket with chains",
        "mask": "a bare flaming skull wreathed in orange fire for a head",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Blade": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an ankle-length black leather trench coat over black armor, and "
                   "wraparound sunglasses",
        "signature": {"hair_color": "jet black", "hair_length": "buzzed very short",
                      "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
        "prop": "a silver katana worn across the back",
    },

    # --- DC (male) --------------------------------------------------------
    "Superman": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a skintight blue bodysuit with a large red and yellow diamond S shield "
                   "on the chest, a red cape, red briefs, red boots, a golden belt, and a "
                   "single curl of hair falling on the forehead",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Batman": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a dark grey armored bodysuit with a black bat emblem across the chest, "
                   "a long scalloped black cape, a yellow utility belt, and black "
                   "gauntlets with fin blades",
        "mask": "a black cowl with pointed bat ears",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Bruce Wayne": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "an immaculately tailored charcoal three-piece suit, a crisp white "
                   "shirt, a silk tie, and a gold watch",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "bright blue"},
        "physique": {"body_type": "fit", "height": "tall", "skin_tone": "fair"},
    },
    "The Flash": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a full red bodysuit with a golden lightning-bolt emblem in a white "
                   "circle on the chest and golden boots",
        "mask": "a red cowl with small golden wing bolts at the ears",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Green Lantern": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black bodysuit with a bright green torso and shoulders, a green "
                   "circular lantern emblem on the chest, a green domino mask, green "
                   "gloves and boots, and a glowing green power ring worn on the finger",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Hal Jordan": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black bodysuit with a bright green torso and shoulders, a green "
                   "circular lantern emblem on the chest, a green domino mask, green "
                   "gloves and boots, and a glowing green power ring worn on the finger",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "John Stewart": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black-and-green Green Lantern bodysuit with a circular lantern "
                   "emblem on the chest, green gloves and boots, and a glowing green "
                   "power ring worn on the finger",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "deep"},
    },
    "Guy Gardner": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a green-and-black Green Lantern jacket-style uniform with a circular "
                   "lantern emblem on the chest, green gloves, and a glowing green power "
                   "ring worn on the finger",
        "signature": {"hair_color": "copper", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Kyle Rayner": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a sleek black bodysuit with green panels and a green crab-shaped "
                   "lantern emblem on the chest, a green domino mask, and a glowing green "
                   "power ring worn on the finger",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "tan"},
    },
    "Alan Scott": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a Golden Age hero outfit of a red tunic with a green lantern emblem, "
                   "a high-collared green cape lined with purple, a black-and-green "
                   "domino mask, and a glowing green magic power ring worn on the finger",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Aquaman": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a golden-orange scaled chainmail shirt, green scaled leggings, and "
                   "golden gauntlets",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "facial_hair": "short beard", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
        "prop": "a five-pronged golden trident with long barbed tines",
    },
    "Green Arrow": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a dark forest-green hooded leather suit, a green domino mask, and a "
                   "quiver of arrows",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "facial_hair": "van dyke", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a drawn recurve bow of green-and-black composite limbs, an arrow "
                "nocked",
    },
    "Cyborg": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "one side a human face, the rest gleaming silver and black robotic "
                   "plating with a glowing eye and an arm-mounted sonic cannon",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Nightwing": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black bodysuit with a bright blue bird symbol sweeping across the "
                   "chest and onto the arms, and a black domino mask",
        "signature": {"hair_color": "jet black", "hair_length": "jaw length",
                      "hair_style": "slicked back", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a pair of blue-tipped escrima fighting sticks, one in each hand",
    },
    "Shazam": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red bodysuit with a golden lightning-bolt emblem on the chest, a "
                   "short white half-cape with gold trim, a golden sash, and golden boots",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Joker": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a purple tailcoat suit with a green vest and a yellow shirt, smooth, "
                   "flawless chalk-white skin, a wide carved red grin, and slicked-back bright "
                   "green hair",
        "signature": {"hair_color": "emerald green", "hair_length": "jaw length",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Bane": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tactical vest, broad bare muscular arms, and a thick green venom "
                   "tube feeding into the back of the skull",
        "mask": "a black luchador mask covering the whole head",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Deathstroke": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue and grey armored tactical suit, bandoliers, and a sword "
                   "sheathed on the back",
        "mask": "a mask split half orange and half black with a single eye slit",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Black Adam": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black bodysuit with a golden lightning-bolt emblem on the chest, a "
                   "golden hood and sash, a flowing black cape, and golden bracers",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Martian Manhunter": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a blue cape held by crossed straps over a bare chest, blue trunks, and blue "
                   "boots, with smooth, flawless green skin and a bald green head",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },

    # --- Star Wars (male) -------------------------------------------------
    "Luke Skywalker": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a black Jedi tunic with a wrapped front and a wide belt, and a single "
                   "black glove",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "an ignited lightsaber with a bright green energy blade and a silver "
                "ribbed hilt",
    },
    "Han Solo": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a white shirt under a black vest, dark trousers with a red side "
                   "stripe, and a low-slung empty blaster holster on the thigh",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Darth Vader": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black ribbed chest control panel, a wide belt box, and a flowing "
                   "black cape",
        "mask": "a glossy black domed helmet and skull-like mask with triangular eye lenses",
        "physique": {"body_type": "athletic", "height": "very tall"},
        "prop": "an ignited lightsaber with a deep red energy blade and a black "
                "ribbed hilt",
    },
    "Obi-Wan Kenobi": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "layered cream and brown Jedi robes with a hooded cloak",
        "signature": {"hair_color": "auburn", "hair_length": "jaw length",
                      "facial_hair": "full beard", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "an ignited lightsaber with a bright blue energy blade and a "
                "ribbed silver hilt",
    },
    "Yoda": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a simple brown Jedi robe, with green wrinkled skin, very large pointed "
                   "ears, and sparse white hair, on a diminutive small-statured figure of notably short height",
        "signature": {"eye_color": "green"},
        "size_scale": "tiny",
        "physique": {"body_type": "slim", "height": "very petite"},
        "prop": "a small ignited lightsaber with a short green energy blade and a "
                "stubby silver hilt",
    },
    "Mace Windu": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "dark brown layered Jedi robes with a cloak, and a clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "dark brown"},
        "prop": "an ignited lightsaber with a deep amethyst-purple energy blade "
                "and a polished silver hilt",
    },
    "Anakin Skywalker": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a dark Jedi tunic and tabards with a single leather glove on the right "
                   "hand, and a scar across the right brow",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "an ignited lightsaber with a bright blue energy blade and a "
                "black-gripped silver hilt",
    },
    "Kylo Ren": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a black ribbed tunic with a layered hooded cape, and a scar down one "
                   "cheek",
        "signature": {"hair_color": "jet black", "hair_length": "jaw length",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "an ignited crossguard lightsaber with a ragged, unstable red "
                "energy blade and two short red blade vents flaring from the hilt",
    },
    "Boba Fett": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "weathered green and rust Mandalorian armor with battle dents, a "
                   "jetpack, and a braided trophy cape on one shoulder",
        "mask": "a green T-visor helmet with a side rangefinder",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "The Mandalorian": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "full polished silver beskar plate armor over a flight suit, a jetpack, "
                   "and a brown half-cape",
        "mask": "a smooth silver T-visor helmet",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Darth Maul": {
        "bald": True,
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "black hooded robes, with smooth, flawless blood-red skin patterned with "
                   "intricate black tattoos and a crown of short black horns ringing the head",
        "physique": {"body_type": "lean", "height": "average height"},
        "prop": "an ignited double-bladed lightsaber, a long silver staff hilt "
                "with a red energy blade burning at each end",
    },
    "Chewbacca": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a single bandolier strap of silver ammo across the chest, with "
                   "all-over long shaggy brown fur over the body",
        "mask": "a long-muzzled Wookiee face covered in shaggy brown fur",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Emperor Palpatine": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "heavy black hooded robes, with pale corrupted wrinkled skin",
        "signature": {"hair_color": "silver", "hair_length": "ear length"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "very pale"},
    },

    # --- Star Trek (male) -------------------------------------------------
    "Mr. Spock": {
        "franchise": "Star Trek",
        "gender": "Male",
        "costume": "a blue Starfleet science tunic with an insignia, black trousers, black "
                   "boots, pointed Vulcan ears, and sharply upswept eyebrows",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Captain Kirk": {
        "franchise": "Star Trek",
        "gender": "Male",
        "costume": "a gold Starfleet command tunic with a starburst insignia, black "
                   "trousers, and black boots",
        "signature": {"hair_color": "medium brown", "hair_length": "very short",
                      "eye_color": "hazel"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Captain Picard": {
        "franchise": "Star Trek",
        "gender": "Male",
        "costume": "a red and black Starfleet uniform with rank pips on the collar",
        "signature": {"hair_length": "buzzed very short", "facial_hair": "clean shaven",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "fit", "height": "tall", "skin_tone": "fair"},
    },
    "Data": {
        "franchise": "Star Trek",
        "gender": "Male",
        "costume": "a gold and black Starfleet uniform, with pale golden synthetic skin "
                   "and golden eyes",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Worf": {
        "franchise": "Star Trek",
        "gender": "Male",
        "costume": "a Starfleet uniform crossed with a metallic Klingon baldric sash, and "
                   "a pronounced ridged Klingon forehead",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "brown"},
    },

    # --- Final Fantasy (male) ---------------------------------------------
    "Cloud Strife": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a sleeveless black turtleneck with a single shoulder pauldron and a "
                   "leather glove",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "the Buster Sword, an enormous broad-bladed greatsword held over one "
                "shoulder",
    },
    "Sephiroth": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a long black leather coat with armored shoulder pauldrons worn over a "
                   "bare chest",
        "eyes": "glowing green with vertical cat-slit pupils",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "hair_texture": "pin straight"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
        "prop": "the Masamune, an impossibly long slender silver katana",
    },
    "Squall": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a black leather jacket with a white fur collar, and a scar slanting "
                   "across the brow and nose",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a gunblade, a broad sword with a revolver grip and trigger at the "
                "hilt",
    },
    "Tidus": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a yellow and black sleeveless top with one long sleeve, overall-shorts "
                   "with suspenders, and a single yellow glove",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "tan"},
    },
    "Zidane": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a white shirt under a blue vest, an orange tail-ring, and a long "
                   "monkey tail",
        "signature": {"hair_color": "golden blonde", "hair_length": "jaw length",
                      "hair_style": "low ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "short", "skin_tone": "tan"},
    },
    "Vincent Valentine": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a red headband and a tattered red cloak with a high collar over dark "
                   "leather, and a golden three-pointed clawed gauntlet",
        "signature": {"hair_color": "jet black", "hair_length": "long"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
    },
    "Auron": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a high red coat worn off one shoulder with the sleeve hanging empty, "
                   "small round sunglasses, and a jug at the belt",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "facial_hair": "short beard"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Street Fighter (male) --------------------------------------------
    "Ryu": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a white sleeveless karate gi with frayed cuffs and a black belt, a red "
                   "headband, and red hand wraps, barefoot",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Ken Masters": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a red sleeveless karate gi with a black belt and red hand wraps, "
                   "barefoot",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Akuma": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a dark torn karate gi worn off the shoulders, a large prayer-bead "
                   "necklace, and the red kanji for heaven on the back, barefoot",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "hair_style": "windswept"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
    },
    "M. Bison": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a red military uniform with broad shoulder pads, a black cape, a wide "
                   "belt, and a peaked military cap with an emblem",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Guile": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "green camouflage fatigue trousers, a green tank top, dog tags, red and "
                   "black hand wraps, combat boots, and a tall blonde flat-top",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Blanka": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "torn brown shorts and ankle manacles, with smooth, flawless bright green "
                   "skin, wild orange hair and mane, and sharp teeth",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Dhalsim": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a torn orange loincloth, multiple skull necklaces, three painted dots "
                   "on the forehead, and a bald head painted with white skull markings",
        "signature": {"eye_color": "dark brown"},
        "physique": {"body_type": "very slim", "height": "tall", "skin_tone": "dark brown"},
    },
    "Zangief": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "red wrestling briefs, red boots, brown hand wraps, a red mohawk, and a "
                   "bare muscular scarred chest with thick chest hair",
        "signature": {"hair_color": "bright red", "eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },

    # --- Mortal Kombat (male) ---------------------------------------------
    "Scorpion": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "covers_face": True,
        "costume": "a yellow and black ninja uniform with ninja-rope wrappings and a "
                   "kunai spear on a chain",
        "mask": "a yellow and black ninja mask and hood",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Sub-Zero": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "a blue and black ninja uniform with a mask over the lower face and a "
                   "frosted chest emblem, with frost forming at the hands",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Raiden": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "a white robe and vest with a wide-brimmed conical straw hat, with blue "
                   "lightning crackling across the body",
        "signature": {"hair_color": "white", "hair_length": "long"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Liu Kang": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "black martial-arts trousers, a red headband, hand wraps, and a bare "
                   "muscular chest, with fire at the fists",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Kung Lao": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "blue and black warrior garb with a bare chest, and a wide black hat "
                   "rimmed with a razor steel blade",
        "signature": {"hair_length": "buzzed very short", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Johnny Cage": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "a black sleeveless tank top, fingerless gloves, dark sunglasses, and "
                   "martial-arts trousers",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Kano": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "a black sleeveless outfit, a metal plate bolted over the right half of "
                   "the face with a glowing red laser eye, and a curved knife sheath",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Shao Kahn": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "covers_face": True,
        "costume": "ornate armor with huge spiked shoulder pauldrons over a bare muscular "
                   "chest",
        "mask": "a horned skull-faced helmet",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Reptile": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "covers_face": True,
        "costume": "green and black ninja garb with uniform, all-over green scaled skin and "
                   "clawed hands",
        "mask": "a green and black ninja mask",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Baraka": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "leather warrior garb, a bald head, a wide mouth of jagged sharp teeth, "
                   "and long retractable blades extending from both forearms",
        "signature": {"eye_color": "nearly black"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Anime (male) -----------------------------------------------------
    "Goku": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "an orange martial-arts gi with a blue undershirt and sash, and blue "
                   "wristbands and boots",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Vegeta": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a blue bodysuit under white and yellow Saiyan armor, with white gloves "
                   "and boots",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
    },
    "Piccolo": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a white turban and a white cape over shoulder pads, a purple gi with a "
                   "blue sash, green skin, pointed ears, and two head antennae",
        "signature": {"eye_color": "nearly black"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Naruto Uzumaki": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "an orange and black tracksuit, a metal-plate forehead protector "
                   "headband, and three whisker marks on each cheek",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Sasuke Uchiha": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a dark high-collared shirt with a rope belt, and a sword sheathed at "
                   "the lower back",
        "signature": {"hair_color": "near black", "hair_length": "jaw length",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Kakashi Hatake": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a green flak vest over dark blues, a dark cloth mask over the lower "
                   "face, and a slanted forehead protector covering one eye",
        "signature": {"hair_color": "silver", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "dark gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Monkey D. Luffy": {
        "franchise": "One Piece",
        "gender": "Male",
        "costume": "an open red vest over a bare chest, blue knee-shorts, sandals, a "
                   "yellow straw hat, and a scar under the left eye",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "tan"},
    },
    "Roronoa Zoro": {
        "franchise": "One Piece",
        "gender": "Male",
        "costume": "a green haramaki sash holding three sheathed swords at the hip, a "
                   "black bandana, gold earrings, and a long vertical scar over the left eye",
        "signature": {"hair_color": "emerald green", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
    },
    "All Might": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a skintight blue costume with bold red and white stripes meeting at a "
                   "V, white gloves, and a permanent wide grin",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Deku": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a green bodysuit with a white-ribbed pattern, a hood with two tall "
                   "rabbit-like ears, a red belt, metal arm braces, and freckles",
        "signature": {"hair_color": "emerald green", "hair_length": "very short",
                      "hair_texture": "curly", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Bakugo": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a black sleeveless costume with an orange X-strap and a high collar, "
                   "and enormous grenade-shaped gauntlets",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "hair_style": "windswept"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Edward Elric": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Male",
        "costume": "a red hooded coat over a black jacket and trousers, white gloves, and "
                   "a steel automail right arm",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "side braid", "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "short", "skin_tone": "fair"},
    },
    "Levi Ackerman": {
        "franchise": "Attack on Titan",
        "gender": "Male",
        "costume": "a brown Survey Corps jacket with the wings-of-freedom crest, a green "
                   "hooded cloak, and a body harness with handheld blades on ODM gear",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "blunt bangs", "eye_color": "dark gray"},
        "physique": {"body_type": "lean", "height": "short", "skin_tone": "fair"},
    },
    "Eren Yeager": {
        "franchise": "Attack on Titan",
        "gender": "Male",
        "costume": "a brown Survey Corps jacket and straps over a white shirt, a green "
                   "hooded cloak, and an ODM-gear harness",
        "signature": {"hair_color": "dark brown", "hair_length": "jaw length",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Saitama": {
        "franchise": "One Punch Man",
        "gender": "Male",
        "costume": "a yellow jumpsuit with a zip collar, a white cape, red gloves, red "
                   "boots, a black belt, and a completely bald shiny head",
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Tatsumaki": {
        "franchise": "One Punch Man",
        "gender": "Female",
        "costume": "a form-fitting black sleeveless cocktail dress and black heels, "
                   "wrapped in a faint swirling green psychic aura, floating just off the ground",
        "signature": {"hair_color": "emerald green", "hair_texture": "curly",
                      "hair_length": "short pixie", "eye_color": "green"},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },

    # --- Nintendo (male) --------------------------------------------------
    "Mario": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "blue overalls over a red shirt, white gloves, brown boots, a red cap "
                   "with a white circle and red M, and a thick brown mustache",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "Luigi": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "blue overalls over a green shirt, white gloves, brown boots, a green "
                   "cap with a white circle and green L, and a thin brown mustache",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Link": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "a green belted tunic over a white undershirt, a long green pointed "
                   "cap, brown boots and gauntlets, pointed elf ears, and a kite shield "
                   "on the back",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "the Master Sword, a double-edged blade with a blue-and-gold winged "
                "crossguard",
    },
    "Ganondorf": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "a black and gold tunic with armor and a jewel on the forehead, with "
                   "long flame-red hair pulled back and dark green-grey skin",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },

    # --- Lord of the Rings (male) -----------------------------------------
    "Aragorn": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "worn brown ranger leathers and a hooded travel cloak",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "facial_hair": "short beard", "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "Anduril, a long broad-bladed sword with an ornate engraved "
                "crossguard",
    },
    "Legolas": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "a green and brown elven tunic, pointed elf ears, and a quiver on the "
                   "back",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "hair_texture": "pin straight", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "a drawn elven longbow of pale carved wood, an arrow nocked",
    },
    "Gandalf": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "layered grey robes and a tall pointed grey hat",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "facial_hair": "full beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "average", "height": "tall", "skin_tone": "fair"},
        "prop": "a tall gnarled wooden staff with a knotted natural crook at the top",
    },
    "Gimli": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "a horned and riveted iron helmet, and layered dwarven armor",
        "signature": {"hair_color": "auburn", "hair_length": "shoulder length",
                      "facial_hair": "full beard", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
        "prop": "a broad double-bitted dwarven battle axe with a rune-etched head "
                "and a leather-wrapped haft",
    },
    "Frodo Baggins": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "a tan waistcoat over a white shirt with a green travel cloak, "
                   "oversized bare hairy feet, and a glowing ring on a chain",
        "signature": {"hair_color": "dark brown", "hair_length": "ear length",
                      "hair_texture": "curly", "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "fair"},
    },

    # --- More games / movies (male) ---------------------------------------
    "Geralt of Rivia": {
        "franchise": "The Witcher",
        "gender": "Male",
        "costume": "dark studded-leather armor with a medallion, and two swords crossed on "
                   "the back",
        "eyes": "yellow with vertical cat-slit pupils",
        "signature": {"hair_color": "white", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "facial_hair": "stubble"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Kratos": {
        "franchise": "God of War",
        "gender": "Male",
        "costume": "a leather harness and bracers over a bare chest, with smooth, flawless "
                   "ash-grey pale skin and a bold red tattoo across the torso and one eye",
        "signature": {"hair_length": "buzzed very short", "facial_hair": "full beard",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "very tall"},
        "prop": "the Leviathan Axe, a heavy frost-etched battle axe with a "
                "leather-wrapped haft",
    },
    "Master Chief": {
        "franchise": "Halo",
        "gender": "Male",
        "covers_face": True,
        "costume": "full matte olive-green Mjolnir power armor with heavy plated shoulders "
                   "and gauntlets",
        "mask": "a helmet with a golden-orange reflective visor",
        "physique": {"body_type": "athletic", "height": "very tall"},
        "prop": "an MA5 assault rifle with a boxy top-mounted magazine and a digital "
                "ammo counter",
    },
    "Solid Snake": {
        "franchise": "Metal Gear",
        "gender": "Male",
        "costume": "a grey skintight sneaking suit with knee pads, a bandana, and a "
                   "holstered pistol",
        "signature": {"hair_color": "dark brown", "hair_length": "jaw length",
                      "facial_hair": "stubble", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Doctor Manhattan": {
        "franchise": "Watchmen",
        "gender": "Male",
        "costume": "a hydrogen-atom symbol glowing on the forehead, with smooth, flawless "
                   "glowing blue skin, a clean-shaven bald head, and blank white eyes",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Rorschach": {
        "franchise": "Watchmen",
        "gender": "Male",
        "covers_face": True,
        "costume": "a belted tan trench coat, a brown fedora, and fingerless gloves",
        "mask": "a white full-face mask covered in shifting black inkblot patterns",
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Optimus Prime": {
        "franchise": "Transformers",
        "gender": "Male",
        "covers_face": True,
        "costume": "towering red and blue metallic armor plating with a windshield chest",
        "mask": "a metallic head with two crest antennae, a faceplate, and glowing blue eyes",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Spawn": {
        "franchise": "Image",
        "gender": "Male",
        "covers_face": True,
        "costume": "a living pitch-black suit with a white spider-like chest symbol, an "
                   "enormous tattered red cape, and wrapped chains and spikes",
        "mask": "a living black hood and mask with glowing white eyes",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Jack Sparrow": {
        "franchise": "Pirates of the Caribbean",
        "gender": "Male",
        "costume": "a red bandana under a brown tricorn hat, a long ragged coat over "
                   "layered sashes, gold rings, and a braided forked beard",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_style": "locs", "facial_hair": "goatee", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "tan"},
    },
    "Indiana Jones": {
        "franchise": "Movie",
        "gender": "Male",
        "costume": "a brown felt fedora, a worn leather jacket over a khaki shirt, a "
                   "coiled bullwhip on the belt, and a satchel",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "tan"},
    },

    # =====================================================================
    # Expansion (June 2026): franchise gaps + requested additions
    # =====================================================================

    # --- Avatar: The Last Airbender / Korra ------------------------------
    "Aang": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Male",
        "costume": "orange and yellow Air Nomad monk robes with a high collar, and a "
                   "clean-shaven bald head marked by a blue arrow tattoo down the forehead",
        "signature": {"facial_hair": "clean shaven", "eye_color": "gray"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "light"},
        "prop": "a wooden glider staff with folding orange fabric wings",
    },
    "Zuko": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Male",
        "costume": "dark red and black Fire Nation armor with a high collar, and a large "
                   "red burn scar around the left eye",
        "signature": {"hair_color": "jet black", "hair_length": "ear length",
                      "hair_style": "top knot", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Sokka": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Male",
        "costume": "a blue Water Tribe warrior tunic with bone-and-leather shoulder armor, "
                   "and blue-and-white war paint across the face",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "high ponytail", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "tan"},
        "prop": "a curved black boomerang",
    },
    "Iroh": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Male",
        "costume": "layered red and gold Fire Nation robes over a stout frame",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "shoulder length",
                      "facial_hair": "full beard", "eye_color": "golden brown"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "light"},
    },
    "Suki": {
        "franchise": "Avatar: The Last Airbender",
        "gender": "Female",
        "costume": "green Kyoshi Warrior robes with metal armor plates, and dramatic "
                   "white face paint with bold red eye and lip makeup",
        "signature": {"hair_color": "chestnut", "hair_length": "shoulder length",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Asami Sato": {
        "franchise": "The Legend of Korra",
        "gender": "Female",
        "costume": "a stylish red and black jacket over fitted dark clothing with "
                   "knee-high boots and a magenta accent",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "wavy", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "light"},
    },

    # --- Demon Slayer ----------------------------------------------------
    "Tanjiro Kamado": {
        "franchise": "Demon Slayer",
        "gender": "Male",
        "costume": "a checkered black-and-green haori over a dark Demon Slayer uniform, "
                   "hanafuda-style earrings, and a scar on the forehead",
        "signature": {"hair_color": "deep red", "hair_length": "very short",
                      "hair_texture": "wavy", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
        "prop": "a black-bladed Nichirin katana",
    },
    "Nezuko Kamado": {
        "franchise": "Demon Slayer",
        "gender": "Female",
        "costume": "a pink asanoha-patterned kimono under a brown haori with a pink obi, "
                   "and a bamboo muzzle held across the mouth by a red cord",
        "signature": {"hair_color": "black with colored tips", "hair_length": "hip length",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Zenitsu Agatsuma": {
        "franchise": "Demon Slayer",
        "gender": "Male",
        "costume": "a bright yellow-orange haori with a white triangle pattern over a "
                   "dark Demon Slayer uniform",
        "signature": {"hair_color": "golden blonde", "hair_length": "short pixie",
                      "eye_color": "golden brown"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Inosuke Hashibira": {
        "franchise": "Demon Slayer",
        "gender": "Male",
        "covers_face": True,
        "costume": "a bare muscular torso, baggy dark hakama, and shaggy fur leg wrappings",
        "mask": "a snarling wild boar's head worn over the face",
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Giyu Tomioka": {
        "franchise": "Demon Slayer",
        "gender": "Male",
        "costume": "a black Demon Slayer uniform under a half-red, half-patterned haori",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Shinobu Kocho": {
        "franchise": "Demon Slayer",
        "gender": "Female",
        "costume": "a black Demon Slayer uniform under a white haori with a butterfly-wing "
                   "pattern, and a butterfly hair ornament",
        "signature": {"hair_color": "deep purple", "hair_length": "shoulder length",
                      "hair_style": "low ponytail"},
        "physique": {"body_type": "very slim", "height": "petite", "skin_tone": "fair"},
    },

    # --- Jujutsu Kaisen --------------------------------------------------
    "Gojo Satoru": {
        "franchise": "Jujutsu Kaisen",
        "gender": "Male",
        "costume": "a black high-collared jujutsu uniform jacket, and a black blindfold "
                   "wrapped over the eyes",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Yuji Itadori": {
        "franchise": "Jujutsu Kaisen",
        "gender": "Male",
        "costume": "a black high-collared jujutsu uniform with a zip front",
        "signature": {"hair_color": "hot pink", "hair_length": "very short",
                      "eye_color": "warm hazel"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Megumi Fushiguro": {
        "franchise": "Jujutsu Kaisen",
        "gender": "Male",
        "costume": "a black high-collared jujutsu uniform",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "eye_color": "dark gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Nobara Kugisaki": {
        "franchise": "Jujutsu Kaisen",
        "gender": "Female",
        "costume": "a black jujutsu uniform skirt-set with knee-high socks",
        "signature": {"hair_color": "orange", "hair_length": "chin length bob",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Sukuna": {
        "franchise": "Jujutsu Kaisen",
        "gender": "Male",
        "costume": "a dark patterned kimono open at the chest, with black curse-mark "
                   "tattoos across the face and body and a second pair of eyes on the cheeks",
        "eyes": "crimson",
        "signature": {"hair_color": "hot pink", "hair_length": "very short"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Bleach ----------------------------------------------------------
    "Ichigo Kurosaki": {
        "franchise": "Bleach",
        "gender": "Male",
        "costume": "a black Soul Reaper shihakusho robe with a long flowing hem",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "hair_texture": "slightly wavy", "eye_color": "warm hazel"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
        "prop": "an oversized cleaver-like zanpakuto with a bandaged hilt",
    },
    "Rukia Kuchiki": {
        "franchise": "Bleach",
        "gender": "Female",
        "costume": "a black Soul Reaper shihakusho robe with a white sash",
        "signature": {"hair_color": "near black", "hair_length": "chin length bob",
                      "eye_color": "violet-gray"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "porcelain"},
    },
    "Orihime Inoue": {
        "franchise": "Bleach",
        "gender": "Female",
        "costume": "a school uniform with blue snowflake-shaped hairpins",
        "signature": {"hair_color": "orange", "hair_length": "waist length",
                      "hair_texture": "sleek straight", "eye_color": "gray"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "fair"},
    },
    "Byakuya Kuchiki": {
        "franchise": "Bleach",
        "gender": "Male",
        "costume": "a black Soul Reaper robe under a white captain's haori, white "
                   "kenseikan hair ornaments, and a white scarf",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_texture": "sleek straight", "eye_color": "dark gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Renji Abarai": {
        "franchise": "Bleach",
        "gender": "Male",
        "costume": "a black Soul Reaper robe with bold black tribal tattoos across the "
                   "brow and body, and white-framed goggles pushed up on the head",
        "signature": {"hair_color": "deep red", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
    },

    # --- JoJo's Bizarre Adventure ----------------------------------------
    "Jotaro Kujo": {
        "franchise": "JoJo's Bizarre Adventure",
        "gender": "Male",
        "costume": "a long dark school-captain coat with gold chains over a cropped "
                   "white shirt, and a peaked cap that blends into the hair",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "light"},
    },
    "Dio Brando": {
        "franchise": "JoJo's Bizarre Adventure",
        "gender": "Male",
        "costume": "a sleeveless yellow outfit with heart motifs, pointed shoulder "
                   "pieces, and tall boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_texture": "thick and voluminous", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Joseph Joestar": {
        "franchise": "JoJo's Bizarre Adventure",
        "gender": "Male",
        "costume": "a green tank top, a long scarf, fingerless gloves, and a flat cap",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Giorno Giovanna": {
        "franchise": "JoJo's Bizarre Adventure",
        "gender": "Male",
        "costume": "a pink suit covered in heart cut-outs, with a ladybug brooch",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "loose braids", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },

    # --- Naruto (more) ---------------------------------------------------
    "Itachi Uchiha": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a black Akatsuki cloak patterned with red clouds, a scratched "
                   "Hidden Leaf headband, and pronounced tear-trough lines under the eyes",
        "eyes": "crimson Sharingan with three black tomoe",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_style": "low ponytail"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Madara Uchiha": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "dark red armor over a high-collared cloak",
        "eyes": "crimson Sharingan",
        "signature": {"hair_color": "near black", "hair_length": "waist length",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Gaara": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a dark crimson coat, a large gourd of sand on the back, and the red "
                   "kanji for love tattooed above the left eye with dark-ringed eyes",
        "signature": {"hair_color": "deep red", "hair_length": "very short",
                      "eye_color": "pale blue"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Jiraiya": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a green kimono and haori over mesh armor, a horned forehead "
                   "protector, and red lines running down from the eyes",
        "signature": {"hair_color": "white", "hair_length": "waist length",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "light"},
    },
    "Rock Lee": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a green spandex jumpsuit, orange leg warmers, bandaged hands, and "
                   "very thick eyebrows",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "blunt bangs", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Orochimaru": {
        "franchise": "Naruto",
        "gender": "Male",
        "costume": "a pale tan tunic with a thick purple rope belt, and pale snake-like "
                   "skin with purple eye markings",
        "signature": {"hair_color": "near black", "hair_length": "waist length",
                      "hair_texture": "sleek straight", "eye_color": "amber"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },

    # --- Dragon Ball (more) ----------------------------------------------
    "Gohan": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a green tunic, a white cape, a red belt, and white-and-black boots",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Future Trunks": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a blue Capsule Corp jacket over a black tank top, gray trousers, and "
                   "a sword strap across the back",
        "signature": {"hair_color": "lavender", "hair_length": "very short",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
        "prop": "a straight broadsword in a back scabbard",
    },
    "Frieza": {
        "bald": True,
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a smooth white-and-purple bio-armor carapace over smooth, flawless white "
                   "skin with purple plated sections, and a long tail",
        "eyes": "crimson",
        "signature": {},
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Cell": {
        "bald": True,
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "an even, all-over coat of green-and-black insectoid armor plating "
                   "with spotted patterning, orange face plates, and a segmented tail",
        "signature": {"eye_color": "violet-gray"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Broly": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a torn fur pelt at the waist, a green crystal pendant, golden "
                   "wrist and ankle guards, and a bare, massively muscled chest",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark gray"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "tan"},
    },
    "Beerus": {
        "bald": True,
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "an Egyptian-styled outfit of purple, gold and teal over an even, "
                   "all-over coat of lilac-grey fur, with large pointed cat ears and a slim tail",
        "signature": {"eye_color": "amber"},
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Krillin": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "an orange martial-arts gi with a blue undershirt, and a clean-shaven "
                   "bald head with six dark dots on the forehead",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "light"},
    },
    "Chi-Chi": {
        "franchise": "Dragon Ball",
        "gender": "Female",
        "costume": "a purple cheongsam-style dress with a yellow sash",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "light"},
    },

    # --- One Piece (more) ------------------------------------------------
    "Sanji": {
        "franchise": "One Piece",
        "gender": "Male",
        "costume": "a sharp black double-breasted suit with a loosened tie, and one eye "
                   "hidden behind a long blond fringe with a curled spiral eyebrow",
        "signature": {"hair_color": "golden blonde", "hair_length": "ear length",
                      "facial_hair": "soul patch", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "light"},
    },
    "Portgas D. Ace": {
        "franchise": "One Piece",
        "gender": "Male",
        "costume": "an open orange cowboy hat, a bare chest with a bold tattoo, an "
                   "orange waist sash, and a knee-length pair of black shorts",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
    },
    "Trafalgar Law": {
        "franchise": "One Piece",
        "gender": "Male",
        "costume": "a black-and-yellow spotted hoodie with a furry hat, dark jeans, and "
                   "bold tattoos across the hands and chest",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "goatee", "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "light"},
    },
    "Boa Hancock": {
        "franchise": "One Piece",
        "gender": "Female",
        "costume": "a backless red gown with a high slit, a long flowing cape, and gold "
                   "snake-shaped earrings",
        "signature": {"hair_color": "raven black", "hair_length": "hip length",
                      "hair_texture": "sleek straight", "eye_color": "deep blue"},
        "physique": {"body_type": "hourglass", "height": "very tall", "skin_tone": "fair"},
    },

    # --- Fullmetal Alchemist ---------------------------------------------
    "Alphonse Elric": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering suit of ornate gray steel armor with a spiked crest and "
                   "a glowing red alchemic seal on one shoulder",
        "mask": "a horned steel helmet with a dark hollow visor and glowing eye-lights",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Roy Mustang": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Male",
        "costume": "a blue military uniform with silver trim and white ignition gloves "
                   "marked with red transmutation circles",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Winry Rockbell": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Female",
        "costume": "a black tube top, a brown work skirt with a tool belt, and a "
                   "bandana tied over the hair",
        "signature": {"hair_color": "light blonde", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Riza Hawkeye": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Female",
        "costume": "a blue military uniform with twin sidearm holsters",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "eye_color": "amber"},
        "physique": {"body_type": "toned", "height": "average height", "skin_tone": "fair"},
    },
    "Scar": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Male",
        "costume": "a dark hooded coat, dark glasses, a bold red alchemic tattoo down "
                   "the right arm, and a large X-shaped scar across the brow",
        "eyes": "crimson",
        "signature": {"hair_color": "white", "hair_length": "very short"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "warm brown"},
    },

    # --- Death Note ------------------------------------------------------
    "Light Yagami": {
        "franchise": "Death Note",
        "gender": "Male",
        "costume": "a neat tan blazer over a dark shirt and tie",
        "signature": {"hair_color": "light chestnut", "hair_length": "very short",
                      "eye_color": "light brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "a black notebook labeled Death Note",
    },
    "L Lawliet": {
        "franchise": "Death Note",
        "gender": "Male",
        "costume": "a plain white long-sleeved shirt and loose blue jeans, worn "
                   "barefoot with a permanently hunched posture and dark-ringed eyes",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "eye_color": "dark gray"},
        "physique": {"body_type": "slim", "height": "tall", "skin_tone": "very pale"},
    },
    "Misa Amane": {
        "franchise": "Death Note",
        "gender": "Female",
        "costume": "a gothic black dress with lace, buckles, and a small top hat",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "light brown"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },

    # --- My Hero Academia (more) -----------------------------------------
    "Shoto Todoroki": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a hero outfit with a frost-covered right side, and a red burn scar "
                   "around the left eye",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "Ochaco Uraraka": {
        "franchise": "My Hero Academia",
        "gender": "Female",
        "costume": "a black-and-pink skintight hero suit with a round helmet and chunky "
                   "wrist and ankle bracers",
        "signature": {"hair_color": "warm brown", "hair_length": "chin length bob",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "softly curved", "height": "short", "skin_tone": "fair"},
    },
    "Endeavor": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a navy hero bodysuit ringed with flames at the wrists and collar, "
                   "and a fiery beard and brows of living flame",
        "signature": {"hair_color": "deep red", "hair_length": "very short",
                      "facial_hair": "full beard", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "light"},
    },
    "Tomura Shigaraki": {
        "franchise": "My Hero Academia",
        "gender": "Male",
        "costume": "a black outfit hung with severed pale hands, one clutched over the "
                   "face, and chapped, cracked pale skin",
        "eyes": "red-rimmed crimson",
        "signature": {"hair_color": "silver", "hair_length": "shoulder length",
                      "hair_texture": "fine and wispy"},
        "physique": {"body_type": "slim", "height": "tall", "skin_tone": "very pale"},
    },

    # --- Other anime: Cowboy Bebop / Fate / Kill la Kill / Evangelion ----
    "Spike Spiegel": {
        "franchise": "Cowboy Bebop",
        "gender": "Male",
        "costume": "a loose blue leisure suit with a yellow shirt and a thin black tie",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "eye_color": "warm hazel"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "light"},
    },
    "Faye Valentine": {
        "franchise": "Cowboy Bebop",
        "gender": "Female",
        "costume": "a yellow vinyl bandeau top and matching short shorts, red suspenders, "
                   "a red jacket tied at the waist, and a yellow headband",
        "signature": {"hair_color": "purple", "hair_length": "chin length bob",
                      "eye_color": "green"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Saber": {
        "franchise": "Fate/stay night",
        "gender": "Female",
        "costume": "a blue-and-white medieval battle dress under silver armor with a "
                   "steel breastplate and gauntlets",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "messy bun", "eye_color": "emerald"},
        "physique": {"body_type": "slender", "height": "short", "skin_tone": "fair"},
        "prop": "an invisible-bladed sword hilt wrapped in blue cloth",
    },
    "Rin Tohsaka": {
        "franchise": "Fate/stay night",
        "gender": "Female",
        "costume": "a red turtleneck sweater, a black skirt, black thigh-high socks, "
                   "and a red jacket",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Ryuko Matoi": {
        "franchise": "Kill la Kill",
        "gender": "Female",
        "costume": "a revealing black-and-red sailor-uniform battle outfit with a single "
                   "glowing red eye motif and one fingerless red glove",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_style": "blunt bangs", "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Satsuki Kiryuin": {
        "franchise": "Kill la Kill",
        "gender": "Female",
        "costume": "a pristine white commander's military uniform with a long cape and "
                   "tall boots, with very long straight black hair",
        "signature": {"hair_color": "raven black", "hair_length": "hip length",
                      "hair_texture": "sleek straight", "eye_color": "bright blue"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Misato Katsuragi": {
        "franchise": "Neon Genesis Evangelion",
        "gender": "Female",
        "costume": "a blue NERV uniform jacket worn over a black dress, with a red cross "
                   "pendant",
        "signature": {"hair_color": "purple", "hair_length": "long",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "fair"},
    },

    # --- Sailor Moon (more) ----------------------------------------------
    "Sailor Mercury": {
        "franchise": "Sailor Moon",
        "gender": "Female",
        "costume": "a sailor-style fuku with a blue collar and skirt, white bodice, blue "
                   "bows, and a blue tiara jewel",
        "signature": {"hair_color": "navy blue", "hair_length": "ear length",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Sailor Mars": {
        "franchise": "Sailor Moon",
        "gender": "Female",
        "costume": "a sailor-style fuku with a red collar and skirt, white bodice, "
                   "purple bows, and red high heels",
        "signature": {"hair_color": "raven black", "hair_length": "hip length",
                      "hair_texture": "sleek straight", "eye_color": "violet-gray"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Sailor Jupiter": {
        "franchise": "Sailor Moon",
        "gender": "Female",
        "costume": "a sailor-style fuku with a green skirt, white bodice, pink bows, and "
                   "rose-stud earrings",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Sailor Venus": {
        "franchise": "Sailor Moon",
        "gender": "Female",
        "costume": "a sailor-style fuku with an orange skirt, white bodice, blue bows, "
                   "and a red bow in the hair",
        "signature": {"hair_color": "golden blonde", "hair_length": "hip length",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Tuxedo Mask": {
        "franchise": "Sailor Moon",
        "gender": "Male",
        "costume": "a black tailcoat and trousers, a white waistcoat and bow tie, a "
                   "flowing black cape with a red lining, a top hat, and a white domino mask",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a single long-stemmed red rose",
    },

    # --- Genshin Impact --------------------------------------------------
    "Raiden Shogun": {
        "franchise": "Genshin Impact",
        "gender": "Female",
        "costume": "an ornate violet-and-black kimono with a tall flower hairpin and a "
                   "sash bearing a glowing Electro vision",
        "signature": {"hair_color": "deep purple", "hair_length": "hip length",
                      "hair_style": "low ponytail", "eye_color": "violet-gray"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Hu Tao": {
        "franchise": "Genshin Impact",
        "gender": "Female",
        "costume": "a dark red mandarin coat with porkpie hat, plum-blossom motifs, and "
                   "a flower-shaped Pyro vision, with flower-shaped pupils",
        "eyes": "crimson with flower-shaped pupils",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_style": "pigtails"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Ganyu": {
        "franchise": "Genshin Impact",
        "gender": "Female",
        "costume": "a white-and-blue bodysuit with a high collar and gold bells, a "
                   "flowing dark train, and two dark blue horns on the head",
        "signature": {"hair_color": "navy blue", "hair_length": "very long",
                      "eye_color": "violet-gray"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Zhongli": {
        "franchise": "Genshin Impact",
        "gender": "Male",
        "costume": "a brown-and-amber formal suit with an ornate collar and gold "
                   "diamond patterning, and amber-tipped hair",
        "signature": {"hair_color": "near black", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "Venti": {
        "franchise": "Genshin Impact",
        "gender": "Male",
        "costume": "a green caped outfit with dark shorts, a beret with a windwheel "
                   "aster, and braids with blue-green tips",
        "signature": {"hair_color": "near black", "hair_length": "ear length",
                      "hair_style": "loose braids", "eye_color": "emerald"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "fair"},
    },

    # --- Pokemon ---------------------------------------------------------
    "Ash Ketchum": {
        "franchise": "Pokemon",
        "gender": "Male",
        "costume": "a red-and-white cap, a blue open jacket over a black tee, fingerless "
                   "green gloves, and blue jeans",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "warm hazel"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "light"},
    },
    "Misty": {
        "franchise": "Pokemon",
        "gender": "Female",
        "costume": "a yellow crop tank top, red suspender shorts, and red sneakers",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "hair_style": "high ponytail", "eye_color": "green"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "fair"},
    },

    # --- Pokemon (the Pokemon themselves) --------------------------------
    "Pikachu": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a round chubby body of bright yellow fur with two brown stripes on the "
                   "back, small stubby arms, and a jagged brown lightning-bolt tail",
        "mask": "a round yellow Pikachu face with red circular cheek pouches, a tiny nose, "
                "and long pointed ears tipped in black",
        "physique": {"body_type": "plump", "height": "very petite"},
    },
    "Charizard": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering orange draconic body with a cream belly, broad blue-green "
                   "membranous wings, clawed limbs, and a long tail ending in a burning flame",
        "mask": "a fierce orange dragon face with a blunt horned snout, sharp teeth, and "
                "narrow teal eyes",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Bulbasaur": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a squat blue-green four-legged body with darker spots and a large green "
                   "plant bulb sprouting from the back",
        "mask": "a wide blue-green Bulbasaur face with large red eyes and a small fanged smile",
        "physique": {"body_type": "stocky", "height": "very petite"},
    },
    "Squirtle": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a small bipedal blue body with stubby limbs and a sturdy brown shell with "
                   "a cream underside and a short curled tail",
        "mask": "a friendly blue Squirtle face with large brown eyes and rounded cheeks",
        "physique": {"body_type": "stocky", "height": "very petite"},
    },
    "Eevee": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a small brown furry four-legged body with a thick fluffy cream collar "
                   "ruff and a bushy cream-tipped tail",
        "mask": "a fox-like Eevee face with big dark eyes and tall rounded brown ears",
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Jigglypuff": {
        "franchise": "Pokemon",
        "gender": "Female",
        "covers_face": True,
        "costume": "a round balloon-like pink body with stubby arms and feet and a small "
                   "curled tuft of fur on the forehead",
        "mask": "a round pink Jigglypuff face with enormous blue eyes and a tiny mouth",
        "physique": {"body_type": "plump", "height": "very petite"},
    },
    "Snorlax": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "an enormous round dark blue-green body with a broad cream belly, stubby "
                   "clawed limbs, and a perpetually drowsy slouch",
        "mask": "a sleepy Snorlax face with closed eyes, a wide mouth, and cat-like ears",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Gengar": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a round squat dark purple shadow body covered in small spikes along the "
                   "back, with stubby clawed limbs",
        "mask": "a mischievous Gengar face with a wide toothy grin and round red eyes",
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Mewtwo": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tall sleek bipedal gray-and-purple feline-humanoid body with a long "
                   "tube running from the back of the skull to the spine and a thick curling tail",
        "mask": "a sculpted gray Mewtwo face with a small snout, a defined brow, and piercing "
                "violet eyes",
        "physique": {"body_type": "lean", "height": "very tall"},
    },
    "Psyduck": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a stout bipedal pale-yellow duck body with stubby webbed feet and small "
                   "arms raised to clutch the head",
        "mask": "a blank Psyduck face with a flat orange bill, vacant staring eyes, and three "
                "stray tufts of hair",
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Lucario": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a lean bipedal blue-and-black jackal-like body with cream chest fur, a "
                   "spike on the back of each hand and the chest, and a swishing tail",
        "mask": "a blue-and-black Lucario jackal face with red eyes, a black mask-like muzzle, "
                "and long backward-pointing ears with sensory appendages",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Meowth": {
        "franchise": "Pokemon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a slender cream-furred bipedal cat body with a curled brown-tipped tail "
                   "and small paws",
        "mask": "a cream Meowth cat face with a gleaming gold oval charm set in the forehead, "
                "whiskers, and a sly grin",
        "physique": {"body_type": "slim", "height": "petite"},
    },

    # --- Street Fighter (more) -------------------------------------------
    "Sakura Kasugano": {
        "franchise": "Street Fighter",
        "gender": "Female",
        "costume": "a white sailor-style school uniform with a red neckerchief, red "
                   "gloves, white headband, and red sneakers",
        "signature": {"hair_color": "warm brown", "hair_length": "very short",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "light"},
    },
    "Juri Han": {
        "franchise": "Street Fighter",
        "gender": "Female",
        "costume": "a purple sleeveless catsuit with cut-outs, a spider-web motif, and a "
                   "glowing eye-implant device over one eye",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_style": "pigtails", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Vega": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red sash and a snake-print loincloth over a bare chest, with a "
                   "steel three-pronged claw on one hand",
        "mask": "a white kabuki-style face mask",
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "Sagat": {
        "franchise": "Street Fighter",
        "gender": "Male",
        "costume": "a purple kickboxing waist-wrap with bandaged hands and feet, an "
                   "eyepatch, and a long scar across a bare, massive chest",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "tan"},
    },

    # --- Mortal Kombat (more) --------------------------------------------
    "Mileena": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a magenta ninja outfit with a veil lowered to reveal a wide mouth "
                   "of long sharp Tarkatan fangs, with twin sai at the hips",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Sindel": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a purple-and-black royal gown with a high collar and long gloves",
        "signature": {"hair_color": "white", "hair_length": "hip length",
                      "hair_texture": "thick and voluminous", "eye_color": "violet-gray"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Jade": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a green ninja outfit with a lowered veil, gold trim, and a metal "
                   "headpiece",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "warm brown"},
        "prop": "a tall metal-tipped bo staff",
    },
    "Sonya Blade": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a green-and-black military tank top with combat trousers, fingerless "
                   "gloves, and a thigh holster",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "toned", "height": "average height", "skin_tone": "fair"},
    },
    "Smoke": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "covers_face": True,
        "costume": "a gray-and-black ninja outfit wreathed in faint curling smoke",
        "mask": "a gray ninja mask covering the lower face",
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Shang Tsung": {
        "franchise": "Mortal Kombat",
        "gender": "Male",
        "costume": "ornate dark sorcerer's robes with a high collar, bone shoulder "
                   "ornaments, and a long thin mustache and beard",
        "signature": {"hair_color": "near black", "hair_length": "long",
                      "facial_hair": "van dyke", "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "light"},
    },

    # --- Tekken ----------------------------------------------------------
    "Jin Kazama": {
        "franchise": "Tekken",
        "gender": "Male",
        "costume": "a hooded black jacket with flame patterns and gold trim over a bare "
                   "chest, and black trousers",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "Kazuya Mishima": {
        "franchise": "Tekken",
        "gender": "Male",
        "costume": "a dark business suit worn open over a bare chest, with a "
                   "swept-back hairstyle",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "Nina Williams": {
        "franchise": "Tekken",
        "gender": "Female",
        "costume": "a purple tactical catsuit with buckles and a thigh holster",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Overwatch (more) ------------------------------------------------
    "Symmetra": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a sleek blue-and-gold bodysuit with a glowing hard-light device "
                   "over one forearm",
        "signature": {"hair_color": "near black", "hair_length": "chin length bob",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "warm brown"},
    },
    "Zarya": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a teal-and-pink armored bodysuit on a towering heavily muscled figure of immense "
                   "proportions, with a glowing particle-cannon harness",
        "signature": {"hair_color": "hot pink", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },
    "Sombra": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a purple-and-black stealth bodysuit with glowing circuitry and a "
                   "shaved-side undercut",
        "signature": {"hair_color": "near black", "hair_length": "chin length bob",
                      "eye_color": "amber"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "warm tan"},
    },
    "Reaper": {
        "franchise": "Overwatch",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black hooded trench coat with bandoliers over dark armor, and "
                   "twin shotguns",
        "mask": "a white skull-faced mask",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Genji": {
        "franchise": "Overwatch",
        "gender": "Male",
        "covers_face": True,
        "costume": "a sleek green-and-silver cyborg ninja body with exposed servos and "
                   "a katana on the back",
        "mask": "a smooth metal faceplate with a glowing green visor slit",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Hanzo": {
        "franchise": "Overwatch",
        "gender": "Male",
        "costume": "a dark sleeveless outfit with one bare arm sleeved in a blue dragon "
                   "tattoo, gold-tipped boots, and a recurve bow",
        "signature": {"hair_color": "charcoal gray", "hair_length": "very short",
                      "facial_hair": "goatee", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
        "prop": "a glowing blue recurve storm bow",
    },
    "Soldier 76": {
        "franchise": "Overwatch",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue tactical jacket with a white '76', a pulse rifle, and combat gear",
        "mask": "a face-concealing combat mask with a glowing red visor",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Reinhardt": {
        "franchise": "Overwatch",
        "gender": "Male",
        "covers_face": True,
        "costume": "an enormous suit of blue crusader power armor on a towering figure of immense armored "
                   "proportions, with a rocket-hammer",
        "mask": "a heavy blue crusader helmet with a barred visor",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Ana": {
        "franchise": "Overwatch",
        "gender": "Female",
        "costume": "a tactical hooded outfit with a sniper rifle, a single eye tattoo, "
                   "and an eyepatch over one eye",
        "signature": {"hair_color": "white", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "fit", "height": "average height", "skin_tone": "warm tan"},
    },
    "Junkrat": {
        "franchise": "Overwatch",
        "gender": "Male",
        "costume": "scorched ragged shorts, a tire of grenades, a peg-leg prosthetic, "
                   "and soot smudges over bare skin, with wild singed hair",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },

    # --- League of Legends (more) ----------------------------------------
    "Vi": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a pink-tinted undercut, a studded jacket over bandaged arms, and "
                   "enormous mechanical gauntlets",
        "signature": {"hair_color": "hot pink", "hair_length": "very short",
                      "eye_color": "violet-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Caitlyn": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a dark Piltover lawkeeper coat with purple trim, a tall top hat, "
                   "and a long rifle",
        "signature": {"hair_color": "near black", "hair_length": "hip length",
                      "hair_texture": "sleek straight", "eye_color": "blue-gray"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
        "prop": "a long ornate Piltover rifle",
    },
    "Akali": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a green ninja crop-top outfit with a face mask pulled down around "
                   "the neck and a kama on a chain",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_style": "high ponytail", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Lux": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a white-and-gold mage outfit with a glowing light-crystal wand",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },

    # --- Final Fantasy / Kingdom Hearts / Zelda (more) -------------------
    "Noctis": {
        "franchise": "Final Fantasy XV",
        "gender": "Male",
        "costume": "an all-black outfit with a fitted jacket, skull-print shirt, and "
                   "many buckles",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Terra Branford": {
        "franchise": "Final Fantasy VI",
        "gender": "Female",
        "costume": "a red leotard with a yellow cape, red boots, and gold armlets",
        "signature": {"hair_color": "mint green", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Rikku": {
        "franchise": "Final Fantasy X",
        "gender": "Female",
        "costume": "a green bikini top, a tan pleated skirt, an orange scarf, and a "
                   "yellow-and-green arm glove",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "loose braids", "eye_color": "green"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "warm tan"},
    },
    "Sora": {
        "franchise": "Kingdom Hearts",
        "gender": "Male",
        "costume": "a red-and-black jumpsuit with oversized yellow shoes, a crown "
                   "pendant, and big white gloves",
        "signature": {"hair_color": "warm brown", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
        "prop": "a Keyblade shaped like a giant silver key with a crown-tooth tip",
    },
    "Kairi": {
        "franchise": "Kingdom Hearts",
        "gender": "Female",
        "costume": "a pink halter dress with a zip front over white-and-black shorts",
        "signature": {"hair_color": "deep red", "hair_length": "shoulder length",
                      "eye_color": "violet-gray"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Riku": {
        "franchise": "Kingdom Hearts",
        "gender": "Male",
        "costume": "a yellow-and-black vest, baggy blue trousers, and fingerless gloves",
        "signature": {"hair_color": "silver", "hair_length": "shoulder length",
                      "hair_texture": "sleek straight", "eye_color": "emerald"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Sheik": {
        "franchise": "The Legend of Zelda",
        "gender": "Female",
        "costume": "a blue-and-white Sheikah bodysuit with wrappings, an eye-of-truth "
                   "tabard, and a cowl with a hanging head-wrap",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Midna": {
        "franchise": "The Legend of Zelda",
        "gender": "Female",
        "costume": "an ornate stone helmet-crown, with uniform, all-over black-and-teal Twili "
                   "skin and glowing turquoise patterns",
        "signature": {"hair_color": "orange", "hair_length": "long"},
        "physique": {"body_type": "slim", "height": "petite"},
    },
    "Urbosa": {
        "franchise": "The Legend of Zelda",
        "gender": "Female",
        "costume": "ornate Gerudo jewelry and a teal-and-gold sarong outfit with a "
                   "feathered headdress, on a tall commanding frame",
        "signature": {"hair_color": "deep red", "hair_length": "very short",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "warm tan"},
    },

    # --- Disney heroes (more) --------------------------------------------
    "Esmeralda": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a white off-shoulder blouse, a teal corset, a purple-sashed skirt, "
                   "gold hoop earrings, and a gold coin armband",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "emerald"},
        "physique": {"body_type": "hourglass", "height": "average height", "skin_tone": "warm tan"},
    },
    "Megara": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a lavender one-shoulder Grecian gown with a purple sash",
        "signature": {"hair_color": "auburn", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "violet-gray"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Kida": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a teal bandeau and loincloth with gold armbands and anklets, a "
                   "crystal pendant, and blue tribal face markings",
        "signature": {"hair_color": "white", "hair_length": "very long",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "caramel"},
    },
    "Jane Porter": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a yellow Victorian skirt and a white blouse with a high collar",
        "signature": {"hair_color": "warm brown", "hair_length": "shoulder length",
                      "hair_style": "messy bun", "eye_color": "medium brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Aladdin": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a sleeveless purple vest over a bare chest, baggy white trousers, a "
                   "red fez, and a long red sash",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "warm tan"},
    },
    "Hercules": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a Grecian armor skirt and sandals with gold bracers over a bare "
                   "muscular chest, and a blue cape",
        "signature": {"hair_color": "auburn", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "tall", "skin_tone": "light"},
    },
    "Maui": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a leaf skirt over a huge frame covered in an even, all-over coat of "
                   "animated dark tribal tattoos, with a bone hook",
        "signature": {"hair_color": "jet black", "hair_length": "shoulder length",
                      "hair_texture": "thick and voluminous", "eye_color": "dark brown"},
        # 'tattoos' isn't a material the colour-anchor regex catches, and the tattoo
        # coat would otherwise suppress his brown skin entirely; anchor it explicitly.
        "skin": "warm brown",
        "physique": {"body_type": "stocky", "height": "very tall"},
        "prop": "a giant carved bone fish-hook",
    },

    # --- Disney villains (more) ------------------------------------------
    "Jafar": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a black-and-red robe with a tall striped collar, a horned headpiece, "
                   "and a thin curled beard",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "van dyke", "eye_color": "dark brown"},
        "physique": {"body_type": "very slim", "height": "very tall", "skin_tone": "light"},
        "prop": "a golden cobra-headed staff with red gem eyes",
    },
    "Hades": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a charcoal-grey toga over smooth, flawless blue-grey skin, with a crown of "
                   "blue flame for hair",
        "signature": {"eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Gaston": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a red tunic with a wide black collar, yellow gloves, brown boots, "
                   "and a small red cape, on a hugely broad frame",
        "signature": {"hair_color": "jet black", "hair_length": "ear length",
                      "hair_style": "low ponytail", "eye_color": "blue-gray"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "light"},
    },
    "Captain Hook": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a red captain's coat with lace cuffs, a large plumed hat, thigh "
                   "boots, a curled mustache, and a polished steel hook for the left hand",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "hair_texture": "curly", "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Frollo": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "long purple-and-black judge's robes with a red-lined cape and a "
                   "rounded black-and-purple hat",
        "signature": {"hair_color": "silver", "hair_length": "ear length",
                      "eye_color": "dark gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "very pale"},
    },
    "Dr. Facilier": {
        "franchise": "Disney",
        "gender": "Male",
        "costume": "a purple tailcoat with a red-and-black waistcoat, a feathered top "
                   "hat, a skull cane, and a thin pencil mustache",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "amber"},
        "physique": {"body_type": "very slim", "height": "tall", "skin_tone": "dark brown"},
    },

    # --- Marvel (more; incl. huge characters) ----------------------------
    "Mister Fantastic": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue Fantastic Four bodysuit with a white '4' chest emblem",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Human Torch": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of living yellow-orange flame over the whole "
                   "body, glowing white-hot at the core and trailing fire off the "
                   "shoulders and arms, with a circular Fantastic Four '4' emblem "
                   "burning brighter on the chest",
        "mask": "a head of living yellow-orange flame with glowing white eyes and no "
                "solid features",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "The Thing": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "blue trunks, and uniform, all-over craggy orange rock-like skin with a heavy "
                   "brow and a bald rocky head",
        "signature": {"eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Green Goblin": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a purple tunic and hood over green scaled armor with a satchel of "
                   "pumpkin bombs, riding a bat-winged glider",
        "mask": "a leering green goblin mask with pointed ears",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Doctor Octopus": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a long green coat over a teal jumpsuit, round tinted glasses, and "
                   "four articulated mechanical tentacle-arms rising from a back harness",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "blunt bangs", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "light"},
    },
    "Mysterio": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green-and-purple caped bodysuit with a fishscale chestplate and a "
                   "cape, hands wreathed in green mist",
        "mask": "a smoky translucent glass dome helmet",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Kingpin": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an immaculate white three-piece suit with a diamond-topped cane, on "
                   "an imposingly large figure of immense mass and towering stature, and a clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "blue-gray"},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },
    "Red Skull": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green military uniform under a long black leather coat",
        "mask": "a skinless crimson skull-like face",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Kang the Conqueror (Classic)": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green-and-purple armored battle suit with a high collar, layered "
                   "plating, and gauntlets",
        "mask": "a purple full-face mask under a green helmet",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Baron Zemo": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tailored dark coat over a fitted combat suit",
        "mask": "a purple balaclava-style mask trimmed with a band of grey fur",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Abomination": {
        "franchise": "Marvel",
        "gender": "Male",
        "bald": True,
        "costume": "torn dark trousers, with uniform, all-over green-grey scaly reptilian skin, "
                   "ridged bony plates over the brow and spine, pointed finned ears, and a gaunt "
                   "monstrous face, on an imposingly large hulking figure of towering stature",
        "eyes": "pale green",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Pyro": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a black bodysuit with orange flame-pattern accents and a fuel-tank "
                   "harness feeding wrist flame-igniters",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a whip of fire curling up from one outstretched hand",
    },
    "Sebastian Shaw": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an 18th-century Hellfire Club outfit of a ruffled white shirt, a "
                   "dark brocade waistcoat and tailcoat, and a black cravat",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "mutton chops", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Professor X": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a sharp business suit, seated in a chrome hover-wheelchair, with a "
                   "clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "blue-gray"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "fair"},
    },
    "Juggernaut": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "bulky crimson-and-brown armor over an enormously tall imposing figure of immense proportions",
        "mask": "a huge rounded crimson helmet with narrow eye-slits",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Apocalypse": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "heavy blue-and-grey techno-organic armor with cabling, over smooth, flawless "
                   "blue-grey skin, on a towering figure of overwhelming size and power",
        "signature": {"eye_color": "bright blue"},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Galactus": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "massive purple-and-blue cosmic armor on a planet-sized figure of cosmic colossal scale",
        "mask": "a towering horned purple cosmic helmet",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Titania": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a purple-and-white sleeveless high-cut costume with white gloves and boots, "
                   "over smooth, flawless orange-toned skin, with a strong jaw and bold features "
                   "on a powerfully muscular frame - towering and gigantic with overwhelming scale and proportion",
        "eyes": "green",
        "signature": {"hair_color": "deep red", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },

    # --- DC (more; incl. huge characters) --------------------------------
    "Two-Face": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a suit split down the middle - one half pristine, the other half "
                   "charred and tattered - over a face badly scarred on the left side",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "The Riddler": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a green suit covered in purple question marks, a green bowler hat, "
                   "and a domino mask",
        "signature": {"hair_color": "warm brown", "hair_length": "very short",
                      "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a green cane topped with a golden question mark",
    },
    "The Penguin": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black tailcoat tuxedo, a purple top hat, a monocle, and a long "
                   "cigarette holder, on a short rotund frame",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark gray"},
        "physique": {"body_type": "plump", "height": "short", "skin_tone": "very pale"},
        "prop": "a black umbrella with a pointed tip",
    },
    "Scarecrow": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tattered dark coat and ragged rope-bound clothing with straw "
                   "poking from the cuffs",
        "mask": "a stitched burlap sack mask with a frayed noose around the neck",
        "physique": {"body_type": "very slim", "height": "tall"},
    },
    "Mr. Freeze": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a bulky silver-and-blue cryo-suit with coolant tubes and a glowing "
                   "chest control panel",
        "mask": "a clear domed glass helmet with glowing red goggles",
        "physique": {"body_type": "stocky", "height": "tall"},
        "prop": "a heavy blue freeze gun with a coiled hose",
    },
    "Sinestro": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black-and-yellow Sinestro Corps uniform with a yellow lantern emblem and a "
                   "glowing yellow power ring worn on the finger, over smooth, flawless red "
                   "skin, with a thin black mustache",
        "signature": {"facial_hair": "mustache", "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Kilowog": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "a black-and-green Green Lantern uniform with a circular lantern emblem and a "
                   "glowing green power ring worn on the finger, over an even, all-over coat of "
                   "pink-grey ridged Bolovaxian skin, with a heavy tusked underbite and small "
                   "pointed ears, on a massive muscular frame",
        "eyes": "solid pink",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Tomar-Re": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "a black-and-green Green Lantern uniform with a circular lantern emblem and a "
                   "glowing green power ring worn on the finger, over smooth, flawless orange "
                   "Xudarian skin, with a tall red fin-like crest running over the head and a "
                   "small beaked mouth",
        "eyes": "large solid black",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Salaak": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "a black-and-green Green Lantern uniform on a gaunt four-armed frame, with a "
                   "circular lantern emblem and a glowing green power ring worn on the finger, "
                   "over smooth, flawless orange-brown alien skin, with a long elongated head "
                   "and a thin slit mouth",
        "eyes": "narrow yellow",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Ch'p": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "a stylized small-statured Green Lantern cosplay with an even, "
                   "all-over coat of brown squirrel-like fur, a bushy tail, large dark "
                   "eyes, and rounded ears, wearing a green-and-black tunic with a "
                   "circular lantern emblem and a glowing green power ring worn on the finger",
        "eyes": "large solid black",
        "physique": {"body_type": "petite and slim", "height": "petite"},
    },
    "Atrocitus": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "a red-and-black Red Lantern uniform with a clawed red lantern emblem and a "
                   "glowing red power ring worn on the finger, over smooth, flawless deep-red "
                   "skin with bony ridges, on a towering figure of overwhelming size",
        "eyes": "burning red",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Larfleeze": {
        "franchise": "DC",
        "gender": "Male",
        "bald": True,
        "costume": "tattered orange Agent Orange robes with a glowing orange power ring worn on "
                   "the finger, over uniform, all-over leathery orange skin, with a gaunt "
                   "hunched frame, pointed ears, and a wide jagged grin",
        "eyes": "glowing orange",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Brainiac": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a pink Coluan harness over smooth, flawless green metallic skin, with a "
                   "clean-shaven bald head studded with control nodes",
        "signature": {"facial_hair": "clean shaven", "eye_color": "bright green"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Lex Luthor": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a green-and-purple armored warsuit with a glowing kryptonite chest "
                   "core, and a clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "John Constantine": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a tan trench coat over a white shirt and loosened black tie",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "blue-gray"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Lobo": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "black biker leathers with chains and spikes over smooth, flawless "
                   "chalk-white skin, on an enormously tall hulking figure of imposing stature",
        "eyes": "red on black sclera",
        "signature": {"hair_color": "jet black", "hair_length": "long"},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Giganta": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a torn leopard-print one-shoulder dress, scaled up to a colossal "
                   "fifty-foot-tall figure of overwhelmingly gigantic scale and proportion",
        "signature": {"hair_color": "deep red", "hair_length": "very long",
                      "eye_color": "green"},
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "warm tan"},
    },
    "Giant-Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red-and-blue size-changing suit grown to a colossal building-high "
                   "figure of overwhelming gigantic scale",
        "mask": "a red domed helmet with antennae and a silver faceplate",
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },

    # --- Movie sci-fi, action & monster icons ----------------------------
    "Predator": {
        "franchise": "Predator",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering hulking figure of immense alien proportions with mottled reptilian skin, a fishnet "
                   "mesh underlayer, segmented armor, wrist blades, and long dreadlock-like "
                   "tendrils, with a shoulder plasma cannon",
        "mask": "a scarred bio-metal hunter's mask with twin laser sights",
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "RoboCop": {
        "franchise": "RoboCop",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full cybernetic armour shell, no bare skin for jewellery
        "costume": "a full suit of matte gunmetal cybernetic police armor with exposed "
                   "servos and a holstered sidearm",
        "mask": "a sleek steel helmet leaving only a stern jaw exposed",
        "physique": {"body_type": "stocky", "height": "tall"},
    },
    "Cylon Centurion": {
        "franchise": "Battlestar Galactica",
        "gender": "Male",  # source-gender scope only; Centurions are genderless robots
        "covers_face": True,
        "covers_body": True,  # all-metal robot shell, no bare skin for jewellery
        "costume": "a towering humanoid war robot sheathed in an even, smooth coat of "
                   "polished gunmetal-chrome armor plating, with a sculpted segmented "
                   "torso, articulated limbs, and clawed armored gauntlets",
        "mask": "a featureless chrome helmeted head with a single horizontal red "
                "eye-slit scanning side to side",
    },
    "The Terminator": {
        "franchise": "The Terminator",
        "gender": "Male",
        "costume": "a black leather jacket, dark jeans, heavy boots, and dark "
                   "sunglasses, with battle-damaged skin revealing chrome endoskeleton beneath",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "stocky", "height": "tall", "skin_tone": "fair"},
    },
    "Xenomorph": {
        "franchise": "Alien",
        "gender": "Male",
        "covers_face": True,
        "costume": "a lithe biomechanical black exoskeleton with ribbed limbs, a "
                   "segmented dorsal spine, clawed hands, and a long bladed tail",
        "mask": "a smooth elongated eyeless black domed head with bared inner jaws",
        "physique": {"body_type": "lean", "height": "very tall"},
    },
    "Ellen Ripley": {
        "franchise": "Alien",
        "gender": "Female",
        "costume": "a grey jumpsuit cinched with a utility harness, with a flamethrower "
                   "slung at the hip",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_texture": "curly", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Sarah Connor": {
        "franchise": "The Terminator",
        "gender": "Female",
        "costume": "a black tank top, cargo trousers, fingerless gloves, dark "
                   "sunglasses, and a slung assault rifle",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "toned", "height": "average height", "skin_tone": "fair"},
    },
    "Mad Max": {
        "franchise": "Mad Max",
        "gender": "Male",
        "costume": "a battered black leather road-warrior jacket with one armored "
                   "shoulder brace, dusty trousers, and a knee brace",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "warm tan"},
    },
    "Snake Plissken": {
        "franchise": "Escape from New York",
        "gender": "Male",
        "costume": "a black tank top, dark trousers, fingerless gloves, and a black "
                   "eyepatch over the left eye",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Judge Dredd": {
        "franchise": "Judge Dredd",
        "gender": "Male",
        "covers_face": True,
        "costume": "black-and-blue armored law-enforcement gear with a gold eagle "
                   "shoulder pad, a chunky utility belt, and a holstered Lawgiver pistol",
        "mask": "a full blue helmet with a black visor leaving only a grim mouth exposed",
        "physique": {"body_type": "stocky", "height": "tall"},
    },

    # --- Other comics / games --------------------------------------------
    "Invincible": {
        "franchise": "Invincible",
        "gender": "Male",
        "costume": "a blue-and-yellow superhero suit with a black domino mask around "
                   "the eyes",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Omni-Man": {
        "franchise": "Invincible",
        "gender": "Male",
        "costume": "a white bodysuit with a red cape and a stylized chest emblem, with "
                   "a thick grey-streaked mustache",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },
    "Hellboy": {
        "franchise": "Hellboy",
        "gender": "Male",
        "costume": "a brown trench coat over a belt of pouches, smooth, flawless brick-red skin, "
                   "two filed-down horn stumps on the forehead, and a massive stone right hand",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "amber"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "He-Man": {
        "franchise": "Masters of the Universe",
        "gender": "Male",
        "costume": "a brown fur loincloth, a steel chest harness, brown furred boots, "
                   "and a bare, hugely muscled chest",
        "signature": {"hair_color": "dark blonde", "hair_length": "ear length",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "tan"},
        "prop": "a broad-bladed Power Sword",
    },
    "Skeletor": {
        "franchise": "Masters of the Universe",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue hooded cloak over a purple-and-blue armored harness",
        "mask": "a glowing bare yellow skull face under a blue hood",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a ram-skull-headed purple staff",
    },
    "She-Ra": {
        "franchise": "Masters of the Universe",
        "gender": "Female",
        "costume": "a white dress with a gold tiara, gold arm cuffs, a red cape, and "
                   "knee-high white-and-gold boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_texture": "thick and voluminous", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a jewel-hilted golden Sword of Protection",
    },
    "Doom Slayer": {
        "franchise": "Doom",
        "gender": "Male",
        "covers_face": True,
        "costume": "a heavy suit of green Praetor combat armor with battle scoring",
        "mask": "a green armored helmet with a dark angular visor",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Agent 47": {
        "franchise": "Hitman",
        "gender": "Male",
        "costume": "a sharp black suit with a red tie, black gloves, and a clean-shaven "
                   "bald head bearing a barcode tattoo at the back",
        "signature": {"facial_hair": "clean shaven", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Senua": {
        "franchise": "Hellblade",
        "gender": "Female",
        "costume": "layered leather Pict warrior garb with body wraps, and teal war "
                   "paint over half the face fading into a dark handprint",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "loose braids", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Shadowheart": {
        "franchise": "Baldur's Gate 3",
        "gender": "Female",
        "costume": "dark studded leather cleric armor bearing a silver teardrop symbol "
                   "of Shar",
        "signature": {"hair_color": "near black", "hair_length": "chin length bob",
                      "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Lae'zel": {
        "franchise": "Baldur's Gate 3",
        "gender": "Female",
        "costume": "spiked Githyanki plate armor over uniform, all-over pale green mottled skin, "
                   "with tightly drawn-back hair",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_style": "top knot"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Astarion": {
        "franchise": "Baldur's Gate 3",
        "gender": "Male",
        "costume": "an ornate ruffled grey shirt and dark embroidered waistcoat, with "
                   "pale vampiric skin and a pair of small fangs",
        "eyes": "crimson",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "hair_texture": "curly"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "very pale"},
    },

    # --- Horror / slasher icons ------------------------------------------
    "Freddy Krueger": {
        "franchise": "A Nightmare on Elm Street",
        "gender": "Male",
        "costume": "a dirty red-and-green striped sweater, a brown fedora, and a bladed "
                   "metal glove on the right hand, over heavily burn-scarred skin and a "
                   "scarred bald scalp",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Jason Voorhees": {
        "franchise": "Friday the 13th",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tattered dark jacket over ragged filthy work clothes on a hulking frame",
        "mask": "a stained white hockey mask with triangular vents",
        "physique": {"body_type": "stocky", "height": "very tall"},
        "prop": "a long rusted machete",
    },
    "Michael Myers": {
        "franchise": "Halloween",
        "gender": "Male",
        "covers_face": True,
        "costume": "dark blue mechanic's coveralls",
        "mask": "an expressionless pale white mask with dark empty eye holes",
        "physique": {"body_type": "athletic", "height": "very tall"},
        "prop": "a large kitchen knife",
    },
    "Pennywise": {
        "franchise": "IT",
        "gender": "Male",
        "costume": "a silver-grey ruffled antique clown costume with red pom-poms, "
                   "white clown face paint, a red-painted grin, and a high domed forehead "
                   "with orange hair tufts at the sides",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "very pale"},
        "prop": "a single red helium balloon on a string",
    },
    "Pinhead": {
        "franchise": "Hellraiser",
        "gender": "Male",
        "covers_face": True,
        "costume": "a long black leather Cenobite robe with ritual hooks and chains",
        "mask": "a pale head carved in a precise grid studded with black pins",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Leatherface": {
        "franchise": "The Texas Chain Saw Massacre",
        "gender": "Male",
        "covers_face": True,
        "costume": "a stained butcher's apron over a dirty shirt and tie on a heavy frame",
        "mask": "a mask of stitched-together dried human skin",
        "physique": {"body_type": "stocky", "height": "very tall"},
        "prop": "a roaring chainsaw",
    },
    "Ghostface": {
        "franchise": "Scream",
        "gender": "Male",
        "covers_face": True,
        "costume": "a long flowing black hooded death-robe with ragged sleeves",
        "mask": "a white elongated ghost mask with a gaping black mouth and eyes",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a bloodied hunting knife",
    },
    "Chucky": {
        "franchise": "Child's Play",
        "gender": "Male",
        "costume": "doll-sized denim dungarees over a colorful striped shirt and "
                   "sneakers, with a freckled doll face crossed by stitched scars",
        "signature": {"hair_color": "deep red", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "very petite", "skin_tone": "fair"},
        "prop": "a kitchen knife",
    },
    "Pyramid Head": {
        "franchise": "Silent Hill",
        "gender": "Male",
        "covers_face": True,
        "costume": "a filthy blood-stained butcher's smock over a grimy, hulking frame",
        "mask": "a huge rusted iron pyramid-shaped helmet",
        "physique": {"body_type": "stocky", "height": "very tall"},
        "prop": "a colossal rusted great-knife dragged along the ground",
    },

    # --- Lord of the Rings (more) ----------------------------------------
    "Sauron": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "covers_face": True,
        "costume": "towering jet-black plate armor with spiked pauldrons and a "
                   "spiked gauntlet bearing the One Ring",
        "mask": "a spiked black war helm with a narrow burning eye-slit",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Galadriel": {
        "franchise": "The Lord of the Rings",
        "gender": "Female",
        "costume": "a flowing white-and-silver elven gown with trailing sleeves",
        "signature": {"hair_color": "light blonde", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "porcelain"},
    },
    "Arwen": {
        "franchise": "The Lord of the Rings",
        "gender": "Female",
        "costume": "a deep blue-and-grey velvet elven gown with embroidered sleeves and "
                   "a silver circlet",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "gray"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Eowyn": {
        "franchise": "The Lord of the Rings",
        "gender": "Female",
        "costume": "steel shieldmaiden armor with a chainmail coif over a layered "
                   "green-and-white gown",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Boromir": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "layered Gondorian leather armor with vambraces and a fur-collared cloak",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "facial_hair": "short beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a curved white war-horn banded with silver",
    },
    "Saruman": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "long flowing white wizard robes with wide sleeves",
        "signature": {"hair_color": "white", "hair_length": "very long",
                      "facial_hair": "full beard", "eye_color": "dark gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "very pale"},
        "prop": "a tall white wizard's staff",
    },

    # --- Harry Potter (more) ---------------------------------------------
    "Harry Potter": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "black Hogwarts robes with a red-and-gold Gryffindor tie, round "
                   "glasses, and a lightning-bolt scar on the forehead",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "eye_color": "bright green"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
        "prop": "a slender wooden wand",
    },
    "Ron Weasley": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "black Hogwarts robes with a red-and-gold Gryffindor scarf, over "
                   "freckled skin",
        "signature": {"hair_color": "bright red", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Albus Dumbledore": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "ornate midnight-blue star-patterned wizard robes with a tall "
                   "pointed hat and half-moon spectacles",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "facial_hair": "full beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "a long knobbled wooden wand",
    },
    "Severus Snape": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "layered black buttoned robes under a long billowing black cloak",
        "signature": {"hair_color": "jet black", "hair_length": "shoulder length",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "very pale"},
    },
    "Lord Voldemort": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "long flowing black robes over smooth, flawless chalk-white skin, with a "
                   "clean-shaven bald head and flat snake-like slits for a nose",
        "eyes": "crimson with vertical slit pupils",
        "signature": {"facial_hair": "clean shaven"},
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a pale bone-white wand",
    },
    "Bellatrix Lestrange": {
        "franchise": "Harry Potter",
        "gender": "Female",
        "costume": "a black gothic corset gown with tattered lace, heavy silver rings, "
                   "and wild unkempt hair",
        "signature": {"hair_color": "near black", "hair_length": "very long",
                      "hair_texture": "curly", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },
    "Draco Malfoy": {
        "franchise": "Harry Potter",
        "gender": "Male",
        "costume": "black Hogwarts robes with a green-and-silver Slytherin tie",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "blue-gray"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "very pale"},
    },
    "Luna Lovegood": {
        "franchise": "Harry Potter",
        "gender": "Female",
        "costume": "Hogwarts robes worn with radish earrings, a butterbeer-cork "
                   "necklace, and rainbow spectrespecs pushed up on the head",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "pale blue"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },

    # --- Star Wars (more) ------------------------------------------------
    "General Grievous": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hunched cyborg body of white-and-grey droid plating over an "
                   "exposed organic sac, with four arms and a tattered cape",
        "mask": "a bone-white skull-like cyborg faceplate with narrow reptilian eyes",
        "physique": {"body_type": "lean", "height": "very tall"},
    },
    "Count Dooku": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "elegant dark Sith robes with a long black cape clasped by a "
                   "shoulder chain",
        "signature": {"hair_color": "silver", "hair_length": "very short",
                      "facial_hair": "van dyke", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "an ignited lightsaber with a curved silver hilt and a red blade",
    },
    "Jango Fett": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "blue-and-silver Mandalorian armor with a jetpack and twin blaster "
                   "holsters",
        "mask": "a blue-and-silver Mandalorian helmet with a T-shaped visor",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Cad Bane": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a long duster coat and a wide-brimmed hat over smooth, flawless blue skin, "
                   "with a clean-shaven bald blue head, breathing tubes running to the cheeks, "
                   "and twin blaster holsters",
        "eyes": "glowing red",
        "signature": {"facial_hair": "clean shaven"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Grand Admiral Thrawn": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a crisp white Imperial Grand Admiral's uniform over smooth, flawless blue "
                   "skin",
        "eyes": "glowing red",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Finn": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a brown leather jacket over a grey Resistance outfit",
        "signature": {"hair_color": "jet black", "hair_length": "buzzed very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "dark brown"},
    },
    "Poe Dameron": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "an orange Resistance pilot flight suit with a chest harness",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "hair_texture": "wavy", "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
    },

    # --- Marvel (more heroes) --------------------------------------------
    "Cyclops": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue-and-yellow X-Men uniform with a ruby-quartz visor over the eyes",
        "signature": {"hair_color": "dark brown", "hair_length": "very short"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Iceman": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an even, smooth coat of translucent pale-blue ice over a lean frame, "
                   "with jagged icicle spikes along the shoulders and forearms",
        "eyes": "solid icy white",
        "signature": {},
        "skin": "icy pale-blue",  # 'ice' isn't a material the anchor regex catches
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Beast": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "torn shorts over an even, all-over coat of blue fur on a hulking "
                   "muscular frame, with pointed ears, fangs, and clawed hands",
        "eyes": "amber",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Firestar": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a yellow-and-red costume wreathed head to toe in flame, with a fiery aura",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Angel": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a red-and-white X-Factor bodysuit with enormous white feathered wings",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Colossus": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "red-and-yellow trunks over smooth, flawless polished chrome steel skin on a "
                   "huge muscular frame",
        "eyes": "steel-grey",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Kitty Pryde": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a royal blue bodysuit with golden shoulder-and-chest panels, a golden "
                   "X-buckle belt, golden gloves, blue boots, and a small golden X emblem "
                   "at the collar",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Cable": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue-and-grey tactical bodysuit with a chrome cybernetic left arm, "
                   "ammo straps, and a scar over the right eye",
        "eyes": "one glowing yellow cybernetic eye",
        "signature": {"hair_color": "white", "hair_length": "very short"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
        "prop": "a massive futuristic plasma rifle bristling with barrels",
    },
    "Bishop": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue-and-red tactical uniform with shoulder armor and a bold 'M' "
                   "tattoo over the right eye",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "goatee", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "dark brown"},
        "prop": "a large futuristic energy rifle",
    },
    "Banshee": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a green-and-yellow costume with a high collar and bat-wing membranes "
                   "stretched under the arms",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Vision": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a yellow cape and green-and-gold accents over smooth, flawless deep red "
                   "android skin, with a glowing yellow gem set in the forehead",
        "eyes": "glowing white",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Ant-Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red-and-silver size-changing suit with utility straps, shrunk to a "
                   "figure of impossibly tiny miniature proportions",
        "mask": "a red-and-silver helmet with round antennae and a dark visor",
        "size_scale": "tiny",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Hawkeye": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a purple-and-black tactical archer outfit with a quiver of arrows on "
                   "the back",
        "signature": {"hair_color": "dark blonde", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a recurve combat bow drawn with a trick arrow",
    },
    "War Machine": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a bulky gunmetal-grey armored suit with a shoulder-mounted minigun",
        "mask": "a grey armored helmet with a glowing eye slit",
        "physique": {"body_type": "stocky", "height": "tall"},
    },
    "Falcon": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a red-and-white tactical flight suit with mechanical wings and red goggles",
        "signature": {"hair_color": "jet black", "hair_length": "buzzed very short",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
    },
    "Drax": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "grey trousers over a bare muscular torso, with smooth, flawless grey skin "
                   "covered in raised dark-red ritual tattoo scars",
        "signature": {"facial_hair": "clean shaven"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Rocket Raccoon": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an orange-and-blue flight suit on a small bipedal frame, over an even, "
                   "all-over coat of brown-and-grey raccoon fur with a black bandit-mask "
                   "of fur and a ringed tail",
        "eyes": "dark beady brown",
        "signature": {},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
        "prop": "an oversized laser blaster rifle",
    },
    "Groot": {
        "bald": True,
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "nothing but uniform, all-over brown wooden bark skin with mossy patches and "
                   "faint glowing seams, on a towering figure of immense tree-like proportions",
        "eyes": "glowing amber",
        "signature": {},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Mantis": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black-and-green high-collared outfit over smooth, flawless pale green "
                   "skin, with two thin antennae rising from the forehead",
        "eyes": "solid black",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "average height"},
    },

    # --- DC (more heroes) ------------------------------------------------
    "Darkseid": {
        "bald": True,
        "franchise": "DC",
        "gender": "Male",
        "costume": "heavy blue-and-grey Apokoliptian armor over uniform, all-over grey craggy "
                   "stone-like skin, on an enormously tall figure of immense towering proportions",
        "eyes": "glowing red Omega energy",
        "signature": {},
        "size_scale": "giant",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Firestorm": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red-and-yellow jumpsuit with a nuclear-symbol chest emblem and a "
                   "flame-wreathed collar",
        "mask": "a head wholly engulfed in roaring orange flame",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Fire": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a green costume wreathed head to toe in green flame, over smooth, flawless "
                   "glowing green skin",
        "eyes": "glowing green",
        "signature": {},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Ice": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a blue-and-white costume with an icy crystalline shimmer over pale skin",
        "signature": {"hair_color": "platinum blonde", "hair_length": "long",
                      "eye_color": "ice blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },
    "Beast Boy": {
        "franchise": "DC (Teen Titans)",
        "gender": "Male",
        "costume": "a black-and-purple uniform over smooth, flawless green skin, with pointed "
                   "ears and small fangs",
        "eyes": "green",
        "signature": {"hair_color": "emerald green", "hair_length": "very short"},
        "physique": {"body_type": "slim", "height": "average height"},
    },
    "Booster Gold": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black-and-blue late-1980s superhero bodysuit with a gold star "
                   "emblem on the chest, a high gold flight collar, gold power-disc "
                   "wristbands, and a yellow visor across the eyes, with the blue costume "
                   "sweeping up around the sides, back, and top-front of the head to frame "
                   "the exposed face and golden hair",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Blue Beetle (Jaime Reyes)": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "blue chitinous scarab armor with black accents and a clawed gauntlet",
        "mask": "a smooth blue beetle-carapace helmet with large round yellow eye-lenses",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Blue Beetle (Ted Kord)": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a classic late-1980s blue spandex superhero bodysuit with black "
                   "gloves and boots, a stylized black beetle emblem on the chest, a "
                   "snug black cowl over the head, and large round black goggles, with "
                   "the lower face exposed",
        "covers_hair": True,  # snug cowl encloses the scalp; lower face shows
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Hawkman": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a bare muscular chest with green harness straps, golden Nth-metal "
                   "wings, and golden gauntlets",
        "mask": "a golden hawk-beaked helmet",
        "physique": {"body_type": "stocky", "height": "very tall"},
        "prop": "a heavy spiked mace",
    },
    "The Atom": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red-and-blue size-changing bodysuit, shrunk to a figure of impossibly "
                   "tiny miniature proportions",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "size_scale": "tiny",
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Plastic Man": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a glossy red rubbery costume with a yellow-and-black striped midsection "
                   "and white goggles, the body comically stretched and bent into impossible shapes",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Huntress": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a dark purple-and-black bodysuit with a cross emblem, a flowing purple "
                   "cape, and a black domino mask",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "blue-gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light medium"},
        "prop": "a compact crossbow",
    },

    # --- Popular villains (Marvel) ---------------------------------------
    "Sabretooth": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a brown fur-trimmed outfit over a bare chest, with a fanged snarl and "
                   "long claws",
        "eyes": "amber",
        "signature": {"hair_color": "dark blonde", "hair_length": "very long",
                      "hair_texture": "thick and voluminous", "facial_hair": "mutton chops"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },
    "Carnage": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a glistening red symbiote body of corded muscle and tendrils with "
                   "black web patterns and bladed limbs",
        "mask": "a writhing red symbiote head with a fanged maw and white eye patches",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Ultron": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering chrome-and-silver robotic body of articulated plating",
        "mask": "a polished silver robotic face with glowing red eyes and a grim metal mouth",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Kang the Conqueror": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green-and-purple armored conqueror's costume with a high collar and cape",
        "mask": "a blue full-face mask under a green hood",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Taskmaster": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "an orange-and-blue tactical costume with a brown cape and weapon straps",
        "mask": "a white skull-faced mask under a brown hood",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a sword and a round shield",
    },
    "Mister Sinister": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a black bodysuit with a high jagged collar and a long cape, over smooth, "
                   "flawless chalk-white skin, with a red diamond gem on the forehead",
        "eyes": "glowing red",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "lean", "height": "very tall"},
    },
    "Bullseye": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a dark bodysuit with white sections and weapon bandoliers",
        "mask": "a black-and-white mask with a bullseye target carved on the forehead",
        "physique": {"body_type": "athletic", "height": "tall"},
    },

    # --- Popular villains (DC) -------------------------------------------
    "Ra's al Ghul": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "ornate green-and-black League of Assassins robes with a high collar "
                   "and a flowing cape",
        "signature": {"hair_color": "salt and pepper", "hair_length": "very short",
                      "facial_hair": "van dyke", "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "light medium"},
    },
    "Reverse-Flash": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a yellow speedster bodysuit with a red lightning-bolt emblem, red "
                   "boots, and crackling red lightning",
        "eyes": "glowing red",
        "signature": {"hair_color": "dark blonde", "hair_length": "very short"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Captain Cold": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a blue insulated parka with a fur-lined hood and round black goggles",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "blue-gray"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "fair"},
        "prop": "a bulky white cold gun",
    },
    "Black Manta": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black-and-grey armored diving suit with a chest control panel",
        "mask": "a large smooth black helmet with huge round red eye-lenses",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Bizarro": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a tattered inside-out Superman costume with a reversed black-and-grey 'S', "
                   "over uniform, all-over chalk-white cracked stone-like skin",
        "eyes": "icy blue",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Silver Banshee": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black bodysuit with tattered, ragged edges and silver mystical symbols, "
                   "smooth, flawless ashen gray-white skin marked with bold black patterns "
                   "tracing across the face and body, and a torn flowing cape",
        "eyes": "glowing white in hollow blackened sockets",
        "signature": {"hair_color": "white", "hair_length": "very long",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "athletic", "height": "statuesque"},
    },

    # --- The Sandman / The Endless ---------------------------------------
    "Dream of the Endless": {
        "franchise": "The Sandman",
        "gender": "Male",
        "costume": "a flowing black robe over pale skin, with wild untamed black hair",
        "eyes": "starry black voids flecked with pinpoint stars",
        "signature": {"hair_color": "jet black", "hair_length": "shoulder length",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "very slim", "height": "tall", "skin_tone": "very pale"},
        "prop": "a leather pouch of glittering dream-sand",
    },
    "Death of the Endless": {
        "franchise": "The Sandman",
        "gender": "Female",
        "costume": "a black tank top and black jeans with a silver ankh necklace, and a "
                   "swirl of dark eyeliner forming an Eye of Horus around the right eye",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "thick and voluminous", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "very pale"},
    },
    "Delirium": {
        "franchise": "The Sandman",
        "gender": "Female",
        "costume": "mismatched colorful ragged clothing trailing tiny butterflies, over "
                   "pale skin",
        "eyes": "heterochromatic - one green and one blue, swirling with colour",
        "signature": {"hair_color": "rainbow ombre", "hair_length": "chin length bob",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "very pale"},
    },

    # --- Thundercats -----------------------------------------------------
    "Lion-O": {
        "franchise": "Thundercats",
        "gender": "Male",
        "costume": "a blue-and-orange bodysuit with one shoulder strap and clawed "
                   "gauntlets, with a wild orange-red lion's mane of hair",
        "eyes": "amber",
        "signature": {"hair_color": "orange", "hair_length": "very long",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "the Sword of Omens, a short blade with a glowing cat's-eye gem in the hilt",
    },
    "Cheetara": {
        "franchise": "Thundercats",
        "gender": "Female",
        "costume": "a form-fitting orange-and-red speed outfit with boots and arm guards, "
                   "over an even, all-over coat of golden-yellow black-spotted fur, with an "
                   "orange-red mane of hair past the shoulders",
        "eyes": "feline green",
        "signature": {"hair_color": "orange", "hair_length": "long"},
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a telescoping bo staff",
    },
    "Tygra": {
        "franchise": "Thundercats",
        "gender": "Male",
        "costume": "blue trousers over a bare chest, with an even, all-over coat of tan "
                   "tiger-striped fur",
        "eyes": "amber",
        "signature": {"hair_color": "orange", "hair_length": "long", "hair_style": "low ponytail"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Panthro": {
        "franchise": "Thundercats",
        "gender": "Male",
        "costume": "red harness straps and studded wristbands over a bare muscular chest, "
                   "with an even, all-over coat of blue-grey panther fur and a clean-shaven bald head",
        "eyes": "amber",
        "signature": {"facial_hair": "clean shaven"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Mumm-Ra": {
        "bald": True,
        "franchise": "Thundercats",
        "gender": "Male",
        "costume": "a black headdress and a crimson cape with golden arm bands, over smooth, "
                   "flawless grey-blue skin on a powerful demonic frame",
        "eyes": "glowing red",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },

    # --- G.I. Joe --------------------------------------------------------
    "Snake Eyes": {
        "franchise": "G.I. Joe",
        "gender": "Male",
        "covers_face": True,
        "costume": "a full black tactical ninja commando bodysuit with a bandolier and a "
                   "sheathed knife, a katana on the back",
        "mask": "a seamless black commando mask with a dark visor",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a drawn katana",
    },
    "Cobra Commander": {
        "franchise": "G.I. Joe",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue military uniform with a black-and-silver Cobra emblem and a cape",
        "mask": "a reflective chrome faceplate under a blue hood",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Baroness": {
        "franchise": "G.I. Joe",
        "gender": "Female",
        "costume": "a glossy black leather catsuit with a silver Cobra emblem, black "
                   "gloves, and thin angular glasses",
        "signature": {"hair_color": "raven black", "hair_length": "long",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "Duke": {
        "franchise": "G.I. Joe",
        "gender": "Male",
        "costume": "green camouflage military fatigues with a tan tactical vest, dog tags, "
                   "and a green helmet",
        "signature": {"hair_color": "golden blonde", "hair_length": "buzzed very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Teenage Mutant Ninja Turtles ------------------------------------
    "Leonardo": {
        "bald": True,
        "franchise": "TMNT",
        "gender": "Male",
        "covers_face": True,
        "costume": "brown elbow and knee pads, with uniform, all-over green pebbled turtle skin, "
                   "a tan plastron, and a domed shell on the back",
        "mask": "a green pebbled turtle face with a beak-like mouth, dark brown eyes, "
                "and a blue bandana tied across the eyes",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "average height"},
        "prop": "twin katanas",
    },
    "Raphael": {
        "bald": True,
        "franchise": "TMNT",
        "gender": "Male",
        "covers_face": True,
        "costume": "brown elbow and knee pads, with uniform, all-over green pebbled turtle skin, "
                   "a tan plastron, and a domed shell on the back",
        "mask": "a green pebbled turtle face with a beak-like mouth, dark brown eyes, "
                "and a red bandana tied across the eyes",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "average height"},
        "prop": "a pair of three-pronged sai",
    },
    "Donatello": {
        "bald": True,
        "franchise": "TMNT",
        "gender": "Male",
        "covers_face": True,
        "costume": "brown elbow and knee pads, with uniform, all-over green pebbled turtle skin, "
                   "a tan plastron, and a domed shell on the back",
        "mask": "a green pebbled turtle face with a beak-like mouth, dark brown eyes, "
                "and a purple bandana tied across the eyes",
        "signature": {},
        "physique": {"body_type": "lean", "height": "average height"},
        "prop": "a long wooden bo staff",
    },
    "Michelangelo": {
        "bald": True,
        "franchise": "TMNT",
        "gender": "Male",
        "covers_face": True,
        "costume": "brown elbow and knee pads, with uniform, all-over green pebbled turtle skin, "
                   "a tan plastron, and a domed shell on the back",
        "mask": "a green pebbled turtle face with a beak-like mouth, dark brown eyes, "
                "and an orange bandana tied across the eyes",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a pair of nunchaku",
    },
    "Shredder": {
        "franchise": "TMNT",
        "gender": "Male",
        "covers_face": True,
        "costume": "a purple cape over a body sheathed in bladed silver armor plates with "
                   "spiked gauntlets",
        "mask": "a steel samurai helmet and faceplate with a menacing visor",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "April O'Neil": {
        "franchise": "TMNT",
        "gender": "Female",
        "costume": "a yellow jumpsuit with a utility belt",
        "signature": {"hair_color": "auburn", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },

    # --- Transformers ----------------------------------------------------
    "Megatron": {
        "franchise": "Transformers",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering grey-and-silver robotic body of tank-like plating with an "
                   "arm cannon",
        "mask": "a silver robotic face with a black helmet crest and glowing red eyes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Bumblebee": {
        "franchise": "Transformers",
        "gender": "Male",
        "covers_face": True,
        "costume": "a sleek yellow-and-black robotic body of car-formed plating",
        "mask": "a yellow-and-black robotic face with blue optic eyes and antennae",
        "physique": {"body_type": "athletic", "height": "tall"},
    },

    # --- Masters of the Universe (more) ----------------------------------
    "Sorceress": {
        "franchise": "Masters of the Universe",
        "gender": "Female",
        "costume": "a white feathered falcon-themed costume with a winged headdress, a "
                   "blue cape, and feathered arm-wings",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
        "prop": "a glowing crystal-topped staff",
    },
    "Teela": {
        "franchise": "Masters of the Universe",
        "gender": "Female",
        "costume": "a golden snake-emblem corset with a white skirt, a golden cobra "
                   "headpiece, and arm bands",
        "signature": {"hair_color": "auburn", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a golden cobra-headed staff",
    },
    "Man-At-Arms": {
        "franchise": "Masters of the Universe",
        "gender": "Male",
        "covers_body": True,  # full battle armor over the torso and limbs
        "costume": "green-and-orange battle armor with a metal harness and a helmet",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "tall", "skin_tone": "fair"},
    },
    "Beast Man": {
        "franchise": "Masters of the Universe",
        "gender": "Male",
        "costume": "red fur-armor straps over an even, all-over coat of shaggy orange "
                   "fur, with a fanged ape-like face and clawed hands",
        "eyes": "yellow",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Orko": {
        "franchise": "Masters of the Universe",
        "gender": "Male",
        "covers_face": True,
        "costume": "a floating blue robe with a wide red hat, a yellow scarf, and an 'O' "
                   "medallion, with no visible legs",
        "mask": "a shadowed face under a red hat showing only two glowing eyes",
        "physique": {"body_type": "very slim", "height": "petite"},
    },

    # --- Big Hero 6 ------------------------------------------------------
    "Aunt Cass": {
        "franchise": "Big Hero 6",
        "gender": "Female",
        "costume": "a casual cardigan over a blouse and jeans, with a small cafe apron",
        "signature": {"hair_color": "warm brown", "hair_length": "chin length bob",
                      "hair_texture": "wavy", "eye_color": "warm hazel"},
        "physique": {"body_type": "softly curved", "height": "average height", "skin_tone": "fair"},
    },
    "Baymax": {
        "franchise": "Big Hero 6",
        "gender": "Male",
        "covers_face": True,
        "costume": "a large rounded soft white inflatable vinyl robot body with stubby "
                   "arms and legs",
        "mask": "a smooth white inflatable face with two small black dot eyes joined by a line",
        "physique": {"body_type": "chubby", "height": "very tall"},
    },

    # --- The Incredibles -------------------------------------------------
    "Mr. Incredible": {
        "franchise": "The Incredibles",
        "gender": "Male",
        "costume": "a red supersuit with a black eye-mask, black trunks and boots, and a "
                   "black-and-orange 'i' chest emblem, on a hugely broad muscular frame",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "fair"},
    },
    "Elastigirl": {
        "franchise": "The Incredibles",
        "gender": "Female",
        "costume": "a red supersuit with a black eye-mask, long gloves, and an 'i' chest emblem",
        "signature": {"hair_color": "warm brown", "hair_length": "chin length bob",
                      "eye_color": "warm hazel"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Violet": {
        "franchise": "The Incredibles",
        "gender": "Female",
        "costume": "a red-and-black supersuit with an 'i' emblem",
        "signature": {"hair_color": "near black", "hair_length": "long",
                      "hair_texture": "sleek straight", "eye_color": "violet-gray"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Dash": {
        "franchise": "The Incredibles",
        "gender": "Male",
        "costume": "a red-and-black supersuit with an 'i' emblem, built for speed",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "fair"},
    },
    "Frozone": {
        "franchise": "The Incredibles",
        "gender": "Male",
        "costume": "a blue-and-white ice-themed supersuit with a visor and ice-form boots",
        "signature": {"hair_color": "jet black", "hair_length": "buzzed very short",
                      "facial_hair": "goatee", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "dark brown"},
    },

    # === DC (heroines, Lanterns, sorceresses, villains) ==================
    "Amethyst, Princess of Gemworld": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a purple-and-white magical gown with crystalline armor pieces, a "
                   "jeweled tiara, and amethyst boots",
        "eyes": "sparkling violet",
        "signature": {"hair_color": "white", "hair_length": "hip length",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "porcelain"},
    },
    "Arisia Rrab": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a white-and-green Green Lantern uniform with a cropped top, a bright green "
                   "miniskirt, and matching gloves and boots, with a glowing green Lantern "
                   "emblem on the chest, and a glowing green power ring worn on the finger, over "
                   "smooth, flawless warm yellow-green skin",
        "eyes": "vivid green",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "petite and slim", "height": "short"},
    },
    "Artemis": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a green sleeveless top with a matching green mini-skirt, dark green "
                   "gloves and boots, a black belt, and a green domino mask",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a recurve bow drawn ready, with a quiver of arrows across the back",
    },
    "Blackfire": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a revealing black-and-purple outfit with a black top, purple shorts, black "
                   "thigh-high boots, and silver armor pieces, over smooth, flawless "
                   "golden-orange skin",
        "eyes": "glowing purple",
        "signature": {"hair_color": "jet black", "hair_length": "very long"},
        "physique": {"body_type": "slender", "height": "very tall"},
    },
    "Bloody Mary": {
        "franchise": "Fables",
        "gender": "Female",
        "costume": "simple dark clothing that seems to blur and shift like a reflection, "
                   "blood-red lips, bare feet, and an aura of floating broken-mirror shards, "
                   "over smooth, flawless pale mirror-bright skin",
        "eyes": "dark and hollow",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Circe": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "form-fitting purple-and-gold sorceress robes with a high-slit skirt, "
                   "ornate golden armlets and a choker, and a dramatic sweeping cape",
        "eyes": "glowing green",
        "signature": {"hair_color": "purple", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "hourglass", "height": "statuesque", "skin_tone": "porcelain"},
    },
    "Dee Dee": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "matching red-and-black jester-inspired crop tops and mini-skirts with "
                   "striped thigh-high stockings and red hair bands, worn as identical twins",
        "signature": {"hair_color": "platinum blonde", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "porcelain"},
    },
    "Donna Troy": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black bodysuit covered in silver star patterns, a red belt, red "
                   "mid-calf boots, a silver tiara, and silver bracelets",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "loosely wavy", "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "golden tan"},
    },
    "Dove": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a white-and-pale-blue bodysuit with feather-like patterns along the "
                   "arms and legs, soft blue gloves and boots, a flowing white wing-shaped "
                   "cape, and a light blue domino mask",
        "signature": {"hair_color": "platinum blonde", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Fatality": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "form-fitting technological armor in metallic purples and blacks with "
                   "integrated alien weaponry and a ridged hairless skull, over smooth, flawless "
                   "purple-grey skin",
        "eyes": "glowing yellow",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Golden Glider": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting golden bodysuit with a golden cape and golden boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "pale"},
    },
    "Granny Goodness": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "heavy blue-and-silver Apokoliptian armor with a cape and imposing "
                   "shoulder plates, on a stout broad-shouldered elderly frame",
        "signature": {"hair_color": "white", "hair_length": "short pixie",
                      "hair_texture": "tightly curled", "eye_color": "dark gray"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "fair"},
    },
    "Gypsy": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a flowing purple-and-gold outfit with a crop top, a flowing skirt, "
                   "boots, large hoop earrings, and mystical jewelry",
        "signature": {"hair_color": "dark brown", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "olive"},
    },
    "Hippolyta": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "ornate gold-and-white Amazon armor with a flowing cape and armored boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "statuesque", "skin_tone": "golden tan"},
    },
    "Jade (Jennifer-Lynn Hayden)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a sleeveless green-and-black costume with a Green Lantern emblem and black "
                   "boots, over smooth, flawless luminous green skin",
        "eyes": "glowing green",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "tall"},
        "prop": "a glowing green energy construct shaped like a star",
    },
    "Jessica Cruz": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a sleek green-and-black form-fitting Green Lantern costume with a "
                   "bright green chest emblem, integrated green gloves and boots, a "
                   "glowing green power ring worn on the finger, and a faint green "
                   "energy aura",
        "eyes": "glowing green",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
    },
    "Jinx (Teen Titans)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black dress with pink trim reaching the thighs, black-and-pink "
                   "striped stockings, black boots, and gothic-punk mystical accessories",
        "eyes": "glowing pink",
        "signature": {"hair_color": "hot pink", "hair_length": "very long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "very slim", "height": "petite", "skin_tone": "very pale"},
    },
    "Katma Tui": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "the green-and-black Green Lantern Corps uniform with a white waist band and "
                   "chest emblem, white forearm-length gloves, green knee-high boots, a green "
                   "domino mask, and a glowing green power ring worn on the index finger, over "
                   "smooth, flawless smooth purple skin",
        "eyes": "vivid emerald green",
        "signature": {"hair_color": "jet black", "hair_length": "mid back",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Killer Frost": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting icy costume with crystalline armor pieces and ice boots, over "
                   "uniform, all-over pale blue frost-rimed skin",
        "signature": {"hair_color": "white", "hair_length": "long", "hair_style": "slicked back",
                      "eye_color": "ice blue"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Livewire": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting bodysuit that looks woven from crackling electrical energy "
                   "with lightning patterns and sparking boots, hair standing up in jagged bolts "
                   "of white electricity, over smooth, flawless pale blue skin",
        "eyes": "electric blue",
        "signature": {"hair_color": "white", "hair_length": "short pixie", "hair_style": "windswept"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Lyssa Drak": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black bikini-style outfit with thin straps and yellow-gold accents along "
                   "the edges, and a long flowing black cloak, over smooth, flawless light blue "
                   "skin",
        "eyes": "glowing yellow",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "tall"},
        "prop": "the Book of Parallax, a heavy chained tome glowing with yellow light",
    },
    "Madame Xanadu": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "elaborate colorful fortune-teller clothing with flowing skirts and "
                   "shawls in purples, golds, and reds, large ornate jewelry including a "
                   "crystal-ball pendant and golden arm bands, and embroidered mystical symbols",
        "eyes": "violet",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "olive"},
        "prop": "a fanned deck of oversized tarot cards",
    },
    "Mary Marvel": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a red costume with a short flared skirt, a bold gold lightning-bolt "
                   "emblem on the chest, gold trim and a sash, and a white cape with gold accents",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "medium brown"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Maxima": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a fitted green costume with a short green miniskirt, matching green "
                   "boots and gloves, and minimal gold accents along the belt and neckline",
        "signature": {"hair_color": "bright red", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "bright green"},
        "physique": {"body_type": "athletic", "height": "statuesque", "skin_tone": "fair"},
    },
    "Miss Martian": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting white bodysuit with red accents, a blue cape, and red boots, "
                   "over smooth, flawless green skin",
        "eyes": "solid red",
        "signature": {"hair_color": "bright red", "hair_length": "long"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Punchline": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a tight black-and-purple outfit streaked with electric blue, with punk "
                   "accents, fingerless gloves, high boots, and bold dark makeup",
        "eyes": "violet",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "pale"},
    },
    "Red Claw": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a deep red single-shoulder-baring outfit with a fitted asymmetrical "
                   "top, a matching skirt, a wide black sash-belt, and black gloves",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "long",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Rose Wilson": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "an orange-and-blue form-fitting costume with armor plating, an "
                   "orange-and-black mask covering the right eye, black boots and gloves, "
                   "and a sword harness across the back",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "hair_style": "high ponytail", "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "olive"},
        "prop": "a pair of curved short swords",
    },
    "Star Sapphire": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting purple-and-pink costume that looks crystallized from "
                   "violet light, with a star-sapphire emblem on the chest, sparkling gem "
                   "boots, and a glowing violet star-sapphire power ring worn on the finger",
        "eyes": "glowing violet",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Tala": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a deep red form-fitting gown with a high slit, gold mystical jewelry, "
                   "bare arms, and elegant heels",
        "eyes": "glowing pale blue",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "porcelain"},
    },
    "Tala (Legion of Doom)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a dark violet form-fitting gown with a high slit, black-and-gold "
                   "arcane jewelry, bare arms, and elegant dark heels",
        "eyes": "glowing pale blue",
        "signature": {"hair_color": "deep purple", "hair_length": "very long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "porcelain"},
    },
    "Talia al Ghul": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "form-fitting dark combat clothing in green and black, with black "
                   "gloves and black boots",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "wavy", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "warm tan"},
    },
    "Thorn": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a costume made entirely of living vines, leaves, and thorns that shift and "
                   "grow, with bare feet trailing root-like tendrils, over uniform, all-over "
                   "pale green leaf-veined skin",
        "eyes": "vivid leaf green",
        "signature": {"hair_color": "emerald green", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Wonder Girl (Cassie Sandsmark)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a red costume with a fitted top and subtle star accents, a bold gold "
                   "'W' emblem across the chest, matching gold bracers and belt, sleek "
                   "black pants, red boots, and a golden lasso coiled at the hip",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "windswept", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "golden tan"},
    },

    # === Marvel (heroines, sorceresses, cosmic & demonic) ================
    "Agatha Harkness": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a flowing purple robe patterned with magical symbols, dark fitted "
                   "pants, black boots, and silver jewelry and mystical amulets",
        "eyes": "violet",
        "signature": {"hair_color": "dark brown", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },
    "Angela": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "elaborate golden armor with wing motifs covering strategic areas, "
                   "flowing red-and-gold ribbons and fabric strips, ornate golden jewelry, "
                   "and massive feathered wings extending from the back",
        "signature": {"hair_color": "copper", "hair_length": "very long",
                      "hair_texture": "loosely wavy", "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "statuesque", "skin_tone": "fair"},
        "prop": "a long curved Asgardian war-blade",
    },
    "Binary": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a body of brilliant golden-white stellar energy with hair transformed into "
                   "flowing solar flames, constellation-like energy patterns across the form, "
                   "and a radiant aura of cosmic fire, over smooth, flawless glowing "
                   "golden-white skin",
        "eyes": "burning starlight",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Blackheart": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a minimal black costume with hellish design elements, clawed hands and feet, "
                   "small horns on the forehead, dark demonic markings, and an aura of dark "
                   "energy, over smooth, flawless dark grey demon skin",
        "eyes": "burning red",
        "signature": {"hair_color": "jet black", "hair_length": "very long"},
        "physique": {"body_type": "slender", "height": "very tall"},
    },
    "Blink": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a sleek black-and-purple tactical suit with light boots, sharp facial "
                   "markings, and a faint teleportation shimmer, over smooth, flawless vibrant "
                   "magenta skin",
        "eyes": "glowing green",
        "signature": {"hair_color": "magenta", "hair_length": "short pixie"},
        "physique": {"body_type": "lean", "height": "average height"},
        "prop": "a pair of glowing energy javelins",
    },
    "Crystal": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting green-and-white costume with cape elements and Inhuman "
                   "design accents",
        "signature": {"hair_color": "auburn", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely wavy", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Krystalin": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a futuristic blue-and-silver armored bodysuit with shimmering "
                   "hard-light crystalline shards forming along the arms and shoulders",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "box braids", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "warm brown"},
    },
    "Lady Sif": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "Asgardian armor in gold and blue with Norse designs, a flowing cape, "
                   "and armored boots",
        "signature": {"hair_color": "raven black", "hair_length": "very long",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "golden tan"},
        "prop": "a double-bladed Asgardian sword",
    },
    "Magic": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "revealing metallic bikini-style armor pieces, thigh-high boots, and a cape "
                   "with demonic and mystical designs, over smooth, flawless blue demon-form "
                   "skin",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "petite", "skin_tone": "fair"},
    },
    "Magik": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black-and-gold armored bodysuit with spiked pauldrons and thigh-high boots",
        "signature": {"hair_color": "platinum blonde", "hair_length": "long",
                      "hair_style": "blunt bangs", "hair_texture": "sleek straight",
                      "eye_color": "ice blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "very pale"},
        "prop": "the Soulsword, a long blade of crackling arcane soul-energy",
    },
    "Mary Jane Watson": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "fashionable chic clothing in colors that complement red hair, from "
                   "casual to glamorous evening wear",
        "signature": {"hair_color": "bright red", "hair_length": "very long",
                      "hair_texture": "thick and voluminous", "eye_color": "bright green"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Mistress Death": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a tattered dark cosmic shroud draping the frame like living darkness, with a "
                   "cold silent aura that seems to bend light, over smooth, flawless pale "
                   "bone-white skin",
        "eyes": "hollow void-black",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "very slim", "height": "tall"},
    },
    "Moonstone": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting white bodysuit with geometric patterns, silver accents "
                   "and cosmic-energy designs, white boots and gloves, and a subtle "
                   "luminescent glow to the skin",
        "eyes": "glowing white",
        "signature": {"hair_color": "platinum blonde", "hair_length": "long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "pale"},
    },
    "Morgan le Fay": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "an elaborate medieval gown in deep green and gold with Celtic knotwork "
                   "embroidery and flowing sleeves, an ornate golden circlet, and mystical "
                   "amulets and rings",
        "eyes": "glowing green",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },
    "Nocturne": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting dark bodysuit with red accents and a high collar, with "
                   "three-fingered hands, two-toed feet, and a long prehensile tail, over "
                   "an even, all-over coat of dark indigo fur",
        "eyes": "solid glowing yellow",
        "signature": {"hair_color": "navy blue", "hair_length": "short pixie"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Nova (Frankie Raye)": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a costume of living cosmic energy with flame patterns, fire-trail boots, and "
                   "golden flame for hair, over smooth, flawless glowing golden energy skin",
        "eyes": "burning cosmic fire",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Satana": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a revealing red-and-black succubus outfit with minimal coverage, a "
                   "high slit, gold-and-bone jewelry, and small curved horns, with a thin "
                   "barbed tail",
        "eyes": "glowing hellfire red",
        "signature": {"hair_color": "jet black", "hair_length": "very long"},
        "physique": {"body_type": "hourglass", "height": "average height", "skin_tone": "fair"},
    },
    "Snowbird": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a white-and-blue costume with Arctic animal motifs, fur trim, feather "
                   "patterns, and traditional Inuit design elements",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "half up half down", "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "bronze"},
    },
    "Spectrum": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "an iconic black-and-white suit with a starburst emblem on the chest, "
                   "surrounded by radiant photon-energy effects giving a luminous glow",
        "eyes": "glowing white",
        "signature": {"hair_color": "dark brown", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely curled"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "brown"},
    },
    "Spiral": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a revealing costume in metallics and blacks with technological "
                   "elements, visible cybernetic implants, and four additional mechanical "
                   "arms extending from the shoulders alongside the natural pair",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very long"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "pale"},
        "prop": "a cluster of high-tech blades and energy weapons held across the extra arms",
    },
    "Sunfire (Exiles)": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a sleek red-and-white armored suit with a Rising Sun motif and "
                   "heat-resistant plating, segmented gauntlets and boots, and a radiant "
                   "ember-glow aura, with black hair tipped in flame-red streaks",
        "eyes": "crimson",
        "signature": {"hair_color": "jet black", "hair_length": "short pixie",
                      "hair_style": "windswept"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "golden tan"},
    },
    "Typhoid Mary": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black leather jacket over tight dark clothing with torn fabric and "
                   "an exposed midriff, fingerless gloves, buckled boots, one side of the "
                   "face painted stark white, and vivid red lipstick",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_texture": "thick and voluminous", "hair_style": "windswept",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Viper": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a tight dark-green bodysuit with matching gloves and boots, a high "
                   "collar, and serpent-themed accents",
        "signature": {"hair_color": "emerald green", "hair_length": "very long",
                      "hair_texture": "sleek straight", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },
    "White Widow": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a form-fitting white tactical bodysuit with subtle gray paneling, a "
                   "lightweight utility belt, white gloves and boots, and minimalist "
                   "silver accents",
        "signature": {"hair_color": "platinum white", "hair_length": "slightly past shoulders",
                      "hair_texture": "sleek straight", "eye_color": "ice blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "porcelain"},
    },

    # === Video Games (MK, Mass Effect, WoW, RE, LoL, and more) ===========
    "Astarte": {
        "franchise": "Divinity: Original Sin",
        "gender": "Female",
        "costume": "gossamer divine robes woven of shimmering iridescent blues and violets and "
                   "soft starlight, with silver constellation markings, on a celestial six-foot "
                   "goddess frame, over smooth, flawless moon-pale skin",
        "eyes": "swirling nebula",
        "signature": {"hair_color": "platinum white", "hair_length": "very long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "very tall"},
    },
    "Cetrion": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "flowing robes formed of earth, water, air, and light, nature-inspired armor "
                   "pieces, leg wrappings of living root and vine, and a crown of living "
                   "branches and crystals, on a towering seven-foot elemental-goddess frame, "
                   "over smooth, flawless pale luminescent skin marked with glowing elemental "
                   "sigils",
        "eyes": "glowing blue-white",
        "signature": {"hair_color": "platinum white", "hair_length": "very long",
                      "hair_texture": "wavy"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Cortana": {
        "franchise": "Halo",
        "gender": "Female",
        "costume": "a slender luminous holographic body of flowing code and light in blue and "
                   "purple, with short swept-back hair blending into the form, over smooth, "
                   "flawless translucent blue holographic skin",
        "eyes": "glowing blue",
        "signature": {"hair_color": "navy blue", "hair_length": "short pixie",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "slender", "height": "average height"},
    },
    "D'Vorah": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "dark organic Kytinn attire in black, yellow, and green chitin, a "
                   "chitinous head crest, and four large insectoid ovipositors extending "
                   "from the back, over an even, all-over coat of pale yellow-green chitin",
        "eyes": "large solid black insectoid",
        "skin": "pale yellow-green",  # 'chitin' isn't a material the anchor regex catches
        "physique": {"body_type": "slender", "height": "average height"},
    },
    "Daisy": {
        "franchise": "Super Mario",
        "gender": "Female",
        "costume": "a yellow-and-orange dress with daisy patterns, white gloves, orange "
                   "high heels, flower hair accessories, and floral jewelry",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "loosely wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Evelynn": {
        "franchise": "League of Legends",
        "gender": "Female",
        "costume": "a skin-hugging bodysuit of shadow-lace and velvet, claw-like horns framing "
                   "the face, shimmering lashes, and scythe-like tendrils slithering behind, "
                   "over smooth, flawless iridescent obsidian-black skin",
        "eyes": "hot pink",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_style": "worn down"},
        "physique": {"body_type": "hourglass", "height": "tall"},
    },
    "Jaina Proudmoore": {
        "franchise": "World of Warcraft",
        "gender": "Female",
        "costume": "elaborate white, blue, and gold Archmage robes with intricate "
                   "embroidery, flowing sleeves, a high collar, and a white streak through "
                   "the hair",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very long",
                      "hair_texture": "loosely wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
        "prop": "a glowing runed archmage staff",
    },
    "Lady Dimitrescu": {
        "franchise": "Resident Evil",
        "gender": "Female",
        "costume": "a champagne-colored 1930s-inspired evening gown cinched at the waist "
                   "with a black rose brooch, long silk gloves tipped with black claw-like "
                   "nails, and a wide-brimmed ivory sunhat over vintage black waves, on an "
                   "impossibly tall nine-and-a-half-foot frame that looms over everything "
                   "in the scene",
        "eyes": "liquid gold",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "very tall", "skin_tone": "porcelain"},
    },
    "Mad Moxxi": {
        "franchise": "Borderlands",
        "gender": "Female",
        "costume": "a revealing red-and-black ringmaster corset cinched impossibly tight, "
                   "mismatched striped stockings, thigh-high boots, long gloves, and heavy "
                   "theatrical makeup with smudged bright-red lipstick",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "hourglass", "height": "average height", "skin_tone": "pale"},
    },
    "Miranda Lawson": {
        "franchise": "Mass Effect",
        "gender": "Female",
        "costume": "a form-fitting white catsuit with black paneling and hexagonal "
                   "patterns, integrated white heeled boots, and black fingerless gloves",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "sleek straight", "eye_color": "bright blue"},
        "physique": {"body_type": "hourglass", "height": "tall", "skin_tone": "fair"},
    },
    "Morrigan (Dragon Age)": {
        "franchise": "Dragon Age",
        "gender": "Female",
        "costume": "layered dark robes in deep purple, brown, and black with a prominent "
                   "cowl, feathers on the shoulders, beaded accents, and gold jewelry",
        "eyes": "golden yellow",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "blunt bangs", "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Palutena": {
        "franchise": "Kid Icarus",
        "gender": "Female",
        "costume": "a white dress with blue-and-gold accents that seems made of light, "
                   "golden arm guards, a blue jeweled crown, sandals, and green hair "
                   "flowing past the feet",
        "eyes": "glowing green",
        "signature": {"hair_color": "emerald green", "hair_length": "hip length",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "very tall", "skin_tone": "fair"},
        "prop": "a tall golden staff topped with a glowing emblem",
    },
    "Rosalina": {
        "franchise": "Super Mario",
        "gender": "Female",
        "costume": "a floor-length turquoise dress patterned with stars, white gloves, a "
                   "small crown, a cosmic shimmer to the skin, and platinum starlight hair "
                   "sweeping past the waist and partly over one eye, on a towering "
                   "seven-foot cosmic-guardian frame",
        "signature": {"hair_color": "platinum blonde", "hair_length": "waist length",
                      "hair_texture": "sleek straight", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "very tall", "skin_tone": "pale"},
        "prop": "a star-topped wand trailing cosmic sparkles",
    },
    "Sarah Kerrigan": {
        "franchise": "StarCraft",
        "gender": "Female",
        "costume": "a bio-organic exoskeleton of purple, brown, and bone-white carapace with "
                   "large segmented insectoid wings and long tendril-like dreadlocks, over "
                   "uniform, all-over purplish carapace skin",
        "eyes": "glowing orange",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Sheeva": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "minimal practical red-and-brown bikini-style warrior attire with armored "
                   "bracers and greaves, a dark topknot, and four powerful arms, over smooth, "
                   "flawless red Shokan skin",
        "eyes": "glowing orange",
        "signature": {"hair_color": "jet black", "hair_length": "long", "hair_style": "top knot"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "SHODAN": {
        "franchise": "System Shock",
        "gender": "Female",
        "costume": "a glitching spectral humanoid silhouette with fractal skin of streaming data "
                   "and jagged synthetic contours that pulse and flicker, over smooth, flawless "
                   "green-tinged data-stream skin",
        "eyes": "glowing green",
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Sylvanas Windrunner": {
        "franchise": "World of Warcraft",
        "gender": "Female",
        "costume": "midnight-purple armor with skull motifs and gothic elements, an arrow-filled "
                   "quiver across the back, a tattered crimson cloak with a deep trailing hood, "
                   "and silver tribal markings, over smooth, flawless pale blue-grey undead skin",
        "eyes": "glowing red",
        "signature": {"hair_color": "white", "hair_length": "very long", "hair_style": "worn down"},
        "physique": {"body_type": "slender", "height": "tall"},
        "prop": "a black-and-bone ranger's bow",
    },
    "Twintelle": {
        "franchise": "ARMS",
        "gender": "Female",
        "costume": "a pearl-gilded red catsuit with art-deco flourishes, a rose-gold opera "
                   "mask, sharp heels, and voluminous white twin-tails of gravity-defying hair",
        "eyes": "violet",
        "signature": {"hair_color": "white", "hair_length": "very long", "hair_style": "pigtails"},
        "physique": {"body_type": "hourglass", "height": "very tall", "skin_tone": "dark brown"},
    },
    "Tyrande Whisperwind": {
        "franchise": "World of Warcraft",
        "gender": "Female",
        "costume": "ornate elven robes and light armor in white, silver, and purple with moon "
                   "symbols, feathers, and intricate patterns, over smooth, flawless pale "
                   "lavender skin",
        "eyes": "glowing silver",
        "signature": {"hair_color": "teal", "hair_length": "very long"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Lilith Aensland": {
        "franchise": "Darkstalkers",
        "gender": "Female",
        "costume": "a form-fitting red-and-blue bodysuit with bat motifs, and red-and-green "
                   "bat wings rising from the back and the head",
        "signature": {"hair_color": "lavender", "hair_length": "chin length bob",
                      "eye_color": "green"},
        "physique": {"body_type": "petite and curvy", "height": "petite", "skin_tone": "fair"},
    },

    # === DC (more) =======================================================
    "Cheshire": {
        "franchise": "DC",
        "gender": "Female",
        "covers_face": True,
        "costume": "a form-fitting green bodysuit with darker green accents, black boots "
                   "and gloves, and various hidden weapons",
        "mask": "a white porcelain mask covering the entire face with red lips and black "
                "markings forming a Cheshire-cat grin",
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "olive"},
    },
    "Lois Lane": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a fitted blouse and a high-waisted skirt with clean tailored lines, "
                   "modest heels, a press badge at the hip, a feminine hair bow, and "
                   "classic red lipstick",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "softly curled", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Supergirl (DCAU)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a white cropped top with a red-and-yellow 'S' shield, a short blue "
                   "skirt, red boots, and a flowing red cape",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_texture": "sleek straight", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },

    # === Anime & Manga (more) ============================================
    "Homura Akemi (Devil)": {
        "franchise": "Madoka Magica",
        "gender": "Female",
        "costume": "an elaborate dark gothic dress in black with dark purple and "
                   "red accents, a feathered collar, a full skirt, and dark feathered wings",
        "eyes": "glowing violet",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "pale"},
    },
    "Madoka Kaname (Ultimate)": {
        "franchise": "Madoka Magica",
        "gender": "Female",
        "costume": "a flowing white-and-pink magical dress that blends into the cosmos, "
                   "wing-like adornments, and a long train patterned with stars and "
                   "galaxies, with very long cosmic-pink hair",
        "eyes": "glowing pink",
        "signature": {"hair_color": "baby pink", "hair_length": "waist length",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
        "prop": "a rose-and-gold celestial bow",
    },
    "Lust": {
        "franchise": "Fullmetal Alchemist",
        "gender": "Female",
        "costume": "a black dress with a plunging neckline, black elbow-length gloves, "
                   "black high heels, and an Ouroboros tattoo above the chest",
        "eyes": "glowing violet",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "voluptuous", "height": "tall", "skin_tone": "pale"},
    },
    "Princess Mononoke": {
        "franchise": "Studio Ghibli",
        "gender": "Female",
        "costume": "a minimal white sleeveless tunic and shorts, brown arm guards and leg "
                   "wrappings, red-and-blue war-paint face markings, and a fur cape with a "
                   "carved wolf mask",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "hair_texture": "thick and voluminous", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "short", "skin_tone": "warm tan"},
        "prop": "a stone dagger",
    },
    "Totoro": {
        "franchise": "Studio Ghibli",
        "gender": "Male",
        "covers_face": True,
        "costume": "a large round grey-furred body with a cream-white belly marked with "
                   "grey chevron arrowheads, tiny arms, and small clawed feet",
        "mask": "a huge round grey Totoro head with wide round eyes, small pointed ears, "
                "and a wide fanged grin",
        "physique": {"body_type": "plump", "height": "very tall"},
    },

    # === Monster High / indie comics =====================================
    "Abbey Bominable": {
        "franchise": "Monster High",
        "gender": "Female",
        "costume": "white fur-trimmed clothing with snowflake patterns, ice-crystal accessories "
                   "in blue, purple, and pink tones, small tusks at the lower lip, and long "
                   "white hair streaked with pink, purple, and blue, over smooth, flawless light "
                   "icy-blue skin",
        "eyes": "light purple",
        "signature": {"hair_color": "white", "hair_length": "very long"},
        "physique": {"body_type": "stocky", "height": "tall"},
    },
    "Frankie Stein": {
        "franchise": "Monster High",
        "gender": "Female",
        "costume": "preppy-punk fashion in plaid, black, white, and yellow, with visible "
                   "stitches on the limbs and neck, small neck bolts, and long black hair "
                   "streaked with white sections, over smooth, flawless pale mint-green skin",
        "eyes": "one blue and one green",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Aspen Matthews": {
        "franchise": "Fathom",
        "gender": "Female",
        "costume": "a sleek form-fitting iridescent metallic aquatic suit with shimmering "
                   "blue accents",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "golden tan"},
    },
    "Lady Death": {
        "franchise": "Chaos! Comics",
        "gender": "Female",
        "costume": "minimal black-and-silver armor with skull motifs and bone accessories, black "
                   "thigh-high studded boots, a flowing dark cape, and ornate skull jewelry and "
                   "crown, over smooth, flawless deathly-white skin",
        "eyes": "glowing pale white",
        "signature": {"hair_color": "white", "hair_length": "waist length",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "hourglass", "height": "statuesque"},
    },
    "Shana the She-Devil": {
        "franchise": "Comics",
        "gender": "Female",
        "costume": "a minimal red barbarian bikini-style top and brief bottom, leather boots and "
                   "bracers, and fire-red battle-flung hair, over smooth, flawless "
                   "sun-and-battle-bronzed skin",
        "signature": {"hair_color": "bright red", "hair_length": "very long",
                      "hair_texture": "thick and voluminous", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "bronze"},
        "prop": "a broad-bladed barbarian sword",
    },
    "Lunatica": {
        "franchise": "Comics",
        "gender": "Female",
        "costume": "black leather straps and armored pieces, clawed gauntlets, and heavy boots, "
                   "with wild red hair, over smooth, flawless pale lavender skin with darker "
                   "markings",
        "eyes": "yellow reptilian slit",
        "signature": {"hair_color": "bright red", "hair_length": "very long",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },

    # === Classic cartoons (Simpsons, Family Guy, Flintstones, etc.) ======
    "Betty Boop": {
        "franchise": "Betty Boop",
        "gender": "Female",
        "costume": "a strapless red curve-hugging dress ending mid-thigh, red high heels, "
                   "large hoop earrings, and a thigh garter",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "curly", "eye_color": "dark brown"},
        "physique": {"body_type": "petite and curvy", "height": "petite", "skin_tone": "porcelain"},
    },
    "Betty Rubble": {
        "franchise": "The Flintstones",
        "gender": "Female",
        "costume": "a simple blue knee-length dress with a scalloped neckline, a blue "
                   "necklace, blue shoes, and a small white hair accessory",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Wilma Flintstone": {
        "franchise": "The Flintstones",
        "gender": "Female",
        "costume": "a white one-shoulder knee-length dress with a scalloped neckline and "
                   "an asymmetrical design, a pearl necklace, and a bone hair ornament",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "updo", "hair_texture": "curly"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
    },
    "Judy Jetson": {
        "franchise": "The Jetsons",
        "gender": "Female",
        "costume": "futuristic 1960s clothing in bright colors with go-go boots, "
                   "retro-future accessories, and hair in a high bouffant",
        "signature": {"hair_color": "white blonde", "hair_length": "long",
                      "hair_style": "updo", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Lisa Simpson": {
        "franchise": "The Simpsons",
        "gender": "Female",
        "costume": "a red sleeveless dress reaching the knees, red shoes, a pearl necklace, and "
                   "tall spiky pointed hair, over smooth, flawless bright yellow skin",
        "signature": {"hair_color": "yellow", "hair_length": "short pixie"},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Marge Simpson": {
        "franchise": "The Simpsons",
        "gender": "Female",
        "costume": "a strapless green dress reaching the ankles, red low-heeled shoes, a pearl "
                   "necklace, and an extremely tall blue beehive of hair, over smooth, flawless "
                   "bright yellow skin",
        "signature": {"hair_color": "electric blue", "hair_length": "very long",
                      "hair_style": "updo"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Lois Griffin": {
        "franchise": "Family Guy",
        "gender": "Female",
        "costume": "a green long-sleeved sweater, tan pants, and brown shoes",
        "signature": {"hair_color": "copper", "hair_length": "long",
                      "hair_texture": "loosely wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "tall", "skin_tone": "fair"},
    },
    "Meg Griffin": {
        "franchise": "Family Guy",
        "gender": "Female",
        "costume": "a pink beanie hat, a white shirt, blue jeans, white sneakers, and "
                   "thick round glasses",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "fine and wispy", "eye_color": "dark brown"},
        "physique": {"body_type": "average", "height": "petite", "skin_tone": "fair"},
    },
    "Leela": {
        "franchise": "Futurama",
        "gender": "Female",
        "costume": "a white tank top, black pants, black boots, a yellow jacket, a digital "
                   "wrist device, and a single large central eye",
        "eyes": "a single large blue eye",
        "signature": {"hair_color": "purple", "hair_length": "very long",
                      "hair_style": "high ponytail"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Jem": {
        "franchise": "Jem and the Holograms",
        "gender": "Female",
        "costume": "flashy 1980s outfits in bright pink, purple, and gold with metallic "
                   "fabrics and bold patterns, star-shaped earrings, and voluminous "
                   "shimmering pink 80s waves",
        "eyes": "bright magenta",
        "signature": {"hair_color": "hot pink", "hair_length": "very long",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "fair"},
    },

    # === Literature & fairy tales ========================================
    "Anne of Green Gables": {
        "franchise": "Anne of Green Gables",
        "gender": "Female",
        "costume": "a simple brown dress with a white collar and cuffs, black stockings, "
                   "practical brown boots, a straw hat, and a freckled face",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "green"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Pippi Longstocking": {
        "franchise": "Pippi Longstocking",
        "gender": "Female",
        "costume": "mismatched long stockings (one red, one blue), a short patched dress, "
                   "enormous oversized shoes, a freckled face, and bright red pigtails "
                   "sticking straight out",
        "signature": {"hair_color": "bright red", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "very petite", "skin_tone": "fair"},
    },
    "Dorothy Gale": {
        "franchise": "The Wizard of Oz",
        "gender": "Female",
        "costume": "a blue-and-white gingham dress with a white apron and puffy sleeves, "
                   "white stockings, ruby-red slippers, and twin braids tied with blue ribbons",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_style": "pigtails", "eye_color": "medium brown"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
        "prop": "a wicker picnic basket",
    },
    "Little Red Riding Hood": {
        "franchise": "Fairy Tales",
        "gender": "Female",
        "costume": "a vibrant red hooded cloak over a simple earthy-toned dress with a "
                   "white apron and leather shoes",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "loosely wavy", "eye_color": "hazel"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
        "prop": "a wicker basket covered with a checkered cloth",
    },
    "White Queen (Alice in Wonderland)": {
        "franchise": "Alice in Wonderland",
        "gender": "Female",
        "costume": "a flowing white gown with intricate baroque patterns, white gloves past the "
                   "elbows, white flowers and ornaments in an elaborate period updo, pale lip "
                   "color, and a powdered ghostly-pale complexion, over smooth, flawless "
                   "chalk-white skin",
        "signature": {"hair_color": "platinum blonde", "hair_length": "very long",
                      "hair_style": "updo", "eye_color": "pale blue"},
        "physique": {"body_type": "slender", "height": "tall"},
    },

    # === Disney (more) ===================================================
    "Minnie Mouse": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "large round black mouse ears, a big yellow bow, a yellow puffy-sleeved "
                   "dress with a flowing skirt, yellow heeled shoes, and white gloves, over "
                   "an even, all-over coat of black fur with a peachy face",
        "signature": {"eye_color": "dark brown"},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Mary Poppins": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a tailored Edwardian navy coat over a high-necked white blouse, a "
                   "smart hat adorned with flowers, white gloves, and ankle boots",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_style": "updo", "eye_color": "bright blue"},
        "physique": {"body_type": "slender", "height": "average height", "skin_tone": "fair"},
        "prop": "a parrot-headed umbrella and a bottomless carpet bag",
    },
    "Wendy Darling": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a light blue floor-length nightgown with long sleeves, a slightly "
                   "ruffled neckline, a darker blue waist sash, and a blue hair ribbon",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "loosely wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Kim Possible": {
        "franchise": "Disney",
        "gender": "Female",
        "costume": "a black crop top showing the midriff, dark green cargo pants with "
                   "pockets, black fingerless gloves, and black boots",
        "signature": {"hair_color": "bright red", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely wavy", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Judy Hopps": {
        "franchise": "Zootopia",
        "gender": "Female",
        "costume": "a blue ZPD police uniform with a badge, dark blue pants, a black "
                   "utility belt, tall grey rabbit ears, over an even, all-over coat of "
                   "grey fur with a white belly and inner ears",
        "eyes": "large violet",
        "physique": {"body_type": "athletic", "height": "petite"},
    },
    "Star Butterfly": {
        "franchise": "Star vs. the Forces of Evil",
        "gender": "Female",
        "costume": "a whimsical colorful A-line dress in teal, green, pink, and purple "
                   "with playful patterns, a magenta devil-horn headband, and small pink "
                   "heart marks on the cheeks",
        "signature": {"hair_color": "golden blonde", "hair_length": "waist length",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
        "prop": "a crystal-topped magic wand",
    },

    # === Movies & TV (more) ==============================================
    "Princess Fiona": {
        "franchise": "Shrek",
        "gender": "Female",
        "costume": "a green medieval dress with gold trim and a brown corset",
        "signature": {"hair_color": "copper", "hair_length": "very long",
                      "hair_texture": "loosely curled", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "The 50 Foot Woman": {
        "franchise": "Attack of the 50 Foot Woman",
        "gender": "Female",
        "costume": "a torn white dress stretched over a colossal fifty-foot-tall figure of "
                   "overwhelmingly gigantic scale, with normal human coloring",
        "signature": {"hair_color": "golden blonde", "hair_length": "very long",
                      "hair_texture": "loosely wavy", "eye_color": "bright blue"},
        "size_scale": "giant",
        "physique": {"body_type": "curvy", "height": "very tall", "skin_tone": "fair"},
    },

    # Expansion (June 2026): comic / movie / game / cartoon icon pass ========

    # --- Marvel (more heroes/villains) ------------------------------------
    "Quicksilver": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a blue bodysuit with a white lightning chevron on the chest and "
                   "silver boots, with a motion-blurred speed trail",
        "signature": {"hair_color": "silver", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Nick Fury": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a long black leather trench coat over black tactical gear, with a "
                   "black eye patch over the left eye and a clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
    },
    "Moon Knight": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hooded pure-white cloak and bodysuit with a crescent-moon emblem "
                   "on the chest",
        "mask": "a smooth white face wrapping with no visible features",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a silver crescent-moon throwing dart",
    },
    "Iron Fist": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a green sleeveless martial-arts tunic with a high collar and a yellow "
                   "chest sash, a yellow mask over the eyes, and soft yellow slippers, "
                   "with one fist glowing white-gold",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Luke Cage": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a yellow open-collar shirt with a silver chain-link belt",
        "signature": {"hair_color": "near black", "hair_length": "buzzed very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
    },
    "Namor": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "green scaled swim trunks, pointed ears, and tiny feathered wings at "
                   "the ankles, on a bare muscular chest",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a three-pronged golden trident",
    },
    "Nova (Richard Rider)": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a dark blue bodysuit with gold trim and a gold starburst chest "
                   "emblem, with the fists wreathed in cosmic energy",
        "mask": "a glowing gold dome helmet",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Sandman": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a green-and-brown horizontal-striped shirt and brown trousers, over uniform, "
                   "all-over yellow-tan sand skin, with one arm morphed into a giant sand hammer",
        "signature": {"hair_color": "warm brown", "hair_length": "very short",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Vulture": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a green flight suit with a feathered ruff collar, enormous mechanical "
                   "feathered wings, talon-tipped boots, and a bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "gray"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Kraven the Hunter": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a lion-mane vest worn open over a bare chest, leopard-print trousers, "
                   "and a beaded belt of fangs",
        "signature": {"hair_color": "dark brown", "hair_length": "ear length",
                      "facial_hair": "full beard", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
        "prop": "a long hunting spear with a leaf-shaped blade",
    },
    "Rhino": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a thick grey rhino-hide armor suit with plated forearms, on a "
                   "towering massively muscled frame",
        "mask": "a grey rhino helmet with a single horn",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Electro": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green bodysuit crackling with blue-white electricity, with sparks "
                   "arcing off the hands",
        "mask": "a green-and-yellow lightning-bolt mask radiating from the face",
        "physique": {"body_type": "lean", "height": "average height"},
    },

    # --- DC (more) --------------------------------------------------------
    "Swamp Thing": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a towering body of mossy green vegetation and bark, with trailing "
                   "vines and roots and leaves and fungus sprouting from the shoulders",
        "eyes": "glowing red",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Etrigan the Demon": {
        "bald": True,
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red tunic with a cape and a high collar, over uniform, all-over yellow "
                   "scaled skin, with pointed ears, small horns, a fanged grin, and flames at "
                   "the hands",
        "eyes": "red",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Static Shock": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a yellow-and-black jacket with a lightning emblem and a backwards "
                   "cap, riding a flying metal disc and crackling with electricity",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "dark brown"},
    },
    "Kid Flash": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a yellow bodysuit with red sleeves and a red lightning emblem, red "
                   "goggles pushed up, and a trailing lightning blur",
        "signature": {"hair_color": "bright red", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },

    # --- Other comics (Dark Horse / 2000 AD / indie) ---------------------
    "V (V for Vendetta)": {
        "franchise": "V for Vendetta",
        "gender": "Male",
        "covers_face": True,
        "costume": "a long black cloak, a black wig, and a wide-brimmed black hat, with a "
                   "bandolier of daggers across the chest",
        "mask": "a smiling white Guy Fawkes mask with a thin curled mustache and a "
                "pointed beard",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "The Tick": {
        "franchise": "Comics",
        "gender": "Male",
        "covers_face": True,
        "costume": "a bright blue muscular bodysuit",
        "mask": "a blue head-cowl with two long wavy antennae and large blank white eyes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Abe Sapien": {
        "bald": True,
        "franchise": "Hellboy",
        "gender": "Male",
        "covers_face": True,
        "costume": "trunks and a breathing harness, over uniform, all-over blue-green scaled "
                   "skin, with red feathery gills at the neck and webbed three-fingered hands",
        "mask": "a smooth blue-green amphibian face with a finned head, red feathery "
                "gill frills, and large solid black eyes",
        "signature": {},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "The Mask": {
        "franchise": "The Mask",
        "gender": "Male",
        "covers_face": True,
        "costume": "a yellow zoot suit with a wide tie and a yellow fedora",
        "mask": "a smooth bright-green bald head with an enormous toothy grin and "
                "bulging white eyes",
        "physique": {"body_type": "lean", "height": "average height"},
    },

    # --- Star Wars (more) -------------------------------------------------
    "Qui-Gon Jinn": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "layered earth-brown Jedi robes with a leather belt and a hooded cloak",
        "signature": {"hair_color": "gray-streaked dark hair", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "facial_hair": "short beard",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a lightsaber with a green energy blade",
    },
    "Lando Calrissian": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a blue shirt with a long flowing blue cape lined in gold and orange",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "dark brown"},
    },
    "Darth Revan": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a flowing dark hooded robe with a cape",
        "mask": "a distinctive red-and-black Sith face mask",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a lightsaber with a red energy blade",
    },
    "Jabba the Hutt": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "an enormous slug-like body of slimy green-brown leathery skin with a "
                   "huge wide mouth, stubby arms, and a long coiling tail",
        "eyes": "small yellow reptilian",
        "signature": {},
        "physique": {"body_type": "plus size", "height": "average height"},
    },
    "Jar Jar Binks": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a ragged leather vest and trousers, over smooth, flawless orange amphibian "
                   "skin",
        "mask": "a long orange Gungan face with floppy ear-flaps, yellow eyes on long "
                "stalks, and a duck-billed snout",
        "signature": {},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "R2-D2": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a riveted white-and-blue cylindrical droid body with three "
                   "mechanical legs",
        "mask": "a white-and-blue rotating dome head with a single blue photoreceptor eye",
        "physique": {"body_type": "stocky", "height": "short"},
    },
    "C-3PO": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a humanoid golden metallic droid body with exposed wires at the "
                   "midriff and stiff jointed limbs",
        "mask": "a golden protocol-droid face with glowing yellow eyes",
        "physique": {"body_type": "slim", "height": "average height"},
    },
    "BB-8": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a rolling spherical white-and-orange droid body",
        "mask": "a domed white-and-orange head with a single round eye that stays on top "
                "as it rolls",
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Captain Rex": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "white clone-trooper armor with blue markings, over a black flight "
                   "suit, with a shaved head",
        "signature": {"hair_color": "golden blonde", "hair_length": "buzzed very short",
                      "facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a pair of dual blaster pistols",
    },
    "Wedge Antilles": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "an orange rebel flight suit with a white chest harness",
        "signature": {"hair_color": "medium brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },

    # --- Star Wars (Imperials, troopers, and creatures) ------------------
    "Grogu": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a loose tan woven robe, with smooth green skin, very large pointed "
                   "ears, and a few wisps of fine white hair, on a tiny figure barely knee-high",
        "eyes": "enormous dark glossy",
        "signature": {},
        "physique": {"body_type": "slim", "height": "very petite"},
    },
    "Stormtrooper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "white plastoid armor plates over a black bodysuit, with a utility belt",
        "mask": "a white stormtrooper helmet with black eye lenses and a vented "
                "frown-shaped mouth grille",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "an E-11 blaster rifle with a folding stock and a stubby barrel",
    },
    "Scout Trooper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "lightweight white shoulder, chest, and shin armor plates over a "
                   "black bodysuit",
        "mask": "a white scout-trooper helmet with a low brow and large angular black "
                "goggle lenses",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a compact hold-out blaster pistol",
    },
    "Imperial Royal Guard": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "flowing deep crimson robes and a hooded cloak over crimson armor",
        "mask": "a smooth crimson helmet with a narrow vertical visor slit",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a tall force pike with a slender black shaft and a gleaming metal "
                "blade tip",
    },
    "Praetorian Guard": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "articulated crimson plate armor with a layered crimson fabric skirt",
        "mask": "a crimson helmet with a fin-like crest and a dark narrow visor",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a vibro-voulge, a long black polearm with a glinting bladed head",
    },
    "TIE Pilot": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black Imperial flight suit with a ribbed chest control box and a "
                   "harness of cables",
        "mask": "a black flight helmet with a slotted face mask and ribbed breathing hoses",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Death Trooper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "matte black reinforced stormtrooper armor over a black bodysuit",
        "mask": "a matte black trooper helmet with a narrow red visor strip",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a black heavy blaster rifle with a long barrel",
    },
    "Dark Trooper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "heavy matte black droid-trooper armor plates with thick segmented limbs",
        "mask": "a faceless black droid-trooper helmet with a smooth blank visor",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "IG-88": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a thin chrome assassin-droid body of exposed pistons and wiring, "
                   "with a bandolier across the chest",
        "mask": "a tall cylindrical chrome droid head with a band of small red "
                "photoreceptors",
        "physique": {"body_type": "slim", "height": "very tall"},
    },
    "Tusken Raider": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "layered tan desert robes and wrappings with a bandolier and a "
                   "pouched belt",
        "mask": "a bandage-wrapped face with round metal goggle eyes and a hooded "
                "mouth grille",
        "physique": {"body_type": "lean", "height": "average height"},
        "prop": "a gaderffii war staff, a long staff with bladed and bludgeoning ends",
    },
    "Wampa": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hulking body covered in shaggy off-white fur, with long clawed arms",
        "mask": "a fanged white-furred beast face with curved horns and small dark eyes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Wicket the Ewok": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "all-over soft brown fur with a pointed orange hood and a slung satchel",
        "mask": "a small round furry face with dark eyes peering out from under the hood",
        "physique": {"body_type": "slim", "height": "very petite"},
        "prop": "a short wooden spear with a bound stone tip",
    },
    "Chief Chirpa": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "all-over grizzled grey fur with a horned headdress and a beaded pouch",
        "mask": "a grey furry muzzled face with dark eyes under a horned headdress",
        "physique": {"body_type": "slim", "height": "short"},
        "prop": "a tall gnarled wooden staff topped with bone ornaments",
    },
    "Bib Fortuna": {
        "franchise": "Star Wars",
        "gender": "Male",
        # Twi'lek: humanoid face stays visible, but the lekku replace scalp hair
        # (covers_hair) and the pale waxy skin must not be overridden by a random
        # human skin tone (body_paint suppresses the Body skin_tone).
        "costume": "long dark layered robes, with pale waxy skin and two long tapering "
                   "head-tails coiling over the shoulders",
        "eyes": "sunken reddish",
        "signature": {},
        "covers_hair": True,
        "body_paint": True,
        "skin": "pale waxy",  # no "coat of" clause for the anchor regex to read
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Greedo": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a worn green jacket and trousers, with smooth green Rodian skin",
        "mask": "a green Rodian face with a tapered snout, short antennae, and large "
                "faceted dark eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Admiral Ackbar": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a white Mon Calamari officer's uniform, with salmon-orange amphibian skin",
        "mask": "a salmon-orange Mon Calamari face with a high domed head and large round "
                "amber fish eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "stocky", "height": "average height"},
    },
    "Jawa": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a heavy hooded brown robe cinched with a bandolier",
        "mask": "a face lost in shadow beneath the hood, with glowing yellow eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "slim", "height": "very petite"},
    },
    "Ithorian": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "simple flowing robes, with brown leathery skin",
        "mask": "a brown leathery Ithorian head on a long curving hammerhead neck rising "
                "to a domed crown, with small dark wide-set eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Max Rebo": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a round pale-blue Ortolan body",
        "mask": "a pale-blue Ortolan face with a short trunk-like snout, broad floppy "
                "ears, and small round dark eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "plus size", "height": "petite"},
    },

    # --- Star Wars (expanded: aliens, Imperials, droids, creatures) ------
    "Lobot": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": False,
        "costume": "a pale blue Cloud City administrator's tunic, with a silver cybernetic "
                   "implant band wrapping around the back of a bald head from temple to temple",
        "signature": {"facial_hair": "clean shaven"},
        "eyes": "calm pale gray with a faint distant stare",
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Nute Gunray": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "elaborate layered Trade Federation viceroy robes with a tall ridged "
                   "headdress and high collar, over mottled green-gray reptilian Neimoidian skin",
        "mask": "a mottled green-gray reptilian Neimoidian face with a wide downturned mouth "
                "and reddish-orange eyes with narrow horizontal pupils",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Imperial Officer": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a crisp gray-green Imperial officer's tunic with a rank insignia plaque, "
                   "a code cylinder clipped at the chest, black gloves, and a peaked uniform cap",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "fit", "height": "average height", "skin_tone": "light"},
    },
    "Captain Phasma": {
        "franchise": "Star Wars",
        "gender": "Female",
        "covers_face": True,
        "costume": "mirror-bright chrome stormtrooper armor over a black bodysuit, with a "
                   "long flowing black cape draped from one shoulder",
        "mask": "a polished mirror-chrome stormtrooper helmet with a sharp angular crest "
                "and a dark visor",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a chrome blaster rifle",
    },
    "Snowtrooper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "bulky insulated white armor with a hooded cloak, a ribbed fabric kama "
                   "skirt, and a survival backpack",
        "mask": "a ribbed white snowtrooper helmet with round dark goggle lenses and a "
                "segmented breath hose running down to the chest",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a long-barreled blaster rifle",
    },
    "Kuiil": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a simple brown leather smock and apron over a stout Ugnaught body with "
                   "leathery pinkish skin",
        "mask": "a leathery pinkish Ugnaught face with long drooping facial whiskers, small "
                "tusks, and small dark deep-set eyes",
        "signature": {},
        "body_paint": True,
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Cassian Andor": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a worn field jacket over a henley shirt, with practical trousers and a "
                   "utility belt",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "light medium"},
    },
    "Mon Mothma": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "flowing pale senatorial robes with a long draped white cloak and a "
                   "simple metal medallion at the throat",
        "signature": {"hair_color": "auburn", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "blue-gray"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Saw Gerrera": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "heavy battle-worn robes and improvised armor plating, a breathing "
                   "apparatus tube running to the chest, and rigid mechanical legs",
        "signature": {"hair_color": "salt and pepper", "hair_length": "very short",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "dark brown"},
        "prop": "a heavy blaster rifle",
    },
    "Obi-Wan Kenobi (Force Ghost)": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "flowing layered Jedi robes rendered in a luminous, translucent pale-blue "
                   "glow, the whole figure softly shimmering and faintly transparent with a "
                   "ghostly aura",
        "signature": {"hair_color": "white", "hair_length": "ear length",
                      "facial_hair": "full beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Watto": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a grubby leather apron over a potbellied blue-gray leathery Toydarian "
                   "body with small fluttering insect-like wings, a long trunk-like snout, "
                   "and short curved tusks",
        "eyes": "small dark beady",
        "signature": {},
        "physique": {"body_type": "plump", "height": "petite"},
    },
    "Aurra Sing": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a form-fitting dark spacer's jumpsuit with bandoliers, smooth, flawless "
                   "chalk-white skin over gaunt limbs, and a bald scalp trailing a single long "
                   "thin braid with a slender antenna probe",
        "eyes": "pale with red rims",
        "signature": {},
        "physique": {"body_type": "very slim", "height": "very tall"},
        "prop": "a long-barreled sniper rifle",
    },
    "Dathomirian": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "tattered dark Nightsister robes and leather wraps, with smooth, flawless "
                   "ashen gray-white skin marked by jagged black clan tattoos across the face "
                   "and arms",
        "eyes": "pale yellow",
        "signature": {"hair_color": "near black", "hair_length": "long",
                      "hair_texture": "loosely wavy"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Asajj Ventress": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a form-fitting dark layered robe with leather straps, smooth, flawless "
                   "chalk-white skin over a bald head, and faint dark Nightsister markings "
                   "tracing the scalp and brow",
        "eyes": "pale ice-blue",
        "signature": {},
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a pair of curved-hilt red lightsabers, one ignited in each hand",
    },
    "Gran": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a simple belted laborer's tunic over a stocky grayish-brown body",
        "mask": "a grayish goat-like Gran face with a broad muzzle, floppy ears, and three "
                "large dark eyes set on short stalks",
        "physique": {"body_type": "stocky", "height": "average height"},
    },
    "Ki-Adi-Mundi": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "earth-toned layered Jedi robes, with a strikingly tall elongated Cerean "
                   "cranium rising high above the brow and pale skin",
        "signature": {"hair_color": "white", "hair_length": "shoulder length",
                      "facial_hair": "full beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "slim", "height": "tall"},
        "prop": "an ignited blue lightsaber",
    },
    "Plo Koon": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "layered earth-toned Jedi robes over reddish-orange Kel Dor skin",
        "mask": "a Kel Dor antiox face-mask with a sculpted metal breathing apparatus, large "
                "round black protective goggles, and a clawed lower jaw",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "an ignited blue lightsaber",
    },
    "Sebulba": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a scuffed podracer's harness over a wiry orange-tan leathery Dug body "
                   "whose arms and legs are inverted, the forelimbs used as legs",
        "mask": "a snarling Dug face with deep-set eyes, a flat snout, and long drooping "
                "fleshy head-tufts",
        "physique": {"body_type": "lean", "height": "petite"},
    },
    "Kaminoan": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "an elegant high-collared robe over a slender pale body, with a very long "
                   "graceful sinuous neck rising to a small smooth-skinned head",
        "eyes": "large dark almond-shaped",
        "signature": {},
        "physique": {"body_type": "very slim", "height": "very tall"},
    },
    "Cal Kestis": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a layered poncho over a henley and padded Jedi field gear, with worn "
                   "trousers and boots",
        "signature": {"hair_color": "copper", "hair_length": "ear length",
                      "facial_hair": "stubble", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "an ignited blue lightsaber",
    },
    "Greez Dritus": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a captain's vest and rolled sleeves over a stout orange-skinned Latero "
                   "body with four arms",
        "eyes": "small dark",
        "signature": {"facial_hair": "mustache"},
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Devaronian": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a rugged spacer's jacket and trousers, over deep red skin and a pair of "
                   "curved cranial horns rising from the brow of a sharp-toothed face",
        "eyes": "dark with a wicked glint",
        "signature": {"facial_hair": "goatee"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Figrin D'an": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tidy dark cantina-band suit over a slender body",
        "mask": "a Bith face: a large pink hairless dome of a head with huge black almond "
                "eyes, a flat folded nose, and a small downturned mouth",
        "physique": {"body_type": "slim", "height": "average height"},
        "prop": "a gleaming silver kloo-horn wind instrument",
    },
    "Duros": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a practical spacer's jumpsuit, over smooth hairless blue-green Duros skin "
                   "and a noseless lipless face",
        "eyes": "large round red",
        "signature": {},
        "physique": {"body_type": "slim", "height": "tall"},
    },
    "Doctor Cornelius Evazan": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a grimy layered spacer's jacket, with a heavily scarred face crossed by "
                   "a deep diagonal scar and rough disfiguring marks",
        "signature": {"hair_color": "dark brown", "hair_length": "ear length",
                      "hair_style": "windswept", "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "light"},
    },
    "Ponda Baba": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a heavy quilted spacer's jacket over a broad hairy body",
        "mask": "an Aqualish face with coarse fur, a pair of downward walrus tusks, and "
                "large dark bulbous eyes",
        "physique": {"body_type": "stocky", "height": "average height"},
    },
    "Bothan": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a practical belted tunic and vest over a lean fur-covered body",
        "mask": "a fur-covered Bothan face with a short canine muzzle, alert eyes, and large "
                "pointed swept-back ears",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Constable Zuvio": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a layered militia uniform with a bandolier, over leathery greenish Kyuzo "
                   "skin, beneath a wide flat-brimmed segmented Kyuzo helmet",
        "eyes": "deep-set dark and stern",
        "signature": {},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Maz Kanata": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "layered earth-toned robes over a tiny deeply wrinkled orange-skinned "
                   "body, with oversized round vision goggles pushed up on the brow",
        "eyes": "large warm brown behind thick round goggle lenses",
        "signature": {},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Nien Nunb": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "an orange Rebel flight suit with a life-support vest and harness",
        "mask": "a Sullustan face with heavy pouched jowls, large round dark eyes, and broad "
                "flap-like ears",
        "physique": {"body_type": "stocky", "height": "short"},
    },
    "Unkar Plutt": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a grubby junk-boss apron and layered rags over a huge bloated body",
        "mask": "a Crolute face: a large pale fleshy blobby head with small sunken eyes and "
                "drooping heavy jowls",
        "physique": {"body_type": "plus size", "height": "tall"},
    },
    "Zorii Bliss": {
        "franchise": "Star Wars",
        "gender": "Female",
        "covers_face": True,
        "costume": "an armored maroon-and-gold flight suit with a utility belt and twin holsters",
        "mask": "a sleek gold-and-maroon spacer helmet with a dark wraparound visor",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a pair of blaster pistols",
    },
    "Dexter Jettster": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a stained cook's apron over a huge four-armed Besalisk body",
        "mask": "a Besalisk face with a row of fleshy chin wattles, small eyes, and a broad "
                "toothy mouth",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Hondo Ohnaka": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a flamboyant pirate coat with a bandolier and brass goggles pushed up "
                   "on the brow, over deeply creased leathery Weequay skin with thin dark "
                   "facial tendrils framing the jaw",
        "eyes": "dark and shrewd",
        "signature": {},
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Sabine Wren": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "brightly painted Mandalorian beskar armor in purples and oranges over a "
                   "gray flight suit, with a jetpack and a holstered blaster, helmet held at "
                   "the hip",
        "signature": {"hair_color": "black with colored tips", "hair_length": "jaw length",
                      "hair_style": "windswept", "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light"},
    },
    "Zeb Orrelios": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a worn cargo harness and bandolier over a towering purple-gray fur-covered "
                   "Lasat body with heavy muscled arms",
        "mask": "a Lasat face covered in purple-gray fur with bold dark stripes, prominent "
                "sideburns, a heavy brow, and small pointed tusks",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Grand Inquisitor": {
        "bald": True,
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "sleek black Inquisitor armor and robes, over smooth, flawless ashen gray "
                   "Pau'an skin etched with thin red ritual markings across a gaunt hairless "
                   "face",
        "eyes": "pale yellow sunken",
        "signature": {},
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a spinning double-bladed red lightsaber",
    },
    "Bossk": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a yellow padded flight suit with bandoliers over a scaly green reptilian "
                   "Trandoshan body with clawed hands",
        "mask": "a reptilian Trandoshan face with rough green scales, slit reptile eyes, and "
                "rows of small sharp teeth",
        "physique": {"body_type": "athletic", "height": "tall"},
        "prop": "a heavy blaster rifle",
    },
    "Dengar": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "battle-worn fatigues and armor scraps, with a grimy off-white bandage "
                   "wrapped turban-like around the head and brow",
        "signature": {"facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "light"},
        "prop": "a heavy blaster rifle",
    },
    "Zuckuss": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a heavy layered protective coat and breathing tanks over a slight body",
        "mask": "a Gand insectoid head with a ribbed breathing respirator over the lower "
                "face and large round dark eyes",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "K-2SO": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a tall lanky matte-black reprogrammed Imperial security droid body with "
                   "long thin jointed limbs and a narrow torso",
        "mask": "a tall angular black droid head with a flat brow and a pair of glowing "
                "yellow photoreceptor eyes",
        "physique": {"body_type": "slim", "height": "very tall"},
    },
    "Chopper": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a squat dented orange-and-white cylindrical astromech body standing on "
                   "two mismatched mechanical legs with a small third retractable foot",
        "mask": "a rounded astromech dome head with a single glowing photoreceptor and a "
                "pair of bent antennae",
        "physique": {"body_type": "stocky", "height": "short"},
    },
    "Battle Droid": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a thin skeletal tan B1 battle-droid body with spindly jointed limbs and "
                   "a folded backpack unit",
        "mask": "a narrow elongated tan droid head with dark recessed eye sockets and a "
                "slit-like mouth grille",
        "physique": {"body_type": "very slim", "height": "tall"},
    },
    "Gonk Droid": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a boxy gray walking power-droid body shaped like an upright crate, "
                   "plodding on two stubby thick legs",
        "mask": "a featureless boxy droid head-end with two small dim photoreceptor lights",
        "physique": {"body_type": "stocky", "height": "short"},
    },
    "2-1B Droid": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a humanoid coppery medical-droid body with a transparent chest panel "
                   "and exposed neck cabling",
        "mask": "a smooth coppery medical-droid face with a fixed expression and softly "
                "glowing eyes",
        "physique": {"body_type": "slim", "height": "average height"},
    },
    "4-LOM": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a humanoid charcoal-gray protocol-droid body with jointed limbs and a "
                   "slung bandolier of gear",
        "mask": "an insectoid protocol-droid face with large round bulbous photoreceptors "
                "and segmented metal mandibles",
        "physique": {"body_type": "slim", "height": "tall"},
        "prop": "a blaster rifle",
    },
    "Porg": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a plump round body of brown-and-cream feathers with stubby flipper-like "
                   "wings and small webbed feet",
        "mask": "a round porg face with enormous orange eyes and a small downturned beak",
        "physique": {"body_type": "plump", "height": "very petite"},
    },
    "Salacious Crumb": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a scrawny brown reptilian Kowakian monkey-lizard body with spindly limbs "
                   "and a long whip-like tail",
        "mask": "a cackling monkey-lizard face with a hooked beak, big yellow eyes, and a "
                "frill of long spiny ears",
        "physique": {"body_type": "very slim", "height": "very petite"},
    },
    "Mynock": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a winged black leathery parasite body with broad membranous bat-like "
                   "wings and clawed wing-tips",
        "mask": "a flat leathery mynock head with no eyes and a round fleshy suction-cup mouth",
        "physique": {"body_type": "slim", "height": "average height"},
    },
    "Rancor": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hulking hunched body of thick brown wrinkled leathery hide with massive "
                   "long clawed arms and stubby powerful legs",
        "mask": "a monstrous rancor head with a wide tusked maw, jagged teeth, deep-set small "
                "eyes, and ridged brown hide",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Tauntaun": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a stocky gray-and-white furred reptilian body on two clawed legs with a "
                   "thick balancing tail and small forelimbs",
        "mask": "a horned reptilian tauntaun head with a blunt snout, curved side horns, and "
                "shaggy fur",
        "physique": {"body_type": "stocky", "height": "tall"},
    },
    "Bantha": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a massive body of thick shaggy brown fur standing on four sturdy legs",
        "mask": "a shaggy bantha head with a long muzzle and a great pair of curling spiral "
                "horns sweeping back from the brow",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Loth-Cat": {
        "franchise": "Star Wars",
        "gender": "Male",
        "covers_face": True,
        "costume": "a small lithe body of tan-and-white striped fur with a long tail and "
                   "soft padded paws",
        "mask": "a loth-cat face with large pointed tufted ears, wide bright eyes, and short "
                "whiskered fur",
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },

    # --- Anime / classic toons (Speed Racer) -----------------
    "Speed Racer": {
        "franchise": "Anime",
        "gender": "Male",
        "costume": "a white racing shirt with a red scarf and a yellow M scarf-pin",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },

    # --- Video game mascots / icons --------------------------------------
    "Sonic the Hedgehog": {
        "franchise": "Sega",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of bright blue fur with a peach muzzle and "
                   "arms, white gloves, and red-and-white running shoes with gold buckles",
        "mask": "a blue hedgehog head with six swept-back spiky quills and large "
                "connected green eyes",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Bowser": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green-and-tan spiked turtle shell, a spiked black collar and arm "
                   "cuffs, and clawed hands and feet",
        "mask": "a horned green Koopa head with a shock of red hair, two curved horns, "
                "and fangs",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Donkey Kong": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of brown gorilla fur on a towering muscular "
                   "frame, with a red necktie bearing yellow DK initials",
        "mask": "a brown gorilla face with small dark eyes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Yoshi": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "orange boots, with uniform, all-over green dinosaur skin, a cream belly, a "
                   "spiny orange back-ridge, and a red saddle-shell",
        "mask": "a round green dinosaur head with big friendly eyes and a wide snout",
        "physique": {"body_type": "stocky", "height": "average height"},
    },
    "Toad": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "a large white mushroom cap with red spots, a blue vest with a white "
                   "collar, and white trousers",
        "signature": {"eye_color": "nearly black"},
        "physique": {"body_type": "stocky", "height": "petite", "skin_tone": "fair"},
    },
    "Wario": {
        "franchise": "Nintendo",
        "gender": "Male",
        "costume": "a yellow cap with a blue W, a yellow shirt, and purple overalls, with "
                   "a big pink nose and a zigzag scowl",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "Kirby": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "a small round pink ball-shaped body with stubby arms and red "
                   "rounded feet",
        "mask": "a round pink face with large dark oval eyes and rosy oval cheeks",
        "physique": {"body_type": "plump", "height": "very petite"},
    },
    "Fox McCloud": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "a white-and-green flight jacket with a red neckerchief and a wrist "
                   "communicator, over an even, all-over coat of orange-and-white fur",
        "mask": "an orange-and-white fox head with pointed ears and green eyes",
        "physique": {"body_type": "athletic", "height": "average height"},
        "prop": "a compact blaster pistol",
    },
    "Captain Falcon": {
        "franchise": "Nintendo",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue racing bodysuit with shoulder pads, a yellow scarf, and "
                   "knee-high boots",
        "mask": "a blue-and-red full-face racing helmet with a golden falcon emblem",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Pac-Man": {
        "franchise": "Namco",
        "gender": "Male",
        "covers_face": True,
        "costume": "a round bright-yellow disc-shaped body",
        "mask": "a yellow circular face with a wide open wedge mouth and a single dot eye",
        "physique": {"body_type": "plump", "height": "average height"},
    },
    "Big Daddy": {
        "franchise": "BioShock",
        "gender": "Male",
        "covers_face": True,
        "costume": "a riveted bronze deep-sea diving suit on a towering hulking frame, "
                   "with a massive arm-mounted drill",
        "mask": "a round brass porthole diving helmet with glowing yellow portholes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },

    # --- Looney Tunes -----------------------------------------------------
    "Bugs Bunny": {
        "franchise": "Looney Tunes",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of grey fur with a white belly and muzzle, and "
                   "white gloves, on a tall lanky frame",
        "mask": "a grey rabbit head with very long upright ears, half-lidded eyes, and "
                "buck teeth",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a half-eaten orange carrot",
    },
    "Daffy Duck": {
        "franchise": "Looney Tunes",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of glossy black feathers with a white neck "
                   "ring and orange webbed feet",
        "mask": "a black duck head with an orange bill and wide white eyes",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Yosemite Sam": {
        "franchise": "Looney Tunes",
        "gender": "Male",
        "costume": "a red shirt and chaps, tall boots, and a cowboy hat over a shock of "
                   "red hair",
        "signature": {"hair_color": "bright red", "hair_length": "very short",
                      "facial_hair": "mustache", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
        "prop": "a pair of holstered six-shooter pistols",
    },

    # --- Disney / Pixar (more) -------------------------------------------
    "Mickey Mouse": {
        "franchise": "Disney",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full black-furred mouse suit, no bare skin
        "costume": "red shorts with two white buttons, white gloves, and big yellow "
                   "shoes, on a small round mouse frame",
        "mask": "a black mouse head with two large round ears, a peach face, and cheerful "
                "eyes",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Donald Duck": {
        "franchise": "Disney",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue sailor shirt and a blue sailor cap with a red bow, over an "
                   "even, all-over coat of white feathers with orange webbed feet, and no "
                   "trousers",
        "mask": "a white duck head with an orange bill and blue eyes",
        "physique": {"body_type": "stocky", "height": "short"},
    },
    "Goofy": {
        "franchise": "Disney",
        "gender": "Male",
        "covers_face": True,
        "costume": "an orange turtleneck under a black vest, blue trousers, a tall green "
                   "hat, white gloves, and oversized brown shoes",
        "mask": "a black dog face with long droopy ears, two buck teeth, and kind eyes",
        "physique": {"body_type": "lean", "height": "very tall"},
    },
    "Genie": {
        "franchise": "Aladdin",
        "gender": "Male",
        "costume": "golden wrist cuffs and a black topknot on a bald head, over smooth, flawless "
                   "bright blue skin, with a wispy blue tail instead of legs on a large floating "
                   "muscular frame",
        "signature": {"facial_hair": "goatee", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Peter Pan": {
        "franchise": "Peter Pan",
        "gender": "Male",
        "costume": "a green tunic with a jagged hem, green tights, and a green pointed "
                   "cap with a red feather",
        "signature": {"hair_color": "copper", "hair_length": "very short",
                      "eye_color": "green"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a small dagger",
    },
    "Stitch": {
        "franchise": "Lilo and Stitch",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of blue fur on a small sturdy koala-like alien "
                   "frame, with two extra arms and retractable back spines",
        "mask": "a blue koala-like alien head with large notched pointed ears, big black "
                "eyes, and a wide toothy mouth",
        "physique": {"body_type": "stocky", "height": "petite"},
    },
    "Gru": {
        "franchise": "Despicable Me",
        "gender": "Male",
        "costume": "a grey-and-black horizontal-striped scarf, a long dark coat, a tan "
                   "turtleneck, and a bald head with a long pointed nose",
        "signature": {"facial_hair": "clean shaven", "eye_color": "dark brown"},
        "physique": {"body_type": "average", "height": "tall", "skin_tone": "fair"},
    },
    "Buzz Lightyear": {
        "franchise": "Toy Story",
        "gender": "Male",
        "costume": "a white space-ranger suit with green and purple panels, a clear dome "
                   "helmet, a green chin and chest control panel, retractable white wings, "
                   "and a wrist communicator",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Woody": {
        "franchise": "Toy Story",
        "gender": "Male",
        "costume": "a yellow plaid shirt, a cow-print vest, blue jeans with a brown belt, "
                   "an empty holster, brown cowboy boots, and a brown cowboy hat",
        "signature": {"hair_color": "medium brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Jiminy Cricket": {
        "franchise": "Pinocchio",
        "gender": "Male",
        "costume": "a black top hat, a blue tailcoat over a yellow vest, white gloves, "
                   "and spats, on a tiny cricket frame",
        "signature": {"eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "very petite", "skin_tone": "fair"},
        "prop": "a small umbrella",
    },

    # --- Nickelodeon / Cartoon Network -----------------------------------
    "SpongeBob SquarePants": {
        "franchise": "Nickelodeon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a white shirt with a red tie, brown square shorts, white knee socks "
                   "with stripes, and black shoes, on a square porous yellow sponge body",
        "mask": "a square porous yellow face with big blue eyes and prominent buck teeth",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Patrick Star": {
        "franchise": "Nickelodeon",
        "gender": "Male",
        "covers_face": True,
        "costume": "green-and-purple flowered shorts on a chunky pink starfish body",
        "mask": "a pink starfish face with small eyes and thick eyebrows",
        "physique": {"body_type": "plump", "height": "average height"},
    },
    "Squidward": {
        "franchise": "Nickelodeon",
        "gender": "Male",
        "covers_face": True,
        "costume": "a brown short-sleeved shirt on a tall lanky teal octopus body with "
                   "six legs",
        "mask": "a teal octopus head with a long drooping nose and half-lidded eyes",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Finn the Human": {
        "franchise": "Adventure Time",
        "gender": "Male",
        "costume": "a white hat with two round bear-like ears, a light-blue shirt and "
                   "shorts, and a green backpack",
        "signature": {"eye_color": "nearly black"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a golden sword",
    },
    "Jake the Dog": {
        "franchise": "Adventure Time",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of yellow-orange fur on a stretchy, elastic "
                   "dog body that can morph and grow",
        "mask": "a yellow-orange dog face with simple dot eyes and a wide muzzle",
        "physique": {"body_type": "average", "height": "average height"},
    },

    # --- The Simpsons / Rick and Morty -----------------------------------
    "Homer Simpson": {
        "franchise": "The Simpsons",
        "gender": "Male",
        "costume": "a white short-sleeved shirt and blue trousers, over smooth, flawless yellow "
                   "skin, with a bald head bearing two stray top hairs",
        "eyes": "large round white",
        "signature": {"facial_hair": "five o'clock shadow"},
        "physique": {"body_type": "plus size", "height": "average height"},
    },
    "Bart Simpson": {
        "franchise": "The Simpsons",
        "gender": "Male",
        "costume": "an orange short-sleeved t-shirt, blue shorts, and blue sneakers, over "
                   "smooth, flawless yellow skin, with spiky yellow hair",
        "eyes": "large round white",
        "signature": {"hair_color": "yellow", "hair_length": "very short"},
        "physique": {"body_type": "slim", "height": "petite"},
    },
    "Rick Sanchez": {
        "franchise": "Rick and Morty",
        "gender": "Male",
        "costume": "a white lab coat over a light-blue shirt and brown trousers, with a "
                   "constant line of drool",
        "signature": {"hair_color": "electric blue", "hair_length": "very short",
                      "eye_color": "pale blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
    },
    "Morty Smith": {
        "franchise": "Rick and Morty",
        "gender": "Male",
        "costume": "a yellow shirt, light-blue trousers, and white sneakers, with an "
                   "anxious open-mouthed expression",
        "signature": {"hair_color": "medium brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "fair"},
    },
    "Mumen Rider": {
        "franchise": "One Punch Man",
        "gender": "Male",
        "costume": "a light-blue bodysuit with a green chest emblem, knee and elbow pads, "
                   "and a green bicycle helmet with goggles",
        "signature": {"eye_color": "dark brown"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "fair"},
    },

    # --- Hanna-Barbera classics ------------------------------------------
    "Fred Flintstone": {
        "franchise": "The Flintstones",
        "gender": "Male",
        "costume": "an orange tunic with black spots, a blue necktie, and bare feet",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "eye_color": "nearly black"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "fair"},
    },
    "Barney Rubble": {
        "franchise": "The Flintstones",
        "gender": "Male",
        "costume": "a brown furry one-shoulder tunic and bare feet",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "nearly black"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "George Jetson": {
        "franchise": "The Jetsons",
        "gender": "Male",
        "costume": "a white space-age tunic with a high collar and white gloves",
        "signature": {"hair_color": "medium brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Shaggy": {
        "franchise": "Scooby-Doo",
        "gender": "Male",
        "costume": "a faded green t-shirt and maroon bell-bottom trousers, with a "
                   "slouching posture",
        "signature": {"hair_color": "dirty blonde", "hair_length": "ear length",
                      "facial_hair": "stubble", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Fred Jones": {
        "franchise": "Scooby-Doo",
        "gender": "Male",
        "costume": "a white sweater with blue accents, an orange ascot, and blue trousers",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },

    # --- Folklore / legend / literature ----------------------------------
    "Robin Hood": {
        "franchise": "Folklore",
        "gender": "Male",
        "costume": "a green hooded tunic and hose with a wide belt and a green feathered "
                   "cap",
        "signature": {"hair_color": "medium brown", "hair_length": "ear length",
                      "facial_hair": "short beard", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
        "prop": "a longbow with a quiver of arrows",
    },
    "King Arthur": {
        "franchise": "Legend",
        "gender": "Male",
        "costume": "silver chainmail and plate armor over a blue tabard, with a golden "
                   "crown",
        "signature": {"hair_color": "medium brown", "hair_length": "ear length",
                      "facial_hair": "short beard", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "Excalibur, a gleaming broadsword with a golden cross-hilt",
    },
    "Merlin": {
        "franchise": "Legend",
        "gender": "Male",
        "costume": "deep-blue robes patterned with golden stars and moons and a tall "
                   "pointed hat",
        "signature": {"hair_color": "white", "hair_length": "very long",
                      "facial_hair": "full beard", "eye_color": "pale blue"},
        "physique": {"body_type": "slim", "height": "tall", "skin_tone": "fair"},
        "prop": "a long gnarled wooden staff",
    },
    "Santa Claus": {
        "franchise": "Folklore",
        "gender": "Male",
        "costume": "a red suit and hat with white fur trim, a wide black belt, and black "
                   "boots",
        "signature": {"hair_color": "white", "hair_length": "ear length",
                      "facial_hair": "full beard", "eye_color": "bright blue"},
        "physique": {"body_type": "plus size", "height": "average height", "skin_tone": "fair"},
        "prop": "a bulging sack of toys",
    },
    "Paddington Bear": {
        "franchise": "Literature",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue duffle coat with toggles and a battered red wide-brimmed hat, "
                   "over an even, all-over coat of brown fur",
        "mask": "a brown bear face with kind dark eyes",
        "physique": {"body_type": "stocky", "height": "short"},
        "prop": "a small worn suitcase",
    },
    "Curious George": {
        "franchise": "Literature",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of brown fur on a small monkey frame with a "
                   "long tail and no clothing",
        "mask": "a brown monkey face with big curious eyes",
        "physique": {"body_type": "slim", "height": "petite"},
    },

    # --- Dr. Seuss --------------------------------------------------------
    "The Grinch": {
        "franchise": "Dr. Seuss",
        "gender": "Male",
        "costume": "a tattered red-and-white Santa coat and hat, over an even, all-over "
                   "coat of shaggy green fur, with a sour pointed grin",
        "eyes": "narrow yellow",
        "signature": {},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Horton": {
        "franchise": "Dr. Seuss",
        "gender": "Male",
        "covers_face": True,
        "costume": "nothing but uniform, all-over grey elephant skin on a large frame",
        "mask": "a grey elephant head with oversized floppy ears, a long trunk, and kind "
                "round eyes",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "The Lorax": {
        "franchise": "Dr. Seuss",
        "gender": "Male",
        "costume": "an even, all-over coat of orange fur on a small stout frame, with "
                   "thick yellow eyebrows",
        "signature": {"hair_color": "yellow", "facial_hair": "mustache",
                      "eye_color": "amber"},
        "physique": {"body_type": "stocky", "height": "petite"},
    },

    # --- Winnie the Pooh --------------------------------------------------
    "Winnie the Pooh": {
        "franchise": "Winnie the Pooh",
        "gender": "Male",
        "covers_face": True,
        "costume": "a short red t-shirt that does not reach the belly, over an even, "
                   "all-over coat of golden-yellow fur",
        "mask": "a round golden-yellow bear face with small black eyes",
        "physique": {"body_type": "plump", "height": "short"},
    },
    "Tigger": {
        "franchise": "Winnie the Pooh",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of orange fur with black stripes and a big "
                   "springy coiled tail",
        "mask": "an orange-and-black tiger face with large eyes and a wide grin",
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Eeyore": {
        "franchise": "Winnie the Pooh",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of grey fur on a small droopy donkey frame, "
                   "with a thin tail tied with a pink bow",
        "mask": "a grey donkey face with sad half-lidded eyes and a long muzzle",
        "physique": {"body_type": "average", "height": "short"},
    },
    "Piglet": {
        "franchise": "Winnie the Pooh",
        "gender": "Male",
        "covers_face": True,
        "costume": "a pink-and-magenta striped pullover on a tiny piglet body",
        "mask": "a small pink piglet face with large ears",
        "physique": {"body_type": "slim", "height": "very petite"},
    },

    # --- Movie monsters / action icons -----------------------------------
    "Dracula": {
        "franchise": "Movie",
        "gender": "Male",
        "costume": "a black formal suit with a high-collared cape lined in red, and two "
                   "long fangs",
        "signature": {"hair_color": "jet black", "hair_length": "ear length",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "very pale"},
    },
    "Frankenstein's Monster": {
        "franchise": "Movie",
        "gender": "Male",
        "costume": "an ill-fitting dark suit and heavy elevated boots, over smooth, flawless "
                   "pale green-grey skin, with a flat-topped head, stitched scars, and two neck "
                   "bolts",
        "eyes": "dark and sunken",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "The Wolf Man": {
        "franchise": "Movie",
        "gender": "Male",
        "costume": "a torn shirt and trousers, over an even, all-over coat of brown fur, "
                   "with a fanged snout, pointed ears, and clawed hands",
        "eyes": "yellow",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "The Mummy": {
        "franchise": "Movie",
        "gender": "Male",
        "covers_face": True,
        "costume": "a body wrapped head to toe in tattered grey ancient bandages, with "
                   "dried preserved skin showing through, one arm outstretched",
        "mask": "a bandage-wrapped face with hollow dark eye sockets",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Godzilla": {
        "franchise": "Movie",
        "gender": "Male",
        "covers_face": True,
        "costume": "an even, all-over coat of charcoal-grey scaled hide with rows of "
                   "jagged white-glowing dorsal fins and a thick powerful tail, on a "
                   "colossal frame",
        "mask": "a charcoal-grey reptilian head with small glowing eyes and rows of teeth",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Rambo": {
        "franchise": "Movie",
        "gender": "Male",
        "costume": "a red headband, torn fatigues, and an ammo bandolier across a bare "
                   "sweat-sheened chest",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
        "prop": "a large survival knife",
    },
    "William Wallace": {
        "franchise": "Braveheart",
        "gender": "Male",
        "costume": "a tartan kilt and leather armor, with blue woad war paint streaked "
                   "across the face",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a great two-handed claymore",
    },

    # === Mascots (more) ===================================================
    "Ronald McDonald": {
        "franchise": "McDonald's",
        "gender": "Male",
        "costume": "a bright yellow jumpsuit with a red-and-white striped long-sleeve "
                   "undershirt, oversized red shoes, a red bow tie, and a wide red-and-yellow "
                   "striped belt, with white clown face paint and a wide painted red smile",
        "signature": {"hair_color": "bright red", "hair_length": "shoulder length",
                      "hair_texture": "curly", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Hamburglar": {
        "franchise": "McDonald's",
        "gender": "Male",
        "covers_face": True,
        "costume": "a black-and-white striped one-piece suit with a red-lined black cape "
                   "and a wide yellow belt buckle",
        "mask": "a wide-brimmed black hat pulled low over a black domino mask and an "
                "upturned coat collar",
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Grimace": {
        "franchise": "McDonald's",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full rounded mascot suit, no bare skin
        "costume": "a huge rounded fuzzy purple mascot body with short stubby arms and legs",
        "mask": "a rounded fuzzy purple mascot head with two small black dot eyes and a wide grin",
        "physique": {"body_type": "chubby", "height": "very tall"},
    },
    "Wendy": {
        "franchise": "Wendy's",
        "gender": "Female",
        "costume": "a blue-and-white striped dress with a white apron, a red bandana-style collar",
        "signature": {"hair_color": "bright red", "hair_length": "shoulder length",
                      "hair_texture": "curly", "hair_style": "high pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "fair"},
    },
    "Kool-Aid Man": {
        "franchise": "Kool-Aid",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # giant glass pitcher shell, no bare skin
        "costume": "a giant smiling glass pitcher body filled with bright red liquid",
        "mask": "the pitcher's own molded glass face with a huge painted grin",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Michelin Man": {
        "franchise": "Michelin",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # stacked rubber-ring mascot suit, no bare skin
        "costume": "a body built from stacked white rubber tire rings from neck to feet",
        "mask": "a smooth white rubber ring-stacked head with small dark eyes and a friendly grin",
        "physique": {"body_type": "plus size", "height": "tall"},
    },
    "Big Boy": {
        "franchise": "Big Boy",
        "gender": "Male",
        "costume": "red-and-white checkered overalls over a white short-sleeve shirt",
        "signature": {"hair_color": "jet black", "hair_length": "very short",
                      "hair_style": "top knot", "eye_color": "dark brown"},
        "physique": {"body_type": "chubby", "height": "short", "skin_tone": "fair"},
        "prop": "a platter stacked with a double-decker hamburger",
    },
    "Mr. Peanut": {
        "franchise": "Planters",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full peanut-shell mascot suit, no bare skin
        "costume": "a tan peanut-shell mascot body with slender black arms and legs, "
                   "a black top hat, white gloves, and white spats over black shoes",
        "mask": "a smooth tan peanut-shell head with a single monocle over one eye "
                "and a cheerful smile",
        "physique": {"body_type": "slim", "height": "tall"},
        "prop": "a black wooden cane",
    },
    "Colonel Sanders": {
        "franchise": "KFC",
        "gender": "Male",
        "costume": "a white double-breasted suit over a white shirt with a black "
                   "western string tie, and black-framed glasses",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "hair_texture": "sleek straight", "facial_hair": "goatee",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "stocky", "height": "average height", "skin_tone": "fair"},
    },
    "Jolly Green Giant": {
        "franchise": "Green Giant",
        "gender": "Male",
        "costume": "a short toga made of woven green leaves, with smooth, flawless rich green "
                   "skin covering his face and entire body, on a towering figure of impossible "
                   "gigantic scale and proportion",
        "signature": {"hair_color": "emerald green", "hair_length": "very short",
                      "hair_texture": "wavy", "hair_style": "slicked back"},
        "size_scale": "giant",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Pillsbury Doughboy": {
        "franchise": "Pillsbury",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # plump smooth dough mascot suit, no bare skin
        "costume": "a plump, smooth white dough mascot body with a small white "
                   "chef's scarf at the neck",
        "mask": "a rounded smooth white dough head under a white chef's hat, with "
                "blue dot eyes and a soft bashful giggle of a smile",
        "physique": {"body_type": "chubby", "height": "short"},
    },
    "Mr. Clean": {
        "franchise": "Mr. Clean",
        "gender": "Male",
        "bald": True,
        "costume": "a crisp fitted white t-shirt and white trousers, with a single "
                   "gold hoop earring and a clean-shaven bald head",
        # The gleaming bald head IS the look: no random hat/sunglasses draw on top.
        "signature": {"eyebrows": "thick and straight", "eye_color": "bright blue",
                      "accessories": "no accessories"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "fair"},
    },
    "Cap'n Crunch": {
        "franchise": "Cap'n Crunch",
        "gender": "Male",
        "covers_hair": True,  # large bicorne hat fully covers the scalp; face shows
        "costume": "a blue Napoleonic naval coat with gold epaulettes and gold "
                   "buttons over white trousers, a large blue bicorne hat with a "
                   "gold 'C' emblem, and bushy white eyebrows",
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "Tony the Tiger": {
        "franchise": "Kellogg's",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full tiger mascot suit, no bare skin
        "costume": "a full orange tiger mascot suit with black stripes and a white "
                   "belly, with a red bandana-style neckerchief tied at the throat",
        "mask": "an orange tiger mascot head with black stripes, a white muzzle, "
                "and a wide confident grin",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Chester Cheetah": {
        "franchise": "Cheetos",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full cheetah mascot suit, no bare skin
        "costume": "a full orange spotted cheetah mascot suit with a long slim "
                   "tail and white high-top sneakers",
        "mask": "a sleek orange cheetah mascot head wearing dark wraparound "
                "sunglasses, with a sly toothy grin",
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Count Chocula": {
        "franchise": "General Mills",
        "gender": "Male",
        "costume": "a chocolate-brown vampire tailcoat over a lighter brown vest, "
                   "a high-collared cape lined in tan, and a large round 'C' medallion "
                   "on a chain",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "dark brown"},
        "physique": {"body_type": "very slim", "height": "tall", "skin_tone": "very pale"},
    },
    "Energizer Bunny": {
        "franchise": "Energizer",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full plush bunny mascot suit, no bare skin
        "costume": "a pink plush bunny mascot body with a large battery strapped "
                   "to its back and blue-and-white sandals",
        "mask": "a pink plush bunny mascot head with tall upright ears and cool "
                "blue sunglasses",
        "physique": {"body_type": "slim", "height": "short"},
        "prop": "a large blue-and-white bass drum with a mallet",
    },
    "Geico Gecko": {
        "franchise": "Geico",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full gecko mascot suit, no bare skin
        "costume": "a full bright green gecko mascot suit with a long curved tail "
                   "and a pale green belly",
        "mask": "a smooth bright green gecko mascot head with large friendly eyes "
                "and a wide easygoing smile",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Duolingo Owl": {
        "franchise": "Duolingo",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,  # full round owl mascot suit, no bare skin
        "costume": "a round bright green owl mascot body with darker green wings "
                   "and orange feet",
        "mask": "a round bright green owl mascot head with huge white-ringed "
                "cartoon eyes and a small orange beak",
        "physique": {"body_type": "chubby", "height": "short"},
    },

    # === More fictional-character gaps (2026 sweep) =======================
    "Shrek": {
        "franchise": "Shrek",
        "gender": "Male",
        "bald": True,
        "costume": "a brown vest over a rough cream peasant shirt and brown trousers, with "
                   "smooth, flawless green ogre skin",
        "eyes": "brown",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Robin": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red tunic with a yellow R chest emblem, green shorts, gloves and "
                   "boots, and a yellow-lined black cape",
        "signature": {"hair_color": "jet black", "hair_length": "very short", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Gollum": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "bald": True,
        "costume": "a tattered loincloth, with uniform, all-over clammy pale grey skin stretched "
                   "over a gaunt, emaciated frame",
        "eyes": "pale luminous",
        "physique": {"body_type": "very slim", "height": "short"},
    },
    "Bilbo Baggins": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "a brown waistcoat over a cream shirt with a velvet coat, and bare "
                   "hairy feet",
        "signature": {"hair_color": "medium brown", "hair_length": "ear length",
                      "hair_texture": "curly", "eye_color": "bright blue"},
        "physique": {"body_type": "chubby", "height": "very petite", "skin_tone": "fair"},
    },
    "Genos": {
        "franchise": "One Punch Man",
        "gender": "Male",
        "covers_body": True,  # cyborg body from the neck down, no bare skin for jewellery
        "costume": "a sleek black metal cyborg body with vented forearms and exposed "
                   "joint mechanisms, worn under a black sleeveless top",
        "eyes": "glowing amber",
        "signature": {"hair_color": "golden blonde", "hair_length": "short pixie"},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Samwise Gamgee": {
        "franchise": "The Lord of the Rings",
        "gender": "Male",
        "costume": "a green waistcoat over a tan shirt with a brown travel cloak, and bare "
                   "hairy feet",
        "signature": {"hair_color": "medium brown", "hair_length": "ear length",
                      "hair_texture": "curly", "eye_color": "medium brown"},
        "physique": {"body_type": "stocky", "height": "very petite", "skin_tone": "fair"},
    },
    "Majin Buu": {
        "franchise": "Dragon Ball",
        "gender": "Male",
        "bald": True,
        "costume": "a black-and-yellow vest with white baggy trousers and a Majin-symbol belt, "
                   "with uniform, all-over pale pink rubbery skin",
        "eyes": "small black",
        "physique": {"body_type": "plump", "height": "average height"},
    },
    "Yondu": {
        "franchise": "Marvel",
        "gender": "Male",
        "bald": True,
        "costume": "a weathered red leather Ravager coat over dark tactical gear, with smooth, "
                   "flawless blue skin and a red crest-shaped fin implant set into the scalp",
        "eyes": "pale blue",
        "physique": {"body_type": "lean", "height": "tall"},
        "prop": "a silver yaka arrow",
    },
    "Buffy Summers": {
        "franchise": "Buffy the Vampire Slayer",
        "gender": "Female",
        "costume": "a fitted tank top under a leather jacket, tight jeans, and practical boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_texture": "loosely wavy", "eye_color": "green"},
        "physique": {"body_type": "petite and slim", "height": "average height", "skin_tone": "fair"},
        "prop": "a wooden stake",
    },
    "Ellie Williams": {
        "franchise": "The Last of Us",
        "gender": "Female",
        "costume": "a worn red t-shirt under a grey hoodie, dark jeans, and scuffed sneakers, "
                   "with a backpack",
        "signature": {"hair_color": "light chestnut", "hair_length": "shoulder length",
                      "hair_texture": "slightly wavy", "eye_color": "green"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Commander Shepard": {
        "franchise": "Mass Effect",
        "gender": "Female",
        "covers_body": True,  # full hardsuit armour shell, no bare skin for jewellery
        "costume": "a dark grey N7 hardsuit with red-and-white arm and chest stripes and "
                   "armored plating",
        "signature": {"hair_color": "bright red", "hair_length": "shoulder length",
                      "hair_texture": "slightly wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Princess Bubblegum": {
        "franchise": "Adventure Time",
        "gender": "Female",
        "costume": "a fitted pink gown with a modest neckline and a small gold crown, with "
                   "smooth, flawless pale pink skin",
        "eyes": "pink",
        "signature": {"hair_color": "baby pink", "hair_length": "very long"},
        "physique": {"body_type": "slender", "height": "average height"},
    },
    "Yoruichi": {
        "franchise": "Bleach",
        "gender": "Female",
        "costume": "a fitted orange tank top with a black stand-up collar, black fingerless "
                   "gloves, and black form-fitting pants",
        "signature": {"hair_color": "deep purple", "hair_length": "waist length",
                      "hair_texture": "sleek straight", "hair_style": "high ponytail",
                      "eye_color": "amber"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "dark brown"},
    },
    "Videl": {
        "franchise": "Dragon Ball",
        "gender": "Female",
        "costume": "a white sleeveless top with a blue collar, dark blue biker shorts under "
                   "a short skirt, and white boots",
        "signature": {"hair_color": "jet black", "hair_length": "chin length bob",
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Garnet": {
        "franchise": "Steven Universe",
        "gender": "Female",
        "costume": "a form-fitting bodysuit in maroon, dark red, black, and purple with shoulder "
                   "pads, smooth, flawless reddish-maroon and purplish-blue fused skin, and a "
                   "dark visor covering the eyes",
        "signature": {"hair_color": "near black", "hair_style": "afro", "hair_texture": "coily"},
        "physique": {"body_type": "curvy", "height": "tall"},
    },
    "Ozymandias": {
        "franchise": "Watchmen",
        "gender": "Male",
        "costume": "a purple-and-gold armored costume with a high collar and a stylized "
                   "gold motif, and gold gauntlets and boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "ear length", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "The Comedian": {
        "franchise": "Watchmen",
        "gender": "Male",
        "costume": "black leather armor with studded shoulders, a yellow smiley-face button, "
                   "and a bandolier of ammunition",
        "signature": {"hair_color": "dark brown", "hair_length": "very short", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "tall", "skin_tone": "fair"},
        "prop": "a lit cigar",
    },
    "Nite Owl": {
        "franchise": "Watchmen",
        "gender": "Male",
        "covers_face": True,
        "costume": "a brown-and-grey armored owl suit with a cape",
        "mask": "a brown cowl with large round goggle lenses",
        "physique": {"body_type": "average", "height": "average height"},
    },
    "Silk Spectre": {
        "franchise": "Watchmen",
        "gender": "Female",
        "costume": "a yellow-and-black latex bodysuit with a stylized collar, a black "
                   "domino mask, and yellow boots",
        "signature": {"hair_color": "near black", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "hourglass", "height": "average height", "skin_tone": "fair"},
    },

    # --- 0.45 classic comics: Justice Society of America -------------------
    "Doctor Fate": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a deep blue bodysuit with a wide golden belt, golden boots, golden "
                   "gauntlets, a golden amulet on a short chain at the collar, and a "
                   "flowing golden cape",
        "mask": "a gleaming full-face golden helm with narrow eye slits",
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Hourman": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black bodysuit with a golden hourglass emblem on the chest, a black "
                   "hood-style cowl leaving the face exposed, a yellow cape, yellow gloves, "
                   "a yellow belt, and a miniature hourglass hanging from a chain around the neck",
        "signature": {"eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "The Spectre": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a deep green hooded cloak clasped at the shoulders, green trunks, green "
                   "gloves, and green boots, over smooth, flawless chalk white skin",
        "eyes": "solid glowing white pupil-less",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Sandman (Wesley Dodds)": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a green double-breasted 1930s suit with a purple cape, purple gloves, "
                   "and a matching green fedora",
        "mask": "a WWI-style gas mask with round glass lenses and a hanging filter canister",
        "physique": {"body_type": "average", "height": "average height"},
        "prop": "a brass gas gun shaped like an oversized pistol",
    },
    "Jay Garrick": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a red long-sleeved shirt with a golden lightning-bolt emblem, blue "
                   "trousers, red boots with small golden wings at the ankles, and a "
                   "polished silver WWI-style helmet with golden wings at the temples",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Wildcat": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a matte black full-body cat suit with a slim yellow belt and black boots",
        "mask": "a black cat cowl with pointed ears and short whiskers",
        "physique": {"body_type": "stocky", "height": "tall"},
    },
    "Starman (Ted Knight)": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a crimson bodysuit with a large golden star emblem on the chest, a "
                   "golden belt, green gloves, green boots, and a green finned helmet "
                   "leaving the face exposed",
        "signature": {"eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
        "prop": "a slender golden gravity rod glowing with starlight at the tip",
    },
    "Doctor Mid-Nite": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a crimson bodysuit with a black crescent-moon emblem on the chest, "
                   "green gloves, green boots, a long black cape with a high collar, and "
                   "round black blackout goggles",
        "signature": {"hair_color": "dark brown", "hair_length": "very short"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Stargirl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a royal blue sleeveless costume scattered with small white stars and a "
                   "large white star emblem on the chest, a red belt, red fingerless gloves, "
                   "and a slim golden headband",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "a golden cosmic staff crackling with starlight energy",
    },
    "Liberty Belle": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a fitted royal blue jacket and matching trousers with a golden "
                   "liberty-bell belt buckle, red gloves, and red boots",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_texture": "loosely curled", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Phantom Lady (Dee Tyler)": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a strapless yellow one-piece costume with a deep neckline, a flowing "
                   "green cape clasped at the shoulders, green opera gloves, and green "
                   "thigh-high boots",
        "signature": {"hair_color": "near black", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "fair"},
    },

    # --- 0.45 classic comics: Legion of Super-Heroes ------------------------
    "Saturn Girl": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting red-and-white bodysuit with a golden ringed-planet "
                   "emblem on the chest, white gloves, white boots, and a golden Legion "
                   "flight ring",
        "signature": {"hair_color": "platinum blonde", "hair_length": "shoulder length",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "slim", "height": "average height", "skin_tone": "fair"},
    },
    "Lightning Lad": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a blue-and-white bodysuit with a golden lightning-bolt emblem across "
                   "the chest, white gloves, white boots, and a golden Legion flight ring",
        "signature": {"hair_color": "copper", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Cosmic Boy": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a magenta-and-black bodysuit with a silver magno-disc emblem on the "
                   "chest, black gloves, black boots, and a golden Legion flight ring",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Brainiac 5": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a form-fitting purple-and-black jumpsuit with a white belt, white boots, and "
                   "a golden Legion flight ring, over smooth, flawless green skin",
        "signature": {"hair_color": "golden blonde", "hair_length": "ear length"},
        "physique": {"body_type": "slim", "height": "average height"},
    },

    # --- 0.45 classic comics: Mad Hatters, Marvel, MHA, golden age ----------
    "Mad Hatter (Alice in Wonderland)": {
        "franchise": "Alice in Wonderland",
        "gender": "Male",
        "costume": "an oversized emerald-green top hat with a '10/6' card tucked in the "
                   "band, a mismatched Victorian tailcoat over a patterned waistcoat, a "
                   "large polka-dot bow tie, and striped trousers",
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Mad Hatter (Jervis Tetch)": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a green Victorian frock coat over a patterned waistcoat, a large blue "
                   "bow tie, striped trousers, white gloves, and an oversized green top hat "
                   "with a '10/6' card in the band",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short"},
        "physique": {"body_type": "slim", "height": "short", "skin_tone": "pale"},
    },
    "Ms. Marvel (Carol Danvers)": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black leotard with a golden lightning-bolt emblem, a red sash "
                   "knotted at the waist, black opera gloves, black thigh-high boots, and "
                   "a black domino mask",
        "signature": {"hair_color": "golden blonde", "hair_length": "slightly past shoulders",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Ms. Marvel (Sharon Ventura)": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a navy blue leotard with a golden lightning-bolt emblem, a red sash "
                   "knotted at the waist, blue opera gloves, blue thigh-high boots, and a "
                   "blue domino mask",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_texture": "wavy", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Momo Yaoyorozu": {
        "franchise": "My Hero Academia",
        "gender": "Female",
        "costume": "a sleeveless crimson leotard with a deep plunging neckline, a golden "
                   "utility belt with a small red tome at the hip, and matching crimson boots",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "curvy", "height": "tall", "skin_tone": "light"},
    },
    "The Spirit": {
        "franchise": "Comics",
        "gender": "Male",
        "costume": "a blue suit and matching blue fedora with a red necktie, a white "
                   "shirt, black leather gloves, and a small blue domino mask",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Zatara": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a black tuxedo tailcoat with a white waistcoat, a white bow tie, "
                   "white gloves, and a black top hat",
        "signature": {"facial_hair": "mustache", "hair_color": "near black",
                      "hair_length": "very short"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "The Phantom": {
        "franchise": "Comics",
        "gender": "Male",
        "costume": "a skin-tight purple bodysuit with a matching purple hood, a black "
                   "domino mask, black-and-white diagonally striped trunks, a black belt "
                   "with a silver skull buckle and twin holsters, and black boots",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "The Atom (Ray Palmer)": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "a blue bodysuit with red gloves, red boots, a red-and-blue torso "
                   "panel, and a blue belt, shrunk to a tiny atom-sized scale beside a "
                   "towering everyday object",
        "mask": "a red-and-blue cowl with a white atomic-symbol emblem on the forehead",
        "physique": {"body_type": "lean", "height": "short"},
    },

    # --- Expansion wave (v0.53.0): broadly recognizable icons ------------
    # Non-natural skin uses the "smooth, flawless <colour> skin" / "uniform,
    # all-over <colour> fur" marker so the engine suppresses the random human
    # tone and anchors the colour (see identity_forge_cosplayer._BODY_PAINT_RE);
    # skin_tone is then omitted from physique. Giants state scale in the costume
    # so it renders in cosplay-only mode too. Full mascot suits set covers_face
    # (+ mask) and covers_body.
    "Oompa Loompa": {
        "franchise": "Charlie and the Chocolate Factory",
        "gender": "Male",
        "costume": "brown lederhosen-style dungaree shorts with suspenders over a white "
                   "long-sleeve shirt, knee-high white socks, and smooth, flawless bright "
                   "orange skin",
        "signature": {"hair_color": "emerald green", "hair_length": "very short",
                      "hair_style": "slicked back"},
        "physique": {"body_type": "stocky", "height": "very petite"},
    },
    "Willy Wonka": {
        "franchise": "Charlie and the Chocolate Factory",
        "gender": "Male",
        "costume": "a deep plum velvet tailcoat over a tan paisley waistcoat, a brown-gold "
                   "top hat, a lilac bow tie, checked trousers, and tan gloves",
        "signature": {"hair_color": "light chestnut", "hair_length": "ear length",
                      "hair_texture": "wavy", "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
        "prop": "a gold-topped walking cane",
    },
    "The BFG": {
        "franchise": "The BFG",
        "gender": "Male",
        "costume": "a long dark waistcoat over a collarless shirt, a knotted red neckerchief, "
                   "rough patched trousers, and a long leather coat, with enormous ears, on a "
                   "colossal towering figure of impossible gigantic scale and proportion",
        "signature": {"hair_color": "silver", "hair_length": "short pixie",
                      "hair_texture": "fine and wispy", "eye_color": "pale blue"},
        "size_scale": "giant",
        "physique": {"body_type": "lean", "height": "very tall", "skin_tone": "fair"},
    },
    "Fantastic Mr Fox": {
        "franchise": "Fantastic Mr Fox",
        "gender": "Male",
        "covers_hair": True,
        "costume": "a tan corduroy suit with a matching necktie, over uniform, all-over "
                   "russet-orange fur, with a pointed fox snout, upright ears, and a bushy tail",
        "signature": {"eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Goldilocks": {
        "franchise": "Fairy Tales",
        "gender": "Female",
        "costume": "a pale blue dress with puffed sleeves, a white pinafore apron, white "
                   "stockings, and black buckled shoes",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_texture": "curly", "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "fair"},
    },
    "Pinocchio": {
        "franchise": "Pinocchio",
        "gender": "Male",
        "costume": "red dungaree shorts with suspenders, a short yellow jacket, a yellow "
                   "peaked hat with a small red feather, a large blue bow, white gloves, and "
                   "a long wooden nose",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "petite and slim", "height": "very petite", "skin_tone": "light"},
    },
    "Jack Frost": {
        "franchise": "Rise of the Guardians",
        "gender": "Male",
        "costume": "a frost-blue hooded sweatshirt laced at the collar with white crystalline "
                   "frost patterns, tan trousers cropped at the calf, and bare feet",
        "signature": {"hair_color": "white", "hair_length": "very short",
                      "hair_texture": "thick and voluminous", "hair_style": "windswept", "eye_color": "ice blue"},
        "physique": {"body_type": "lean", "height": "slightly above average height", "skin_tone": "very pale"},
        "prop": "a curved wooden shepherd's-crook staff glazed with frost",
    },
    "Gingerbread Man": {
        "franchise": "Fairy Tales",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,
        "costume": "a plump brown gingerbread-cookie body with white piped-icing swirls "
                   "trimming the arms and legs and two round red gumdrop buttons",
        "mask": "a round brown gingerbread head with white piped-icing eyes and a wide smiling icing mouth",
        "physique": {"body_type": "chubby", "height": "average height"},
    },
    "Baba Yaga": {
        "franchise": "Folklore",
        "gender": "Female",
        "costume": "layered ragged dark peasant robes, a knotted headscarf, a tattered woolen "
                   "shawl, and a string of bone-and-bead amulets",
        "signature": {"hair_color": "silver", "hair_length": "long",
                      "hair_texture": "fine and wispy", "hair_style": "natural and unstyled", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "pale"},
        "prop": "a gnarled wooden broom",
    },
    "Bride of Frankenstein": {
        "franchise": "Movie",
        "gender": "Female",
        "costume": "a long flowing white burial gown with trailing gauze wrappings, over "
                   "smooth, flawless pale grey skin, with faint stitched neck scars and dramatic "
                   "white lightning streaks framing a tall conical beehive",
        "eyes": "pale and sunken",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "thick and voluminous", "hair_style": "updo"},
        "physique": {"body_type": "slender", "height": "tall"},
    },
    "Samara": {
        "franchise": "The Ring",
        "gender": "Female",
        "costume": "a dirty, water-soaked pale dress, with long, stringy wet black hair hanging "
                   "down over the face",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "pin straight", "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "petite and slim", "height": "petite", "skin_tone": "very pale"},
    },
    "Ghostbuster": {
        "franchise": "Ghostbusters",
        "gender": "Male",
        "costume": "a tan jumpsuit with a name patch and a no-ghost shoulder emblem, a bulky "
                   "proton pack with a neutrona wand strapped across the back, utility straps, "
                   "and black boots",
        "signature": {"hair_color": "dark brown", "hair_length": "very short", "eye_color": "dark brown"},
        "physique": {"body_type": "average", "height": "average height", "skin_tone": "light"},
    },
    "Stay Puft Marshmallow Man": {
        "franchise": "Ghostbusters",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,
        "costume": "a giant, puffy, pillowy white marshmallow body wearing a little blue-and-red "
                   "sailor's neckerchief, on a colossal towering figure of overwhelming gigantic scale",
        "mask": "a big round white marshmallow head with a cheerful painted smile under a small white sailor cap",
        "size_scale": "giant",
        "physique": {"body_type": "plus size", "height": "very tall"},
    },
    "Roger Rabbit": {
        "franchise": "Who Framed Roger Rabbit",
        "gender": "Male",
        "covers_hair": True,
        "costume": "red dungaree overalls with two large yellow buttons, a blue-and-yellow "
                   "polka-dot bow tie, yellow gloves, and tall floppy rabbit ears, over uniform, "
                   "all-over soft white fur",
        "signature": {"eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Popeye": {
        "franchise": "Popeye",
        "gender": "Male",
        "costume": "a black long-sleeve sailor shirt with a red collar, blue trousers, a white "
                   "sailor cap, brown boots, and a blue anchor tattoo on one enormously oversized "
                   "forearm",
        "signature": {"hair_color": "dirty blonde", "hair_length": "very short",
                      "facial_hair": "stubble", "eye_color": "blue-gray"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "tan"},
        "prop": "a corncob pipe",
    },
    "Olive Oyl": {
        "franchise": "Popeye",
        "gender": "Female",
        "costume": "a fitted red long-sleeve top, a long black skirt, and big black boots on very "
                   "long, thin limbs",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_texture": "sleek straight", "hair_style": "chignon", "eye_color": "dark brown"},
        "physique": {"body_type": "very slim", "height": "very tall", "skin_tone": "fair"},
    },
    "Johnny Bravo": {
        "franchise": "Johnny Bravo",
        "gender": "Male",
        "costume": "a snug black t-shirt, blue jeans, black boots, and black sunglasses on an "
                   "exaggeratedly muscular, barrel-chested build",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "hair_style": "slicked back", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "tan"},
    },
    "Crash Bandicoot": {
        "franchise": "Crash Bandicoot",
        "gender": "Male",
        "costume": "blue denim shorts, red sneakers, and brown fingerless gloves, over uniform, "
                   "all-over bright orange fur with a pale belly",
        "signature": {"hair_color": "orange", "hair_length": "very short",
                      "hair_style": "windswept", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "short"},
    },
    "Sackboy": {
        "franchise": "LittleBigPlanet",
        "gender": "Male",
        "covers_face": True,
        "covers_body": True,
        "costume": "a small, stout knitted brown burlap body with a zipper up the front and "
                   "visible stitched seams, on a compact doll-sized figure",
        "mask": "a round brown knitted head with stitched button eyes and a small zipper mouth set in a friendly expression",
        "physique": {"body_type": "stocky", "height": "very petite"},
    },
    "Edward Scissorhands": {
        "franchise": "Edward Scissorhands",
        "gender": "Male",
        "costume": "a black buckled leather bodysuit covered in straps, buckles, and zippers, "
                   "over pale skin criss-crossed with faint scars, with hands made of long, sharp "
                   "scissor blades",
        "signature": {"hair_color": "jet black", "hair_length": "ear length",
                      "hair_texture": "thick and voluminous", "hair_style": "tousled bedhead", "eye_color": "dark brown"},
        "physique": {"body_type": "slender", "height": "tall", "skin_tone": "very pale"},
    },
}


#: Broad category each franchise belongs to, for the node's "random_scope" control
#: (so a Random pick can be limited to e.g. only Anime or only Marvel). Written as
#: category -> franchises and inverted below. A franchise not listed falls back to
#: _DEFAULT_CATEGORY, so a new entry still scopes sensibly until it is mapped here.
_CATEGORY_FRANCHISES: dict[str, tuple[str, ...]] = {
    "Anime & Manga": (
        "Naruto", "Dragon Ball", "One Piece", "Bleach", "Demon Slayer", "Jujutsu Kaisen",
        "My Hero Academia", "JoJo's Bizarre Adventure", "Fullmetal Alchemist", "Death Note",
        "Cowboy Bebop", "Fate/stay night", "Kill la Kill", "Neon Genesis Evangelion",
        "Sailor Moon", "Attack on Titan", "One Punch Man", "Ghost in the Shell", "Vocaloid",
        "Pokemon", "Madoka Magica", "Studio Ghibli", "Anime",
    ),
    "Marvel": ("Marvel",),
    "DC": ("DC", "DC (Teen Titans)", "Watchmen", "The Sandman", "Fables"),
    "Star Wars": ("Star Wars",),
    "Disney": (
        "Disney", "The Little Mermaid", "Sleeping Beauty", "Frozen", "Snow White", "Tangled",
        "Pocahontas", "Mulan", "Moana", "The Princess and the Frog", "Peter Pan", "Cinderella",
        "Beauty and the Beast", "Aladdin", "Brave", "Alice in Wonderland", "101 Dalmatians",
        "Big Hero 6", "The Incredibles", "Zootopia", "Star vs. the Forces of Evil",
        "Toy Story", "Lilo and Stitch", "Pinocchio",
    ),
    "Video Games": (
        "Final Fantasy", "Final Fantasy VII", "Final Fantasy X", "Final Fantasy XV",
        "Final Fantasy XIII", "Final Fantasy VI", "NieR: Automata", "Street Fighter",
        "Mortal Kombat", "Tekken", "Overwatch", "League of Legends", "Arcane", "Genshin Impact",
        "The Legend of Zelda", "The Legend of Zelda: Breath of the Wild", "Nintendo",
        "Super Mario", "Metroid", "Resident Evil", "Tomb Raider", "Mass Effect", "Halo",
        "Metal Gear", "God of War", "Kingdom Hearts", "Baldur's Gate 3", "The Witcher",
        "Horizon", "Hitman", "Hellblade", "Doom", "Portal", "Silent Hill", "Darkstalkers",
        "The King of Fighters", "Bayonetta", "Divinity: Original Sin", "World of Warcraft",
        "StarCraft", "Borderlands", "Dragon Age", "Kid Icarus", "ARMS", "System Shock",
        "Sega", "Namco", "BioShock", "The Last of Us", "Crash Bandicoot", "LittleBigPlanet",
    ),
    "Fantasy & Literature": (
        "The Lord of the Rings", "Harry Potter", "Game of Thrones", "The Hunger Games",
        "Anne of Green Gables", "Pippi Longstocking", "The Wizard of Oz", "Fairy Tales",
        "Literature", "Folklore", "Legend", "Dr. Seuss", "Winnie the Pooh",
        "Charlie and the Chocolate Factory", "The BFG", "Fantastic Mr Fox",
    ),
    "Movies & TV": (
        "Star Trek", "Battlestar Galactica", "The Terminator", "Alien", "Predator", "RoboCop",
        "Judge Dredd", "Mad Max",
        "Escape from New York", "Pirates of the Caribbean", "Movie", "The Addams Family",
        "Scooby-Doo", "Who Framed Roger Rabbit", "Mistress of the Dark", "Xena: Warrior Princess",
        "A Nightmare on Elm Street", "Friday the 13th", "Halloween", "IT", "Hellraiser",
        "The Texas Chain Saw Massacre", "Scream", "Child's Play", "Shrek",
        "Attack of the 50 Foot Woman", "Buffy the Vampire Slayer",
        "Rise of the Guardians", "The Ring", "Ghostbusters", "Edward Scissorhands",
        "McDonald's", "Wendy's", "Kool-Aid", "Michelin", "Big Boy", "Planters",
        "KFC", "Green Giant", "Pillsbury", "Mr. Clean", "Cap'n Crunch", "Kellogg's",
        "Cheetos", "General Mills", "Energizer", "Geico", "Duolingo",
    ),
    "Comics & Cartoons": (
        "Avatar: The Last Airbender", "The Legend of Korra", "Masters of the Universe",
        "Invincible", "Image", "Hellboy", "Transformers", "Vampirella", "Rainbow Brite",
        "The Smurfs", "Adventure Time", "Thundercats", "G.I. Joe", "TMNT", "Monster High",
        "Fathom", "Chaos! Comics", "Comics", "Betty Boop", "The Flintstones", "The Jetsons",
        "The Simpsons", "Family Guy", "Futurama", "Jem and the Holograms",
        "Looney Tunes", "Nickelodeon", "Rick and Morty", "Despicable Me", "The Mask",
        "Steven Universe", "Popeye", "Johnny Bravo",
    ),
}
_FRANCHISE_CATEGORY: dict[str, str] = {
    fr: cat for cat, frs in _CATEGORY_FRANCHISES.items() for fr in frs
}
_DEFAULT_CATEGORY = "Movies & TV"


def get_cosplayer_category(franchise: str) -> str:
    """Return the broad category for ``franchise`` (falls back to a sensible default)."""
    return _FRANCHISE_CATEGORY.get(franchise, _DEFAULT_CATEGORY)


def get_cosplayer_categories() -> list[str]:
    """Return the sorted broad categories that actually have characters."""
    return sorted({get_cosplayer_category(e.get("franchise", "")) for e in COSPLAYERS.values()})


def get_cosplayer_names(gender: str | None = None, category: str | None = None) -> list[str]:
    """Return sorted character names, optionally filtered by SOURCE gender and/or category.

    ``gender`` (``"Female"``/``"Male"``) and ``category`` scope the node's "Random — …"
    picks; ``category`` of ``None``/``"Any"`` means no franchise limit. The *person's*
    gender is chosen separately on the IdentityForge node.
    """
    return sorted(
        name for name, entry in COSPLAYERS.items()
        if (gender is None or entry.get("gender") == gender)
        and (category in (None, "Any")
             or get_cosplayer_category(entry.get("franchise", "")) == category)
    )


def get_cosplayer(name: str) -> dict:
    """Return the cosplay record for ``name`` (empty dict if unknown)."""
    return COSPLAYERS.get(name, {})


def get_cosplayer_names_by_gender(gender: str) -> list[str]:
    """Return sorted names whose SOURCE character matches ``gender`` (back-compat shim)."""
    return get_cosplayer_names(gender=gender)


# Merge optional user-supplied cosplayers (./user_options.json, "cosplayers"
# section) so they survive ``git pull``. Done last so user entries can override
# a built-in of the same name and so a user "Male" entry can populate the
# "Random — male" scope.
from .user_options import apply_user_cosplayers  # noqa: E402

apply_user_cosplayers(COSPLAYERS)
