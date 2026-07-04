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
profile values are documentation-backed — and the key ones are
hardware-confirmed on a real unit.

## Context

The Epson TM-T20III is a compact, monochrome thermal receipt printer. It utilizes direct thermal printing technology, which eliminates the need for ink or toner, producing high-quality text and graphics at speeds up to 200mm per second. The printer is known for its reliability and ease of integration, offering various connectivity options including USB, serial, parallel, and Ethernet interfaces (depending upon model).

**The TM-T20III supports standard width of 80mm roll paper**. It also features an adjustable paper guide that allows it to accommodate 58mm paper rolls. The printer includes an auto-cutter function to separate receipts and typically supports roll diameters up to 83mm, ensuring extended operation without frequent paper changes.

## Development status

Core hardware findings are **done**. Two evidence prints remain before the
upstream PR (see `docs/pr-readiness.md`), which is left to do manually.

| Probe | What | Status |
|-------|------|--------|
| `00_list_usb.py` | USB id / endpoints | ✅ 04B8:0E28, EP 0x01/0x82 |
| `01_at_and_pipe.py` | @ / \| fix | ✅ R0 USA; fix = send `ESC R 0` |
| `02_codepage_matrix.py` | code page for åäö / € | ✅ default CP858 |
| `03_bitmap_emoji.py` | raster image / logo | ✅ Logo png prints clean |
| `04_user_defined_glyph.py` | `ESC &` custom glyph | not run (not needed) |
| `05_nv_logo.py` | NV stored logo | ⏭️ skipped (issue #7, wontfix) |
| `07_capabilities_print.py` | self-test-style evidence page + 512/576 ruler | ⏳ pending run |
| `08_escpos_php_binfiles.py` | escpos-php `.bin` feature files (upstream ask) | ⏳ pending run |

## Printer specification (Epson TM-T20III)

**Identity & interfaces**

- Epson TM-T20III, 80 mm direct-thermal receipt printer, ESC/POS
- This unit: **USB** (`04B8:0E28`), bound to **WinUSB** via Zadig for pyusb
- Model family: built-in USB 2.0 Type B on all variants, plus RS-232 serial
  (model 011) **or** 10/100 Ethernet (model 012); regional parallel/Wi-Fi
  variants exist; drawer kick-out (DK) port on all
- Data buffer 4 KB (or 45 B, switchable)

**Printing**

- Thermal line printing, **203 × 203 dpi**, max **250 mm/s**
- Printable width **72 mm ≈ 576 dots** on 80 mm paper (58 mm mode available
  via roll guide + memory switch)
- Fonts: **A** 12×24 (48 columns), **B** 9×17 (64 columns); 95 alphanumeric
  characters, 18 international sets, 43 code pages incl. user-defined page 255
- Barcodes (per TRG): UPC-A/E, EAN13/8, CODE39, ITF, CODABAR, CODE93,
  CODE128, GS1-128, GS1 DataBar; 2D: QR, PDF417, MaxiCode, composite
- Hardware-confirmed here: `ESC R 0` for @/|, CP858 for åäö + €, raster
  images — see Status table and `docs/hardware.md`

**Reliability (vendor figures)**

- Autocutter 1.5 M cuts · print head 150 km · MTBF 360,000 h

## Paper specification

**Printer requirements (Epson)**

- Roll width 79.5 ± 0.5 mm (80 mm nominal) · max roll diameter 83 mm

**Tested stock — the only paper used for all probes**

- DoubleDragon.co.uk *80mm Premium Thermal POS Rolls*, SKU **`20-80-80`**
  (nominal 80 mm × 80 mm)
- Our empirical measurements (35 ruler-measured receipts, roll-geometry
  calibration): thickness **≈ 92 µm**; usable length **≈ 36–44 m per roll** —
  well below the "80 m" often assumed for 80×80 rolls
- Practical yield in our race workload: ≈ 3 full "Print All" runs per roll

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
           07_capabilities_print.py  self-test-style evidence page + rulers
           08_escpos_php_binfiles.py escpos-php .bin files, one per pause
           conn.py                Usb() primary (profile=None fallback), raw pyusb
scripts/   build_capabilities.py  make TM-T20III resolvable (the "recompile")
docs/      at-and-pipe.md         root cause + fix for the @/| bug
           bitmaps-and-glyphs.md  emoji/bitmap/glyph options & tradeoffs
           codepages.md           code-page map decisions
           logo.md                NV-graphics findings (not pursued)
           hardware.md            this unit's confirmed facts + result sheets
           pr-readiness.md        upstream submission checklist
assets/    put emoji/logo PNGs here for tests/03
           escpos-php-bin/        tests/08 download cache (gitignored)
artifacts/ scans/photos of probe printouts (PR evidence)
```

## Quick start (Windows PC with the printer)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install python-escpos pyusb pillow
python tests\00_list_usb.py          # confirm/fix IDs in tests\conn.py
python tests\01_at_and_pipe.py       # the @/| fix: find the right ESC R set
python tests\02_codepage_matrix.py   # find the right code page for å ä ö
python tests\07_capabilities_print.py   # one-page capabilities evidence sheet
python tests\08_escpos_php_binfiles.py  # escpos-php feature files (upstream ask)
```

Printer must be bound to **WinUSB / libusb-win32 via [Zadig](https://github.com/pbatard/libwdi/releases/)** (not Epson APD) so
pyusb can claim it — only one driver can own the device at a time on Windows 11.

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
ready-to-adapt PR description live in **`docs/pr-readiness.md`**. Remaining
gates: `yamllint`, a real escpos-printer-db build, and the two evidence prints
(tests/07 + tests/08). **The PR itself is intentionally left to do manually.**

## License

MIT (see [`LICENSE`](LICENSE)) — chosen to match python-escpos and to be
permissively compatible with escpos-printer-db's CC BY 4.0, so the profile can
be incorporated upstream without friction.

## References

- [Epson TM-T20III product/spec pages](https://epson.com/For-Work/Printers/POS/TM-T20III-Thermal-Receipt-Printer/p/C31CH51A9972) — 203 dpi, 250 mm/s, interfaces
- [Epson Character Code Tables](https://download4.epson.biz/sec_pubs/pos/reference_en/charcode/index.html) — support matrix + master page list
- [Epson ESC/POS Command Reference rev 3.40](https://download4.epson.biz/sec_pubs/pos/reference_en/escpos/index.html) — `ESC t`, `ESC R`, `ESC &`,
  `GS ( L`, `FS p`, `GS v 0`
- [TM-T20III Technical Reference Guide (Rev. A)](https://files.support.epson.com/pdf/pos/bulk/tm-t20iii_trg_en_reva.pdf)
- [escpos-printer-db](https://github.com/receipt-print-hq/escpos-printer-db) `doc/add-your-printer.md`
- [escpos-php test files](https://github.com/mike42/escpos-php/tree/master/test/integration/resources/output) — the `.bin` set tests/08 streams
