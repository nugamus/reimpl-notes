# terrasse — the café terrace at night, Arles (scene 10)

Scene index 10 (`terrasse.BFG`, E-0306). Callbacks: init `0x42ddbf`, per frame `0x42e023`
(E-0366). Reached from the museum (painting `m03_05`, entry movie `terrasse`, return movie
`terr`, E-0309, E-0310), from the café (`cafe`, 5) and the Yellow House (`maisonj`, 7). Complete
when zones 16 and 17 are done (`DAT_004abb4c`, `DAT_004abb50`, E-0311). Generic mechanics are
in `engines/peintre/docs/spec/`.

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum / reload (0 → 10, 10 → 10) | -123, -102, -846 | 0xfe2, 0x01f, 0 |
| cafe (5 → 10) | -430, 63, 3711 | 0xfe2, 0x5ef, 0 |
| maisonj (7 → 10) | 677, -63, -2216 | 0xfe2, 0x044, 0 |

## Scene data (E-0366)

Object table at `0x4afc08`, 9 entries of 0x3c bytes (count `0x4afc00`): name, cursor type
at +0x32, handle at +0x34, start-hidden word at +0x38 (none hidden).

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `lettre` | 2 | the letter: item 27 |
| 1 | `de` | 0xff | the die on the plate (taken through `platode`) |
| 2 | `MANIVELLE` | 4 until the awning is rolled, then 0xff | the awning crank |
| 3 | `lunette` | 2 | the spectacles: item 17 |
| 4 | `KASKET` | 3; 0x3c once zone 17 is done | zone 17 |
| 5 | `drapo` | 3; 0x3c once zone 16 is done | zone 16 (only once the awning is rolled) |
| 6, 7 | `porte01`, `porte02` | 6 | doors to the café |
| 8 | `platode` | 2 until the die is taken, then 0xff | the plate with the die |

Animation table at `0x4afe28`, 1 entry of 0x78 bytes (count `0x4afe24`, E-0318):

| # | Track | Node | Started by | On end |
|---:|---|---|---|---|
| 0 | `terrasse.3da` | `storeho` | click `MANIVELLE` | `DAT_004abd74` := 1 (awning rolled), `MANIVELLE` cursor 0xff; the playing word is not cleared, so the end branch repeats each frame without posing again |

Frames advance by the elapsed ticks (`0x42df65`).

Static sounds (`0x42dcb0`, E-0320): `cafenuit` (ambient, looped), `store`. No box sets of its
own.

## Entry (`0x42ddbf`)

1. Resolve handles, load the track and sounds.
2. First visit (`DAT_004abd78` = 0): stream the voice `apierre` (`Snd_PlayStreamWav`),
   `DAT_004abd78` := 1.
3. Loop `cafenuit`.
4. Die taken (`DAT_004abd68`) → hide `de`, `platode` cursor 0xff. Letter taken
   (`DAT_004abd70`) → hide `lettre`. Spectacles taken (`DAT_004abd6c`) → hide `lunette`.
5. Awning rolled (`DAT_004abd74`): track stopped, pose its last frame, `MANIVELLE` cursor
   0xff; else pose frame 1, cursor 4.
6. Zone 16 done → `drapo` cursor 0x3c; zone 17 done → `KASKET` cursor 0x3c.

## Flow

Clicks need the arrow cursor and an object of the table (E-0315), first match wins:

| Click | Precondition | Effect |
|---|---|---|
| `MANIVELLE` | `DAT_004abd74` = 0 | start the track, play `store` once |
| `lettre` | — | hide it, cursor := item 27, open the bar (E-0316), `DAT_004abd70` := 1 |
| `KASKET` | — | enter zone 17 (E-0312) |
| `drapo` | `DAT_004abd74` = 1 | enter zone 16 |
| `lunette` | — | hide it, item 17, bar, `DAT_004abd6c` := 1 |
| `platode` | `platode` cursor = 2 | hide `de`, item 26, bar, `DAT_004abd68` := 1, `platode` cursor 0xff |
| `porte01` or `porte02` | — | leave for `cafe` (10 → 5) |

**Automatic trigger (every frame):** camera z < -2500 → leave for `maisonj` (10 → 7).

**State written:** `DAT_004abd68`, `DAT_004abd6c`, `DAT_004abd70`, `DAT_004abd74`,
`DAT_004abd78`. **Read:** those, `DAT_004abb4c`, `DAT_004abb50`.

**Exits:** doors → `cafe`; edge → `maisonj`; Backspace or the corner arrow → museum
(E-0310).
