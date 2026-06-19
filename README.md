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
- 🦹 **Cosplayers** — a random person cosplaying a fictional character, with crossplay supported.
- 🔌 **Zero dependencies, fully offline** — no LLM, no API keys, no model downloads.
- ✍️ **Extensible** — add your own dropdown options (and outfit styles) without touching the source.

| Node | What it does |
| --- | --- |
| **Identity Forge** | 70+ lockable dropdown fields (8 collapsible groups) + a constraint engine → `prompt_text` (prose) and `prompt_json`. |
| **Identity Forge Archetype** | Dozens of themed presets (knight, sorceress, pirate, ninja, samurai, pop star, astronaut, surgeon…) that wire into Identity Forge to set the *look* while the person underneath randomizes. |
| **Identity Forge Cosplayer** | Fictional characters (2B, Lara Croft, Sailor Moon, She-Hulk, Zelda…) as a *cosplay look* — the costume is locked onto a random, optionally cross-gender person. |

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
- Shares the `archetype_json` socket with the Archetype node (use one or the
  other). Held props/weapons are left out on purpose — add them in the prompt.

See [docs/cosplayer-notes.md](docs/cosplayer-notes.md) for the finer details.

---

## Controls

The widgets at the top of Identity Forge steer the whole character:

| Control | Default | Effect |
| --- | --- | --- |
| `seed` | randomize | Reproducibility. Auto-randomizes each run; set to *fixed* to repeat. Not written to the JSON. |
| `gender` | Any | Pronouns + gender-specific pools (no beards on women, etc.). `Any` defers to a connected archetype. |
| `wardrobe` | Match gender | Outfit wardrobe. `Feminine`/`Masculine`/`Any` deliberately mix (e.g. a man in feminine outfits). |
| `hair_color_scope` | Natural only | Keeps random hair realistic; `Full spectrum` allows fantasy colours. |
| `accessory_density` | Balanced | How often bags/jewellery/accessories appear: `None` (bare) · `Minimal` · `Balanced` · `Maximal`. |
| `location_setting` | Any | Restrict the random scene to `Indoor` or `Outdoor` (a locked location wins). |

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
  modes) and `physique` (Full character) are `{field: value}` maps. A `gender:
  "Male"` entry is how you populate the `Random — male` pick.

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
