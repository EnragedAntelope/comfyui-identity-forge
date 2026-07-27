"""Deploy gallery to gh-pages branch.

Copies optimized images, manifest, and page files from the build output
to the gh-pages working tree, commits, and pushes.

Run from the repo root AFTER running build_manifest.py.

Usage:
  python gallery/cosplay/deploy.py              # Deploy (timestamp-based)
  python gallery/cosplay/deploy.py --force      # Copy ALL files
  python gallery/cosplay/deploy.py --dry-run    # Show what would happen
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO_ROOT)

OPTIMIZED_IMAGES = r"D:\tempforgithubrepo\identityforge\optimized\cosplay"
GALLERY_SRC_DIR = os.path.join(REPO_ROOT, "gallery", "cosplay")


def run(*cmd):
    """Run a git command given as separate argv words.

    Deliberately NOT ``shell=True``: the commit message is user-supplied via
    ``--message`` and used to be interpolated into a shell string, so a quote or a
    semicolon in it either broke the command or ran as shell syntax. Passing argv
    removes the quoting problem entirely.
    """
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    out = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        print(f"  CMD FAILED: {' '.join(cmd)}")
        print(f"  {out}")
        raise RuntimeError(f"Command failed (exit {result.returncode})")
    return out


def try_copy(img_path, dest, retries=3):
    """Copy with retry for transient Windows file locks."""
    for i in range(retries):
        try:
            shutil.copy2(img_path, dest)
            return
        except PermissionError:
            if i < retries - 1:
                time.sleep(1.0)
            else:
                raise


def main():
    parser = argparse.ArgumentParser(description="Deploy gallery to gh-pages branch")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="Copy ALL files regardless of timestamp")
    parser.add_argument("--message", default="Update cosplay gallery",
                        help="Commit message")
    args = parser.parse_args()

    manifest_path = os.path.join(GALLERY_SRC_DIR, "manifest.json")
    if not os.path.isfile(manifest_path):
        print("ERROR: manifest.json not found. Run build_manifest.py first.")
        sys.exit(1)
    if not os.path.isdir(OPTIMIZED_IMAGES):
        print(f"ERROR: Optimized images not found at {OPTIMIZED_IMAGES}")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    image_files = sorted(Path(OPTIMIZED_IMAGES).glob("*.jpeg"))
    print(f"Manifest: {manifest_data['entries_with_images']} entries with images")
    print(f"Images: {len(image_files)} files")

    # Exactly the image files the manifest points at. Anything else under
    # images/ on gh-pages is an orphan -- a character that was renamed or deleted
    # since the last deploy -- and gets pruned below.
    wanted = {
        os.path.basename(e["image"])
        for e in manifest_data["entries"] if e.get("image")
    }

    if args.dry_run:
        print("\nDRY RUN -- would copy images, page files, manifest, commit, push.")
        print(f"Manifest references {len(wanted)} image files.")
        return

    current_branch = run("git", "rev-parse", "--abbrev-ref", "HEAD")
    print(f"\nBranch: {current_branch}")

    has_stash = False
    stash_out = run("git", "stash", "--include-untracked")
    if "No local changes to save" not in stash_out:
        has_stash = True
        print("Stashed changes.")

    try:
        print("Switching to gh-pages...")
        run("git", "checkout", "gh-pages")
        print("Pulling latest...")
        run("git", "pull", "origin", "gh-pages", "--ff-only")

        target = os.path.join(REPO_ROOT, "gallery", "cosplay", "images")
        os.makedirs(target, exist_ok=True)

        # Copy images
        copied = 0
        for img in image_files:
            dest = os.path.join(target, img.name)
            do_copy = args.force
            if not do_copy:
                src_mtime = img.stat().st_mtime
                dest_mtime = os.path.getmtime(dest) if os.path.exists(dest) else 0
                do_copy = src_mtime > dest_mtime
            if do_copy:
                try_copy(str(img), dest)
                copied += 1
        print(f"Images: {copied} copied, {len(image_files) - copied} unchanged")

        # Prune orphans. Without this the deploy is copy-only, so a character who
        # is renamed or removed keeps a live image on the site forever -- the
        # gallery slowly fills with entries no dropdown can reach. Driven off the
        # manifest rather than off the source directory, so a stale local build
        # cannot delete images the manifest still wants.
        pruned = []
        for existing in sorted(os.listdir(target)):
            if existing.lower().endswith(".jpeg") and existing not in wanted:
                os.remove(os.path.join(target, existing))
                pruned.append(existing)
        if pruned:
            print(f"Images: {len(pruned)} orphan(s) pruned")
            for name in pruned:
                print(f"    - {name}")

        # Sync page files via read+write (avoids Windows shutil.copy2 locks)
        page_files = ["index.html", "style.css", "gallery.js",
                      "Krea2_IdentityForge_CharacterCycle.json"]
        synced = []
        for fname in page_files:
            src = os.path.join(GALLERY_SRC_DIR, fname)
            if os.path.exists(src):
                dest = os.path.join(REPO_ROOT, "gallery", "cosplay", fname)
                with open(src, "r", encoding="utf-8") as fsrc:
                    content = fsrc.read()
                with open(dest, "w", encoding="utf-8", newline="") as fdst:
                    fdst.write(content)
                synced.append(fname)
        if synced:
            print(f"Page files: {', '.join(synced)}")

        # Write manifest
        manifest_dest = os.path.join(REPO_ROOT, "gallery", "cosplay", "manifest.json")
        os.makedirs(os.path.dirname(manifest_dest), exist_ok=True)
        with open(manifest_dest, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        print("Wrote manifest.json")

        # `git add -A` on the path, not `git add`: a plain add stages additions and
        # modifications but NOT deletions, so the pruned orphans above would be
        # restored by the next checkout and never actually leave the site.
        run("git", "add", "-A", "gallery/cosplay/")
        status = run("git", "status", "--porcelain")
        if not status:
            print("Nothing changed.")
        else:
            print(f"Committing: {args.message}")
            run("git", "commit", "-m", args.message)
            print("Pushing...")
            run("git", "push", "origin", "gh-pages")
            print("Deployed.")

    finally:
        print(f"\nSwitching back to {current_branch}...")
        try:
            run("git", "checkout", current_branch)
        except RuntimeError:
            print("WARNING: Could not switch back. Run: git checkout main")
        if has_stash:
            try:
                run("git", "stash", "pop")
            except RuntimeError:
                print("WARNING: Could not restore stash. Run: git stash pop")

    print("\nDone.")
    print("https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/")


if __name__ == "__main__":
    main()
