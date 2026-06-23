# ComfyUI Identity Forge

**Endless, coherent characters from dropdowns — no prompt-wrangling.** Queue once
for a believable person; queue again for a brand-new one. Identity Forge turns
70+ menu choices into clean natural-language prose (for CLIP Text Encode) plus a
structured JSON record — with a constraint engine that keeps every result
sensible: no beards on the buzz-cut, no handbag with the gym kit, no Irish
ancestry rendered in ebony skin.

Lock the few traits you care about, let the rest roll. Drop in an **archetype**
for an instant costumed look on an ever-changing person, or a **cosplayer**
preset to put a fictional character's outfit on a random (optionally cross-gender)
person. Set the scene fields to `None` to get a **character-only** description you
can splice into a larger prompt.

- 🎲 **Reproducible** — seed-driven, so any character you like comes back exactly.
- 🧩 **Coherent by design** — a constraint engine resolves clashing traits for you.
- 🎭 **Archetypes** — knight, sorceress, pirate, ninja, samurai, pop star, astronaut, surgeon… as a one-wire preset.
- 🦹 **Cosplayers** — a random person cosplaying a fictional character, with crossplay, a helmet-off *Unmask* toggle, and opt-in signature props (Thor's hammer, Cap's shield) supported.
- ✨ **Modifiers** — prepend a custom descriptor to a single element (sci-fi shoes, glowing earrings, iridescent skin) without theming the whole image.
- 💾 **Character vault** — save a generated character (with a thumbnail) and recall it later; a built-in gallery lets you browse, rename and delete saves.
- 🔗 **Chainable presets** — wire Archetype → Cosplayer → Modifier → Identity Forge so they stack instead of fighting over one socket.
- 🔌 **Zero dependencies, fully offline** — no LLM, no API keys, no model downloads.
- ✍️ **Extensible** — add your own dropdown options (and outfit styles) without touching the source.

| Node | What it does |
| --- | --- |
| **Identity Forge** | 70+ lockable dropdown fields (8 collapsible groups) + a constraint engine → `prompt_text` (prose) and `prompt_json`. |
| **Identity Forge Archetype** | Dozens of themed presets (knight, sorceress, pirate, ninja, samurai, pop star, astronaut, surgeon…) that wire into Identity Forge to set the *look* while the person underneath randomizes. |
| **Identity Forge Cosplayer** | Fictional characters (Spider-Man, Batman, Darth Vader, Cloud, 2B, She-Hulk, Zelda…) as a *cosplay look* — the costume is locked onto a random, optionally cross-gender person. |
| **Identity Forge Modifier** | Prepend a custom descriptor to one field (`footwear: sci-fi`) or a whole group (`Clothing: weathered`) for per-element stylistic tilts — without touching the main node. |
| **Identity Forge Vault Save** | Save the generated character to a local vault. Terminal node like Save Image — branch in `prompt_json` (and optionally the image for a thumbnail). |
| **Identity Forge Vault Load** | Recall a saved character as a chainable `character_json` preset, with a thumbnail preview and a Manage Vault gallery. |

Built on the ComfyUI **V3 API** (`comfy_api.latest`). Category:
`conditioning/character`.

---

## Showcase

**The main node** — only a slice of the 70+ options is shown:

<img src="https://github.com/user-attachments/assets/01be6441-457a-4ea1-b88d-e93b40623756" alt="Identity Forge main node" width="480" />

**Example archetypes:**

<img src="https://github.com/user-attachments/assets/96da503c-eea8-489a-82c8-a48f34888ba5" alt="Identity Forge archetype presets" width="320" />

**Sample outputs** (each image embeds the test workflow — drag one into ComfyUI to load it):

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/26f0ec17-35dd-40e1-a036-21a7de81a0cd" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/ebb55a64-6694-4285-bb92-13cba5745709" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/d7107faf-498d-41e2-8b7c-dce5c6c0f503" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/5794b2d8-a0ce-41f4-b02f-731cb3f85992" alt="sample output" width="190" /></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/16805e63-77b1-4334-9f25-5f9f30877929" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/7ae12729-d7f6-4ea8-aea3-e7b769c87e59" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/1ab4f93a-ce8b-43c0-a587-308db8475344" alt="sample output" width="190" /></td>
    <td><img src="https://github.com/user-attachments/assets/4db343ea-1c57-43a8-b5e8-d530416cb780" alt="sample output" width="190" /></td>
  </tr>
</table>

---

## Install

Clone into `custom_nodes` and restart ComfyUI (no Python dependencies):

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/EnragedAntelope/comfyui-identity-forge
```

Or install via **ComfyUI Manager** (search *Identity Forge*, once published).

---

## Quick start

1. Add **Identity Forge**, connect `prompt_text` → **CLIP Text Encode**.
2. Leave fields on `Random`, or pick a value to lock the ones you care about.
3. Queue. The seed auto-randomizes, so each run is a new character (set the seed
   control to *fixed* to reproduce one).

### Adding an archetype

```
Identity Forge Archetype ──(character_json)──▶ Identity Forge.archetype_json
                                                       │ (prompt_text)
                                                       ▼
                                              CLIP Text Encode ▶ KSampler …
```

The archetype overrides its signature fields (costume above all) and lets the
rest randomize — e.g. *Fairy Princess* gives a fairy gown (with seed-varied
colour/fabric/flower) on a different person every run. Pick `Random` to let the
seed choose an archetype; `None` overrides nothing. Anything you set on the
Identity Forge widgets still wins.

Its **lock level**: **Essentials** (default) sends only the look, so face/body/
ethnicity randomize each run; **Full preset** locks every field it defines for a
fixed character.

**Stacking presets.** Both preset nodes have an optional `upstream` input, so you
can chain them into one wire instead of swapping plugs:

```
Identity Forge Archetype ─▶ Identity Forge Cosplayer ─(character_json)─▶ Identity Forge.archetype_json
```

The node closest to Identity Forge wins where fields overlap (downstream wins);
non-overlapping values from upstream survive. Set any node in the chain to `None`
and it simply passes its upstream through — so both presets can stay wired and you
just toggle which is active.

### Cosplaying a fictional character

```
Identity Forge Cosplayer ──(character_json)──▶ Identity Forge.archetype_json
```

Pick a character (or a `Random — any / female / male` entry) and the costume drops
onto a freshly randomized person — a *cosplayer*, not a clone. The prose is
prefixed `Cosplaying as <Character> (<Franchise>):`.

- **`look_level`**: **Costume only** (default) sends the costume plus signature
  hair/eyes, so body, face, and ethnicity randomize; **Full character** also locks
  the physique.
- **Crossplay just works.** The character's gender only scopes the `Random …`
  picks — the *person's* gender is the Identity Forge `gender` widget. Aim a female
  character at a `Male` node and you get a man in that costume.
- **Full-mask characters look right.** Entries whose head is fully covered (Spider-
  Man, a Mandalorian helmet, a ninja hood) suppress the randomized face/hair so
  only the mask is described — no stray face fighting the costume at render time.
- **`mask`**: **Default** keeps the mask on (face/hair hidden). **Unmask (show
  face)** drops the head covering and reveals the randomized head/hair under the
  suit — a helmet-off look (Tony Stark in the Iron Man armor, Peter Parker in the
  suit). It has no effect on face-visible characters.
- **`props`**: **off by default.** Choose **Include signature prop** to add a
  character's iconic held item — Thor's hammer, Captain America's shield, Link's
  Master Sword — voiced as *holding …*. Only characters that have a signature prop
  are affected; everyone else is unchanged. (Note: held objects can stress hand
  rendering in some models, which is why it is opt-in.)
- Chain it with the Archetype node via the `upstream` input (see *Stacking
  presets* above) — no need to unplug one to use the other. Costumes still list
  only *worn* items; held props beyond the signature toggle go in the prompt.

See [docs/cosplayer-notes.md](docs/cosplayer-notes.md) for the finer details.

### Tilting a single element (Modifier node)

```
Identity Forge Modifier ──(character_json)──▶ Identity Forge.archetype_json
```

Want *just the shoes* to read sci-fi, or *just the skin* to look iridescent —
without theming the whole image? The **Modifier** node prepends a custom descriptor
in front of one element's randomized value (right where text-to-image models pick up
textures and genres). Type one `key: descriptor` per line:

```
footwear: sci-fi chrome      # a FIELD  -> only the shoes change
earrings: glowing            # a FIELD  -> only the earrings
skin_tone: iridescent        # a FIELD  -> only the skin tone
Clothing: weathered          # a GROUP  -> prepended to every clothing item
```

- **`key`** is either a **field name** — the same labels shown on the Identity Forge
  node (`footwear`, `skin_tone`, `hair_color`, `earrings`, …) — for pin-point control,
  or a **group header** (`Demographics`, `Body`, `Face`, `Hair`, `Makeup`,
  `Jewelry & Nails`, `Clothing`, `Setting & Shot`) to tilt the whole group. A group
  key is prepended to *each* present item in the group (so it can repeat — reach for
  field keys when you want one item).
- Keys are **case-insensitive**; a field key wins over a group key for the same field.
  `#` comments and blank lines are ignored; unknown keys are skipped with a console
  note. The box ships pre-filled with commented examples — delete a `#` to switch a
  line on.
- Modifiers only **decorate elements that are present** — they style an item, they
  don't force an absent/`None` one to appear.
- **Chainable**: wire it after an Archetype/Cosplayer via `upstream`
  (`Cosplayer → Modifier → Identity Forge`). Clear the box or **mute the node** to
  disable it.

### Saving & recalling characters (Vault)

Found a character you love and want it back later? Save it, then load it.

```
Identity Forge ──(prompt_json)──▶ Identity Forge Vault Save   (terminal — like Save Image)
   VAE Decode ──(image, optional)─▶
```

```
Identity Forge Vault Load ──(character_json)──▶ Identity Forge.archetype_json
```

- **Vault Save** is a small terminal node, used just like **Save Image**: branch
  Identity Forge's `prompt_json` into it — that's the only required wire. Optionally
  wire the rendered `image` for a thumbnail. The `name` is optional: leave it blank
  and you get an automatic one — the cosplay/archetype label if present, otherwise a
  description like `Woman, 25, auburn hair`, otherwise `Character N`. Auto-names never
  overwrite a prior save; a name you type honours `on_existing` (overwrite / keep-both
  / skip). **Mute the node (Ctrl+M) to skip saving** without rewiring.
- **`prompt_json` is all it needs** — by the time Identity Forge emits it, any wired
  Cosplayer / Archetype / Modifier is already baked in, so one saved file captures
  the whole character regardless of how the graph was wired. (The prose is
  regenerated from the same fields on reload, so it isn't saved.)
- **Vault Load** recalls it as a `character_json` — the *same* output the preset
  nodes use — so it wires into `archetype_json` and can even stack with a Modifier
  via `upstream`. Because recall flows back through the JSON string input (not the
  individual dropdowns), it keeps working even if field options change in a later
  update. **🔄 Refresh** updates the list without restarting; **🗂 Manage Vault…**
  opens a thumbnail gallery to pick (*Use*), rename, delete, or bulk-delete saves.
- **Where it's stored:** `ComfyUI/user/identity_forge/characters/<name>/` — one
  folder per character (`character.json`, `prompt.txt`, `preview.png`, `meta.json`).
  It lives under `user/`, so it survives node updates and is **not** wiped when you
  clear your `output/` images. To move or share a single character, copy its folder.

---

## Controls

The widgets at the top of Identity Forge steer the whole character:

| Control | Default | Effect |
| --- | --- | --- |
| `seed` | randomize | Reproducibility. Auto-randomizes each run; set to *fixed* to repeat. Not written to the JSON. |
| `gender` | Any | Pronouns + gender-specific presentation (no beards on women; no random makeup, nail polish, feminine jewellery or hairstyles on men). `Any` deliberately mixes both. Deferring to a connected archetype when set to `Any`. |
| `wardrobe` | Match gender | Outfit wardrobe. `Feminine`/`Masculine`/`Any` deliberately mix (e.g. a man in feminine outfits). |
| `hair_color_scope` | Natural only | Keeps random hair realistic; `Full spectrum` allows fantasy colours. |
| `accessory_density` | Balanced | How often bags/jewellery/accessories appear: `None` (bare) · `Minimal` · `Balanced` · `Maximal`. |
| `location_setting` | Any indoor/outdoor | Restrict the random scene. `Any indoor/outdoor` (default) picks any real location but never a studio. `Indoor` / `Outdoor` narrow to real scenes. `Studio / solid backdrop` forces a plain, easily-maskable background — seamless grey, solid white, solid black, or chroma-key green screen — plus clean studio light (handy for cutting the subject out afterwards). A locked location wins. |
| `set_all_fields` | Off | `All to None` blanks every field still on `Random` so only the fields you lock to a value appear — a one-click "start from nothing". A wired costume and the character's signature look (hair, eyes, physique) are kept. |

> **Tip:** the old "everyone carries a bag" problem is handled by
> `accessory_density` — drop it to `Minimal`/`None` for clean portraits, without
> locking ten fields by hand.

### How locking works

A field's dropdown value *is* its lock state — there's no separate lock button:

- **`Random`** (default) — randomize each run.
- **a concrete value** — lock it (kept across runs).
- **`None`** — omit the field from the output entirely. Every field offers this,
  so you can set `location`, `lighting`, `framing`, `mood`, etc. to `None` to
  describe a **character only** and add your own scene in a larger prompt.

Master buttons act on all fields: **🎲 Unlock all (set to Random)** and
**🔒 Roll + lock all fields** (freeze the current random values so you can tweak
from there). Click a `▾ Group` header to collapse it.

To go the other way — start from *nothing* and switch on only a handful of
fields — set **`set_all_fields` → `All to None`**: every field left on `Random`
is dropped, so just the ones you lock to a value are emitted. Ideal for tweaking
a cosplay (its costume and signature look are preserved) without setting dozens of
fields to `None` by hand.

### Constraints

After randomizing, an engine resolves coherence rules — a buzz cut never gets a
braid, "no makeup" clears every cosmetic, an athletic outfit drops the handbag, a
sedentary build is never "very muscular", and so on. A rule never overrides a
field **you** locked; it logs an `[IdentityForge]` notice and keeps your value.

The `gender` toggle is a hard gate, not a coherence rule: gender-specific values
(e.g. facial hair) are always validated against the chosen gender, even when they
arrive locked from an archetype. So pointing a masculine archetype at a
`Female` node never produces a beard — the engine drops the incompatible value,
re-randomizes it within the `Female` pool, and logs an `[IdentityForge]` notice.

`Male` also applies **masculine presentation defaults** to the *random* fill: no
makeup, nail polish, feminine jewellery, lip colour or hairstyles. These govern
randomization only — a value you lock yourself, or one carried by an archetype or
cosplayer signature, is respected (so a man cosplaying a pigtailed character keeps
the pigtails). Choose `gender: Any` to mix presentations freely.

### Custom options

Add your own choices without editing the source (they survive updates): copy
`user_options.example.json` to `user_options.json` in the pack folder, then
restart ComfyUI. Four optional sections:

```json
{
  "fields":     { "ethnicity": ["Atlantean"], "location": ["a floating sky temple"] },
  "outfits":    { "spacesuit": { "unisex": ["a sleek white EVA suit with a gold visor"] } },
  "archetypes": { "Sky Pirate": { "gender": "Female", "outfit_description": "a {color} longcoat over a leather bodice" } },
  "cosplayers": { "Custom Hero (My OC)": { "gender": "Female", "costume": "a teal-and-silver bodysuit with a star emblem" } }
}
```

- **`fields`** extends a dropdown's options — any field except the control
  toggles (`gender`, `hair_color_scope`, `location_setting`) and the
  garment-coupled `outfit_style` / `outfit_description`.
- **`outfits`** adds a whole new `outfit_style`, registering its garment text
  *and* the dropdown entry together (so the style can never be picked without
  clothing). Buckets are `unisex` (always eligible) plus `female` / `male`,
  chosen by the `wardrobe` control; any subset works.
- **`archetypes`** adds presets to the **Archetype** node (same `{field: value}`
  shape as the built-ins; `outfit_description` may use `{slot}` placeholders).
- **`cosplayers`** adds characters to the **Cosplayer** node. `costume` (worn
  items only) is required; `franchise`/`gender` are optional; `signature` (both
  modes) and `physique` (Full character) are `{field: value}` maps. An optional
  `"prop"` string adds a signature held item, voiced as *holding …* when the
  node's `props` toggle is on (describe it richly, like a costume). A `gender:
  "Male"` entry is how you populate the `Random — male` pick. For a fully masked
  head set `"covers_face": true` **and** put the head covering in a separate
  `"mask"` string (kept out of `costume`) so the *Unmask* toggle can drop it.

A user entry whose name matches a built-in **overrides** it. Run
`python tests/validate_data.py` to check that your custom field values are valid
options.

---

## Field groups

| Group | Fields |
| --- | --- |
| Demographics | age, ethnicity |
| Body | skin tone, body type, height, bust/chest, waist, hips, shoulders, neck, posture, fitness, muscle |
| Face | shape, eyes, nose, lips, cheekbones, jawline, chin, eyebrows, complexion, freckles, skin details |
| Hair | colour, length, texture, style, part, volume, highlights, facial hair |
| Makeup | style, eyeshadow, eyeliner, lashes, lips, blush, brows, contour, highlight, finish |
| Jewelry & Nails | earrings, necklace, rings, bracelet, watch, other jewellery, piercings, nails |
| Clothing | outfit style (→ a full outfit), footwear, colour, pattern, bag, accessories |
| Setting & Shot | expression, pose, location (indoor/outdoor), lighting, time of day, season, framing, mood |

---

## Example

Seed `42`, Female, `hair_color` = auburn:

> A 22-year-old Finnish woman with an average build, short, and very pale skin. …
> Her hair is mid back loosely wavy auburn, French twist. … She wears a fresh-faced
> dewy look, cool browns and taupes eyeshadow, …, and natural finish. She has a
> simple gold bracelet, a chain bracelet, and medium length natural nails. She
> wears a burgundy wrap dress with gold hoop earrings and strappy heels, carrying
> a tan leather crossbody. Her expression is relaxed, set in a suburban basement, …

`prompt_json` mirrors this, nested by group with a small `_meta` block.

---

## Notes

- The ethnicity→skin-tone link is a *soft* bias over coarse regional bands; lock
  `skin_tone` for an exact tone.
- Costume archetypes carry their own outfit, so `wardrobe`/outfit randomization
  don't apply (colours still vary by seed).
- Prose summarizes: a few fine fields (hair volume, eye size, teeth) live in the
  JSON but are left out of the prose to avoid clutter.

## Contributing characters & archetypes

The `user_options.json` route above is for private or instant additions, but you
don't have to maintain your own list forever. **Suggestions are welcome** — open an
[issue](https://github.com/EnragedAntelope/comfyui-identity-forge/issues) (or a PR)
proposing new cosplayers, archetypes, outfit styles, or fields and they can be
folded into the built-in set so everyone gets them on the next update. For
cosplayers, a costume description (worn items only) and the franchise are enough to
start; mark `covers_face` + `mask` if the head is fully covered.

## Development

The engine runs without ComfyUI:

```bash
python tests/validate_data.py            # data integrity
python -m unittest discover -s tests -v  # engine + integration tests
```

`js/identity_forge.js` embeds data generated from `data/fields.py` — regenerate
it only if you change the gender-divergent fields or the field set.

## License

MIT — see [LICENSE](LICENSE).
