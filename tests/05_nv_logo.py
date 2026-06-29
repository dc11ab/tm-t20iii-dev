"""
05_nv_logo.py - print a logo stored in the printer's NV graphics memory.

The T20III TRG confirms NV Graphics Memory and Receipt Enhancement (auto
top/bottom logo). A logo is registered via the Epson TM-T20III Utility
(Windows) with a key code, then recalled at print time -- no per-receipt
bitmap streaming.

BEFORE running: register a logo with the TM-T20III Utility and confirm its key
code via the printer's NV Graphics Information print mode
(self-test -> Feed x1 -> hold). Put the key code below.

    python 05_nv_logo.py

Tries both command generations; record which works in docs/logo.md.
"""

from conn import open_printer, writer_for

ESC = 0x1B
GS = 0x1D
FS = 0x1C

KEY1, KEY2 = ord("1"), ord("1")   # GS ( L key code (set to YOUR registered code)
NV_INDEX = 1                       # FS p image index (obsolete command)


def gs_paren_l(write, kc1, kc2):
    m, fn, x, y = 48, 69, 1, 1
    payload = bytes([fn, kc1, kc2, x, y])
    write(bytes([GS, ord("("), ord("L"), len(payload) + 1, 0, m]) + payload)


def fs_p(write, n, mode=0):
    write(bytes([FS, ord("p"), n, mode]))


def main():
    mode, p = open_printer()
    write = writer_for(mode, p)
    write(bytes([ESC, ord("@")]))
    write(b"NV logo test\n\n[1] GS ( L by key code:\n")
    try:
        gs_paren_l(write, KEY1, KEY2)
    except Exception as exc:  # noqa: BLE001
        write(f"  GS ( L raised: {exc}\n".encode("ascii", "replace"))
    write(b"\n[2] FS p by index:\n")
    try:
        fs_p(write, NV_INDEX)
    except Exception as exc:  # noqa: BLE001
        write(f"  FS p raised: {exc}\n".encode("ascii", "replace"))
    write(b"\nNote which method printed the logo.\n\n\n\n")
    write(bytes([GS, ord("V"), 66, 0]))
    if mode == "raw":
        p.close()


if __name__ == "__main__":
    main()
