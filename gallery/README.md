# Sample galleries

Three sibling galleries, one per preset node:

| Folder | Entries from | Live page |
| --- | --- | --- |
| [`cosplay/`](cosplay/) | `data/cosplayers.py` | [cosplay gallery](https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/) |
| [`archetypes/`](archetypes/) | `data/templates.py` (`ARCHETYPES`) | [archetype gallery](https://enragedantelope.github.io/comfyui-identity-forge/gallery/archetypes/) |
| [`creatures/`](creatures/) | `data/creatures.py` (`CREATURES`) | [creature gallery](https://enragedantelope.github.io/comfyui-identity-forge/gallery/creatures/) |

**Images live only on the `gh-pages` branch.** `gallery/.gitignore` blocks `images/`
on `main`, so cloning or pulling the repo never drags down hundreds of megabytes of
samples. The pages, scripts and manifests live on `main`; publishing copies them across.

---

## Publishing

Double-click `update_gallery.bat` in the gallery you want, or drag a folder of images
onto it. It asks for a source folder and a mode, then optimizes, commits and pushes in
one pass. Everything it does is also available directly:

```bash
python gallery/cosplay/publish.py --source <folder>              # add missing only
python gallery/cosplay/publish.py --source <folder> --overwrite  # also replace existing
python gallery/cosplay/publish.py --source <folder> --dry-run    # report, change nothing
```

Name each source file after the entry it depicts — `Batman.jpeg`, `Elven Ranger.png`,
`wolf.jpeg`. Matching ignores case-insensitive whitespace differences and a trailing
period (Windows strips it, so the entry `C.C.` is stored as `C.C.jpeg`). A file that
matches no entry is **reported and skipped**, never published under a name no dropdown
can reach — that catches typos before they reach the site.

`.jpeg`, `.jpg`, `.png` and `.webp` sources are all accepted; everything is re-encoded
to JPEG at 600px wide, quality 80.

---

## Release stamps and the "Newest first" sort

Each page offers **A–Z** or **Newest first**, plus a **New in `<version>`** filter, because
every roster entry carries the release it first shipped in. That lives in `data/versions.py`,
written by `scripts/stamp_versions.py` and gated in CI:

```bash
python scripts/stamp_versions.py --stamp   # after adding entries; commit data/versions.py
python scripts/stamp_versions.py --check   # what CI runs
```

`build_manifest.py` copies the stamps into `manifest.json` as `added`, alongside a top-level
`version` and `releases` list. The page **ranks by position in `releases`**, never by parsing
the version strings — `"0.10.0"` sorts before `"0.9.0"` as text.

Both controls hide themselves when the manifest does not carry the fields, so a page served an
older (`schema_version: 1`) manifest silently falls back to plain A–Z rather than showing a
control that cannot do anything. That means the pages and the manifests can be published
independently, in either order.

A **user-added** entry has no stamp. It sorts as oldest and never appears under "New in", which
is the right failure mode — it has no image on `gh-pages` either.

---

## Editing the page files

`gallery.js` and `style.css` are copies too, exactly like the four `.py` scripts. `style.css` is
byte-identical across all three and `gallery.js` differs **only** in its header banner;
`PageAssetsStayInSyncTests` in `tests/test_gallery.py` fails until a change has landed in all
three. It also checks that every `$('#id')` the script reaches for exists in that gallery's
`index.html` — a lookup returning `null` is how the "Clear search" button sat dead for several
releases without anyone noticing.

---

## The safety model

This is the part worth reading before changing anything.

- **`gh-pages` is the source of truth for what is published.** The manifest is rebuilt
  from the files actually on the branch *after* staging — never from your source folder.
- **Your source folder only ever adds or overwrites.** An entry you did not supply an
  image for is not touched, not re-encoded, and not deleted. If a Batman image is
  already live and there is no Batman file in your source folder, nothing happens to it.
- **Nothing is deleted unless you ask.** `--prune-orphans` is off by default, is not
  wired into the `.bat`, and even then removes only images whose filename matches *no
  roster entry at all* — a character that was renamed or deleted in the data. Never one
  that is merely absent from this run.
- **Your working tree is never touched.** Publishing checks `gh-pages` out into a
  temporary `git worktree` and removes it afterwards. It does not stash, and it does not
  switch the branch you are sitting on.

> The predecessor (`deploy.py`, removed at 0.80.0) built the manifest from the *source
> folder*. Pointing it at a folder of five new images marked every other entry
> image-less, and its prune step would then have deleted them all from the branch. That
> is the failure this design exists to make impossible.

Check coverage any time without changing anything:

```bash
python gallery/cosplay/cross_reference.py     # what still needs an image, what is orphaned
```

---

## Three copies, deliberately

Each gallery owns its scripts rather than importing a shared package. The four Python
files are **byte-identical outside their docstring and their `GALLERY CONFIG` block** —
that block is where the data module, the roster accessor and the page file list live.

**If you fix a bug or make an improvement in one, port it to the other two.**
`tests/test_gallery.py::CopiesStayInSyncTests` enforces this: it strips the docstring
and config block, neutralises the gallery name, and fails if the remaining code differs.
You cannot land a one-gallery fix by accident.

`tests/test_gallery.py::BatchLauncherTests` guards the `.bat` files against the failure
modes that broke a shipped installer once already — every exit path pauses, no
parenthesised `if` blocks, ASCII only, and CRLF enforced by `.gitattributes`.

---

## Adding a fourth gallery

1. Copy a gallery folder wholesale.
2. Edit only the `GALLERY CONFIG` block in each of the four `.py` files: `GALLERY_KIND`,
   the data import, `entry_names()`, `entry_meta()`, and `PAGE_FILES`.
3. Update the title, subtitle and search placeholder in `index.html`.
4. Add the new kind to `KINDS` in `tests/test_gallery.py`.
5. Run `python gallery/<kind>/cross_reference.py` — it should list every entry as
   missing. That is the empty gallery, ready for its first publish.
