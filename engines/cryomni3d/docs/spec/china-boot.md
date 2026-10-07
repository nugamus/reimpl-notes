# China: from start-up to the first panorama

What *China: The Forbidden City* (`CHINE.EXE`, English CD) does from WinMain to the first
interactive panorama of a new game. `<L>` below is the CD drive letter found by the CD
check; `<L>:\Chine\Data\` is the CD's `CHINE/DATA/` folder. Addresses are `CHINE.EXE`.

## Start-up

1. One instance only: a second copy exits without a word (E-0500).
2. Modules start in a fixed order; any failure ends start-up (E-0500). The screen is
   640x480, 16 bits per pixel (E-0503). Warp init sets up the projection (75.137, 50.0,
   units Q-0501), zeroes the view angles and allocates a 2048x768 16-bit warp buffer
   (E-0503).
3. CD check (disk 1): the first drive C..Z holding `\Chine\Data\disk1.dat` is the game CD.
   None: the still `cd` (`Cd.hnm` in the game folder) is shown; Space rescans after 4 s,
   Escape quits (E-0502). In ScummVM the game folder is the CD: no check is needed.
4. Loading screen: still `Load` (`DATA/LOC/LOAD.HNM`, lookup order E-0510, Q-0502) with
   the white text "Chargement en cours..." at x 50, y 200, font 3 (E-0504).
5. The remaining modules load, then fonts (E-0500).
6. `chine.cfg` (game folder, optional): four LE uint32 = panorama speed 0..4 (default 2),
   subtitles (1), music (1), `unk_save_mode` (0; Q-0500) (E-0501). ScummVM keeps these as
   game settings.

## Before the menu

In this order, each skippable on its own by Escape or a left click (E-0504):

1. `DATA/HNM/LOGO.HNS`
2. `DATA/HNM/INTRO.HNS`
3. Dialogue `ANJGEN41` ("Majesty, your humble servant awaits your august decision."):
   voice `LOC/VOICES/ANJGEN41.WAV`, two speakers animated from `SYNC/P000ANJ0..3.HNM` and
   `SYNC/P000EMP0..3.HNM`; subtitles are off for this dialogue whatever the option says;
   Escape stops it.
4. `DATA/HNM/ITB.HNS`
5. Music `ALLEE.ZIK` starts (only if the music option is on); it plays under the menu.

## Main menu

Background `DATA/INTERF/FONDTITR.HNM` (E-0505). Eight 14x14 bullet sprites run
diagonally; each has a label from `DATA/LOC/LABELS.TXT` drawn at bullet (x+20, y+1).
Normal bullet `ROUG_n.SPR`, hovered `BLC_n.SPR` (same position); SPR layout in E-0505.

| # | Bullet x, y | Label key (English) | Enabled when | Action |
|---|---|---|---|---|
| 0 | 196, 225 | `nouveau_jeu` (Start the game) | fewer than 12 save files | New game |
| 1 | 212, 254 | `charge_jeu` (Load a game) | a save exists, or save mode | Load |
| 2 | 230, 283 | `reprendre` / `reprendre2` (Resume the game / visit) | a game or visit is running | Resume |
| 3 | 246, 312 | `sauve_jeu` (Save the game) | save mode and a game is running | Save |
| 4 | 264, 341 | `visite` (Visit the site) | always | Visit mode |
| 5 | 280, 370 | `consulte_doc` (Consult the documentation) | always | documentation screens, back to menu |
| 6 | 300, 395 | `options` (Options) | always | options screen, back to menu |
| 7 | 320, 420 | `quitter` (Leave the game) | always | quit, after the credits |

Hit area: the bullet rectangle grown right by the label's width and down by its height.
Hovered: `BLC_n` and white label (0xffff); otherwise `ROUG_n` and the label in 0x7020
(enabled) or 0x9a73 (disabled). Bullets 6 and 7 reuse sprite 6, moved (+20, +25) per step
(E-0505). Save files are `Data\Saved\<name>_game<1..12>.sav` (E-0505). The options screen
has four buttons: panorama speed (very slow .. very fast, cycling), subtitles, music,
`save` (E-0501).

## New game

1. Game state reset; if save mode is off, the emblem chooser ("CHOISISSEZ VOTRE
   EMBLEME:") runs first, and Cancel returns to the menu (E-0506, Q-0500).
2. Game running = on, visit variable = 0, object 0x1e set to state 2, scene = the start
   script `Script_Start` (E-0506). No video plays here.
3. On its first frame `Script_Start` sets game variable 1 = 1, calls 0x411d80("MIN001"),
   sets the view to alpha 4.7, beta 0, and switches to place `pne140` (E-0507).
4. `pne140` registers its zones (labels `lionne_pne`, `lion_pne`) and loads the warp
   `DATA/WARP/PNE140.HNM`; the switch is drawn as a cross-fade from the old screen
   (E-0507, E-0508). This is the first interactive panorama.

Warp file names: a place loads `<L>:\Chine\Data\warp\<name>` with the name as the script
gives it (`pne140` for `PNE140.HNM`) (E-0507).

## Main loop

The game alternates menu and play: the menu runs, then frames until a frame asks for the
menu again, or quit is chosen, which shows the credits and ends (E-0508). One frame:

1. Keys: frame-rate count, debug keys, Space or the interface trigger (opens the interface
   screen, which can return to the menu), Escape (E-0508).
2. If the window is active: music tick, mouse, sound, hotspot under the cursor, then the
   current scene's script (entry call once, then the per-frame call) (E-0508).
3. Draw: a still, or the warp: cross-fade first if a new warp was just loaded, then the
   view update (cursor-edge scrolling, below), warp render, labels, debug overlays,
   cursor, then flip (E-0508).

Frames are not paced: no timer wait and no vsync (the flip is a plain back-to-front blit),
so the original ran as fast as the PC drew, and the per-frame edge scrolling below turned
at the machine's speed. Our rate is a choice (E-0804, Q-0800).

Edge scrolling (E-0509): with the cursor centre (x, y), dx = 100 - x left of 100,
540 - x right of 540; dy = y - 100 above 100, y - 380 below 380. With s = 5 - speed:
alpha velocity += dx / (1250 s), beta velocity += dy / (1500 s); the angles advance by the
velocities, then both decay by x0.8 each frame. Beta is clamped, alpha wraps (Q-0501).

## Text and colours

Fonts (E-0800): eleven slots, slot n-1 = `DATA/FONTES/FONT0n.CRF` (FONT01 = slot 0 ..
FONT11 = slot 10), loaded at start-up; any missing file is fatal. CRF layout in
`docs/formats/` (`crf.ksy`). Character 0xFF of slots 0..9 is unusable (E-0800).

Drawing a string (E-0801), given slot, colour, top y and left x:
- 0x0A: x back to the start, y += height of the slot's space glyph. 0x0D and other bytes
  below 0x20 are skipped.
- A glyph's top-left is (x + off_x, y + off_y + font line height - 2), each clamped to 0;
  rows from 480 down are cut, columns are not.
- Each non-zero bitmap byte becomes one pixel in the current colour; zero bytes are
  transparent. No shadow, outline or blending.
- x advances by the glyph's advance + 1. String width = sum of (advance + 1) over the last
  line. The string-height measure reads the wrong glyph (character + 32), so the menu's
  hit rectangles are slightly off (original bug).

Colours (E-0802, E-0803): the screen is 15-bit (555) or 16-bit (565) and every pixel is
converted to it once, when loaded: TGA/SPR files are X1R5G5B5, HNM is decoded straight to
the screen format, and colour constants are R5G6B5 (converted down for a 555 screen). So on
a 565 surface: constants as they are, file pixels 555 -> 565. Initial text colour 0xFFFF.

| Use | Slot (file) | Colour |
|---|---|---|
| Main-menu labels (measured with slot 0) | 1 (FONT02) | 0xFFFF hovered, 0x7020 = RGB (115, 4, 0) enabled, 0x9A73 = RGB (156, 77, 156) disabled |
| `Chargement en cours...` at x 50, y 200 | 3 (FONT04) | 0xFFFF |
