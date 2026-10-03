# The score display and the ambience (engine behaviour)

Two global actors that scenes command: 8, the score display (`CFXGrumpaScore`, type 0x1b,
E-0703), and 180, the ambience (type 6, E-0702). Both are loaded with the other global actors
at a new game and kept for the whole game. Character side: `characters.md` (E-0704).

## Score (actor 8)

Loaded from `UI/008_Score/008_Score.atx`: active and visible, the coin at (10, 10), the heart
at (758, 10), digit gap 10, digit spacing 2; 13 pictures and 6 sounds in `UI/008_Score/`.

**Slots** (conditions read them): 0 State, 1 Coins (0), 2 Life (99), 3 Air (99). Values stay
in 0..99.

**Elements**, each a sprite (frame files as `scene.md` Sprites; colour key = frame 0's pixel
(0, 0)):

| # | picture | place | shown |
|---|---|---|---|
| 0, 1 | `curage_star`, `scare_star` (5 frames) | (687, 0) | while their animation plays: once forward and back, one frame per update, then hidden |
| 2 | `coin` | (10, 10) | always |
| 3 | `heart` (11 frames) | (758, 10) | always |
| 8..12 | form icons `grumpa`, `bear`, `boat`, `seahorse`, `dragonfly` | (758 − w − 8, 10) | the current form's only |
| 4 | `air` (11 frames) | 8 px left of the form icon | ops 78/79 |
| 6 | `poison_icon` | 8 px left of the air bar | ops 80/81 |
| 7 | `strength_icon` | 8 px left of the poison icon | ops 82/83 |
| 5 | `scorefont` (digits 0..9) | the coin count | always |

The form is a character: 10 Grumpa → icon 8, 13 → 9 (bear), 11 → 10 (boat), 88 → 11
(seahorse), 12 → 12 (dragonfly); a new game starts with Grumpa.

**Bars:** the heart shows Life, the air bar Air, as frame `count − value/9 − 1` (11 frames: 90
and up full = frame 0, 0..8 = frame 10). A frame outside the picture's frames leaves it as it
was; at 99 the frame is 0 after an add, `count − 1` after a subtract.

**Commands:**

| opcode | effect |
|---:|---|
| 2 / 3 | shown / hidden |
| 11 / 12 | active (animating) / not |
| 9 / 10 | Coins + / − `arg1`; adding plays `coin.wav` |
| 76 / 77 | Air + / − `arg1`; plays `SX_addair` (if not at 99 after a non-zero add) / `SX_subair` (if Air was not 0) |
| 78 / 79, 80 / 81, 82 / 83 | show / hide the air bar, the poison icon, the strength icon |
| 85 | the form becomes character `arg1`: Life = that character's slot 1, its icon shown, the heart redrawn |
| 50 / 51 | Life + / − `arg1`, for `arg2`: 0 the score's own Life, then the form character's slot 1 = Life; a character id: that character's slot 1 ± `arg1`, and the score's Life too if it is the current form; −10 / −11: passed on to actor 3 / 4 |

A Life add (non-zero, not ending at 99) plays star 0 and `SX_currage`; a Life subtract from a
non-zero Life plays star 1 and `SX_scare`. A character's opcodes 50/51 reach here as
`(op, arg1, character id)`.

**Drawing** (layer 6, after the scene's sprites and meshes; when shown): every element shown,
then the coin count: one digit, or two when above 9, from x = coin x + coin width + 10, the
second digit at x + digit width + 2, at the coin's y.

**Kept** in a save: active, visible, the form, which of air/poison/strength are shown, Coins,
Air (Life comes back from the form character).

## Ambience (actor 180)

Ten looping sounds from `Sounds\` (`Actors/global2.atx`): 0 jungle, 1 monkey, 2 ship, 3 ship
underwater, 4 desert, 5 indoor, 6 surface, 7 swamp, 8 undersea, 9 alternative. Volume −5 dB.

| opcode | effect |
|---:|---|
| 73 | play `arg1` (out of range: nothing). The same one: restarted only if it stopped. Another: it becomes the current one and fades in from −50 dB to −5 dB over 100 updates (sound 0, the start one, starts at −5 dB at once); the old one fades out from 0 dB to −50 dB over 100 updates and stops |
| 74 | stop the current and the fading one |

Loading the global actors plays sound 0 (Q-0700 for the main menu). Kept in a save: the
current index, played again on load.
