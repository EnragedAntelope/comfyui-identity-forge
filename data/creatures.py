"""Creature dataset for IdentityForge — a non-human *form* layer.

Each entry describes a creature as a set of **anatomy slots** that can be worn by
a character: a head, eyes, an integument (skin / fur / scales / chitin / shell), and
optional limbs, tail, wings and extra features. The Creature node picks one creature
(or hybridizes several — a praying-mantis body with a sloth's head) and emits a
``Species & Anatomy`` JSON group plus suppression flags that tell IdentityForge which
human fields to drop. Everything not replaced (a wired costume, the surviving human
body, the scene) still composes.

Schema per entry (keyed by creature name)::

    "praying mantis": {
        "class":      "Insects & Arachnids",  # which "Random - <class>" pool it joins
        "palette":    "emerald",               # default colour, applied to the integument
        "head":       "a triangular mantis head with swiveling antennae",
        "eyes":       "large bulbous compound eyes",
        "integument": "a segmented chitinous exoskeleton",   # colour-free; palette colours it
        "arms":       "raptorial spiked forelimbs",          # optional
        "hands":      "barbed grasping claws",               # optional
        "legs_feet":  "thin spined insectoid legs",          # optional
        "tail":       None,                                   # optional
        "wings":      "a folded pair of translucent wing-cases",  # optional
        "extras":     "a slender segmented abdomen",          # optional
    }

Curation rules (so the data stays coherent with the engine):

* **Slots are prose-ready phrases**, voiced after "... with" / "It has ...". A
  singular slot carries its article ("a triangular mantis head"); a mass/plural slot
  does not ("large compound eyes", "shaggy fur"). They are *not* validated against
  ``data/fields.py`` — the species group is rendered by its own prose path, which is
  what frees non-humans from the human field pools.
* **The integument is colour-free.** Leave the hue out of ``integument`` and put it in
  ``palette`` — the node prepends the palette (and any finish) onto the integument, so a
  user can recolour it ("crimson" instead of "emerald") without fighting baked-in text.
  Texture words (chitinous, scaled, furred, plated) stay in ``integument``.
* ``head`` and ``integument`` drive suppression: a creature head hides the human
  Face / Hair / Makeup; a creature integument hides the human skin fields. ``arms`` /
  ``hands`` / ``legs_feet`` have no human field to hide (the body is humanoid under an
  anthro form) — they simply add description.
* **Required slots:** ``class``, ``palette``, ``head``, ``eyes``, ``integument``.
  The rest are optional; set them to ``None`` or omit them when not iconic.
* **Plain ASCII only.** Slot text reaches the prompt, so avoid em/en dashes, smart
  quotes and ellipses (use ``-``, ``'``, ``...``) — some tokenizers mangle them.

This is a curated starter set spanning every class; add more incrementally (here or via
the ``creatures`` section of ``user_options.json``). ``tests/validate_data.py`` checks
the structure.
"""
from __future__ import annotations

#: Class ordering — also the order of the "Random - <class>" pools in the node.
CREATURE_CLASSES: tuple[str, ...] = (
    "Mammals",
    "Birds",
    "Reptiles & Amphibians",
    "Insects & Arachnids",
    "Marine Life",
    "Monsters",
    "Aliens",
    "Mythic & Fantasy",
    "Plant & Fungal",
)

#: The anatomy slots an entry may fill, in natural reading order.
CREATURE_SLOTS: tuple[str, ...] = (
    "head", "eyes", "integument", "arms", "hands", "legs_feet", "wings", "tail", "extras",
)

#: Creature name -> anatomy record. See module docstring for the schema.
CREATURES: dict[str, dict] = {
    # --- Mammals ----------------------------------------------------------
    "sloth": {
        "class": "Mammals", "palette": "grey-brown",
        "head": "a sloth's round, sleepy face with a blunt muzzle",
        "eyes": "small dark half-lidded eyes",
        "integument": "a coat of coarse shaggy fur",
        "arms": "long, slow-moving arms",
        "hands": "three-clawed hooked hands",
        "legs_feet": "stout clawed feet",
        "extras": "a faint algae-green tint to the fur",
    },
    "wolf": {
        "class": "Mammals", "palette": "slate-grey",
        "head": "a lupine head with a long muzzle and upright ears",
        "eyes": "sharp amber eyes",
        "integument": "a dense double coat of fur",
        "arms": "lean muscular arms",
        "hands": "clawed paw-like hands",
        "legs_feet": "digitigrade paws",
        "tail": "a bushy tail",
    },
    "lion": {
        "class": "Mammals", "palette": "tawny gold",
        "head": "a broad leonine head framed by a thick mane",
        "eyes": "golden predatory eyes",
        "integument": "short tawny fur",
        "arms": "powerful muscular arms",
        "hands": "heavy clawed paws",
        "legs_feet": "muscular digitigrade legs",
        "tail": "a long tufted tail",
    },
    "fox": {
        "class": "Mammals", "palette": "rust-orange",
        "head": "a slender vulpine head with large pointed ears",
        "eyes": "bright slitted amber eyes",
        "integument": "soft fur with a cream underbelly",
        "arms": "slim agile arms",
        "hands": "small black-clawed hands",
        "legs_feet": "neat black-socked paws",
        "tail": "a long white-tipped brush tail",
    },
    "bear": {
        "class": "Mammals", "palette": "deep brown",
        "head": "a massive ursine head with a wide snout and small round ears",
        "eyes": "small dark eyes",
        "integument": "a thick rugged coat of fur",
        "arms": "enormous powerful arms",
        "hands": "broad clawed paws",
        "legs_feet": "heavy plantigrade feet",
    },
    "rabbit": {
        "class": "Mammals", "palette": "dove-grey",
        "head": "a soft rounded head with tall upright ears",
        "eyes": "large gentle dark eyes",
        "integument": "plush velvety fur",
        "arms": "slender arms",
        "hands": "small soft-padded hands",
        "legs_feet": "powerful elongated hind feet",
        "tail": "a small cotton-puff tail",
    },
    "stag": {
        "class": "Mammals", "palette": "chestnut",
        "head": "a noble deer head crowned with broad branching antlers",
        "eyes": "deep liquid brown eyes",
        "integument": "sleek short fur",
        "arms": "lithe arms",
        "hands": "slim hands",
        "legs_feet": "slender cloven-hoofed legs",
        "extras": "a velvet sheen along the antlers",
    },

    # --- Birds ------------------------------------------------------------
    "owl": {
        "class": "Birds", "palette": "mottled brown",
        "head": "a rounded owl head with a sharp hooked beak and a facial disc",
        "eyes": "huge forward-facing golden eyes",
        "integument": "soft barred plumage",
        "arms": "feathered arms",
        "hands": "taloned grasping hands",
        "legs_feet": "feathered legs ending in hooked talons",
        "wings": "broad silent feathered wings",
    },
    "eagle": {
        "class": "Birds", "palette": "umber and white",
        "head": "a fierce eagle head with a hooked golden beak",
        "eyes": "piercing pale eyes with a heavy brow",
        "integument": "crisp overlapping feathers",
        "arms": "feathered arms",
        "hands": "powerful taloned hands",
        "legs_feet": "scaled yellow legs with black talons",
        "wings": "vast outstretched wings",
    },
    "raven": {
        "class": "Birds", "palette": "iridescent black",
        "head": "a sleek raven head with a stout black beak",
        "eyes": "glossy black eyes",
        "integument": "smooth dark plumage with an oily sheen",
        "arms": "feathered arms",
        "hands": "slender clawed hands",
        "legs_feet": "wiry scaled feet",
        "wings": "broad black wings",
    },
    "peacock": {
        "class": "Birds", "palette": "jewel-blue and green",
        "head": "a delicate head topped with a fan crest of filament feathers",
        "eyes": "bright dark eyes",
        "integument": "shimmering iridescent plumage",
        "arms": "graceful feathered arms",
        "hands": "fine slender hands",
        "legs_feet": "trim scaled feet",
        "tail": "a sweeping train of eyed tail feathers",
    },
    "falcon": {
        "class": "Birds", "palette": "steel-grey",
        "head": "a streamlined falcon head with a notched beak and a dark eye-stripe",
        "eyes": "keen black eyes",
        "integument": "tight aerodynamic plumage",
        "arms": "swept feathered arms",
        "hands": "sharp taloned hands",
        "legs_feet": "yellow scaled feet with black talons",
        "wings": "long pointed wings",
    },

    # --- Reptiles & Amphibians -------------------------------------------
    "gecko": {
        "class": "Reptiles & Amphibians", "palette": "leaf-green",
        "head": "a smooth lizard head with a wide jaw",
        "eyes": "large lidless eyes with vertical pupils",
        "integument": "fine pebbled scales",
        "arms": "slim arms",
        "hands": "splayed toe-padded hands",
        "legs_feet": "clinging padded feet",
        "tail": "a long tapering tail",
    },
    "cobra": {
        "class": "Reptiles & Amphibians", "palette": "olive and gold",
        "head": "a flat serpentine head with a flaring hood",
        "eyes": "fixed lidless eyes",
        "integument": "smooth overlapping scales",
        "arms": "sinuous arms",
        "hands": "slim scaled hands",
        "legs_feet": "a long coiling serpent's tail in place of legs",
        "extras": "a forked flickering tongue",
    },
    "crocodile": {
        "class": "Reptiles & Amphibians", "palette": "swamp-green",
        "head": "a long armored crocodilian head with interlocking teeth",
        "eyes": "raised reptilian eyes set far back",
        "integument": "thick bony-plated hide",
        "arms": "short powerful arms",
        "hands": "stubby clawed hands",
        "legs_feet": "squat clawed feet",
        "tail": "a heavy ridged tail",
    },
    "chameleon": {
        "class": "Reptiles & Amphibians", "palette": "shifting teal",
        "head": "a knobbed chameleon head with a tall casque",
        "eyes": "independently swiveling turret eyes",
        "integument": "colour-shifting granular scales",
        "arms": "slow deliberate arms",
        "hands": "pincer-like grasping hands",
        "legs_feet": "gripping zygodactyl feet",
        "tail": "a tightly coiled prehensile tail",
    },
    "frog": {
        "class": "Reptiles & Amphibians", "palette": "bright green",
        "head": "a wide-mouthed amphibian head",
        "eyes": "bulging golden eyes set high",
        "integument": "smooth moist glistening skin",
        "arms": "slender arms",
        "hands": "webbed sticky-tipped hands",
        "legs_feet": "long powerful webbed feet",
    },

    # --- Insects & Arachnids ---------------------------------------------
    "praying mantis": {
        "class": "Insects & Arachnids", "palette": "emerald",
        "head": "a triangular mantis head with swiveling antennae",
        "eyes": "large bulbous compound eyes",
        "integument": "a segmented chitinous exoskeleton",
        "arms": "raptorial spiked forelimbs",
        "hands": "barbed grasping claws",
        "legs_feet": "thin spined insectoid legs",
        "wings": "a folded pair of translucent wing-cases",
        "extras": "a slender segmented abdomen",
    },
    "rhinoceros beetle": {
        "class": "Insects & Arachnids", "palette": "glossy black",
        "head": "an armored beetle head bearing a curved horn",
        "eyes": "small dark bead eyes",
        "integument": "a hard glossy carapace",
        "arms": "stout segmented arms",
        "hands": "hooked gripping claws",
        "legs_feet": "spined clinging legs",
        "wings": "hardened wing-cases over folded flight wings",
    },
    "tarantula": {
        "class": "Insects & Arachnids", "palette": "dusky brown",
        "head": "a low arachnid head clustered with eyes",
        "eyes": "eight glossy black eyes",
        "integument": "a coat of bristled setae over a hard exoskeleton",
        "arms": "long hairy forelimbs",
        "hands": "fanged pedipalp claws",
        "legs_feet": "multiple jointed walking legs",
        "extras": "a bulbous spinneret abdomen",
    },
    "butterfly": {
        "class": "Insects & Arachnids", "palette": "sunset-orange",
        "head": "a delicate head with long curled antennae",
        "eyes": "round dark compound eyes",
        "integument": "a fine velvety scaled body",
        "arms": "slender arms",
        "hands": "dainty clawed hands",
        "legs_feet": "thin clinging legs",
        "wings": "large patterned scaled wings",
        "extras": "a coiled proboscis",
    },
    "scorpion": {
        "class": "Insects & Arachnids", "palette": "sand-amber",
        "head": "a low armored head with grasping mouthparts",
        "eyes": "rows of tiny dark eyes",
        "integument": "a hard segmented exoskeleton",
        "arms": "heavy pincered forelimbs",
        "hands": "serrated claws",
        "legs_feet": "eight spined walking legs",
        "tail": "a raised segmented tail tipped with a stinger",
    },
    "dragonfly": {
        "class": "Insects & Arachnids", "palette": "metallic teal",
        "head": "a globular head dominated by enormous eyes",
        "eyes": "vast wraparound compound eyes",
        "integument": "a slender iridescent exoskeleton",
        "arms": "spindly arms",
        "hands": "fine bristled claspers",
        "legs_feet": "thin clasping legs",
        "wings": "two pairs of long veined glassy wings",
        "extras": "a long jointed abdomen",
    },

    # --- Marine Life ------------------------------------------------------
    "octopus": {
        "class": "Marine Life", "palette": "mottled coral-red",
        "head": "a bulbous domed octopus head",
        "eyes": "horizontal slit-pupiled eyes",
        "integument": "soft colour-shifting skin dotted with chromatophores",
        "arms": "long sucker-lined tentacle arms",
        "hands": "curling tentacle tips",
        "legs_feet": "a base of writhing tentacles",
        "extras": "skin that flushes through shifting patterns",
    },
    "shark": {
        "class": "Marine Life", "palette": "steel-blue",
        "head": "a streamlined shark head with rows of jagged teeth",
        "eyes": "flat black lidless eyes",
        "integument": "rough denticled grey skin",
        "arms": "muscular arms",
        "hands": "clawed webbed hands",
        "legs_feet": "powerful finned legs",
        "tail": "a tall crescent tail fin",
        "extras": "a row of dorsal and gill slits",
    },
    "anglerfish": {
        "class": "Marine Life", "palette": "abyssal black",
        "head": "a huge-jawed anglerfish head bristling with needle teeth",
        "eyes": "tiny milky eyes",
        "integument": "loose dark scaleless skin",
        "arms": "stubby fin-like arms",
        "hands": "spined webbed hands",
        "legs_feet": "short finned legs",
        "extras": "a glowing bioluminescent lure on a stalk",
    },
    "jellyfish": {
        "class": "Marine Life", "palette": "translucent rose",
        "head": "a translucent domed bell of a head",
        "eyes": "no distinct eyes, only faint light-sensing rims",
        "integument": "gelatinous translucent flesh",
        "arms": "trailing frilled oral arms",
        "hands": "drifting tentacle fingers",
        "legs_feet": "a curtain of stinging tentacles",
        "extras": "a soft internal bioluminescent glow",
    },
    "crab": {
        "class": "Marine Life", "palette": "brick-red",
        "head": "a low carapaced head with stalked eyes",
        "eyes": "eyes on swiveling stalks",
        "integument": "a hard calcified shell",
        "arms": "asymmetric clawed arms",
        "hands": "one oversized crushing claw and one fine pincer",
        "legs_feet": "jointed sideways-walking legs",
    },
    "manta ray": {
        "class": "Marine Life", "palette": "ink-blue and white",
        "head": "a flat broad head flanked by curling cephalic fins",
        "eyes": "wide-set dark eyes",
        "integument": "smooth countershaded skin",
        "arms": "broad wing-like arms",
        "hands": "fused fin-tips",
        "legs_feet": "a tapering finned lower body",
        "tail": "a long whip-thin tail",
    },

    # --- Monsters ---------------------------------------------------------
    "zombie": {
        "class": "Monsters", "palette": "ashen grey-green",
        "head": "a gaunt rotting head with a slack jaw",
        "eyes": "clouded sunken eyes",
        "integument": "decayed mottled flesh stretched over bone",
        "arms": "stiff wasted arms",
        "hands": "skeletal clutching hands",
        "legs_feet": "shuffling withered legs",
        "extras": "exposed sinew and torn skin",
    },
    "vampire": {
        "class": "Monsters", "palette": "corpse-pale",
        "head": "a gaunt aristocratic head with a widow's peak and pointed ears",
        "eyes": "blood-red eyes",
        "integument": "cold porcelain-pale skin",
        "arms": "lean elegant arms",
        "hands": "long clawed fingers",
        "legs_feet": "slender legs",
        "extras": "a pair of needle fangs",
    },
    "werewolf": {
        "class": "Monsters", "palette": "charcoal",
        "head": "a snarling wolfen head with a bristling ruff",
        "eyes": "burning yellow eyes",
        "integument": "coarse bristling fur over corded muscle",
        "arms": "huge hunched arms",
        "hands": "great clawed hands",
        "legs_feet": "powerful digitigrade hind legs",
        "tail": "a thick lupine tail",
    },
    "demon": {
        "class": "Monsters", "palette": "ember-red",
        "head": "a horned demonic head with a fanged grin",
        "eyes": "slitted glowing eyes",
        "integument": "cracked smoldering hide",
        "arms": "brawny clawed arms",
        "hands": "taloned hands",
        "legs_feet": "cloven hooves on backward-jointed legs",
        "tail": "a long barbed tail",
        "wings": "a pair of leathery bat wings",
    },
    "eldritch horror": {
        "class": "Monsters", "palette": "void-violet",
        "head": "an asymmetric head wreathed in writhing tendrils",
        "eyes": "too many eyes scattered across the flesh",
        "integument": "shifting non-euclidean flesh that the gaze slides off",
        "arms": "branching tentacular limbs",
        "hands": "grasping suckered tendrils",
        "legs_feet": "a roiling mass of tentacles",
        "extras": "a faint halo of warped space",
    },
    "gargoyle": {
        "class": "Monsters", "palette": "weathered stone-grey",
        "head": "a grotesque horned head carved in stone",
        "eyes": "blank hollow eyes",
        "integument": "rough weathered stone skin",
        "arms": "heavy carved arms",
        "hands": "blunt clawed stone hands",
        "legs_feet": "squat taloned stone feet",
        "wings": "folded stone wings",
    },
    "slime": {
        "class": "Monsters", "palette": "translucent lime",
        "head": "a soft rounded head that holds its shape only loosely",
        "eyes": "two simple dark spots for eyes",
        "integument": "a translucent gelatinous body",
        "arms": "fluid dripping arms",
        "hands": "blunt amorphous hands",
        "legs_feet": "a wobbling gelatinous base",
        "extras": "small objects suspended within the jelly",
    },

    # --- Aliens -----------------------------------------------------------
    "grey alien": {
        "class": "Aliens", "palette": "ash-grey",
        "head": "an oversized smooth cranium tapering to a small chin",
        "eyes": "huge opaque black almond eyes",
        "integument": "smooth hairless rubbery skin",
        "arms": "thin elongated arms",
        "hands": "long four-fingered hands",
        "legs_feet": "spindly legs",
    },
    "insectoid xeno": {
        "class": "Aliens", "palette": "obsidian black",
        "head": "an elongated ridged carapace head with no visible eyes",
        "eyes": "a smooth eyeless domed crown",
        "integument": "a biomechanical chitinous shell",
        "arms": "double-jointed clawed arms",
        "hands": "bladed talon hands",
        "legs_feet": "digitigrade clawed legs",
        "tail": "a long bladed segmented tail",
        "extras": "dorsal vent tubes",
    },
    "reptilian alien": {
        "class": "Aliens", "palette": "venom-green",
        "head": "a ridged saurian head with a frill",
        "eyes": "vertical-slit golden eyes",
        "integument": "fine iridescent scales",
        "arms": "wiry scaled arms",
        "hands": "three-clawed hands",
        "legs_feet": "digitigrade clawed legs",
        "tail": "a tapering reptilian tail",
    },
    "energy being": {
        "class": "Aliens", "palette": "electric cyan",
        "head": "a head of coalesced glowing plasma",
        "eyes": "two brighter cores where eyes would be",
        "integument": "a body of luminous semi-transparent energy",
        "arms": "trailing arms of streaming light",
        "hands": "hands that flare and dissipate at the fingertips",
        "legs_feet": "a tapering tail of light instead of legs",
        "extras": "a constant crackle of arcing sparks",
    },
    "biomechanical alien": {
        "class": "Aliens", "palette": "gunmetal and chrome",
        "head": "a sleek fused organic-metal head with sensor slits",
        "eyes": "a glowing horizontal optical band",
        "integument": "ridged metal plating grown over grey flesh",
        "arms": "piston-jointed mechanical arms",
        "hands": "articulated steel digits",
        "legs_feet": "hydraulic reverse-jointed legs",
        "extras": "exposed cabling and softly pulsing lights",
    },
    "crystalline alien": {
        "class": "Aliens", "palette": "amethyst",
        "head": "a faceted angular crystal head",
        "eyes": "glowing geometric eye-facets",
        "integument": "a body of translucent growing crystal",
        "arms": "sharp prismatic arms",
        "hands": "blade-like crystal fingers",
        "legs_feet": "faceted crystalline legs",
        "extras": "light refracting through the body",
    },

    # --- Mythic & Fantasy -------------------------------------------------
    "dragon": {
        "class": "Mythic & Fantasy", "palette": "crimson",
        "head": "a horned draconic head with a long snout and back-swept horns",
        "eyes": "slit-pupiled molten eyes",
        "integument": "overlapping armored scales",
        "arms": "powerful clawed arms",
        "hands": "great taloned hands",
        "legs_feet": "muscular clawed legs",
        "tail": "a long spined tail",
        "wings": "vast leathery membranous wings",
    },
    "naga": {
        "class": "Mythic & Fantasy", "palette": "jade",
        "head": "a regal serpent-browed head crowned with a small hood",
        "eyes": "golden slit-pupiled eyes",
        "integument": "smooth jeweled scales over a human torso",
        "arms": "graceful arms",
        "hands": "ringed slender hands",
        "legs_feet": "a long coiling serpent's tail in place of legs",
    },
    "centaur": {
        "class": "Mythic & Fantasy", "palette": "chestnut",
        "head": "a human head with a flowing mane",
        "eyes": "warm dark eyes",
        "integument": "a human torso joined to a horse's hide",
        "arms": "strong arms",
        "hands": "broad hands",
        "legs_feet": "the four hooved legs of a horse",
        "tail": "a long horse's tail",
    },
    "gryphon": {
        "class": "Mythic & Fantasy", "palette": "gold and brown",
        "head": "an eagle's head with a hooked beak and tufted crest",
        "eyes": "fierce golden eyes",
        "integument": "feathered forequarters blending into a lion's pelt",
        "arms": "feathered taloned forelimbs",
        "hands": "eagle talons",
        "legs_feet": "a lion's powerful hind legs",
        "tail": "a tufted leonine tail",
        "wings": "great feathered wings",
    },
    "minotaur": {
        "class": "Mythic & Fantasy", "palette": "dark umber",
        "head": "a broad bovine head with heavy curved horns and a ring-pierced nose",
        "eyes": "deep-set dark eyes",
        "integument": "short coarse hide over a massive frame",
        "arms": "tremendous muscular arms",
        "hands": "thick blunt-nailed hands",
        "legs_feet": "cloven-hoofed digitigrade legs",
        "tail": "a tufted tail",
    },
    "merfolk": {
        "class": "Mythic & Fantasy", "palette": "aqua and pearl",
        "head": "a comely head with finned ears and pearl-strung hair",
        "eyes": "large sea-green eyes",
        "integument": "a human torso scaled below into shimmering fish-skin",
        "arms": "smooth arms with faint fin-ridges",
        "hands": "webbed hands",
        "legs_feet": "a long iridescent fish tail in place of legs",
        "extras": "translucent fins along the forearms",
    },
    "satyr": {
        "class": "Mythic & Fantasy", "palette": "earthy brown",
        "head": "a human head with small curling ram's horns and pointed ears",
        "eyes": "mischievous amber eyes",
        "integument": "a human torso above shaggy goat-furred legs",
        "arms": "lean arms",
        "hands": "calloused hands",
        "legs_feet": "cloven-hoofed digitigrade goat legs",
        "tail": "a short flicking tail",
    },
    "harpy": {
        "class": "Mythic & Fantasy", "palette": "dusky brown",
        "head": "a fierce human head with a feathered crest",
        "eyes": "wild raptor-bright eyes",
        "integument": "a human torso edged in feathers",
        "arms": "feathered wing-arms",
        "hands": "clawed wing-fingers",
        "legs_feet": "scaled bird legs ending in great talons",
        "wings": "broad feathered wings in place of arms",
    },

    # --- Plant & Fungal ---------------------------------------------------
    "treant": {
        "class": "Plant & Fungal", "palette": "mossy bark-brown",
        "head": "a head of knotted bark with a face in the grain",
        "eyes": "deep-set glowing sap-amber eyes",
        "integument": "rough living bark wrapped in moss",
        "arms": "branching wooden arms",
        "hands": "twig-fingered hands",
        "legs_feet": "root-bundled legs",
        "extras": "small leaves and lichen sprouting along the limbs",
    },
    "mushroom folk": {
        "class": "Plant & Fungal", "palette": "spotted scarlet",
        "head": "a broad domed mushroom cap for a head",
        "eyes": "small dark dot eyes beneath the cap",
        "integument": "a soft spongy fibrous body",
        "arms": "stubby fungal arms",
        "hands": "soft rounded hands",
        "legs_feet": "a stout pale stipe-like base",
        "extras": "a faint drift of spores",
    },
    "carnivorous plant": {
        "class": "Plant & Fungal", "palette": "venus-green and red",
        "head": "a great hinged trap-jaw head fringed with teeth-like cilia",
        "eyes": "no eyes, only sensing trigger-hairs",
        "integument": "waxy veined plant flesh",
        "arms": "coiling vine arms",
        "hands": "snapping bud-traps",
        "legs_feet": "a writhing root base",
        "extras": "beads of glistening nectar",
    },
    "cactus folk": {
        "class": "Plant & Fungal", "palette": "sage-green",
        "head": "a rounded cactus head topped with a crown of small flowers",
        "eyes": "simple dark dot eyes",
        "integument": "thick ribbed succulent skin studded with spines",
        "arms": "upraised branching arms",
        "hands": "blunt spined hands",
        "legs_feet": "a stout rooted base",
    },
    "flower folk": {
        "class": "Plant & Fungal", "palette": "blossom-pink",
        "head": "a head haloed by a wide blooming flower",
        "eyes": "bright dew-glistening eyes",
        "integument": "smooth petal-soft green skin",
        "arms": "slender leaf-edged arms",
        "hands": "delicate petal-tipped hands",
        "legs_feet": "vine-wrapped legs",
        "extras": "leaves and buds curling from the shoulders",
    },
}


# ===========================================================================
# Lookups (mirror data/cosplayers.py so the node code reads the same way)
# ===========================================================================

def get_creature_names() -> list[str]:
    """Return the sorted list of available creature names."""
    return sorted(CREATURES.keys())


def get_creature(name: str) -> dict:
    """Return the anatomy record for ``name`` (empty dict if unknown)."""
    return CREATURES.get(name, {})


def get_creature_names_by_class(creature_class: str) -> list[str]:
    """Return sorted creature names belonging to ``creature_class``.

    Used for the node's "Random - <class>" scoping (only-a-monster /
    only-an-insect / etc.). An unknown class yields an empty list.
    """
    return sorted(
        name for name, entry in CREATURES.items()
        if entry.get("class") == creature_class
    )


# Merge optional user-supplied creatures (./user_options.json, "creatures"
# section) so custom forms survive a git pull. Imported late to avoid a cycle.
from .user_options import apply_user_creatures  # noqa: E402

apply_user_creatures(CREATURES)
