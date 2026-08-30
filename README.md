# ComfyUI Identity Forge

**Create believable, coherent characters from dropdowns — no prompt engineering required.**

Identity Forge turns menu choices into clean, natural-language character descriptions that feed directly into your image model. Queue once and get a fully-realized person. Queue again and meet someone completely new.

Browse the galleries: [cosplay](https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/) ·
[archetypes](https://enragedantelope.github.io/comfyui-identity-forge/gallery/archetypes/) ·
[creatures](https://enragedantelope.github.io/comfyui-identity-forge/gallery/creatures/) — every roster
entry with a sample render, searchable by name and franchise, each linked to the exact workflow it was made with.

## Why Identity Forge?

**The problem:** Writing good character prompts is hard. You need to describe age, ethnicity, body type, face, hair, makeup, clothing, accessories, pose, lighting, location — and make sure none of it contradicts (a beard on a buzz cut, open-sky lighting indoors, a handbag with gym kit). The constraint engine handles all of this automatically.

**The solution:** Every field is `Random` (roll it), a specific value (lock it), or `None` (omit it). Lock the few traits you care about, let the rest roll, and get a result that's coherent, reproducible (seed-driven), and yours to steer.

## What makes this different

### Character creation that actually works

Most character generators emit a name and hope the model recognizes it. Identity Forge builds every trait itself — demographics through lighting — composed into natural-language prose any image model can render, with skin tone kept plausible for the chosen ancestry.

### Cosplay nodes that understand the characters

The Cosplayer node is where Identity Forge really shines. Most character wildcards emit a name — `Chun-Li` — and hope for the best. Every character here carries a **hand-written, canon-checked description of the costume**: garments, colours, masks, markings, signature props.

Ask a plain wildcard for Chun-Li and your prompt says `Chun-Li`. Ask this Cosplayer node and you get: *the blue qipao with gold trim, brown tights, white cross-laced boots, and spiked bracelets.* The look renders even on checkpoints that have never heard of the character.

**Find one fast:** open the in-node picker to browse and search the whole roster without leaving the node — trait facets (Giant, Masked, Mascot/full-suit, Beast, franchise) and optional thumbnail previews.

**Characters from every major franchise:** Marvel, DC, Star Wars, anime, video games, fantasy, sci-fi, horror. Each one with multiple costume variants where applicable (Harley Quinn's three iconic looks, Catwoman's different suits, etc.). Characters rotate between variants by seed, so the same name yields a different signature costume each roll.

**Crossplay built in:** Set the person's gender independently of the character. The costume adapts. A female Spider-Man gets the suit resized and reshaped; a male Wonder Woman gets the armor reconfigured. The constraint engine handles the anatomy.

**Named beasts render as the animal, not as someone dressed as it:** Appa, Toothless, Catbus, a bantha, Jabba — characters nobody can physically be inside — render from their own anatomy, with the human demographics, proportions, clothing and jewellery dropped. Full mascot suits (Pikachu, Godzilla) stay costumes on a randomized wearer.

### Turnaround: one character, every angle, one queue

The Turnaround node is a reference-sheet builder: wire Identity Forge's `prompt_json` into it and one queue
emits front / three-quarter / profile / back views of the same **resolved** character — no re-rolling
between views, unlike an auto-incrementing index widget where an upstream node left on `randomize` swaps
the person on every frame. Full controls and the back-view face-omission behavior: [docs/usage.md](docs/usage.md#turnaround-views).

### Additional layers

- **Archetype:** Themed looks (knight, sorceress, astronaut, surgeon, 1950s homemaker…) that set the *look* while the person randomizes.
- **Creature:** Turn the person into an animal, monster, or alien. Hybridized slot-by-slot (head, eyes, integument, arms, hands, legs, tail, wings).
- **Modifier:** Prepend a custom descriptor to one field (`footwear: sci-fi`) or a whole group (`Clothing: weathered`).
- **Vault Save / Load:** Save a generated character with a thumbnail; recall it later as a chainable preset.

All preset nodes stack via an `upstream` input — chain them through each other and keep them all wired. Set any node to `None` and it passes through.

---

## Showcase

Chain the preset nodes into the main Identity Forge node — the node **closest to Identity Forge
wins** any conflict:

<img width="560" alt="Sample node chain" src="https://github.com/user-attachments/assets/82d80ecd-b25a-475a-a4e0-ae0d6116a744" />

A taste of archetypes, cosplay characters and creatures — generated with the Krea2 T2I model on
randomized identities, so your own results will vary:

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
</table>

---

## The nodes

| Node | What it does |
| --- | --- |
| **Identity Forge** | Lockable dropdowns in collapsible groups + the constraint engine → `prompt_text` (prose) and `prompt_json`. |
| **Archetype** | Themed presets (knight, sorceress, pirate, samurai, pop star, astronaut, surgeon, 1950s homemaker…) that set the *look* while the person randomizes. |
| **Cosplayer** | Fictional characters (Spider-Man, 2B, She-Hulk, Zelda…) as a *cosplay look* — the costume on a random, optionally cross-gender person. An in-node picker browses and searches the whole roster with trait facets and thumbnails. |
| **Creature** | Render the character as a non-human form (animal, insect, marine, reptile, bird, monster, alien, mythic, plant), across all classes or one, hybridized slot-by-slot. Generic species only — a *named* fictional beast (Appa, Toothless) is a Cosplayer entry. |
| **Modifier** | Prepend a custom descriptor to one field (`footwear: sci-fi`) or a whole group (`Clothing: weathered`). |
| **Vault Save / Load** | Save a generated character (with a thumbnail) to a local vault; recall it later as a chainable preset, with a Manage Vault gallery. |
| **Turnaround** | A reference-sheet builder: wire Identity Forge's `prompt_json` in and it emits front / three-quarter / profile / back as a **list**, so one queue renders the whole set of the same person. It only moves the camera - the character and the scene stay configured on Identity Forge. |

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

## Using with Stylebook

[Stylebook](https://github.com/EnragedAntelope/comfyui-stylebook) describes the
*rendering*: medium, lighting, colour grade, era, finish and mood. Identity Forge
describes the *subject* — who or what is in the picture, and where the camera is:
framing, shot type, composition, pose, expression and eye contact. Connect Identity
Forge's `prose` output into Stylebook's `user_prompt` and chain Stylebook downstream.

Stylebook owns lighting and mood, so set both to `None` here when pairing the two packs
— otherwise you get two descriptions competing for the same axis. See Stylebook's
[`examples/stylebook_with_identity_forge.json`](https://github.com/EnragedAntelope/comfyui-stylebook/blob/main/examples/stylebook_with_identity_forge.json)
for a ready-to-run workflow.

---

## Must-know

- **Seed** auto-randomizes each run; set it to *fixed* to reproduce a character. Not written to the JSON.
- **Every field is `Random` (roll) / a value (lock) / `None` (omit).** Set scene fields
  (`location`, `lighting`, framing) to `None` for a character-only description to splice elsewhere.
- **`accessory_density`** — drop it to `Minimal`/`None` for clean portraits without locking fields by hand.
- **`size_scale`** — force an unrealistic body scale on an ordinary person: a doll-sized office worker, a fifty-foot commuter. It is **manual only**; `Auto` is the default and is never chosen at random, so it can't affect normal output. Picking a tier replaces the height description in the opening sentence and overrides a wired character's own scale, so you can make anyone giant or tiny.
- **The scene shows the scale.** A giant only *looks* giant if the frame has something to compare against, so a giant tier — or a canonically giant character like Godzilla or the Iron Giant — moves the shot outdoors and picks a wide, low or establishing framing, stops the build being described as petite, and stops the composition cropping the surroundings away. Lock `location`, `shot_type` or `composition` yourself and your choice wins as always. Tiny characters get the lighter version: only the framings too wide to resolve them are dropped.
- **The light matches the place.** Indoor locations never draw open-sky light and outdoor ones never draw window or hearth light, and a light naming a physical fixture — a hearth, a television, a stained-glass window, a stage rig — only appears where that fixture exists. The **location** stands and the light adapts; lock a light instead and the location re-rolls to somewhere it can exist. Most locations are interiors, so set `location_setting: Outdoor` when you want sunny, golden-hour looks. The pool includes named world landmarks (the Eiffel Tower plaza, Shibuya Crossing, Uluru, the Cliffs of Moher) alongside everyday places.
- **The outfit is built, not just picked.** `outfit_style` chooses a garment set, then `clothing_color`, `clothing_pattern` and `footwear` are composed onto it — "a jewel-toned satin slip gown with delicate straps, in strappy heels". Locking any of them changes the outfit, and the shoes are kept plausible for the style (no slippers with a business suit). A garment that names its own colour or shoes keeps them and the matching field steps aside. A costume from the Cosplayer or Archetype node is a complete look and overrides all of this.
- **Nothing is worn twice.** If a costume or outfit already names a necklace, earrings, a ring, a
  bangle, a bag or a hat, the randomizer does not add a second one.
- **The pose fits the body.** Poses that reach for something the subject does not have are never
  drawn: hair to run a hand through under a helmet, pockets on a mascot suit, a *free hand* when
  a signature prop is switched on (no more "hands in pockets, holding Mjolnir"), or a seat to
  perch on when the subject is fifty feet tall outdoors. Lock a pose and your choice wins.
- **A mask hides the face — unless you say otherwise.** A full-mask character (Spider-Man, a
  Mandalorian helmet) drops the randomized face, hair, makeup and expression so nothing
  contradicts it; lock any of those widgets yourself and it renders anyway. The Cosplayer
  `Unmask` toggle reveals the head under the suit.
- **Gender & crossplay.** The person's `gender` is independent of any character's — pair `Any`
  with `wardrobe: Any` for fully mixed-gender output; locked / preset values always win. Full
  mechanics: [docs/usage.md](docs/usage.md#controls).
- **Scope and filter the random character.** On the Cosplayer node, `random_scope` narrows
  `Random — …` picks to an attribute (Giant, Masked, Mascot/full-suit, Beast…), a category, or a
  franchise; `random_pool` layers a positive filter — *People only* or *Mascot suits and beasts
  only* — on top of it. Both combine with gender (scope/pool win; gender relaxes to fill an empty
  combo). Full mechanics and pool values:
  [docs/cosplayer-notes.md](docs/cosplayer-notes.md#filtering-the-pool-random_pool-110).
- **Alternate costumes.** Characters with more than one iconic look (Harley Quinn, Catwoman,
  Poison Ivy, …) rotate between them by seed, so the same character yields a different signature
  costume each roll.
- **Non-human skin colour skips ethnicity too.** When a character's colour covers the whole
  body (She-Hulk's green, Lobo's chalk-white), the wearer's ethnicity is dropped along with the
  human skin tone — naming one only fought the colour and left the face rendering as an
  ordinary human above a coloured body.
- **Fully-encased cosplays skip ethnicity.** With no visible skin or face left (Iron Giant, a
  droid), mentioning the cosplayer's ethnicity only risked nudging the render toward a stray human
  trait. Face-visible cosplays still describe the person underneath as usual.
- **Vault** — *Vault Save* is a terminal node used like Save Image (branch `prompt_json` in,
  optionally the image for a thumbnail; mute it to skip). *Vault Load* recalls a save as a
  `character_json` that wires into `archetype_json`.

---

## Troubleshooting

- **A `NoneType` error (or a missing/blank widget) after updating.** A node's fields are built when
  it is created, so a node on a saved graph can hold a stale widget after an update changes the
  options. Right-click the node and choose **Fix node (recreate)** and the error clears — every
  widget value and every link is preserved (this pack ships its own working recreate; ComfyUI-
  Manager's own version of that menu entry can fail on the current frontend — see
  [docs/architecture.md](docs/architecture.md#a-working-fix-node-recreate)).
- **Background lettering (signage, a costume's printed text, tattoo script) shows up more
  than you'd like.** The pack authors canonical text where a character's design calls for
  it and emits no negative prompt of its own, so if you'd rather not see incidental
  background lettering, add `text, signage, watermark` to your own negative prompt.

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
python tests/validate_data.py                 # data integrity
python -m unittest discover -s tests -t . -v  # engine + integration tests
```

`js/identity_forge.js` embeds data generated from `data/fields.py` by
`scripts/generate_js_data.py` — rerun it (and commit the result) after changing the field set
or the gender-divergent pools; CI's `--check` catches a stale commit.

A jsdom suite exercises the real, unmodified frontend files outside a browser (wiring,
collapse/expand, gender pool swaps, the vault dialog, "Fix node (recreate)") — see
[docs/architecture.md](docs/architecture.md) for what it does and doesn't catch.

```bash
npm ci
npm run test:frontend
```

## License

MIT — see [LICENSE](LICENSE).
