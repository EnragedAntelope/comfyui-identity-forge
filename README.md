# ComfyUI Identity Forge

**Endless, coherent characters from dropdowns — no prompt-wrangling.** Queue once for a
believable person; queue again for a brand-new one. Identity Forge turns menu choices into clean
natural-language prose (for CLIP Text Encode) plus a structured JSON record — with a constraint
engine that keeps every result sensible: no beard on the buzz-cut, no handbag with the gym kit,
and skin tone that stays plausible for the chosen ancestry in either direction — no Irish
subject in ebony skin, no West African subject in porcelain. Lock the few traits you care about,
let the rest roll.

**Why you'll like it**

- **Coherent by design** — a constraint engine resolves clashing traits for you, automatically.
- **Reproducible** — seed-driven, so any character you like comes back exactly.
- **Archetypes & cosplayers** — a deep library of themed looks and fictional-character costumes
  dropped onto an ever-changing person, with crossplay and a helmet-off *Unmask* toggle.
- **Creature layer** — render the character as an animal / monster / alien, *hybridized
  slot-by-slot* (a praying-mantis body with a sloth's head), anthropomorphic, feral or a subtle accent.
- **Chainable** — Archetype → Cosplayer → Creature → Modifier → Identity Forge stack instead of
  fighting over one socket; a **character vault** saves and recalls the ones you love.
- **Zero dependencies, fully offline** — no LLM, no API keys, no model downloads.

Built on the ComfyUI **V3 API** (`comfy_api.latest`). Category: `conditioning/character`.

---

## Showcase

Chain the preset nodes into the main Identity Forge node — the node **closest to Identity Forge
wins** any conflict:

<img width="560" alt="Sample node chain" src="https://github.com/user-attachments/assets/82d80ecd-b25a-475a-a4e0-ae0d6116a744" />

A taste of archetypes, cosplay characters and creatures:

<table>
  <tr>
    <td><img width="240" alt="Archetypes" src="https://github.com/user-attachments/assets/c1871f28-f52d-42b6-8ca6-6dff2d1793f8" /></td>
    <td><img width="240" alt="Cosplay characters" src="https://github.com/user-attachments/assets/256d81e2-ed75-47cd-80f5-e8e7e2837a91" /></td>
    <td><img width="240" alt="Creatures" src="https://github.com/user-attachments/assets/65b0cbfa-6e93-47de-bf39-8d497c9dfb47" /></td>
  </tr>
</table>

### Sample outputs

**Identity Forge** — random people:

<table>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/5c6d404d-8cb8-4466-9575-21783c6f2287" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/82d0bb40-d3c6-47c9-83f1-6f33aa7e9260" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/9755ef20-0429-4d64-949f-2826a83cc2e7" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/15d61d28-d79a-4ad0-b17f-7346b83ab56c" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/00172e67-12f7-4518-b08f-663afce2a363" /></td>
  </tr>
</table>

**Archetypes** — themed looks on a random person:

<table>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/8bc9809d-c0be-4edd-b60c-cd8ac84d9f05" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/d48eddbb-97a8-4e61-ab11-de41d4ef386c" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/7ce1a556-dc01-454b-ac7e-0646815ecddc" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/a75a9f6f-3db1-4e08-b219-249a029a2aba" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/90857fdd-7d17-4e36-aa4d-15e42a1a5424" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/9fa83b75-2028-4362-b67b-4459810fd2d6" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/6a25443a-e040-44f4-8d48-33a4118ab55b" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/c0d28e5e-094b-413e-babc-d88d03fc539c" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/6526567f-c660-4be3-b426-0a7c80438405" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/9132bccc-9f3b-49f9-9968-a7510048f2f8" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/9a2acf90-ef21-4acc-9161-b132b9245130" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/33bd47f1-1789-473f-b041-4b1af0332146" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/757f60c8-8ebc-42f8-a3d8-9d2b79abae57" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/1ffecfc2-b2c7-4ff2-aa95-a998e798283a" /></td>
    <td></td>
  </tr>
</table>

**Cosplayers** — a fictional character's costume on a random (optionally cross-gender) person:

<table>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/62c88ab8-52d3-4798-a8e2-b9aa47be82c9" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/286001ec-b6ff-43aa-be11-4e8adbcc5c82" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/0661c12c-5e6f-47a9-9315-0435e3950c61" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/a88405b4-0e94-4092-886a-550b49a59c1a" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/5ebb67c2-ce9c-4099-a1a4-8fcc91dbad81" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/3ee5c9bf-1c76-4161-a6b7-f0dbfc889a78" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/1018c740-86f9-4da4-88f1-de2b8615bb53" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/0c26529d-e39e-4696-a674-39efe2681f9d" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/3d91ddf8-5a41-4ec7-995e-b6cae00628fc" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/2b0fd5c6-08e8-4a2a-bfb9-e829823d7c13" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/5eb24c4f-4812-4d3e-953a-147aec5db6d5" /></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</table>

**Creatures** — the character rendered as a non-human form:

<table>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/42802824-755a-4a7d-aebf-2b2c4c9183e2" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/32267bfd-0b15-4312-be08-9b378f7783a9" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/c4236750-a597-4680-b1a1-5a610b2b172a" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/08d138c7-c05f-436c-ba65-c4d9768f7cef" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/f1f30601-754b-4fcd-b44f-15314f0804c7" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/6b58cce8-eec8-46a8-bb8a-893a35cd7d72" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/a0ab604d-7aaa-482b-af7c-3020ba9eac38" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/de7237f7-3989-409a-939c-1cd607965aa8" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/e9b96ae3-e795-4cee-a6da-8c39789dde74" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/d4a1714d-72ec-40d1-bc01-f5be5b019d1e" /></td>
  </tr>
  <tr>
    <td><img width="200" src="https://github.com/user-attachments/assets/0eac2c2a-e93a-422d-99a6-b870a13242ae" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/41ffb934-702d-4299-8fdf-f260a3836ec2" /></td>
    <td><img width="200" src="https://github.com/user-attachments/assets/0ba4e7a2-b897-4d8b-9132-2eca3e3262f7" /></td>
    <td></td>
    <td></td>
  </tr>
</table>

---

## The nodes

| Node | What it does |
| --- | --- |
| **Identity Forge** | Lockable dropdowns in collapsible groups + the constraint engine → `prompt_text` (prose) and `prompt_json`. |
| **Archetype** | Themed presets (knight, sorceress, pirate, samurai, pop star, astronaut, surgeon, 1950s homemaker…) that set the *look* while the person randomizes. |
| **Cosplayer** | Fictional characters (Spider-Man, 2B, She-Hulk, Zelda…) as a *cosplay look* — the costume on a random, optionally cross-gender person. |
| **Creature** | Render the character as a non-human form (animal, insect, marine, reptile, bird, monster, alien, mythic, plant), across all classes or one, hybridized slot-by-slot. |
| **Modifier** | Prepend a custom descriptor to one field (`footwear: sci-fi`) or a whole group (`Clothing: weathered`). |
| **Vault Save / Load** | Save a generated character (with a thumbnail) to a local vault; recall it later as a chainable preset, with a Manage Vault gallery. |

---

## Install

Clone into `custom_nodes` and restart ComfyUI (no Python dependencies):

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/EnragedAntelope/comfyui-identity-forge
```

Or install via **ComfyUI Manager** (search *Identity Forge*).

## Quick start

1. Add **Identity Forge**, connect `prompt_text` → **CLIP Text Encode**.
2. Leave fields on `Random`, or pick a value to lock the ones you care about.
3. Queue. The seed auto-randomizes, so each run is a new character (set the seed control to
   *fixed* to reproduce one).

---

## Chaining presets

The Archetype, Cosplayer, Creature and Modifier nodes all feed Identity Forge's single
`archetype_json` socket. Instead of swapping plugs, chain them through each node's optional
`upstream` input:

```
Archetype ─▶ Cosplayer ─▶ Creature ─▶ Modifier ─(character_json)─▶ Identity Forge.archetype_json
```

- **The node closest to Identity Forge wins** where fields overlap; non-overlapping upstream
  values survive.
- Set any node to `None` and it passes its upstream through — keep every preset wired and just
  toggle which is active.

The headline combo: a Cosplayer in front of a Creature gives *Superman as an anthropomorphic
praying-mantis hybrid with a sloth's head* — the costume survives, the body becomes the creature.

---

## Must-know

- **Seed** auto-randomizes each run; set it to *fixed* to reproduce a character. Not written to the JSON.
- **Every field is `Random` (roll) / a value (lock) / `None` (omit).** Set scene fields
  (`location`, `lighting`, framing) to `None` for a character-only description to splice elsewhere.
- **`accessory_density`** — drop it to `Minimal`/`None` for clean portraits without locking fields by hand.
- **The light matches the place.** An indoor location never draws open-sky light and an outdoor one
  never draws window/ceiling/hearth light, so you won't get a spice-market stall lit by "dappled
  sunlight through forest canopy". The **location** is what stands: the light adapts to it. Lock a
  light instead (e.g. `harsh desert sun`) and the *location* re-rolls to somewhere that light can
  exist. Most locations are interiors, so random daylight is uncommon by design — set
  `location_setting: Outdoor` when you want sunny, golden-hour looks.
- **Gender & crossplay.** The *person's* gender is the Identity Forge `gender` widget (independent
  of a character's). `Any` rolls a **coherent man or woman each run**; pair it with `wardrobe: Any`
  to unlock fully mixed-gender output. Locked / archetype / cosplayer values are always respected.
- **Scope the random character.** On the Cosplayer node, `random_scope` limits the `Random — …`
  picks to one franchise/category (Anime & Manga, Marvel, DC, Star Wars, …) or to an attribute
  scope (Giant characters, Tiny characters, Non-human / colored, Masked), and combines with gender.
- **Alternate costumes.** Characters with more than one iconic look (Harley Quinn, Catwoman,
  Poison Ivy, Titania, Giganta, Diane, …) rotate between them by seed, so the same character
  yields a different signature costume each roll.
- **Masked characters** (Spider-Man, a Mandalorian helmet) suppress the randomized face/hair so
  only the mask shows; the Cosplayer `Unmask` toggle reveals the head under the suit.
- **Vault** — *Vault Save* is a terminal node used like Save Image (branch `prompt_json` in,
  optionally the image for a thumbnail; mute it to skip). *Vault Load* recalls a save as a
  `character_json` that wires into `archetype_json`.

---

## Troubleshooting

- **A `NoneType` error (or a missing/blank widget) after updating.** A node's fields are built when
  it is created, so a node on a saved graph can hold a stale widget after an update changes the
  options. **Recreate the node** - or delete and re-add it -  and the error clears. You may have to
  reselect any locked values after recreation (but it's worth it, because that means improvement!).
  
---

## Learn more

- [docs/usage.md](docs/usage.md) — controls, locking, constraints, custom options
  (`user_options.json`), the field set, and a worked example.
- [docs/cosplayer-notes.md](docs/cosplayer-notes.md) · [docs/creature-notes.md](docs/creature-notes.md)
  — per-node design notes and how to add your own characters / creatures.
- [docs/architecture.md](docs/architecture.md) — schemas and engine internals for contributors.

## Contributing characters & archetypes

Add private entries via `user_options.json` (see *Custom options* in
[docs/usage.md](docs/usage.md)) — or open an
[issue](https://github.com/EnragedAntelope/comfyui-identity-forge/issues) / PR proposing new
cosplayers, archetypes, outfit styles, creatures or fields to fold into the built-in set. For
cosplayers, a costume description (worn items only) and the franchise are enough to start; mark
`covers_face` + `mask` if the head is fully covered. The advanced flags (`covers_body`,
`covers_hair`, `bald`, `body_paint` + `skin`) also work in custom entries — see the commented
examples in [user_options.example.json](user_options.example.json).

## Development

The engine runs without ComfyUI:

```bash
python tests/validate_data.py            # data integrity
python -m unittest discover -s tests -v  # engine + integration tests
```

`js/identity_forge.js` embeds data generated from `data/fields.py` — regenerate it only if you
change the gender-divergent fields or the field set.

## License

MIT — see [LICENSE](LICENSE).
