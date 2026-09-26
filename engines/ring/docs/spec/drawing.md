# Drawing: screen, image draw types, puzzles (Ring, DVD)

Evidence: E-0036. Addresses are `RING_DVD.EXE`.

## Screen

640×480, 16 bits per pixel (`spec/boot.md`). The game view is the 640×448 band between
y = 16 and y = 464: puzzle backgrounds are declared at (0, 16) (`PuzAddBgrImg(…, 0, 16,
…)` in every set-up), and each frame fills the rows 0..15 and 464..479 with colour 0
(`spec/boot.md`, "Frame"). The display's 16-bit layout is taken from DirectDraw and may be
555, 565, 655 or 556 (0x414410); images are converted to it when loaded or drawn
(Q-0002). ScummVM uses one fixed 16-bit format.

## Draw types (0x414790, the video device's draw method, vtable 0x47e388 slot 9)

`draw(image, x, y, type)` places the image's top-left at (x, y) in screen coordinates,
clipped to the screen:

- 8- or 16-bit images (packed BMA, cursors): copied opaque, whatever the type.
- 24- or 32-bit images (plain BMP/TGA, packed TGC):
  - type 1: copied opaque (through `aImage::Display1`);
  - type 2: colour key: a source pixel of (0, 0, 0) is skipped, others are converted to
    the display format and written;
  - type 3: alpha blend (0x42c210 → 0x42c180) of a 32-bit image prepared at load
    (below): alpha 0 skips the pixel, 255 writes it, otherwise each channel of the result
    is `src + (dst × (255 − alpha) >> 8)`, masked to the channel.

When a 32-bit TGA is loaded (`aImageFileTgc::ReadImage` 0x42b600 → 0x42c0a0), every pixel
becomes `channel × (alpha × 1/255)` truncated, per channel, packed into the display's
16-bit layout, with the alpha kept in bits 16..23.

## Puzzle drawing (`aPuzzle::Update` 0x41c320)

1. The background is drawn with type 1 at its declared position (loaded first if needed,
   `spec/resources.md`).
2. The puzzle's animations advance (0x416870, with the tick count), unless puzzle +0x28 is
   set.
3. The puzzle's presentation images (+0x10) are drawn in their list order, which is
   ascending priority: an image is inserted before the first image of higher priority
   (`aPuzzle::AddPreImg` 0x41cb70), so equal priorities keep declaration order. An image
   is drawn when its handle is active (+0x65) and its presentation is shown (+0x71 → +4);
   image handles (kind 1) are drawn with their draw type (+0x66), animation handles (kind
   2) by their animation (0x422940).

`ObjPreAddImgToPuz`'s arguments after the position are: active (u8), draw type (u8,
+0x66), priority (int, +0x67) (0x42d320, setters 0x42d790, 0x42d770): e.g.
`ObjPreAddImgToPuz(90000, 0, 90000, "gm_new.bmp", 148, 85, 1, 1, 1000)` is the picture
`gm_new.bmp` of menu object 90000, active, opaque, priority 1000; the SY dialogues' `.tga` pictures use
type 3.
