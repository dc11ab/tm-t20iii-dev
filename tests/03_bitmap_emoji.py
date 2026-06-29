"""
03_bitmap_emoji.py - print bitmaps / emojis / glyphs as raster images.

The TM-T20III has no Unicode or emoji concept -- it's a 1-bit thermal printer.
But it prints arbitrary MONOCHROME RASTER images via GS v 0 / GS ( L, which
python-escpos exposes as printer.image(). So "print an emoji" = rasterize the
emoji to 1-bit and send it as a bitmap.

This probe:
  1. prints a small generated test bitmap (a checker + a bold pipe bar), proving
     the raster path works and giving you a clean | you can trust absolutely;
  2. if Pillow + an image file are available, prints that image too
     (point IMAGE_PATH at an emoji PNG or your logo).

    python 03_bitmap_emoji.py [path-to-image.png]

Notes:
  * Monochrome only. For grayscale/photographic art, python-escpos can dither
    (impl="bitImageRaster" with Floyd-Steinberg via Pillow) -- flat-color
    emoji/line art print cleanest.
  * Width budget: 512 dots at 80mm. Keep images <= ~384px wide for margins.
  * This is the robust fallback for ANY glyph the font can't render: euro,
    special symbols, or a guaranteed-correct | .
"""

import sys
from conn import get_escpos


def make_test_bitmap():
    """Generate a tiny 1-bit test image without needing an asset file."""
    from PIL import Image, ImageDraw
    w, h = 240, 80
    img = Image.new("1", (w, h), 1)  # white
    d = ImageDraw.Draw(img)
    # checker block
    for y in range(0, 40, 8):
        for x in range(0, 80, 8):
            if (x // 8 + y // 8) % 2 == 0:
                d.rectangle([x, y, x + 7, y + 7], fill=0)
    # a bold, unmistakable pipe bar (3px wide) + label area
    d.rectangle([120, 5, 123, 75], fill=0)          # the "perfect pipe"
    d.text((140, 30), "PIPE^", fill=0)
    return img


def main():
    p = get_escpos()
    p.set(align="center")
    p.text("bitmap / emoji / glyph test\n\n")

    p.set(align="left")
    p.text("1) generated 1-bit test bitmap:\n")
    try:
        from PIL import Image  # noqa: F401
        img = make_test_bitmap()
        p.image(img)
    except ImportError:
        p.text("   (Pillow not installed: pip install pillow)\n")

    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        p.text(f"\n2) your image: {path}\n")
        try:
            p.image(path)
        except Exception as exc:  # noqa: BLE001
            p.text(f"   image() failed: {exc}\n")
    else:
        p.text("\n2) (pass an emoji PNG path as arg to test a real glyph)\n")

    p.text("\nMonochrome raster prints anything the font can't.\n")
    p.text("\n\n\n")
    p.cut()


if __name__ == "__main__":
    main()
