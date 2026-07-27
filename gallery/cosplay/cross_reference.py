"""Cross-reference cosplayers.py entries against available JPEG sample images.

Tells you two things after a roster change: which characters still need a sample
image generated, and which image files are now orphaned (a character renamed or
deleted). ``deploy.py`` prunes the orphans from gh-pages on the next deploy.

Usage: python cross_reference.py
Outputs: missing.txt, extra.txt, and prints a summary.
"""

import os
import sys

# Add repo root to path to import cosplayers data
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from data.cosplayers import COSPLAYERS
from build_manifest import normalize_name

# Path to source images
IMAGES_DIR = r"D:\tempforgithubrepo\identityforge"


def main():
    # Match the way build_manifest.py pairs entries with files, or this script
    # reports phantom problems: Windows strips a trailing period, so the entry
    # "C.C." is stored as "C.C.jpeg". Exact-matching flagged it as BOTH a missing
    # entry and an orphaned image on every run, while the gallery showed it fine.
    cosplayer_names = {normalize_name(k) for k in COSPLAYERS}
    print(f"Cosplayer entries in code: {len(cosplayer_names)}")

    # Get all JPEG filenames (without extension)
    image_names = set()
    if os.path.isdir(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            if f.lower().endswith('.jpeg'):
                image_names.add(normalize_name(f[:-5]))
    else:
        print(f"WARNING: images directory not found: {IMAGES_DIR}")
        print("         Every entry will be reported as missing.")

    print(f"JPEG files available:     {len(image_names)}")

    # Cross-reference
    have_images = cosplayer_names & image_names
    missing_images = cosplayer_names - image_names
    extra_images = image_names - cosplayer_names

    print(f"\nEntries WITH images:      {len(have_images)}")
    print(f"Entries MISSING images:    {len(missing_images)}")
    print(f"Extra images (no code entry): {len(extra_images)}")

    # Write missing list
    missing_path = os.path.join(os.path.dirname(__file__), "missing.txt")
    with open(missing_path, "w", encoding="utf-8") as f:
        for name in sorted(missing_images):
            f.write(f"{name}\n")
    print(f"\nMissing entries written to: {missing_path}")

    # Write extra list
    if extra_images:
        extra_path = os.path.join(os.path.dirname(__file__), "extra.txt")
        with open(extra_path, "w", encoding="utf-8") as f:
            for name in sorted(extra_images):
                f.write(f"{name}\n")
        print(f"Extra images written to: {extra_path}")

    # Print sample missing
    if missing_images:
        print("\n--- Sample missing entries (first 25) ---")
        for name in sorted(missing_images)[:25]:
            print(f"  {name}")

    # Check for naming mismatches
    print("\n--- Checking for close-but-not-exact matches ---")
    for code_name in sorted(missing_images)[:50]:
        # Try to find close matches in extra_images
        code_lower = code_name.lower().replace(" ", "")
        for img_name in sorted(extra_images):
            img_lower = img_name.lower().replace(" ", "")
            if code_lower == img_lower:
                print(f"  EXACT match (case/space): code='{code_name}' <-> img='{img_name}'")
            elif code_lower in img_lower or img_lower in code_lower:
                if len(code_lower) > 3 and len(img_lower) > 3:
                    print(f"  PARTIAL match: code='{code_name}' <-> img='{img_name}'")


if __name__ == "__main__":
    main()
