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
* **Body paint reads as a single even coat.** A solid non-natural skin colour is
  worded ``"an even, smooth coat of <colour> body paint"`` (drop "all-over") so
  text-to-image models render it uniform instead of patchy/streaked. Keep "paint"
  (it layers over the randomized skin without contradicting the spoken skin tone).
  Where the surface has an intrinsic texture/pattern, anchor on the same even coat
  and append it: scales/fur use ``"an even, all-over coat of …"`` and keep
  "scaled-skin" / "fur"; markings, tattoos and plating follow as ``"… with <pattern>"``.
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
        "costume": "a form-fitting dark purple bodysuit with technological enhancements, "
                   "a high collar, integrated armor, a visor, stealth boots, and "
                   "an even, smooth coat of blue-violet body paint",
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
        "signature": {"hair_color": "electric blue", "hair_length": "hip length",
                      "hair_style": "loose braids"},
        "physique": {"body_type": "very slim", "height": "short", "skin_tone": "pale"},
    },

    # --- Star Wars --------------------------------------------------------
    "Ahsoka Tano": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "an even coat of orange body paint with white Togruta facial markings, a blue-and-"
                   "white striped montral-and-lekku headpiece, a practical grey-and-blue "
                   "tunic with leggings, and armored pieces",
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
    "Padmé Amidala": {
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "the white Geonosis battle outfit with a form-fitting white top, "
                   "white pants, a utility belt, and beige boots",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
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
                      "skin_details": "scattered sun freckles"},
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
        "costume": "a tight white crop top, very short tattered shorts over fishnet "
                   "stockings, studded accessories, and heavy punk-inspired makeup",
        "signature": {"hair_color": "platinum blonde", "hair_length": "shoulder length",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
        "prop": "an oversized wooden mallet with a red-and-black striped head, slung "
                "over one shoulder",
    },
    "Poison Ivy": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a form-fitting bodysuit of overlapping leaves and vines with an even coat of green "
                   "body paint, and tiny leaves entwined in the hair",
        "signature": {"hair_color": "bright red", "hair_length": "waist length",
                      "hair_style": "worn down", "eye_color": "green"},
        "physique": {"body_type": "slender", "height": "tall"},
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
        "costume": "a purple crop top, a purple miniskirt, purple thigh-high boots, "
                   "silver arm guards, and an even, smooth coat of warm golden-orange body paint",
        "signature": {"hair_color": "bright red", "hair_length": "hip length",
                      "hair_style": "worn down", "eye_color": "bright green"},
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
        "costume": "an even, all-over coat of dark blue scaled-skin body paint with natural "
                   "scale coverage",
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
                      "skin_details": "light freckles across nose"},
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
                      "hair_style": "low ponytail", "eye_color": "dark brown"},
        "physique": {"body_type": "curvy", "height": "average height", "skin_tone": "warm tan"},
    },
    "Mulan": {
        "franchise": "Mulan",
        "gender": "Female",
        "costume": "a traditional Chinese red wrap-style top with gold trim, matching "
                   "red pants, black boots, a red waist sash, and subtle armor pieces",
        "signature": {"hair_color": "jet black", "hair_length": "long",
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
                      "skin_details": "light freckles across nose"},
        "physique": {"body_type": "athletic", "height": "short", "skin_tone": "fair"},
        "prop": "a drawn wooden longbow worn smooth with use, an arrow nocked",
    },
    "Pocahontas": {
        "franchise": "Pocahontas",
        "gender": "Female",
        "costume": "a tan fringed buckskin dress reaching mid-thigh with geometric "
                   "patterns, a turquoise necklace, and brown moccasins",
        "signature": {"hair_color": "jet black", "hair_length": "waist length",
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
                      "hair_texture": "sleek straight", "eye_color": "dark brown"},
        "physique": {"body_type": "hourglass", "height": "statuesque", "skin_tone": "porcelain"},
    },
    "Wednesday Addams": {
        "franchise": "The Addams Family",
        "gender": "Female",
        "costume": "a simple black dress with a white collar and cuffs, black stockings, "
                   "and black shoes",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "pigtails", "eye_color": "dark brown"},
        "physique": {"body_type": "slim", "height": "petite", "skin_tone": "very pale"},
    },

    # --- More Marvel ------------------------------------------------------
    "She-Hulk": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a purple-and-white athletic leotard, with an even, smooth coat of rich green body "
                   "paint",
        "signature": {"hair_color": "emerald green", "hair_length": "slightly past shoulders",
                      "hair_texture": "loosely wavy", "eye_color": "emerald"},
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
        "costume": "tactical dark leather armor in black and deep teal with a long coat, "
                   "fitted pants, boots, an even, smooth coat of green body paint, and magenta hair tips",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Nebula": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a fitted dark combat suit with armored segments, boots, gauntlets, "
                   "an even, smooth coat of blue metallic body paint with intricate plating, and purple "
                   "biomechanical lines over a shaved head",
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
                   "wings, matching boots, and an antennae headpiece",
        "signature": {"hair_color": "warm brown", "hair_length": "chin length bob",
                      "hair_style": "worn down", "eye_color": "medium brown"},
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
        "franchise": "Star Wars",
        "gender": "Female",
        "costume": "a practical brown and orange flight suit with a utility belt, brown "
                   "boots, an even, smooth coat of green Twi'lek body paint, and two long head-tails (lekku)",
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
    },

    # --- More Disney / animation -----------------------------------------
    "Tinker Bell": {
        "franchise": "Peter Pan",
        "gender": "Female",
        "costume": "a strapless green leaf dress, tiny green slippers, translucent "
                   "iridescent fairy wings, and a dusting of pixie dust",
        "signature": {"hair_color": "golden blonde", "hair_length": "shoulder length",
                      "hair_style": "messy bun", "eye_color": "bright blue"},
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
        "costume": "a black strapless dress, golden shell earrings, a nautilus necklace, "
                   "a white bouffant wig, an even, smooth coat of purple-gray body paint, and eight large purple "
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
        "costume": "a grey tank top, ripped jeans, sturdy boots, and an even, smooth coat of pale greyish-blue "
                   "body paint with two small neck bite marks",
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
    "Ms. Marvel": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a blue and red costume with a gold lightning-bolt emblem, a red scarf, "
                   "a domino mask, red gloves, and blue boots",
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
        "costume": "an even, all-over coat of golden spotted cheetah-fur body paint, pointed "
                   "ears, sharp fangs, and a spotted bikini-style outfit",
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
        "costume": "a white dress and white high-heeled shoes, with an even, smooth coat of light blue "
                   "Smurf skin body paint",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright blue"},
        "physique": {"body_type": "petite and slim", "height": "very petite"},
    },
    "Liara T'Soni": {
        "franchise": "Mass Effect",
        "gender": "Female",
        "costume": "a white and blue sleeveless top with a high collar, dark fitted "
                   "pants, and practical boots, with an even coat of light blue Asari skin body "
                   "paint and a smooth cartilage head crest",
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
        "costume": "only torn purple trousers, with an even, smooth coat of rich green body paint over "
                   "enormous muscles",
        "signature": {"hair_color": "near black", "hair_length": "very short",
                      "eye_color": "green"},
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
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "gold and blue armored battle plate, blue greaves, and the golden "
                   "Infinity Gauntlet, with an even coat of deeply ridged purple body paint",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },
    "Venom": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a hulking glossy pitch-black symbiote bodysuit with a white spider "
                   "emblem across the chest and clawed hands",
        "mask": "a featureless symbiote head with huge jagged white eye patches",
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
        "costume": "a red and black bodysuit, with an even, velvety coat of indigo-blue body "
                   "paint, pointed ears, and a long spaded tail",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "lean", "height": "average height"},
    },
    "Silver Surfer": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a seamless mirror-chrome silver bodysuit with an even, smooth coat of reflective "
                   "silver body paint",
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
                   "gloves and boots, and a glowing green power ring",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "green"},
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
        "costume": "a purple tailcoat suit with a green vest and a yellow shirt, an even, smooth coat of "
                   "chalk-white skin body paint, a wide carved red grin, and slicked-back "
                   "bright green hair",
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
        "costume": "a blue cape held by crossed straps over a bare chest, blue trunks, and "
                   "blue boots, with an even, smooth coat of green body paint and a bald green head",
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
                   "ears, and sparse white hair",
        "signature": {"eye_color": "green"},
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
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "black hooded robes, with an even coat of blood-red body paint patterned with "
                   "intricate black tattoos and a crown of short black horns ringing the "
                   "head",
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
        "costume": "torn brown shorts and ankle manacles, with an even, smooth coat of bright green skin "
                   "body paint, wild orange hair and mane, and sharp teeth",
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
        "costume": "a green and black ninja uniform with an even coat of green scaled skin body paint and "
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
        "costume": "a leather harness and bracers over a bare chest, with an even, smooth coat of ash-grey pale "
                   "skin body paint and a bold red tattoo across the torso and one eye",
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
        "costume": "a hydrogen-atom symbol glowing on the forehead, with an even, smooth coat of glowing "
                   "blue body paint, a bald head, and blank white eyes",
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
        "franchise": "Dragon Ball",
        "gender": "Male",
        "costume": "a smooth white-and-purple bio-armor carapace over an even, smooth "
                   "coat of white body paint with purple plated sections, and a long tail",
        "eyes": "crimson",
        "signature": {},
        "physique": {"body_type": "slim", "height": "short"},
    },
    "Cell": {
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
        "costume": "a gothic-lolita black dress with lace, buckles, and a small top hat",
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
        "costume": "a teal-and-pink armored bodysuit on a towering, hugely muscular "
                   "frame, with a glowing particle-cannon harness",
        "signature": {"hair_color": "hot pink", "hair_length": "very short",
                      "eye_color": "bright blue"},
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
        "costume": "an enormous suit of blue crusader power armor on a towering frame, "
                   "with a rocket-hammer",
        "mask": "a heavy blue crusader helmet with a barred visor",
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
        "costume": "an even, all-over coat of black-and-teal Twili skin with glowing "
                   "turquoise patterns, and an ornate stone helmet-crown",
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
        "physique": {"body_type": "stocky", "height": "very tall", "skin_tone": "warm brown"},
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
        "costume": "a charcoal-grey toga over an even, smooth coat of blue-grey skin, "
                   "with a crown of blue flame for hair",
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
        "costume": "a blue Fantastic Four bodysuit with a white '4' emblem, wreathed "
                   "head to toe in flame",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "light"},
    },
    "The Thing": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "blue trunks, and an even, all-over coat of craggy orange rock-like "
                   "skin with a heavy brow and a bald rocky head",
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
                   "a towering, immensely heavy frame, and a clean-shaven bald head",
        "signature": {"facial_hair": "clean shaven", "eye_color": "blue-gray"},
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
        "costume": "bulky crimson-and-brown armor over an enormous, towering muscular frame",
        "mask": "a huge rounded crimson helmet with narrow eye-slits",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Apocalypse": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "heavy blue-and-grey techno-organic armor with cabling, over an even, "
                   "all-over coat of blue-grey skin, on a towering frame",
        "signature": {"eye_color": "bright blue"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Galactus": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "massive purple-and-blue cosmic armor on a planet-sized, colossal frame",
        "mask": "a towering horned purple cosmic helmet",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Titania": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a purple-and-white sleeveless high-cut costume with white gloves and "
                   "boots, over an even, smooth coat of orange-toned skin, with a strong jaw "
                   "and bold features on a powerfully muscular frame - towering and gigantic, "
                   "vastly larger than everything around her, dwarfing the entire scene with "
                   "an overwhelming sense of scale",
        "eyes": "green",
        "signature": {"hair_color": "deep red", "hair_length": "very long",
                      "hair_texture": "wavy"},
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
        "costume": "a black-and-yellow Sinestro Corps uniform with a yellow lantern "
                   "emblem, over an even, smooth coat of red skin, with a thin black mustache",
        "signature": {"facial_hair": "mustache", "eye_color": "amber"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Brainiac": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a pink Coluan harness over an even, smooth coat of green metallic "
                   "skin, with a clean-shaven bald head studded with control nodes",
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
        "costume": "black biker leathers with chains and spikes over an even, smooth "
                   "coat of chalk-white skin, on a massive muscular frame",
        "eyes": "red on black sclera",
        "signature": {"hair_color": "jet black", "hair_length": "long"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Giganta": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a torn leopard-print one-shoulder dress, scaled up to a towering, "
                   "skyscraper-high fifty-foot giantess looming over the scene",
        "signature": {"hair_color": "deep red", "hair_length": "very long",
                      "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "very tall", "skin_tone": "warm tan"},
    },
    "Giant-Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red-and-blue size-changing suit grown to a towering, building-high "
                   "giant scale",
        "mask": "a red domed helmet with antennae and a silver faceplate",
        "physique": {"body_type": "athletic", "height": "very tall"},
    },

    # --- Movie sci-fi, action & monster icons ----------------------------
    "Predator": {
        "franchise": "Predator",
        "gender": "Male",
        "covers_face": True,
        "costume": "a towering hulking frame with mottled reptilian skin, a fishnet "
                   "mesh underlayer, segmented armor, wrist blades, and long dreadlock-like "
                   "tendrils, with a shoulder plasma cannon",
        "mask": "a scarred bio-metal hunter's mask with twin laser sights",
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "RoboCop": {
        "franchise": "RoboCop",
        "gender": "Male",
        "covers_face": True,
        "costume": "a full suit of matte gunmetal cybernetic police armor with exposed "
                   "servos and a holstered sidearm",
        "mask": "a sleek steel helmet leaving only a stern jaw exposed",
        "physique": {"body_type": "stocky", "height": "tall"},
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
        "costume": "a brown trench coat over a belt of pouches, an even, smooth coat of "
                   "brick-red skin, two filed-down horn stumps on the forehead, and a "
                   "massive stone right hand",
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
        "costume": "spiked Githyanki plate armor over an even, all-over coat of pale "
                   "green mottled skin, with tightly drawn-back hair",
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
        "costume": "child-sized denim dungarees over a colorful striped shirt and "
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
        "costume": "long flowing black robes over an even, smooth coat of chalk-white "
                   "skin, with a clean-shaven bald head and flat snake-like slits for a nose",
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
        "costume": "a long duster coat and a wide-brimmed hat over an even, smooth coat "
                   "of blue skin, with a clean-shaven bald blue head, breathing tubes "
                   "running to the cheeks, and twin blaster holsters",
        "eyes": "glowing red",
        "signature": {"facial_hair": "clean shaven"},
        "physique": {"body_type": "lean", "height": "tall"},
    },
    "Grand Admiral Thrawn": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a crisp white Imperial Grand Admiral's uniform over an even, smooth "
                   "coat of blue skin",
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
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an even, smooth coat of translucent pale-blue ice over a lean frame, "
                   "with jagged icicle spikes along the shoulders and forearms",
        "eyes": "solid icy white",
        "signature": {},
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
        "costume": "red-and-yellow trunks over an even, smooth coat of polished chrome "
                   "steel skin on a huge muscular frame",
        "eyes": "steel-grey",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Kitty Pryde": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a blue-and-gold X-Men uniform",
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
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "a yellow cape and green-and-gold accents over an even, smooth coat of "
                   "deep red android skin, with a glowing yellow gem set in the forehead",
        "eyes": "glowing white",
        "signature": {},
        "physique": {"body_type": "athletic", "height": "tall"},
    },
    "Ant-Man": {
        "franchise": "Marvel",
        "gender": "Male",
        "covers_face": True,
        "costume": "a red-and-silver size-changing suit with utility straps, shrunk to a "
                   "tiny scale beside a towering everyday object",
        "mask": "a red-and-silver helmet with round antennae and a dark visor",
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
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "grey trousers over a bare muscular torso, with an even, all-over coat "
                   "of grey skin covered in raised dark-red ritual tattoo scars",
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
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "an even, all-over coat of brown wooden bark skin with mossy patches "
                   "and faint glowing seams, on a towering tree-like frame with branching limbs",
        "eyes": "glowing amber",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Mantis": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a black-and-green high-collared outfit over an even, smooth coat of "
                   "pale green skin, with two thin antennae rising from the forehead",
        "eyes": "solid black",
        "signature": {"hair_color": "jet black", "hair_length": "very long",
                      "hair_texture": "sleek straight"},
        "physique": {"body_type": "slender", "height": "average height"},
    },

    # --- DC (more heroes) ------------------------------------------------
    "Darkseid": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "heavy blue-and-grey Apokoliptian armor over an even, smooth coat of "
                   "grey craggy stone-like skin, on a towering, monstrously powerful frame",
        "eyes": "glowing red Omega energy",
        "signature": {},
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
        "costume": "a green costume wreathed head to toe in green flame, over an even, "
                   "smooth coat of glowing green skin",
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
        "costume": "a black-and-purple uniform over an even, smooth coat of green skin, "
                   "with pointed ears and small fangs",
        "eyes": "green",
        "signature": {"hair_color": "emerald green", "hair_length": "very short"},
        "physique": {"body_type": "slim", "height": "average height"},
    },
    "Booster Gold": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a gold-and-blue futuristic suit with a star chest emblem, power-disc "
                   "wristbands, and a flight collar",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Blue Beetle": {
        "franchise": "DC",
        "gender": "Male",
        "covers_face": True,
        "costume": "blue chitinous scarab armor with black accents and a clawed gauntlet",
        "mask": "a smooth blue beetle-carapace helmet with large round yellow eye-lenses",
        "physique": {"body_type": "athletic", "height": "average height"},
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
        "costume": "a red-and-blue size-changing bodysuit, shrunk to a tiny atom-sized "
                   "scale beside a towering everyday object",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "dark brown"},
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
        "costume": "a black bodysuit with a high jagged collar and a long cape, over an "
                   "even, smooth coat of chalk-white skin, with a red diamond gem on the forehead",
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
        "costume": "a tattered inside-out Superman costume with a reversed black-and-grey "
                   "'S', over an even, smooth coat of chalk-white cracked stone-like skin",
        "eyes": "icy blue",
        "signature": {"hair_color": "jet black", "hair_length": "very short"},
        "physique": {"body_type": "stocky", "height": "very tall"},
    },
    "Silver Banshee": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a black bodysuit with silver chains and a torn cape, over a chalk-white "
                   "skull-like face with hollow black eye sockets",
        "eyes": "glowing white",
        "signature": {"hair_color": "white", "hair_length": "very long",
                      "hair_texture": "thick and voluminous"},
        "physique": {"body_type": "slender", "height": "tall"},
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
        "franchise": "Thundercats",
        "gender": "Male",
        "costume": "a black headdress and a crimson cape with golden arm bands, over an "
                   "even, smooth coat of grey-blue skin on a powerful demonic frame",
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
        "franchise": "TMNT",
        "gender": "Male",
        "costume": "an even, all-over coat of green pebbled turtle skin with a tan "
                   "plastron and a domed shell on the back, brown elbow and knee pads, and "
                   "a blue bandana mask",
        "eyes": "dark brown",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "average height"},
        "prop": "twin katanas",
    },
    "Raphael": {
        "franchise": "TMNT",
        "gender": "Male",
        "costume": "an even, all-over coat of green pebbled turtle skin with a tan "
                   "plastron and a domed shell on the back, brown elbow and knee pads, and "
                   "a red bandana mask",
        "eyes": "dark brown",
        "signature": {},
        "physique": {"body_type": "stocky", "height": "average height"},
        "prop": "a pair of three-pronged sai",
    },
    "Donatello": {
        "franchise": "TMNT",
        "gender": "Male",
        "costume": "an even, all-over coat of green pebbled turtle skin with a tan "
                   "plastron and a domed shell on the back, brown elbow and knee pads, and "
                   "a purple bandana mask",
        "eyes": "dark brown",
        "signature": {},
        "physique": {"body_type": "lean", "height": "average height"},
        "prop": "a long wooden bo staff",
    },
    "Michelangelo": {
        "franchise": "TMNT",
        "gender": "Male",
        "costume": "an even, all-over coat of green pebbled turtle skin with a tan "
                   "plastron and a domed shell on the back, brown elbow and knee pads, and "
                   "an orange bandana mask",
        "eyes": "dark brown",
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
        "Pokemon",
    ),
    "Marvel": ("Marvel",),
    "DC": ("DC", "DC (Teen Titans)", "Watchmen", "The Sandman"),
    "Star Wars": ("Star Wars",),
    "Disney": (
        "Disney", "The Little Mermaid", "Sleeping Beauty", "Frozen", "Snow White", "Tangled",
        "Pocahontas", "Mulan", "Moana", "The Princess and the Frog", "Peter Pan", "Cinderella",
        "Beauty and the Beast", "Aladdin", "Brave", "Alice in Wonderland", "101 Dalmatians",
        "Big Hero 6", "The Incredibles",
    ),
    "Video Games": (
        "Final Fantasy", "Final Fantasy VII", "Final Fantasy X", "Final Fantasy XV",
        "Final Fantasy XIII", "Final Fantasy VI", "NieR: Automata", "Street Fighter",
        "Mortal Kombat", "Tekken", "Overwatch", "League of Legends", "Arcane", "Genshin Impact",
        "The Legend of Zelda", "The Legend of Zelda: Breath of the Wild", "Nintendo",
        "Super Mario", "Metroid", "Resident Evil", "Tomb Raider", "Mass Effect", "Halo",
        "Metal Gear", "God of War", "Kingdom Hearts", "Baldur's Gate 3", "The Witcher",
        "Horizon", "Hitman", "Hellblade", "Doom", "Portal", "Silent Hill", "Darkstalkers",
        "The King of Fighters", "Bayonetta",
    ),
    "Fantasy & Literature": (
        "The Lord of the Rings", "Harry Potter", "Game of Thrones", "The Hunger Games",
    ),
    "Movies & TV": (
        "Star Trek", "The Terminator", "Alien", "Predator", "RoboCop", "Judge Dredd", "Mad Max",
        "Escape from New York", "Pirates of the Caribbean", "Movie", "The Addams Family",
        "Scooby-Doo", "Who Framed Roger Rabbit", "Mistress of the Dark", "Xena: Warrior Princess",
        "A Nightmare on Elm Street", "Friday the 13th", "Halloween", "IT", "Hellraiser",
        "The Texas Chain Saw Massacre", "Scream", "Child's Play",
    ),
    "Comics & Cartoons": (
        "Avatar: The Last Airbender", "The Legend of Korra", "Masters of the Universe",
        "Invincible", "Image", "Hellboy", "Transformers", "Vampirella", "Rainbow Brite",
        "The Smurfs", "Adventure Time", "Thundercats", "G.I. Joe", "TMNT",
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
