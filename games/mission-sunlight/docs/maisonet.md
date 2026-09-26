# maisonet — the cottage at Nuenen (scene 3)

Scene index 3 (`maisonet.BFG`, E-0306). Callbacks: init `0x4279a3`, per frame `0x427e04`
(E-0362). Reached from the museum (painting `m01_02`, entry movie `maisa`, return movie
`maisr`, E-0309, E-0310) and from the potato eaters' room (`mangeurs`, 4). Complete when zone
1 is done (`DAT_004abb10`, E-0311). Generic mechanics are in `engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 3, 3 → 3) | 1149, 141, -1491 | 0, 0x113, 0 |
| mangeurs (4 → 3) | 7310, 183, 5921 | 0, 0xb39, 0 |

## Scene data (E-0362)

Object table at `0x4ad390`, 7 entries of 0x40 bytes (count `0x4ad388`): name, cursor type
at +0x32, handle at +0x38, start-hidden word at +0x3c (none hidden).

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `poule` | 0xff | the hen (animated when approached) |
| 1 | `pelle` | 4; 0xff once used | the spade: digs |
| 2 | `oiso` | 0xff | the bird |
| 3 | `terre` | 0xff; 2 after digging | the dug earth: item 1 |
| 4 | `plume` | 2 | item 2 |
| 5 | `nid` | 3; 0x3c once zone 1 is done | zone 1 |
| 6 | `porte04` | 6 | door to `mangeurs` |

Animation table at `0x4ad558`, 4 entries of 0x78 bytes (count `0x4ad550`, E-0318):

| # | Track | Node | Started by | Step | On end |
|---:|---|---|---|---|---|
| 0 | `poule2.3da` | `poule` | camera within 2000 of `poule` | elapsed | holds the last frame; `DAT_004abc74` := 1 (hen done) |
| 1 | `pelle.3da` | `pelle` | click `pelle` | elapsed | holds the last frame; shows `terre` unless taken; `DAT_004abc84` := 1 (dug); `pelle` cursor 0xff, `terre` cursor 2 |
| 2 | `oisaller.3da` | `oiso` | camera within 5000 of `nid` | elapsed / 2 (at least 1) | `DAT_004abc94` := 1; track 2 stops at frame 1, track 3 starts |
| 3 | `oisrturn.3da` | `oiso` | end of track 2 | elapsed / 2 (at least 1) | track 3 stops, track 2 restarts from frame 1 |

Tracks 2 and 3 alternate forever once started: the bird flies off and back
(`0x427b98`).

Static sounds (`0x427870`, E-0320): `ferme` (ambient, looped), `poule`, `pelle`, `oiseau`.
No box sets of its own.

Distances: `d` is `√(x² + z²)` of the object's position read by `0x436200` (as in the
museum). Constants: 2000.0 at `0x4a2548`, 5000.0 at `0x4a2544`.

## Entry (`0x4279a3`)

1. Resolve handles, load tracks.
2. Hide `terre` if taken (`DAT_004abc68`), `plume` if taken (`DAT_004abc64`).
3. Bird flown (`DAT_004abc94`): track 2 playing, track 3 stopped.
4. Hen: `DAT_004abc74` = 0 → pose track 0 at frame 1; else at its last frame.
5. Spade: not used (`DAT_004abc84` = 0) → pose track 1 at frame 1 and hide `terre`; used →
   pose track 1 at base + (track 0's length) − 1 (the code reads track 0's length here, not
   track 1's) and `pelle` cursor 0xff.
6. Hide `terre` again if taken; zone 1 done → `nid` cursor 0x3c.
7. Load the sounds, loop `ferme`.

## Flow

Clicks need the arrow cursor and an object of the table (E-0315):

| Click | Precondition | Effect |
|---|---|---|
| `plume` | — | hide it, cursor := item 2, open the bar (E-0316), `DAT_004abc64` := 1 |
| `pelle` | `DAT_004abc84` = 0 | play `pelle` once, start track 1, show `terre` |
| `terre` | — | hide it, item 1, bar, `DAT_004abc68` := 1 |
| `nid` | — | enter zone 1 (E-0312) |
| `porte04` | `d` < 5000 | leave for `mangeurs` (3 → 4) |

`terre` is hidden until the spade is used, so the pick cannot reach it before. Hover:
`porte04` shows its cursor only when `d` ≤ 5000.

**Automatic triggers (every frame):**

| Trigger | Condition | Effect |
|---|---|---|
| Hen | track 0 stopped at frame 1, `DAT_004abc74` = 0, `poule` within 2000 | play `poule` once, start track 0 |
| Bird | tracks 2 and 3 stopped, `DAT_004abc94` = 0, `nid` within 5000 | play `oiseau` once, start track 2 |

**State written:** `DAT_004abc64`, `DAT_004abc68`, `DAT_004abc74`, `DAT_004abc84`,
`DAT_004abc94`. **Read:** those, `DAT_004abb10`.

**Exits:** `porte04` → `mangeurs`; Backspace or the corner arrow → museum (E-0310).
