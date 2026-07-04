r"""
10_fn112_matrix.py - isolate the receipt-with-logo.bin garble.

Facts so far (tests/09 + generator sources):
  * receipt-with-logo.bin garbles its logo: GS ( L fn112, W=300 x H=236,
    payload 8,968 B, printed with ESC a 1 (CENTER) active.
  * graphics.bin prints fine: same fn112, W=125 x H=148, 2,368 B, LEFT.
  * demo.bin (marked OK) contains FOUR of the big 300x236 fn112 blocks,
    printed LEFT-justified -- check the demo photo: 8 logos, all clean?

This probe varies one factor at a time. Each case prints a banner, then a
synthetic raster (border + X diagonals + tick marks -- unmistakable whether
clean or garbled), then pauses so you can note the result.

  case 1  LEFT   fn112  300x236 (8,968 B)   <- big payload alone
  case 2  CENTER fn112  300x236 (8,968 B)   <- exact receipt-with-logo combo
  case 3  CENTER fn112  125x148 (2,368 B)   <- small payload + center
  case 4  LEFT   GS v 0 300x236             <- same image, older raster cmd

Interpretation:
  1 garbles           -> payload-size limit on fn112 (bisect later)
  only 2 garbles      -> fn112 + centered justification firmware bug
  3 garbles           -> centering + fn112 in general
  4 garbles           -> not command-specific at all (would be surprising;
                         GS v 0 is python-escpos's default and proven)

    python 10_fn112_matrix.py
"""

from conn import RawUsb

ESC = 0x1B
GS = 0x1D


def make_raster(w, h):
    """1-bit test pattern: border, X diagonals, ticks. Returns packed rows."""
    from PIL import Image, ImageDraw
    img = Image.new("1", (w, h), 1)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=0, width=3)
    d.line([0, 0, w - 1, h - 1], fill=0, width=3)
    d.line([0, h - 1, w - 1, 0], fill=0, width=3)
    for x in range(0, w, 50):
        d.line([x, 0, x, 12], fill=0, width=2)
    d.text((10, h // 2 - 6), f"{w}x{h}", fill=0)
    row_bytes = (w + 7) // 8
    px = img.load()
    out = bytearray()
    for y in range(h):
        for xb in range(row_bytes):
            b = 0
            for bit in range(8):
                x = xb * 8 + bit
                if x < w and px[x, y] == 0:
                    b |= 1 << (7 - bit)
            out.append(b)
    return bytes(out), row_bytes


def fn112(p, w, h, data):
    """GS ( L store raster (fn 112) + print (fn 50), exactly as escpos-php."""
    payload = (bytes([48, 112, 48, 1, 1, 49]) +          # m fn a bx by c
               bytes([w & 0xFF, w >> 8, h & 0xFF, h >> 8]) + data)
    p.write(bytes([GS, ord("("), ord("L"),
                   len(payload) & 0xFF, len(payload) >> 8]) + payload)
    p.write(bytes([GS, ord("("), ord("L"), 2, 0, 48, 50]))   # fn 50: print


def gsv0(p, w, h, data, row_bytes):
    p.write(bytes([GS, ord("v"), ord("0"), 0,
                   row_bytes & 0xFF, row_bytes >> 8,
                   h & 0xFF, h >> 8]) + data)


def banner(p, text):
    p.write(bytes([ESC, ord("@")]))
    p.write(bytes([ESC, ord("R"), 0]))
    p.write(bytes([GS, ord("!"), 0x11]))
    p.write(text.encode("ascii") + b"\n")
    p.write(bytes([GS, ord("!"), 0x00]))
    p.write(b"-" * 42 + b"\n")


def main():
    big, big_rb = make_raster(300, 236)
    small, _ = make_raster(125, 148)
    print(f"big payload: {len(big)} B (expect 8968), "
          f"small: {len(small)} B (expect 2368)")

    cases = [
        ("case 1: LEFT fn112 300x236", 0,
         lambda p: fn112(p, 300, 236, big)),
        ("case 2: CENTER fn112 300x236", 1,
         lambda p: fn112(p, 300, 236, big)),
        ("case 3: CENTER fn112 125x148", 1,
         lambda p: fn112(p, 125, 148, small)),
        ("case 4: LEFT GS v 0 300x236", 0,
         lambda p: gsv0(p, 300, 236, big, big_rb)),
    ]

    p = RawUsb()
    for i, (label, justify, send) in enumerate(cases, 1):
        print(f"[{i}/4] {label}")
        banner(p, label)
        p.write(bytes([ESC, ord("a"), justify]))
        send(p)
        p.write(bytes([ESC, ord("a"), 0]))
        p.write(b"\n\n\n\n")
        p.write(bytes([GS, ord("V"), 66, 0]))
        if i < len(cases):
            input("  note the result, Enter for next: ")
    p.close()
    print("\nRecord which cases were clean vs garbled in docs/hardware.md.")


if __name__ == "__main__":
    main()
