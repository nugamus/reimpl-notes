# mangeurs — the potato eaters' room at Nuenen (scene 4)

Scene index 4 (`mangeurs.BFG`, E-0306). Callbacks: init `0x4298e5`, per frame `0x429dd6`
(E-0364). Reached from the museum (painting `m01_03`, entry movie `mangeurs`, return movie
`mangeurr`, E-0309, E-0310) and from the cottage (`maisonet`, 3). Complete when zones 2 and 3
are done (`DAT_004abb14`, `DAT_004abb18`, E-0311). Generic mechanics are in
`engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 4, 4 → 4) | -106, 6, 100 | 0xf6a, 0x091, 0 |
| maisonet (3 → 4) | -384, 35, 1373 | 0xf6a, 0x6a5, 0 |

## Scene data (E-0364)

Object table at `0x4ae060`, 12 entries of 0x3c bytes (count `0x4ae058`): name, cursor type
at +0x32, handle at +0x34, start-hidden word at +0x38.

| # | Object | Cursor type | Start hidden | Role |
|---:|---|---|---|---|
| 0 | `buche` | 0xff; 4 once the faggot burns | no | the log: carried to the fire |
| 1 | `chaise1` | 0xff | no | none in the code |
| 2 | `fagot` | 0xff; 4 once the stove door is open | no | the faggot: carried to the fire |
| 3 | `fenetre` | 0xff; 4 when the baby cries | no | the window |
| 4 | `portepoel` | 4; 0xff once open | no | the stove door |
| 5 | `bersso` | 0xff; 3 once the window is shut; 0x3c once zone 2 is done | no | the cradle: zone 2 |
| 6 | `patat01` | 2 | no | item 4 |
| 7 | `pendul` | 0xff | no | the clock (distance probe only) |
| 8 | `POT` | 3; 0x3c once zone 3 is done | no | zone 3 |
| 9 | `vapeur` | 0xff | yes | the kettle's steam |
| 10 | `theieres` | 0xff; 2 once the kettle steams | no | the kettle: item 3 |
| 11 | `porte` | 6 | no | door to `maisonet` |

Animation table at `0x4ae338`, 5 entries of 0x78 bytes (count `0x4ae330`, E-0318):

| # | Track | Node | Started by | Step | On end |
|---:|---|---|---|---|---|
| 0 | `buche.3da` | `buche` | nothing in the 3D code (Q-0236) | elapsed | hide `buche`, stop, UV callback `0x4296e7` on `fire` |
| 1 | `chaise.3da` | `chaise1` | nothing in the 3D code (Q-0236) | elapsed / 2 | loops |
| 2 | `fagot.3da` | `fagot` | nothing in the 3D code (Q-0236) | elapsed | hide `fagot`, stop, UV callback `0x4296d0` on `fire` |
| 3 | `fenetre.3da` | `fenetre` | shutting the window | elapsed | holds the last frame, stops |
| 4 | `portpoel.3da` | `portepoel` | click `portepoel` | +1 per frame | `fagot` cursor 4, `portepoel` cursor 0xff, stops |

UV callbacks (`0x4399d0`, E-0319) on every vertex of an object: `0x4296d0` v −= 0x550000,
`0x4296e7` v += 0x550000, `0x4296fe` u += 0x550000 (wrapped to 24 bits), `0x42972b`
u += 0x400000 (wrapped). Every frame the scene scrolls `fire` with `0x4296fe` and `vapeur`
with `0x42972b`.

Static sounds (`0x429758`, E-0320), 9 slots: `mangeurs` (ambient, looped), `coucou`, `bebe`,
`fenclaq`, `finfeu`, `feu`, `bouilloi`, `chaise`, `porpoel`. No box sets of its own.

## Entry (`0x4298e5`)

1. Resolve handles (hide `vapeur`), load tracks and sounds. Timers `DAT_00599034`,
   `DAT_00599024` := 0; `DAT_00599038` (baby crying) := 0; `DAT_0059903c` (window shut) := 0;
   `DAT_00599044` := (`DAT_004abc08` = 0).
2. Stove door open (`DAT_004abc00`): pose track 4 at its last frame, `portepoel` cursor 0xff,
   `fagot` cursor 4.
3. Window: open (`DAT_004abc58` = 0) → pose track 3 at length / 2, loop `fenclaq`; shut → pose
   its last frame, `DAT_0059903c` := 1, `DAT_00599038` := 1.
4. Kettle taken (`DAT_004abc1c`) → hide `theieres`. Faggot burnt (`DAT_004abc3c`) → hide
   `fagot`, `buche` cursor 4. Log burning (`DAT_004abc2c`) → hide `buche`, loop `feu`.
   Log burning and kettle not taken → loop `bouilloi`. Potato taken (`DAT_004abbfc`) → hide
   `patat01`.
5. `DAT_00599038` = 1 → `bersso` cursor 3. Loop `mangeurs`; `DAT_00599040` := 0.
6. Zone 2 done → `bersso` cursor 0x3c; zone 3 done → `POT` cursor 0x3c.

## Flow

Carrying (E-0317): `fagot` and `buche` are picked up as 3D objects (hidden, cursor 0x28
while hovering anything). A click while carrying:

| Hovered | Carried | Effect |
|---|---|---|
| `fire` | `fagot` | play `finfeu` once, `DAT_004abc3c` := 1 (faggot burnt), UV callback `0x4296e7` on `fire`, `buche` cursor 4, autosave (`0x42f873`, E-0316) |
| `fire` | `buche` | loop `feu`, `DAT_004abc2c` := 1 (log burning), `DAT_004abc18` := 1, kettle timer `DAT_00599040` := 0, autosave |
| anything else | either | show the carried object again (dropped back) |

Carrying ends after that click. The burnt faggot or log stays hidden.

Clicks with the arrow on an object of the table (E-0315), first match wins:

| Click | Precondition | Effect |
|---|---|---|
| `fagot` | `fagot` cursor ≠ 0xff (stove open) | carry it |
| `buche` | `DAT_004abc3c` = 1 | carry it |
| `bersso` | `bersso` cursor ≠ 0xff | enter zone 2 (E-0312) |
| `theieres` | `DAT_004abc18` = 1 and its cursor ≠ 0xff | hide it, cursor := item 3, open the bar (E-0316), stop `bouilloi`, `DAT_004abc1c` := 1 |
| `patat01` | its cursor ≠ 0xff | hide it, item 4, bar, `DAT_004abbfc` := 1 |
| `POT` | its cursor ≠ 0xff | enter zone 3 |
| `fenetre` | its cursor ≠ 0xff and `DAT_0059903c` = 0 | shut the window (below) |
| `porte` | — | leave for `maisonet` (4 → 3) |
| `portepoel` | — | start track 4, `DAT_004abc00` := 1, play `porpoel` once |

**Shut the window** (click or timer): `DAT_0059903c` := 1, play `chaise` once, stop `bebe`
and `fenclaq`, start track 3, `DAT_004abc58` := 1, `bersso` cursor 3, `fenetre` cursor 0xff.

**Automatic triggers (every frame):**

| Trigger | Condition | Effect |
|---|---|---|
| Cuckoo | `DAT_00599044` = 0 (entry found `DAT_004abc08` ≠ 0) | play `coucou` once, `DAT_004abc08` := 0, `DAT_00599024` := 0, `DAT_00599044` := 1 |
| Baby cries | `DAT_00599024` > 50 ticks, `DAT_00599038` = 0, kettle not taken | loop `bebe`, `fenetre` cursor 4, `DAT_00599038` := 1 |
| Window shuts itself | baby crying, window open, `DAT_00599034` (+ elapsed) > 500 | shut the window |
| Kettle steams | `DAT_00599040` > 150, `DAT_004abc18` = 1, kettle not taken | show `vapeur`, loop `bouilloi`, `theieres` cursor 2 (repeated every frame while true) |

`DAT_00599024` and `DAT_00599040` grow by the elapsed ticks each frame. What sets
Nothing writes `DAT_004abc08` but this clear: a new player starts with 1 (E-0369), so the cuckoo sounds on the first visit only.

**State written:** `DAT_004abbfc`, `DAT_004abc00`, `DAT_004abc08`, `DAT_004abc18`,
`DAT_004abc1c`, `DAT_004abc2c`, `DAT_004abc3c`, `DAT_004abc58`. **Read:** those,
`DAT_004abb14`, `DAT_004abb18`.

**Exits:** `porte` → `maisonet`; Backspace or the corner arrow → museum (E-0310).
