"""Field definitions and option pools for IdentityForge."""
from __future__ import annotations

from collections import OrderedDict
import re

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
        # ``natural_hair_colors`` is the ONLY extra key the engine reads here: the
        # "Natural only" hair_color_scope filters the randomization pool through it
        # (_build_option_pool). It is a subset of the option pool, and the filter
        # fails OPEN if the key ever goes missing (no key = no filter = full
        # spectrum), so validate_data.py pins both its presence and its membership.
        # A "full_spectrum_hair_colors" twin shipped here until 0.91.1 and was read
        # by nothing -- the full spectrum IS the option pool. Do not re-add it.
        "group": 'Hair',
        "female_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "male_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "optional": False, "natural_hair_colors": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair']
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
        "female_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled', 'tousled bedhead', 'ballerina bun', 'braided ponytail', 'fade', 'undercut', 'pompadour', 'quiff', 'shag', 'milkmaid braids', 'rope braid', 'braided bun', 'two-strand twists', 'bubble ponytail', 'micro bangs', 'hair puff', 'crew cut', 'textured crop', 'high-top fade',
                            'side-swept bangs', 'wispy bangs'],
        "male_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled', 'tousled bedhead', 'ballerina bun', 'braided ponytail', 'comb over', 'mullet', 'fade', 'undercut', 'pompadour', 'quiff', 'shag', 'milkmaid braids', 'rope braid', 'braided bun', 'two-strand twists', 'bubble ponytail', 'micro bangs', 'hair puff', 'crew cut', 'textured crop', 'high-top fade',
                            'side-swept bangs', 'wispy bangs'],
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
        "female_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'subtle chain', 'beaded necklace', 'layered pendant necklaces', 'pendant on a leather cord'],
        "male_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'subtle chain', 'beaded necklace', 'layered pendant necklaces', 'pendant on a leather cord'],
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
        "female_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing', 'eyebrow piercing', 'labret stud', 'double nostril piercing', 'medusa piercing', 'stretched lobes'],
        "male_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing', 'eyebrow piercing', 'labret stud', 'double nostril piercing', 'medusa piercing', 'stretched lobes'],
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
        "female_options": ['no bag', 'small black leather crossbody', 'tan leather crossbody', 'structured top handle bag in black', 'structured top handle bag in cream', 'structured top handle bag in tan', 'envelope clutch in black', 'envelope clutch in gold', 'envelope clutch in nude', 'woven rattan bag', 'canvas tote', 'leather tote in black', 'leather tote in tan', 'leather tote in cognac', 'small quilted chain bag', 'saddlebag in brown', 'saddlebag in black', 'saddlebag in cognac', 'belt bag in black', 'belt bag in tan', 'beaded evening clutch', 'velvet evening bag', 'mini backpack in black', 'mini backpack in tan', 'straw beach tote', 'printed silk scarf tied as bag accent', 'leather briefcase in black', 'canvas messenger bag', 'canvas duffel bag'],
        "male_options": ['no bag', 'small black leather crossbody', 'tan leather crossbody', 'structured top handle bag in black', 'structured top handle bag in cream', 'structured top handle bag in tan', 'envelope clutch in black', 'envelope clutch in gold', 'envelope clutch in nude', 'woven rattan bag', 'canvas tote', 'leather tote in black', 'leather tote in tan', 'leather tote in cognac', 'small quilted chain bag', 'saddlebag in brown', 'saddlebag in black', 'saddlebag in cognac', 'belt bag in black', 'belt bag in tan', 'beaded evening clutch', 'velvet evening bag', 'mini backpack in black', 'mini backpack in tan', 'straw beach tote', 'printed silk scarf tied as bag accent', 'leather briefcase in black', 'canvas messenger bag', 'canvas duffel bag'],
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
        "female_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'silk pocket square', 'statement belt', 'reading glasses pushed up on head', 'woven hat', 'leather gloves', 'long opera gloves', 'fingerless gloves', 'suspenders', 'flat cap', 'bucket hat', 'wool beanie', 'lapel pin', 'clear-framed glasses', 'round wire-rim eyeglasses', 'cat-eye eyeglasses', 'browline eyeglasses'],
        "male_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'silk pocket square', 'statement belt', 'reading glasses pushed up on head', 'woven hat', 'leather gloves', 'long opera gloves', 'fingerless gloves', 'suspenders', 'flat cap', 'bucket hat', 'wool beanie', 'lapel pin', 'clear-framed glasses', 'round wire-rim eyeglasses', 'cat-eye eyeglasses', 'browline eyeglasses'],
        # 0.90.0 added three everyday eyeglass frames, closing a gap the archetype
        # conventions had been working around ("everyday eyeglasses aren't an
        # accessories option -- put them in costume prose instead"). Straight
        # appending would have taken the EYEWEAR CONCEPT from 6/24 (25%) of the pool
        # to 9/27 (33%). This field has no FIELD_FAMILIES entry, so no family-share
        # check would have caught that -- it is the same trap documented for the
        # landmark locations, where every family share held and the concept still got
        # commoner. These weights hold all nine eyewear values at a combined
        # 6/24 = 25%: 18 non-eyewear at 1.0 plus 9 eyewear at 2/3 = 6.0. Variety
        # triples; the odds of a character wearing glasses do not move.
        "weights": {'classic black sunglasses': 2/3, 'cat eye sunglasses': 2/3,
                    'round sunglasses': 2/3, 'aviator sunglasses': 2/3,
                    'reading glasses pushed up on head': 2/3,
                    'clear-framed glasses': 2/3, 'round wire-rim eyeglasses': 2/3,
                    'cat-eye eyeglasses': 2/3, 'browline eyeglasses': 2/3},
        "optional": False
    }),
    ("expression", {
        "group": 'Setting & Shot',
        "female_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious', 'gentle smile', 'beaming', 'calm and composed', 'at ease', 'steely', 'focused', 'brooding', 'mischievous', 'coy', 'melancholic', 'lost in thought', 'intrigued', 'skeptical', 'quiet amusement', 'daydreaming', 'delighted', 'quietly content', 'defiant', 'sly', 'solemn', 'unimpressed'],
        "male_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious', 'gentle smile', 'beaming', 'calm and composed', 'at ease', 'steely', 'focused', 'brooding', 'mischievous', 'coy', 'melancholic', 'lost in thought', 'intrigued', 'skeptical', 'quiet amusement', 'daydreaming', 'delighted', 'quietly content', 'defiant', 'sly', 'solemn', 'unimpressed'],
        "optional": False
    }),
    ("location", {
        "group": 'Setting & Shot',
        "female_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'mission control room with monitor banks', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace overlooking the skyline', 'wide sandy beach', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'rolling desert dune', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street', 'rainy street with umbrellas', 'working harbor dock', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'open-air street food market', 'home office with bookshelves', 'walk-in closet with mirrors', 'ramen shop counter', 'artisan bakery interior', 'flower shop interior', 'vintage camera store', 'indoor spice market stall', 'climbing gym with colorful holds', 'dance studio with mirrors', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium', 'woodworking workshop', "artist's painting studio", 'commercial kitchen', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'alpine meadow with wildflowers', 'cracked salt flats', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop', 'ceramics studio with pottery wheels', 'rooftop cocktail bar', 'gastropub with an open kitchen', 'tea house with low wooden tables', 'old-fashioned ice cream parlor', 'hardware store aisle', 'butcher shop counter', 'garden centre greenhouse aisle', 'bicycle repair shop', 'neighborhood dry cleaner counter', 'arcade with glowing cabinets', 'independent cinema auditorium', 'billiards hall', 'martial arts dojo', 'university chemistry laboratory', 'veterinary clinic exam room', 'city hall rotunda', 'community theatre auditorium', 'auto repair shop service bay', 'print shop with running presses', 'machine shop with lathes', 'brewery tank room', 'ferry terminal waiting hall', 'hotel conference room', 'long-distance bus station', 'the Brooklyn Bridge pedestrian walkway', 'Trafalgar Square', 'the Spanish Steps in Rome', 'the Griffith Observatory terrace', 'red rock desert arch', 'slot canyon with striated walls', 'geothermal geyser basin', 'redwood grove with towering trunks', 'alpine glacier lake', 'coastal lighthouse bluff', 'waterfall plunge pool', 'volcanic black sand beach', 'moss-draped rainforest trail', 'the Grand Canyon south rim', 'a Yosemite valley meadow', 'a Zion canyon riverbank', 'tidy bedroom with a neatly made bed', 'tiled bathroom with a large mirror', 'laundry room with stacked machines', 'narrow hallway lined with family photos', "children's playroom with toy bins", 'music room with an upright piano', 'bustling food court', 'taqueria with a tiled counter', 'French bistro with mirrored walls', 'juice bar with a chrome counter', 'barbecue joint with paper-lined trays', 'shopping mall concourse', 'bank lobby with teller windows', 'pet shop lined with aquariums', 'department store perfume counter', 'stationery and art supply shop', 'shoe repair and key cutting counter', 'boxing gym with hanging heavy bags', 'indoor ice rink', 'karaoke room with song menus', 'casino floor with card tables', 'empty theater stage with the curtain up', 'trampoline park with foam pits', 'Buddhist temple hall', 'Shinto shrine interior', 'school cafeteria', 'dentist office treatment room', 'prison visiting room', 'university dormitory room', 'newsroom with desks and monitors', 'blacksmith forge with an anvil', "tailor's workroom with dress forms", 'television studio control room', 'fishing trawler wheelhouse', 'glassblowing studio with a furnace', 'airplane cabin aisle', 'cable car cabin', 'cruise ship interior corridor', 'departure hall with a split-flap board', 'the back seat of a taxi', 'bus stop shelter', 'fire escape landing', 'construction site with scaffolding', 'outdoor basketball court with chain nets', 'city fountain plaza', 'pier with a Ferris wheel', 'community garden allotment', 'canal towpath', 'the Eiffel Tower plaza', 'Times Square', 'the Colosseum exterior', 'Shibuya Crossing', 'the Sydney Opera House forecourt', 'the Grand Canal in Venice', 'the Charles Bridge in Prague', 'the Bund waterfront in Shanghai', 'the Jemaa el-Fnaa square in Marrakech', 'the Zocalo in Mexico City', 'the India Gate lawns in Delhi', 'the Copacabana promenade in Rio', 'the Golden Gate Bridge viewpoint', 'frozen lake surface', 'steaming hot spring pool', 'rolling wheat field', 'apple orchard rows', 'sea cave mouth', 'terraced rice paddies', 'basalt column coastline', 'high desert with joshua trees', 'the red desert plain below Uluru', 'the Table Mountain plateau', 'the Iguazu Falls lookout', 'the Cliffs of Moher', 'the Halong Bay karst waters', 'the Mount Fuji foothills', 'the Plitvice lake boardwalks'],
        "male_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'mission control room with monitor banks', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace overlooking the skyline', 'wide sandy beach', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'rolling desert dune', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street', 'rainy street with umbrellas', 'working harbor dock', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'open-air street food market', 'home office with bookshelves', 'walk-in closet with mirrors', 'ramen shop counter', 'artisan bakery interior', 'flower shop interior', 'vintage camera store', 'indoor spice market stall', 'climbing gym with colorful holds', 'dance studio with mirrors', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium', 'woodworking workshop', "artist's painting studio", 'commercial kitchen', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'alpine meadow with wildflowers', 'cracked salt flats', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop', 'ceramics studio with pottery wheels', 'rooftop cocktail bar', 'gastropub with an open kitchen', 'tea house with low wooden tables', 'old-fashioned ice cream parlor', 'hardware store aisle', 'butcher shop counter', 'garden centre greenhouse aisle', 'bicycle repair shop', 'neighborhood dry cleaner counter', 'arcade with glowing cabinets', 'independent cinema auditorium', 'billiards hall', 'martial arts dojo', 'university chemistry laboratory', 'veterinary clinic exam room', 'city hall rotunda', 'community theatre auditorium', 'auto repair shop service bay', 'print shop with running presses', 'machine shop with lathes', 'brewery tank room', 'ferry terminal waiting hall', 'hotel conference room', 'long-distance bus station', 'the Brooklyn Bridge pedestrian walkway', 'Trafalgar Square', 'the Spanish Steps in Rome', 'the Griffith Observatory terrace', 'red rock desert arch', 'slot canyon with striated walls', 'geothermal geyser basin', 'redwood grove with towering trunks', 'alpine glacier lake', 'coastal lighthouse bluff', 'waterfall plunge pool', 'volcanic black sand beach', 'moss-draped rainforest trail', 'the Grand Canyon south rim', 'a Yosemite valley meadow', 'a Zion canyon riverbank', 'tidy bedroom with a neatly made bed', 'tiled bathroom with a large mirror', 'laundry room with stacked machines', 'narrow hallway lined with family photos', "children's playroom with toy bins", 'music room with an upright piano', 'bustling food court', 'taqueria with a tiled counter', 'French bistro with mirrored walls', 'juice bar with a chrome counter', 'barbecue joint with paper-lined trays', 'shopping mall concourse', 'bank lobby with teller windows', 'pet shop lined with aquariums', 'department store perfume counter', 'stationery and art supply shop', 'shoe repair and key cutting counter', 'boxing gym with hanging heavy bags', 'indoor ice rink', 'karaoke room with song menus', 'casino floor with card tables', 'empty theater stage with the curtain up', 'trampoline park with foam pits', 'Buddhist temple hall', 'Shinto shrine interior', 'school cafeteria', 'dentist office treatment room', 'prison visiting room', 'university dormitory room', 'newsroom with desks and monitors', 'blacksmith forge with an anvil', "tailor's workroom with dress forms", 'television studio control room', 'fishing trawler wheelhouse', 'glassblowing studio with a furnace', 'airplane cabin aisle', 'cable car cabin', 'cruise ship interior corridor', 'departure hall with a split-flap board', 'the back seat of a taxi', 'bus stop shelter', 'fire escape landing', 'construction site with scaffolding', 'outdoor basketball court with chain nets', 'city fountain plaza', 'pier with a Ferris wheel', 'community garden allotment', 'canal towpath', 'the Eiffel Tower plaza', 'Times Square', 'the Colosseum exterior', 'Shibuya Crossing', 'the Sydney Opera House forecourt', 'the Grand Canal in Venice', 'the Charles Bridge in Prague', 'the Bund waterfront in Shanghai', 'the Jemaa el-Fnaa square in Marrakech', 'the Zocalo in Mexico City', 'the India Gate lawns in Delhi', 'the Copacabana promenade in Rio', 'the Golden Gate Bridge viewpoint', 'frozen lake surface', 'steaming hot spring pool', 'rolling wheat field', 'apple orchard rows', 'sea cave mouth', 'terraced rice paddies', 'basalt column coastline', 'high desert with joshua trees', 'the red desert plain below Uluru', 'the Table Mountain plateau', 'the Iguazu Falls lookout', 'the Cliffs of Moher', 'the Halong Bay karst waters', 'the Mount Fuji foothills', 'the Plitvice lake boardwalks'],
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
        #
        # 0.85.0 amendment: 'selfie framing at arm's length' is the one deliberate
        # exception to "camera-only, no second object". It still names only a camera
        # distance/position, not a phone or an arm holding one -- the difference from the
        # deleted "shot through a doorway" class is that a selfie does not put anything
        # *between* the camera and the subject, and this pack's whole frame is already "a
        # photographed cosplayer", so arm's-length is a coherent camera position rather
        # than an intruding object. Guarded by a pose exclusion in constraints.py so it
        # never draws a both-hands-occupied pose (see gesture_pockets/gesture_two_hands).
        "female_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'selfie framing at arm\'s length', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'from behind and slightly below, looking up toward subject', 'from above and behind, looking down toward subject', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
        "male_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'selfie framing at arm\'s length', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'from behind and slightly below, looking up toward subject', 'from above and behind, looking down toward subject', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
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
        "female_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips', 'money piece', 'peekaboo highlights', 'split dye'],
        "male_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips', 'money piece', 'peekaboo highlights', 'split dye'],
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
        "female_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'bare feet', 'ankle boots', 'wedges', 'mules', 'chelsea boots', 'combat boots', 'knee-high boots', 'ballet flats', 'high-top sneakers', 'espadrilles', 'derbies', 'kitten heels', 'mary janes', 'cowboy boots'],
        "male_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'bare feet', 'ankle boots', 'wedges', 'mules', 'chelsea boots', 'combat boots', 'knee-high boots', 'ballet flats', 'high-top sneakers', 'espadrilles', 'derbies', 'kitten heels', 'mary janes', 'cowboy boots'],
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
        "female_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim', 'polka dot', 'houndstooth', 'paisley', 'pinstripe', 'gingham', 'tie-dye', 'argyle'],
        "male_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim', 'polka dot', 'houndstooth', 'paisley', 'pinstripe', 'gingham', 'tie-dye', 'argyle'],
        # 0.90.0 grew this 10 -> 16. A bare append would have dropped the PLAIN
        # concept ('solid' + 'subtle texture') from 2/10 = 20% of characters to
        # 2/16 = 12.5%, quietly dressing everyone in busier clothes. These weights
        # hold plain at exactly 20%: 2 plain at 1.0 plus the patterned values sharing
        # a fixed 8.0 between them, so plain keeps its 2/10 share and every new
        # pattern subdivides the PATTERNED half only.
        #
        # 0.97.0 added 'argyle' and repriced the whole patterned set 4/7 -> 8/15 to
        # keep that sum at 8.0. A bare append would have taken plain from 2/10 to
        # 2/10.571 (18.9%) -- exactly the drift ConceptShareTests exists to catch,
        # and the reason the weight is written as a fraction of the count rather
        # than a decimal: the next pattern reprices to 8/16 and the arithmetic
        # stays visible.
        "weights": {'stripes': 8/15, 'plaid': 8/15, 'floral': 8/15,
                    'animal print': 8/15, 'geometric': 8/15, 'abstract': 8/15,
                    'camouflage': 8/15, 'denim': 8/15, 'polka dot': 8/15,
                    'houndstooth': 8/15, 'paisley': 8/15, 'pinstripe': 8/15,
                    'gingham': 8/15, 'tie-dye': 8/15, 'argyle': 8/15},
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
        "female_options": ['cheerful', 'sorrowful', 'mysterious', 'self-assured', 'dreamy', 'tense', 'tranquil', 'carefree', 'intense', 'joyful', 'lighthearted', 'somber', 'grim', 'peaceful', 'fierce', 'triumphant', 'enigmatic', 'moody', 'radiant', 'nostalgic', 'restless', 'exuberant', 'foreboding', 'hushed', 'commanding', 'uncanny'],
        "male_options": ['cheerful', 'sorrowful', 'mysterious', 'self-assured', 'dreamy', 'tense', 'tranquil', 'carefree', 'intense', 'joyful', 'lighthearted', 'somber', 'grim', 'peaceful', 'fierce', 'triumphant', 'enigmatic', 'moody', 'radiant', 'nostalgic', 'restless', 'exuberant', 'foreboding', 'hushed', 'commanding', 'uncanny'],
        "optional": False
    }),
    ("pose", {
        "group": 'Setting & Shot',
        # Phrased to read after "{subject} is …"; avoid pronouns so gender stays
        # correct ("a hand", not "their hand"). Every value must be a PARTICIPLE
        # PHRASE that completes that frame: "standing naturally" -> "She is standing
        # naturally." A bare noun phrase does not, and three values silently broke
        # this until 0.66.0 -- "arms relaxed at the sides" rendered "She is arms
        # relaxed at the sides." They were reworded in place (same slot, same family
        # weight, zero bias impact) to "standing with arms relaxed at the sides",
        # "touching the collar with one hand" and "holding both hands loosely
        # clasped". `PoseGrammarTests` pins the rule for new values.
        "female_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'standing with arms relaxed at the sides', 'touching the collar with one hand', 'standing with weight on one leg', 'standing tall with shoulders back', 'perched on the edge of a seat', 'sitting cross-legged', 'leaning forward slightly', 'leaning back casually', 'turning toward the viewer mid-stride', 'stepping forward', 'running one hand through the hair', 'holding both hands loosely clasped', 'tilting the head slightly', 'lifting the chin slightly', 'standing with hands clasped behind the back', 'standing with feet planted wide', 'sitting on the floor with knees drawn up', 'sitting with one leg crossed over the other', 'striding forward with purpose', 'stretching both arms overhead', 'adjusting one cuff', 'looking down thoughtfully', 'looking directly into the camera', 'looking off past the camera'],
        "male_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'standing with arms relaxed at the sides', 'touching the collar with one hand', 'standing with weight on one leg', 'standing tall with shoulders back', 'perched on the edge of a seat', 'sitting cross-legged', 'leaning forward slightly', 'leaning back casually', 'turning toward the viewer mid-stride', 'stepping forward', 'running one hand through the hair', 'holding both hands loosely clasped', 'tilting the head slightly', 'lifting the chin slightly', 'standing with hands clasped behind the back', 'standing with feet planted wide', 'sitting on the floor with knees drawn up', 'sitting with one leg crossed over the other', 'striding forward with purpose', 'stretching both arms overhead', 'adjusting one cuff', 'looking down thoughtfully', 'looking directly into the camera', 'looking off past the camera'],
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
    ("composition", {
        "group": 'Setting & Shot',
        # Frame LAYOUT only -- where the subject sits within the frame, never distance,
        # height, angle or lens (that is shot_type's axis; the two would otherwise
        # restate each other) and never a physical object (0.63.0 deleted doorway /
        # window / foliage framing from shot_type for exactly that reason -- an object
        # in the frame that the model has to invent). Every value reads after
        # "composed with ...". Deliberately absent from FIELD_FAMILIES, like shot_type:
        # a flat field, so any coherence exclusion (see constraints.py) re-picks
        # uniform rather than concentrating weight on survivors.
        "female_options": ['the subject on a rule-of-thirds line', 'centered symmetry',
                            'the subject small against open negative space',
                            'a tight crop and little headroom',
                            'leading lines drawing the eye to the subject',
                            'a low horizon line and open sky above',
                            'a high horizon line and a sliver of sky',
                            'the subject filling most of the frame'],
        "male_options": ['the subject on a rule-of-thirds line', 'centered symmetry',
                          'the subject small against open negative space',
                          'a tight crop and little headroom',
                          'leading lines drawing the eye to the subject',
                          'a low horizon line and open sky above',
                          'a high horizon line and a sliver of sky',
                          'the subject filling most of the frame'],
        "optional": False
    }),

    # ======================================================================
    # APPENDED AT 0.90.0 -- and the position is load-bearing twice over.
    # ======================================================================
    # These three belong to the Body and Clothing groups, so by the convention
    # above they "should" sit up with their neighbours. They are appended at the
    # END instead, deliberately, for two independent reasons:
    #
    # 1. SERIALIZATION. `define_schema` emits one widget per entry in this dict's
    #    insertion order, and ComfyUI stores `widgets_values` positionally. Adding
    #    a field mid-dict would shift every widget after it, so a workflow saved
    #    before 0.90.0 would reload with its values one slot out. Appending leaves
    #    every existing index untouched; an old workflow simply has no value for
    #    these three and they take their "Random" default. There is deliberately
    #    NO migration notice for this -- nothing is migrated, and a banner on every
    #    load of an older workflow is an irritant, not a service.
    #    UI position is unaffected: js/identity_forge.js rebuilds node.widgets into
    #    group order from FIELD_TO_GROUP, so these still render inside Body and
    #    Clothing where they belong.
    #
    # 2. DRAW ORDER. A field's pool filter can only read fields drawn BEFORE it
    #    (the same constraint documented on _performable_poses). All three gate on
    #    `outfit_description` and `footwear`, so they must be drawn after them --
    #    which appending guarantees. The order WITHIN this block also matters:
    #    `legwear` must precede `tattoo_placement`, because a leg tattoo is only
    #    offered when the leg is both uncovered by clothing and not hidden under
    #    opaque legwear.
    ("tattoos", {
        "group": 'Body',
        # Style and scale in one value, on purpose. A separate colour field would
        # let the randomizer roll "blackwork" against "pastel colour", and would
        # cost a third widget for no expressive gain. Placement is separate because
        # it is the one axis that has to be gated on what the clothes actually show.
        # 'no tattoos' is the absent token: it starts with "no ", so _is_absent()
        # hides it from the widget and omits it from prose, and _EXTRA_ABSENCE
        # drives it to ~85% so tattoos read as a distinguishing feature rather than
        # a default -- the same treatment skin_details and freckles already get.
        "female_options": ['no tattoos', 'a small fine-line black tattoo',
                            'a delicate minimalist tattoo', 'an ornamental geometric tattoo',
                            'a bold traditional tattoo in red and black',
                            'a dense blackwork tattoo', 'a floral illustrative tattoo',
                            'a soft watercolor tattoo', 'a fine dotwork tattoo',
                            'a small script lettering tattoo',
                            'a neo-traditional colour tattoo',
                            'a few scattered small tattoos'],
        "male_options": ['no tattoos', 'a small fine-line black tattoo',
                          'a delicate minimalist tattoo', 'an ornamental geometric tattoo',
                          'a bold traditional tattoo in red and black',
                          'a dense blackwork tattoo', 'a floral illustrative tattoo',
                          'a soft watercolor tattoo', 'a fine dotwork tattoo',
                          'a small script lettering tattoo',
                          'a neo-traditional colour tattoo',
                          'a few scattered small tattoos'],
        "optional": True
    }),
    ("legwear", {
        "group": 'Clothing',
        # Only ever voiced when the outfit actually shows leg (skirt / dress / gown /
        # shorts / playsuit); _wearable_legwear forces the absent token otherwise, so
        # tights never render under jeans. That is a WHOLE-pool suppression rather
        # than a partial cull, so there is no family weight to concentrate -- and the
        # field carries no FIELD_FAMILIES entry, so the draw is flat either way.
        # Male pool is the absent token alone, so the field is inert for men. The
        # original reasoning ("under trousers legwear is invisible") is true but is
        # NOT the whole story, because _wearable_legwear has already required a
        # leg-showing garment before this pool is ever read -- a man in shorts, a
        # kilt or a sarong reaches here with bare legs and still draws nothing, and
        # 'slouchy ankle socks' / 'ribbed knee-high socks' would read fine on him.
        # Left as-is deliberately: this is a curation call, not an oversight, and
        # widening it shifts the realized absence rate (measured 0.70 across genders
        # versus the 0.55 floor, precisely because half the draws are male and
        # forced). Recorded here so the next reader does not "fix" it by accident.
        "female_options": ['no visible legwear', 'sheer black tights',
                            'opaque black tights', 'opaque cream tights',
                            'fishnet tights', 'patterned tights', 'sheer stockings',
                            'ribbed knee-high socks', 'over-the-knee socks',
                            'slouchy ankle socks'],
        "male_options": ['no visible legwear'],
        "optional": True
    }),
    ("tattoo_placement", {
        "group": 'Body',
        # Gated by _visible_tattoo_placements: forearm/hand/wrist drop under long
        # sleeves, thigh/calf drop unless the leg is bare AND legwear is absent or
        # sheer, collarbone drops on a high neckline. Neck, behind-ear, upper-arm and
        # shoulder-blade survive every outfit, so the pool can never empty.
        # Flat field, no FIELD_FAMILIES entry: a partial cull re-picks uniformly
        # among the survivors instead of concentrating a frozen family weight.
        "female_options": ['on one forearm', 'across the back of one hand',
                            'on the inner wrist', 'on the side of the neck',
                            'behind one ear', 'across the collarbone',
                            'on one upper arm', 'across one shoulder blade',
                            'down one thigh', 'on one calf'],
        "male_options": ['on one forearm', 'across the back of one hand',
                          'on the inner wrist', 'on the side of the neck',
                          'behind one ear', 'across the collarbone',
                          'on one upper arm', 'across one shoulder blade',
                          'down one thigh', 'on one calf'],
        "optional": True
    }),
])

#: Per-field help, shown as the tooltip on that field's dropdown (0.78.0).
#:
#: Every field previously shared one generic string ("<group> · 'Random' =
#: randomize, a value = lock, 'None' = omit"), which explained the *mechanic* but
#: never the *field* -- nothing told a user that ``bust`` renders as "chest" on a
#: man, that ``fitness_level`` is where muscle lives rather than ``body_type``, or
#: that ``shot_type`` is camera-only. The mechanic sentence is still appended by the
#: node, so these say what the field means and flag any engine behaviour that will
#: surprise someone (automatic suppression, cross-field effects, gender defaults).
#:
#: Keep them short -- one sentence naming the field, plus at most one more only when
#: there is a genuine cross-field or cross-pack behaviour to flag (as with ethnicity,
#: skin_tone, height and lighting/mood below). Missing keys fall back to the generic
#: text, and tests/validate_data.py checks that every key names a real field and that
#: every user-visible field has an entry.
FIELD_HELP: dict[str, str] = {
    # --- Demographics ---
    "age": "Apparent age in years.",
    "ethnicity": "Also nudges skin tone toward a plausible range; locking skin tone overrides that.",
    # --- Body ---
    "skin_tone": "Overall skin colour. A costume that colours the whole body replaces this.",
    "body_type": "Overall build and proportions. Muscle definition is separate - see fitness_level.",
    "height": "Relative height. To force an unrealistic scale (doll-sized, fifty feet tall), use the size_scale control near the top instead.",
    "bust": "Chest size and shape. Renders as 'chest' on a male subject.",
    "waist": "Waist width relative to the rest of the figure.",
    "hips": "Hip width relative to the rest of the figure.",
    "shoulder_width": "Shoulder breadth relative to the hips.",
    "neck_length": "Neck length and thickness.",
    "posture": "How the subject carries themselves - upright, slouched, confident.",
    "fitness_level": "How conditioned the body looks, from sedentary to muscular. This is where muscle lives, not body_type.",
    # --- Face ---
    "face_shape": "Overall shape of the face - oval, square, heart.",
    "forehead": "Forehead height and brow ridge.",
    "cheekbones": "How high and prominent the cheekbones sit.",
    "eyebrows": "Natural brow shape and thickness. Grooming and product are eyebrow_makeup.",
    "eye_color": "Iris colour. A cosplay character with non-human eyes overrides this.",
    "eye_shape": "Eye shape and set - almond, hooded, deep-set.",
    "nose": "Nose shape and bridge.",
    "lips": "Lip shape and fullness. Colour and finish are lips_makeup.",
    "smile_type": "What the mouth is doing - closed, toothy, smirking.",
    "jawline": "Jaw width and definition.",
    "chin": "Chin shape and projection.",
    "complexion": "Skin quality and undertone - rosy, sallow, weathered.",
    "skin_details": "Moles, beauty marks, scars and other distinguishing marks.",
    "freckles_density": "How heavily freckled the skin is.",
    # --- Hair ---
    "hair_color": "Limited to realistic shades unless the hair_color_scope control is set to 'Full spectrum'.",
    "hair_length": "Hair length. Styles that need more length are automatically excluded on short cuts.",
    "hair_texture": "Curl pattern and body - straight, wavy, coily, fine.",
    "hair_style": 'How the hair is worn. Styles needing gatherable length are dropped automatically on a pixie or a buzz cut, and the short barbered crops only appear on short hair.',
    "facial_hair": "Beard and moustache. Randomized only on male subjects.",
    "hair_part": "Where the hair is parted. Cleared automatically on a bald or buzzed head.",
    "hair_highlights": "Colour worked through the hair - balayage, streaks, frosted tips.",
    "hair_accessory": "Headband, clip, scarf in the hair. Dropped automatically when a costume is supplied.",
    # --- Makeup ---
    "makeup_style": "The overall makeup look. Set it to 'no makeup' and every other Makeup field clears automatically; male subjects default to bare-faced.",
    "eyebrow_makeup": "Brow grooming and product. Natural brow shape is the eyebrows field.",
    "eye_makeup": "Eyeshadow colour and finish.",
    "eyeliner": "Liner style and weight.",
    "lashes": "Mascara or falsies.",
    "contour": "Sculpting on the cheeks, nose and jaw.",
    "highlight": "Where the skin catches the light.",
    "blush": "Cheek colour and placement.",
    "lips_makeup": "Lip colour and finish. Lip shape is the lips field.",
    "skin_finish": "How the base reads - matte, dewy, glass.",
    # --- Jewelry & Nails ---
    "earrings": "Ear jewellery. Name earrings in a costume only if you also lock this field, or you get two sets.",
    "necklace": "Neck jewellery. Same caution as earrings if a costume already describes one.",
    "other_jewelry": "Brooches, anklets, body chains and the like.",
    "piercings": "Piercings other than earlobes.",
    "nails": "Nail length, shape and polish.",
    "rings": "Finger rings.",
    "bracelet": "Wrist jewellery.",
    "watch_type": "Wristwatch. Dropped automatically when a costume is supplied, so no smartwatch on a samurai.",
    # --- Clothing ---
    "outfit_style": "How dressed up, and for what occasion. Subculture and era themes live on the Archetype node instead.",
    "bag": "Bag carried. Dropped automatically when a costume is supplied.",
    "accessories": 'Hats, glasses, gloves, belts and scarves. Dropped automatically when a costume is supplied, and gloves suppress nail polish and rings.',
    "footwear": 'Shoes. Voiced with the generated outfit, so locking this actually changes the shoes. Narrowed to what the chosen outfit_style plausibly wears; a supplied costume overrides it.',
    "clothing_color": 'Dominant palette of the outfit, voiced as an adjective in front of the garment ("a jewel-toned satin slip gown"). Yields to a garment that names its own colour.',
    "clothing_pattern": 'Print or weave of the outfit. Yields to a garment that names its own (a denim or sequined piece), and a monochrome palette rules out multi-colour prints.',
    # --- Setting & Shot ---
    "expression": 'The face the subject is pulling. Dropped automatically behind a full mask or helmet, unless you lock it.',
    "location": 'Where the shot happens, including named world landmarks. Narrow it with the location_setting control; a value locked here overrides that control.',
    "lighting": "Quality and source of the light. Automatically kept coherent with whether the location is indoors or out. Set to 'None' if a downstream rendering pack owns this axis.",
    "shot_type": "The camera only - distance, height, angle and lens. Never scene content.",
    "composition": "Where the subject sits within the frame - layout, not camera position. Kept coherent with shot_type.",
    "season": "Time of year, which colours the setting and wardrobe.",
    "mood": "Overall emotional tone of the image. Set to 'None' if a downstream rendering pack owns this axis.",
    "pose": "What the body is doing. A pose needing something the subject lacks is dropped: hair or pockets to reach for, a free hand when a prop is held, a seat at giant scale. A lock wins.",
    "tattoos": "Body ink - style and how much of it. Deliberately uncommon at random, and scaled by the accessory density control. Where it sits is tattoo_placement.",
    "legwear": "Tights, stockings or socks. Only rendered when the outfit actually shows leg, so it never appears under trousers. Feminine wardrobe only.",
    "tattoo_placement": "Where the tattoo sits. Placements the clothing would hide are dropped automatically - no forearm ink under long sleeves, no thigh ink under a skirt-less outfit or opaque tights.",
}


#: Hair styles grouped into families for weighted random selection. The flat
#: ``hair_style`` option list above still drives the widget (every variant is
#: lockable); this structure only steers the *random* pick. The engine first
#: chooses a family (weighted by ``weight``), then a variant uniformly within it,
#: so adding variants to a family subdivides that family's share instead of
#: inflating it. Each ``weight`` is frozen to the family's original variant count
#: (scaled uniformly, see below), so the macro distribution still matches the
#: pre-families uniform pick;
#: only the within-family split changes as variants are added. The union of all
#: ``variants`` must equal the ``hair_style`` options exactly (checked in tests).
#:
#: --- 0.78.0: the loose/braid split (finishes the 0.77.0 buzz-cut fix) ----------
#: Only a WHOLE family may be excluded by a constraint rule: ``_pick_family_weighted``
#: intersects a family's variants with the available pool but keeps the family's
#: **full frozen weight**, so culling *part* of a family dumps its entire share onto
#: the survivors. 0.77.0 fixed bangs-on-a-buzz-cut (``bangs`` is exactly two values,
#: so it drops whole) but had to leave five equally-impossible ``loose`` styles in
#: place -- roughly 4% of all output -- because they were 5 of 9 in one family.
#:
#: The fix is the treatment ``POSE_FAMILIES`` got at 0.66.0: split the family into
#: sub-families whose weights are **proportional to variant count**, so each
#: exclusion boundary lands on a whole unit. Sub-family boundaries are drawn from
#: the *actual* rules in data/constraints.py, not from intuition:
#:
#:   * ``loose_styled``   -- needs length to style; impossible on a buzz cut only.
#:   * ``loose_natural``  -- possible at every length; never excluded.
#:   * ``loose_combover`` -- excluded on a buzz cut (no length on top).
#:   * ``loose_mullet``   -- excluded on a buzz cut AND on very short (no back
#:                           length). Different boundary from comb over, hence its
#:                           own singleton -- ``half-up`` is the existing precedent.
#:   * ``braid_long``     -- needs gatherable length; excluded on a pixie.
#:   * ``braid_short``    -- cornrows and locs work at pixie length (a pixie-length
#:                           TWA is a real look), so they survive there.
#:   * ``bun_gathered``   -- an updo / French twist needs gatherable length;
#:                           excluded on a pixie.
#:   * ``bun_small``      -- the small buns a pixie CAN hold; the 0.72.0 rule
#:                           deliberately keeps them reachable there.
#:
#: All weights are scaled **x105** so every proportional sub-weight stays an integer
#: (``loose`` 6 splits 5:2:1:1, needing /9; ``bun`` 5 splits 5:2, needing /7;
#: ``braid`` 9 splits 8:2, needing /10; lcm(3, 5, 7) = 105). Scaling every weight by
#: the same factor is a no-op on relative shares, so **each variant keeps its exact
#: pre-split probability**: a loose variant was (6/30)x(1/9) = 1/45 and is now
#: (350/3150)x(1/5) = 1/45; a bun variant was (5/30)x(1/7) = 1/42 and is now
#: (375/3150)x(1/5) = 1/42. Pinned against a hardcoded pre-split baseline in
#: ``HairStyleFamilyTests``. Sum = 3150 (was 30). **Seeds drift** -- ``rng.choices``
#: now sees 14 families instead of 9 -- which is why this needed its own decision.
#: The distribution is unchanged.
#:
#: ``bun`` was split for the same reason as the other two, one step later: the pixie
#: rule drops ``updo`` + ``French twist``, 2 of the 7-variant family, which handed
#: bun's full frozen weight to its 5 small-bun survivors on every pixie. It was
#: nearly left as a documented wart, but ``HairStyleFamilyTests`` asserts the
#: whole-family invariant *mechanically* across every hair_length rule, and an
#: exception list in that test would have been the thing most likely to rot. Every
#: hair_length -> hair_style exclusion now drops whole families.
#:
#: MEASURED AND DELIBERATELY LEFT ALONE (0.78.0) -- the ``gender = Male`` hair_style
#: rule in data/constraints.py partially culls three families: ``bun_small`` (1/5,
#: ballerina bun), ``braid_long`` (2/8, crown + fishtail braid) and ``knots`` (1/2,
#: space buns). By the theory above that should concentrate each family's full
#: weight on its survivors for ~half of all output, which would be a far bigger bug
#: than the buzz cut. **It does not, and the reason is worth recording**: the engine
#: re-picks only a value it actually rejected (the mixture property documented at
#: 0.64.0), and most males draw a permitted style on the first try and never enter
#: the re-pick path, so only that minority sees the concentrated weight. Measured
#: over 23,270 male samples: ``bantu knots`` 3.79% vs ``cornrows`` 3.51%, a ratio of
#: 1.08 against a proportional expectation of 1.11 -- i.e. marginally *under* its
#: fair share, not doubled. Splitting these three (which M = 105 does accommodate:
#: 375 -> 300/75, 756 -> 567/189, 210 -> 105/105) would add three more families for
#: a sub-1pp correction. Do not "fix" this without re-measuring first.
HAIR_STYLE_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("loose_styled", {"weight": 700, "variants": ['worn down', 'slicked back', 'windswept', 'freshly blown out', 'tousled bedhead']}),
    ("loose_natural", {"weight": 280, "variants": ['wet look', 'natural and unstyled']}),
    ("loose_combover", {"weight": 140, "variants": ['comb over']}),
    ("loose_mullet", {"weight": 140, "variants": ['mullet']}),
    ("half-up", {"weight": 210, "variants": ['half up half down']}),
    ("ponytail", {"weight": 420, "variants": ['high ponytail', 'low ponytail', 'side ponytail', 'braided ponytail', 'bubble ponytail']}),
    ("bun_small", {"weight": 750, "variants": ['messy bun', 'sleek bun', 'top knot', 'chignon', 'ballerina bun']}),
    ("bun_gathered", {"weight": 300, "variants": ['updo', 'French twist']}),
    ("braid_long", {"weight": 1485, "variants": ['side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'milkmaid braids', 'rope braid', 'braided bun']}),
    ("braid_short", {"weight": 405, "variants": ['cornrows', 'locs', 'two-strand twists']}),
    ("knots", {"weight": 420, "variants": ['space buns', 'bantu knots']}),
    ("pigtails", {"weight": 210, "variants": ['pigtails', 'high pigtails', 'low pigtails', 'curled pigtails', 'braided pigtails']}),
    ("texture", {"weight": 420, "variants": ['afro', 'twist-out', 'hair puff']}),
    # 0.90.0 adds 'side-swept bangs' and 'wispy bangs'. Pure Mode A into a
    # PRE-EXISTING family (not a split, and bangs carry no hair_length restriction),
    # so the frozen weight is simply subdivided and the field-level distribution does
    # not move at all. Total weight stays 7140; `bangs` keeps its 0.058824 share.
    #
    # Two siblings were proposed and deliberately REJECTED, both for arithmetic
    # rather than taste -- and both were caught by HairStyleFamilyTests, not by eye:
    #   * 'hime cut' -> loose_styled. loose_styled is a SPLIT sub-family, so adding a
    #     sixth variant broke the loose split's proportionality (140 vs 116.67 per
    #     variant). It also needs long hair, which would make any length exclusion a
    #     PARTIAL cull of the sub-family and concentrate its frozen weight on the
    #     survivors. It needs its own sub-family, i.e. a reprice.
    #   * 'wolf cut' -> barbered_shag, an ADDED family pinned to the field's
    #     "everyday cut" rate; growing it needs the family repriced AND the _DILUTION
    #     constant restated.
    # Both are recorded in docs/suggested-additions.md rather than forced through.
    ("bangs", {"weight": 420, "variants": ['curtain bangs', 'blunt bangs', 'micro bangs',
                                           'side-swept bangs', 'wispy bangs']}),
    # 0.81.0: the ordinary-barbering gap. The pool had 40 ways to arrange hair and
    # no everyday BARBER cut at all -- no fade, undercut, pompadour, quiff or shag --
    # so any short-haired character fell back on "natural and unstyled" or a bun.
    #
    # WEIGHT, and why these numbers: `loose_combover` and `loose_mullet` are the
    # existing "one ordinary everyday cut" families, each 70 for a single variant.
    # Pricing a barbered cut identically gives 70 per variant: 280 for the four
    # short cuts and 70 for the shag. Total family weight therefore goes 3150 ->
    # 3500, so every pre-existing value keeps EXACTLY 9/10 of its former share
    # (3150/3500) and each new value lands on 70/3500 = 2.0%, the same as `mullet`.
    # There is no bias-free way to add a genuinely new concept -- share has to come
    # from somewhere -- so it is taken uniformly rather than out of one family.
    # SEEDS DRIFT (rng.choices sees more families): accepted, as at 0.66.0/0.78.0.
    #
    # SPLIT INTO TWO, and this is the load-bearing part: the four short cuts are
    # impossible on hip-length hair and the shag is impossible on a buzz, so the two
    # groups must be excludable independently. As one family, culling four of five
    # variants would hand the whole family weight to the survivor -- the exact trap
    # documented for `loose` at 0.78.0. As two families each is dropped WHOLE.
    ("barbered_short", {"weight": 560, "variants": ['fade', 'undercut', 'pompadour', 'quiff']}),
    ("barbered_shag", {"weight": 140, "variants": ['shag']}),

    # 0.83.0: the ONE hair_style change that is not free. `crew cut` / `textured crop` /
    # `high-top fade` cannot join `barbered_short` (fade/undercut/pompadour/quiff)
    # because their LENGTH GATE differs -- a crew cut at `chin length bob` is
    # impossible, a quiff is not -- and culling part of barbered_short at mid lengths
    # would concentrate that family's frozen weight on the survivors (the 0.64.0
    # LIGHTING_FAMILIES trap). So they need their own family, and a NEW family
    # enlarges the denominator: total 3500 -> 3570, so every other family loses 1.96%
    # relative share. Accepted knowingly.
    #
    # WEIGHT 70 IS DELIBERATE AND BELOW CONVENTION. The house rule is weight ~ original
    # variant count, and this field's rate is 3500/47 = 74.5 per variant, so three
    # crops "should" carry 224 (and dilute everything by 6.0%). 70 is the smallest unit
    # the field already uses (`barbered_shag`, `loose_combover`), which buys the smaller
    # dilution at the price of each crop sitting 3.2x rarer than an average value. That
    # is a feature here -- a crew cut and a high-top fade are specific looks, and
    # keeping them rare stops the base node reading as barbered. **This is the first
    # family priced below the per-variant rate; do not "fix" it in a weights audit.**
    ("barbered_crop", {"weight": 140, "variants": ['crew cut', 'textured crop', 'high-top fade']}),
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
    ("warm", {"weight": 6, "variants": ['subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'candid mid-laugh', 'gentle smile', 'beaming', 'delighted']}),
    ("calm", {"weight": 3, "variants": ['neutral', 'relaxed', 'serene', 'calm and composed', 'at ease', 'quietly content']}),
    ("intense", {"weight": 5, "variants": ['serious', 'confident', 'intense gaze', 'determined', 'stern', 'steely', 'focused', 'brooding', 'defiant']}),
    ("playful", {"weight": 5, "variants": ['playful', 'sultry', 'smirking', 'flirtatious', 'slightly bashful', 'mischievous', 'coy', 'quiet amusement', 'sly']}),
    ("pensive", {"weight": 3, "variants": ['pensive and thoughtful', 'contemplative', 'wistful', 'melancholic', 'lost in thought', 'daydreaming', 'solemn']}),
    ("reactive", {"weight": 2, "variants": ['surprised', 'curious', 'intrigued', 'skeptical', 'unimpressed']}),
])

MOOD_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    # 0.36 renames (mood vocabulary must stay disjoint from expression's — the
    # two randomize independently): playful->carefree, melancholic->sorrowful,
    # confident->self-assured, serene->tranquil, brooding->grim.
    ("positive", {"weight": 2, "variants": ['cheerful', 'carefree', 'joyful', 'lighthearted', 'radiant', 'exuberant']}),
    ("heavy", {"weight": 2, "variants": ['sorrowful', 'tense', 'somber', 'grim', 'restless', 'foreboding']}),
    ("calm", {"weight": 2, "variants": ['dreamy', 'tranquil', 'peaceful', 'nostalgic', 'hushed']}),
    ("bold", {"weight": 2, "variants": ['self-assured', 'intense', 'fierce', 'triumphant', 'commanding']}),
    ("enigmatic", {"weight": 1, "variants": ['mysterious', 'enigmatic', 'moody', 'uncanny']}),
])

#: 0.66.0 split the former single `gesture` family (weight 4, 6 variants) into three,
#: so the engine can drop the gestures a covered character cannot perform — a Moogle
#: has no hair to run a hand through and no pockets to put hands in. See
#: HAIR_DEPENDENT_POSES / GARMENT_DEPENDENT_POSES below and the Cosplayer suppression
#: in nodes/identity_forge.py.
#:
#: THE SPLIT IS EXACTLY DISTRIBUTION-NEUTRAL, and that is load-bearing. A family's
#: weight is its whole share, divided evenly among its variants, so a sub-family must
#: carry weight PROPORTIONAL TO ITS VARIANT COUNT or the split would silently
#: re-weight poses. Splitting 6 variants 3/2/1 needs weights 2 / 1.33 / 0.67, so every
#: family weight here is scaled x3 (a no-op on relative shares) to keep them integers:
#:   gesture         6/54 x 1/3 = 1/27   (was 4/18 x 1/6 = 1/27)
#:   gesture_garment 4/54 x 1/2 = 1/27
#:   gesture_hair    2/54 x 1/1 = 1/27
#: and e.g. standing 15/54 x 1/7 = 5/126 (was 5/18 x 1/7 = 5/126). Unchanged, value by
#: value. `PoseFamilyTests` in tests/test_engine.py pins this — do not retune a weight
#: here without updating that proof.
#:
#: 0.84.0 applied the SAME device four more times, in one rescale, for two fixes. The
#: rule it implements is the one `studio_stage` established at 0.83.0: **a pose value the
#: scene or the subject cannot support gets its own family, and the family is excluded
#: whole.** A partial cull would leave the parent's frozen weight concentrated on the
#: survivors.
#:   * `seated_perch` — a giant is forced outdoors by `_scale_coherent_pool`, and there is
#:     no seat outdoors. Audited: of 38 poses this is the ONLY one impossible at giant
#:     scale (`leaning against a wall` reads better at scale, not worse).
#:   * `standing_hands_bound` / `gesture_two_hands` / `gesture_pockets` — poses that
#:     occupy BOTH hands, which contradict a Cosplayer node signature prop. Measured
#:     before the fix at 14.37% of prop-enabled renders ("posing with hands in pockets,
#:     holding Mjolnir"). One-handed poses stay legal: the other hand holds the prop.
#: Splitting 9 variants 7/2 and 8/1 needs thirds, so every weight here is scaled x3 (a
#: no-op on relative shares) to keep them integers. Per-variant share after the split is
#: identical to before, family by family:
#:   standing 70/7 = standing_hands_bound 20/2 = 10   (was 30/9 x 3 = 10)
#:   seated   80/8 = seated_perch         10/1 = 10   (was 30/9 x 3 = 10)
#:   gesture  18/2 = gesture_two_hands    18/2 =  9   (was 12/4 x 3 =  9)
#:   gesture_garment 18/2 = gesture_pockets 9/1 =  9  (was  9/3 x 3 =  9)
#: Total 324 = 108 x 3.
POSE_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("standing", {"weight": 70, "variants": ['standing naturally', 'in a relaxed contrapposto stance', 'in a confident power pose', 'standing with arms relaxed at the sides', 'standing with weight on one leg', 'standing tall with shoulders back', 'standing with feet planted wide']}),
    # Standing poses that occupy BOTH hands/arms. Split out of `standing` so a held
    # signature prop can drop them as a whole family. A new both-hands standing pose
    # MUST go here, not in `standing`.
    ("standing_hands_bound", {"weight": 20, "variants": ['standing with arms crossed', 'standing with hands clasped behind the back']}),
    ("seated", {"weight": 80, "variants": ['sitting relaxed', 'sitting upright', 'reclining', 'kneeling gracefully', 'crouching low', 'sitting cross-legged', 'sitting on the floor with knees drawn up', 'sitting with one leg crossed over the other']}),
    # The one seated pose that needs FURNITURE rather than the ground. Split out so the
    # giant scale — which forces the scene outdoors — can drop it as a whole family.
    # Everything else in `seated` works on the ground and stays available at any scale.
    ("seated_perch", {"weight": 10, "variants": ['perched on the edge of a seat']}),
    ("leaning", {"weight": 18, "variants": ['leaning against a wall', 'leaning forward slightly', 'leaning back casually']}),
    ("motion", {"weight": 18, "variants": ['walking mid-stride', 'turning toward the viewer mid-stride', 'stepping forward', 'striding forward with purpose']}),
    # Gestures that need only a body and leave ONE hand free: safe for anyone, including
    # a full shell, and compatible with a held prop.
    ("gesture", {"weight": 18, "variants": ['posing with a hand on one hip', 'resting chin on one hand']}),
    # Gestures that occupy BOTH hands/arms — see `standing_hands_bound`.
    ("gesture_two_hands", {"weight": 18, "variants": ['holding both hands loosely clasped', 'stretching both arms overhead']}),
    # Gestures that reach for a GARMENT — a collar, a cuff. Nothing to grab on a
    # fur body, an armour shell or a droid chassis. A new garment-touching pose
    # MUST go here (or in `gesture_pockets`), not in `gesture`: the suppression set is
    # derived from these families, so a cuff-adjusting pose filed elsewhere would reach
    # for a sleeve a mascot suit does not have.
    ("gesture_garment", {"weight": 18, "variants": ['touching the collar with one hand', 'adjusting one cuff']}),
    # Garment-dependent AND both-hands: pockets need a garment to have pockets and both
    # hands to be free. Its own family so each rule can drop it independently.
    ("gesture_pockets", {"weight": 9, "variants": ['posing with hands in pockets']}),
    # Gestures that reach for SCALP HAIR. Nothing to touch under a helmet or on a
    # bald / masked / hooded head.
    ("gesture_hair", {"weight": 9, "variants": ['running one hand through the hair']}),
    # 0.85.0: two eye-contact variants grown in place (family weight unchanged, only
    # the per-value share shifts) -- the documented bias-safe channel for adding to an
    # existing family. Closes the gap where the pack had no way to state eye contact
    # at all.
    ("looking", {"weight": 36, "variants": ['looking over one shoulder', 'glancing back', 'tilting the head slightly', 'lifting the chin slightly', 'looking down thoughtfully', 'looking directly into the camera', 'looking off past the camera']}),
])

#: Poses the engine drops when a character has no visible scalp hair (a full mask, a
#: hood, or a bald head), no worn garment (a full hard shell / non-skin body), or a
#: signature prop already occupying both hands.
#: Derived from POSE_FAMILIES rather than hand-listed so the two cannot drift apart,
#: and deliberately whole families: dropping *part* of a family would leave its full
#: weight concentrated on the survivors (the bias trap documented for LIGHTING_FAMILIES
#: in 0.64.0). Removing a whole family instead leaves every other family's share
#: proportionally intact.
HAIR_DEPENDENT_POSES: frozenset[str] = frozenset(POSE_FAMILIES["gesture_hair"]["variants"])
#: Both garment families — `gesture_pockets` was split out of `gesture_garment` at
#: 0.84.0 for the held-prop rule, and pockets are the *most* garment-dependent pose of
#: all, so it must be unioned back in here or the split would silently let a mascot suit
#: put its hands in pockets it does not have.
GARMENT_DEPENDENT_POSES: frozenset[str] = frozenset(
    POSE_FAMILIES["gesture_garment"]["variants"] + POSE_FAMILIES["gesture_pockets"]["variants"]
)
#: Poses that occupy BOTH hands or both arms, dropped when a Cosplayer node supplies a
#: signature held prop (`held_item`). One-handed poses are deliberately absent: the free
#: hand holds the prop, which is the natural reading.
HAND_OCCUPIED_POSES: frozenset[str] = frozenset(
    POSE_FAMILIES["standing_hands_bound"]["variants"]
    + POSE_FAMILIES["gesture_two_hands"]["variants"]
    + POSE_FAMILIES["gesture_pockets"]["variants"]
)
#: Poses that need furniture rather than the ground, dropped at giant scale (which forces
#: an outdoor scene). Whole family, same reasoning as the two sets above.
FURNITURE_DEPENDENT_POSES: frozenset[str] = frozenset(POSE_FAMILIES["seated_perch"]["variants"])

#: Poses that assume an upright, two-armed body, dropped for a FERAL subject -- a
#: cosplay entry with ``body_plan: "feral"`` or a Creature node set to the Feral form
#: (0.95.0). Every ``pose`` value is written as a gesture a *person* performs; a
#: quadruped, a serpent or a six-legged sky bison has no arms to cross behind its back,
#: no hip to rest a hand on, and no chin to prop. Measured before the gate: **26.7%**
#: of feral renders (80/300, five creatures x 60 seeds) reached for something the
#: subject does not have -- "standing with arms crossed" on a six-legged sky bison.
#:
#: Six families go, and they are the same six the humanoid rules already drop one at a
#: time -- ``covers_face`` takes ``gesture_hair``, ``covers_body`` takes the two garment
#: families -- so this mostly formalizes what the flags achieve piecemeal, and covers
#: the Creature node's Feral form, which sets neither flag (it suppresses by group).
#: ``seated_perch`` joins them because perching on the edge of a seat is a human sit.
#:
#: What SURVIVES is the point: `standing`, `seated`, `leaning`, `motion` and `looking`
#: all read correctly on an animal -- standing four-square, lying down, walking
#: mid-stride, looking over one shoulder. Whole families throughout, so the survivors
#: keep their proportional shares (the POSE_FAMILIES rule above).
QUADRUPED_UNPERFORMABLE_POSES: frozenset[str] = frozenset(
    POSE_FAMILIES["standing_hands_bound"]["variants"]
    + POSE_FAMILIES["gesture"]["variants"]
    + POSE_FAMILIES["gesture_two_hands"]["variants"]
    + POSE_FAMILIES["gesture_garment"]["variants"]
    + POSE_FAMILIES["gesture_pockets"]["variants"]
    + POSE_FAMILIES["gesture_hair"]["variants"]
    + POSE_FAMILIES["seated_perch"]["variants"]
)

#: 0.65.0: the `studio` family's former `'Dutch angle with hard shadows'` mixed a pure
#: camera concept (Dutch angle = frame tilt) into a lighting field -- the same class of
#: wart the 0.63.0 shot_type camera-only doctrine would have caught there. Reworded to
#: `'harsh angled spotlight casting long hard shadows'` (light direction, not camera
#: framing) in the SAME slot at the SAME family weight -- zero bias impact, no field
#: pool or weight change. Migrating it into shot_type instead was considered and
#: rejected: that changes shot_type's own pool/weights, the exact risk flagged in 0.63.
#
# --- 0.82.0: the fixture split (every exclusion boundary is now a whole family) --
# Reported case: a render set in a `neighborhood pharmacy` "under flickering
# firelight from a hearth". The buckets below are binary indoor/outdoor, so three
# values that name a *specific fixture* -- a hearth, a television, a stained-glass
# window -- were legal in all ~139 indoor locations. A pharmacy has none of them.
#
# Fixing that needs a per-location rule, and a per-location rule may only remove a
# WHOLE family (`_pick_family_weighted` keeps a family's full frozen weight when
# it intersects with the pool, so a partial cull dumps that weight onto the
# survivors). Each fixture value therefore becomes its own single-variant family.
#
# The same move retires the approximation this block used to admit to -- "only the
# mixed `artificial` and `neon` families contribute individual values, and each
# keeps a clear majority of its variants in both directions". That majority-rule
# hand-wave was a real (accepted) bias: indoors, `neon` lost 2 of 8 variants while
# keeping its full 6/38 weight, inflating each of the 6 survivors by ~33% relative.
# Splitting on the actual bucket seams makes EVERY location<->lighting exclusion a
# whole-family drop, so the remaining families stay exactly proportional.
#
# All weights are scaled x6, the lcm that keeps each sub-weight an integer while
# holding the per-variant share identical (e.g. window was (4/38)/6 = 0.017544;
# window_general is now (20/228)/5 and window_stained (4/228)/1 -- both 0.017544).
# Total 228 = 38 x 6. **Seeds drift for `lighting`**: the distribution is unchanged
# but `rng.choices` sees 10 families instead of 5, so a given seed can land on a
# different value. Accepted, same precedent as 0.64.0 / 0.66.0 / 0.78.0 / 0.81.0.
LIGHTING_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("daylight", {"weight": 924, "variants": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'moonlight with cool blue tones', 'soft overcast golden light', 'harsh desert sun', 'snow-reflected daylight']}),
    # Indoor daylight. The whole family is indoor-only, so it drops whole outdoors;
    # stained glass splits off because it additionally needs the *building* to have it.
    ("window_general", {"weight": 220, "variants": ['soft window light from the side', 'backlit silhouette against bright window', 'light through venetian blinds casting stripes', 'warm sunlight streaming through a window', 'diffused skylight from above']}),
    ("window_stained", {"weight": 44, "variants": ['light through stained glass casting colors']}),
    # Portable / open flame -- reads fine on a patio, at a campfire, on a terrace.
    ("artificial_open", {"weight": 220, "variants": ['warm candlelight', 'warm incandescent lamp glow', 'warm string lights bokeh background', 'fire and flame warm flicker', 'warm lantern light']}),
    # A ceiling fixture asserts a built interior: indoor-only, and now drops whole.
    ("artificial_ceiling", {"weight": 88, "variants": ['cool LED overhead lighting', 'harsh fluorescent lighting']}),
    # Fixture-specific: indoors AND only where that fixture plausibly exists.
    ("artificial_hearth", {"weight": 44, "variants": ['flickering firelight from a hearth']}),
    ("artificial_screen", {"weight": 44, "variants": ['flickering television glow in a dark room']}),
    ("neon_venue", {"weight": 297, "variants": ['neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'golden bokeh lights in background', 'purple and teal neon wash', 'colored gel lighting']}),
    # Exterior street fixtures: outdoor-only, and now drop whole indoors.
    ("neon_street", {"weight": 99, "variants": ['fog-diffused streetlamp glow', 'reflection off wet pavement']}),
    # 0.83.0 fixture split, same argument as the hearth/television/stained-glass
    # values above: a "stage spotlight" asserts an overhead stage RIG, which is an
    # object, not a light quality. Measured before this: it landed on outdoor
    # locations in ~2% of outdoor renders ("stage spotlight from above" on
    # `high desert with joshua trees`). The other ten values are deliberately left
    # together -- Rembrandt / butterfly / split / soft-box / chiaroscuro / low key /
    # three-point all describe the SHAPE of light on the face and are achievable on
    # location with a reflector, so they are not fixture claims and need no allowlist.
    # Weights: 48 -> 480 + 48, proportional at 10:1, hence the x11 rescale of every
    # family in this map (480/10 == 48/1 == the old per-variant share). Total
    # 2508 = 228 x 11. **Seeds drift for `lighting`** (11 families, not 10).
    ("studio_shape", {"weight": 480, "variants": ['dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'harsh angled spotlight casting long hard shadows', 'soft-box style diffused light', 'split lighting with deep shadow', 'butterfly beauty lighting', 'Rembrandt lighting']}),
    ("studio_stage", {"weight": 48, "variants": ['stage spotlight from above']}),
])

#: Location families. Each is entirely indoor, entirely outdoor, or entirely
#: studio -- **never mixed**. That purity is load-bearing twice over: the giant
#: scale filter narrows `location` to OUTDOOR_LOCATIONS and stays bias-free only
#: because doing so drops seven WHOLE families (see ScaleCoherenceTests), and the
#: lighting buckets rely on the same seam. A location added to the "wrong" family
#: silently turns a coherence rule into a distribution bug.
#:
#: 0.82.0 grew the pool 204 -> 260, spread across all nine non-studio families so
#: no family's share concentrates. Because the field is family-weighted, adding a
#: variant subdivides its family's share and the field-level distribution does not
#: move at all -- only the within-family split changes.
#:
#: **Do not re-add `server room with blinking racks`.** It shipped from 0.29.0 and
#: was deliberately removed at 0.78.0 (`b201007`) as too dull to keep seeing; it is
#: the one obvious-looking gap in `work_industrial` that is a settled decision, not
#: an oversight.
LOCATION_FAMILIES: OrderedDict[str, dict] = OrderedDict([
    ("domestic", {"weight": 8856, "variants": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'cozy home library', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'home office with bookshelves', 'walk-in closet with mirrors', 'tidy bedroom with a neatly made bed', 'tiled bathroom with a large mirror', 'laundry room with stacked machines', 'narrow hallway lined with family photos', "children's playroom with toy bins", 'music room with an upright piano']}),
    ("food_drink", {"weight": 5535, "variants": ['elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'ramen shop counter', 'artisan bakery interior', 'gastropub with an open kitchen', 'tea house with low wooden tables', 'old-fashioned ice cream parlor', 'bustling food court', 'taqueria with a tiled counter', 'French bistro with mirrored walls', 'juice bar with a chrome counter', 'barbecue joint with paper-lined trays']}),
    ("retail_services", {"weight": 5904, "variants": ['neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'flower shop interior', 'vintage camera store', 'indoor spice market stall', 'hardware store aisle', 'butcher shop counter', 'garden centre greenhouse aisle', 'bicycle repair shop', 'neighborhood dry cleaner counter', 'shopping mall concourse', 'bank lobby with teller windows', 'pet shop lined with aquariums', 'department store perfume counter', 'stationery and art supply shop', 'shoe repair and key cutting counter']}),
    ("leisure_fitness", {"weight": 4059, "variants": ['local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'climbing gym with colorful holds', 'dance studio with mirrors', 'ceramics studio with pottery wheels', 'arcade with glowing cabinets', 'independent cinema auditorium', 'billiards hall', 'martial arts dojo', 'boxing gym with hanging heavy bags', 'indoor ice rink', 'karaoke room with song menus', 'casino floor with card tables', 'empty theater stage with the curtain up', 'trampoline park with foam pits']}),
    ("civic_institutional", {"weight": 6273, "variants": ['university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'police station bullpen', 'courtroom', 'planetarium dome interior', 'aquarium tunnel', 'science museum atrium', 'university chemistry laboratory', 'veterinary clinic exam room', 'city hall rotunda', 'community theatre auditorium', 'Buddhist temple hall', 'Shinto shrine interior', 'school cafeteria', 'dentist office treatment room', 'prison visiting room', 'university dormitory room']}),
    ("work_industrial", {"weight": 2583, "variants": ['corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'mission control room with monitor banks', 'factory floor', 'warehouse interior', 'woodworking workshop', "artist's painting studio", 'commercial kitchen', 'auto repair shop service bay', 'print shop with running presses', 'machine shop with lathes', 'brewery tank room', 'newsroom with desks and monitors', 'blacksmith forge with an anvil', "tailor's workroom with dress forms", 'television studio control room', 'fishing trawler wheelhouse', 'glassblowing studio with a furnace']}),
    ("transit_travel", {"weight": 2583, "variants": ['hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'vintage train compartment', 'ferry passenger cabin', 'airport lounge', 'ferry terminal waiting hall', 'hotel conference room', 'long-distance bus station', 'airplane cabin aisle', 'cable car cabin', 'cruise ship interior corridor', 'departure hall with a split-flap board', 'the back seat of a taxi']}),
    ("urban_outdoor", {"weight": 6560, "variants": ['sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace overlooking the skyline', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street', 'rainy street with umbrellas', 'working harbor dock', 'riverside boardwalk', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'open-air street food market', 'crumbling stone ruin', 'pedestrian shopping street', 'graffiti-covered skate park', 'harbor with moored boats', 'rooftop cocktail bar', 'bus stop shelter', 'fire escape landing', 'construction site with scaffolding', 'outdoor basketball court with chain nets', 'city fountain plaza', 'pier with a Ferris wheel', 'community garden allotment', 'canal towpath']}),
    # 0.83.0 landmark sub-family. The 4 named landmarks that shipped INSIDE
    # urban_outdoor are split out at a weight proportional to their original
    # count (6560:820 == 32:4), then grown 4 -> 17. The point of the split:
    # landmark VARIETY rises while P(any landmark | urban) stays exactly 4/36.
    # A plain add would have taken the famous-landmark concept from ~11% of urban
    # scenes to ~27% -- more variety AND more frequency, i.e. overweighting a
    # concept. Growing only the landmark side buys the first without the second.
    ("urban_landmark", {"weight": 820, "variants": ['the Brooklyn Bridge pedestrian walkway', 'Trafalgar Square', 'the Spanish Steps in Rome', 'the Griffith Observatory terrace', 'the Eiffel Tower plaza', 'Times Square', 'the Colosseum exterior', 'Shibuya Crossing', 'the Sydney Opera House forecourt', 'the Grand Canal in Venice', 'the Charles Bridge in Prague', 'the Bund waterfront in Shanghai', 'the Jemaa el-Fnaa square in Marrakech', 'the Zocalo in Mexico City', 'the India Gate lawns in Delhi', 'the Copacabana promenade in Rio', 'the Golden Gate Bridge viewpoint']}),
    ("nature_outdoor", {"weight": 5130, "variants": ['wide sandy beach', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'rolling desert dune', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'alpine meadow with wildflowers', 'cracked salt flats', 'mangrove boardwalk', 'bamboo forest path', 'tide pools at low tide', 'golden savanna with acacia trees', 'red rock desert arch', 'slot canyon with striated walls', 'geothermal geyser basin', 'redwood grove with towering trunks', 'alpine glacier lake', 'coastal lighthouse bluff', 'waterfall plunge pool', 'volcanic black sand beach', 'moss-draped rainforest trail', 'frozen lake surface', 'steaming hot spring pool', 'rolling wheat field', 'apple orchard rows', 'sea cave mouth', 'terraced rice paddies', 'basalt column coastline', 'high desert with joshua trees']}),
    # 0.83.0, same device as urban_landmark (5130:405 == 38:3), grown 3 -> 10.
    # Natural landmarks are deliberately fewer: the pool already ships generic
    # equivalents of several famous ones (volcanic black sand beach ~ Iceland,
    # basalt column coastline ~ the Giant's Causeway, rolling desert dune ~ the
    # Sahara, alpine glacier lake ~ Banff), so those were skipped as near-dupes.
    ("nature_landmark", {"weight": 405, "variants": ['the Grand Canyon south rim', 'a Yosemite valley meadow', 'a Zion canyon riverbank', 'the red desert plain below Uluru', 'the Table Mountain plateau', 'the Iguazu Falls lookout', 'the Cliffs of Moher', 'the Halong Bay karst waters', 'the Mount Fuji foothills', 'the Plitvice lake boardwalks']}),
    ("studio", {"weight": 1476, "variants": ['seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop']}),
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

# =========================================================================
# The wardrobe axis (0.83.0)
# =========================================================================
#
# THE DEFECT THIS FIXES. ``OUTFIT_DESCRIPTIONS`` superseded ``footwear``,
# ``clothing_color`` and ``clothing_pattern`` when it was added, and nobody retired
# them. In the base node's normal path an outfit is ALWAYS generated, and the prose
# only voiced those three when there was NO outfit — so for releases they were drawn
# every render, never spoken, and written to the JSON where they contradicted the
# prose:
#
#     prose : "She wears an ivory silk blouse with a high waisted skirt suit and
#              slingback pumps."
#     json  : footwear "ankle boots" / clothing_color "black monochrome"
#
# Locking them was worse than a no-op: the lock changed nothing visible but removed
# RNG draws, so five unrelated fields silently moved. The widget looked like it worked.
#
# THE CONTRACT NOW. Every value in ``OUTFIT_DESCRIPTIONS`` is a GARMENT PHRASE:
#   * garments and fabrics only — no footwear, no colour word, no pattern word, no
#     jewellery, no bag, no hat. Those axes belong to the fields that own them.
#   * NO leading article. The engine prefixes the palette adjective and then articles
#     the whole phrase with ``_article_if_singular``, so a plural head still works.
# ``validate_data.py`` enforces both, so the corpus cannot drift back.
#
# The engine composes:  {palette_adj} {garment}{pattern_tail}, in {footwear}
#   -> "a jewel-toned satin slip gown with delicate straps, in strappy heels"
#
# BIAS: zero drift on the three fields. They were already drawn in this order from
# these flat pools; making them RENDER consumes no extra RNG and moves no
# distribution. Only the outfit string itself drifts per seed, because the pool grew.

#: ``clothing_color`` value -> the adjective form used in front of a garment phrase.
#: Every option must have an entry (validated) — a missing key would silently drop the
#: palette from the prose, which is the exact class of bug this phase exists to kill.
PALETTE_ADJECTIVES: dict[str, str] = {
    'neutral tones': 'neutral-toned',
    'black monochrome': 'monochrome black',
    'white and cream': 'white-and-cream',
    'earth tones': 'earth-toned',
    'pastels': 'pastel',
    'bold primary colors': 'bold primary-colored',
    'jewel tones': 'jewel-toned',
    'gradient ombre': 'ombre-gradient',
    'all black': 'all-black',
    'all white': 'all-white',
    'mixed prints': 'mixed-print',
}

#: ``clothing_pattern`` value -> the phrase appended after a garment phrase (already
#: including its leading space), or ``""`` to say nothing. Per-value rather than a
#: blanket "with a {value} pattern" because the pool mixes true patterns (`plaid`,
#: `floral`) with a surface quality (`subtle texture`) and a fabric (`denim`), and
#: "with a denim pattern" is wrong. ``solid`` is deliberately silent: it is the
#: default reading of any garment, so saying it only adds noise.
#:
#: **Every tail uses "in", never "with".** Garment phrases very often end in their own
#: "with ..." clause ("satin slip gown with delicate straps"), and a "with" tail stacked
#: onto that reads "...with delicate straps with a floral print". Caught in preview, and
#: it is the same class of prose wart as the 0.82.0 doubled location article.
PATTERN_TAILS: dict[str, str] = {
    'solid': '',
    'subtle texture': ' in a subtle texture',
    'stripes': ' in stripes',
    'plaid': ' in plaid',
    'floral': ' in a floral print',
    'animal print': ' in an animal print',
    'geometric': ' in a geometric print',
    'abstract': ' in an abstract print',
    'camouflage': ' in camouflage',
    'denim': ' in denim',
    # 0.90.0. Each reads after a garment phrase, so the article has to suit the noun
    # ("in a paisley print", but "in gingham"). validate_data.py requires an entry
    # here for every clothing_pattern value -- it caught all six being missing.
    'polka dot': ' in polka dots',
    'houndstooth': ' in houndstooth',
    'paisley': ' in a paisley print',
    'pinstripe': ' in pinstripes',
    'gingham': ' in gingham',
    'tie-dye': ' in tie-dye',
    # 0.97.0. Named in the menswear pool comment below as a staple, and distinct from
    # plaid/houndstooth/gingham: a diamond lattice with an overlaid diagonal stripe.
    'argyle': ' in argyle',
}

#: Outfit descriptions keyed by outfit_style, split into gendered buckets.
#: The engine draws from ``unisex`` plus the bucket(s) selected by the wardrobe
#: control, so a black-tie gown never lands on a male subject by default — yet a
#: user can deliberately mix wardrobes for diversity.
#:
#: **Garment phrases only, no leading article** — see the contract note above.
OUTFIT_DESCRIPTIONS: dict[str, dict[str, list[str]]] = {
    'casual': {
        'female': [
            'cropped hoodie with high-waisted joggers',
            'fitted ribbed tank with mom jeans',
            'oversized wool sweater with high-waisted straight-leg jeans',
            'flowy cotton sundress under a denim jacket',
            'cropped cardigan over a camisole with wide-leg jeans',
            'boatneck jersey tee with cuffed chinos',
            'slouchy linen shirt knotted over leggings',
            'waffle-knit henley with corduroy trousers',
            'fleece quarter-zip over a tank with track pants',
            'cotton poplin shirtdress with a woven belt',
            'brushed-cotton flannel over a fitted long sleeve with jeans',
            'boxy crewneck sweatshirt with cargo trousers',
        ],
        'male': [
            'brushed flannel shirt with straight-leg jeans',
            'long-sleeve jersey tee with chinos',
            'relaxed linen button-up with cotton shorts',
            'henley shirt with corduroy pants',
            'crewneck sweatshirt with slim jeans',
            'zip-up fleece over a plain tee with tapered joggers',
            'waffle-knit thermal with washed denim',
            'cotton overshirt over a pocket tee with work trousers',
            'lightweight merino crewneck with straight chinos',
            'short-sleeve camp-collar shirt with relaxed jeans',
            'hooded sweatshirt under a quilted vest with jeans',
            'jersey polo with cuffed twill trousers',
        ],
        'unisex': [
            'fitted cotton tee with jeans under a denim jacket',
            'plain jersey tee with distressed jeans',
            'vintage-wash tee with cutoff shorts',
            'denim overalls over a fitted long sleeve',
            'oversized rugby shirt with loose-fit jeans',
            'cotton chore jacket over a tee with straight jeans',
            'sweatshirt with drawstring cotton shorts',
            'linen popover with rolled sleeves and loose trousers',
        ],
    },
    'smart casual': {
        'female': [
            'silk-blend blouse with tailored ankle trousers',
            'midi shirtdress with a slim leather belt',
            'cropped blazer over a fine-knit shell with cigarette pants',
            'wrap blouse with a bias-cut midi skirt',
            'fine-knit turtleneck with pleated trousers',
            'soft-shouldered jacket over a camisole with wide-leg trousers',
            'knitted polo shirt with tailored shorts',
            'sleeveless shift dress with a cropped cardigan',
            'tucked satin camisole with high-waisted twill trousers',
            'longline waistcoat over a poplin shirt with slim trousers',
        ],
        'male': [
            'unstructured cotton blazer over a merino polo with slim trousers',
            'oxford shirt with rolled sleeves and chinos',
            'fine-gauge crewneck over a collared shirt with wool trousers',
            'knitted polo with pleated trousers',
            'linen sport coat over a tee with tailored chinos',
            'brushed-twill overshirt over a henley with straight trousers',
            'merino quarter-zip with flat-front chinos',
            'camp-collar silk shirt with tailored trousers',
            'cotton-cashmere cardigan over an oxford with wool trousers',
            'soft-shouldered blazer with dark selvedge denim',
        ],
        'unisex': [
            'lightweight knit over a collared shirt with tapered trousers',
            'unlined linen jacket with drawstring tailored trousers',
            'fine merino crewneck with pleated wide-leg trousers',
            'cotton twill blazer over a jersey tee with chinos',
        ],
    },
    'business casual': {
        'female': [
            'fitted sheath dress with a thin belt',
            'cardigan over a silk blouse with a knee-length pencil skirt',
            'poplin blouse tucked into an A-line skirt',
            'shift dress under a cropped jacket',
            'crepe blouse with straight-leg tailored trousers',
            'soft blazer over a shell top with cropped wool trousers',
            'belted wrap dress in fine jersey',
            'knitted twinset with a bias midi skirt',
            'collarless jacket over a camisole with slim ankle trousers',
            'pleated culottes with a tucked silk shirt',
        ],
        'male': [
            'dress shirt with cuffed sleeves and pressed chinos',
            'merino v-neck over a collared shirt with wool trousers',
            'soft blazer over an oxford shirt with flat-front trousers',
            'long-sleeve knitted polo with tailored chinos',
            'poplin shirt with a fine-gauge cardigan and wool trousers',
            'twill blazer with a button-down shirt and pressed chinos',
            'brushed-cotton shirt with pleated wool trousers',
            'sweater vest over a poplin shirt with tapered trousers',
            'unlined wool jacket over a jersey polo with straight trousers',
            'linen-blend shirt with tailored trousers and a leather belt',
        ],
        'unisex': [
            'ponte blazer with matching tailored trousers',
            'fine-knit crewneck with a collared shirt and wool trousers',
            'unstructured jacket over a jersey top with pressed chinos',
            'tailored waistcoat over a poplin shirt with straight trousers',
        ],
    },
    'business formal': {
        'female': [
            'double-breasted blazer with wide-leg trousers and a silk camisole',
            'tailored skirt suit with a silk shell',
            'single-breasted trouser suit with a poplin shirt',
            'sheath dress under a structured tailored jacket',
            'peak-lapel jacket with a pencil skirt and a crepe blouse',
            'three-piece trouser suit with a fine-knit shell',
            'wool crepe dress with a matching tailored coat',
            'collarless tailored jacket with straight trousers and a silk blouse',
            'belted wool suit dress with sharp shoulders',
            'long-line blazer with pressed wide trousers and a camisole',
        ],
        'male': [
            'notch-lapel suit with a spread-collar shirt and a silk tie',
            'peak-lapel double-breasted suit with a poplin shirt and a tie',
            'three-piece wool suit with a waistcoat and a knitted tie',
            'single-breasted worsted suit with a twill shirt and a tie',
            'tailored suit with a pinned-collar shirt and a silk tie',
            'sharp-shouldered suit with a poplin shirt and a grenadine tie',
            'wool flannel suit with an oxford shirt and a wool tie',
            'slim two-piece suit with a french-cuff shirt and a silk tie',
            'double-breasted flannel suit with a spread-collar shirt',
            'worsted suit with a waistcoat, poplin shirt and a silk tie',
        ],
        'unisex': [
            'tailored suit with a crisp shirt and minimal detailing',
            'structured two-piece suit with a fine-knit shell',
            'sharply pressed suit with a poplin shirt and a slim tie',
            'long-line tailored coat over a two-piece suit',
        ],
    },
    'evening formal': {
        'female': [
            'floor-length velvet gown with delicate straps',
            'floor-length crepe dress with a deep v back',
            'ball gown with a structured bodice and a full skirt',
            'off-shoulder mermaid gown with long satin gloves',
            'sequined evening gown with a satin wrap',
            'draped satin column gown with a draped neck',
            'one-shoulder chiffon gown with a slit skirt',
            'beaded silk gown with a high halter neck',
            'tulle ballgown with an embroidered bodice',
            'high-neck lace gown with a sweeping train',
            'silk-faille gown with an asymmetric neckline',
            'liquid-satin slip gown with a bias-cut skirt',
        ],
        'male': [
            'classic tuxedo with a crisp shirt and a silk bow tie',
            'dinner jacket with tuxedo trousers and a bow tie',
            'velvet dinner jacket with tuxedo trousers and a bow tie',
            'double-breasted tuxedo with a shawl-lapel jacket',
            'peak-lapel tuxedo with a pleated-front shirt and a bow tie',
            'midnight wool dinner suit with a cummerbund and a bow tie',
            'shawl-collar dinner jacket with a marcella shirt',
            'tailcoat with a wing-collar shirt and a white bow tie',
            'silk-lapel tuxedo with a fly-front shirt and a bow tie',
            'brocade dinner jacket with tuxedo trousers',
        ],
        'unisex': [
            'sharply tailored dinner suit with a satin lapel',
            'floor-length tailored cape over evening tailoring',
            'high-shine satin tailoring with a bow tie',
            'velvet tuxedo jacket with pressed evening trousers',
        ],
    },
    'cocktail semi-formal': {
        'female': [
            'velvet wrap dress with a draped neckline',
            'metallic midi dress with a draped neckline',
            'sequined top with high-waisted tailored trousers',
            'fit-and-flare crepe cocktail dress',
            'bodice-seamed satin midi dress',
            'pleated chiffon midi dress with a tie waist',
            'beaded shell top with a bias satin skirt',
            'tuxedo-style mini dress with sharp shoulders',
            'asymmetric-hem jacquard cocktail dress',
            'corseted midi dress in duchess satin',
            'off-shoulder ruched jersey dress',
            'feather-trimmed crepe cocktail dress',
        ],
        'male': [
            'tailored suit with a fine-knit shirt and no tie',
            'blazer with dress trousers and an open-collar shirt',
            'double-breasted blazer with a turtleneck and tailored trousers',
            'textured wool jacket with a silk shirt and pressed trousers',
            'shawl-collar knit jacket with tailored trousers',
            'velvet blazer over a fine merino crewneck with wool trousers',
            'unstructured silk-blend jacket with a camp-collar shirt',
            'slim suit with a knitted polo and a pocket square',
            'cropped tuxedo jacket with slim tailored trousers',
            'jacquard blazer with a poplin shirt and wool trousers',
        ],
        'unisex': [
            'fitted blazer with a silk camisole and leather trousers',
            'satin tailoring with a soft-collar shirt',
            'textured cocktail jacket with pressed trousers',
            'sharply cut jumpsuit in fluid crepe',
        ],
    },
    'streetwear': {
        'female': [
            'puffer jacket over a cropped top with biker shorts',
            'mesh long-sleeve over a sports bra with baggy jeans',
            'oversized tee dress with a cropped hoodie',
            'cropped bomber over a bralette with cargo trousers',
            'windbreaker with a pleated tennis skirt',
            'boxy varsity jacket over a ribbed tank with wide jeans',
            'cropped puffer vest over a longline hoodie with joggers',
            'oversized flannel over a crop top with parachute trousers',
            'track jacket with a matching pleated skort',
            'longline anorak over a fitted bodysuit with baggy denim',
        ],
        'male': [
            'oversized hoodie with cargo trousers',
            'bomber jacket over a plain tee with ripped jeans',
            'boxy tee with wide-leg jeans',
            'baseball jersey over a turtleneck with loose jeans',
            'quilted vest over a longline hoodie with stacked denim',
            'techwear shell jacket with tapered cargo trousers',
            'oversized coach jacket with nylon track pants',
            'half-zip fleece with wide corduroy trousers',
            'longline tee under a cropped puffer with joggers',
            'hooded flannel overshirt with baggy carpenter jeans',
        ],
        'unisex': [
            'oversized sweatshirt with nylon track pants',
            'boxy anorak over a longline tee with cargo trousers',
            'cropped puffer with wide-leg jeans',
            'zip-through hoodie under a canvas chore coat with joggers',
            'relaxed coach jacket with parachute trousers',
            'longline knit vest over a tee with loose denim',
        ],
    },
    'bohemian': {
        'female': [
            'velvet burnout maxi dress',
            'flowing maxi dress with bell sleeves',
            'crochet top with high-waisted wide-leg trousers and a woven belt',
            'smocked prairie dress with a tiered hem',
            'embroidered peasant blouse with a broomstick skirt',
            'gauzy tiered maxi skirt with a knotted linen blouse',
            'quilted patchwork waistcoat over a gauze dress',
            'fringed suede jacket over a slip dress',
            'batik-wrap skirt with an embroidered cropped blouse',
            'layered gauze tunic over flared linen trousers',
            'hand-loomed shawl over a smocked midi dress',
            'crinkled cotton kaftan with a corded belt',
        ],
        'male': [
            'open linen shirt with loose drawstring trousers',
            'embroidered tunic with wide linen trousers',
            'crochet-panel overshirt with cropped linen trousers',
            'gauze grandad-collar shirt with relaxed trousers',
            'fringed suede jacket over a henley with flared jeans',
            'hand-loomed poncho over a linen shirt',
            'corduroy flares with a knitted open-weave sweater',
            'kaftan-cut cotton shirt with drawstring trousers',
        ],
        'unisex': [
            'kimono cardigan over a slip top',
            'patchwork layers over a gauze shift',
            'crinkled linen duster over wide drawstring trousers',
            'open-weave knit poncho over a gauze tunic',
            'embroidered waistcoat over a loose linen shirt',
            'layered gauze scarves over a tiered cotton dress',
        ],
    },
    'athletic': {
        'female': [
            'fitted crop top with high-rise leggings',
            'racerback sports bra with running shorts',
            'zip-up training jacket with full-length leggings',
            'seamless athletic bodysuit',
            'pleated tennis dress with a built-in short',
            'cropped windbreaker with cycling shorts',
            'compression tank with a pleated running skirt',
            'longline sports bra with flared yoga trousers',
            'quarter-zip base layer with thermal running tights',
            'loose training tee over a bike short',
        ],
        'male': [
            'compression shirt with training shorts',
            'sports jersey with basketball shorts',
            'moisture-wicking tee with tapered training joggers',
            'sleeveless training top with mesh shorts',
            'half-zip base layer with running tights',
            'lightweight running singlet with split shorts',
            'hooded training top with woven track pants',
            'technical windbreaker with fitted training shorts',
            'rash-guard long sleeve with board shorts',
            'quarter-zip thermal with brushed-back joggers',
        ],
        'unisex': [
            'moisture-wicking tee with training shorts',
            'full tracksuit in brushed technical jersey',
            'hooded shell over a base layer with training tights',
            'sleeveless training top with woven joggers',
            'packable running gilet over a long-sleeve base layer',
            'mesh-panel tee with fitted training leggings',
        ],
    },
    'resort vacation': {
        'female': [
            'sarong wrap over a bandeau swimsuit',
            'crochet cover-up over a one-piece swimsuit',
            'maxi skirt with a halter top',
            'linen shirtdress worn open over a swimsuit',
            'gauze kaftan with a knotted waist',
            'cropped linen shirt with wide drawstring trousers',
            'tiered cotton sundress with a smocked bodice',
            'wrap-front linen playsuit',
            'broderie-anglaise cover-up over a bikini',
            'silk-blend camisole with flowing palazzo trousers',
        ],
        'male': [
            'tropical camp-collar shirt with relaxed trousers',
            'linen shirt worn open over swim shorts',
            'short-sleeve resort shirt with tailored linen shorts',
            'gauze grandad shirt with drawstring linen trousers',
            'swim shorts with an unbuttoned linen overshirt',
            'knitted polo with pleated linen shorts',
            'seersucker shirt with cotton chino shorts',
            'terry-cloth polo with tailored swim shorts',
        ],
        'unisex': [
            'loose linen set with a camp-collar shirt and shorts',
            'gauze cotton kaftan over swimwear',
            'terry-towelling overshirt with drawstring shorts',
            'crinkled linen shirt with wide-leg trousers',
            'lightweight seersucker set with an open shirt',
            'cotton robe worn open over swimwear',
        ],
    },
    'edgy alternative': {
        'female': [
            'fishnet top under a slip dress',
            'cropped moto jacket over a ribbed tank with skinny jeans',
            'corset top with a mesh long sleeve and vinyl trousers',
            'distressed knit over a bodysuit with ripped denim',
            'buckled pinafore over a fitted long sleeve',
            'harness-detail top with wide leather trousers',
            'asymmetric-hem mesh dress over a bodysuit',
            'shredded oversized knit with cropped leggings',
            'vinyl trench over a ribbed bodysuit',
            'deconstructed tailored jacket with laddered tights and shorts',
        ],
        'male': [
            'distressed denim jacket with studded patches and jeans',
            'moto jacket over a ripped tee with skinny jeans',
            'buckled leather jacket over a mesh long sleeve',
            'deconstructed knit with tapered cargo trousers',
            'vinyl-panel bomber with slim leather trousers',
            'shredded oversized tee with buckled utility trousers',
            'long leather coat over a ribbed tank with slim jeans',
            'harness-strapped overshirt with distressed denim',
        ],
        'unisex': [
            'denim vest with frayed shorts and a studded belt',
            'layered mesh over a distressed knit with leather trousers',
            'buckled utility harness over a shredded tee',
            'asymmetric deconstructed jacket with laddered leggings',
        ],
    },
    'preppy': {
        'female': [
            'knife-pleated skirt with a fine-knit sweater',
            'cable-knit sweater over a poplin shirt with tailored shorts',
            'sleeveless polo dress with a knitted trim',
            'quilted jacket over a rugby shirt with slim chinos',
            'lambswool vest over a poplin shirt with a pleated skirt',
            'blazer with a pleated tennis skirt and knee socks',
            'shetland crewneck with straight chinos and a webbing belt',
            'poplin shirtdress with a rope belt',
            'knitted polo with a box-pleated midi skirt',
            'cricket-trim cardigan over a shell top with tailored trousers',
        ],
        'male': [
            'cable-knit sweater over an oxford shirt with chinos',
            'quarter-zip lambswool sweater with pressed chinos',
            'rugby shirt with straight-leg chinos and a webbing belt',
            'blazer over a button-down shirt with cotton trousers',
            'shetland crewneck over an oxford shirt with corduroys',
            'quilted vest over a fine-knit sweater with chinos',
            'cricket sweater with pleated cotton trousers',
            'cotton camp shirt with tailored shorts',
            'lambswool vest over a button-down with wool trousers',
            'harrington jacket over a knitted polo with chinos',
        ],
        'unisex': [
            'lambswool crewneck over a collared shirt with chinos',
            'quilted field jacket over a cable-knit sweater',
            'harrington jacket with pressed cotton trousers',
            'knitted vest over an oxford shirt with tailored shorts',
        ],
    },
    'vintage retro': {
        'female': [
            'high-waisted mom jeans with a tucked-in jersey tee',
            'swing dress with a full circle skirt and a cinched waist',
            'fitted wiggle dress with a portrait collar',
            'cropped cardigan over a halter sundress',
            'wide-leg sailor trousers with a tucked blouse',
            'shirtwaist dress with a pleated skirt and a fabric belt',
            'boucle skirt suit with a boxy collarless jacket',
            'corduroy pinafore over a ribbed roll-neck',
            'empire-waist crepe dress with lantern sleeves',
            'gabardine pencil skirt with a tucked short-sleeve knit',
        ],
        'male': [
            'rolled-cuff jeans with a jersey tee and a leather jacket',
            'bowling shirt with pleated gabardine trousers',
            'knitted polo with high-waisted wide trousers',
            'corduroy blazer over a roll-neck with flared trousers',
            'double-pleated trousers with braces and a poplin shirt',
            'boxy gabardine jacket with cuffed wool trousers',
            'cardigan over a ribbed tank with high-waisted denim',
            'safari-cut jacket with pleated cotton trousers',
            'waffle henley with wide-cut workwear denim',
            'shawl-collar cardigan with tapered wool trousers',
        ],
        'unisex': [
            'boxy gabardine jacket with pleated trousers',
            'knitted roll-neck with high-waisted wide trousers',
            'corduroy blazer with cuffed straight denim',
            'cropped harrington with rolled-cuff workwear jeans',
        ],
    },
    'loungewear': {
        'female': [
            'soft camisole with drawstring lounge trousers',
            'ribbed lounge set with a cropped long sleeve and shorts',
            'oversized waffle-knit sweatshirt with matching joggers',
            'brushed-jersey nightdress with a wrap robe',
            'cashmere-blend lounge set with wide-leg trousers',
            'slouchy knitted cardigan over a rib tank with lounge shorts',
            'modal pyjama set with a piped collar',
            'fleece-lined hoodie with brushed jersey joggers',
            'linen-blend lounge shirt with matching drawstring trousers',
        ],
        'male': [
            'cotton robe over lounge trousers',
            'brushed-jersey tee with drawstring lounge trousers',
            'waffle-knit henley with fleece-back joggers',
            'piped poplin pyjama set',
            'hooded sweatshirt with brushed lounge shorts',
            'modal lounge tee with matching wide trousers',
            'shawl-collar knitted robe over a jersey lounge set',
            'linen-blend lounge shirt with drawstring shorts',
        ],
        'unisex': [
            'waffle-knit lounge set with a crewneck and joggers',
            'brushed jersey hoodie with matching lounge trousers',
            'cotton-modal pyjama set with a piped trim',
            'oversized knitted robe over a jersey lounge set',
            'fleece-back sweatshirt with drawstring lounge shorts',
            'ribbed lounge set with a long sleeve and wide trousers',
        ],
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

# --- complexion <-> skin_tone coherence (0.82.0) -----------------------------
# `complexion` is a surface quality, and most of its values (`clear`, `rosy`,
# `ruddy`, `sallow`) read on any skin tone -- redness and pallor are visible
# across the range. **`peaches and cream` is the exception**: it names a specific
# pink-white colouring, so it directly contradicts a deep tone. Rendered output
# read "a 35-year-old Jamaican woman with ... deep ebony skin. ... Her skin shows
# a peaches and cream complexion."
#
# This is the same contradiction the Ka D'Argo entry comment records ("a Dominican
# man ... light skin ... a peaches and cream complexion" above "weathered
# bronze-red skin"). That case was only ever fixed *per entry*, by the body-paint
# suppression; nothing handled the ordinary human case.
#
# Excluding it is bias-clean **because `complexion` is a flat field** -- no
# FIELD_FAMILIES entry and no `weights` map -- so `_repick` draws flat-uniform
# over whatever survives and the whole-family rule simply does not apply here.
# Scoped as tightly as the evidence supports: one value, and only the tones where
# it is genuinely impossible rather than merely unusual.
DEEP_SKIN_TONES: frozenset[str] = frozenset([
    'brown', 'warm brown', 'dark brown', 'deep', 'ebony', 'deep ebony',
])

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
    # 0.83.0 landmarks. Registering them here is MANDATORY: the indoor bucket is
    # DERIVED (all - OUTDOOR_LOCATIONS - STUDIO_BACKDROPS), so a missing entry would
    # silently classify the Eiffel Tower as an interior and let it draw a hearth.
    'the Eiffel Tower plaza', 'Times Square', 'the Colosseum exterior',
    'Shibuya Crossing', 'the Sydney Opera House forecourt', 'the Grand Canal in Venice',
    'the Charles Bridge in Prague', 'the Bund waterfront in Shanghai', 'the Jemaa el-Fnaa square in Marrakech',
    'the Zocalo in Mexico City', 'the India Gate lawns in Delhi', 'the Copacabana promenade in Rio',
    'the Golden Gate Bridge viewpoint', 'the red desert plain below Uluru', 'the Table Mountain plateau',
    'the Iguazu Falls lookout', 'the Cliffs of Moher', 'the Halong Bay karst waters',
    'the Mount Fuji foothills', 'the Plitvice lake boardwalks',
    'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street',
    'rooftop terrace overlooking the skyline', 'wide sandy beach', 'rocky coastal cliff',
    'forest trail', 'mountain overlook', 'rolling desert dune',
    'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom',
    'sunlit vineyard', 'lavender field', 'quiet suburban backyard',
    'urban alley with graffiti', 'neon-lit city street', 'rainy street with umbrellas',
    'working harbor dock', 'riverside boardwalk', 'botanical garden path',
    'open meadow', 'lakeside pier', 'misty moor',
    'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden',
    'busy city crosswalk', 'country dirt road', 'palm-lined promenade',
    'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater',
    'poolside cabana', 'open-air street food market', 'rooftop cocktail bar',
    'pedestrian shopping street', 'graffiti-covered skate park',
    'harbor with moored boats', 'alpine meadow with wildflowers',
    'cracked salt flats', 'mangrove boardwalk', 'bamboo forest path',
    'tide pools at low tide', 'golden savanna with acacia trees',
    # 0.78.0 additions. Indoor is DERIVED (all - OUTDOOR - STUDIO), so anything
    # outdoors that is missing here silently buckets as indoor and starts pairing
    # with window light. Keep this list in step with the two outdoor families.
    'red rock desert arch', 'slot canyon with striated walls',
    'geothermal geyser basin', 'redwood grove with towering trunks',
    'alpine glacier lake', 'coastal lighthouse bluff', 'waterfall plunge pool',
    'volcanic black sand beach', 'moss-draped rainforest trail',
    'the Grand Canyon south rim', 'a Yosemite valley meadow',
    'a Zion canyon riverbank',
    'the Brooklyn Bridge pedestrian walkway', 'Trafalgar Square',
    'the Spanish Steps in Rome', 'the Griffith Observatory terrace',
    # 0.82.0 additions -- urban_outdoor
    'bus stop shelter', 'fire escape landing',
    'construction site with scaffolding',
    'outdoor basketball court with chain nets', 'city fountain plaza',
    'pier with a Ferris wheel', 'community garden allotment', 'canal towpath',
    # 0.82.0 additions -- nature_outdoor
    'frozen lake surface', 'steaming hot spring pool', 'rolling wheat field',
    'apple orchard rows', 'sea cave mouth', 'terraced rice paddies',
    'basalt column coastline', 'high desert with joshua trees',
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
# ``window_*`` families ARE indoor daylight. Bucketing whole families means a
# filtered family drops out entirely and the remaining families' shares stay
# exactly proportional, instead of one family keeping its full weight while
# concentrated onto two or three surviving variants.
#
# 0.82.0: every bucket below is now an exact union of whole families -- see the
# fixture-split note above LIGHTING_FAMILIES. Before that, ``artificial`` and
# ``neon`` each contributed individual values and were partially culled, which was
# a real bias accepted on a "clear majority survives" argument. **When adding a
# lighting value, add it to a family whose members share its bucket**, or the
# bucket stops being a whole-family union and the guarantee silently lapses;
# ``LightingBucketFamilyTests`` fails if that happens.

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
#: the location is outdoors. Exactly four whole families -- ``window_general``,
#: ``window_stained``, ``artificial_ceiling``, ``artificial_hearth`` and
#: ``artificial_screen`` -- so the drop stays proportional. The five
#: ``artificial_open`` values (candle, lamp, string lights, open flame, lantern)
#: read fine on a patio or at a campfire and stay available outdoors.
INDOOR_ONLY_LIGHTING: frozenset[str] = frozenset([
    'soft window light from the side', 'backlit silhouette against bright window',
    'light through venetian blinds casting stripes',
    'light through stained glass casting colors',
    'warm sunlight streaming through a window', 'diffused skylight from above',
    'cool LED overhead lighting', 'harsh fluorescent lighting',
    'flickering firelight from a hearth', 'flickering television glow in a dark room',
])


# --- fixture lighting: indoors is necessary but not sufficient ----------------
# Three indoor values name a physical fixture rather than a quality of light, so
# being indoors does not make them possible -- the *building* has to have the
# thing. Each is its own single-variant LIGHTING family so a per-location rule
# removes it as a whole unit (see the fixture-split note above LIGHTING_FAMILIES).
#
# These are allowlists, so the safe default for any location NOT named here is
# "no fixture" -- a new location is automatically excluded from all three rather
# than silently inheriting a hearth. ``validate_data`` checks every name is a real
# indoor location, which is what catches a typo or a renamed/removed location.

#: Interiors where an open fireplace or wood stove is plausible: homes and
#: lounge-like hospitality, not shops, clinics or offices.
HEARTH_LOCATIONS: frozenset[str] = frozenset([
    'modern open-concept living room', 'mid-century modern living room',
    'cozy farmhouse living room', 'bohemian eclectic living room',
    'minimalist Scandinavian living room', 'dark moody Victorian parlor',
    'cluttered grandparent living room',
    'upscale penthouse living room with city view', 'rustic log cabin interior',
    '1970s wood-paneled den', 'formal dining room with chandelier',
    'cozy home library', 'elegant hotel dining room',
    'fine dining restaurant interior', 'wood-paneled pub',
    'dimly lit cocktail lounge', 'wine bar with exposed brick',
    'speakeasy-style basement bar', 'gastropub with an open kitchen',
    'tea house with low wooden tables', 'grand hotel suite',
    'hotel lobby with marble floors', 'university library reading room',
    'public library with tall bookshelves',
])

#: Dim interiors with a screen throwing light: living spaces, lodging, bars with
#: a set on, and the handful of rooms that ARE banks of screens.
SCREEN_GLOW_LOCATIONS: frozenset[str] = frozenset([
    'modern open-concept living room', 'mid-century modern living room',
    'cozy farmhouse living room', 'bohemian eclectic living room',
    'minimalist Scandinavian living room', 'cluttered grandparent living room',
    'upscale penthouse living room with city view', '1970s wood-paneled den',
    'suburban basement', 'budget motel room', 'grand hotel suite',
    'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge',
    'hospital room', 'independent cinema auditorium',
    'arcade with glowing cabinets', 'mission control room with monitor banks',
    'university dormitory room', 'television studio control room',
])

#: Buildings that actually have stained or leaded coloured glass: places of
#: worship, civic and Victorian-era interiors, and the traditional public house.
STAINED_GLASS_LOCATIONS: frozenset[str] = frozenset([
    'grand cathedral interior', 'small chapel interior', 'mosque interior',
    'synagogue interior', 'city hall rotunda', 'dark moody Victorian parlor',
    'wood-paneled pub', 'hotel lobby with marble floors',
    'university library reading room', 'public library with tall bookshelves',
])

#: Places with an overhead stage RIG (0.83.0). The four studio backdrops are included
#: deliberately and are load-bearing: ``studio_stage`` is carved out of the family that
#: :data:`VOID_ALLOWED_LIGHTING` admits, so leaving them out would strip a void backdrop
#: of a value it legitimately had. ``outdoor amphitheater`` is why this fixture is
#: allowlisted across ALL locations rather than filed as indoor-only -- it is an outdoor
#: place with a real stage. ``concert hall backstage`` is deliberately absent: backstage
#: is not the stage.
STAGE_LOCATIONS: frozenset[str] = frozenset([
    *STUDIO_BACKDROPS,
    'photography studio with backdrop', 'empty theater stage with the curtain up',
    'outdoor amphitheater', 'community theatre auditorium',
    'independent cinema auditorium', 'neon-lit nightclub',
    'karaoke room with song menus', 'dance studio with mirrors',
    'high school gymnasium',
])

#: {fixture lighting value -> the locations that have that fixture}. Consumed by
#: data/constraints.py, which turns it into one exclusion rule per location listing
#: whichever fixtures that location lacks.
#:
#: **The loop covers every location, not just the indoor ones (0.83.0).** The first three
#: fixtures are also indoor-only, so for an outdoor location their rule is redundant with
#: the bucket rule -- harmless, since the engine unions every firing exclusion on a
#: target. Widening the loop is what lets ``studio_stage`` be allowlisted at
#: ``outdoor amphitheater`` while still being excluded from a forest trail, using the ONE
#: mechanism that already existed instead of a second one.
FIXTURE_LIGHTING: "OrderedDict[str, frozenset[str]]" = OrderedDict([
    ('flickering firelight from a hearth', HEARTH_LOCATIONS),
    ('flickering television glow in a dark room', SCREEN_GLOW_LOCATIONS),
    ('light through stained glass casting colors', STAINED_GLASS_LOCATIONS),
    ('stage spotlight from above', STAGE_LOCATIONS),
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


# =========================================================================
# Worn-item / garment-phrase text contracts (0.83.0)
# =========================================================================
# These patterns are assertions about DATA -- what a costume or garment phrase
# may and may not name -- so they live in the data layer with one source of
# truth. nodes/identity_forge.py imports them to drive suppression at render
# time; tests/validate_data.py imports them to gate the shipped corpus, which
# keeps that module free of any node-layer import (it must run without ComfyUI).

#: **The general rule ``_HAT_RE`` was a special case of (0.83.0).** If the resolved
#: ``outfit_description`` already NAMES a worn item, the separately-randomized field for
#: that item must not add a second one — "a gown … and diamond stud earrings" beside a
#: randomized "medium gold hoops" is two sets of earrings in one prose string.
#:
#: Until 0.83.0 the engine enforced this for headwear only, and the other five items were
#: patched **per entry**: 28 cosplayers hand-pin ``"necklace": "no necklace"`` because
#: their costume names a neck ornament. A per-entry workaround for a cross-field
#: contradiction means the general rule is missing — so here it is. The 28 pins STAY
#: (they are explicit, they cost nothing, and removing one would add an RNG draw where a
#: lock used to skip it and drift that character's seed). They are now belt-and-braces.
#:
#: **This does NOT reopen the 0.66.0 "has skin but wouldn't accessorise" decision.** That
#: one asked *may jewellery be worn over a costume* — answered yes, do not re-flag. This
#: asks *does the costume text already name this item*. Only the named field is dropped;
#: every other jewellery field still draws, so a character whose costume names earrings
#: can still get a necklace.
#:
#: Scope note, so the effect is not overclaimed: ``bag`` is ALREADY dropped for every
#: cosplayer/archetype by ``_COSTUME_SUPPRESSED_EXTRAS`` (a locked outfit suppresses the
#: carried extras wholesale), so the ``bag`` pattern only bites on an engine-GENERATED
#: outfit. The five jewellery fields are the ones this genuinely fixes on the roster
#: (~169 entries at 0.83.0), because jewellery is deliberately absent from that set.
#:
#: Every pattern below is tuned against real roster text; the traps are load-bearing and
#: ``WornItemDeduplicationTests`` pins each one:
#:   * ``rings`` must not fire on "earrings" (no word boundary inside the word), nor on a
#:     PIERCING ("brow ring", "lip ring") or a non-jewellery ring ("tire ring", "halo
#:     ring", "neck ring", "arm ring") — hence the fixed-width negative lookbehinds.
#:   * ``bracelet`` must never match a bare "cuff": "cuffed chinos", "rolled-cuff jeans",
#:     "ear cuff" and "arm cuff" are all real roster text and none is a bracelet.
#:   * ``earrings`` must not fire on garment "studs" (Simon's gold-studded trench coat),
#:     so a bare ``studs`` is deliberately NOT in the pattern — "stud earrings" is.
#:   * ``bag`` must not fire on "baggy jeans" (safe: no boundary at "bag|gy"), and
#:     ``clutch`` must not fire on the VERB ("arms raised to clutch the head" — Psyduck).
WORN_ITEM_RES: "OrderedDict[str, re.Pattern[str]]" = OrderedDict([
    ("necklace", re.compile(
        r"\b(?:necklaces?|pendants?|chokers?|torcs?|torque|medallions?|amulets?|"
        r"lockets?|dog tags|rosary)\b",
        re.IGNORECASE)),
    ("earrings", re.compile(
        r"\b(?:earrings?|ear studs|stud earrings|hoops)\b",
        re.IGNORECASE)),
    ("rings", re.compile(
        r"(?<!nose )(?<!brow )(?<!lip )(?<!ear )(?<!arm )(?<!neck )(?<!tire )"
        r"(?<!halo )(?<!septum )\brings?\b",
        re.IGNORECASE)),
    ("bracelet", re.compile(
        r"\b(?:bracelets?|bangles?|wrist cuffs?|wristbands?)\b",
        re.IGNORECASE)),
    ("other_jewelry", re.compile(
        r"\b(?:anklets?|arm cuffs?|body chains?|brooch(?:es)?|waist chains?)\b",
        re.IGNORECASE)),
    ("bag", re.compile(
        r"\b(?:bags?|totes?|backpacks?|purses?|satchels?|handbags?)\b"
        r"|\bclutch(?:es)?\b(?!\s+(?:the|his|her|their|its|at|onto))",
        re.IGNORECASE)),
])

#: --- The wardrobe axis (0.83.0) -----------------------------------------------------
#:
#: ``footwear`` / ``clothing_color`` / ``clothing_pattern`` were drawn every render and
#: never voiced, because ``OUTFIT_DESCRIPTIONS`` superseded them and nobody retired them.
#: They now compose with the generated outfit (see ``_compose_outfit_clause``). The four
#: patterns below are the BACK-COMPAT half of that change.
#:
#: A ``user_options.json`` "outfits" section can register outfit strings, and any that
#: already exist were written for the OLD contract: leading article, baked-in shoes and
#: colours. Composing blindly onto those would produce "a jewel-toned a sleek white EVA
#: suit ... in loafers" beside its own magnetic boots. Each guard fires EXACTLY in the
#: collision case — when the string already names the thing — so a user's existing data
#: degrades gracefully instead of breaking. The rewritten shipped corpus matches none of
#: them, which ``validate_data.py`` enforces, so for shipped data every guard is inert.
#:
#: ``SHOE_RE`` does double duty: it is also the validator gate, so one pattern both
#: protects user strings and keeps the corpus honest.
#: Deliberately PLURAL-ONLY for the ambiguous stems, because every ``footwear`` pool
#: value is plural and the singular forms collide with real garment vocabulary:
#: "oxford shirt" (a fabric), "flat-front trousers", "bootcut jeans", "a boot-lace tie".
#: The first draft matched ``oxfords?`` / ``flats?`` / ``boots?`` and false-positived on
#: five shipped garment phrases, silently deleting their footwear clause. ``barefoot`` and
#: the "<x> shoes" forms are the only singulars kept, and both are unambiguous.
SHOE_RE = re.compile(
    r"\b(?:shoes|sneakers|trainers|boots|booties|heels|pumps|loafers|flats|sandals|"
    r"oxfords|slippers|wedges|mules|clogs|derbies|brogues|espadrilles|moccasins|"
    r"stilettos|slingbacks|slides|cleats|high tops|mary janes|barefoot|bare feet)\b",
    re.IGNORECASE,
)
#: Colour words that mean a garment phrase already states its own palette. Deliberately
#: broad: a false positive only costs one clause, a false negative ships a contradiction.
COLOUR_WORD_RE = re.compile(
    r"\b(?:black|white|cream|ivory|navy|blue|red|green|pink|purple|violet|lavender|"
    r"yellow|orange|brown|tan|beige|khaki|olive|grey|gray|charcoal|silver|gold|golden|"
    r"burgundy|maroon|crimson|scarlet|emerald|sage|teal|turquoise|mustard|rust|camel|"
    r"blush|champagne|ruby|amber|copper|bronze|indigo|magenta|coral|peach|mint|"
    r"monochrome|pastel|neon|metallic|two-tone|color-blocked|colour-blocked)\b",
    re.IGNORECASE,
)
#: Pattern / fabric-pattern words that mean the garment phrase already states its own.
PATTERN_WORD_RE = re.compile(
    r"\b(?:striped?|stripes|pinstripe[ds]?|plaid|tartan|check(?:ed|s)?|houndstooth|"
    r"floral|paisley|polka[- ]dot(?:ted|s)?|animal print|leopard|zebra|snakeskin|"
    r"camo(?:uflage)?|geometric|abstract|argyle|herringbone|tie-dye|denim|graphic|"
    r"patterned|printed|sequined|sequin)\b",
    re.IGNORECASE,
)
#: Leading article stripped from a garment phrase before the palette adjective is
#: prefixed. The shipped corpus carries none; this exists for user-supplied strings.
LEADING_ARTICLE_RE = re.compile(r"^(?:a|an|the)\s+", re.IGNORECASE)

# Merge optional user-supplied options (./user_options.json in the pack root).
# Kept last so it can extend any pool above; fails closed if absent/malformed.
# OUTFIT_DESCRIPTIONS is passed so the "outfits" section can register new outfit
# styles together with their garment text.
from .user_options import apply_user_options  # noqa: E402

apply_user_options(FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS)
