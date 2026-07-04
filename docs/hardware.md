# Hardware facts — this specific TM-T20III

Fill in from the probes and the printer self-test.

## USB identity (tests/00_list_usb.py)

```
idVendor:     0x04b8   (Seiko Epson)
idProduct:    0x0e28   (confirmed via Zadig + 00_list_usb.py)
OUT endpoint: 0x01
IN endpoint:  0x82
Zadig driver: [x] WinUSB  [ ] libusb-win32  [ ] other
```

## Self-test (power on holding Feed)

```
Product name: TM-T20III
Firmware version: 15.05 ESC/POS, Main 15.05
Buffer capacity: 4K bytes
Resident character: Alphanumeric
Default international set: not reported on the TM-T20III self-test printout.
  Moot for rr-receipt: every job pins ESC R 0 right after ESC @, so the
  power-on default never matters. To determine it empirically anyway:
  power-cycle, temporarily comment the ESC R line in tests/07 init(), run 07
  and read the ASCII rows -- whatever glyphs appear at 0x40/0x7C reveal the
  default set.
```

## @ and | (tests/01_at_and_pipe.py)  ** primary issue — RESOLVED **

```
International set where @ AND | are both correct:  R0  (USA)
  Other "clean ASCII" rows that also keep @ and |: R3 UK, R8 Japan,
  R13 Korea, R15 China — but each alters the #/$ slot (UK #->£,
  Japan/China $->¥), so R0 USA is the only fully-correct row.
  Non-USA Western sets (R1 France, R2 Germany, R5 Sweden, R7/R11 Spain,
  R4/R10 Denmark, R9 Norway, ...) remap 0x40/0x7C -> accented/currency.

Mechanism confirmed: code page was held fixed during the test; @ and |
changed purely with ESC R. So ESC R (international set), not ESC t
(code page), governs these characters. See docs/at-and-pipe.md.

Was the printer's default set already USA?   [ ] yes  [ ] no
  (the self-test doesn't report it -- see Self-test section for the optional
  empirical check; moot since ESC R 0 is pinned per job)
Fix applied: [x] send ESC R 0 (1B 52 00) per job after ESC @
             [ ] changed memory-switch default to USA (optional, via Utility)
```

## Code pages (tests/02_codepage_matrix.py)  ** RESOLVED **

```
Page rendering å ä ö correctly:  0 (CP437), 2 (CP850), 5 (CP865), 19 (CP858)
                                 all render "Smorgas åäö ÅÄÖ" correctly from
                                 the DOS byte positions.
  Page 16 (CP1252): DOS-bytes line is garbage (expected); the 1252-bytes line
    reads "Smörgås åäö ÅÄÖ" correctly (correct when text is CP1252-encoded).
  Page 18 (CP852): å/Å slot becomes ć/Ć — NOT suitable for Swedish.
  Page 45 (CP1250): DOS-bytes garbage (Windows codepage, expected).

Chosen rr-receipt default page:  19 (CP858)
  Rationale: renders å ä ö correctly AND carries € at 0xD5 in the same page.
  CP1252 (page 16) is the equally-valid alternative for UTF-8/Windows source
  text; kept selectable (see configurable code page, below).

Euro sign OK on page 19?         [x] yes  (euro(0xD5) printed € correctly)
```

## Configurable code page (rr-receipt)

```
Default:        CP858 (Epson page 19)
Override via:   [ ] CLI flag        (e.g. --codepage CP858 / --codepage CP1252)
                [ ] Admin-UI setting (printer settings -> code page dropdown)
Allowed values: CP858, CP1252, CP850, CP865, CP437  (all confirmed to render
                Swedish; CP858/CP1252 also carry €)
Status:         decided; implementation pending in rr-receipt repo (issue #55).
```

## Bitmaps / glyphs (tests/03, tests/04)  ** RASTER RESOLVED **

```
Raster image() printed test bitmap?   [x] yes  (checker + bold pipe bar clean)
Real PNG printed acceptably?          [x] yes  (Viadal_Ultra_Horizontal.png —
                                       wordmark + foot line-art printed sharp,
                                       no banding/garbage; via profile=None +
                                       impl="bitImageRaster")
User-defined bold | (ESC &) worked?   [ ] not tested (probe 04 not run; not
                                       needed — raster path covers logo/glyphs,
                                       and the ESC R 0 fix already gives a
                                       correct resident |)

Note: very fine hairline strokes in the foot logo are near the 203 dpi 1-bit
limit; printed fine here, watch on worn heads / low density. Wordmark has ample
margin. Confirms the decision to skip NV-stored logo (issue #7) — the raster
path rr-receipt already uses produces a good result.
```

## Media width

```
Paper width: [x] 80mm  [ ] 58mm (58mm supported but not tested)
Columns (Font A): 48
media.width.pixels: [ ] 512  [x] 576   <-- settle with the tests/07 rulers

Spec arithmetic says 576: Font A 48 cols x 12 dots = 576; Font B 64 x 9 = 576;
576 / 203 dpi = 72.06 mm = the documented 72 mm printable width. Profile
corrected to pixels: 576 + dpi: 203 on this basis; the tests/07 ruler pair
(512 and 576) verifies it on paper -- tick the box above when printed.
```

## Capabilities print (tests/07) -- one-page evidence sheet

```
Printed OK end-to-end?    [x] yes  [ ] no
GS I identity readable?   [ ] yes (firmware: ______, model: ______)  [ ] no
1D symbologies printed:   [x] UPC-A  [x] UPC-E  [x] EAN13  [x] EAN8
                          [x] CODE39 [x] ITF    [x] CODABAR
                          [x] CODE93 [x] CODE128
QR printed?               [x] yes  [ ] no
512-dot ruler:            [x] clean
576-dot ruler:            [x] clean & wider than 512 (=> 576 confirmed)
                          [ ] wrapped/garbled (=> width is 512; revert profile)
Photo in artifacts/?      [x] yes
```

## escpos-php test files (tests/08) -- upstream evidence requirement

add-your-printer.md: "For testing out features, you can send escpos-php test
files to your printer and note the output for each file." Run
`tests/08_escpos_php_binfiles.py` and note each file below (add rows as the
upstream set grows; the probe lists the current set via the GitHub API).

```
File                          Result                Notes
----------------------------  --------------------  -----------------------
barcode.bin                   [x] OK
bit-image.bin                 [x] OK
character-encodings.bin       [x] OK
character-tables.bin          [x] OK
demo.bin                      [x] OK
graphics.bin                  [x] OK                Not reached, but worked on retest
margins-and-spacing.bin       [x] OK
pdf417-code.bin               [x] OK
qr-code.bin                   [x] OK
receipt-with-logo.bin         [x] FAIL        Garbled logo, text-string at end visible
text-size.bin                 [x] OK
unifont-print-buffer.bin      [x] OK
TM-T20III self-test           [x] OK

Upstream ships 12 .bin files (verified via the GitHub API, 2026-07-04). The
first run printed exactly the first five in sort order, then nothing --
including files whose features tests/07 already proved on this unit (QR,
text sizes). Hypothesis: a graphics block with a declared byte-length
swallowed all subsequent bytes (banners included) as raster payload, so the
later silences are artifacts of ONE bad stream, not per-file failures.

Retest: power-cycle the printer, then run each remaining file in its own
session (files are already cached in assets/escpos-php-bin/):
    python 08_escpos_php_binfiles.py --only text-size
    python 08_escpos_php_binfiles.py --only qr-code
    python 08_escpos_php_binfiles.py --only pdf417
    python 08_escpos_php_binfiles.py --only margins
    python 08_escpos_php_binfiles.py --only unifont
    python 08_escpos_php_binfiles.py --only receipt-with-logo
    python 08_escpos_php_binfiles.py --only graphics    <- LAST; power-cycle after
Mark results above; only a file that stays silent when run ALONE after a
fresh power-cycle is a genuine FAIL.
```

Photos of each file's output go in `artifacts/`.

## NV logo (tests/05, docs/logo.md)  ** NOT PURSUED — see issue #7 (wontfix) **

```
Decision: skip NV-stored logo. rr-receipt prints the logo as a raster image
(printer.image, impl="bitImageRaster") every receipt — confirmed good above.
NV path would only save streaming time but needs the Epson Utility + a driver
swap off WinUSB. Probe tests/05_nv_logo.py + how-to retained for future use.
```

## Outcome

```
[ ] Profile matches hardware as written
[x] Profile edited — changes:
    - media.dpi 180 -> 203 (Epson datasheet + TRG; 180 was a TM-T88III
      convention artifact)
    - media.width.pixels 512 -> 576 (Font A 48x12 = Font B 64x9 = 576 dots
      = 72 mm @ 203 dpi; verify on paper via the tests/07 ruler pair)
```
