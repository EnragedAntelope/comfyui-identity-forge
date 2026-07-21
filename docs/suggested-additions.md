# Suggested cosplayer additions (backlog)

A running list of characters proposed for `data/cosplayers.py` but **not yet
added**, kept for a future revision. Everything here was checked against the
shipped roster at the time of writing and confirmed **absent** unless noted.

When adding any of these, follow the usual rules (see
[cosplayer-notes.md](cosplayer-notes.md) and the `data/cosplayers.py`
docstring): worn items only in `costume`; `covers_face` + `mask` for full
helmets/heads; `covers_hair` for lekku/montrals/hoods; skin-native wording for
non-natural skin colour; free-text `eyes` for non-standard eye colour; keep text
plain ASCII; then run `python tests/validate_data.py`, the unittest suite, and
`python scripts/generate_reference_docs.py` before committing.

> Heads-up on **duplicate dict keys** — several candidates share a name with an
> existing entry. Python dicts silently collapse duplicate keys and
> `validate_data` will flag it, so these need a disambiguated key such as
> `"Christie (Dead or Alive)"`. They are marked **[key collision]** below.

---

## Priority — obvious gaps in recently-expanded franchises

### Dead or Alive
- **Lisa Hamilton (La Mariposa)** — luchadora mask + wrestling gear.
- **Mila** — MMA fighter, red/white gear, short strawberry hair.
- **Rachel** (Ninja Gaiden fiend hunter) — armored bodice, blonde.
- **Christie** **[key collision — "Christie" would clash with Tekken's Christie Monteiro]** — assassin in a slinky black outfit, silver-white bob.
- Male roster if desired: Ryu Hayabusa (also Ninja Gaiden), Hayate, Zack, Bass Armstrong (Tina's father), Bayman, Jann Lee, Eliot.

### Date A Live
- **Kotori Itsuka** — twin-tailed, red/black military-coat astral dress (Efreet).
- **Yoshino** — pale blue, rabbit-hood puppet (Zadkiel), gentle.
- **Miku Izayoi** **[key collision — Vocaloid "Hatsune Miku" exists; use "Miku Izayoi"]** — idol spirit, blue hair, pipe-organ astral dress.
- Also: Natsumi, Nia Honjo, Mukuro Hoshimiya.

### Archer
- **Ray Gillette** — ISIS field agent, green turtleneck.
- **Barry Dylan** — rival cyborg spy, exposed robotic arm/eye.
- Also: Woodhouse, Slater, AJ.

### Pokemon
- **Brock** — squinting gym leader, brown spiky hair, green vest.
- **Iris** — dark-skinned, huge purple pigtails, Unova.
- **Lillie** — white sun-dress + hat, blonde, Alola.
- Also: Gary Oak/Blue, Red, Leon (Galar champion, cape), Marnie, Bea, Elesa, Nemona. (Meowth already present.)

### Star Wars
- **Jyn Erso** — Rogue One, layered utility jacket + scarf, brown bob.
- **Vette** (SWTOR) — cheeky blue Twi'lek, light armor (more alien-skin variety).
- (Sabine Wren, Padme, Leia, Rey, Ahsoka, Mara Jade, Aurra Sing, Asajj Ventress, Hera Syndulla already present.)

### Captain Planet (remaining eco-villains)
- **Duke Nukem** (the radioactive villain, green-skinned) — skin-native green.
- **Looten Plunder** — corporate polluter, business suit.
- **Sly Sludge** — sloppy waste-dumper.
- **Captain Pollution** — Captain Planet's grey/toxic evil counterpart (mask-free, coloured skin). Great villain foil.
- **Zarm** — red-armored spirit-of-war antagonist.

---

## Marvel deep cuts (same cheesecake / obscure-hero vein)
- **Hellcat (Patsy Walker)** — yellow-and-blue catsuit, cat-ear cowl, orange hair.
- **Photon / Spectrum (Monica Rambeau)** — sleek white/black energy suit.
- **Sersi** — Eternal, green-and-gold sorceress look.
- **Namora** — Atlantean, green-scaled swimsuit, dark hair (pairs with the added Namorita).
- **Julia Carpenter (Spider-Woman II / Madame Web)** — black-and-white spider suit.
- New Warriors teammates (pair with Namorita): Night Thrasher, Speedball, Justice, Rage.
- (Titania, Spider-Woman/Jessica Drew, Sebastian Shaw, Mantis, Clea, Satana, Firestar, Dazzler, Domino already present.)

## DC
- **Terra (Tara Markov)** **[key collision — FF's "Terra Branford" exists; use "Terra (Teen Titans)"]** — Teen Titans, orange/yellow bodysuit, blonde.
- **Bumblebee (Karen Beecher)** **[key collision — Transformers "Bumblebee" exists; use "Bumblebee (DC)"]** — black/yellow winged suit.
- Darkstars corps members if the Donna Troy Darkstar alt sparks interest.
- (Ice, Jade, Vixen, Galatea, Nightstar, Power Girl, Starfire, Raven, Zatanna, Huntress, Hawkgirl, Mera already present.)

## Tekken (roster still open)
- **Jun Kazama** — nature-toned fighting dress, brown hair.
- **Anna Williams** — red slit dress, dark hair (rival/sister to the existing Nina Williams).
- (Kazuya, Jin, Heihachi, Hwoarang, Paul Phoenix, King, Eddy, Lili, Xiaoyu, Asuka, Nina, Christie Monteiro already present. Note Yoshimitsu exists only under Soul Calibur; a Tekken variant would be a near-duplicate.)

## Kim Possible
- **Dr. Drakken** — blue-skinned mad scientist, black coat + scar.
- **Monkey Fist** — monkey-themed martial-arts villain.
- Also: Duff Killigan, Senor Senior Sr./Jr. (Kim, Ron, Shego, Bonnie already present.)

## The Fifth Element
- **Ruby Rhod** — flamboyant leopard-print/black radio host, horned hairpiece.
- **Jean-Baptiste Emanuel Zorg** — villain, half-fringe hair, cream suit.

## The Road to El Dorado
- **Tzekel-Kan** — sinister high priest, elaborate feathered/bone headdress and robes (villain foil to the added Tulio/Miguel/Chel).

## Smaller franchise round-outs (nice-to-have)
- **Anastasia** — Bartok (bat sidekick), Dowager Empress Marie.
- **Lollipop Chainsaw** — Cordelia & Rosalind Starling (Juliet's sisters), Nick Carlyle (severed head).
- **Cool World** — Jack Deebs, Detective Frank Harris.
- **Carmen Sandiego** — Player, Ivy & Zack, Chase Devineaux, Coach Brunt, Tigress.

---

## Already in the set — do NOT re-add (surfaced during review)
These were requested/suggested but ship already, so they were intentionally
skipped as duplicates:

Nico Robin, Emma Frost, Jean Grey, Belle, Esmeralda, Misty, Misa Amane, Circe,
Boa Hancock, Madame Viper (as "Viper"), Phantom Lady (as "Phantom Lady (Dee
Tyler)"), Jessica Drew (as "Spider-Woman"), Sebastian Shaw, Kaguya (Ghibli's, a
different character from the added Kaguya Yamai), Jessie (Toy Story's, distinct
from the added "Jessie (Team Rocket)").
