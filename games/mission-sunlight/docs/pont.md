# pont — the Langlois bridge at Arles (scene 9)

Scene index 9 (`pont.BFG`, E-0306). Callbacks: init `0x42cfe2`, per frame `0x42d489`
(E-0365). Reached from the museum (painting `m03_06`, entry movie `pont`, return movie
`pontr`, E-0309, E-0310), from the Yellow House (`maisonj`, 7) and the hospital courtyard
(`hopiext`, 2). Complete when zone 18 is done (`DAT_004abb54`, E-0311). Generic mechanics are
in `engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 9, 9 → 9) | 7805, 1167, 2183 | 0x01e, 0xcc1, 0 |
| hopiext (2 → 9) | 4933, -22, 13060 | 0, 0xa15, 0 |
| maisonj (7 → 9) | 11579, -56, -2069 | 0x01e, 0xcb5, 0 |

## Scene data (E-0365)

Object table at `0x4af610`, 7 entries of 0x3c bytes (count `0x4af608`): name, cursor type
at +0x32, handle at +0x34, start-hidden word at +0x38 (none hidden).

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `apple01` | 2 | the apples: item 7 |
| 1 | `chemise` | 3; 0x3c once zone 18 is done | zone 18 |
| 2 | `trappe` | 4 until opened, then 0xff | the trapdoor |
| 3 | `pouli03` | 4 until the bridge is down, then 0xff | pulley: target for the carried handle |
| 4 | `encre01` | 2 | the ink: item 28 |
| 5 | `pouli02` | 4 until the bridge is down, then 0xff | the other pulley |
| 6 | `poignee04` | 4 | the loose crank handle: carried |

`poignee02` (the handle fitted on the pulley) is not in the table; the code shows or hides
it by name.

Animation table at `0x4af7b8`, 5 entries of 0x78 bytes (count `0x4af7b4`, E-0318):

| # | Track | Node | Started by | Step | On end |
|---:|---|---|---|---|---|
| 0 | `pond.3da` | `ciel` | handle on a pulley | elapsed | stops; `DAT_004abd80` := 1 (bridge down), box set 0, pulley cursors 0xff |
| 1 | `trappe.3da` | `trappe` | click `trappe` | elapsed | stops; `DAT_004abd7c` := 1 (trapdoor open), `trappe` cursor 0xff |
| 2 | `arbres.3da` | `ciel` | playing from the start (static word 1) | — | its step returns at once: never posed |
| 3 | `pommes.3da` | `apple01` | camera within 2000 of `apple01` | elapsed | stops; `DAT_004abd88` := 1 (apples fallen) |
| 4 | `train.3da` | `train01` | playing from the start | elapsed | stops at frame 1: the train passes once per visit; `pastrain` plays at its end, first pass only (`DAT_00598ff4`) |

(`0x42d26a`.) Tracks with a node name refer to the node looked up by that name (E-0318);
two tracks name `ciel`.

Box sets (E-0319, `0x42cd80`): `LoadBoxPont` loads `BOX2.3DI` as set 1; set 0 is `BOX.3DI`.
Set 1 while the bridge is up, set 0 once it is down.
Static sounds (`0x42ce66`, E-0320): `pont` (ambient, looped), `pastrain`, `pontlev2`,
`trappe`.

`0x42cf99` ("fit the handle"): show `poignee02`, hide `poignee04`, pulley cursors 0xff,
`DAT_004abd84` := 1.

## Entry (`0x42cfe2`)

1. Resolve handles, `DAT_00598ff4` := 0, load tracks, sounds, `BOX2.3DI`, register set 1,
   loop `pont`. Pose tracks 0 and 3 at frame 1.
2. Ink taken (`DAT_004abd90`) → hide `encre01`. Apples fallen (`DAT_004abd88`) → pose track 3
   at its last frame. Apples taken (`DAT_004abd8c`) → hide `apple01`.
3. Bridge down (`DAT_004abd80`): pose track 0 at its last frame, box set 0, pulley cursors
   0xff, fit the handle. Else pulley cursors 4, box set 1.
4. Handle not fitted (`DAT_004abd84` = 0) → hide `poignee02`; fitted → hide `poignee04`.
5. Trapdoor open → pose track 1 at its last frame, `trappe` cursor 0xff; else 4.
6. Zone 18 done → `chemise` cursor 0x3c.

## Flow

Carrying (E-0317): `poignee04` is picked up as a 3D object (cursor 0x28 while hovering). A
click while carrying:

| Hovered | Effect |
|---|---|
| `pouli03` | show `poignee02`; if the bridge is up: play `pontlev2` once, start track 0, autosave (`0x42f873`); `DAT_004abd84` := 1 |
| anything else | show the carried `poignee04` again |

Clicks with the arrow on an object of the table (E-0315), first match wins:

| Click | Precondition | Effect |
|---|---|---|
| `trappe` | `DAT_004abd7c` = 0 | play `trappe` once, start track 1 |
| `chemise` | — | enter zone 18 (E-0312) |
| `apple01` | — | `DAT_004abd88` := 1, `DAT_004abd8c` := 1, hide it, cursor := item 7, open the bar (E-0316) |
| `encre01` | — | hide it, item 28, bar, `DAT_004abd90` := 1 |
| `poignee04` | — | carry it |
| `pouli02` | `DAT_004abd80` = 0 | fit the handle (`0x42cf99`), play `pontlev2` once, start track 0 |

The frame code also has a branch for an object `de` (hide, item 26, bar) between `chemise`
and `apple01`; `de` is not in this table, so the table test before the name tests never lets
it run. Clicking `pouli02` lowers the bridge without carrying the handle; it still fits
`poignee02` and hides `poignee04`.

The hover switch has no case for type 6 and no `break` after a match (harmless: handles are
unique).

**Automatic triggers (every frame):**

| Trigger | Condition | Effect |
|---|---|---|
| Apples fall | `apple01` within 2000 (`0x4a255c`) | start track 3 (every frame while close; it stops at its end) |
| To the Yellow House | camera x > 12000 | leave for `maisonj` (9 → 7) |
| To the courtyard | camera x > 5500 and z > 11000 | leave for `hopiext` (9 → 2); tested after the previous one, so it wins when both hold |

**State written:** `DAT_004abd7c`, `DAT_004abd80`, `DAT_004abd84`, `DAT_004abd88`,
`DAT_004abd8c`, `DAT_004abd90`. **Read:** those, `DAT_004abb54`.

**Exits:** edges → `maisonj`, `hopiext`; Backspace or the corner arrow → museum (E-0310).
