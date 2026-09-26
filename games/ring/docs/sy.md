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
language's messages, `spec/text.md` to come) at (225, 193) and (225, 213); presentation 0
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
- the preferences, load, save and status objects: `sy` notes, to come.

**On nothing (0x433bc0):** hide presentation 0 of every menu entry and of the other SY
screens' lit pictures, presentations 1 and 2 of objects 2 and 4, presentation 1 of 3;
then `CurSet(0x38)` (`CUR_MenuIdle`). So in SY the cursor is `CUR_MenuIdle` off a hot
spot and the hot spot's cursor (57, `CUR_MenuActive`) on one.

**On a movability (0x433b80):** formats a debug string only.

**Object click (0x431660, `object`, `unk_19`):**

| Object | Action |
|---:|---|
| 90000 new game | `GetMultiLanMes("DoYouWantToStartNewGame")`, question with kind 2 |
| 90001 preferences | `PuzSetAct(90001, 1, 1)`, then the preferences read from app+0xa1 (`sy` notes, to come) |
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
