"""Generate manifest.json for the CREATURE gallery.

    python gallery/creatures/build_manifest.py --images <dir>

=============================================================================
 THIS FILE IS ONE OF THREE NEAR-IDENTICAL COPIES
 gallery/creatures/build_manifest.py - gallery/archetypes/build_manifest.py -
 gallery/creatures/build_manifest.py
 They differ ONLY in the GALLERY CONFIG block below. Fix a bug here and apply
 it to the other two (see gallery/README.md).
=============================================================================

``publish.py`` calls this against the images that are actually on ``gh-pages``,
which is what makes "an entry you did not supply is left alone" true. Running it
by hand against some *other* folder describes that folder instead -- fine for a
local preview, dangerous if you then publish it. ``publish.py`` never does that.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

# === GALLERY CONFIG - the only part that differs between the three copies ====
GALLERY_KIND = "creatures"

from data.creatures import CREATURES  # noqa: E402

def entry_names() -> list[str]:
    """Every creature name this gallery can show an image for."""
    return list(CREATURES)


def entry_meta(name: str) -> dict:
    """Extra per-entry fields for the manifest; also searchable on the page."""
    data = CREATURES[name]
    return {
        "gender": "any",
        "group": data.get("class", ""),
    }
# ============================================================================

DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "manifest.json")


def normalize_name(name: str) -> str:
    """Normalize a name for filename comparison.

    Windows strips a trailing period, so the entry ``C.C.`` lands on disk as
    ``C.C.jpeg``. Matching without this reported that entry as simultaneously
    missing an image and having an orphaned one, on every single run.
    """
    name = name.rstrip(".")
    name = " ".join(name.split())
    return unicodedata.normalize("NFC", name)


def generate_manifest(images_dir: str, output_path: str) -> dict:
    """Build the manifest describing ``images_dir``."""
    images_path = Path(images_dir)
    if not images_path.is_dir():
        # Fail loudly. Continuing would emit a well-formed manifest in which
        # every entry has has_image=false -- a silently wrong artifact that,
        # once published, blanks the live gallery.
        raise SystemExit(
            f"ERROR: images directory not found: {images_dir}\n"
            f"Refusing to write a manifest claiming no entry has an image."
        )

    available: dict[str, str] = {}
    for f in images_path.iterdir():
        if f.suffix.lower() == ".jpeg":
            available.setdefault(normalize_name(f.stem), f.stem)

    entries, missing = [], []
    for name in sorted(entry_names()):
        stem = available.get(normalize_name(name))
        entry = {"name": name, "has_image": stem is not None, **entry_meta(name)}
        if stem is not None:
            entry["image"] = f"images/{stem}.jpeg"
        else:
            missing.append(name)
        entries.append(entry)

    manifest = {
        "schema_version": 1,
        "gallery": GALLERY_KIND,
        "generated": __import__("datetime").datetime.now().isoformat(),
        "total_entries": len(entries),
        "entries_with_images": len(entries) - len(missing),
        "entries_missing_images": len(missing),
        "missing": sorted(missing),
        "entries": entries,
    }

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Generate the {GALLERY_KIND} gallery manifest.")
    parser.add_argument("--images", required=True,
                        help="Directory of optimized JPEGs to describe.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = generate_manifest(args.images, args.output)
    print(f"  Total entries:  {manifest['total_entries']}")
    print(f"  With images:    {manifest['entries_with_images']}")
    print(f"  Missing images: {manifest['entries_missing_images']}")
    print(f"Written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
