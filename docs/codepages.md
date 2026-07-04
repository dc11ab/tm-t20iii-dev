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

**The shipped profile lists 37 of the 43 pages.** Every codec name is
validated against escpos-printer-db's authoritative `data/encoding.yml`
(the DB build rejects unknown names -- its assertion caught our original
`ISO8859_2` spelling; canonical is `ISO_8859-2`). Six pages are deliberately
omitted:

| Omitted | Epson name | Why |
|--------:|------------|-----|
| 11 | PC851 Greek | exists in encoding.yml but marked *"Not used, due to inconsistencies between implementations"* |
| 20/21/26 | Thai Character Code 42/11/18 | Epson-custom layouts; no encoding.yml mapping (would need custom `data:` char-map blocks) |
| 42/43 | PC1118/PC1119 Lithuanian | no encoding.yml mapping; related Baltic pages exist but equivalence unverified |

Notable canonical names (differ from obvious guesses): Vietnamese 30/31 =
`TCVN-3-1`/`TCVN-3-2`, Kazakh 53 = `RK1048` (Epson calls it KZ-1048; same
ST RK 1048 standard), Farsi 41 = `CP1098`. Full resolution history: issue #11.

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

## Width: 576 dots

The TM-T20III's printable width is **576 dots / 72 mm** at 203 dpi (Font A
48 cols x 12 dots = Font B 64 x 9 = 576; ruler-confirmed on paper by
`tests/07`). An early profile draft said 512 -- corrected. Affects
`media.width.pixels` and full-width raster images.
