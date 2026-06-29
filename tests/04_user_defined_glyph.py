"""
04_user_defined_glyph.py - bake a custom glyph with ESC & (text-speed glyphs).

Alternative to bitmaps when you want a custom/guaranteed glyph that prints as
FAST as normal text and aligns on the text grid: define a user-defined
character into a code position with ESC & , enable user-defined chars with
ESC % 1, then just print that byte.

Use cases:
  * a guaranteed-solid | even if the font's pipe is too thin on your head,
  * a custom currency/symbol mark,
  * a tiny logo mark inline with text.

This probe defines a bold vertical bar into code 0x7C itself (so a literal '|'
in your text renders as the strong custom bar), prints a before/after compare,
then restores the resident font.

    python 04_user_defined_glyph.py

Font A on the T20III is 12x24. ESC & sends, per character, a width byte then
(width * bytes-per-column) column bytes, 3 bytes/column for a 24-dot height.
"""

from conn import open_printer, writer_for

ESC = 0x1B
GS = 0x1D


def define_bold_pipe(write, code=0x7C, width=12):
    """Define a thick vertical bar centred in a width x 24 cell at `code`."""
    # 24-dot height => 3 bytes per column (MSB top). A solid column = 0xFF*3.
    # Make a 4-px-wide bar centred in the 12-px cell: columns 4..7 solid.
    cols = []
    for x in range(width):
        if 4 <= x <= 7:
            cols += [0xFF, 0xFF, 0xFF]   # full-height solid
        else:
            cols += [0x00, 0x00, 0x00]   # blank
    # ESC & y c1 c2 [width d1..dk] ...
    # y = bytes per column (3), c1=c2=code (single char range)
    header = bytes([ESC, ord("&"), 3, code, code, width])
    write(header + bytes(cols))


def main():
    mode, p = open_printer()
    write = writer_for(mode, p)

    write(bytes([ESC, ord("@")]))
    write(bytes([ESC, ord("R"), 0]))          # USA, so resident | is normal
    write(b"user-defined glyph test\n\n")

    write(b"resident pipe:  a|b|c|d\n")

    define_bold_pipe(write, code=0x7C)
    write(bytes([ESC, ord("%"), 1]))          # enable user-defined char set
    write(b"custom pipe:    a|b|c|d\n")

    write(bytes([ESC, ord("%"), 0]))          # back to resident font
    write(b"resident again: a|b|c|d\n")

    write(b"\nUse ESC % 1 only around the glyphs you want customised.\n")
    write(b"\n\n\n")
    write(bytes([GS, ord("V"), 66, 0]))
    if mode == "raw":
        p.close()


if __name__ == "__main__":
    main()
