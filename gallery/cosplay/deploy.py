"""Deploy gallery to gh-pages branch.

Copies optimized images and manifest from the build output to the gh-pages
working tree, commits, and pushes. Run from the repo root.

Usage:
  python gallery/cosplay/deploy.py              # Deploy all files
  python gallery/cosplay/deploy.py --dry-run    # Show what would happen
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO_ROOT)

# Paths
OPTIMIZED_IMAGES = r"D:\tempforgithubrepo\identityforge\optimized\cosplay"
GALLERY_SRC_DIR = os.path.join(REPO_ROOT, "gallery", "cosplay")


def run(cmd):
    """Run a command, return combined stdout+stderr. Raise on failure."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO_ROOT)
    out = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        print(f"  ERROR: {out}")
        raise RuntimeError(f"Command failed: {cmd}")
    return out

def main():
    parser = argparse.ArgumentParser(description="Deploy gallery to gh-pages branch")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--message", default="Update cosplay gallery images and manifest", help="Commit message")
    args = parser.parse_args()

    # Validate inputs
    manifest_path = os.path.join(GALLERY_SRC_DIR, "manifest.json")
    if not os.path.isfile(manifest_path):
        print("ERROR: manifest.json not found.")
        print("Run: python gallery/cosplay/build_manifest.py")
        sys.exit(1)

    if not os.path.isdir(OPTIMIZED_IMAGES):
        print(f"ERROR: Optimized images not found at {OPTIMIZED_IMAGES}")
        sys.exit(1)

    # Read manifest into memory BEFORE switching branches (avoids file-lock on self-copy)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    image_files = sorted(Path(OPTIMIZED_IMAGES).glob("*.jpeg"))
    print(f"Manifest: {manifest_data['entries_with_images']} entries with images")
    print(f"Optimized images: {len(image_files)} files")

    if args.dry_run:
        print("\nDRY RUN -- no changes.")
        print(f"Would copy {len(image_files)} images to gh-pages branch")
        print(f"Would write manifest.json ({len(json.dumps(manifest_data))} bytes)")
        print(f"Would commit: {args.message}")
        print("Would push to origin gh-pages")
        return

    # --- Git dance ---
    current_branch = run("git rev-parse --abbrev-ref HEAD")
    print(f"\nCurrent branch: {current_branch}")

    has_stash = False
    stash_out = run("git stash --include-untracked")
    if "No local changes to save" not in stash_out:
        has_stash = True
        print("Stashed uncommitted changes.")
    try:
        print("Switching to gh-pages...")
        run("git checkout gh-pages")
        print("Pulling latest...")
        run("git pull origin gh-pages --ff-only")

        target_images = os.path.join(REPO_ROOT, "gallery", "cosplay", "images")
        os.makedirs(target_images, exist_ok=True)

        copied = 0
        for img in image_files:
            dest = os.path.join(target_images, img.name)
            src_mtime = img.stat().st_mtime
            dest_mtime = os.path.getmtime(dest) if os.path.exists(dest) else 0
            if src_mtime > dest_mtime:
                shutil.copy2(img, dest)
                copied += 1

        print(f"Images: {copied} new/updated, {len(image_files) - copied} unchanged")

        # Write manifest from memory (avoids PermissionError on self-copy)
        manifest_dest = os.path.join(REPO_ROOT, "gallery", "cosplay", "manifest.json")
        os.makedirs(os.path.dirname(manifest_dest), exist_ok=True)
        with open(manifest_dest, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        print("Wrote manifest.json")

        run('git add "gallery/cosplay/images/" "gallery/cosplay/manifest.json"')

        status = run("git status --porcelain")
        if not status:
            print("\nNothing changed -- already up to date.")
        else:
            print(f"\nCommitting: {args.message}")
            run(f'git commit -m "{args.message}"')
            print("Pushing to origin gh-pages...")
            run("git push origin gh-pages")
            print("Deployed!")

    finally:
        print(f"\nSwitching back to {current_branch}...")
        run(f"git checkout {current_branch}")
        if has_stash:
            run("git stash pop")
            print("Restored stashed changes.")

    print("\nDone.")
    print("Gallery: https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/")


if __name__ == "__main__":
    main()
