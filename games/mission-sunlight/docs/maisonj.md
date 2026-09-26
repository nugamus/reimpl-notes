# maisonj — the Yellow House in Arles (scene 7)

Scene index 7 (`maisonj.BFG`, E-0306). Callbacks: init `0x42897f`, per frame `0x428e63`
(E-0363). Reached from the museum (painting `m03_03`, entry movie `maisonj`, return movie
`maisonjr`, E-0309, E-0310) and from the bedroom (`chambrev`/`chambreb`, 6), the bridge
(`pont`, 9), the café terrace (`terrasse`, 10) and the hospital courtyard (`hopiext`, 2). It is
the hub of the Arles act. Complete when zone 12 is done (`DAT_004abb3c`, E-0311). Generic
mechanics are in `engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 7, 7 → 7) | -3350, 489, -5996 | 0x03c, 0xf68, 0 |
| hopiext (2 → 7) | 3320, 358, 12464 | 0, 0x8d8, 0 |
| chambre (6 → 7) | -6199, 358, 737 | 0, 0x679, 0 |
| pont (9 → 7) | -831, 489, -9000 | 0xfe2, 0x048, 0 |
| terrasse (10 → 7) | -7605, 358, -1698 | 0, 0x41e, 0 |

## Scene data (E-0363)

Object table at `0x4ad8d0`, 8 entries of 0x3c bytes (count `0x4ad8c8`): name, cursor type
at +0x32, handle at +0x34, start-hidden word at +0x38.

| # | Object | Cursor type | Start hidden | Role |
|---:|---|---|---|---|
| 0 | `pot01` | 4 at entry; 0xff once `pot02` was used or `DAT_004abda8` is set | no | a flower pot: reveals the snail, plays `pluie` |
| 1 | `pot02` | 0xff; 4 after `pot01` | no | the other pot: repaints the world map |
| 2 | `nuages` | 0xff | yes | clouds (not used by the code) |
| 3 | `escargot` | 2 | no | the snail: item 11 |
| 4 | `pendule` | 3; 0x3c once zone 12 is done | no | zone 12 |
| 5 | `portail` | 4 until the gate is open, then 0xff | no | the gate |
| 6 | `portemj` | 4 until the door is open, then 0xff | no | the house door |
| 7 | `portail01` | 4 until the gate is open, then 0xff | no | the gate's other leaf |

Animation table at `0x4adab8`, 5 entries of 0x78 bytes (count `0x4adab0`, E-0318):

| # | Track | Node | Started by | On end |
|---:|---|---|---|---|
| 0 | `escargot.3da` | `escargot` | entry when the snail is revealed, or the `pot01` click | loops |
| 1 | `nuages.3da` | `nuages` | nothing in the 3D code (Q-0236) | — |
| 2 | `portail.3da` | `portail` | click `portail` / `portail01` | stops; `DAT_004abda0` := 1 (gate open), both gate cursors 0xff, box set update |
| 3 | `porte-mj.3da` | `portemj` | click `portemj` | stops; `DAT_004abda4` := 1 (door open), `portemj` cursor 0xff, box set update |
| 4 | `train.3da` | `TRAIN02` | playing from the start (static word 1) | stops at frame 1: the train passes once per visit; `pastrain` plays once when the frame passes 70 |

All tracks advance by the elapsed ticks (`0x428c8c`).

Box sets (E-0319, `0x4285e0`, `0x428904`): `LoadBoxMaisonj` loads `BOX1.3DI`, `BOX2.3DI`,
`BOX3.3DI` as sets 1..3 (set 0 = `BOX.3DI`). The registered set follows the two openings:

| Gate (`DAT_004abda0`) | Door (`DAT_004abda4`) | Set |
|---|---|---|
| 0 | 0 | 0 (`BOX`) |
| 1 | 0 | 1 (`BOX1`) |
| 1 | 1 | 2 (`BOX2`) |
| 0 | 1 | 3 (`BOX3`) |

Static sounds (`0x4287d1`, E-0320): `maisjaun` (ambient, looped), `pastrain`, `placard`,
`portail01`.

Textures (E-0319): the entry loads `WMJ01`/`WMJ02`, `BMJ01`/`BMJ02`, `JMJ01`/`JMJ02` as
textures `WMAP01`/`WMAP02`, `BMAP01`/`BMAP02`, `JMAP01`/`JMAP02` (`0x4395d0`), then on the
object `world` replaces `MJ01` by `WMAP01` and `MJ02` by `WMAP02` (`0x435dc0`). The `B`
textures are loaded but not applied by this code.

## Entry (`0x42897f`)

1. Resolve handles, hide `nuages`, load tracks, sounds and box sets, register the set for
   the gate/door state, loop `maisjaun`. `DAT_00599058` := 0.
2. Load and apply the `W` world textures (above); `pot01` and `pot02` cursors := 4.
3. Map repainted (`DAT_004abd94` = 1): on `world`, `WMAP01` → `JMAP01`, `WMAP02` → `JMAP02`;
   `DAT_0059905c` := 1; `pot01` cursor 0xff.
4. `pot02` cursor := 0xff. `DAT_00599060` := `DAT_004abda8`; if set, `pot01` cursor 0xff.
5. Snail taken (`DAT_004abd98`) → hide `escargot`. Snail not revealed (`DAT_004abd9c` = 0) →
   hide `escargot`; revealed → start track 0.
6. Gate open → pose track 2 at its last frame, gate cursors 0xff, else 4. Door open → pose
   track 3 at its last frame, `portemj` cursor 0xff, else 4.
7. Zone 12 done (`DAT_004abb3c`) → `pendule` cursor 0x3c.

## Flow

Clicks need the arrow cursor and an object of the table (E-0315). This scene's reset list
(cursors `&`, `'`, `:`, `<` back to the arrow) omits `;`, and its hover switch has no case
for type 6; no object here has type 6.

| Click | Precondition | Effect |
|---|---|---|
| `pot01` | — | first time (`DAT_00599060` = 0): `DAT_004abd9c` := 1 (snail revealed), show `escargot`, `DAT_004abda8` := 1, `DAT_00599060` := 1, start track 0, `pot02` cursor := 4. Then, every time while `DAT_0059905c` = 0: play the movie `pluie` (mode 2, the movie path of E-0309) |
| `pot02` | `DAT_00599060` = 1 | on `world`: `WMAP01` → `JMAP01`, `WMAP02` → `JMAP02`; `DAT_0059905c` := 1, `DAT_004abd94` := 1, **`DAT_004abd14` := 1** (the bedroom becomes `chambreb`, E-0306), both pot cursors 0xff |
| `escargot` | — | hide it, cursor := item 11, open the bar (E-0316), `DAT_004abd98` := 1 |
| `portail` or `portail01` | `DAT_004abda0` = 0 | start track 2, play `portail01` once |
| `portemj` | `DAT_004abda4` = 0 | start track 3, play `placard` once |
| `pendule` | — | enter zone 12 (E-0312) |

So the pot order is fixed: `pot01` (rain movie, snail) first, then `pot02` (sunny map);
`pot01` replays `pluie` on every click until `pot02` is used.

**Automatic triggers (every frame):**

| Trigger | Condition | Effect |
|---|---|---|
| To the bridge | camera z < -12500 | leave for `pont` (7 → 9) |
| To the terrace | camera x < -8500 | leave for `terrasse` (7 → 10) |
| To the bedroom | -6233 < x < -6000 and z > 2000 | leave for the bedroom (7 → 6) |

The start-position table also has an arrival for 7 → 2 (`hopiext`, E-0308), but this scene's
code has no trigger that sets it (Q-0237).

**State written:** `DAT_004abd14`, `DAT_004abd94`, `DAT_004abd98`, `DAT_004abd9c`,
`DAT_004abda0`, `DAT_004abda4`, `DAT_004abda8`. **Read:** those, `DAT_004abb3c`.

**Exits:** edges → `pont`, `terrasse`, bedroom; Backspace or the corner arrow → museum
(E-0310).
