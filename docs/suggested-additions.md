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

Each of these was researched during the 0.87.0 franchise-gap pass and deliberately
not shipped, so the next session does not repeat the survey.

| Candidate | The case |
|---|---|
| **The Sonic cast** — Shadow, Amy Rose, Dr. Eggman | `Sonic the Hedgehog` ships alone. All three are the mascot-suit shape ~50 entries already run on (`covers_face` + `covers_body` + `mask`), so the mechanism is settled; Eggman is the cleanest of them, being a plain human in a red coat with goggles and a moustache. 0.85.0 closed the funny-animal class "pending a fresh case", and a cast expansion is exactly that — it needs its own written argument, not a ride-along. Tails and Knuckles are weaker: another two-tone furry silhouette each. |
| **The rest of the Pixar gap** — Monsters Inc., Ratatouille, Turning Red | Toy Story, The Incredibles, Inside Out, Big Hero 6 and Brave ship; Coco and Up joined them at 0.87.0 (Hector Rivera, Carl Fredricksen). Sulley and Mike are mascot-suit shapes; Remy is a quadruped with no worn look (Creature node); Mei's red panda form is the same question. Each needs deciding on its own merits. |
| Castlevania — Alucard, a Belmont | Two strong, distinct worn looks (high-collared black coat; layered hunter's leathers) in a franchise with none. |
| Fallout — a Vault Dweller | The blue-and-yellow vault suit is unmistakable, and the Pip-Boy is a clean `prop` + `prop_costume` pair since it is worn on the forearm. |
| Power Rangers | Helmet = `covers_face` + `mask`. The Miraculous lesson applies directly: a whole cast in near-identical suits makes the **shared** mechanics the risk, not any one entry. Ship one or two, not a team. |
| Inuyasha; Yu Yu Hakusho; Ranma 1/2; Hellsing | Four anime franchises with no representation and one obvious lead each. |
| Sakura Kinomoto (Cardcaptor Sakura) | Key must be the full name — four other Sakuras already ship. |
| Gravity Falls; Encanto; Hocus Pocus | Distinct, describable looks; no franchise representation. |
| Marty McFly (Back to the Future); The Dude (The Big Lebowski) | Both are ordinary modern dress carried entirely by one specific garment (the puffer vest; the cardigan). Borderline against the "iconic *and* specific outfit" bar — decide deliberately. |
| Elphaba (Wicked) | Note `Wicked Witch of the West` already ships under The Wizard of Oz, so this is a variant question as much as a new entry. |

**Researched and skipped — do not re-survey.** Valorant, Apex Legends, Destiny,
Monster Hunter, Warhammer 40K, Skyrim, Splatoon, Animal Crossing, Undertale, FNAF,
Cuphead, Among Us, Minecraft. Each is an armoured, abstract or mascot silhouette
that would render as something generic without the name doing the work — the same
reason Ryze, Swain and Viktor were declined below.

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

### Whole classes

| Class | Why |
|---|---|
| Akumatized Miraculous villains (Volpina, Antibug, Style Queen, Timebreaker, Miracle Queen…) | Mostly one-episode designs. **Chat Blanc** is the exception and ships as an *alternate* on Cat Noir, not a separate entry. |
| The kwamis (Tikki, Plagg, Wayzz…) | Palm-sized floating creatures with no worn look. Creature-node shape. |
| Quadrupeds with no worn look — Appa, Momo, Luna, Artemis, Nala, Simba, Baloo, Shere Khan, Yogi Bear, Tom & Jerry, Courage, Reptar | No garments to describe. The **Creature node** already covers this ground exactly, rendering an animal form slot by slot. |
| The full ~170-champion League roster | Offered and declined. ~155 adds would make League the largest franchise in the pack and take Video Games to ~28%, letting one game steer the global Random pool. The curated 15 → 38 expansion is where it stops. |

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
| 2 | **A creature face-colour restatement**, mirroring what `_format_prose` already does for cosplayers. | `palette` reaches `integument` but never `head`, so a creature whose identity is its pallor or hue renders an ordinary human face. Found on `jiangshi` at 0.87.0 and worked around with colour-free intensifiers in the `head` slot, which only partly wins. This is an engine change, not a data one — see the gotcha in `architecture.md`. |
| 1 | **Re-examining the softest shipped entries** if the "iconic *and* specific outfit" bar is ever tightened. | `Chizuru Mizuhara` is first in line (canonical look is ordinary modern dress), then `Hitagi Senjougahara` (a school uniform, carried by the lavender hair and the specific Naoetsu High cut). Both shipped on an explicit maintainer decision over the shortlist's own reservation — recorded so the bar is not misread as having dropped. |

**Closed at 0.85.0:** Maid Marian, Scrooge McDuck and Darkwing Duck shipped — the funny-animal
question resolved at exactly those three, not an open-ended class. `Robin Hood (1973)`,
`DuckTales` and `Darkwing Duck` are registered as their own Disney sub-franchises (not folded
into `Mickey Mouse & Friends`, which would have crossed `_FRANCHISE_SCOPE_MINIMUM` and added an
unplanned `random_scope` option). A further funny-animal batch needs a fresh case, same as any
other candidate.
