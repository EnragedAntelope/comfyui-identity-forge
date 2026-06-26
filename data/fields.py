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
    ("face_shape", {
        "group": 'Face',
        "female_options": ['oval', 'round', 'soft round', 'square', 'soft square', 'heart-shaped', 'diamond', 'oblong', 'rectangular', 'wide with high forehead', 'narrow and angular'],
        "male_options": ['oval', 'round', 'soft round', 'square', 'soft square', 'heart-shaped', 'diamond', 'oblong', 'rectangular', 'wide with high forehead', 'narrow and angular'],
        "optional": False
    }),
    ("eye_color", {
        "group": 'Face',
        "female_options": ['pale blue', 'ice blue', 'bright blue', 'deep blue', 'blue-gray', 'gray', 'dark gray', 'green', 'bright green', 'emerald', 'hazel', 'warm hazel', 'light brown', 'medium brown', 'dark brown', 'nearly black', 'amber', 'golden brown', 'violet-gray'],
        "male_options": ['pale blue', 'ice blue', 'bright blue', 'deep blue', 'blue-gray', 'gray', 'dark gray', 'green', 'bright green', 'emerald', 'hazel', 'warm hazel', 'light brown', 'medium brown', 'dark brown', 'nearly black', 'amber', 'golden brown', 'violet-gray'],
        "optional": False
    }),
    ("eye_shape", {
        "group": 'Face',
        "female_options": ['almond', 'round', 'slightly hooded', 'hooded', 'upturned', 'downturned', 'monolid', 'deep-set', 'wide-set', 'close-set', 'large and expressive', 'small and delicate'],
        "male_options": ['almond', 'round', 'slightly hooded', 'hooded', 'upturned', 'downturned', 'monolid', 'deep-set', 'wide-set', 'close-set', 'large and expressive', 'small and delicate'],
        "optional": False
    }),
    ("nose", {
        "group": 'Face',
        "female_options": ['small and button', 'small and upturned', 'straight', 'slightly upturned', 'aquiline', 'Roman', 'broad', 'wide', 'narrow and refined', 'slightly crooked', 'prominent', 'petite', 'snub', 'wide with flared nostrils'],
        "male_options": ['small and button', 'small and upturned', 'straight', 'slightly upturned', 'aquiline', 'Roman', 'broad', 'wide', 'narrow and refined', 'slightly crooked', 'prominent', 'petite', 'snub', 'wide with flared nostrils'],
        "optional": False
    }),
    ("lips", {
        "group": 'Face',
        "female_options": ['very thin', 'thin', 'average', 'slightly full', 'full', 'very full', 'plump', 'bow-shaped', 'heart-shaped', 'wide and full', 'petite and defined', 'uneven slightly asymmetric'],
        "male_options": ['very thin', 'thin', 'average', 'slightly full', 'full', 'very full', 'plump', 'bow-shaped', 'heart-shaped', 'wide and full', 'petite and defined', 'uneven slightly asymmetric'],
        "optional": False
    }),
    ("cheekbones", {
        "group": 'Face',
        "female_options": ['very high and prominent', 'high and defined', 'high and soft', 'prominent', 'softly prominent', 'average', 'wide and flat', 'subtle', 'barely defined'],
        "male_options": ['very high and prominent', 'high and defined', 'high and soft', 'prominent', 'softly prominent', 'average', 'wide and flat', 'subtle', 'barely defined'],
        "optional": False
    }),
    ("jawline", {
        "group": 'Face',
        "female_options": ['sharp and defined', 'strong', 'square', 'slightly square', 'soft', 'rounded', 'delicate', 'narrow', 'wide', 'tapered', 'prominent'],
        "male_options": ['sharp and defined', 'strong', 'square', 'slightly square', 'soft', 'rounded', 'delicate', 'narrow', 'wide', 'tapered', 'prominent'],
        "optional": False
    }),
    ("chin", {
        "group": 'Face',
        "female_options": ['rounded', 'softly pointed', 'pointed', 'slightly cleft', 'cleft', 'wide', 'narrow', 'small and delicate', 'receding', 'strong and square'],
        "male_options": ['rounded', 'softly pointed', 'pointed', 'slightly cleft', 'cleft', 'wide', 'narrow', 'small and delicate', 'receding', 'strong and square'],
        "optional": False
    }),
    ("eyebrows", {
        "group": 'Face',
        "female_options": ['thin and arched', 'thin and straight', 'pencil thin', 'barely there', 'natural full', 'thick and straight', 'thick and arched', 'bushy', 'feathered', 'well defined and arched', 'bleached', 'bold statement brows', 'laminated brows'],
        "male_options": ['thin and arched', 'thin and straight', 'pencil thin', 'barely there', 'natural full', 'thick and straight', 'thick and arched', 'bushy', 'feathered', 'well defined and arched', 'bleached', 'bold statement brows', 'laminated brows'],
        "optional": False
    }),
    ("skin_details", {
        "group": 'Face',
        # Distinguishing marks / texture only. Freckles are owned solely by the
        # freckles_density field (no double-sourcing); skin-finish words live in
        # complexion. The 'no notable marks' token is the absent value driven by
        # accessory_density via _EXTRA_ABSENCE, so most faces carry no mark.
        "female_options": ['no notable marks', 'porcelain smooth', 'lightly textured', 'mole above lip', 'beauty mark on cheek', 'birthmark on neck', 'small scar on chin', 'dimples when smiling', 'laugh lines'],
        "male_options": ['no notable marks', 'porcelain smooth', 'lightly textured', 'mole above lip', 'beauty mark on cheek', 'birthmark on neck', 'small scar on chin', 'dimples when smiling', 'laugh lines'],
        "optional": True
    }),
    ("hair_color", {
        "group": 'Hair',
        "female_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "male_options": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips'],
        "optional": False, "natural_hair_colors": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair'], "full_spectrum_hair_colors": ['platinum blonde', 'white blonde', 'golden blonde', 'dirty blonde', 'strawberry blonde', 'light blonde', 'dark blonde', 'auburn', 'copper', 'bright red', 'deep red', 'light chestnut', 'chestnut', 'warm brown', 'medium brown', 'ash brown', 'dark brown', 'near black', 'jet black', 'raven black', 'salt and pepper', 'silver', 'white', 'charcoal gray', 'gray-streaked dark hair', 'hot pink', 'baby pink', 'magenta', 'lavender', 'purple', 'deep purple', 'electric blue', 'navy blue', 'teal', 'mint green', 'emerald green', 'lime green', 'orange', 'coral', 'yellow', 'platinum white', 'rose gold', 'iridescent', 'rainbow ombre', 'black with colored tips']
    }),
    ("hair_length", {
        "group": 'Hair',
        "female_options": ['buzzed very short', 'very short', 'short pixie', 'ear length', 'chin length bob', 'jaw length', 'shoulder length', 'slightly past shoulders', 'mid back', 'lower back', 'long', 'very long', 'waist length', 'hip length'],
        "male_options": ['buzzed very short', 'very short', 'short pixie', 'ear length', 'chin length bob', 'jaw length', 'shoulder length', 'slightly past shoulders', 'mid back', 'lower back', 'long', 'very long', 'waist length', 'hip length'],
        "optional": False
    }),
    ("hair_texture", {
        "group": 'Hair',
        "female_options": ['pin straight', 'sleek straight', 'slightly wavy', 'loosely wavy', 'wavy', 'beachy waves', 'loosely curled', 'softly curled', 'curly', 'tightly curled', 'coily', 'kinky coily', 'fine and wispy', 'thick and voluminous'],
        "male_options": ['pin straight', 'sleek straight', 'slightly wavy', 'loosely wavy', 'wavy', 'beachy waves', 'loosely curled', 'softly curled', 'curly', 'tightly curled', 'coily', 'kinky coily', 'fine and wispy', 'thick and voluminous'],
        "optional": False
    }),
    ("hair_style", {
        "group": 'Hair',
        "female_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled'],
        "male_options": ['worn down', 'half up half down', 'high ponytail', 'low ponytail', 'side ponytail', 'messy bun', 'sleek bun', 'top knot', 'chignon', 'side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs', 'space buns', 'pigtails', 'braided pigtails', 'bantu knots', 'afro', 'twist-out', 'updo', 'French twist', 'slicked back', 'curtain bangs', 'blunt bangs', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled'],
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
        # pool union) for "Any"/manual stylized looks.
        "male_options": ['no makeup', 'no makeup', 'barely there natural makeup', 'soft natural makeup', 'fresh-faced dewy look', 'classic no-makeup makeup'],
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
    ("lips_makeup", {
        "group": 'Makeup',
        "female_options": ['bare natural lips', 'tinted lip balm', 'nude lipstick', 'MLBB lipstick', 'coral', 'pink', 'classic red', 'deep red', 'berry', 'plum', 'mauve', 'brown nude', 'dark brown', 'glossy clear', 'high shine gloss', 'ombre lip'],
        "male_options": ['bare natural lips', 'tinted lip balm', 'nude lipstick', 'MLBB lipstick', 'coral', 'pink', 'classic red', 'deep red', 'berry', 'plum', 'mauve', 'brown nude', 'dark brown', 'glossy clear', 'high shine gloss', 'ombre lip'],
        "optional": False
    }),
    ("blush", {
        "group": 'Makeup',
        "female_options": ['no blush', 'barely there flush', 'soft pink blush', 'peach blush', 'coral blush', 'rosy blush', 'warm terra cotta', 'bronzed sun-kissed', 'light draping blush', 'heavy editorial blush', 'monochromatic blush and eyeshadow'],
        "male_options": ['no blush', 'barely there flush', 'soft pink blush', 'peach blush', 'coral blush', 'rosy blush', 'warm terra cotta', 'bronzed sun-kissed', 'light draping blush', 'heavy editorial blush', 'monochromatic blush and eyeshadow'],
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
        "female_options": ['no earrings', 'small gold studs', 'small silver studs', 'pearl studs', 'diamond studs', 'small gold hoops', 'medium gold hoops', 'large bold gold hoops', 'silver hoops', 'chandelier earrings', 'long drop earrings', 'tassel earrings', 'mismatched earrings', 'clip-on pearl earrings'],
        "male_options": ['no earrings', 'small gold studs', 'small silver studs', 'pearl studs', 'diamond studs', 'small gold hoops', 'medium gold hoops', 'large bold gold hoops', 'silver hoops', 'chandelier earrings', 'long drop earrings', 'tassel earrings', 'mismatched earrings', 'clip-on pearl earrings'],
        "optional": False
    }),
    ("necklace", {
        "group": 'Jewelry & Nails',
        "female_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'nothing but a subtle chain'],
        "male_options": ['no necklace', 'delicate gold chain', 'layered gold chains', 'pearl necklace', 'pearl strand', 'diamond pendant', 'gemstone pendant', 'cross necklace', 'locket necklace', 'choker', 'velvet choker', 'statement necklace', 'collar necklace', 'nothing but a subtle chain'],
        "optional": False
    }),
    ("other_jewelry", {
        "group": 'Jewelry & Nails',
        "female_options": ['no other jewelry', 'simple gold bracelet', 'silver cuff bracelet', 'stacked bracelets', 'thin rings on multiple fingers', 'cocktail ring', 'plain band ring', 'watch', 'layered rings'],
        "male_options": ['no other jewelry', 'simple gold bracelet', 'silver cuff bracelet', 'stacked bracelets', 'thin rings on multiple fingers', 'cocktail ring', 'plain band ring', 'watch', 'layered rings'],
        "optional": False
    }),
    ("piercings", {
        "group": 'Jewelry & Nails',
        "female_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing'],
        "male_options": ['no piercings beyond ears', 'nose stud', 'small septum ring', 'multiple ear piercings', 'industrial earring', 'tragus piercing', 'helix piercing'],
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
        "female_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'watch', 'smart watch', 'long pendant necklace layered over outfit', 'reading glasses pushed up on head', 'woven hat'],
        "male_options": ['no accessories', 'classic black sunglasses', 'cat eye sunglasses', 'round sunglasses', 'aviator sunglasses', 'wide brim sun hat', 'baseball cap', 'beret', 'silk neck scarf', 'belt cinching waist', 'western belt', 'watch', 'smart watch', 'long pendant necklace layered over outfit', 'reading glasses pushed up on head', 'woven hat'],
        "optional": False
    }),
    ("expression", {
        "group": 'Setting & Shot',
        "female_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious'],
        "male_options": ['neutral', 'relaxed', 'subtle soft smile', 'warm smile', 'bright smile', 'wide toothy grin', 'laughing', 'pensive and thoughtful', 'serious', 'confident', 'intense gaze', 'playful', 'sultry', 'serene', 'slightly bashful', 'candid mid-laugh', 'smirking', 'determined', 'surprised', 'contemplative', 'wistful', 'flirtatious', 'stern', 'curious'],
        "optional": False
    }),
    ("location", {
        "group": 'Setting & Shot',
        "female_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'server room with blinking lights', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace at dusk', 'sandy beach at golden hour', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'desert dune at sunset', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas', 'harbor dock at sunrise', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'street food market at night', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop'],
        "male_options": ['modern open-concept living room', 'mid-century modern living room', 'cozy farmhouse living room', 'bohemian eclectic living room', 'minimalist Scandinavian living room', 'dark moody Victorian parlor', 'cluttered grandparent living room', 'upscale penthouse living room with city view', 'rustic log cabin interior', '1970s wood-paneled den', 'sunny suburban kitchen', 'sleek modern kitchen with marble countertops', 'retro diner-style kitchen', 'cramped apartment kitchenette', 'farmhouse kitchen with open shelving', 'formal dining room with chandelier', 'mid-century dining room', 'casual breakfast nook', 'elegant hotel dining room', 'small-town family diner', 'cozy corner coffee shop', 'upscale urban cafe', 'busy chain coffee shop', 'old-school greasy spoon', 'fine dining restaurant interior', 'dim sum restaurant', 'sushi bar counter', 'crowded bar and grill', 'wood-paneled pub', 'dimly lit cocktail lounge', 'neon-lit nightclub', 'wine bar with exposed brick', 'speakeasy-style basement bar', 'neighborhood pharmacy', 'small-town grocery store aisle', 'big box store warehouse aisle', 'corner bodega', 'upscale grocery market deli counter', 'farmers market indoor stall', 'cluttered antique shop', 'indie record store', 'cozy bookstore with reading nooks', 'dusty second-hand thrift store', 'luxury retail boutique', 'hair salon', 'nail salon', 'old-school barbershop', 'tattoo parlor', 'laundromat', 'local gym weight room', 'yoga studio with wood floors', 'indoor swimming pool', 'bowling alley', 'roller skating rink', 'high school gymnasium', 'university lecture hall', 'elementary school classroom', 'university library reading room', 'public library with tall bookshelves', 'cozy home library', 'museum gallery with white walls', 'natural history museum hall', 'art gallery opening night', 'grand cathedral interior', 'small chapel interior', 'mosque interior', 'synagogue interior', 'hospital room', 'hospital waiting room', "doctor's examination room", 'emergency room', 'corporate open office', 'corner executive office', 'co-working space', 'cubicle farm', 'server room with blinking lights', 'factory floor', 'warehouse interior', 'police station bullpen', 'courtroom', 'hotel lobby with marble floors', 'grand hotel suite', 'budget motel room', 'airport departure gate', 'train station waiting area', 'subway car interior', 'parking garage', 'movie theater lobby', 'backstage dressing room', 'concert hall backstage', 'recording studio', 'photography studio with backdrop', 'home garage workshop', 'suburban basement', 'cluttered home attic', 'sunlit sunroom', 'mudroom entryway', 'sunny city park', 'tree-lined boulevard', 'cobblestone old-town street', 'rooftop terrace at dusk', 'sandy beach at golden hour', 'rocky coastal cliff', 'forest trail', 'mountain overlook', 'desert dune at sunset', 'snowy pine forest', 'autumn park with falling leaves', 'flower field in bloom', 'sunlit vineyard', 'lavender field', 'quiet suburban backyard', 'urban alley with graffiti', 'neon-lit city street at night', 'rainy street with umbrellas', 'harbor dock at sunrise', 'riverside boardwalk', 'botanical garden path', 'open meadow', 'lakeside pier', 'misty moor', 'cherry blossom grove', 'crumbling stone ruin', 'rooftop garden', 'busy city crosswalk', 'country dirt road', 'palm-lined promenade', 'stone bridge over a river', 'castle courtyard', 'outdoor amphitheater', 'poolside cabana', 'street food market at night', 'seamless grey studio backdrop', 'solid white studio backdrop', 'solid black studio backdrop', 'chroma-key green screen backdrop'],
        "optional": False
    }),
    ("lighting", {
        "group": 'Setting & Shot',
        "female_options": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'soft window light from the side', 'backlit silhouette against bright window', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'warm candlelight', 'warm incandescent lamp glow', 'cool LED overhead lighting', 'harsh fluorescent lighting', 'warm string lights bokeh background', 'neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'stage spotlight from above', 'dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'Dutch angle with hard shadows', 'soft-box style diffused light', 'moonlight with cool blue tones', 'fog-diffused streetlamp glow', 'fire and flame warm flicker', 'light through venetian blinds casting stripes', 'light through stained glass casting colors', 'reflection off wet pavement', 'golden bokeh lights in background'],
        "male_options": ['golden hour sunlight', 'late afternoon warm sunlight', 'soft morning light', 'harsh overhead midday sun', 'overcast diffused daylight', 'hazy overcast winter light', 'blue hour twilight', 'pre-dawn darkness with ambient glow', 'dramatic stormy sky light', 'sun rays through broken cloud cover', 'dappled sunlight through forest canopy', 'soft window light from the side', 'backlit silhouette against bright window', 'direct sunlight from behind camera', 'rim lighting from setting sun', 'warm candlelight', 'warm incandescent lamp glow', 'cool LED overhead lighting', 'harsh fluorescent lighting', 'warm string lights bokeh background', 'neon sign glow in multiple colors', 'single neon light from one side', 'club strobe lighting', 'stage spotlight from above', 'dramatic single overhead spotlight', 'soft studio three-point lighting', 'high key bright even lighting', 'low key moody single light source', 'dramatic chiaroscuro side lighting', 'Dutch angle with hard shadows', 'soft-box style diffused light', 'moonlight with cool blue tones', 'fog-diffused streetlamp glow', 'fire and flame warm flicker', 'light through venetian blinds casting stripes', 'light through stained glass casting colors', 'reflection off wet pavement', 'golden bokeh lights in background'],
        "optional": False
    }),
    ("shot_type", {
        "group": 'Setting & Shot',
        "female_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'over-the-shoulder perspective', 'shot through a doorway frame', 'shot through a window from outside', 'shot through foreground foliage', 'reflected in a mirror', 'reflected in a shop window', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
        "male_options": ['extreme close-up on face', 'close-up portrait', 'medium close-up from chest up', 'medium shot from waist up', 'cowboy shot from mid-thigh up', 'full body shot', 'full body shot with environment visible', 'wide shot with subject at center', 'wide shot with subject off-center', 'extreme wide establishing shot', 'straight-on eye level', 'slightly above eye level', 'high angle looking down', "steep overhead bird's-eye view", 'low angle looking up', "worm's-eye view from ground", 'slight Dutch angle', 'three-quarter angle facing left', 'three-quarter angle facing right', 'side profile', 'from slightly behind and to the side', 'view from directly behind', 'over-the-shoulder perspective', 'shot through a doorway frame', 'shot through a window from outside', 'shot through foreground foliage', 'reflected in a mirror', 'reflected in a shop window', 'fish-eye wide lens distortion', 'telephoto compressed perspective'],
        "optional": False
    }),
    ("forehead", {
        "group": 'Face',
        "female_options": ['high and broad', 'low and broad', 'average', 'narrow', 'rounded', 'prominent brow ridge', 'smooth'],
        "male_options": ['high and broad', 'low and broad', 'average', 'narrow', 'rounded', 'prominent brow ridge', 'smooth'],
        "optional": False
    }),
    ("eye_size", {
        "group": 'Face',
        "female_options": ['large', 'medium', 'small', 'almond medium', 'doe-like', 'deep set'],
        "male_options": ['large', 'medium', 'small', 'almond medium', 'doe-like', 'deep set'],
        "optional": False
    }),
    ("eyelid_type", {
        "group": 'Face',
        "female_options": ['double eyelid', 'monolid', 'hooded', 'slightly hooded', 'creased', 'tapered crease'],
        "male_options": ['double eyelid', 'monolid', 'hooded', 'slightly hooded', 'creased', 'tapered crease'],
        "optional": False
    }),
    ("lip_color", {
        "group": 'Face',
        "female_options": ['pale pink', 'rose', 'coral', 'berry', 'red', 'nude', 'brown', 'mauve', 'plum'],
        "male_options": ['pale pink', 'rose', 'coral', 'berry', 'red', 'nude', 'brown', 'mauve', 'plum'],
        "optional": False
    }),
    ("teeth_visibility", {
        "group": 'Face',
        "female_options": ['closed lips', 'slight part', 'teeth showing', 'broad smile showing teeth'],
        "male_options": ['closed lips', 'slight part', 'teeth showing', 'broad smile showing teeth'],
        "optional": False
    }),
    ("smile_type", {
        "group": 'Face',
        "female_options": ['closed mouth', 'soft smile', 'toothy grin', 'asymmetric', 'broad', 'subtle dimpled'],
        "male_options": ['closed mouth', 'soft smile', 'toothy grin', 'asymmetric', 'broad', 'subtle dimpled'],
        "optional": False
    }),
    ("freckles_density", {
        "group": 'Face',
        "female_options": ['none', 'few', 'scattered', 'moderate', 'heavy', 'all-over'],
        "male_options": ['none', 'few', 'scattered', 'moderate', 'heavy', 'all-over'],
        "optional": False
    }),
    ("complexion", {
        "group": 'Face',
        # Skin finish / undertone (always rendered). 'olive' removed: it collided
        # with the skin_tone field's 'olive'. Texture words live in skin_details.
        "female_options": ['clear', 'rosy', 'sallow', 'ruddy', 'peaches and cream', 'matte', 'dewy'],
        "male_options": ['clear', 'rosy', 'sallow', 'ruddy', 'peaches and cream', 'matte', 'dewy'],
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
    ("muscle_definition", {
        "group": 'Body',
        "female_options": ['soft', 'lightly toned', 'defined', 'cut', 'very muscular', 'lean'],
        "male_options": ['soft', 'lightly toned', 'defined', 'cut', 'very muscular', 'lean'],
        "optional": False
    }),
    ("hair_part", {
        "group": 'Hair',
        "female_options": ['center part', 'side part', 'deep side part', 'no part', 'zigzag part', 'diagonal'],
        "male_options": ['center part', 'side part', 'deep side part', 'no part', 'zigzag part', 'diagonal'],
        "optional": False
    }),
    ("hair_volume", {
        "group": 'Hair',
        "female_options": ['flat', 'slight volume', 'medium volume', 'voluminous', 'big hair', 'thick'],
        "male_options": ['flat', 'slight volume', 'medium volume', 'voluminous', 'big hair', 'thick'],
        "optional": False
    }),
    ("hair_highlights", {
        "group": 'Hair',
        "female_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips'],
        "male_options": ['none', 'subtle balayage', 'chunky highlights', 'face framing', 'ombre', 'sombre', 'frosted tips'],
        "optional": False
    }),
    ("eyebrow_makeup", {
        "group": 'Makeup',
        "female_options": ['none', 'filled in', 'feathered', 'bold sculpted', 'laminated look', 'tinted'],
        "male_options": ['none', 'filled in', 'feathered', 'bold sculpted', 'laminated look', 'tinted'],
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
        "female_options": ['none', 'subtle glow', 'dewy high points', 'strobing', 'glitter highlight', 'inner corner'],
        "male_options": ['none', 'subtle glow', 'dewy high points', 'strobing', 'glitter highlight', 'inner corner'],
        "optional": False
    }),
    ("rings", {
        "group": 'Jewelry & Nails',
        "female_options": ['none', 'simple band', 'stacked thin bands', 'statement ring', 'signet ring', 'delicate gemstone'],
        "male_options": ['none', 'simple band', 'stacked thin bands', 'statement ring', 'signet ring', 'delicate gemstone'],
        "optional": False
    }),
    ("bracelet", {
        "group": 'Jewelry & Nails',
        "female_options": ['none', 'tennis bracelet', 'chain bracelet', 'cuff', 'beaded bracelet', 'charm bracelet'],
        "male_options": ['none', 'tennis bracelet', 'chain bracelet', 'cuff', 'beaded bracelet', 'charm bracelet'],
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
        "female_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'barefoot'],
        "male_options": ['sneakers', 'loafers', 'boots', 'heels', 'flats', 'sandals', 'oxfords', 'slippers', 'barefoot'],
        "optional": False
    }),
    ("clothing_color", {
        "group": 'Clothing',
        "female_options": ['neutral tones', 'black monochrome', 'white and cream', 'earth tones', 'pastels', 'bold primary colors', 'jewel tones', 'all black', 'all white', 'mixed prints'],
        "male_options": ['neutral tones', 'black monochrome', 'white and cream', 'earth tones', 'pastels', 'bold primary colors', 'jewel tones', 'all black', 'all white', 'mixed prints'],
        "optional": False
    }),
    ("clothing_pattern", {
        "group": 'Clothing',
        "female_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim'],
        "male_options": ['solid', 'subtle texture', 'stripes', 'plaid', 'floral', 'animal print', 'geometric', 'abstract', 'camouflage', 'denim'],
        "optional": False
    }),
    ("time_of_day", {
        "group": 'Setting & Shot',
        "female_options": ['early morning', 'mid morning', 'noon', 'afternoon', 'golden hour', 'twilight', 'night', 'late night'],
        "male_options": ['early morning', 'mid morning', 'noon', 'afternoon', 'golden hour', 'twilight', 'night', 'late night'],
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
        "female_options": ['cheerful', 'melancholic', 'mysterious', 'confident', 'dreamy', 'tense', 'serene', 'playful', 'intense'],
        "male_options": ['cheerful', 'melancholic', 'mysterious', 'confident', 'dreamy', 'tense', 'serene', 'playful', 'intense'],
        "optional": False
    }),
    ("pose", {
        "group": 'Setting & Shot',
        # Phrased to read after "{subject} is …"; avoid pronouns so gender stays
        # correct ("a hand", not "their hand").
        "female_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'arms relaxed at the sides', 'one hand touching the collar'],
        "male_options": ['standing naturally', 'standing with arms crossed', 'leaning against a wall', 'sitting relaxed', 'sitting upright', 'looking over one shoulder', 'walking mid-stride', 'crouching low', 'kneeling gracefully', 'reclining', 'posing with a hand on one hip', 'posing with hands in pockets', 'glancing back', 'in a relaxed contrapposto stance', 'in a confident power pose', 'resting chin on one hand', 'arms relaxed at the sides', 'one hand touching the collar'],
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
    ("loose", {"weight": 6, "variants": ['worn down', 'slicked back', 'wet look', 'windswept', 'freshly blown out', 'natural and unstyled']}),
    ("half-up", {"weight": 1, "variants": ['half up half down']}),
    ("ponytail", {"weight": 2, "variants": ['high ponytail', 'low ponytail', 'side ponytail']}),
    ("bun", {"weight": 5, "variants": ['messy bun', 'sleek bun', 'top knot', 'chignon', 'updo', 'French twist']}),
    ("braid", {"weight": 9, "variants": ['side braid', 'fishtail braid', 'French braid', 'dutch braids', 'crown braid', 'waterfall braid', 'loose braids', 'box braids', 'cornrows', 'locs']}),
    ("knots", {"weight": 2, "variants": ['space buns', 'bantu knots']}),
    ("pigtails", {"weight": 1, "variants": ['pigtails', 'braided pigtails']}),
    ("texture", {"weight": 2, "variants": ['afro', 'twist-out']}),
    ("bangs", {"weight": 2, "variants": ['curtain bangs', 'blunt bangs']}),
])

#: Outfit descriptions keyed by outfit_style, split into gendered buckets.
#: The engine draws from ``unisex`` plus the bucket(s) selected by the wardrobe
#: control, so a black-tie gown never lands on a male subject by default — yet a
#: user can deliberately mix wardrobes for diversity.
OUTFIT_DESCRIPTIONS: dict[str, dict[str, list[str]]] = {
    "casual": {
        "female": ['cropped hoodie with high waisted joggers and running shoes', 'fitted ribbed tank with mom jeans and white sneakers', 'oversized cream sweater with high waisted straight leg jeans and canvas sneakers', 'flowy floral sundress with white sneakers and a denim jacket', 'cropped cardigan over a camisole with wide leg jeans and loafers'],
        "male": ['plaid flannel shirt with dark jeans and brown leather boots', 'striped long sleeve shirt with navy chinos and clean white sneakers', 'relaxed linen button-up with khaki shorts and leather sandals', 'henley shirt with corduroy pants and desert boots', 'crewneck sweatshirt with slim jeans and skate shoes'],
        "unisex": ['white fitted tee with light wash jeans, white sneakers, and a denim jacket', 'black graphic tee with distressed jeans and chunky boots', 'vintage band tee with cutoff shorts and combat boots', 'denim overalls over a fitted long sleeve with canvas sneakers'],
    },
    "smart casual": {
        "female": ['structured blazer over a silk blouse with straight leg trousers and pointed flats', 'patterned midi dress with a cropped blazer and ankle boots', 'wrap blouse with a pencil skirt and block heel pumps', 'fine-knit turtleneck with pleated trousers and loafers'],
        "male": ['fitted navy blazer over a white oxford shirt with dark chinos and brown loafers', 'charcoal merino sweater over a collared shirt with tailored trousers and derby shoes', 'light blue button-down with tan chinos and suede loafers', 'tailored vest over a crisp white tee with wide leg trousers and loafers'],
        "unisex": ['cream knit polo with high waisted trousers and minimal leather sneakers', 'chambray shirt with tailored shorts and leather sandals'],
    },
    "business casual": {
        "female": ['fitted sheath dress with a thin belt and closed toe pumps', 'cardigan over a silk blouse with a knee length pencil skirt and low heels', 'patterned blouse tucked into an a-line skirt with modest heels', 'shift dress with a cropped jacket and classic pumps'],
        "male": ['navy blazer, light blue dress shirt, charcoal dress pants, and black leather loafers', 'gray trousers, white oxford, and burgundy loafers', 'turtleneck under a structured blazer with slim trousers and leather oxfords', 'dress shirt with cuffed sleeves, dark jeans, a leather belt, and loafers'],
        "unisex": ['tailored blazer with ankle length trousers and pointed toe flats', 'ponte blazer with matching trousers and minimal sneakers'],
    },
    "business formal": {
        "female": ['tailored black blazer and matching trousers with a silk blouse and closed toe pumps', 'navy pencil skirt suit with a cream shell top and pumps', 'double breasted blazer with wide leg trousers and a silk camisole', 'fitted black dress with a structured blazer, sheer tights, and pumps'],
        "male": ['black two piece suit with a white dress shirt, silk tie, and black oxfords', 'navy pinstripe suit with a pale blue shirt, burgundy tie, and brown oxfords', 'charcoal suit with a white spread collar shirt and black cap toe shoes', 'light gray suit with a white shirt, navy tie, and brown brogues'],
        "unisex": ['subtle houndstooth suit with a white shirt and dark tie', 'sharp black suit with a crisp white shirt and minimal accessories'],
    },
    "evening formal": {
        "female": ['floor length black velvet gown with delicate straps and diamond stud earrings', 'emerald green satin slip gown with strappy gold heels and a clutch', 'burgundy floor length dress with a deep v back and chandelier earrings', 'champagne sequined evening gown with a satin wrap and stiletto sandals', 'navy ball gown with a structured bodice, full skirt, and pearl drop earrings'],
        "male": ['classic black tuxedo with a crisp white shirt and black silk bow tie', 'midnight blue tuxedo with black satin lapels and patent leather shoes', 'white tie tailcoat with a wing collar shirt, white bow tie, and opera pumps', 'charcoal three piece suit with a black tie and oxford shoes', 'ivory dinner jacket with black trousers and a black bow tie'],
        "unisex": ['sleek black formal ensemble with satin detailing and polished dress shoes'],
    },
    "cocktail semi-formal": {
        "female": ['little black cocktail dress with lace overlay and black heels', 'burgundy wrap dress with gold hoop earrings and strappy heels', 'metallic midi dress with a draped neckline and minimalist sandals', 'deep green velvet wrap dress with a gold pendant necklace', 'sequined top with high waisted trousers and pointed heels'],
        "male": ['navy tailored suit with a light gray shirt and no tie', 'charcoal blazer with black dress pants and an open collar white shirt', 'black dress shirt with dark jeans and Chelsea boots', 'burgundy blazer over a black tee with tailored trousers and loafers'],
        "unisex": ['fitted blazer with a silk camisole and leather pants with heeled boots', 'white blazer over a pastel sheath with nude shoes'],
    },
    "streetwear": {
        "female": ['puffer jacket over a cropped top with biker shorts and platform sneakers', 'mesh top under a sports bra with baggy jeans and statement sneakers', 'oversized graphic tee dress with chunky sneakers and a crossbody bag', 'cropped bomber over a bralette with cargo pants and high tops'],
        "male": ['oversized hoodie with cargo pants and chunky sneakers', 'bomber jacket with a plain tee, ripped jeans, and skate shoes', 'boxy graphic tee with wide leg jeans, high top sneakers, and a chain necklace', 'baseball jersey over a turtleneck with loose jeans and bold sneakers'],
        "unisex": ['distressed denim jacket over a hoodie with joggers and retro sneakers', 'bucket hat, oversized sweatshirt, track pants, and designer sneakers', 'utility vest with layered long sleeves, tactical pants, and combat boots'],
    },
    "bohemian": {
        "female": ['flowing floral maxi dress with bell sleeves, leather sandals, and layered necklaces', 'off shoulder ruffled top with a tiered maxi skirt and leather sandals', 'crochet top with high waisted wide leg pants, a woven belt, and ankle boots', 'velvet burnout maxi dress with a wide brim hat and layered rings', 'embroidered peasant blouse with distressed denim shorts and gladiator sandals'],
        "male": ['embroidered linen tunic with drawstring trousers and leather sandals', 'open paisley shirt over a henley with flared cords and suede boots', 'fringed suede jacket over a plain tee with relaxed jeans and boots'],
        "unisex": ['kimono cardigan over a slip top with a fringe bag and beaded jewelry', 'patchwork layers with stacked bangles and hoop earrings', 'tie dye tee with flowy palazzo pants and espadrilles'],
    },
    "athletic": {
        "female": ['fitted sports bra with high waisted leggings, running shoes, and a zip hoodie', 'tennis skirt with a polo shirt, court shoes, and a visor', 'yoga pants with a cropped tank and grip socks', 'racerback tank with bike shorts and cross training shoes'],
        "male": ['moisture wicking tank with athletic shorts, trainers, and a sweatband', 'compression top with fitted shorts and cross training shoes', 'gym tee with basketball shorts, a baseball cap, and athletic sneakers', 'boxing tank with compression shorts and high top sneakers'],
        "unisex": ['tracksuit jacket with matching joggers and running shoes', 'windbreaker with leggings and trail running shoes', 'performance hoodie with joggers and cushioned trainers'],
    },
    "resort vacation": {
        "female": ['strapless floral sundress with a wide brim sun hat and wedge espadrilles', 'maxi skirt with a halter top, gold sandals, and a woven bag', 'sarong wrap with a bandeau swimsuit and shell jewelry', 'crochet cover up over a one piece swimsuit with a straw hat'],
        "male": ['linen camp shirt with tailored swim trunks and leather sandals', 'polo shirt with chino shorts and boat shoes', 'tropical print shirt with relaxed trousers and canvas slip ons', 'open linen shirt over swim trunks with espadrilles'],
        "unisex": ['white linen button-up with high waisted shorts and leather sandals', 'lightweight jumpsuit with open weave sandals', 'breton stripe tee with white jeans and leather sandals'],
    },
    "edgy alternative": {
        "female": ['fishnet top under a slip dress with platform boots and a choker', 'corset top with a plaid skirt and thigh high boots', 'mesh long sleeve under a crop top with vinyl pants and combat boots', 'motorcycle jacket over a sheer blouse with leather pants and ankle boots'],
        "male": ['black leather jacket over a band tee with ripped skinny jeans and combat boots', 'distressed black denim jacket with studded patches and black jeans', 'oversized black hoodie with chains, cargo pants, and chunky boots', 'graphic tee with a tartan kilt, fishnet sleeves, and boots'],
        "unisex": ['denim vest with band patches, frayed shorts, and a studded belt', 'black turtleneck with suspenders and platform loafers'],
    },
    "preppy": {
        "female": ['pleated tennis skirt with a cable knit sweater and leather loafers', 'gingham shirt dress with a headband and ballet flats', 'navy blazer with a pleated skirt, knee socks, and oxfords', 'collared blouse under a sweater vest with tailored shorts and loafers'],
        "male": ['polo shirt with a sweater tied over the shoulders, chinos, and boat shoes', 'oxford shirt under a quarter-zip pullover with chinos and loafers', 'navy blazer with a gingham shirt, khakis, and penny loafers', 'striped rugby shirt with tailored shorts and deck shoes'],
        "unisex": ['argyle sweater vest over a collared shirt with chinos and loafers', 'crisp white polo with pressed khakis and clean leather sneakers'],
    },
    "vintage retro": {
        "female": ['1950s polka dot swing dress with a cinched waist and kitten heels', 'high waisted mom jeans with a tucked-in striped tee and cat eye sunglasses', '1970s flared corduroys with a fitted turtleneck and platform boots', 'tea length floral dress with a cardigan and Mary Jane shoes'],
        "male": ['1950s rolled-cuff jeans with a white tee, leather jacket, and loafers', 'tweed jacket with a knit tie, high waisted trousers, and brogues', '1970s wide collar shirt with flared trousers and suede boots', 'bowling shirt with cuffed chinos and canvas sneakers'],
        "unisex": ['high waisted trousers with suspenders, a tucked button-down, and oxfords', 'retro track jacket with slim trousers and vintage trainers'],
    },
    "loungewear": {
        "female": ['matching ribbed knit lounge set with fuzzy slippers', 'oversized sweater dress with cozy socks', 'soft camisole with drawstring lounge pants and a robe', 'cropped sweatshirt with matching joggers and slides'],
        "male": ['waffle-knit henley with soft sweatpants and slippers', 'plain crewneck with relaxed lounge pants and slides', 'zip hoodie with jersey shorts and house slippers'],
        "unisex": ['oversized hoodie with matching sweatpants and thick socks', 'flannel pajama set with a robe and slippers', 'soft tee with cuffed sweatpants and bare feet'],
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
    'poolside cabana', 'street food market at night',
])


#: Plain, easily-maskable backgrounds. Only reachable when the location_setting
#: control is "Studio / solid backdrop"; filtered *out* of every other mode so a
#: studio never appears unless explicitly chosen. Includes a chroma-key green
#: screen for masking and solid white / black sweeps.
STUDIO_BACKDROPS: frozenset[str] = frozenset([
    'seamless grey studio backdrop', 'solid white studio backdrop',
    'solid black studio backdrop', 'chroma-key green screen backdrop',
])


# Merge optional user-supplied options (./user_options.json in the pack root).
# Kept last so it can extend any pool above; fails closed if absent/malformed.
# OUTFIT_DESCRIPTIONS is passed so the "outfits" section can register new outfit
# styles together with their garment text.
from .user_options import apply_user_options  # noqa: E402

apply_user_options(FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS)
