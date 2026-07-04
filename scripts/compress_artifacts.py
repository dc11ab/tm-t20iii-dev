#!/usr/bin/env python3
"""
compress_artifacts.py - recompress evidence photos in artifacts/ in place.

Receipt photos straight off a phone are 4-6 MB each; that bloats the repo
without adding legibility (the print itself is only 576 dots wide, so a
2800 px long edge still captures it at ~5x the printer's own resolution).

Default: long edge 2800 px, JPEG quality 85, EXIF orientation baked in,
all other EXIF (including GPS location!) stripped. Files whose long edge is
already <= the target are skipped, so re-runs are idempotent.

    python scripts/compress_artifacts.py                # defaults
    python scripts/compress_artifacts.py --edge 3200 --quality 90
    python scripts/compress_artifacts.py --dry-run      # report only
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(HERE, os.pardir, "artifacts")
EXTS = (".jpg", ".jpeg")


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--edge", type=int, default=2800,
                    help="max long-edge pixels (default 2800)")
    ap.add_argument("--quality", type=int, default=85,
                    help="JPEG quality (default 85)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would happen, change nothing")
    args = ap.parse_args()

    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit("Pillow required: pip install pillow")

    files = sorted(f for f in os.listdir(ARTIFACTS)
                   if f.lower().endswith(EXTS))
    if not files:
        sys.exit(f"No jpegs found in {ARTIFACTS}")

    total_before = total_after = 0
    for name in files:
        path = os.path.join(ARTIFACTS, name)
        before = os.path.getsize(path)
        with Image.open(path) as im:
            gps = "GPS" if 34853 in (im.getexif() or {}) else "-"
            im = ImageOps.exif_transpose(im)      # bake orientation
            w0, h0 = im.size
            if max(w0, h0) <= args.edge:
                print(f"  skip {name:<48} {human(before):>8}  "
                      f"({w0}x{h0}, already <= {args.edge}px, exif:{gps})")
                total_before += before
                total_after += before
                continue
            im.thumbnail((args.edge, args.edge), Image.LANCZOS)
            w1, h1 = im.size
            if not args.dry_run:
                im = im.convert("RGB")
                im.save(path, "JPEG", quality=args.quality, optimize=True)
        after = os.path.getsize(path)
        total_before += before
        total_after += after
        tag = "would " if args.dry_run else ""
        print(f"  {tag}compress {name:<40} {human(before):>8} -> "
              f"{human(after):>8}  ({w0}x{h0} -> {w1}x{h1}, exif:{gps})")

    print(f"\ntotal: {human(total_before)} -> {human(total_after)}")
    if args.dry_run:
        print("(dry run - nothing written)")
    else:
        print("EXIF (incl. any GPS) stripped; orientation baked in.")


if __name__ == "__main__":
    main()
