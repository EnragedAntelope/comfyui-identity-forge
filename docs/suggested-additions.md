# Suggested cosplayer additions (backlog)

A short, picky shortlist of higher-value candidates for `data/cosplayers.py`.
The roster is already very deep, so add only genuinely iconic, broadly-
recognizable characters with a real, canonical *worn look* — no deep cuts.

Rules for adding a character live in
[architecture.md → "Adding a character — curation checklist"](architecture.md)
(and the working principles above it). In brief: only if it fits the project; if a
requested character already ships, verify the entry is solid and add any missing
iconic variant rather than skipping; correct sub-franchise; masks/props identified
accurately; canonical well-described look; disambiguate colliding dict keys; then
validate + regenerate docs before committing.

**Always grep the live keys before adding.** `validate_data.py` catches two kinds of
duplicate — an exact repeated dict key, and a same-franchise pair where one name
extends the other *and* their costumes overlap ≥ 40% (this is what caught
"Violet" + "Violet Parr" in 0.75.0) — but neither catches a duplicate filed under a
genuinely different name, so the grep is still the first step.

---

## Curated shortlist (higher-value, genuinely missing)

**Cleared in 0.77.0.** Every candidate carried over from the 0.76.0 coverage pass has
now shipped, except the two animal entries, which moved to the TBD section below.
Added: Akame, Kirito, Lelouch vi Britannia (civilian), Ainz Ooal Gown,
`Aqua (KonoSuba)`, `Darkness (KonoSuba)`, `Morpheus (The Matrix)`, Columbia, Rachael,
Kiss-Shot Acerola-Orion Heart-Under-Blade, Hitagi Senjougahara, and Chizuru Mizuhara.

Three of those shipped over the shortlist's own reservations, on an explicit
maintainer decision — worth recording so the bar is not misread as having dropped:

| Candidate | Reservation | How it was resolved |
|---|---|---|
| Shinobu Oshino | Listed both as "no costume that reads without series context" **and** in the skip table as child-bodied — the file contradicted itself. | Shipped as the **adult Kiss-Shot Acerola-Orion Heart-Under-Blade** form, which has a real, ornate worn look and sidesteps the child-bodied objection entirely. Keyed under the Kiss-Shot name, not "Shinobu". |
| Hitagi Senjougahara | Canonical look is a school uniform. | Shipped anyway; the lavender hair and the specific Naoetsu High uniform carry it. Genuinely a soft entry. |
| Chizuru Mizuhara | Canonical look is ordinary modern dress. | Shipped anyway. The softest entry of the three — if a future pass tightens the "iconic *and* specific outfit" bar, this is the first one to re-examine. |

**The shortlist is currently empty.** Add new candidates here as they are found.

### League of Legends — the 0.81.0 expansion and where it stopped

League went 15 → 38 entries. The maintainer explicitly offered the **full ~170-champion roster**
and it was declined, which is the decision worth recording:

| Scope | Effect |
|---|---|
| The 11 requested + 12 curated (**shipped**) | League 15 → 38, comparable to Pokemon (32) and Mortal Kombat (28). Video Games 19.72% → 20.79%. |
| Full champion roster (**rejected**) | ~155 adds. League would become the largest franchise in the pack and Video Games would jump to ~28% — one game steering the global Random pool. |

`Evelynn` and `Seraphine` were on the request list and **already shipped**; they were refined, not
duplicated (Seraphine's neck-worn headphones needed a `necklace` pin). `Akali` got the same pin for
her lowered face mask.

Shipped: Nidalee, Brand, Briar, Zyra, Dr. Mundo, Elise, Janna, Jax, Yunara, Zilean, Zeri (the
request), plus Thresh, Jhin, Illaoi, Pyke, Sett, Irelia, Sona, Neeko, `Gwen (League of Legends)`,
Ambessa, `Mel Medarda`, Yone.

Deliberately **skipped**, so they are not re-proposed:

| Candidate | Why skipped |
|---|---|
| Bard | A floating cosmic spirit with a chime-and-bell body. No worn garments at all — fails curation rule 1, the same test that excluded the bare-chested Record of Ragnarok cast. |
| Yordles (Teemo, Lulu, Veigar, Poppy, Kennen…) | Small-child-bodied by design. Same rule that keeps Anya Forger and Beatrice off the roster. |
| Sylas, Braum, Udyr, Volibear, Rammus, Malphite, Blitzcrank | Either shirtless with no describable garment, or a non-humanoid construct/elemental better served by the Creature node. |
| Ryze, Swain, Viktor, Singed, Twisted Fate, Graves | Real looks, but each is a coat-and-trousers silhouette that would render as a generic robed or long-coated man without the name doing the work. Reconsider individually, not as a block. |

Two naming notes: `Gwen` was disambiguated because a bare "Gwen" sits beside `Gwen Tennyson` and
`Spider-Gwen` in the dropdown; `Mel Medarda` is keyed on her full name because a bare "Mel" is not
findable in a 1,700-row list. `Arcane` stays a separate franchise string for `Silco`, who is
Arcane-only; Ambessa and Mel are playable champions and file under League of Legends.

### Record of Ragnarok — characters deliberately NOT added (0.78.0)

The franchise opened at 0.78.0 with Aphrodite, Brunhilde, Lu Bu, Jack the Ripper, Buddha and
Shiva. The rest of the headline cast was assessed and skipped, so it is not re-litigated:

| Candidate | Why skipped |
|---|---|
| Adam, Heracles, Raiden Tameemon, Zeus | Fight bare-chested in plain shorts or a loincloth. No describable worn look — fails curation rule 1, and they would render as a generic muscular figure. |
| Thor, Poseidon, Hermes | The names collide with far better-known Marvel/DC keys already shipping, and their Record of Ragnarok designs are not distinctive enough to earn a disambiguated key. |
| Qin Shi Huang, Nikola Tesla, Sasaki Kojiro, Beelzebub, Hajun | Real deep cuts outside the series' own audience. |

**Aphrodite carries a note in the data:** her canonical presentation is essentially nude with
attendants physically supporting her bust. That is unusable twice over — a costume roster needs
a worn look, and naming attendants puts extra figures in the frame (the reason 0.63.0 deleted
the over-the-shoulder shot type). She ships as the clothed Grecian reading, keeping the canon
identifiers (flower-dressed shoulder-length blonde hair, blue eyes).

---

## TBD — how to handle animal characters

Candidates parked pending a decision on how (and whether) fully-animal characters
should be represented. Moved here in 0.77.0 from the shortlist and the skip table.

| Candidate | Franchise | Shape of the problem |
|---|---|---|
| Sandy Cheeks | SpongeBob | The pressurised diving suit with the glass dome hides the head, and the squirrel underneath arguably belongs to the Creature node. |
| Gadget Hackwrench | Chip 'n Dale Rescue Rangers | Purple jumpsuit and goggles — a real worn look — but she is a mouse. |
| Appa, Momo | Avatar: The Last Airbender | Non-human companions, no worn look at all. |
| Luna, Artemis | Sailor Moon | Same — talking cats. |
| Nala, Simba, Baloo, Shere Khan, Maid Marian, Yogi Bear, Tom & Jerry, Courage, Reptar, Scrooge McDuck, Darkwing Duck | various | Quadruped or funny-animal characters. Some (Maid Marian, Scrooge, Darkwing) *do* wear clothes; the rest do not. |

### The important context: the pack already ships ~50 of these

This was framed as an open question, but the roster answered a large part of it years
ago. **91 entries carry both `covers_body` and `covers_face`** — a full head-and-body
covering, i.e. a mascot suit — and roughly 50 of those are animals or creatures:

> Bugs Bunny · Daffy Duck · Mickey Mouse · Donald Duck · Horton · Winnie the Pooh ·
> Tigger · Eeyore · Pikachu · Eevee · Jigglypuff · Yoshi · Sonic the Hedgehog ·
> Donkey Kong · Fox McCloud · Stitch · Olaf · Jake the Dog · Cheshire Cat ·
> Curious George · Paddington Bear · Cowardly Lion · the four TMNT + Splinter ·
> King Shark · Killer Croc · Gorilla Grodd · Godzilla · King Kong · Abe Sapien ·
> Porg · Loth-Cat · Salacious Crumb · Chester Cheetah · Tony the Tiger ·
> Energizer Bunny · Duolingo Owl · Geico Gecko · Zoidberg · Moogle · Ultros ·
> Blaidd the Half-Wolf · Jon Talbain · Rikuo · Sasquatch · Q-Bee · Verminous Skumm ·
> Fievel Mousekewitz · No-Face · Baron Humbert von Gikkingen · Reptile

So the mechanism is settled and works: `covers_body: True` + `covers_face: True` +
a `mask` renders a coherent person-in-a-full-suit. **The real open question is much
narrower than "how do we handle animals":** it is whether *quadrupeds with no worn
look at all* (Appa, Simba, Baloo, Luna/Artemis) belong in a costume roster.

**Recommendation: they do not.** A quadruped has no garments to describe, which fails
curation rule 1, and the **Creature node already covers exactly this ground** — it
renders a character as an animal form, hybridized slot-by-slot. Sandy Cheeks and
Gadget Hackwrench are the genuinely borderline pair, because both wear real,
describable garments over an animal body; they would work as ordinary entries with
`covers_body: True` if the animal head is written into a `mask`.

### Proposed grouping/toggle (not built — needs a decision)

Add a **`Mascot / full-suit`** attribute scope to the Cosplayer node's `random_scope`,
derived from `covers_body and covers_face`:

```python
"Mascot / full-suit": lambda e: e.get("covers_body") and e.get("covers_face"),
```

- `_SPECIAL_SCOPES` in `nodes/identity_forge_cosplayer.py` is already a
  `{label: predicate}` map with its own branch in `_resolve_character`, so this is
  **one lambda** — the same shape as the existing `Giant` / `Tiny` / `Masked` /
  `Non-human / colored` scopes.
- It is a **filter over the existing pool**, so it adds no entries and cannot shift
  any field's distribution. Bias-free by construction.
- It is self-maintaining: derived from the flags, so it counts `user_options.json`
  additions and grows with the roster.
- UX: users who want mascot suits get a way to find them (91 entries is a lot to
  stumble on by luck), and users who don't get to see the category exists.

Alternatives considered and **rejected**:

- **A per-entry `is_animal` key.** A new schema key driving no engine behaviour —
  fails working principle 1 (no unwarranted complexity). The two flags already encode
  what matters.
- **A global "no animal cosplays" toggle.** A negative filter is worse UX than a
  positive scope, and `accessory_density` is the only global-control precedent in the
  pack — it earns its place by affecting every run, which this would not.

---

## Considered and deliberately skipped

Recorded so they are not re-litigated. Reopen only with a specific reason.
(The animal rows that used to live here moved to the TBD section above.)

| Candidate | Why skipped |
|---|---|
| Shanna / "Shana the She-Devil" | The available description conflates her with **Red Sonja**, who already ships. Would need a canon-checked jungle-heroine look to be worth a distinct entry. |
| "Magic" (Limbo sorceress) | A misspelling of **Magik**, who ships — including the blue demon-form look as an alternate costume. |
| "The Wolfman" | Already ships as **The Wolf Man** (Universal Monsters). |
| "Catwoman 1940s" | Catwoman already carries four alternate looks, including the Golden-Age emerald gown. |
| Jessica Jones, Marion Ravenwood, Baby Houseman, Frankie Foster, Peggy Hill, Luanne Platter | Everyday modern dress. Fails the "iconic *and* specific outfit" bar that admitted Trinity, Mia Wallace and Sandy Olsson. |
| Barbarella | Re-confirmed skip (first recorded in the 0.70.0 comic-women review). |
| Sue Storm, Ghost-Spider, Spider-Gwen, Kurisu (Steins;Gate) | Already ship under their other names — **Invisible Woman**, **Spider-Gwen**, **Makise Kurisu**. |
| Alice Abernathy | The *Resident Evil* films only. `Resident Evil` is registered under **Video Games**, so she would be filed in the wrong category; a `Resident Evil (film)` franchise is not worth the split. |
| Anya Forger, Beatrice (Re:Zero) | Small-child or child-bodied characters. Distinct from the accepted child *cosplays* (Dora, the Powerpuff Girls, Tina Belcher, Charlie Brown), whose looks are ordinary clothing. |

**Two rows were removed from this table in 0.77.0 because they no longer apply:**
*Kimberly (Space Ace)* was skipped as "obscure, and the name collides with Kimberly
Jackson" — the maintainer reopened it, and she ships as `Kimberly (Space Ace)`.
*Shinobu Oshino* was skipped as child-bodied — the adult Kiss-Shot form ships instead,
which is why the child-bodied rule itself still stands for Anya and Beatrice.
