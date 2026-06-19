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
                   "blue-violet body paint",
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
        "costume": "orange body paint with white Togruta facial markings, a blue-and-"
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
        "costume": "a form-fitting bodysuit of overlapping leaves and vines with green "
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
                   "silver arm guards, and warm golden-orange body paint",
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
        "costume": "an all-over coat of dark blue scaled-skin body paint with natural "
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
        "costume": "a purple-and-white athletic leotard, with all-over leaf-green body "
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
                   "fitted pants, boots, all-over green body paint, and magenta hair tips",
        "signature": {"hair_color": "jet black", "hair_length": "long",
                      "hair_style": "worn down", "eye_color": "dark brown"},
        "physique": {"body_type": "athletic", "height": "average height"},
    },
    "Nebula": {
        "franchise": "Marvel",
        "gender": "Female",
        "costume": "a fitted dark combat suit with armored segments, boots, gauntlets, "
                   "blue metallic body paint with intricate plating, and purple "
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
                   "boots, green Twi'lek body paint, and two long head-tails (lekku)",
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
                   "a white bouffant wig, purple-gray body paint, and eight large purple "
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
        "costume": "a grey tank top, ripped jeans, sturdy boots, and pale greyish-blue "
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
