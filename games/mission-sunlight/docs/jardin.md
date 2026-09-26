# jardin — the garden at Auvers (scene 11)

Scene index 11 (`jardin.BFG`, E-0306). Callbacks: init `0x426d9b`, per frame `0x427069`
(E-0361). Reached from the museum (painting `m04_01`, entry movie `jardin`, return movie
`jardinr`, E-0309, E-0310), from the inn (`auberge`, 1), the wheat field (`champ`, 12) and the
church (`eglise`, 13). It is the hub of the Auvers act: doors to the inn, walk-off edges to the
field and the church. Its completion test is always false (E-0311): leaving it never plays
`jardinr` and entering from the museum always plays `jardin`. Generic mechanics are in
`engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 11, 11 → 11) | -46, -335, 1263 | 0, 0xfd4, 0 |
| auberge (1 → 11) | -6620, 182, -578 | 0xfe2, 0x468, 0 |
| champ (12 → 11) | -8760, 228, -928 | 0xf6a, 0x3cd, 0 |
| eglise (13 → 11) | 6743, 235, -1283 | 0xfa6, 0xbdc, 0 |

## Scene data (E-0361)

This scene's tables use short records. Object table at `0x4ad080`, 8 entries of 0x14 bytes
(count `0x4ad078`): name at +0, cursor type at +0xa, handle at +0xc, start-hidden word at
+0x10 (none hidden).

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `rato` | 2 | item 30 |
| 1 | `fuzz` | 2 | item 29 (the butterfly; also taken through `aild`, `ailg`) |
| 2 | `auberge` | 0xff | none in the code |
| 3 | `cerf` | 4 | the kite: starts its flight |
| 4 | `partoche` | 3; 0x3c once zone 19 is done | zone 19 |
| 5 | `barriere` | 0xff; 4 at entry until opened | the gate |
| 6, 7 | `porte01`, `porte02` | 6 | exits to the inn |

`aild` and `ailg` (the butterfly's wings) are not in the table. Hovering them gives the
cursor of entry 0 (`rato`, a hand): the hover loop tests "handle of entry i" then "hovered is
`aild`/`ailg`" on its first pass, i = 0 (`0x427069`).

Animation table at `0x4ad128`, 5 entries of 0x34 bytes (count `0x4ad120`): track name at +0,
node name at +0xf, then handle, node handle, length, frame, playing at +0x20..+0x30
(E-0318; the fields are those of the 0x78-byte tables, packed).

| # | Track | Node | Started by | On end |
|---:|---|---|---|---|
| 0 | `barriere.3da` | `barriere` | click `barriere` | stops; `DAT_004abcc4` := 1 (gate open), `barriere` cursor 0xff, box set 1 |
| 1 | `cerfvol.3da` | `cerf` | click `cerf` | stops at its last frame |
| 2 | `papiyon1.3da` | `fuzz` | playing from the start (static word 1); restarted after track 3 | loops |
| 3 | `papiyon2.3da` | `fuzz` | the butterfly timer (below) | stops; track 2 restarts from frame 1 |
| 4 | `papiyon3.3da` | `fuzz` | nothing in the 3D code (Q-0236) | — |

All tracks advance by the elapsed ticks (`0x426f34`).

Box sets (E-0319, `0x426b70`): `LoadBoxJardin` loads `BOX1.3DI` as set 1; set 0 is
`BOX.3DI`. `0x426c56` registers set 1 when the gate is open (`DAT_004abcc4` = 1), else set 0.
Static sounds (`0x426c7a`, E-0320): `jardin` (ambient, looped), `clochjar`, `barriere`.

## Entry (`0x426d9b`)

1. Resolve handles, load tracks, sounds, `BOX1.3DI`, register the box set for the gate state,
   loop `jardin`.
2. Hide `fuzz` if taken (`DAT_004abcbc`), `rato` if taken (`DAT_004abcc0`).
3. Gate open: pose track 0 at its last frame, `barriere` cursor 0xff; else cursor 4.
4. Kite flown (`DAT_004abccc` = 1): hide `cerf`. Else pose track 1 at frame 1, stopped.
5. Butterfly timer: `DAT_00599064` := 0, interval `DAT_00599074` := 5 ticks.
6. Zone 19 done (`DAT_004abb58`) → `partoche` cursor 0x3c.

## Flow

Clicks need the arrow cursor (E-0315). This scene tests the names directly, without
checking the table first, so `aild`/`ailg` work:

| Click | Precondition | Effect |
|---|---|---|
| `rato` | — | hide it, cursor := item 30, open the bar (E-0316), `DAT_004abcc0` := 1 |
| `fuzz`, `aild` or `ailg` | — | hide `fuzz`, item 29, bar, `DAT_004abcbc` := 1 |
| `porte01` or `porte02` | — | leave for `auberge` (11 → 1) |
| `cerf` | — | start track 1, play `clochjar` once, `DAT_004abccc` := 1 (kite flown), `DAT_004abcd8` := 0 (role unknown here) |
| `partoche` | — | enter zone 19 (E-0312) |
| `barriere` | — | start track 0, play `barriere` once |

The kite is hidden on the next entry, since `DAT_004abccc` is set at the click.
`barriere` is clickable again while its track runs or after it (the cursor goes to 0xff
but the click test does not look at it); a second click restarts the track's playing word.

**Automatic triggers (every frame):**

| Trigger | Condition | Effect |
|---|---|---|
| Butterfly | track 2 playing and `DAT_00599064` (+ elapsed ticks) > `DAT_00599074` | stop track 2, start track 3, timer := 0, interval += 20 |
| To the church | camera z < 300 and x > 10000 | leave for `eglise` (11 → 13) |
| To the field | camera z < -500 and x < -9300 | leave for `champ` (11 → 12) |

**State written:** `DAT_004abcbc`, `DAT_004abcc0`, `DAT_004abcc4`, `DAT_004abccc`,
`DAT_004abcd8`. **Read:** those, `DAT_004abb58`.

**Exits:** doors → `auberge`; edges → `eglise`, `champ`; Backspace or the corner arrow →
museum (E-0310).
