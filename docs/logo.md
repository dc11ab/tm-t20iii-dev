# Built-in logo (NV graphics / Receipt Enhancement) — TM-T20III

> **Status: NOT PURSUED (decided 2026-06-29).** rr-receipt prints the Viadal
> logo reliably as a raster image on every receipt
> (`receipt_encoder._print_logo()` → `printer.image(..., impl="bitImageRaster")`),
> which is fast enough for this use case. The NV-stored-logo path would only
> save per-receipt bitmap-streaming time, at the cost of installing the Epson
> TM-T20III Utility and a Zadig/Device-Manager driver swap (the Utility needs
> the Epson driver, not WinUSB). Not worth it. See issue #7 (closed wontfix).
> The probe and how-to below are kept in case we ever want the speed-up later.

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

## Procedure (if revisited)

1. Install the Epson **TM-T20III Utility** (Windows).
2. Register a monochrome logo to NV graphics with a known key code.
3. Run **NV Graphics Information** print mode; confirm the key code. Photograph
   into `artifacts/`.
4. Put that key code in `tests/05_nv_logo.py`; run it.

## Findings

```
Status: not tested — NV-logo path not pursued (see banner above).
Logo on receipts is handled by raster image() in rr-receipt instead.
```
