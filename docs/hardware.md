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

## Code pages (tests/02_codepage_matrix.py)

```
Page rendering å ä ö correctly:  ____  (encoding ______)
Chosen rr-receipt default page:  ____
Euro sign OK on page 19?         [ ] yes  [ ] no
```

## Bitmaps / glyphs (tests/03, tests/04)

```
Raster image() printed test bitmap?   [ ] yes  [ ] no
Emoji PNG printed acceptably?         [ ] yes  [ ] no
User-defined bold | (ESC &) worked?   [ ] yes  [ ] no
```

## Media width

```
Paper width: [ ] 80mm  [ ] 58mm
Columns (Font A): __
media.width.pixels: [ ] 512  [ ] 576
```

## NV logo (tests/05, docs/logo.md)

```
NV graphics present?  [ ] yes  [ ] no
Working method:       [ ] GS ( L  [ ] FS p  [ ] R/E auto  [ ] none
```

## Outcome

```
[ ] Profile matches hardware as written
[ ] Profile edited — changes:
```
