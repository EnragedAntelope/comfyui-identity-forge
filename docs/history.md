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

## 1.6.0 — content only: field values, the outfit corpus and new archetypes

A review mined third-party wildcard packs (DGirls, TheLook, a hairstyle list, an expression
list, a nested natural-language pack) for gaps. Most of what they offer already ships: the
locations include the landmarks, the hairstyle lists are mostly length x texture x colour (which
the engine composes from separate fields), and much of the rest is glamour or NSFW. What was a
real gap shipped; the engine and UX findings from the same review are the 1.7.0 backlog in
`docs/suggested-additions.md`. Shares below are from 2,000 seeds per gender.

**Bias rules applied to every addition.** New values carry the same weight for every
presentation (no `male_weights` on emotions or gestures). New hair colours join existing
families, so `_bias_hair_color` weights them by ethnicity automatically; `burgundy` is a dye and
joined `vivid`, so it draws only under Full spectrum or a lock. New braids joined `braid_short`
and inherit `_AFRO_BRAIDS` and the texture gates. New archetypes lock no `skin_tone`, and the
skin locks on `Korean Hanbok`, `Chinese Qipao` and `Vietnamese Ao Dai` were removed: in Full
preset they pinned the palest tones of the ethnicity's band (Ao Dai's `fair` sat outside it), and
unlocked, `_bias_skin_tone` draws the band's whole range. Essentials (the default) already drops
ethnicity and skin, so a cultural look goes on anyone there.

**Weather is a `lighting` family, not a field or a location variant.** Lighting already owned
hour, weather and light, and a separate field would need a widget, the JS legacy repair, and a
rule against every sunny lighting value. Weather-in-location multiplies places x weather and
dilutes each place. Two new families: `weather` (light rain, a fine drizzle, low fog) and
`snowfall`. They are outdoor-only, rain and fog skip arid places and the two sun-named places,
snow joins `_WINTER_LIGHTING` (so it forces winter, and a locked snow with a random season
resolves to winter) and stays off `_NO_SNOW_PLACES`, and all four exclude sunglasses. `weather`
is priced at three quarters of the window/artificial rate because the full rate put weather on
about 12% of outdoor renders; it now lands on 9–11%, snow on well under 1%.

**Expression.** A new `troubled` family (teary-eyed, frowning, worried, anxious, heartbroken):
the heavy mood is about 22% of renders but had three faces to wear it. It denies the positive,
calm and bold moods, its faces are closed-mouth, and it lands on about 7–8% of both genders.
`playful` gained winking, pouting and deadpan; `reactive` gained wide-eyed with shock, startled,
bewildered and flustered (both Mode A, family share unchanged). Two values were renamed before
shipping because the prose templates read them badly: `deadpan stare` became `deadpan` ("Her
expression is deadpan") and `hands clasped behind the head` became `clasping both hands behind
the head` ("He is clasping ...").

**Pose.** Weights rescaled x2 so the grown families divide evenly (no change to relative
shares). New: `gesture_social` (peace sign, thumbs up, waving, finger heart), priced below the
gesture rate and about 1.5% of renders, excluded by sad faces, heavy and enigmatic moods and an
extreme close-up. "Lost in thought" and "daydreaming" no longer draw "looking directly into the
camera" (the cheap part of the gaze idea; the field itself is deferred). Floor poses gained
seiza and side-saddle; side-saddle is trimmed from masculine presentation.

**Hair.** `faux hawk` grows `barbered_short` in place; `mohawk` is its own family at a quarter
of the everyday rate (about 0.6%), so the formal-dress and age-55+ gates drop it whole.
`hair_highlights` gained babylights, grown-out roots and a skunk stripe, and its first
`weights` entry holds the stripe to about 1.4% of women and 0.1% of men.

**Outfits.** The corpus gained entries filling the thinnest cells first (cocktail, evening,
business-formal and bohemian unisex; edgy and bohemian menswear), plus the shapes the corpus
had none of: ruffles, puff sleeves, Bardot and square necks, a cowl-neck slip, a corset top with
jeans, a bow-neck blouse. Pyjamas are `loungewear`, which is already limited to homes, hotel
suites, a hospital room and an airplane aisle; onesies and kigurumi were skipped as costume.

**Archetypes.** Metalhead; Wedding Groom (with four alternate gowns for Bridal Portrait,
append-only so existing seeds keep the original); Lehenga & Sherwani (the
sherwani half of the 1.5.0 "Saree + Sherwani" request); RCMP Mountie; Royal Guard; Evzone Guard (male, like
the real guard); Yukata (summer-locked, distinct from Geisha); Hanfu (distinct
from the qipao); Kebaya; Muay Thai Fighter (age and a standing pose locked, since both
survive Essentials); Dressage Rider; Fly-Fishing Angler; Highwayman. Metal slots were fixed to
gold or silver where the garment is only ever made in those (zari thread, a topknot crown).
Garment looks are named for the garment (Yukata, not Japanese Yukata): Essentials, the
default, puts the look on anyone, and the picker still finds them by ethnicity. Shipped names
keep their prefix, since nothing maps a renamed archetype for saved workflows.

**Declined:** see `docs/suggested-additions.md` → "Field options — declined (1.6.0)".

## 1.7.0 — engine and UX fixes from the 1.6.0 review

Five fixes the 1.6.0 review queued. None of them moves a draw, so a seed resolves the same
values as on 1.6.0; the prose wording changes where noted.

**"Roll + lock all" locks one engine roll.** The button used to pick each dropdown uniformly
in JS. A lock beats a guard, so the engine kept every pick, clashes included: over 50 such
rolls the engine logged 799 lock conflicts ("waist length" hair locked beside a quiff). The
button now posts the node's widgets and a fresh seed to `POST /identity_forge/roll`, which runs
the node's own path (`run_identity_forge`, factored out of `execute`) and returns every resolved
field. Each `Random` field locks to that value, and a field the run left absent locks to `None`.
The same 50 rolls log one conflict, and a test pins that re-running a locked roll reproduces it
field for field. The route is read-only and shares the vault routes' JSON content-type check.
Without it (an older server) the button falls back to the uniform pick and warns in the console.

**A framing that crops the feet no longer names the shoes.** Extreme close-up through cowboy
shot (`_FEET_OUT_OF_FRAME_SHOTS`) drop the footwear clause from the prose; full-body framings
keep it. The JSON keeps `footwear` in its `outfit_description`, because a Turnaround or Vault
replay reads the shoes from there and may re-frame to full body. Turnaround's composed shot
("medium shot from waist up, side profile") matches on its distance half. Footwear the user
locked on the widget is still voiced; a wired lock is not, because a Vault Load replay wires
every field back in (and hands the outfit back as a costume, whose path pops `footwear`), and
a test pins that a same-shot replay reproduces the trimmed prose. Measured: from about 14% of
tight framings to none.

**Hair reads as prose.** Every noun style now gets a connector, as the gathered styles already
had since 1.5.3: "worn in a fade", "worn in a French braid", "with curtain bangs", "with a wet
look". Styles that are already predicates ("worn down", "slicked back") keep their words, and a
free-text style outside the families is voiced as written. The two noun lengths go last behind
an article ("a sleek straight dark brown chin length bob"). Before, about 58% of hair sentences
ended in a bare noun ("hair is very short loosely curled jet black, fade"); now none do.

**A footwear or legwear modifier reaches a generated outfit.** The composed `outfit_description`
voices those values verbatim, but `_apply_modifiers` decorated only the field, so the prose
showed the plain shoes. The decorated value now replaces its last whole-phrase occurrence in the
composed outfit. Colour and pattern are rewritten when composed, so they are left as a backlog
item. The Modifier node's help example used group keys (`Makeup`, `Setting & Shot`) that
decorate every field in the group, staging fields included ("galaxy-glitter smiling"); it now
shows field keys and says what a group key does.

**`generate_character` is keyword-only from `widget_locked`.** It was documented so, but had
no `*`, and `execute` passes the parameters before it positionally: one inserted mid-signature
would silently shift every argument after it.

## 1.8.0 — facets read flags, ethnicity locks only in Full, `subject_text`, and a reachability gate

**Picker trait facets read structured flags, not prose.** The Tiny / Giant / Masked / Mascot /
Non-human / Beast facets matched words in the costume, so Poison Ivy ("tiny leaves") showed as
Tiny and a green-skinned human as Non-human. `scripts/generate_js_data.py` now emits a `traits`
list per cosplayer, computed from the same data the backend's `_SPECIAL_SCOPES` predicates read
(`size_scale`, `covers_face`, `covers_body`, `mask`, `body_plan`, the body-paint marker).
`RosterTraitsMatchBackendScopes` compares the committed roster's traits with those predicates, so
the picker and the Random scope cannot disagree. Facets apply to cosplayers only; archetypes and
creatures carry no traits.

**Ethnicity and skin tone lock only in Full character / Full preset.** A signature `skin_tone`
and costume prose that named a natural skin tone ("over fair skin") locked both under Essentials,
which promises a Costume-only lock. They moved to `physique` (Full only) or out of the prose;
Essentials archetypes no longer keep `skin_tone` from the Body group. Stylized or supernatural
pallors (Kratos, Dream of the Endless, a Ferengi and similar) stay in the costume and are listed,
each with its reason, in `_STYLIZED_PALLOR_OK` in `tests/test_engine.py`. The regex sweep over
costume prose is the test that keeps new entries honest.

**`subject_text` output.** A new last output: the person and their outfit, with no pose, smile or
scene, so it can feed a prompt that has its own scene. The prose output is byte-identical with
and without it (200 seeds pinned). Shoes stay on close-ups, unlike the prose; the cosplay label
stays.

**Colour and pattern modifiers reach a generated outfit.** `_compose_outfit_clause` records the
hue and pattern adjective it voiced; `_apply_modifiers` decorates that word, with the right
article ("an emerald" becomes "a faded emerald"). A group key still decorates as before.

**Roster.** New cosplayers: Megamind, Alita with a Motorball alternate, Sesshomaru, Raya,
Barbie with the pink cowboy and 1959 swimsuit looks, Minion, and Lord Fanny and Ragged Robin
(The Invisibles, a new franchise in the DC category; Ragged Robin's Volume 2 leather look is
an alternate). Effie Trinket was rewritten rather than duplicated: the Reaping look is the
primary and the Catching Fire liquid-gold look the alternate; the unverified grey Mockingjay
alternate was dropped. "Julia Carpenter" and "Spider-Woman (Julia Carpenter)" were one
character listed twice, so they are now one entry with the classic suit as an alternate
(a saved workflow naming "Julia Carpenter" falls back to a random pick). Three archetypes
(American Football Player, Scuba Diver, Thai Classical Dancer) and one creature
(stegosaurus). Canon was written from knowledge plus the maintainer's hooks, not from reference
images. Anxiety was declined (see `docs/suggested-additions.md`).
The football archetype is gated to the two park locations because no stadium location exists;
adding one is a field-value change and was left out.

**Reachability.** Every value in a field pool that no gender draws under default widgets is now
listed by `python scripts/sweep_marginals.py --unreachable` and must match
`tests/fixtures/unreachable_by_design.json`, each with a reason: the control widgets, the vivid
hair colours (Natural scope), `bleached` eyebrows (Full spectrum), the four studio backdrops
(Studio setting), `thin headband` (removed for men in 1.5.0) and `behind one ear` (lock-only
since 1.5.1). `test_sweep_marginals` fails on a new accidental gate and on a stale exception.
A value only one gender draws is a gendered coherence filter, so it is not listed.

**Coherence checklist for this release.** Items 1-6 were run for each new value, phrase and
entry. Hidden items: the football helmet is held, the dive mask is pushed up on the forehead and
the fins are on the feet (full-body framing only). Masculine defaults: the wetsuit and the pads
read for either gender, so no single-gender costume ships without variants. Gating: the sweep
baseline did not move (`--check` clean at 4,000 seeds per gender), and `ethnicity` and
`skin_tone` stay flat across genders in `--report`. The Random cosplayer pick stays uniform; the
roster only grew.

**Saved widget order readable without a browser.** ComfyUI writes `widgets_values` positionally,
one entry per `node.widgets` item, buttons included. `IdentityForge` and `IdentityForgeCreature`
re-sort their widgets under headers and `IdentityForgeCosplayer` splices `franchise_filter` in
after `character`, so a headless tool mapped the array onto the wrong inputs. Each now saves the
schema widgets only, marks the save `properties.if_widget_order = "schema"`, and expands a marked
save back into display order on load; unmarked (pre-1.8.0) saves take the legacy path unchanged.
Read in the installed frontend bundle rather than assumed: a widget added with
`{serialize: false}` carries it in `options` only, so it still takes a positional slot, and
restoration indexes `widgets_values` over every such widget. The jsdom suite pins serialize,
round trip, a pre-1.8.0 interleaved save, and a marked save one field short. **Not run live:**
the server loads a separate installed copy of the pack, so the Playwright check in both
renderers is left for the maintainer after pulling the branch there.

**CI.** `ci.yml` is callable, every job has a 30-minute cap, and a Windows leg runs the suite
with autocrlf off. `publish_action.yml` runs it first and `publish-node` needs it, with no new
write scope.

## 1.9.0 - independent-comics curation and maintenance

**Canon before supplied AI descriptions.** Mervyn Pumpkinhead uses the comic look in
[Todd Klein's published panel](https://kleinletters.com/LetteringImages/MervP.jpg):
orange carved pumpkin head, a thin scarecrow frame, white shirt, denim bib overalls,
green bow tie and work gloves. The optional broom is supported by
[Netflix's character reference](https://www.netflix.com/tudum/articles/the-sandman-merv-pumpkinhead-mark-hamill-clip).
He is human-scale, not a giant, and the pumpkin head and wooden body use the existing
head/body concealment flags. `Merv Pumpkinhead` is an alias, not a duplicate entry.

Prince Robot IV earns the Saga entry on the television head and cavalry uniform,
shown together on [Fiona Staples' Saga #12 cover](https://imagecomics.com/comics/releases/saga-12).
Its screen can show color bars; an extra held gun would misrepresent the character's
transforming hand, so none was invented. The worn military look and artificial head
remain separate for Unmask.

Crow's look follows [Nick Dragotta's original drawing](https://www.2dgalleries.com/art/crow-from-east-of-west-93778?lang=en)
and [Image's free East of West #1](https://imagecomics.com/read/east-of-west):
ink-black skin, extremely long white hair, an ivory marking across the eyes, a
layered pale collar and necklaces, pale arm bands, white loin panels and boots.
The supplied black face wrap and striped tactical bodysuit were not supported by
that artwork. Her optional props are paired short knives; no permanent magic aura
was invented. She files under `East of West`, separate from Eric Draven's `The Crow`.

Bloodshot uses [Barry Windsor-Smith's classic omnibus cover](https://valiantentertainment.com/comics/bloodshot/bloodshot-classic-omnibus-vol-1-hc/):
paper-white skin, red eyes, short black hair with a white temple streak, an open
shell-loaded dark vest, an exposed red chest disc, olive military trousers and
combat boots. Paired pistols are optional. The supplied exact height and weight
were not corroborated, so he retains normal human scale with a tall, muscular
build. For both Crow and Bloodshot, random human face and hair sentences washed
out their defining colors in the first samples. Their actual heads now use the
existing authored-head field (`mask` with `covers_face`), as other nonhuman heads
already do; this does not invent a worn face covering. Their body skin color also
stays explicit in the costume text.
The final samples kept Bloodshot's shell loops and white temple streak, and
Crow's white eye-mask pattern after explicit painted-makeup wording.

**Savage Dragon.** The [official profile](https://wiki.savagedragon.com/profiles/characters/Dragon/)
lists green eyes, a bald head and a disproportionately massive upper body. It gives
5'10" without the fin and 6'6" to its tip, so the old `very tall` physique was wrong
and a giant tier would be wrong too. The fin leads the anatomy sentence; the head is
authored separately to suppress random human facial traits, and `bald: True` also
suppresses any random hair. The white tank top, jeans and utility belt follow the
official art. No generic weapon or healing aura was added. The entry now files under
`Savage Dragon`, rather than the publisher-level `Image` bucket.

**Other silhouettes were gated by rendering.** Morris Dancer uses a coherent
[EFDSS Cotswold kit](https://www.efdss.org/learning/resources/beginners-guides/34-english-folk-costume/2462-efdss-section-3-cotswold-morris):
white shirt and trousers, crossed colored baldrics, rosettes, a floral straw hat,
shin bell pads and handkerchiefs. The review image preserved those features and
stays distinct from Court Jester's motley. A barreleye candidate had new anatomy
on paper, but its render lost the transparent dome and put ordinary eyes on the
outside of the fish head. It was removed before review; the remaining case and
render gate live in `docs/suggested-additions.md`. The Corinthian also stays a
candidate until exposed tooth-lined eye sockets render correctly; a suit and
sunglasses alone do not earn an entry. Existing Sandman characters were not
duplicated to fill out the cast.

**Gallery manifests have one owner.** Removed the stale deployment snapshots from
`main` for every gallery and ignored their paths. The publisher already rebuilds each
manifest from the staged images on `gh-pages`; it never copied these snapshots, and
the picker already fetched the live site. Local preview instructions are in
[gallery/README.md](../gallery/README.md). `gallery/render_manifest.json` remains the
tracked render-hash gate. Exercising each real manifest generator against a temporary
images directory proved the deleted snapshots are unnecessary.

**Pyright contracts.** `generate_character` has overloads for its default pair,
`with_subject=True` triple, and a dynamic boolean. The runtime parameters and engine
body are unchanged. Parsed presets and archetype templates now admit their existing
nested metadata and list alternatives in their annotations. Tests narrow optional
values before indexing or membership checks; diagnostics are fixed at their source,
without diagnostic suppression. The Random character snapshot is refreshed for the
curated roster; the field-marginals baseline remains unchanged.

**Validation.** The full dependency-free Python suite passed (the image test that
requires Pillow was skipped by that interpreter). The frontend suite, Ruff and
focused Pyright check passed. Reference docs, JS data, frontend fixtures, release
stamps and gallery hashes are current. The field-marginals baseline and reachability
gate passed, as did the public-safety and maintainer documentation checks. Review
renders were published to the galleries at merge.

## 1.10.0 - engine and tooling: expression sheets, a free-text prop, and a publish gate

Random characters do not move: `sweep_marginals.py --check` reports no drift against the
4000-seed baseline. Four cosplay entries do: the garment-regex fix below changes their pose
pool (Bartok, Lola Bunny, Tellarite and Tasmanian Devil, each "a coat of" fur or hair).
Found by diffing `resolve_prose` for every gallery entry against the previous release;
`render_gallery.py --check` cannot see it, because `entry_hash` covers the entry's data,
not the engine's prose. Hashing the resolved prose instead would catch an engine change
too, but it marks every record stale, so it waits for the 2.0.0 re-render.

**Those four re-renders exposed bad entries, repaired here.** Each had its defining
anatomy in the costume text, which a t2i model reads as a person in clothes:

- Bartok drew a man in a shirt holding a small bat. A foot-tall upright bat nobody can be
  inside is the feral case (architecture.md -> "Animal characters split four ways"), so
  it is now `body_plan: "feral"`, tiny, with its own upright poses.
- Lola Bunny drew a human face in a blonde wig with no ears; Tasmanian Devil drew a
  man's bare face over a shaggy suit. Both now follow their Looney Tunes siblings Bugs
  and Daffy: the head, ears and jaw live in `mask` with `covers_face` + `covers_body`.
- Tellarite drew a plain man in a tweed overcoat: the snout was lost and "a shaggy coat
  of thick facial and body hair" drew a garment. Four rewordings failed (an authored
  head; head plus `covers_body`; the canonical porcine description; a beardless boar
  head): each drew a human or a generic ridged alien, never the snout and tusks. The
  entry keeps its 1.9.0 text and tile, and the attempts are logged in
  `docs/suggested-additions.md` for 1.11.0.

**Expression Sheet node.** The backlog asked for a re-run like Turnaround that "releases"
`smile_type` and `mood` per view. Releasing would need a seed per view and could land two
views on the same face, so each view instead pins a curated (expression, mood, smile_type)
triple. Tests check every triple's values are still live options and that no triple pairs
values a live rule excludes (a lock beats a rule, so the engine would otherwise voice a
contradiction). A `covers_face` character has no visible expression and emits one view.
The node reuses the Turnaround's replay helpers rather than copying them.

**Free-text `held_item`.** It lives on the Modifier node as an optional box, so the main
node's schema is unchanged. It is emitted as an ordinary `held_item` lock, which means the
existing "holding ..." voicing and the hands-occupied pose gate already apply; downstream
wins in `merge_preset_documents`, so it replaces an upstream Cosplayer prop. The input is
appended after `upstream`, keeping saved workflows' `widgets_values` order.

**Legwear in a tight shot.** The 1.7.0 rule drops the shoes from the prose when the framing
crops the feet. Legwear now follows for the framings that also crop the legs; the cowboy
shot is the one feet-cropping framing that still shows the thighs, so it keeps them. Prose
only, no draw, the JSON keeps the value, and a widget lock still voices it.

**The pockets gap was mostly stale.** AGENTS.md listed `_POCKETED_RE` as an allowlist that
lets a pocketless costume draw a pockets gesture. Measured over every cosplay entry
(8,340 renders), 47 drew a pockets gesture and all but one were legitimate. The one bug was
a body, not a garment: Bartok's "coat of downy white fur" matched `coat`. In the roster
"a coat of ..." is always fur, feathers or paint and "a suit of ..." is armour, so the
collar, cuff and pocket regexes now refuse a garment word followed by "of". The gap is
removed from the known-gaps list.

**Typing overloads kept, guarded.** A review suggested dropping the three
`generate_character` overloads. Removing them broke pyright at `execute`, which unpacks the
triple. They stay, and a test now compares each overload's parameters, annotations, keyword-
only arguments and defaults with the implementation by `ast` (CI runs Python 3.10, which
cannot introspect overloads), so a signature change that skips the stubs fails.

**Gallery publish gate.** The render loop now records `"published": false` for a new
image and flips it to `true` only after `publish_kind` succeeds; `--check` fails on a record
still marked unpublished. A missing key counts as published, so earlier records pass.
`--publish-pending` publishes those images without re-rendering. The six 1.9.0 images
thought to be unpublished were already on `gh-pages`; the mismatch was a git quotepath
artifact on "Dia de los Muertos".

## 1.11.0 - roster release: new cosplayers, retro archetypes, a drive-in, and four declines

Random characters move through one change only: a new location value, `the parking lot of
a retro drive-in diner with classic cars`, joins the `urban_outdoor` family. Family weights
are frozen, so the family's share is unchanged, and the marginals sweep shows no other share
moving (`sweep_marginals.py --check` reported only the new value, at about 0.6%, before
`--write`). Per seed the move is wider: every seed that draws the family re-picks within a
longer list, so it can land on a different street place, and its outfit, lighting and pose
then re-resolve to fit. A main-vs-branch diff of 1500 seeds per gender changed 225 of 4500
characters (5%), every one of them with a moved location; 17 landed on the drive-in. A location
cannot be lock-only: the validator requires the families to partition the options with
positive weights, and the engine draws any leftover value. The value is also in
`OUTDOOR_LOCATIONS`, the neon-signage venues and the floor-free places (an asphalt lot
takes no floor pose).

**New roster, each render-gated.** Cosplay: Miles Morales, Spider-Punk, Sylvie, Doc
Brown (the 1985 radiation suit), Elle Woods, Vecna (reopened on the mascot-suit route: a
full prosthetic body), Enid Sinclair, Messmer the Impaler, Laios Touden, Himmel, Jin
Sakai, Charlie Morningstar, Angel Dust, and Birdie the Early Bird (the backlog row closed:
the aviator cap, pigtails and flight suit are what the other bird mascots lack).
Archetypes: 1970s Fast-Food Crew, Carhop, Bellhop, Mail Carrier, Roller Derby,
Majorette, Mountaineer, Zoot Suit, Lounge Singer, 1950s Gas Station Attendant and Rodeo
Rider. Creatures: frilled lizard, quetzalcoatl, leafy sea dragon and giant isopod.

**Gallery framing pins.** `render_gallery.py` gained `_GALLERY_SHOT`, alongside the
gender and pose pins: a sample whose defining feature sits below mid-thigh must not draw a
cowboy shot. Carhop (roller skates, pinned female) and Zoot Suit (the knee-length drape)
use it. A test checks every pin names a real archetype and an allowed gallery framing.

**Carhop.** The first tile drew the male variant in a cowboy shot, so the skates never
showed. A pastel dress alone read drab, so the women's `outfit_description` is now a
seed-picked list: a bright `{team_color}` dress with white trim and apron, or a
`{pastel}`-and-white candy stripe. The location moved from an indoor diner to the new
drive-in lot, under golden-hour or neon light.

**Repairs.** Lola Bunny's costume names fur on the arms and legs and "furry tan rabbit
paws for hands"; with fur on the limbs alone, the render still drew bare human hands. The costume's "covering her bare
arms" became "the bare arms": costume text stays pronoun-free so crossplay reads
correctly (`CostumePronounTests`). Tellarite ships the canon text (a full latex
prosthetic head with snout, tusks and beard, on the mascot route) at the maintainer's
call. It still renders a ridged brow and a beard with no snout, no worse than the 1.9.0
text, and it drops the "shaggy coat of hair" that drew an overcoat. The snout stays open
in `docs/suggested-additions.md`.

**Declined on the render bar** (one rewording each, reasons in
`docs/suggested-additions.md`): The Corinthian (the eye-socket mouths never drew),
Feyd-Rautha (the chalk-white hairless head never held), the women's pachuca variant of
Zoot Suit (a cropped vest twice; the archetype ships men's only), the barreleye (the
transparent dome never drew), and the vampire squid (the webbed cloak never showed; a red
squid already ships through `squid`'s palette). Verso, Rockabilly and the thorny devil
were declined before rendering as near-duplicates of shipped entries.

**Render-script gotcha.** A render can fail with `OSError: [Errno 22] Invalid argument`
on the output PNG when that file is open in a viewer. Move the old image aside before
re-rendering an entry someone may be looking at.

## 2.0.0 - the seed epoch: every seed-moving change at once

**Seeds break in this release, on purpose.** A given seed resolves to a different person
in 2.0.0 than in 1.11.0, for every gender. Every
change that had to move seeds was held back into this one release so the break happens
once. Over 4000 seeds per gender against 1.11.0, every seed changed at least one field
(gaze on all of them, by construction; pose, outfit and age on most). The per-item numbers
below are each step diffed against the step before it, measured with the same 4000 seeds.

**`gaze`, a new widget.** The `looking` family of `pose` (seven values) moved into its own
field, appended last in the schema and drawn last with `pose` (see architecture.md -> "pose
and gaze draw last"). A character can now stand one way and look another, and the gaze is
gated: a view from behind turns the head back over the shoulder, a selfie and a social
gesture look at the lens, walking toward the camera never glances back, lost-in-thought
never stares into the lens, and warm or intense expressions do not look down. Step diff:
4000/4000 seeds per gender changed (gaze on all; pose on 7742 of 8000, because `pose` now
draws after the outfit; outfit on 7061, because pose no longer consumes a draw mid-loop).
Shares over 1000 seeds per gender: looking into the camera 31.1%, off past the camera
21.1%, tilting the head 14.9%, lifting the chin 12.0%, over one shoulder 11.7%, glancing
back 7.2%, looking down thoughtfully 1.9% (the turn-back share is mostly forced by
from-behind framings). First weights gave 23% turn-back gazes; the two were lowered.
0 live-rule violations for pose or gaze. A save that locked a `looking` pose migrates to a
gaze lock. The Expression Sheet gained a `gaze` input; a Turnaround that pins the stance
states no gaze.

**`pose` is deferred, and `_repair_pose` is retired.** The 0.92.0 repair existed only
because moving the pose draw would move seeds; in the epoch release the clean fix is
allowed. Pose now draws after the generated outfit, so the pocket/collar gesture gate reads
the real garment, and its rules are live (the from-behind pose rule was rewritten as an
allowlist of back-readable poses).

**Women's hair length and the oldest ages.** The three shortest women's lengths were
weighted to 0.4 (9.7% of women over 4000 seeds, down from 22.1%); `75` and `80` joined `age`,
weighted so 60+ holds near 16% (first tuning gave 14.4%; retuned to 16.1%). Step diff:
3995/4000 female and 3898/4000 male seeds changed (a new age option shifts the weighted
index for every seed).

**Studio lighting needs a studio.** A portrait rig (`studio_shape`) no longer lights an
everyday interior; it stays legal in a studio, outdoors, and in the listed interiors that
own one (`_STUDIO_LIT_INTERIORS`). The first cut gated the whole studio family and caused
48 archetype lock clashes, so the family was split: `studio_shape` (the rigs) is gated,
`studio_mood` (low-key, colour gels and similar) is not. Indoor rig lighting fell from
32.6% to 1.7% of indoor renders; mood lighting rose from 14.4% to 20.7%. Step diff: about
1936/4000 female and 1882/4000 male seeds changed.

**Per-garment variation slots.** Seven corpus phrases in the thinnest style x gender cells
carry `{slot}` words (knit weight, chino cut, skirt length, tee fit, work canvas), filled
from their own seed stream so a slot moves no other draw; season and age gates apply per
value, and a leg-cropping framing drops the skirt length from the prose. Two slot values
were changed before shipping so every value answers every garment guard the same way
(`ribbed` -> `rib-knit`, `moleskin` -> `twill`); validate_data.py now enforces that. Step
diff: 59/4000 female and 115/4000 male seeds changed a field (the outfit text, plus the
gates that read it: legwear, tattoo placement, pose, gaze, pattern), 47 female seeds
changed prose only (the length trim).

**Turnaround back views (`costume_back`).** The first known gap from 1.x: a back view drew
the chest emblem. Entries may now carry an opt-in `costume_back`, swapped in for back and
rear-three-quarter views. The first entries are Superman, Batman, Spider-Man, The Flash,
Captain America and Wonder Woman; verified that the back views swap the text for all six in
both Costume only and Full character, and every other view is unchanged.

**Prose-only items.** An eponymous entry no longer reads "Name (Name)" (93 entries, e.g.
Sailor Moon, Mulan, Bayonetta). A noun expression takes an article ("her expression is a
bright smile"); 16.6% of random characters draw one.

**The gallery hash covers resolved prose.** `entry_hash` now hashes what the entry renders
from rather than the entry dict, so an engine change marks its images stale (it could not
before; see architecture.md -> "The gallery render pipeline"). Its first run marked every
entry stale, because every entry's prose moved with the seeds.

**No full gallery re-render (maintainer decision).** The plan was to re-render the whole
roster once. It was dropped: no entry's own text changed, only the random person and scene
around it plus a gaze clause, the same incidental drift 0.90.0 and 0.97.0 accepted, and
`costume_back` only reaches Turnaround back views, which the gallery never renders. Three
samples were rendered and published (Superman, Carhop, owlbear); every other record was
accepted as-is with the new `render_gallery.py --rehash`, which moves only the recorded
hash. From here the prose hash flags any entry whose text changes.

## 2.1.0 - droids render as droids, a lead noun for non-human faces, Orion, a picker gender filter

**Random characters are unchanged.** Every change is a roster entry's own text, a new
roster entry, or the picker UI. Two knock-ons for the Cosplayer node's random picks: the
three droids and Pac-Man leave the `Masked` scope and the "People only" `random_pool` for `Beast /
non-humanoid`, and the new entries grow the candidate list, so a fixed seed under any
`Random - ...` choice can now pick a different character (as at every roster release).

**R2-D2, BB-8 and Gonk Droid moved to `body_plan: "feral"`.** The maintainer saw a man
posing beside R2-D2 in the gallery. The published BB-8 tile showed the same thing, and Gonk
showed a man's head out of a grey box. All three were suit entries whose prompt led "a short
man with a stocky build ... He wears a ... droid body": a famous name makes the model draw the
machine as an object, and the sentence then adds a person next to it. As feral entries
("R2-D2 (Star Wars), a three-legged astromech droid, ...") all three rendered as the droid
alone on the first seed. Chopper and Lumiere stay suit entries: both rendered correctly
because their long descriptions win, and neither tile is wrong. The feral route was written
for animals, so this opens it to non-humanoid machines with a cosplay-only
`creature_class: "Machines"`; see architecture.md -> "Writing a feral entry". The Claptrap
and Wrecking Ball declines rested on the old "a machine is not a beast" reading, and are
marked lapsed in suggested-additions.md.

The look level was considered as the switch ("Costume only" = a person in an R2-D2 costume,
"Full character" = R2-D2 itself) and not built: the person-in-costume reading is exactly the
render that failed.

**Blue Beetle (Ted Kord) rewritten.** The entry said black cowl, black gloves and boots and
"large round black goggles", and rendered a black hood with black swim goggles. Canon
(Wikipedia plus figure references) is a light-blue suit with dark navy gloves, trunks, boots and
cowl, a dark beetle shape across the chest and shoulders, and yellow goggles. A maintainer-
supplied description added white lenses and antenna lines on the cowl; no source backed either,
so neither was used. The first render drew the right suit on a heavy 55-year-old; one
`--reroll` gave the published tile.

**More machines and enchanted objects.** Claptrap, WALL-E, Dalek, Johnny 5, Codsworth and
Mrs. Potts ship on the feral route, and Cogsworth on the suit route beside Lumiere (arms and
legs where a person's are). Every one rendered as the machine or object alone on its first
seed, with no person in frame. Wrecking Ball, BD-1, the Mouse Droid and K-9 were declined;
see suggested-additions.md.

**The sd-character-finder survey.** The catalogue (Danbooru, e621 and AnimaDex tags with a
popularity rank) was ranked against the roster. Its unmatched top is mostly large uniform or
gacha casts the backlog already closes, so the survivors ship: the first Touhou entries (Reimu
Hakurei, Marisa Kirisame, Sakuya Izayoi, Yukari Yakumo), Black Rock Shooter, Noriaki Kakyoin,
Mash Kyrielight, Edelgard (her Part II emperor look), Shantae, Catra (the 2018 reboot, its own
franchise beside the 1985 She-Ra) and Kasane Teto as worn looks; Toriel, Undyne, Doraemon,
Hello Kitty, Kuromi, Meta Knight, King Dedede, Monokuma and Tony Tony Chopper on the mascot
route (the last two with the Pikachu scale pin); Snoopy and Kyubey on the feral route. The
Hololive VTubers were left out at the maintainer's call; Domo-kun, the maintainer's own pick, joins on the mascot route. Two authoring notes: a body-colour
clause needs a material noun ("a coat of blue fur"), or the colour capture runs on to the
next comma and voices "a red skin"; Doraemon uses the `skin` key instead. A feral pose
sentence follows "He is", so it cannot say "its back".

**Unmask on a droid.** The question was whether "Unmask (show face)" should put a person
inside a droid. It already does for a suit entry (C-3PO, Lumiere, Cogsworth): a cosplayer
with the helmet off. It stays a no-op on a feral entry, because a human head on R2-D2's body
is the Gonk render this release removed. The mask tooltip now says so.

**Roster picker gender filter.** A Female / Male select beside the trait facet. Entries with no
single gender (creatures, "Any" archetypes) stay visible under both choices. Like the facet,
it survives closing the picker and resets on reload.

**The lead noun (`subject`).** The Tellarite repair from 1.11.0 stayed open because the
snout never rendered: the prompt led "a short man with a stocky build" and the mask
sentence that followed lost to it every time. A new optional `subject` key replaces
"man"/"woman" in that lead (architecture.md -> "The lead noun: `subject`"). With
"pig-headed humanoid alien" the Tellarite drew the snout and beard on the first seed. The
same test ran on every masked or mascot entry whose published tile showed a person, each
trial at the gallery seed beside the published tile:

- *Kept:* Kuiil, Unkar Plutt, Ithorian, Nien Nunb, Bothan, Kilowog, Larfleeze, Ponda Baba
  (with a walrus-led mask rewrite), Mynock, Krampus, Ainz, Spinal, Witch-King, Orko, Vivi,
  and the mascots that had drawn a person holding a plush: Pikachu, Jigglypuff, Gengar,
  SpongeBob, Mr. Krabs, Eeyore, Piglet, Sackboy, Kool-Aid Man, Mr. Peanut, Rosie the
  Robot, White Rabbit, Ultros and Voldo. Gardevoir ships with one from the start.
- *Moved to the feral route instead:* Pac-Man. With the noun it was still a person in a
  yellow suit; as the character itself ("a round yellow arcade character") it rendered as
  the arcade Pac-Man alone on both seeds. A cartoon version with arms, gloves and red shoes
  rendered as well; the arcade disc is the better-known look, and a feral entry has no
  alternates. A person-in-a-Pac-Man-suit option was not kept: that is the render that failed.
- *Kept, with a new mask:* the noun alone still drew a plain man for Red Skull and a
  human face for Moon Knight. Rewritten as "a full-head red latex Red Skull mask" and "a
  full-head white cloth mask wrapping his whole face", both rendered right on both seeds.
  Porco Rosso, as "a pig's head instead of a human head", gets the ears and snout on one
  seed of two; nothing tried did better.
- *Obscure aliens:* several Star Wars species are close to unknown to the model. They keep
  the noun and the most specific description sources support; that is where they land.

**One eye is a model limit.** Allen the Alien and Leela are cyclopes, and every render drew
two eyes. Tried, two seeds each: the noun ("one-eyed cyclops alien", "cyclops woman"); an
eye phrase saying "no other eyes"; a latex cyclops mask; a cyclops face prosthetic on Leela
(which also dropped her purple hair); a close-up framing. All failed. A bare prompt ("a
photo of a big orange cyclops alien with one huge eye in the middle of his face") drew one
eye on both seeds, so the model can do it, but the same prompt prefixed with "Cosplaying as
Allen the Alien (Invincible):", or lengthened to the gallery's detail, drew two again. Both
entries keep the cyclops noun and their best text; Leela's costume no longer lists "a single
large central eye" as something she wears.

**Two-colour eyes.** An `eyes` override is voiced as "She has <eyes>", so "one blue and one
yellow" read "one blue and one yellow eyes". Catra, Frankie Stein and Ragna now say "one
blue eye and one yellow eye" in full.

**Orion.** The TOS dancer (jewelled two-piece, veils, bangles, green skin) is the canonical
look; Gaila's red Starfleet cadet dress (Kelvin films) is the alternate. The new
`costume_weights` key leans the pick 2:1 toward the dancer (measured: about a third of seeds
draw the cadet), without moving any other entry's seeds (architecture.md -> "Weighted
alternate looks").

**The survey's second tier.** Hilda, Gloria, Iono, Gardevoir (mascot), Byleth, Nagito
Komaeda, Chiaki Nanami, Jonathan Joestar, Tamamo no Mae, Falin Touden, Senshi, Suletta
Mercury, the four RWBY leads, Wild Tiger and Barnaby, Nanoha and Fate, Ragna and Noel,
Arcueid Brunestud and Serval. Kiana Kaslana and Caesar Zeppeli were declined (no one stable
outfit, colours not verifiable); see suggested-additions.md.

## 2.2.0 - Cyberpunk roster, Volcana, period court dress, a picker franchise filter

**Random characters move through the outfit corpus and one new location** (below). Four new phrases (three in
`edgy alternative`, one in `vintage retro`) change which outfit a fixed seed draws in those
two styles; field marginals still match the committed baseline (`sweep_marginals.py
--check`). Nine creature gallery tiles whose outfit draw moved were re-rendered.

**Cyberpunk entries checked against Danbooru tag counts and the wiki, not the brief.**
- David Martinez wore a red bomber; canon is the yellow EMT jacket with the glowing blue
  collar. Panam Palmer and Rebecca were rebuilt the same way (Rebecca's tagged skin is
  chalk-white with seam lines, her eyes green on red sclera; the huge cyberarms are a
  weighted alternate).
- New: Maine, Kiwi, Talia Yang (Edgerunners 2), Adam Smasher (a full-body suit entry, the
  C-3PO precedent), Song So Mi (green gown primary, netrunner alternate at weight 1 of 3).
- The brief's Maine (buzzcut, yellow optics) and Pilar (white pompadour, pink skin) did not
  match the sources; Maine follows the tags (flattop, red shades), Pilar was declined.

**Volcana (DC)** ships with fair skin and red-orange hair; the brief's olive skin is not in
the sources.

**A costume that names earrings or a necklace now suppresses the random one**
(`_COSTUME_JEWELRY_RES` in the Cosplayer node), so Volcana's gold hoops no longer sit beside
a second pair in Costume-only mode. Full character already dropped random jewellery, so no
gallery tile moved.

**An eyes override must not end in an eye part.** Kiwi's "feline red, yellow-sclera" dropped
the noun "eyes" (`_EYE_PART_RE`); the adjectives were reordered.

**Period court dress.** Rococo Courtier, Medieval Monarch, Ottoman Court and Heian Court were
added from a 15-prompt historical-costume list; the rest were existing looks under other
names (see suggested-additions.md -> "Archetypes - declined"). Ancient Roman Patrician gained
a Female variant (stola and palla). The new looks lock "no tattoos", and `_is_essential` now
keeps a `tattoos` lock in Essentials: before this a Heian court lady drew a modern script
tattoo. No older archetype locks tattoos, so nothing else moved.

**Picker franchise filter.** The roster picker gains a franchise select beside the gender
filter, grouped by category, kept for the session like the other filters.

**The outfit wildcards were mostly not usable.** The punk and pinup packs are lingerie worn
as outerwear, with footwear and fabric jargon built into each line; they break the corpus
contract and would tilt women's outfits toward sexualized looks. Four phrases were taken,
with pattern words (tartan, leopard, gingham) removed because the `pattern` field owns them.

**Render-review fixes.** Adam Smasher drew a human face over the armor ("a very tall man"
led the prompt); a `subject` of "towering armored cyborg" fixed it. Talia Yang's mandible
mask, last in a long costume list, was dropped; it now leads the costume. The leprechaun's
integument repeated its palette ("ruddy freckled ruddy freckled skin", the only creature
that did) and its gallery seed drew a woman with the folklore beard; the integument is now
plain "skin" and the gallery tile is pinned Male (`_GALLERY_GENDER`). The node itself still
gives a female leprechaun the beard: creature slots have no gender gate.

**A `gilded palace throne room` location.** Rococo Courtier and Ottoman Court were using a
grand hotel suite and a European castle courtyard as stand-ins. The value joins the
`civic_institutional` family (frozen family weight, so the family's share is unchanged; the
new value draws about 0.5% of random characters) and the formal-room rules: dressy outfit
styles, no athletic wear, no casual headwear, candlelight allowed. Medieval Monarch stays in
the cathedral, where coronations happen. Every seed that draws the civic family re-picks
within a longer list, so 94 gallery samples whose prompt moved were re-rendered, and the
marginals baseline was rewritten.

**Period looks lock tattoos and piercings.** Renaissance Noble, Victorian Lady, Victorian
Dandy, Gibson Girl, Regency Aristocrat, Greek Goddess, Egyptian Pharaoh, Roman Centurion,
Medieval Peasant, Musketeer and Highwayman now lock "no tattoos" and "no piercings beyond
ears", as the four new court looks do. Bracelets and rings are left free: pharaohs and
nobles wore them. Warrior and living-tradition looks (Gladiator, Viking Shieldmaiden,
Samurai, the cultural-dress archetypes) are unchanged.

**Maintainer render review of the re-rendered tiles.** Each fix names what the render
lacked, because the model only draws what the prose says:
- Darth Vader drew bare hands: the costume never named the suit, gloves or boots. They are
  named now, and `covers_body` drops the wearer's skin and build.
- Reverse-Flash had no mask (none was written); a yellow cowl with red ear bolts now mirrors
  The Flash entry, with `covers_face` and a `costume_back`.
- The Maxx and the Tusken Raider showed a human face inside the mask: the prose led with "a
  ... man with ... skin". Both take `covers_body` and a `subject` lead noun, and the Tusken
  mask says the head is fully wrapped with no skin showing ("a bandage-wrapped face" drew a
  face). "Unmask (show face)" still shows the face.
- Tatsumaki's "faint" aura, last in the list, did not render; the glow now leads. Her dress
  is canon (long sleeves, high collar, leg slits, not a sleeveless cocktail dress), and her
  age (28) and pale skin are pinned.
- The horseshoe crab drew a plain man ("drawn low over the face"), then a man wearing the
  shell as a hat ("a shell in place of a head"). A negated "no human head at all" was
  ignored on most seeds, so the head now leads positively ("a faceless horseshoe crab
  head"), like the other arthropods. Body parts with no place on a biped ("two smooth
  shields", "a plated abdomen", "the rear shield") rendered as a second whole crab held at
  the side; each is now anchored (carapace over back and chest, tail from the lower back,
  gills under the torso). Chitin arms and pincers for hands; the tile is rerolled once.
- Three creature tiles were rerolled without a data change (`--reroll`, recorded in the
  manifest): the biomechanical alien ("biomechanical" is a Giger style token and restyled
  a gilded palace around it), the ocean sunfish (drew a woman holding a fish) and the
  crystalline alien (a hoodie hid the translucent body).

## 2.3.0 - offline picker previews, Outfit Sheet, Age Progression, Aztec Noble, more back views

**Picker previews survive `--offline`.** ComfyUI's `--offline` adds a CSP that blocks the
browser from fetching github.io, so the picker's thumbnails silently showed nothing. Checked in
ComfyUI's `server.py`: the policy is a response header, so it binds the browser only. The pack's
server now fetches the manifest and images and serves them from ComfyUI's own origin, caching
them under the user directory. Measured before choosing the design: the published galleries
total a few hundred MiB (about 100 KiB an image), so the cache is lazy, never a full mirror;
GitHub Pages returns ETags and honours `If-None-Match`, and image filenames are stable across
re-renders, so revalidation is cheap. Verified on an isolated ComfyUI started with `--offline`:
a direct github.io fetch was blocked, the cached routes served the manifest and a JPEG, and
unlisted, traversal and unknown-kind paths returned 404. Design and safety rules:
architecture.md -> "Superseded in 2.3.0: previews go through a server-side cache".

**Outfit Sheet and Age Progression.** Both replay a resolved `prompt_json` like the Turnaround,
but they change fields other fields depend on. The first Outfit Sheet draft overrode only the
Clothing group and skipped nearly every style: makeup, jewellery and hair accessories are
style-gated, so a casual look's ponytail or a formal look's earrings refused the next style.
Overriding is the wrong tool; the nodes now ask `lock_clash` what each pin refuses and release
those fields for a redraw (architecture.md -> "Sheets that change the person"). Three more
conflict sources turned up in seed sweeps and are covered the same way: a locked season under
a studio backdrop, a close-up framing against a locked composition or pose, and pinned grey hair
against locked highlights. A 20-year-old also briefly gained laugh lines, because the natural
hair colour was drawn from a replay that kept the old skin detail; both paths now share one
helper. Final sweep: every studio-backdrop sheet and every age sheet kept all its views with no
engine conflicts; keep-scene sheets usually keep 3 to 4 of 6 styles, by design. The first
example render looked grey in four of six outfits: each style replayed with one fixed seed, so
every character drew the same few outfits per style (40 characters, four casual looks). The
seed now hashes the character, and an `outfit_seed` input re-dresses the same person; measured
after, 36 to 40 distinct outfits per style over 40 characters and a grey share matching plain
random characters.

**Period archetypes.** Edo, Victorian and Regency were proposed and dropped: Samurai, Geisha,
Victorian Lady, Victorian Dandy and Regency Aristocrat already ship. Silk Road was declined as a
blend of Mongolian Deel, Ottoman Court and Hanfu. Aztec Noble is new (Codex Mendoza and
Florentine Codex dress: huipil and cueitl, or tilmatli and maxtlatl with a quetzal headdress).

**Gallery samples.** The first Aztec Noble tile, rendered at the gallery's default
`Essentials` lock level, drew a random ethnicity; the look needs `Full preset`, now a per-entry
gallery pin (`_GALLERY_LOCK_LEVEL` in `scripts/render_gallery.py`). The Ancient Roman Patrician
sample is pinned Male (the toga is the expected look; the node still offers both). Example
workflows for the two new nodes ship in `example_workflows/`, built in the real frontend on an
isolated instance and reloaded to confirm what they execute. `--publish-pending` ignored
`--dry-run` and pushed; it now only lists what it would publish.

**More `costume_back` entries,** starting with caped and back-emblem heroes (Survey Corps
wings, Gotei 13 captains' haori, capes for Thor, Doctor Strange, Shazam, Supergirl, Robin,
Saitama and Vision, plus suit backs for Captain Marvel and Green Lantern). Each is checked by
rendering the Turnaround's back view text, never by parsing the front costume. Test renders of
six back views (Thor, Doctor Strange, Saitama, Levi, Byakuya, Superman) showed the cape or back
emblem and no chest emblem; Byakuya's kanji is not the right glyph (a model text limit).

Random characters are unchanged: no field pool, weight or draw order moved (verified by hashing
the prose of several hundred seeds before and after, and the Turnaround and Expression Sheet
output over the shared-helper refactor). The Archetype node's `Random` pick moves on some seeds,
as with every archetype addition, because it chooses from a longer list.

## 2.4.0 - archetype scene coherence (in progress)

**Figure Skater was set off the ice.** It locked "roller skating rink" or "dance studio with
mirrors", so a skater in blades stood among mirrors and barres, sometimes on a wood floor. It
now locks "indoor ice rink". Its pose was never locked, so the random pool drew "walking
mid-stride" on blades; it now locks four standing poses. Hockey Goalie and Roller Derby (also
on blades or wheels) got the same treatment. A pose lock is Setting & Shot, so it holds in
Essentials as well as Full preset. Both rinks already ban floor poses (kneel, crouch, sit), so
"crouching low" could never draw there and is not in the lists.

**The goalie rendered in black and white.** Its pads drew from `{color}` and its jersey named
no colour; a charcoal draw on white ice under cool LED light left nothing colourful in the
prompt, and the model went monochrome. Pads and jersey now share one `{team_color}` draw.

**More pose locks.** Carhop skates the order out, so motion stays, but the drive-in lot does
not ban floor poses: it now locks two posed and two mid-step poses. Scuba Diver wears fins, so
standing poses only. Samurai drew lounging, wall-leaning and hair-touching poses in armour and
a horned helm; it now locks warrior stances and seiza, and moved from a photo studio (with
three-point lighting) to the Mount Fuji foothills in overcast daylight.

**Found, not fixed (candidates):** no rule keeps "leaning against a wall" or "perched on the
edge of a seat" out of open landscapes (meadow, dunes, beach, foothills), which affects random
characters too and would need a marginals re-baseline. Emo, Indie Sleaze and 1980s New Wave
lock eyeliner, but a man's "no makeup" default wins and drops it. Many archetypes lock a
location their own `outfit_style` gate refuses; the engine keeps both and only logs it, so the
prose is unaffected.

**Locations written before a better one existed.** Audited every archetype's locked location
against the current pool. Moved where a matching place now exists and the engine reports no new
conflict: Swashbuckling Pirate (cocktail lounge to a harbour, lighting candlelight to golden
hour), Gladiator (museum gallery to the Colosseum exterior, lighting to midday sun), Chef
(home kitchen to commercial kitchen), Veterinarian (doctor's room to a veterinary exam room),
Boxer (weight room to a boxing gym), Glassblower and Dwarven Blacksmith (factory floor to their
own studio and forge), Florist, Potter, Tailor, Martial Artist and Kendo Practitioner (to a
flower shop, ceramics studio, tailor's workroom and dojo). Egyptian Pharaoh stays in the museum
hall: the Giza plateau adds clashes with its locked spotlight and evening-formal style.

Each change touches only that archetype's draws; random characters are unchanged.
