# Boot and main menu (Gilbert)

What `Gilbert.exe` does from process start until the main menu takes clicks, the main
menu with its pages, the film player and the exit. Addresses are `Gilbert.exe`
(`/gilbert-import/GILBERT.EXE`); function names are in
`engines/gilbert/notes/names/GILBERT.EXE-boot.csv`.

## Conventions

- **Screen:** one 640×480 16-bit surface pair (back buffer + primary), drawn into the back
  buffer and flipped (E-0004, E-0200). A *clear* is a fill of the whole back buffer with
  black; a *flip* shows it.
- **Clip rectangle:** every picture draw is clipped to (64, 50)–(576, 430), the 512×380
  window in the middle of the screen (set once at start-up). Clears and text are not
  clipped (E-0200).
- **Pictures** are items of DelphiX collections (formats README, `.wxi`). `i2[n]` is item
  n of `Data/maps/!global/interface2.wxi`, `i1[0]` the one item of `interface1.wxi`,
  `cur[n]` item n of `cursor.wxi` (E-0205). Every interface picture is drawn with
  fuchsia (FF00FF) transparent, top-left corner at the given point. Drawing a picture
  **records that point in the item**; the menu's hit tests use the item's last drawn
  rectangle (x, y, x + w, y + h), whatever screen drew it last (E-0205). Items never drawn
  sit at (0, 0).
- **Colours** are Delphi TColors ($00BBGGRR) and are given as RGB: tan (221, 189, 142)
  = $008EBDDD, yellow (255, 255, 0), white, black.
- **Text** is Windows GDI text on the back buffer: font Arial, the given point size,
  transparent background, drawn with its top-left corner at the point (E-0206, Q-0205).
- **Paths** are relative to the game folder (`Program/` on the disc); *resolve(p)* is
  HDPath + p if that file exists, else CDPath + p (see Settings).

## Settings

Read at start-up from `HKEY_LOCAL_MACHINE\SOFTWARE\Pir\Gilbert\1.0`, written back at exit
(E-0201). ScummVM keeps them in its configuration with these defaults (the original's
values when the key does not exist):

| Value | Type | Default | Read | Written at exit | Used for |
|---|---|---|---|---|---|
| `CDPath` | string | the EXE's folder | one trailing `\` removed | no | CD check, resolve |
| `HDPath` | string | the EXE's folder | one trailing `\` removed | no | resolve; `default.dat` and saves |
| `FirstTime` | DWORD | 0 | = 1 → true | always 0 | nothing else |
| `FullscreenVideo` | DWORD | 0 | = 1 → true | 1 / 0 | film player path |
| `InstallationType` | DWORD | −1 | as is | no | saving is off when −1 |
| `SoundVolume` | DWORD | 4 | outside 1..6 → 4 | yes | wave lists, sound stream |
| `MusicVolume` | DWORD | 5 | outside 1..6 → 5 | yes | music streams |

Volume level → DirectSound attenuation (hundredths of a dB): 1 −5000, 2 −4000, 3 −3000,
4 −2000, 5 −1000, 6 0 (E-0207). When the key is missing, `InstallationType` is −1 and the
game cannot save (E-0214, E-0216; Q-0204).

## Start-up

1. The program entry sets the application title `Gilbert`, creates the main form `gMain`
   and runs it (E-0200). The form is a full-screen 640×480×16 DirectDraw screen with a
   disabled 10 ms timer (E-0004).
2. When the screen is initialised (`DxScreen1Initialize` 0x469ecc): the clip rectangle
   (64, 50)–(576, 430), the Windows cursor hidden, the boot (below), then the timer on
   (E-0200).

## The boot (boot::Run 0x47b2f0)

In this order (E-0204):

1. Read the settings.
2. **CD check** (E-0202): `CDPath\data\misc\gilbert.nfo`, else `HDPath\...` the same. If
   neither exists, a box with language line 19 ("Indsæt venligst Gilbert-cd’en") and the
   buttons Retry / Cancel, repeated until the file is found. Cancel runs the exit sequence
   (below); the original then goes on with the boot until the quit reaches the message
   loop.
3. COM initialised (for DirectShow).
4. Clear, flip, clear, flip, clear (both buffers black); film `logo1.mpg`; clear, flip,
   clear, flip, clear; film `logo2.mpg`; clear, flip, clear. The logos play in the
   configured film mode (the boot saves and restores `FullscreenVideo` around them;
   nothing in between changes it).
5. Sounds: the six DirectSound objects initialised; `Data/Sounds/misc/menu.wxs` becomes
   wave list 1, `2.wxs` wave list 2 (E-0207).
6. Pictures: `interface1.wxi`, `map.wxi`, `interface2.wxi`, `cursor.wxi` (E-0205).
7. Loading step 2 (line 11). Then the slot rectangles (menu, below), `inventory.wxi`,
   `Data/anims/gilbert.wxi`.
8. Loading step 3 (line 12). Gilbert's sprite is created (gilbert.wxi item 0, 96×96, at
   (272, 210) in the 512×380 sprite space; rooms spec).
9. Loading step 4 (line 13). The slot names are read from `gilbert.ini`.
10. Loading step 5 (line 14). Mode := 0 (main menu); the timer interval becomes 16 ms; the
    display's gamma ramp is saved for the room fades (E-0218).
11. Loading step 6 (line 15). `GEInit` with the 22 call-backs (below).
12. Timer on; the menu music `Data/Sounds/MUSIC/menu1.wav` is opened, looped, not yet
    playing (it starts on the menu's 10th frame, below).

### Loading panel (boot::LoadingStep 0x478234)

Each step draws, without clearing (E-0206):

- `i2[0x3a]` laddbkg (169×125, opaque) at (235, 178);
- the lit lamps: step 2 `i2[0x60]` laddb21 (red) at (251, 244) and `i2[0x61]` laddb22
  (orange) at (296, 244); step 3 laddb22; step 4 laddb22 and `i2[0x62]` laddb23 (green) at
  (341, 244); steps 5 and 6 laddb23;
- the language line (E-0203) in Arial 8, horizontally centred on x = 320: first black at
  y 201, then tan at y 200;

then flips and busy-waits (50,000,000 empty loop iterations, Q-0200). The steps' lines:
11 "Initialiserer grafik...", 12 "Initialiserer Gilbert...", 13 and 14 "Initialiserer
gamma...", 15 "Initialiserer logik...". The original measures the text width with the
canvas font of the previous text (Q-0201).

`language.txt` (E-0203): line n is the n-th CR-terminated line counted from 0, with
leading and trailing characters ≤ space removed (so the LF of CR LF goes).

## Films (movie::Play 0x4797f0)

`movie::Play(name)` plays `Data/mpg/<name>` (resolve) (E-0208):

1. The timer stops and every sound stream stops (StopAll, below).
2. **Full-screen** (`FullscreenVideo` = 1): both buffers black; each decoded frame is
   stretched to the whole 640×480 screen and flipped; no frame picture.
3. **Windowed** (otherwise): the film is drawn at its own size (all films are 384×288,
   E-0007) with its top-left corner at (127, 80). For every film except `logo1.mpg`,
   `logo2.mpg`, `logo3.mpg` (exact names), `i2[0x97]` filmsm (512×380, a copper frame with
   a black window) is first drawn at (64, 50) into both buffers; the logos play on
   whatever is on screen (black at boot and exit).
4. Timing comes from the stream (audio through the default device); after each shown
   frame the Escape key is sampled (held down at that moment): pressed → the film stops.
   Full-screen: both buffers are cleared and flipped at the end.
5. Afterwards: if the film was started from the menu's Intro button, the menu music
   `menu1` is opened again and the menu frame counter set to 9 (so it starts on the next
   menu frame); otherwise, if a room music is set, it restarts (looped). The timer runs
   again.

## Exit (boot::Exit 0x47b5fc)

Timer off; settings written; `FullscreenVideo` := 0 (so the next film is windowed); clear,
flip, clear, flip, clear; film `logo3.mpg` (windowed, 1:1 at (127, 80) on black); the
credits surface and two other off-screen objects freed; the DirectSound objects finalised; `GEExit`; COM
uninitialised; the application terminates (E-0209).

## Main loop (TgMain.DXTimer1Timer 0x469fa0)

One tick every 16 ms of the DelphiX timer (Q-0207). Each tick (E-0210):

1. `GEEllapsed()`; if `GEGetVariable(198)` ≠ 0: mode := 0 and *game running* and *can
   save* := false (back to the menu with Continue and Save disabled).
2. By mode: 0 main menu (below); 1, 2, 4, 5 the game screens (rooms, close-ups and the
   rest: other specs); 0x99 while a room loads and 3: nothing.

The menu mode per tick: draw the menu, handle the mouse, draw the cursor, flip; then the
music: when the menu frame counter equals 10 the menu music starts; the credits music and
(counter > 10) the menu music get their streaming update. The counter counts menu frames
up to 20; it is 0 at start, 0 again when the game returns to the menu, 9 after the intro
or the credits.

## Main menu

### State

| Name here | Global | Start | Meaning |
|---|---|---|---|
| running | 0x47cf4c | false | a game has been started or loaded |
| can save | 0x47cf50 | false | Save is enabled |
| shown | 0x47ce68 | false | a room has been shown since the last new/load (set by the room draw) |
| hover | 0x47cf1c | −1 | column button under the mouse |
| pressed | 0x47cf20 | −1 | column button last pressed |
| page | 0x47cf34 | −1 | page on the left (1..8 = pressed − 10) |
| help / credits | 0x47cf88 / 0x47cfb4 | false | the Help or About page is open |
| page hover / press | 0x47cf44 / 0x47cf48 | −1 | item of a page |
| load row hover / picked | 0x47cf64 / 0x47cf6c | 0 | row 1..6 |
| save row hover / picked | 0x47cf68 / 0x47cf70 | 0 | row 1..5 |
| load / save top | 0x47cf58 / 0x47cf5c | 0 | first slot shown − 1 |
| name, editing | 0x47cf74, 0x47cf78 | '', false | the save name being typed |
| last action | 0x47cf40 | −1 | item of the last button action |

(E-0210, E-0212..E-0215)

### Frame (gmenu::Draw 0x46b490)

In this order (E-0212):

1. Clear.
2. Background. Normal: `i2[0]` 0bkg at (64, 50), `i2[2]` 1m01bkg at (352, 56), `i1[0]`
   ibkg03 (the frame) at (64, 50). Credits open: `i2[3]` credbkg at (64, 50), `i1[0]` at
   (64, 50). Both: `i2[0x32]` ilockbkg at (64, 337).
3. The column (only when neither Help nor About is open), x = 384:

   | y | Button | Item | Hover | Pressed | Disabled |
   |---:|---|---|---|---|---|
   | 70 | Fortsæt spil (Continue) | 0xb | 0x13 | 0x1b | 0x24 when not running |
   | 104 | Nyt spil (New game) | 0xc | 0x14 | 0x1c | |
   | 138 | Åbn spil (Load) | 0xd | 0x15 | 0x1d | |
   | 172 | Gem spil (Save) | 0xe | 0x16 | 0x1e | 0x25 when not can save |
   | 206 | Indstillinger (Settings) | 0xf | 0x17 | 0x1f | |
   | 240 | Hjælp (Help) | 0x10 | 0x18 | 0x20 | |
   | 274 | Om Gilbert (About) | 0x11 | 0x19 | 0x21 | |
   | 308 | Intro | 0x12 | 0x1a | 0x22 | |
   | 380 | Afslut (Quit) | 0x33 | 0x70 | 0x72 | |

   The plain picture is drawn for each; then the hover picture over the hovered button,
   then the pressed picture over the pressed one, which also runs its action (below) —
   every frame while it stays pressed. A disabled Continue or Save gets neither hover nor
   pressed picture nor action.
4. About open: `i2[0x77]` 0tillbkg at (509, 336), `i2[0x73]` 0tillb11 (back) at (513, 340).
   With Help or About open: hover back → `i2[0x74]` at (513, 340); pressed back →
   `i2[0x75]` at (513, 340) and the back action.
5. The page, if any (below).
6. The frame counter + 1 (up to 20).

Then the mouse handling, then the cursor: `cur[0]` VANLIG at (x − 16, y − 16) of the mouse;
the mouse is kept inside x 72..568, y 58..422 (the Windows cursor is moved back when it
leaves) (E-0211).

### Mouse (gmenu::HandleMouse 0x471380)

The mouse is a 6×6 rectangle (x − 3, y − 3)–(x + 3, y + 3); a picture is hit when its last
drawn rectangle overlaps it (E-0211, E-0213). The left button's press is taken once, on
the tick after it goes down (the button state is set by the mouse events; releasing any
button clears it). Right presses are ignored by the menu.

- **Right side** (only when the mouse overlaps (320, 50)–(512, 440), or Help or About is
  open): hover := the first hit of Continue (only when *shown*), New, Load, Save,
  Settings, Help, About, Intro, back (0x73), Quit; none → −1. When the gate fails, hover
  keeps its value. A new left press sets *pressed* the same way.
- **Left side** (mouse overlapping (0, 0)–(320, 440), or Help or About open): page hover
  from 0x44, 0x45, 0x63, 0x66, 0x73, 0x84, 0x87; load row hover (1..6 or 0) and save row
  hover (1..5 or 0) from the row rectangles. A new left press sets the page press (the
  same items plus 0x8a..0x96, or −1) and the picked load row and save row (unchanged when
  no row is hit).
- After a press, unless Help or About is open: if *pressed* ≠ −1, page := pressed − 10.

Row rectangles (E-0213): load row k (1..6) and save row k (1..5) = (111, 107 + 30(k−1))–
(298, 134 + 30(k−1)); the save name field = (111, 269)–(298, 292).

No key does anything in the menu except typing a save name (below); Escape only skips
films (E-0211).

### Button actions (gmenu::Action 0x46fa74)

Called with the item every frame it is shown pressed (column) or once per press (page
items). "First" means the item differs from the last action's item; sounds and one-time
work happen only then (E-0214). *Click n* is `PlayWave(list 1, item n)` of `menu.wxs`
(E-0207): 0 "click 1" … 5 "click 6".

| Item | Action |
|---|---|
| Continue 0xb | first: click 4, stop all sounds, restart the room music (looped) if one is set. Then close the menu state, mode := 1 (the game). |
| New game 0xc | first: click 4; stop all sounds; `GEExit`; `GEInit`(call-backs); `GELoadFile(HDPath\data\game\default.dat)`; if it succeeds: reset the game state, `GEStartNewGame`, and *can save* := true unless `InstallationType` = −1; *running* := true. Then close the menu state. The first room comes from ge.dll's start event through the GotoWalkmap call-back, which loads the room and sets mode 1. |
| Load 0xd | first: click 5, re-read the slot names, clear the row choices. Page 3. |
| Save 0xe | as Load; page 4. |
| Settings 0xf | first: click 5. Page 5. |
| Help 0x10 | first: click 5, build the help text. Help open. |
| About 0x11 | first: click 5, stop all sounds, build the credits, `credit.wav` looped (music volume). About open, scroll 0. |
| Intro 0x12 | first: film `intro.mpg` (the menu music comes back after it). Then pressed, page := −1, Help and About closed. |
| Quit 0x33 | stop all sounds; first: click 3 played to its end; close the menu state; exit sequence. |
| back 0x73 | click 4 played to its end; if About was open: stop all sounds, `menu1` again (counter 9). Close the menu state. |
| Load button 0x45 | click 0; if a load row is picked: `GEExit`, `GEInit`, `GELoadFile`(the slot's file); success → reset the game state, *running* and *can save* := true, `GEContinueGame` (which enters the saved room); failure → both false. |
| Save button 0x44 | click 0; if a save row is picked: save slot (top + row) with the typed name. Close the menu state. |
| Up 0x63 / down 0x66 | click 1; load page: top − 1 (not below 0) / + 1 (not above 44); save page: top − 1 / + 1 (not above 45); editing stops. |
| Music 1..6 (0x8a..0x8f) | click 0, then `MusicVolume` := n and applied. |
| Sound 1..6 (0x90..0x95) | `SoundVolume` := n and applied, then click 0. |
| Video 0x96 | click 0; `FullscreenVideo` toggled. |
| Help arrows 0x84, 0x87 | nothing (the help text never scrolls). |

Page presses are dispatched by page, not by item (E-0219): a page press of 0x44 **or**
0x45 draws the pressed button and loads on page 3 (`i2[0x4d]`, Load action), saves on page
4 (`i2[0x4c]`, Save action), and does nothing on other pages. The hit test finds 0x44
before 0x45; both sit at (258, 302), so either works on either page. 0x63 and 0x66 run
their action (click 1, scroll only on pages 3/4) on every page; their pressed pictures
only on pages 3/4. 0x8a..0x96 act only on page 5, 0x73/0x84/0x87 (page items) only on
page 6.

"Reset the game state" (ResetState, after a successful new game or load) also sets
MusicVolume 5, SoundVolume 4 and FullscreenVideo 0 in memory, whatever the settings were
(rooms.md "State", E-0309).

"Close the menu state": page, hover, pressed := −1, Help and About closed. Page-item
actions also clear the page hover and press.

In the game, the "Menu" button (item 0x26) returns here: click 2, stop all sounds, counter
0, `menu1` looped, mode 0 (E-0214).

### Pages (gmenu::DrawPage 0x46bf58)

Drawn after the column (E-0215). Page 1 and 2 only re-run the Continue / New game action.

**Load (3).** `i2[0x23]` 2m03bkg and `i2[0x3f]` (title "Åbn spil") at (102, 63), `i2[0x38]`
list at (104, 100). The hovered row's rectangle is filled with (196, 38, 0) at alpha 50
(Q-0202). Rows k = 1..6: "`n`: `name[n]`", n = top + k, Arial 8 at (119, 85 + 30k), tan,
yellow for the picked row. `i2[0x45]` "Åbn" button at (258, 302) (hover `i2[0x49]`, pressed
`i2[0x4d]`), `i2[0x63]` up at (301, 107) (hover 0x64, pressed 0x65), `i2[0x66]` down at
(301, 272) (hover 0x67, pressed 0x68).

**Save (4)** (only when *can save*). `i2[0x23]`, `i2[0x40]` ("Gem spil") at (102, 63),
`i2[0x39]` at (104, 100); hovered row filled as on page 3; rows k = 1..5 as on page 3 with
the save top and picked row. When a row is picked for the first time, or another row is
picked while editing, the name becomes that slot's name and editing starts. While a row is
picked, the name field is filled with (196, 38, 0) at an alpha that falls by 2 per frame to
0 and rises by 5 to 80, over and over, and the name is drawn at (119, 274), tan. `i2[0x44]`
"Gem" button at (258, 302) (hover 0x48, pressed 0x4c), up at (301, 107), down at (301, 241).

**Typing** (E-0211): while editing on page 4 with a row picked, a key whose unshifted
character (Windows `MapVirtualKey` type 2) is space, 0–9, `:`, `@`, A–Z, `[`, `\`, Ä, Å or Ö
is appended while the name is shorter than 20 characters; Backspace removes the last
character. (Letters come in upper case; the Danish Æ and Ø keys are not accepted.)

**Settings (5).** `i2[0x23]`, `i2[0x37]` ("Indstillinger") at (102, 63). Music ("Musik"):
`i2[0x3b]` at (108, 97); six lamps `i2[0x3c]` (off) at x = 114 + 33j, y 122 (j = 0..5), the
MusicVolume-th lit with `i2[0x71]`; buttons 1..6 `i2[0x8a..0x8f]` at the same x, y 153.
Sound effects ("Lydeffekter"): `i2[0x3e]` at (108, 192), lamps at y 216 (SoundVolume),
buttons `i2[0x90..0x95]` at y 247. Full-screen video ("Fuldskærmsvideo til/fra"):
`i2[0x7d]` at (112, 288), the lamp `i2[0x71]` (on) or `i2[0x3c]` (off) at (279, 293), the
button `i2[0x96]` at (246, 294). The buttons have no hover or pressed pictures.

**Help (6).** Drawn over everything: `i2[0]` and `i2[0x6f]` s03bkg at (64, 50); the help
text (440×1400 off-screen, rows 0..320, width 355) at (135, 95) with black transparent
(Q-0203); `i1[0]` at (64, 50); `i2[0x32]` at (64, 337); `i2[1]` ssky05 ("Hjælp") at (192,
56); `i2[0x77]` at (509, 336); back `i2[0x73]` at (513, 340) (hover 0x74 at (513, 340),
pressed 0x75 at (513, 320)); arrows `i2[0x84]` at (503, 93) (hover 0x85, pressed 0x86) and
`i2[0x87]` at (503, 313) (hover 0x88, pressed 0x89). The help text: `Data/misc/help.txt`
(resolve), character by character; `#` and `%` switch to regular, `$` to bold; CR and LF
each end a line, drawn at (0, y), Arial 8, (128, 64, 64), y += 10 from 0 (a CR LF pair
therefore advances 20).

**About (7).** The credits text (440×3000 off-screen) rows t..t + 280 at (102, 55), black
transparent, t = trunc(scroll); scroll += 0.5 per frame, back to 0 when it reaches 3000.
Built from `Data/misc/credits.txt`: `#` size 9 tan, `$` size 9 yellow, `%` size 11 white;
each CR or LF draws the collected line centred on x 220, first in (3, 22, 2) at (221 − w/2,
y + 1), then in the colour at (220 − w/2, y), Arial, y += 10 from 300.

**Intro (8), Quit (0x29).** No page (their actions run from the column).

### Sounds in the menu

Wave list 1 is `menu.wxs` (items 0..5 "click 1".."click 6", 10 "NewTop", E-0207). Music is
streamed from `Data/Sounds/MUSIC/<name>.wav`: `menu1` (menu), `credit` (About), the room
music (Continue). Stop-all ends every stream (menu, room, dialogue, credits and the fifth)
(E-0207).

## Save slots (gilbert.ini)

`.\gilbert.ini` in the current directory (E-0216): `[SAVEDGAMES] total=50` and
`[SLOT1]`..`[SLOT50]` with `file=` and `name=` (all empty on the disc). Names are read for
slots 1..50 (default `default` when the key is missing). Loading slot n reads
`HDPath\data\game\<file>` (default `default.dat`; an empty `file=` gives a path that
cannot load). Saving slot n (not when `InstallationType` = −1) writes `file=game<n>.dat` and
`name=<typed name>`, then `GESaveFile(HDPath\data\game\game<n>.dat)`.

## ge.dll from the boot and the menu

(E-0214, E-0217; the calls themselves are specified with ge.dll.)

- `GEInit(cb1..cb22)`, 22 function pointers, stdcall, argument 1 first:
  1 GotoWalkmap (loads a room, mode 1), 2 refresh the room's objects, 3 GotoCUA, 4 refresh
  the close-up's objects, 5 refresh the inventory, 6 dialogue, 7 PlayWave(list, index,
  looped, wait), 8 StopWave(list, index), 9 load a wave list, 10 music(name, loop, kind:
  0 room music, 1 dialogue stream, 2 another stream), 11 nothing, 12 play a film, 13/14
  Gilbert's position, 15/16 nothing, 17/18 the room map's width/height in cells, 19 a map
  cell, 20 Gilbert's walking direction (rooms.md, E-0308), 21 a sound (list 1 item 10), 22
  nothing.
- `GEExit`, `GEInit` again, `GELoadFile(path)` (non-zero = loaded), `GEStartNewGame` (new
  game), `GEContinueGame` (after a load), `GESaveFile(path)`, `GEEllapsed` every tick,
  `GEGetVariable(198)` every tick.

## Quirks kept from the original

- Hit tests use the last drawn place of each picture, so buttons of pages not shown can
  still be hit where they were last drawn; the actions check the page (E-0213, E-0215).
  Visible effect (E-0219): on Settings, after Load or Save was shown, the stale
  Åbn/Gem rectangle (258, 302)–(319, 326) covers the lower right of the video button
  (246, 294)–(275, 323), where a press does nothing, and the stale down arrow ((301, 272)–
  (316, 284) after Load, (301, 241)–(316, 253) after Save) covers the right edge of sound
  button 6 (279, 247)–(308, 276), where a press only plays click 1 (all rectangles before
  the mouse's ±3 widening).
- The right-side gate stops at x 512 (mouse x ≤ 514), so the right end of the column
  buttons does not update the hover (E-0213).
- A pressed column button stays pressed (drawn pressed, its action re-run) until the next
  press elsewhere (E-0212).
- Save is disabled after a new game when `InstallationType` is −1 (E-0214).
