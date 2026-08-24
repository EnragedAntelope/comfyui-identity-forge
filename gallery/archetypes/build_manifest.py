"""Generate manifest.json for the ARCHETYPE gallery.

    python gallery/archetypes/build_manifest.py --images <dir>

=============================================================================
 THIS FILE IS ONE OF THREE NEAR-IDENTICAL COPIES
 gallery/cosplay/build_manifest.py - gallery/archetypes/build_manifest.py -
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
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

# === GALLERY CONFIG - the only part that differs between the three copies ====
GALLERY_KIND = "archetypes"
#: This gallery's key in ``data/versions.py`` (written by
#: ``scripts/stamp_versions.py``). Differs from GALLERY_KIND for cosplay,
#: whose folder is "cosplay" but whose data module is "cosplayers".
VERSIONS_KIND = "archetypes"

from data.templates import ARCHETYPES  # noqa: E402

def entry_names() -> list[str]:
    """Every archetype name this gallery can show an image for."""
    return list(ARCHETYPES)


def entry_meta(name: str) -> dict:
    """Extra per-entry fields for the manifest; also searchable on the page."""
    data = ARCHETYPES[name]
    return {
        "gender": data.get("gender", "any"),
        "group": data.get("outfit_style", ""),
    }
# ============================================================================

DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "manifest.json")


def pack_version() -> str:
    """The version in ``pyproject.toml``, used for the "New in ..." filter."""
    import re
    text = (Path(REPO_ROOT) / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else ""


def release_order() -> tuple:
    """Every release that shipped roster content, oldest first."""
    from data.versions import RELEASES
    return RELEASES


def release_stamps() -> dict:
    """``{entry name: release}`` for this gallery's kind.

    Written by ``scripts/stamp_versions.py`` and checked in CI. An entry with no
    stamp (a user-added one) gets ``""`` and the page treats it as oldest.
    """
    from data.versions import ADDED_IN
    return dict(ADDED_IN.get(VERSIONS_KIND, {}))



#: Characters no Windows (and, for ``/``, no POSIX) filename may contain. A roster
#: name is a display label, not a filename, so any entry is free to use them --
#: ``B-Boy / B-Girl`` reads correctly in the dropdown and must not be renamed just
#: to suit the gallery. The saving side strips them silently, so the MATCHING side
#: has to do the same or the image can never be paired with its entry.
_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


def normalize_name(name: str) -> str:
    """Normalize a name for filename comparison.

    Three separate things Windows does to a name on its way to disk, each of which
    silently broke the pairing before it was handled here:

    * **Trailing period dropped** -- the entry ``C.C.`` lands as ``C.C.jpeg``.
      Without this, that entry was reported as *both* missing an image and having
      an orphaned one, on every single run.
    * **Illegal characters removed** -- ``B-Boy / B-Girl`` is saved as
      ``B-Boy  B-Girl.jpeg``. Substituting a space (not the empty string) is what
      makes the stripped filename and the original label converge, since the label
      already has spaces either side of the slash.
    * **Whitespace runs** -- the substitution above leaves a double space, and a
      hand-typed filename may differ in spacing anyway. Collapsing both sides makes
      ``B-Boy  B-Girl`` and ``B-Boy B-Girl`` the same key.

    Callers that build a *filename* use this too, so the canonical on-disk form is
    whatever this returns. NFC last, so a decomposed accent from a Mac-authored
    filename matches a composed one in the roster.
    """
    name = _UNSAFE_FILENAME_CHARS.sub(" ", name)
    name = name.rstrip(". ")
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

    stamps = release_stamps()

    entries, missing = [], []
    for name in sorted(entry_names()):
        stem = available.get(normalize_name(name))
        entry = {"name": name, "has_image": stem is not None, **entry_meta(name)}
        # The release this entry first shipped in, "" for a user-added one. The page
        # ranks by POSITION IN ``releases`` below, never by parsing this string --
        # "0.10.0" sorts before "0.9.0" as text.
        entry["added"] = stamps.get(name, "")
        if stem is not None:
            entry["image"] = f"images/{stem}.jpeg"
        else:
            missing.append(name)
        entries.append(entry)

    manifest = {
        # 2 (0.97.0): entries gained "added", and the manifest gained
        # "version" + "releases", so the page can offer a Newest-first sort.
        # A page served an older manifest simply sees every entry as unstamped
        # and falls back to A-Z, so the bump is informational.
        "schema_version": 2,
        "gallery": GALLERY_KIND,
        "generated": __import__("datetime").datetime.now().isoformat(),
        "version": pack_version(),
        "releases": list(release_order()),
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
