# Hardware facts — this specific TM-T20III

Fill in from the probes and the printer self-test.

## USB identity (tests/00_list_usb.py)

```
idVendor:    0x04b8 (expected)
idProduct:   0x____   (conn.py provisional 0x0e03 — confirm)
OUT endpoint: 0x__
IN endpoint:  0x__
Zadig driver: [ ] WinUSB  [ ] libusb-win32  [ ] other
```

## Self-test (power on holding Feed)

```
Product name:
Firmware version:
Resident fonts:
Default code table:
Default international set:   <-- if this is NOT USA, it explains the @/| bug
```

## @ and | (tests/01_at_and_pipe.py)  ** primary issue **

```
International set where @ AND | are both correct:  R__  (______)
Was the printer's default set already USA?         [ ] yes  [ ] no
Fix applied: [ ] send ESC R 0 per job  [ ] changed memory-switch default to USA
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
