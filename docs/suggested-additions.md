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

Carried over from the 0.76.0 coverage pass, which opened a batch of previously
unrepresented franchises. These are the next-best candidates in each — worth
adding, but they were below the line for that revision's scope.

| Candidate | Franchise | Why it is worth adding |
|---|---|---|
| Akame | Akame ga Kill | The title character; black uniform, red eyes, a named katana. The franchise currently ships only Esdeath. |
| Kirito | Sword Art Online | The lead; black long coat and dual blades. Franchise ships only Asuna. |
| Lelouch vi Britannia (civilian) | Code Geass | Only the masked **Zero** look ships. The Ashford uniform plus the Geass sigil is a distinct second look. |
| Ainz Ooal Gown | Overlord | Skeletal overlord in dark robes; the only male anchor for a franchise that ships two succubi. |
| Aqua / Darkness | KonoSuba | Both need a disambiguating key (`Aqua` is taken by Kingdom Hearts). |
| Morpheus | The Matrix | Long leather coat and pince-nez mirrored glasses; completes the trio with Neo and Trinity. |
| Columbia | The Rocky Horror Picture Show | Gold sequinned tailcoat and top hat — visually distinct from Magenta's maid look. |
| Rachael | Blade Runner | 1940s-revival suit with padded shoulders and victory rolls; a different silhouette from Pris. |
| Shinobu Oshino / Hitagi Senjougahara | Monogatari | Well-known, but neither has a costume that reads without series context. |
| Sandy Cheeks | SpongeBob | Needs a decision first: the pressurised diving suit with the glass dome hides the head, and the squirrel underneath arguably belongs to the Creature node. |
| Gadget Hackwrench | Chip 'n Dale Rescue Rangers | Purple jumpsuit and goggles, but she is a mouse — same Creature-node question as Sandy. |
| Chizuru Mizuhara | Rent-a-Girlfriend | Top of the popularity rankings, but the canonical look is ordinary modern dress. |

---

## Considered and deliberately skipped

Recorded so they are not re-litigated. Reopen only with a specific reason.

| Candidate | Why skipped |
|---|---|
| Shanna / "Shana the She-Devil" | The available description conflates her with **Red Sonja**, who already ships. Would need a canon-checked jungle-heroine look to be worth a distinct entry. |
| Kimberly (Space Ace) | Obscure, and the name collides with **Kimberly Jackson** (Street Fighter), which is already in the roster. |
| "Magic" (Limbo sorceress) | A misspelling of **Magik**, who ships — including the blue demon-form look as an alternate costume. |
| "The Wolfman" | Already ships as **The Wolf Man** (Universal Monsters). |
| "Catwoman 1940s" | Catwoman already carries four alternate looks, including the Golden-Age emerald gown. |
| Appa / Momo, Luna / Artemis | Non-human companions — these belong to the **Creature** node's domain, not the cosplayer roster. |
| Nala, Simba, Baloo, Shere Khan, Maid Marian, Yogi Bear, Tom & Jerry, Courage, Reptar, Scrooge McDuck, Darkwing Duck | Same rule — quadruped or funny-animal characters with no worn look. The **Creature** node covers this ground. |
| Jessica Jones, Marion Ravenwood, Baby Houseman, Frankie Foster, Peggy Hill, Luanne Platter | Everyday modern dress. Fails the "iconic *and* specific outfit" bar that admitted Trinity, Mia Wallace and Sandy Olsson. |
| Barbarella | Re-confirmed skip (first recorded in the 0.70.0 comic-women review). |
| Sue Storm, Ghost-Spider, Spider-Gwen, Kurisu (Steins;Gate) | Already ship under their other names — **Invisible Woman**, **Spider-Gwen**, **Makise Kurisu**. |
| Alice Abernathy | The *Resident Evil* films only. `Resident Evil` is registered under **Video Games**, so she would be filed in the wrong category; a `Resident Evil (film)` franchise is not worth the split. |
| Anya Forger, Beatrice (Re:Zero), Shinobu Oshino | Small-child or child-bodied characters. Distinct from the accepted child *cosplays* (Dora, the Powerpuff Girls, Tina Belcher), whose looks are ordinary clothing. |
