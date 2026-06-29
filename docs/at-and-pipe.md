# The @ and | problem — root cause and fix

## TL;DR

`@` (0x40) and `|` (0x7C) are **low-ASCII** characters in the common 0x00–0x7F
region. The **code page** (`ESC t`) does *not* control them. The **international
character set** (`ESC R n`) does. Pin the international set to **USA**
(`ESC R 0`) and both render correctly. This is almost certainly your bug.

## Why it happens

ESC/POS layers two independent selections over the character map:

1. **Code page** (`ESC t n`) — controls the high region **0x80–0xFF** only.
   Swedish å ä ö live here. This is what most people reach for, but it has *no
   effect* on @ or |.
2. **International character set** (`ESC R n`) — a holdover from national-variant
   ASCII. It remaps about a dozen positions in the **0x00–0x7F** region,
   including exactly the troublesome ones:

   | byte | USA (R0) | remapped in some national sets |
   |------|----------|--------------------------------|
   | 0x23 | `#`      | `£` (UK) |
   | 0x24 | `$`      | `¤` |
   | 0x40 | `@`      | `§`, `É`, `à` (various) |
   | 0x5B | `[`      | `Ä`, `°`, `¡` |
   | 0x5C | `\`      | `Ö`, `Ñ`, `¥` |
   | 0x5D | `]`      | `Å`, `é`, `¿` |
   | 0x7C | `\|`     | `ò`, `ñ`, `ø`, accented (various) |
   | 0x7E | `~`      | `à`, `¨` |

   In the **USA** set, every one of these keeps its plain ASCII glyph. The
   moment the active set is, say, Sweden or Germany, `@` and/or `|` mutate.

So if rr-receipt (or the printer's memory-switch default) has a non-USA
international set active, `@` and `|` break while everything else looks fine —
exactly the confusing, "only these two characters" symptom.

## The fix (three layers, most robust last)

1. **Pin USA at job start.** Send `ESC R 0` (bytes `1B 52 00`) right after
   `ESC @`. In python-escpos: `p._raw(b"\x1b\x52\x00")` before printing, or use
   a profile/charcode path that doesn't disturb `ESC R`.
2. **Fix the memory-switch default.** Use the Epson TM-T20III Utility to set the
   default international character set to USA, so it survives power cycles even
   if a job forgets to send `ESC R`.
3. **Guaranteed glyph fallback.** If a specific head/font still renders `|` too
   faintly (it's a thin 1-dot vertical), define a bold user-defined `|` with
   `ESC &` (see `tests/04_user_defined_glyph.py`) or print it as a tiny raster
   bitmap. This makes the glyph independent of font and national set entirely.

## Verify on hardware

`tests/01_at_and_pipe.py` sweeps `ESC R 0..15` and prints @ | and neighbours
for each, so you can read off which set is correct on your unit. Record the
result in `docs/hardware.md`.

## rr-receipt action item

At the start of every print job, after initialise, send `ESC R 0`. Treat it as
non-optional boilerplate alongside `ESC @`. Then `@` and `|` are correct
regardless of whatever the printer's saved default happens to be.
