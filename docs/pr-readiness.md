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

- [ ] Run **yamllint** — see "Gate 1" below.
- [ ] Run the **real escpos-printer-db build** — see "Gate 2" below.
- [ ] Smoke-test via python-escpos (`tests/06_profile_smoke.py`, or set
      `ESCPOS_CAPABILITIES_FILE`): confirm `get_profile("TM-T20III")` resolves
      and Swedish + barcode/QR print.
- [ ] Confirm the vendor-doc link in the profile header still resolves (Epson
      reshuffles URLs; update if it 404s).
- [ ] *(optional)* Edge-measure printable width to confirm 512 vs 576 px.

## Gate 1 — yamllint (quick)

This is the linter the upstream CI runs on every PR. It checks formatting
(indent, line length, trailing spaces, document start/end), not correctness.

```
pip install yamllint
cd tm-t20iii-dev
yamllint profile/TM-T20III.yml
```

No output = pass. If it complains, the message names the rule and line — fix and
re-run. (The repo's own `.yamllint` config is already tuned to match; upstream
applies its own, so a clean run under the stock `default` config is safest.)

## Gate 2 — real escpos-printer-db build

This proves the YAML actually compiles into the shared capabilities file and
that every codec name is recognised (the build **rejects unknown codecs** —
that's the real check on the `codePages` map).

```
# 1. clone the upstream DB and install its build deps
git clone https://github.com/receipt-print-hq/escpos-printer-db
cd escpos-printer-db
pip install -r requirements.txt        # if present; else: pip install pyyaml jsonschema

# 2. drop our profile in alongside the others
cp ../tm-t20iii-dev/profile/TM-T20III.yml data/profile/

# 3. run the build. There is NO Makefile — it's a Python script under scripts/.
#    List the dir and run the generator (name may be e.g. generate.py / build.py):
ls scripts/
python scripts/<the-build-script>.py

# 4. confirm our profile made it into the generated output (written to dist/)
grep -c "TM-T20III" dist/capabilities.json
```

A successful build writes `dist/capabilities.json` (and `dist/capabilities.yml`)
with a `TM-T20III` entry and **no error** about an unknown code page / codec. If
a codec name is rejected, that page is the problem — drop it or correct the name
against the DB's codec table, then rebuild.

### Optional: use the freshly built file with python-escpos

To exercise the real profile end-to-end before the PR, point python-escpos at
the file you just built (no reinstall needed):

```
# Windows PowerShell
$env:ESCPOS_CAPABILITIES_FILE = "C:\path\to\escpos-printer-db\dist\capabilities.json"
python tests\06_profile_smoke.py
# unset afterwards:  Remove-Item Env:\ESCPOS_CAPABILITIES_FILE
```

```
# Linux/macOS
export ESCPOS_CAPABILITIES_FILE=/path/to/escpos-printer-db/dist/capabilities.json
python tests/06_profile_smoke.py
unset ESCPOS_CAPABILITIES_FILE
```

`scripts/build_capabilities.py` in this repo also automates copying a built
`capabilities.json` into an installed python-escpos (with `--install` /
`--restore`) if you'd rather not use the env var.

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
