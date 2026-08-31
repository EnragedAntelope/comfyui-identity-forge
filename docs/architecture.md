# Identity Forge — architecture & contributor reference

A map of how the pack fits together, the data schemas, and the conventions that keep
changes safe. Aimed at anyone (human or agent) extending the data or the engine.

## Working principles (standing maintainer rules)

These are the maintainer's non-negotiable expectations for **every** change. Read them
before adding or editing anything; they override "it would be neat to add".

1. **No bloat, no unwarranted complexity.** Prefer the smallest change that fully solves
   the task. Reuse existing patterns/keys/fields instead of inventing new ones. Do **not**
   add features, options, schema keys, or docs "for the sake of adding things" — every
   addition must earn its place. Keep the engine and data efficient.
2. **No duplication.** Before adding a character/creature/archetype, grep the current keys
   (data is large — see the roster-size note in the gotchas). If the subject already exists,
   don't re-add it: instead check whether the entry needs an enhancement, an alternate
   costume, or another well-known look/variant that isn't represented yet.
3. **Docs stay accurate and in sync.** After data changes, regenerate
   `docs/reference/*.md`. Keep `architecture.md`, `cosplayer-notes.md`, `creature-notes.md`,
   and `usage.md` truthful — update them when behaviour changes, but don't pad them. Leave
   version-stamped audit figures alone (they record a point-in-time analysis, not a live
   count). Keep the **README human-readable and genuinely useful without getting long**.
4. **Tooltips/help stay useful and current.** When a widget's behaviour changes, update its
   tooltip (node `INPUT_TYPES` and the JS extensions) in the same change. No stale or
   filler help text.
5. **Be on the lookout — but curate.** Whatever you are working on, continuously scan the
   whole project for genuinely useful additions or improvements — to any **node, field,
   option, widget, constraint, the engine, or the UX**, as well as new
   characters/creatures/archetypes. Record only the **legit-useful** ones (act on them if in
   scope, otherwise note them as potential to-dos in this file — see the considered/rejected
   notes for the house style); skip anything speculative.
6. **Best practices always.** Maintain good UI/UX and ease of use, security (validate any
   file paths / user input, no unsafe eval, keep the pack offline and zero-dep), sound
   coding, and clean git/GitHub hygiene (focused commits, no PR unless asked).

## Repo layout

```
data/        cosplayers.py · creatures.py · fields.py · templates.py (archetypes/outfits)
             · constraints.py · user_options.py (runtime JSON merge)
nodes/       identity_forge.py (engine + main node) · identity_forge_cosplayer.py
             · identity_forge_creature.py · identity_forge_archetype.py
             · identity_forge_modifier.py · identity_forge_vault_{save,load}.py
js/          identity_forge.js · identity_forge_cosplayer.js · identity_forge_creature.js
             · identity_forge_vault.js (ComfyUI frontend extensions)
tests/       validate_data.py (static integrity) · test_engine.py · test_creature.py
             · test_vault.py · preview_cosplayer.py
scripts/     generate_reference_docs.py (regenerates docs/reference/*.md)
             · generate_js_data.py (regenerates the GROUP_ORDER/FIELD_TO_GROUP/GENDER_POOLS
               block in js/identity_forge.js, and the COSPLAYER_FRANCHISES block in
               js/identity_forge_cosplayer.js)
docs/        usage.md · cosplayer-notes.md · creature-notes.md · architecture.md (this file)
             · reference/ (GENERATED indexes — see below)
```

### Generated reference indexes (`docs/reference/`)

`docs/reference/cosplayers.md`, `creatures.md`, and `archetypes.md` are a **generated**,
human-readable catalogue of the full roster (names + compact flags — source gender, size
scale, masked, alt-costume count, signature prop), so the data can be reviewed without
opening the large data modules. They are produced by `scripts/generate_reference_docs.py`
and hold no source-of-truth data.

**Keep them in sync:** after adding or changing entries in `data/cosplayers.py`,
`data/creatures.py`, or `data/templates.py`, run `python scripts/generate_reference_docs.py`
and commit the refreshed files. `--check` regenerates in memory and exits non-zero if the
committed docs are stale (suitable for CI / a pre-commit guard).

### Sample galleries (`gallery/`)

Three sibling galleries — `cosplay/`, `archetypes/`, `creatures/` — each publishing a
sample render per roster entry to GitHub Pages. Full detail in
[gallery/README.md](../gallery/README.md); the parts that constrain future work:

- **Images live only on `gh-pages`.** `gallery/.gitignore` blocks `images/` on `main`, so
  a clone never pulls hundreds of megabytes. Pages, scripts and manifests live on `main`.
- **The manifest is rebuilt from what is published, never from the source folder.** This
  is the whole safety model: your source folder only adds or overwrites, so an entry you
  did not supply an image for is never touched and never deleted. The removed `deploy.py`
  got this backwards and would have deleted the entire gallery if pointed at a folder of
  a few new images.
- **Publishing uses `git worktree`, not `stash` + `checkout`.** The current working tree
  is never touched. Deletion requires an explicit `--prune-orphans`, and even then only
  removes images matching no roster entry at all.
- **The three copies are byte-identical outside their docstring and `GALLERY CONFIG`
  block.** This is copy-and-adapt by design (three independently-published sites, no
  shared package), so **an improvement to one script must be ported to the other two** —
  `tests/test_gallery.py::CopiesStayInSyncTests` fails until it is. `BatchLauncherTests`
  guards the `.bat` launchers (every exit pauses, no parenthesised `if` blocks, ASCII
  only, CRLF via `.gitattributes`).
- Adding a fourth gallery is a folder copy plus one config block per file; the checklist
  is at the bottom of `gallery/README.md`.

Pack is **V3 API** (`comfy_api.latest`), category `conditioning/character`, **zero deps**,
fully offline. The engine half of every node is a pure function importable without ComfyUI
(that's how the tests run headless). Pillow is required *only* by the gallery publishing
scripts, which are maintainer tooling and never imported by a node.

## A working "Fix node (recreate)"

That menu entry is not a ComfyUI feature. ComfyUI-Manager contributes it, and on frontend
1.47 its implementation throws partway through:

```
TypeError: t.findInputSlot is not a function
  at LGraphNode.connect
  at node_info_copy   (node_fixer.js, reconnecting the inputs)
```

Node ids are strings now. Manager calls `src.connect(slot, dest.id, name)`, and `connect`
only resolves its second argument to a node when that argument is a *number*, so a string
id sails past the lookup and `connect` calls `findInputSlot` on it. The callback creates
the replacement first and removes the original last, so the exception leaves both on the
canvas: the original still wired up, the replacement floating unconnected on top of it.
That is the whole of the reported bug, and it is not specific to this pack — it happens to
any node with a connected input, in any pack (reported upstream; see the issue link in
`docs/worklog/2026-08-03-revision-0.85.md`).

`js/identity_forge_recreate.js` installs a correct one for Identity Forge nodes and takes
the broken entry out of their menu. Nothing global is patched. Ported from
[comfyui-stylebook](https://github.com/EnragedAntelope/comfyui-stylebook)'s
`stylebook_recreate.js`, which diagnosed and fixed the same bug first.

Three rules make a recreate correct, and each is a bug avoided:

1. **Pass the node object to `connect()`, never its id.** Ids are strings.
2. **Restore widget values by name, never by index.** Recreating a node is what you do
   *because* the schema changed, so an index-based copy writes every value into the wrong
   widget from the first added or removed input onward. A value that is no longer valid
   for a combo is dropped and reported, not forced: writing an invalid value produces a
   node that fails prompt validation over something the user never chose.
3. **Reconnect by slot name, never slot number**, for the same reason.

Remove the original *before* reconnecting. An input holds one link, so reconnecting first
fights the link still attached to the old node.

The menu entry is installed as an own property on the node instance, not as another
prototype wrapper. Every pack that adds menu entries wraps the prototype, and the last
wrapper installed runs its additions last; an instance property shadows the whole chain,
so we always see the finished option list regardless of extension load order.

**One addition beyond the Stylebook port, specific to this pack's widget shape.** The main
node rebuilds `node.widgets` into ~66 field combos plus ten button widgets (two master
buttons, one collapse header per field group — see `js/identity_forge.js`
`setupIdentityForge`), and picking a `gender` swaps the option list of six other widgets
via a wrapped callback. `copyWidgetValues` skips button widgets outright (a toggled
collapse header's *name* changes at runtime, which would otherwise report every collapsed
group as a dropped widget on every recreate), and after copying values the recreate
re-invokes the fresh node's `gender` widget callback so the gender-divergent widgets'
option lists get re-scoped to the restored gender — a value copy alone restores the
correct *value* but leaves the fresh node's default "Any" pool as the *option list* until
the user touches gender again.

**A known, narrow limitation, inherited from the port rather than introduced by it.** If
a widget has been right-click-converted to an input socket *and* has something wired
into it, the fresh node reverts that widget to its normal, unconverted form, so the link
finds no matching socket and is silently dropped (no console warning — `snapshotLinks`'s
reconnect loop only guards `slot >= 0`). Verified live against the `stylebook_with_
identity_forge` example, whose `IdentityForge` node has `seed`/`gender`/`wardrobe`/
`set_all_fields` converted this way (none actually linked in that file, so the case
itself wasn't triggered, only confirmed by inspection). Not fixed here — Stylebook's own
`stylebook_recreate.js` has the identical gap and it has not been a reported problem
there either.

## Nodes & data flow

The four preset nodes each emit a grouped-JSON **`character_json`** string and chain through
an optional **`upstream`** input. They wire into IdentityForge's single **`archetype_json`**
socket. On overlap, the node **closest to IdentityForge wins** (downstream wins); a node set to
`None` emits `{}` and passes its upstream through. `merge_preset_documents` (deep-merge, incl.
`_meta`) is the chaining primitive.

```
Archetype ─▶ Cosplayer ─▶ Creature ─▶ Modifier ─▶ IdentityForge ─▶ prompt_text + prompt_json
```

- **IdentityForge** ([nodes/identity_forge.py](../nodes/identity_forge.py)) — the engine. Many
  lockable dropdowns + control toggles → randomize → constraints → prose + JSON. Entry point
  `generate_character(...)`; widget schema in `define_schema`.
- **Cosplayer** → `build_cosplayer_json`: a character's `costume` becomes the hidden
  `outfit_description` lock; `signature` (hair/eyes) always applied; `physique` only in *Full
  character* mode; `covers_face`/`mask`/`prop` handled here.
- **Creature** → `build_creature_json`: emits a `Species & Anatomy` group + `_meta`
  (`form`, `suppress_groups`, `suppress_fields`).
- **Modifier** → prepends a descriptor to one field or a whole group.
- **Vault Save/Load** → persist a generated `prompt_json` under `ComfyUI/user/identity_forge/`.
  The frontend's list/preview/delete/rename routes are registered by `_register_vault_routes()`
  in `__init__.py`. Path safety is `sanitize_name` + `_entry_dir` (resolve, then require the
  parent to *be* the vault root), which blocks `..` and absolute-path escapes. **0.72.0 added a
  content-type check on the two mutating routes**: `request.json()` parses any body regardless of
  content type, and a `text/plain` POST is a CORS-*simple* request a browser sends cross-origin
  **without a preflight** — so any page open while ComfyUI ran could have deleted or renamed
  saved characters. Requiring `application/json` forces a preflight, which fails since these
  routes send no CORS headers. `_json_body()` also turns a malformed body into a 400 instead of
  letting it raise into a 500. The pack's own JS already sent the right header, so the UI was
  unaffected. Graph execution never touches these routes.
- **Turnaround** ([nodes/identity_forge_turnaround.py](../nodes/identity_forge_turnaround.py),
  rewritten 0.99.0) - a reference-set builder. It takes a **resolved** character
  (`IdentityForge.prompt_json`) on `character_json` and emits every camera view of it as a
  **list**, so one queue renders the whole set. See "The Turnaround owns only the camera"
  below for why it is shaped that way.

### The Turnaround owns only the camera (0.99.0 rewrite)

The 0.98.0 draft was a second Identity Forge. It re-exposed six of the main node's steering
widgets, passed `"Random"` for the other ~75 fields, pinned `shot_type` to the view chosen by
an auto-incrementing `index`, and carried its own `seed`. Three things were wrong with that,
and only the first was visible:

1. **Duplicated controls with no stated winner.** Six widgets appeared on both nodes, and the
   other seventy-odd silently did not appear at all — so choosing the Turnaround meant losing
   every field lock, `set_all_fields`, and the vault, with nothing on the node face saying so.
   Its `seed` was a *third* seed, competing with the one on every upstream preset.
2. **The identity was not actually fixed.** `index` advances between queues, so a complete set
   took N queues — and any upstream preset left on `control_after_generate="randomize"`
   re-rolled the character between them. A "turnaround" of six different people.
3. It needed the ComfyUI#11905 NaN signature purely to work around its own `index` widget.

The rewrite deletes the questions rather than documenting answers, on one line:
**Identity Forge owns the character and the scene; the Turnaround owns only the camera.**

- **Input is a resolved document, not a preset.** `character_json` takes `prompt_json` —
  self-describing by contract, because it is exactly what Vault Save writes and Vault Load
  feeds back through `archetype_json` (see "a self-describing `prompt_json`", 0.92.0). Every
  field is already concrete, so re-running the engine over it with only `shot_type` overridden
  reproduces the character exactly and the seed cannot move anything. All the configuration a
  user wants is on the main node, where it always was; nothing is re-exposed.
- **Output is a list.** Both outputs set `is_output_list=True`, so ComfyUI runs everything
  downstream once per view (`execution.py` → `merge_result_data`) and shorter inputs — the
  negative prompt, model, latent — broadcast off their last element (`slice_dict`). One queue,
  the whole set, from a single upstream resolution. Which also means an upstream node left on
  `randomize` is now a *feature*: each queue is one new character × N coherent views.
- **No `fingerprint_inputs`.** With no auto-advancing widget and no RNG the node is a pure
  function of its inputs, so ComfyUI's normal caching is correct — see the counter-example
  note under "Seeded nodes re-roll every queue".
- **`shot_type` is composed, not picked.** That field mixes distance ("full body shot"),
  orientation ("side profile") and lens in one pool, so a turnaround cannot express both halves
  by choosing a value. `compose_shot()` emits `"<distance>, <rotation>"`. The free text survives
  only because `shot_type`'s two gender pools are identical, which makes `_gender_permits` pass
  anything — `test_composed_shots_are_free_text_the_gender_gate_lets_through` pins that, since a
  future divergence would silently drop every composed shot.

**The back view omits the face (0.99.0, from a live render).** The first turnaround rendered
from the new node came back with the subject's head turned: the prose still carried "bright
blue downturned eyes ... deep red lip colour ... a broad smile", and a t2i model draws what it
is given, so it rotated the head to show them. `_FACE_ONLY_FIELDS` - the whole `Face` and
`Makeup` groups plus `facial_hair` and `expression`, **derived from `FIELD_DEFINITIONS` rather
than hand-listed** so a field added later is covered - is set to the engine's `"None"` omit
token on that view only. Three things this deliberately does not do: it does not touch hair,
costume, build or ear jewellery (all of which read from behind); it does not touch the mask,
which is `_meta` prose rather than a Face field, so a helmeted cosplayer keeps their helmet;
and **it never negates**. Writing "the face is not visible" would name the face and draw one -
the same rule that rewrote nine feral clauses at 0.96.0 (see "Never negate in prompt data").
Only `view from directly behind` qualifies: `from slightly behind and to the side` still shows
a cheek and jaw, and stripping it would discard description a viewer can see.

**What the back view still cannot fix, deliberately.** A costume is ONE authored free-text
string, so a chest-front detail inside it is drawn on the back too - measured on a live
Supergirl render, where "a blue crop top with the Superman S-shield" put the shield on her
back. Suppressing it would mean regex-parsing authored prose to guess which clause faces
front, which is the failure this repo has already paid for twice: `_POCKETLESS_GARMENT_RE` is
an incomplete allowlist to this day, and the AGENTS.md "costume text that asserts a body trait"
gap carries the standing warning that its naive regex reported 171 and was wrong. The only
correct fix is structured front/back costume data
across the whole roster, which is not worth one artifact on one view of six. Left as-is on
purpose.

Two engine-facing traps this rewrite hit, both silent, both now pinned by tests:

- **Controls do not share the fields' vocabulary.** Filling the engine call with `"Random"` for
  every input looks right and is not: `"Random"` is nonsense to `size_scale` (logged and
  ignored) and, worse, is *not* `"Any"` to `gender` — so `execute` never falls through to the
  document's `_meta.gender` and re-rolled it, turning a woman into a man between the two nodes.
  The node now builds its call from `IdentityForge.define_schema()`'s own **defaults**, which
  gives every field `"Random"` and every control its defer value, and self-maintains when a
  control is added later.
- **`_meta.wardrobe` is recorded but not honoured on the `archetype_json` path.** That is
  deliberate for a *preset* (`_parse_archetype_json` explains it: neither `wardrobe` nor
  `hair_color_scope` has a "defer to the preset" sentinel, so honouring them would let a
  recalled character override a live widget). But this node is **replaying a finished run**, not
  steering a new one, and has no such widgets to override — so it restores both off `_meta`.
  Measured before the fix: a character generated with `wardrobe: "Any"` (which unlocks
  mixed-gender features) came back rebuilt under "Match gender" in **150 of 150** sampled seeds.
  **The vault had the same hole; fixed at 0.102.0** — `IdentityForgeVaultLoad` recall of a
  `wardrobe: "Any"` character used to rebuild a different person for exactly this reason. Fixed
  by the "Auto (preset)" sentinel on the two widgets (see "Vault recall and the control
  sentinels"); the Turnaround did not wait, because it has no widget to add one to.

### Vault recall and the control sentinels (0.102.0)

`wardrobe` and `hair_color_scope` are control fields — they live only in `_meta`, never in
the body, and `execute` reads them from the widget, not from a wired character. That is
correct for a *preset* (a preset must not override a live widget), but wrong for the
vault, which is replaying a finished run that already chose those controls.

The fix is the `"Auto (preset)"` sentinel on both widgets. When the widget is set to it,
`execute` defers to the value `_parse_archetype_json` surfaced under `__wardrobe__` /
`__hair_color_scope__` (the saved `_meta.wardrobe` / `_meta.hair_color_scope`); otherwise
it keeps the widget default. The sentinel is never passed through to generation, and
`_parse_archetype_json` ignores an `"Auto (preset)"` value stored in `_meta` (a vault save
can only ever store a concrete choice), so the 0.91.1 trap — a recalled character silently
overriding the user's toggle — cannot recur.

Recall workflow: load a saved character with `wardrobe` and `hair_color_scope` both set to
`Auto (preset)` to replay its exact saved controls. Any other widget value is a deliberate
override and wins. `tests/test_vault.py::VaultRecallControlDeferralTests` pins the four
cases (faithful recall, default-widget divergence, exposed control meta, and no-archetype
fallback).

### Adding a whole node — the registries it has to join (0.98.0)

Adding a node class is not enough; it is invisible or half-tested until it is named in
each of these. The Turnaround shipped its first draft missing the last two.

1. `__init__.py` — both the `try`/`except ImportError` import pair **and**
   `IdentityForgeExtension.get_node_list()`. Miss the second and ComfyUI never loads it.
2. `README.md`'s node table and `__init__.py`'s module docstring ("Exposes N nodes").
3. `scripts/dump_frontend_fixtures.py` — `_NODE_CLASSES`. The fixture is what the jsdom
   suite builds fake nodes from, so a node absent from that map has **no** frontend
   coverage and its `--check` gate silently passes forever.
4. `fingerprint_inputs` returning NaN **if** any widget sets `control_after_generate` —
   see "Seeded nodes re-roll every queue" below. The trigger is the auto-advancing
   widget, not the presence of a seed.
5. A tooltip on **every** input. There is no lint for this; the frontend fixture records
   widget names and defaults, not help text, so only `tests/test_*.py` can hold the line
   (`test_every_widget_carries_a_tooltip`).

## fields.py — the field engine

`FIELD_DEFINITIONS` is an `OrderedDict[name -> {group, female_options, male_options, optional,
…}]`. Notes:

- **Control fields** carry `"control": True` (`gender`, `hair_color_scope`, `location_setting`):
  read from their toggle, never randomized, never described. `_CONTROL_FIELDS` collects them.
  They are **widget-owned**: `execute` filters `_CONTROL_FIELDS` out of `archetype_locked`, so a
  preset cannot set one from its `_meta`. `gender` is the exception, and `wardrobe` /
  `hair_color_scope` joined it at 0.102.0: each widget carries an `"Auto (preset)"` defer
  sentinel, so `execute` reads the saved value back by name (from `__wardrobe__` /
  `__hair_color_scope__` surfaced by `_parse_archetype_json`) only when the widget is set to
  it — the widget default otherwise wins, so a recall never silently overrides a deliberate
  user choice. `tests/test_engine.py::HairScopeTests` pins the scope; `tests/test_vault.py::VaultRecallControlDeferralTests` pins the recall.
  A user's `user_options.json` `hair_color` additions extend the option pools but not
  `natural_hair_colors`, so they are randomizable only under `Full spectrum` (documented in
  `docs/usage.md` and `data/user_options.py`); lockable by hand under either scope.
- **Hidden fields** (`outfit_description`, `held_item`): free-form prose locks, no widget;
  `_HIDDEN_FIELDS` / `_PRESET_HIDDEN_FIELDS`.
- **Gender-divergent fields** are the only ones whose female/male pools differ: **`bust`,
  `facial_hair`, `makeup_style`, `hair_accessory`** (`hair_accessory` gives random women the
  full feminine range but random men only a small unisex set, so a bow never lands on a random
  male). These (and only these) are mirrored in the JS `GENDER_POOLS` for live gender-swap —
  **edit both Python and JS when you touch them**.
- **Absence model (important).** `_is_absent(v)` treats `""`, `"None"`, `"Random"`, `"none"`,
  any `"no …"`, and `_ABSENCE_EXACT` (`bare nails`, `clean shaven`, `natural bare`,
  `bare natural lips`) as "omit from prose". `_EXTRA_ABSENCE` maps accessory fields to their
  canonical absent token + a base probability — the `accessory_density` control injects it so
  portraits aren't over-accessorised. **Those absent tokens must stay in the pools** (the
  density logic needs them); they are merely *hidden from the widget*.
- **Widget building** (`define_schema`): each field combo = `["Random"] + <real options, with
  `_is_absent` values filtered out> + ["None"]`. Result: exactly one "omit" affordance
  (`None`). Picking `None` == any in-pool absent value == omit.
- **Weighted family pick (the bias-safe growth channel).** Fields registered in `FIELD_FAMILIES`
  do **not** use a flat `rng.choice`: `_pick_family_weighted(field, pool, rng)` first draws a family
  (weighted by `weight`, frozen to each family's *original* variant count), then a variant uniformly
  within it. So adding a variant subdivides its family's share instead of inflating it, and the
  field's top-level distribution never shifts — the safe way to enlarge a flat field without biasing
  randomization. Because each weight equals the family's original size, the pick reproduces a flat
  uniform draw until new variants are added. Registered fields: `hair_style` (`HAIR_STYLE_FAMILIES`),
  `hair_color` (shade neighbourhoods; its `vivid` family is exactly the set the "Natural only"
  scope filters, so the pick stays uniform under both scopes — keep new fashion shades in `vivid`),
  `expression`, `mood`, `pose`, `lighting`, `location` (each `<FIELD>_FAMILIES` in `data/fields.py`).
  The picker intersects each family's variants with `pool` and drops empty families, so upstream
  filtering still composes — e.g. the `location_setting` Indoor/Outdoor/Studio scope, or a hair-length
  constraint. The flat option list still drives the widget (every variant lockable); `validate_data`
  checks **every** `FIELD_FAMILIES` entry partitions its field's options exactly. New `hair_style`
  variants must also be slotted into the relevant `data/constraints.py` length lists
  (`_LONG_HAIR_STYLES`, the pixie exclusion) so they're culled on short hair like their siblings.
  **This is the rule `cornrows` and `bantu knots` escaped until 0.72.0** — they were in no length
  list at all, so a 4000-seed sweep put cornrows on `buzzed very short`/`very short` 210 times and
  bantu knots on a buzz or pixie 86 times. Both are now in `_LONG_HAIR_STYLES`, and `box braids` +
  `bantu knots` joined the pixie exclusion. Note the trap that hid them: the texture note in the
  gotchas says braids, locs, cornrows and bantu knots "read fine on any texture and stay unpaired"
  — true, but that is the **texture** axis. Length is a separate gate, and a style can be free on
  one and constrained on the other. The pixie list stays deliberately narrower than
  `_LONG_HAIR_STYLES`: `afro`/`twist-out` (a pixie-length TWA), `locs` (starter locs) and
  `cornrows` are all real at that length.
- **`pose` values are participle phrases, and must stay performable (0.66.0 doctrine).**
  Two separate rules, both learned the hard way.
  *Grammar:* the prose renders `"{subject} is {pose}."`, so every value has to complete that
  frame — a present participle (`standing naturally`), a past participle (`perched on the edge
  of a seat`), or a preposition introducing a noun (`in a confident power pose`). **Never a bare
  noun phrase**: three values had shipped since the field was added, reading "She is arms relaxed at the sides."
  They were reworded in place at 0.66.0 (same slot, same family weight, zero bias impact).
  `PoseGrammarTests` pins the rule; a new past-participle opener must be added to its allowlist,
  which is deliberate friction.
  *Performability:* a pose quietly assumes the subject has the body part it reaches for.
  `running one hand through the hair` needs scalp hair; `posing with hands in pockets` and
  `touching the collar with one hand` need a worn garment. A masked/hooded/bald character has
  neither hair nor, if `covers_body`, pockets — the Moogle-cosplay-does-a-hair-flip bug (~28% of
  the cosplayer roster was affected, ~1 in 9 of their renders). `_performable_poses` in
  `nodes/identity_forge.py` narrows the pool; it reads `hair_length` and `outfit_description`
  straight out of `resolved` (pose is field index 67, they are 24 and 46, so both are already
  final — which also catches an auto-detected `_FULL_COVER_RE` shell for free) and takes only the
  `covers_*` flags as parameters. **Both bald routes count**: the engine's own `"bald"`
  `hair_length` *and* the Cosplayer node's `_BALD_SUPPRESS`, which locks the scalp fields to an
  *absent* value instead (never `"bald"` — that option is male-only and would be gender-gated).
  *The split that makes it bias-free:* the old single `gesture` family (weight 4, 6 variants) is
  now three families, because **dropping part of a family leaves its full weight on the
  survivors** (the trap documented for `LIGHTING_FAMILIES` at 0.64.0) — only whole families may
  be excluded. Sub-family weights must be **proportional to variant count** or the split itself
  re-weights the field; splitting 3/2/1 needs 2/1.33/0.67, so every pose family weight is scaled
  ×3 to keep integers. Each pose still sits at exactly its old probability (gesture values at
  1/27, `standing` at 5/126, …), proven analytically by `PoseFamilyTests` and verified by Monte
  Carlo (worst deviation 0.068pp at N=400k, inside sampling noise). **Seeds drift for `pose`**:
  the distribution is identical but `rng.choices` sees 8 families instead of 6, so a given seed
  can land on a different pose. Accepted, same as the 0.64.0 `_repick` fix.
  `HAIR_DEPENDENT_POSES` / `GARMENT_DEPENDENT_POSES` are derived *from* `POSE_FAMILIES`, never
  hand-listed, so they cannot drift out of sync.
- **`shot_type` is camera-only (0.63.0 doctrine).** Every value describes the *camera* —
  distance, height, subject orientation, or lens — and never introduces scene content. Values
  that placed an object or a second person in frame were removed (`shot through a doorway /
  window / foliage`, `reflected in a mirror / shop window`, and `over-the-shoulder perspective`,
  which in film grammar puts the camera behind *another person's* shoulder and renders an
  unwanted second figure). **Keep it that way**: a "shot through X" value re-introduces X into
  every scene it lands in, and is also what forced location↔shot coherence rules. Because the
  surviving values imply neither indoors nor outdoors, the *only* location rule needed is the
  void-backdrop pair in `constraints.py` (`_VOID_BACKDROPS` × `_ENVIRONMENT_SHOTS`): a seamless
  sweep has no environment to establish or reveal. `location` is that rule's **trigger**, not its
  target, so the picked place always stands and the camera adapts; a *locked* environment shot
  instead re-rolls the location via the engine's contrapositive repair. Under
  `location_setting = "Studio / solid backdrop"` the location pool is exactly the four void
  backdrops, so a locked environment shot has nowhere to move and degrades to warn-and-keep (the
  lock wins) — expected, not a bug. `shot_type` is deliberately **not** in `FIELD_FAMILIES` and
  carries no `weights`, so exclusion re-picks stay flat-uniform. Most values leave orientation
  unstated, which text-to-image models render frontally — a retained, intentional bias toward
  facing the camera (only 2 of 26 are true rear views).
- **`lighting` is bucketed against `location` (0.64.0 doctrine).** `shot_type` solved its
  location-coherence problem by deleting scene content; **lighting cannot follow it**, because
  "golden hour sunlight" is inherently outdoors and there is no wording that isn't — and the
  `daylight` family alone is 14/38 of the field's weight, so purging place-implying values would
  gut the field. Instead `data/fields.py` defines three buckets beside `OUTDOOR_LOCATIONS`
  (`OUTDOOR_ONLY_LIGHTING`, `INDOOR_ONLY_LIGHTING`, `VOID_ALLOWED_LIGHTING`), and
  `data/constraints.py` expands them into **165 generated exclusion rules** — one per location,
  since `excludes_values` takes a list. Indoor locations are *derived*
  (`all − OUTDOOR_LOCATIONS − STUDIO_BACKDROPS`), so a new location is bucketed automatically;
  this is why `constraints.py` imports `fields.py` (no cycle — `fields` imports nothing back).
  As with the backdrop rule, `location` is the **trigger**: the place stands and the light adapts,
  while a *locked* light re-rolls the location via contrapositive repair.
  **Split whole `LIGHTING_FAMILIES` at a time — this is the bias constraint, not a style
  preference.** `_pick_family_weighted` intersects a family's variants with the pool but keeps the
  family's **full frozen weight**, so a family reduced to two or three survivors would concentrate
  its entire share onto them. Bucketing whole families means a filtered family drops out and the
  rest stay exactly proportional. The seam the data already encodes: the `daylight` family is
  open-sky light, and **the `window` family IS indoor daylight**. Void backdrops therefore allow
  the `studio` family and nothing else — admitting a couple of neon/gel values would hand the
  8-variant `neon` family its full weight over 2–3 survivors. Expect the *marginal* distribution
  to look daylight-poor (~11% vs ~37% before): 116 of 165 locations are indoor, and daylight
  previously landed on them incoherently. Set `location_setting = "Outdoor"` for sunny looks.
  **This is a deliberate trade, revisit only if `LIGHTING_FAMILIES` weights are ever rebased.**
  `constraints.py`'s `_VOID_BACKDROPS` (0.65.0) is just `sorted(STUDIO_BACKDROPS)` now that the
  module imports `fields.py` anyway — it used to hand-duplicate the four strings.
- **`lighting`'s `studio` family is lighting-only, not camera framing (0.65.0).** The former
  `'Dutch angle with hard shadows'` value mixed a pure camera concept (frame tilt) into a
  lighting field — the same class of wart the 0.63.0 shot_type camera-only doctrine would have
  caught if it lived there. Reworded to `'harsh angled spotlight casting long hard shadows'`
  (light direction, not camera framing) **in the same slot at the same family weight** — zero
  bias impact, no pool/weight change to either field. `shot_type` already has its own,
  unaffected `'slight Dutch angle'` camera-tilt option; migrating the lighting value there
  instead was considered and rejected because it would have changed `shot_type`'s own pool and
  weights, the exact risk flagged when this wart was first noticed.
- **Constraint re-picks go through `_repick`, not `_weighted_choice` directly (0.64.0).** A
  re-pick must draw the way the *initial fill* would. `_repick(field_name, field_def, pool, gender,
  rng)` routes `FIELD_FAMILIES` fields to `_pick_family_weighted` and everything else to
  `_weighted_choice`. Calling `_weighted_choice` directly is a bug for a family field: it is flat
  when the field has no `weights` map, so an exclusion silently rebalanced the survivors by raw
  variant count (it was skewing `neon` by 6.4 points on the filtered indoor lighting pool, and had
  been quietly doing the same to `hair_style` re-rolls for several releases). Note the engine
  re-picks **only the rejected value** rather than redrawing the character, so the final marginal
  is a mixture — `P_init(v)·[v ok] + P_init(reject)·P_repick(v)` — landing within ~2.5pp of the
  pure conditional, and erring *low* on a filtered family. Making it exact would require
  full-rejection resampling, which changes the RNG stream shape and therefore every seed. Don't.
- **Per-value draw weights (`weights` / `male_weights`).** A field definition may carry two
  draw-weight maps consumed by the shared `_weighted_choice(field_def, pool, gender, rng)` helper.
  `"weights": {value: number}` biases the draw for **every** gender; `"male_weights": {value: number}`
  is a **male-only overlay** that wins on key collision. Weights may be **floats**, so a single value
  can sit *below* its peers' implicit weight of 1 — this is how a value is made rare without touching
  the others (`eyebrows` weights `bleached` at `0.2` ≈ 2%; `hair_texture` male-weights `silky and glossy`
  at `0.3` so salon-shine hair is rare on random men but still lockable; `makeup_style` still leans men
  `2×` toward `no makeup`). Missing values weigh 1; the engine uses one `rng.choices` call so the RNG
  stream shape matches a flat pick. `_weighted_choice` is used by both the initial random fill **and**
  the constraint engine's exclusion re-picks, so a down-weighted value stays rare even after a
  masculine-trim (or other exclusion) re-roll. Never duplicate a value inside an options list to weight
  it — the validator rejects duplicates and checks every weight key is a real option (positive number).

## cosplayers.py — characters as a worn look

### Adding a character — curation checklist

The standing rules for **every** character addition (mechanics are detailed below the
list; the working principles at the top of this file also apply):

1. **Only if it fits the project.** Add a character when it has a describable, canonical
   *worn look* that suits a character-costume generator. Skip subjects with no real costume
   (e.g. an infant, an off-screen/faceless entity) rather than inventing one.
2. **No duplicates — but don't just skip a dupe.** Grep the existing keys first (the roster
   is large). If a character you were asked to add already ships, do **not** silently skip it:
   (a) **verify the existing entry is strong, accurate and solid** and tighten it if not, and
   (b) check for any **iconic variant look or alternate costume** that isn't represented yet
   and add it (as a `costumes` alternate, or by enhancing the entry) — e.g. Poison Ivy's
   Arkham look alongside the classic, or Harley Quinn's multiple signature looks. Only leave
   it untouched if the entry is already solid and no notable variant is missing. Note what you
   did (enhanced / added variant / left as-is) in the commit message.
3. **Correct sub-franchise.** Set `franchise` to the specific sub-franchise the look comes
   from, and map any new franchise into `_CATEGORY_FRANCHISES` so `random_scope` works.
4. **Masks & props identified and accurate.** A fully-covered head → `covers_face: True` +
   a separate `mask`; a scalp-enclosing hood/lekku/montral → `covers_hair`. A *truly iconic*
   held item → `prop` (worn items never go in `prop`). Describe each richly and correctly.
5. **Canonical, well-described look.** Costume text is worn items only, plain-ASCII, lowercase
   with a leading article; coloured/alien skin is skin-native; non-standard eyes use `eyes`
   (a short noun phrase only — see the `eyes` gotcha; asymmetric details go in the costume).
   Use only valid `FIELD_DEFINITIONS` values in `signature`/`physique`.
6. **Disambiguate colliding keys.** A name that clashes with an existing dict key needs a
   parenthetical key (`"Christie (Dead or Alive)"`, `"Red (Pokemon)"`); duplicate keys
   silently collapse and `validate_data` flags them.
   **A parenthetical may never name something narrower than the entry's `franchise`.**
   It may *abbreviate* the franchise (`"Mai (Avatar)"` under `Avatar: The Last
   Airbender`), or name a character, alter ego, team, version or medium
   (`"Blue Beetle (Ted Kord)"`, `"Obi-Wan Kenobi (Force Ghost)"`, `"Duke Nukem (video
   game)"`). It must not name an *installment* of a franchise this pack has
   consolidated — the dropdown would then contradict `docs/reference/cosplayers.md`,
   which is the roster's public face. `"Joker (Persona 5)"` under the franchise
   `Persona` was the one shipped violation, renamed to `"Joker (Persona)"` at 0.90.0;
   `validate_data.py` now rejects any parenthetical that extends its franchise.
   Strict *equality* was considered and rejected: it would force
   `"Mai (Avatar: The Last Airbender)"` and `"Duke Nukem (Duke Nukem)"`, which reads
   worse in the dropdown than the problem it solves.
   Renaming a key is cheap on the data side but **not** free on the gallery side:
   images are keyed on the entry name, so a rename must also move the file on
   `gh-pages` and rename the key in `gallery/render_manifest.json`. The `entry_hash`
   covers the entry *dict*, not the key, so no re-render is needed.
7. **Validate before commit.** Run `python tests/validate_data.py`, the unittest suite, and
   `python scripts/generate_reference_docs.py`, and commit the refreshed reference index.

#### Judgement calls that keep recurring

Rules learned from curation passes, kept here rather than in the backlog file so they
outlive any one candidate list.

- **A small *person* is excluded; a person in a small-*creature* suit is not.** The
  child-bodied rule (which keeps Anya Forger and Beatrice off the roster) was misapplied
  to yordles once and had to be reversed. Teemo is not a child — he is a mascot suit: a
  furry animal head and body with a real, describable uniform worn over it. That is the
  `covers_face` + `covers_body` + `mask` shape roughly **50 entries already ship on**
  (Pikachu, Moogle, Bugs Bunny, the TMNT, Mr. Krabs…), and `size_scale: "tiny"` handles
  a three-foot subject. Ask *"is this a small person, or a person in a small-creature
  suit?"* — only the first is excluded.
- **Animal characters split four ways (0.95.0; was three).** (a) A *generic* animal that
  the name adds nothing to — a wolf, a lion, a bear — **Creature node**. (b) Full mascot
  suits (Pikachu, Mr. Krabs, Rancor, Wampa) — ordinary entries, mechanism long settled.
  (c) Animals wearing real garments (Sandy Cheeks, Gadget Hackwrench, Maid Marian) — also
  ordinary entries: `covers_body: True` with the animal head written into `mask`. (d) A
  **named fictional beast whose canonical body the creature roster cannot render** —
  Appa, Toothless, Catbus, Buckbeak, Mothra — an ordinary roster entry carrying
  `body_plan: "feral"` (see below).

  The old three-way rule sent (d) to the Creature node on the grounds that it "already
  covers this ground exactly". **It does not, and four entries had quietly proved it:**
  `Bantha`, `Bulbasaur`, `Eevee` and `Loth-Cat` were shipping in the roster in violation
  of the rule, plus `Jabba the Hutt` and `Mynock`. `data/creatures.py` is a taxonomy of
  *generic anatomies* with no name and no `franchise` key, and its own bar (0.93.0,
  "anatomy, not species") would reject Appa as a bison with a `palette` — Appa is
  six-legged, chalk-white, and carries a brown arrow. So Appa was producible by neither
  node, which was the actual gap.

  Two tests separate the cases. **(d) vs (a): does the beast bring a body the creature
  roster cannot render?** Appa (six legs, arrow), Catbus (twelve legs, lit windows),
  Buckbeak (eagle front, horse back), Luna (crescent-moon mark) — yes. Simba, Nala,
  Baloo, Shere Khan, Sven, Epona, Shadowfax — **no**, and they stay declined: by the
  0.93.0 rule the difference from `lion` / `bear` / `tiger` / `horse` is a `palette` and
  a `size_scale`. **(d) vs (b): could one person be inside it?** Rancor and Wampa were
  literally suit performers and keep the mascot idiom; nobody can be inside a bantha.
- **A whole cast in near-identical suits makes the *shared* mechanics the risk**, not the
  individual entries. Writing the Miraculous Ladybug team surfaced three that recurred
  per-entry: a talisman worn **at the throat** needs `necklace: "no necklace"` (Cat Noir's
  bell, Ryuko's choker, Rena Rouge's pendant); one worn **as a bracelet** is left unnamed
  entirely, because no bracelet field exists to pin; one that is a **hair comb or
  glasses** is safe to name, because `hair_accessory` and `accessories` *are*
  costume-suppressed. And a **domino mask is never `covers_face`** — the eyes are
  covered, the face is not.
- **An iconic variant is an alternate, not a second entry** (rule 2). Two shapes: a plain
  string in `costumes` when only the costume changes (Shadow Moth on Hawk Moth), and a
  dict alternate carrying its own `signature` when a look-defining field must be replaced
  (Chat Blanc's white hair and blue eyes over Cat Noir's blond — the Gwen Tennyson
  mechanism).
- **A key has to be findable in a 1,700-row dropdown.** Disambiguate collisions
  (`Gwen (League of Legends)` beside `Gwen Tennyson` and `Spider-Gwen`), and prefer a full
  name where a short one would be unsearchable (`Mel Medarda`, not `Mel`). A franchise
  that spans a spin-off keeps its own string where the character is spin-off-only
  (`Arcane` for Silco), while playable champions file under the parent.
- **A cast of bare common nouns gets parenthesised as a set (0.88.0).** The dropdown shows the
  entry key and nothing else — no franchise. `Heavy`, `Medic`, `Spy`, `Sniper` identify nothing
  in an 1,800-row list, and two of the nine Team Fortress 2 classes collide outright (`Pyro` with
  the Marvel entry, `Soldier` with an archetype). So the whole shipped set is parenthesised
  uniformly rather than only the two collisions — a half-parenthesised cast is worse than either
  consistent choice. This extends rule 6 rather than replacing it: a *unique* generic key
  (`Stormtrooper`, `Jawa`, `Vault Dweller`) still stands alone, because it is already findable.
- **Numbered installments file under the series, not the number (0.88.0).** `Final Fantasy` spans
  FF6 to FF14, `Dragon Age` spans two games, likewise `Mass Effect` and `Resident Evil`. A
  pre-existing `Persona 5` string was the lone outlier and was folded into `Persona` at 0.88.0,
  which also took the series past `_FRANCHISE_SCOPE_MINIMUM` and earned it a browsable scope that
  three separate 2/1/6-entry strings never could. A digit that is part of the *title*
  (`Cyberpunk 2077`, `Team Fortress 2`, `Ranma 1/2`, `Warhammer 40,000`) is not an installment
  index and stays.
- **Never put a second figure in the frame.** A canonical look that requires attendants,
  a partner or a companion is not usable — 0.63.0 deleted the over-the-shoulder shot type
  for the same reason. Aphrodite (Record of Ragnarok) ships as a clothed Grecian reading
  keeping her canon identifiers, because her canonical presentation is both unclothed and
  attendant-supported.

`COSPLAYERS: dict[name -> entry]`. Required: `franchise`, `gender` (`Female`/`Male` — SOURCE
gender, used only to scope the `Random — female/male` picks; the *person's* gender is the
IdentityForge widget, so crossplay works), `costume`. Optional: `signature` / `physique`
`{field: value}` maps (values **must** be valid `FIELD_DEFINITIONS` options — `validate_data`
enforces), `covers_face` + `mask`, `covers_hair`, `body_paint`, `prop`, `eyes` (free-text
eye-colour override), and `skin` (free-text body-paint skin-colour anchor).

Conventions (keep the data coherent):

- **Worn, not held.** `costume` lists only worn items and reads after "She/He wears …"
  (lowercase, leading article). Held/wielded props go in the optional `prop` (emitted only when
  the node's prop toggle is on, voiced "holding …").
- **`prop_costume` — when the signature object is worn (0.64.0).** Some characters *wear* their
  iconic object: Indiana Jones' bullwhip is coiled on his belt, Zoro's three swords are sheathed
  at his hip, Kingpin carries his cane. Giving them a `prop` alone renders the object **twice**
  (0.63.0 caught a real double-whip render, and had to delete 12 props for exactly this reason).
  Such an entry carries `prop_costume`: *the same look with that object removed*, swapped in only
  when the prop toggle is on — so the item moves from belt to hand instead of appearing in both
  places. Default output is unchanged, which makes the key purely additive. **Always diff a new
  prop against the costume text, and use a substring not a word-boundary match** (`\bwhip\b`
  misses "bull**whip**"). Some of those 12 are *not* hand items at all and must stay worn with no
  prop: Cinderella's slippers (feet), Frodo's ring (neck chain), the proton pack (back), Big
  Daddy's drill (arm-mounted). Zoro shows the ideal shape — his `prop_costume` sheathes **two**
  swords so the drawn third makes three, not six. Validator: `prop_costume` requires a `prop` and
  must differ from `costume`. It is in `_LOOK_OVERRIDE_KEYS`, and `_pick_look` **drops** it when an
  alternate overrides `costume` without supplying its own, since it only ever describes the costume
  it ships with.
- **Full masks/helmets:** `covers_face: True` **and** the head covering in a separate `mask`
  string (kept out of `costume`) so the *Unmask* toggle can drop it. IdentityForge then
  suppresses Face/Hair/Makeup (+ earrings/piercings). Omit both when the face shows.
- **Bald / shaven-headed:** state it in `costume` (e.g. "…, and a clean-shaven bald head") — the
  builder auto-detects it and locks the scalp-hair (and, for "clean-shaven", facial-hair) fields
  absent (see the Bald / Clean-shaven notes below). Do **not** lock a `hair_length`/`hair_style`
  (locking `buzzed very short` renders a buzz cut — the Mace Windu bug).
- **Non-human skin colour is skin-native (0.52+):** word as `"smooth, flawless <colour> skin"`
  (textured: `"uniform, all-over <colour> <material>"` — scaled/craggy/pebbled keep their texture
  word); leave `skin_tone` out so the person underneath randomizes. Live A/B testing showed
  "body paint" / "dye" wording makes t2i models render a streaky coat OVER a human tone, while
  skin-native wording renders one uniform colour — the paint word was swept out in 0.52. Fur /
  feather / flame / ice / plating entries keep the legacy `"an even … coat of …"` wording (still
  recognised). The builder **auto-detects all three markers**
  (face-visible entries only) and force-locks `skin_tone`, `complexion`, `skin_details`,
  `freckles_density`, `makeup_style` (→ `no makeup`, which cascades every cosmetic sub-field
  absent), and the skin-toned makeup (`blush`, `skin_finish`, `contour`, `highlight`)
  absent — otherwise a random human skin tone/complexion *or* a randomized `makeup_style`
  ("soft glam" with no foundation colour) renders the *face* pale under the paint (the
  She-Hulk green-body/pale-face bug). An explicit `body_paint: True/False` entry key
  overrides the auto-detection. This suppression **also runs when the face is masked**
  (`covers_face`): `covers_face` hides the Face/Hair/Makeup groups but **not** the Body-group
  `skin_tone`, so an all-over coat (Human Torch flame) would otherwise still report a stray
  skin tone under it. See `_BODY_PAINT_RE` / `_BODY_PAINT_SUPPRESS` in
  `nodes/identity_forge_cosplayer.py`.
- **Skin-colour anchor (re-plant the colour).** Suppressing `skin_tone` leaves the *opening*
  prose with no skin colour ("…with a slim build and tall."), so t2i routinely defaults the
  high-attention **face** to a human tone (the Poison Ivy white-face / TMNT pale-face bug). After
  suppression the builder **re-injects the paint colour into `skin_tone`** so the lead sentence
  anchors it ("…tall, **and vivid green skin**"). The colour is auto-derived from the canonical
  clause — `"smooth, flawless <colour> skin"`, `"uniform, all-over <colour> <material>"`, or the
  legacy `"coat of <colour> <material>"` (`_BODY_PAINT_COLOR_RE` → `_body_paint_skin_color`); an
  explicit free-text **`skin` entry key** wins for phrasings the regex misses (`ice`, `chitin`,
  `tattoos`, marker-free prose) or where a cleaner word reads better — it mirrors the `eyes`
  override and is voiced verbatim. The anchor is a *wired value*, so it survives both look-levels
  and "set all to none". The demographics formatter (`_format_…`) guards the trailing `" skin"`
  when the value already ends in a skin/fur/scale/hide word ("dark blue scaled-skin"). For a
  genuinely non-human **face** prefer Pattern A (`covers_face` + `mask`) over relying on the anchor
  alone (TMNT turtles, King Shark, Abe Sapien, Jar Jar Binks, Despero); humanoid coloured
  characters (She-Hulk, Mystique, Gamora) stay face-visible and lean on the anchor.
- **Face-colour reinforcement (engine, the green-body/white-face fix).** The opening anchor colours
  the *body* only; the face is otherwise described by colourless feature tokens ("…oval face…, green
  eyes, red lips"), so t2i kept defaulting the high-attention **face** to a human tone even with the
  anchor in place. `_format_prose` therefore **restates the colour on the face** ("…**Her face has the
  same vivid green skin**") when the resolved `skin_tone` is a non-human colour (not in
  `_STANDARD_SKIN_TONES`, i.e. a body-paint anchor or free-text `skin` override) **and** the face is
  actually described (`face_struct`/`features` non-empty). It reuses the same material-noun guard so
  "scaled-skin" isn't doubled. This fires for face-visible coloured characters only: a masked
  (`covers_face`) or creature-replaced face has its Face-group fields dropped before render, so the
  reinforcement is skipped (the head is the mask/creature); standard human tones are never restated
  (prose-only, zero RNG draws — no output churn, no randomization bias).
- **Hand-colour reinforcement (engine, the white-hands fix).** The same restatement for the
  **hands**: `_format_prose` adds "...**Her hands have the same vivid green skin**" when `skin_tone`
  is non-standard, so bare hands (and any nail polish) do not render in a default human tone (the
  green-body / **white-hands** bug -- She-Hulk, Gamora). Gated on the hands actually showing:
  `generate_character` passes `hands_visible`, false when gloves (`_GLOVE_RE`, unless
  `_FINGERLESS_RE`) or a full shell (`covers_body` / `_FULL_COVER_RE`) hide them -- exactly where
  the finger fields are already dropped -- so it never colours skin or paints nails under a
  covering. Same material-noun guard as the face; prose-only, zero RNG (no bias).
- **Bald characters:** state it in `costume` ("a bald head", "a clean-shaven bald scalp"). The
  builder **auto-detects `\bbald\b`** (won't catch "baldric") and locks the scalp-hair fields
  (`hair_color/length/texture/style/part/highlights/accessory`) absent, so a random
  "His hair is …" line can't contradict the bald head (the Doctor Manhattan / Voldemort bug).
  Auto-detected bald is **scalp-only** (a bald man may keep a beard). For a *fully* hairless
  head (creatures/aliens — Kilowog, King Shark, Despero) set the explicit `bald: True` key,
  which also clears `facial_hair`. `setdefault` semantics: a deliberate signature lock (topknot,
  stray hairs, a beard) still wins. See `_BALD_RE` / `_BALD_SUPPRESS`.
- **Clean-shaven faces:** `"clean-shaven"`/`"clean shaven"` in `costume` **auto-locks**
  `facial_hair` absent so a random beard can't sprout on a bare face. See `_CLEAN_SHAVEN_RE`.
- **Gloved hands:** a costume that covers the hands (`glove`/`gauntlet`/`mitten`) makes the
  engine force the finger fields (`nails`, `rings`) absent — otherwise a randomized polish/ring
  renders *on top of* the glove. (`other_jewelry` now holds only body pieces — anklet, arm cuff,
  body chain — that never sit on the fingers, so it is untouched here.) This lives in the **engine**
  (`generate_character`, `_GLOVE_RE`), not the cosplayer builder, so it also covers archetype
  costumes and random outfits. `"fingerless"` anywhere in the text opts out (fingers exposed →
  nails/rings stay). A user-locked `nails`/`rings` is respected. **Power rings worn over the
  glove** (Green Lantern, Sinestro) belong in the `costume` prose ("a glowing green power ring
  worn on the finger"), not the `rings` field, so they survive the suppression — keep writing
  them that way. (For an all-metal robot like the Cylon Centurion, give it `gauntlets` so the
  finger details drop.)
- **Full hard shell (`covers_body`):** a robot / droid / powered-armour / full-plate /
  exoskeleton body has no bare skin for worn jewellery, so the engine drops the whole
  **Jewelry & Nails** group, plus the Clothing-group `accessories` and `bag` fields
  (`_CONCEALED_BODY_FIELDS`) — sunglasses / belts / a carried bag would render on top of a
  mascot suit or armour shell (the sunglasses-on-Michelin-Man bug, 0.51+). It auto-detects from the costume prose (`_FULL_COVER_RE` —
  `robot`, `droid`, `exoskeleton`, `plate armor`, `armored bodysuit`, …) and also honours an
  explicit `covers_body: True` entry key for cases the prose doesn't spell out (Nebula,
  Man-At-Arms). Independent of `covers_face` (a face mask doesn't imply a covered body, and a
  covered body may still show the face). Body/demographics stay (the silhouette has a build).
  **Fully encased** (`covers_face` **and** a full shell): the body's `skin_tone` is dropped too —
  the only Body-group skin field `covers_face` doesn't already hide — so a masked droid/armour
  (Iron Man, 2-1B) reports no stray human skin tone under the plating. **0.65.0: `ethnicity`
  (Demographics) joins this same gate.** It describes the cosplayer *underneath* the costume,
  which is deliberate elsewhere in the schema (see the Cosplayer node's "Costume only" tooltip —
  body/face/ethnicity randomize freely by design when only the costume is locked), but on an
  entirely-encased character there is no visible skin or face left to attach it to, so mentioning
  it (e.g. "a 45-year-old Kazakh man") only risks nudging the render toward a stray human trait.
  Iron Giant, Ultraman, and Salacious Crumb are the characters that surfaced this. Both fields
  share `_CONCEALED_SHELL_SKIN_FIELDS` in `nodes/identity_forge.py`; an explicit user lock on
  either is respected, same as every other suppression here.
  **`_FULL_COVER_RE` only knows hard shells** — it has no idea about fur, feathers, scales, flame
  or bark, so an *animal* body needs the explicit `covers_body: True` or it gets a randomized tote
  bag and a smart watch. 0.64.0 audited this against rendered output and set the flag on 53 entries
  (Bugs Bunny, the TMNT, Judy Hopps, Groot, Sandman, Tin Man, …). Two lessons for anyone repeating
  the sweep: **(1) `covers_body` is for a body made of something that is not skin** (fur, feathers,
  flame, ice, bark, metal, sand, stone, scales, chitin). A humanoid whose *skin* is merely an odd
  colour or texture still has skin, and worn jewellery is correct on them — Gamora, Poison Ivy,
  Thanos, Gollum, Midna and Majin Buu are deliberate non-fixes. **(2) The costume prose is a weak
  detector.** `_BODY_PAINT_RE`'s `smooth, flawless` branch matches coloured *humanoids*, so it
  over-reports; and entries that describe fur without the canonical "an even, all-over coat of"
  marker (Pikachu, Eevee, Porg, Loth-Cat) are missed entirely. Audit against **rendered output**,
  then judge each hit by material. `Maui` is the trap: his "an even, all-over coat of bold dark
  tribal **tattoos**" is a human body, not a pelt.
- **Hood / cowl / lekku (`covers_hair`):** a head covering that fully encloses the scalp while the
  **face still shows** (a snug cowl, a jester hood, a Twi'lek's lekku) has no visible hair, so a
  randomized "Her hair is …" line only fights the look. The `covers_hair: True` entry key drops the
  whole **Hair** group (engine `_CONCEALED_HAIR_GROUPS`) but keeps Face + Makeup — narrower than
  `covers_face`. Apply it only when the covering truly encloses the scalp and **no signature hair
  is locked** (an iconic fringe under the hood = leave it off): Harley (Classic Jester), Blue Beetle
  (Ted Kord), Bib Fortuna. Independent of `covers_face` (which already drops Hair on its own).
- **Elemental / energy beings whose head is also covered** (Human Torch flame, Ghost Rider
  skull): use the `covers_face` + `mask` mechanism (head described in `mask`) so no random
  hair/face contradicts the effect, and keep the `an even … coat of …` body-paint phrasing in
  `costume` so the Body-group `skin_tone` is suppressed too (see body-paint note above).
- **Extreme-size characters** (giants Giganta, Titania, Giant-Man, The BFG, Stay Puft, Hulk…; tiny
  Tinker Bell, Wasp, Smurfette, The Atom, Yoda, Papa Smurf): set `size_scale` (`"giant"`/`"tiny"`)
  **plus** a hand-authored `scale_prose` phrase — the builder locks `scale_prose` into the `height`
  slot (override=True, beats any `physique.height`), so the scale renders in the **lead sentence**
  in both look levels ("… with an athletic build, colossal and fifty feet tall, and warm tan
  skin"). This works because `height`'s gender pools are identical, so the gender gate passes free
  text — the same route as the body-paint `skin_tone` anchor. Repeat/reinforce the scale at the end
  of the `costume` prose too. Wording must be **self-contained**: strong scale tokens ("colossal",
  "giantess", "hulking", "fifty feet tall"; "tiny", "fairy-sized", "barely an inch tall") and NEVER
  a reference object ("beside a towering everyday object", "three apples high", "insect-sized") —
  T2I models render the named object next to the character. The validator enforces the
  size_scale↔scale_prose pairing and rejects comparison-object phrases. Tier the language: Hulk is
  enormously-tall-hulking, NOT building-scale; Galactus/Giganta are colossal; Yoda is two-feet-short,
  NOT fairy-scale. **Moogle resolved in 0.65.0** (`"tiny"` / "just under three feet tall") — canon
  height genuinely varies across FF titles (a ~1ft field critter in some, a ~3ft companion in
  others), so previous revisions deferred it; the user's "should be pretty short" steer settled it
  at the upper end of the tiny tier rather than leaving the pre-existing `height: "short"`
  (short-*human* reading) unresolved.
- **Plain ASCII only** in names and text (no em/en dashes, smart quotes, accents — e.g. use
  `Padme`, `Eowyn`). Tokenizers mangle the rest. Names are dict keys: a duplicate **silently
  overrides** — grep before adding.
- **Iconic non-standard eyes** (red/violet/gold cat-slit) use the free-text `eyes` override
  (a top-level entry key, not the signature) — it replaces `eye_color` and is voiced verbatim,
  passing the gender gate because `eye_color`'s pools are identical. The main node's dropdown
  stays believable (no fantasy colours added there). The cosplayer also locks `eye_shape` to
  `None` (injected after `group_fields`, which strips it on the build side) so no random shape
  word contradicts the free-text description — the engine keeps the locked `None` as absent and
  drops it from prose/JSON. (`eye_shape` is the single eye-structure field; it also encodes
  size/lid, so the former separate `eye_size`/`eyelid_type` fields were merged out.)
- **Random scope.** `_FRANCHISE_CATEGORY` maps every franchise to one of nine broad categories
  (Anime & Manga, Marvel, DC, Star Wars, Disney, Video Games, Fantasy & Literature, Movies & TV,
  Comics & Cartoons). The Cosplayer node's `random_scope` control narrows the `Random — …` picks
  by category (combines with the gender scope); `get_cosplayer_names(gender, category)` does the
  filtering. Unmapped franchises fall back to a default.

### Writing a feral entry (`body_plan: "feral"`, 0.95.0)

A named beast is rendered **as the beast**. The entry emits the Creature node's
`Species & Anatomy` payload instead of a costume, so the engine's existing species
prose path and Feral suppression do all the work — there is no second prose path, and
`nodes/identity_forge_cosplayer.py` imports the Creature node's own `_suppression()`
rather than restating its lists, so the two producers cannot drift.

| Entry key | Becomes | Notes |
|---|---|---|
| `mask` | the `head` slot | reused, not renamed, so `entry_hash`, the Masked/Mascot scopes and the gallery keep working |
| `costume` | the `integument` slot | colour and material only; it is not clothing |
| `anatomy` | any other creature slot | `eyes`, `arms`, `hands`, `legs_feet`, `wings`, `tail`, `extras` |
| `creature_of` | the subject noun | a **bare lowercase noun phrase**, no article and no `with`/`and` clause |
| `poses` | replaces `_FERAL_POSES` | for a body plan the default pool does not fit (a serpent cannot walk) |
| `scale_prose` | the `height` value | may stand **without** a `size_scale` tier here, uniquely |

**Word `scale_prose` as an appositive here, not a conjunction.** The other 101 tiered
entries read "tiny and barely a foot tall", which works because a human entry has three
core items (build, height, skin tone) and `_join` separates them with commas. A feral
entry has exactly two — there is no skin tone — so the conjunctive form renders *"with a
stocky build **and** tiny **and** barely two feet long"*. "small, about two feet long
from nose to rump" is the correct form for this path; do not "align" it with the others.

`covers_face` and `covers_body` are both **required** — they are what drop the human
Face/Hair/Makeup, the jewellery, the accessories and (together) the skin tone and
ethnicity. `physique` applies in **both** look levels, because there is no person
underneath to randomize; that also closes the costume-asserts-a-body-trait problem
(backlog "Still to consider" #2) for these entries. `prop`, `body_paint`, `skin`,
`eyes` and `costumes` alternates are rejected by `validate_data.py`: a beast has no
hand for a prop, its colour is its integument, and a body plan is not a look.

**Prose framing.** A feral subject does **not** take the `Cosplaying as X:` prefix —
that framing tells a t2i model to render a human in a suit, which is precisely the
failure the path exists to fix. The label is apposed instead: *"Appa (Avatar: The Last
Airbender), a six-legged flying sky bison with …"*. Derived from the species payload in
`_format_prose`, so no signature changed and `prompt_json` still records `cosplay_of`.
`Unmask` is forced off: there is no person under a bantha to reveal, and clearing
`covers_face` let the human Face group back in ("His expression is warm smile").

**Write the anatomy so it renders with the NAME STRIPPED OUT.** Most checkpoints have
never heard of a loth-cat or a fell beast; an entry that leans on the name renders a
generic animal. Each slot goes silhouette/proportion → colour → material → markings:

- **Count and proportion explicit** — "six thick columnar legs", "three long
  independent necks", "twelve legs in six pairs". Never "many legs".
- **Colour named**, and stated on the integument when the colour *is* the identity
  (Appa's white, Toothless's black, Luna's black). Same instinct as the 0.93.0
  `mandrill` / `cassowary` rule of shipping **no** `palette_pool` in that case.
- **The one unmistakable marker gets its own clause** — Appa's brown arrow, Luna's gold
  crescent, Catbus's lit windows and grin, Toothless's patched red tail fin, Mothra's
  wing eyespots. This is what separates the entry from the generic species.
- **No comparison objects, anywhere** — not just in scale text. "as long as a road
  coach", "the bulk of a swan", "folded like a bat's" all render the coach, the swan and
  the bat. `validate_data.py` now rejects `the size of a …` / `as big as …` in scale
  text; the rest is a review job. Anatomical `-like` adjectives ("bat-like wings",
  "dog-like head") are fine — a simile with its own clause is not.
- **No garment words at all** in a feral entry's slots — no *wear*, *worn*, *dressed*,
  *suit*, *outfit*. A draft that said Falkor was "wearing an open smiling expression"
  was caught by the test that scans for exactly this.
- Every `poses` value must complete "He/She is …", so participles only: "standing with
  the head lowered", never the noun-absolute "head lowered and turned".

## creatures.py — non-human form layer

`CREATURES: dict[name -> {class, palette, <slots>}]`. Slots: `head`, `eyes`, `integument`
(required) + optional `arms`, `hands`, `legs_feet`, `wings`, `tail`, `extras`. Slot text is
free-form prose (own render path — not validated against human fields). Rules:

- **Integument is colour-free**; the hue lives in `palette` and is prepended at render
  (`_prepend_descriptor` fixes a/an). Texture words stay in `integument`.
- **`palette_pool`** (optional list): for colour-variable species — most of the roster
  since 0.38 (dragons, wolves, parrots, chameleons, demons, blobs…). When the node palette
  is `Auto` it draws a seed-varied hue from the pool instead of the single `palette` (so
  they aren't one fixed colour). Conventions: the entry's `palette` leads the pool (iconic
  colour stays reachable); pattern words may ride in entries ("black-and-orange banded");
  skip species whose colour IS the identity (raven, panda, orca, skeleton…). The palette
  combo also offers `Random` (rolls `_PALETTES` for any creature). The
  palette RNG draw happens **last** in `build_creature_json`, after creature/slot/form picks,
  so existing seeds keep their creature and only colour shifts; the `Auto`+no-pool path draws no
  RNG and is byte-identical to before.
- **The roster bar is anatomy, not species** (0.93.0, from sifting a ~600-name animal list
  down to ten adds). An entry earns a slot only if it brings a head, integument, limb or
  silhouette the set does not already own; two animals a viewer cannot tell apart in a
  rendered image are one entry, however far apart they sit taxonomically. What this rules
  out, in descending frequency: breeds (a breed is a colour and a size — `palette` and
  `size_scale` already cover it), juveniles (scale is a widget, so a "baby elephant" is the
  elephant rendered tiny), colour and region morphs (that is exactly `palette_pool`), and
  the long tail of animals that render as the same shape (generic fish, songbirds, snake
  variants, small drab bugs). Prefer the *ornamented* member of a group when one exists —
  cassowary shipped over a fourth drab ratite. Each 0.93.0 entry carries an inline comment
  naming the incumbent it beat; do that for new adds too. Closed decisions and the named
  near-misses live in `docs/suggested-additions.md`.
- **Spread a batch across classes.** The creature list is picked uniformly, so a
  Mammals-heavy batch shifts what a plain `Random - any` tends to produce even though no
  per-entry weight exists (noted at 0.90.0, held to at 0.93.0). The test is the resulting
  *balance*, not the batch: 0.94.0 added six entries all to Insects & Arachnids because
  the source list was all insects, and that was fine — the class was the smallest
  non-Alien one at 20 against Mammals' 48, so it moved the distribution toward even.
  Check the class counts before deciding, not the shape of the batch.
- **Suppression:** a creature `head` hides human Face/Hair/Makeup; `integument` hides skin
  fields; `form` (Anthropomorphic/Feral/Subtle) sets group-level suppression. Generalizes the
  cosplayer `covers_face` mechanism via `_meta.suppress_groups` / `suppress_fields`.

## Extending at runtime — user_options.json

`data/user_options.py` merges an optional pack-root `user_options.json` at import (sections:
`fields`, `outfits`, `archetypes`, `cosplayers`, `creatures`). Fails closed on a bad file. User
entries override built-ins of the same name. `palette_pool` is a built-in-only key (the user
creature loader copies only the standard slots).

User additions are first-class (0.46.1):

- The loader records what it added (`USER_ADDED_FIELD_VALUES` / `USER_ADDED_OUTFIT_STYLES`);
  `validate_data` subtracts those from its strict shipped-data checks (family partitions,
  expected outfit-style set, bucket/variety floors), so a valid user file never fails validation
  while shipped-data drift is still caught.
- User values on a **family-weighted field** (hair_style, hair_color, expression, mood, pose,
  lighting, location) sit outside every family; `_pick_family_weighted` draws them via an
  implicit leftover family weighted by its size, so they are reachable at the flat per-value
  share (previously they appeared in the widget but could never randomize).
- The cosplayer loader follows the built-in schema: optional `mask` / `prop` / `eyes` / `skin`
  keys are **omitted** when unused, never stored as `""`; the advanced bool flags
  (`covers_body`, `covers_hair`, `bald`, `body_paint`) are copied only when explicitly `true`
  (0.47.0), mirroring built-ins which never carry a `False` flag.
- A custom value used inside a user archetype should also be listed under `fields` so it is a
  real option (the shipped example demonstrates this with Sky Pirate).

## Validation, tests, versioning

- `python tests/validate_data.py` — value integrity: every signature/physique/constraint/
  archetype value must be a real field option; mask rules; creature structure (allowed keys:
  `class`, `palette`, `palette_pool`, slots; non-empty strings, `palette_pool` a non-empty list
  of strings); studio-backdrop/skin-tone/ethnicity affinity maps.
- `python -m unittest discover -s tests -t . -v` — engine + creature + vault (headless). The
  `-t .` is load-bearing: see "Frontend smoke tests" below.
- `npm run test:frontend` — jsdom tests against the real, unmodified `js/*.js` files. See
  "Frontend smoke tests" below for what this layer is and its honest limits.
- **Version:** bump `pyproject.toml` on every functional commit — **minor** for feature/content,
  **patch** for fixes (standing order).
- **JS regen:** `js/identity_forge.js` embeds a `GROUP_ORDER` / `FIELD_TO_GROUP` / `GENDER_POOLS`
  block (between `GENERATED DATA` markers) built by `python scripts/generate_js_data.py` from
  `data/fields.py`; rerun it and commit the result after changing the field set or the
  gender-divergent pools. `--check` exits non-zero if the committed JS is stale (CI-enforced);
  `tests/test_js_sync.py` guards the same invariant independently.
- **Frontend fixture regen:** `python scripts/dump_frontend_fixtures.py` rebuilds
  `tests/frontend/fixtures/nodes.json` from live `define_schema()` output; rerun and commit
  after any schema change. `--check` is CI-enforced.
- **CI:** `.github/workflows/ci.yml` runs `validate_data.py`, the unittest suite, all three
  `--check` generators, and (in a separate job) the frontend jsdom suite on every push/PR.

### Frontend smoke tests

Everything above runs headless and never opens a browser — and until 0.86.0, every node
class in `nodes/*.py` was never even *defined* outside ComfyUI (each sits behind its own
`try: from comfy_api.latest import io / except ImportError`), so nothing could exercise the
UI layer in `js/*.js` at all. Three layers close that gap, ported from
`comfyui-stylebook`'s identical harness with one real adaptation:

**Layer A — a `comfy_api.latest.io` stub** (`tests/comfy_stub/`), registered real-first /
stub-fallback in `tests/__init__.py`. This is what lets every node class actually define
outside ComfyUI at all. **`-t .` is load-bearing**: `tests/__init__.py` only runs before
every `test_*.py` file when `unittest discover` is invoked with `-t .` (making `tests` a
genuine subpackage of the repo root); without it, `discover` imports test files as bare
top-level modules and the stub registration never happens first, so any node module a test
imports first permanently locks in `_COMFY_AVAILABLE = False` for the rest of the run.

**Layer B — jsdom tests** (`tests/frontend/*.test.mjs`, run via `npm run test:frontend`)
importing the real, unmodified `js/*.js` files, via a `node --import ./tests/frontend/hooks.mjs`
module-resolution hook that redirects `scripts/app.js` / `scripts/api.js` imports to local
stubs. **The one real adaptation from Stylebook**: three of this pack's four extensions
(`identity_forge.ui`, `identity_forge.creature.ui`, `identity_forge.vault`) hook
`beforeRegisterNodeDef`, not `nodeCreated` — only `identity_forge.recreate` uses the latter.
`tests/frontend/fake_node.mjs`'s `driveBeforeRegisterNodeDef` builds a fake `nodeType`
*class* with a real `.prototype`, awaits `ext.beforeRegisterNodeDef(FakeType, {name: nodeId})`
against it, and `createNode` then invokes the now-wrapped `prototype.onNodeCreated` on a
fixture-built fake node instance — exactly what ComfyUI does when a node is dropped on the
canvas. Each test is pinned to a real or latent bug (reintroduce → confirm red → restore →
confirm green), not generic coverage.

**Layer C — `scripts/dump_frontend_fixtures.py`** writes `tests/frontend/fixtures/nodes.json`:
per node, its widgets in real `define_schema()` order, fully derived (no hand-listing) by
walking live schema output and using the `Input`/`WidgetInput` split from the Layer A stub to
tell a real widget from a link-only socket (`force_input=True`, or a type with no `default`
attribute at all — this pack's only such type is `Image.Input`). This is what makes the tests
mean something: a Python field with no `FIELD_TO_GROUP` entry on the JS side genuinely fails
`main_node.test.mjs`, not just a hand-typed fixture agreeing with a hand-typed test.
`tests/test_frontend_fixture_sync.py` and `--check` both guard against a stale fixture.

**Honest limits** — say this explicitly wherever this harness is documented: jsdom has no
layout engine, so `clientWidth`/`clientHeight` read 0, and anything depending on real layout
(CSS, drag/drop, DOM-widget pixel positions) cannot be exercised here. This catches wiring,
visibility, serialization and dialog logic — the class of bug that has actually shipped —
not painting. **It does not replace opening the page in a real browser before a release.**

## The gallery render pipeline (0.87.0)

`scripts/render_gallery.py` renders, records and publishes one image per roster entry, and
`gallery/render_manifest.json` records a content hash per entry so a skipped or stale image
fails CI. Before it existed, every new entry was rendered by hand from one of the three
checked-in workflows and drag-dropped onto `update_gallery.bat`, and nothing anywhere noticed
when that was forgotten. Adding an entry is now: write it → `--missing --publish` → done, and
forgetting turns the build red.

**Prompts are resolved in-process, and the posted graph contains none of this pack's nodes.**
This is the load-bearing design decision, so it is worth stating why the obvious approach does
not work. An entry name is a **dropdown widget value** on `IdentityForgeCosplayer` /
`…Creature` / `…Archetype`, and ComfyUI caches its data layer at startup — a running instance
would reject a brand-new name at `/prompt` validation until it was restarted, and would need
this pack installed to know the name at all. So the script registers the `comfy_api` stub the
way `tests/__init__.py` does, imports the real node classes, calls their `execute()` in the
order the workflows wire them (preset → engine), and posts a plain Krea2 graph whose
`CLIPTextEncode` is fed the finished literal string. The target instance never has to know the
entry exists: no restart, no install, nothing synced anywhere. Calling the node classes rather
than re-implementing the plumbing is deliberate — see the `generate_character` footguns above;
an image that does not represent what the node emits is worse than no image.

**The graph ends in `PreviewImage`, not `SaveImage`.** Preview output goes to ComfyUI's temp
directory, is fetched straight back over `GET /view?…&type=temp`, and is cleared by ComfyUI on
its own, so a run leaves someone else's instance exactly as it was found. `--save-originals`
switches to `SaveImage` (`type=output`) when full-resolution originals are wanted on the
ComfyUI side; `SaveImage` numbers from the highest existing counter, so it adds files and never
replaces one. Images are always fetched over HTTP, never read off the instance's filesystem —
which also keeps a remote instance workable.

**Render settings are read, not transcribed.** Model filenames, LoRA strengths, latent size,
sampler, scheduler, steps, cfg and the photographic style prefix are all parsed out of
`gallery/cosplay/Krea2_IdentityForge_CharacterCycle.json`, which is already committed and
already published. One source of truth, nothing new written down about anyone's local setup,
and updating that workflow updates the renderer. A gitignored `scripts/render_config.json` and
then CLI flags override it. A missing file or absent node fails loudly naming the exact key —
never a guessed default, and **never a substring match on a model name**: the sibling
`comfyui-stylebook` pipeline did exactly that and rendered a whole gallery off the wrong Turbo
merge, plausible enough that nobody noticed until it was published. Preflight checks every
model, `sampler_name` and `scheduler` against live `/object_info` before the first queue.

**Render settings are excluded from the entry hash, on purpose.** Stylebook folds its render
settings into each tile's hash, which is right there because every tile was produced under
recorded settings. Here, ~2,150 images predate this pipeline and were rendered by hand under
settings nobody wrote down, so folding settings in would mark every entry stale on day one.
Changing the model is therefore a deliberate, manual re-render. Do not "fix" this.

**Queue etiquette.** `POST /prompt` carries `{"front": true}`, which inserts at position 0 of
`queue_pending`, leaves already-queued jobs untouched and does not interrupt the running job.
`/interrupt` and `DELETE /queue` are never called — the queue may not be ours. `--back` opts
out. The default target is `http://127.0.0.1:8288`, the disposable test instance, not the
primary one.

**`--check` is the gate**: network-free, stdlib-only, no ComfyUI, wired into the dependency-free
CI job. It reports **missing** (in the data layer, absent from the manifest), **stale** (hash
differs) and **orphan** (in the manifest, gone from the data layer — prune it in the same commit
that removed the entry), and prints a real runnable remediation command. It is manifest-only by
design: `gallery/.render_out` is scratch and never reaches a clone, so testing for a file on
disk would report every entry missing in CI. **Accepted cost:** editing an entry's text while
ComfyUI is off turns CI red until it is re-rendered. That is the enforcement, not a bug.

**Order of operations, once:** `--seed-manifest` must be run and committed **before** new
content lands, or seeding silently blesses unrendered entries as `"pre-existing"`.

### Front-facing shots and overwrite publishing (0.98.0)

Two publish-quality gaps closed together:

**Gallery shots are pinned front-facing.** A user request: no gallery image shows a back.
`_gallery_shot()` picks each entry's `shot_type` from the schema pool minus the four
back-facing values and the `Random` control value (pinning the control would just
re-randomize the camera - caught at 0.98.0 when a seed drew it), on a dedicated stream
(`seed ^ 0x5A17C105`) so the choice never shifts
the engine's RNG stream.
Back-facing values stay available to users; only the sample images avoid them. The pin
initially shipped DEAD: a leftover second `IdentityForge.execute(...)` line below the pin
block overwrote the pinned result with an unpinned one, so every render used whatever the
unpinned stream rolled - plausible output, silently wrong mechanism. It surfaced only when
an entry whose seed rolled "from above and behind" hid its defining feature (the
mosquito's proboscis). Lesson: verify a pin by reading the prompt back out of the saved
artifact, not by trusting the code path.

**Re-renders now overwrite.** `gallery/*/publish.py` defaults to ADD-MISSING-ONLY, so a
re-render of an existing entry was silently dropped and the published image stayed old -
caught exactly that way at 0.98.0. Passing the whole archive folder with `--overwrite`
would instead re-encode every historical image, so `render_gallery.py` stages only the
originals rendered in THIS run into a temp dir and publishes that folder with
`--overwrite`. Both halves matter.

### Adding a field without breaking saved workflows (0.90.0)

`tattoos`, `legwear` and `tattoo_placement` are the first genuinely new *widgets* the
node has grown in a long time, and the mechanism is worth stating once because the
obvious placement is the wrong one.

**Append at the end of `FIELD_DEFINITIONS`, never next to the field's group-mates.**
`define_schema` emits one COMBO per entry in that dict's insertion order, and ComfyUI
stores `widgets_values` **positionally**. A field inserted mid-dict shifts every widget
after it, so a workflow saved before the change reloads with its values one slot out —
silently, and on every node. Appending leaves every existing index untouched; an older
workflow simply has no value for the new trailing widgets and they take their `Random`
default.

This costs nothing in UI terms, because `js/identity_forge.js` **rebuilds
`node.widgets` into group order** from `FIELD_TO_GROUP` / `GROUP_ORDER` before the user
sees anything. Serialization order and visual order are already decoupled; the append
just uses that fact. So `tattoos` sits in Body and `legwear` in Clothing on screen while
living at the end of the dict on disk.

Proved against the real thing rather than argued: the running pre-0.90.0 instance
reports 74 widgets, the new schema 77, and the first 74 names match index for index.

**Do not add a migration notice.** There is nothing to migrate — that is the whole
point of appending — and a banner that fires on every load of an older workflow is an
irritant, not a service. (The recreate-reconnect warning in `js/` is a different thing:
it reports a real, actionable loss.)

**Second constraint, same answer.** A field's pool filter can only read fields drawn
*before* it. All three gate on `outfit_description`, so they must be drawn after it —
which appending also guarantees. But `outfit_description` is composed **after
`_randomize_fields` returns** for a randomly generated character, so "later in the dict"
is not late enough: gating inside the loop reads an empty string. Hence
`_DEFERRED_FIELDS`, drawn in `_resolve_deferred_fields` once the outfit exists.

Deferring bought a third property for free: because every new draw now happens after
every pre-existing one, **no existing seed changes**. Verified by diffing 600 generated
characters against the previous commit — every difference is an added clause, none is a
different person.

Note in passing: `_performable_poses` reads `outfit_description` from inside the loop
too, so for a *randomly generated* outfit its garment check is inert; it only ever sees
a preset costume. Pre-existing, not fixed here, and flagged on `_DEFERRED_FIELDS`.

### Gating a field on what the clothes actually show (0.90.0)

A tattoo the viewer cannot see is worse than no tattoo, because the phrase still steers
the image: "a floral tattoo down one thigh" on a character in jeans pushes the model
toward showing a thigh. `legwear` has the same problem in reverse — tights named under
trousers are a contradiction the model resolves by inventing a visible pair.

There is no structured garment model and building one for two fields would cost far more
than it returns, so both gate on **regexes over the resolved outfit text**, the technique
`_POCKETLESS_GARMENT_RE` already uses for poses: `_BARE_LEG_RE`, `_LONG_SLEEVE_RE`,
`_LONG_HEM_RE`, `_HIGH_NECK_RE`, `_OPAQUE_LEGWEAR_RE`, `_TALL_BOOT_RE`.

Two rules that keep this honest:

- **Conservative in the safe direction.** For legwear, anything not matched as
  leg-baring is treated as covering, so a miss costs a missing option rather than a
  contradiction. For sleeves the polarity inverts — a match *removes* options — so
  ambiguous words (`shirt`, `top`) are deliberately excluded; they are as often
  short-sleeved.
- **A cull must never empty the pool.** Four placements (neck, behind-ear, upper-arm,
  shoulder-blade) are unreachable by every rule, pinned by a test, so a character in a
  turtleneck, blazer and trousers still has somewhere to put a tattoo.

`legwear` is *whole-pool* suppressed when the leg is covered, not partially culled —
the shape that cannot concentrate a frozen family weight. Neither field carries a
`FIELD_FAMILIES` entry, so `tattoo_placement`'s partial cull re-picks uniformly among
survivors, which is the documented "a flat field is where a partial cull is FINE" case.

Rarity runs through `_EXTRA_ABSENCE` (`tattoos` at 0.85), **not** a `weights` map. That
was a deliberate change of approach: routing it through the absence table makes the
existing `accessory_density` control govern tattoos for free — "None" strips them,
"Maximal" makes them common — which a weights map could not do.

Finally, the tattoo gets **its own sentence**, not another item on the clothing list.
A marking appended to a long garment list is exactly what made Judy Alvarez's face
tattoo and the Kabuki Actor's kumadori fail to render.

### Limb and part counts: position beats repetition (0.96.0, measured)

The same rule governs **anatomy that is not the head**, and it was measured directly on
`Dexter Jettster`. His costume stated the arm count *three times in one sentence* —
"all four sleeves rolled to the elbow", "over four thick arms", "a second pair of
shoulders set below the first so all four arms are clearly visible" — and the render
still came back with **two arms**. Saying it more times inside the `He wears …`
sentence does nothing.

What fixed it was moving the count into a sentence that renders **before** the
clothing. `mask` is voiced as its own `He has …` sentence (see the note on `_MASK_KEY`),
so the count was appended there — "…carried on a four-armed body: two pairs of arms, an
upper pair at the shoulders and a second pair set lower on the ribs" — and the very next
render produced four correctly-placed arms. Confirmed again on `General Grievous` (four
arms, four sabers) and `Stitch`.

Two consequences for authoring:

* **A count is load-bearing prose, so give it a clause of its own, early.** Restating it
  later is free but does not carry the render.
* `mask` means *what the head looks like*, so carrying body anatomy in it is a
  compromise, taken because **a non-feral entry has no per-entry anatomy sentence**. The
  costume keeps its own mention of the count so the Unmask toggle - which drops `mask` -
  degrades to the old behaviour instead of losing the limbs entirely. `Greez Dritus` was
  moved onto this pattern at 0.98.0 (his published render had come back two-armed); the
  three multi-armed entries still without a `mask` (`Shiva (Record of Ragnarok)`, `Salaak`,
  `Spiral`) carry the count via `anatomy_note` instead, and closing the general case
  properly still needs an optional anatomy sentence for non-feral entries, mirroring
  `_MASK_KEY`.

### Never negate in prompt data

A negated clause lands as the thing it excludes: t2i draws "no wings", not the absence of
wings. Six feral entries shipped nine of them at 0.95.0 (`Falkor` "with no scales
anywhere" **and** "with no wings at all", `Toothless` "no horns and no visible teeth",
`King Ghidorah` "no forelimbs at all", …) and `Falkor` rendered with branched antlers and
a tangle of limbs. All nine were rewritten as positive statements at 0.96.0 — say what
*is* there ("furred from mane to tail tip", "an unbroken domed brow", "the shoulders
given over entirely to the wings"). `-less` adjectives count too (`scaleless`,
`featherless`); `lipless` is kept because it names a real mouth shape rather than an
absence. Applies to `mask`, `costume` and every `anatomy` slot.

## Considered and deferred

Design notes for ideas that were scoped but deliberately not built. Kept so the reasoning
does not have to be rediscovered — and so a future decision starts from the real numbers.

### Sequential / "cycle through the pool" pick mode (deferred 0.66.0, **DECIDED AGAINST 0.84.0**)

**Closed on a maintainer decision — do not re-propose.** The design below is kept because it is
sound and cheap; what killed it is that none of the three open questions has a good answer, and
the feature's value (browsing a scope) does not justify either a second number widget or a
knowingly unstable index. The `_announce_scope` pool-size print already gives users the
"how big is this scope" information that motivated most of the ask.

**The ask:** let a user walk a scope one character at a time instead of only picking randomly —
e.g. contact-sheet every Star Wars character, or every Giant.

**The cheap design.** Add a `pick_mode` combo to the Cosplayer node: `Random` (default) /
`Sequential`. In `Sequential`, `_resolve_character` indexes rather than draws:

```python
pool = get_cosplayer_names(gender=gender, category=category)   # already sorted, already built
name = pool[seed % len(pool)]                                  # instead of rng.choice(pool)
```

The user then sets the **existing** `seed` widget's `control_after_generate` to `increment`, and
each run advances exactly one character. No new seed/index widget, no new state, and the pool
construction is untouched — `Sequential` only changes how one value is chosen from it.

**Why it is attractive:** ~15 lines, default `Random` keeps every existing workflow byte-identical
(non-breaking), and it reuses ComfyUI's built-in increment rather than inventing a control. It
also turns the four attribute scopes into review tools — "show me all 26 Tiny characters" becomes
26 runs instead of luck.

**Open questions to settle before building** (these are why it was deferred, not the cost):
1. **Seed does double duty.** The same seed still drives `_pick_look` (alt costume) and the whole
   downstream person randomization. So cycling characters also re-rolls the person and the
   costume alternate on every step — you cannot hold the person fixed and vary only the
   character, which may be exactly what a contact sheet wants. A separate `index` widget would
   decouple them, at the cost of a second number widget to explain.
2. **Pool identity is not stable.** `pool[seed % len(pool)]` shifts *every* index whenever a
   character is added to that category — and the roster grows most releases. A saved workflow at
   seed 40 silently means a different character next version. Acceptable for browsing, bad if
   anyone treats it as a stable reference.
3. **Interaction with the gender scope** — `Sequential` + `Random — female` is coherent, but
   `Sequential` + a specific character is a no-op that needs a tooltip.

**Franchise scoping — deferred here, then built in 0.72.0 with a threshold.** Same request,
different half: scope Random picks by franchise rather than the 9 broad categories. The original
objection was the shape of the data, and it still holds — at the current roster **135 of 263
franchises are singletons**, so exposing all of them would give most options one fixed character
forever. What changed is the framing: the answer was never "all franchises or none", it was
*thresholding*, which the original note dismissed too quickly. `_build_franchise_scopes()` in
`nodes/identity_forge_cosplayer.py` derives a scope for every franchise with
`_FRANCHISE_SCOPE_MINIMUM` (8) or more characters, minus the three whose name is already a
category (Marvel, DC, Star Wars) — 26 entries covering ~389 characters, taking `random_scope`
from 14 options to 40. Singletons are simply never offered. It needed **no new plumbing**:
`_SPECIAL_SCOPES` was already a `{label: predicate}` map with its own branch in
`_resolve_character`, so a franchise scope is one `lambda`. Being derived rather than hand-listed,
it counts `user_options.json` additions and self-maintains as the roster grows. Current
thresholds for a future re-tune: ≥3 chars → 94 franchises covering 1093 of 1296; ≥5 → 54 covering
955; ≥8 → 30 covering 817 (27 after removing the category-named three).

**Re-tuning `_FRANCHISE_SCOPE_MINIMUM` is DECIDED AGAINST (0.84.0) — do not re-propose.**
The threshold stays at **8**. Lowering it trades a longer dropdown for scopes that are barely
scopes: at ≥3 the control grows to ~94 franchise entries on top of the 14 attribute ones, and
a three-character scope is close enough to picking the character by name that the *random* pick
stops meaning anything. The numbers above are kept so the trade can be re-examined with real
figures if the roster's shape ever changes materially — a *new argument*, not a repeat of the
request.

**Related pre-existing UX wart — legibility addressed in 0.68.0, correctness in 0.75.0.**
`_resolve_character` used to fall back to the **full gender pool** silently when a (gender, scope)
combo came up empty, and small combos looked like the scope had been ignored. 0.68.0 added
`_announce_scope`, which prints the in-scope pool size once per `(character, scope)` combination.

0.68.0 also asserted, in this document, that *"the shipped roster has no empty combo (the
smallest, `Masked` + `Random — female`, is 8), so the fallback branch only fires for a
`user_options.json` configuration."* **That was wrong, and the wrong claim is why the bug
survived.** It was checked against the attribute scopes only; the franchise scopes added in
0.74.0 introduced `Franchise: Date A Live` — an all-female cast — whose intersection with
`Random — male` is empty. The user hit it, and got Ghostbusters and Ewoks back from a franchise
scope.

**0.75.0 changed the precedence: the scope wins, the gender relaxes.** When a (gender, scope)
combo is empty the pick is redrawn from the scope with the gender filter dropped, so the user
still gets a character from the franchise they asked for. This is the right way round because the
scope is the deliberate, visible choice, the source gender only pre-filters the pool, and the
*person* cosplaying is gendered separately on the Identity Forge node — crossplay is a
first-class feature, so a relaxed pick is already valid output. Only a scope matching nothing at
all for any gender (reachable solely via `user_options.json`) still falls back to the full roster,
and shouts `The result will be OUT OF SCOPE.` `_announce_scope` takes an outcome of `_SCOPE_OK` /
`_SCOPE_GENDER_RELAXED` / `_SCOPE_ABANDONED` rather than a boolean, so the console says which of
the three happened.

**Testing lesson.** The franchise-scope test sampled one franchise (Pokemon) against one gender
(`Random — any`) — the bug lives in the *intersection*, which that sample never touched.
`EveryScopeGenderComboTests` now walks the entire dropdown × all three character picks. Any scope
matrix should be tested as a matrix; do not re-narrow it to a sample.

One-sided casts are a permanent feature of the data, not a defect to fix by padding: `Date A Live`
is 11F/0M and `Sailor Moon` is 9F/1M because those casts are one-sided. The relax-gender path is
what makes them behave.

### Field-pool growth: `outfit_style` and `hair_style` (deferred 0.77.0)

Both were scoped at 0.77.0 after the maintainer asked whether more hairstyles or clothing
styles should be on offer. Both were **deliberately not built**. The reasoning is worth keeping,
because the *shape* of the objection generalises to any future field-pool expansion.

**`outfit_style` remains DEFERRED as a pool, and the register-vs-theme reasoning below still
governs it — but 0.83.0 solved the underlying "not enough clothing variety" complaint a
different way, by making `clothing_color` / `clothing_pattern` / `footwear` actually render and
doubling the garment corpus. The pool stayed at 14. See "The wardrobe axis" above.**

**`outfit_style` is a register axis, not a theme axis.** Its 14 values answer *how dressed up,
for what occasion* — `casual` → `business formal` → `athletic` → `loungewear`. The obvious
additions (goth, cottagecore, western, punk, y2k, utility/workwear) are **subculture and era
themes**, which is the **Archetype node's** job, not the base node's. This was checked, not
assumed: `1990s Goth`, `Gothic Doll`, `Cottagecore`, `Y2K Mall Casual`, `1990s Grunge` and
`Punk Rocker` **already ship as archetypes**, so adding them here would have duplicated a whole
layer of the pack inside the "believable person" node and pulled its output away from believable
and toward costumed. `bohemian`, `edgy alternative` and `vintage retro` are the existing
borderline values; they are **grandfathered, not precedent**. Note the separate mechanical cost:
`outfit_style` is a **flat** field, so 14 → 19 would dilute every existing style from 7.1% to
5.3%.

**`hair_style` is family-weighted, so additions are provably bias-free — but the same theme
objection applies to half the list.** Splitting the candidates is the useful part of this note:

- *Era- or subculture-coded — do not add without a fresh decision:* `victory rolls` (1940s
  pin-up), `hime cut` (anime-coded), `faux hawk`, `wolf cut`. Same failure mode as
  `outfit_style`; `1940s Factory Worker`, `Pin-up Model` and `Gothic Doll` already cover this
  ground as archetypes.
- *Ordinary contemporary barbering — the real, theme-free gap:* `fade`, `undercut`,
  `pompadour`, `quiff`, `shag`. None of these date or theme a person. The **male pool currently
  adds only `comb over` and `mullet`** over the female pool, both of which are *more* era-coded
  than anything in this group — so masculine styling is simultaneously thin and skewed toward
  the dated end. This is the half worth revisiting.
  **BUILT: all five at 0.81.0, plus `crew cut` / `textured crop` / `high-top fade` at 0.83.0**
  (see the `barbered_crop` note above). The era/subculture half of this list is still
  **rejected** and the reasoning still stands — 0.83.0 re-affirmed it while adding the
  theme-free residue the wildcard sources surfaced (`milkmaid braids`, `rope braid`,
  `braided bun`, `two-strand twists`, `bubble ponytail`, `micro bangs`, `hair puff`).

If the second group is ever built, each value must be slotted into a `HAIR_STYLE_FAMILIES`
family **and** into the `data/constraints.py` length lists (`_LONG_HAIR_STYLES`, the pixie
exclusion) — the rule `cornrows` and `bantu knots` escaped until 0.72.0.

Two **archetype** gaps were recorded here at 0.77.0 ("no western/cowboy archetype and no biker
archetype"). **Both are now closed and the note was stale** — verified against the live
225-archetype list: `Wild West Gunslinger`, `Rancher`, `Backyard Country Casual` and
`Country Star` cover the western ground, and `Biker` ships. Kept as a line rather than
deleted because a stale "gap" invites someone to fill it twice.

### A bare-adjective `height` read awkwardly in the lead sentence (CLOSED 0.97.0)

Found in a preview pass, **pre-existing since the lead sentence was written** and unrelated to
anything 0.84.0 changed. The lead joins `[body_type, height, skin_tone]`, and `height` was
inserted verbatim:

> Iron Man: *"a 22-year-old man with an average build **and short**."*
> Thor: *"…with an average build, **short**, and medium skin."*

Six of the nine `height` values are bare adjectives (`very petite`, `petite`, `short`, `tall`,
`statuesque`, `very tall`); the other three are already noun phrases (`average height`,
`slightly below/above average height`) and read correctly. It was most visible on a fully
encased character, where `_CONCEALED_SHELL_SKIN_FIELDS` drops `skin_tone` and the list falls to
two items, leaving a naked "and short".

**It sat open from 0.84.0 to 0.97.0 because the obvious fix was priced wrong.** The assumed
remedy was rewrapping the value — `short` → `a short stature` — which changes the conditioning
tokens for every user of a T2I prompt builder, not just the phrasing. That is a real cost and
the deferral was correct for that fix.

**What shipped instead moves the word, it does not rewrite it.** The six bare adjectives are
voiced as a PRENOMINAL adjective on the subject noun, which is the slot English actually allows
them in, and size precedes age in English adjective order:

> now: *"**A short** 22-year-old man with an average build and medium skin."*

The token `short` is still there, exactly once; only its position changed. `_PRENOMINAL_HEIGHTS`
in `nodes/identity_forge.py` is the membership list, and it goes at the FRONT of `lead_bits`
while `core` skips it, so nothing is voiced twice.

**The constraint the old note named is respected, and it is why the list is literal rather than
computed.** `height` is also the slot the `size_scale` / `scale_prose` override writes into
(`"colossal and fifty feet tall"`), and those are hand-authored phrases that already read
correctly where they are — "A colossal and fifty feet tall man" would be worse than the wart.
Anything not named in `_PRENOMINAL_HEIGHTS` — the three noun-phrase values and every free-text
override — stays in the trailing list untouched. `HeightPrenominalTests` pins every member
against `FIELD_DEFINITIONS["height"]` (so a renamed value fails loudly instead of silently
falling back to the old wording), pins the split against the "contains the word height" rule,
and pins that free text is never moved.

**The cost that was accepted:** the lead sentence of roughly two-thirds of all renders now
reads differently, so the published gallery images for those entries are no longer literal
reproductions of what the pack emits today. `--check` cannot see it — `entry_hash` covers the
entry *dict*, not the prose — which is the same blind spot the 0.90.0 mask rewrite hit. A
maintainer decision, taken deliberately, not a regression.

### The `loose` hair_style family blocks the rest of the buzz-cut fix (CLOSED 0.78.0)

**Done.** `loose` was split into `loose_styled` / `loose_natural` / `loose_combover` /
`loose_mullet`, `braid` into `braid_long` / `braid_short`, and `bun` into `bun_small` /
`bun_gathered`, with all weights scaled **×105** so every proportional sub-weight stays an
integer (lcm of the 9, 10 and 7 denominators). Every value keeps its exact pre-split
probability, pinned in `HairStyleFamilyTests` against a hardcoded 0.77.0 baseline. The
impossible pairings went from **790 per 12,000 samples to 0**, and `hair_length` / `lighting`
marginals moved ≤0.18pp (sampling noise). Seeds drifted, as designed.

Two things were learned doing it that are worth more than the fix itself:

1. **A latent multi-rule bug surfaced immediately** — see the constraint re-pick note in the
   gotchas below. Splitting the family took the legal hair_style set on a buzz cut from 7 of 33
   to 2 of 33, which made an existing convergence failure bite constantly.
2. **The `gender = Male` rule partially culls three families and it does not matter.** By the
   theory above, `bun_small` (1/5), `braid_long` (2/8) and `knots` (1/2) should concentrate
   their full weight on the survivors for half of all output. Measured over 23,270 male
   samples: `bantu knots` 3.79% vs `cornrows` 3.51%, ratio 1.08 against a proportional
   expectation of 1.11 — marginally *under* its fair share. The 0.64.0 mixture property is why:
   the engine re-picks only a value it actually rejected, and most subjects draw a permitted
   style first time and never enter that path. **Measure before splitting anything else.**

### Superseded: why it was deferred at 0.77.0

0.77.0 fixed bangs-on-a-buzz-cut (see `constraints.py`), but a 12,000-sample sweep found five
more physically impossible pairings that were **deliberately left in place**:
`buzzed very short` × `worn down` (98), `windswept` (103), `freshly blown out` (102),
`tousled bedhead` (93), `slicked back` (99) — roughly 4% of all output.

They could not be fixed the same way. `curtain bangs` + `blunt bangs` are *exactly* the `bangs`
family, so excluding both drops a **whole family** and every other family stays proportional.
All five of these instead live in the 9-variant `loose` family beside `wet look`,
`natural and unstyled`, `comb over` and `mullet`. Culling part of a family leaves its **full
frozen weight** on the survivors (the trap documented for `LIGHTING_FAMILIES` at 0.64.0), so the
"fix" would have concentrated `loose`'s entire share onto `wet look` and `natural and unstyled`
for every buzz cut — trading a coherence bug for a distribution bug.

**The real fix is a family split**, exactly the treatment `POSE_FAMILIES` got at 0.66.0: break
`loose` into sub-families whose weights are **proportional to variant count**, so the
buzz-impossible ones can be dropped as whole units. That is a designed change with seed drift,
so it needs its own decision. The same argument applies to `short pixie` × `dutch braids` (69)
and `crown braid` (30), which are the two braids missing from the pixie exclusion list: culling
them would double `cornrows`/`locs` on pixies, because they would be the `braid` family's only
survivors there.

### Per-character "has skin but wouldn't wear jewellery" (closed 0.66.0 — do not re-flag)

Raised at 0.64.0 and **closed by explicit user decision**: leave it alone entirely.

The 0.64.0 `covers_body` audit deliberately skipped 10 characters (Gollum, Thanos, Midna, Majin
Buu, Killer Frost, Kilowog, Larfleeze, Lord Raptor, Victor von Gerdenheim) on the rule that
`covers_body` means *the body is made of something that is not skin* — those are humanoids whose
skin is merely an odd colour, so jewellery correctly stays reachable and Gollum can draw a charm
bracelet. The gap was that no key says "has skin, but wouldn't accessorise": `covers_body` would
be a lie, and `accessory_density` is a global user control, not per-character. A `wears_no_jewelry`
key was considered and **rejected** — the current behaviour is defensible and the schema stays
smaller. Do not add it back without a fresh decision.

### Comic-women roster review (0.70.0 — do not re-litigate the skips)

A pass over two external popularity rankings of comic-book women against the live roster
confirmed the broadly-recognizable entries are already covered: the Marvel/DC mains and their
alter-egos/variants (Star Sapphire = Carol Ferris, Spider-Gwen = Gwen Stacy, Captain Marvel =
Carol/Ms. Marvel, Death of the Endless, Wonder Girl = Donna Troy, DC Jade and MK Jade, both
Huntresses, Dazzler, Batwoman, Viper/Madame Hydra, Mary Marvel, Invisible Woman, Shanna,
Valkyrie, Lois Lane, Hawkgirl, Mera, Big Barda, Wasp), plus the indie/other icons Vampirella,
Red Sonja, Witchblade (Sara Pezzini), Fathom (Aspen Matthews), Lady Death, Caitlin Fairchild
(Gen13), Lara Croft, Kitana, and the Masters of the Universe cast.

**Added (rule 2 — a represented franchise missing an iconic character):** **Abbey Chase** (Danger
Girl shipped only via the side operative Natalia Kassle); **Evil-Lyn** (Masters of the Universe had
He-Man/Skeletor/She-Ra/Sorceress/Teela but not its iconic sorceress-villainess); **Sheena, Queen of
the Jungle** (a genuinely classic, broadly-recognizable pulp/comics character with a clear worn look).

**Venus was reopened at 0.78.0** on an explicit maintainer request and now ships as
`Venus (Marvel)` — the same precedent as Kimberly (Space Ace) at 0.77.0. The original skip
reason was sound (she alters her own appearance in canon and has no single fixed costume), so
she ships with her most-drawn look, the white Grecian gown, plus the Agents of Atlas green gown
as an alternate. She is struck from the list below rather than left to contradict the roster.

Deliberately **skipped as deep cuts** (fail the "genuinely iconic, broadly-recognizable" bar, or
have no distinct worn costume): Tarot, Linsner's Dawn, Purgatori/Chastity, Dejah Thoris, Barbarella,
Cassie Hack, Painkiller Jane, Shi, Ghost (Dark Horse), Clea, Fury, Shadow Lass, Phantom Girl,
Lady Blackhawk, P'Gell, Katy Keene, the Love & Rockets women (Hopey/Maggie/Luba), and the
civilian/no-costume names (Lois Lane's Lana Lang, Vicki Vale, plus the Archie girls Betty/Veronica —
everyday teen fashion). Don't re-add these without a fresh curation decision.

### Only `lighting` may state the hour (0.81.0)

`time_of_day` was **deleted as a field** because `lighting` already encodes it — "golden hour
sunlight", "moonlight with cool blue tones", "harsh overhead midday sun". Nine `location` values
had quietly reintroduced it (`rooftop terrace at dusk`, `harbor dock at sunrise`, `sandy beach at
golden hour`, `the Griffith Observatory terrace at dusk`, …), so nothing stopped a dusk terrace
rendering under midday sun. A real preview produced *"set in a harbor dock at sunrise, under fire
and flame warm flicker."*

All nine were **reworded in place** — same slot, same family, same count, so the share multiset is
byte-identical and no seed moved for any other reason. `LocationAndPoseTests::
test_no_location_bakes_in_a_time_of_day` is the standing gate. Two lookalikes are deliberately
fine: `tide pools at low tide` names a tide state, and `art gallery opening night` names an event
type indoors, where the lighting pool is artificial anyway.

**The general rule: a location describes a PLACE. Anything about the hour, the weather or the
light belongs to `lighting`, which owns it exclusively.**

### Per-character canonical makeup — the targeted form that shipped (0.81.0)

The long-deferred item was "female cosplayers draw a *random* makeup look rather than the
character's". The full version (a makeup lock on ~815 female entries) was rejected as a data
project with no clear finish line. What shipped is the subset where the current behaviour is an
actual **contradiction** rather than merely a variation:

> If the entry's own `costume` prose already paints the face, the random draw puts a *second*,
> conflicting face on top of it — full glam over Senua's warpaint.

19 entries were found mechanically (costume prose matching an unambiguous face-paint phrasing) and
pinned. **No schema change was needed**: `signature.makeup_style` already accepts any pool value,
and `"no makeup"` cascades through `CONSTRAINT_RULES` to clear every cosmetic sub-field, then
`_is_absent()` drops the whole makeup sentence — the same end state `_BODY_PAINT_SUPPRESS` reaches
automatically for body-painted characters. Where the canonical look genuinely *is* a makeup look
and the prose does not carry it (Elvira, Morticia), the **style** is pinned and the sub-fields are
left to vary, following the pre-existing `Lydia Deetz` precedent.

`CanonicalMakeupTests` is the standing gate. Two things it deliberately does **not** do:

- It only inspects **female** entries. Men are forced to `no makeup` globally, so a male
  character whose face *is* makeup (the Joker, Beetlejuice, Krusty, Pennywise, William Wallace)
  must author it into `costume` prose — all of those already do.
- It does not fire on an entry that merely mentions lipstick in passing. A gate that cries wolf
  gets suppressed instead of fixed.

**`Harley Quinn` is correct as shipped and is not a counter-example.** Her signature pins a full
makeup look (`club makeup` + four sub-fields) that matches her *Suicide Squad* pale-face-plus-bold-
colour design. That is the deliberate per-character lock this section describes, not the random
draw the 0.78.0 report complained about.

### Barbering: the first genuinely NEW hair_style values since the splits (0.81.0)

`hair_style` had 40 ways to arrange hair and no everyday **barber** cut — no fade, undercut,
pompadour, quiff or shag. Unlike the 0.66.0/0.78.0 family *splits*, this adds new values, so it
cannot be probability-neutral: share has to come from somewhere.

It is taken **uniformly**. `loose_combover` and `loose_mullet` are the existing "one ordinary
everyday cut" families at weight 70 for a single variant each; every barbered cut is priced
identically. Total family weight goes 3150 → 3500, so **every pre-existing value keeps exactly
9/10 of its former share** and each new value lands on 70/3500 = 2.0%. No family is singled out.
**Seeds drift** (`rng.choices` sees more families) — accepted, same as 0.64.0 / 0.66.0 / 0.78.0.

It ships as **two** families, and that is the load-bearing decision:

```
barbered_short  w=280  fade · undercut · pompadour · quiff
barbered_shag   w= 70  shag
```

The four short cuts are impossible on hip-length hair and the shag is impossible on a buzz, so the
two groups must be excludable **independently**. As one family, culling four of five variants would
hand the whole frozen weight to the survivor — the exact trap documented for `loose` above. As two
families, each is dropped whole. `_BARBERED_SHORT_STYLES` in `data/constraints.py` must stay equal
to the `barbered_short` family or the exclusions silently become partial culls;
`HairStyleFamilyTests` pins the two lists together.

One deliberate imprecision: `buzzed very short` excludes the *whole* short group even though "buzz
fade" is a real barbershop order, because the family cannot be cut in half. Losing a marginal
buzz-fade is the cheaper side of that trade.

### A roster label is not a filename (0.81.0)

`B-Boy / B-Girl` cannot exist on disk. Windows strips the slash silently, so a hand-generated
sample arrived as `B-Boy  B-Girl.jpeg` — slash gone, a double space left behind — and matched
nothing. The gallery reported two archetypes as imageless while both files sat in the directory.

**Fixed in the gallery scripts, not by renaming the entries.** `normalize_name()` now substitutes a
space for each of the nine filename-illegal characters (`< > : " / \ | ? *`) and collapses
whitespace runs, so the label and the filename the OS produces for it converge. Renaming the
archetypes was rejected: it breaks saved workflows for no user benefit and fixes only those two
names, while the next entry containing a colon breaks again.

Two follow-on hazards fixed at the same time, both in `publish.py`, which compared a **raw**
`Path.stem` against normalized roster names:

1. add-mode never recognised such an entry's own published image, so it re-encoded it every run;
2. `--prune-orphans` classified it as matching no roster entry and would have **deleted** it.

`FilesystemUnsafeNameTests::test_sanitising_never_merges_two_distinct_entries` guards the risk the
sanitiser itself creates: stripping characters can make two labels collide on one filename, and a
collision is silent — both entries would show the same image and one would be wrong.

### Contrapositive repair, requirement side (0.82.0)

`_apply_constraints` has re-rolled a randomized **trigger** since 0.50.0 when an *exclusion*
rule's target was locked — the locked "sleek bun" re-rolls the random buzz cut. The
**requirement** branch never got the same treatment: it warned and kept, which is the right
*outcome* for the lock but leaves the *output* incoherent. The user-visible symptom was two
console lines every run:

```
'makeup_style=no makeup' wants 'lashes=natural bare' but 'lashes' is locked to
'lash extension look'; keeping lock.
```

The lock did win — the message described the engine doing the right thing, while a bare-face
style still rendered beside lash extensions. Re-rolling the *trigger* instead produces a makeup
style that actually wants those lashes, and the warning disappears because the conflict does.
Two more cases were silently shipping the same way: a locked `smile_type="toothy grin"` beside
a randomly drawn `expression="stern"`, and a locked `hair_part` beside `hair_style="slicked
back"`.

Two details are load-bearing:

- **`_requirement_pins()` is the ping-pong guard.** `gender=Male` *requires*
  `makeup_style="no makeup"`, so repairing `makeup_style` there would be undone on the next
  pass, forever. The guard skips the repair when another live requirement rule pins the
  trigger, falling back to warn-and-keep. It is presentation-aware, so a `Feminine`/`Any`
  wardrobe — where that rule is gated off and `makeup_style` genuinely randomizes — still
  repairs. Removing the guard fails
  `ContrapositiveRequirementTests::test_male_makeup_chain_still_warns_instead_of_ping_ponging`.
- **The conflicting set is the union over EVERY locked target**, not just this rule's. Filtering
  on one rule is the 0.78.0 exclusion bug in the other branch; the union converges in one pass.

**Zero bias, zero seed drift**: the branch only runs when a target is in `locked`, so ordinary
random output cannot move. Verified byte-identical over 900 unlocked prose strings (3 genders ×
300 seeds) against a `git worktree` at the previous commit.

### Fixture lighting: indoors is necessary, not sufficient (0.82.0)

A real render came out *"set in a neighborhood pharmacy, under flickering firelight from a
hearth."* `INDOOR_ONLY_LIGHTING` is a binary bucket, so three values that name a **physical
fixture** — a hearth, a television, a stained-glass window — were legal in all ~139 indoor
locations. A pharmacy has none of them.

The fix has to be per-location, and a per-location rule may only remove a **whole** family. So
each fixture value became its own single-variant family, and `LIGHTING_FAMILIES` went 5 → 10
with every weight scaled **×6** (the lcm keeping each sub-weight an integer). Every one of the
51 values keeps its **exact** prior probability; total 228 = 38×6.

Doing that made it cheap to retire an approximation the bucket comment had admitted to since
0.64.0 — *"only the mixed `artificial` and `neon` families contribute individual values, and
each keeps a clear majority of its variants."* That majority hand-wave was **a real, accepted
bias**: indoors, `neon` lost 2 of 8 variants while keeping its full 6/38 weight, inflating each
of the 6 survivors by ~33% relative. Every location↔lighting bucket is now an exact union of
whole families, pinned by `LightingBucketFamilyTests`.

`HEARTH_LOCATIONS` / `SCREEN_GLOW_LOCATIONS` / `STAINED_GLASS_LOCATIONS` in `data/fields.py` are
**allowlists**, which makes the safe default automatic: a newly added location is excluded from
all three fixtures until someone deliberately opts it in, rather than silently inheriting a
hearth. `data/constraints.py` emits one rule per indoor location naming the fixtures that
location *lacks* (~136 rules, not the ~380 a per-pair rule would need — the engine already
unions all firing exclusions on a target).

**The general rule, extending the 0.81.0 one:** a location describes a PLACE; `lighting` owns
the hour and the light — **and a lighting value that names an OBJECT is only possible where that
object is.** Seeds drift for `lighting` (`rng.choices` sees 10 families, not 5).

### The "set in ..." slot articles the location, and got it wrong twice (0.82.0)

`_format_prose` built the clause as a blind `f"set in {_a(v)} {v}"`. That is correct for a
common-noun location and wrong for two whole classes that had accumulated since:

| Shipping output | Cause |
|---|---|
| "set in **a the** Brooklyn Bridge pedestrian walkway" | the value supplies its own article |
| "set in **an a** Yosemite valley meadow" | same, with `_a` reading the leading "a" |
| "set in **a** Trafalgar Square" | a bare proper name wants no article at all |
| "set in **a** cracked salt flats" | plural head noun |

`_location_clause()` handles all four: values whose first word is `a`/`an`/`the` pass through,
`_NO_ARTICLE_LOCATIONS` covers proper names (capitalisation cannot decide this — "Buddhist
temple hall" and "French bistro with mirrored walls" are capitalised and *do* want "a"), and
everything else routes through the existing **`_article_if_singular`**, whose head-noun split
already gets "a public library with tall bookshelves" right rather than articling on
`bookshelves`.

Fixed in the **engine**, not by rewording data: "the Grand Canyon south rim" is the correct way
to name that place, and `user_options.json` is free text no validator can reach. Prose-only —
no pool change, no RNG draw, no seed drift. `LocationArticleTests` pins it.

### Growing a family-weighted field is the sanctioned way to add variety (0.82.0)

0.82.0 grew four fields at once: `location` 204 → 260, `pose` 30 → 38, `expression` 39 → 45,
`mood` 21 → 26. Because all four are in `FIELD_FAMILIES`, **the field-level distribution does
not move at all** — a family's weight is frozen, so a new variant subdivides that family's
share instead of inflating the field. This is the growth channel the family mechanism exists
for, and it is why `outfit_style` (flat, so 14 → 19 would dilute every value from 7.1% to 5.3%)
and `shot_type` (flat, 26 values) were **not** grown.

Two traps this run surfaced:

1. **A value-level probability pin freezes the pool size.** `PoseFamilyTests` asserted each pose
   sat at a fixed probability, which also silently forbade *adding* one — it failed for the
   wrong reason. Restated at the level the 0.66.0 split actually guarantees: family share
   unchanged from the 0.65.0 baseline, plus internal uniformity, plus sub-family weights
   proportional to size. Same correction `HairStyleFamilyTests` took at 0.81.0. **A baseline pin
   should assert the invariant, not the current data.**
2. **Adding into a split family breaks the split's own arithmetic.** The 0.66.0 gesture split
   priced `gesture`/`gesture_garment`/`gesture_hair` proportional to variant count so all six
   values stayed at 1/27. Adding one variant to two of the three made
   `running one hand through the hair` 1.33× likelier than its siblings. Repriced ×2
   (12/9/3 over 4/3/1 variants) so all eight sit at exactly 1/36 and the parent share is
   untouched. **After adding to a sub-family, re-check the proportionality that justified the
   split.**

`location` additions carry two extra obligations, both test-enforced: a new outdoor value must
join `OUTDOOR_LOCATIONS` (indoor is *derived*, so a miss silently buckets it indoors and starts
drawing window light on a canyon rim), and **no family may span the indoor/outdoor boundary** —
the giant-scale filter narrows `location` to outdoors and stays bias-free only because that
drops seven whole families.

**Do not re-add `server room with blinking racks`.** It shipped from 0.29.0 and was deliberately
removed at 0.78.0 (`b201007`) as too dull; it is the one obvious-looking `work_industrial` gap
that is a settled decision rather than an oversight. A note sits next to `LOCATION_FAMILIES`.

`bedroom` and `bathroom` were added at explicit maintainer request, worded neutrally
("tidy bedroom with a neatly made bed", "tiled bathroom with a large mirror") — no
bed-as-focus phrasing, since the pack has no NSFW guard to fall back on.

### A flat field is where a partial cull is FINE (0.82.0)

The whole-family rule is stated so emphatically elsewhere in this document that it is worth
recording the boundary: **it only applies to `FIELD_FAMILIES` fields.** A flat field — no
family entry, no `weights` map — re-picks flat-uniform over whatever survives an exclusion, so
removing one value of five is bias-clean by construction.

That is what made the `complexion` fix cheap. Real output read *"a 35-year-old Jamaican woman
with … deep ebony skin. … Her skin shows a peaches and cream complexion."* `peaches and cream`
names a pink-white **colouring**, not a surface quality, so it contradicts a deep tone outright;
`clear` / `rosy` / `ruddy` / `sallow` describe redness, pallor and clarity and read on any tone.
`DEEP_SKIN_TONES` in `data/fields.py` drives six generated exclusions.

Measured over 20,000 renders: on deep tones the four survivors sit at 24.6–25.6% (uniform =
25%), and on every other tone all five stay at 19.8–20.4% (uniform = 20%) — the value is
preserved exactly where it is correct. `ComplexionSkinToneTests` pins the behaviour *and*
asserts `complexion` is still flat, so the exclusion has to be re-argued if it ever gains
families or weights.

Note this contradiction was already recorded in the `Ka D'Argo` entry comment, but only ever
fixed *per entry* by the body-paint suppression. **A per-entry workaround for a cross-field
contradiction is a signal that the general rule is missing.**

### The worn-item de-duplication rule — what `_HAT_RE` was a special case of (0.83.0)

The signal above was acted on. The engine had exactly **one** worn-item rule: `_HAT_RE`,
*"if the outfit text names headwear, drop the randomized hat."* Built for hats, never
generalised. Meanwhile **28 cosplayers hand-pinned `"necklace": "no necklace"`** because
their costume names a neck ornament, and the base node's own outfit corpus had the same bug
with no pins at all — 19 of its 180 strings named earrings, a necklace, rings, bangles or a
bag while the engine drew those fields independently. `Boa Hancock` and `Shirahoshi` were
measurably shipping two sets of earrings.

`WORN_ITEM_RES` in `data/fields.py` generalises it to six fields (`necklace`, `earrings`,
`rings`, `bracelet`, `other_jewelry`, `bag`). Lock-respecting, no RNG consumed, and it drops
**only the named field** — a character whose costume names earrings can still get a necklace.

Three things worth keeping:

- **This does NOT reopen the closed 0.66.0 decision.** That asked *may jewellery be worn
  over a costume* (answered yes, do not re-flag). This asks *does the costume text already
  name this item*. Different question, different answer.
- **The 28 pins stay.** They are explicit and cost nothing, and removing one would add an
  RNG draw where a lock used to skip it, drifting that character's seed. They are now
  belt-and-braces; the general rule is what catches the entry that forgets.
- **Do not overclaim the scope.** `bag` is *already* dropped for every cosplayer/archetype
  by `_COSTUME_SUPPRESSED_EXTRAS`, so the `bag` pattern only bites on an engine-generated
  outfit. The five jewellery fields are what this genuinely fixes on the roster (~169
  entries), because jewellery is deliberately absent from that set.

The regexes are tuned against real roster text and the traps are load-bearing —
`rings` must not fire on "earrings" (no word boundary inside the word) nor on a piercing
("brow ring", "lip ring") nor a non-jewellery ring ("tire ring", "neck ring", "arm ring");
`bracelet` must never match a bare "cuff" ("cuffed chinos", "ear cuff", "arm cuff");
`earrings` must not fire on garment "studs"; `bag` must not fire on "baggy" or on `clutch`
as a **verb** ("arms raised to clutch the head"). `WornItemDeduplicationTests` pins every one.

### The wardrobe axis: three shipped widgets that did nothing (0.83.0)

`OUTFIT_DESCRIPTIONS` superseded `footwear`, `clothing_color` and `clothing_pattern` when it
was added, and **nobody retired them**. In the base node's normal path an outfit is *always*
generated, and the prose only voiced those three when there was **no** outfit. So for
releases they were drawn every render, never spoken, and written to the JSON where they
contradicted the prose:

```
prose : "She wears an ivory silk blouse with a high waisted skirt suit and slingback pumps."
json  : footwear "ankle boots" · clothing_color "black monochrome"
```

Locking one was **worse than a no-op**: it changed nothing visible but removed an RNG draw,
so five unrelated fields silently moved. The widget looked like it worked.

**The corpus contract.** Every `OUTFIT_DESCRIPTIONS` value is now a *garment phrase* —
garments and fabrics only, **no leading article**. The engine composes:

```
{palette_adj} {garment}{pattern_tail}, in {footwear}
  -> "a jewel-toned satin slip gown with delicate straps, in strappy heels"
```

`PALETTE_ADJECTIVES` (11) and `PATTERN_TAILS` (10) are explicit per-value maps, and
`validate_data.py` fails if an option lacks an entry — a missing key would silently drop the
clause, the exact class of bug being fixed. The corpus grew 180 → 351, each style's
female/male/unisex bucket doubled in its existing ratio so no style or wardrobe bucket gains
share. Fabric vocabulary is where "texture" variety lives; no new field was needed.

Details that are easy to get wrong:

- **Every pattern tail uses "in", never "with".** Garment phrases routinely end in their own
  "with ..." clause, so a "with" tail rendered *"...with delicate straps with a floral
  print"*. Caught in preview — same class as the 0.82.0 doubled location article.
- **Order.** Palette is prefixed and the phrase articled *before* the tail is appended, so
  `_article_if_singular` reads the garment's head noun ("gown"), not the tail's ("print").
- **A lock beats a guard.** The guards below suppress an *unlocked* axis when the garment
  already states it. A locked one is voiced anyway (striped denim is a real fabric) — the
  alternative would leave the locked value in the JSON while omitting it from the prose,
  putting back the very mismatch this removes.
- **Hard vs soft contract.** `validate_data` hard-fails on a garment naming **footwear,
  jewellery or a bag** (a duplicate *item*) and on a leading article. Colour and pattern
  words are allowed: they are *modifiers*, so "sequined evening gown" or "denim overalls" is
  a legitimate override, not drift. Measured at 0.83.0: 0.6% of strings state a colour, 4.8%
  a pattern (nearly all genuinely denim).
- **`_SHOE_RE` is plural-only for the ambiguous stems.** The first draft matched `oxfords?` /
  `flats?` / `boots?` and false-positived on five shipped garment phrases ("oxford shirt",
  "flat-front chinos"), silently deleting their footwear clause. Every `footwear` pool value
  is plural, so plural-only is both tighter and sufficient.

**Back-compat.** A `user_options.json` "outfits" section holds strings written for the old
contract (article, baked-in shoes and colours). Four guards — `LEADING_ARTICLE_RE`,
`SHOE_RE`, `COLOUR_WORD_RE`, `PATTERN_WORD_RE` — each fire *exactly* in the collision case,
so user data degrades gracefully instead of rendering "a jewel-toned a sleek white EVA suit
… in loafers". The shipped corpus matches none of them.

**These patterns live in `data/fields.py`, not the node.** They are assertions about *data*,
and `tests/validate_data.py` must stay free of node-layer imports (it has to run without
ComfyUI). One source of truth, used by both.

**BIAS: zero drift on the three fields.** They were already drawn in this order from these
flat pools; making them render consumes no extra RNG and moves no distribution. Only the
outfit string drifts per seed, because the pool grew.

### `footwear × outfit_style` is an ALLOWLIST, not a deny-list (0.83.0)

Turning `footwear` on activated three hand-written deny-lists (athletic / business formal /
evening formal) and exposed that the other **eleven** styles had no rule at all. They were
replaced by `FOOTWEAR_BY_STYLE` — what each style *can* wear. Two reasons, and both
generalise:

1. The deny-lists were incomplete in a way inspection does not reveal: `athletic` denied
   heels, loafers, oxfords, slippers and sandals but still permitted **bare feet, wedges and
   mules**.
2. A deny-list silently admits every value added later. The 12 → 20 footwear growth in this
   same revision would have leaked `kitten heels` into sportswear. An allowlist fails safe,
   the same safety model as the fixture-lighting allowlists.

`footwear`, `clothing_color` and `clothing_pattern` are all flat, so these culls re-pick
flat-uniform — the case the "a flat field is where a partial cull is FINE" note exists for.
A `clothing_color × clothing_pattern` rule was added alongside: a monochrome palette
(`all black` / `all white` / …) rules out multi-colour prints, and `mixed prints` rules out
naming a second pattern. Both came straight out of preview output.

**Adding a hat or glove to `accessories` has required side-effects.** `_HAT_ACCESSORY_VALUES`
must gain the hat (its own docstring said so; `GloveAccessoryTests` now enforces it
mechanically), and gloves need `_GLOVE_ACCESSORY_VALUES` so nails and rings drop for them —
`_GLOVE_RE` only ever scanned `outfit_description`. `fingerless gloves` is deliberately
excluded, mirroring `_FINGERLESS_RE`. The glove check runs *after* the costume-extras
suppression, so a glove that was itself just dropped cannot suppress anything.

### Landmark sub-families: variety without frequency (0.83.0)

`location` shipped 7 named landmarks, 4 inside `urban_outdoor` and 3 inside
`nature_outdoor`. Adding more straight in would have kept every family share intact — that
is what family weighting guarantees — while still taking the *famous landmark* concept from
~11% of urban scenes to ~27%. **That is overweighting a concept even though no family share
moved: the subtler half of the bias rule.**

So each family was split into base + landmark at a weight proportional to the *original*
counts, and only the landmark side grew (4 → 17 and 3 → 10, `location` 260 → 280).
`P(any landmark)` is **exactly unchanged**; `P(a specific landmark)` falls, which is the point.

Weights must stay positive **ints**, so the rescale is forced arithmetic: urban needs
`20·s/36` integral (`s ≡ 0 mod 9`), nature needs `15·s/41` integral (`s ≡ 0 mod 41`), giving
**`s = lcm(9,41) = 369`** and a total of `136 × 369 = 50184`. Large, but the same device as
`hair_style`'s ×105 and `lighting`'s ×6, and `LandmarkFamilyTests` pins it.

Two hard requirements for any new landmark:

- **It must be added to `OUTDOOR_LOCATIONS`.** Indoor is *derived*
  (`all − OUTDOOR_LOCATIONS − STUDIO_BACKDROPS`), so omitting it would silently classify the
  Eiffel Tower as an interior and let it draw a hearth.
- **A bare proper noun must be declared in `_NO_ARTICLE_LOCATIONS`** or it renders "set in a
  Times Square". This cannot be derived: of the four capital-initial locations, `Trafalgar
  Square` / `Times Square` / `Shibuya Crossing` are proper-noun *places* while `French
  bistro with mirrored walls`, `Buddhist temple hall` and `Shinto shrine interior` open with
  a capitalised *adjective* and still need "a". `LocationArticleTests` now asserts every
  capital-initial location is declared in one bucket or the other, so adding one without
  deciding fails the suite — deliberate friction, like `PoseGrammarTests`' opener allowlist.

**Indoor landmarks: DECIDED AGAINST (0.84.0) — do not re-propose.** `civic_institutional` and
`transit_travel` have *zero* landmarks, so there is nothing to split from: any add would raise
the famous-landmark frequency **from zero**, which is precisely the overweighting this whole
device exists to prevent. There is no version of the change that keeps the guarantee, so it is
closed rather than parked. (Outdoor landmarks were only addable *because* seven already
existed inside `urban_outdoor` / `nature_outdoor` to split away from.)

### `stage spotlight` is a fixture, the other ten studio values are not (0.83.0)

Measured: studio-family lighting landed on outdoor locations in **25.7%** of outdoor renders.
Most of that is fine and was left alone — `Rembrandt`, `butterfly`, `split`, `soft-box`,
`chiaroscuro`, `low key` and `three-point` describe the *shape of light on a face* and are
achievable on location with a reflector. Only `stage spotlight from above` claims a physical
**rig**, which is the `artificial_hearth` class from 0.82.0. It became its own single-variant
family (`studio` 48 → `studio_shape` 480 + `studio_stage` 48, every lighting weight ×11,
total `228 × 11 = 2508`) with a `STAGE_LOCATIONS` allowlist.

The fixture loop in `constraints.py` was widened from `_INDOOR_LOCATIONS` to **every**
location, so one mechanism can allowlist a rig at an *outdoor* place (`outdoor
amphitheater`) while excluding it from a forest trail. For the three indoor-only fixtures the
extra outdoor rule is redundant with the bucket rule — harmless, since the engine unions
every firing exclusion. The four studio backdrops **must** be in `STAGE_LOCATIONS`:
`studio_stage` is carved out of the family `VOID_ALLOWED_LIGHTING` admits, so omitting them
would strip a void backdrop of a value it legitimately had.

### `expression` under a full mask, and why it got its own block (0.83.0)

A masked subject rendered *"He wears a plush yordle suit. … **His expression is steely.**"*
for every release. The cause was mechanical, never a decision: `covers_face` drops the
**Face / Hair / Makeup** groups, and `expression` lives in **Setting & Shot**.

Fixed via `_CONCEALED_FACE_SOFT_FIELDS`, a **separate** block — separate because `expression`
lives outside the concealed groups and so cannot be reached by group name. `mood` stays: it
describes the scene, not the face. The lock semantics were finished at 0.84.0 (below).

### `barbered_crop`: the first family priced below the per-variant rate (0.83.0)

Seven new hairstyles slotted into existing families (`milkmaid braids`, `rope braid`,
`braided bun` → `braid_long`; `two-strand twists` → `braid_short`; `bubble ponytail` →
`ponytail`; `micro bangs` → `bangs`; `hair puff` → `texture`). Those are **free**: a new
variant subdivides its family and the field-level distribution does not move.

`crew cut` / `textured crop` / `high-top fade` could **not** join `barbered_short`
(fade/undercut/pompadour/quiff) because their **length gate is the mirror image**: a crop is
legal at a buzz and impossible from ear length up, where a fade or quiff is legal at a buzz
and only fails past the shoulders. Culling part of `barbered_short` at mid lengths would
concentrate its frozen weight on the survivors — the 0.64.0 trap. So they need their own
family, and a new family enlarges the denominator: **every other family loses 1.96% relative
share**.

Weight **70** (×2 = 140 after the rescale below) is deliberately *below* convention. The
house rule is weight ∝ original variant count, and this field's rate is 3500/47 ≈ 74.5, so
three crops "should" carry 224 and dilute everything by 6.0%. 70 is the smallest unit the
field already uses (`barbered_shag`, `loose_combover`); it buys the smaller dilution at the
price of each crop sitting ~3.2× rarer than an average value — which is *wanted*, since these
are specific looks and rarity stops the base node reading as barbered.
**Do not "fix" this in a weights audit**; `test_the_deliberately_rare_family_is_rare_on_purpose`
pins it and explains why.

Two traps this hit, both already documented and both hit anyway:

1. **Adding into a split family breaks the split's own arithmetic** (the 0.82.0 pose trap).
   Adding 3 to `braid_long` and 1 to `braid_short` made a `braid_short` variant 8.4% rarer
   than a `braid_long` sibling. Repriced to 1485/405 over 11/3 variants — both exactly 135
   per variant — which forced a **×2 rescale of every `hair_style` family** to stay integral.
   Total 7140.
2. **A length list omission is a partial cull.** `hair puff` was first left out of
   `_LONG_HAIR_STYLES` on the reasoning "a puff is a short-coil look like afro and
   twist-out" — but *both of those are in the list*, so the omission culled 2 of 3 in the
   `texture` family at buzz lengths and would have dumped its full weight on the puff alone.
   Same for `micro bangs` and the bangs buzz rule. This is the `cornrows` lesson (0.72.0)
   recurring: **check the family, not just the physical plausibility.**

`HairStyleFamilyTests::test_split_preserves_every_pre_split_family_share` was **restated** at
0.83.0. It used to pin each pre-existing *value* to a fixed probability, which made the pool
size part of the contract, so it failed on merely *adding* a hairstyle — for the wrong
reason. That is 0.82.0's `PoseFamilyTests` trap, and the fix is the same: assert the
guarantee the mechanism actually makes (family share × one uniform dilution, plus sub-family
proportionality), never a frozen per-value number.

### A widget lock and a preset lock are not the same lock (0.84.0)

The `covers_face` group block and the `covers_hair` block dropped their fields
**unconditionally**, ignoring every lock — so on a masked character, moving the `hair_color`
widget off `Random` did nothing, silently. That is the dead-widget failure mode 0.83.0 closed
for the wardrobe axis, and it was inconsistent with every other suppression in the module
(bald, full-shell skin, `expression`), all of which honour a lock.

**The obvious fix is wrong, and measurement is what showed it.** 0.83.0 assumed
"lock-respecting" meant honouring `locked_clean` and priced the change at "~200 masked entries
change as a drive-by". But `locked_clean` merges three sources — the user's widget choices, a
wired preset's authored `signature`/`physique`/`eyes`, and the Cosplayer builder's injected
`"None"` suppressions — and only the first is a user decision. Of the **295** `covers_face`
entries, **8** pin a concealed field in their `signature` (Princess Leia Organa, The Atom,
Bo-Katan Kryze, Night Thrasher, Denji, Katana, Jane Foster Thor, Ermac), and in every one of
those the mask is an *alternate* costume. Honouring `locked_clean` would render Leia's side
buns under the Boushh helmet — a regression wearing a fix's clothes.

So `generate_character` takes a keyword-only **`widget_locked: frozenset[str] | None`**, built
in `execute` straight from `kwargs` (a field whose widget is not `"Random"`). The rule both
blocks now share is one sentence: **the mask hides the face; only your own widget overrides
it.** `_CONCEALED_FACE_SOFT_FIELDS` was narrowed from `locked_clean` to the same set so there
is a single semantic — verified a no-op on shipped data (`Harley Quinn` is the only entry
pinning `expression` and she is not masked; **no archetype sets `covers_face` at all**).

Properties worth keeping in mind: the parameter defaults to empty, so every other caller —
tests, gallery builders, the preview script — is **byte-identical** and the change is purely
additive; and it consumes **no RNG**, because locked fields already skip the randomize loop, so
this only decides whether an already-drawn value survives to the output.

**The generalisable rule:** when a suppression needs to "respect locks", first ask *whose*
lock. A pack that injects preset values into the same mapping as user choices has two
different things in one dict, and the coherence rules almost always mean the user's.

### Two pose contradictions, one rescale (0.84.0)

Both are the `studio_stage` shape from 0.83.0 — *a value naming a physical thing the scene or
the subject does not have gets its own family, and the family is excluded whole* — and both
were bundled into a single `POSE_FAMILIES` rescale so the seed drift is paid **once**.

1. **A giant cannot perch on the edge of a seat.** `_scale_coherent_pool` already forces a
   giant outdoors, and there is no seat outdoors. An audit of all 38 poses at giant scale
   found this to be the *only* genuinely impossible one — `leaning against a wall` reads
   **better** at scale, since the wall becomes a building. `pose` therefore joins `shot_type`,
   `location` and `body_type` in `_scale_coherent_pool`, giant-only: a three-foot subject on a
   seat edge is fine, so `tiny` is untouched.
2. **A held prop cannot share a hand with a two-handed pose.** With the Cosplayer node's prop
   toggle on, the prose rendered *"She is posing with hands in pockets, holding Mjolnir"* and
   *"holding both hands loosely clasped, holding Mjolnir"*. **468 of 1,732** cosplayers carry
   a `prop`; measured over 4,000 renders, **14.37%** of prop-enabled output hit this (analytic
   14.51%). `_performable_poses` gained a third branch, needing **no new parameter** —
   `held_item` is a `_PRESET_HIDDEN_FIELDS` lock, so it is in `resolved` from the first line
   of `_randomize_fields`, exactly like the `hair_length` and `outfit_description` it already
   reads.

**The exclusion is deliberately narrow.** Only *both*-handed poses go
(`standing with arms crossed`, `standing with hands clasped behind the back`, `holding both
hands loosely clasped`, `stretching both arms overhead`, `posing with hands in pockets`).
One-handed poses stay legal — `resting chin on one hand`, `adjusting one cuff`,
`running one hand through the hair` — because the free hand holds the prop, which is the
natural reading and a better image than dropping them.

**The arithmetic.** Four families split; `standing` and `seated` are 30/9 per variant so they
need thirds, which makes **×3** the scale that closes all four:

```
standing 30/9  ->  standing 70/7  + standing_hands_bound 20/2   (10 per variant)
seated   30/9  ->  seated   80/8  + seated_perch         10/1   (10)
gesture  12/4  ->  gesture  18/2  + gesture_two_hands    18/2   ( 9)
gesture_garment 9/3 -> gesture_garment 18/2 + gesture_pockets 9/1 ( 9)
leaning 18/3 · motion 18/4 · gesture_hair 9/1 · looking 36/5
total 324 = 108 x 3
```

Verified analytically: no value lost, worst per-value probability delta **3.5e-18**, and each
of the four exclusion sets is an *exact* union of whole families with the survivors staying
proportional to within float noise.

**One trap the split sets, and the fix for it.** `gesture_pockets` was carved out of
`gesture_garment`, so `GARMENT_DEPENDENT_POSES` had to be re-derived as the **union** of both
— pockets are the most garment-dependent pose there is, and leaving the derivation alone would
have quietly let a mascot suit put its hands in pockets it does not have. Any future split of
a family that some suppression set is derived from carries the same hazard:
**check every set derived from a family before you split it.**
`PoseFamilyTests::test_dependent_pose_sets_are_whole_families` now asserts *every* pose
suppression set is a union of whole families, so a partial cull cannot be introduced silently.

### A second camera axis, a selfie, and eye contact (0.85.0)

Pairing with a downstream rendering pack ([Stylebook](https://github.com/EnragedAntelope/comfyui-stylebook))
surfaced a real gap in the "camera-only" doctrine `shot_type` has carried since 0.63.0: distance,
height, angle and lens say nothing about *layout* — where the subject sits inside the frame. Two
`shot_type` values (`wide shot with subject at center` / `off-center`) had already leaked layout
into the camera field, which was the tell.

**`composition`** is the new field for exactly that: rule-of-thirds, centered symmetry, negative
space, a tight crop, leading lines, a low/high horizon, filling the frame. Flat like `shot_type`
(absent from `FIELD_FAMILIES`) for the same reason — any coherence exclusion re-picks uniform. Two
rules bound the value list, both inherited from why `shot_type` looks the way it does: no physical
object (the 0.63.0 lesson — an object in frame is something the model has to invent) and no camera
restatement (that is `shot_type`'s axis, and a second statement of it renders twice). Seven
generated `CONSTRAINT_RULES` keep the two fields from contradicting each other (a tight shot
excludes the four layouts that presuppose an environment; a centered/off-center shot excludes its
direct opposite; a wide establishing shot excludes the two tight-crop layouts) — see the loops at
the tail of `constraints.py`.

**`selfie framing at arm's length`** joins `shot_type` as one deliberate exception to
"camera-only, no second object": it still names only a camera position, not a phone or an arm, and
unlike the deleted doorway/window/foliage values it puts nothing *between* camera and subject —
the frame is already "a photographed cosplayer". It reuses the *existing* `HAND_OCCUPIED_POSES`
constant (built for the 0.84.0 held-prop rule) rather than a hand-listed subset: `_performable_poses`
now drops that whole set when `shot_type` is the selfie value, exactly as it already does when a
signature prop occupies a hand. One more generated rule excludes the environment-dependent
`composition` values under a selfie, reusing the same list the tight-shot rule uses.

**Eye contact** had no field at all — a real gap, since Stylebook's own README already credits
Identity Forge with owning it. Two variants, `looking directly into the camera` and
`looking off past the camera`, were grown into the existing `looking` `POSE_FAMILIES` entry in
place (family weight unchanged, 5 -> 7 variants) — the documented bias-safe channel, not a new
family and not a re-weight.

**On the Stylebook pairing itself: docs and tooltips only, no default change.** `lighting` and
`mood` keep defaulting to `Random` — most users run this pack standalone, and `lighting` in
particular drives 165 generated location-coherence rules that would otherwise sit unused. The
README gets a short "Using with Stylebook" section mirroring Stylebook's own, and both fields'
`FIELD_HELP` gained one extra sentence pointing at `None` when a downstream pack owns the axis.

## Gotchas cheat-sheet

- **An extreme scale needs the SCENE, not just the prose (0.79.0).** "Colossal and fifty feet
  tall" is a claim about the subject's relationship to their surroundings, so it only survives
  into an image when the frame holds something to measure against. Measured before the fix, 71
  giant entries x 30 seeds drew a scale-showing framing 26.2% of the time and an outdoor
  location 25.9% of the time — a giant that could actually read as giant was about 1 render in
  14, and ~7% called the subject "petite" in the same sentence as the scale phrase.
  `_scale_coherent_pool` narrows three fields when a giant tier is active: `shot_type` to
  `_SCALE_SHOWING_SHOTS`, `location` to `OUTDOOR_LOCATIONS`, `body_type` away from
  `_STATURE_BODY_TYPES`, and (0.84.0) `pose` away from `FURNITURE_DEPENDENT_POSES` — a
  consequence of the location rule, since forcing the scene outdoors leaves no seat to perch
  on. `tiny` gets only the light framing rule. It runs inside the randomize
  loop, which has already skipped every locked field, **so an explicit user lock is never
  narrowed**; an empty result falls back to the unfiltered pool (the 0.63.0 empty-studio-pool
  precedent — warn and keep, never raise).
  - *The bias argument, which is what made this buildable.* `shot_type` and `body_type` are
    flat — no `FIELD_FAMILIES` entry, no `weights` map — so narrowing them stays uniform.
    `location` **is** family-weighted and passes only because its families bucket perfectly:
    `domestic`, `food_drink`, `retail_services`, `leisure_fitness`, `civic_institutional`,
    `work_industrial` and `transit_travel` are entirely indoor; `urban_outdoor` and
    `nature_outdoor` entirely outdoor. Filtering to outdoors drops seven WHOLE families and
    leaves the surviving two proportional (20 : 15) — the whole-unit drop the family-weight
    rule demands, never a partial cull. `ScaleCoherenceTests.test_the_location_filter_drops_
    whole_families` pins this: **a location added to a family that spans the indoor/outdoor
    boundary would silently turn this coherence rule into a distribution bug**, and that test
    is the only thing that would catch it.
  - The tier reaches the engine two ways: the manual `size_scale` widget, and a wired
    Cosplayer entry's own `size_scale` via the reserved `_SCALE_TIER_KEY` (`"__scale_tier__"`),
    which travels exactly like the `covers_*` flags. **The widget wins**, consistent with the
    height override it already performs. `short` and `large` are in neither tier set — "well
    over seven feet tall" is a very tall person whose scene still works.
  - Ordinary output is untouched (verified: 300 seeds byte-identical across the change). Seeds
    *do* drift for giant/tiny cosplayers.
- **A constraint re-pick must exclude every rule firing on that field, not just its own
  (0.78.0).** `_apply_constraints` filtered the re-pick pool with only the current rule's
  `excludes_values`, so the replacement it drew was frequently forbidden by a *different* live
  rule. Rule A re-picked a value rule B bans, B re-picked one A bans, and whatever the 12th
  pass happened to hold got emitted. It hid for releases because convergence was likely while
  few values were banned; the 0.78.0 `loose` split cut the legal hair_style set on a buzz cut
  from 7 of 33 to 2 of 33 and it began firing constantly — buzz cuts with high ponytails, afros
  on pin-straight hair. The fix collects the union of all currently-firing exclusions for the
  target and converges in one pass. **If you add a rule that makes a field's legal set small,
  this is the failure mode to expect.**
- **`covers_body` / full-shell detection is spelling-sensitive (0.78.0).** `_FULL_COVER_RE`
  matched only American `armor` while `data/cosplayers.py` carried 32 British-spelled values,
  so those characters silently failed the shell test and drew necklaces and drop earrings over
  plate armour. The data is normalised to `armor` (enforced by `FullCoverSpellingTests`) and
  the regex now accepts `armou?r` everywhere, because `user_options.json` is free text that no
  validator can reach.
- **A costume does NOT suppress jewellery, but naming one no longer doubles it
  (0.78.0, fixed generally at 0.83.0).** `_COSTUME_SUPPRESSED_EXTRAS` still covers
  `bag` / `watch_type` / `hair_accessory` / `accessories` only — deliberately, since earrings
  over a costume are coherent (the closed 0.66.0 decision). What changed is the *other* half:
  a costume string that **names** a necklace, earrings, a ring, a bangle, a brooch or a bag no
  longer renders a second, different one, because `WORN_ITEM_RES` drops the matching field.
  Pinning `"necklace": "no necklace"` in `signature` is therefore **belt-and-braces, not a
  requirement** — the 28 entries that do it keep it (removing a pin adds an RNG draw and
  drifts that character's seed), but a new entry does not need it. Still worth wording costume
  prose deliberately: the general rule is regex-based, so an unusual synonym can slip past it.
- **Face colour and body colour cannot differ through the skin anchor alone (0.78.0).** The
  anchor plants one colour and `_format_prose` restates it on the face and hands, so Krusty's
  white greasepaint face over a yellow body rendered as a flat contradiction. The explicit
  `body_paint: True` + `skin: "<colour>"` pair is the escape hatch: it forces the suppression
  without needing a marker phrase and pins the anchor to whichever colour matters most —
  normally the face, being the high-attention region.
- **`ethnicity` is suppressed under a full-body colour (0.78.0).** It was the last
  skin-describing field still randomizing there and the loudest, landing in the lead sentence
  ("a 19-year-old Chilean man … with chalk-white skin"), which t2i resolved into an ordinary
  human face above a coloured body. Same argument as the 0.65.0 decision for fully-encased
  characters. Note this **drifts seeds for body-paint entries only** — a locked field stops
  consuming an RNG draw.
- **A male character's face makeup must be authored into the costume prose (0.78.0).** The
  global `Male → makeup_style: "no makeup"` rule cascades through every cosmetic sub-field, so
  the engine will never supply makeup on a man. Anything a male character wears on his face —
  Lobo's blacked-out lips, a clown's greasepaint, corpse paint — renders only if the costume
  string says so.
  **This binds archetypes too, and the failure there is silent (0.96.0).** The whole makeup
  sentence in `_format_prose` is gated on `makeup_style` being present, and `makeup_style`'s
  *male* pool holds only natural values, so a male archetype variant that locks
  `eyeliner`/`eye_makeup`/`lips_makeup` gets **no makeup sentence at all** — the locks are
  accepted, validate clean, and never reach the prose. Caught on the `Visual Kei` and
  `Cybergoth` male variants, whose whole point is the makeup. The fix is the same one this
  bullet already prescribes: pin `makeup_style: "no makeup"` (so no contradictory "soft natural
  makeup" lead-in can roll) and write the makeup into `outfit_description`, which always
  renders. Same class as any dead widget: a field accepted on every build and never voiced —
  check what `_format_prose` actually reads before authoring content into a field.
- **A franchise-disambiguated key must not restate its franchise in the label (0.77.0).** The
  cosplay prefix is built as `f"{cosplay_of} ({franchise})"`, so the 29 entries whose key is
  disambiguated *by their franchise* rendered it twice — `Cosplaying as Red (Pokemon)
  (Pokemon)`, `Zero (Code Geass) (Code Geass)`, `Selene (Underworld) (Underworld)`. It had been
  shipping in the prompt text for many releases and nothing caught it, because the roster
  validator checks key *uniqueness* and never looks at the rendered label. Fixed in
  `nodes/identity_forge.py` with an `endswith(f"({franchise})")` guard rather than by renaming
  26 shipped keys, which would have broken every saved workflow that locked one. Prose-only,
  zero RNG draws, no seed drift. The disambiguation convention itself is unchanged — keep using
  `Christie (Dead or Alive)`; the label just no longer stutters.
- **…and that `endswith` guard only caught the exact case (0.88.0).** It tests whether the
  parenthetical *is* the franchise, so four keys kept stuttering straight through it for
  releases: `Ms. Marvel (Kamala Khan) (Marvel)` and `Ms. Marvel (Sharon Ventura) (Marvel)`
  (the franchise is in the *base name*), `Duke Nukem (video game) (Duke Nukem)` (same), and
  `Mai (Avatar) (Avatar: The Last Airbender)` / `Jeanne d'Arc (Fate) (Fate/Grand Order)` /
  `Rebecca (Cyberpunk) (Cyberpunk: Edgerunners)` (the parenthetical is a *shorter form* of the
  franchise). Merging the Persona installments added a seventh, `Joker (Persona 5) (Persona)`,
  which is how it was noticed. `_name_already_carries_franchise()` now tests three shapes:
  exact match, either string being a whole-word prefix of the other, and the franchise
  appearing as a whole word in the base name. Both tests are **word-bounded** — a bare
  substring check fires on any name containing a short franchise string, and a bare prefix
  check lets a one-letter parenthetical swallow a long franchise.
- **…and the seventh key was a data bug, not just a label bug (0.90.0).** Suppressing the
  stutter made `Joker (Persona 5)` *render* correctly while leaving the dropdown claiming an
  installment the pack does not group by. Renamed to `Joker (Persona)`, and the shape is now
  rejected by `validate_data.py` rather than merely papered over at the label layer — see
  curation checklist rule 6. Six of the seven keys were legitimate all along; only this one
  needed the data to change.

  **It is deliberately scoped to keys that carry a `(...)` disambiguator**, which is what the
  0.77.0 rule is about. It does *not* touch an eponymous key whose franchise repeats it —
  `Shrek (Shrek)`, `Godzilla (Godzilla)`, `Sterling Archer (Archer)`. Broadening it there is a
  one-line change that rewrites **91 more entries' prose**, and because `entry_hash` hashes the
  entry dict and cannot see a prose-only change, the gate would *not* flag them — 91 published
  gallery images would silently stop matching their prompt. That is a separate decision with a
  real re-render bill, not a side effect, and `test_the_rule_is_scoped_to_disambiguated_keys_only`
  pins it so it is not "tidied up" by accident.
- **The franchise filter is a view, not an input (0.89.0).** With ~1,800 bare names in one
  flat combo and no franchise shown anywhere, a user who remembers a *look* had nothing to
  narrow by. The obvious fix — decorating each option as `"Ann Takamaki — Persona"` — is not
  available: `io.Combo.Input` has no display/value split, so the option text **is** the stored
  value, and ComfyUI validates combo values at `/prompt` (the same fact that forces
  `render_gallery.py` to resolve prompts in-process). Decorating them would invalidate the
  character stored in every saved workflow.

  So `js/identity_forge_cosplayer.js` adds a `franchise_filter` combo with **`serialize:
  false`**, the same mechanism the main node's group headers and bulk buttons already use.
  There is **no schema change**, so `define_schema()` and `tests/frontend/fixtures/nodes.json`
  are untouched, and the filter sits where it belongs, directly under `character`.

  > **The compatibility claim originally written here was wrong, and it cost the maintainer
  > every Cosplayer node in their workflows (corrected 0.90.0).** It read: "ComfyUI skips
  > non-serializing widgets when writing `widgets_values`, so the serialized array is
  > byte-identical … a workflow saved by an older version loads unchanged." The first half is
  > true and the second does not follow. **`serialize: false` is honoured when WRITING and
  > ignored when READING.** Measured on a live instance: this node has 8 widgets, two of them
  > non-serializing, and `serialize()` still emits **8** values — one per `node.widgets` entry —
  > with `configure()` reading them back the same way. A workflow saved before 0.89.0 carries 7
  > values against 8 widgets with the filter at index 1, so every widget after `character` was
  > restored one slot out.
  >
  > `tests/frontend/cosplayer.test.mjs` did assert the claim rather than assume it — but only
  > the **write** path, which is the half that holds. Asserting half a round trip is how a
  > wrong claim survives a green suite. 0.90.0 added a `configure` wrapper
  > (`padLegacyCosplayerValues`) that splices the filter's default into its slot when the
  > incoming array is exactly one short, and the same repair on the main node. See
  > "Adding a field without breaking saved workflows".

  Two UX invariants it must not break, both tested: filtering never changes the current
  selection (an out-of-franchise pick stays selected *and* stays in the list), and the
  `None` / `Random —` sentinels survive every filter. Every filter is derived from a pristine
  snapshot of the option list, never from the currently-filtered one, so narrowing is always
  reversible. `random_scope` is a different control and is untouched — it limits what the
  `Random —` entries roll on the backend; the filter only limits what the dropdown shows.

  The generated map is built by **AST-parsing** `data/cosplayers.py`, not importing it:
  importing runs `apply_user_cosplayers(COSPLAYERS)` and would bake a maintainer's private
  `user_options.json` characters into a committed, published file. A user-added character is
  therefore absent from the map, which is the right failure mode — the frontend treats an
  unknown name as unfiltered and always shows it.
- **Count the family before adding a coherence exclusion (0.77.0).** Whether an "obviously
  correct" exclusion is safe depends entirely on whether it removes a **whole**
  `FIELD_FAMILIES` family. Excluding `curtain bangs` + `blunt bangs` on a buzz cut is safe
  because those two *are* the `bangs` family; excluding the five equally-impossible `loose`
  family members alongside them would have dumped that family's full frozen weight on two
  survivors. Same rule, same reason as the lighting buckets — check
  `HAIR_STYLE_FAMILIES`/`POSE_FAMILIES`/etc. **before** writing the rule, not after. The
  deferred half is written up under "Considered and deferred".

- **A character rendering in the wrong *medium* (drawn / illustrated / 3D) is almost never a data
  bug.** Investigated at 0.66.0 for Rydia (FF4), who renders as official art. A scan of **every
  string value in all 1095 cosplayer entries** for style-biasing words (`anime|animated|cartoon|
  illustrat*|drawn|chibi|cel-shaded|comic-book|manga|stylized|toon|figurine|render*|painterly|
  sketch*|2D`) found **20 hits, 19 benign**: `drawn` was always "a bow drawn", `stylized` always
  described an emblem's design. Only Obi-Wan (Force Ghost)'s "robes **rendered** in a luminous
  glow" was a plausible 3D trigger, and it was reworded to "suffused with". Rydia's own entry is
  clean. The cause is **model association with the character name** — same class as the Mt. Lady
  finding (0.59.0) and not fixable per-character. Note the structural gap behind it: the node
  emits **no photographic anchor at all** (the prose opens `Cosplaying as X (Franchise): a
  33-year-old …` and never establishes a medium), so style is entirely the user's to supply
  downstream. An optional realism-anchor toggle was floated and **not built** — flagged here so
  the next person measures before assuming the data is at fault.
- **Diff a new costume string against the fields the archetype already locks.** The 0.63.0 lesson
  was props double-describing a costume object; the same trap exists for `accessories`,
  `bag` and `hair_accessory`. Found at 0.66.0: **Archaeologist** wrote "a brimmed explorer hat"
  into its costume *and* locked `accessories: "wide brim sun hat"` — it rendered two hats for
  several releases. **1940s Factory Worker** locks `hair_accessory: "thin scarf tied in hair"`, so
  the obvious Rosie bandana would have tied a second scarf on the same head. `bag` is unlocked on
  most archetypes, so a costume must never mention one. Whichever field owns the object, the other
  must stay silent.
- **`gender == "Any"` resolves to a concrete `Female`/`Male` per seed** (first rng draw in
  `generate_character`) so the person is coherent — the gender gate and randomizer then draw from
  one pool, no beard beside a feminine bust. An anatomical lock decides it (`_gender_from_locks`:
  a beard -> Male, a feminine-only `bust` -> Female) so explicit choices are honored; otherwise an
  even 50/50. The old unioned androgynous mode (both pools mixed, *they/them* pronouns,
  `_meta.gender` stays `"Any"`) is preserved **only** when `wardrobe == "Any"`, the explicit
  "anything goes" escape hatch.
- **Archetype list values (0.37+).** Any archetype (or variant) field value may be a `list[str]`
  of curated alternatives — `build_archetype_json` seed-picks one uniformly (no bias by
  construction), so one archetype yields a range of looks. An `outfit_description` list picks an
  alternative costume template before its slots fill. Draw order is append-only for seed
  stability: archetype pick → base costume template pick + slot fills → variant costume picks +
  fills → ONE scalar list pass (base fields in template order, then Female/Male variants) before
  the Essentials filter, so lock level never shifts draws. `gender` may never be a list; every
  element must be a real field option; the validator enforces len ≥ 2, no dups. The 0.39 sweep
  widened 150 hair/eye locks to shade-family lists (the original shade leads each list);
  hair_style/location/lighting locks deliberately stay fixed (look/scene-defining).
- **Bald heads (0.50+).** `hair_length` has a male-only `"bald"` option (comb-over precedent).
  When it resolves — locked or randomly drawn — the engine drops the *randomized* scalp-hair
  fields (colour/texture/style/part/highlights/accessory; locked ones survive, locked-wins) and
  prose voices "his head is bald"; `facial_hair` is untouched. `_build_option_pool` never draws
  `bald` under an already-locked `hair_style`. Mirrors the Cosplayer `_BALD_SUPPRESS` mechanism.
- **Contrapositive constraint repair (0.50+).** When an exclusion rule's *target* is locked to an
  excluded value (a locked "sleek bun" against a randomly drawn "buzzed very short" length), the
  engine re-rolls the randomized *trigger* away from every conflicting trigger value instead of
  warning and leaving the incoherent pair. Both-locked contradictions and control-field triggers
  (gender, scope) still warn-and-keep.
- **Texture↔style coherence (0.53+).** Only `afro` and `twist-out` are physically texture-bound
  (the style *is* the coil pattern), so `constraints.py` excludes them when a straight/wavy
  `hair_texture` is drawn (`_NON_COILED_TEXTURES` × `_TEXTURE_BOUND_STYLES`). Braids, locs, cornrows
  and bantu knots read fine on any texture and stay unpaired. A preset that locks `afro`/`twist-out`
  is repaired by the contrapositive rule above (the random texture re-rolls toward a coiled value).
- **Mood and expression vocabularies are disjoint** (0.36+, test-enforced): they randomize
  independently, so a shared word ("playful") could double in one output. When adding options to
  either field, pick words the other doesn't use (mood is the scene's tone, expression the face).
- **Per-gender archetype variants** — an archetype may carry a `variants: {"Female": {...},
  "Male": {...}}` block so *one* selection yields two coherent looks (a 1980s Aerobics leotard vs
  the male tank/shorts). The base dict holds only shared fields + a soft `gender` lean (e.g.
  `"Female"`, applied when the widget is `"Any"`, overridable by the widget). `build_archetype_json`
  fills each variant's costume slots and Essentials-filters it, emitting `_meta.variants`;
  `generate_character` folds `variants[resolved_gender]` into the locks **after** the coin-flip and
  before the gender gate, so the variant's look wins. Author the divergent fields (outfit, hair,
  body, makeup) in the variants and keep `gender` on the base — never inside a variant.
  `merge_preset_documents` carries `_meta.variants` through chaining (downstream wins).
- **`smile_type` is the mouth/smile field and IS rendered** (in `_format_prose` face features);
  `constraints.py` buckets every `expression` into closed / soft-smile / open so the mouth never
  contradicts the face. (It was dead — resolved but unrendered — before 0.33.)
- Duplicate `COSPLAYERS` / `CREATURES` / `ARCHETYPES` keys silently override — the last
  wins. `validate_data` now AST-scans the roster literals and fails on a duplicate key,
  and rejects duplicated values inside any field option pool (a hidden 2x draw weight).
- `signature`/`physique` values are gender-gated downstream; prefer unisex fields for crossplay.
- Physique↔fitness coherence is soft (0.46+): exclusion rules cull only the outright
  contradictions (soft-curved/plus-size builds never roll `muscular`; athletic/toned/fit
  builds never roll `sedentary`). Mid-range pairings randomize freely; locks on both
  fields still win.
- **A downstream Full-preset Archetype overrides a chained Cosplayer's costume/skin.** Presets
  merge with the *downstream* node winning field-by-field (`merge_preset_documents`), so
  `Cosplayer -> Archetype (Full preset) -> IdentityForge` lets the archetype's `outfit_description`
  (and any Body `skin_tone`) replace the cosplayer's -- e.g. She-Hulk chained into a "Tennis Player"
  Full preset comes out in tennis whites with a human tone, losing the green. To **layer** a tilt
  onto a cosplay instead of overwriting it, set the archetype (or cosplayer) to **Essentials** so it
  emits only the look groups and leaves the rest to flow through.
- **Every node with an auto-advancing widget re-executes each queue via `fingerprint_inputs`.**
  `IdentityForge`, `Archetype`, `Cosplayer` and `Creature` return `float("nan")` from
  `fingerprint_inputs`, forcing ComfyUI to re-execute them -- otherwise a widget advanced by
  `control_after_generate` can be served from cache and the output "sticks" (ComfyUI#11905).
  The trigger is the auto-advancing widget, not the seed as such. Pure cache control (no RNG):
  a *fixed* seed still reproduces exactly, and identical output keeps expensive downstream nodes
  cached. **The Turnaround is the counter-example and stays one:** it carries no
  `control_after_generate` widget and no RNG, so it is a pure function of its inputs and
  ComfyUI's normal caching is correct for it. It had the NaN signature at 0.98.0 only because
  its `index` combo auto-advanced; 0.99.0 deleted the widget, so the workaround went with it.
- Adding RNG draws in the creature node mid-sequence shifts seed→creature mapping — append draws
  at the end.
- The roster is large (~1300 cosplayers across ~263 franchises, ~195 creatures): always grep
  the current keys before adding to avoid silent overrides (the validator's duplicate-key scan
  backstops this).
- **`franchise` names a franchise, not a medium (0.72.0).** Eight entries shipped with the
  placeholder `"Movie"` (Dracula, Frankenstein's Monster, The Wolf Man, The Mummy, Bride of
  Frankenstein, Godzilla, Rambo, Indiana Jones). It read badly in the cosplay label
  ("Cosplaying as Dracula (Movie)") and would have produced a nonsense `Franchise: Movie`
  scope, so they were refranchised (the five Universal horror leads share
  `"Universal Monsters"`) and mapped into `_CATEGORY_FRANCHISES["Movies & TV"]`.
  `FranchiseLabelTests` now rejects any medium-as-franchise label. The two `"Comics"` entries
  were resolved in the same release (see below).
- **The two `"Comics"` placeholders, resolved (0.72.0).** Both were flagged as needing a source
  and then checked against the actual characters.
  *Shana the She-Devil* was **deleted**: no such character exists. The name was a one-letter
  drift off Marvel's *Shanna the She-Devil* — which ships, correctly, in its leopard-print
  jungle look — while the *described* look (red bikini, fire-red very long hair, green eyes,
  bronzed skin, broad-bladed sword) was Red Sonja, who also ships. It shared 3 of 4 signature
  fields and 2 of 3 physique fields with Red Sonja. Sheena, the character Shanna was created to
  imitate, is on the roster too, so all three real subjects stay covered and nothing was lost.
  *Lunatica* → **`La Lunatica`, franchise `Marvel`** (X-Men 2099). The entry had the leather and
  the tall, muscular build right but every high-attention colour trait wrong: it shipped red
  hair, pale lavender skin and yellow reptilian slit eyes, where canon is an albino-pale psychic
  vampire with **bone-white hair and skin, burning red eyes** and pronounced fangs, dressed in
  black leather that deliberately leaves skin bare (her power works on touch). Corrected to
  canon, keeping the canonical `smooth, flawless bone-white skin` phrasing so the body-paint
  suppression and colour anchor both fire.
  **Lesson for future roster work:** a wrong `franchise` is worth treating as a smell, not just
  a tidiness issue. Both placeholder entries turned out to have substantive problems underneath
  — one was not a real character at all — because nobody could name the source when they were
  written. The same check paid off again at 0.73.0: *Gabimaru* was about to be written with
  black hair from memory, and is canonically **white**-haired.
- **Hell's Paradise added (0.73.0).** Four entries under the new `Hell's Paradise` franchise
  (mapped into `Anime & Manga`): **Gabimaru** (protagonist), **Yamada Asaemon Sagiri**
  (deuteragonist), **Yuzuriha** and **Akaginu**. Three things worth knowing for future anime
  additions from this run:
  *Anime/manga colour splits are real.* Gabimaru's pupils are yellow in the anime and red in the
  manga; Yuzuriha's hair is black in the manga and purple in the anime, and sources give her eyes
  as red, blue *and* purple. Where the anime reading is the widely-cosplayed one it leads
  (Yuzuriha's purple garb, Gabimaru's yellow eyes); where sources genuinely conflict, the field is
  **left unlocked** rather than guessed at — Yuzuriha ships with no `eye_color`, so it randomizes.
  Asserting a wrong colour is worse than randomizing one.
  *A half-mask is not `covers_face`.* Gabimaru's battle look pulls a turtleneck over the nose;
  the eyes and brow still show, so it is a plain `costumes` alternate. `covers_face` is for a
  fully enclosed head only — setting it here would have wrongly dropped the whole Face group.
  *Sagiri wears her sword*, so she carries a `prop_costume` that empties the scabbard (the Zoro
  pattern) — prop off leaves "a katana in a black lacquered scabbard" at the hip, prop on swaps
  to "an empty black lacquered scabbard" and puts the drawn blade in her hands.
- **A free-text `eyes` override may name its own eye part (0.74.0).** The prose builds
  `"{colour} {shape} eyes"`, so the ten overrides that already end in an eye part rendered
  "...has green with vertical cat-slit **pupils eyes**" (Cheetah, Sephiroth, Geralt, Hu Tao,
  Lobo, Voldemort, Maz Kanata, Nightstar, Power, and Nia Teppelin, who surfaced it). `_EYE_PART_RE`
  drops the noun when the value already ends in `eyes/pupils/irises/sclera/lenses` — the same
  guard, for the same reason, as the `skin_tone` material-noun check ("dark blue scaled-skin").
  Fixed in the **engine**, not by rewording ten values: the data phrasing is good prose and the
  next entry describing a pupil would have hit it again. `EyePartPhrasingTests` sweeps every
  shipped override.
- **…so an `eyes` override must be a *noun phrase*, not a clause (0.76.0).** `_EYE_PART_RE`
  only looks at the **end** of the string, and the value is dropped into a feature list:
  `"She has {eyes}, a wide nose, thin lips…"`. A multi-clause value therefore reads badly
  whichever branch it takes — `"glowing cyan, the left one sealed shut beneath an azure sigil
  eyes"` (noun appended to the wrong clause) or `"pink with a slitted pupil, a wide nose"`
  (noun suppressed, so the phrase never resolves as eyes). Two shapes are safe:
  a short colour phrase (`"molten gold"`, `"glacial ice blue"`) or a phrase whose **last word**
  is the eye part (`"one pale blue eye and one darkly dilated eye"`). **Anything asymmetric or
  conditional — a sealed eye, a sigil, an eyepatch — belongs in the costume prose**, which is
  free-form, alongside markings and tattoos. Two long-standing values were reworded in place
  under this rule (Delirium, Victor von Gerdenheim).
- **Gurren Lagann, High School DxD and friends (0.74.0).** Twelve entries; the reusable notes:
  *Enhancing beats skipping (rule 2 in practice).* **Yoko Littner** already shipped with a solid
  entry, so per the curation checklist she was not skipped but *enhanced* — she gained the
  "Yomako-sensei" timeskip teacher look and the Dai-Gurren officer suit. The teacher look carries
  its own `signature` because the glasses come with hair worn down instead of her ponytail; a
  plain-string alternate would have left the ponytail on.
  *A worn signature object is not a `prop`.* **Issei Hyoudou**'s Boosted Gear is a gauntlet, so it
  belongs in the costume — which also, correctly, trips `_GLOVE_RE` and drops randomized
  nails/rings that would otherwise render on top of an armoured hand. Compare **Kamina**'s nodachi,
  which is carried and so *is* a prop.
  *Tattoos are skin, not a pelt.* **Kamina** is bare-chested with blue flame tattoos up both arms:
  no body-paint marker phrasing and no `covers_body`, so his tan `skin_tone` stands (the Maui rule).
  *A tint is not a body-paint colour.* **Nia Teppelin**'s pale-pink skin is a tint, not an all-over
  non-human colour, so it stays an ordinary `skin_tone`; using the marker phrasing would have
  suppressed her face and makeup for no gain.
  *An object-character still needs a wearable look.* **Babette** is a feather duster for the whole
  film, so she is written the way she is actually cosplayed — a French maid whose skirt and
  headpiece are built from ostrich plumes — with her restored human form as the alternate. A
  literal prop object would have failed rule 1.
  *A shared uniform needs per-entry differentiation.* The five Kuoh Academy entries would
  otherwise be near-identical costume strings, so each spells out what distinguishes it (Koneko
  drops the shoulder cape, Akeno adds calf socks and a hair ribbon) and the alternates carry the
  looks that genuinely differ — Akeno's miko outfit, Asia's nun habit.
- **Gwen Tennyson and Yzma added (0.73.0)**, each demonstrating a mechanism worth reusing.
  *Gwen* rolls four looks and shows **an alternate overriding `signature`**: the three teen
  outfits share her waist-length hair, but the Original Series look is a short clipped bixie, so
  that alternate is a dict carrying its own `signature` rather than a plain string. `signature`
  is in `_LOOK_OVERRIDE_KEYS` precisely for this. She gets **no prop** — her mana is an energy
  effect, not a held object, matching Green Lantern and Scarlet Witch.
  *Yzma* is the instructive one: she is lavender-skinned **and** her makeup is iconic, and those
  two facts fight. The skin-native phrasing auto-suppresses `makeup_style` (override=True, so
  even an explicit signature lock loses), which would have erased the arched brows and false
  lashes she is entirely recognisable by. The fix is to write the makeup into the **costume
  prose**, which is voiced verbatim and untouched by the suppression — the same escape the bald
  and free-text-eye cases use. Her headdress fully encloses the scalp while the face shows, so
  `covers_hair` with no hair signature. Her orb earrings are omitted for the same reason as
  Fern's bracelet. Her age is locked in `signature` (the `Tellah` precedent) so she reads elderly
  in both look levels.
  **The general rule these three surface:** when a suppression mechanism would delete a trait the
  character is defined by, move that trait into the costume prose rather than fighting the
  suppression or disabling it with an explicit flag.
- **Fern added (0.73.0)**, alongside the existing Frieren entry, with the Count Granat winter
  look as an alternate. Her mirrored lotus bracelet was deliberately **left out** of the costume:
  the Jewelry group is not in `_COSTUME_SUPPRESSED_EXTRAS`, so naming a bracelet in costume prose
  would double against a randomized one — the wart the gotchas warn about for `accessories` /
  `bag` / `hair_accessory`. Her butterfly hair clip *is* included, because `hair_accessory` **is**
  costume-suppressed and so cannot double. Worth checking per-item, not per-costume.
  **Superseded at 0.83.0:** `WORN_ITEM_RES` now drops `bracelet` when the costume names one, so
  the lotus bracelet could be written in. Left out anyway — this is a content call, not a bug,
  and rewording a shipped costume changes that character's render for no functional gain.
- **Costume prose must not hardcode a gendered pronoun (0.72.0).** `costume` is voiced verbatim
  after "She/He wears …", and the *person's* gender is the IdentityForge widget, not the
  character's — that is the whole basis of crossplay. Ten entries carried `her`/`his`/`she`/`he`
  (She-Hulk, Jolly Green Giant, Iori Yagami, Heihachi Mishima, Paul Phoenix, Medusa, Allen the
  Alien, Liz Sherman, Rumi, Zoey), so a man cosplaying She-Hulk rendered "…covering **her** face
  and entire body". All ten were reworded to a neutral construction ("covering the face…", "with
  long crimson hair…"), preserving each body-paint marker verbatim so `_BODY_PAINT_RE` and the
  colour anchor still match. `CostumePronounTests` covers `costume`, `mask`, `prop_costume` and
  every `costumes` alternate.
- **Prose articles are chosen by sound, not spelling (0.72.0).** `_a()` carries two exception
  sets (`_CONSONANT_VOWEL_PREFIXES`, `_VOWEL_CONSONANT_PREFIXES`) because a bare vowel-letter
  test shipped "a hourglass build" and "an university lecture hall". Free-text `skin` / `eyes`
  / `scale_prose` overrides route through the same helper, so the fix is keyed on the leading
  word rather than on a list of known values. `ArticleTests` pins both classes.
- **`outfit_description` is voiced verbatim, so every source must supply its own article
  (0.72.0).** Cosplayer costumes (1107 of them) and archetype outfits (346 of 394) already
  did; the built-in `OUTFIT_DESCRIPTIONS` pool never had, so plain runs read "She wears cropped
  hoodie with…" while cosplay runs read "She wears a gothic black dress…". 171 values gained an
  article; the 9 with a mass/plural head (`denim overalls`, `yoga pants`, `high waisted
  trousers`, …) are correctly bare and are the documented exception. Pure data edit — no pool
  change, no RNG draw, no seed drift. `OutfitArticleTests` guards the convention.
- **Every field value has to complete the frame its prose slot puts it in (0.73.0).**
  `footwear` is voiced as `"in {value}"`, so `"barefoot"` — an adjective, not a noun phrase —
  rendered "in barefoot". Renamed to `"bare feet"` (the two `constraints.py` exclusion lists
  that name it moved in the same commit; `validate_data` would have caught a miss). This is the
  same class as the 0.66.0 `pose` participle rule and the `shot_type` camera-only doctrine:
  the slot's sentence frame is part of the field's contract, not just its wording.
  `FootwearPhrasingTests` pins it. Note the branch is nearly unreachable in practice —
  `_resolve_outfit_description` always fills `outfit_description`, so the separate
  footwear/colour/pattern clause only renders when no outfit resolves — but the value is
  lockable from the widget, which is enough to matter.
- **Singular worn items are articled in prose, plural ones are not (0.72.0).** The jewellery,
  bag and accessory pools mix both in one slot — "brooch", "thumb ring" and "canvas tote" sit
  beside "pearl studs", "layered gold chains" and "classic black sunglasses" — and `_format_prose`
  voices them in a single list. Only `watch_type` and `nails` were ever articled, so a run read
  "He has brooch, thumb ring, nose stud, **a** metal link watch". `_article_if_singular` articles
  just the singular heads. The head split (`_ITEM_TAIL_RE`) is the load-bearing part: a naive
  last-word test calls "reading glasses pushed up on **head**" singular and "belt cinching
  **waist**" plural, i.e. exactly backwards on both. Prose-only, zero RNG. Adding a value to any
  of those pools needs no bookkeeping — the head noun decides.
- **A Modifier must not prepend in front of an article (0.72.0).** `_apply_modifiers` used a
  blind f-string and produced "wears weathered a gothic black dress". It now routes through
  `_prepend_descriptor`, which **moved from the creature node into `nodes/identity_forge.py`**
  (the creature node imports it) — the palette-onto-integument case and the
  descriptor-onto-costume case are the same problem, so they share one implementation. Note it
  re-articles on the *descriptor* ("a gothic black dress" + "emerald" → "an emerald gothic
  black dress"), which is why `_a`'s exception sets matter here too.
- An outfit whose prose already includes headwear (hat/helmet/hood/crown…, `_HAT_RE`)
  suppresses a hat-valued random `accessories` draw so two hats never stack; non-hat
  accessories still show and an explicit lock wins. Keep `_HAT_ACCESSORY_VALUES` in sync
  with the hat entries of the `accessories` pool.
- Gloved/gauntleted costumes suppress randomized `nails`/`rings` in the engine (`_GLOVE_RE`);
  a **full hard shell** (robot/droid/powered-armour/full-plate/exoskeleton, detected by
  `_FULL_COVER_RE` or the cosplayer `covers_body` flag) drops the whole **Jewelry & Nails**
  group plus the `accessories`/`bag` fields (`_CONCEALED_BODY_FIELDS`, 0.51+) so an all-armour
  or full-suit cosplayer (RoboCop, Iron Man, Michelin Man) reports no stray necklace,
  sunglasses, or carried bag. Both respect explicit user locks. The shell rule also fires on full-plate **archetypes** (Human
  Knight, Holy Paladin).
- Adding options to a **flat** field shifts its distribution; prefer the density-gated
  `_EXTRA_ABSENCE` fields (variety changes, frequency doesn't). New feminine-coded values on a
  shared-pool field must also be added to `_MALE_EXCLUDED_VALUES` so a random Male skips them.
- **Masculine-default trims are wardrobe-gated for jewellery/nails *and makeup*.**
  `_MALE_EXCLUDED_VALUES` drives the "no chandeliers/pearls/polish on a random man" behaviour, but
  the jewellery/nails fields (`_PRESENTATION_GATED_FIELDS`) tag their rules
  `presentation_gated=True`. `_apply_constraints` skips those unless the man reads `"Masculine"`
  (i.e. `wardrobe == "Match gender"`), so a **Feminine/"Any" wardrobe leaves the full
  feminine-coded pool available** to a man for a femme look; the structural defaults (hair,
  brows, lips, eye_shape, bust) always apply. Presentation is `_presentation_mode(gender,
  wardrobe)`, shared with the outfit picker. Locked/archetype values bypass the trim entirely
  (constraint warns and keeps them).
  **0.72.0: the `gender=Male → makeup_style="no makeup"` requirement joined the gate.** It had
  been left ungated, so the presentation switch reached the jewellery and the wardrobe but not
  the face: a man with `wardrobe="Feminine"` drew chandelier earrings, almond nails and a mini
  skirt while staying bare-faced in **300 of 300 seeds** — the most visible half of the femme
  look was the one part it could not touch. Gated, `Match gender`/`Masculine` are byte-identical
  to before (verified over the full control matrix); only the explicit Feminine/"Any" wardrobes
  change. The result needs no extra tuning because `makeup_style`'s **male pool is already the
  cap** — `no makeup` plus the four natural styles — and its `male_weights` leans `no makeup`
  2×, so a femme male look lands ~1 in 3 bare-faced and never reaches glam by random draw. Bold
  glam still needs an explicit lock, which `_GENDER_FLEXIBLE_GROUPS` already honours.
  `PresentationGateTests` pins all three directions.
- **Wired `"None"` is an explicit omit and survives to the engine.** `IdentityForge.execute`
  builds `archetype_locked` from every wired value *except* `"Random"` — so a cosplayer/archetype
  field set to `"None"` (the builder's body-paint, bald, and free-text-eye suppressions) reaches
  the engine as an omit instead of being silently re-randomized by the default `"Random"` widget.
  A deliberate concrete widget choice still overrides it. (Pre-0.27.0 the `"None"` was dropped, so
  She-Hulk rendered a human skin tone under her green and bald characters grew hair — the
  documented suppressions only worked when calling `generate_character` directly, not through the
  node.) Tests that exercise suppression must route through `resolve_locked_fields`, not pass the
  flat preset dict straight in (see `SuppressionLockSurvivalTests`).
- **A node pack cannot render a brand-new dropdown value against a running ComfyUI (0.87.0).**
  The data layer is cached at startup, so `/prompt` validation rejects a name added since. There
  is exactly one no-restart path: resolve the prompt in-process from this repo and post a graph
  containing none of this pack's nodes. It also removes any need to install or sync the pack onto
  the target instance. See "The gallery render pipeline" above.
- **A committed workflow JSON's own `inputs` array is the authority on its widget order, not
  `define_schema()` (0.87.0).** All three `Krea2_IdentityForge_*Cycle.json` downloads predated the
  `composition` field, and each also carried ten stale trailing `widgets_values`. Aligning the
  value array against the *current* schema made `composition` appear to be present and correctly
  positioned in every one of them — it was not; the check that actually works is comparing the
  file's own `[i["name"] for i in node["inputs"] if "widget" in i]` against schema order. The
  frontend tolerates trailing extras silently, so nothing surfaces until someone reads the file.
- **`dump_frontend_fixtures.py --check` goes stale on a pure content addition (0.87.0).** The
  fixture embeds the Cosplayer/Creature/Archetype dropdown option lists, so adding entries changes
  it even when no schema changed. That is expected: regenerate and commit it, then read the diff —
  if the only change is names appended to `IdentityForgeCosplayer[0].options` and `random_scope` is
  untouched, no franchise crossed `_FRANCHISE_SCOPE_MINIMUM` and nothing breaking happened.
- **A sealed-headgear archetype must pin `makeup_style: "no makeup"` (0.87.0).** Hazmat Technician
  first rendered heavy glam, a cat eye and a fade *under a full-face respirator and a sealed hood*.
  The existing sealed archetypes never surfaced this only because they are `gender: "Male"`
  (Firefighter, Race Car Driver), where the global male rule already forces no makeup. Pin it
  explicitly on any `gender: "Any"` archetype whose head is enclosed, keep the hair plain, and
  follow the Beekeeper/Welder convention of offering one costume variant with the headgear pushed
  back so a face can read at all.
- **A creature's FACE has no colour anchor — measured and scoped down (0.88.0).** `palette` is
  prepended to `integument` only, never to `head`. This was logged at 0.87.0 as a systemic gap
  needing an engine-side restatement mirroring `_format_prose`. **It is not systemic, and the
  engine fix was rejected at 0.88.0 after measuring it.**

  The cosplayer green-body/pale-face bug happens because a *human face under paint* is a
  separable region with a strong default — ordinary human skin — to fall back on. That
  precondition only holds where the creature's head is human-shaped. **186 of 209 creature heads
  are anatomically fused animal heads** (muzzle, beak, mandibles, carapace, ruff, antennae): head
  and body are one continuous material, so the model carries the integument colour across
  unaided. That is why the roster renders correctly today.

  Of the 23 human-shaped heads: 5 already name a colour or material (`jiangshi`, `porcelain
  cyborg`, `tiger`, `red panda`, `bramble folk`); 6 name a non-skin material or have no face at
  all (`android`, `chrome-flesh cyborg`, `treant`, `mandrake`, `radial alien` — "no face and no
  front" — and `wraith` — "a hooded void"); and 3 *should* read as a human face (`centaur`,
  `satyr`, `sphinx`). The genuine risk set was six entries, closed as **data** at 0.88.0 by
  adding colour-free material words to `flesh golem`, `troll`, `manticore` and `yeti`.

  **The authoring rule this leaves behind:** a creature whose head is human-shaped must tie that
  head to the body's material with a **colour-free** word (`waxen`, `furred to the jaw`, `sheathed
  in the same warty hide`, `framed in the same shaggy fur`). Never name a colour in a slot — the
  slots are colour-free precisely so `palette` can recolour them. An engine-side restatement
  would also have silently invalidated ~189 published gallery images, because `entry_hash` hashes
  the entry dict and cannot see a prose-only change.

### Both contrapositive repairs must share one ban list (0.92.0)

The 0.82.0 note above ends on the right principle — *"the conflicting set is the union over
EVERY locked target, not just this rule's"* — and applies it one dimension short. Each branch
built its union over every locked *target* but only over its own rule **type**: the exclusion
branch collected `type == "exclusion"`, the requirement branch collected `type ==
"requirement"`. Neither could see the other's bans on the same trigger, so each repair handed
the other precisely the value it would reject on the next pass.

For a male character with a bold eyeliner locked, the two sets partition the entire five-value
`makeup_style` pool between them:

```
male pool            barely there / classic no-makeup / fresh-faced dewy /
                     soft natural / no makeup
exclusion branch     bans the four naturals   -> leaves only "no makeup"
requirement branch   bans "no makeup"         -> leaves only the four naturals
union of both bans   covers the whole pool
```

That is a closed cycle, not a near miss. The loop ran to `_MAX_CONSTRAINT_ITERATIONS` and
emitted whichever half of the cycle the 12th pass happened to hold, so a character came out
wearing `makeup_style: "no makeup"` beside nude lipstick, lash extensions, laminated brows and
dewy skin. Measured at **40 of 40 seeds** for each of 14 lock values (the bold `eye_makeup`,
`eyeliner` and `lashes` entries) under gender `Male` with wardrobe `Feminine` or `Any` — which
is exactly the deliberately-femme male look the wardrobe axis was built for (0.83.0). Under
`Match gender` the same lock produced the honest warn-and-keep, because `_requirement_pins`
blocked the repair there; the guard was doing its job, it just could not see this shape.

`_conflicting_trigger_values()` now builds the set once, over both rule types and every locked
target, and both branches call it. When every candidate is banned the pool comes back empty,
the repair is correctly abandoned, and control falls through to the existing `warn()` — the
lock wins, the trigger keeps a value coherent with everything else, and the user is told.

**Zero bias, zero drift on free runs.** The set is a strict superset of what each branch
computed before, and `_repick` consumes the same RNG regardless of pool contents, so no seed
moves except where the broader ban removes the candidate that was about to be wrongly chosen.
Pinned by `ConstraintRepairDeadlockTests`, whose `test_union_covers_the_whole_male_makeup_pool`
asserts the mechanism directly rather than the symptom.

### "Downstream wins" has to cover `_meta`, not just fields (0.92.0)

Every preset node's docstring promises the same contract — *"this node wins on overlap"* — and
`merge_preset_documents` honoured it key by key, which silently means *only for keys the
downstream node actually writes*. Two classes of reserved key escaped:

- **Costume state.** The Cosplayer node writes `covers_face` / `covers_body` / `covers_hair`
  unconditionally, including when false, precisely so a downstream node overrides an upstream
  one. `mask` and `size_scale` were only written when present, so they survived the merge.
  Chaining Cosplayer "Iron Man" → Cosplayer "Hermione Granger" correctly reset `covers_face`
  to false and still rendered *"She has a faceplate with narrow glowing eye slits"* over the
  Hogwarts uniform. Via Godzilla it also leaked `size_scale: giant` **and** the authored
  `scale_prose` sitting in `height`, so Hermione arrived "colossal and hundreds of feet tall"
  with the scene pools narrowed to suit a scale she did not have. The Archetype, Creature and
  Modifier nodes write *none* of the five, so Cosplayer → Archetype leaked all of them at once:
  a ballerina in a tutu with Iron Man's faceplate, no face, no hair and no jewellery.
- **`_meta.variants`.** A per-gender archetype ships its two looks there, and
  `generate_character` folds the matching block into `locked_clean` *after* the merged locks,
  so it beat everything downstream. Archetype "Battle Bard" → Cosplayer "Hermione Granger"
  merged the Hogwarts uniform correctly into `Clothing` and then rendered the Bard's velvet
  doublet, speakeasy, string lights and cheerful mood over it — still labelled "Cosplaying as
  Hermione Granger". **34 archetypes carry variants.**

Both are fixed in `merge_preset_documents`, because that is where the precedence contract
lives; fixing it there covers every node pairing at once, including hand-authored documents,
instead of patching each emitter. Two rules:

- A document supplying its own `outfit_description` replaces the *look*, so the upstream's
  `_COSTUME_META_KEYS` are stale and are dropped — along with the upstream `height` when
  `size_scale` goes, since the validator guarantees the two ship together.
- A variant look may only fill fields the downstream document leaves open. It still wins over
  its **own** archetype's base value, which is the point of the feature (`Regency Aristocrat`
  sets `bag` in both) — the oracle is the downstream document's fields, not the merged ones.

`_parse_archetype_json` additionally gates its `mask` read on `covers_face`: a mask describes a
head that is *hidden*, so voicing it on a face-visible character is never right. Belt and
braces for documents the merge never saw. `ChainedPresetPrecedenceTests` covers both rules and
the negative cases (a Modifier downstream must **not** invalidate anything; a solo document
must pass through untouched).

### `prompt_json` is what the vault stores, so it has to be self-describing (0.92.0)

Vault Save writes IdentityForge's `prompt_json` to disk and Vault Load feeds it straight back
into `archetype_json` — the node's stated promise being that *"a single saved document captures
the whole character regardless of how the graph was wired"*. It did not, for two reasons that
compounded:

- `_format_json` wrote only `gender`, `hair_color_scope`, `wardrobe` and `cosplay_of` into
  `_meta`. The concealment state lived on the *Cosplayer* document and never reached this one,
  so recall restored Iron Man's costume but not the reasons it hid anything: the faceplate
  sentence vanished and a full randomized face, hair and makeup were generated under the
  armour, with a stray ethnicity and skin tone on a fully-encased character.
- `group_fields` strips `"None"`, which is exactly the token the Cosplayer builder injects to
  suppress a field. She-Hulk's `ethnicity: "None"` did not survive, and a randomized ethnicity
  reappeared under the body paint — the failure 0.78.0 added that suppression to fix.

`_format_json` now records the five costume keys plus an `omitted` list of *explicitly* locked
absences. Recall needed no changes on the load side: `_parse_archetype_json` already read the
costume keys and now re-injects `omitted` as `"None"` locks. **All 1,827 cosplayers round-trip
byte-identically at a different recall seed**, which is the real assertion — if the document is
complete, the seed cannot matter, because everything meaningful is locked.

Only emitted when actually in play, so an ordinary character's `_meta` is unchanged
(`VaultRoundTripTests::test_a_plain_character_records_nothing_extra` pins the exact key list).
`omitted` deliberately excludes a field that merely randomized to nothing — that is not a
decision worth restoring.

### The pose gate could not see a generated outfit (0.92.0)

`_performable_poses` runs inside the randomize loop, where `pose` (field index 67) is drawn
long before a *generated* `outfit_description` exists — it is composed after the loop ends. So
its `_POCKETLESS_GARMENT_RE` and `_FULL_COVER_RE` tests read an empty string and the whole
`GARMENT_DEPENDENT_POSES` gate was inert for random outfits. The `_DEFERRED_FIELDS` docstring
has named this trap since 0.90.0 ("that is pre-existing and is left alone here, but it is the
same trap"); measurement made the case to close it: of 324 random outfits matching
`_POCKETLESS_GARMENT_RE` in 6,000 runs, **26 (8.0%)** drew a pockets/collar gesture — *"a
pastel off-shoulder mermaid gown with long satin gloves"* while *"posing with hands in
pockets"*. The hair half of the same function was always correct, because `hair_length` (index
24) settles first: bald characters drew a hair-touching pose 0 times in 6,000 runs.

**Deferral is the obvious fix and the wrong one.** Moving `pose` into `_DEFERRED_FIELDS`
relocates a draw from the middle of the stream, so every existing seed would resolve to a
different pose *and* different tattoos/legwear — silently invalidating every published gallery
image exactly as the 0.90.0 prose change did, with `entry_hash` unable to flag it. That is the
same append-only reasoning `_DEFERRED_FIELDS` itself documents, applied to its own remedy.

`_repair_pose` instead runs at the very end of the draw order, after
`_resolve_deferred_fields`, and **consumes no RNG unless the pose is genuinely unperformable** —
the pool-membership test is free. A seed only changes when its pose was already wrong, and even
then nothing downstream shifts, because nothing downstream draws. A preset costume was already
in `resolved` during the loop, so this is a verified no-op across the whole cosplayer and
archetype roster.

### Ink needs skin: the shell tattoo gap (0.95.0)

`_CONCEALED_BODY_FIELDS` — the fields a `covers_body` shell drops on top of the whole
`Jewelry & Nails` group — was written for `accessories` and `bag`. The **`tattoos`
cascade shipped afterwards, at 0.90.0**, and its own rule pointed the other way: ink
sits on the body *under* the costume, which is exactly why `tattoos` is deliberately
absent from `_COSTUME_SUPPRESSED_EXTRAS`. That rule silently assumes there is skin
under the costume. Under a mascot suit, plate armour or a droid chassis there is none.

Measured before the fix: **38 of 480 renders (7.9%)** across 60 `covers_body` +
`covers_face` entries × 8 seeds described a tattoo on a surface that does not exist —
*Iron Man* with "a soft watercolor tattoo across the back of one hand", *RoboCop* with
one on the neck, a *Cylon Centurion* with "a dense blackwork tattoo across the
collarbone". Both fields now join the set, so the auto-detected `_FULL_COVER_RE` shells
(Sabine Wren's beskar, Honey Lemon's armoured bodysuit) are covered too.

This is the same shape as the 0.92.0 pose finding directly above: **a gate that
predates the axis it needed to cover.** When a new randomizable axis is added, walk the
existing suppression sets and ask which of them the new field should have joined.
Drift from the change is 72 of 730 sampled renders, every one a shell, every one a
removed tattoo; a character in ordinary clothes still gets ink.

### A feral subject has no arms to cross (0.95.0)

Every `pose` value is written as a gesture a *person* performs. `_performable_poses`
already dropped the ones needing hair, a garment or free hands; nothing knew about a
subject with no upright two-armed body at all. Measured: **80 of 300 feral renders
(26.7%)** reached for something the subject does not have — "standing with arms
crossed" on a six-legged sky bison.

`QUADRUPED_UNPERFORMABLE_POSES` (in `data/fields.py`) drops six gesture families plus
`seated_perch`, **whole families only**, so the survivors keep their proportional
shares. It overlaps the `covers_*` rules on purpose: the Creature node's Feral form
sets none of those flags (it suppresses by group), so without this its beasts kept
crossing arms. It is derived from the species payload in `generate_character`, so one
rule covers both producers, and it is **off for Anthropomorphic and Subtle** — which is
why the 249-entry creature gallery, rendered Anthropomorphic, cannot drift.

The surviving pool still holds human *stances* ("in a relaxed contrapposto stance",
"sitting cross-legged"). Culling those would mean splitting and repricing the two
largest pose families — the expensive kind of change the backlog warns about — so a
feral cosplay entry instead **locks an authored pose** from `_FERAL_POSES`, the same
replace-the-field pattern `scale_prose` uses for `height`. Nothing is drawn from the
global pool for those entries, so no family weight moves.

### The vault round-trip was only half-closed (0.95.0)

0.92.0 made `prompt_json` self-describing for the Cosplayer node's five concealment
keys. The **species path was left short**: `_format_json` recorded `form`,
`creature_of` and `creature_class` but not `suppress_groups` / `suppress_fields`, so a
saved creature recalled with nothing suppressed:

```
saved:   A lion with a plump build and petite. He has a broad leonine head ...
recall:  A 45-year-old Kenyan lion with a plump build, petite, and brown skin.
         He has a very fit physique with sloped shoulders, a slightly defined
         chest, a narrow waist ...
```

`omitted` could not stand in for them — it records *explicitly locked* absences, and a
suppressed field is dropped outright, so it never appears there. Both lists are now
emitted whenever the document carries anatomy slots; `_parse_archetype_json` already
read them, so recall needed no change. This fixes the **Creature node's** own vault
round-trip as much as the feral cosplay path that would otherwise have inherited it.

### `anatomy_note`: the early sentence a maskless entry never had (0.97.0)

The 0.96.0 limb-count fix works by moving a count into a sentence that renders **before** the
`He wears …` garment list. The only such sentence a non-feral entry had was `mask`, so the fix
could not reach the four multi-armed entries that have no mask — `Shiva (Record of Ragnarok)`,
`Salaak`, `Spiral`, `Greez Dritus`. That gap was written up at 0.96.0 as needing "an optional
anatomy sentence for non-feral entries, mirroring `_MASK_KEY`". This is it.

`anatomy_note` is an optional string on a cosplayer entry. It travels as `_ANATOMY_NOTE_KEY`
exactly as the mask travels as `_MASK_KEY`, and `_format_prose` voices it as its own
`He has …` sentence immediately **before** the mask sentence — body first, then head, which is
how the two read together on an entry carrying both.

Five rules, each with a reason:

* **It describes the BODY, never the clothes.** A garment here would survive into a render a
  downstream node has re-costumed, and would then compete with the real clothing sentence.
  `validate_data.py` rejects a garment noun in the field.
* **It is voiced with `has`, not `wears`** — for the same reason `mask` is: this is what the
  body *is*, not something on it.
* **State the count as a word, early.** "four arms in total" carries the render; "a second pair
  below the first" makes the model do arithmetic and it does not. See "Limb and part counts"
  above.
* **It is in `_COSTUME_META_KEYS`**, so a downstream document that supplies its own
  `outfit_description` drops it. That is the 0.92.0 "downstream wins" contract, and skipping it
  would reintroduce the leak class that put Iron Man's faceplate on a Hogwarts uniform —
  chaining Cosplayer `Spiral` → Cosplayer `Hermione Granger` would otherwise leave six arms on
  the new look.
* **It is rejected on a feral entry.** A beast already has a per-slot `anatomy` dict routed into
  the species payload; carrying both would describe the same body twice. Note the two keys are
  different things: `anatomy` (feral, a `{slot: text}` dict) and `anatomy_note` (non-feral, a
  plain string).

Unmasking does **not** clear it — it is not part of the head. `AnatomyNoteTests` pins all of
the above, including the body-before-head ordering, which no shipped entry exercises yet but
which the first entry carrying both will inherit.

`Mizora` (0.97.0) is the first non-arm use: four horns and a pair of wings are a count and an
unusual body plan, and both were buried in her costume sentence before this existed.

### `composition` joins the giant/tiny scale gate (0.97.0, measured)

`_scale_coherent_pool` narrowed `location`, `shot_type`, `body_type` and `pose` for an extreme
scale, but not `composition` — so a forty-foot subject could still draw
*"composed with the subject filling most of the frame"*, which throws away the very surroundings
the other three rules work to keep in shot. Observed on `Falkor`.

The two ends fail for opposite reasons and get their own sets. **Giant** drops the two framings
that crop the world away (`the subject filling most of the frame`, `a tight crop and little
headroom`), because "colossal and fifty feet tall" is a claim about a *relationship* and a frame
containing only the subject has nothing to measure it against. **Tiny** drops the one framing
that makes a doll-sized subject resolve to nothing (`the subject small against open negative
space`) — the mirror of `_SHOTS_TOO_WIDE_FOR_TINY`, and the same single-value light touch the
tiny tiers get everywhere else.

**BIAS.** `composition` is flat — no `FIELD_FAMILIES` entry, no `weights` map — so the survivors
stay uniform over each other. This is the partial cull "A flat field is where a partial cull is
FINE (0.82.0)" sanctions, and the same property that clears `shot_type` and `body_type`.
Four of the eight values are *also* in `_ENVIRONMENT_DEPENDENT_COMPOSITIONS`, which culls them in
a studio; the two rules compose, and worst case a giant in a studio narrows to two with the
`or pool` fallback behind it.

Measured after the change: 0/300 bad draws at each tier, and the full pool still reachable with
no scale in play.

### A species `hands` slot suppresses the human `nails` field (0.97.0, measured)

All **249** creatures fill the `hands` slot — "small black-clawed hands", "broad hoof-tipped
forelimbs", "sucker-lined tentacles" — and the human `nails` field could still draw
"He has square nails" over the claws. `hands_covered` (the glove/full-shell rule) never saw it,
because a species slot is not a glove.

The fix sits beside the glove rule and drops `nails` when `species["slots"]["hands"]` is filled.
The same slot reaches a Cosplayer entry carrying `body_plan: "feral"`, so a named beast is
covered too.

**`nails` only — not `rings`.** A ring is a *worn* item and a clawed or taloned hand can wear
one; a fingernail is a claim about the hand itself, which is exactly what the slot has just
overwritten. Two entries name human-like hands (`raccoon`, `android`) and neither wants a
manicure either.

No RNG moves — the field is drawn and then dropped, the same shape as the glove rule — so
nothing biases, and an explicit lock still wins. Measured after the change: 0/600 creature JSONs
carry a `nails` key, while a plain human still gets one.

### `bag` was the last feminine-coded field with no masculine trim (0.97.0, measured)

Same class of miss as the 0.83.0 `footwear` trim, and found the same way. `bag` shares one
option pool across genders and had **no entry in `_MALE_EXCLUDED_VALUES` at all**, while every
other feminine-coded field — nails, earrings, necklace, rings, bracelet, footwear, hair_style —
had one.

**Measured before the fix, over 1000 male renders at the default `wardrobe="Match gender"`:
137 (13.7%)** carried a strictly feminine handbag.

> *"…a fine-knit poplin shirt and a silk tie in a floral print, in loafers, carrying **an
> envelope clutch in gold**."*

Twelve values are trimmed, and the trim is **presentation-gated** like the other wardrobe trims,
so a Feminine/"Any" wardrobe on a man keeps the whole pool — that mechanism is the entire point.
Deliberately *not* trimmed: the totes, crossbodies, saddlebags, belt bags and mini backpacks,
which are unisex carriers.

**Three men's bags ship in the same revision** (`leather briefcase in black`,
`canvas messenger bag`, `canvas duffel bag`). That is not a coincidental content addition — cull
twelve of twenty-six and the masculine pool is nearly empty, so the trim and the additions are
one change. `bag` is flat, so both halves are bias-free.

Measured after: 0/1000, with the men's bags reachable and a Feminine wardrobe still opening the
full pool.

### Release stamps, and the gallery's "Newest first" (0.97.0)

`data/versions.py` records the release each roster entry first shipped in, written by
`scripts/stamp_versions.py` and checked in CI. It exists so the three sample galleries can offer
a **Newest first** sort and a **New in `<version>`** filter without a human keeping a changelog
of thousands of tiles in their head.

**It is presentation data only.** Nothing in it reaches a prompt, and no seed, saved workflow,
dropdown order or gallery image depends on it — which is why adding a stamp can never change
what the node generates.

Three things about it are load-bearing:

* **A generated file must never be able to see the maintainer's own data — and `ast` is
  not the only route in.** `scripts/dump_frontend_fixtures.py` imports nothing from the data
  layer, so the `ast` rule below did not apply to it, and it leaked anyway by a second route:
  `IdentityForgeVaultLoad.define_schema()` lists the characters actually saved under ComfyUI's
  user directory, so regenerating the fixture on a box with a real ComfyUI on `sys.path` wrote
  three private vault entries into a committed, published file (found at 0.99.0, by running the
  suite against the real `comfy_api` instead of the stub). CI cannot catch it — dependency-free,
  so the stub's `folder_paths` finds no vault and the sentinel is all it ever sees. The script
  now **refuses to write or `--check`** when the vault is non-empty, and
  `test_fixture_matches_live_schema` **skips** rather than failing, because its old advice
  ("regenerate") was precisely the action that committed the data.
* **The reader uses `ast`, never an import.** Importing `data/cosplayers.py` runs
  `apply_user_cosplayers` at the bottom of it, which merges the maintainer's local
  `user_options.json` — so an import-based stamper would bake private entries into a committed,
  published file. `scripts/generate_js_data.py` documents this trap at length and this follows
  it. A user-added entry therefore never gets a stamp, and the gallery treats an unstamped entry
  as oldest, which is the right failure mode: it has no image on `gh-pages` either.
* **`RELEASES` is an ordered tuple and the page ranks by POSITION in it**, never by parsing the
  version strings — `"0.10.0"` sorts before `"0.9.0"` as text.
* **`--stamp` never rewrites an existing stamp.** A release date is a fact about the past;
  rewriting one silently reorders the gallery.
* **`RELEASES` holds only releases that shipped ROSTER CONTENT, so it is not the release
  history.** An engine-only release is legitimately absent from it. That distinction cost a red
  suite at 0.99.0 — the Turnaround rewrite was the first release since stamping shipped that
  added no characters, and `test_the_current_version_is_the_last_release` asserted the pyproject
  version *equals* `RELEASES[-1]`, an invariant that had held only by accident. The test now
  asserts the version is never *behind* the newest stamp (unstamped entries are `--check`'s job,
  not its). Nothing on the page needed changing: the "New in `<version>`" button already hides
  itself when no entry matches, which is exactly the right behaviour for such a release.

`--check` is the CI gate. It fails when a shipped entry has no stamp *and* when the map still
names something the pack no longer ships — the half a convention alone cannot enforce, since an
unstamped entry would simply sort as though it had always been there.

The manifest carries this to the page: `schema_version` 2 adds `added` per entry plus `version`
and `releases` at the top level. A page served an older manifest sees every entry as unstamped,
hides both controls and behaves exactly as before, so the two sides can be published
independently.

**Two pre-existing page bugs were fixed in the same pass**, both found by driving the page in a
browser rather than by reading it: `showMissing()` planted the literal text `missing entries` in
the search box (it looked like a query the viewer had typed and could not be un-typed without
clearing a real search), and the **"Clear search" button in the markup was never wired to
anything** — a dead control, shipped for releases. Search and the two toggles now funnel through
one `applyView()` so they compose instead of overwriting each other, and the empty-state panel
fires for any narrowing rather than only for a search.

### Neon signage: a fixture split instead of a reprice (1.1.0)

`neon_venue` (weight 297 of 2508, 6 variants) was legal at every location except the four void
studio backdrops. Because `_pick_family_weighted` keeps a family's full frozen weight when it
retains even one surviving variant, excluding `daylight` (36.8% of the field, indoors-only)
inflated `neon_venue` to **22.76% of indoor draws**; outdoors, `neon_venue` + `neon_street`
reached **19.6%**. Roughly one render in four carried a neon or signage cue — measured, not
estimated, before any fix landed.

**Why a reprice was the wrong tool.** Halving `neon_venue`'s weight would only lower its
*frequency*; it does nothing about *where* it lands — a neon sign in a cathedral is wrong
regardless of how rarely it's drawn. The actual bug is location-coherence, the same class this
file has closed twice before (0.82.0's hearth/TV/stained-glass split, 0.83.0's `studio_stage`
split): fixture values need a location allowlist, and a per-location rule may only remove a
**whole** family, or the excluded family's frozen weight dumps onto whatever survives inside it
(see "Fixture lighting: indoors is necessary, not sufficient" above). `neon_venue` mixed three
different fixture claims in one six-variant family, so it could not be gated as a unit without
also gating its two unrelated members — the fix had to split the family along the fixture seam
first, then gate the pieces.

**The split.** Every `LIGHTING_FAMILIES` weight was rescaled ×2 first (2508 → 5016), which keeps
every sub-weight integral and reproduces the pre-gate distribution **exactly** — no taste-based
reweighting anywhere in this change. `neon_venue`'s 297 was then split three ways, proportional
to each half's variant count (3:2:1):

| new family | weight | variants |
|---|---|---|
| `neon_signage` | 297 | `neon sign glow in multiple colors`, `single neon light from one side`, `purple and teal neon wash` |
| `venue_rig` | 198 | `club strobe lighting`, `colored gel lighting` |
| `bokeh` | 99 | `golden bokeh lights in background` |

`neon_street`'s weight was also doubled (99 → 198) by the same ×2 rescale, unsplit — it was
already its own two-value family. Total weight is 5016 across **13 families, not 11** (seeds
drift for `lighting`, the same accepted precedent as 0.64.0 / 0.66.0 / 0.78.0 / 0.81.0 / 0.82.0 /
0.83.0). No variant string was renamed, added, or removed — all six original `neon_venue`
strings reappear byte-identical, now split across three families.

**The allowlists.** `NEON_SIGNAGE_VENUE_LOCATIONS` (24 locations) gates `neon_signage` and
`venue_rig` to nightlife/entertainment/urban-strip locations: 5 `food_drink` bar/club members
(`crowded bar and grill`, `wood-paneled pub`, `dimly lit cocktail lounge`, `neon-lit nightclub`,
`speakeasy-style basement bar`), 10 `leisure_fitness`
arcade/karaoke/casino/bowling/skating/cinema and music/performance venues, 5 `urban_outdoor`
night-street members, 3 signage-dense `urban_landmark` members (`Times Square`, `Shibuya
Crossing`, `the Bund waterfront in Shanghai`), and one `retail_services` addition (`tattoo
parlor`, added because the shipped `Tattoo Artist` archetype locks it and the pairing is as
iconic as a nightclub). `NEON_STREET_LOCATIONS` gates `neon_street` to `urban_outdoor` ∪ any
outdoor `transit_travel` member — **computed, not hand-listed** (currently just `urban_outdoor`,
32 locations, since no `transit_travel` member ships outdoors today), so a new outdoor transit
location is picked up automatically. `bokeh` deliberately never appears in `FIXTURE_LIGHTING` —
it is a light quality with no fixture claim, so it stays broadly legal. `data/constraints.py`
needed no changes: its existing generic loop over `FIXTURE_LIGHTING` already turns any new entry
into a per-location exclusion rule.

**The mandatory pre-flight audit.** Every archetype's location×lighting combination was
enumerated exhaustively (not sampled) against the real `data/templates.py` and checked against
the new gate. A handful of allowlist additions beyond the brief's literal category list were
justified by a shipped archetype actually needing them (`recording studio`, `cobblestone
old-town street`, `tattoo parlor`, …); seven pairs were deliberately left as declared,
individually-tested exceptions rather than widening the allowlist to cover them, because
widening for one archetype's sake would have reopened the exact frequency problem this task
closes for every *non*-archetype character — including one, `Grim Reaper` / `misty moor`, that
is the identical bug class this task's own motivating example describes (a streetlamp on a
Yosemite meadow), left as a flagged pre-existing authoring miss rather than a reason to widen
`NEON_STREET_LOCATIONS` to `nature_outdoor`. `NeonSignageGateTests` and
`ArchetypeNeonLocationTests` pin the weight/family-count invariant, per-location reachability,
and the exception set itself (so it cannot silently go stale).

### `random_pool` composes with `random_scope` instead of a seventh scope (1.1.0)

`random_pool` is a third `io.Combo.Input` on `IdentityForgeCosplayer`, appended at the end of
`define_schema()` (after `upstream`, per the widget-append convention — see "Adding a field
without breaking saved workflows"), offering three values: `All characters`, `People only — no
mascot suits or beasts`, `Mascot suits and beasts only`.

**Why a filter, not a scope value.** `random_scope`'s existing values already partition the
roster by franchise/category — the nine broad `_FRANCHISE_CATEGORY` buckets plus per-franchise
`Franchise: …` scopes once a franchise crosses `_FRANCHISE_SCOPE_MINIMUM`. Person-vs-mascot is an
orthogonal axis: multiplying every existing scope value by a mascot/people toggle would double
the widget's option list and mint mostly-dead combinations (a franchise with zero mascot entries
would grow a `Franchise: X — mascot only` option with nothing behind it). Composing two
independent filters instead keeps both option lists exactly the size they already are, and every
combination that has *any* matching entry stays reachable — the filters intersect inside
`_resolve_character`'s `in_scope()` closure rather than being enumerated as a cross-product.

**Composition and fallback order.** The pool filter (`_pool_is_people` / `_pool_is_mascot_or_beast`,
built on the existing `_scope_is_mascot` / `_scope_is_feral` predicates — no new detection logic)
applies inside `in_scope()` after the `random_scope` predicate, so both constrain the same
candidate list together. The pre-existing fallback order is preserved exactly: a gender mismatch
relaxes first (so scope/pool is never silently dropped just because a scope had no entries of the
rolled gender), and the loud full-roster fallback fires only if the pool is still empty after
that relaxation. This means `random_pool` **stacks** with `random_scope` — "Franchise: Pokemon" +
"Mascot suits and beasts only" is a real, correctly-intersected query, not two competing filters
that only one of which can win.

**`fingerprint_inputs` needed no change.** This node's `fingerprint_inputs` already ignores every
kwarg and unconditionally returns `float("nan")` — a pre-existing workaround for
ComfyUI#11905 that forces a re-roll on every queue regardless of any single field's value. Since
caching is already bypassed for every input, there is nothing to add for `random_pool`
specifically; the code documents this in a comment rather than a no-op kwargs read that would
otherwise look like an oversight to a future reader.

`_announce_scope` folds `pool` into its cache key and message text, but the default pool
(`All characters`) omits the note entirely, so a pre-1.1.0 announcement string is unchanged
byte-for-byte — the new widget is additive to the message surface, never a rewording of it.

### The roster picker: text-first cards, sprite atlases rejected (1.1.0)

The picker (`js/identity_forge_picker.js` / `.css`) is a searchable modal over the whole roster —
cosplayers, archetypes, creatures — attached to the `character` / `archetype` / `creature` combo
on their respective preset nodes via a trigger button. It is a **pure DOM overlay appended to
`document.body`, never a member of `node.widgets`** (not `addDOMWidget`): even a `serialize:
false` widget still counts toward `node.widgets.length`, which the pre-existing legacy
`widgets_values` padding logic (`WIDGETS_ADDED_BY_RELEASE`) depends on matching exactly, so a DOM
overlay outside that array is the only option that adds zero risk to backward-compatible
workflow loading.

**The search index.** `scripts/generate_js_data.py` emits `js/identity_forge_roster.json`, a flat
JSON array tagging every entry with a `kind` discriminator (`cosplayer` / `archetype` /
`creature`) and a precomputed, lowercased `haystack` string (name + franchise/category + costume
prose + derived trait words such as `masked`, `mascot`, `feral`, `giant`, `tiny`) for
substring/keyword search. Search is case-insensitive substring matching with multi-word tokens
AND'd (order-independent), **filtered within the active tab** — the "All" tab is what searches
every kind at once, and the trait facet composes on top of both. This replaced the original
"a query spans every tab, tabs only apply to an empty box" rule, which meant a user who had
narrowed to one category lost that scope the instant they typed, with no way to search inside a
single kind at all. Because a tab-scoped search can hide matches the user would have wanted to
see, two things carry the cross-kind discoverability the old rule provided for free: while a
query or a non-default facet is active, **each tab renders its own match count** (`Creatures (7)`
is readable from the Cosplayers tab, and a zero-count tab renders dimmed via
`.if-picker-tab.empty`), and an active tab with no matches shows how many matches exist elsewhere
plus a one-click **"Search all categories"** button rather than a bare dead end. Kind badges on
the cards now appear only on the "All" tab, since every other tab is single-kind by construction.
The generator reads the data modules with `ast.parse` only, never
by importing them, for the same reason `stamp_versions.py` does: importing runs
`apply_user_*` and would bake a maintainer's private `user_options.json` entries into a committed,
published file. The file sits under a **~1.5 MB budget** (`tests/test_js_sync.py`), and ships as
`.json`, never `.js` — a startup-tax rule that applies to any future generated frontend data file
(see the memory note of the same name): `.js` is parsed and executed by every ComfyUI page load
regardless of whether the picker ever opens, while `.json` is only fetched, and only lazily, the
first time a user actually opens the dialog.

**Why sprite atlases were rejected — the Registry-zip-size argument.** An atlas image (or a
per-entry thumbnail set) bundled into the pack would ship inside every Registry download and
every git clone, growing the distributed package for a feature most sessions never open. The
existing sample-render images already solve this correctly for the *public galleries*:
`gallery/.gitignore` keeps them off `main` entirely, living only on `gh-pages`. The picker follows
that same boundary instead of re-litigating it — cards are **text-first by default** (name,
franchise/category, kind badge, trait chips), carrying zero image payload, so the picker itself
adds nothing to package size.

**The opt-in thumbnail layer.** "Show preview images" is an unchecked checkbox by default; its
state persists to `localStorage` (`identity_forge.picker.show_previews`, wrapped in try/catch so
a blocked storage API degrades to text-only rather than throwing). Only once enabled does the
picker fetch `.../gallery/<folder>/manifest.json` from the public `gh-pages` site over a plain,
absolute `fetch` — never ComfyUI's own `api.fetchApi` — where `<folder>` is the gallery's own
directory name (`cosplay`, not the roster's `cosplayer` kind string; a real naming mismatch caught
and handled explicitly). A failed or offline fetch resolves to an empty `Map` silently, with no
error dialog, and the fetch promise is only cached **while in flight** (cleared via `.finally()`
the instant it settles) so a later call issues a fresh `fetch()` that the browser's own HTTP cache
serves from the manifest's real `Cache-Control: max-age=600` + `ETag` contract — not an indefinite
JS-level cache that would otherwise show a stale roster for an entire long-lived tab, a real bug
caught and fixed during this task's review rounds. `<img>` tags lazy-load via
`IntersectionObserver` once a kind's manifest resolves, mirroring the public gallery page's own
lazy-load pattern, so opening the dialog with previews on does not eagerly fetch hundreds of
images at once.

**Two Critical bugs surfaced only by live testing**, not by the automated jsdom suite (documented
at length in the task's own reports; named here because they shaped what shipped): the trigger
button was fully clickable while its node was still an unplaced LiteGraph "ghost" (Escape then
appeared to delete the *dialog's node* — actually a pre-existing, unrelated LiteGraph platform
shortcut for cancelling ghost placement, reproduced identically on a stock core `Note` node with
no Identity Forge code involved), and `random_pool` was silently stripped from every saved
workflow on reload by a real bug in ComfyUI's own shipped `migrateWidgetsValues()` — a coincidence
where this node's total widget count exactly matched that function's schema-derived migration
mask length. Neither bug lived in this pack's business logic; both were closed by working around
platform behaviour (gating the trigger on `node.flags.ghost`, and padding one inert trailing
`widgets_values` element to dodge the length collision) rather than by touching the platform
itself.
