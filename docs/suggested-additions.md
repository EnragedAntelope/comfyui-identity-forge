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

**Two `hair_style` values, blocked on arithmetic rather than taste (0.90.0).** Both
were written, tested, and backed out when `HairStyleFamilyTests` failed — recorded
here with the exact cost so a future pass can decide whether to pay it.

| Candidate | What it needs |
|---|---|
| **hime cut** | Its natural home is `loose_styled`, which is a **split** sub-family — adding a sixth variant broke the `loose` split's proportionality (140 vs 116.67 per variant). It also requires long hair, so any length exclusion would be a *partial* cull of the sub-family and would concentrate its frozen weight on the survivors. Needs its own sub-family and a reprice of the whole `loose` group. |
| **wolf cut** | Belongs in `barbered_shag`, an **added** family pinned to the field's "everyday cut" rate. Growing it needs the family repriced *and* `_DILUTION` in `HairStyleFamilyTests` restated. |

The two that *did* ship (`side-swept bangs`, `wispy bangs`) went into `bangs` — a
pre-existing, non-split family with no length restriction — so the total weight stayed
7140 and no share moved at all. That is the difference between a cheap addition and an
expensive one, and it is not visible from the option list.

**Everything else: empty.** The 0.87.0 survey list was worked to completion at 0.88.0: everything with a
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
| Ork Boyz, Necrons (Warhammer 40,000) | No worn look — a hulking green brute and a skeletal metal automaton. Both are shapes a person fits inside, so they are the mascot-suit case rather than the feral one, and neither adds a silhouette the four shipped 40K entries lack. (The old wording filed them "the same call as Appa and Simba"; Appa shipped at 0.95.0 and Simba did not — see the quadruped row below for the test that separates them.) |
| Chaos Space Marines, Aeldari Farseers (Warhammer 40,000) | More armour. The four that shipped were chosen because two of them are cloth; these would re-add exactly the silhouette the original skip was right about. |

### Whole classes

| Class | Why |
|---|---|
| Akumatized Miraculous villains (Volpina, Antibug, Style Queen, Timebreaker, Miracle Queen…) | Mostly one-episode designs. **Chat Blanc** is the exception and ships as an *alternate* on Cat Noir, not a separate entry. |
| The kwamis (Tikki, Plagg, Wayzz…) | Palm-sized floating creatures with no worn look. Re-checked against the 0.95.0 feral test and still closed: each is a simple coloured blob with a head, which is not a body `data/creatures.py` cannot render, and at palm scale nothing distinguishing survives. |
| Quadrupeds with no worn look — Nala, Simba, Baloo, Shere Khan, Yogi Bear, Tom & Jerry, Courage | **Reason replaced at 0.95.0, verdict unchanged for these seven.** The old reason ("the Creature node already covers this ground exactly") was wrong, and `Appa`, `Momo`, `Luna` and `Reptar` shipped at 0.95.0 under `body_plan: "feral"`. The real test is the mirror of the creature roster's *anatomy, not species* bar: **does the beast bring a body `data/creatures.py` cannot render?** These seven do not — `lion`, `bear`, `tiger` and `cat` render them and the name changes nothing a model draws, so by the 0.93.0 rule the difference is a `palette` and a `size_scale`. Appa (six legs, brown arrow) and Catbus (twelve legs, lit windows) do. See [architecture.md → "Animal characters split four ways"](architecture.md). |
| The full ~170-champion League roster | Offered and declined. ~155 adds would make League the largest franchise in the pack and take Video Games to ~28%, letting one game steer the global Random pool. The curated 15 → 38 expansion is where it stops. |
| The rest of the Pixar gap — Monsters Inc., Ratatouille, Turning Red | Closed unshipped at 0.88.0. Sulley and Mike are mascot-suit shapes already covered ~50 times over; Remy is an ordinary rat and Mei's red panda form an ordinary red panda, both of which `data/creatures.py` already renders, so they fail the 0.95.0 feral test too. None brings new visual ground. |
| Power Rangers | Closed unshipped. This is the Miraculous case at its worst — a whole cast in the same suit in different colours, where the shared mechanics are the risk and no single entry earns its place. |
| Gravity Falls; Hocus Pocus | Closed unshipped at 0.88.0 when the row they shared with Encanto was split. Encanto had four distinct silhouettes; these two are ordinary modern dress and period costume respectively, carried by the ensemble rather than by any one look. |

### Creature-node animals — the recurring rejects

Two lists were sifted against the creature roster: ~600 animals at 0.93.0 (ten shipped)
and ~390 insects at 0.94.0 (six shipped). These are the closed rejects from both. The bar
they were judged against (**anatomy, not species**) lives in
[architecture.md → "creatures.py — non-human form layer"](architecture.md).

| Pattern | Why |
|---|---|
| Breeds and cultivars — ~40 dog breeds, ~11 cat breeds, 7 horse breeds, 3 cows | A breed is a colour and a size, not an anatomy. `palette` and `size_scale` already cover that ground on the entry that ships. |
| Juveniles — the ~50 `baby *` / cub / pup / kit / fawn / gosling names | Not a form. Scale is a node widget (`size_scale`), so a "baby elephant" is the elephant entry rendered tiny. |
| Colour and region morphs — arctic/black/white/gray wolf, red/gray squirrel, brown/black/polar bear, african/asian elephant | Exactly what `palette_pool` exists for. Wolf's pool already carries five of these. |
| Generic fish — bass, cod, carp, trout, tuna, perch, minnow, snapper, tilapia, ~25 more | One fish-shaped fish. The class ships the ones with a *shape*: anglerfish, pufferfish, seahorse, koi, and now lionfish. |
| Small drab bugs — aphid, gnat, midge, tick, mite, weevil, earwig, silverfish, thrips-scale insects | Nothing legible survives at figure scale. |
| Snake and small-lizard variants — garter, corn, milk, king, rat, boa, copperhead; skink, anole, bearded dragon | Cobra, python and rattlesnake carry the snake anatomy; the lizard slot is held by gecko, iguana, chameleon, monitor and horned lizard. |
| Songbirds — sparrow, robin, finch, wren, starling, oriole, chickadee, canary, budgie, ~15 more | One small perching bird. Cardinal has it. |

Near misses, closed with the incumbent that beat them: **cheetah** (leopard), **jaguar /
panther / cougar / bobcat** (leopard, lynx, tiger), **armadillo** (pangolin owns the
armoured-plate integument), **porcupine** (hedgehog owns spines), **anteater** (aardvark
shipped instead — one long-snouted myrmecophage is enough), **yak / water buffalo / ox**
(bison), **coyote / jackal / african wild dog** (wolf, fox, hyena), **badger / weasel /
mink / ferret** (otter, wolverine, skunk hold the mustelids), **manatee / dugong /
sea lion** (seal, walrus, whale), **turkey** (rooster's wattles, peacock's fan),
**woodpecker** (kingfisher already carries a dagger-billed crested bird), **jumping /
orb-weaver / widow spiders** (tarantula), **luna moth** (moth, and it is a palette),
**millipede** (centipede), **hermit crab** (crab plus a shell), **sea urchin** (hedgehog
and pufferfish own the spine-ball), **swordfish / marlin / sailfish** and **betta**
(thinner differentiators than lionfish, which took the fish slot), **wombat / wallaby**
(koala, kangaroo), **opossum** (raccoon, rat), **gibbon** (orangutan shipped instead),
**dog** (wolf).

**The insect list (0.94.0)** resolved into twelve anatomies, and the ~390 names spent
themselves on ten the class already owns. Its rejection patterns, on top of the ones
above:

| Pattern | Why |
|---|---|
| 59 butterflies and 42 moths — monarch, swallowtail, morpho, admiral, atlas, luna, cecropia, hawk, tiger… | One body, repainted. Wing colour is `palette_pool` and wing *pattern* is slot text; neither is a new entry. `butterfly` and `moth` already carry the two silhouettes. |
| 53 beetles — Hercules, Japanese, click, darkling, longhorn, jewel, dung, June, ground, diving, ~40 more | Three beetles ship (rhinoceros, stag, scarab) chosen for three different pronotal/mandible shapes. The rest are size, gloss and host plant. `jewel`/`metallic`/`golden` beetles are the `iridescent` and `metallic` integument finishes. |
| Castes and life stages — queen / worker / soldier / winged ant and termite, `* nymph`, `* larva`, `butterfly pupa`, male / female mosquito | A caste is not a form, and the node has no caste axis. Where a *larva* is genuinely a different animal it ships on its own (caterpillar, antlion, caddisfly larva at 0.94.0) — the rest are the adult, smaller. |
| Named localities and hosts — American / German / Oriental cockroach, European / Chinese mantis, Colorado potato / asparagus / cucumber beetle, tomato / tobacco hornworm | The name records where it was found or what it eats. Neither renders. |
| The remaining flies — crane, hover, robber, bot, blow, bluebottle, deer, horse, stable, drain, tsetse, ~12 more | `housefly` and `mosquito` ship the order's two mouthparts (sponging and piercing). Everything else is a fly with different leg length. |
| The remaining true bugs — stink, shield, squash, boxelder, milkweed, seed, plant, bed, kissing, leaf-footed | `assassin bug` carries the rostrum, which is what makes a true bug one. A shield-shaped back is already the cockroach's and the beetles'. |
| Bees and wasps — mason, leafcutter, sweat, mining, carpenter, digger, orchard; yellowjacket, mud dauber, potter, sand, spider, ichneumon, three hornets | `honeybee` and `wasp` hold both. The differences are nesting behaviour and gloss. |

Insect near misses, with the incumbent: **damselfly** (dragonfly), **leaf insect** (stick
insect — planar vs linear mimicry is not enough), **katydid / camel / cave / Jerusalem /
mole cricket** (grasshopper; and mole cricket's spade hands are now the `mole`'s),
**treehopper / thorn bug** (a second Hemipteran in one batch, and `assassin bug` took the
slot), **water strider** (leg length is its only feature — the flying-squirrel-patagium
case), **mayfly / stonefly / lacewing / dobsonfly / scorpionfly / snakefly** (dragonfly
holds the lace-winged silhouette; dobsonfly's mandibles are the stag beetle's),
**giant water bug** (assassin bug's beak plus the mantis's grasp), **weevil** (the snout
is real, but it is a small drab beetle — closed under that row above), **earwig**
(forceps, same row), **termite** (an ant at figure scale), **flea / louse / bed bug**
(nothing survives the scale), **grub / maggot / mealworm** (caterpillar shipped as the
soft segmented larva; these are it without the legs, bristles or horn), **glasswing
butterfly** (the `translucent` finish), **death's-head hawkmoth** (a marking on `moth`).

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
| 2 | **Costume text that asserts a body trait against an unpinned random field.** A costume reading "on a hulking frame" can render beside "a very slim build" in the same sentence, because `physique` applies only in Full-character mode while `costume` renders in both. | Measured at 0.90.0, **33 entries** (`Colossus`, `Gollum`, `Jabba the Hutt`, `Space Marine`, `Brook`, …). Not swept, for two reasons. First, the `signature` / `physique` split is *deliberate* — the schema says physique is Full-mode-only, so a randomly-built person wearing the costume is the intended behaviour, and most of the 33 are mascot suits where the suit supplies the bulk regardless of the wearer. Second, a naive regex reported **171** and was wrong: "tiny" on `Trinity` and `Neo` is their *sunglasses*, "enormous" on `Edna Mode` is her *lashes*. Requiring the adjective to modify a body noun cut it to 33. **If this is ever taken up, measure it again from scratch — do not trust the 171.** The four entries fixed at 0.90.0 (`Dexter Jettster`, `Figrin D'an`, `Ithorian`, plus the new Fallout/GoT entries) pin the trait in `signature`, which applies in both modes; that is the pattern to follow. |
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

**Closed at 0.95.0 — the fictional-animal question.** Settled as a mechanism
(`body_plan: "feral"`) rather than an admit/exclude list: six misfiled entries were
retrofitted (`Bantha`, `Tauntaun`, `Loth-Cat`, `Bulbasaur`, `Eevee`, `Jabba the Hutt`)
and 22 shipped (Appa, Momo, Toothless, Falkor, Buckbeak, Fawkes, Aragog, Chocobo,
Cactuar, Drogon, Ghost the Direwolf, Shelob, Fell Beast, Arcanine, Gyarados, Lapras,
Catbus, Haku, Luna, Mothra, King Ghidorah, Reptar). The admission test is in
[architecture.md → "Animal characters split four ways"](architecture.md) and it is
narrow on purpose — it is the creature roster's own *anatomy, not species* bar pointed
the other way, so it admits Appa and Catbus and keeps Simba, Baloo, Sven, Epona and
Shadowfax closed. **A new beast needs a written case that the creature roster cannot
already render its body.** Deferred with reasons, not declined: `Smaug` (belongs to
*The Hobbit*; a one-entry sub-franchise split is not yet worth it) and Sailor Moon's
`Artemis` (the key is taken by the Greek goddess, and a rename is not free on the
gallery side).
