"""Report which CREATURE entries still need a sample image.

    python gallery/creatures/cross_reference.py                 # against gh-pages
    python gallery/creatures/cross_reference.py --images <dir>  # against a folder

Read-only. Writes ``missing.txt`` / ``orphans.txt`` beside this script (both
git-ignored) and prints a summary. Deletes nothing, publishes nothing.

=============================================================================
 THIS FILE IS ONE OF THREE NEAR-IDENTICAL COPIES
 gallery/creatures/ - gallery/archetypes/ - gallery/creatures/
 They differ ONLY in the GALLERY CONFIG block below. Fix a bug here and apply
 it to the other two (see gallery/README.md).
=============================================================================
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# === GALLERY CONFIG - the only part that differs between the three copies ====
GALLERY_KIND = "creatures"
# ============================================================================

from build_manifest import entry_names, normalize_name  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
BRANCH = "gh-pages"


def published_stems() -> set[str]:
    """Image stems currently on the gh-pages branch, read without checking out."""
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", BRANCH,
         f"gallery/{GALLERY_KIND}/images/"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if listing.returncode != 0:
        print(f"WARNING: could not read branch {BRANCH}; treating it as empty.")
        return set()
    return {normalize_name(Path(line).stem)
            for line in listing.stdout.splitlines() if line.endswith(".jpeg")}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Report {GALLERY_KIND} gallery image coverage.")
    parser.add_argument("--images", help="Check a local folder instead of gh-pages.")
    args = parser.parse_args()

    if args.images:
        folder = Path(args.images)
        if not folder.is_dir():
            print(f"ERROR: folder not found: {folder}")
            return 1
        have = {normalize_name(f.stem) for f in folder.iterdir()
                if f.suffix.lower() == ".jpeg"}
        source_label = str(folder)
    else:
        have = published_stems()
        source_label = f"branch {BRANCH}"

    names = entry_names()
    wanted = {normalize_name(n): n for n in names}

    missing = sorted(orig for norm, orig in wanted.items() if norm not in have)
    orphans = sorted(stem for stem in have if stem not in wanted)

    print(f"Gallery : {GALLERY_KIND}")
    print(f"Images  : {source_label}")
    print(f"Entries : {len(names)}")
    print(f"  with an image : {len(names) - len(missing)}")
    print(f"  MISSING       : {len(missing)}")
    print(f"  orphaned files: {len(orphans)}  (no roster entry matches these)")

    (HERE / "missing.txt").write_text(
        "\n".join(missing) + ("\n" if missing else ""), encoding="utf-8")
    (HERE / "orphans.txt").write_text(
        "\n".join(orphans) + ("\n" if orphans else ""), encoding="utf-8")

    if missing:
        print("\n--- Entries needing an image (first 25) ---")
        for name in missing[:25]:
            print(f"  {name}")
        if len(missing) > 25:
            print(f"  ... and {len(missing) - 25} more (see missing.txt)")
    if orphans:
        print("\n--- Orphaned images (first 25) ---")
        for stem in orphans[:25]:
            print(f"  {stem}.jpeg")
        print("\nThese match no roster entry, usually because the entry was "
              "renamed or removed.\nRemove them with: publish.py --prune-orphans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
