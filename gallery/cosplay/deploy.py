"""Deploy gallery to gh-pages branch.

Copies optimized images and manifest from the build output to the gh-pages
working tree, commits, and pushes. Run from the repo root.

Usage:
  python gallery\cosplay\deploy.py              # Deploy all files
  python gallery\cosplay\deploy.py --dry-run    # Show what would happen
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO_ROOT)

# Paths
OPTIMIZED_IMAGES = r"D:\tempforgithubrepo\identityforge\optimized\cosplay"
GALLERY_DIR = os.path.join(REPO_ROOT, "gallery", "cosplay")
MANIFEST_SRC = os.path.join(GALLERY_DIR, "manifest.json")


def run(cmd, **kwargs):
    """Run a git command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO_ROOT, **kwargs)
    return result.stdout.strip() + result.stderr.strip()


def main():
    parser = argparse.ArgumentParser(description="Deploy gallery to gh-pages branch")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--message", default="Update cosplay gallery images and manifest", help="Commit message")
    args = parser.parse_args()

    # Verify optimized images exist
    if not os.path.isdir(OPTIMIZED_IMAGES):
        print(f"ERROR: Optimized images not found at {OPTIMIZED_IMAGES}")
        sys.exit(1)

    if not os.path.isfile(MANIFEST_SRC):
        print(f"ERROR: manifest.json not found at {MANIFEST_SRC}")
        print("Run build_manifest.py first: python gallery/cosplay/build_manifest.py")
        sys.exit(1)

    # Count images
    image_files = list(Path(OPTIMIZED_IMAGES).glob("*.jpeg"))
    print(f"Found {len(image_files)} optimized images")
    print(f"Manifest: {MANIFEST_SRC}")
    print()

    if args.dry_run:
        print("DRY RUN — no changes will be made.")
        print(f"Would copy {len(image_files)} images to gh-pages branch")
        print(f"Would commit with message: {args.message}")
        print("Would push to origin gh-pages")
        return

    # Step 1: Save current branch
    current_branch = run("git rev-parse --abbrev-ref HEAD")
    print(f"Current branch: {current_branch}")

    # Step 2: Stash any uncommitted changes
    stash_result = run("git stash --include-untracked")
    has_stash = "No local changes to save" not in stash_result

    try:
        # Step 3: Switch to gh-pages
        print("Switching to gh-pages branch...")
        run("git checkout gh-pages")

        # Step 4: Pull latest gh-pages
        print("Pulling latest gh-pages...")
        run("git pull origin gh-pages --ff-only")

        # Step 5: Copy images
        target_images = os.path.join(REPO_ROOT, "gallery", "cosplay", "images")
        os.makedirs(target_images, exist_ok=True)

        print(f"Copying {len(image_files)} images...")
        copied = 0
        for img in image_files:
            dest = os.path.join(target_images, img.name)
            src_mtime = img.stat().st_mtime
            dest_mtime = os.path.getmtime(dest) if os.path.exists(dest) else 0
            if src_mtime > dest_mtime:
                shutil.copy2(img, dest)
                copied += 1

        print(f"  {copied} new/updated, {len(image_files) - copied} unchanged")

        # Step 6: Copy manifest
        manifest_dest = os.path.join(GALLERY_DIR, "manifest.json")
        shutil.copy2(MANIFEST_SRC, manifest_dest)
        print("Copied manifest.json")

        # Step 7: Stage
        run(f'git add "gallery/cosplay/images/" "gallery/cosplay/manifest.json"')

        # Step 8: Check if anything changed
        status = run("git status --porcelain")
        if not status:
            print("\nNothing changed — already up to date.")
        else:
            # Step 9: Commit
            print(f"\nCommitting: {args.message}")
            run(f'git commit -m "{args.message}"')

            # Step 10: Push
            print("Pushing to origin gh-pages...")
            run("git push origin gh-pages")
            print("Deployed!")

    finally:
        # Step 11: Switch back to original branch
        print(f"\nSwitching back to {current_branch}...")
        run(f"git checkout {current_branch}")

        # Step 12: Restore stash
        if has_stash:
            run("git stash pop")

    print("\nDone. Gallery updated at:")
    print("  https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/")


if __name__ == "__main__":
    main()
