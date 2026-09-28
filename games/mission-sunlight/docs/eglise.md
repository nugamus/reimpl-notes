# eglise — the church at Auvers (scene 13)

Scene index 13 (`eglise.BFG`, E-0306). Callbacks: init `0x4242ed`, per frame `0x424467`
(E-0335). Entered from the museum painting `m04_03` (Auvers group), from the garden
(`jardin`, 11) and from the wheat field (`champ`, 12). Completion: zone 23
(`DAT_004abb68`, E-0311); entry movie `eglise`, return movie `eglr` (E-0309, E-0310).

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum (0 → 13) | −0x1c15, 0x322, 0x66 | 0xd2, 0xeac, 0 |
| jardin (11 → 13) | −0x4b79, 0x349, 0x5bbd | 0, 0x673, 0 |
| champ (12 → 13) | −0x9c4, −0x27a, 0x180 | 0x3c, 0xccf, 0 |

## Scene data (E-0335)

Object table at `0x4ac408`, 3 entries (count `0x4ac400`), none hidden: `cerf` (cursor 2,
the kite, item 33), `gerbe` (2, the sheaf, item 34), `eglise10` (3, zone 23).
Animation table `0x4ac4c0`: `eglise.3DA` on `cerf`, playing from the start (its playing
word is 1 in the EXE's data); `0x4243cb` adds half the elapsed ticks per frame and resets
the frame to 1 when it **equals** the length (E-0318). Static sound (E-0320, `0x4241f0`):
`eglise`, the ambient, looping from the entry.

## Entry (`0x4242ed`)

`cerf` hidden if `DAT_004abcd8` = 1 (a new player starts with 1, E-0369; the garden clears it when the kite flies, `jardin.md`) or
`DAT_004abcdc` = 1 (kite taken); `gerbe` hidden if `DAT_004abce0` = 1. Zone 23 done →
`eglise10` cursor 0x3c.

## Every frame (`0x424467`)

| Object | Effect |
|---|---|
| `eglise10` | zone 23 |
| `gerbe` | hide, item 34, bar (E-0316), `DAT_004abce0` := 1 |
| `cerf` | hide, item 33, bar, `DAT_004abcdc` := 1 |

Hover: cursor types 2, 3, 4, 0x3c (E-0315), no distance limit.

**Walking out:** camera x > −2000 → previous 13, target 12 (wheat field); camera z >
0x5fb4 → previous 13, target 11 (garden).

## Flow

| # | Goal | Achieved by | Unlocks |
|---:|---|---|---|
| 1 | The sheaf | click `gerbe` | item 34 |
| 2 | The kite | click `cerf` (if the garden has not removed it) | item 33 |
| 3 | Zone 23 | click `eglise10` | completion (E-0311) |

**Exits:** walk east (x > −2000) → wheat field (12); walk north (z > 0x5fb4) → garden
(11); museum exit (E-0310) → museum at the church painting, `eglr` if zone 23 is done.

**State** (saved block): `DAT_004abcd8` (read), `DAT_004abcdc`, `DAT_004abce0`
(read/written), `DAT_004abb68` (read).
