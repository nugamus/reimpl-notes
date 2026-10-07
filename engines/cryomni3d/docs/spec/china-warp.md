# China: warp view (panorama projection, turning, hit testing)

How *China: The Forbidden City* (`CHINE.EXE`) turns a warp image into the 640x480 view,
and how it differs from upstream `Omni3DManager` (`engines/cryomni3d/omni3d.cpp`,
Versailles). Short answer: **the projection grid, the per-pixel stepping and the
screen-to-image mapping are upstream's algorithm with the same constants**; China differs in
the field of view, two row-delta shifts in the renderer (Q-0600), the hit-test y flip,
16-bit pixels, and a completely different turning model.

## Warp image

- One `DATA/WARP/<name>.HNM` per place: HNM6, 2048 x 768, decoded as a single frame into
  a 3 MB buffer of 16-bit pixels (555 or 565, following the display mode) (E-0600).
- Rows as the projection uses them: image row y grows *up* the panorama (row 0 is the
  bottom); the grid centre row is 384. Columns 0..2047 cover 360 degrees (E-0602).

## Projection tables (`Warp::init(hfov, vfov)`, 0x441c90)

Called with hfov 75.137 deg and vfov 50 deg (E-0601). Identical to upstream `init` with
these inputs: hypV = 384 / sin(77.5 deg), step = tan(hfov/2) x 16 / 320, scale = 2^27 / 2pi,
31 rows (oppH = (i-15) x step) by 21 columns (oppV = (j-20) x step) (E-0601).
Differences: upstream derives vfov from hfov (52.31 deg for 75 deg); China passes 50 deg.
China stores everything as 32-bit floats (E-0601).

To reuse `Omni3DManager`: allow the caller to set vfov (50 deg) instead of deriving it.

## View angles (`Warp::setView(alpha, beta)`, 0x441df0)

- `WRP_Alpha` = alpha (yaw, radians, 0..2pi, wrapped by one 2pi step); `WRP_Beta` = beta
  (pitch, radians, clamped to +-0.9 x vfov = +-45 deg; negative looks up) (E-0602).
  No alpha limits are applied in China's warp code (E-0605).
- Grid: upstream `updateImageCoords` term for term (31 x 82 ints, 16.16 image
  coordinates, x = 2^27 - alpha x scale +- atan2(oppV, cos(angleH + beta) x hypH) x scale,
  y = 384 x 65536 - coord x sin(angleH + beta)) (E-0602).
- China also records the image x of both ends of the top grid row (beta > 0) or bottom row
  (beta <= 0); its use is unknown (Q-0601).

## Rendering (`Warp::render`, 0x44205c)

Full 640 x 480, no toolbar inside the warp: 30 x 40 blocks of 16 x 16 pixels, each
interpolated from its four grid corners with upstream's fixed-point scheme (E-0603).
One difference: down a block, the per-pixel x step changes by
((bottom delta >> 4) - (top delta >> 4)) >> 4 and the y step by ... >> 9, where upstream
uses >> 10 and >> 15 (E-0603, Q-0600). Pixels are 16-bit, destination pitch 1280 bytes.

## Turning (`MyWarp::scrollByCursor`, 0x4170a0, once per frame)

Cursor-position scrolling, not mouse-delta (E-0605):
- Cursor centre (cx, cy) (top-left plus half the cursor sprite). Push x = 100 - cx left of
  x 100, 540 - cx right of x 540; push y = cy - 100 above y 100, cy - 380 below y 380;
  zero inside.
- k = 5 - speed option (0..4, default 2). Velocity: vAlpha += pushX / (1250 k),
  vBeta += pushY / (1500 k). If either is non-zero: alpha += vAlpha, beta += vBeta,
  setView, then both velocities x 0.8 (inertia). Per frame, no time base.
- Cursor movement itself is DirectInput relative motion clamped to the screen (E-0605).

## Transitions (zone kinds 2..5, E-0606)

1. `turnToPoint(x, y)` with the cursor top-left: target yaw/pitch = current +
   atan2(320 - x, 416) / atan2(y - 240, 416) (416 = focal length in pixels); 32 frames, each
   moving 20 % of the remaining (wrapped) difference.
2. `zoomIn(n)`: n frames, hfov 75.137, 74.137, ... (re-init each frame), then back to
   75.137.

## Hit testing (`Warp::screenToImage`, 0x441b80)

Upstream `mapMouseCoords` exactly, at the cursor hot point (sprite hot-spot offset, or
sprite centre when none); x = 0..2047, and y returned as **767 - image row** (Versailles'
caller uses 768 - row). The result is tested against the place's zone list, first match
wins (E-0604).
