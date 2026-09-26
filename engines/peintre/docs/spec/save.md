# Saves and players

Three kinds of files in `<Target>\SAVE\` (`boot.md` "Data root"), all little-endian, written
with the Cryo file library (`wb`) or Win32: the player list `USERS.BIN`, one resume file
`GGAME<p>.BIN` per player and up to 35 game saves `GAME<pp><ss>.BIN` per player. `p` is the
player's index in `USERS.BIN` (`%u` / `%d`: no padding), `pp`/`ss` two-digit player and slot.
Layouts: `docs/formats/users.ksy`, `game.ksy`, `ggame.ksy`. The corpus has no save file, so
there is no validator (E-0432).

## USERS.BIN (E-0402)

`u32 count` (0..5), then `count` records of 40 bytes: `char name[32]` (NUL-terminated,
at most 20 characters typed), `i32 volume` (DirectSound attenuation, 0 = full, -5000 =
silent; `ui.md` "Option menu"), `u32 view_size` (0..3 = 640×480, 512×384, 400×300,
320×240). Read at start (0x41889c; a missing file is 0 players), written after the
player-name screen (0x418966) and on Quit. A new player gets volume 0 and size 0.

## Integrity check (E-0424)

At start (`Users_CheckSessions` 0x41861d), for each player p whose `GGAME<p>.BIN` does not
exist: delete `GAME<pp><00..34>.BIN`, show the message "'<name>' previous session was not
properly closed: User record has been discarded from database." (title "Users database
integrity"), remove the record and shift the later records down one index. The later
players' files are not renamed, so after a removal they are read under their new index
(original behaviour).

A new player (and a name that replaces one of 5 players) first loses that index's
`GGAME<p>.BIN` and `GAME<pp><00..34>.BIN` (0x4187ba).

## GAME<pp><ss>.BIN — game save (E-0419, E-0421, E-0422)

1,132 bytes: the 3D state block (0x36C bytes) then the 2D block (0x100 bytes).

- **Written** by the 2D shell only (`Save_WriteGame` 0x40ff77, state 0x21), after an object
  was placed and its sequence ended, or after a sunflower was won, or at the end of zone 0.
  The slot is the **id of the object just used** (0..34). Before writing, the held flags
  are copied into the 3D block (+0x40) and into the 3D side's live flags (0x42eede).
  An existing file is overwritten.
- **Listed** by the option menu's Load page: slots 1..34 of the current player that exist,
  sorted by last-write time, oldest first (`Save_ListGames` 0x40e78a). Slot 0 (zone 0) is
  never listed.
- **Loaded** by `Load3DGame(pp * 100 + ss)` (0x42ef0f, format `%sSAVE\GAME%04d.BIN`): a file
  larger than 0x800 bytes is ignored. It restores both blocks and the 3D fields below, clamps the sunflower byte, sets the player's view size from +0x00, stops
  the 3D timer and enters the saved zone (`Entry2D` with +0x3E): a game always resumes in
  the 2D zone where it was saved.

## GGAME<p>.BIN — resume file (E-0420)

1,136 bytes: `u32 in_2d` then the same two blocks.

- **Written** (`Save_WriteGGame` 0x410153) on Quit from the option menu (`in_2d` = 1 when
  quitting from a 2D zone, 0 from 3D), on entering zone 21 (0), and by four 3D scene
  events (0x42f873, called from 0x41bbcf, 0x426171, 0x429dd6, 0x42d489; 0).
- **Read** at start for a known player (`Load3DGGame` 0x42f111, `%sSAVE\GGAME%d.BIN`): same
  restore as a game save, but it does not enter 2D itself; `in_2d` = 1 makes the end of
  the intro enter the saved zone, 0 starts the 3D world (`boot.md` step 9).

## 2D block (0x100 bytes, 0x40ff77 / 0x40fed7)

| Offset | Type | Content |
|---|---|---|
| 0x00 | u32[25] | zone `done` flags, zones 0..24 (`ui.md` zone table) |
| 0x64 | u32[35] | object `placed` flags, objects 0..34 |
| 0xF0 | u32[4] | sunflower counters, indexed by the zone's `counter` field (0: zone 0; 1: A01/A11; 2: A03/A13; 3: A04/A14) |

## 3D block (0x36C bytes, image of 0x4aba40)

Owned by the 3D side (world spec); the fields the save and 2D glue touch (0x42f755,
0x42f873, 0x42edef, 0x42f2c2, `Load3DGame`, `Load3DGGame`):

| Offset | Type | Content |
|---|---|---|
| 0x00 | u8 | view size (copied to the player record on load) |
| 0x08, 0x0C | u32 | set to 1 when leaving zone 0 |
| 0x1C | u32 | 1 after leaving zone 21 (end sequence running) |
| 0x24 | i32[3] | the 3D's three s16 at 0x651346 (restored to 0x5b7fb0) |
| 0x30 | i32[3] | the 3D's three s16 at 0x651352 (restored to 0x5b7f80) |
| 0x3C | u8 | 3D byte 0x4e3144 (set to 0 by RetourM, Q-0251) |
| 0x3D | u8 | 3D byte 0x4e3140 |
| 0x3E | u8 | the zone the player is in / last entered |
| 0x40 | u32[35] | object held flags (the inventory) |
| 0xCC | u32[25] | zone solved (set when the zone's counter rose) |
| 0x194 | u8 | the counter of the last zone's chapter; on load reset to 0 when 3 and +0x1A0 = 0, or 15 and +0x1A4 = 0 |
| 0x1A0, 0x1A4 | u32 | tested by that reset |

Everything else is opaque here (Q-0252).
