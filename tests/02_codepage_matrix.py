"""
02_codepage_matrix.py - which code page renders high-byte chars (åäö, €) right.

Complements 01: where 01 covers the COMMON region (@ |), this covers the
0x80-0xFF region governed by ESC t (the code page). For each candidate page it
prints the page number, the high-byte row, and a Swedish test line.

    python 02_codepage_matrix.py

Whichever page makes the Swedish line correct on YOUR T20III is the page to
default to in rr-receipt. International set is pinned to USA throughout so it
doesn't confound the high-byte test.
"""

from conn import open_printer, writer_for

ESC = 0x1B
GS = 0x1D

CANDIDATES = [0, 2, 5, 16, 19, 18, 45]
NAMES = {0: "CP437", 2: "CP850", 5: "CP865", 16: "CP1252",
         19: "CP858", 18: "CP852", 45: "CP1250"}

# Swedish letters at DOS positions (CP437/850/858/865):
# 0x86 å  0x84 ä  0x94 ö  0x8F Å  0x8E Ä  0x99 Ö
SWE_DOS = bytes([0x53, 0x6D, 0x6F, 0x72, 0x67, 0x61, 0x73, 0x20,
                 0x86, 0x84, 0x94, 0x20, 0x8F, 0x8E, 0x99])
SWE_1252 = "Smörgås åäö ÅÄÖ".encode("cp1252")
EURO_858 = bytes([0xD5])  # € is at 0xD5 in CP858


def hi_row(write):
    for base in range(0x80, 0x100, 32):
        write(bytes(range(base, base + 32)))
        write(b"\n")


def main():
    mode, p = open_printer()
    write = writer_for(mode, p)

    write(bytes([ESC, ord("@")]))
    write(bytes([ESC, ord("R"), 0]))   # USA international set, fixed
    write(b"=== code page matrix (high bytes) ===\n\n")

    for n in CANDIDATES:
        write(bytes([ESC, ord("t"), n]))
        write(f"--- page {n} ({NAMES.get(n, '?')}) ---\n".encode("ascii", "replace"))
        hi_row(write)
        write(b"DOS-bytes : ")
        write(SWE_DOS)
        write(b"\n")
        if n == 16:
            write(b"1252-bytes: ")
            write(SWE_1252)
            write(b"\n")
        if n == 19:
            write(b"euro(0xD5): ")
            write(EURO_858)
            write(b"\n")
        write(b"\n")

    write(b"=== end ===\n\n\n\n")
    write(bytes([GS, ord("V"), 66, 0]))
    if mode == "raw":
        p.close()


if __name__ == "__main__":
    main()
