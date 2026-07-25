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

Currently empty — the 0.75.0 pass added the outstanding shortlist.

Add here only when a genuinely iconic, broadly-recognizable character is
confirmed absent.

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
