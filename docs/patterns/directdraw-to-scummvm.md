# DirectDraw games on ScummVM's graphics

Most of our games draw through DirectDraw (3, 5 or 7) on one 16-bit surface. What maps to
what, and the traps.

**The screen.** The original's primary surface becomes a `Graphics::ManagedSurface` (or
`Graphics::Screen`) of the same size and a 16-bit `Graphics::PixelFormat` matching the
original's: RGB555 `(2, 5, 5, 5, 0, 10, 5, 0, 0)` or RGB565 `(2, 5, 6, 5, 0, 11, 5, 0, 0)`.
Which one the game assumed matters for colour keys and for any colour constants in the
data: read it from the code that builds colours (shifts by 10 or 11), not from the
monitor mode. Grumpa is RGB555 at 800x600, Gilbert and Monet 640x480 16-bit. Call
`initGraphics(w, h, &format)` once and present with `g_system->copyRectToScreen` +
`updateScreen` (or `Graphics::Screen::update`).

**Blits.** `IDirectDrawSurface::Blt`/`BltFast` with a source colour key becomes
`ManagedSurface::transBlitFrom(src, rect, pos, key)`; without a key, `blitFrom`. Stretch
blits: `blitFrom(src, srcRect, dstRect)` scales. Keep the key in the surface's own pixel
format (a 16-bit value), as the original compared it: converting the key through RGB888
and back can miss by one level. Grumpa's sprites use a blue key, Gilbert's collections a
per-picture key.

**Surface memory.** The original often locks a surface and writes pixels with its own
loops (fades, effects). Do the same on `getBasePtr()`: in-memory pixels are native-endian
and fine to write as `uint16`. Only bytes coming *from files* need `READ_LE_UINT16`.

**Palettes (8-bit games).** `IDirectDrawPalette::SetEntries` becomes
`g_system->getPaletteManager()->setPalette`; palette fades are palette writes per frame.

**Flip and timing.** `Flip` or the blit to the primary is one `updateScreen`; the game's
frame timer (`timeGetTime`, `WM_TIMER`, a DelphiX `DXTimer`) becomes a loop on
`g_system->getMillis()` with `g_system->delayMillis` and event polling, at the original's
tick rate (Gilbert's main loop is a `DXTimer` callback; Grumpa updates every 20 ms).

**Gamma and fades.** DirectDraw gamma ramps (Grumpa's `CFXFadeEffect`) have no ScummVM
equivalent: scale the colours yourself when composing the frame, last, as the hardware did.

**Higher resolution.** Drawing the original's 640x480 page into a larger OpenGL view (Monet
and Mission Sunlight's `high_res` option) is an enhancement on top: keep the original-size
path as the default and the reference for scenarios.
