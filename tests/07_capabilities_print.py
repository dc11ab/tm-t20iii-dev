r"""
07_capabilities_print.py - one-page self-test-style capabilities print.

Prints a single ">>> PRINT TEST <<<" receipt in the style of a printer
self-test page (cf. the evidence photos on escpos-printer-db PRs, e.g. #102):
identity block, font & style demos, an ASCII table, the profile's code-page
list with hardware samples, all nine GS k 1D barcode symbologies, a QR code,
and 512/576-dot width rulers that settle media.width.pixels on paper.

    python 07_capabilities_print.py

Photograph the output into artifacts/ -- it is the one-page evidence sheet
for the upstream escpos-printer-db submission (docs/pr-readiness.md).

Also best-effort reads the printer ID / firmware via GS I over the IN
endpoint; results go to the console and onto the receipt when readable.

Note: the printer's own BUILT-IN self-test (power on while holding FEED) is
separate evidence -- it reports firmware and the default international set.
Run both.
"""

import os
import re

from conn import RawUsb

ESC = 0x1B
GS = 0x1D

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE_YML = os.path.join(HERE, os.pardir, "profile", "TM-T20III.yml")

SWE_DOS = bytes([0x53, 0x6D, 0x6F, 0x72, 0x67, 0x61, 0x73, 0x20,
                 0x86, 0x84, 0x94, 0x20, 0x8F, 0x8E, 0x99])
SWE_1252 = "Sm\u00f6rg\u00e5s \u00e5\u00e4\u00f6 \u00c5\u00c4\u00d6".encode("cp1252")
EURO_858 = bytes([0xD5])

# GS k function-B symbology ids the TM-T20III TRG documents.
BARCODES = [
    (65, "01234567890", "UPC-A"),
    (66, "0123456", "UPC-E"),
    (67, "471234567890", "EAN13"),
    (68, "9031101", "EAN8"),
    (69, "TM-T20III", "CODE39"),
    (70, "1234567890", "ITF"),
    (71, "A123456A", "CODABAR"),
    (72, "TM-T20III", "CODE93"),
    (73, "{BViadal Ultra", "CODE128"),
]


def w(p, *chunks):
    for c in chunks:
        p.write(c if isinstance(c, bytes) else c.encode("ascii", "replace"))


def init(p):
    w(p, bytes([ESC, ord("@")]))           # initialise
    w(p, bytes([ESC, ord("R"), 0]))        # USA international set (@ | correct)
    w(p, bytes([ESC, ord("t"), 0]))        # baseline code page 0 (PC437)


def title(p, text):
    w(p, bytes([ESC, ord("a"), 1]))
    w(p, bytes([GS, ord("!"), 0x11]))
    w(p, text + "\n")
    w(p, bytes([GS, ord("!"), 0x00]))
    w(p, bytes([ESC, ord("a"), 0]))


def heading(p, text):
    w(p, "\n", bytes([ESC, ord("E"), 1]), text + "\n",
      bytes([ESC, ord("E"), 0]))


def kv(p, key, val):
    w(p, f"{key:<12}: {val}\n")


def read_gs_i(p, n):
    """Best-effort GS I query. Returns cleaned bytes or None."""
    try:
        p.write(bytes([GS, ord("I"), n]))
        data = p.read(length=64, timeout=500)
        return bytes(data).strip(b"_\x00\r\n") if data else None
    except Exception:  # noqa: BLE001  (timeouts are expected, not errors)
        return None


def profile_codepages():
    """Parse the codePages map from our own profile YAML (no deps)."""
    pages = []
    try:
        with open(PROFILE_YML, encoding="utf-8") as f:
            in_cp = False
            for line in f:
                if re.match(r"^\s*codePages:\s*$", line):
                    in_cp = True
                    continue
                if in_cp:
                    m = re.match(r"^\s+(\d+):\s*(\S+)", line)
                    if m:
                        pages.append((int(m.group(1)), m.group(2)))
                    else:
                        break
    except OSError:
        pass
    return pages


def barcode(p, m, data, label):
    w(p, bytes([GS, ord("h"), 64]))        # height 64 dots
    w(p, bytes([GS, ord("w"), 2]))         # module width 2
    w(p, bytes([GS, ord("H"), 2]))         # HRI below
    payload = data.encode("ascii")
    w(p, bytes([GS, ord("k"), m, len(payload)]), payload)
    w(p, "\n" + label + "\n\n")


def qr(p, data):
    d = data.encode("ascii")

    def gsk(payload):
        w(p, bytes([GS, ord("("), ord("k"),
                    len(payload) & 0xFF, len(payload) >> 8]), payload)

    gsk(bytes([49, 65, 50, 0]))            # fn 165: model 2
    gsk(bytes([49, 67, 6]))                # fn 167: module size 6
    gsk(bytes([49, 69, 49]))               # fn 169: EC level M
    gsk(bytes([49, 80, 48]) + d)           # fn 180: store data
    gsk(bytes([49, 81, 48]))               # fn 181: print


def ruler(p, width):
    """Print a width-px raster ruler via GS v 0 (needs Pillow)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        w(p, f"(Pillow missing -- {width}px ruler skipped)\n")
        return
    hpx = 40
    img = Image.new("1", (width, hpx), 1)
    d = ImageDraw.Draw(img)
    d.rectangle([0, hpx - 10, width - 1, hpx - 1], fill=0)   # solid base bar
    for x in range(0, width, 64):
        d.line([x, 0, x, hpx - 1], fill=0)                   # tick every 64 px
        d.text((min(x + 2, width - 30), 2), str(x), fill=0)
    d.line([width - 1, 0, width - 1, hpx - 1], fill=0)       # end tick
    row_bytes = width // 8
    px = img.load()
    out = bytearray()
    for y in range(hpx):
        for xb in range(row_bytes):
            b = 0
            for bit in range(8):
                if px[xb * 8 + bit, y] == 0:                 # PIL '1': 0=black
                    b |= 1 << (7 - bit)
            out.append(b)
    w(p, bytes([GS, ord("v"), ord("0"), 0,
                row_bytes & 0xFF, row_bytes >> 8,
                hpx & 0xFF, hpx >> 8]), bytes(out))
    w(p, f"^ {width}-dot ruler (ticks every 64)\n\n")


def main():
    p = RawUsb()

    # identity over the IN endpoint, best-effort, before any printing
    fw = read_gs_i(p, 65)
    model = read_gs_i(p, 67)
    print("GS I firmware:", fw or "(no response)")
    print("GS I model:   ", model or "(no response)")

    init(p)
    title(p, ">>> PRINT TEST <<<")
    w(p, "\n")

    kv(p, "PRINT MODEL", model.decode("ascii", "replace")
       if model else "Epson TM-T20III")
    if fw:
        kv(p, "FIRMWARE", fw.decode("ascii", "replace"))
    kv(p, "INSTRUCTION", "ESC/POS")
    kv(p, "INTERFACE", "USB 2.0 (04B8:0E28, WinUSB)")
    kv(p, "PRINT WIDTH", "80mm paper / 72mm printable")
    kv(p, "RESOLUTION", "203 x 203 dpi")
    kv(p, "PRINT SPEED", "max 250 mm/s")
    kv(p, "FONT A", "12x24, 48 columns")
    kv(p, "FONT B", "9x17, 64 columns")
    kv(p, "BARCODE 1D", "UPC-A/E EAN13/8 CODE39 ITF")
    kv(p, "", "CODABAR CODE93 CODE128")
    kv(p, "BARCODE 2D", "QR (PDF417/MaxiCode per TRG)")

    heading(p, "FONT & STYLE")
    w(p, "Font A: The quick brown fox 0123456789\n")
    w(p, bytes([ESC, ord("M"), 1]),
      "Font B: The quick brown fox 0123456789\n",
      bytes([ESC, ord("M"), 0]))
    w(p, bytes([ESC, ord("E"), 1]), "bold ", bytes([ESC, ord("E"), 0]),
      bytes([ESC, ord("-"), 1]), "underline ", bytes([ESC, ord("-"), 0]),
      bytes([GS, ord("B"), 1]), " reverse ", bytes([GS, ord("B"), 0]), "\n")
    w(p, bytes([GS, ord("!"), 0x11]), "2x size ",
      bytes([GS, ord("!"), 0x22]), "3x",
      bytes([GS, ord("!"), 0x00]), "\n")

    heading(p, "ASCII 0x20-0x7E (ESC R 0)")
    w(p, bytes(range(0x20, 0x40)), "\n")
    w(p, bytes(range(0x40, 0x60)), "\n")
    w(p, bytes(range(0x60, 0x7F)), "\n")

    heading(p, "CODE PAGES (profile)")
    pages = profile_codepages()
    kv(p, "COUNT", f"{len(pages)} listed (43 in printer)")
    kv(p, "DEFAULT", "0 (PC437); rr-receipt uses 19 (CP858)")
    line = ""
    for n, name in pages:
        tok = f"{n}:{name} "
        if len(line) + len(tok) > 46:
            w(p, line.rstrip() + "\n")
            line = ""
        line += tok
    if line:
        w(p, line.rstrip() + "\n")

    heading(p, "HW SAMPLES (Swedish + euro)")
    for n in (0, 2, 5, 19):
        w(p, bytes([ESC, ord("t"), n]), f"p{n:<3} ", SWE_DOS, b"\n")
    w(p, bytes([ESC, ord("t"), 16]), "p16  ", SWE_1252, b"\n")
    w(p, bytes([ESC, ord("t"), 19]), "p19  euro(0xD5): ", EURO_858, b"\n")
    w(p, bytes([ESC, ord("t"), 0]))

    heading(p, "1D BARCODES (GS k)")
    for m, data, label in BARCODES:
        try:
            barcode(p, m, data, label)
        except Exception as exc:  # noqa: BLE001
            w(p, f"{label}: send failed ({exc})\n")

    heading(p, "QR")
    w(p, bytes([ESC, ord("a"), 1]))
    qr(p, "https://github.com/dc11ab/tm-t20iii-dev")
    w(p, bytes([ESC, ord("a"), 0]), "\n")

    heading(p, "WIDTH RULERS (512 vs 576)")
    ruler(p, 512)
    ruler(p, 576)
    w(p, "576 clean & wider than 512 -> pixels: 576 OK\n")
    w(p, "576 wrapped/garbled        -> width is 512\n")

    w(p, "\n")
    title(p, "*** completed ***")
    w(p, "\n\n\n\n")
    w(p, bytes([GS, ord("V"), 66, 0]))
    p.close()

    print("Done. Photograph into artifacts/, fill docs/hardware.md.")
    print("Also run the BUILT-IN self-test: power on while holding FEED")
    print("(reports firmware + default international set).")


if __name__ == "__main__":
    main()
