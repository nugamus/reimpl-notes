# chambreb — Van Gogh's bedroom (scene 6, the painting's version)

Scene index 6 loads `chambreb.BFG` when `DAT_004abd14` = 1 and `chambrev.BFG` otherwise
(E-0306); the museum painting `m03_02` sets `DAT_004abd14` := 1 before the flight, so the
room entered from the museum is this one. Callbacks: init `0x41c979`, per frame `0x41d167`
(E-0332); the callback selector `0x41ee1d` gives scene 6 these callbacks whichever BFG is
loaded, except the maisonj → 6 transition with `DAT_004abd14` = 0, which uses chambrev's
(`chambrev.md`). Completion: zones 7..11 (`DAT_004abb28` .. `DAT_004abb38`, E-0311);
entry movie `chamba`, return movie `chambr` (E-0309, E-0310).

## Arrival (E-0308)

| From | Position (x, y, z) | Angles (pitch, yaw, roll) |
|---|---|---|
| museum (0 → 6) | −0x274, −0x150, −0x10c | 0xf6a, 0x96, 0 |
| maisonj (7 → 6) | 100, −0x150, 0x1b7 | 0xf6a, 0xd76, 0 |

## Scene data (E-0332)

Object table at `0x4aa880`, 27 entries of 0x3c bytes (count `0x4aa878`):

| # | Object | Cursor type | Role |
|---:|---|---|---|
| 0 | `Object09` | 2 | item 15 (opens the drawer's way) |
| 1 | `porte` | 0xff / 4 | the cupboard door |
| 2 | `CHAISE1` | 0xff / 4 | the chair |
| 3 | `cadre` | 2 | item 10 |
| 4 | `Object02` | 2 | item 12 |
| 5 | `TIROIR` | 0xff / 4 / 3 | the drawer, zone 9 |
| 6 | `camee` | 0xff / 2 | item 13 (in the cupboard) |
| 7 | `shoes` | 0xff / 2 | the shoes, item 14 |
| 8 | `Object07` | 2 | item 18 |
| 9 | `papier` | 0xff | the paper (animated) |
| 10 | `mirroircas` | 0xff, starts hidden | the broken mirror |
| 11 | `ombrelle` | 0xff / 2 | item 8 (in the cupboard) |
| 12 | `oreiller` | 3 | zone 7 |
| 13 | `tab01` | 3 → 0xff until zone 7 | zone 11 |
| 14 | `tab02` | 3 | zone 10 |
| 15 | `bougie` | 0xff | none in the code |
| 16 | `Object01` | 0xff / 2 | shoe hot-spot (no click of its own) |
| 17 | `mirroir1` | 0xff | the whole mirror |
| 18 | `rasoir` | 0xff | none in the code |
| 19 | `mirroirmor` | 2, starts hidden | item 24 (mirror piece) |
| 20 | `porte02` | 6 | exit to the Yellow House |
| 21 | `papierferm` | 0xff / 4 | the folded paper |
| 22 | `Object10` | 0xff | shoes (click) |
| 23 | `Object01` | 0xff | second entry with the same name |
| 24 | `shoes01` | 0xff / 2 | shoes (click) |
| 25 | `tabpay` | 3 → 0xff until zone 7 | zone 8 |
| 26 | `Object06` | 0xff / 2 | shoes (click) |

Animations (table `0x4aaed8`, E-0318; `0x41cee9`):

| # | Track | Node | Step | At the end |
|---:|---|---|---|---|
| 0 | `chaise.3da` | `CHAISE1` | 1 per frame | `porte` cursor 4, `CHAISE1` 0xff, `DAT_004abd44` := 1, `DAT_00650fbc` := 1, stop |
| 1 | `chaussur.3da` | `perpompe` | 1 every other frame (`DAT_00650fb4` toggles) | loops |
| 2 | `mirroir.3da` | `mirroircas` | 1 per frame | show `mirroirmor`, `DAT_00650fa0` := 1, stop |
| 3 | `papier.3da` | `papier` | 1 per frame | `papierferm` cursor 0xff, `DAT_004abd48` := 1, `DAT_00650fb8` := 1, stop |
| 4 | `porte.3da` | `porte` | 1 per frame | `porte` 0xff, `camee` and `ombrelle` 2, `DAT_004abd38` := 1, `DAT_00650fc0` := 1, stop |
| 5 | `tiroir.3da` | `TIROIR` | 1 per frame | `TIROIR` cursor 3, `DAT_004abd40` := 1, `DAT_00650fb0` := 1, stop |

Track 1's playing word is 1 in the EXE's data and the entry clears it whenever the shoes
are still in the room; nothing in the scene code starts track 2 (Q-0220).

Static sounds (E-0320, `0x41c810`): `chambrVG` (ambient, looping), `chaiseVG`, `placard`,
`shoes`, `miroir`, `tiroir`, `papier`.

## Entry (`0x41c979`)

1. Handles, tracks, sounds; `chambrVG` looping; scene-local flags `DAT_00650fb0`,
   `fb4`, `fb8`, `fbc`, `fc0`, `fa0` := 0.
2. Shoes (`DAT_004abd50`, set on return from zone 8, E-0311): 0 → track 1 stopped,
   `shoes`, `Object01` (16), `shoes01`, `Object01` (23), `Object06` cursor 0xff. 1 and
   shoes not taken (`DAT_004abd34` = 0) → track 1 stopped, cursor 2 on `shoes`,
   `Object01` (16), `shoes01`, `Object06`. Otherwise hide `shoes`, `shoes01`, `perpompe`.
3. `DAT_004abd60` = 0, `DAT_004abd70` = 0 and `DAT_004abd14` = 1 → `DAT_004abd60` := 1
   (role unknown, Q-0220).
4. Taken items hidden: `Object09` (`DAT_004abd18`), `Object07` (`abd1c`), `cadre`
   (`abd20`), `Object02` (`abd24`), `ombrelle` (`abd28`), `camee` (`abd2c`).
5. Cupboard open (`DAT_004abd38`): pose track 4 at its end, `DAT_00650fc0` := 1, `porte`
   0xff, `camee` and `ombrelle` 2. Else `camee`, `ombrelle` 0xff, `porte` 4.
6. `Object09` taken → `TIROIR` cursor 4.
7. Mirror broken (`DAT_004abd4c`, set on return from zone 11): hide `mirroir1`, show
   `mirroircas`, pose track 2 at its end, `DAT_00650fa0` := 1; mirror piece not taken
   (`DAT_004abd30` = 0) → show `mirroirmor`.
8. Drawer open (`DAT_004abd40`): pose track 5 at its end, `DAT_00650fb0` := 1, `TIROIR` 3.
9. Chair moved (`DAT_004abd44`): pose track 0 at its end, `DAT_00650fbc` := 1, `CHAISE1`
   0xff. Else `CHAISE1` 4 and `porte` 0xff (overriding step 5).
10. Paper open (`DAT_004abd48`): pose track 3 at its end, `DAT_00650fb8` := 1,
    `papierferm` 0xff. Else pose track 3 at frame 1, `papierferm` 4.
11. `tabpay`, `tab01` cursor 0xff. Zone 7 done (`DAT_004abb28`): `tabpay` 3 with texture
    `TOILES2` → `RASOIR`, `tab01` 3 with `TOILES` → `RASOIR` (E-0319), `oreiller` 0x3c.
12. `DAT_004e30f4` = 1 (set on return from zone 11 while `DAT_004abd5c` = 0) and
    `DAT_004abd5c` = 0 → `DAT_004abd5c` := 1, `miroir` plays once.
13. Zones done: 8 → `tabpay` 0x3c, 9 → `TIROIR` 0x3c, 10 → `tab02` 0x3c, 11 → `tab01`
    0x3c.

## Clicks (`0x41d167`)

| Object | Condition | Effect |
|---|---|---|
| `Object09` | — | hide, item 15, bar, `DAT_004abd18` := 1, `TIROIR` cursor 4 |
| `cadre` | — | hide, item 10, bar, `DAT_004abd20` := 1 |
| `Object02` | — | hide, item 12, bar, `DAT_004abd24` := 1 |
| `TIROIR` | drawer closed and `Object09` taken | start track 5, `tiroir` plays |
| `TIROIR` | drawer open (`DAT_00650fb0`) | zone 9 |
| `papierferm` | paper closed | start track 3, stream `sm03_012` (voice, `Snd_PlayStreamWav`) |
| `camee` | cupboard open | hide, item 13, bar, `DAT_004abd2c` := 1 |
| `Object07` | — | hide, item 18, bar, `DAT_004abd1c` := 1 |
| `ombrelle` | cupboard open | hide, item 8, bar, `DAT_004abd28` := 1 |
| `mirroirmor` | — | hide, item 24, bar, `DAT_004abd30` := 1 |
| `porte` | chair moved, cupboard closed | start track 4, `placard` plays |
| `CHAISE1` | chair not moved | start track 0, `chaiseVG` plays |
| `oreiller` | — | zone 7 |
| `tab02` | — | zone 10 |
| `tabpay` | cursor type 3 or 0x3c | zone 8 |
| `tab01` | cursor type 3 or 0x3c | zone 11 |
| `porte02` | — | previous 6, target 7 (Yellow House) |
| `Object06`, `Object10`, `shoes`, `shoes01` | `DAT_004abd50` = 1 | hide `shoes`, `shoes01`, `perpompe`; item 14, bar, `DAT_004abd34` := 1 |

Hover: cursor types as E-0315 (2, 3, 4, 6, 0x3c), no distance limit.

## Flow

| # | Goal | Achieved by | Precondition | Unlocks |
|---:|---|---|---|---|
| 1 | Loose items | `cadre`, `Object02`, `Object07` | — | items 10, 12, 18 |
| 2 | `Object09` | click it | — | item 15; drawer clickable |
| 3 | Drawer | click `TIROIR` | 2 | zone 9 |
| 4 | Chair | click `CHAISE1` | — | cupboard clickable |
| 5 | Cupboard | click `porte` | 4 | `camee` (item 13), `ombrelle` (item 8) |
| 6 | Paper | click `papierferm` | — | voice `sm03_012` |
| 7 | Pillow | click `oreiller` | — | zone 7; its completion enables `tabpay`, `tab01` |
| 8 | Painting `tabpay` | zone 8 | 7 done | on return `DAT_004abd50`: the shoes (item 14) |
| 9 | Painting `tab01` | zone 11 | 7 done | on return `DAT_004abd4c`: broken mirror, `mirroirmor` (item 24) |
| 10 | Painting `tab02` | zone 10 | — | completion |

**Exits:** `porte02` → Yellow House (7); museum exit (E-0310) → museum at the bedroom
painting, `chambr` if zones 7..11 are done.

**State:** saved block `DAT_004abd14` .. `DAT_004abd5c` as listed, `DAT_004abd60`,
`DAT_004abd70` (read), `DAT_004abb28` .. `DAT_004abb38` (read); `DAT_004e30f4`
(set by the 2D return, E-0311); scene-local `DAT_00650fa0` .. `DAT_00650fc0`.
