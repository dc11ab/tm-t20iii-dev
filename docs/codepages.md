# Code pages — TM-T20III

## Authoritative set

The TM-T20III **is** in Epson's *Character Code Tables* support matrix
(rev 2.40). For "Other models" (non-South-Asia) the supported set is:

```
0–5, 11–21, 26, 30–53, 255   (43 entries)
```

The TM-T20III Technical Reference Guide independently confirms "43 pages
including the user-defined page," default **PC437 (page 0)**, default
international set **USA**. (South Asia models drop page 255; this profile targets
"Other models.")

So unlike a guessed profile, the code-page count and default are
documentation-backed.

## Integer → encoding map

The profile maps each Epson page number to the escpos-printer-db codec name.
The pages relevant to Swedish receipts:

| Page | Epson name        | DB codec | Note |
|-----:|-------------------|----------|------|
| 0    | PC437 USA/Std Eur | CP437    | power-on default; å ä ö present at DOS positions |
| 2    | PC850 Multilingual| CP850    | Latin-1 DOS |
| 5    | PC865 Nordic      | CP865    | Nordic |
| 16   | WPC1252           | CP1252   | Windows-1252 |
| 19   | PC858 Euro        | CP858    | CP850 + € (use if you print euro) |

Entries flagged `[VERIFY]` in the YAML (Thai pages 20/21/26, Vietnamese 30/31,
Farsi 41, Lithuanian 42/43, Kazakh 53) have codec names that may not match
escpos-printer-db's exact strings. The DB build validation rejects unknown
names — fix against the DB's codec table before the PR rather than guessing.

## Recommended default for rr-receipt

**Page 16 (CP1252)** if source strings are UTF-8/Windows text — clean transcode,
least surprising. **Page 19 (CP858)** if you print €. Confirm on paper with
`tests/02_codepage_matrix.py`; trust the printout over this table.

## Important: code pages do NOT fix @ or |

Those are low-ASCII and governed by `ESC R` (international set), not `ESC t`.
See `docs/at-and-pipe.md`. Don't chase the @/| bug through code pages.

## Width: 512 vs 576

T20-class 80mm is 512 dots. Affects `media.width.pixels` and full-width raster
images. Confirm via a printable-area test if you print edge-to-edge bitmaps.
