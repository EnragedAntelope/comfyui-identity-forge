"""Cross-reference cosplayers.py entries against available JPEG sample images.

Usage: python cross_reference.py
Outputs: missing.txt, extra.txt, and prints a summary.
"""

import os
import sys

# Add repo root to path to import cosplayers data
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from data.cosplayers import COSPLAYERS

# Path to source images
IMAGES_DIR = r"D:\tempforgithubrepo\identityforge"

def main():
    # Get all cosplayer names
    cosplayer_names = set(COSPLAYERS.keys())
    print(f"Cosplayer entries in code: {len(cosplayer_names)}")

    # Get all JPEG filenames (without extension)
    image_names = set()
    if os.path.isdir(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            if f.lower().endswith('.jpeg'):
                name = f[:-5]  # Remove '.jpeg'
                image_names.add(name)

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
        print(f"\n--- Sample missing entries (first 25) ---")
        for name in sorted(missing_images)[:25]:
            print(f"  {name}")

    # Check for naming mismatches
    print(f"\n--- Checking for close-but-not-exact matches ---")
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
