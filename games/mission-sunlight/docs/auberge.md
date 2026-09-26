# auberge — the Auberge Ravoux (scene 1)

Scene index 1 (`auberge.BFG`, E-0306). Callbacks: init `0x41a0b0`, per frame `0x41a42b`
(E-0330). Not reachable from the museum: there is no painting for it; the player enters it
from the garden (`jardin`, scene 11) and leaves through its doors back to the garden.
Generic mechanics (loading, start positions, hover cursors, inventory bar, animations,
box sets) are in `engines/peintre/docs/spec/`; this file lists what the scene's own code
does.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| jardin (11 → 1) | 0, 0, 0 | 0, 0, 0 |
| reload / museum selector (1 → 1) | 0, 0, 0 | 0, 0, 0 |

The floor snap (E-0305) lifts the eye to 700 above the floor on the first frame.

## Scene data (E-0330)

Object table at `0x4a9950`, 12 entries of 0x3c bytes (count at `0x4a9948`); name, cursor
type at +0x32 (E-0315), start-hidden word at +0x38 (none hidden):

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `hors` | 0xff | on hover, arrow once the bag is open (below) |
| 1 | `saccoche` | 4 (finger) | the doctor's bag |
| 2 | `blanche` | 0xff | none in the code |
| 3 | `stetoscop` | 2 (hand) | item 31 |
| 4 | `portebas` | 6 (access) | lower door |
| 5 | `portehaut` | 6 (access) | upper door |
| 6 | `casquette` | 3 (zone) | zone 20 |
| 7 | `tableau` | 0xff, 3 when enabled | zone 21 (the ending) |
| 8, 9 | `porte01`, `porte02` | 6 (access) | exits to the garden |
| 10, 11 | `sac`, `sac01` | 4 (finger) | the bag again |

Animation table at `0x4a9c28`, 3 entries (E-0318):

| # | Track | Node | Stops at | On stop |
|---:|---|---|---|---|
| 0 | `saccoch.3da` | `saccoche` | length / 2 | `saccoche` cursor 0xff, `DAT_004abce8` := 1 (bag opened), `DAT_004e2aec` := 1 |
| 1 | `portehau.3da` | `portehaut` | length / 2 | `DAT_004abcf0` := 1 (upper door open), box set 2 (`BOXHAUT`), `portehaut` cursor 0xff |
| 2 | `portebas.3da` | `portebas` | length / 2 | `DAT_004abcec` := 1 (lower door open), box set 1 (`BOXBAS`), `portebas` cursor 0xff |

Frames advance by the elapsed ticks (`0x41a2ab`).

Box sets (E-0319): `LoadBoxAuberge` loads `BOXBAS.3DI` (set 1) and `BOXHAUT.3DI` (set 2);
`0x419e50` n removes the current set from collision and registers set n (0 = `BOX.3DI`).
Static sound (E-0320): `auberge`, the looping ambient (`0x419fb3`).

## Entry (`0x41a0b0`)

1. Resolve the table's handles, load the tracks, sounds and box sets; start `auberge`
   looping; `DAT_004e2aec` := (`DAT_004abce8` ≠ 0).
2. Bag opened (`DAT_004abce8`): pose track 0 at length / 2; `saccoche`, `sac`, `sac01`
   cursor 0xff.
3. Stethoscope taken (`DAT_004abce4`): hide `stetoscop`.
4. Lower door open (`DAT_004abcec`): pose track 2 at length / 2, box set 1, `portebas`
   cursor 0xff. Upper door open (`DAT_004abcf0`): pose track 1 at length / 2, box set 2,
   `portehaut` cursor 0xff (so with both open, set 2 is the one registered).
5. Sunflowers (`DAT_004abbd4`) = 5: `tableau` cursor 3. Zone 20 done (`DAT_004abb5c`,
   E-0311): `casquette` cursor 0x3c (déjà vu).

## Clicks (`0x41a42b`)

With the arrow cursor and a click on an object of the table (E-0315):

| Object | Condition | Effect |
|---|---|---|
| `porte01`, `porte02` | — | leave for the garden: previous 1, target 11 (E-0308) |
| `saccoche`, `sac`, `sac01` | `DAT_004e2aec` = 0 | start track 0; cursors of `saccoche`, `sac`, `sac01` 0xff; `DAT_004e2aec` := 1 |
| `stetoscop` | — | hide it, cursor := item 31, inventory bar opens (`DAT_004acfa0` := 2, E-0316), `DAT_004abce4` := 1 |
| `casquette` | — | enter 2D zone 20 (E-0312) |
| `tableau` | its cursor type = 3 | enter 2D zone 21 (the ending, E-0311) |
| `portebas` | its cursor type = 6 | start track 2; `portebas` cursor := 0xff |
| `portehaut` | its cursor type = 6 | start track 1; writes 0xff to **`portebas`**'s cursor (`DAT_004a9a72`), not its own |

Hover (no click): object 0 (`hors`) shows the arrow once `DAT_004e2aec` = 1; the others
map their cursor type as in E-0315 (no distance limit in this scene).

Every frame, after the clicks: sunflowers = 34 (`0x22`) sets `tableau` cursor 3 (the
entry tests 5; both are in the code).

## Flow

| # | Goal | Achieved by | Precondition | Unlocks |
|---:|---|---|---|---|
| 1 | Open the bag | click `saccoche`/`sac`/`sac01` | bag not open | `DAT_004abce8` |
| 2 | Take the stethoscope | click `stetoscop` | — | item 31 |
| 3 | Open the doors | click `portebas` / `portehaut` | cursor type 6 | box sets `BOXBAS` / `BOXHAUT` |
| 4 | Zone 20 | click `casquette` | — | its completion flag (E-0311) |
| 5 | The ending | click `tableau` | sunflowers 5 at entry or 34 during the frame | zone 21 → `cinefin` (E-0311) |

**Exits:** `porte01`/`porte02` → garden (11); Backspace or the "retour" corner → museum,
placed at the garden painting (prev 1, E-0310); no return movie (scene 1 has none).

**State read:** `DAT_004abce4`, `DAT_004abce8`, `DAT_004abcec`, `DAT_004abcf0`,
`DAT_004abbd4` (sunflowers), `DAT_004abb5c` (zone 20 done). **Written:** `DAT_004abce4`,
`DAT_004abce8`, `DAT_004abcec`, `DAT_004abcf0` (all in the saved state block, E-0312),
`DAT_004e2aec` (scene-local).
