r"""
01_at_and_pipe.py - diagnose the @ (0x40) and | (0x7C) rendering problem.

These two characters live in the COMMON region (0x00-0x7F), so the CODE PAGE
(ESC t) does NOT control them. The INTERNATIONAL CHARACTER SET (ESC R n) does:
several national variants remap 0x40 and/or 0x7C to accented letters or
currency marks. The USA set (ESC R 0) keeps both as plain @ and | .

This probe prints, for each international set 0..15, a line containing the
exact bytes 0x40 and 0x7C (plus the neighbours that national variants also
remap: # $ [ \ ] ^ ` { | } ~ ). Read the paper: the set where @ and | are
BOTH correct is the one to pin in rr-receipt via ESC R.

    python 01_at_and_pipe.py

Expected result: ESC R 0 (USA) is correct. If your printer's memory-switch
default international set is NOT USA, that explains the bug -- fix it either by
sending ESC R 0 at the start of every job, or by changing the memory switch
with the Epson TM-T20III Utility.
"""

from conn import open_printer, writer_for

ESC = 0x1B
GS = 0x1D

# The low-ASCII positions that national variants are known to remap.
PROBE_BYTES = bytes([
    0x23, 0x24, 0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x60,
    0x7B, 0x7C, 0x7D, 0x7E,
])  # # $ @ [ \ ] ^ ` { | } ~

# Epson international set numbers (ESC R n). 0 = USA.
SETS = {
    0: "USA", 1: "France", 2: "Germany", 3: "UK", 4: "Denmark I",
    5: "Sweden", 6: "Italy", 7: "Spain I", 8: "Japan", 9: "Norway",
    10: "Denmark II", 11: "Spain II", 12: "Latin America", 13: "Korea",
    14: "Slovenia/Croatia", 15: "China",
}


def main():
    mode, p = open_printer()
    write = writer_for(mode, p)

    write(bytes([ESC, ord("@")]))                 # initialize
    write(bytes([ESC, ord("t"), 0]))              # code page 0 (PC437) fixed
    write(b"=== @ and | across international sets ===\n")
    write(b"Looking for the row where @ and | are BOTH correct.\n")
    write(b"order: # $ @ [ \\ ] ^ ` { | } ~\n\n")

    for n, label in SETS.items():
        write(bytes([ESC, ord("R"), n]))          # select international set n
        tag = f"R{n:<2} {label:<16} ".encode("ascii", "replace")
        write(tag)
        write(PROBE_BYTES)
        write(b"\n")

    # Reset to USA explicitly and show a clean reference line.
    write(bytes([ESC, ord("R"), 0]))
    write(b"\nUSA reference (should read: # $ @ [ \\ ] ^ ` { | } ~):\n")
    write(PROBE_BYTES)
    write(b"\n")
    write(b"\nNote which Rn row is correct, then pin it in rr-receipt.\n")
    write(b"\n\n\n")
    write(bytes([GS, ord("V"), 66, 0]))           # partial cut

    if mode == "raw":
        p.close()


if __name__ == "__main__":
    main()
