# hopiint — the hospital ward in Arles (scene 8)

Scene index 8 (`hopiint.BFG`, E-0306). Callbacks: init `0x425541`, per frame `0x42579a`
(E-0360). Reached from the museum (painting `m03_04`, entry movie `hopi`, return movie
`hopir`, E-0309, E-0310) and from the hospital courtyard (`hopiext`, scene 2). Complete when
zones 13, 14 and 15 are done (`DAT_004abb40`, `DAT_004abb44`, `DAT_004abb48`, E-0311); zone 14
is not entered from this scene. Generic mechanics are in `engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 8, 8 → 8) | -67, -78, -345 | 0xfc4, 0x011, 0 |
| hopiext (2 → 8) | -1318, -11, 8435 | 0xfc4, 0x5c4, 0 |

## Scene data (E-0360)

Object table at `0x4acb08`, 9 entries of 0x3c bytes (count `0x4acb00`): name, cursor type
at +0x32, handle at +0x34, start-hidden word at +0x38 (none hidden).

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `ARMOIRE` | 0xff; 4 at entry until opened | the wardrobe, opens once |
| 1 | `LAMPE` | 2 | item 21 |
| 2 | `BONNET` | 2 | item 20 |
| 3 | `CROIX` | 2 | item 23 |
| 4 | `BOUGIE` | 2 | item 22 |
| 5 | `MIRROIRVG` | 3; 0x3c once zone 15 is done | zone 15 |
| 6 | `FOU` | 3 | zone 13 |
| 7 | `PLAK` | 6 | exit to `hopiext` |
| 8 | `ECHIK` | 3; 0x3c once zone 13 is done | zone 13 |

Animation table at `0x4acd28`, 2 entries of 0x78 bytes (count `0x4acd24`, E-0318):

| # | Track | Node | Started by | On end |
|---:|---|---|---|---|
| 0 | `hopiint.3da` | `ARMOIRE` | click `ARMOIRE` | stops; `DAT_004abd00` := 1 (wardrobe open), `ARMOIRE` cursor 0xff |
| 1 | `fou.3da` | `FOU` | every frame: plays while the camera is within 1500 of `ECHIK` | loops (frame back to 1) |

Track 0 advances by the elapsed ticks; the "within 1500" test writes track 1's playing word
directly, so it stops (holding its pose) as soon as the camera is 1500 or more away
(`0x42579a`, `_DAT_004ace14`, constant at `0x4a253c` = 1500.0).

Static sounds (`0x4254f2`, E-0320): `hopi_int` (ambient, looped from entry), `armoire`,
`fou` (created, not played by this code). No box sets of its own (only `BOX.3DI`).

Distances: `d` below is `√(x² + z²)` of the object's position read by `0x436200`, the same
measure the museum uses for its paintings.

## Entry (`0x425541`)

1. Resolve handles, hide start-hidden objects, load the tracks and sounds, loop `hopi_int`.
2. Wardrobe open (`DAT_004abd00` = 1): pose track 0 at its last frame, `ARMOIRE` cursor
   0xff; else `ARMOIRE` cursor 4.
3. Hide each item already taken: `BONNET` (`DAT_004abd0c`), `LAMPE` (`DAT_004abd08`),
   `CROIX` (`DAT_004abd04`), `BOUGIE` (`DAT_004abd10`).
4. Zone 13 done → `ECHIK` cursor 0x3c; zone 15 done → `MIRROIRVG` cursor 0x3c.

## Flow

Clicks need the arrow cursor and an object of the table (E-0315); the first matching line
wins.

| Click | Precondition | Effect |
|---|---|---|
| `ARMOIRE` | `DAT_004abd00` = 0 | play `armoire` once, start track 0 |
| `BOUGIE` | — | hide it, cursor := item 22, open the inventory bar (E-0316), `DAT_004abd10` := 1 |
| `LAMPE` | — | hide, item 21, bar, `DAT_004abd08` := 1 |
| `BONNET` | — | hide, item 20, bar, `DAT_004abd0c` := 1 |
| `CROIX` | — | hide, item 23, bar, `DAT_004abd04` := 1 |
| `MIRROIRVG` | — | enter zone 15 (E-0312) |
| `FOU` or `ECHIK` | — | enter zone 13 |
| `PLAK` | `d` < 3000 | leave for `hopiext` (8 → 2) |

Hover: `PLAK` shows its cursor only when `d` ≤ 3000 (`0x4a2538` = 3000.0); the others show
their table cursor.

Nothing ties the four items to the wardrobe in code: they are clickable whenever the pick
reaches them.

**State written:** `DAT_004abd00`, `DAT_004abd04`, `DAT_004abd08`, `DAT_004abd0c`,
`DAT_004abd10` (all in the saved block `0x4aba40`, E-0312). **Read:** those, plus
`DAT_004abb40`, `DAT_004abb48`.

**Exits:** `PLAK` → `hopiext`; Backspace or the corner arrow → museum (E-0310).
