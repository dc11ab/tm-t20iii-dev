# Bitmaps, emojis, and custom glyphs

The TM-T20III is a 1-bit monochrome thermal printer. It has **no Unicode and no
emoji**. But there are three ways to put non-font marks on paper, in increasing
order of "feels like text":

## 1. Raster images — anything, including emoji  (tests/03)

Rasterize any image (emoji PNG, logo, special symbol) to 1-bit and print it via
`GS v 0` / `GS ( L`. python-escpos exposes this as `printer.image(path_or_PIL)`.

- **Pros:** prints literally anything visual; emoji become bitmaps.
- **Cons:** monochrome (needs dithering for photos; flat-color line art and
  emoji print cleanest); slower than text; aligns as a block, not inline with a
  text baseline.
- **Width:** 512 dots at 80mm; keep images ≤ ~384px wide for margins.
- **Emoji how-to:** render the emoji to a small PNG (e.g. 48–64px) with a
  transparent/white background, threshold or Floyd–Steinberg dither to 1-bit,
  then `p.image(img)`. Color emoji become silhouettes — pick emoji that read
  well in pure black/white.

## 2. User-defined characters — custom glyph at text speed  (tests/04)

Define a glyph into a code position with `ESC &`, enable with `ESC % 1`, then
print that byte like normal text. Font A is 12×24.

- **Pros:** prints as fast as text, aligns on the text grid, reusable.
- **Cons:** limited cell size (one character cell); you manage which code points
  hold custom glyphs; lost on power cycle unless re-defined each session.
- **Best for:** a guaranteed-solid `|`, a custom currency mark, a small inline
  symbol, a tiny brand mark beside text.

## 3. NV graphics logo — a stored bitmap by key code  (tests/05)

Register a logo once via the Epson TM-T20III Utility; recall it by key code with
`GS ( L`, or have Receipt Enhancement auto-print it at top/bottom of every
receipt. Best for a fixed shop logo; not for dynamic content.

## Choosing

| Need | Use |
|------|-----|
| Shop logo on every receipt | NV graphics (3), or R/E auto top/bottom |
| One emoji / arbitrary picture | raster image (1) |
| A perfect/bold `\|` or custom symbol inline | user-defined char (2) |
| A euro sign you don't trust in the font | code page 19 (CP858) first; raster (1) as fallback |

## Practical note for rr-receipt

For a TypeScript/node print path, the same three mechanisms exist in
node-escpos (`printImage`, raster commands). The byte sequences and the
"rasterize to 1-bit first" rule are identical; only the API wrapper differs. The
findings here are library-agnostic on purpose.
