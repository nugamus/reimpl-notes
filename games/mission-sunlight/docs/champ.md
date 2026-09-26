# champ — the wheat field with crows (scene 12)

Scene index 12 (`champ.BFG`, E-0306). Callbacks: init `0x41e383`, per frame `0x41e5de`
(E-0334). Entered from the museum painting `m04_02` (Auvers group), from the garden
(`jardin`, 11) and from the church (`eglise`, 13). Completion: zones 22 and 24
(`DAT_004abb64`, `DAT_004abb6c`, E-0311); entry movie `champ`, return movie `champr`
(E-0309, E-0310).

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum (0 → 12) | 0x85c, 0xfd, 0x8de | 0xfa6, 0xd6, 0 |
| jardin (11 → 12) | 0x979, 0xa0, −0x1108 | 0xfa6, 0xf95, 0 |
| eglise (13 → 12) | −0x3621, −0x20a, 0x26f5 | 0xfa6, 0x4d9, 0 |

## Scene data (E-0334)

Object table at `0x4ab750`, 4 entries (count `0x4ab748`), none hidden:

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `faux` | 0xff; entry sets 4 or 0xff | the scythe |
| 1 | `coclicot` | 3 | zone 22 |
| 2 | `gun` | 2 | item 32 |
| 3 | `sabots` | 3 | zone 24 |

Animations (table `0x4ab848`, E-0318; `0x41e4cc`, frames by the elapsed ticks):
0 `korbeaux.3da` on `corbopere` (the crows), stops at its end; 1 `faux.3da` on
`animfaux01`, at its end `faux` cursor 0xff, `DAT_004abcf8` := 1, stop.
Static sounds (E-0320, `0x41e250`): `champ` (ambient, looping), `faux`, `pistolet`,
`corbeaux`.

## Entry (`0x41e383`)

Hide `faux`; show it again if the sunflower count (`DAT_004abbd4`) is exactly 4. Scythe
used (`DAT_004abcf8`): pose track 1 at its last frame, `faux` cursor 0xff; else `faux`
cursor 4. Gun taken (`DAT_004abcf4`): hide `gun`. Zone 22 done → `coclicot` 0x3c; zone 24
done → `sabots` 0x3c. `champ` starts looping.

## Every frame (`0x41e5de`)

| Object | Condition | Effect |
|---|---|---|
| `coclicot` | — | zone 22 |
| `sabots` | — | zone 24 |
| `faux` | scythe not used | start track 1, `faux` plays |
| `gun` | — | hide, item 32, bar, `pistolet` plays, `DAT_004abcf4` := 1, start track 0 (crows), `corbeaux` plays |

Hover: cursor types 2, 3, 4, 0x3c (E-0315), no distance limit.

**Walking out** (checked every frame after the animations):
camera x (`DAT_00651352`) < −16000 → previous 12, target 13 (church);
camera z (`DAT_00651356`) < −0x157c → previous 12, target 11 (garden).

## Flow

| # | Goal | Achieved by | Precondition | Unlocks |
|---:|---|---|---|---|
| 1 | The gun | click `gun` | — | item 32, the crows fly |
| 2 | The scythe | click `faux` | visible only with exactly 4 sunflowers at entry | `DAT_004abcf8` |
| 3 | Zones 22, 24 | `coclicot`, `sabots` | — | completion (E-0311) |

**Exits:** walk west (x < −16000) → church (13); walk south (z < −0x157c) → garden (11);
museum exit (E-0310) → museum at the wheat-field painting, `champr` if zones 22 and 24
are done.

**State** (saved block, E-0312): `DAT_004abcf4`, `DAT_004abcf8` (read/written),
`DAT_004abbd4`, `DAT_004abb64`, `DAT_004abb6c` (read).
