# ComfyUI Identity Forge

**Endless, coherent characters from dropdowns — no prompt-wrangling.** Queue once
for a believable person; queue again for a brand-new one. Identity Forge turns menu
choices into clean natural-language prose (for CLIP Text Encode) plus a structured
JSON record — with a constraint engine that keeps every result sensible: no beards
on the buzz-cut, no handbag with the gym kit, no Irish ancestry rendered in ebony skin.

Lock the few traits you care about, let the rest roll. Drop in an **archetype** for
an instant costumed look on an ever-changing person, or a **cosplayer** preset to put
a fictional character's outfit on a random (optionally cross-gender) person. Set the
scene fields to `None` to get a **character-only** description you can splice into a
larger prompt.

- **Reproducible** — seed-driven, so any character you like comes back exactly.
- **Coherent by design** — a constraint engine resolves clashing traits for you.
- **Archetypes** — knight, sorceress, pirate, ninja, samurai, pop star, astronaut, surgeon… as a one-wire preset.
- **Cosplayers** — a random person cosplaying a fictional character, with crossplay, a helmet-off *Unmask* toggle, and opt-in signature props (Thor's hammer, Cap's shield).
- **Creatures** — render the character as an animal / insect / monster / alien / mythic form, *hybridized slot-by-slot* (a praying-mantis body with a sloth's head), anthropomorphic, feral or a subtle accent.
- **Modifiers** — prepend a custom descriptor to a single element (sci-fi shoes, glowing earrings, iridescent skin) without theming the whole image.
- **Character vault** — save a generated character (with a thumbnail) and recall it later; a built-in gallery browses, renames and deletes saves.
- **Chainable presets** — wire Archetype → Cosplayer → Creature → Modifier → Identity Forge so they stack instead of fighting over one socket.
- **Zero dependencies, fully offline** — no LLM, no API keys, no model downloads.
- **Extensible** — add your own dropdown options (and outfit styles) without touching the source.

| Node | What it does |
| --- | --- |
| **Identity Forge** | Lockable dropdown fields in collapsible groups + a constraint engine → `prompt_text` (prose) and `prompt_json`. |
| **Identity Forge Archetype** | Themed presets (knight, sorceress, pirate, ninja, samurai, pop star, astronaut, surgeon…) that set the *look* while the person underneath randomizes. |
| **Identity Forge Cosplayer** | Fictional characters (Spider-Man, Batman, Darth Vader, Cloud, 2B, She-Hulk, Zelda…) as a *cosplay look* — the costume on a random, optionally cross-gender person. |
| **Identity Forge Creature** | Render the character as a non-human form — animal, insect, marine, reptile, bird, monster, alien, mythic or plant — picked across all classes or scoped to one, and hybridized slot-by-slot. |
| **Identity Forge Modifier** | Prepend a custom descriptor to one field (`footwear: sci-fi`) or a whole group (`Clothing: weathered`) — without touching the main node. |
| **Identity Forge Vault Save** | Save the generated character to a local vault. Terminal node like Save Image. |
| **Identity Forge Vault Load** | Recall a saved character as a chainable `character_json` preset, with a thumbnail preview and a Manage Vault gallery. |

Built on the ComfyUI **V3 API** (`comfy_api.latest`). Category: `conditioning/character`.

---

## Showcase

**The main node** (a slice of the fields shown):

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

---

## Chaining presets (the rule that matters)

The Archetype, Cosplayer, Creature, and Modifier nodes all feed Identity Forge's single
`archetype_json` socket. Instead of swapping plugs, chain them through each node's optional
`upstream` input:

```
Archetype ─▶ Cosplayer ─▶ Creature ─▶ Modifier ─(character_json)─▶ Identity Forge.archetype_json
```

- **The node closest to Identity Forge wins** where fields overlap (downstream wins);
  non-overlapping values from upstream survive.
- Set any node in the chain to `None` and it passes its upstream through — so every preset can
  stay wired and you just toggle which one is active.

The headline combo: a Cosplayer in front of a Creature gives *Superman as an anthropomorphic
praying-mantis hybrid with a sloth's head* — the costume survives, the body becomes the creature.

---

## Must-know

- **Seed** auto-randomizes each run; set it to *fixed* to reproduce a character. It is not
  written to the JSON.
- **Every field is `Random` (randomize) / a value (lock) / `None` (omit)** — one `None` per
  field. Set scene fields (`location`, `lighting`, framing) to `None` for a character-only
  description.
- **`accessory_density`** — drop it to `Minimal`/`None` for clean portraits without locking
  fields by hand.
- **Crossplay just works.** The *person's* gender is the Identity Forge `gender` widget,
  independent of the character's; the gender gate drops anything invalid for the chosen gender.
- **Scope the random character.** On the Cosplayer node, `random_scope` limits the `Random — …`
  picks to one franchise/category (Anime & Manga, Marvel, DC, Star Wars, …) and combines with gender.
- **Masked characters** (Spider-Man, a Mandalorian helmet) suppress the randomized face/hair so
  only the mask is described; the Cosplayer `Unmask` toggle reveals the head under the suit.
- **Vault** — *Vault Save* is a terminal node used like Save Image (branch `prompt_json` in,
  optionally the image for a thumbnail; mute it to skip). *Vault Load* recalls a save as a
  `character_json` that wires into `archetype_json`, with a Manage Vault gallery.
- **Offline, zero dependencies** — no LLM, no API keys, no downloads.

---

## Troubleshooting

- **A `NoneType` error (or a missing/blank widget) after updating.** The node's fields and
  options are built when the node is created, so an existing node on a saved graph can hold a
  stale widget after an update changes the available options. **Reload the node** — delete it
  and drop a fresh Identity Forge in, or reload the workflow (browser refresh) — and the error
  clears. Your locked values for fields that still exist are preserved; only removed/renamed
  options need re-picking.

---

## Learn more

- [docs/usage.md](docs/usage.md) — controls, how locking works, constraints, custom options
  (`user_options.json`), the field set, and a worked example.
- [docs/cosplayer-notes.md](docs/cosplayer-notes.md) · [docs/creature-notes.md](docs/creature-notes.md)
  — per-node design notes and how to add your own characters / creatures.
- [docs/architecture.md](docs/architecture.md) — schemas and engine internals for contributors.

---

## Contributing characters & archetypes

You can add private or instant entries via `user_options.json` (see *Custom options* in
[docs/usage.md](docs/usage.md)) — but you don't have to maintain your own list forever.
**Suggestions, additions, and bug reports are welcome.** Open an
[issue](https://github.com/EnragedAntelope/comfyui-identity-forge/issues) (or a PR) proposing new
cosplayers, archetypes, outfit styles, creatures, or fields and they can be folded into the
built-in set so everyone gets them on the next update. For cosplayers, a costume description
(worn items only) and the franchise are enough to start; mark `covers_face` + `mask` if the head
is fully covered, and state baldness in the costume rather than locking a hair length.

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
