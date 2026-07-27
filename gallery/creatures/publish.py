"""Publish the CREATURE gallery: optimize, stage and push, in one pass.

    python gallery/creatures/publish.py --source <dir>              # add missing only
    python gallery/creatures/publish.py --source <dir> --overwrite  # also replace existing
    python gallery/creatures/publish.py --source <dir> --dry-run    # report, change nothing

=============================================================================
 THIS FILE IS ONE OF THREE NEAR-IDENTICAL COPIES
 gallery/creatures/publish.py - gallery/archetypes/publish.py -
 gallery/creatures/publish.py
 They differ ONLY in the GALLERY CONFIG block below. Fix a bug here and apply
 it to the other two (see gallery/README.md).
=============================================================================

THE SAFETY MODEL, which is the whole point of this script:

  * ``gh-pages`` is the source of truth for what is published. The manifest is
    rebuilt from the files that are actually on the branch AFTER staging, never
    from the source folder.
  * The source folder only ever ADDS or OVERWRITES. An entry you did not supply
    an image for is not touched, not re-encoded, and above all not deleted.
  * Nothing is removed unless you pass ``--prune-orphans``, and even then only
    images whose filename matches no roster entry at all - i.e. a creature that
    was renamed or deleted in the data, never one that is merely absent from
    this run's source folder.

The predecessor (``deploy.py``, removed at 0.80.0) got this wrong in a way that
could have destroyed the gallery: it built the manifest from the source folder,
so pointing it at a folder of five new images marked every other entry as
image-less, and its prune step would then have deleted them all from the branch.

It also switched branches in place with ``git stash``/``git checkout``, which
runs over whatever is in your working tree. This uses ``git worktree`` instead,
which touches the current checkout not at all.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# === GALLERY CONFIG — the only part that differs between the three copies ====
GALLERY_KIND = "creatures"
GALLERY_TITLE = "creature form"
PAGE_FILES = ["index.html", "style.css", "gallery.js"]
# ============================================================================

from build_manifest import entry_names, generate_manifest, normalize_name  # noqa: E402
from build_gallery_images import optimize_image  # noqa: E402

GALLERY_SRC_DIR = Path(__file__).resolve().parent
BRANCH = "gh-pages"
REL_DIR = f"gallery/{GALLERY_KIND}"


def run(*cmd: str, cwd: Path | None = None) -> str:
    """Run a git command from argv words.

    Never ``shell=True``: the commit message is user-supplied, and interpolating
    it into a shell string means a quote breaks the command and a semicolon runs
    as shell syntax.
    """
    result = subprocess.run(cmd, capture_output=True, text=True,
                            cwd=str(cwd or REPO_ROOT))
    out = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        print(f"  COMMAND FAILED: {' '.join(cmd)}")
        print(f"  {out}")
        raise RuntimeError(f"git exited {result.returncode}")
    return out


def match_sources(source_dir: Path) -> tuple[dict[str, Path], list[Path]]:
    """Pair source images with roster entries by filename stem.

    Returns ``({entry_name: source_path}, [unmatched_files])``. Unmatched files
    are reported rather than published: a typo in a filename would otherwise put
    an image on the site under a name no dropdown can ever reach.
    """
    by_norm = {normalize_name(name): name for name in entry_names()}
    matched: dict[str, Path] = {}
    unmatched: list[Path] = []
    for path in sorted(source_dir.iterdir(), key=lambda p: p.name.lower()):
        if path.suffix.lower() not in (".jpeg", ".jpg", ".png", ".webp"):
            continue
        entry = by_norm.get(normalize_name(path.stem))
        if entry is None:
            unmatched.append(path)
        else:
            matched[entry] = path
    return matched, unmatched


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Publish the {GALLERY_KIND} gallery to the {BRANCH} branch.")
    parser.add_argument("--source", required=True,
                        help="Folder of full-size images named after entries.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace images for entries that already have one. "
                             "Default is to add only what is missing.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report the plan and exit without changing anything.")
    parser.add_argument("--prune-orphans", action="store_true",
                        help="Also delete published images matching no roster "
                             "entry (renamed/deleted characters). Off by default.")
    parser.add_argument("--no-push", action="store_true",
                        help="Commit to the local branch but do not push. Lets you "
                             "inspect the result before it goes live.")
    parser.add_argument("--message", default=f"Update {GALLERY_KIND} gallery",
                        help="Commit message.")
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.is_dir():
        print(f"ERROR: source folder not found: {source_dir}")
        return 1

    matched, unmatched = match_sources(source_dir)
    print(f"Gallery      : {GALLERY_KIND}")
    print(f"Source folder: {source_dir}")
    print(f"Mode         : {'OVERWRITE existing' if args.overwrite else 'ADD missing only'}")
    print(f"Roster        : {len(entry_names())} entries")
    print(f"Source images : {len(matched)} matched, {len(unmatched)} unmatched")
    if unmatched:
        print("\n  These files match no roster entry and will be IGNORED "
              "(check the spelling):")
        for path in unmatched[:20]:
            print(f"    ? {path.name}")
        if len(unmatched) > 20:
            print(f"    ... and {len(unmatched) - 20} more")
    if not matched:
        print("\nNothing to publish. Stopping before touching the branch.")
        return 0

    worktree = Path(tempfile.mkdtemp(prefix=f"ifgallery-{GALLERY_KIND}-"))
    created = False
    try:
        print(f"\nChecking out {BRANCH} into a temporary worktree...")
        print("(your current checkout is not touched)")
        run("git", "worktree", "add", str(worktree), BRANCH)
        created = True
        run("git", "pull", "--ff-only", "origin", BRANCH, cwd=worktree)

        images_dir = worktree / "gallery" / GALLERY_KIND / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        published = {p.stem for p in images_dir.glob("*.jpeg")}
        print(f"Already published: {len(published)} image(s)")

        # Decide per entry. An entry that already has an image and was not
        # supplied this run never appears here at all -- that is the guarantee.
        to_write, skipped = {}, []
        for entry, src in matched.items():
            if normalize_name(entry) in published and not args.overwrite:
                skipped.append(entry)
            else:
                to_write[entry] = src

        print(f"\nPlan: {len(to_write)} to write, {len(skipped)} already present "
              f"(left untouched), {len(published) - len(skipped)} untouched entries "
              f"not in this source folder")

        orphans = []
        if args.prune_orphans:
            keep = {normalize_name(n) for n in entry_names()}
            orphans = sorted(p.name for p in images_dir.glob("*.jpeg")
                             if p.stem not in keep)
            print(f"Orphans to prune: {len(orphans)}")
            for name in orphans:
                print(f"    - {name}")

        if args.dry_run:
            print("\nDRY RUN - nothing written, nothing committed, nothing pushed.")
            for entry in sorted(to_write)[:30]:
                print(f"    + {entry}")
            if len(to_write) > 30:
                print(f"    ... and {len(to_write) - 30} more")
            return 0

        # Optimize straight into the branch checkout. No intermediate staging
        # directory to go stale and be published by accident on a later run.
        print()
        written = errors = 0
        for i, entry in enumerate(sorted(to_write), 1):
            dest = images_dir / f"{normalize_name(entry)}.jpeg"
            result = optimize_image(to_write[entry], dest)
            if result["status"] == "optimized":
                written += 1
                print(f"  [{i:4d}/{len(to_write)}] {entry[:48]:48s} "
                      f"{result['new_size']} ({result['output_bytes'] // 1024} KB)")
            else:
                errors += 1
                print(f"  [{i:4d}/{len(to_write)}] {entry[:48]:48s} "
                      f"ERROR: {result.get('reason')}")

        for name in orphans:
            (images_dir / name).unlink()

        # Rebuild the manifest from what is ACTUALLY on the branch now. This is
        # the line that makes the safety guarantee true rather than aspirational.
        manifest = generate_manifest(str(images_dir),
                                     str(images_dir.parent / "manifest.json"))
        print(f"\nManifest: {manifest['total_entries']} entries, "
              f"{manifest['entries_with_images']} with images, "
              f"{manifest['entries_missing_images']} still missing")

        for fname in PAGE_FILES:
            src = GALLERY_SRC_DIR / fname
            if src.exists():
                (worktree / REL_DIR / fname).write_text(
                    src.read_text(encoding="utf-8"), encoding="utf-8", newline="")

        # -A, not a bare add: a plain `git add` stages additions and
        # modifications but NOT deletions, so a prune would be silently undone.
        run("git", "add", "-A", REL_DIR, cwd=worktree)
        if not run("git", "status", "--porcelain", cwd=worktree):
            print("\nNothing changed on the branch.")
            return 0

        run("git", "commit", "-m", args.message, cwd=worktree)
        if args.no_push:
            print()
            print(f"Committed to the local {BRANCH} branch but NOT pushed.")
            print(f"Review it:   git log {BRANCH} -1 --stat")
            print(f"Publish it:  git push origin {BRANCH}")
            print(f"Discard it:  git branch -f {BRANCH} origin/{BRANCH}")
            return 1 if errors else 0
        print("Pushing...")
        run("git", "push", "origin", BRANCH, cwd=worktree)
        print(f"\nDone. {written} image(s) published"
              + (f", {errors} error(s)" if errors else "") + ".")
        print(f"https://enragedantelope.github.io/comfyui-identity-forge/{REL_DIR}/")
        return 1 if errors else 0

    finally:
        if created:
            try:
                run("git", "worktree", "remove", "--force", str(worktree))
            except RuntimeError:
                print(f"WARNING: could not remove the temporary worktree at "
                      f"{worktree}.\n         Run: git worktree prune")


if __name__ == "__main__":
    raise SystemExit(main())
