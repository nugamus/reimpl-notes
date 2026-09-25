# 2D interface: frames, inventory bar, menus

Everything 2D that is not the cursor (`interaction.md`) or a video (`boot.md`): the frame
system, the Space inventory bar, the players screen, the Option menu and the path from the
players screen to U01. All 2D coordinates are absolute pixels of the 640×480 frame; nothing
here scales, so a widescreen engine must place the whole 640×480 2D layer (for example
centred) rather than stretch rects. Evidence E-0100..E-0107.

## Frames (E-0100, E-0101)

A frame is one 2D screen, loaded by name from `Data/2DFRA/<name>.fra` (`fra.ksy`). It is a
flat list of views in file order; each view may name a parent view by id (children move
with their parent). The game finds views by id. A view is a rect plus:

| Class tag | What it is |
|---|---|
| `EIV#` | plain view: draws nothing, carries properties (most buttons are this: a hit rect over the background) |
| `TIB#` | bitmap view: draws `Data/2DBIT/<bitmap>` (`.bmp` appended when the name has no `.`) at view position + (`bmp_dx`, `bmp_dy`); name `0` = no bitmap; `w`/`h` 0 take the bitmap's size |
| `POL#` | bitmap view of the magnifier (not U01) |
| `cSU#` `AOL#` `VAS#` `RCS#` | list with scroll bar: players (`cSU#`), saves to load / to overwrite (Q-0061) |
| `dEU#` `dES#` `idE#` | one-line text edit: player name (max 30 chars), save name (max 40) |
| `vop#` `bop#` | inventory strip and its arrows (below) |
| `loV#` `AoV#` `BoV#` | settings sliders (not specified) |
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
- A take step sets the cursor to `<target>C`: nothing enters the bar until the player
  clicks the strip (or presses Escape, which also stores a held item, E-0105).

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

Only while "Escape allowed" (E-0043). First, a held item goes back to the bar. Then:

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
| 6 | 323, 225, 85, 28 | Gallery | `SomE3` | `OptionGalerie` | the painting gallery; greyed with `SomE2` when empty |
| 5 | 321, 292, 98, 32 | Settings | `SomD3` | `OptionReglage` | open `OptionReglages` |
| 7 | 324, 362, 84, 31 | Credits | `SomF3` | `OptionCredits` | open `Credits` (`Credit01..05`); a click or 6 s → next page, a key → leave |
| 8 | 322, 433, 84, 27 | Quit | `SomG3` | `OptionQuitter` | open `OptionQuitter` (OK quits, No returns) |

The greyed look is the id's bitmap replaced by `SomB2` / `SomE2` (ids 3 and 6 are `TIB#`
with no bitmap otherwise). Whether a greyed item still reacts: Q-0063.

**New game** (`OptionNouvelleP`): close the menu, then read `App.bin` `#GAME#` (the start
scene, `U01.X3D`, E-0037; `U01.X3D` if the chunk is missing), mark a game as started,
name the game `NoName`, app mode 1, and empty the inventory strip. The main loop then loads
U01 normally (`a = 1`), which plays the prologue (`boot.md` step 4).

## Boot to U01 (answers Q-0018)

1. Intro bitmaps (`boot.md`), then U00 (the garden) with Monet's first line.
2. `OptionUser`: type a name, OK or Enter.
3. New player: the tutorial runs in U00 (app mode 0); Escape (when allowed) opens the
   Option menu. Known player: the Option menu opens directly.
4. Option → New game → App.bin → U01 with the prologue.

An engine that skips U00 must still open `PorteF` (parked, empty) and put `U02_01P` in it
through `U01_Start`, so Space works in U01.
