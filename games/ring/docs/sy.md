# Zone SY (1): system screens — menu, dialogues (Ring, DVD)

Evidence: E-0041 (handlers), E-0040 (tracking and clicks), E-0031/E-0032 (set-up calls),
E-0257..E-0264 (load, save, game status; the files are in `engines/ring/docs/spec/save.md`).
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
- 90101, 90102, 90104: "Preferences" below; 90207 / 90208, 90309 / 90310: the lit picture of
  the button under the mouse shown, the other's hidden; 90401: its lit picture shown.

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
| 90002 load | builds the saved-game list, `PuzSetAct(90002, 1, 1)` ("Load" below) |
| 90003 save | busy cursor (0x33), the thumbnail written, `PuzSetAct(90003, 1, 1)` ("Save" below) |
| 90004 continue | busy cursor, reloads the zone set-ups (0x408bc0, 0x431040) and loads `SaveGame` (`LoadSave("SaveGame", 1)`, `engines/ring/docs/spec/save.md`): the game goes on where F12 left it; when that fails: set-ups reloaded, `aApplication::Init` 0x431140, and the warning `CanNotCountineGame` |
| 90005 game status | `PuzSetAct(90004, 1, 1)` ("Game status" below) |
| 90006 exit | posts `WM_CLOSE`: the exit dialogue (`spec/boot.md`, "Input") |
| 2, `unk_19` 0 (no) | `ObjPreHidDeaPuz(2)`, accessibilities of 2 off, `PuzSetMod(1, 1, 0)` |
| 2, `unk_19` 1 (yes) | posts `WM_DESTROY`: the game quits |
| 3 | closes the warning (0x40e060) |
| 4, `unk_19` 0 or 1 | closes the question (kind 0) |
| 4, `unk_19` 2 (new game, OK) | busy cursor, set-ups reloaded (0x408bc0, 0x431040), `aApplication::Init` 0x431140 (loads the preferences, then `SetZone(7, 999)`: zone AS, `spec/boot.md`), then closes the question (kind 2) |
| 4, `unk_19` 3 | closes the question (kind 2) |
| 4, `unk_19` 4 | deletes the selected saved game ("Load" below) |
| 4, `unk_19` 5 | closes the question (kind 4) |
| 90207, 90208, 90309, 90310, 90401 | "Load", "Save", "Game status" below |

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

## Load (puzzle 90002)

Evidence: E-0260, E-0261, E-0263. Background `Load.bmp`; objects (flag 1, cursor 57):

| Object | Hot spot (x1, y1)–(x2, y2), key | Lit picture |
|---:|---|---|
| 90208 OK | (325, 418)–(375, 461), 13 | `g_ok.tga` (328, 421) |
| 90207 cancel | (416, 418)–(498, 461), 27 | `g_cancel.tga` (407, 421) |

**The list** is visual object 1 of puzzle 90002, an `aVisualObjectList` (`VisAddLisToPuz`
0x406f90, called at 0x467c7e; init 0x46d130, setters 0x46dcf0..0x46e460, hot spots
0x46de50). Its values here (the widget's origin is (0, 0)):

- flags 65 (bit 0: rows one under the other; bit 6: the selected entry's picture shown);
- 4 rows; row r's centre line at y = 127 + 45 / 2 + 45 r (C division); row hot spots
  (kind 3, index r) x 335..635, y 127 − 35 / 2 + 45 / 2 + 45 r .. 127 + 35 / 2 + 45 / 2 +
  45 r;
- each row: an icon at x 311, centred on the row (`load_gun.tga`; the selected row
  `load_gua.tga`), and two text lines in font 1 at x 335: the entry's name split at its
  first `#`; line 1 centred on the row's centre line, line 2 three pixels under it; colour
  (255, 95, 0), the selected row (245, 235, 50); no background;
- up arrow: picture at (330, 349), hot spot (320, 339)–(360, 379) (kind 1); down arrow:
  (330, 380), hot spot (320, 370)–(360, 410) (kind 2). The pictures come from the SY
  zone's `VISUAL` folder: `up_gun.tga` / `down_gun.tga` when the arrow cannot be used (its
  hot spot disabled), `up_gua.tga` / `down_gua.tga` when it can, `up_gur.tga` /
  `down_gur.tga` drawn while the mouse is on a usable arrow. Up can be used when the first
  shown entry is not the first; down when first shown + 4 < the number of entries;
- the selected entry's picture at (0, 0), draw type 1 (`spec/save.md`, "Thumbnails").

The list is drawn with the puzzle (0x46bf90); row hot spots past the last entry are
disabled. Hovering (0x46bd80): on a usable arrow or a row the cursor is 57
(`CUR_MenuActive`), and a usable arrow shows its `_gur` picture. A click (0x46bc50): up
moves the first shown entry one up (not past 0); down one down (while it is below the
number of entries, so the list can scroll until one row is left); a row selects its entry:
the previous selection's picture is freed, and the entry's picture
`<install>Data\Save\<file>.bmp` is loaded (load-from `'e'`) and drawn from then on (a
missing file: nothing drawn). Each of these raises the event 0x40d1f0(1, kind), which no
zone handles.

**Opening** (object click 90002): `Save.aba` is read (a missing or broken file: nothing
happens). Entry i (in file order) becomes object 90500 + i, named `<description>#<typed
name>`, its icon name the file name (`ArSa<n>`), and is added to the list. Adding puts an
object at the top (`aList::Add` 0x46e4a0), so the newest save is on top; it clears the
selection and, with more than 4 entries, shows from the first. Then `PuzSetAct(90002, 1,
1)`.

**OK** (90208): busy cursor; without a selection the warning `SelectGame`. Otherwise the
entry is looked up in `Save.aba` at index count − 1 − the selected row's list index (the
list is reversed), the list emptied (`VisLisRemAll(1, 90002, 1)`), the zone set-ups rerun
(0x408bc0, 0x431040) and `LoadSave(<file>, 1)` called. On success each of
`<file>_ALB.ars`, `_LOG`, `_SIE`, `_BRU` that exists is copied over `alb.ars`, `log.ars`,
`sie.ars`, `bru.ars` (`SHFileOperation` copy, no confirmation); a failed copy is logged and
the rest skipped. On failure `LoadSave("SaveGame", 1)` restores the game left with F12
(failing that, `aApplication::Init`) and the warning `CanNotLoadGame` is shown.

**Cancel** (90207): `PuzSetAct(90000, 1, 1)`, the list emptied.

**Delete** (key Delete, 0x2e, while 90002 is current; SY's key handler 0x433d30): the
question `DoYouWantToDeleteSavedGame` (kind 4). Its OK (`unk_19` 4): without a selection
the question closes and the warning `SelectGame` shows; otherwise the entry (same index
rule) is removed from `Save.aba`, which is written back, the object leaves the list
(`VisLisRem`), and `<file>.ars`, `.bmp`, `_ALB.ars`, `_LOG.ars`, `_SIE.ars`, `_BRU.ars` are
deleted (`SHFileOperation`, no confirmation, silent; failures logged). If `Save.aba` cannot
be read the warning is `CanNotDeleteSavedGame`. The question then closes.

## Save (puzzle 90003)

Evidence: E-0258, E-0259, E-0262. Background `Save.bmp`; objects:

| Object | Hot spot (x1, y1)–(x2, y2), key | Lit picture |
|---:|---|---|
| 90309 OK | (325, 418)–(375, 461), 13 | `g_ok.tga` (328, 421) |
| 90310 cancel | (416, 418)–(498, 461), 27 | `g_cancel.tga` (407, 421) |
| 90313 (no hot spot) | — | presentation 0, shown: text 0 (the typed name) at (344, 181), text 1 (the description), the caret animation `kybcur` (6 frames, 12.5 fps) at (346, 181), the picture `osc.bmp` at (0, 0) |

**Opening** (object click 90003): busy cursor; the name buffer (0x4a1a68, 260 bytes)
emptied and set as text 0 at (344, 181), the caret at (346, 181); the description
`"<character>  <time>   <date>"` (`"%s  %s   %s"`: the character of the zone the menu was
opened from, 0x4020b0 with app+0x6f; `_strtime`, `HH:MM:SS`; `_strdate`, `MM/DD/YY`) built
into 0x4a1b6c and set as text 1 at (344, 155); the F12 snapshot scaled to 260 × 480 and
written as `<install>\data\SY\Image\osc.bmp` (without a snapshot: logged, the old file
stays); `PuzSetAct(90003, 1, 1)`.

**Typing** (SY's key handler 0x433d30, only while 90003 is current; keys are `WM_CHAR`
codes, `spec/events.md`): Backspace (8) removes the last character; Escape (27) empties
the name; Enter (13) does nothing here; any other code is appended as a character, unless
the name's width in its font is already 280 or more. After each of these text 0 is set
again at (344, 181) and the caret moved to x = the text's width + 346, y 181. Enter and
Escape then also reach the accessibilities with their keys (OK, cancel), so Escape both
empties the name and leaves.

**OK** (90309): busy cursor; `<n>` = the first free `ArSa<n>`; copies `SaveGame.ars` →
`ArSa<n>.ars`, `DATA\SY\Image\osc.bmp` → `ArSa<n>.bmp`, and each of `alb.ars`, `log.ars`,
`sie.ars`, `bru.ars` that exists → `ArSa<n>_ALB.ars`, `_LOG`, `_SIE`, `_BRU`, in that
order (a failed copy shows `CanNotSaveGame` and stops; a failed picture copy shows it and
goes on); appends (`ArSa<n>`, the description, the typed name) to `Save.aba` and writes it
(failing: `CanNotSaveGame`). Then the zone set-ups are rerun and `LoadSave("SaveGame", 1)`:
the game goes on from where F12 left it; if that fails, `aApplication::Init` and
`CanNotSaveGame`. The name may be empty. The save entry is not disabled when the menu came
up at start-up: OK then copies whatever `SaveGame.ars` an earlier session left (or fails).

**Cancel** (90310): `PuzSetAct(90000, 1, 1)`.

## Game status (puzzle 90004)

Evidence: E-0264. Background `GameStat.bmp`; object 90401 OK: hot spot (28, 79)–(107, 109),
key 13, lit `g_ok.tga` (46, 95); a click returns to the main menu (`PuzSetAct(90000, 1,
1)`). Object 90402 has four texts in font 1, colour (255, 150, 0), at x 600 and y 327, 356,
384, 410.

The bars are visual object 2 of puzzle 90004 (`VisAddShoToPuz(2, 90004, 1, 4, 295, 343, 28,
4, 300, 38655)`, 0x4074f0; drawn by 0x46ec60). When the screen is shown (virtual +0x18,
0x46ed40; once until it is hidden again, 0x46efd0) it reads the four SY floats, the four
characters' scores: 90005 Alberich (NI, RH), 90006 Loge (N2, RO), 90007 Siegmund (FO),
90008 Brünnhilde (WA); each clamped to 0..100, writes each as
`"%3.1f"` into text k of 90402 and sets bar k's length to ceil(300 × value × 0.01). Each
frame, bar k is a GDI `Rectangle` filled with `RGB(255, 150, 0)` (the outline in the
device context's current pen) from (295, y_k) to (295 + length, y_k + 4), with y_0 = 343,
y_1 = 343 + 28 + 1, y_2 = 343 + 56 + 1, y_3 = 343 + 84 − 1.

## Flow

1. **StartMenu(from_game)** (0x40dc80, `aApplication::StartMenu`; F12 in play calls it
   with 1, the start-up with 0), only when the menu is not already up (app+0x6f = 0):
   - with 1: busy cursor (0x33), the bag hidden, the game saved as `SaveGame`
     (`LoadSave("SaveGame", 2)`; when that fails the menu does not open) and the screen
     copied into a 640×480 24-bit picture (0x49556c, the save screen's thumbnail);
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
   Continue reloads `SaveGame`; load and save open their screens, whose OKs both end by
   loading a game (`engines/ring/docs/spec/save.md`).
