# Roster backlog

Three sections, and only three:

1. **[Under consideration](#under-consideration)** — candidates with a real case behind them.
2. **[Decided against](#decided-against)** — closed, with the reason. Do not re-propose.
3. **[Still to consider](#still-to-consider)** — open questions with no decision yet.

This file is a **backlog**, not a changelog. It does not record which release something
shipped in — `git log` does that. Reusable rules learned while curating live in
[architecture.md → "Adding a character — curation checklist"](architecture.md), not here.

**Before adding anything, grep the live keys.** `validate_data.py` catches an exact
repeated dict key and a same-franchise pair where one name extends the other *and* their
costumes overlap >= 40% (this caught "Violet" + "Violet Parr"). Neither catches a
duplicate filed under a genuinely different name.

**The bar:** genuinely iconic, broadly recognizable, and with a real canonical *worn
look*. No deep cuts. A character with no describable garments is not a roster entry —
that is what the Creature node is for.

---

## Under consideration

**Empty.** The 0.87.0 survey list was worked to completion at 0.88.0: everything with a
real case shipped, and everything else was closed into [Decided against](#decided-against)
rather than left to be re-surveyed. Add a row here only with a fresh, written case.

**Researched and skipped — do not re-survey.** Valorant, Apex Legends, Destiny,
Monster Hunter, Skyrim, Splatoon, Animal Crossing, Undertale, FNAF,
Cuphead, Among Us, Minecraft. Each is an armoured, abstract or mascot silhouette
that would render as something generic without the name doing the work — the same
reason Ryze, Swain and Viktor were declined below.

> **Warhammer 40K was removed from that list at 0.88.0 and shipped.** The original skip
> treated the whole setting as uniformly armoured silhouettes. That is true of two of the
> four that shipped (`Space Marine`, `Sister of Battle`, which take the settled
> `covers_face` + `mask` route), but not the other two: `Tech-Priest` is hooded robes and
> augmetics and `Commissar` is a greatcoat and peaked cap — cloth silhouettes that read
> correctly without the name doing the work. That is the new argument; the rest of the
> skipped list still stands on the old one.

---

## Decided against

Closed with a reason. Reopen only with a **new** argument, not a repeat of the request.

### Individual characters

| Candidate | Why |
|---|---|
| Marinette Dupain-Cheng, Adrien Agreste (civilian) | Ordinary modern teen dress. Their transformed looks (Ladybug, Cat Noir) carry them. |
| Jessica Jones, Marion Ravenwood, Baby Houseman, Frankie Foster, Peggy Hill, Luanne Platter | Everyday modern dress. Fails the "iconic *and* specific outfit" bar that admitted Trinity, Mia Wallace and Sandy Olsson. |
| Anya Forger, Beatrice (Re:Zero) | Human children in ordinary clothes. Distinct from the accepted child *cosplays* (Dora, the Powerpuff Girls, Tina Belcher, Charlie Brown), whose looks are ordinary clothing on an adult wearer. See the mascot-suit distinction in architecture.md — it does **not** rescue these two. |
| Barbarella | Re-confirmed skip. |
| Shanna / "Shana the She-Devil" | The available description conflates her with **Red Sonja**, who already ships. |
| Alice Abernathy | *Resident Evil* films only; `Resident Evil` is registered under Video Games, so she would file in the wrong category, and a `Resident Evil (film)` franchise is not worth the split. |
| Bard (League of Legends) | A floating cosmic spirit with a chime-and-bell body. No worn garments at all. |
| Sylas, Braum, Udyr, Volibear, Rammus, Malphite, Blitzcrank | Either shirtless with no describable garment, or a non-humanoid construct better served by the Creature node. |
| Ryze, Swain, Viktor, Singed, Twisted Fate, Graves | Real looks, but each is a coat-and-trousers silhouette that would render as a generic robed or long-coated man without the name doing the work. |
| Lulu, Veigar, Poppy, Kennen | Scope, not shape. **Teemo** already covers the yordle concept; four more would push League past every other franchise for no new visual ground. |
| Adam, Heracles, Raiden Tameemon, Zeus (Record of Ragnarok) | Fight bare-chested in plain shorts or a loincloth. No describable worn look. |
| Thor, Poseidon, Hermes (Record of Ragnarok) | The names collide with far better-known Marvel/DC keys already shipping, and these designs are not distinctive enough to earn a disambiguated key. |
| Qin Shi Huang, Nikola Tesla, Sasaki Kojiro, Beelzebub, Hajun | Deep cuts outside the series' own audience. |
| Shadow, Amy Rose, Tails, Knuckles (Sonic) | `Dr. Eggman` shipped at 0.88.0 as the one clean case — a plain human in a red coat. The other four are each another two-tone furry mascot silhouette, which is the ride-along 0.85.0 closed the funny-animal class against. |
| Sakura Kinomoto (Cardcaptor Sakura) | Closed unshipped. Four other Sakuras already ship, and the magical-girl-in-a-school-uniform shape is well covered. |
| Elphaba (Wicked) | `Wicked Witch of the West` already ships under The Wizard of Oz and carries the green-skinned witch silhouette. A second one is a variant, not a new look. |
| Chie Satonaka, Yukiko Amagi, Rise Kujikawa, Yukari Takeba, Fuuka Yamagishi (Persona) | School uniform plus one coloured jacket. That is the exact shape flagged below as the roster's softest already-shipped entries — adding five more of it would move the bar, not meet it. The Persona entries that shipped at 0.88.0 all have a distinct non-uniform silhouette. |
| Scout, Soldier (Team Fortress 2) | The seven that shipped each carry a silhouette that reads alone. Scout is a backwards baseball cap over a t-shirt and Soldier is a generic helmeted soldier — both need the franchise name to do the work. |
| The rest of the Guilty Gear cast — Potemkin, Faust, Chipp Zanuff, Nagoriyuki, Ramlethal, Axl Low | The curated eleven already cover every distinct silhouette in the cast. This is the League ceiling applied early: a franchise stops where more entries stop adding new visual ground. |
| Ork Boyz, Necrons (Warhammer 40,000) | No worn look — a hulking green brute and a skeletal metal automaton. **Creature node** shape, the same call as Appa and Simba. |
| Chaos Space Marines, Aeldari Farseers (Warhammer 40,000) | More armour. The four that shipped were chosen because two of them are cloth; these would re-add exactly the silhouette the original skip was right about. |

### Whole classes

| Class | Why |
|---|---|
| Akumatized Miraculous villains (Volpina, Antibug, Style Queen, Timebreaker, Miracle Queen…) | Mostly one-episode designs. **Chat Blanc** is the exception and ships as an *alternate* on Cat Noir, not a separate entry. |
| The kwamis (Tikki, Plagg, Wayzz…) | Palm-sized floating creatures with no worn look. Creature-node shape. |
| Quadrupeds with no worn look — Appa, Momo, Luna, Artemis, Nala, Simba, Baloo, Shere Khan, Yogi Bear, Tom & Jerry, Courage, Reptar | No garments to describe. The **Creature node** already covers this ground exactly, rendering an animal form slot by slot. |
| The full ~170-champion League roster | Offered and declined. ~155 adds would make League the largest franchise in the pack and take Video Games to ~28%, letting one game steer the global Random pool. The curated 15 → 38 expansion is where it stops. |
| The rest of the Pixar gap — Monsters Inc., Ratatouille, Turning Red | Closed unshipped at 0.88.0. Sulley and Mike are mascot-suit shapes already covered ~50 times over; Remy is a quadruped with no worn look (**Creature node**); Mei's red panda form is the same question. None brings new visual ground. |
| Power Rangers | Closed unshipped. This is the Miraculous case at its worst — a whole cast in the same suit in different colours, where the shared mechanics are the risk and no single entry earns its place. |
| Gravity Falls; Hocus Pocus | Closed unshipped at 0.88.0 when the row they shared with Encanto was split. Encanto had four distinct silhouettes; these two are ordinary modern dress and period costume respectively, carried by the ensemble rather than by any one look. |

### Already ship under another name — check before proposing

| Proposed as | Actually ships as |
|---|---|
| "The Wolfman" | **The Wolf Man** (Universal Monsters) |
| "Magic" (Limbo sorceress) | **Magik**, including the blue demon-form alternate |
| "Catwoman 1940s" | **Catwoman**, which carries four alternate looks incl. the Golden-Age emerald gown |
| Sue Storm | **Invisible Woman** |
| Ghost-Spider | **Spider-Gwen** |
| Kurisu (Steins;Gate) | **Makise Kurisu** |
| Evelynn, Seraphine, Akali | Already on the roster — they were *refined*, not duplicated |

---

## Still to consider

Open. No decision has been made either way.

| # | Question | Where it stands |
|---|---|---|
| 1 | **Re-examining the softest shipped entries** if the "iconic *and* specific outfit" bar is ever tightened. | `Chizuru Mizuhara` is first in line (canonical look is ordinary modern dress), then `Hitagi Senjougahara` (a school uniform, carried by the lavender hair and the specific Naoetsu High cut). Both shipped on an explicit maintainer decision over the shortlist's own reservation — recorded so the bar is not misread as having dropped. |

**Closed at 0.88.0 — the creature face-colour question (was #2).** The proposal was an engine
change restating `palette` on the `head` slot, mirroring `_format_prose`. Measurement killed it:
**186 of 209 creature heads are anatomically fused animal heads** (muzzle, beak, mandibles,
carapace, ruff), where head and body are one continuous material and the model carries the
integument colour across unaided — which is why the roster renders correctly today. Only 23 heads
are human-shaped, and of those 5 already name a colour, 6 name a non-skin material or have no face
at all (`radial alien`, `wraith`), and 3 *should* have a human face (`centaur`, `satyr`, `sphinx`).
The real risk set was six entries, fixed as data at 0.88.0 by adding colour-free material words to
`flesh golem`, `troll`, `manticore` and `yeti` (`ghost` and `leprechaun` already self-described).
**Do not re-propose the engine change from the "systemic" premise** — it was measured and it is not.

**Closed at 0.85.0:** Maid Marian, Scrooge McDuck and Darkwing Duck shipped — the funny-animal
question resolved at exactly those three, not an open-ended class. `Robin Hood (1973)`,
`DuckTales` and `Darkwing Duck` are registered as their own Disney sub-franchises (not folded
into `Mickey Mouse & Friends`, which would have crossed `_FRANCHISE_SCOPE_MINIMUM` and added an
unplanned `random_scope` option). A further funny-animal batch needs a fresh case, same as any
other candidate.
