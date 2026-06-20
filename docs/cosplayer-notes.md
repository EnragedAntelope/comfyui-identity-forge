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
The Cosplayer node re-attaches the mask to the costume and passes `covers_face`
through its `_meta`; IdentityForge then drops the randomized **Face / Hair /
Makeup** fields (plus earrings/piercings) from both the prose and JSON — so a
random face never gets described fighting the mask. Leave both off whenever the
face is visible (an open cowl, a domino mask, a body-painted but visible face like
Hulk).

The node's **`mask`** widget controls this per render: **Default** keeps the mask
on, while **Unmask (show face)** drops the mask clause *and* clears `covers_face`,
so the randomized head/hair shows under the suit — a helmet-off look (Tony Stark in
the Iron Man armor). It is a no-op for face-visible characters. Keeping the head
covering in its own field is what lets it be removed cleanly, with no stray
"faceplate" reference stranded in the costume prose.

### Chaining presets

Both preset nodes expose an optional **`upstream`** input, so Archetype and
Cosplayer nodes chain into one wire (`Archetype → Cosplayer → Identity Forge`)
instead of competing for the single socket. Documents are deep-merged with the
**downstream** node (closest to Identity Forge) winning on overlap, including
`_meta`; non-overlapping upstream values survive. A node set to `None` emits `{}`,
which passes its upstream through unchanged — so both presets can stay wired and
you just toggle which one is active.

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

3. **Full-character coherence is loose.** A locked physique (e.g. `slender`) can
   still randomize `fitness`/`muscle` to something like `very muscular`. There is
   no constraint tying those together; this predates the cosplayer node and
   affects locked body types generally.

4. **Hair under partial headpieces.** For characters whose head is *partly* covered
   (montrals, a circlet, an open cowl) but whose face shows, hair still randomizes
   underneath in Costume-only mode. Give the entry a `signature` hair value to tame
   it, or — for a *fully* masked head — set `covers_face: True` (see above) to drop
   the face/hair entirely.

5. **Some iconic eye colours don't map.** The eye-colour field has no violet / red
   / yellow / pink options, so those characters' eyes randomize rather than being
   forced. Hair and costume carry recognizability instead.

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
how the `Random — male` pick gets populated. Worn items only; leave held props and
weapons out and add them by editing the prompt before rendering. For a fully masked
head set `"covers_face": true` **and** put the head covering in a separate `"mask"`
string (kept out of `costume`) so the *Unmask* toggle can drop it. Keep costume
text and names plain ASCII (no em dashes / smart quotes) so text-to-image
tokenizers don't mangle them.

For a **non-natural skin colour** (green, blue, chrome, …), word it as
`"an even, smooth coat of <colour> body paint"` rather than `"all-over <colour>
body paint"` — the "even, smooth coat" wording renders as a uniform colour instead
of the patchy/streaked paint many models produce. Keep the word "paint" (in
Costume-only mode the person underneath randomizes and their skin tone is spoken,
so the colour reads as paint *over* that skin, not a contradiction). Textured
surfaces (scales, fur) use `"an even, all-over coat of …"` and keep their texture
word; patterns/markings/plating follow as `"… with <pattern>"`.

Contributions are welcome, too: if you'd rather a character ship in the built-in
set than live in your own `user_options.json`, open an issue or PR suggesting it.
