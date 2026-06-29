# Upstream PR readiness — escpos-printer-db

Everything needed to submit `profile/TM-T20III.yml` to
[receipt-print-hq/escpos-printer-db](https://github.com/receipt-print-hq/escpos-printer-db).
**This repo stops here — the PR itself is done manually, later.**

## Status: READY (pending two local checks)

The profile is written to match the conventions of merged Epson profiles
(compared against `data/profile/TM-T88III.yml`): vendor-doc link comment,
quoted vendor, folded `notes`, `media` with `dpi`, a `fonts` section, and a
trimmed `codePages` map with only unambiguous codec names. No `[VERIFY]`
placeholders remain.

## Evidence backing the profile (all on hardware)

| Claim | Probe | Result |
|-------|-------|--------|
| USB id 04B8:0E28 | `00_list_usb.py` | confirmed |
| @ / \| need ESC R 0 (USA) | `01_at_and_pipe.py` | R0 USA correct; mechanism confirmed |
| Code pages 0/2/5/16/19 render åäö | `02_codepage_matrix.py` | confirmed; CP858 also prints € |
| Raster image() (logo/bitmap) | `03_bitmap_emoji.py` | confirmed (Viadal logo + test bitmap) |
| Media width 512 px @ 80mm | `03` (logo fit) | adequate; not edge-measured |

See `docs/hardware.md` for the detail and `artifacts/` for the printout photos.

## Do-before-PR checklist

- [ ] **Run yamllint locally** (the upstream CI gate we couldn't run offline):
      ```
      pip install yamllint
      yamllint profile/TM-T20III.yml
      ```
      Fix any complaints (line length, indentation, trailing spaces).
- [ ] **Validate against the real DB build.** Clone escpos-printer-db, drop the
      file in `data/profile/`, run its build/generate step, and confirm it emits
      `capabilities.json` without rejecting any codec name:
      ```
      git clone https://github.com/receipt-print-hq/escpos-printer-db
      cp profile/TM-T20III.yml escpos-printer-db/data/profile/
      cd escpos-printer-db && make    # or the generate step in its README
      ```
- [ ] **Smoke-test via python-escpos** with the regenerated capabilities
      (`tests/06_profile_smoke.py`, or set `ESCPOS_CAPABILITIES_FILE`). Confirm
      `get_profile("TM-T20III")` resolves and Swedish + barcode/QR print.
- [ ] **Confirm the vendor-doc link** in the profile header resolves to a real
      TM-T20III page (Epson reshuffles these URLs; update if it 404s).
- [ ] *(optional)* Edge-measure printable width to confirm 512 vs 576 px.

## How to submit (when ready — not done here)

1. Per `doc/add-your-printer.md`, the maintainers prefer you **open an issue
   first** with the printer info + test-page evidence, then PR the profile.
2. Fork escpos-printer-db, add `data/profile/TM-T20III.yml`, open the PR.
3. The PR must pass yamllint + the automated build and a contributor review.
4. Attach/link the hardware evidence (the `artifacts/` photos, this repo).

## Suggested PR description (copy/adapt)

> Adds a profile for the Epson TM-T20III (80mm thermal). Code-page set per the
> Epson ESC/POS Character Code Tables matrix ("Other models" group); pages 0,
> 2, 5, 16 and 19 verified on hardware (Swedish åäö correct, CP858 prints €).
> Feature support inherits `default`, consistent with sibling TM-T88III. Only
> code pages with an unambiguous codec mapping are listed; the printer supports
> additional pages (Thai/Vietnamese/etc.) not included here.

## What intentionally stays OUT of the profile

- **`ESC R 0` (international set / the @ \| fix)** — this is a runtime command,
  not a profile field. It belongs in the consuming app (rr-receipt #55), not
  the capabilities DB.
- **NV-logo commands** — not modelled by escpos-printer-db; `graphics: true`
  (from `default`) is all the DB carries. See `docs/logo.md` (#7, wontfix).
- **The trimmed exotic code pages** — re-add individually only with a verified
  escpos-printer-db codec name.
