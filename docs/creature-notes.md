# Creature node — design notes & known limitations

Reference notes for the **Identity Forge Creature** node. These are intentional
trade-offs, not bugs — recorded so behaviour is predictable and future changes are
informed.

## How it works

The Creature node emits a grouped-JSON document with a **`Species & Anatomy`** group
(a `{slot: prose}` map) plus a `_meta` block carrying the `form` and the
`suppress_groups` / `suppress_fields` lists. It wires into Identity Forge's
`archetype_json` socket like the other preset nodes. Identity Forge renders the
anatomy through a dedicated **species prose path** and **suppresses** the human fields
the creature replaces — generalizing the cosplayer `covers_face` mechanism.

A creature is stored as anatomy **slots**: `head`, `eyes`, `integument` (skin / fur /
scales / chitin / shell), and optional `arms`, `hands`, `legs_feet`, `tail`, `wings`,
`extras`. Picking one creature fills every slot it defines; each slot can also be
overridden to **Follow base / Random / a specific creature**, so a praying-mantis body
with a sloth's head is `creature = praying mantis` + `head = sloth`.

### Only one vs mix everything

The **`creature`** dropdown is the whole scoping control:

- `None` — node off (emits `{}`, passes its upstream through).
- `Random — any` — pick across **every** class.
- `Random — <class>` — stay within one class (only a monster / only an insect / only
  an alien / …). The nine classes are Mammals, Birds, Reptiles & Amphibians, Insects
  & Arachnids, Marine Life, Monsters, Aliens, Mythic & Fantasy, Plant & Fungal.
- a specific creature name.

### Forms & suppression

`form` decides how much of the human is replaced:

- **Anthropomorphic** (default) — humanoid silhouette, so a wired costume still fits.
  Drops the human **Demographics**; a creature head additionally hides **Face / Hair /
  Makeup**, an integument hides the **skin** fields. Build / height / proportions stay.
- **Feral / full creature** — a true beast. Also drops **Clothing / Makeup / Jewellery**
  and the humanoid proportions (bust / waist / hips / shoulders / neck / posture); build,
  height and fitness remain.
- **Subtle hybrid** — keeps the human and *adds* what humans lack (creature limbs,
  wings, tail, extras). The conflicting replacers (head, eyes, integument) are dropped
  so the result is never a human face described next to a creature face. Suppresses
  nothing.
- **Random** — rolls one of the three with the seed.

### Detail & free text

`palette` recolours the integument (default is the source creature's own colour);
`integument_finish` adds a surface (matte / glossy / iridescent / slimy /
bioluminescent…); `size_scale` scales the subject (tiny … towering). The
**`more_features`** box takes `slot: phrase` lines (override a slot verbatim) or bare
lines (extra features), for unlimited detail without more widgets.

### Compact UI

Only `creature` / `form` / `seed` show by default. The eight hybrid-slot dropdowns,
the detail dropdowns and the free-text box live in **collapsed** sections (the same
zero-height collapse the main node uses for its 70+ fields), so the node stays small.

### Chaining presets

The node has an optional **`upstream`** input, so it chains with the others. The node
closest to Identity Forge wins on overlap. The headline combo is **Cosplayer →
Creature → Identity Forge**: the costume (a different JSON group) survives, the body
becomes the creature, and the prose reads *Cosplaying as Superman: an anthropomorphic
praying-mantis hybrid with a sloth's head, …*. Order barely matters — costume and
anatomy live in different groups, and the suppression flags simply union (a masked
cosplayer + an integument creature drop both the face and the skin).

## Known limitations

1. **Slot text is not validated against the human fields.** The species group has its
   own prose path, so slot phrases are free-form (this is what frees non-humans from
   the human option pools). `tests/validate_data.py` checks structure, not wording.

2. **Hybrid coherence is the author's job.** Nothing stops a chimera that reads oddly
   (a jellyfish head on crab legs); the slots are combined as given. That freedom is
   the point.

3. **Render quality varies by model.** Anthropomorphic and hybrid forms are harder for
   some checkpoints than realistic humans. Lean on a checkpoint that knows the
   creature, and use `form`/`palette` to steer.

4. **Feral form vs a wired costume.** Feral drops Clothing, so a costume wired in front
   of a feral creature is intentionally discarded (a feral dragon is not wearing a
   suit). Use **Anthropomorphic** to keep the costume.

5. **Subtle drops the head/eyes/integument you may have picked.** By design — Subtle is
   a light accent pass. Use **Anthropomorphic** when you want a creature head or skin.

6. **One preset socket on Identity Forge.** As with the other presets, chain through
   the `upstream` inputs rather than competing for the single `archetype_json` socket.

## Extending the creature set

Add your own without editing the source (survives `git pull`) via the `creatures`
section of `user_options.json` — see `user_options.example.json`. Required keys:
`class` (one of the nine), `palette`, and the core slots `head` / `eyes` /
`integument`; the limb / tail / wing / extras slots are optional. Leave the colour
**out** of `integument` (the `palette` is prepended onto it, so a recolour stays
clean). Keep slot text plain ASCII (no em dashes / smart quotes) so text-to-image
tokenizers don't mangle it. Run `python tests/validate_data.py` to check the
structure.

Contributions are welcome, too: open an issue or PR suggesting a creature for the
built-in set.
