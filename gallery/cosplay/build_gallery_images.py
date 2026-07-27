"""Optimize cosplay sample images for web gallery display.

Resizes JPEGs to max 600px wide, quality 80, maintaining aspect ratio.
Processes images from source directory to output directory.

Usage:
  python build_gallery_images.py                    # Process all images
  python build_gallery_images.py --dry-run          # Show what would be done
  python build_gallery_images.py --source <dir>      # Custom source dir
  python build_gallery_images.py --output <dir>      # Custom output dir

This script is designed to be re-run as new images are added.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required. Install: pip install Pillow")
    sys.exit(1)

# Default paths
DEFAULT_SOURCE = r"D:\tempforgithubrepo\identityforge"
DEFAULT_OUTPUT = r"D:\tempforgithubrepo\identityforge\optimized\cosplay"

# Optimization settings
MAX_WIDTH = 600
JPEG_QUALITY = 80


def optimize_image(source_path: Path, output_path: Path, dry_run: bool = False) -> dict:
    """Optimize a single JPEG image. Returns stats dict."""
    if source_path.suffix.lower() not in ('.jpeg', '.jpg'):
        return {"status": "skipped", "reason": "not a JPEG"}

    if dry_run:
        return {"status": "would_process", "source_size": source_path.stat().st_size}

    try:
        img = Image.open(source_path)

        # Convert to RGB if necessary (e.g., RGBA, P mode)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        original_size = img.size
        original_bytes = source_path.stat().st_size

        # Resize only if wider than MAX_WIDTH
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save optimized JPEG
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

    except Exception as e:
        return {"status": "error", "reason": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Optimize cosplay gallery images for web")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without processing")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source directory with original JPEGs")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output directory for optimized images")
    parser.add_argument("--skip-existing", action="store_true", help="Skip images already present in output (incremental mode)")
    args = parser.parse_args()

    source_dir = Path(args.source)
    output_dir = Path(args.output)

    if not source_dir.is_dir():
        print(f"ERROR: Source directory not found: {source_dir}")
        sys.exit(1)

    # Find all JPEG files
    jpeg_files = sorted(
        [f for f in source_dir.iterdir() if f.suffix.lower() == '.jpeg'],
        key=lambda f: f.name.lower(),
    )
    incremental = args.skip_existing

    print(f"Found {len(jpeg_files)} JPEG files in {source_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Max width: {MAX_WIDTH}px, Quality: {JPEG_QUALITY}")
    if incremental:
        print("Mode: INCREMENTAL (skipping existing in output)")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("-" * 60)

    stats = {
        "total": len(jpeg_files),
        "optimized": 0,
        "skipped": 0,
        "errors": 0,
        "total_original_mb": 0.0,
        "total_output_mb": 0.0,
    }

    for i, jpeg_file in enumerate(jpeg_files, 1):
        output_file = output_dir / jpeg_file.name

        # In incremental mode, skip if output already exists
        if incremental and not args.dry_run and output_file.exists():
            stats["skipped"] += 1
            continue

        result = optimize_image(jpeg_file, output_file, dry_run=args.dry_run)

        if result["status"] == "optimized":
            stats["optimized"] += 1
            stats["total_original_mb"] += result["original_bytes"] / (1024 * 1024)
            stats["total_output_mb"] += result["output_bytes"] / (1024 * 1024)
            pct = result["reduction_pct"]
            print(f"  [{i:4d}/{len(jpeg_files)}] {jpeg_file.name[:50]:50s} "
                  f"{result['original_size']} -> {result['new_size']} "
                  f"({result['output_bytes']//1024}KB, -{pct}%)")
        elif result["status"] == "error":
            stats["errors"] += 1
            print(f"  [{i:4d}/{len(jpeg_files)}] {jpeg_file.name[:50]:50s} ERROR: {result['reason']}")
        elif result["status"] == "would_process":
            stats["optimized"] += 1  # count as would-process
        else:
            stats["skipped"] += 1

    print("-" * 60)
    print("\nSUMMARY:")
    print(f"  Total files:       {stats['total']}")
    print(f"  Optimized:         {stats['optimized']}")
    print(f"  Skipped:           {stats['skipped']}")
    print(f"  Errors:            {stats['errors']}")

    if not args.dry_run and stats["optimized"] > 0:
        print(f"  Original size:     {stats['total_original_mb']:.1f} MB")
        print(f"  Optimized size:    {stats['total_output_mb']:.1f} MB")
        reduction = (1 - stats['total_output_mb'] / stats['total_original_mb']) * 100 if stats['total_original_mb'] > 0 else 0
        print(f"  Total reduction:   {reduction:.1f}%")

    print(f"\nDone. {'DRY RUN - no files written.' if args.dry_run else 'Images saved to: ' + str(output_dir)}")


if __name__ == "__main__":
    main()
