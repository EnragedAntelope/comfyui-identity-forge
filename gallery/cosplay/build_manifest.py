"""Generate manifest.json for the cosplay gallery.

Reads cosplayers.py to get character names and metadata, scans the optimized
images directory, and generates a manifest JSON file used by the gallery page.

Usage:
  python build_manifest.py                    # Generate from default paths
  python build_manifest.py --images <dir>     # Custom images directory
  python build_manifest.py --output <file>    # Custom output path
"""

import argparse
import json
import os
import sys
import unicodedata
from pathlib import Path

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from data.cosplayers import COSPLAYERS

# Default paths
DEFAULT_IMAGES_DIR = r"D:\tempforgithubrepo\identityforge\optimized\cosplay"
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "manifest.json")

# Sentinel entries in the dropdown (not real characters, no images)
SENTINEL_NAMES = {"None", "Random — any", "Random — female", "Random — male"}


def normalize_name(name: str) -> str:
    """Normalize a name for filename comparison.

    Handles edge cases:
    - Trailing periods that Windows strips (C.C. -> C.C)
    - Extra whitespace
    - Unicode normalization (smart quotes, etc.)
    """
    name = name.rstrip('.')
    name = ' '.join(name.split())
    name = unicodedata.normalize('NFC', name)
    return name


def find_image_name(code_name: str, available_images: set, norm_lookup: dict) -> str | None:
    """Find matching image filename for a code entry name.

    Tries exact match first, then normalized match via lookup.
    Returns the actual image filename stem, or None.
    """
    if code_name in available_images:
        return code_name

    # Try normalized match
    normalized = normalize_name(code_name)
    if normalized in norm_lookup:
        return norm_lookup[normalized]

    return None


def generate_manifest(images_dir: str, output_path: str) -> dict:
    """Generate the gallery manifest."""
    # Build set of available images and normalized lookup
    available_images = set()
    norm_lookup = {}  # normalized_name -> actual_filename_stem

    images_path = Path(images_dir)
    if not images_path.is_dir():
        # Fail loudly. Continuing would write a perfectly well-formed manifest in
        # which every entry has has_image=false -- a silently wrong artifact that
        # deploy.py would then push, blanking the live gallery.
        raise SystemExit(
            f"ERROR: images directory not found: {images_dir}\n"
            f"Pass --images <dir>, or mount the drive holding the optimized JPEGs. "
            f"Refusing to write a manifest that claims no character has an image."
        )
    if images_path.is_dir():
        for f in images_path.iterdir():
            if f.suffix.lower() == '.jpeg':
                stem = f.stem
                available_images.add(stem)
                norm = normalize_name(stem)
                if norm not in norm_lookup:
                    norm_lookup[norm] = stem

    # Build entries list
    entries = []
    missing = []
    total = 0

    for name in sorted(COSPLAYERS.keys()):
        if name in SENTINEL_NAMES:
            continue
        total += 1
        char_data = COSPLAYERS[name]

        # Find matching image name (handles Windows filename edge cases)
        img_stem = find_image_name(name, available_images, norm_lookup)
        has_image = img_stem is not None

        entry = {
            "name": name,
            "has_image": has_image,
            "gender": char_data.get("gender", "unknown"),
            "franchise": char_data.get("franchise", ""),
        }

        if has_image:
            entry["image"] = f"images/{img_stem}.jpeg"
        entries.append(entry)

        if not has_image:
            missing.append(name)

    manifest = {
        "schema_version": 1,
        "generated": __import__("datetime").datetime.now().isoformat(),
        "total_entries": total,
        "entries_with_images": total - len(missing),
        "entries_missing_images": len(missing),
        "missing": sorted(missing),
        "entries": entries,
    }

    # Write manifest
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate gallery manifest from cosplayers.py")
    parser.add_argument("--images", default=DEFAULT_IMAGES_DIR, help="Directory with optimized JPEGs")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output manifest.json path")
    args = parser.parse_args()

    print("Reading cosplayer data from cosplayers.py...")
    print(f"Scanning images in: {args.images}")
    print(f"Output: {args.output}")

    manifest = generate_manifest(args.images, args.output)

    print("\nManifest generated:")
    print(f"  Total entries:        {manifest['total_entries']}")
    print(f"  With images:          {manifest['entries_with_images']}")
    print(f"  Missing images:       {manifest['entries_missing_images']}")

    if manifest["missing"]:
        print("\nMissing entries (no image yet):")
        for name in sorted(manifest["missing"])[:10]:
            print(f"  - {name}")
        if len(manifest["missing"]) > 10:
            print(f"  ... and {len(manifest['missing']) - 10} more")

    print(f"\nDone. Manifest written to {args.output}")


if __name__ == "__main__":
    main()
