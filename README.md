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

**Optionally chain nodes to the main Identity Forge node. Pro Tip: Closest node "wins" if there is a conflict:**
<img width="480" alt="Sample Node Chain" src="https://github.com/user-attachments/assets/82d80ecd-b25a-475a-a4e0-ae0d6116a744" />

**Sample archetypes, cosplay characters, creatures:**

<img width="320" alt="Archetypes" src="https://github.com/user-attachments/assets/c1871f28-f52d-42b6-8ca6-6dff2d1793f8" />
<img width="320" alt="Cosplay Characters" src="https://github.com/user-attachments/assets/256d81e2-ed75-47cd-80f5-e8e7e2837a91" />
<img width="320" alt="Creatures" src="https://github.com/user-attachments/assets/65b0cbfa-6e93-47de-bf39-8d497c9dfb47" />


**Sample outputs**:
Identity Forge:
<img width="1728" height="2304" alt="krea2unstable_00018_" src="https://github.com/user-attachments/assets/5c6d404d-8cb8-4466-9575-21783c6f2287" />
<img width="1728" height="2304" alt="krea2turbo_ID_00010_" src="https://github.com/user-attachments/assets/82d0bb40-d3c6-47c9-83f1-6f33aa7e9260" />
<img width="1728" height="2304" alt="krea2turbo_ID_00009_" src="https://github.com/user-attachments/assets/9755ef20-0429-4d64-949f-2826a83cc2e7" />
<img width="1728" height="2304" alt="krea2turbo_04470_" src="https://github.com/user-attachments/assets/15d61d28-d79a-4ad0-b17f-7346b83ab56c" />
<img width="1728" height="2304" alt="krea2turbo_04440_" src="https://github.com/user-attachments/assets/00172e67-12f7-4518-b08f-663afce2a363" />


Archetypes:
<img width="1728" height="2304" alt="krea2turbo_04279_" src="https://github.com/user-attachments/assets/8bc9809d-c0be-4edd-b60c-cd8ac84d9f05" />
<img width="1728" height="2304" alt="krea2turbo_04178_" src="https://github.com/user-attachments/assets/d48eddbb-97a8-4e61-ab11-de41d4ef386c" />
<img width="1728" height="2304" alt="krea2turbo_04155_" src="https://github.com/user-attachments/assets/7ce1a556-dc01-454b-ac7e-0646815ecddc" />
<img width="1728" height="2304" alt="krea2turbo_00024_" src="https://github.com/user-attachments/assets/a75a9f6f-3db1-4e08-b219-249a029a2aba" />
<img width="1728" height="2304" alt="krea2turbo_00023_" src="https://github.com/user-attachments/assets/90857fdd-7d17-4e36-aa4d-15e42a1a5424" />
<img width="1728" height="2304" alt="krea2turbo_00020_" src="https://github.com/user-attachments/assets/9fa83b75-2028-4362-b67b-4459810fd2d6" />
<img width="1728" height="2304" alt="krea2unstable_00010_" src="https://github.com/user-attachments/assets/6a25443a-e040-44f4-8d48-33a4118ab55b" />
<img width="1728" height="2304" alt="krea2unstable_00009_" src="https://github.com/user-attachments/assets/c0d28e5e-094b-413e-babc-d88d03fc539c" />
<img width="1728" height="2304" alt="krea2turbo_04469_" src="https://github.com/user-attachments/assets/6526567f-c660-4be3-b426-0a7c80438405" />
<img width="1728" height="2304" alt="krea2turbo_04467_" src="https://github.com/user-attachments/assets/9132bccc-9f3b-49f9-9968-a7510048f2f8" />
<img width="1728" height="2304" alt="krea2turbo_04465_" src="https://github.com/user-attachments/assets/9a2acf90-ef21-4acc-9161-b132b9245130" />
<img width="1728" height="2304" alt="krea2turbo_04462_" src="https://github.com/user-attachments/assets/33bd47f1-1789-473f-b041-4b1af0332146" />
<img width="1728" height="2304" alt="krea2turbo_04436_" src="https://github.com/user-attachments/assets/757f60c8-8ebc-42f8-a3d8-9d2b79abae57" />
<img width="1728" height="2304" alt="krea2turbo_04280_" src="https://github.com/user-attachments/assets/1ffecfc2-b2c7-4ff2-aa95-a998e798283a" />

Cosplayers:
<img width="1728" height="2304" alt="krea2turbo_03474_" src="https://github.com/user-attachments/assets/62c88ab8-52d3-4798-a8e2-b9aa47be82c9" />
<img width="1728" height="2304" alt="krea2turbo_03268_" src="https://github.com/user-attachments/assets/286001ec-b6ff-43aa-be11-4e8adbcc5c82" />
<img width="1728" height="2304" alt="krea2turbo_00311_" src="https://github.com/user-attachments/assets/0661c12c-5e6f-47a9-9315-0435e3950c61" />
<img width="1728" height="2304" alt="krea2turbo_00269_" src="https://github.com/user-attachments/assets/a88405b4-0e94-4092-886a-550b49a59c1a" />
<img width="1728" height="2304" alt="krea2turbo_00250_" src="https://github.com/user-attachments/assets/5ebb67c2-ce9c-4099-a1a4-8fcc91dbad81" />
<img width="1728" height="2304" alt="krea2turbo_00202_" src="https://github.com/user-attachments/assets/3ee5c9bf-1c76-4161-a6b7-f0dbfc889a78" />
<img width="1728" height="2304" alt="krea2turbo_cosp_00018_" src="https://github.com/user-attachments/assets/1018c740-86f9-4da4-88f1-de2b8615bb53" />
<img width="1728" height="2304" alt="krea2turbo_04430_" src="https://github.com/user-attachments/assets/0c26529d-e39e-4696-a674-39efe2681f9d" />
<img width="1728" height="2304" alt="krea2turbo_04328_" src="https://github.com/user-attachments/assets/3d91ddf8-5a41-4ec7-995e-b6cae00628fc" />
<img width="1728" height="2304" alt="krea2turbo_04323_" src="https://github.com/user-attachments/assets/2b0fd5c6-08e8-4a2a-bfb9-e829823d7c13" />
<img width="1728" height="2304" alt="krea2turbo_03938_" src="https://github.com/user-attachments/assets/5eb24c4f-4812-4d3e-953a-147aec5db6d5" />

Creatures:
<img width="1728" height="2304" alt="krea2turbo_00019_" src="https://github.com/user-attachments/assets/42802824-755a-4a7d-aebf-2b2c4c9183e2" />
<img width="1728" height="2304" alt="krea2turbo_00017_" src="https://github.com/user-attachments/assets/32267bfd-0b15-4312-be08-9b378f7783a9" />
<img width="1728" height="2304" alt="krea2turbo_00015_" src="https://github.com/user-attachments/assets/c4236750-a597-4680-b1a1-5a610b2b172a" />
<img width="1728" height="2304" alt="krea2turbo_00011_" src="https://github.com/user-attachments/assets/08d138c7-c05f-436c-ba65-c4d9768f7cef" />
<img width="1728" height="2304" alt="krea2turbo_04387_" src="https://github.com/user-attachments/assets/f1f30601-754b-4fcd-b44f-15314f0804c7" />
<img width="1728" height="2304" alt="krea2turbo_04375_" src="https://github.com/user-attachments/assets/6b58cce8-eec8-46a8-bb8a-893a35cd7d72" />
<img width="1728" height="2304" alt="krea2turbo_04359_" src="https://github.com/user-attachments/assets/a0ab604d-7aaa-482b-af7c-3020ba9eac38" />
<img width="1728" height="2304" alt="krea2turbo_04226_" src="https://github.com/user-attachments/assets/de7237f7-3989-409a-939c-1cd607965aa8" />
<img width="1728" height="2304" alt="krea2turbo_04120_" src="https://github.com/user-attachments/assets/e9b96ae3-e795-4cee-a6da-8c39789dde74" />
<img width="1728" height="2304" alt="krea2turbo_04012_" src="https://github.com/user-attachments/assets/d4a1714d-72ec-40d1-bc01-f5be5b019d1e" />
<img width="1728" height="2304" alt="krea2turbo_03657_" src="https://github.com/user-attachments/assets/0eac2c2a-e93a-422d-99a6-b870a13242ae" />
<img width="1728" height="2304" alt="krea2turbo_03528_" src="https://github.com/user-attachments/assets/41ffb934-702d-4299-8fdf-f260a3836ec2" />
<img width="1728" height="2304" alt="krea2turbo_02228_" src="https://github.com/user-attachments/assets/0ba4e7a2-b897-4d8b-9132-2eca3e3262f7" />

---

## Install

Clone into `custom_nodes` and restart ComfyUI (no Python dependencies):

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/EnragedAntelope/comfyui-identity-forge
```

Or install via **ComfyUI Manager** (search *Identity Forge*).

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
