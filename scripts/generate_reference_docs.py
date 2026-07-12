#!/usr/bin/env python
"""Generate the human-readable reference indexes under ``docs/reference/``.

These Markdown files are a **generated** catalogue of everything the data layer
ships -- cosplayers, creatures, and archetypes -- so contributors and users can
review the full roster without opening the (large) data modules. They carry no
data of their own: run this script after any change to ``data/cosplayers.py``,
``data/creatures.py`` or ``data/templates.py`` and commit the refreshed output.

Usage (from the repo root)::

    python scripts/generate_reference_docs.py            # write docs/reference/*.md
    python scripts/generate_reference_docs.py --check    # fail if out of date (CI)

The ``--check`` mode regenerates in memory and compares, exiting non-zero if the
committed files differ -- so a stale index is caught before merge.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.cosplayers import (  # noqa: E402
    COSPLAYERS, get_cosplayer_category, get_cosplayer_categories,
)
from data.creatures import CREATURES  # noqa: E402
from data.templates import ARCHETYPES  # noqa: E402

REFERENCE_DIR = ROOT / "docs" / "reference"

_GENERATED_BANNER = (
    "<!-- GENERATED FILE - do not edit by hand.\n"
    "     Regenerate with: python scripts/generate_reference_docs.py -->\n"
)


def _cosplayer_flags(entry: dict) -> str:
    """Compact bracketed markers for a cosplayer's optional features."""
    flags: list[str] = []
    gender = entry.get("gender", "Any")
    flags.append({"Female": "F", "Male": "M"}.get(gender, "any"))
    if entry.get("size_scale"):
        flags.append(entry["size_scale"])  # giant / tiny
    if entry.get("covers_face"):
        flags.append("masked")
    alts = entry.get("costumes")
    if alts:
        flags.append(f"+{len(alts)} alt")
    if entry.get("prop"):
        flags.append("prop")
    return ", ".join(flags)


def build_cosplayers_md() -> str:
    """Roster grouped by broad category, then franchise, then name."""
    lines = [_GENERATED_BANNER, "# Cosplayer reference", ""]
    lines.append(f"**{len(COSPLAYERS)} characters.** Flags: `F`/`M` = source gender, "
                 "`giant`/`tiny` = size scale, `masked` = full-face covering, "
                 "`+N alt` = extra costumes, `prop` = signature held item.")
    lines.append("")
    # category -> franchise -> [(name, flags)]
    by_cat: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for name, entry in COSPLAYERS.items():
        franchise = entry.get("franchise", "")
        cat = get_cosplayer_category(franchise)
        by_cat.setdefault(cat, {}).setdefault(franchise, []).append(
            (name, _cosplayer_flags(entry)))
    for cat in get_cosplayer_categories():
        franchises = by_cat.get(cat, {})
        count = sum(len(v) for v in franchises.values())
        lines.append(f"## {cat} ({count})")
        lines.append("")
        for franchise in sorted(franchises):
            lines.append(f"### {franchise}")
            lines.append("")
            for name, flags in sorted(franchises[franchise]):
                lines.append(f"- **{name}** ({flags})")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_creatures_md() -> str:
    """Creature roster grouped by taxonomic class."""
    lines = [_GENERATED_BANNER, "# Creature reference", ""]
    lines.append(f"**{len(CREATURES)} creatures.** Each fills a hybrid's anatomy "
                 "slots; the default colour palette is shown in parentheses.")
    lines.append("")
    by_class: dict[str, list[tuple[str, str]]] = {}
    class_order: list[str] = []
    for name, entry in CREATURES.items():
        cls = entry.get("class", "Other")
        if cls not in by_class:
            class_order.append(cls)
        by_class.setdefault(cls, []).append((name, entry.get("palette", "")))
    for cls in class_order:
        members = by_class[cls]
        lines.append(f"## {cls} ({len(members)})")
        lines.append("")
        for name, palette in sorted(members):
            suffix = f" ({palette})" if palette else ""
            lines.append(f"- **{name}**{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_archetypes_md() -> str:
    """Archetype roster, alphabetical, with source gender and outfit style."""
    lines = [_GENERATED_BANNER, "# Archetype reference", ""]
    lines.append(f"**{len(ARCHETYPES)} archetypes.** Each is a curated look wired "
                 "through the Archetype node. `gender` shows a locked gender (blank = "
                 "either); `outfit` is the archetype's outfit style.")
    lines.append("")
    for name in sorted(ARCHETYPES):
        preset = ARCHETYPES[name]
        gender = preset.get("gender", "")
        gtag = f" [{gender}]" if gender else ""
        outfit = preset.get("outfit_style") or preset.get("outfit_description") or ""
        # A curated multi-option field may be a list; show the first for brevity.
        if isinstance(outfit, list):
            outfit = outfit[0] if outfit else ""
        otag = f" -- {outfit}" if outfit else ""
        lines.append(f"- **{name}**{gtag}{otag}")
    return "\n".join(lines).rstrip() + "\n"


_BUILDERS = {
    "cosplayers.md": build_cosplayers_md,
    "creatures.md": build_creatures_md,
    "archetypes.md": build_archetypes_md,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Verify the committed docs match the data (exit 1 if stale).")
    args = parser.parse_args(argv)

    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    for filename, builder in _BUILDERS.items():
        content = builder()
        path = REFERENCE_DIR / filename
        if args.check:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if existing != content:
                stale.append(filename)
        else:
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")

    if args.check:
        if stale:
            print("Reference docs are STALE: " + ", ".join(stale))
            print("Regenerate with: python scripts/generate_reference_docs.py")
            return 1
        print("Reference docs are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
