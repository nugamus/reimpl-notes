# chambrev — the bedroom seen from the Yellow House (scene 6, other version)

Scene index 6 loads `chambrev.BFG` when `DAT_004abd14` = 0 (E-0306). Its callbacks, init
`0x41dd7f` and per frame `0x41ded8` (E-0333), are used only by the maisonj → 6 transition
with `DAT_004abd14` = 0 (E-0308); any other load of scene 6 runs chambreb's callbacks
(`chambreb.md`). Nothing here completes a zone.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| maisonj (7 → 6) | 100, −0x150, 0x1b7 | 0xf6a, 0xd76, 0 |

## Scene data (E-0333)

Object table at `0x4ab5c8`, 2 entries (count `0x4ab5c0`): `porte` (cursor 0xff, the
entry sets 4 or 0xff), `porte02` (cursor 6, the exit). Animation table `0x4ab648`, one
entry: `portev.3da` on `porte`, one frame per call (`0x41de65`); at its last frame it
stops, `DAT_004abd3c` := 1 (door open), `porte` cursor 0xff, `DAT_00650fc0` := 0.
Static sounds (E-0320, `0x41dc70`): `chambrVG` (ambient, looping), `placard`.

## Entry (`0x41dd7f`)

Door open (`DAT_004abd3c` = 1): pose the track at its last frame, `porte` cursor 0xff,
`DAT_00650fc0` := 1. Else `porte` cursor 4 (finger), `DAT_00650fc0` := 0.

## Clicks (`0x41ded8`)

| Object | Condition | Effect |
|---|---|---|
| `porte` | door closed | start the track, `placard` plays |
| `porte02` | — | previous 6, target 7 (Yellow House) |

Hover: cursor types 2, 3, 4, 6 as E-0315 (no 0x3c case in this scene).

## Flow

One optional action: open the door (`DAT_004abd3c`, saved). **Exits:** `porte02` →
Yellow House (7); museum exit (E-0310) as for scene 6 (`chambr` if zones 7..11 are done).
