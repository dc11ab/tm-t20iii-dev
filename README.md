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
profile values are documentation-backed — and the key ones are now
hardware-confirmed on a real unit.

## Status

Hardware testing is **done**. The profile is **PR-ready** (stops short of the
actual upstream PR — see `docs/pr-readiness.md`).

| Probe | What | Status |
|-------|------|--------|
| `00_list_usb.py` | USB id / endpoints | ✅ 04B8:0E28, EP 0x01/0x82 |
| `01_at_and_pipe.py` | @ / \| fix | ✅ R0 USA; fix = send `ESC R 0` |
| `02_codepage_matrix.py` | code page for åäö / € | ✅ default CP858 |
| `03_bitmap_emoji.py` | raster image / logo | ✅ Viadal logo prints clean |
| `04_user_defined_glyph.py` | `ESC &` custom glyph | not run (not needed) |
| `05_nv_logo.py` | NV stored logo | ⏭️ skipped (issue #7, wontfix) |

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
           conn.py                Usb() primary (profile=None fallback), raw pyusb
scripts/   build_capabilities.py  make TM-T20III resolvable (the "recompile")
docs/      at-and-pipe.md         root cause + fix for the @/| bug
           bitmaps-and-glyphs.md  emoji/bitmap/glyph options & tradeoffs
           codepages.md           code-page map decisions
           logo.md                NV-graphics findings (not pursued)
           hardware.md            this unit's confirmed facts
           pr-readiness.md        upstream submission checklist
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

1. **Profile (this repo → escpos-printer-db PR):** the `.yml` carries
   name/vendor/notes, `media` (width + dpi), `fonts`, and `codePages`. Feature
   support is inherited from `inherits: default` — the profile does **not**
   redeclare a `features` block, matching merged Epson profiles. Reviewed via
   `yamllint` + the DB build. See `docs/pr-readiness.md`.
2. **App features (in rr-receipt):** `ESC R 0`, the code-page selection, NV
   logo, raster images, user-defined glyphs are print-time commands and runtime
   config, **not** profile fields. Tracked in rr-receipt issue #55. Probes here
   prototype them first.

## The "recompile escpos" reality

python-escpos isn't recompiled — it loads a generated `capabilities.json` built
from escpos-printer-db's YAML. Use our profile by regenerating that JSON from a
DB checkout containing `TM-T20III.yml`, or point the library at a custom file
via `ESCPOS_CAPABILITIES_FILE`. See `scripts/build_capabilities.py`. (Until then
`conn.get_escpos()` falls back to `profile=None`, which is confirmed working.)

## Upstream PR

The profile is written to match merged-profile conventions and carries no
unverified codec names. The full readiness checklist, evidence table, and a
ready-to-adapt PR description live in **`docs/pr-readiness.md`**. The two
remaining gates are local: run `yamllint`, and validate against a real
escpos-printer-db build. **The PR itself is intentionally left to do manually.**

## References

- [Epson Character Code Tables](https://download4.epson.biz/sec_pubs/pos/reference_en/charcode/index.html) — support matrix + master page list
- [Epson ESC/POS Command Reference rev 3.40](https://download4.epson.biz/sec_pubs/pos/reference_en/escpos/index.html) — `ESC t`, `ESC R`, `ESC &`,
  `GS ( L`, `FS p`, `GS v 0`
- [TM-T20III Technical Reference Guide (Rev. A)](https://files.support.epson.com/pdf/pos/bulk/tm-t20iii_trg_en_reva.pdf)
- [escpos-printer-db](https://github.com/receipt-print-hq/escpos-printer-db) `doc/add-your-printer.md`
