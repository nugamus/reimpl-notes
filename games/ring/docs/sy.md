# Zone SY (1): system screens — menu, dialogues (Ring, DVD)

Evidence: E-0041 (handlers), E-0040 (tracking and clicks), E-0031/E-0032 (set-up calls).
Addresses are `RING_DVD.EXE`. The set-up (0x4662a0) is listed in
`engines/ring/notes/zones/sy.md`; object ids below are decimal (the code has them in hex:
90000 = 0x15f90).

## Puzzles and objects

| Puzzle | Background | What |
|---:|---|---|
| 1 | — | the dialogue layer, drawn over every screen (`spec/boot.md`, "Frame") |
| 90000 | `GenMen.bmp` | main menu |
| 90001 | `Preferences.bmp` | preferences |
| 90002 | `Load.bmp` | load |
| 90003 | `Save.bmp` | save |
| 90004 | `GameStat.bmp` | game status |
| 90005 | `insertcd.bmp` | insert CD |

Main menu objects 90000..90006 (flag 1, so clicks reach the zone): each has one
accessibility on puzzle 90000, enabled, cursor 57 (`CUR_MenuActive`), `unk_19` 0, and one
presentation: an opaque picture of the lit entry at x 148, priority 1000:

| Object | Entry | Hot spot (x1, y1)–(x2, y2) | Picture, y |
|---:|---|---|---|
| 90000 | new game | (148, 69)–(500, 99) | `gm_new.bmp`, 85 |
| 90001 | preferences | (148, 105)–(500, 135) | `gm_pre.bmp`, 121 |
| 90002 | load | (148, 168)–(500, 198) | `gm_loa.bmp`, 184 |
| 90003 | save | (148, 236)–(500, 266) | `gm_sav.bmp`, 252 |
| 90004 | continue | (148, 303)–(500, 333) | `gm_con.bmp`, 319 |
| 90005 | game status | (148, 342)–(500, 372) | `gm_sta.bmp`, 358 |
| 90006 | exit | (148, 380)–(500, 410) | `gm_exi.bmp`, 396 |

The pictures are 352×30; each hot spot is 16 pixels above its picture (Q-0009).

Dialogue objects on puzzle 1 (accessibilities declared disabled, cursor 57):

- **2, exit:** `Exit.bmp` at (160, 165) (presentation 0, the question is part of the
  picture), `ex_yes.bmp` at (261, 279) (presentation 1), `ex_no.bmp` at (318, 279)
  (presentation 2), all opaque. Accessibility 0 (262, 270)–(321, 306) `unk_19` 1, key 13;
  accessibility 1 (310, 270)–(370, 306) `unk_19` 0, key 27.
- **3, warning:** `Warning.bmp` at (160, 165), two text lines, `wr_ok.tga` (presentation
  1); one accessibility, `unk_19` 0, key 13.
- **4, question:** `Question.bmp` at (160, 165), two text lines, `g_ok.tga` (presentation
  1), `qu_cancel.tga` (presentation 2); six accessibilities in pairs (OK, cancel) with
  `unk_19` 0/1, 2/3, 4/5, keys 13/27.

## Showing a puzzle (`PuzSetAct` 0x402490)

`PuzSetAct(puzzle, unk_2, unk_3)`: the puzzle becomes the current one (app+0x81), is
loaded and drawn once, and the application's mode becomes 2 (puzzle); then the puzzle's
ambient sounds are started (`spec/sound.md`, to come).

## Dialogue mode (`PuzSetMod` 0x404ab0)

`PuzSetMod(puzzle, mode, object)` sets the puzzle's mode (+0x24) and object (+0x29);
refused when mode 2 is asked of a puzzle already in mode 2. Mode 2 (a dialogue is up)
also hides the inventory (0x40de90, 0x419350) and drops an inventory object in hand
(0x406570); mode 1 calls 0x40ded0. While puzzle 1 is in mode 2, only its object's hot
spots answer the mouse (`spec/cursor.md`).

Question (0x40e090, `kind`): `PuzSetMod(1, 2, 4)`; object 4's two text lines are set to
the message buffers (0x49536c, 0x49546c; filled by `GetMultiLanMes` 0x40e150 from the
language's messages, `spec/text.md`) at (225, 193) and (225, 213); presentation 0
shown; accessibilities `kind`..`kind`+1 enabled (0x403070). Closing it (0x40e120,
`kind`): all of object 4's presentations hidden (`ObjPreHidDeaPuz`), accessibilities
`kind`..`kind`+1 disabled, `PuzSetMod(1, 1, 0)`. The warning (0x40dfd0 / 0x40e060) is the
same with object 3 and one accessibility.

## Handlers

**On an accessibility (0x4335a0, `object`, `unk_19`):**

- a main menu entry: hide presentation 0 of 90000..90006, show the entry's. (For 90000
  the list hides 90000..90004 and 90006, not 90005.)
- 2: `unk_19` 0 → hide presentation 1, show 2 (no lit); 1 → hide 2, show 1 (yes lit).
- 3: show presentation 1.
- 4: odd `unk_19` → hide 1, show 2 (cancel lit); even → hide 2, show 1 (OK lit).
- the preferences objects: "Preferences" below; load, save and status: to come.

**On nothing (0x433bc0):** hide presentation 0 of every menu entry and of the other SY
screens' lit pictures (90101, 90102, 90207, 90208, 90309, 90310, 90401, 90912), presentation
2 of 90104, presentations 1 and 2 of objects 2 and 4, presentation 1 of 3;
then `CurSet(0x38)` (`CUR_MenuIdle`). So in SY the cursor is `CUR_MenuIdle` off a hot
spot and the hot spot's cursor (57, `CUR_MenuActive`) on one.

**On a movability (0x433b80):** formats a debug string only.

**Object click (0x431660, `object`, `unk_19`):**

| Object | Action |
|---:|---|
| 90000 new game | `GetMultiLanMes("DoYouWantToStartNewGame")`, question with kind 2 |
| 90001 preferences | opens the preferences screen ("Preferences" below) |
| 90002 load | builds the saved-game list, `PuzSetAct(90002, 1, 1)` |
| 90003 save | busy cursor (0x33), saves the menu's snapshot as a picture, `PuzSetAct(90003, 1, 1)` |
| 90004 continue | busy cursor, reloads the zone set-ups (0x408bc0, 0x431040) and loads the `SaveGame` snapshot (`spec/save.md`, to come); when that fails: set-ups reloaded, `aApplication::Init` 0x431140, and the warning `CanNotCountineGame` |
| 90005 game status | `PuzSetAct(90004, 1, 1)` |
| 90006 exit | posts `WM_CLOSE`: the exit dialogue (`spec/boot.md`, "Input") |
| 2, `unk_19` 0 (no) | `ObjPreHidDeaPuz(2)`, accessibilities of 2 off, `PuzSetMod(1, 1, 0)` |
| 2, `unk_19` 1 (yes) | posts `WM_DESTROY`: the game quits |
| 3 | closes the warning (0x40e060) |
| 4, `unk_19` 0 or 1 | closes the question (kind 0) |
| 4, `unk_19` 2 (new game, OK) | busy cursor, set-ups reloaded (0x408bc0, 0x431040), `aApplication::Init` 0x431140 (loads the preferences, then `SetZone(7, 999)`: zone AS, `spec/boot.md`), then closes the question (kind 2) |
| 4, `unk_19` 3 | closes the question (kind 2) |
| 4, `unk_19` 4, 5 | delete a saved game / cancel (load screen) |

## Preferences (puzzle 90001)

Evidence: E-0048. Background `Preferences.bmp`; objects (all flag 1, cursor 57):

| Object | Hot spots (x1, y1)–(x2, y2), `unk_19` | Presentations |
|---:|---|---|
| 90101 cancel | (410, 420)–(490, 445), 0; key 27 | 0: `g_cancel.tga` (407, 421), lit |
| 90102 OK | (320, 420)–(370, 445), 0; key 13 | 0: `g_ok.tga` (328, 421), lit |
| 90103 subtitles | on (310, 315)–(370, 350), 0; off (400, 315)–(460, 350), 1 | 0: `pr_on.bmp` (317, 326); 1: `pr_off.bmp` (402, 326) |
| 90104 stereo | (355, 260)–(420, 295), 1 | 0: `pr_left.tga` (336, 288) + `pr_right.tga` (428, 288); 1: the two swapped; 2: `pr_3ds.tga` (356, 281), lit |
| 90105 volume (flag 4, icon `ni_handsel`) | (300, 140)–(600, 180), 1 | 0: `pr_slider.tga` at (x, 155), shown |
| 90106 dialogue volume (flag 4, icon `ni_handsel`) | (300, 197)–(600, 237), 1 | 0: `pr_slider.tga` at (x, 212), shown |
| 90107 (no picture) | (0, 448)–(20, 640), 1 | — |

90105 and 90106 have drag cursors (15, 15, 0, 3, 0, 0, 3): kind 3 pictures `ni_handsel_dp`
and `ni_handsel_da` at offset (15, 15) (`spec/cursor.md`, "Dragging").

**The preferences** (`aPreFer`, app+0xa1): four integers, `aPre.ini` in the game's
directory, text `"%d %d %d %d"` (read at start-up, 0x407b80, and when a game starts,
0x431140; a missing or short file is reported through 0x413f10 and the values stay;
every edition ships `100 100 -1 1`):

1. volume, 46..100 (the slider): all sound channels except 5 (0x469350);
2. dialogue volume, 46..100: channel 5 (0x4692f0);
3. stereo: −1 normal, 1 swapped (`aSoundHandler::SetLR`: the pan factor −1.0 or 1.0);
4. subtitles: 1 on, 0 off (the dialogue handler, app+0xc, draws dialogue texts only when
   its +0x28 is set).

Loading and saving both apply them at once (0x4289e0; the stereo only with a sound
handler).

**Opening** (object click 90001): `PuzSetAct(90001, 1, 1)`, then the four values are
copied to the screen's working values (volume, dialogue volume, swapped = stereo is 1,
subtitles); without a preferences object 100, 100, 0, 1. When no sound device is up
(0x406ee0: the sound system's object at 0x4a1d04 is null), subtitles become 1 and
90103's hot spots are disabled. Then: subtitles 1 → 90103 presentation 0 shown, 1
hidden; 0 → the reverse. Slider pictures at x = volume × 5 + 84 (90105, y 155) and
dialogue volume × 5 + 84 (90106, y 212). 90104: all presentations hidden, then
presentation "swapped" (0 or 1) shown.

**On an accessibility:** 90101 → its presentation 0 shown, 90102's hidden; 90102 → the
reverse; 90104 → presentation 2 shown.

**Object clicks:**

- 90101 cancel: `PuzSetAct(90000, 1, 1)`; the preferences are unchanged.
- 90102 OK: `PuzSetAct(90000, 1, 1)`, then the preferences are saved (`aPreFer::Save`
  0x428920: stored, applied, written to `aPre.ini`) with (volume, dialogue volume,
  swapped ? 1 : −1, subtitles).
- 90103: `unk_19` 0 → presentation 0 shown, 1 hidden, subtitles 1; `unk_19` 1 → the
  reverse, subtitles 0.
- 90104: swapped toggles; all presentations hidden, presentation "swapped" shown.
- 90107: the credits (0x431350): 0x406ea0(0x400), `SetZone(6)`, 0x406de0(51002, 2),
  `SetZone(1)`, then `ScrollImage("cre_01.bma", 0, 2, 101)` … `cre_10.bma` and
  `ScrollImage("cre_11.bma", 5000, 2, 101)`, stopping at the first that returns 2;
  finally 0x406e00(51002, 0x400). (`SetZone(6)` around the play makes 51002 a WA sound.)
  `ScrollImage(name, hold_ms, kind, load_from)` (0x401260, E-0096): waits until Escape is
  released, loads the picture (load-from `'e'`: `DATA\<zone>\IMAGE\<name>`, the zone SY), and
  for i = 0 .. height − 449 draws its rows i .. i + 447 at (0, 16) (`aVideoDeviceRaw::Display`
  0x414c20 → `aImage::Display` 0x413c10, then the device's flip): one row per frame; Escape
  held ends it (after its release) and makes it return 2 (the credits stop); a full scroll is
  followed by `hold_ms` of waiting (0x402890), returning 1. The `cre_*.bma` pictures are
  640 × 896 (448 rows each). The frame rate is the device's flip (Q-0080). Clicks only
  reach it at y 448..464 (button events need y < 465).

**The sliders** (drag event 0x4331b0, for 90105 and 90106 alike; `pos` is the slider's
x, kept between drags, `delta` the signed horizontal distance of the last move):

- phase 1 (press): drag mode 2, limit rectangle (310, 140)–(600, 180) for 90105,
  (310, 197)–(600, 237) for 90106; step = (press x − 314) / 5 (C division, towards 0),
  clamped to 0..54; `pos` = step × 5 + 314; the picture moves to `pos`.
- phase 3 (move): `delta` = current x − press x; the picture moves to `pos` + `delta`
  (not clamped; the limit rectangle keeps it near the track).
- phase 2 (release): step = (`pos` + `delta` − 314) / 5, clamped to 0..54; the value
  (volume or dialogue volume) = step + 46; `pos` = step × 5 + 314; the picture moves to
  `pos`. `delta` is not reset at a press, so a press and release without a move reuses
  the last drag's `delta`.

## Flow

1. **StartMenu(from_game)** (0x40dc80, `aApplication::StartMenu`; F12 in play calls it
   with 1, the start-up with 0), only when the menu is not already up (app+0x6f = 0):
   - with 1: busy cursor, the game is saved to the `SaveGame` snapshot and the screen is
     copied into a 640×480 picture (the save screen's thumbnail);
   - app+0x6f = the current zone (so the menu knows where to return);
   - 0x406ea0(4) (`spec/sound.md`), `SetZone(1)`, `PuzSetAct(90000, 1, 1)`,
     `PuzSetMod(1, 1, 0)`;
   - objects 1..7: accessibilities off, presentations hidden (`ObjPreHidDeaPuz`);
   - the inventory is hidden, the object in hand dropped;
   - "continue" (90004) is disabled when coming from the start-up, enabled otherwise.
2. The player moves over the entries: each frame the entry under the mouse is lit and the
   cursor is `CUR_MenuActive`; elsewhere nothing is lit and the cursor is
   `CUR_MenuIdle`.
3. A click on an entry runs its action (table above). Exit opens the exit dialogue on
   puzzle 1; yes quits, no closes it. New game asks the question; OK starts the game.
