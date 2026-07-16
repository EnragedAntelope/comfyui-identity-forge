"""Field definitions and option pools for IdentityForge."""
from __future__ import annotations

from collections import OrderedDict

#: OrderedDict of all IdentityForge fields.
#: Each entry has: group, female_options, male_options, optional.
FIELD_DEFINITIONS: OrderedDict[str, dict] = OrderedDict([
    ("gender", {
        "group": 'Demographics',
        "female_options": ['Female', 'Male', 'Any'],
        "male_options": ['Female', 'Male', 'Any'],
        "optional": False,
        # Control field: read directly from the gender toggle, never randomized,
        # and never emitted as a descriptive value.
        "control": True
    }),
    ("age", {
        "group": 'Demographics',
        "female_options": ['18', '19', '20', '22', '25', '28', '30', '33', '35', '38', '40', '43', '45', '48', '50', '55', '60', '65', '70'],
        "male_options": ['18', '19', '20', '22', '25', '28', '30', '33', '35', '38', '40', '43', '45', '48', '50', '55', '60', '65', '70'],
        "optional": False
    }),
    ("ethnicity", {
        "group": 'Demographics',
        "female_options": ['Aboriginal Australian', 'Afghan', 'Argentinian', 'Armenian', 'Austrian', 'Bangladeshi', 'Berber', 'Bolivian', 'Brazilian', 'Burmese', 'Cambodian', 'Chilean', 'Chinese', 'Colombian', 'Congolese', 'Croatian', 'Cuban', 'Czech', 'Danish', 'Dominican', 'Dutch', 'Egyptian', 'English', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Guatemalan', 'Haitian', 'Hawaiian', 'Hungarian', 'Icelandic', 'Indian', 'Indonesian', 'Inuit', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Jamaican', 'Japanese', 'Kazakh', 'Kenyan', 'Korean', 'Laotian', 'Lebanese', 'Malaysian', 'Maori', 'Mexican', 'Mongolian', 'Moroccan', 'Native American', 'Nepali', 'Nigerian', 'Norwegian', 'Pakistani', 'Palestinian', 'Peruvian', 'Polish', 'Portuguese', 'Puerto Rican', 'Romani', 'Romanian', 'Russian', 'Samoan', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Singaporean', 'Somali', 'South African', 'Spanish', 'Sri Lankan', 'Sudanese', 'Swedish', 'Syrian', 'Taiwanese', 'Thai', 'Tibetan', 'Turkish', 'Ukrainian', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemeni'],
        "male_options": ['Aboriginal Australian', 'Afghan', 'Argentinian', 'Armenian', 'Austrian', 'Bangladeshi', 'Berber', 'Bolivian', 'Brazilian', 'Burmese', 'Cambodian', 'Chilean', 'Chinese', 'Colombian', 'Congolese', 'Croatian', 'Cuban', 'Czech', 'Danish', 'Dominican', 'Dutch', 'Egyptian', 'English', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Guatemalan', 'Haitian', 'Hawaiian', 'Hungarian', 'Icelandic', 'Indian', 'Indonesian', 'Inuit', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Jamaican', 'Japanese', 'Kazakh', 'Kenyan', 'Korean', 'Laotian', 'Lebanese', 'Malaysian', 'Maori', 'Mexican', 'Mongolian', 'Moroccan', 'Native American', 'Nepali', 'Nigerian', 'Norwegian', 'Pakistani', 'Palestinian', 'Peruvian', 'Polish', 'Portuguese', 'Puerto Rican', 'Romani', 'Romanian', 'Russian', 'Samoan', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Singaporean', 'Somali', 'South African', 'Spanish', 'Sri Lankan', 'Sudanese', 'Swedish', 'Syrian', 'Taiwanese', 'Thai', 'Tibetan', 'Turkish', 'Ukrainian', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemeni'],
        "optional": False
    }),
    ("skin_tone", {
        "group": 'Body',
        "female_options": ['porcelain', 'very pale', 'pale', 'fair', 'light', 'light medium', 'medium', 'medium olive', 'olive', 'warm tan', 'tan', 'golden tan', 'bronze', 'caramel', 'brown', 'warm brown', 'dark brown', 'deep', 'ebony', 'deep ebony'],
        "male_options": ['porcelain', 'very pale', 'pale', 'fair', 'light', 'light medium', 'medium', 'medium olive', 'olive', 'warm tan', 'tan', 'golden tan', 'bronze', 'caramel', 'brown', 'warm brown', 'dark brown', 'deep', 'ebony', 'deep ebony'],
        "optional": False
    }),
    ("body_type", {
        "group": 'Body',
        "female_options": ['very slim', 'slim', 'slender', 'lean', 'athletic', 'toned', 'fit', 'average', 'softly curved', 'curvy', 'full figured', 'voluptuous', 'hourglass', 'stocky', 'chubby', 'plump', 'plus size', 'petite and slim', 'petite and curvy'],
        "male_options": ['very slim', 'slim', 'slender', 'lean', 'athletic', 'toned', 'fit', 'average', 'softly curved', 'curvy', 'full figured', 'voluptuous', 'hourglass', 'stocky', 'chubby', 'plump', 'plus size', 'petite and slim', 'petite and curvy'],
        "optional": False
    }),
    ("height", {
        "group": 'Body',
        "female_options": ['very petite', 'petite', 'short', 'slightly below average height', 'average height', 'slightly above average height', 'tall', 'statuesque', 'very tall'],
        "male_options": ['very petite', 'petite', 'short', 'slightly below average height', 'average height', 'slightly above average height', 'tall', 'statuesque', 'very tall'],
        "optional": False
    }),
    ("bust", {
        "group": 'Body',
        "female_options": ['very small', 'small', 'modest', 'medium', 'full', 'large', 'very large', 'generously proportioned'],
        "male_options": ['flat', 'slightly defined', 'average', 'broad', 'muscular', 'large'],
        "optional": True
    }),
    ("waist", {
        "group": 'Body',
        "female_options": ['very narrow', 'narrow', 'defined', 'average', 'slightly wide', 'wide', 'full'],
        "male_options": ['very narrow', 'narrow', 'defined', 'average', 'slightly wide', 'wide', 'full'],
        "optional": False
    }),
    ("hips", {
        "group": 'Body',
        "female_options": ['narrow', 'slightly narrow', 'average', 'slightly wide', 'wide', 'full', 'very full', 'rounded'],
        "male_options": ['narrow', 'slightly narrow', 'average', 'slightly wide', 'wide', 'full', 'very full', 'rounded'],
        "optional": False
    }),
    # --- Face: ordered structure -> eyes -> nose -> mouth/lower face -> skin.
    # The widget order on the node follows this list order within the group; the
    # prose order is independent (hard-coded in _format_prose).
    ("face_shape", {
        "group": 'Face',
        "female_options": ['oval', 'round', 'soft round', 'square', 'soft square', 'heart-shaped', 'diamond', 'oblong', 'rectangular', 'wide', 'narrow and angular'],
        "male_options": ['oval', 'round', 'soft round', 'square', 'soft square', 'heart-shaped', 'diamond', 'oblong', 'rectangular', 'wide', 'narrow and angular'],
        "optional": False
    }),
    ("forehead", {
        "group": 'Face',
        "female_options": ['high and broad', 'low and broad', 'average', 'narrow', 'rounded', 'prominent brow ridge', 'smooth'],
        "male_options": ['high and broad', 'low and broad', 'average', 'narrow', 'rounded', 'prominent brow ridge', 'smooth'],
        "optional": False
    }),
    ("cheekbones", {
        "group": 'Face',
        "female_options": ['very high and prominent', 'high and defined', 'high and soft', 'prominent', 'softly prominent', 'average', 'wide and flat', 'subtle', 'barely defined'],
        "male_options": ['very high and prominent', 'high and defined', 'high and soft', 'prominent', 'softly prominent', 'average', 'wide and flat', 'subtle', 'barely defined'],
        "optional": False
    }),
    # Natural brow shape/thickness only. Styling/makeup looks (feathered, laminated,
    # bold sculpted) are owned by the Makeup eyebrow_makeup field, so they are not
    # repeated here -- avoids "feathered eyebrows ... laminated look brows" doubling.
    ("eyebrows", {
        "group": 'Face',
        "female_options": ['thin and arched', 'thin and straight', 'pencil thin', 'barely there', 'natural full', 'thick and straight', 'thick and arched', 'bushy', 'well defined and arched', 'bleached'],
        "male_options": ['thin and arched', 'thin and straight', 'pencil thin', 'barely there', 'natural full', 'thick and straight', 'thick and arched', 'bushy', 'well defined and arched', 'bleached'],
        # 'bleached' brows read as "missing/invisible" to T2I models often enough
        # that a flat 1-in-10 draw is too frequent, so an all-gender draw-weight
        # trims it to ~2% (0.2 vs the implicit 1 of every other option). It stays
        # fully selectable in the widget and lockable by presets that want it.
        "weights": {'bleached': 0.2},
        "optional": False
    }),
    ("eye_color", {
        "group": 'Face',
        "female_options": ['pale blue', 'ice blue', 'bright blue', 'deep blue', 'blue-gray', 'gray', 'dark gray', 'green', 'bright green', 'emerald', 'hazel', 'warm hazel', 'light brown', 'medium brown', 'dark brown', 'nearly black', 'amber', 'golden brown', 'violet-gray', 'gray-green', 'honey', 'dark hazel', 'steel blue'],
        "male_options": ['pale blue', 'ice blue', 'bright blue', 'deep blue', 'blue-gray', 'gray', 'dark gray', 'green', 'bright green', 'emerald', 'hazel', 'warm hazel', 'light brown', 'medium brown', 'dark brown', 'nearly black', 'amber', 'golden brown', 'violet-gray', 'gray-green', 'honey', 'dark hazel', 'steel blue'],
        "optional": False
    }),
    # eye_shape is the single comprehensive eye-structure field: it encodes shape,
    # lid (monolid/hooded), spacing (wide/close-set) and size (large/small/doe-like),
    # so separate eye_size / eyelid_type fields were removed to avoid duplication.
    ("eye_shape", {
        "group": 'Face',
        "female_options": ['almond', 'round', 'slightly hooded', 'hooded', 'upturned', 'downturned', 'monolid', 'deep-set', 'wide-set', 'close-set', 'large and expressive', 'small and delicate', 'doe-like'],
        "male_options": ['almond', 'round', 'slightly hooded', 'hooded', 'upturned', 'downturned', 'monolid', 'deep-set', 'wide-set', 'close-set', 'large and expressive', 'small and delicate', 'doe-like'],
        "optional": False
    }),
    ("nose", {
        "group": 'Face',
        "female_options": ['small and button', 'small and upturned', 'straight', 'slightly upturned', 'aquiline', 'Roman', 'broad', 'wide', 'narrow and refined', 'slightly crooked', 'slightly bumped', 'prominent', 'petite', 'snub', 'wide with flared nostrils'],
        "male_options": ['small and button', 'small and upturned', 'straight', 'slightly upturned', 'aquiline', 'Roman', 'broad', 'wide', 'narrow and refined', 'slightly crooked', 'slightly bumped', 'prominent', 'petite', 'snub', 'wide with flared nostrils'],
        "optional": False
    }),
    ("lips", {
        "group": 'Face',
        "female_options": ['very thin', 'thin', 'average', 'slightly full', 'full', 'very full', 'plump', 'bow-shaped', 'heart-shaped', 'wide and full', 'petite and defined', 'uneven slightly asymmetric'],
        "male_options": ['very thin', 'thin', 'average', 'slightly full', 'full', 'very full', 'plump', 'bow-shaped', 'heart-shaped', 'wide and full', 'petite and defined', 'uneven slightly asymmetric'],
        "optional": False
    }),
    # smile_type is the single mouth-state field (teeth_visibility was merged in and
    # removed): its values span closed mouth -> toothy grin, so it covers teeth too.
    ("smile_type", {
        "group": 'Face',
        "female_options": ['closed mouth', 'soft smile', 'toothy grin', 'asymmetric', 'broad', 'subtle dimpled'],
        "male_options": ['closed mouth', 'soft smile', 'toothy grin', 'asymmetric', 'broad', 'subtle dimpled'],
        "optional": False
    }),
    # jawline (line angularity / width) and chin (tip shape) keep disjoint vocabularies
    # so adjacent face structure never restates the same word ("rounded jawline and
    # rounded chin"). jawline owns wide/narrow; chin owns rounded.
    ("jawline", {
        "group": 'Face',
        "female_options": ['sharp and defined', 'strong', 'square', 'slightly square', 'soft', 'delicate', 'narrow', 'wide', 'tapered', 'prominent'],
        "male_options": ['sharp and defined', 'strong', 'square', 'slightly square', 'soft', 'delicate', 'narrow', 'wide', 'tapered', 'prominent'],
        "optional": False
    }),
    ("chin", {
        "group": 'Face',
        "female_options": ['rounded', 'softly pointed', 'pointed', 'slightly cleft', 'cleft', 'small and delicate', 'receding', 'strong and square'],
        "male_options": ['rounded', 'softly pointed', 'pointed', 'slightly cleft', 'cleft', 'small and delicate', 'receding', 'strong and square'],
        "optional": False
    }),
    ("complexion", {
        "group": 'Face',
        # Skin undertone / health (always rendered). 'olive' removed: it collided with
        # skin_tone's 'olive'. 'matte'/'dewy' removed: those are finishes owned by the
        # Makeup skin_finish field (avoids "matte complexion ... matte finish" doubling).
        # Texture words live in skin_details.
        "female_options": ['clear', 'rosy', 'sallow', 'ruddy', 'peaches and cream'],
        "male_options": ['clear', 'rosy', 'sallow', 'ruddy', 'peaches and cream'],
        "optional": False
    }),
    ("skin_details", {
        "group": 'Face',
        # Distinguishing marks / texture only. Freckles are owned solely by the
        # freckles_density field (no double-sourcing); skin-finish words live in
        # complexion. The 'no notable marks' token is the absent value driven by
        # accessory_density via _EXTRA_ABSENCE, so most faces carry no mark.
        # "small scar through eyebrow" was "dimples when smiling" pre-0.36:
        # dimples are owned by smile_type ("subtle dimpled") and the pair read
        # as a tautology when both landed in one output.
        "female_options": ['no notable marks', 'porcelain smooth', 'lightly textured', 'mole above lip', 'beauty mark on cheek', 'birthmark on neck', 'small scar on chin', 'small scar through eyebrow', 'laugh lines', 'vitiligo patches', 'faint acne scarring', 'prominent beauty mark'],
        "male_options": ['no notable marks', 'porcelain smooth', 'lightly textured', 'mole above lip', 'beauty mark on cheek', 'birthmark on neck', 'small scar on chin', 'small scar through eyebrow', 'laugh lines', 'vitiligo patches', 'faint acne scarring', 'prominent beauty mark'],
        "optional": True
    }),
    ("freckles_density", {
        "group": 'Face',
        "female_options": ['none', 'few', 'scattered', 'moderate', 'heavy', 'all-over'],
        "male_options": ['none', 'few', 'scattered', 'moderate', 'heavy', 'all-over'],
        "optional": False
    }),
    ("hair_color", {
        "group": 'Hair',
        "female_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "male_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "optional": False, "natural_hair_colors": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair'], "full_spectrum_hair_colors": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips']
    }),
    ("hair_length", {
        "group": 'Hair',
        # 'bald' is male-only (like hair_style's 'comb over'): a random bald
        # woman reads as an unintended costume/illness cue, while bald men are
        # everyday. The engine treats a resolved 'bald' as scalp-only: it drops
        # the other scalp-hair fields (colour/texture/style/part/highlights/
        # accessory) and voices "his head is bald" (facial hair may remain).
        "female_options": ['buzzed very short', 'very short', 'short pixie', 'ear length', 'chin length bob', 'jaw length', 'shoulder length', 'slightly past shoulders', 'mid back', 'lower back', 'long', 'very long', 'waist length', 'hip length'],
        "male_options": ['bald', 'buzzed very short', 'very short', 'short pixie', 'ear length', 'chin length bob', 'jaw length', 'shoulder length', 'slightly past shoulders', 'mid back', 'lower back', 'long', 'very long', 'waist length', 'hip length'],
        "optional": False
    }),
    ("hair_texture", {
        "group": 'Hair',
        # 'silky and glossy' is the luxurious salon-shine look (silken straight
        # hair catching the light); 'sleek straight' stays the plainer
        # styled-straight without the lustre cue. Adjectival like 'fine and
        # wispy' so it reads clean in the inline "{length} {texture} {color}"
        # hair sentence.
        "female_options": ['pin straight', 'sleek straight', 'silky and glossy', 'slightly wavy', 'loosely wavy', 'wavy', 'beachy waves', 'loosely curled', 'softly curled', 'curly', 'tightly curled', 'coily', 'kinky coily', 'fine and wispy', 'thick and voluminous'],
        "male_options": ['pin straight', 'sleek straight', 'silky and glossy', 'slightly wavy', 'loosely wavy', 'wavy', 'beachy waves', 'loosely curled', 'softly curled', 'curly', 'tightly curled', 'coily', 'kinky coily', 'fine and wispy', 'thick and voluminous'],
        # 'silky and glossy' is the luxurious salon-shine look. It stays in the
        # male pool (legit for K-pop idol / Bollywood hero / bishonen / glam looks
        # and lockable by such archetypes) but reads feminine as a random default
        # on rugged male subjects, so a male-only draw-weight makes it rare on
        # random men (0.3 vs the implicit 1). Female and "Any" draws are unchanged.
        "male_weights": {'silky and glossy': 0.3},
        "optional": False
    }),
    ("hair_style", {
        "group": 'Hair',
        # 'comb over' is deliberately male-only: T2I models read it as a
        # balding-male cue, which ages/masculinizes random female characters.
        # 'mullet' is male-only for the same pool-hygiene reason: T2I models
        # render the term as the masculine 80s cut, which reads as a costume
        # gag on a random female character (archetypes can still curate it).
        "female_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled', 'tousled bedhead', 'ballerina bun', 'braided ponytail'],
        "male_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled', 'tousled bedhead', 'ballerina bun', 'braided ponytail', 'comb over', 'mullet'],
        "optional": False
    }),
    ("hair_color_scope", {
        "group": 'Hair',
        "female_options": ['Full spectrum', 'Natural only'],
        "male_options": ['Full spectrum', 'Natural only'],
        "optional": False,
        # Control field: a user toggle that gates the hair_color pool. Never
        # randomized and never emitted as a descriptive value.
        "control": True
    }),
    ("facial_hair", {
        "group": 'Hair',
        # Female characters are clean-shaven by default so randomization never
        # grows a beard on a woman; the full range stays available on the widget
        # (via male_options) for the "Male"/"Any" pools and manual locking.
        "female_options": ['clean shaven'],
        "male_options": ['clean shaven', 'stubble', 'short beard', 'full beard', 'goatee', 'mustache', 'van dyke', 'soul patch', 'mutton chops', "five o'clock shadow"],
        "optional": True
    }),
    ("hair_accessory", {
        "group": 'Hair',
        # Gender-divergent like facial_hair: random women draw the full feminine
        # range, random men only a small unisex set, so a bow never lands on a
        # random male subject -- yet the widget exposes everything for manual
        # locking. Absence ("no hair accessory") is density-gated in the engine's
        # _EXTRA_ABSENCE so adding options diversifies which piece appears without
        # changing how often a hair accessory appears at all.
        "female_options": ['no hair accessory', 'hair bow', 'oversized hair bow', 'satin ribbon tied in hair', 'silk headband', 'knotted headband', 'padded headband', 'scrunchie', 'claw clip', 'small hair clip', 'decorative hair pins', 'jeweled hair comb', 'thin scarf tied in hair', 'flower crown'],
        "male_options": ['no hair accessory', 'thin headband', 'bandana tied over hair'],
        "optional": False
    }),
    ("makeup_style", {
        "group": 'Makeup',
        "female_options": ['no makeup', 'barely there natural makeup', 'soft natural makeup', 'fresh-faced dewy look', 'classic no-makeup makeup', 'soft everyday glam', 'soft glam', 'full glam', 'bold glam', 'heavy glam', 'editorial makeup', 'vintage 1950s pin-up makeup', 'mod 1960s eye makeup', 'gothic dark makeup', 'club makeup'],
        # Male randomization leans natural so a random man is not painted in full
        # glam by default; the full range stays on the widget (via the female
        # pool union) for "Any"/manual stylized looks. The lean is the explicit
        # male_weights entry below (a 2x draw weight on 'no makeup'), consumed by
        # the engine's flat pick — never duplicate a value in an options list to
        # weight it (the validator rejects duplicates).
        "male_options": ['no makeup', 'barely there natural makeup', 'soft natural makeup', 'fresh-faced dewy look', 'classic no-makeup makeup'],
        "male_weights": {'no makeup': 2},
        "optional": False
    }),
    # Makeup widgets are ordered top-to-bottom of the face: makeup_style (the
    # umbrella) -> brows -> eyes -> cheeks (contour/highlight/blush) -> lips ->
    # overall skin finish. The prose order is independent (hard-coded in
    # _format_prose), so this ordering is a UI nicety with no output effect.
    ("eyebrow_makeup", {
        "group": 'Makeup',
        "female_options": ['none', 'filled in', 'feathered', 'bold sculpted', 'laminated look', 'tinted'],
        "male_options": ['none', 'filled in', 'feathered', 'bold sculpted', 'laminated look', 'tinted'],
        "optional": False
    }),
    ("eye_makeup", {
        "group": 'Makeup',
        "female_options": ['no eyeshadow', 'neutral matte', 'warm earth tones', 'cool browns and taupes', 'rosy mauve', 'copper and bronze', 'warm bronze', 'smoky gray', 'smoky black', 'deep navy', 'colorful bold eyeshadow', 'glittery', 'cut crease', 'floating liner look'],
        "male_options": ['no eyeshadow', 'neutral matte', 'warm earth tones', 'cool browns and taupes', 'rosy mauve', 'copper and bronze', 'warm bronze', 'smoky gray', 'smoky black', 'deep navy', 'colorful bold eyeshadow', 'glittery', 'cut crease', 'floating liner look'],
        "optional": False
    }),
    ("eyeliner", {
        "group": 'Makeup',
        "female_options": ['no eyeliner', 'barely there', 'thin subtle liner', 'classic thin cat eye', 'bold cat eye', 'dramatic winged', 'smudged kohl', 'tight-lined waterline', 'graphic editorial liner'],
        "male_options": ['no eyeliner', 'barely there', 'thin subtle liner', 'classic thin cat eye', 'bold cat eye', 'dramatic winged', 'smudged kohl', 'tight-lined waterline', 'graphic editorial liner'],
        "optional": False
    }),
    ("lashes", {
        "group": 'Makeup',
        "female_options": ['natural bare', 'natural mascara', 'volumizing mascara', 'lengthening mascara', 'bold thick mascara', 'wispy false lashes', 'dramatic falsies', 'lash extension look'],
        "male_options": ['natural bare', 'natural mascara', 'volumizing mascara', 'lengthening mascara', 'bold thick mascara', 'wispy false lashes', 'dramatic falsies', 'lash extension look'],
        "optional": False
    }),
    ("contour", {
        "group": 'Makeup',
        "female_options": ['none', 'subtle', 'medium', 'heavy', 'nose contour', 'jawline contour'],
        "male_options": ['none', 'subtle', 'medium', 'heavy', 'nose contour', 'jawline contour'],
        "optional": False
    }),
    ("highlight", {
        "group": 'Makeup',
        # "glistening high points" was "dewy high points" pre-0.41: "dewy" is
        # already owned by makeup_style ("fresh-faced dewy look") and
        # skin_finish ("dewy skin"), and the word doubled in one sentence.
        "female_options": ['none', 'subtle glow', 'glistening high points', 'strobing', 'glitter highlight', 'inner corner'],
        "male_options": ['none', 'subtle glow', 'glistening high points', 'strobing', 'glitter highlight', 'inner corner'],
        "optional": False
    }),
    ("blush", {
        "group": 'Makeup',
        "female_options": ['no blush', 'barely there flush', 'soft pink blush', 'peach blush', 'coral blush', 'rosy blush', 'warm terra cotta', 'bronzed sun-kissed', 'light draping blush', 'heavy editorial blush', 'monochromatic blush and eyeshadow'],
        "male_options": ['no blush', 'barely there flush', 'soft pink blush', 'peach blush', 'coral blush', 'rosy blush', 'warm terra cotta', 'bronzed sun-kissed', 'light draping blush', 'heavy editorial blush', 'monochromatic blush and eyeshadow'],
        "optional": False
    }),
    ("lips_makeup", {
        "group": 'Makeup',
        "female_options": ['bare natural lips', 'tinted lip balm', 'nude lipstick', 'MLBB lipstick', 'coral', 'pink', 'classic red', 'deep red', 'berry', 'plum', 'mauve', 'brown nude', 'dark brown', 'glossy clear', 'high shine gloss', 'ombre lip'],
        "male_options": ['bare natural lips', 'tinted lip balm', 'nude lipstick', 'MLBB lipstick', 'coral', 'pink', 'classic red', 'deep red', 'berry', 'plum', 'mauve', 'brown nude', 'dark brown', 'glossy clear', 'high shine gloss', 'ombre lip'],
        "optional": False
    }),
    ("skin_finish", {
        "group": 'Makeup',
        "female_options": ['matte finish', 'satin finish', 'dewy skin', 'glass skin', 'luminous', 'natural finish', 'full coverage matte', 'sun-kissed glow'],
        "male_options": ['matte finish', 'satin finish', 'dewy skin', 'glass skin', 'luminous', 'natural finish', 'full coverage matte', 'sun-kissed glow'],
        "optional": False
    }),
    ("earrings", {
        "group": 'Jewelry & Nails',
        "female_options": ['no earrings', 'small gold studs', 'small silver studs', 'pearl studs', 'diamond studs', 'small gold hoops', 'medium gold hoops', 'large bold gold hoops', 'silver hoops', 'chandelier earrings', 'long drop earrings', 'tassel earrings', 'mismatched earrings', 'clip-on pearl earrings', 'ear cuff', 'huggie hoops', 'threader earrings'],
        "male_options": ['no earrings', 'small gold studs', 'small silver studs', 'pearl studs', 'diamond studs', 'small gold hoops', 'medium gold hoops', 'large bold gold hoops', 'silver hoops', 'chandelier earrings', 'long drop earrings', 'tassel earrings', 'mismatched earrings', 'clip-on pearl earrings', 'ear cuff', 'huggie hoops', 'threader earrings'],
        "optional": False
    }),
    ("necklace", {
        "group": 'Jewelry & Nails',
        "female_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'nothing but a subtle chain', 'beaded necklace', 'layered pendant necklaces', 'pendant on a leather cord'],
        "male_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'nothing but a subtle chain', 'beaded necklace', 'layered pendant necklaces', 'pendant on a leather cord'],
        "optional": False
    }),
    ("other_jewelry", {
        "group": 'Jewelry & Nails',
        # "Other / body" jewelry only -- rings, bracelets and watches each have their
        # own dedicated field (rings / bracelet / watch_type), so this slot holds just
        # the pieces none of those cover, removing the old triple-sourced ring/watch
        # overlap (a watch could otherwise be asserted by 2-3 fields at once).
        "female_options": ['no other jewelry', 'anklet', 'arm cuff', 'body chain', 'brooch', 'waist chain'],
        "male_options": ['no other jewelry', 'anklet', 'arm cuff', 'body chain', 'brooch', 'waist chain'],
        "optional": False
    }),
    ("piercings", {
        "group": 'Jewelry & Nails',
        "female_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing', 'eyebrow piercing', 'labret stud', 'double nostril piercing', 'medusa piercing'],
        "male_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing', 'eyebrow piercing', 'labret stud', 'double nostril piercing', 'medusa piercing'],
        "optional": True
    }),
    ("nails", {
        "group": 'Jewelry & Nails',
        "female_options": ['bare nails', 'natural short nails', 'neat short nails', 'medium length natural', 'long nails', 'almond nails', 'square nails', 'coffin nails', 'stiletto nails', 'french manicure', 'nude polish', 'red polish', 'coral polish', 'pink polish', 'mauve polish', 'deep burgundy', 'black polish', 'navy polish', 'colorful nail art', 'minimalist nail art', 'chrome nails', 'gel nails'],
        "male_options": ['bare nails', 'natural short nails', 'neat short nails', 'medium length natural', 'long nails', 'almond nails', 'square nails', 'coffin nails', 'stiletto nails', 'french manicure', 'nude polish', 'red polish', 'coral polish', 'pink polish', 'mauve polish', 'deep burgundy', 'black polish', 'navy polish', 'colorful nail art', 'minimalist nail art', 'chrome nails', 'gel nails'],
        "optional": False
    }),
    ("outfit_style", {
        "group": 'Clothing',
        "female_options": ['casual', 'smart casual', 'business casual', 'business formal', 'evening formal', 'cocktail semi-formal', 'streetwear', 'bohemian', 'athletic', 'resort vacation', 'edgy alternative', 'preppy', 'vintage retro', 'loungewear'],
        "male_options": ['casual', 'smart casual', 'business casual', 'business formal', 'evening formal', 'cocktail semi-formal', 'streetwear', 'bohemian', 'athletic', 'resort vacation', 'edgy alternative', 'preppy', 'vintage retro', 'loungewear'],
        "optional": False
    }),
    ("outfit_description", {
        "group": 'Clothing',
        "female_options": ['auto'],
        "male_options": ['auto'],
        "optional": True
    }),
    ("bag", {
        "group": 'Clothing',
        "female_options": ['no bag', 'small black leather crossbody', 'tan leather crossbody', 'structured top handle bag in black', 'structured top handle bag in cream', 'structured top handle bag in tan', 'envelope clutch in black', 'envelope clutch in gold', 'envelope clutch in nude', 'woven rattan bag', 'canvas tote', 'leather tote in black', 'leather tote in tan', 'leather tote in cognac', 'small quilted chain bag', 'saddlebag in brown', 'saddlebag in black', 'saddlebag in cognac', 'belt bag in black', 'belt bag in tan', 'beaded evening clutch', 'velvet evening bag', 'mini backpack in black', 'mini backpack in tan', 'straw beach tote', 'printed silk scarf tied as bag accent'],
        "male_options": ['no bag', 'small black leather crossbody', 'tan leather crossbody', 'structured top handle bag in black', 'structured top handle bag in cream', 'structured top handle bag in tan', 'envelope clutch in black', 'envelope clutch in gold', 'envelope clutch in nude', 'woven rattan bag', 'canvas tote', 'leather tote in black', 'leather tote in tan', 'leather tote in cognac', 'small quilted chain bag', 'saddlebag in brown', 'saddlebag in black', 'saddlebag in cognac', 'belt bag in black', 'belt bag in tan', 'beaded evening clutch', 'velvet evening bag', 'mini backpack in black', 'mini backpack in tan', 'straw beach tote', 'printed silk scarf tied as bag accent'],
        "optional": False
    }),
    ("accessories", {
        "group": 'Clothing',
        # Hair-specific pieces (headbands, scarf-in-hair, hair clip) live in the
        # dedicated ``hair_accessory`` field so they can co-exist with a hat or
        # sunglasses and don't double up against this single clothing slot.
        # Watches live solely in the dedicated watch_type field, so they are not
        # repeated here (a watch was previously sourceable from both this slot and
        # watch_type, over-representing it). Pocket square / statement belt keep variety.
        # No necklace here: the necklace field owns necklaces, so a "long pendant
        # necklace" accessory would double up. Hats/glasses/belts/scarf only.
        "female_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'silk pocket square', 'statement belt', 'reading glasses pushed up on head', 'woven hat'],
        "male_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'silk pocket square', 'statement belt', 'reading glasses pushed up on head', 'woven hat'],
        "optional": False
    }),
    ("expression", {
        "group": 'Setting & Shot',
        "female_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious', 'gentle smile', 'beaming', 'calm and composed', 'at ease', 'steely', 'focused', 'brooding', 'mischievous', 'coy', 'melancholic', 'lost in thought', 'intrigued', 'skeptical', 'quiet amusement', 'daydreaming'],
        "male_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious', 'gentle smile', 'beaming', 'calm and composed', 'at ease', 'steely', 'focused', 'brooding', 'mischievous', 'coy', 'melancholic', 'lost in thought', 'intrigued', 'skeptical', 'quiet amusement', 'daydreaming'],
        "optional": False
    }),
    ("location", {
        "group": 'Setting & Shot',
        "female_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'server room with blinking lights', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace at dusk', 'sandy beach at golden hour', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'desert dune at sunset', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas', 'harbor dock at sunrise', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'street food market at night', 'home office with bookshelves', 'walk-in closet with mirrors', 'ramen shop counter', 'artisan bakery interior', 'flower shop interior', 'vintage camera store', 'indoor spice market stall', 'climbing gym with colorful holds', 'dance studio with mirrors', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium', 'woodworking workshop', "artist's painting studio", 'commercial kitchen', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'alpine meadow with wildflowers', 'salt flats at dusk', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop', 'ceramics studio with pottery wheels', 'rooftop bar at night'],
        "male_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'server room with blinking lights', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace at dusk', 'sandy beach at golden hour', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'desert dune at sunset', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas', 'harbor dock at sunrise', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'street food market at night', 'home office with bookshelves', 'walk-in closet with mirrors', 'ramen shop counter', 'artisan bakery interior', 'flower shop interior', 'vintage camera store', 'indoor spice market stall', 'climbing gym with colorful holds', 'dance studio with mirrors', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium', 'woodworking workshop', "artist's painting studio", 'commercial kitchen', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'alpine meadow with wildflowers', 'salt flats at dusk', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop', 'ceramics studio with pottery wheels', 'rooftop bar at night'],
        "optional": False
    }),
    ("lighting", {
        "group": 'Setting & Shot',
        "female_options": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'soft window light from the side', 'backlit silhouette against bright window', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'warm candlelight', 'warm incandescent lamp glow', 'cool LED overhead lighting', 'harsh fluorescent lighting', 'warm string lights bokeh background', 'neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'stage spotlight from above', 'dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'harsh angled spotlight casting long hard shadows', 'soft-box style diffused light', 'moonlight with cool blue tones', 'fog-diffused streetlamp glow', 'fire and flame warm flicker', 'light through venetian blinds casting stripes', 'light through stained glass casting colors', 'reflection off wet pavement', 'golden bokeh lights in background', 'soft overcast golden light', 'harsh desert sun', 'snow-reflected daylight', 'warm sunlight streaming through a window', 'diffused skylight from above', 'warm lantern light', 'flickering firelight from a hearth', 'purple and teal neon wash', 'colored gel lighting', 'split lighting with deep shadow', 'butterfly beauty lighting', 'Rembrandt lighting', 'flickering television glow in a dark room'],
        "male_options": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'soft window light from the side', 'backlit silhouette against bright window', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'warm candlelight', 'warm incandescent lamp glow', 'cool LED overhead lighting', 'harsh fluorescent lighting', 'warm string lights bokeh background', 'neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'stage spotlight from above', 'dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'harsh angled spotlight casting long hard shadows', 'soft-box style diffused light', 'moonlight with cool blue tones', 'fog-diffused streetlamp glow', 'fire and flame warm flicker', 'light through venetian blinds casting stripes', 'light through stained glass casting colors', 'reflection off wet pavement', 'golden bokeh lights in background', 'soft overcast golden light', 'harsh desert sun', 'snow-reflected daylight', 'warm sunlight streaming through a window', 'diffused skylight from above', 'warm lantern light', 'flickering firelight from a hearth', 'purple and teal neon wash', 'colored gel lighting', 'split lighting with deep shadow', 'butterfly beauty lighting', 'Rembrandt lighting', 'flickering television glow in a dark room'],
        "optional": False
    }),
    ("shot_type", {
        "group": 'Setting & Shot',
        # Every value describes the CAMERA only -- distance, height, subject
        # orientation, or lens. Values that introduce a physical object or a second
        # person into the frame were removed in 0.63.0 ("shot through a doorway /
        # window / foliage", "reflected in a mirror / shop window", and
        # "over-the-shoulder perspective", which in film grammar means the camera
        # sits behind *another person's* shoulder and renders an unwanted second
        # figure). Keeping the field camera-only also removed the need for
        # location<->shot coherence rules: none of these values imply indoors or
        # outdoors. The two rear composites added in 0.63.0 fill the only real gap
        # (rear views existed, low/high angles existed, neither combined).
        # Most values leave subject orientation unstated, which text-to-image models
        # render frontally -- a deliberate, retained bias toward facing the camera.
        "female_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'from behind and slightly below, looking up toward subject', 'from above and behind, looking down toward subject', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
        "male_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'from behind and slightly below, looking up toward subject', 'from above and behind, looking down toward subject', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
        "optional": False
    }),
    ("shoulder_width", {
        "group": 'Body',
        "female_options": ['narrow', 'slightly narrow', 'average', 'broad', 'very broad', 'sloped'],
        "male_options": ['narrow', 'slightly narrow', 'average', 'broad', 'very broad', 'sloped'],
        "optional": False
    }),
    ("neck_length", {
        "group": 'Body',
        "female_options": ['short', 'average', 'long', 'elegant', 'thick', 'slender'],
        "male_options": ['short', 'average', 'long', 'elegant', 'thick', 'slender'],
        "optional": False
    }),
    ("posture", {
        "group": 'Body',
        "female_options": ['slouched', 'relaxed', 'upright', 'rigid', 'confident', 'slightly hunched'],
        "male_options": ['slouched', 'relaxed', 'upright', 'rigid', 'confident', 'slightly hunched'],
        "optional": False
    }),
    ("fitness_level", {
        "group": 'Body',
        "female_options": ['sedentary', 'lightly active', 'moderately fit', 'very fit', 'athletic', 'muscular'],
        "male_options": ['sedentary', 'lightly active', 'moderately fit', 'very fit', 'athletic', 'muscular'],
        "optional": False
    }),
    ("hair_part", {
        "group": 'Hair',
        "female_options": ['center part', 'side part', 'deep side part', 'no part', 'zigzag part', 'diagonal'],
        "male_options": ['center part', 'side part', 'deep side part', 'no part', 'zigzag part', 'diagonal'],
        "optional": False
    }),
    ("hair_highlights", {
        "group": 'Hair',
        "female_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips', 'money piece', 'peekaboo highlights'],
        "male_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips', 'money piece', 'peekaboo highlights'],
        "optional": False
    }),
    ("rings", {
        "group": 'Jewelry & Nails',
        "female_options": ['none', 'simple band', 'stacked thin bands', 'statement ring', 'signet ring', 'delicate gemstone', 'thumb ring', 'midi ring'],
        "male_options": ['none', 'simple band', 'stacked thin bands', 'statement ring', 'signet ring', 'delicate gemstone', 'thumb ring', 'midi ring'],
        "optional": False
    }),
    ("bracelet", {
        "group": 'Jewelry & Nails',
        "female_options": ['none', 'tennis bracelet', 'chain bracelet', 'cuff', 'beaded bracelet', 'charm bracelet', 'bangle stack', 'leather wrap bracelet'],
        "male_options": ['none', 'tennis bracelet', 'chain bracelet', 'cuff', 'beaded bracelet', 'charm bracelet', 'bangle stack', 'leather wrap bracelet'],
        "optional": False
    }),
    ("watch_type", {
        "group": 'Jewelry & Nails',
        "female_options": ['none', 'minimal analog', 'chronograph', 'smart watch', 'vintage leather', 'metal link'],
        "male_options": ['none', 'minimal analog', 'chronograph', 'smart watch', 'vintage leather', 'metal link'],
        "optional": False
    }),
    ("footwear", {
        "group": 'Clothing',
        "female_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'barefoot', 'ankle boots', 'wedges', 'mules'],
        "male_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'barefoot', 'ankle boots', 'wedges', 'mules'],
        "optional": False
    }),
    ("clothing_color", {
        "group": 'Clothing',
        "female_options": ['neutral tones', 'black monochrome', 'white and cream', 'earth tones', 'pastels', 'bold primary colors', 'jewel tones', 'gradient ombre', 'all black', 'all white', 'mixed prints'],
        "male_options": ['neutral tones', 'black monochrome', 'white and cream', 'earth tones', 'pastels', 'bold primary colors', 'jewel tones', 'gradient ombre', 'all black', 'all white', 'mixed prints'],
        "optional": False
    }),
    ("clothing_pattern", {
        "group": 'Clothing',
        "female_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim'],
        "male_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim'],
        "optional": False
    }),
    ("season", {
        "group": 'Setting & Shot',
        "female_options": ['spring', 'summer', 'autumn', 'winter'],
        "male_options": ['spring', 'summer', 'autumn', 'winter'],
        "optional": False
    }),
    ("mood", {
        "group": 'Setting & Shot',
        # Mood is the scene's tone; expression is the face. The two randomize
        # independently, so their vocabularies must not overlap (0.36 renames:
        # playful->carefree, melancholic->sorrowful, confident->self-assured,
        # serene->tranquil, brooding->grim). test_engine enforces disjointness.
        "female_options": ['cheerful', 'sorrowful', 'mysterious', 'self-assured', 'dreamy', 'tense', 'tranquil', 'carefree', 'intense', 'joyful', 'lighthearted', 'somber', 'grim', 'peaceful', 'fierce', 'triumphant', 'enigmatic', 'moody', 'radiant', 'nostalgic', 'restless'],
        "male_options": ['cheerful', 'sorrowful', 'mysterious', 'self-assured', 'dreamy', 'tense', 'tranquil', 'carefree', 'intense', 'joyful', 'lighthearted', 'somber', 'grim', 'peaceful', 'fierce', 'triumphant', 'enigmatic', 'moody', 'radiant', 'nostalgic', 'restless'],
        "optional": False
    }),
    ("pose", {
        "group": 'Setting & Shot',
        # Phrased to read after "{subject} is …"; avoid pronouns so gender stays
        # correct ("a hand", not "their hand").
        "female_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'arms relaxed at the sides', 'one hand touching the collar', 'standing with weight on one leg', 'standing tall with shoulders back', 'perched on the edge of a seat', 'sitting cross-legged', 'leaning forward slightly', 'leaning back casually', 'turning toward the viewer mid-stride', 'stepping forward', 'running one hand through the hair', 'hands loosely clasped together', 'tilting the head slightly', 'lifting the chin slightly'],
        "male_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'arms relaxed at the sides', 'one hand touching the collar', 'standing with weight on one leg', 'standing tall with shoulders back', 'perched on the edge of a seat', 'sitting cross-legged', 'leaning forward slightly', 'leaning back casually', 'turning toward the viewer mid-stride', 'stepping forward', 'running one hand through the hair', 'hands loosely clasped together', 'tilting the head slightly', 'lifting the chin slightly'],
        "optional": True
    }),
    ("held_item", {
        "group": 'Setting & Shot',
        # Hidden field: never randomized and never shown as a widget on the main
        # node (listed in _HIDDEN_FIELDS in nodes/identity_forge.py). It is
        # supplied only by a Cosplayer preset — a character's signature prop, when
        # that node's prop toggle is on — and voiced as "holding <value>". Like
        # outfit_description it carries a placeholder pool so the gender gate
        # (which passes any value when the two pools are identical) always allows
        # the free-text prop through.
        "female_options": ['auto'],
        "male_options": ['auto'],
        "optional": True
    }),
    ("location_setting", {
        "group": 'Setting & Shot',
        # Control toggle: filters the location pool. "Any indoor/outdoor" (the
        # default) draws from every real location but never a studio backdrop, so
        # the default never surprises someone expecting a real scene. "Studio /
        # solid backdrop" forces a plain, easily-maskable background (incl. green
        # screen). See STUDIO_BACKDROPS below and _build_option_pool.
        "female_options": ['Any indoor/outdoor', 'Indoor', 'Outdoor', 'Studio / solid backdrop'],
        "male_options": ['Any indoor/outdoor', 'Indoor', 'Outdoor', 'Studio / solid backdrop'],
        "optional": False,
        "control": True
    }),
])

#: Hair styles grouped into families for weighted random selection. The flat
#: ``hair_style`` option list above still drives the widget (every variant is
#: lockable); this structure only steers the *random* pick. The engine first
#: chooses a family (weighted by ``weight``), then a variant uniformly within it,
#: so adding variants to a family subdivides that family's share instead of
#: inflating it. Each ``weight`` is frozen to the family's original variant count
#: (sum = 30), so the macro distribution matches the pre-families uniform pick;
#: only the within-family split changes as variants are added. The union of all
#: ``variants`` must equal the ``hair_style`` options exactly (checked in tests).
HAIR_STYLE_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("loose", {"weight": 6, "variants": ['worn down', 'slicked back', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled', 'tousled bedhead', 'comb over', 'mullet']}),
    ("half-up", {"weight": 1, "variants": ['half up half down']}),
    ("ponytail", {"weight": 2, "variants": ['high ponytail', 'low ponytail', 'side ponytail', 'braided ponytail']}),
    ("bun", {"weight": 5, "variants": ['messy bun', 'sleek bun', 'top knot', 'chignon', 'updo', 'French twist', 'ballerina bun']}),
    ("braid", {"weight": 9, "variants": ['side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs']}),
    ("knots", {"weight": 2, "variants": ['space buns', 'bantu knots']}),
    ("pigtails", {"weight": 1, "variants": ['pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails']}),
    ("texture", {"weight": 2, "variants": ['afro', 'twist-out']}),
    ("bangs", {"weight": 2, "variants": ['curtain bangs', 'blunt bangs']}),
])

#: hair_color families (0.41): shade neighbourhoods, weights = current family
#: sizes so the pick reproduces the flat uniform draw exactly (sum = 45). The
#: "vivid" family is precisely the set the "Natural only" hair_color_scope
#: filters out, so the conversion is distribution-neutral under both scopes.
#: New colours join their shade family and subdivide its share (no bias).
HAIR_COLOR_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("blonde", {"weight": 7, "variants": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde']}),
    ("red", {"weight": 4, "variants": ['auburn', 'copper', 'bright red', 'deep red']}),
    ("brunette", {"weight": 6, "variants": ['light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown']}),
    ("black", {"weight": 3, "variants": ['near black', 'jet black', 'raven black']}),
    ("gray_white", {"weight": 5, "variants": ['salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair']}),
    # "platinum white" is a fashion shade (full-spectrum only, not in
    # natural_hair_colors) so it lives with the vivids — this keeps every
    # family entirely inside or entirely outside the "Natural only" scope,
    # which is what makes the family pick exactly uniform under both scopes.
    ("vivid", {"weight": 20, "variants": ['hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips']}),
])

#: Weighted families for other large flat fields, following the HAIR_STYLE_FAMILIES
#: contract: the flat option list above still drives the widget (every variant is
#: lockable); these only steer the *random* pick. The engine draws a family
#: (weighted by ``weight``) then a variant uniformly within it, so adding variants
#: to a family subdivides that family's share instead of inflating it -- the
#: bias-safe channel for growing a field. Each ``weight`` is frozen to the family's
#: *original* variant count, so the macro distribution reproduces the old uniform
#: pick exactly and only the within-family split changes as variants are added.
#: The union of every field's family variants must equal that field's option list
#: exactly (enforced for all FIELD_FAMILIES entries by tests/validate_data.py).
EXPRESSION_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("warm", {"weight": 6, "variants": ['subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'candid mid-laugh', 'gentle smile', 'beaming']}),
    ("calm", {"weight": 3, "variants": ['neutral', 'relaxed', 'serene', 'calm and composed', 'at ease']}),
    ("intense", {"weight": 5, "variants": ['serious', 'confident', 'intense gaze', 'determined', 'stern', 'steely', 'focused', 'brooding']}),
    ("playful", {"weight": 5, "variants": ['playful', 'sultry', 'smirking', 'flirtatious', 'slightly bashful', 'mischievous', 'coy', 'quiet amusement']}),
    ("pensive", {"weight": 3, "variants": ['pensive and thoughtful', 'contemplative', 'wistful', 'melancholic', 'lost in thought', 'daydreaming']}),
    ("reactive", {"weight": 2, "variants": ['surprised', 'curious', 'intrigued', 'skeptical']}),
])

MOOD_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    # 0.36 renames (mood vocabulary must stay disjoint from expression's — the
    # two randomize independently): playful->carefree, melancholic->sorrowful,
    # confident->self-assured, serene->tranquil, brooding->grim.
    ("positive", {"weight": 2, "variants": ['cheerful', 'carefree', 'joyful', 'lighthearted', 'radiant']}),
    ("heavy", {"weight": 2, "variants": ['sorrowful', 'tense', 'somber', 'grim', 'restless']}),
    ("calm", {"weight": 2, "variants": ['dreamy', 'tranquil', 'peaceful', 'nostalgic']}),
    ("bold", {"weight": 2, "variants": ['self-assured', 'intense', 'fierce', 'triumphant']}),
    ("enigmatic", {"weight": 1, "variants": ['mysterious', 'enigmatic', 'moody']}),
])

POSE_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("standing", {"weight": 5, "variants": ['standing naturally', 'standing with arms crossed', 'in a relaxed contrapposto stance', 'in a confident power pose', 'arms relaxed at the sides', 'standing with weight on one leg', 'standing tall with shoulders back']}),
    ("seated", {"weight": 5, "variants": ['sitting relaxed', 'sitting upright', 'reclining', 'kneeling gracefully', 'crouching low', 'perched on the edge of a seat', 'sitting cross-legged']}),
    ("leaning", {"weight": 1, "variants": ['leaning against a wall', 'leaning forward slightly', 'leaning back casually']}),
    ("motion", {"weight": 1, "variants": ['walking mid-stride', 'turning toward the viewer mid-stride', 'stepping forward']}),
    ("gesture", {"weight": 4, "variants": ['posing with a hand on one hip', 'posing with hands in pockets', 'resting chin on one hand', 'one hand touching the collar', 'running one hand through the hair', 'hands loosely clasped together']}),
    ("looking", {"weight": 2, "variants": ['looking over one shoulder', 'glancing back', 'tilting the head slightly', 'lifting the chin slightly']}),
])

#: 0.65.0: the `studio` family's former `'Dutch angle with hard shadows'` mixed a pure
#: camera concept (Dutch angle = frame tilt) into a lighting field -- the same class of
#: wart the 0.63.0 shot_type camera-only doctrine would have caught there. Reworded to
#: `'harsh angled spotlight casting long hard shadows'` (light direction, not camera
#: framing) in the SAME slot at the SAME family weight -- zero bias impact, no field
#: pool or weight change. Migrating it into shot_type instead was considered and
#: rejected: that changes shot_type's own pool/weights, the exact risk flagged in 0.63.
LIGHTING_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("daylight", {"weight": 14, "variants": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'moonlight with cool blue tones', 'soft overcast golden light', 'harsh desert sun', 'snow-reflected daylight']}),
    ("window", {"weight": 4, "variants": ['soft window light from the side', 'backlit silhouette against bright window', 'light through venetian blinds casting stripes', 'light through stained glass casting colors', 'warm sunlight streaming through a window', 'diffused skylight from above']}),
    ("artificial", {"weight": 6, "variants": ['warm candlelight', 'warm incandescent lamp glow', 'cool LED overhead lighting', 'harsh fluorescent lighting', 'warm string lights bokeh background', 'fire and flame warm flicker', 'warm lantern light', 'flickering firelight from a hearth', 'flickering television glow in a dark room']}),
    ("neon", {"weight": 6, "variants": ['neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'fog-diffused streetlamp glow', 'reflection off wet pavement', 'golden bokeh lights in background', 'purple and teal neon wash', 'colored gel lighting']}),
    ("studio", {"weight": 8, "variants": ['stage spotlight from above', 'dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'harsh angled spotlight casting long hard shadows', 'soft-box style diffused light', 'split lighting with deep shadow', 'butterfly beauty lighting', 'Rembrandt lighting']}),
])

LOCATION_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("domestic", {"weight": 24, "variants": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'cozy home library', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'home office with bookshelves', 'walk-in closet with mirrors']}),
    ("food_drink", {"weight": 15, "variants": ['elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'ramen shop counter', 'artisan bakery interior']}),
    ("retail_services", {"weight": 16, "variants": ['neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'flower shop interior', 'vintage camera store', 'indoor spice market stall']}),
    ("leisure_fitness", {"weight": 11, "variants": ['local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'climbing gym with colorful holds', 'dance studio with mirrors', 'ceramics studio with pottery wheels']}),
    ("civic_institutional", {"weight": 17, "variants": ['university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'police station bullpen', 'courtroom', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium']}),
    ("work_industrial", {"weight": 7, "variants": ['corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'server room with blinking lights', 'factory floor', 'warehouse interior', 'woodworking workshop', "artist's painting studio", 'commercial kitchen']}),
    ("transit_travel", {"weight": 7, "variants": ['hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge']}),
    ("urban_outdoor", {"weight": 20, "variants": ['sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace at dusk', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas', 'harbor dock at sunrise', 'riverside boardwalk', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'street food market at night', 'crumbling stone ruin', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'rooftop bar at night']}),
    ("nature_outdoor", {"weight": 15, "variants": ['sandy beach at golden hour', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'desert dune at sunset', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'alpine meadow with wildflowers', 'salt flats at dusk', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees']}),
    ("studio", {"weight": 4, "variants": ['seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop']}),
])

#: Registry of every field that uses the weighted two-tier random pick. Keyed by
#: field name; ``hair_style`` reuses the long-standing HAIR_STYLE_FAMILIES object.
#: The engine (_pick_family_weighted) looks fields up here; absence means the
#: field uses a flat uniform rng.choice as before.
FIELD_FAMILIES: OrderedDict[str, OrderedDict[str, dict]] = OrderedDict([
    ("hair_style", HAIR_STYLE_FAMILIES),
    ("hair_color", HAIR_COLOR_FAMILIES),
    ("expression", EXPRESSION_FAMILIES),
    ("mood", MOOD_FAMILIES),
    ("pose", POSE_FAMILIES),
    ("lighting", LIGHTING_FAMILIES),
    ("location", LOCATION_FAMILIES),
])

#: Outfit descriptions keyed by outfit_style, split into gendered buckets.
#: The engine draws from ``unisex`` plus the bucket(s) selected by the wardrobe
#: control, so a black-tie gown never lands on a male subject by default — yet a
#: user can deliberately mix wardrobes for diversity.
OUTFIT_DESCRIPTIONS: dict[str, dict[str, list[str]]] = {
    "casual": {
        "female": ['cropped hoodie with high waisted joggers and running shoes', 'fitted ribbed tank with mom jeans and white sneakers', 'oversized cream sweater with high waisted straight leg jeans and canvas sneakers', 'flowy floral sundress with white sneakers and a denim jacket', 'cropped cardigan over a camisole with wide leg jeans and loafers', 'striped boatneck tee with cuffed chinos and slip-on sneakers'],
        "male": ['plaid flannel shirt with dark jeans and brown leather boots', 'striped long sleeve shirt with navy chinos and clean white sneakers', 'relaxed linen button-up with khaki shorts and leather sandals', 'henley shirt with corduroy pants and desert boots', 'crewneck sweatshirt with slim jeans and skate shoes', 'zip-up fleece over a plain tee with tapered joggers and trail sneakers'],
        "unisex": ['white fitted tee with light wash jeans, white sneakers, and a denim jacket', 'black graphic tee with distressed jeans and chunky boots', 'vintage band tee with cutoff shorts and combat boots', 'denim overalls over a fitted long sleeve with canvas sneakers'],
    },
    "smart casual": {
        "female": ['structured blazer over a silk blouse with straight leg trousers and pointed flats', 'patterned midi dress with a cropped blazer and ankle boots', 'wrap blouse with a pencil skirt and block heel pumps', 'fine-knit turtleneck with pleated trousers and loafers', 'sleeveless mock-neck top with tapered ankle trousers and mules'],
        "male": ['fitted navy blazer over a white oxford shirt with dark chinos and brown loafers', 'charcoal merino sweater over a collared shirt with tailored trousers and derby shoes', 'light blue button-down with tan chinos and suede loafers', 'tailored vest over a crisp white tee with wide leg trousers and loafers', 'unstructured cotton blazer over a merino polo with slim trousers and suede derbies'],
        "unisex": ['cream knit polo with high waisted trousers and minimal leather sneakers', 'chambray shirt with tailored shorts and leather sandals'],
    },
    "business casual": {
        "female": ['fitted sheath dress with a thin belt and closed toe pumps', 'cardigan over a silk blouse with a knee length pencil skirt and low heels', 'patterned blouse tucked into an a-line skirt with modest heels', 'shift dress with a cropped jacket and classic pumps', 'tie-neck blouse with tailored cigarette trousers and pointed flats'],
        "male": ['navy blazer, light blue dress shirt, charcoal dress pants, and black leather loafers', 'gray trousers, white oxford, and burgundy loafers', 'turtleneck under a structured blazer with slim trousers and leather oxfords', 'dress shirt with cuffed sleeves, dark jeans, a leather belt, and loafers', 'houndstooth sport coat with an open-collar shirt, gray chinos, and monk strap shoes'],
        "unisex": ['tailored blazer with ankle length trousers and pointed toe flats', 'ponte blazer with matching trousers and minimal sneakers'],
    },
    "business formal": {
        "female": ['tailored black blazer and matching trousers with a silk blouse and closed toe pumps', 'navy pencil skirt suit with a cream shell top and pumps', 'double breasted blazer with wide leg trousers and a silk camisole', 'fitted black dress with a structured blazer, sheer tights, and pumps', 'ivory silk blouse with a high waisted skirt suit and slingback pumps'],
        "male": ['black two piece suit with a white dress shirt, silk tie, and black oxfords', 'navy pinstripe suit with a pale blue shirt, burgundy tie, and brown oxfords', 'charcoal suit with a white spread collar shirt and black cap toe shoes', 'light gray suit with a white shirt, navy tie, and brown brogues', 'deep green flannel suit with a white shirt, knit tie, and black oxfords'],
        "unisex": ['subtle houndstooth suit with a white shirt and dark tie', 'sharp black suit with a crisp white shirt and minimal accessories'],
    },
    "evening formal": {
        "female": ['floor length black velvet gown with delicate straps and diamond stud earrings', 'emerald green satin slip gown with strappy gold heels and a clutch', 'burgundy floor length dress with a deep v back and chandelier earrings', 'champagne sequined evening gown with a satin wrap and stiletto sandals', 'navy ball gown with a structured bodice, full skirt, and pearl drop earrings', 'off shoulder ruby mermaid gown with long satin gloves'],
        "male": ['classic black tuxedo with a crisp white shirt and black silk bow tie', 'midnight blue tuxedo with black satin lapels and patent leather shoes', 'white tie tailcoat with a wing collar shirt, white bow tie, and opera pumps', 'charcoal three piece suit with a black tie and oxford shoes', 'ivory dinner jacket with black trousers and a black bow tie', 'burgundy velvet dinner jacket with black trousers and a black bow tie'],
        "unisex": ['sleek black formal ensemble with satin detailing and polished dress shoes', 'tailored ivory evening suit with a silk shirt and patent shoes'],
    },
    "cocktail semi-formal": {
        "female": ['little black cocktail dress with lace overlay and black heels', 'burgundy wrap dress with gold hoop earrings and strappy heels', 'metallic midi dress with a draped neckline and minimalist sandals', 'deep green velvet wrap dress with a gold pendant necklace', 'sequined top with high waisted trousers and pointed heels', 'one shoulder cobalt satin dress with a thigh slit and silver heels'],
        "male": ['navy tailored suit with a light gray shirt and no tie', 'charcoal blazer with black dress pants and an open collar white shirt', 'black dress shirt with dark jeans and Chelsea boots', 'burgundy blazer over a black tee with tailored trousers and loafers', 'light gray double breasted blazer with a black turtleneck and tailored trousers'],
        "unisex": ['fitted blazer with a silk camisole and leather pants with heeled boots', 'white blazer over a pastel sheath with nude shoes'],
    },
    "streetwear": {
        "female": ['puffer jacket over a cropped top with biker shorts and platform sneakers', 'mesh top under a sports bra with baggy jeans and statement sneakers', 'oversized graphic tee dress with chunky sneakers and a crossbody bag', 'cropped bomber over a bralette with cargo pants and high tops', 'color-blocked windbreaker with a pleated tennis skirt and retro sneakers'],
        "male": ['oversized hoodie with cargo pants and chunky sneakers', 'bomber jacket with a plain tee, ripped jeans, and skate shoes', 'boxy graphic tee with wide leg jeans, high top sneakers, and a chain necklace', 'baseball jersey over a turtleneck with loose jeans and bold sneakers', 'longline tee under an open flannel shirt with tapered cargos and chunky retro sneakers'],
        "unisex": ['distressed denim jacket over a hoodie with joggers and retro sneakers', 'bucket hat, oversized sweatshirt, track pants, and designer sneakers', 'utility vest with layered long sleeves, tactical pants, and combat boots'],
    },
    "bohemian": {
        "female": ['flowing floral maxi dress with bell sleeves, leather sandals, and layered necklaces', 'off shoulder ruffled top with a tiered maxi skirt and leather sandals', 'crochet top with high waisted wide leg pants, a woven belt, and ankle boots', 'velvet burnout maxi dress with a wide brim hat and layered rings', 'embroidered peasant blouse with distressed denim shorts and gladiator sandals', 'smocked prairie dress with tooled leather boots and turquoise jewelry'],
        "male": ['embroidered linen tunic with drawstring trousers and leather sandals', 'open paisley shirt over a henley with flared cords and suede boots', 'fringed suede jacket over a plain tee with relaxed jeans and boots', 'collarless linen tunic shirt with rolled trousers and huarache sandals'],
        "unisex": ['kimono cardigan over a slip top with a fringe bag and beaded jewelry', 'patchwork layers with stacked bangles and hoop earrings', 'tie dye tee with flowy palazzo pants and espadrilles'],
    },
    "athletic": {
        "female": ['fitted sports bra with high waisted leggings, running shoes, and a zip hoodie', 'tennis skirt with a polo shirt, court shoes, and a visor', 'yoga pants with a cropped tank and grip socks', 'racerback tank with bike shorts and cross training shoes', 'one shoulder seamless top with flared leggings and lifting shoes'],
        "male": ['moisture wicking tank with athletic shorts, trainers, and a sweatband', 'compression top with fitted shorts and cross training shoes', 'gym tee with basketball shorts, a baseball cap, and athletic sneakers', 'boxing tank with compression shorts and high top sneakers', 'quarter-zip running top with split shorts and racing flats'],
        "unisex": ['tracksuit jacket with matching joggers and running shoes', 'windbreaker with leggings and trail running shoes', 'performance hoodie with joggers and cushioned trainers'],
    },
    "resort vacation": {
        "female": ['strapless floral sundress with a wide brim sun hat and wedge espadrilles', 'maxi skirt with a halter top, gold sandals, and a woven bag', 'sarong wrap with a bandeau swimsuit and shell jewelry', 'crochet cover up over a one piece swimsuit with a straw hat', 'off shoulder linen midi dress with flat leather sandals'],
        "male": ['linen camp shirt with tailored swim trunks and leather sandals', 'polo shirt with chino shorts and boat shoes', 'tropical print shirt with relaxed trousers and canvas slip ons', 'open linen shirt over swim trunks with espadrilles', 'terry cloth polo with pleated shorts and woven loafers'],
        "unisex": ['white linen button-up with high waisted shorts and leather sandals', 'lightweight jumpsuit with open weave sandals', 'breton stripe tee with white jeans and leather sandals'],
    },
    "edgy alternative": {
        "female": ['fishnet top under a slip dress with platform boots and a choker', 'corset top with a plaid skirt and thigh high boots', 'mesh long sleeve under a crop top with vinyl pants and combat boots', 'motorcycle jacket over a sheer blouse with leather pants and ankle boots', 'harness top over a mesh tee with a bleached denim mini skirt and creepers'],
        "male": ['black leather jacket over a band tee with ripped skinny jeans and combat boots', 'distressed black denim jacket with studded patches and black jeans', 'oversized black hoodie with chains, cargo pants, and chunky boots', 'graphic tee with a tartan kilt, fishnet sleeves, and boots', 'long black trench coat over a mesh tank with waxed jeans and steel toe boots'],
        "unisex": ['denim vest with band patches, frayed shorts, and a studded belt', 'black turtleneck with suspenders and platform loafers'],
    },
    "preppy": {
        "female": ['pleated tennis skirt with a cable knit sweater and leather loafers', 'gingham shirt dress with a headband and ballet flats', 'navy blazer with a pleated skirt, knee socks, and oxfords', 'collared blouse under a sweater vest with tailored shorts and loafers', 'belted shirtdress with a silk scarf, cardigan, and riding boots'],
        "male": ['polo shirt with a sweater tied over the shoulders, chinos, and boat shoes', 'oxford shirt under a quarter-zip pullover with chinos and loafers', 'navy blazer with a gingham shirt, khakis, and penny loafers', 'striped rugby shirt with tailored shorts and deck shoes', 'seersucker blazer with a pastel oxford shirt, white chinos, and loafers'],
        "unisex": ['argyle sweater vest over a collared shirt with chinos and loafers', 'crisp white polo with pressed khakis and clean leather sneakers'],
    },
    "vintage retro": {
        "female": ['1950s polka dot swing dress with a cinched waist and kitten heels', 'high waisted mom jeans with a tucked-in striped tee and cat eye sunglasses', '1970s flared corduroys with a fitted turtleneck and platform boots', 'tea length floral dress with a cardigan and Mary Jane shoes', '1960s mod shift dress with white go-go boots and a headband'],
        "male": ['1950s rolled-cuff jeans with a white tee, leather jacket, and loafers', 'tweed jacket with a knit tie, high waisted trousers, and brogues', '1970s wide collar shirt with flared trousers and suede boots', 'bowling shirt with cuffed chinos and canvas sneakers', '1940s pleated trousers with a tucked work shirt, suspenders, and cap toe boots'],
        "unisex": ['high waisted trousers with suspenders, a tucked button-down, and oxfords', 'retro track jacket with slim trousers and vintage trainers'],
    },
    "loungewear": {
        "female": ['matching ribbed knit lounge set with fuzzy slippers', 'oversized sweater dress with cozy socks', 'soft camisole with drawstring lounge pants and a robe', 'cropped sweatshirt with matching joggers and slides', 'satin pajama set with plush slippers'],
        "male": ['waffle-knit henley with soft sweatpants and slippers', 'plain crewneck with relaxed lounge pants and slides', 'zip hoodie with jersey shorts and house slippers', 'thermal long sleeve with plaid flannel pants and wool socks'],
        "unisex": ['oversized hoodie with matching sweatpants and thick socks', 'flannel pajama set with a robe and slippers', 'soft tee with cuffed sweatpants and bare feet', 'chunky knit cardigan over a soft tee with fleece joggers and slipper socks'],
    },
}


# --- Ethnicity-aware skin-tone affinity (a soft bias, not a hard rule) -------
# Real-world skin tone spans a wide range within every ethnicity, so this only
# *biases* random skin_tone toward a plausible band for the chosen ethnicity
# (see SKIN_TONE_INBAND_PROBABILITY in the engine). The full spectrum stays
# possible, and locking skin_tone overrides the bias entirely.
SKIN_TONE_BANDS: dict[str, list[str]] = {
    "fair": ['porcelain', 'very pale', 'pale', 'fair', 'light', 'light medium', 'medium'],
    "olive": ['fair', 'light', 'light medium', 'medium', 'medium olive', 'olive', 'warm tan', 'tan'],
    "tan": ['light', 'light medium', 'medium', 'medium olive', 'olive', 'warm tan', 'tan', 'golden tan', 'bronze', 'caramel'],
    "brown": ['medium olive', 'olive', 'warm tan', 'tan', 'golden tan', 'bronze', 'caramel', 'brown', 'warm brown', 'dark brown'],
    "dark": ['caramel', 'brown', 'warm brown', 'dark brown', 'deep', 'ebony', 'deep ebony'],
}

#: Maps each ethnicity to a skin-tone band above. Approximate and intentionally
#: generous/overlapping; intended only to avoid jarring defaults (e.g. an Irish
#: subject rendered with deep ebony skin), never to pin an exact shade.
ETHNICITY_REGION: dict[str, str] = {
    # Northern / Eastern European
    "Austrian": "fair", "Croatian": "fair", "Czech": "fair",
    "Danish": "fair", "Dutch": "fair", "English": "fair",
    "Finnish": "fair", "German": "fair", "Hungarian": "fair",
    "Icelandic": "fair", "Irish": "fair", "Norwegian": "fair",
    "Polish": "fair", "Russian": "fair", "Scottish": "fair",
    "Serbian": "fair", "Swedish": "fair", "Ukrainian": "fair",
    "Welsh": "fair",
    # Mediterranean / Middle Eastern / Caucasus
    "Afghan": "olive", "Armenian": "olive", "French": "olive",
    "Georgian": "olive", "Greek": "olive", "Iranian": "olive",
    "Iraqi": "olive", "Israeli": "olive", "Italian": "olive",
    "Kazakh": "olive", "Lebanese": "olive", "Palestinian": "olive",
    "Portuguese": "olive", "Romani": "olive", "Romanian": "olive",
    "Spanish": "olive", "Syrian": "olive", "Turkish": "olive",
    # North African / South Asian / Gulf
    "Bangladeshi": "brown", "Berber": "brown", "Egyptian": "brown",
    "Indian": "brown", "Moroccan": "brown", "Nepali": "brown",
    "Pakistani": "brown", "Saudi": "brown", "Sri Lankan": "brown",
    "Sudanese": "brown", "Yemeni": "brown",
    # East & SE Asian / Pacific / Latin American / Indigenous
    "Argentinian": "tan", "Bolivian": "tan", "Brazilian": "tan",
    "Burmese": "tan", "Cambodian": "tan", "Chilean": "tan",
    "Chinese": "tan", "Colombian": "tan", "Cuban": "tan",
    "Dominican": "tan", "Filipino": "tan", "Guatemalan": "tan",
    "Hawaiian": "tan", "Indonesian": "tan", "Inuit": "tan",
    "Japanese": "tan", "Korean": "tan", "Laotian": "tan",
    "Malaysian": "tan", "Maori": "tan", "Mexican": "tan",
    "Mongolian": "tan", "Native American": "tan", "Peruvian": "tan",
    "Puerto Rican": "tan", "Samoan": "tan", "Singaporean": "tan",
    "Taiwanese": "tan", "Thai": "tan", "Tibetan": "tan",
    "Venezuelan": "tan", "Vietnamese": "tan",
    # Sub-Saharan African and diaspora
    "Aboriginal Australian": "dark", "Congolese": "dark", "Ethiopian": "dark",
    "Fijian": "dark", "Ghanaian": "dark", "Haitian": "dark",
    "Jamaican": "dark", "Kenyan": "dark", "Nigerian": "dark",
    "Senegalese": "dark", "Somali": "dark", "South African": "dark",
}


#: Locations that are outdoors (everything else in the pool is indoor).
OUTDOOR_LOCATIONS: frozenset[str] = frozenset([
    'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street',
    'rooftop terrace at dusk', 'sandy beach at golden hour', 'rocky coastal cliff',
    'forest trail', 'mountain overlook', 'desert dune at sunset',
    'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom',
    'sunlit vineyard', 'lavender field', 'quiet suburban backyard',
    'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas',
    'harbor dock at sunrise', 'riverside boardwalk', 'botanical garden path',
    'open meadow', 'lakeside pier', 'misty moor',
    'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden',
    'busy city crosswalk', 'country dirt road', 'palm-lined promenade',
    'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater',
    'poolside cabana', 'street food market at night', 'rooftop bar at night',
    'pedestrian shopping street', 'graffiti-covered skate park',
    'harbor with moored boats', 'alpine meadow with wildflowers',
    'salt flats at dusk', 'mangrove boardwalk', 'bamboo forest path',
    'tide pools at low tide', 'golden savanna with acacia trees',
])


#: Plain, easily-maskable backgrounds. Only reachable when the location_setting
#: control is "Studio / solid backdrop"; filtered *out* of every other mode so a
#: studio never appears unless explicitly chosen. Includes a chroma-key green
#: screen for masking and solid white / black sweeps.
STUDIO_BACKDROPS: frozenset[str] = frozenset([
    'seamless grey studio backdrop', 'solid white studio backdrop',
    'solid black studio backdrop', 'chroma-key green screen backdrop',
])


# --- location <-> lighting coherence buckets ---------------------------------
# Real renders paired "indoor spice market stall" with "dappled sunlight through
# forest canopy", and "palm-lined promenade" with "warm sunlight streaming
# through a window". Unlike shot_type -- which 0.63.0 made camera-only, deleting
# the incoherence at the source -- light quality is genuinely tied to whether you
# are indoors, so the field cannot be scrubbed of place the way shot_type was.
# data/constraints.py turns these three buckets into generated exclusion rules.
#
# The split follows the seam LIGHTING_FAMILIES already encodes, which is what
# keeps it bias-clean: the ``daylight`` family is open-sky light and the
# ``window`` family IS indoor daylight. Bucketing whole families means a filtered
# family drops out entirely and the remaining families' shares stay exactly
# proportional, instead of one family keeping its full weight while concentrated
# onto two or three surviving variants. Only the mixed ``artificial`` and ``neon``
# families contribute individual values, and each keeps a clear majority of its
# variants in both directions.

#: Lighting that asserts open sky, weather, or an exterior fixture. Excluded when
#: the location is indoors -- indoor daylight is what the ``window`` family is for.
#: The whole ``daylight`` family, plus the two exterior-fixture ``neon`` values.
OUTDOOR_ONLY_LIGHTING: frozenset[str] = frozenset([
    'golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light',
    'harsh overhead midday sun', 'overcast diffused daylight',
    'hazy overcast winter light', 'blue hour twilight',
    'pre-dawn darkness with ambient glow', 'dramatic stormy sky light',
    'sun rays through broken cloud cover', 'dappled sunlight through forest canopy',
    'direct sunlight from behind camera', 'rim lighting from setting sun',
    'moonlight with cool blue tones', 'soft overcast golden light',
    'harsh desert sun', 'snow-reflected daylight',
    'fog-diffused streetlamp glow', 'reflection off wet pavement',
])

#: Lighting that asserts a built interior: a window or skylight you are looking
#: *out* of, a ceiling fixture, a hearth, a television in a room. Excluded when
#: the location is outdoors. The whole ``window`` family plus four ``artificial``
#: values; the other five artificial values (candle, lamp, string lights, open
#: flame, lantern) read fine on a patio or at a campfire and stay available.
INDOOR_ONLY_LIGHTING: frozenset[str] = frozenset([
    'soft window light from the side', 'backlit silhouette against bright window',
    'light through venetian blinds casting stripes',
    'light through stained glass casting colors',
    'warm sunlight streaming through a window', 'diffused skylight from above',
    'cool LED overhead lighting', 'harsh fluorescent lighting',
    'flickering firelight from a hearth', 'flickering television glow in a dark room',
])

#: The only lighting a void backdrop may draw: the ``studio`` family, exactly.
#: A seamless sweep is a studio, so it gets studio light. Restricting to one whole
#: family is also the bias-safe choice -- admitting a few neon/gel values would
#: hand the eight-variant ``neon`` family its full weight concentrated onto the
#: two or three survivors, spiking those individual values far above the studio
#: ones. Void backdrops are a subset of the indoor bucket; this rule is simply
#: stricter, and the two rules coexist (the engine cascades to a fixed point).
VOID_ALLOWED_LIGHTING: frozenset[str] = frozenset([
    'stage spotlight from above', 'dramatic single overhead spotlight',
    'soft studio three-point lighting', 'high key bright even lighting',
    'low key moody single light source', 'dramatic chiaroscuro side lighting',
    'harsh angled spotlight casting long hard shadows', 'soft-box style diffused light',
    'split lighting with deep shadow', 'butterfly beauty lighting',
    'Rembrandt lighting',
])


# Merge optional user-supplied options (./user_options.json in the pack root).
# Kept last so it can extend any pool above; fails closed if absent/malformed.
# OUTFIT_DESCRIPTIONS is passed so the "outfits" section can register new outfit
# styles together with their garment text.
from .user_options import apply_user_options  # noqa: E402

apply_user_options(FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS)
