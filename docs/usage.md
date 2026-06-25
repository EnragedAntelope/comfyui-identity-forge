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
| `gender` | Any | Pronouns + gender-specific presentation (no beards on women; no random makeup, nail polish, feminine jewellery or hairstyles on men). `Any` deliberately mixes both, and defers to a connected preset's gender when set to `Any`. |
| `wardrobe` | Match gender | Outfit wardrobe. `Feminine`/`Masculine`/`Any` deliberately mix (e.g. a man in feminine outfits). |
| `hair_color_scope` | Natural only | Keeps random hair realistic; `Full spectrum` allows fantasy colours. |
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
pigtailed character keeps the pigtails). Choose `gender: Any` to mix presentations freely.

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
  `outfit_description`.
- **`outfits`** adds a whole new `outfit_style`, registering its garment text *and* the dropdown
  entry together (so the style can never be picked without clothing). Buckets are `unisex`
  (always eligible) plus `female` / `male`, chosen by the `wardrobe` control; any subset works.
- **`archetypes`** adds presets to the Archetype node (same `{field: value}` shape as the
  built-ins; `outfit_description` may use `{slot}` placeholders).
- **`cosplayers`** adds characters to the Cosplayer node. `costume` (worn items only) is required;
  `franchise`/`gender` are optional; `signature` (both modes) and `physique` (Full character) are
  `{field: value}` maps. An optional `"prop"` string adds a signature held item; an optional
  free-text `"eyes"` string sets a canonical non-standard eye colour (e.g. `"crimson"`). A
  `gender: "Male"` entry is how you populate the `Random — male` pick. For a fully masked head set
  `"covers_face": true` **and** put the head covering in a separate `"mask"` string. For a bald
  character, state it in `costume` and do not lock a hair length.
- **`creatures`** adds forms to the Creature node. `class` (one of the nine classes), `palette`
  and the three core slots `head` / `eyes` / `integument` are required; the rest are optional.

A user entry whose name matches a built-in **overrides** it. Run `python tests/validate_data.py`
to check that your custom field values are valid options.

## Field groups

| Group | Fields |
| --- | --- |
| Demographics | age, ethnicity |
| Body | skin tone, body type, height, bust/chest, waist, hips, shoulders, neck, posture, fitness, muscle |
| Face | shape, eyes, nose, lips, cheekbones, jawline, chin, eyebrows, complexion, freckles, skin details |
| Hair | colour, length, texture, style, part, volume, highlights, facial hair |
| Makeup | style, eyeshadow, eyeliner, lashes, lips, blush, brows, contour, highlight, finish |
| Jewelry & Nails | earrings, necklace, rings, bracelet, watch, other jewellery, piercings, nails |
| Clothing | outfit style (a full outfit), footwear, colour, pattern, bag, accessories |
| Setting & Shot | expression, pose, location (indoor/outdoor), lighting, time of day, season, framing, mood |

## Example

Seed `42`, Female, `hair_color` = auburn:

> A 22-year-old Finnish woman with an average build, short, and very pale skin. …
> Her hair is mid back loosely wavy auburn, French twist. … She wears a fresh-faced
> dewy look, cool browns and taupes eyeshadow, …, and natural finish. She has a
> simple gold bracelet, a chain bracelet, and medium length natural nails. She
> wears a burgundy wrap dress with gold hoop earrings and strappy heels, carrying
> a tan leather crossbody. Her expression is relaxed, set in a suburban basement, …

`prompt_json` mirrors this, nested by group with a small `_meta` block.

## Notes

- The ethnicity-to-skin-tone link is a *soft* bias over coarse regional bands; lock `skin_tone`
  for an exact tone.
- Costume archetypes carry their own outfit, so `wardrobe`/outfit randomization don't apply
  (colours still vary by seed).
- Prose summarizes: a few fine fields (hair volume, eye size, teeth) live in the JSON but are left
  out of the prose to avoid clutter.
