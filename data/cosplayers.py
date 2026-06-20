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

* **Worn, not held.** Costumes list only *worn* items — clothing, footwear,
  gloves, masks/cowls, headwear, hair bows, jewellery, belts, empty holsters,
  body paint, markings, capes. Held / wielded props (swords, staves, bows, guns,
  shields, wands) are deliberately omitted; add them by editing the prompt.
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
    },
    "Kitana": {
        "franchise": "Mortal Kombat",
        "gender": "Female",
        "costume": "a blue form-fitting leotard with thigh-high boots, matching long "
                   "gloves, and a blue face mask covering the mouth and nose",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "high ponytail", "eye_color": "medium brown"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "light medium"},
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
    },
    "Harley Quinn": {
        "franchise": "DC",
        "gender": "Female",
        "costume": "a tight white crop top, very short tattered shorts over fishnet "
                   "stockings, studded accessories, and heavy punk-inspired makeup",
        "signature": {"hair_color": "platinum blonde", "hair_length": "shoulder length",
                      "hair_style": "pigtails", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
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
    },
    "Daenerys Targaryen": {
        "franchise": "Game of Thrones",
        "gender": "Female",
        "costume": "a flowing blue-grey gown with dragon-scale motifs and metallic "
                   "elements",
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
                   "ears, a fanged grin, and a spotted bikini-style outfit",
        "signature": {"hair_color": "warm brown", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "bright green"},
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
    },
    "Thor": {
        "franchise": "Marvel",
        "gender": "Male",
        "costume": "sleeveless silver and black armor with rows of circular silver chest "
                   "discs, a flowing red cape, and engraved bracers",
        "signature": {"hair_color": "golden blonde", "hair_length": "long",
                      "facial_hair": "short beard", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
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
    },
    "Green Arrow": {
        "franchise": "DC",
        "gender": "Male",
        "costume": "a dark forest-green hooded leather suit, a green domino mask, and a "
                   "quiver of arrows",
        "signature": {"hair_color": "golden blonde", "hair_length": "very short",
                      "facial_hair": "van dyke", "eye_color": "green"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
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
    },
    "Obi-Wan Kenobi": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "layered cream and brown Jedi robes with a hooded cloak",
        "signature": {"hair_color": "auburn", "hair_length": "jaw length",
                      "facial_hair": "full beard", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
    },
    "Yoda": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a simple brown Jedi robe, with green wrinkled skin, very large pointed "
                   "ears, and sparse white hair",
        "signature": {"eye_color": "green"},
        "physique": {"body_type": "slim", "height": "very petite"},
    },
    "Mace Windu": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "dark brown layered Jedi robes with a cloak",
        "signature": {"hair_length": "buzzed very short", "facial_hair": "clean shaven",
                      "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "dark brown"},
    },
    "Anakin Skywalker": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a dark Jedi tunic and tabards with a single leather glove on the right "
                   "hand, and a scar across the right brow",
        "signature": {"hair_color": "dark brown", "hair_length": "shoulder length",
                      "hair_texture": "wavy", "eye_color": "bright blue"},
        "physique": {"body_type": "athletic", "height": "average height", "skin_tone": "fair"},
    },
    "Kylo Ren": {
        "franchise": "Star Wars",
        "gender": "Male",
        "costume": "a black ribbed tunic with a layered hooded cape, and a scar down one "
                   "cheek",
        "signature": {"hair_color": "jet black", "hair_length": "jaw length",
                      "hair_texture": "wavy", "eye_color": "dark brown"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
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
    },
    "Sephiroth": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a long black leather coat with armored shoulder pauldrons worn over a "
                   "bare chest",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "hair_texture": "pin straight", "eye_color": "bright green"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "pale"},
    },
    "Squall": {
        "franchise": "Final Fantasy",
        "gender": "Male",
        "costume": "a black leather jacket with a white fur collar, and a scar slanting "
                   "across the brow and nose",
        "signature": {"hair_color": "dark brown", "hair_length": "very short",
                      "eye_color": "deep blue"},
        "physique": {"body_type": "lean", "height": "average height", "skin_tone": "fair"},
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
        "franchise": "Lord of the Rings",
        "gender": "Male",
        "costume": "worn brown ranger leathers and a hooded travel cloak",
        "signature": {"hair_color": "dark brown", "hair_length": "long",
                      "facial_hair": "short beard", "eye_color": "gray"},
        "physique": {"body_type": "athletic", "height": "tall", "skin_tone": "fair"},
    },
    "Legolas": {
        "franchise": "Lord of the Rings",
        "gender": "Male",
        "costume": "a green and brown elven tunic, pointed elf ears, and a quiver on the "
                   "back",
        "signature": {"hair_color": "light blonde", "hair_length": "long",
                      "hair_texture": "pin straight", "eye_color": "bright blue"},
        "physique": {"body_type": "lean", "height": "tall", "skin_tone": "fair"},
    },
    "Gandalf": {
        "franchise": "Lord of the Rings",
        "gender": "Male",
        "costume": "layered grey robes and a tall pointed grey hat",
        "signature": {"hair_color": "silver", "hair_length": "very long",
                      "facial_hair": "full beard", "eye_color": "blue-gray"},
        "physique": {"body_type": "average", "height": "tall", "skin_tone": "fair"},
    },
    "Gimli": {
        "franchise": "Lord of the Rings",
        "gender": "Male",
        "costume": "a horned and riveted iron helmet, and layered dwarven armor",
        "signature": {"hair_color": "auburn", "hair_length": "shoulder length",
                      "facial_hair": "full beard", "eye_color": "dark brown"},
        "physique": {"body_type": "stocky", "height": "short", "skin_tone": "fair"},
    },
    "Frodo Baggins": {
        "franchise": "Lord of the Rings",
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
        "signature": {"hair_color": "white", "hair_length": "shoulder length",
                      "hair_style": "low ponytail", "facial_hair": "stubble",
                      "eye_color": "amber"},
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
    },
    "Master Chief": {
        "franchise": "Halo",
        "gender": "Male",
        "covers_face": True,
        "costume": "full matte olive-green Mjolnir power armor with heavy plated shoulders "
                   "and gauntlets",
        "mask": "a helmet with a golden-orange reflective visor",
        "physique": {"body_type": "athletic", "height": "very tall"},
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
}


def get_cosplayer_names() -> list[str]:
    """Return the sorted list of available cosplayer character names."""
    return sorted(COSPLAYERS.keys())


def get_cosplayer(name: str) -> dict:
    """Return the cosplay record for ``name`` (empty dict if unknown)."""
    return COSPLAYERS.get(name, {})


def get_cosplayer_names_by_gender(gender: str) -> list[str]:
    """Return sorted names whose SOURCE character matches ``gender``.

    Used for the node's "Random — female / male" scoping. The *person's* gender
    is chosen separately on the IdentityForge node, so this only filters which
    characters the random pick draws from.
    """
    return sorted(
        name for name, entry in COSPLAYERS.items() if entry.get("gender") == gender
    )


# Merge optional user-supplied cosplayers (./user_options.json, "cosplayers"
# section) so they survive ``git pull``. Done last so user entries can override
# a built-in of the same name and so a user "Male" entry can populate the
# "Random — male" scope.
from .user_options import apply_user_cosplayers  # noqa: E402

apply_user_cosplayers(COSPLAYERS)
