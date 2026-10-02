# Release history (1.5.0 and later)

Per-release investigation notes -- measured numbers, what was tried, what was declined
and why -- moved out of `docs/architecture.md` at 1.5.5 because the accumulated
releases had grown to about half that file's length. This file is a log: read it to
understand why a specific release did what it did. `docs/architecture.md` is the
reference: current data schemas, conventions and the gotchas cheat-sheet, independent
of which release introduced them.

Earlier releases (pre-1.5.0) are not here -- `git log` and the release PRs are the
record for those; nothing before 1.5.0 was long enough to justify moving.

## 1.5.0 — the place, the weather and the face decide what is plausible

Measured first, over 3,000–6,000 default renders on 1.4.0: `outfit_style` had no rule tying it
to `location` (evening gowns in an emergency room, loungewear in a machine shop), `season` had
**no rule at all** (~8% of renders wore sandals, shorts or a sun hat "during winter", or a beanie
in summer), `expression` and `mood` contradicted each other in 5.4%, and 30% of default men drew
a feminine-coded `body_type`. `docs/worklog/` holds the sweep; the tests named below pin each fix.

### `outfit_style` answers to the place (1.5.0)

`location` is the trigger, so the place stands and the style adapts — the lighting and
composition doctrine. Data lives in `data/constraints.py`: a per-family allowlist
(`OUTFIT_STYLES_BY_LOCATION_FAMILY`), `OUTFIT_STYLE_VENUES` for places narrower than their family
(gyms, shop floors, beaches), then `OUTFIT_STYLE_EXTRAS` / `OUTFIT_STYLE_REMOVALS`;
`outfit_styles_allowed_at()` resolves one place. A location the family map does not know (a
`user_options.json` addition) returns `None` and gets no rule, so custom places are never
narrowed. `outfit_style` is flat, so every re-pick is uniform over the survivors. The realized
style mix moves the way the base node's brief says it should — streetwear/casual ~12% each,
evening formal ~1%, loungewear and resort ~2% — which is realism, not bias: lock a style and the
random location re-rolls to somewhere it is worn. `utility workwear` joined as the 15th style
because workshops, docks, farms and building sites had nothing plausible to draw.
**Archetypes:** some archetype style/location pairs disagree with the table, because an
archetype's `outfit_style` is a proxy that steers accessories under a supplied costume. In Full
lock level both are locked, so the rule only logs; in Essentials the location is free and is
steered to a venue that fits. Pinned by `OutfitStyleByLocationTests`.

### The season is an outdoor fact (1.5.0)

Three layers, in rule order. **(1)** every built-in indoor or studio location *requires*
`season = "None"`, so indoors the season is dropped from prose and JSON at zero RNG cost, and
every season rule below is outdoors-only for free; a locked season moves a random location
outdoors (the requirement branch's contrapositive). `validate_data.py` now accepts `"None"` as a
requirement value — it is every widget's omit token. **(2)** `SEASONS_BY_LOCATION` pins seven
seasonal places (cherry blossom = spring, snowy pine forest = winter, …). **(3)** the season gates
what is worn (`SEASON_EXCLUSIONS` → footwear, accessories, bag, `outfit_style`), and
`_garment_fits_season` drops warm-only garment phrases in winter and cold-only ones in summer
(regexes beside `COLOUR_WORD_RE` in `data/fields.py`, read only against the engine's own corpus).

Two traps. **Direction matters for bias:** the first draft let the two winter lights pin the
season, which skewed outdoor seasons to 29% winter / 21.5% summer, because 2 of the 17
`daylight` variants dragged the season. Flipped so the season is the trigger (a winter light
drawn out of season is re-picked alone — the mixture property), the seasons measure uniform.
**Never trigger a rule on `season = "None"`:** with a locked scarf, the exclusion's
contrapositive re-rolls a season the indoor requirement pins straight back, and the two repairs
ping-pong to the iteration cap. Indoor-only exclusions are keyed on each indoor *location*
instead, whose contrapositive moves the place. Pinned by `SeasonGateTests`, `SeasonGarmentTests`.

### `outerwear`: weather wear, drawn last (1.5.0)

A deferred field appended at the end of `FIELD_DEFINITIONS` (the `legwear` template:
`_DEFERRED_FIELDS`, `_COSTUME_SUPPRESSED_EXTRAS`, a pool filter instead of a rule). The coat
LEADS the clause ("a trench coat over a pastel sweatshirt with shorts ..."): trailing it read
as the shorts being under the coat. `_eligible_outerwear` returns `no outerwear` **without
touching the RNG** unless the garment is engine-generated, the place is not a built-in
interior (a *locked* season survives indoors, so the season alone is not enough), the season
is voiced and not summer, the footwear is not open (bare feet, sandals, slides), and the
garment has no outer layer of its own (`OUTER_LAYER_RE`); a light layer (`LIGHT_LAYER_RE`:
blazer, cardigan, tailored jacket) takes a coat only in winter. A character who cannot wear
a coat draws what it drew before the field existed; `outerwear` resolves before
`tattoo_placement` (`_DEFERRED_ORDER`) so a coat hides sleeve-covered ink. A coat the user
LOCKS onto a supplied costume is voiced too (never JSON-only), unless a recalled vault
save's text already names it. A `user_options.json` coat with no season row fails open.
`OUTERWEAR_BY_STYLE` (allowlist, validated both ways like `FOOTWEAR_BY_STYLE`) and
`OUTERWEAR_SEASONS` (heavy = winter, mid = the cold half, light = spring/autumn) narrow the pool;
winter outdoors always gets one, spring/autumn half the time. Measured over 4,000: 0 indoors,
0 in summer, 83% winter outdoors, 31% spring/autumn, 9.4% overall. Why a field rather than coats
in the garment corpus: 37% of corpus phrases already carry a layer, and a field adds the lock
and the outfit × coat variety that fixed pairings cannot. Vault recall of an older character is
unaffected — its saved `outfit_description` is the composed clause, which takes the costume
path. Pinned by `OuterwearTests`.

**The legacy `widgets_values` repair had a latent multi-release bug.** Both
`padLegacyWidgetValues` and `padLegacyCosplayerValues` padded one release at a time, so a
workflow two releases old got a newer widget one slot late whenever it sits *after* an older
one — never exercised while the main node's table had one release. `outerwear` (slot 79) sits
after `legwear` (78) and `tattoos` (25), so 1.5.0 would have hit it. Both now grow the missing set
newest-first and splice it in one ascending pass; the jsdom suite pins a 1.4.0 and a 0.89.0
array.

### The face and the mood agree (1.5.0)

A warm face drops the whole `heavy` mood family; a sad face (`melancholic`, `solemn`,
`wistful`, `brooding`, `weary`) drops the whole `positive` family — whole families only, so the
survivors stay proportional. 5.4% → 0.6%; the rest is a sad face with `triumphant`, which is a
partial cull of `bold` and was left. Pinned by `ExpressionMoodTests`.

### The male anatomy trim, and palette double-counting (1.5.0)

The body half of the 1.4.0 "men with female body parts" report: `body_type`, `hips`, `waist`,
`height` and `nose` share one list across genders and had no trim — 30% of default men drew a
curvy/hourglass/voluptuous build and "petite" was in 35% of male prose. Added to
`_MALE_EXCLUDED_VALUES` as anatomy (not presentation-gated); all five fields are flat.
`clothing_color` carried black twice and white twice, so 36% of generated outfits were black or
white; each pair now weighs as one value, six everyday palettes joined, and `PaletteShareTests`
pins the pair weights.

### The picker keeps its filter for the session (1.5.0)

Search, tab and facet now survive close/reopen on the per-node picker instance and are written
back into the rebuilt controls (the search text pre-selected, so typing replaces it). That keeps
the 1.1.0 invariant — the box never reads empty over a narrowed grid — while matching Stylebook's
"remembers my filter" behaviour. Nothing is persisted, so a reload or a new workflow starts clean.

### Round 2: what the maintainer's test renders found (1.5.0)

A 49-image test batch, read against its PNG metadata (so locks were known, not guessed).

**Men read feminine through RANDOM draws, not locks.** Three causes, all fixed on the
wardrobe PRESENTATION (a man with a Feminine/"Any" wardrobe keeps the full odds — that is
the crossplay switch):

- **One absence table for everyone.** `_EXTRA_ABSENCE` forces the absent value with a base
  probability, and the rest is uniform over the pool, so the realized rate is
  `(1 - base) * (n - 1) / n`. For men that put earrings on 56%, a necklace on 54%, an arm cuff
  on 25%, a facial piercing on 37%, highlights on 41%, a bandana or headband on 30%.
  `_EXTRA_ABSENCE_MASCULINE` (engine) holds everyday men's rates; `_maybe_absent` reads it for
  a Masculine presentation. Same RNG shape, only the threshold moves.
- **Men drew hair families at the women's odds** (`braid_long` alone was a fifth of the
  mass, and all fifteen lengths were flat). `MASCULINE_FAMILY_WEIGHTS` (fields.py) re-weights
  whole families for a Masculine presentation in `_pick_family_weighted`, and `hair_length`
  gained `masculine_weights` (a new draw-weight map beside `weights` / `male_weights`, read
  by `_weighted_choice`). Measured: long hair 50% -> 11%.
- **Trims were missing.** Presentation-gated `_MASCULINE_EXCLUDED_VALUES` (feminine braids,
  chignon, blowout, bangs, "short pixie") beside the structural hair trims, and the wardrobe
  trims grew (saddlebags, small crossbodies, mini backpacks, flats, platform boots, delicate
  and jewelled pendants, a medusa piercing). Seven "unisex" outfit phrases were dresses,
  camisoles or leggings and moved to the female bucket (a man was rendered in a tiered dress).
  `presentation` is threaded through `_randomize_fields`, `_repick` and the deferred draw;
  `generate_character` computes it before the fill.

**Patterns and palettes.** Every pattern weighed 8/15 of `solid`, so 80% of outfits were
patterned and camouflage/tie-dye/animal print were ~5% each. Plain now carries ~70%, and
`PATTERN_BY_STYLE` (allowlist, validated both ways) keeps each pattern to the styles that wear
it; `PALETTE_DENIED_BY_STYLE` keeps ombre / mixed prints / bold primaries off tailored dress.
The new palettes are two-tone ("blue and white", "burgundy and grey", "camel and cream"): a
single-hue palette read as one colour head to toe.

**A locked coat now adapts the random scene.** Rules triggered by `outerwear` only ever fire
on a lock (a random coat is drawn after the loop), which is exactly when they are needed: the
place goes outdoors (every interior is a whole location family), the season, shoes and style
follow the coat, and `_resolve_outfit_description` drops garments with their own outer layer.

**Scene gates.** `fire and flame warm flicker` rendered literal flames (a lavender field, an
airplane cabin): split into its own `artificial_fire` family at the family's own rate and
gated as a fixture (`FIRE_LOCATIONS`). The `studio_shape` family is excluded outdoors (whole
family). `seated` split into `seated` / `seated_floor` (proportional) so public and formal
places drop the floor poses whole, and `_repair_pose` now honours live exclusions
(`_live_exclusions`) instead of re-opening them. Also: grey hair needs age 35+ (whole
`gray_white` family), a comb over needs short hair, a hat requires no hair accessory, sun
hats stay outdoors, barefoot means no legwear, a watch excludes the watch-like bracelets, a
high-top fade needs coily hair, paired accessories are voiced as "a pair of", and
`outfit_style: None` no longer voices a random "earth tones houndstooth clothing, in flats".
Pinned by `MasculinePresentationTests`, `PatternByStyleTests`, `LockedCoatAdaptsTests`,
`RoundTwoSceneGateTests`.

**Natural colouring follows ethnicity and age (round 2, found in the QA renders).** Eye
colour was flat (57% of everyone drew blue, grey or green eyes) and natural hair ignored
ethnicity, so blonde Sudanese and Tibetan men and blue-eyed Somali men were common -- and a
blonde head pulls a T2I model toward rendering a white person, quietly eroding the
diversity the ethnicity roll exists to give. `_bias_hair_color` / `_bias_eye_color` add the
same soft, per-band lean the skin tone already had (`_HAIR_INBAND_PROBABILITY`,
`_EYE_INBAND_PROBABILITY`): light hair is now ~2-4% outside the fair and olive bands, light
eyes ~5%, and the fair band keeps its blondes. Grey hair was 20% at every age; it is now
drawn by age at the pool (`_GREY_BY_AGE`: 0 under 35, ~78% at 65+). **Decide it at the draw,
not with a rule:** the first version excluded grey under 35 with a constraint, and every
re-pick it forced ignored the ethnicity lean (light hair stayed ~10%); a locked grey still
ages a random person up through a grey -> `age` rule. Also: streetwear and casual caps stay
out of formal rooms, dense freckles stay off deep skin, and the three places named for their
sunlight are never lit by night. Pinned by `EthnicAndAgeColouringTests`.

**Round 3: the maintainer's review of the QA renders.** Three causes behind "still strange
for straight men", each measured before the fix:

- **Palette families rendered as colour-blocking.** A family adjective ("bold
  primary-colored", "pastel", "jewel-toned", "navy-and-white") made the model paint several
  colours across one garment: rainbow knits, a patchwork safari jacket. `PALETTE_HUES` now
  resolves a family to ONE named hue per render, voiced on the lead garment
  (`_compose_outfit_clause`, which gained `rng` and `presentation`); a Masculine presentation
  draws from `PALETTE_HUES_MASCULINE` (no blush pink, lavender or butter yellow), and the loud
  palettes carry `masculine_weights`. Whole-look palettes (all black, all white) keep their
  adjective. The JSON still records the family.
- **Independent odds still stacked.** Each adornment's rate was realistic, but they are
  independent, so one man could draw chains, a thumb ring, a wrap bracelet and an earring.
  `_cap_adornments` (after the constraint loop, no RNG) holds a Masculine presentation to 2
  pieces and a Feminine one to 4, dropping the least everyday first and never a lock.
- **Menswear that renders feminine.** "Cropped" puffers and harringtons rendered
  belly-out on men (rewritten or moved to the female bucket); leather totes rendered as purses
  (trimmed; two backpacks joined the bag pool); "layered gold chains", "posing with a hand on
  one hip" and "kneeling gracefully" are masculine-trimmed, with `MASCULINE_FAMILY_WEIGHTS`
  keeping each pose family's survivors at their old rate; the `playful` expression family is
  halved for men. `clothing_pattern` also carries `masculine_weights` (floral, paisley, polka
  dot, animal, tie-dye, abstract made rare): a floral knit with flares read as costume on a man.
  The `longline knit vest` phrase became a plain sweater vest -- it rendered as a dress over jeans.

Also: bare feet and slippers only where shoes come off (home, water, soft ground, the
barefoot studios); `denim` yields to a garment that names its own fabric
(`FABRIC_WORD_RE`); pocket squares need a tailored style and evening clutches an evening
style; formal suits lose fingerless gloves and casual hats. Review fixes in the same pass:
the grey -> age rule covers only the three age-greys (white and silver are also dye and
fiction -- the first version aged every white-haired anime character past 35), Full spectrum
drops only the age-greys under 35, `_live_exclusions` is now the one union helper both the
constraint loop and `_repair_pose` use, and the Welder / Glassblower archetypes' locked fire
light is legal at their workshops. Pinned by `RoundThreeQaTests`.

**Round 4: the maintainer's 47 flagged renders.** Every one reproduced byte-for-byte from
the branch, so the fixes are by cause, not by image. Measured after: a coherence sweep of
~10k characters (defaults, Male, Female, each style and five locked coats) finds 0
violations of any class below, and a final-state check -- no unlocked field holds a value a
live rule excludes -- finds 0 stuck values in 6,600.

- **Extras that the finished garment cannot carry** (`_fit_extras_to_garment`, after the
  outfit is composed, no RNG). Suspenders need trousers with nothing over them (they
  rendered over a double-breasted jacket and with swimwear); belts stay off suits, gowns,
  robes, hoodies and track pants; lapel pins and pocket squares need lapels; opera gloves
  need a dress; a waist chain needs a bare midriff, a body chain a bare torso, an arm cuff a
  bare upper arm, an anklet a bare ankle over an open shoe, a brooch a jacket, cardigan or
  dress. It writes the field's ABSENT token rather than popping it, so a Turnaround or
  Vault replay pins the absence instead of re-rolling a different extra into the gap.
- **Tattoos where the clothes leave skin.** A covered placement did not hide the ink -- the
  model cut a window in the suit or tore off a sleeve. The upper arm needs short sleeves,
  the shoulder blade a bare back, the neck no turtleneck; the back of a hand always shows
  (only a glove covers it). A random tattoo with no visible placement is dropped.
- **Legwear.** Trousers win over a tunic or dress in the same phrase; a floor-length hem or
  a garment that already names its hosiery takes none; no tights outdoors in summer; the
  youthful values stop at 45; no socks with espadrilles, boat shoes or sandals. Men's socks
  also show where they really do: under a cuffed or ankle-length hem over a low shoe.
  `LEGWEAR_BY_STYLE` now covers the women's values (fishnets on an evening gown).
- **One wrist, one thing.** A watch excludes every bracelet (they stacked on one wrist);
  opera gloves exclude both.
- **Extras belong to a style and a place.** `EXTRAS_DENIED_BY_STYLE` (bag, accessories, hair
  accessory, necklace, bracelet, watch, rings, earrings, piercings) plus body jewellery by
  style: a bucket hat with a sequined cocktail top, a flower crown with a gown, a briefcase
  with coveralls. By place: no bag at home, no gloves, beanie, bucket hat or sunglasses
  indoors (a studio sweep keeps them), no dress shoes on rough ground, candle and lamp
  light outdoors only at a patio. `warm candlelight` split out of `artificial_open` as its
  own family (88, share-preserving) with a fixture allowlist, `CANDLE_LOCATIONS` -- it lit
  a trampoline park. Men's earrings are studs; a thumb ring, statement belt, canvas tote,
  ankle boots (rendered heeled) and a zigzag part are masculine trims. A masculine
  presentation also VOICES its jewellery plainly (`_MASCULINE_JEWELRY_CLAUSES`: "a small
  plain cross on a steel chain", "a small gold stud in one ear") because "a cross necklace"
  rendered as a glittering diamond-cut chain; the values and JSON are unchanged. Men's
  necklace absence rose 0.72 -> 0.8. From the QA renders: a braided ponytail, a thin
  headband and a silk neck scarf read feminine on men (trimmed); a tie rules out a
  necklace and a neck tattoo; pigtails and space buns stop at 45 and leave business and
  evening dress; mod and gothic makeup stop at 55; a pixie takes no half-up.
- **Hair.** Gathered styles need length (ear length and a bob: no ponytail, bun, updo, long
  braid or pigtails; jaw length: no updo, long braid or pigtails; a pixie: no bun).
  Afro-textured styles (`texture`, `braid_short`) need textured hair; a buzz shows no wave;
  a high-top fade needs tight coils; the parting follows the style; no highlights on grey
  hair or a buzz; hair accessories need hair to hold; no windswept hair indoors. To keep
  every cull whole-family, `bantu knots` moved `knots` -> `texture` (210 / 630) and `box
  braids` moved `braid_long` -> `braid_short` (1350 / 540), both share-preserving, and
  `barbered_short`'s base weight fell 560 -> 280 (women drew it twice as often once short
  lengths stopped drawing buns; men read `MASCULINE_FAMILY_WEIGHTS`).
- **Ethnicity lean.** Coily textures stay open 8% of the time outside the `dark` band (the
  flat draw gave them to 13% of Czech, Japanese and Hungarian characters). In the darker
  bands natural hair is black 60% of the time, else dark or medium brown or chestnut. The
  skin band `tan` lost `east_asian` and `pacific` (a Japanese man in caramel skin was in
  band), Sudanese moved to `dark`, and the in-band probability rose 0.8 -> 0.9.
- **One body.** The build word binds waist, hips, neck, shoulders, chest, fitness and height
  ("a plus size build ... a very fit physique ... a narrow waist").
- **Makeup.** Each look binds its details (pin-up liner and red lip, gothic dark lip, soft
  glam without falsies, natural without glitter or heavy contour); stage looks leave
  workwear, loungewear, sportswear and business dress, religious sites and workshops; club
  and editorial looks stop at 55.
- **Frame and pose.** Close-ups drop full-body poses; a selfie drops strides and power
  poses; a back view requires a head turn; an overhead shot drops the horizon compositions;
  the cuff, collar and pocket gestures need a garment that has one.
- **Face and mood.** A whole-family matrix per expression family. `bold` split into
  `bold_bright` (self-assured, triumphant) and `bold_fierce` (weights x5, shares exact), so
  a smile can still be self-assured. Every mood lands between 3% and 6%.
- **One colour flooded the outfit** (found in the round-4 QA renders themselves: ivory on
  ivory, a rust suit with a rust shirt and tie). Round 3's single hue binds to the lead
  garment and the model spreads it everywhere, so `_colour_the_rest` now colours each later
  garment: a tonal palette with its other hues at a contrasting lightness, a two-colour
  palette with its pair, an accent palette with a contrasting neutral. A set stays one
  colour and takes no pattern (a striped lounge set striped top to bottom); a suit keeps its
  trousers but its shirt contrasts. The four all-one-colour palettes weigh 0.3.
- **Colour and pattern.** The pattern is an ADJECTIVE on the lead garment
  (`PATTERN_ADJECTIVES`): a tail landed on the last noun, so "chinos in stripes". Knitwear
  takes only solid, texture, stripes, argyle or geometric; self-patterned fabrics
  (seersucker, tweed) take none; `white and cream` is voiced as one hue (it rendered a
  two-colour block); "midnight" and similar count as colour words; business formal loses
  jewel tones and edgy loses pastels.
- **Garments.** Robes and swimwear only at home or by water; a coat never goes over a
  two-layer garment or a summer top; youthful phrases stop at 45; a dress re-picks away
  from men's lace-ups. Phrase fixes: "broomstick skirt" drew a broom, several men's
  phrases had no bottoms, "high-waisted wide trousers" read as a skirt, longline hoodies
  read as dresses.
- **Age and skin.** No laugh lines under 30 or "porcelain smooth" from 50; dense freckles on
  fair skin only; scars and a neck birthmark weigh 0.3 (they rendered as wounds).
- **Two engine bugs.** A locked coat that moved an indoor scene outdoors left the season
  blank (72 of 100 locked winter coats) -- it is now redrawn and the rules re-run.
  `_repair_pose` passed no presentation, so the masculine pose trims and family weights
  were skipped on every repair.

**Round 5: the maintainer's test of the round-4 branch** (14 flags, "overall much better"):
- A constraint re-pick bypassed the ethnicity lean -- a buzz cut re-picks `hair_texture` off
  a wave, and a Welsh man came back coily. `_repick` now applies the same skin, eye, hair
  colour and texture leans as the draw (Welsh men coily: 0.5%); out-of-band coily 0.08 -> 0.03.
  The Afro-textured STYLES (`texture`, `braid_short` families) lean the same way, since the
  texture gate allows them on "curly" hair every band draws (two-strand twists on a
  70-year-old Welsh man): open 5% of the time outside the dark band, at the draw and on
  re-picks, whole families.
- outfit_style None voiced "accessorized with a silk pocket square" and nothing else, so the
  model drew a bare chest: garment-bound extras go when there is no garment.
- No sunglasses under night light; no coat (random or locked) at a pool or hot spring; an
  ombre palette takes no print and a knit lead takes no mixed-print or ombre palette;
  all-one-colour palettes leave business dress and workwear and weigh less (all white 0.15,
  men 0.1); a corset top is a bare top for the season filter and, with vinyl and harness
  pieces, a young look past 45; cornrows, locs and twists need tighter curls than a loose
  curl; an undercut and a mullet stop at 55; chiffon and lace dresses are "lined" (one
  rendered see-through); a men's boho knit-and-flares phrase became straight-leg corduroys.
- The two "unisex" phrases that carry a tie (a pressed suit with a slim tie, a satin-lapel
  dinner suit with a bow tie) moved to the men's buckets: a Feminine wardrobe drew a woman
  in a suit and tie. A suit and tie stays reachable for women under a Masculine or Any
  wardrobe.
- **Decided (maintainer, round 5): `outfit_style` None stays silent.** It voices no
  clothing at all -- it exists for users who write their own clothing prompt -- so with
  nothing else in the prompt the model may render a person undressed (a bathroom selfie
  did). Only garment-bound extras are dropped with it.

Pinned by `RoundFourQaTests`. The sweeps behind the numbers are `docs/worklog/sweep_r4.py`,
`dist_r4.py` and `invariant_r4.py` (gitignored, local).

## 1.5.1 — the maintainer's 33 flagged renders (idforge-927-concern)

Every flagged prompt was reproduced exactly (33/33) by executing the PNG's whole node chain
(Creature -> Cosplayer -> Archetype -> IdentityForge) against the working tree, and the
wording fixes were A/B-rendered on the maintainer's own Krea2 graph at the original seeds.

### A preset may not lock a pair the engine forbids

Both sides locked means `_apply_constraints` can only warn and keep both, so the clash renders
every time: the Farmer in an indoor market stall under golden-hour sun, the Astronomer with a
moon painted inside a planetarium. A scan found 97 archetypes locking such a pair (place vs
light, expression vs mood, hair length vs style, male-pool hair on a Male variant, sunglasses
indoors). Two mechanisms:

- **Fixed values** are data bugs, fixed in `data/templates.py`.
- **Independent list picks** (a location list beside a lighting list) now agree:
  `_resolve_list_values` picks each list among the alternatives that `lock_clash()`
  (`data/constraints.py`) accepts against everything already settled, base look first, then
  each variant with its gender. Still one draw per list. Presentation-gated rules are skipped
  (they depend on the wardrobe control at run time).

`tests/validate_data.py` gates it (`_archetype_lock_clashes`), mirroring the resolver and
walking every list branch. `outfit_style` is skipped under a costume: it is not voiced there.
A new constraint rule can make an existing preset clash -- run the validator after adding one.

### Encased means no human body

A masked, fully shelled character (`covers_face` and a full shell) voiced the wearer's age,
build and proportions ("a short 38-year-old Korean man with a slender build ... a slightly
defined chest"), and the model drew a man inside Chopper and a bare torso inside Megatron.
`_ENCASED_HIDDEN_FIELDS` (was `_CONCEALED_SHELL_SKIN_FIELDS`) now drops every randomized body
field; an entry's own `physique`, its `scale_prose` and widget locks still speak. The shell
regex wants `robot`/`droid`, so "robotic body" and "astromech body" never matched: Megatron,
Chopper, Ultron, Bumblebee and Genji gained `covers_body`. An adjectival scale phrase is now
an appositive ("a man, colossal and over thirty feet tall, with a stocky build").

### Skin tone and ethnicity lean both ways

The out-of-band skin draw reopened the whole spectrum (a Kenyan in porcelain, an Icelandic
woman in warm brown); it now stays within two steps of the band (`_NEAR_BAND`). And a locked
skin tone left ethnicity flat, so a locked "pale" came back Sudanese or Ethiopian about one
time in six; `_bias_ethnicity` leans the ethnicity draw toward the tone with the same odds.
Measured over 3,000 seeds per case: 0% of draws beyond the near band, locked or not.

### Words the model misreads

Any `tie` token drew a necktie: "tie-front top", "tie-dye", even "tie-dyed". Render-tested
replacements: "front-knot", "sash waist", "lace-up back", and the `tie-dye` pattern voiced as
"psychedelic spiral-dyed" (the option value is unchanged, so saved workflows keep working).
"Behind one ear" never rendered there (a temple patch, the neck, a ponytail), so it is no
longer drawn at random. A "rescue can" became a canteen clipped to a swimsuit: the Lifeguard
carries "a red torpedo rescue buoy slung from a strap over one shoulder".

### Garments that leave a person bare, and gendered costumes

A male-only costume under a Female lock rendered a topless woman (Lifeguard). Lifeguard,
Surfer, Boxer, Pro Wrestler, Sumo Wrestler and Berserker Barbarian now carry per-gender
variants; so do Renaissance Noble, News Anchor, Court Jester, Celestial Cleric, Angelic Being,
Pop Star, 1960s Mod, 1950s Sock Hop, Cheerleader, Flight Attendant, Corporate Executive,
Trial Lawyer and Orchestra Conductor (makeup, a doublet or a necktie on the other gender).
Watchmaker and Sommelier lost their ties. In the generated wardrobe: a denim vest now has a
tee under it, the harness pieces became jackets, mesh tops name the opaque layer beneath, and
the fishnet-top phrase became a slip dress over a band tee.

### Scene gates

- Place-named lights: "harsh desert sun" only at arid places, "dappled sunlight through
  forest canopy" only under trees, "snow-reflected daylight" never in desert or tropical
  places, and no clear-sky light on the rainy street. The `venue_rig` family (club strobes,
  gels) joins the outdoor studio-rig exclusion (whole families).
- Winter outdoors takes no flats, ballet flats or slippers, and no loungewear (it never
  takes a coat). Nobody stands in the back seat of a taxi.
- Hair: no barbered short cut (pompadour, quiff, fade, undercut) at shoulder length; no bandana on a buzz or crew cut (it rendered round the neck).
- `outfit_style` None (maintainer, 1.5.1): it says nothing about clothing at all -- and
  nothing that implies there is none. A bag, a cap or glasses with no garment beside them
  read "wearing nothing but" and drew bare chests, so bag, accessories and legwear go absent
  too (a lock is still voiced), and a tattoo only lands on a hand, wrist or neck.
- Build: a petite build is not tall; a very petite frame has no very broad shoulders;
  edgy alternative stops at 60. Bleached brows need a Full-spectrum hair scope. Flannel,
  seersucker and gingham count as patterned fabrics.

### Variety (from the maintainer's wildcard folder)

Seven landmarks inside the existing landmark families (family weights unchanged): Giza,
Petra, the Taj Mahal, Angkor Wat, the Great Wall, Machu Picchu and Victoria Falls -- the
landmark set leaned European and North American, with little from Africa and nothing from the
Middle East. Garments the wardrobe never produced: cargo shorts, a pearl-snap western shirt,
a raglan baseball tee, a denim skirt, a sweater dress, a peplum top, a mock-neck knit, tweed
with corduroy, a camp-collar shirt with Bermuda shorts, a guayabera, a leather mini skirt, a
basketball jersey.

Pinned by `tests/test_revision_151.py`. Local tools (gitignored): `docs/worklog/repro_graph.py`
(reproduce a flagged PNG), `render_test.py` (A/B wording on the maintainer's graph),
`clash_report.py`, `edit_arch.py`.

### Gender-neutral roles coin-flip (1.5.1, maintainer-approved)

A soft `gender` lean decides the gender whenever the widget is "Any", so a leaning
archetype rendered ONE gender every time under Random -- every Firefighter a man, every
Teacher a woman. Roles whose name is gender-neutral and whose look has an authentic
other-gender version now set `gender: "Any"`: the old lean's look moved verbatim into its
variant (beard, makeup, hair, feminine-coded build), the other variant was authored, and a
proof script confirmed each lean look resolves byte-identically to before. Unisex costumes
stay on the base (`_COSTUMES` plus a costume-less variants block). Leans remain only where
the concept itself is gendered (Leading Man, Gent, Dandy, Teddy Boy, Rude Boy, Suburban
Dad, Flapper, Geisha, Nun, Tuareg's men's veil and similar). One-sided variant blocks
gained their other half: a men's agbada look for Aso-Ebi with Gele, a women's gondolier.

### Roster (1.5.1)

The Inhuman Royal Family and the Eternals from maintainer-supplied descriptions: Gorgon
(hooves via `anatomy_note`), Karnak (enlarged cranium under a hood), Triton (scaled body,
face visible), Maximus, Lockjaw (`body_plan: "feral"`, a five-foot-tall bulldog), Ikaris,
Thena, Makkari, Sprite, Druig, Ajak, `Gilgamesh (Marvel)` (bare `Gilgamesh` is Fate's),
Zuras, Starfox, Kro and Arishem (colossal). Black Bolt rewritten (cowl, glide-wings, no
hair), Crystal onto the black-and-yellow classic, Medusa gained the classic masked look
as an alternate. Declined: Ahura (a black-and-silver bodysuit with white hair reads as a
generic look beside Black Bolt).

### Samples, ages and gallery pins (1.5.1)

- An archetype's `age` lock now survives Essentials (`_is_essential`): authors lock age
  only where the look implies a life stage, and dropping it drew a 70-year-old cheerleader.
  Cheerleader, 1950s Sock Hop and E-Girl / E-Boy gained young-adult ages.
- Essentials also keeps the Body group for the archetypes in `BODY_IS_THE_LOOK`
  (`data/templates.py`): Sumo Wrestler, Dwarven Blacksmith, Halfling Rogue. Their
  costumes state the build ("on an enormous, heavyweight frame"), so a randomized body
  contradicted the sentence -- the female sumo sample led with "a softly curved build,
  narrow shoulders". An opt-in list, not a costume regex: most "tall" in costume text is a
  hat or boots.
- A costume that holds something takes no both-hands pose. `_performable_poses` already
  dropped `HAND_OCCUPIED_POSES` for a Cosplayer `held_item`; `_HAND_PROP_RE` now reads the
  same thing in `outfit_description` ("a clipboard in one hand", "a helmet under one arm",
  ", holding a diploma"). "Stretching both arms overhead" with a clipboard drew the clipboard
  floating beside her. It matches held forms only -- "trousers held up by braces", "a belt
  carrying a sword" and "a clip holding the hair" occupy no hand. A prop that should stay
  put whatever the pose is anchored instead (the yoga mat is on a carry strap now).
- `full body shot` and both `wide shot` values joined the tight-composition exclusion that
  already covered `full body shot with environment visible`: "wide shot ... composed with a
  tight crop and little headroom" rendered waist-up (Sommelier, Sumo). `composition` is
  flat, so the partial cull is bias-safe.
- Sumo: "mawashi belt" in a dojo rendered a knotted karate belt; "sumo mawashi, the wide
  wrestling loincloth" drew the wrap. Seven body wordings were A/B'd on the female sample's
  seed ("obese", a weight, the lead build phrase, a sumo-stable location); none drew a much
  heavier woman and several drew a slimmer one, so the size ceiling is the model's.
- Gallery samples use front-facing body framings only (`_GALLERY_SHOTS`), a coin-flip
  entry's sample can be pinned to one gender (`_GALLERY_GENDER`, Cheerleader female), and
  an entry whose defining feature needs one pose can pin it (`_GALLERY_POSE`, Black Bolt's
  arms raised so the underarm wings spread). All live in `scripts/render_gallery.py`;
  none changes what the node emits.

## 1.5.2 — idforge-928-concern

Every flagged prompt was replayed from its PNG's node chain against the working tree, and each
wording fix was A/B-rendered on the maintainer's Krea2 graph at the original KSampler seed.

### A possessive person in a costume is a second person

The Female sumo costume ended "on a very large, heavy sumo wrestler's body". Every render drew
a big man standing behind the woman, and he took the size words. That is why the 1.5.1 note
above called body size a model ceiling: the seven wordings tried there all kept the
possessive. Worded like Big Bertha ("worn on an enormously large, powerfully heavyset body of
immense girth"), the same three seeds drew one heavy woman and no second figure. On the
gallery pipeline (raw checkpoint + turbo LoRA, "professional photograph" prefix) the same
words still drew a lean body for both genders, so the size ceiling there is real. Rule: a
costume describes the body without naming who it belongs to ("a wrestler's", "a dancer's").

### Words that draw objects

The `tie-dye` class again, fixed the same way: the value (and JSON) stays, only the words
change, via `_OBJECT_TOKEN_CLAUSES` in `nodes/identity_forge.py`. "money piece highlights"
drew a fan of banknotes, "feathered brows" drew feathers along the neckline and in the hair
(it was voiced for 17% of default women), and "birthmark on neck" beside a collarbone tattoo
drew a red paint splash. A Modifier on exactly those fields ("eyebrow_makeup: bold") turns the
value into "bold feathered" before the prose is built, so the table misses it and the old
words come back. That is a known gap, left open because it needs a hand-written modifier on
one of three values.

Costume wording found by the same review:
- **An unworn item has nowhere to go.** "Heavy gloves tucked in a hip pocket" drew one glove
  hanging out of it (1940s Factory Worker; Farmer and Stonemason had the same phrase). "A
  surgical mask pulled down under the chin, a face shield pushed up" hung both off the back
  of the head (ER Nurse). The mask alone still dangled from one ear, so both are gone.
  "Goggles pushed up on the forehead" says where they sit and has not been reported.
- **Named boots in a waist-up frame hang from the belt.** Country Star's "a tooled leather
  belt, and embroidered cowboy boots" drew a boot at the hip when the model cropped at the
  thigh. "On her feet" and "tucked into" did the same, and only dropping the boots fixed it.
  "belt, and boots" appears in dozens of costumes, but this is the only report so far.
- **"White and {metal} robes" is two robes.** The Angelic Being rendered half white, half
  brass-brown. "A single flowing white robe trimmed in {metal}" keeps the metal as trim.
- **A mask needs a place too.** "a ball gown with gold thread and an ornate feathered mask"
  put the mask on the bodice, and the male "filigree half-mask" floated at the chest in the
  gallery sample. "worn over the eyes" put the male mask on the face. The feathered masks
  land on the forehead or the side of the head, which still reads as worn. The Surgeon's
  "a hanging mask" was dropped, for the ER Nurse reason. A full-face mask is different: the
  Plague Doctor's beaked mask hung on the cane, and "worn over the face" still left it
  beside the head, because the randomized face prose wins. "Pushed up onto the top of the
  head", with the cane gone and a shirt named under the robe, rendered on the hat.
- **Goggles plus a necklace draw two pairs of goggles.** A Mad Scientist with goggles on
  the forehead and a statement necklace grew a second pair at the neck. Without the
  necklace, one pair rendered. "A single pair ... resting on the forehead" moved the only
  pair to the neck. `_fit_extras_to_garment` now drops an unlocked necklace under goggles,
  the same way it already does under a tie.
- **Name every garment, or the model supplies skin.** "Utility straps" on the Cyberpunk
  Netrunner rendered as suspenders. With them removed, the jacket was the only garment
  named, and the gallery sample came back bare under the open jacket. It was never
  published. The costume now names the top and trousers. This is the 1.5.1
  missing-top rule again, and it applies to any edit that removes a clause from a costume.
- **A vague garment gets invented.** "A floor-length tailored cape over evening tailoring"
  named no garment under the cape, and the render filled it with a grey dress of the cape's
  colour. The phrase now says "a slim black evening suit".

### Garment-bound extras, tightened

`_fit_extras_to_garment` now checks two extras against a stricter garment test:
- **Pocket square:** needs `_POCKET_SQUARE_RE` (suit, tuxedo, blazer, sport coat, tailcoat,
  dinner jacket, any `*-lapel`). `_LAPEL_RE`'s bare "coat"/"jacket" let one onto a wrap coat
  over a velvet dress (it rendered as a silk scarf in the hand) and onto harrington and
  collarless jackets. The lapel pin keeps `_LAPEL_RE`.
- **Opera gloves:** a dress qualifies only under an evening or cocktail style. Otherwise the
  garment must be a gown. `_DRESS_RE` matched "a smocked mini sundress" (vintage retro, in a
  taxi) and only one glove rendered.

Both drops write the absent token and use no RNG, so no other field shifts. A diff of 800
default Female seeds, old against new, changed only where a fix applied.

### Men's earrings

Default men wore earrings 15.5% of the time, a third of them diamond studs, which read as
feminine, and ear-cartilage piercings 4.7%. `diamond studs` joined the masculine earring trim,
which is presentation-gated: a Feminine wardrobe still reaches it, measured 25 in 600. The
`_EXTRA_ABSENCE_MASCULINE` odds went from 0.8 to 0.9 for earrings and from 0.9 to 0.95 for
piercings, and the voiced studs say "plain". Measured after: 6.9% studs, 2.2% ear piercings.
A locked diamond stud on a male preset is kept (50/50). The odds change shifts men's seeds
from the earring draw onward.

### Not a bug: a Random archetype replaces the picked cosplayer

The "Arishem renders as someone random" report reproduced exactly from the PNG: the Archetype
node downstream of the Cosplayer was set to `Random`, rolled "Judge", and the downstream
preset's costume wins by design (`merge_preset_documents`). Recreating the nodes changed
nothing. The renders came right when that Archetype node went back to `None`.

## 1.5.3 — idforge-929-concern

Six renders were read against their prompts; every flagged symptom traced to the prose.

### A costume-text mask hides the mouth

Kitana's mask ("a blue face mask covering the mouth and nose") lives in the costume, so the
entry is not `covers_face` and the prose still voiced "petite and defined lips ... a soft
smile ... glossy lip colour". The model drew that mouth and pulled the mask under the chin.
`_LOWER_FACE_COVER_RE` (identity_forge.py) matches a mask/veil/scarf/muzzle worn over the
mouth, nose or lower face and pops `lips`, `smile_type`, `nose`, `lips_makeup`,
`facial_hair` and `expression` (a widget lock survives, the `covers_face` rule). A pulled-down
mask and an upper-face half mask do not match. The pop is value-independent, so replays agree.

### Cosplay jewellery follows the look level

Four of five renders carried jewellery the costume never names (Chewbacca's signet ring,
Shao Kahn's ring, Kitana's bracelet, a stud on a 1940s detective). `_JEWELRY_SUPPRESS` in the
Cosplayer builder locks it absent with `override=False`, so an entry's own signature pin
survives: **Full character** drops all random jewellery and nails (it is the canon
character); **Costume only** keeps it (a person wearing the costume) unless the head is
masked and not unmasked. A widget on the Identity Forge node always wins. Men's random
earrings went from 10% to 5% (`_EXTRA_ABSENCE_MASCULINE`).

### Furred shells and stated muscle

Chewbacca had no `covers_body` and "all-over long shaggy brown fur" matches neither the shell
nor the body-paint marker, so he drew a human body and a ring. Wicket, Chief Chirpa and Wampa
had the same gap. All four now carry `covers_body`; Chewbacca and Wicket-class entries with an
all-over fur coat should use the canonical "an even, all-over coat of ..." wording and a
`skin` key when the colour anchor would otherwise voice "brown skin". A costume that says
"muscular" now pins `fitness_level: muscular` (`_MUSCLE_RE`, `override=False`; 42 entries)
so Shao Kahn's bare muscular chest no longer sits beside "a lightly active physique". His
skull helmet now says its faceplate covers the face; Daredevil's suit names sleeves, gloves,
bracers, belt, knee pads and boots, and his cowl leaves the jaw bare.

### Words without a noun

Voice-only fixes; option values are unchanged. `_OBJECT_TOKEN_CLAUSES` gained "a delicate
gemstone ring" (the bare value drew a loose stone), "a simple band ring", "stacked thin band
rings", "a cuff bracelet" and "a prominent brow ridge" (was "brow ridge forehead"). A
masculine presentation voices "elegant" neck as "a long neck". "A petite ... woman with a
petite and slim build" says petite once. Gathered hair (`_GATHERED_HAIR_STYLES`: half-up,
ponytail, buns, space buns, pigtails) reads "hair is <length colour>, worn in a ballerina
bun" so the style is not a second hairdo.

### Not fixed

The two-women render (#01432) is unproven: the prompt had one woman, the hair phrase and
selfie framing are the suspects, and the hair wording above is the only change made for it.
Ethnicity over 300 seeds per gender (`docs/worklog/ethnicity_929.py`) is flat across 88
values, the top at 3.3%, so the six European faces were chance.

## 1.5.4 — idforge-929-concern, second batch

A second batch of renders against the 1.5.3 code; each flagged symptom was traced to the prose and the
fix A/B-rendered at the maintainer's seeds before it went into data.

### A lower-face mask hides the jaw too

`_LOWER_FACE_HIDDEN_FIELDS` gained `jawline` and `chin`. Under Sub-Zero's, Ibuki's and Kaneki's
masks the prose still said "a sharp and defined jawline, a pointed chin", and the model drew a
bare jaw and slid the mask down. Poses ("lifting the chin") and makeup ("jawline contour") are
other fields and stay.

### Masks lead the costume and say where they sit

Sub-Zero, Kakashi, Ibuki, Kaneki, Nezuko, Rage and the Titania mask alternate put the mask FIRST
in the costume with a worn position ("pulled up over the nose and mouth", "worn over the eyes").
Trailing list items landed on the neck, chest or crown. Sub-Zero is now the canon rigid metallic
guard with ice-crystal vents, frost mist and icy forearms (a plain "cloth mask" drew a surgical
mask). Silk's makeshift alternate is opaque webbing over a grey base layer (it drew sheer web
over bare skin) and its mask now matches `_LOWER_FACE_COVER_RE`. Shao Kahn's helmet says
"bone-white skull mask covering the whole face"; Daredevil's cowl has "blank dark-red eye
panels sewn flush into the leather" ("lenses" drew red safety glasses).

### The colour anchor keeps a fur, scale or hide material

`_body_paint_skin_color` captured the colour and dropped the material, so Beast voiced "blue
skin" in the lead and on the face while the costume said "a coat of blue fur": the model drew a
fur JACKET over blue skin. The anchor now returns "blue fur" for fur, scales and hide (an
explicit `skin` key still wins), and Beast's costume says "uniform, all-over thick blue fur"
(no garment word, same body-paint marker). Many roster entries voiced "<colour> skin" over fur,
hide, scales or plating before this; their prose (and `skin_tone` in the JSON) now names the
material.

### Ewoks: name the species, describe the face

"a small round face ... large dark eyes ... soft fur" drew a teddy bear. Chief Chirpa's and
Wicket's masks now say "the flat, wrinkled face of an elderly Ewok" (Chirpa), a flat face with a
short snout, small glossy all-black eyes with no visible whites and a mouth hidden in coarse
grizzled fur. Chirpa keeps the pinkish-brown snout from the maintainer's reference photos.
Wicket's wording is from memory of the film, not a reference image.

### Colossus, Zangief, the Namors

Colossus rendered a human face on steel plates through three A/B rounds; an early face
sentence (`anatomy_note`) did not move it because the voiced jaw, nose, lips and brows still
described a man. He is now `covers_face` with a steel head as the mask (hair sculpted in steel).
Zangief's "a red mohawk" lost to the random hair sentence; "bald" in his costume drops the
scalp-hair fields (`_BALD_RE`), leaving the mohawk as the only hair. The canon ankle wings on
Namor, Namora and Namorita are KEPT (the pack is model-agnostic, so a Krea2 turbo limit does not
remove canon): they now say "a small white feathered wing sprouting from the outer side of each
bare ankle", but Krea2 turbo still draws them on the back or shoulders because the ankles sit
below almost every framing.

### Daredevil's collar, Nezuko's muzzle

"A high protective collar" drew a neck brace; "a plain mock-neck collar of the same red
leather" drew a roll collar. Nezuko's "muzzle clenched across the mouth" vanished in full-body
framing; "a bamboo muzzle tube gripped between the teeth across the mouth, a red cord running
from both ends around the back of the head" renders in the maintainer's graph. The gallery
pipeline (no prompt enhancer) still draws a stock cosplay photo without the muzzle, so her tile
shows none: a gallery-pipeline limit, not a prose one. Costume text avoids pronouns (crossplay).

### Beast's head, Daredevil's DD, ankle wings again

Beast rendered an ordinary man's face inside blue fur: the random face, jaw and hair were still
voiced. He is now `covers_face` with a `mask` that names "Hank McCoy, the X-Men's Beast" and
describes the comics face (mostly human shape, broad flat nose, heavy brow ridge, wide jaw, fine
blue fur, yellow eyes, canines resting over the lower lip, high swept-back ears, wild dark mane);
the costume adds the long arms and oversized clawed hands and feet. A first feline-muzzle mask
drew a werewolf; naming the character and the human-ape face shape did not. Daredevil's
"double-D emblem" drew one D; "a raised red 'DD' monogram ... two capital Ds interlocked, the
vertical spine of the second D passing through the open center of the first" draws the nested
pair. The ankle wings (Namor, Namora, Namorita) moved into `anatomy_note` ("feathered ankles: a
small white feather fan on each ankle bone, sticking out sideways just above the foot like the
winged heels of Hermes, each fan the size of a hand") with "bare feet" in the costume. That
drew feathers at the ankles and none on the back on four seeds. Wordings that said "wings" drew
back wings as well, and mentioning the back ("the shoulders and back are plain") drew them
there: never name the place you do not want.

### Not changed

Kakashi's forehead protector "pulled down over the left eye" still does not show (the random
hair covers it); random hair, beards, ages and Costume-only jewellery are the person under the
costume, by design. Zangief's scars read as a rash in one seed.

## 1.5.5 — an audit, four over-draws fixed, and a committed sweep gate

The maintainer flagged one symptom ("vitiligo pops too much") during a full-repo audit; the
same technique — a 5,000-seed-per-gender sweep of `generate_character(seed, gender, {})`,
flattened and counted per field value — found three more. All four share a cause: a value
that reads as visually loud, or survives almost every outfit, had the SAME flat weight (1) as
its ordinary peers.

- **`skin_details: "vitiligo patches"`** — 4.1–4.3% of ALL characters (flat weight, same as
  `"mole above lip"`), as common as an everyday mark despite being a far more distinctive
  trait. Weighted to 0.3, matching the existing scar weights in the same field. ~1.3% after.
- **`eye_color`: amber / honey / golden brown** — ~24% combined (flat weight 1 each over 23
  values), as common as dark + medium brown together. A "warm gold" look that visually reads
  as one family despite being three separate pool entries. Weighted to 0.3 / 0.5 / 0.6. ~12–14%
  after. Applies through `_bias_eye_color`'s ethnicity-conditional narrowing too, since
  `_weighted_choice` / `_repick` weigh whatever pool they are handed, not just the unconditional
  draw.
- **`hair_style: "wet look"` on a buzz cut** — 34% of buzzed women, 20% of buzzed men. Declined
  at 1.5.1 as a partial cull (excluding it alone would have dumped the old 9-variant
  `loose_natural` family's weight onto "natural and unstyled"). Un-blocked by splitting
  `loose_natural` into `loose_wet` (just "wet look") and `loose_natural` (just "natural and
  unstyled") — each keeps the pre-split per-variant rate exactly (280/2 = 140 either way) — so
  the exclusion now drops a whole family instead of a partial one. 0% after; see
  [[identity-forge-family-weight-rule]].
- **`tattoo_placement`: hand + neck** — ~55–60% of tattooed characters (both survive almost
  every outfit per `_visible_tattoo_placements`'s coverage gate, so a flat draw concentrates on
  them). Weighted to 0.25 each. ~35% after.

Reviewed and left alone: shot_type's three from-behind values (~11% of prompts) and indoor
lighting's studio-rig values (bokeh, lantern light, spotlights — drawing at the same rate as
practical light, as designed). Neither was a maintainer complaint, and the sweep found nothing
disproportionate about either once measured.

**`scripts/sweep_marginals.py`** is new: the AGENTS.md coherence checklist has always asked for
"a before/after sweep of every field's marginals" before shipping a new value, phrase or rule,
but every session wrote its own throwaway version — including the one that found the bugs
above. `--write` commits `tests/fixtures/marginals_baseline.json`
({gender: {field: {value: count}}} over 4,000 seeds/gender); `--check` re-sweeps and fails if
any value's share moved past a binomial-tolerance z-score (catches a new/removed value too,
since a missing baseline entry floors at a near-zero prior); `--report` prints 2x-mean outliers
for a by-eye scan. Both `--write` and `--check` refuse to run against a local
`user_options.json` (same class of trap `generate_js_data.py` documents — the baseline is
`{value: count}`, so a private addition's value string would be swept straight into a committed
file). Wired into CI after the gallery `--check` step, ~30s.

**Vault hardening**, all from reading `nodes/identity_forge_vault_save.py` /
`identity_forge_vault_load.py` end to end rather than from a specific bug report:

- `save_character`'s overwrite used to `shutil.rmtree` the old entry BEFORE writing the new
  one, so a write failure partway through (a locked preview file, a full disk) silently lost
  the old save. Now builds the new entry in a scratch dir outside `vault_root` (never listed —
  `list_characters` only scans `vault_root` itself), then swaps it in by rename, with the old
  entry only ever touched after every new file has written successfully.
- `save_character` now refuses a blank (`""` or literal `"{}"`) `character_json` instead of
  silently writing `"{}"` over a good existing save — a disconnected or momentarily-empty
  upstream wire used to be able to wipe a saved character.
- `IdentityForgeVaultLoad` gained a `fingerprint_inputs` override: the selected entry's
  `character.json` mtime + size now folds into the node's cache key, so an Overwrite,
  rename or delete that leaves the `character` widget unchanged still invalidates ComfyUI's
  cache. Before this, recalling the same name twice after an Overwrite could serve the OLD
  character from cache.
- `sanitize_name` now suffixes a Windows-reserved device name (`NUL`, `CON`, `COM1`, …,
  regardless of case or any extension that follows) — confirmed on a Windows dev machine that a
  save named `NUL` would otherwise target the null device, not an ordinary folder.
- Several crash-on-malformed-entry fixes, all the same shape (an access that assumed a dict
  sat outside the try/except that would have caught it): `_source_label` on a non-dict
  top-level `_meta`; `_entry_info` on a non-dict `meta.json` (this one took down the WHOLE
  `/identity_forge/vault/characters` listing, not just the malformed entry); `load_character`'s
  unwrapped `character.json` read. Also: `delete_characters` now checks `_is_entry` instead of
  `is_dir()` (a decoy directory that happened to sanitize to a requested name could be deleted);
  the HTTP delete route now type-checks `names` (an unchecked string iterated character by
  character); the rename route now also catches `OSError`, not just `ValueError`.
- `js/identity_forge_vault.js`'s Manage Vault modal dereferenced `null` when the vault API was
  unreachable (a separate code path from the node's own combo widget, which already degraded
  gracefully) — now shows "Vault unavailable" instead of leaving the grid silently empty.

**Smaller fixes:** `data/user_options.py`'s `covers_face` flag used `bool(...)`, so the STRING
`"false"` coerced to `True` and hid the face on a character that asked not to — now `is True`,
matching the other advanced flags in the same function. `tests/__init__.py` now purges any
`comfy_api*` entries from `sys.modules` before inserting the stub path (closes the local-only,
CI-harmless false-alarm this file has documented since the 1.1.0 investigation).
`OUTERWEAR_SEASONS`'s `dict.fromkeys()` now iterates `sorted()` frozensets, so the
`CONSTRAINT_RULES` built from it stop depending on `PYTHONHASHSEED` (latent, not currently
reachable — only one `outerwear` value is ever active and it is never re-picked mid-loop, but a
future rule that re-picks a deferred field through this list would have seen a different legal
set from one process to the next).

**Docs:** `docs/history.md` split out of `docs/architecture.md` (this file) — the 1.5.0–1.5.4
sections had grown to about half that file's length. `AGENTS.md`'s release list and known-gaps
section trimmed to match its own long-standing "one line, no paragraphs" rule. `SECURITY.md`'s
"no network calls" corrected (the opt-in gallery-picker thumbnails are the one exception) and a
note added about `--enable-cors-header` exposing the vault's mutating routes to cross-origin
requests. `README.md`: the Stylebook pairing section said `prose`, the actual output is named
`prompt_text`; a note that a seed reproduces a character only within one installed version (a
release can change pools/weights/rules), and that Vault Save/Load is how to keep a specific
character across updates.
