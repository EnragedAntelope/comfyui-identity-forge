# Suggested cosplayer additions (backlog)

A running list of characters proposed for `data/cosplayers.py`, with status.

When adding any candidate, follow the usual rules (see
[cosplayer-notes.md](cosplayer-notes.md) and the `data/cosplayers.py`
docstring): worn items only in `costume`; `covers_face` + `mask` for full
helmets/heads; `covers_hair` for lekku/montrals/hoods; skin-native wording for
non-natural skin colour; free-text `eyes` for non-standard eye colour; keep text
plain ASCII; then run `python tests/validate_data.py`, the unittest suite, and
`python scripts/generate_reference_docs.py` before committing.

> Heads-up on **duplicate dict keys** — a candidate that shares a name with an
> existing entry needs a disambiguated key (Python dicts silently collapse
> duplicate keys and `validate_data` flags it). Examples used below:
> `"Christie (Dead or Alive)"`, `"Miku Izayoi"`, `"Terra (Teen Titans)"`,
> `"Bumblebee (DC)"`, `"Red (Pokemon)"`, `"Leon (Pokemon)"`, `"Bea (Pokemon)"`,
> `"Ivy (Carmen Sandiego)"`, `"Zack (Carmen Sandiego)"`,
> `"Photon (Monica Rambeau)"`, `"Justice (New Warriors)"`, `"Rage (Marvel)"`,
> `"Duke Nukem (Captain Planet)"` vs `"Duke Nukem (video game)"`.

---

## Status

**Everything previously listed in this backlog was added to
`data/cosplayers.py`** (roster grew from 1,132 to 1,251), across these
franchises: Dead or Alive (incl. Ryu Hayabusa, Hayate, Jann Lee, Bass
Armstrong, Bayman, Eliot, Zack), Date A Live (Kotori, Yoshino, Miku Izayoi,
Natsumi, Nia Honjo, Mukuro), Archer (Ray, Barry, Woodhouse, Slater), Pokemon
(Brock, Iris, Lillie, Gary Oak, Red, Leon, Marnie, Bea, Elesa, Nemona), Star
Wars (Jyn Erso, Vette), Captain Planet eco-villains (Duke Nukem, Looten
Plunder, Sly Sludge, Captain Pollution, Zarm), Marvel (Hellcat, Photon, Sersi,
Namora, Julia Carpenter, Night Thrasher, Speedball, Justice, Rage), DC (Terra,
Bumblebee), Tekken (Jun Kazama, Anna Williams), Kim Possible (Drakken, Monkey
Fist, Duff Killigan, both Senor Seniors), The Fifth Element (Ruby Rhod, Zorg),
The Road to El Dorado (Tzekel-Kan), Anastasia (Bartok, Dowager Empress Marie),
Lollipop Chainsaw (Cordelia, Rosalind, Nick), Cool World (Jack Deebs, Frank
Harris), and Carmen Sandiego (Player, Ivy, Zack, Chase Devineaux, Coach Brunt,
Tigress). The video-game **Duke Nukem** was also added as a separate entry from
the Captain Planet villain.

### Intentionally skipped
- **AJ** (Archer) — Lana and Archer's daughter is an infant; there is no
  cosplay costume for an adult-figure generator.
- **Darkstars corps members** (DC) — listed only as a vague group; add a
  specific named member if wanted.

---

## Ideas for the next round (not yet added)
Fresh candidates that pair well with the franchises now in the set:

- **Dead or Alive** — Kokoro's mother Miyako, La Mariposa alt looks; male:
  Zack's rival Bass has a daughter (Tina, present).
- **Date A Live** — Yoshinon-only novelty, Nia's inverse form, Mukuro's civ look.
- **Pokemon** — Champions/leaders still open: Steven Stone, Diantha, Lance,
  Wallace, Jasmine, Whitney, Skyla, Nessa, Roxie.
- **Marvel** — remaining New Warriors: Silhouette, Nova (already present);
  Hellfire Club guards; Firestar (present) allies.
- **DC** — the Darkstars (Ferrin Colos), Jesse Quick, Gypsy (present), Grace
  Choi, Thunder.
- **Star Wars** — Twi'lek Hera (present), Sith Twi'lek Darth Talon, Oola's
  fellow dancers.
- **Kim Possible** — DNAmy, Camille Leon, Warmonga, Adrena Lynn.
- **Carmen Sandiego** — remaining VILE faculty: Dr. Saira Bellum, Cleo, Maelstrom,
  Countess Cleo; operatives El Topo, Le Chevre, Paper Star, The Cleaner.
- **Archer** — Katya (present), Slater (present), Conway Stern, Trinette.

---

## Already in the set — do NOT re-add (surfaced during review)
Requested/suggested but already shipped, so intentionally skipped as duplicates:

Nico Robin, Emma Frost, Jean Grey, Belle, Esmeralda, Misty, Misa Amane, Circe,
Boa Hancock, Madame Viper (as "Viper"), Phantom Lady (as "Phantom Lady (Dee
Tyler)"), Jessica Drew (as "Spider-Woman"), Sebastian Shaw, Kaguya (Ghibli's,
distinct from the added Kaguya Yamai), Jessie (Toy Story's, distinct from the
added "Jessie (Team Rocket)").
