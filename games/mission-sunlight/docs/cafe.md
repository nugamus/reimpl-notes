# cafe — the Night Café interior (scene 5)

Scene index 5 (`cafe.BFG`, E-0306). Callbacks: init `0x41b77d`, per frame `0x41bbcf`
(E-0331). Entered from the museum painting `m03_01` (Arles group) or from the terrace
(`terrasse`, scene 10). Completion: zones 4, 5 and 6 (`DAT_004abb1c`, `DAT_004abb20`,
`DAT_004abb24`, E-0311); until then the museum plays `cafe` on the way in (E-0309), and
`cafer` on the way out once they are all done (E-0310).

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum (0 → 5) | 0x189, −0xaf, −0x88 | 0xf88, 0x5c, 0 |
| terrasse (10 → 5) | 0x651, −0x5a, −0x74 | 0xf88, 0xecc, 0 |

## Scene data (E-0331)

Object table at `0x4aa050`, 15 entries of 0x3c bytes (count `0x4aa048`), none hidden:

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `ke` | 4 (finger) | the billiard cue |
| 1 | `gant` | 3 (zone) | zone 5 |
| 2 | `briket` | 2 | item 6 |
| 3 | `clef` | 4 | the key, carried (E-0317) |
| 4 | `carte` | 2 | item 5 |
| 5 | `pomme` | 2 | none in the code |
| 6 | `barporte` | 0xff | the bar door (key target) |
| 7 | `ombre` | 0xff, 2 after the cue | item 16 |
| 8 | `orloge` | 2 | the clock, item 19 |
| 9 | `lampe4` | 3 (zone) | zone 4 |
| 10 | `theiere` | 2 | item 25 |
| 11 | `pichet` | 2 | item 9 |
| 12 | `mirroir` | 0xff / 3 by position | zone 6 |
| 13, 14 | `porte01`, `porte02` | 6 | exits to the terrace |

Animations (table `0x4aa3d8`, E-0318): 0 `billard.3da` on `ke`, advanced by the elapsed
ticks; at its end `ke` cursor 0xff, `ombre` cursor 2, `DAT_00650fc4` := 1 (cue played),
stop. 1 `portebar.3da` on `barporte`, one frame per call; at its last frame it stays
posed there and stops (`0x41ba80`).

Static sounds (E-0320, `0x41b5a0`): `billiard`, `cafe_int` (ambient, looping from the
entry), `pendule`, `serrure`, `tictac`. Textures preloaded: `MIRROIR1`, `MIRROIR2`,
`MIRROIR3` (E-0319); `mirroir`'s node flags are set to 0xf by `0x435930`.

## Entry (`0x41b77d`)

- Clock taken (`DAT_004abcb8`): hide `orloge`. Else start `tictac` looping, `orloge`
  cursor 0xff.
- Taken items hidden: `briket` (`DAT_004abca8`), `carte` (`DAT_004abca4`), `pichet`
  (`DAT_004abcac`), `theiere` (`DAT_004abcb4`).
- Bar door opened (`DAT_004abcb0`): hide `clef`, pose track 1 at its last frame.
- Shadow taken (`DAT_004abca0`): show `ke`, hide `ombre`, `ke` cursor 0xff, pose track 0
  at its last frame. Else `ke` cursor 4, `ombre` cursor 0xff.
- Clock state: `DAT_004aa4c8` := 1 (running), `DAT_00650fd4` = `DAT_00650fd8` =
  `DAT_00650fdc` := 0, `DAT_00650fc4` := 0; UV callback `0x41b613` applied to `orloge`
  with state 0 (no change).
- Zones done: 4 → `lampe4` cursor 0x3c, 5 → `gant` 0x3c, 6 → `mirroir` 0x3c.

## Every frame (`0x41bbcf`)

**Carrying the key** (`DAT_00502734` = 1, E-0317): cursor `(` (closed hand). A click on
`barporte` while the carried object is `clef`: arrow back, `serrure` plays, the key stays
hidden, track 1 starts, `DAT_004abcb0` := 1, autosave (`0x42f873`, E-0316). A click
anywhere else: the key is shown again. Either click ends the carry.

**Clicks** with the arrow:

| Object | Condition | Effect |
|---|---|---|
| `gant` | — | zone 5 |
| `mirroir` | its cursor type 3 or 0x3c this frame | zone 6 |
| `lampe4` | — | zone 4 |
| `orloge` | clock state `DAT_00650fdc` = 3 | stop `pendule` and `tictac`, hide, item 19, bar opens, `DAT_004abcb8` := 1 |
| `briket` | — | hide, item 6, bar, `DAT_004abca8` := 1 |
| `theiere` | — | hide, item 25, bar, `DAT_004abcb4` := 1 |
| `carte` | — | hide, item 5, bar, `DAT_004abca4` := 1 |
| `pichet` | — | hide, item 9, bar, `DAT_004abcac` := 1 |
| `ke` | cue not played (`DAT_00650fc4` = 0), track 0 stopped, `ke`'s hidden word 0, `DAT_004abca0` = 0 | `billiard` plays, track 0 starts |
| `ombre` | cue played, track 0 stopped | hide, item 16, bar, `ombre`'s hidden word := 1, `DAT_004abca0` := 1 |
| `clef` | — | carry it: `DAT_00502734` := 1, hide, `DAT_00502a80` := its handle |
| `porte01`, `porte02` | — | previous 5, target 10 (terrace) |

Hover: cursor types as E-0315 (types 2, 3, 4, 6, 0x3c), no distance limit.

**The mirror**, after the animations: `mirroir`'s cursor type := 0x25 (the arrow), then by
the camera's z (`DAT_00651356`) its texture is swapped (E-0319) from the current one
(name kept in `0x650fe0`) to:

| z | Texture | Cursor type |
|---|---|---|
| ≥ 0xaf1 | `MIRROIR3` | 0x25 |
| 0x8fd .. 0xaf0 | `MIRROIR2` | 0x25 |
| 0x7d1 .. 0x8fc | `MIRROIR1` | 0x25 |
| 0x321 .. 0x7d0 | `MIRROIRG` | 3, or 0x3c if zone 6 done |
| 0x1f5 .. 0x320 | `MIRROIR1` | 0x25 |
| 0x72 .. 0x1f4 | `MIRROIR2` | 0x25 |
| < 0x72 | `MIRROIR3` | 0x25 |

So zone 6 can be entered only from z 0x321..0x7d0.

**The clock**: `DAT_00650fd8` += elapsed; when it is more than 199 ticks past
`DAT_00650fd4` while `DAT_004aa4c8` = 1 and the clock is not taken, the state
`DAT_00650fdc` goes up by one, `DAT_00650fd4` := `DAT_00650fd8`, and `0x41b613` is applied
to every UV of `orloge`: state 1 u += 0x800000 (16.16: half the texture), state 2 u −= 0x800000 and v += 0x800000,
state 3 u += 0x800000, running := 0, `pendule` plays once, `orloge` cursor := 2. The clock
becomes takeable after 3 × 200 ticks.

## Flow

| # | Goal | Achieved by | Precondition | Unlocks |
|---:|---|---|---|---|
| 1 | Loose items | click `briket`, `carte`, `pichet`, `theiere` | — | items 6, 5, 9, 25 |
| 2 | The clock | wait 600 ticks in the scene, click `orloge` | state 3 | item 19 |
| 3 | The cue | click `ke` | — | `ombre` takeable |
| 4 | The shadow | click `ombre` | 3 done | item 16 |
| 5 | The bar door | carry `clef` onto `barporte` | — | `DAT_004abcb0`, autosave |
| 6 | Zones 4, 5, 6 | `lampe4`, `gant`, `mirroir` (from the right z) | — | completion (E-0311) |

**Exits:** `porte01`/`porte02` → terrace (10); museum exit (E-0310) → museum at the café
painting, `cafer` if zones 4, 5, 6 are done.

**State read/written** (saved block, E-0312): `DAT_004abca0`, `DAT_004abca4`,
`DAT_004abca8`, `DAT_004abcac`, `DAT_004abcb0`, `DAT_004abcb4`, `DAT_004abcb8`; read
`DAT_004abb1c`, `DAT_004abb20`, `DAT_004abb24`. Scene-local: `DAT_00650fc4`,
`DAT_00650fd4`, `DAT_00650fd8`, `DAT_00650fdc`, `DAT_004aa4c8`, `0x650fe0`.
