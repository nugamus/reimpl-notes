# Rotations: panorama rendering, looking around, hot spots

A rotation (`AddRot`, `spec/api.md`) is a panorama node (`.aqc`, formats README) viewed
through a perspective camera. Evidence E-0046; decompiles and disassembly notes in
`engines/ring/notes/decomp/rot/`.

## Node in memory

`CAquatorStream::InitFull` (0x4111d0) keeps the node's 13-word header (0x412640; width,
height, …, `unk_3` .. `unk_6`) and two buffers: the colour table (64,800 16-bit values =
16,200 entries of 4 pixels, converted to the display's 16-bit layout by 0x410ff0) and,
0x1fa40 bytes after it, the index array (one 16-bit index per 4 pixels, `data_size / 4`
values). The pixel at panorama column x, row y is

    table[4 * index[(y * 2048 + x) / 4] + (x & 3)]

(the sampler 0x4116e0 masks x with 0x7ff and multiplies y by 2048: the width is fixed at
2048).

From the header (0x410410 on load, again every frame in 0x40f9e0), reading `unk_3` .. `unk_6`
as floats (`unk_3` is 0, so 0.0):

- horizontal range `hr = unk_4 − unk_3` (360), middle `hm = (unk_3 + unk_4) / 2` (180);
- vertical range `vr = unk_6 − unk_5` (120 or 150), middle `vm = (unk_5 + unk_6) / 2` (0);
- height `H` (688 or 856); rows are clamped to `[0, H − 2]`.

## Camera (0x40f9e0, every frame)

The rotation holds alpha (+0x68), beta (+0x6c) and ran (+0x70), in degrees.
`RotSetAlp(rotation, a)` (0x405920) stores `a − 135`, plus 360 when negative;
`RotSetBet` (0x4059b0) and `RotSetRan` (0x405a30) store their value.

1. ran is clamped to [30, 87].
2. The view is 640 × 448 (0x40f900), split in 40 × 28 blocks of 16 × 16 pixels.
   With `s = sin(ran / 2)`: the image plane's half width is `s`, its half height
   `t = 448 / 640 × s`, at depth `cos(ran / 2)`: ran is the horizontal field of view. The
   vertical one is `fv = 2 asin(t)`.
3. alpha is brought into [0, 360] (360 subtracted while above, added while below 0).
   beta is clamped to `vm ± ((vr − fv) / 2 − 5)`.
4. Forward `F = (sin α cos β, sin β, cos α cos β)` (α, β in radians), normalised; up
   `U` = (0, 1, 0) minus its component along F, normalised; right `R = U × F` (0x410a20).
5. The four corners of the image plane, top left, top right, bottom left, bottom right, are
   `(∓s, ∓t)` with top = −t: `(−s, −t), (s, −t), (−s, t), (s, t)` at depth `cos(ran/2)`,
   turned into world directions `x R + y U + z F` (0x410bb0).
6. For each of the 41 × 29 grid points (0x411c90), the direction `(X, Y, Z)` is the bilinear
   interpolation of the corners (column i of 40, row j of 28), `r = |(X, Y, Z)|`, and

       lat = asin(clamp(Y / r, −1, 1))
       lon = asin(clamp(X / r / cos lat, −1, 1)), mirrored when Z < 0:
             π − lon (lon > 0) or −π − lon (lon ≤ 0)          (that is, atan2(X, Z))
       u = (lon° + hm) / hr × 2048
       v = (lat° − vm) / vr × H + H / 2

   stored as 16.16 fixed point (truncated). Screen x grows with lon and screen y with lat.
   Before drawing, each v is clamped to [0, (H − 2) × 65536] (0x412180).

A rotation facing alpha `a` therefore shows panorama column `(a − 135 + 180) / 360 × 2048`
at the screen's centre.

## Drawing (0x4107c0 → 0x412230, 0x4116e0)

The frame (`spec/boot.md`, mode 1) locks the back surface and draws the view at row 16.
Each 16 × 16 block is filled from its four grid points: their u values are first brought
within half a panorama of each other by adding 2048 (0x411810); then, row by row, the
left and right edge points move down by a sixteenth of their edge per row, and along a
row u and v step by `(right − left) / 16` (integer shift). Each pixel is the panorama pixel
at `(u >> 16) & 2047`, `v >> 16`. No filtering.

## Looking around (0x4107f0, every frame)

Unless the rotation's byte +0x67 is set, with the mouse at (x, y) in window pixels:

    dx = x / 640 − 0.5,  dy = y / 480 − 0.5
    |dx| > 0.25: alpha += dx × (|dx| − 0.25) × 48
    |dy| > 0.25: beta  += dy × (|dy| − 0.25) × 48

and ran decreases by 1 while the Up arrow is held, increases by 1 while Down is held
(`GetAsyncKeyState`). This is per frame (Q-0011). `RotSetAct` puts the mouse at
(320, 240) (`SetCursorPos`), so nothing turns until it moves. Only the saved-game restore
writes +0x67 (0x40d34d / 0x40d359); the constructor leaves it (Q-0012).

## Hot spots on rotations

The same function then turns the mouse into panorama coordinates, and hot-spot tracking and
clicks use those on the rotation's accessibilities and movabilities:

1. y −= 16; x, y clamped to the view (0..639, 0..447).
2. The four grid points around (x, y) (block `x / 16`, `y / 16`) are interpolated
   bilinearly with the fractions `x & 15`, `y & 15` (after the same 2048 unwrapping), giving
   a panorama column and row (truncated) (0x4119e0); the column is taken modulo 2048, the
   row modulo H.
3. They become tenths of a degree (0x412360): `x' = column / 2048 × hr × 10`,
   `y' = ((row − H/2) / H × vr + vm) × 10` (truncated).

So `ObjAddRotAcc` and the `Rot*Mov*` rectangles are in tenths of a degree: x 0..3600 around
the panorama, y from −600 (top) to 600 (bottom) for a ±60° node. E.g. AS rotation 80001's
movabilities are at x 757..928, 1251..1444 and 1784..1982.

## Clicking a movability (`MouseLeftEvent` 0x409d90, rotation part)

After the rotation's accessibilities (clicked as in `spec/cursor.md`), the first enabled
movability containing the panorama point is taken:

1. The "movability clicked" event (0x40c2b0: rotation id, target id, movability index,
   `unk_19`, kind) goes to the zone; if the mode is then 4 (a zone change), stop.
2. The turn, chosen by the transition's kind byte (+0x28), or 2 for a Ctrl-click
   (0x40afb0 clears app+0xa5, which 0x40af80 sets):
   - 0: an animated turn to (alpha1, beta1, ran1) (0x4101c0, below);
   - 1: alpha1, beta1, ran1 set at once (0x410170, alpha stored minus 135);
   - 2: no turn.
3. 0x40b650 (the current view is left), then for kind 0 (to a rotation) the target's
   alpha is set to alpha2 (minus 135).
4. Unless Ctrl-clicked, the ride video plays: `PlyCin(ride, 0)` (0x401490,
   `spec/video.md`: `DATA\<zone>\PLA\<ride>.cnm`).
5. Kind 0: `RotSetAct(target, 1, 1)`, then alpha2, beta2, ran2 set at once (0x410170);
   kind 1: `PuzSetAct(target, 1, 1)`. Then the "movability done" event (0x40c420: the new
   rotation or puzzle id, the old rotation id, index, `unk_19`, kind).

Puzzle movabilities (kinds 2, 3) are clicked the same way from the current puzzle
(the puzzle part of the same function): no turn; for kind 2 the target rotation's alpha is set to alpha2 first, then
the ride plays (unless Ctrl-clicked), then `RotSetAct(target, 1, 1)` with alpha2, beta2,
ran2 (kind 2) or `PuzSetAct(target, 1, 1)` (kind 3), and the "movability done" event.

### Animated turn (0x4101c0)

The target alpha is stored minus 135 (plus 360 when negative). Differences are truncated
to integers: `dα = |target − alpha|`, folded to `360 − dα` when above 180; `dβ`, `dran`.
The step count is `trunc(0.8 × max(dα, dβ, dran))`. When the target alpha is more than
180 above the current one 360 is subtracted from it, more than 180 below 360 is added.
For step i of n, with `t = i / (n − 1)` (t = 0 when n = 1): alpha, beta and ran are
`target × t + start × (1 − t)` (alpha brought back below 360), +0x31 = 1 − t, then one
frame is drawn (0x410610, 0x40f9e0, 0x4100a0 draws and flips). Held Escape only waits for
its release. One step per frame (Q-0011).

## Not yet specified

Layers (sections of the `.aqc`, drawn into the panorama by 0x410610 / 0x411530 / 0x4114c0),
the juggle effect (+0x65, `RotSetJugOn`) and the wave (+0x66), Space (+0x28), the
movability events' handlers per zone.
