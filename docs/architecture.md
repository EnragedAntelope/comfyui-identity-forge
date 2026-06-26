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
js/          identity_forge.js · identity_forge_creature.js  (ComfyUI frontend extensions)
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

- **IdentityForge** ([nodes/identity_forge.py](../nodes/identity_forge.py)) — the engine. 70+
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
- **Weighted hair-style pick.** `hair_style` is the one field that does **not** use a flat
  `rng.choice`: `_pick_hair_style` first draws a family from `HAIR_STYLE_FAMILIES` (weighted by
  `weight`, frozen to each family's original variant count, sum = 30), then a variant uniformly
  within it. So adding a variant subdivides its family's share instead of inflating it (3
  ponytails still total the same ~6.7% the 2 originals did). The flat option list still drives
  the widget (every variant lockable); `validate_data` checks the families partition it exactly.
  New variants must also be slotted into the relevant `data/constraints.py` length lists
  (`_LONG_HAIR_STYLES`, the pixie exclusion) so they're culled on short hair like their siblings.

## cosplayers.py — characters as a worn look

`COSPLAYERS: dict[name -> entry]`. Required: `franchise`, `gender` (`Female`/`Male` — SOURCE
gender, used only to scope the `Random — female/male` picks; the *person's* gender is the
IdentityForge widget, so crossplay works), `costume`. Optional: `signature` / `physique`
`{field: value}` maps (values **must** be valid `FIELD_DEFINITIONS` options — `validate_data`
enforces), `covers_face` + `mask`, `prop`, and `eyes` (free-text eye-colour override).

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
- **Non-human skin / body paint:** word as `"an even, smooth coat of <colour> body paint"`
  (textured: `"an even, all-over coat of …"` + keep the texture word); leave `skin_tone` out so
  the person underneath randomizes. The builder **auto-detects this `an even … coat of …` marker**
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
- **Bald characters:** state it in `costume` ("a bald head", "a clean-shaven bald scalp"). The
  builder **auto-detects `\bbald\b`** (won't catch "baldric") and locks the scalp-hair fields
  (`hair_color/length/texture/style/part/volume/highlights/accessory`) absent, so a random
  "His hair is …" line can't contradict the bald head (the Doctor Manhattan / Voldemort bug).
  Auto-detected bald is **scalp-only** (a bald man may keep a beard). For a *fully* hairless
  head (creatures/aliens — Kilowog, King Shark, Despero) set the explicit `bald: True` key,
  which also clears `facial_hair`. `setdefault` semantics: a deliberate signature lock (topknot,
  stray hairs, a beard) still wins. See `_BALD_RE` / `_BALD_SUPPRESS`.
- **Clean-shaven faces:** `"clean-shaven"`/`"clean shaven"` in `costume` **auto-locks**
  `facial_hair` absent so a random beard can't sprout on a bare face. See `_CLEAN_SHAVEN_RE`.
- **Gloved hands:** a costume that covers the hands (`glove`/`gauntlet`/`mitten`) makes the
  engine force the finger fields (`nails`, `rings`, and ring-typed `other_jewelry`) absent —
  otherwise a randomized polish/ring renders *on top of* the glove. This lives in the **engine**
  (`generate_character`, `_GLOVE_RE`), not the cosplayer builder, so it also covers archetype
  costumes and random outfits. `"fingerless"` anywhere in the text opts out (fingers exposed →
  nails/rings stay). A user-locked `nails`/`rings` is respected. **Power rings worn over the
  glove** (Green Lantern, Sinestro) belong in the `costume` prose ("a glowing green power ring
  worn on the finger"), not the `rings` field, so they survive the suppression — keep writing
  them that way. (For an all-metal robot like the Cylon Centurion, give it `gauntlets` so the
  finger details drop.)
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
  stays believable (no fantasy colours added there). The cosplayer also locks `eye_shape` **and
  `eye_size`** to `None` (injected after `group_fields`, which strips them on the build side) so
  no random shape/size word contradicts the free-text description — the engine keeps the locked
  `None` as absent and drops it from prose/JSON.
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
- **`palette_pool`** (optional list): for amorphous/colour-variable creatures (blob, slime,
  energy being, jellyfish, crystalline alien). When the node palette is `Auto` it draws a
  seed-varied hue from the pool instead of the single `palette` (so they aren't one fixed
  colour). The palette combo also offers `Random` (rolls `_PALETTES` for any creature). The
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

- Duplicate `COSPLAYERS` / `CREATURES` keys silently override — the last wins.
- `signature`/`physique` values are gender-gated downstream; prefer unisex fields for crossplay.
- A locked physique doesn't constrain `fitness`/`muscle` (known loose coherence).
- Adding RNG draws in the creature node mid-sequence shifts seed→creature mapping — append draws
  at the end.
- The roster is large (~840 cosplayers, ~130 creatures): always grep the current keys before
  adding to avoid silent overrides.
- Gloved/gauntleted costumes suppress randomized `nails`/`rings` in the engine (`_GLOVE_RE`),
  but **not** other Body-group jewellery (necklace/bracelet/watch) — an all-armour cosplayer
  (RoboCop, Iron Man, Cylon) may still report a stray necklace; that is pre-existing.
- Adding options to a **flat** field shifts its distribution; prefer the density-gated
  `_EXTRA_ABSENCE` fields (variety changes, frequency doesn't). New feminine-coded values on a
  shared-pool field must also be added to `_MALE_EXCLUDED_VALUES` so a random Male skips them.
