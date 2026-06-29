# Code pages — TM-T20III

## Authoritative set vs. what the profile ships

The TM-T20III **is** in Epson's *Character Code Tables* support matrix
(rev 2.40). For "Other models" (non-South-Asia) the documented set is:

```
0–5, 11–21, 26, 30–53, 255   (43 pages, per the TRG: "43 pages including the
                              user-defined page")
```

Default **PC437 (page 0)**, default international set **USA**. (South Asia
models drop page 255; this profile targets "Other models.")

**The shipped profile deliberately lists fewer than 43 pages (27).** Matching
the convention of merged Epson profiles (e.g. TM-T88III, which lists ~12), it
includes only pages whose escpos-printer-db **codec name is unambiguous**. The
exotic pages — Thai (20/21/26), Vietnamese (30/31), Farsi (41), Lithuanian
(42/43), Kazakh (53) — were dropped rather than shipped with guessed codec
names, because the DB's build validation rejects unknown codecs and a clean PR
shouldn't carry unverified mappings. The profile `notes` records that the
printer supports more pages than are listed.

## Integer → encoding map (the Swedish-relevant pages)

| Page | Epson name        | DB codec | Note |
|-----:|-------------------|----------|------|
| 0    | PC437 USA/Std Eur | CP437    | power-on default; å ä ö at DOS positions |
| 2    | PC850 Multilingual| CP850    | Latin-1 DOS |
| 5    | PC865 Nordic      | CP865    | Nordic |
| 16   | WPC1252           | CP1252   | Windows-1252 |
| 19   | PC858 Euro        | CP858    | CP850 + € (use if you print euro) |

Pages **0, 2, 5, 16, 19 are hardware-confirmed** on a real unit via
`tests/02_codepage_matrix.py` (see `docs/hardware.md`): all render
`Smorgas åäö ÅÄÖ` correctly, and page 19 also prints € at 0xD5.

## Chosen default: CP858 (page 19)

Renders å ä ö correctly **and** carries € in the same page. CP1252 (page 16) is
the equally-valid alternative for UTF-8/Windows source text. Both are kept
selectable in rr-receipt — see rr-receipt issue #55 (configurable code page,
default CP858).

## Important: code pages do NOT fix @ or |

Those are low-ASCII and governed by `ESC R` (international set), not `ESC t`.
See `docs/at-and-pipe.md`. Don't chase the @/| bug through code pages.

## Width: 512 vs 576

T20-class 80mm is 512 dots — confirmed adequate for the Viadal logo raster
(`tests/03`). Affects `media.width.pixels` and full-width raster images.
