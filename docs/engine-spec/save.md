# Players, settings, saved games

The files under `<exe dir>/Save/`, what the game writes into them and when, what a load
restores and in which order, and the three frames that drive it (`OptionUser`,
`OptionSave`, `OptionLoad`). Evidence E-0180..E-0185; validator
`tools/parsers/savegame.py` (formats README, `savegame.ksy`). An engine is free to keep
its saves in ScummVM's own format; this spec is what the original stores and restores, so
the engine saves the same state (and could import original saves).

## Files (E-0180, E-0181)

All are the `.BIN` chunk container of `binchunk.py` (payloads back to back from offset 0,
then a table of 28-byte entries `name[20]`, u32 offset, u32 size, then u32 count). Chunk
names are written `#NAME#`; the bytes after the name's NUL are garbage (0xCD). The writer
holds at most 50 chunks per file. Strings below are fixed-size, NUL-terminated, garbage
after the NUL.

| Path (relative to `Save/`) | Chunks | Written |
|---|---|---|
| `Info.bin` | `CURRENT`: u16 index of the last selected player | whenever a player is selected |
| `InfoPara.bin` | `FILTER`: u32 texture filter, 0 = point, else bilinear (D3D mag/min filter 1 / 2) | at startup if missing, at exit if changed |
| `User_<i>/Info.bin` | `USERINFO`: char name[64], u16 unit number reached | player created (unit 0); after each save (unit of the save) |
| `User_<i>/Gamesave.<n>` | one saved game, below | OptionSave OK |
| `DbgInfo.txt` | a debug text log | ignore |

`<i>` is the player index (decimal, from 0), `<n>` the save slot (decimal). The original
also appends `File Copy: <dir>\*.*` to the installer's `Install.log` when it creates a
player folder (uninstaller bookkeeping; skip).

**Players.** At startup every folder `User_*` is scanned; the index is the number after
the last `_`, and the name comes from its `USERINFO`. Up to 99 players. `CURRENT` from
`Info.bin` names the player whose save list is loaded before the players screen. A new
player gets index = the current number of players (not the first free index), a folder,
and `USERINFO` with unit 0. The unit number is read only by the gallery, which unlocks paintings
from it (`ui.md`, E-0452).

**Saves of a player.** Slots 0..99 exist in the file name (a slot above 99 is saved as 0);
the lists handle 0..98. The save list is rebuilt by scanning `Gamesave.*` in the player's
folder: slot = the number after the last `.`, name = **the file's first 64 bytes**. That
works because `GAME` is always the first chunk and its first field is the name; an engine
should parse the chunk instead. "Newest" = the file with the greatest last-write time.

## Saved game: `Gamesave.<n>` (E-0182, E-0183)

Chunks in write order. The unit decides which scene chunks it writes (all units write
the base set; some add one chunk). The sample (U01 at the hand-over, 10,552 bytes) has
`GAME SCENE CURSOR ACTIONS CAMERA OBJECTS ANIMATIONS TRAIN_CHANGED PORTEF`.

| Chunk | Size | Payload |
|---|---:|---|
| `GAME` | 86 | char name[64] (the save's name); u16 unit number; char scene[20] (`U01.X3D`) |
| `SCENE` | 4 | u8 r, g, b: current ambient light; u8 `unk_pad` |
| `CURSOR` | 38 | char image[30]; u32 mode; u32 pending (below) |
| `ACTIONS` | 2048 + 256·k | u32 exhausted[256]; u32 runs[256] (both indexed by action id); then, for every action id 0..255 that has an action in this unit, in id order, its current condition text, 256 bytes |
| `CAMERA` | 48 | f32 x, y, z (eye); u32 `unk_w`; f32 yaw, pitch; f32 sphere radius, sphere Z offset; u32 can move, can turn, collide; f32 eye height |
| `OBJECTS` | 4 + 68·n | as `INFOOBJ.BIN` (`infoobj.ksy`): u32 n, then n hotspot records with their live state |
| `ANIMATIONS` | var. | playback nodes with scripted sub-slot clips (below) |
| `JAUGE` | 42 | only while the gauge runs: char name[30]; u32 visible; u32 duration ms; u32 elapsed ms |
| unit chunk | var. | U01 `TRAIN_CHANGED` 8, U02 `TIMEVENDEUSE` 16, U04 `PARAMS` 12, U07 `PLANCHE` 4 (below) |
| `PORTEF` | 4 + 30·(k+1) | i32 k = index of the last item (−1 = empty); k + 1 item names (`U02_01P`), strip order |

Field notes:

- **CURSOR.** When the app leaves play mode while the cursor holds an item, the cursor
  remembers it: pending = 1, mode = 1 (holding), image = the held cursor image name
  (`U01_04C`); the restore turns it back into a held item and clears pending. Escape
  already puts a held item back in the bar before the save screen opens, so saves
  normally have pending = 0 and the rest uninitialised.
- **ACTIONS.** "Exhausted" and "runs" are the per-id tables of `interaction.md` "Run"
  (conditions `mNN` read "exhausted"). The condition text is the action's current
  condition, which steps 15/16 rewrite to `TRUE`/`FALSE`. Unit U01: 23 condition blocks.
- **CAMERA.** The fields of `movement.md`: can move / can turn gate the arrow keys,
  collide selects the sliding-sphere move, eye height is ground + this.
- **OBJECTS.** The writer re-reads the unit's `INFOOBJ.BIN` and, for each record whose
  object and hotspot exist, overwrites cursor := the object's current cursor kind,
  visible := object not hidden, and, if an animation node has the record's name,
  frame, paused and loop from that node. Name, type and fps stay as in `INFOOBJ.BIN`.
- **ANIMATIONS.** One entry per playback node that has a sub-slot clip (`animation.md`
  "Sub-slots"): only nodes whose name starts with `*` and which hold at least one slot.
  Entry: char node name[64]; u16 slot count c; u16 active slot; then c slots: u16 slot
  (1..15); char path[260] (absolute path of the `.A3D` as loaded, e.g.
  `C:\MonetRun\Data\U01/Anim/U01_02/Action03.A3D`); char clip name[64] (`GiveCard`);
  u32 enabled; u32 paused; u32 loop; u32 ping-pong; u32 backward; f32 frame; f32 fps;
  u32 first frame; u32 last frame; u32 `unk_1cc`, `unk_1d0`. Base-node frames are not in
  this chunk (they are in `OBJECTS`). Entries run to the end of the chunk. Written for every
  node of the scene's node list whose name starts `*` and that has at least one slot clip;
  `unk_1cc`/`unk_1d0` are the clip's own first/last frame saved while a frame-range
  override is active (0xCD otherwise). Reading: find the node by name, re-create each slot
  clip from its path, then set the fields and the active slot; a name not found desyncs
  the rest of the chunk. Nodes made at run time without slot clips (U07's plank) are not
  saved (E-0535, E-0536).
- **JAUGE.** The timed gauge of `u01.md` ("escape timer"); duration = ⌊seconds⌋·1000.
- **Unit chunks.** U01: u32 `train2Loaded`, u32 `onTrain` (`u01.md`). U02: u32
  `callStart`, `callPeriod`, `callOff`, `magpie` (`u02.md`; `callStart` is a raw clock
  value, Q-0092). U04 `PARAMS`: u32 unit `+0x6ec`, `+0x6e8`, `+0x6e4`; U07 `PLANCHE`: u32
  unit `+0x6c8`, the plank-tipped flag (`u07.md`, E-0395; U04's meanings: Q-0103). U00, U03, U05, U06, U33 and U50 write none.

## Saving (E-0182)

`OptionSave` OK with slot s and the edit's text as name:
1. File `Save/User_<player>/Gamesave.<s>` (s > 99 → 0), created or overwritten.
2. `GAME`: name, current unit number, current scene name.
3. The scene's chunks, in the table order above (`SCENE`, `CURSOR`, `ACTIONS`, `CAMERA`,
   `OBJECTS`, `ANIMATIONS`, `JAUGE` if running, then the unit's chunk).
4. `PORTEF` (the inventory strip).
5. Close (table + count), then rewrite the player's `USERINFO` with the unit number.

## Loading (E-0182, E-0183)

`OptionLoad` OK with slot s (also reachable from U01's "caught", `u01.md`):
1. Open `Gamesave.<s>`. Read `GAME`: name, unit number, scene name.
2. Inventory: empty the strip, then add the `PORTEF` items in order.
3. Load the scene by name exactly as a normal scene switch (`boot.md`, `scene.md`: destroy
   the current scene, reset the cursor, create the unit, load the `.X3D`, app mode 0, the
   unit's load hook such as U01's renames), then the unit's start with **a = 0** and the
   save as stream. The base start restores the state (below) and then runs the scene's
   post-load step; unit starts skip their intro on a = 0 (`u01.md` "Entry": no prologue,
   no scripted hand-over; the ambient still starts).
4. Game state: game-started flag off, unit number and scene name from the load,
   "inventory allowed" on.

Restore order inside the unit start (each step skipped when its chunk is absent):
1. `SCENE`: ambient colour.
2. `CURSOR`: remembered held item.
3. `CAMERA`: fields; the camera is placed at the position with the angles, and the
   collision sphere moved there.
4. `OBJECTS`: the hotspots are created from these records instead of `INFOOBJ.BIN`
   (same rules as `interaction.md` "Hotspots"; a hotspot is created if missing).
5. `ANIMATIONS`: per entry, find the node by name; per slot, re-root the path at the data
   folder (the text after the first `Data` + 1 separator, appended to the current data
   root), load the clip into that slot as a scripted clip (`animation.md`), then set its
   paused, loop, ping-pong, backward, frame, fps, first/last and the two unknown fields;
   then the node's active slot.
6. `JAUGE`: name, visible, duration, elapsed; if elapsed > 0 the gauge's start time is
   reset to now, so it resumes with the saved remainder (elapsed = 0: it stays stopped).
7. A pending held item is given back to the cursor.
8. Actions are built from `INFOACT.BIN` (`interaction.md`), then `ACTIONS` overwrites the
   exhausted and runs tables and every action's condition.
9. The unit's chunk (U01 `TRAIN_CHANGED`: `u01.md` step 4 reads it).

Original quirk to keep: each action also has a private run counter that the restore
does not set, and a run writes that counter into the table. After a load an action with
`max_runs` > 1 that had run m times starts counting from 0 again. Exhausted actions stay
exhausted.

## Save screen: frame `OptionSave` (E-0184)

Opened by `SaveOui` on the "Do you want to save?" frame (`ui.md` "Escape").

| id | Class | Rect | What |
|---:|---|---|---|
| 1 | `TIB#` | 0, 0, 640, 480 | background `SaveFond` |
| 2 | `TIB#` | 99, 445, 105, 20 | `SaveRetourD`, hover `SaveRetourH`: `OptionSave3D` |
| 3 | `TIB#` | 281, 445, 85, 17 | `SaveSommaireD`, hover `…H`: `OptionSaveSommaire` |
| 4 | `TIB#` | 452, 445, 26, 16 | `SaveOKN`, hover `SaveOKH`: `OptionSelectSave` |
| 5 | `TIB#` | 561, 445, 60, 18 | `SaveQuitterD`, hover `…H`: `SaveQuit` |
| 10 | `VAS#` | 149, 126, 406, 288 | save slot list |
| 11 | `dES#` | 149, 91, 372, 19 | save name edit, max 40 characters |

- **Edit.** Starts with the text `Save without name` (`Message.txt` line 300); typed
  characters are appended to it (runtime: typing ` A` gave `Save without name A`).
  Clicking a row does not change it.
- **List.** One row per slot 1..98 (slot 0 is never shown), in slot order, text
  `"<s+1> - <name>"`, or `"<s+1> - Empty"` for a free slot (`Message.txt` line 1). The
  selected slot starts as the first free one (1 if all are free) and the list scrolls to
  it; a click selects the row under the pointer.
- **OK** (`OptionSelectSave`): save to the selected slot with the edit's text (Saving),
  rebuild and redraw the list, and switch buttons 2, 3, 5 from their `…D` bitmaps to
  `…N` (runtime: dim before the first save, bright after).
- `OptionSave3D` (Back to the game): close the frame, back to play. `OptionSaveSommaire`
  (Main menu): the Option menu. `SaveQuit` (Quit): the quit confirmation
  `OptionQuitter`. They react while dimmed (E-0545).

## Load screen: frame `OptionLoad` (E-0184)

| id | Class | Rect | What |
|---:|---|---|---|
| 1 | `TIB#` | 0, 0, 640, 480 | background `LoadFond` |
| 2 | `TIB#` | 511, 445, 27, 16 | `LoadOKN`, hover `LoadOKH`: `OptionSelectGame` |
| 3 | `EIV#` | 131, 446, 82, 15 | hover `LoadSomH`: `OptionScreen` (Main menu) |
| 10 | `AOL#` | 133, 83, 444, 320 | saved games |

- **List.** Only the used slots, in slot order, `"<s+1> - <name>"`; nothing selected at
  first; a click selects a row (row r = the r-th used slot).
- **OK** (`OptionSelectGame`): if a row is selected, load that slot (Loading), close the
  frame and return to play. Runtime: it restored U01 at the saved hand-over (camera
  −466.36, −452.495, 30.48, yaw 4.7, pitch π/2; the mayor holding out the card).
- The OK bitmap is switched between `LoadOKN` and `LoadOKM` as the selection changes
  (runtime: dim with no selection, bright with one); the Option menu greys "Load a game"
  when the player has no save (`ui.md`).

## Lists (E-0184, E-0185, E-0600)

The three list classes (`#SCR` subclasses `#LOA` = `AOL#`, `#SAV` = `VAS#`, `#USc` =
`cSU#`) draw the same way:
- Rows 32 px high from the top of the view; the text area is the view width minus 38 px
  (the scroll bar lives in the rest); rows beyond the view height are not drawn and the
  list scrolls by rows.
- Each row: text centred horizontally and vertically in (0, 32·row, w − 38, 32), single
  line, GDI, colour (247, 196, 90) for the selected row and (135, 186, 235) otherwise,
  on the frame background (the list surface is colour-keyed, key RGB (32, 32, 80)).

**Scroll bar** (E-0600). Scroll position p (the top row), 0 ≤ p ≤ max, max = rows −
⌊view h / 32⌋ (players: player count − 9; saves: 98 − 9 = 89; loads: used saves − 10).
With R the view rect, up = down = 33 (`fra.ksy` `scroll.unk_a`, `unk_b`), track length
L = R.h − 66, f = L / max (float), bar width w_b and thumb height h_t from the bitmaps:
- **Draw**, only when max > 0 (players list: max ≥ 0; with max = 0 its thumb position is
  undefined, so draw the bar only): bitmap `name_a` (`UserASC` 29×288, `SaveAsc` 29×288,
  `LoadASC` 34×320: the whole bar with both arrows, as tall as the view) at
  (R.right − w_b, R.top); bitmap `name_b` (`UserBoule`/`SaveBoule` 29×13, `LoadBoule`
  34×14) at (R.right − w_b, trunc(R.top + 33 + p · f − ⌊h_t / 2⌋)). Both are blitted
  like the `LIH@` highlights (same blit flags).
- **Press** (left button down, only when max > 0), inside the column
  R.right − w_b ≤ x < R.right, first match wins: y < R.top + 33 → p − 1 (if p > 0);
  y ≥ R.bottom − 33 → p + 1 (if p < max); within ⌊h_t / 2⌋ of the thumb centre
  c = trunc(R.top + 33 + p · f) → start dragging; elsewhere between the arrows → one page
  (page = ⌊R.h / 32⌋ rows; players and saves 9, loads 10) up if y ≤ R.top + 33 + p · f,
  else down, clamped to 0..max. A press outside the column goes to the rows.
- **Drag** (mouse moves with the button down after a thumb press): d = y − R.top − 33,
  s = trunc(L / max) px per row, p = d div s, plus 1 when d mod s > s div 2, clamped to
  0..max. Releasing the button ends the drag.
- Every change of p redraws the rows from the new top.

**Players list** (`OptionUser` id 10): one row per existing player in index order, text
`"<n> - <name>"` where n is the row's position on screen counted from the scroll
position: the first visible row is p + 1, the next p + 2, … (not the player's `User_<i>`
index; E-0601). Scrolled by p, the rows show the used player slots from slot p on (the
original starts the slot walk at slot index p, so with gaps in the slots a scrolled list
can start with a player that was already above; parity keeps that). A click selects the row and copies that
player's name into the name edit (id 11); it does not select the player: OK (or Enter)
does (`ui.md` `SelectUser`). Typing in the edit selects the row whose name matches and
switches the OK bitmap (`UserOKM` with text, `UserOKN` when empty). The edit starts with
`Player's name` (`Message.txt` line 301) and, like the save edit, appends typed
characters (the sample player created by typing `Name` is `Player's nameName`).

## Engine notes

- Everything here is in 640×480 frame pixels; the lists draw text, so pick a font close to
  Arial 12 pt (`ui.md` "Text").
- Keep the restore order; in particular apply `ACTIONS` after the actions exist and
  restore `OBJECTS` before the animation slots.
- Map the original's slots onto ScummVM save slots 1..98 if importing; the `GAME` name is
  the save description.
