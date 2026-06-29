# Hardware facts — this specific TM-T20III

Fill in from the probes and the printer self-test.

## USB identity (tests/00_list_usb.py)

```
idVendor:    0x04b8 (Seiko Epson)
idProduct:   0x0e28   (confirmed via Zadig + 00_list_usb.py)
OUT endpoint: 0x01
IN endpoint:  0x82
Zadig driver: [x] WinUSB  [ ] libusb-win32  [ ] other
```

## Self-test (power on holding Feed)

```
Product name:
Firmware version:
Resident fonts:
Default code table:
Default international set:   <-- TODO: run self-test. If this is NOT USA, it
                                explains why rr-receipt saw broken @/|.
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

Was the printer's default set already USA?   [ ] yes  [ ] no  (TODO: self-test)
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
Paper width: [ ] 80mm  [ ] 58mm
Columns (Font A): __
media.width.pixels: [ ] 512  [ ] 576
```

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
[ ] Profile edited — changes:
```
