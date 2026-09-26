# 2D interface: frames, inventory bar, menus

Everything 2D that is not the cursor (`interaction.md`) or a video (`boot.md`): the frame
system, the Space inventory bar, the players screen, the Option menu and the path from the
players screen to U01. All 2D coordinates are absolute pixels of the 640×480 frame; nothing
here scales, so a widescreen engine must place the whole 640×480 2D layer (for example
centred) rather than stretch rects. Evidence E-0100..E-0107, E-0450..E-0457.

## Frames (E-0100, E-0101)

A frame is one 2D screen, loaded by name from `Data/2DFRA/<name>.fra` (`fra.ksy`). It is a
flat list of views in file order; each view may name a parent view by id (children move
with their parent). The game finds views by id. A view is a rect plus:

| Class tag | What it is |
|---|---|
| `EIV#` | plain view: draws nothing, carries properties (most buttons are this: a hit rect over the background) |
| `TIB#` | bitmap view: draws `Data/2DBIT/<bitmap>` (`.bmp` appended when the name has no `.`) at view position + (`bmp_dx`, `bmp_dy`); name `0` = no bitmap; `w`/`h` 0 take the bitmap's size |
| `POL#` | bitmap view of the magnifier: pans its bitmap near the edges (Gallery, below) |
| `cSU#` `AOL#` `VAS#` `RCS#` | list with scroll bar: players (`cSU#`), saves to load / to overwrite (Q-0061) |
| `dEU#` `dES#` `idE#` | one-line text edit: player name (max 30 chars), save name (max 40) |
| `vop#` `bop#` | inventory strip and its arrows (below) |
| `loV#` `AoV#` `BoV#` | volume slider base; music slider (group 1); voice slider (groups 2 + 3) (Settings, below) |
| `nCC#` `nIC#` | video frames: unknown to the game (E-0100), never loaded |

A view is drawn and hit-tested only while `visible` ≠ 0 (all corpus views start visible).

**Properties** give views behaviour. Each receives the view's events:

| Tag | Data | Behaviour |
|---|---|---|
| `ucg@` | cursor kind | pointer enters → game cursor kind = value (0 default, 2 click, table in `interaction.md`); leaves → 0. Ignored while the cursor holds an item. |
| `LIH@` | bitmap, dx, dy | hover highlight: while the pointer is inside, draw `bitmap` over the view at view position + (dx, dy) |
| `GIH@` | as `LIH@` | same, but starts disabled |
| `RCS@` | command | on press (event 4) run the named command (table below) |
| `ARF@` `RUC@` `ARD@` `INA@` | | not used by any corpus frame |

**Events** a view gets: 1 pointer left, 2 pointer entered, 3 pointer moved inside, 4 left
button pressed on it (a click acts on press, not release), 13 released, 15 key pressed
(sent to every property of the frame, with the virtual key). Event 7 redraws a hovered
highlight; its sender is not traced (Q-0060).

## Frame manager (E-0101)

- **Open** a frame by name: it is added to the list of open frames. **Close** removes it.
  Several frames can be open at once (the inventory bar stays open under the menus).
- **Input**: while at least one frame is open, the window procedure offers every message
  to the frame manager before the game (E-0031, E-0043):
  - key down: offered to each open frame; the first that accepts it consumes it (the
    inventory bar accepts Space, below); also broadcast as event 15;
  - character: to the frames (text edits);
  - mouse: hit test from the last view in the list to the first, visible views only,
    point in rect; move sends 1/2/3 as the hovered view changes; press sends 4 to the
    hit view and remembers it; release sends 13 to that view.
  A message a frame consumes never reaches the scene.
- **Timer**: the manager runs a 50 ms Windows timer (`SetTimer`); frame animations (the
  inventory slide) advance one step per tick, not per rendered frame.
- **Drawing**: in app mode 0 each rendered frame is 3D scene, then the open frames (list
  order, views in file order), then the cursor, then the tutorial help panel, then
  present. In app mode 2 (scene paused under a frame) the 3D scene is not re-rendered: the
  frames and cursor are drawn over the last image. A frame with a full-screen background
  (`OptionUser`, `Option`) therefore hides the scene completely; `Save` and the bar do not.

## Text (E-0107)

Menu labels are bitmaps. Only the text edits and the lists draw text, with Windows GDI:
font Arial, 12 point (height = −12 × dpi / 72), drawn onto the back buffer's DC. There are
no font files in the data. The engine needs an equivalent sans-serif at about 16 px.

## Inventory bar: frame `PorteF` (E-0104)

Class: the frame named `PorteF` (registered by name, vtable `0x0043ae9c`). Layout from
`PorteF.fra` (`PorteFD.fra` is an unused variant without the bitmap):

| id | Class | Rect | Role |
|---:|---|---|---|
| 1 | `EIV#` | (0, 420, 640, 60) | root; everything moves with it |
| 2 | `TIB#` | (0, 420, 640, 60) | background `PorteF.bmp` (640×60, 7 empty slots drawn in it), cursor kind 2 |
| 100 | `bop#` | (20, 430, 33, 40) | left arrow |
| 101 | `bop#` | (580, 430, 33, 40) | right arrow |
| 200 | `vop#` | (57, 420, 535, 60) | item strip |

**Lifetime.** Opened when a player is selected (below) and parked at y = 480, off
screen. A new game empties the strip.

**Show / hide.** Space (key down, only while the app's "inventory allowed" flag is set,
E-0043) toggles: if a slide is running, reverse it (shown → hide, else show); otherwise
show when the bar is parked (y = 480), else hide. Show: step −4 px per timer tick for
(y − 420)/4 ticks; hide: +4 px for (480 − y)/4 ticks. Each tick moves the root (and so
every view) by the step, stops when the count runs out, and clamps y to [420, 480]. With the 50 ms timer a full slide is
15 ticks = 750 ms (80 px/s). Keep the tick in logic time, not render frames.

Other show/hide triggers: a take step (INFOACT op 2) shows the bar; a use-up step (op 3),
taking an item out of the bar, storing the held item in the bar and clearing the
"inventory allowed" flag hide it.

**Items.** The strip holds item names `<object>P` (e.g. `U01_04P`); each item is a
bitmap view of `Data/2DBIT/<name>.bmp` (50×50), 51×51, cursor kind 4 (take), at
x = 86 + 70 · i (i = slot, from 0), y = strip y + 5; slot i + 1 is 70 px right of slot i.
Adding appends at the end; removing shifts every later item 70 px left.

- **Arrows** (on press): right arrow shifts all items 70 px right if the scroll offset is
  below 0 (offset + 1); left arrow shifts them 70 px left if count + offset > 7
  (offset − 1). Clipping of items shifted outside the strip: Q-0062.
- **Click an item** (press): first, if the cursor holds an item, that item is stored in
  the bar (as below); then the cursor holds this item — cursor image name = item name
  with its 7th character replaced by `C` (`U01_04P` → `U01_04C`, 32×32), cursor mode
  "holding" (`interaction.md`); the item is removed from the strip; the bar hides.
- **Click the strip while holding an item**: the held item's name with its 7th character
  replaced by `P` is added; the cursor returns to normal; the bar hides.
- A take step sets the cursor to `<target>C` and slides the bar up; nothing enters the
  bar by itself (E-0211). Clicking anywhere on the strip (not only an empty slot) stores it.

**The held item (E-0210..E-0212).** Once held, the item stays on the cursor until one of:

| Event | Result |
|---|---|
| click on the strip / on a bar item | stored (a bar item is then taken: swap) |
| click on a hotspot whose action accepts it (trigger 7) | the action runs (op 3 uses it up) |
| left click on nothing, or on a hotspot with no matching action | nothing, still held |
| right click, Space, hover | nothing, still held (Space only slides the bar) |
| Escape (or F5) in a game (unit ≠ U00) | stored, then the `Save` prompt |
| Escape in U00 (no game) | not stored; the Option menu opens with the item still on the cursor |
| any frame / menu (app mode 2) | still drawn on the cursor over the frame, restored on return |
| caught (`OptionLoad` path) | stored |
| unit switch (Practice, a unit's exit to the next unit) | stored, then the new unit loads |
| New game | lost (the strip is emptied; U01 starts with only `U02_01P`) |
| a unit's start, loading a save | cursor normal (a save restores its own `CURSOR` chunk) |

U01 gives the player `U02_01P` (a banknote) at `U01_Start` if the bar does not have it
(runtime: the first slot shows it at the hand-over). The bar's contents are saved in a
`PORTEF` chunk: u32 last index, then 30-byte names. Saving, loading, `OptionSave`, `OptionLoad` and the lists: `save.md`.

## Players screen: frame `OptionUser` (E-0105)

Opened by `U00_Start` after Monet's first line when "practice" is off (`boot.md`). Views:
background `UserFond` (id 1); OK button `UserOKM` at (510, 443, 31, 23), hover `UserOKH`,
command `SelectUser` (id 2); players list (id 10, (149, 126, 406, 288), Q-0061); name edit
(id 11, (306, 91, 236, 19), max 30 characters; runtime shows the default text
"Player's name"). Enter in the edit also reaches `SelectUser` (the capture script types a
name and presses Enter).

`SelectUser`: take the edit's text; if empty do nothing. Otherwise look the name up in the
player list; if absent add a new player. Open `PorteF` (parked), select the player, close
`OptionUser`, then:
- new player: app mode 0, so U00 continues: Monet's tutorial (move, jump, take; Space
  opens the bar) runs in the garden;
- known player: open the Option menu at once.

Escape on the players screen quits the game.

## Escape (E-0105)

Only while "Escape allowed" (E-0043). In a game (unit ≠ U00) a held item first goes back to
the bar; in U00 it stays on the cursor (E-0210, E-0212). Then:

- **App mode 0, no game started** (U00 before New game): stop the voice, open the Option
  menu (app mode 2).
- **App mode 0 in a game** (U01 …): pause the tutorial help panel, open the frame `Save`
  ("Do you want to save?", Yes/No over the frozen 3D view) and block scene input.
  Yes (`SaveOui`) opens the save screen `OptionSave`; No (`SaveNon`) the Option menu;
  Escape in `Save` just closes it and resumes.
- **App mode 2**: on `OptionUser` quit; on a submenu (`OptionSave`, `OptionLoad`, …)
  return to the Option menu; on the Option menu itself nothing.

In app mode 0 the main loop also runs this for F5 (when the unit's input step allows it).

## Option menu: frame `Option` (E-0106)

Background `SomFond` (640×480: Monet on the left, the item labels on the right). Each item
is a view over its label with a hover bitmap, cursor kind 2, and a command:

| id | Rect (x, y, w, h) | Label | Hover | Command | Does |
|---:|---|---|---|---|---|
| 2 | 322, 20, 164, 30 | New game | `SomA3` | `OptionNouvelleP` | close the menu; new game (below) |
| 3 | 324, 92, 198, 31 | Load a game | `SomB3` | `OptionLoad` | open `OptionLoad`; greyed with `SomB2` when a save-list flag is 0 (runtime: no saves) |
| 9 | 323, 156, 144, 35 | Practice | `SomH3` | `OptionEntrenement` | close the menu; load `U00.X3D` with the players screen skipped (the tutorial) |
| 6 | 323, 225, 85, 28 | Gallery | `SomE3` | `OptionGalerie` | open the gallery (below); greyed with `SomE2` when no painting is unlocked |
| 5 | 321, 292, 98, 32 | Settings | `SomD3` | `OptionReglage` | open `OptionReglages` (below) |
| 7 | 324, 362, 84, 31 | Credits | `SomF3` | `OptionCredits` | open `Credits` (below) |
| 8 | 322, 433, 84, 27 | Quit | `SomG3` | `OptionQuitter` | open `OptionQuitter` (OK quits, No returns) |

The greyed look is the id's bitmap replaced by `SomB2` / `SomE2` (ids 3 and 6 are `TIB#`
with no bitmap otherwise). A greyed item still reacts: Load opens `OptionLoad` and Gallery
opens the gallery with every thumbnail removed (E-0456).

Settings and Credits leave the same way ("back to the menu", option screen `+0x4c`,
E-0450): clear the credits flag, close the submenu's frame and reopen `Option`, which
recomputes the greying and the gallery's unlock list.

**New game** (`OptionNouvelleP`): close the menu, then read `App.bin` `#GAME#` (the start
scene, `U01.X3D`, E-0037; `U01.X3D` if the chunk is missing), mark a game as started,
name the game `NoName`, app mode 1, and empty the inventory strip. The main loop then loads
U01 normally (`a = 1`), which plays the prologue (`boot.md` step 4).

## Settings: frame `OptionReglages` (E-0450)

Background `ReglageFond`; two sliders, OK and Cancel. There is nothing else: no texture
filter (`FILTER` in `InfoPara.bin`, `save.md`, has no control in any frame), no other
option.

| id | Class | Rect | Role |
|---:|---|---|---|
| 2 | `EIV#` | 473, 445, 30, 19 | OK: hover `ReglageOK`, command `ReglageOK` |
| 3 | `EIV#` | 193, 444, 66, 20 | Cancel: hover `ReglageAnnuler`, command `ReglageAnnuler` |
| 4 | `AoV#` | 182, 179, 311, 29 | music slider, sound group 1 |
| 5 | `BoV#` | 182, 289, 311, 29 | voice slider, sound groups 2 and 3 |

**Slider.** Margin m = 30 (the view's `unk_a`), knob bitmap `ReglageCabine` (8×29).
Position p is an integer 0..max, max = view width − 2m = 251. On open, p = ⌊max · 0.01 ·
G⌋ with G the group's current volume (group 1 for the music slider, group 2 for the voice
slider, `sound.md`). Draw the knob at x = view x + m + p − 4, y = view y. Press (event 4)
inside the left margin (view x .. x + m): p −= 5 (not below 0); inside the right margin
(right − m .. right): p += 5 (not above max); on the knob: start dragging. While dragging,
each move sets p = mouse x − m − view x, clamped to 0..max; release stops. A press on the
track outside the knob and margins does nothing.

**OK** (`ReglageOK`): G₁ := ⌊p₄ · 100 / max⌋ from the music slider, G₂ := G₃ := the same
from the voice slider, applied at once to playing sounds (`sound.md`); then back to the
menu. **Cancel** (`ReglageAnnuler`): back to the menu, volumes unchanged.

**Persistence.** None: no file stores a volume. G₂ and G₃ keep the value until the game
exits (nothing else changes them). G₁ does not survive: every app-mode change sets it (0
in mode 2, 85 otherwise, `sound.md`), so in the menu the music slider opens at 0 and the
next change out of mode 2 replaces OK's value with 85 (Q-0190). An engine that wants a
working music volume should keep it as a user setting and scale the mode rule by it
(beyond parity).

## Credits: frame `Credits` (E-0451)

One full-screen bitmap view (id 1) with command `MoveCredit`; pages are `Credit01.bmp`
.. `Credit05.bmp` (640×480).

- Open (`OptionCredits`): close the menu, open `Credits` showing `Credit01`, start the
  page clock (credits flag on, time = now).
- Next page: on a click anywhere (event 4) or when 6000 ms have passed since the last
  page change. The page number is parsed from the current bitmap name (the two characters
  before `.bmp`); the frame's initial name `Credit01` has no extension, so the first step
  shows `Credit01` again: page 1 stays up for two steps (12 s untouched), then 2, 3, 4, 5.
  A step from page 5 leaves.
- Any key (event 15 reaches the command) leaves at once.
- Leave: back to the menu (`Option`).

Keep the 6 s clock in real time (it is `GetTickCount`, not the frame timer).

## Gallery (E-0452..E-0455)

Twenty of Monet's paintings, unlocked by the player's progress, each viewable full
screen, at real size, through a magnifier, and as a 3D scene.

**Unlock state** is per player and is not a gallery file: it is the u16 unit number in
the player's `User_<i>/Info.bin` `USERINFO` (`save.md`), written with the current unit on
every save (so the last save wins, not the furthest). Each time the Option menu opens, the
unlocked list is rebuilt from it:

| Saved unit | Unlocked (list order; each row adds to the previous) | Count |
|---|---|---:|
| 0, 8..32, 34+ | none | 0 |
| 1 | `U11_01` | 1 |
| 2 | `U11_02`, `U11_03` | 3 |
| 3 | `U12_03` | 4 |
| 33 | `U12_04` | 5 |
| 4 | `U13_14`, `U13_05`, `U13_13`, `U13_03`, `U13_01`, `U13_12`, `U13_11`, `U13_06`, `U13_04` | 14 |
| 5, 6, 7 | `U14_01`, `U13_15`, `U14_02`, `U14_05`, `U14_03`, `U14_07` | 20 |

(Whether unit 33 can be saved as 33: Q-0193.) The menu greys Gallery when the list is
empty.

**`Galerie`** (opened by `OptionGalerie`; the Option frame is hidden, not closed):
background `GalerieFond`, a bar `GalerieBarre` at (73, 441) with the back button (id 3,
(81, 442, 33, 25), hover `RetourTAB`, `GoBack`), and 20 thumbnails, each a `TIB#` showing
`<p>IndexB`, hover `<p>IndexC`, cursor kind 2, command `GoToTableau`:

| id | Painting | Rect | id | Painting | Rect |
|---:|---|---|---:|---|---|
| 5 | `U11_01` | 54, 83, 79, 63 | 13 | `U13_11` | 554, 165, 54, 83 |
| 22 | `U11_02` | 151, 83, 82, 63 | 14 | `U13_12` | 453, 169, 77, 79 |
| 6 | `U11_03` | 247, 83, 89, 61 | 15 | `U13_13` | 160, 166, 73, 87 |
| 7 | `U12_03` | 368, 76, 55, 77 | 30 | `U13_14` | 540, 80, 81, 67 |
| 40 | `U12_04` | 459, 75, 50, 77 | 16 | `U14_01` | 450, 270, 80, 63 |
| 8 | `U13_01` | 349, 176, 87, 67 | 17 | `U13_15` | 543, 269, 80, 63 |
| 9 | `U13_03` | 255, 168, 79, 77 | 18 | `U14_02` | 267, 353, 59, 79 |
| 10 | `U13_04` | 351, 269, 82, 63 | 19 | `U14_03` | 461, 352, 55, 79 |
| 11 | `U13_05` | 65, 169, 67, 81 | 20 | `U14_05` | 352, 361, 80, 62 |
| 12 | `U13_06` | 262, 260, 64, 82 | 21 | `U14_07` | 544, 362, 79, 58 |

A locked painting's thumbnail gets no bitmap and a zero size: not drawn, not clickable.
Each thumbnail also carries a disabled `GIH@` (`<p>IndexA`, 194×111, at +49, +292); no code
that enables it has been found, so draw nothing for it (Q-0191). Every screen change below shows the wait cursor (kind 1) while
the frame loads, and each opens replacing the current frame.

**`Tableau`** (the painting; `GoToTableau` takes the painting as the first 6 characters of
the clicked thumbnail's bitmap name): view 1 full screen `<p>TAB`; bottom bar
`BarreBasTAB` (76, 442); buttons (each hover bitmap, cursor 2): back (81, 442, 33, 25)
`RetourTAB` `GoBack`, previous (132, 442) `PrevTAB` `GoPrev`, next (175, 442) `NextTAB`
`GoNext`, real size (499, 442) `TailleTAB` `GoTaille`, magnifier (537, 442) `LoupeTab`
`GoLoupe`; view 30 (228, 99, 406, 308), cursor 2, `GotoScene3D`, hidden for `U14_02`
and `U14_05`.

**`Taille`** (real size): view 1 `<p>_Size`; bars `BarreTAILLEB` (76, 442) and
`BarreTAILLEA` (501, 442); back, previous, next and magnifier as in `Tableau`, and
(500, 442, 27, 26) `GOTableauSize` `GoEcranTableau` → `Tableau` of the same painting.

**Navigation.** Previous / next step through the *unlocked list* (table order above, not
the thumbnail layout), wrapping at both ends, and reopen the same kind of screen
(`Tableau` or `Taille`) for the new painting. Back from `Tableau` or `Taille` → `Galerie`;
back from `Galerie` → the Option menu shown again and the gallery discarded. Escape
follows the generic rule (`OptionUser` quits, any other submenu reopens `Option`, E-0105).

**`Loupe`** (magnifier): one full-screen `POL#` view showing `<p>Loupe`, a multi-part
image listed in `Data/2dbit/Media.txt` (`name;id;cols,rows;file;;;`): parts
`<p>Loupe1.BMP` .. `<p>Loupe<cols·rows>.BMP`, row-major, every part 640×480 except the
last column and row; total ((cols − 1)·640 + last width) × ((rows − 1)·480 + last height)
(e.g. `U11_01` 2×2, 1200×928). The image starts at offset (0, 0) (top-left). While the
pointer moves inside the view, at most every 80 ms: within 30 px (edge zone) of the left
edge, pan by dx = ⌊(30 − d)/30 · 5 · 10⌋ (d = distance to the edge, so up to 50 px) to show
more of the left, cursor kind 10 (`LOUPEG`); right edge the same towards the right, kind
7; top edge, kind 13 (12 with left, 9 with right); bottom edge, kind 6 (11 with left, 8
with right); elsewhere kind 0. The offset is clamped so the image always covers the view.
A click anywhere (`FinLoupe`) returns to `Tableau`. The pan is event-driven in the
original (no movement, no pan); an engine may pan per logic tick while the pointer rests in
a zone, at the same 80 ms rate.

**3D view** (`GotoScene3D` on `Tableau`): discard the gallery, load the painting's scene as
unit class 50: `U01D.X3D` (`U11_01`), `U02D.X3D` (`U11_02`, `U11_03`), `U03D.X3D`
(`U12_03`), `U33D.X3D` (`U12_04`), `U04D.X3D` (the nine `U13_0x/1x` except `U13_15`),
`U05D.X3D` (`U13_15`, `U14_01`), `U06D.X3D` (`U14_02/03/05/07`); app mode 0. Escape
there: stop group 1, open the Option menu, open `Galerie` then `Tableau` of the same
painting, app mode 2.

What the scene does (unit class 50, E-0502):
1. **Load:** start the painting's unit ambient (group 1, looping, `sound.md`): unit 1
   `U01`, 2 `s1_15`, 3 and 33 `s2_01`, 4 `s3_01`, 5 `s4_01a`, 6 `s4_11`, from the scene's
   own `Sound/`. Then the generic load (`scene.md`; asset directory from the scene name,
   so `U33D.X3D` uses `Data/U33/`).
2. **Fix-ups** by unit, before the objects' info is read:
   - 1: none (the original hides `Tapiroug*`, which no longer exists under that name).
   - 2: renames `*U02_01` → `*U02_06`, `lourde05` → `*U02_12` (object only), first
     `*U02_07` → `*U02_07b`, next `*U02_07` → `*U02_07a`, `*ZonePlanc` → `*U02_13`,
     `*colplanch` → `*U02_14`; show `*U02_05` and enable its node.
   - 3 and 33: hide `*Ecran01`..`*Ecran09` and `Box186`; hide and remove from collision
     `table03`, `trépied`, `*U03_11`, `*U03_12`, `*U03_13`, `objectif0`, `objectif`,
     `Box206`, `Box207`, `Box187`, `Cylinder28/31/32/33/34/36/37/38/39`, `Sphere03`,
     `Sphere06`, `Tube16/17/18`.
   - 4: `U04_FixObjectNames` (`u00.md` step 0); hide and remove from collision `*U04_05`,
     `*U04_31`, `*U04_32`; collision sphere radius 5, Z offset 0.
   - 5: collision sphere radius 19, Z offset 29.
   - 6: none.
3. **Start:** the scene's `INFOOBJ.BIN` and actions as for a new unit (hotspot and node
   states), the lights. For `U11_03` only (not `U11_02`): show `*U02_05`, show its hotspot,
   its node running and looping.
4. **Camera cut** to the painting's pose (eye x, y, z; yaw; pitch):

   | Painting | Eye | Yaw | Pitch |
   |---|---|---|---|
   | U11_01 | 308.53, −508.20, 29.55 | 1.56 | π/2 |
   | U11_02 | 652.36, 153.88, 78.93 | −6.24 | π/2 |
   | U11_03 | 408.00, −831.52, 52.53 | −4.44 | π/2 |
   | U12_03 | 449.35, −232.52, 68.83 | −8.04 | 2.11 |
   | U12_04 | 320.98, −92.88, 68.83 | −1.68 | 2.05 |
   | U13_01 | −26.42, 37.10, −3.60 | 2.98 | π/2 |
   | U13_03 | 53.62, 132.69, −4.60 | 7.66 | π/2 |
   | U13_04 | 196.00, 284.00, 15.00 | −0.07 | π/2 |
   | U13_05 | 44.25, 150.98, −3.63 | 4.807 | π/2 |
   | U13_06 | 165.60, 291.76, 15.00 | 3.307 | π/2 |
   | U13_11 | 176.40, 311.57, 15.00 | 3.37 | π/2 |
   | U13_12 | 137.41, 123.18, −4.61 | 2.647 | 1.21 |
   | U13_13 | 110.47, −48.46, −4.61 | −6.29 | π/2 |
   | U13_14 | 108.50, 286.05, 15.00 | −2.93 | π/2 |
   | U13_15 | 226.37, −1075.79, 47.58 | −3.37 | π/2 |
   | U14_01 | 680.45, −135.73, 45.83 | −3.19 | π/2 |
   | U14_03 | −1033.06, 146.35, 25.41 | −3.66 | π/2 |
   | U14_07 | −1104.90, −1042.33, 25.41 | −2.586 | π/2 |

   (`U14_02`, `U14_05` have no 3D button.) Units 3 and 33 then hide and de-collide
   `*U03_13` and `*Ecran10`.
5. **Play:** the normal frame loop with no unit logic: keyboard movement and turning as in
   a game unit (`movement.md`, with collision), animations and the ambient play. The mouse
   does nothing: no hover cursor, no clicks. Escape as above.

## Other frames (E-0457)

| Frame | Opened by | Behaviour |
|---|---|---|
| `TableauJeu` | unit code: U04 (`U13_01`, `U13_99`, `U13_04`, `U13_06`, `U16_02`, `U16_01`, `U14_01`, `U13_11`, `U13_14`), U05 `DoTableauA` / `DoTableauB` (`U14_02` / `U14_05`) | full-screen `<name>.bmp`, cursor 2; app mode 2 without the sound change and Escape blocked; a click (`FinTableauJeu`) closes it, app mode 0, Escape allowed, stop sound group 2 |
| `OptionQuitter`, `Save`, `OptionSave`, `OptionLoad`, `OptionUser`, `Option`, `PorteF` | see above and `save.md` | |
| `Intro`, `InsertCD`, `Temp`, `PorteFD` | nothing (names absent from both EXEs) | skip; the missing-CD prompt is a message box (`Message.txt` 952) |
| `Prologue`, `Epilogue`, `GivParis`, `LeHavRou`, `RouGiv`, `V33_01`, `V33_02` | never loaded as frames (E-0100) | the AVIs play through the video path (`boot.md`) |

## Boot to U01 (answers Q-0018)

1. Intro bitmaps (`boot.md`), then U00 (the garden) with Monet's first line.
2. `OptionUser`: type a name, OK or Enter.
3. New player: the tutorial runs in U00 (app mode 0); Escape (when allowed) opens the
   Option menu. Known player: the Option menu opens directly.
4. Option → New game → App.bin → U01 with the prologue.

An engine that skips U00 must still open `PorteF` (parked, empty) and put `U02_01P` in it
through `U01_Start`, so Space works in U01.
