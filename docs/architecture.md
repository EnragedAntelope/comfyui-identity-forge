# Identity Forge — architecture & contributor reference

A map of how the pack fits together, the data schemas, and the conventions that keep
changes safe. Aimed at anyone (human or agent) extending the data or the engine.

## Repo layout

```
data/        cosplayers.py · creatures.py · fields.py · templates.py (archetypes/outfits)
             · constraints.py · user_options.py (runtime JSON merge)
nodes/       identity_forge.py (engine + main node) · identity_forge_cosplayer.py
             · identity_forge_creature.py · identity_forge_archetype.py
             · identity_forge_modifier.py · identity_forge_vault_{save,load}.py
js/          identity_forge.js · identity_forge_creature.js · identity_forge_vault.js
             (ComfyUI frontend extensions)
tests/       validate_data.py (static integrity) · test_engine.py · test_creature.py
             · test_vault.py · preview_cosplayer.py
docs/        usage.md · cosplayer-notes.md · creature-notes.md · architecture.md (this file)
```

Pack is **V3 API** (`comfy_api.latest`), category `conditioning/character`, **zero deps**,
fully offline. The engine half of every node is a pure function importable without ComfyUI
(that's how the tests run headless).

## Nodes & data flow

The four preset nodes each emit a grouped-JSON **`character_json`** string and chain through
an optional **`upstream`** input. They wire into IdentityForge's single **`archetype_json`**
socket. On overlap, the node **closest to IdentityForge wins** (downstream wins); a node set to
`None` emits `{}` and passes its upstream through. `merge_preset_documents` (deep-merge, incl.
`_meta`) is the chaining primitive.

```
Archetype ─▶ Cosplayer ─▶ Creature ─▶ Modifier ─▶ IdentityForge ─▶ prompt_text + prompt_json
```

- **IdentityForge** ([nodes/identity_forge.py](../nodes/identity_forge.py)) — the engine. Many
  lockable dropdowns + control toggles → randomize → constraints → prose + JSON. Entry point
  `generate_character(...)`; widget schema in `define_schema`.
- **Cosplayer** → `build_cosplayer_json`: a character's `costume` becomes the hidden
  `outfit_description` lock; `signature` (hair/eyes) always applied; `physique` only in *Full
  character* mode; `covers_face`/`mask`/`prop` handled here.
- **Creature** → `build_creature_json`: emits a `Species & Anatomy` group + `_meta`
  (`form`, `suppress_groups`, `suppress_fields`).
- **Modifier** → prepends a descriptor to one field or a whole group.
- **Vault Save/Load** → persist a generated `prompt_json` under `ComfyUI/user/identity_forge/`.

## fields.py — the field engine

`FIELD_DEFINITIONS` is an `OrderedDict[name -> {group, female_options, male_options, optional,
…}]`. Notes:

- **Control fields** carry `"control": True` (`gender`, `hair_color_scope`, `location_setting`):
  read from their toggle, never randomized, never described. `_CONTROL_FIELDS` collects them.
- **Hidden fields** (`outfit_description`, `held_item`): free-form prose locks, no widget;
  `_HIDDEN_FIELDS` / `_PRESET_HIDDEN_FIELDS`.
- **Gender-divergent fields** are the only ones whose female/male pools differ: **`bust`,
  `facial_hair`, `makeup_style`, `hair_accessory`** (`hair_accessory` gives random women the
  full feminine range but random men only a small unisex set, so a bow never lands on a random
  male). These (and only these) are mirrored in the JS `GENDER_POOLS` for live gender-swap —
  **edit both Python and JS when you touch them**.
- **Absence model (important).** `_is_absent(v)` treats `""`, `"None"`, `"Random"`, `"none"`,
  any `"no …"`, and `_ABSENCE_EXACT` (`bare nails`, `clean shaven`, `natural bare`,
  `bare natural lips`) as "omit from prose". `_EXTRA_ABSENCE` maps accessory fields to their
  canonical absent token + a base probability — the `accessory_density` control injects it so
  portraits aren't over-accessorised. **Those absent tokens must stay in the pools** (the
  density logic needs them); they are merely *hidden from the widget*.
- **Widget building** (`define_schema`): each field combo = `["Random"] + <real options, with
  `_is_absent` values filtered out> + ["None"]`. Result: exactly one "omit" affordance
  (`None`). Picking `None` == any in-pool absent value == omit.
- **Weighted family pick (the bias-safe growth channel).** Fields registered in `FIELD_FAMILIES`
  do **not** use a flat `rng.choice`: `_pick_family_weighted(field, pool, rng)` first draws a family
  (weighted by `weight`, frozen to each family's *original* variant count), then a variant uniformly
  within it. So adding a variant subdivides its family's share instead of inflating it, and the
  field's top-level distribution never shifts — the safe way to enlarge a flat field without biasing
  randomization. Because each weight equals the family's original size, the pick reproduces a flat
  uniform draw until new variants are added. Registered fields: `hair_style` (`HAIR_STYLE_FAMILIES`),
  `hair_color` (shade neighbourhoods; its `vivid` family is exactly the set the "Natural only"
  scope filters, so the pick stays uniform under both scopes — keep new fashion shades in `vivid`),
  `expression`, `mood`, `pose`, `lighting`, `location` (each `<FIELD>_FAMILIES` in `data/fields.py`).
  The picker intersects each family's variants with `pool` and drops empty families, so upstream
  filtering still composes — e.g. the `location_setting` Indoor/Outdoor/Studio scope, or a hair-length
  constraint. The flat option list still drives the widget (every variant lockable); `validate_data`
  checks **every** `FIELD_FAMILIES` entry partitions its field's options exactly. New `hair_style`
  variants must also be slotted into the relevant `data/constraints.py` length lists
  (`_LONG_HAIR_STYLES`, the pixie exclusion) so they're culled on short hair like their siblings.
- **Per-value draw weights (`male_weights`).** A field definition may carry a
  `"male_weights": {value: int}` map to lean the *male* random draw (currently only
  `makeup_style` leans 2x toward `no makeup` so a random man is bare-faced more often).
  Missing values weigh 1; the engine uses one `rng.choices` call so the RNG stream shape
  matches a flat pick. Never duplicate a value inside an options list to weight it — the
  validator rejects duplicates and checks every weight key is a real option.

## cosplayers.py — characters as a worn look

`COSPLAYERS: dict[name -> entry]`. Required: `franchise`, `gender` (`Female`/`Male` — SOURCE
gender, used only to scope the `Random — female/male` picks; the *person's* gender is the
IdentityForge widget, so crossplay works), `costume`. Optional: `signature` / `physique`
`{field: value}` maps (values **must** be valid `FIELD_DEFINITIONS` options — `validate_data`
enforces), `covers_face` + `mask`, `covers_hair`, `body_paint`, `prop`, `eyes` (free-text
eye-colour override), and `skin` (free-text body-paint skin-colour anchor).

Conventions (keep the data coherent):

- **Worn, not held.** `costume` lists only worn items and reads after "She/He wears …"
  (lowercase, leading article). Held/wielded props go in the optional `prop` (emitted only when
  the node's prop toggle is on, voiced "holding …").
- **Full masks/helmets:** `covers_face: True` **and** the head covering in a separate `mask`
  string (kept out of `costume`) so the *Unmask* toggle can drop it. IdentityForge then
  suppresses Face/Hair/Makeup (+ earrings/piercings). Omit both when the face shows.
- **Bald / shaven-headed:** state it in `costume` (e.g. "…, and a clean-shaven bald head") — the
  builder auto-detects it and locks the scalp-hair (and, for "clean-shaven", facial-hair) fields
  absent (see the Bald / Clean-shaven notes below). Do **not** lock a `hair_length`/`hair_style`
  (locking `buzzed very short` renders a buzz cut — the Mace Windu bug).
- **Non-human skin colour is skin-native (0.52+):** word as `"smooth, flawless <colour> skin"`
  (textured: `"uniform, all-over <colour> <material>"` — scaled/craggy/pebbled keep their texture
  word); leave `skin_tone` out so the person underneath randomizes. Live A/B testing showed
  "body paint" / "dye" wording makes t2i models render a streaky coat OVER a human tone, while
  skin-native wording renders one uniform colour — the paint word was swept out in 0.52. Fur /
  feather / flame / ice / plating entries keep the legacy `"an even … coat of …"` wording (still
  recognised). The builder **auto-detects all three markers**
  (face-visible entries only) and force-locks `skin_tone`, `complexion`, `skin_details`,
  `freckles_density`, `makeup_style` (→ `no makeup`, which cascades every cosmetic sub-field
  absent), and the skin-toned makeup (`blush`, `skin_finish`, `contour`, `highlight`)
  absent — otherwise a random human skin tone/complexion *or* a randomized `makeup_style`
  ("soft glam" with no foundation colour) renders the *face* pale under the paint (the
  She-Hulk green-body/pale-face bug). An explicit `body_paint: True/False` entry key
  overrides the auto-detection. This suppression **also runs when the face is masked**
  (`covers_face`): `covers_face` hides the Face/Hair/Makeup groups but **not** the Body-group
  `skin_tone`, so an all-over coat (Human Torch flame) would otherwise still report a stray
  skin tone under it. See `_BODY_PAINT_RE` / `_BODY_PAINT_SUPPRESS` in
  `nodes/identity_forge_cosplayer.py`.
- **Skin-colour anchor (re-plant the colour).** Suppressing `skin_tone` leaves the *opening*
  prose with no skin colour ("…with a slim build and tall."), so t2i routinely defaults the
  high-attention **face** to a human tone (the Poison Ivy white-face / TMNT pale-face bug). After
  suppression the builder **re-injects the paint colour into `skin_tone`** so the lead sentence
  anchors it ("…tall, **and vivid green skin**"). The colour is auto-derived from the canonical
  clause — `"smooth, flawless <colour> skin"`, `"uniform, all-over <colour> <material>"`, or the
  legacy `"coat of <colour> <material>"` (`_BODY_PAINT_COLOR_RE` → `_body_paint_skin_color`); an
  explicit free-text **`skin` entry key** wins for phrasings the regex misses (`ice`, `chitin`,
  `tattoos`, marker-free prose) or where a cleaner word reads better — it mirrors the `eyes`
  override and is voiced verbatim. The anchor is a *wired value*, so it survives both look-levels
  and "set all to none". The demographics formatter (`_format_…`) guards the trailing `" skin"`
  when the value already ends in a skin/fur/scale/hide word ("dark blue scaled-skin"). For a
  genuinely non-human **face** prefer Pattern A (`covers_face` + `mask`) over relying on the anchor
  alone (TMNT turtles, King Shark, Abe Sapien, Jar Jar Binks, Despero); humanoid coloured
  characters (She-Hulk, Mystique, Gamora) stay face-visible and lean on the anchor.
- **Face-colour reinforcement (engine, the green-body/white-face fix).** The opening anchor colours
  the *body* only; the face is otherwise described by colourless feature tokens ("…oval face…, green
  eyes, red lips"), so t2i kept defaulting the high-attention **face** to a human tone even with the
  anchor in place. `_format_prose` therefore **restates the colour on the face** ("…**Her face has the
  same vivid green skin**") when the resolved `skin_tone` is a non-human colour (not in
  `_STANDARD_SKIN_TONES`, i.e. a body-paint anchor or free-text `skin` override) **and** the face is
  actually described (`face_struct`/`features` non-empty). It reuses the same material-noun guard so
  "scaled-skin" isn't doubled. This fires for face-visible coloured characters only: a masked
  (`covers_face`) or creature-replaced face has its Face-group fields dropped before render, so the
  reinforcement is skipped (the head is the mask/creature); standard human tones are never restated
  (prose-only, zero RNG draws — no output churn, no randomization bias).
- **Hand-colour reinforcement (engine, the white-hands fix).** The same restatement for the
  **hands**: `_format_prose` adds "...**Her hands have the same vivid green skin**" when `skin_tone`
  is non-standard, so bare hands (and any nail polish) do not render in a default human tone (the
  green-body / **white-hands** bug -- She-Hulk, Gamora). Gated on the hands actually showing:
  `generate_character` passes `hands_visible`, false when gloves (`_GLOVE_RE`, unless
  `_FINGERLESS_RE`) or a full shell (`covers_body` / `_FULL_COVER_RE`) hide them -- exactly where
  the finger fields are already dropped -- so it never colours skin or paints nails under a
  covering. Same material-noun guard as the face; prose-only, zero RNG (no bias).
- **Bald characters:** state it in `costume` ("a bald head", "a clean-shaven bald scalp"). The
  builder **auto-detects `\bbald\b`** (won't catch "baldric") and locks the scalp-hair fields
  (`hair_color/length/texture/style/part/highlights/accessory`) absent, so a random
  "His hair is …" line can't contradict the bald head (the Doctor Manhattan / Voldemort bug).
  Auto-detected bald is **scalp-only** (a bald man may keep a beard). For a *fully* hairless
  head (creatures/aliens — Kilowog, King Shark, Despero) set the explicit `bald: True` key,
  which also clears `facial_hair`. `setdefault` semantics: a deliberate signature lock (topknot,
  stray hairs, a beard) still wins. See `_BALD_RE` / `_BALD_SUPPRESS`.
- **Clean-shaven faces:** `"clean-shaven"`/`"clean shaven"` in `costume` **auto-locks**
  `facial_hair` absent so a random beard can't sprout on a bare face. See `_CLEAN_SHAVEN_RE`.
- **Gloved hands:** a costume that covers the hands (`glove`/`gauntlet`/`mitten`) makes the
  engine force the finger fields (`nails`, `rings`) absent — otherwise a randomized polish/ring
  renders *on top of* the glove. (`other_jewelry` now holds only body pieces — anklet, arm cuff,
  body chain — that never sit on the fingers, so it is untouched here.) This lives in the **engine**
  (`generate_character`, `_GLOVE_RE`), not the cosplayer builder, so it also covers archetype
  costumes and random outfits. `"fingerless"` anywhere in the text opts out (fingers exposed →
  nails/rings stay). A user-locked `nails`/`rings` is respected. **Power rings worn over the
  glove** (Green Lantern, Sinestro) belong in the `costume` prose ("a glowing green power ring
  worn on the finger"), not the `rings` field, so they survive the suppression — keep writing
  them that way. (For an all-metal robot like the Cylon Centurion, give it `gauntlets` so the
  finger details drop.)
- **Full hard shell (`covers_body`):** a robot / droid / powered-armour / full-plate /
  exoskeleton body has no bare skin for worn jewellery, so the engine drops the whole
  **Jewelry & Nails** group, plus the Clothing-group `accessories` and `bag` fields
  (`_CONCEALED_BODY_FIELDS`) — sunglasses / belts / a carried bag would render on top of a
  mascot suit or armour shell (the sunglasses-on-Michelin-Man bug, 0.51+). It auto-detects from the costume prose (`_FULL_COVER_RE` —
  `robot`, `droid`, `exoskeleton`, `plate armor`, `armored bodysuit`, …) and also honours an
  explicit `covers_body: True` entry key for cases the prose doesn't spell out (Nebula,
  Man-At-Arms). Independent of `covers_face` (a face mask doesn't imply a covered body, and a
  covered body may still show the face). Body/demographics stay (the silhouette has a build).
  **Fully encased** (`covers_face` **and** a full shell): the body's `skin_tone` is dropped too —
  the only Body-group skin field `covers_face` doesn't already hide — so a masked droid/armour
  (Iron Man, 2-1B) reports no stray human skin tone under the plating.
- **Hood / cowl / lekku (`covers_hair`):** a head covering that fully encloses the scalp while the
  **face still shows** (a snug cowl, a jester hood, a Twi'lek's lekku) has no visible hair, so a
  randomized "Her hair is …" line only fights the look. The `covers_hair: True` entry key drops the
  whole **Hair** group (engine `_CONCEALED_HAIR_GROUPS`) but keeps Face + Makeup — narrower than
  `covers_face`. Apply it only when the covering truly encloses the scalp and **no signature hair
  is locked** (an iconic fringe under the hood = leave it off): Harley (Classic Jester), Blue Beetle
  (Ted Kord), Bib Fortuna. Independent of `covers_face` (which already drops Hair on its own).
- **Elemental / energy beings whose head is also covered** (Human Torch flame, Ghost Rider
  skull): use the `covers_face` + `mask` mechanism (head described in `mask`) so no random
  hair/face contradicts the effect, and keep the `an even … coat of …` body-paint phrasing in
  `costume` so the Body-group `skin_tone` is suppressed too (see body-paint note above).
- **Extreme-size characters** (Giganta, Titania, Giant-Man): put the scale in `costume` prose
  ("towering 50-foot stature, …") — there is no size field for humans.
- **Plain ASCII only** in names and text (no em/en dashes, smart quotes, accents — e.g. use
  `Padme`, `Eowyn`). Tokenizers mangle the rest. Names are dict keys: a duplicate **silently
  overrides** — grep before adding.
- **Iconic non-standard eyes** (red/violet/gold cat-slit) use the free-text `eyes` override
  (a top-level entry key, not the signature) — it replaces `eye_color` and is voiced verbatim,
  passing the gender gate because `eye_color`'s pools are identical. The main node's dropdown
  stays believable (no fantasy colours added there). The cosplayer also locks `eye_shape` to
  `None` (injected after `group_fields`, which strips it on the build side) so no random shape
  word contradicts the free-text description — the engine keeps the locked `None` as absent and
  drops it from prose/JSON. (`eye_shape` is the single eye-structure field; it also encodes
  size/lid, so the former separate `eye_size`/`eyelid_type` fields were merged out.)
- **Random scope.** `_FRANCHISE_CATEGORY` maps every franchise to one of nine broad categories
  (Anime & Manga, Marvel, DC, Star Wars, Disney, Video Games, Fantasy & Literature, Movies & TV,
  Comics & Cartoons). The Cosplayer node's `random_scope` control narrows the `Random — …` picks
  by category (combines with the gender scope); `get_cosplayer_names(gender, category)` does the
  filtering. Unmapped franchises fall back to a default.

## creatures.py — non-human form layer

`CREATURES: dict[name -> {class, palette, <slots>}]`. Slots: `head`, `eyes`, `integument`
(required) + optional `arms`, `hands`, `legs_feet`, `wings`, `tail`, `extras`. Slot text is
free-form prose (own render path — not validated against human fields). Rules:

- **Integument is colour-free**; the hue lives in `palette` and is prepended at render
  (`_prepend_descriptor` fixes a/an). Texture words stay in `integument`.
- **`palette_pool`** (optional list): for colour-variable species — most of the roster
  since 0.38 (dragons, wolves, parrots, chameleons, demons, blobs…). When the node palette
  is `Auto` it draws a seed-varied hue from the pool instead of the single `palette` (so
  they aren't one fixed colour). Conventions: the entry's `palette` leads the pool (iconic
  colour stays reachable); pattern words may ride in entries ("black-and-orange banded");
  skip species whose colour IS the identity (raven, panda, orca, skeleton…). The palette
  combo also offers `Random` (rolls `_PALETTES` for any creature). The
  palette RNG draw happens **last** in `build_creature_json`, after creature/slot/form picks,
  so existing seeds keep their creature and only colour shifts; the `Auto`+no-pool path draws no
  RNG and is byte-identical to before.
- **Suppression:** a creature `head` hides human Face/Hair/Makeup; `integument` hides skin
  fields; `form` (Anthropomorphic/Feral/Subtle) sets group-level suppression. Generalizes the
  cosplayer `covers_face` mechanism via `_meta.suppress_groups` / `suppress_fields`.

## Extending at runtime — user_options.json

`data/user_options.py` merges an optional pack-root `user_options.json` at import (sections:
`fields`, `outfits`, `archetypes`, `cosplayers`, `creatures`). Fails closed on a bad file. User
entries override built-ins of the same name. `palette_pool` is a built-in-only key (the user
creature loader copies only the standard slots).

User additions are first-class (0.46.1):

- The loader records what it added (`USER_ADDED_FIELD_VALUES` / `USER_ADDED_OUTFIT_STYLES`);
  `validate_data` subtracts those from its strict shipped-data checks (family partitions,
  expected outfit-style set, bucket/variety floors), so a valid user file never fails validation
  while shipped-data drift is still caught.
- User values on a **family-weighted field** (hair_style, hair_color, expression, mood, pose,
  lighting, location) sit outside every family; `_pick_family_weighted` draws them via an
  implicit leftover family weighted by its size, so they are reachable at the flat per-value
  share (previously they appeared in the widget but could never randomize).
- The cosplayer loader follows the built-in schema: optional `mask` / `prop` / `eyes` / `skin`
  keys are **omitted** when unused, never stored as `""`; the advanced bool flags
  (`covers_body`, `covers_hair`, `bald`, `body_paint`) are copied only when explicitly `true`
  (0.47.0), mirroring built-ins which never carry a `False` flag.
- A custom value used inside a user archetype should also be listed under `fields` so it is a
  real option (the shipped example demonstrates this with Sky Pirate).

## Validation, tests, versioning

- `python tests/validate_data.py` — value integrity: every signature/physique/constraint/
  archetype value must be a real field option; mask rules; creature structure (allowed keys:
  `class`, `palette`, `palette_pool`, slots; non-empty strings, `palette_pool` a non-empty list
  of strings); studio-backdrop/skin-tone/ethnicity affinity maps.
- `python -m unittest discover -s tests -v` — engine + creature + vault (headless).
- **Version:** bump `pyproject.toml` on every functional commit — **minor** for feature/content,
  **patch** for fixes (standing order).
- **JS regen:** `js/identity_forge.js` embeds `GROUP_ORDER` / `FIELD_TO_GROUP` / `GENDER_POOLS`
  from `data/fields.py`; update it when the field set or the gender-divergent pools change.

## Gotchas cheat-sheet

- **`gender == "Any"` resolves to a concrete `Female`/`Male` per seed** (first rng draw in
  `generate_character`) so the person is coherent — the gender gate and randomizer then draw from
  one pool, no beard beside a feminine bust. An anatomical lock decides it (`_gender_from_locks`:
  a beard -> Male, a feminine-only `bust` -> Female) so explicit choices are honored; otherwise an
  even 50/50. The old unioned androgynous mode (both pools mixed, *they/them* pronouns,
  `_meta.gender` stays `"Any"`) is preserved **only** when `wardrobe == "Any"`, the explicit
  "anything goes" escape hatch.
- **Archetype list values (0.37+).** Any archetype (or variant) field value may be a `list[str]`
  of curated alternatives — `build_archetype_json` seed-picks one uniformly (no bias by
  construction), so one archetype yields a range of looks. An `outfit_description` list picks an
  alternative costume template before its slots fill. Draw order is append-only for seed
  stability: archetype pick → base costume template pick + slot fills → variant costume picks +
  fills → ONE scalar list pass (base fields in template order, then Female/Male variants) before
  the Essentials filter, so lock level never shifts draws. `gender` may never be a list; every
  element must be a real field option; the validator enforces len ≥ 2, no dups. The 0.39 sweep
  widened 150 hair/eye locks to shade-family lists (the original shade leads each list);
  hair_style/location/lighting locks deliberately stay fixed (look/scene-defining).
- **Bald heads (0.50+).** `hair_length` has a male-only `"bald"` option (comb-over precedent).
  When it resolves — locked or randomly drawn — the engine drops the *randomized* scalp-hair
  fields (colour/texture/style/part/highlights/accessory; locked ones survive, locked-wins) and
  prose voices "his head is bald"; `facial_hair` is untouched. `_build_option_pool` never draws
  `bald` under an already-locked `hair_style`. Mirrors the Cosplayer `_BALD_SUPPRESS` mechanism.
- **Contrapositive constraint repair (0.50+).** When an exclusion rule's *target* is locked to an
  excluded value (a locked "sleek bun" against a randomly drawn "buzzed very short" length), the
  engine re-rolls the randomized *trigger* away from every conflicting trigger value instead of
  warning and leaving the incoherent pair. Both-locked contradictions and control-field triggers
  (gender, scope) still warn-and-keep.
- **Mood and expression vocabularies are disjoint** (0.36+, test-enforced): they randomize
  independently, so a shared word ("playful") could double in one output. When adding options to
  either field, pick words the other doesn't use (mood is the scene's tone, expression the face).
- **Per-gender archetype variants** — an archetype may carry a `variants: {"Female": {...},
  "Male": {...}}` block so *one* selection yields two coherent looks (a 1980s Aerobics leotard vs
  the male tank/shorts). The base dict holds only shared fields + a soft `gender` lean (e.g.
  `"Female"`, applied when the widget is `"Any"`, overridable by the widget). `build_archetype_json`
  fills each variant's costume slots and Essentials-filters it, emitting `_meta.variants`;
  `generate_character` folds `variants[resolved_gender]` into the locks **after** the coin-flip and
  before the gender gate, so the variant's look wins. Author the divergent fields (outfit, hair,
  body, makeup) in the variants and keep `gender` on the base — never inside a variant.
  `merge_preset_documents` carries `_meta.variants` through chaining (downstream wins).
- **`smile_type` is the mouth/smile field and IS rendered** (in `_format_prose` face features);
  `constraints.py` buckets every `expression` into closed / soft-smile / open so the mouth never
  contradicts the face. (It was dead — resolved but unrendered — before 0.33.)
- Duplicate `COSPLAYERS` / `CREATURES` / `ARCHETYPES` keys silently override — the last
  wins. `validate_data` now AST-scans the roster literals and fails on a duplicate key,
  and rejects duplicated values inside any field option pool (a hidden 2x draw weight).
- `signature`/`physique` values are gender-gated downstream; prefer unisex fields for crossplay.
- Physique↔fitness coherence is soft (0.46+): exclusion rules cull only the outright
  contradictions (soft-curved/plus-size builds never roll `muscular`; athletic/toned/fit
  builds never roll `sedentary`). Mid-range pairings randomize freely; locks on both
  fields still win.
- **A downstream Full-preset Archetype overrides a chained Cosplayer's costume/skin.** Presets
  merge with the *downstream* node winning field-by-field (`merge_preset_documents`), so
  `Cosplayer -> Archetype (Full preset) -> IdentityForge` lets the archetype's `outfit_description`
  (and any Body `skin_tone`) replace the cosplayer's -- e.g. She-Hulk chained into a "Tennis Player"
  Full preset comes out in tennis whites with a human tone, losing the green. To **layer** a tilt
  onto a cosplay instead of overwriting it, set the archetype (or cosplayer) to **Essentials** so it
  emits only the look groups and leaves the rest to flow through.
- **Seeded nodes re-roll every queue via `fingerprint_inputs`.** The four randomizers
  (`IdentityForge`, `Archetype`, `Cosplayer`, `Creature`) return `float("nan")` from
  `fingerprint_inputs`, forcing ComfyUI to re-execute them -- otherwise an auto-advanced seed can be
  served from cache and the output "sticks" (ComfyUI#11905). Pure cache control (no RNG): a *fixed*
  seed still reproduces exactly, and identical output keeps expensive downstream nodes cached.
- Adding RNG draws in the creature node mid-sequence shifts seed→creature mapping — append draws
  at the end.
- The roster is large (~895 cosplayers, ~169 creatures): always grep the current keys before
  adding to avoid silent overrides (the validator's duplicate-key scan backstops this).
- An outfit whose prose already includes headwear (hat/helmet/hood/crown…, `_HAT_RE`)
  suppresses a hat-valued random `accessories` draw so two hats never stack; non-hat
  accessories still show and an explicit lock wins. Keep `_HAT_ACCESSORY_VALUES` in sync
  with the hat entries of the `accessories` pool.
- Gloved/gauntleted costumes suppress randomized `nails`/`rings` in the engine (`_GLOVE_RE`);
  a **full hard shell** (robot/droid/powered-armour/full-plate/exoskeleton, detected by
  `_FULL_COVER_RE` or the cosplayer `covers_body` flag) drops the whole **Jewelry & Nails**
  group plus the `accessories`/`bag` fields (`_CONCEALED_BODY_FIELDS`, 0.51+) so an all-armour
  or full-suit cosplayer (RoboCop, Iron Man, Michelin Man) reports no stray necklace,
  sunglasses, or carried bag. Both respect explicit user locks. The shell rule also fires on full-plate **archetypes** (Human
  Knight, Holy Paladin).
- Adding options to a **flat** field shifts its distribution; prefer the density-gated
  `_EXTRA_ABSENCE` fields (variety changes, frequency doesn't). New feminine-coded values on a
  shared-pool field must also be added to `_MALE_EXCLUDED_VALUES` so a random Male skips them.
- **Masculine-default trims are wardrobe-gated for jewellery/nails.** `_MALE_EXCLUDED_VALUES`
  drives the "no chandeliers/pearls/polish on a random man" behaviour, but the jewellery/nails
  fields (`_PRESENTATION_GATED_FIELDS`) tag their rules `presentation_gated=True`. `_apply_constraints`
  skips those unless the man reads `"Masculine"` (i.e. `wardrobe == "Match gender"`), so a
  **Feminine/"Any" wardrobe leaves the full feminine-coded pool available** to a man for a femme look;
  the structural defaults (hair, brows, lips, eye_shape, bust) always apply. Presentation is
  `_presentation_mode(gender, wardrobe)`, shared with the outfit picker. Locked/archetype values
  bypass the trim entirely (constraint warns and keeps them).
- **Wired `"None"` is an explicit omit and survives to the engine.** `IdentityForge.execute`
  builds `archetype_locked` from every wired value *except* `"Random"` — so a cosplayer/archetype
  field set to `"None"` (the builder's body-paint, bald, and free-text-eye suppressions) reaches
  the engine as an omit instead of being silently re-randomized by the default `"Random"` widget.
  A deliberate concrete widget choice still overrides it. (Pre-0.27.0 the `"None"` was dropped, so
  She-Hulk rendered a human skin tone under her green and bald characters grew hair — the
  documented suppressions only worked when calling `generate_character` directly, not through the
  node.) Tests that exercise suppression must route through `resolve_locked_fields`, not pass the
  flat preset dict straight in (see `SuppressionLockSurvivalTests`).
