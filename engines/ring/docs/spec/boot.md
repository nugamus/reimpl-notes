# Boot (Ring, DVD edition)

What `RING_DVD.EXE` does from process start to the main menu. Evidence: E-0030 unless
noted. Addresses are `RING_DVD.EXE`.

## Window and display

`WinMain` (0x40f720 via the CRT entry 0x46fbfc) calls 0x40f460, which:

1. hides the cursor, changes to the directory of the EXE (taken from the quoted command
   line);
2. registers class `Ring` and creates a 640×480 popup window titled `Ring`;
3. opens DirectDraw at 640×480, 16 bits (0x40e740(0x280, 0x1e0, 0x10));
4. starts timer 100 with a 3,000 ms period.

The message loop runs `PeekMessage`; when the queue is empty and the window is active and
the application exists, it reads the cursor position and runs one frame (0x40e9f0, see
"Frame") and the sound update (0x468da0); otherwise it waits (`WaitMessage`).

## Start-up timers (window procedure 0x40eec0)

- **Timer 100** (3 s after the window appears): kill the timer, create the application
  (`aApplication`, 0xa6 bytes, ctor 0x407750), `aApplication::Init` (0x407b80, below),
  then the game set-up 0x430ed0 and the zone set-up 0x431040, then start timer 101 (2 s).
- **Timer 101**: kill it, run the start-up screens 0x4314a0, then
  `aApplication::StartMenu(0)`.
- Any other timer id goes to the application's timer handler 0x40b4a0.

## aApplication::Init (0x407b80)

Registers ten languages (`AddLanguage`), then reads `fl.ini` (formats README
"Configuration files"): `CDPATH` (the literal `CDROM` sets a flag at app+0x1c; the value is
stored as the CD path, a `\` appended), `LANGUAGE` (`SetActLanguage`), `CHECKCD`, the
`SOUNDCHUNCK_*`/`LOADFROM_*` pairs, `ART_*` and `CHECKLOADSAVE`. `ART_x: 1` makes zone x
load its images from its `.AT2` archive; 0 from loose files (below). It then creates the
subsystems (art, bag, drag control, preferences, timers, …; its error strings name
`AGV_art`, `AGV_bag`, `AGV_dragControl`, `AGV_preferences`, `ASV_timer`), loads
`aPre.ini` and `aObj.ini`.

## Zones

| Id | Folder (0x402010) | Archive flag (fl.ini) | Character (0x4020b0) |
|---:|---|---|---|
| 1 | `sy` (system: menus, inventory) | `ART_SY` (app+0x4b) | — |
| 2 | `ni` | `ART_NI` (+0x4d) | Alberich |
| 3 | `rh` | `ART_RH` (+0x50) | Alberich |
| 4 | `fo` | `ART_FO` (+0x52) | Siegmund |
| 5 | `ro` | `ART_RO` (+0x4f) | Loge |
| 6 | `wa` | `ART_WA` (+0x51) | Brünnhilde |
| 7 | `as` | `ART_AS` (+0x4c) | Dril |
| 8 | `n2` | `ART_N2` (+0x4e) | Loge |

`GetreadFrom(zone)` (0x402130) returns `'f'` (archive) when the zone's
flag is set and the global mode at app+0x58 is not `'e'`, else `'e'` (disk). `ART_BAG`
(+0x49) and `ART_CURSOR` (+0x4a) do the same for inventory icons and cursors.

## Game set-up (0x430ed0)

Switches to zone 1 (0x402280(1, 0)), registers the cursors with `CurAdd` (id, name, then arguments of `aCursorHandler::Add`
0x41efb0; the last is the load-from byte per `ART_CURSOR`) and 0x402860 (id, x, y),
sets subtitle colours (text 255,255,255; background 50,50,50):

| Id | Name | `CurAdd` arguments after the name | 0x402860 |
|---:|---|---|---|
| 0x36 | (empty) | 1, 1, 3 | — |
| 0x33 | `CUR_busy` | 3, 1, 3 | — |
| 10000 | `ni_handsel` | 3, 1, 3 | 15, 15 |
| 0x32 | `cur_idle` | 4, 1, 15, 12.5 (f32), 4, 3 | 10, 6 |
| 0x35 | `cur_muv` | 4, 1, 20, 12.5, 4, 3 | 10, 6 |
| 0x34 | `CUR_Hotspot` | 4, 1, 19, 12.5, 4, 3 | 10, 6 |
| 0x37 | `cur_back` | 3, 1, 3 | 10, 20 |
| 0x38 | `CUR_MenuIdle` | 3, 1, 3 | — |
| 0x39 | `CUR_MenuActive` | 3, 1, 3 | — |

(Their meaning is the cursor spec's; `CurAdd`'s error strings distinguish animated and
non-animated cursors.)

## Zone set-up (0x431040)

Calls the set-up function of every zone once, each with app+0x58 = `'f'` when that zone's
`ART_*` flag is set, else `'e'`, and app+0x5d = 2 for SY then 1: SY 0x4662a0, AS 0x4635a0,
NI 0x45eb30, N2 0x45b610, RO 0x458a90, RH 0x455a50, FO 0x44f3e0, WA 0x44ab00. Afterwards
app+0x58 = `'f'` if any zone flag is set, and 0x40b7b0(0) clears the current mode. (These
functions declare every puzzle, rotation, object and sound of their zone: the zone specs
in `games/ring/docs/`.)

## Start-up screens (0x4314a0)

1. 0x402210(1) (zone SY active);
2. play `logo.cnm` (`DATA/SY/PLA/LOGO.CNM`) with 0x401490 (waits for Escape to be
   released first);
3. fade between full-screen images with `aApplication::DisFad` (0x4018c0; 20 frames each,
   read from disk): `beg0.bmp` → `beg1.bmp`, hold 3 s, → `beg0.bmp`, → `beg2.bmp` 3 s,
   → `beg0`, → `beg3` 3 s, → `beg0`, → `beg4` 3 s, → `beg0`, → `beg5` 3 s, → `beg0`,
   → `beg6` 6 s. Holding Escape between steps skips the rest.

## Frame (0x40e9f0)

Once per idle loop: restore a lost primary surface; clear the screen's top 16 rows
(0..0x10) and rows 0x1d0..0x1e0 (the 16-pixel bands above and below the 640×448 view);
then by the application's mode (0x40b7c0):

- 1 — rotation: the active rotation (0x4210f0) draws its panorama into the back surface
  (0x410410 load, 0x410610 update, 0x4107f0 mouse, 0x4107c0 draw) and its animations;
  Space toggles a rotation state (+0x28: 0 ↔ 3);
- 2 — puzzle: `aPuzzle::Alloc` + `aPuzzle::Update` on the current puzzle;
- 3 — 0x418ca0 on the object at 0x40b7e0 (the inventory/bag view);
- 4 — pending zone change: 0x408bc0, 0x431040, 0x431190(zone, app[0x1c]).

Then puzzle 1 (SY's dialog puzzle, looked up by id with 0x40b760) is drawn on top, the bag if shown, the drag
cursor (0x409520) while the left button is down, hotspot tracking (0x408dd0),
dialogs (0x427c70), the cursor (0x423a60), and the frame is flipped. A frame counter
gives the fps each second.

## Input (window procedure 0x40eec0)

- Left button down (y < 465): 0x409630(x, y); up: 0x40af80 (0x40afb0 with Ctrl held);
  release with y < 16 calls 0x409d70.
- Right button down: 0x44a100; up: 0x40afe0.
- F12 (0x7b): `StartMenu(1)`; Delete and characters (`WM_CHAR`): 0x40b060(key).
- Close (`WM_CLOSE`): `PuzSetMod(1, 2, 2)` then `ObjPreSho(2, 0)` and 0x403030(2) (the
  quit confirmation of zone SY).
- `WM_SETCURSOR`: hidden while active.

## Open

The two directory helpers (app+0x6b, the strings at app+0x14 and app+0x18) and how a file
name is resolved between the CD path and the install directory: Q-0006.
