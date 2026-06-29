# tm-t20iii-dev

A clean, peer-reviewable **python-escpos / escpos-printer-db** profile for the
**Epson TM-T20III**, plus hardware probes and docs — with particular focus on
two real problems in the `rr-receipt` app:

1. **`@` and `|` render incorrectly** — root-caused to the international
   character set (`ESC R`), not the code page. See `docs/at-and-pipe.md`.
2. **Bitmaps / emojis / custom glyphs** — three mechanisms (raster image,
   user-defined char, NV logo). See `docs/bitmaps-and-glyphs.md`.

Unlike a guessed profile, the TM-T20III is fully documented: it's in Epson's
ESC/POS code-table matrix and has a public Technical Reference Guide, so the
profile values are documentation-backed.

## Layout

```
profile/   TM-T20III.yml          the deliverable (inherits `default`)
tests/     00_list_usb.py         confirm USB IDs / endpoints (run first)
           01_at_and_pipe.py      ** @ and | diagnostic across ESC R sets **
           02_codepage_matrix.py  which code page renders å ä ö / €
           03_bitmap_emoji.py     raster image() — bitmaps & emoji
           04_user_defined_glyph.py  ESC & — custom glyph at text speed
           05_nv_logo.py          NV logo by key code (GS ( L / FS p)
           06_profile_smoke.py    validate via python-escpos once registered
           conn.py                Usb() primary, raw pyusb fallback
scripts/   build_capabilities.py  make TM-T20III resolvable (the "recompile")
docs/      at-and-pipe.md         root cause + fix for the @/| bug
           bitmaps-and-glyphs.md  emoji/bitmap/glyph options & tradeoffs
           codepages.md           code-page map decisions
           logo.md                NV-graphics findings + log
           hardware.md            this unit's confirmed facts (fill in)
assets/    put emoji/logo PNGs here for tests/03
artifacts/ scans/photos of probe printouts (PR evidence)
```

## Quick start (Windows PC with the printer)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install python-escpos pyusb pillow
python tests\00_list_usb.py          # confirm/fix IDs in tests\conn.py
python tests\01_at_and_pipe.py       # the @/| fix: find the right ESC R set
python tests\02_codepage_matrix.py   # find the right code page for å ä ö
python tests\03_bitmap_emoji.py assets\some_emoji.png
```

Printer must be bound to **WinUSB / libusb-win32 via Zadig** (not Epson APD) so
pyusb can claim it — only one driver can own the device at a time.

## The @/| fix in one line

After `ESC @`, send **`ESC R 0`** (USA international set): `p._raw(b"\x1b\x52\x00")`.
That keeps `@` (0x40) and `|` (0x7C) as plain ASCII. The code page never
controls these — see `docs/at-and-pipe.md` for why.

## Two tracks (keep separate)

1. **Profile PR** (small): the `.yml` carries name/vendor/notes, `codePages`,
   `media.width`, feature flags. Reviewed via `yamllint` + the DB build.
2. **App features** (in rr-receipt): `ESC R 0`, NV logo, raster images,
   user-defined glyphs are print-time commands, not profile fields. The profile
   just advertises `graphics: true`. Probes prototype them here first.

## The "recompile escpos" reality

python-escpos isn't recompiled — it loads a generated `capabilities.json` built
from escpos-printer-db's YAML. Use our profile by regenerating that JSON from a
DB checkout containing `TM-T20III.yml`, or point the library at a custom file
via `ESCPOS_CAPABILITIES_FILE`. See `scripts/build_capabilities.py`.

## Upstream PR checklist

- [ ] Confirm code-page set on hardware (`tests/02`); fix `[VERIFY]` codec names
- [ ] Confirm `media.width.pixels` (512 vs 576)
- [ ] Confirm NV-graphics method (`tests/05`); note in `docs/logo.md`
- [ ] `yamllint profile/TM-T20III.yml` passes
- [ ] Attach probe printout photos from `artifacts/`
- [ ] Open an issue first (per the guide), then PR `TM-T20III.yml`

## References

- Epson Character Code Tables — support matrix + master page list
- Epson ESC/POS Command Reference rev 3.40 — `ESC t`, `ESC R`, `ESC &`,
  `GS ( L`, `FS p`, `GS v 0`
- TM-T20III Technical Reference Guide (Rev. A)
- escpos-printer-db `doc/add-your-printer.md`
