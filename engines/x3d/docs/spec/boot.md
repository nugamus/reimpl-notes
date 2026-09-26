# Boot

From process start to the first interactive screen. Paths are relative to the data root
`Data/` (E-0027: `<exe dir>\Data\` or the CD's `Data\`; both hold the same tree).

## Detection

The engine needs only the data tree. Files that identify the English CD release
(corpus statistics, `games/monet/discs/cd/Data`):

| File | Size | MD5 of first 5000 bytes |
|---|---:|---|
| `Data/App.bin` | 440 | `0963102a249b8d930cc02a13aad2fd0c` |
| `Data/2dbit/Intro1.bmp` | 921,656 | `11104526a28e99fb42b1c8c4538e777b` |

The window title of this release is "Monet - The Mystery of the Orangerie Museum"
(runtime, `snap.ps1`).

## Sequence

1. **Intro bitmaps** (E-0032). Draw `2dbit/Intro1.bmp` (640×480, 24-bit) at (0,0), present,
   wait 3000 ms. Draw `2dbit/Intro2.bmp`, present, wait 2000 ms. Draw Intro2 once more
   (the original redraws it so both buffers hold it). The waits are a `timeGetTime` busy
   loop: no input is read, nothing can skip them.
2. **Menu scene** (E-0033, E-0034). Set the next scene name to `U00.X3D` and app mode 1.
   The loop then loads U00 normally (`a = 1`): U04's garden with Monet, who says `sb01`;
   then app mode 2 and the 2D frame `OptionUser` ("The players"). The 3D garden shows
   briefly before the frame covers it (runtime snap at 6 s). Load, start, the players
   screen timing and the tutorial: `u00.md`.
3. **Players screen to U01** (E-0105): name + OK; a new player gets U00's tutorial, then
   Escape opens the Option menu; a known player gets the menu at once; New game reads
   `App.bin` and enters U01 with `a = 1`. Details in `ui.md` "Boot to U01".
4. **U01 entry** (E-0035). Entering U01 normally (`a = 1`) first plays the prologue:
   `Video/Prologue.avi` (IV50, 640×480, 10 fps, 652 frames) at (0,0) together with
   `Video/prologue.wav` (22,050 Hz mono 8-bit, separate file, started right after the
   video). Enter or Escape skips; otherwise it ends with the video. The sound is stopped
   when the video ends.

## Scene switching (E-0033)

Every scene change is: store the scene file name (`U01.X3D` etc.), set app mode 1. The
main loop then destroys the current scene and builds the unit class chosen by the two
digits after the first character of the name (0..7, 33, 50; others get the generic scene),
loads the `.X3D`, and calls the unit's start hook with `a = 1`. A save restore calls the
same loader with `a = 0` and the save stream.

App modes (`SetAppMode`, app `+0x47c`): 0 running scene, 1 load pending, 2 scene paused
under a 2D frame, 3 video playing.

## Timing

The intro waits are wall-clock milliseconds. Video pacing belongs to the AVI's own frame
rate (`AviPlayMovie`), not to the game loop.

## Engine deviations

- After step 1 the engine goes straight to step 4 (U01, `a = 1`). U00 and the frames of
  step 3 are specified (`ui.md`) but not implemented yet.
- The engine pumps events during the intro waits so the ScummVM quit and menu keys work.
  The original cannot be interrupted there.

## Skipping (E-0043)

- Videos: Enter or Escape, read as the key's current state (held), not as a key event.
- Scripted sequences: only the waits whose unit code checks it end early on Enter held;
  the script then continues with its next step. Fixed-length waits and waits for an
  animation frame run to the end. U00's talk has no check.
- Escape (menu) and Space (inventory bar) are read by the main loop only, so neither works
  during a blocking sequence; U01's entry clears the "Escape allowed" flag around it.
