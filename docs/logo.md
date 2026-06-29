# Built-in logo (NV graphics / Receipt Enhancement) — TM-T20III

The T20III TRG documents all of this directly (no guessing needed):

- **NV Graphics Memory** — logos registered via the **Epson TM-T20III Utility**,
  recalled by key code at print time.
- **Receipt Enhancement (R/E)** — *auto* top/bottom logo printing configured by
  memory switch (Software Setting Mode shows: Auto top logo, Auto bottom logo,
  and extended settings for when each fires — on power-on, on cover close, etc).
- **NV Graphics Information Print Mode** — self-test → Feed ×1 → hold; prints
  capacity and the key codes of every stored graphic.

## Commands (issued from rr-receipt at print time, not from the profile)

- `GS ( L` function 69 — print stored graphics by key code (current).
- `FS p n m` — print NV bit image by index (obsolete; often still honoured).

`tests/05_nv_logo.py` fires both; record which works.

## Procedure

1. Install the Epson **TM-T20III Utility** (Windows).
2. Register a monochrome logo to NV graphics with a known key code.
3. Run **NV Graphics Information** print mode; confirm the key code. Photograph
   into `artifacts/`.
4. Put that key code in `tests/05_nv_logo.py`; run it.

## Findings (fill in from hardware)

```
Date:
Firmware version (self-test):
NV graphics present?         [ ] yes  [ ] no
Stored key code(s):
GS ( L (fn 69) printed logo?  [ ] yes  [ ] no
FS p printed logo?            [ ] yes  [ ] no
R/E auto top/bottom logo?     [ ] yes  [ ] no
Notes:
```
