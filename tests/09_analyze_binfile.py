r"""
09_analyze_binfile.py - static ESC/POS stream analyzer for .bin files.

Walks a binary ESC/POS job (e.g. the escpos-php test files cached by
tests/08 in assets/escpos-php-bin/) WITHOUT a printer, decoding each command
it recognizes -- with full header decode for the raster/graphics commands,
which is what you need to diagnose width-related garbling:

  GS ( L / GS 8 L  fn 112  -> declared image W x H in DOTS
  GS v 0           (obsolete raster)  -> W bytes*8 x H dots
  ESC *            (column image)     -> W dots

    python 09_analyze_binfile.py ..\assets\escpos-php-bin\receipt-with-logo.bin
    python 09_analyze_binfile.py ..\assets\escpos-php-bin\graphics.bin

Compare declared widths against this unit's printable width (576 dots).
A raster wider than the print area is clipped by some Epson firmwares but
REJECTED as a parameter error by others -- in which case the whole data
block is interpreted as text and prints as garbage until the stream
re-syncs (the receipt-with-logo.bin symptom).
"""

import os
import sys

MAX_WIDTH = 576  # this unit's printable width in dots


def dle_scan(payload, where):
    """Real-time cmd sequences inside a data block desync some Epson
    firmwares (the TRG warns against embedding DLE EOT/ENQ/DC4 in graphics
    data): the printer consumes them mid-payload, its byte count shifts,
    and the rest of the block spills out as text garbage."""
    hits = {"DLE EOT (10 04)": payload.count(b"\x10\x04"),
            "DLE ENQ (10 05)": payload.count(b"\x10\x05"),
            "DLE DC4 (10 14)": payload.count(b"\x10\x14")}
    total = sum(hits.values())
    if total:
        detail = ", ".join(f"{k} x{v}" for k, v in hits.items() if v)
        print(f"        !! {total} real-time DLE sequence(s) inside "
              f"{where} payload: {detail}")
        print("        !! these can be executed mid-block and desync the "
              "raster byte count -> garble")
    else:
        print(f"        DLE scan of {where} payload: clean "
              "(no 10 04 / 10 05 / 10 14)")


def u16(b, i):
    return b[i] | (b[i + 1] << 8)


def printable(run):
    txt = run.decode("cp437", "replace")
    return txt if len(txt) <= 48 else txt[:45] + "..."


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    data = open(path, "rb").read()
    print(f"{os.path.basename(path)}: {len(data)} bytes\n")

    i, n = 0, len(data)
    warnings = []
    while i < n:
        b = data[i]

        # ---- text runs & whitespace -------------------------------------
        if b == 0x0A:
            j = i
            while j < n and data[j] == 0x0A:
                j += 1
            print(f"{i:6}  LF x{j - i}")
            i = j
            continue
        if 0x20 <= b <= 0xFF and b not in (0x1B, 0x1D, 0x1C):
            j = i
            while j < n and 0x20 <= data[j] <= 0xFF and \
                    data[j] not in (0x1B, 0x1D, 0x1C):
                j += 1
            print(f"{i:6}  text[{j - i:4}] \"{printable(data[i:j])}\"")
            i = j
            continue

        # ---- ESC family --------------------------------------------------
        if b == 0x1B and i + 1 < n:
            c = data[i + 1]
            if c == 0x40:
                print(f"{i:6}  ESC @        initialize")
                i += 2
                continue
            if c in (0x61, 0x45, 0x4D, 0x74, 0x52, 0x21, 0x2D, 0x33,
                     0x4A, 0x64, 0x47):
                name = {0x61: "ESC a  justification", 0x45: "ESC E  bold",
                        0x4D: "ESC M  font", 0x74: "ESC t  code page",
                        0x52: "ESC R  intl set", 0x21: "ESC !  print mode",
                        0x2D: "ESC -  underline", 0x33: "ESC 3  line spacing",
                        0x4A: "ESC J  feed n dots", 0x64: "ESC d  feed n lines",
                        0x47: "ESC G  double-strike"}[c]
                print(f"{i:6}  {name} = {data[i + 2] if i + 2 < n else '?'}")
                i += 3
                continue
            if c == 0x32:
                print(f"{i:6}  ESC 2        default line spacing")
                i += 2
                continue
            if c == 0x70 and i + 4 < n:
                print(f"{i:6}  ESC p        drawer pulse "
                      f"(m={data[i+2]} t1={data[i+3]} t2={data[i+4]})")
                i += 5
                continue
            if c == 0x2A and i + 3 < n:          # ESC * m nL nH
                m = data[i + 2]
                w = u16(data, i + 3)
                bpc = 3 if m in (32, 33) else 1
                total = w * bpc
                flag = "  <-- WIDER than printable!" if w > MAX_WIDTH else ""
                print(f"{i:6}  ESC * m={m}  column image W={w} dots "
                      f"({total} data bytes){flag}")
                i += 5 + total
                continue
            warnings.append(i)
            print(f"{i:6}  ESC 0x{c:02X}     (unknown -- skipping 2)")
            i += 2
            continue

        # ---- GS family ----------------------------------------------------
        if b == 0x1D and i + 1 < n:
            c = data[i + 1]
            if c == 0x28 and i + 2 < n and data[i + 2] == 0x4C:  # GS ( L
                plen = u16(data, i + 3)
                m, fn = data[i + 5], data[i + 6]
                if fn == 0x70 and plen >= 10:    # fn 112: store raster
                    a = data[i + 7]
                    bx, by, ctone = data[i + 8], data[i + 9], data[i + 10]
                    w = u16(data, i + 11)
                    h = u16(data, i + 13)
                    flag = ("  <-- WIDER than printable "
                            f"({MAX_WIDTH})!" if w * bx > MAX_WIDTH else "")
                    print(f"{i:6}  GS ( L fn112 store raster: "
                          f"W={w} x H={h} dots, scale {bx}x{by}, "
                          f"tone={ctone}, payload={plen - 10}B{flag}")
                    dle_scan(data[i + 15:i + 5 + plen], "fn112")
                elif fn == 0x32:
                    print(f"{i:6}  GS ( L fn50  print stored raster")
                else:
                    print(f"{i:6}  GS ( L fn{fn} (m={m}, len={plen})")
                i += 5 + plen
                continue
            if c == 0x38 and i + 2 < n and data[i + 2] == 0x4C:  # GS 8 L
                plen = (data[i + 3] | data[i + 4] << 8 |
                        data[i + 5] << 16 | data[i + 6] << 24)
                fn = data[i + 8]
                if fn == 0x70:
                    w = u16(data, i + 13)
                    h = u16(data, i + 15)
                    flag = ("  <-- WIDER than printable "
                            f"({MAX_WIDTH})!" if w > MAX_WIDTH else "")
                    print(f"{i:6}  GS 8 L fn112 store raster (large): "
                          f"W={w} x H={h} dots, payload={plen - 10}B{flag}")
                else:
                    print(f"{i:6}  GS 8 L fn{fn} (len={plen})")
                i += 7 + plen
                continue
            if c == 0x76 and i + 3 < n and data[i + 2] == 0x30:  # GS v 0
                m = data[i + 3]
                wb = u16(data, i + 4)
                h = u16(data, i + 6)
                w = wb * 8
                flag = "  <-- WIDER than printable!" if w > MAX_WIDTH else ""
                print(f"{i:6}  GS v 0 m={m}  raster W={w} dots x H={h} "
                      f"({wb * h} data bytes){flag}")
                dle_scan(data[i + 8:i + 8 + wb * h], "GS v 0")
                i += 8 + wb * h
                continue
            if c == 0x21:
                print(f"{i:6}  GS !         char size = 0x{data[i + 2]:02X}")
                i += 3
                continue
            if c in (0x68, 0x77, 0x48, 0x66):
                name = {0x68: "GS h  barcode height",
                        0x77: "GS w  barcode module width",
                        0x48: "GS H  HRI position",
                        0x66: "GS f  HRI font"}[c]
                print(f"{i:6}  {name} = {data[i + 2]}")
                i += 3
                continue
            if c == 0x6B:                        # GS k
                m = data[i + 2]
                if m <= 6:                       # function A: NUL-terminated
                    j = i + 3
                    while j < n and data[j] != 0:
                        j += 1
                    print(f"{i:6}  GS k (fn A) m={m} "
                          f"data=\"{printable(data[i + 3:j])}\"")
                    i = j + 1
                else:                            # function B: length byte
                    ln = data[i + 3]
                    print(f"{i:6}  GS k (fn B) m={m} len={ln} "
                          f"data=\"{printable(data[i + 4:i + 4 + ln])}\"")
                    i += 4 + ln
                continue
            if c == 0x28 and i + 2 < n and data[i + 2] == 0x6B:  # GS ( k
                plen = u16(data, i + 3)
                cn, fn = data[i + 5], data[i + 6]
                print(f"{i:6}  GS ( k cn={cn} fn={fn} len={plen} "
                      f"(2D code: QR/PDF417)")
                i += 5 + plen
                continue
            if c == 0x56:                        # GS V cut
                m = data[i + 2]
                extra = 1 if m in (65, 66) else 0
                print(f"{i:6}  GS V         cut (m={m}"
                      f"{', n=' + str(data[i + 3]) if extra else ''})")
                i += 3 + extra
                continue
            if c == 0x42:
                print(f"{i:6}  GS B         reverse = {data[i + 2]}")
                i += 3
                continue
            if c == 0x4C:
                print(f"{i:6}  GS L         left margin = {u16(data, i + 2)}")
                i += 4
                continue
            if c == 0x57:
                print(f"{i:6}  GS W         print width = {u16(data, i + 2)}")
                i += 4
                continue
            warnings.append(i)
            print(f"{i:6}  GS 0x{c:02X}      (unknown -- skipping 2)")
            i += 2
            continue

        # ---- FS / other ----------------------------------------------------
        warnings.append(i)
        print(f"{i:6}  0x{b:02X}         (unknown byte -- skipping)")
        i += 1

    if warnings:
        print(f"\nNOTE: {len(warnings)} unknown byte(s)/command(s) -- "
              "offsets may have desynced after the first one; treat "
              "everything after offset {} with suspicion.".format(warnings[0]))


if __name__ == "__main__":
    main()
