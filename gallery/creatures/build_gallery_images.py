"""Optimize CREATURE sample images for web display.

Standalone bulk tool: resize to 600px wide, JPEG quality 80, keep aspect ratio.

    python gallery/creatures/build_gallery_images.py --source <dir> --output <dir>

``publish.py`` imports :func:`optimize_image` from here and writes straight into
the gh-pages checkout, so the normal workflow never needs this script directly.
Use it when you want a local optimized copy without publishing.

=============================================================================
 THIS FILE IS ONE OF THREE NEAR-IDENTICAL COPIES
 gallery/creatures/ - gallery/archetypes/ - gallery/creatures/
 They differ ONLY in the GALLERY CONFIG block below. Fix a bug here and apply
 it to the other two (see gallery/README.md).
=============================================================================
"""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised by the dependency-free CI run
    # Pillow is OPTIONAL and only the encode path needs it. Importing this module
    # must never kill the process: `publish.py`, `cross_reference.py` and the test
    # suite all import it, and CI installs no third-party packages at all (the
    # pack itself is zero-dependency). A `sys.exit(1)` here took the whole test
    # run down with "ERROR: Pillow is required" the moment tests/test_gallery.py
    # started importing it.
    Image = None

PILLOW_HINT = "Pillow is required to optimize images. Install it: pip install Pillow"

# === GALLERY CONFIG - the only part that differs between the three copies ====
GALLERY_KIND = "creatures"
# ============================================================================

#: 600px is the widest the gallery grid ever renders a card, so anything larger
#: is bytes the visitor downloads and never sees.
MAX_WIDTH = 600
JPEG_QUALITY = 80

SOURCE_SUFFIXES = (".jpeg", ".jpg", ".png", ".webp")


def optimize_image(source_path: Path, output_path: Path) -> dict:
    """Resize and re-encode one image. Returns a stats dict, never raises."""
    if Image is None:
        return {"status": "error", "reason": PILLOW_HINT}
    source_path = Path(source_path)
    output_path = Path(output_path)
    if source_path.suffix.lower() not in SOURCE_SUFFIXES:
        return {"status": "skipped", "reason": f"not an image ({source_path.suffix})"}

    try:
        img = Image.open(source_path)
        # JPEG has no alpha channel; converting first avoids a save error on
        # PNG/WebP sources with transparency.
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        original_size = img.size
        original_bytes = source_path.stat().st_size
        if img.width > MAX_WIDTH:
            new_height = int(img.height * (MAX_WIDTH / img.width))
            img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        output_bytes = output_path.stat().st_size
        return {
            "status": "optimized",
            "original_size": f"{original_size[0]}x{original_size[1]}",
            "new_size": f"{img.size[0]}x{img.size[1]}",
            "original_bytes": original_bytes,
            "output_bytes": output_bytes,
            "reduction_pct": round((1 - output_bytes / original_bytes) * 100, 1),
        }
    except Exception as exc:  # noqa: BLE001 - report and continue the batch
        return {"status": "error", "reason": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Optimize {GALLERY_KIND} gallery images for the web.")
    parser.add_argument("--source", required=True, help="Folder of full-size images.")
    parser.add_argument("--output", required=True, help="Folder for optimized JPEGs.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Leave images already present in --output alone.")
    args = parser.parse_args()

    if Image is None:
        print(f"ERROR: {PILLOW_HINT}")
        return 1

    source_dir, output_dir = Path(args.source), Path(args.output)
    if not source_dir.is_dir():
        print(f"ERROR: source folder not found: {source_dir}")
        return 1

    files = sorted((f for f in source_dir.iterdir()
                    if f.suffix.lower() in SOURCE_SUFFIXES),
                   key=lambda f: f.name.lower())
    print(f"Found {len(files)} image(s) in {source_dir}")
    print(f"Output: {output_dir}   ({MAX_WIDTH}px wide, quality {JPEG_QUALITY})")
    if args.skip_existing:
        print("Mode: INCREMENTAL - existing outputs are left alone")
    if args.dry_run:
        print("Mode: DRY RUN - nothing will be written")
    print("-" * 62)

    done = skipped = errors = 0
    src_mb = out_mb = 0.0
    for i, path in enumerate(files, 1):
        dest = output_dir / f"{path.stem}.jpeg"
        if args.skip_existing and dest.exists():
            skipped += 1
            continue
        if args.dry_run:
            done += 1
            continue
        result = optimize_image(path, dest)
        if result["status"] == "optimized":
            done += 1
            src_mb += result["original_bytes"] / (1024 * 1024)
            out_mb += result["output_bytes"] / (1024 * 1024)
            print(f"  [{i:4d}/{len(files)}] {path.name[:46]:46s} "
                  f"{result['original_size']} -> {result['new_size']} "
                  f"({result['output_bytes'] // 1024} KB, -{result['reduction_pct']}%)")
        elif result["status"] == "error":
            errors += 1
            print(f"  [{i:4d}/{len(files)}] {path.name[:46]:46s} "
                  f"ERROR: {result['reason']}")
        else:
            skipped += 1

    print("-" * 62)
    print(f"  Processed: {done}   Skipped: {skipped}   Errors: {errors}")
    if not args.dry_run and src_mb:
        print(f"  {src_mb:.1f} MB -> {out_mb:.1f} MB "
              f"({(1 - out_mb / src_mb) * 100:.1f}% smaller)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
