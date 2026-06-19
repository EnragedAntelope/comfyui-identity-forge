# Cosplayer node — design notes & known limitations

Reference notes for the **Identity Forge Cosplayer** node. These are intentional
trade-offs, not bugs — recorded so behaviour is predictable and future changes
are informed.

## How it works

The Cosplayer node emits the same grouped-JSON document the Archetype node does
and wires into Identity Forge's shared `archetype_json` socket. A character is
stored as a **costume** (worn items only) plus a small **signature** look (hair,
eyes) and an optional **physique** (body/skin/height). Identity Forge randomizes
everything else, so each run is a different person wearing the same costume.

- **Costume only** (default): costume + signature; body, face, ethnicity randomize.
- **Full character**: also locks the physique for a faithful look.

## Known limitations

1. **Shared socket with Archetype.** Identity Forge has one preset input, so the
   Cosplayer and Archetype nodes are mutually exclusive — use one or the other.

2. **`Any` gender follows the character.** With a cosplayer connected and the
   Identity Forge `gender` widget on `Any`, the person defaults to the *character's*
   gender. Crossplay requires explicitly setting `gender` to `Male`/`Female`. This
   mirrors how archetypes behave.

3. **Full-character coherence is loose.** A locked physique (e.g. `slender`) can
   still randomize `fitness`/`muscle` to something like `very muscular`. There is
   no constraint tying those together; this predates the cosplayer node and
   affects locked body types generally.

4. **Hair under headpieces.** For characters whose head is a prosthetic/headpiece
   (e.g. montrals, helmets), hair still randomizes underneath in Costume-only mode.
   Give the entry a `signature` hair value to tame it if it matters.

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
weapons out and add them by editing the prompt before rendering.
