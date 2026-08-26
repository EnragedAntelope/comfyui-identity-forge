# Identity Forge — usage guide

The full reference for the main node's controls, locking, constraints, custom options, and
field set. For the overview, install, and node chaining, see the [README](../README.md). Per-node
design notes live in [cosplayer-notes.md](cosplayer-notes.md) and
[creature-notes.md](creature-notes.md); the system map is in [architecture.md](architecture.md).

## Controls

The widgets at the top of Identity Forge steer the whole character:

| Control | Default | Effect |
| --- | --- | --- |
| `seed` | randomize | Reproducibility. Auto-randomizes each run; set to *fixed* to repeat. Not written to the JSON. |
| `gender` | Any | Pronouns + gender-specific presentation (no beards on women; no random makeup, nail polish, feminine jewellery or hairstyles on men). `Any` **rolls a coherent man OR woman each run** (a 50/50 coin-flip; an anatomical lock like a beard decides it), so features stay self-consistent. Defers to a connected preset's gender. To instead unlock fully mixed-gender output, set `wardrobe` to `Any` (see below). |
| `wardrobe` | Match gender | Outfit wardrobe **and presentation**. `Match gender` follows the (rolled) gender; `Feminine`/`Masculine` force a wardrobe (e.g. a man in feminine outfits). `Any` mixes outfits — and, when `gender` is also `Any`, restores the fully mixed-gender "anything goes" mode (both feature pools unioned, neutral *they/them* pronouns). On a **man**, a `Feminine` or `Any` wardrobe also lifts the masculine defaults for jewellery, nails, footwear, **bags** and makeup, so the whole femme look is reachable; `Match gender`/`Masculine` keep him bare-faced, unjewelled and carrying a men's bag if any. Structural defaults (hair, brows, lips, eye shape, bust) always apply. Set to **Auto (preset)** when loading a saved character to replay its exact saved wardrobe instead of the default. |
| `hair_color_scope` | Natural only | Keeps random hair realistic; `Full spectrum` allows fantasy colours. Set to **Auto (preset)** when loading a saved character to replay its exact saved scope. |
| `accessory_density` | Balanced | How often bags/jewellery/accessories appear: `None` (bare), `Minimal`, `Balanced`, `Maximal`. Drop it for clean portraits without locking fields by hand. |
| `location_setting` | Any indoor/outdoor | Restrict the random scene. `Any indoor/outdoor` picks any real location but never a studio; `Indoor`/`Outdoor` narrow to real scenes; `Studio / solid backdrop` forces a plain, easily-maskable background (seamless grey, solid white, solid black, or chroma-key green) plus clean studio light. A locked location wins. |
| `set_all_fields` | Off | `All to None` blanks every field still on `Random` so only the fields you lock to a value appear — a one-click "start from nothing". A wired costume and the character's signature look (hair, eyes, physique) are kept. |

## How locking works

A field's dropdown value *is* its lock state — there is no separate lock button:

- **`Random`** (default) — randomize each run.
- **a concrete value** — lock it (kept across runs).
- **`None`** — omit the field from the output entirely. Every field offers exactly one `None`,
  so you can set `location`, `lighting`, `framing`, `mood`, etc. to `None` to describe a
  **character only** and add your own scene in a larger prompt.

Master buttons act on all fields: **Unlock all (set to Random)** and **Roll + lock all fields**
(freeze the current random values so you can tweak from there). Click a group header to collapse
it.

To go the other way — start from *nothing* and switch on only a handful of fields — set
`set_all_fields` to `All to None`: every field left on `Random` is dropped, so just the ones you
lock to a value are emitted. Ideal for tweaking a cosplay (its costume and signature look are
preserved) without setting dozens of fields to `None` by hand.

## Constraints

After randomizing, an engine resolves coherence rules — a buzz cut never gets a braid,
"no makeup" clears every cosmetic, an athletic outfit drops the handbag, a sedentary build is
never "very muscular", and so on. A rule never overrides a field **you** locked; it logs an
`[IdentityForge]` notice and keeps your value.

The `gender` toggle is a hard gate, not a coherence rule: gender-specific values (e.g. facial
hair) are always validated against the chosen gender, even when they arrive locked from a preset.
Pointing a masculine preset at a `Female` node never produces a beard — the engine drops the
incompatible value, re-randomizes it within the `Female` pool, and logs a notice.

`Male` also applies **masculine presentation defaults** to the *random* fill: no makeup, nail
polish, feminine jewellery, lip colour or hairstyles. These govern randomization only — a value
you lock yourself, or one carried by a preset's signature, is respected (so a man cosplaying a
pigtailed character keeps the pigtails).

`Any` resolves to a concrete man or woman per seed (so the whole character is coherent — no beard
beside a feminine bust), then applies that gender's rules above. A strongly gendered lock decides
the coin-flip (locking a beard yields a man); otherwise it is an even 50/50. For deliberately
mixed-gender output, set `wardrobe: Any` together with `gender: Any` — that keeps both feature
pools unioned and uses neutral *they/them* pronouns.

## Pairing with a rendering pack

`prose` is a plain string, so it composes with any downstream node that takes text —
notably [Stylebook](https://github.com/EnragedAntelope/comfyui-stylebook), which adds
medium, lighting, colour grade, era, finish and mood on top. When pairing the two, set
`lighting` and `mood` here to `None` so the two packs don't each state the same axis;
see the [README](../README.md#using-with-stylebook) for the full split.

## Custom options

Add your own choices without editing the source (they survive updates): copy
`user_options.example.json` to `user_options.json` in the pack folder, then restart ComfyUI. Five
optional sections:

```json
{
  "fields":     { "ethnicity": ["Atlantean"], "location": ["a floating sky temple"] },
  "outfits":    { "spacesuit": { "unisex": ["a sleek white EVA suit with a gold visor"] } },
  "archetypes": { "Sky Pirate": { "gender": "Female", "outfit_description": "a {color} longcoat over a leather bodice" } },
  "cosplayers": { "Custom Hero (My OC)": { "gender": "Female", "costume": "a teal-and-silver bodysuit with a star emblem" } },
  "creatures":  { "axolotl": { "class": "Marine Life", "palette": "pale pink", "head": "a smiling axolotl head with feathery gills", "eyes": "tiny dark eyes", "integument": "smooth translucent skin" } }
}
```

- **`fields`** extends a dropdown's options — any field except the control toggles (`gender`,
  `hair_color_scope`, `location_setting`) and the garment-coupled `outfit_style` /
  `outfit_description`. A custom **`hair_color`** is only drawn at random under
  `Full spectrum`: the `Natural only` scope filters the pool through the shipped
  realistic-shade list, which your additions are not part of. They stay selectable by
  hand under either scope.
- **`outfits`** adds a whole new `outfit_style`, registering its garment text *and* the dropdown
  entry together (so the style can never be picked without clothing).

  **Write garment text as a garment phrase: garments and fabrics only, no leading article, and
  no shoes, colour, jewellery or bag.** The engine composes the palette, the pattern and the
  footwear onto it from their own fields — `"satin slip gown with delicate straps"` renders as
  *"a jewel-toned satin slip gown with delicate straps, in strappy heels"*. Strings written the
  old way (with an article and their own shoes) still work: the engine detects what a string
  already states and skips that clause rather than doubling up. They simply will not gain the
  new colour/pattern/footwear variety until reworded.

  Buckets are `unisex`
  (always eligible) plus `female` / `male`, chosen by the `wardrobe` control; any subset works.
- **`archetypes`** adds presets to the Archetype node (same `{field: value}` shape as the
  built-ins; `outfit_description` may use `{slot}` placeholders).
- **`cosplayers`** adds characters to the Cosplayer node. `costume` (worn items only) is required;
  `franchise`/`gender` are optional; `signature` (both modes) and `physique` (Full character) are
  `{field: value}` maps. An optional `"prop"` string adds a signature held item; an optional
  free-text `"eyes"` string sets a canonical non-standard eye colour (e.g. `"crimson"`). A
  `gender: "Male"` entry is how you populate the `Random — male` pick. For a fully masked head set
  `"covers_face": true` **and** put the head covering in a separate `"mask"` string. The advanced
  flags work too, each optional and off by default: `"covers_body": true` (full hard suit — hides
  bare skin, suppresses jewellery/nails), `"covers_hair": true` (hood/cowl hides the hair while
  the face shows), `"bald": true` (fully hairless head), `"body_paint": true` (the skin itself is
  the costume colour; add `"skin": "warm green"` to name the colour when it isn't obvious from
  the costume text). Word a full-body colour skin-native — `"smooth, flawless <colour> skin"` —
  not as "body paint"/"dye", which t2i models render as a streaky coat over a human tone; the
  skin-native marker is auto-detected, so the flag is only needed for other phrasings. See the
  worked examples in
  [user_options.example.json](../user_options.example.json).
- **`creatures`** adds forms to the Creature node. `class` (one of the nine classes), `palette`
  and the three core slots `head` / `eyes` / `integument` are required; the rest are optional.

A user entry whose name matches a built-in **overrides** it. Run `python tests/validate_data.py`
to check that your custom field values are valid options.

## Field groups

| Group | Fields |
| --- | --- |
| Demographics | age, ethnicity |
| Body | skin tone, body type, height, bust/chest, waist, hips, shoulders, neck, posture, fitness |
| Face | shape, forehead, cheekbones, eyebrows, eyes, nose, lips, smile, jawline, chin, complexion, skin details, freckles |
| Hair | colour, length, texture, style, part, highlights, facial hair, accessory |
| Makeup | style, eyeshadow, eyeliner, lashes, lips, blush, brows, contour, highlight, finish |
| Jewelry & Nails | earrings, necklace, rings, bracelet, watch, other jewellery, piercings, nails |
| Clothing | outfit style (which picks a garment set), footwear, colour palette, pattern, bag, accessories — the palette, pattern and shoes are composed onto the garment, so locking any of them changes the outfit |
| Setting & Shot | expression, pose, location (indoor/outdoor), lighting, season, framing, composition, mood |

## Example

Seed `42`, Female, `hair_color` = auburn:

> A 22-year-old Finnish woman with an average build, short, and very pale skin. …
> Her hair is mid back loosely wavy auburn, French twist. … She wears a fresh-faced
> dewy look, cool browns and taupes eyeshadow, …, and natural finish. She has a
> simple gold bracelet, a chain bracelet, and medium length natural nails. She
> wears a burgundy wrap dress with gold hoop earrings and strappy heels, carrying
> a tan leather crossbody. Her expression is relaxed, set in a suburban basement, …

`prompt_json` mirrors this, nested by group with a small `_meta` block.

## Turnaround views

The **Identity Forge Turnaround** node builds a reference set: one character, every camera
angle, from a single queue.

```
Cosplayer/Archetype -> Identity Forge -(prompt_json)-> Turnaround -(prompt)-> CLIPTextEncode -> ...
```

Wire Identity Forge's **`prompt_json`** output into `character_json`. That output is a fully
resolved character, so every angle reproduces it exactly - nothing is re-rolled between
views, and it does not matter whether the nodes upstream are set to randomize each run.

`prompt` and `view_label` are **list** outputs: ComfyUI runs everything downstream once per
view, so one queue produces the whole set. The rest of the graph needs no rewiring - a
single negative prompt, model and latent are reused across all of them. Wire `view_label`
into Save Image's `filename_prefix` and the set lands on disk in rotation order
(`1-front`, `2-three-quarter-left`, …).

Three controls, all camera:

- **`views`** - `Turnaround (6)`, `Turnaround (4)`, `Front + back (2)` or `Front + profile (2)`.
  This is also how many images one queue produces.
- **`framing`** - how much of the subject each view frames, `Full body` by default. It is
  combined with the angle and replaces whatever framing the character resolved to.
- **`pose`** - a standing, symmetric stance, so the only thing changing between views is
  the camera. An asymmetric pose (a hand on one hip) reads as a different body from each
  side. `Keep the character's pose` leaves it alone for a looser character sheet.

The straight-back view drops the face automatically. A t2i model draws whatever the prose
names, so "bright blue eyes ... deep red lip colour ... a broad smile" made it turn the head
to show them - which is not a back view. On `6-back` the Face and Makeup fields, `facial_hair`
and `expression` are simply omitted; hair, costume, build, earrings and the scene all stay,
and a masked character keeps their mask. Nothing is ever *negated* (a prompt that says "the
face is not visible" draws a face). `5-rear-three-quarter` keeps its face description, because
at that angle a cheek and jaw genuinely are in frame.

Everything else belongs on the Identity Forge node - it owns the character and the scene,
the Turnaround owns only the camera. For a clean reference sheet, set that node's
`location_setting` to `Studio / solid backdrop` and lock `composition` to `centered symmetry`.

## Notes

- The ethnicity-to-skin-tone link is a *soft* bias over coarse regional bands; lock `skin_tone`
  for an exact tone.
- Costume archetypes carry their own outfit, so `wardrobe`/outfit randomization don't apply
  (colours still vary by seed).
- Prose summarizes: a few fine fields (eye size, teeth) live in the JSON but are left
  out of the prose to avoid clutter.
