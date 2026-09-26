# hopiext — the hospital courtyard at Arles, outside (scene 2)

Scene index 2 (`hopiext.BFG`, E-0306). Callbacks: init `0x424af7`, per frame `0x424d93`
(E-0336). No museum painting leads here and the default-position switch has no case for
it (E-0308): it is entered only from the hospital interior (`hopiint`, 8), the bridge
(`pont`, 9) or the Yellow House (`maisonj`, 7). No completion flag and no movies.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| hopiint (8 → 2) | 0x253d, 0x1a4f, 0x2c21 | 0xfe2, 0x6bf, 0 |
| pont (9 → 2) | 0x4284, 0x1a9f, −0x185 | 0xfc4, 0xff6, 0 |
| maisonj (7 → 2) | 0x4457, 0x1a4d, 0x38a4 | 0xfc4, 0x7e2, 0 |

## Scene data (E-0336)

Object table at `0x4ac5e0`, 11 entries (count `0x4ac5d8`), none hidden:

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `cloche` | 0xff; entry 4 | the bell |
| 1 | `grille` | 0xff | none in the code |
| 2 | `plak` | 0xff | none in the code |
| 3, 4 | `grilledrt`, `grillegche` | 4 | the gate's two leaves |
| 5 | `arbre11` | 3 | zone 14 |
| 6 | `porteent` | 6 | door to the interior |
| 7..10 | `korde1` .. `korde4` | 0xff; entry 4 | the bell ropes |

Animations (table `0x4ac878`, E-0318; `0x424c4c`, frames by the elapsed ticks, which it
raises to 1 in the global when 0):

| # | Track | Node | At the end |
|---:|---|---|---|
| 0 | `grille.3da` | `ciel` | `DAT_004abcfc` := 1, stop, box set 1 (`BOX1.3DI`), `cloche`, `grilledrt`, `grillegche` cursor 0xff |
| 1 | `cloche.3da` | `cloche` | frame := 1, stop; start track 0, `portail` plays, `cloche` cursor 0xff |

Box sets (E-0319): `LoadBoxHopiExt` loads `BOX1.3DI` as set 1; `0x4248f0` n swaps
between `BOX.3DI` (0) and `BOX1.3DI` (1). Static sounds (E-0320, `0x424aa8`): `hopi_ext`
(ambient, looping), `portail`, `cloche`.

## Entry (`0x424af7`)

Gate open (`DAT_004abcfc`): pose track 0 at its last frame; `cloche`, `korde1..4`,
`grilledrt`, `grillegche` cursor 0xff; box set 1. Else those seven cursors := 4.
`DAT_004abd00` = 1 → `plak` cursor 0xff. Zone 14 done (`DAT_004abb44`) → `arbre11` 0x3c.

## Every frame (`0x424d93`)

The picked object's horizontal distance d = √(x² + z²) of its position (`0x436200`, as in
the museum, E-0313) is compared with 1500.0 (`0x4a2534`).

| Object | Condition | Effect |
|---|---|---|
| `arbre11` | d < 1500 | zone 14 |
| `cloche`, `korde1..4` | gate not open | start track 1, `cloche` plays, `DAT_004abcfc` := 1 at once |
| `porteent` | — | previous 2, target 8 (hospital interior) |
| `grilledrt`, `grillegche` | gate not open | start track 0 directly (no bell), `DAT_004abcfc` := 1 |

Hover: cursor types 2, 3, 4, 6, 0x3c (E-0315); `arbre11` changes the cursor only when
d ≤ 1500.

**Walking out:** camera z < −1000 → previous 2, target 9 (bridge).

## Flow

| # | Goal | Achieved by | Unlocks |
|---:|---|---|---|
| 1 | Open the gate | ring (`cloche`/`korde*`) or push a leaf | `DAT_004abcfc`; collision set `BOX1` |
| 2 | Zone 14 | click `arbre11` from within 1500 | completion flag of zone 14 (hopiint's, E-0311) |

**Exits:** `porteent` → hospital interior (8); walk south (z < −1000) → bridge (9);
museum exit (E-0310) → museum at the hospital painting (same place as from 8), no
return movie.

**State** (saved block): `DAT_004abcfc` (read/written), `DAT_004abd00`, `DAT_004abb44`
(read).
