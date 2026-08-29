# Cosplayer node — design notes & known limitations

Reference notes for the **Identity Forge Cosplayer** node. These are intentional
trade-offs, not bugs — recorded so behaviour is predictable and future changes
are informed.

## How it works

The Cosplayer node emits the same grouped-JSON document the Archetype node does
and wires into Identity Forge's `archetype_json` socket. A character is stored as
a **costume** (worn items only) plus a small **signature** look (hair, eyes) and
an optional **physique** (body/skin/height). Identity Forge randomizes everything
else, so each run is a different person wearing the same costume.

- **Costume only** (default): costume + signature; body, face, ethnicity randomize.
- **Full character**: also locks the physique for a faithful look.

An entry may set **`covers_face: True`** when the head is fully masked/helmeted
(Spider-Man, a Mandalorian helmet, a ninja hood, a featureless chrome head). The
head covering is stored in a separate **`mask`** string, kept *out* of `costume`.
The Cosplayer node forwards the mask beside `covers_face` in its `_meta` (since
0.90.0 — it is *not* glued onto the costume), and IdentityForge voices it as its
own sentence ahead of the clothing; IdentityForge then drops the randomized
**Face / Hair / Makeup** fields (plus earrings/piercings) from both the prose and
JSON — so a random face never gets described fighting the mask. Leave both off
whenever the face is visible (an open cowl, a domino mask, a body-painted but
visible face like Hulk).

The node's **`mask`** widget controls this per render: **Default** keeps the mask
on, while **Unmask (show face)** drops the mask *and* clears `covers_face`,
so the randomized head/hair shows under the suit — a helmet-off look (Tony Stark in
the Iron Man armor). It is a no-op for face-visible characters. Keeping the head
covering in its own field is what lets it be removed cleanly, with no stray
"faceplate" reference stranded in the costume prose.

### An unusual body: `anatomy_note`

A count or a body plan buried in the `He wears …` garment list does not reach the
render — measured on Dexter Jettster, who stated "four arms" three times inside one
sentence and still came back with two. What fixes it is a sentence that renders
**before** the clothing, and until 0.97.0 the only one a non-feral entry had was
`mask`. Four multi-armed entries have no mask, so they could not be fixed at all.

**`anatomy_note`** is that sentence, decoupled from the head: one optional string,
voiced as its own `He has …` immediately ahead of the mask sentence. Use it for a
limb or part count, or a body plan the costume cannot carry:

```python
"anatomy_note": "a four-armed body: two pairs of arms, an upper pair at the "
                "shoulders and a second pair set lower on the ribs, four arms in total",
```

Four rules:

- **State the count as a word, and say it plainly** — "four arms in total". Making the
  model do arithmetic ("a second pair below the first") does not carry.
- **It describes the body, never the clothes.** Garments belong in `costume`;
  `validate_data.py` rejects a garment noun here.
- **Lowercase, unpadded, no trailing period** — the engine sentences it.
- **Not on a feral entry.** Those use the per-slot `anatomy` map instead (below), and
  carrying both would describe the same body twice.

Unmasking does not clear it — it is not part of the head. A *downstream* node that
supplies its own costume does drop it, like every other costume-derived `_meta` key.

### Signature props

Costumes stay **worn, not held** — but a character with a *truly iconic* held prop
may carry it in an optional **`prop`** string (Thor's hammer, Captain America's
shield, Link's Master Sword). The node's **`props`** widget is **off by default**;
**Include signature prop** emits the prop as the hidden `held_item` field, voiced
downstream as *holding …*. It is a no-op for characters without a `prop`. The prop
is described richly, like a costume (shape, colours, materials, markings), and lives
*outside* `costume` so the toggle can add or drop it cleanly. It is opt-in because
most characters have no signature prop and because held objects can stress hand
rendering in some text-to-image models.

### Named beasts (`body_plan`)

Some characters are not a person in a costume and cannot be: a bantha is a quadruped,
Jabba is a legless slug, Appa has six legs. Rendering them through the mask-and-costume
idiom produced *"a 33-year-old Singaporean man ... He has a simple band, a cuff ... He
**wears** a massive body of thick shaggy brown fur standing on four sturdy legs."*

Such an entry sets **`body_plan: "feral"`**. The node then emits the Creature node's
`Species & Anatomy` payload instead of a costume — `mask` becomes the head, `costume`
becomes the integument, and an optional `anatomy` map fills the rest — so IdentityForge
renders it through the species path and drops the human demographics, proportions,
clothing, jewellery, skin tone and ethnicity. The prose leads with the character name
apposed to the species rather than *"Cosplaying as"*, because that framing pushes a
text-to-image model back toward a human in a suit:

> Appa (Avatar: The Last Airbender), a six-legged flying sky bison with a plus size
> build and enormous, over twenty feet long from nose to tail. He has a broad
> flat-fronted bison head ... and a single wide brown arrow marking that runs from
> between the horns down the centre of the forehead to the nose ...

The **`mask`** widget is a no-op on these entries (there is no person underneath to
reveal), and `physique` applies in **both** look levels for the same reason. **Full
mascot suits are not feral** — Pikachu, Godzilla, Rancor and Wampa are all shapes a
person fits inside, and they keep the settled `covers_face` + `covers_body` + `mask`
idiom. The dividing question is *"could one person be inside this?"*; the schema and
the authoring rules are in
[architecture.md → "Writing a feral entry"](architecture.md).

### Chaining presets

Both preset nodes expose an optional **`upstream`** input, so Archetype and
Cosplayer nodes chain into one wire (`Archetype → Cosplayer → Identity Forge`)
instead of competing for the single socket. Documents are deep-merged with the
**downstream** node (closest to Identity Forge) winning on overlap, including
`_meta`; non-overlapping upstream values survive. A node set to `None` emits `{}`,
which passes its upstream through unchanged — so both presets can stay wired and
you just toggle which one is active.

### Scoping the Random picks

The **`random_scope`** widget limits the `Random — any / female / male` picks. It offers
three families, in this order:

1. **Attribute scopes** — Giant characters, Tiny characters, Non-human / colored, Masked,
   Mascot / full-suit, Beast / non-humanoid. Filtered by a predicate over the entry
   (`_SPECIAL_SCOPES` in the node), not by franchise. *Mascot / full-suit* is derived from
   `covers_body and covers_face` (`_scope_is_mascot`) — a person inside a full creature suit
   (Pikachu, the TMNT, Godzilla, Moogle, Teemo), previously findable only by luck.
   *Beast / non-humanoid* (0.95.0) is derived from `body_plan == "feral"`
   (`_scope_is_feral`) — the animal itself rather than someone dressed as it (Appa,
   Toothless, Catbus, Bantha).
2. **Broad categories** — Anime & Manga, Marvel, DC, Star Wars, Disney, Video Games,
   Fantasy & Literature, Movies & TV, Comics & Cartoons.
3. **Single franchises** — `Franchise: Pokemon`, `Franchise: Final Fantasy`, … Derived at
   import from the roster for every franchise with at least `_FRANCHISE_SCOPE_MINIMUM` (8)
   characters, minus the three whose name is already a category (Marvel, DC, Star Wars).
   The threshold matters: 135 of the 263 franchises are singletons and would each return
   one fixed character forever, which is why the whole franchise list is *not* exposed.
   Because it is derived, `user_options.json` additions count toward the threshold and the
   list self-maintains as the roster grows.

Any scope **combines** with the gender scope — `Random — female` + `Marvel` draws a random
female Marvel character — and is ignored when a specific character is chosen; `Any`
(default) applies no limit. The first time you use a `(character, scope, pool)` combination
the console prints how many characters are in scope, so a small pool that repeats across
seeds is legible rather than looking broken. If a combination is empty it falls back to the
full gender pool and says so loudly. Each franchise's category lives in `_FRANCHISE_CATEGORY`
in `data/cosplayers.py`; an unmapped franchise falls back to a default so a new entry still
scopes sensibly.

### Filtering the pool: `random_pool` (1.1.0)

**`random_pool`** is a *positive attribute filter* over the same Random draw, and composes
with `random_scope` rather than replacing it — `random_scope` stays single-select, so
"Franchise: Marvel" + "People only" stays reachable as scope + pool together. Three values:
`All characters` (default, no filter), `People only — no mascot suits or beasts`, and
`Mascot suits and beasts only` (the exact complement of "People only" over any fixed scope).
It reuses `_scope_is_mascot` / `_scope_is_feral` — the same predicates the "Mascot / full-suit"
and "Beast / non-humanoid" scopes use — so it self-maintains as the roster grows and needs no
new detection logic. Only the source gender is ever relaxed to fill an empty (gender, scope,
pool) combo; scope and pool are both deliberate, visible choices and are never silently
dropped.

## Known limitations

1. **One preset input on Identity Forge.** Identity Forge still has a single
   `archetype_json` socket, but preset nodes now chain through their `upstream`
   input (see *Chaining presets* above), so you no longer have to unplug one to use
   the other. Combining an Archetype with a Cosplayer is allowed but unusual; the
   downstream node wins on overlap.

2. **`Any` gender follows the character.** With a cosplayer connected and the
   Identity Forge `gender` widget on `Any`, the person defaults to the *character's*
   gender. Crossplay requires explicitly setting `gender` to `Male`/`Female`. This
   mirrors how archetypes behave.

3. **Full-character coherence is soft, not exact.** `fitness_level` still
   randomizes alongside a locked physique, but since 0.46 exclusion rules cull
   the outright contradictions (a soft-curved / plus-size build never rolls
   `muscular`; an `athletic`/`toned`/`fit` build never rolls `sedentary`).
   Mid-range pairings stay free on purpose — only extremes are constrained,
   and explicit locks on both fields still win (warn + keep).

4. **Hair under partial headpieces.** For characters whose head is *partly* covered
   (montrals, a circlet, an open cowl) but whose face shows, hair still randomizes
   underneath in Costume-only mode. Give the entry a `signature` hair value to tame
   it, or — for a *fully* masked head — set `covers_face: True` (see above) to drop
   the face/hair entirely.

5. **Iconic non-standard eye colours use an `eyes` override.** The main node's
   `eye_color` dropdown stays focused on believable people (no red / violet / gold
   cat-slit), so a character with canonical fantasy eyes carries a free-text **`eyes`**
   string (e.g. `"crimson"`, `"yellow with vertical cat-slit pupils"`, `"violet"`) that
   overrides `eye_color` and is voiced verbatim. It works because `eye_color`'s two
   gender pools are identical, so the gender gate passes the free text straight through;
   `validate_data` only checks that it is a non-empty string (and not also pinned in the
   signature). The override also locks `eye_shape` to absent, so the random shape word never
   piggybacks on it — you get *"crimson eyes"*, not *"crimson deep-set eyes"*. No effect on
   `covers_face` characters, whose eyes are hidden.

6. **Costume overrides suppress auto garment fields.** When a costume is supplied,
   the separately-randomized `outfit_style` / `footwear` / `clothing_color` /
   `clothing_pattern` are dropped from the JSON so they can't contradict the
   costume. `bag` / `accessories` remain (they are additive and density-driven).

7. **User entries are validated by `validate_data`.** Custom archetypes/cosplayers
   added via `user_options.json` are merged in-memory, so `python tests/validate_data.py`
   also checks them — handy for catching a typo'd field value. They are *not*
   strictly validated at load time, so an invalid value never breaks node loading;
   for unisex fields it passes through to the prompt text, for gender-specific
   fields the gender gate drops it.

## Extending the character set

The shipped set is a curated starter list and grows over time. Add your own
without editing the source (survives `git pull`) via the `cosplayers` section of
`user_options.json` — see `user_options.example.json`. A `gender: "Male"` entry is
how the `Random — male` pick gets populated. `costume` lists worn items only; give
a character its one iconic held item via the optional `"prop"` string (emitted only
when the node's `props` toggle is on), and add any other held items by editing the
prompt before rendering. For a canonical **non-standard eye colour** outside the main
node's pool (red / violet / gold cat-slit), add an optional free-text `"eyes"` string
(e.g. `"crimson"`) — it overrides `eye_color` and is voiced verbatim. For a fully masked
head set `"covers_face": true` **and** put the head covering in a separate `"mask"`
string (kept out of `costume`) so the *Unmask* toggle can drop it. Keep costume
text and names plain ASCII (no em dashes / smart quotes) so text-to-image
tokenizers don't mangle them.

For a **named beast that is not a person in a costume** (a quadruped, a serpent, a
six-legged sky bison), set `"body_plan": "feral"` and describe it as anatomy rather than
a worn look — see *Named beasts* above and the full schema in
[architecture.md](architecture.md). The anatomy has to carry the likeness with the name
stripped out: most checkpoints have never heard of a loth-cat.

For a **bald / shaven-headed character** (Mace Windu, Saitama, Professor X, Lex
Luthor, Dhalsim), state the bald head in `costume` (e.g. `"…, and a clean-shaven bald
head"`) and do **not** give the entry a `hair_length` / `hair_style` signature —
locking a short cut like `"buzzed very short"` makes the character render *with* hair
(a buzz cut). The costume text carries the baldness; the unlocked hair fields under it
simply randomize and read as absent. A clean-shaven `facial_hair` lock is fine and
keeps the male randomizer from adding a beard.

For a **non-natural skin colour** (green, blue, chrome, …), word it skin-native:
`"smooth, flawless <colour> skin"` — never as "body paint" or "dye". Live A/B
testing (0.52) showed paint/dye wording makes models render a streaky applied
coat *over* a human skin tone, while describing it as the character's own skin
renders one uniform colour (the builder suppresses the randomized human skin
underneath either way). Textured surfaces (scales, craggy rock, pebbled hide)
use `"uniform, all-over <colour> <material>"` and keep their texture word;
patterns/markings/plating follow as `"… with <pattern>"`. Fur/feather/flame/ice
entries may keep the older `"an even, all-over coat of …"` wording — all three
markers are auto-detected.

Contributions are welcome, too: if you'd rather a character ship in the built-in
set than live in your own `user_options.json`, open an issue or PR suggesting it.
