# Close-ups, inventory, dialogues, books, map (Gilbert)

The game screens of `Gilbert.exe` other than the walkmap room: the close-ups (CUAs, mode 2)
with the inventory, the map (a close-up too), the dialogue box (an overlay), the books
(mode 4) and the unused mode 5. The room (mode 1), its panel, the radar, the eggs and the
area hits are in `rooms.md`; ge.dll's rules (events, anims, which objects are listed) in
`logic.md`. Addresses are `Gilbert.exe`; names in
`engines/gilbert/notes/names/GILBERT.EXE-screens.csv`.

## Conventions

As in `boot.md` (screen, clip rectangle (64, 50)–(576, 430), `i1`/`i2`/`cur` pictures drawn
fuchsia-transparent at their top-left corner, last-drawn rectangles for hit tests, colours as
RGB, GDI text in Arial). Also:

- **Mouse** (E-0506): the point (x, y) and the 6×6 *mouse rectangle* (x − 3, y − 3)–(x + 3,
  y + 3), both updated on every mouse move. A picture or rectangle is *hit* when it overlaps
  the mouse rectangle; an object or inventory item is *under* the mouse when its rectangle
  contains the point.
- **Button state:** −1, or 1 (left) / 2 (right), set on mouse down (and on a move with that
  button held while the state is −1), −1 on any mouse up. A screen sees a *press* when the
  state differs from the last state it saw and is now 1; it then stores the state as seen.
  Mouse up also sets the last state to −1.
- **Buttons:** each tick the hovered item and the pressed item are computed; the frame draws
  the hover picture over the hovered button and the pressed picture over the pressed one and
  calls `gmenu::Action(item)` for it. *Click n* is `PlayWave(list 1, n)` (`menu.wxs`,
  `boot.md`). Most actions clear the hover and pressed items, so they run once per press.
- **Cursor:** `cur[k]` at (x − 16, y − 16), the mouse kept inside x 72..568, y 58..422
  (`boot.md`). k is 0 (VANLIG) in every screen here except the book's pointing hand, 7
  (TOPOINTER).
- **Tables:** the close-up objects and the inventory items are copied from ge.dll into two
  tables of records (E-0501, E-0507):

  | Field | CUA object | Inventory item |
  |---|---|---|
  | code | object ID · 100 + state | the same |
  | picture | index in the close-up's pictures, or −1 | — |
  | icon | pattern in the inventory strip (0..160) | the same |
  | text | the state's description (Danish) | the same |
  | x, y | position in the 512-wide view | — |
  | pickable | the state's flag | — |
  | rect | (64 + x, 50 + y, 64 + x + w, 50 + y + h), w × h the picture's size | the grid cell (below) |

## Ticks by mode

The main loop (`boot.md`) runs per tick (E-0502, E-0511, E-0514):

| Mode | Screen | Tick |
|---|---|---|
| 2 | close-up (and map) | cua::Draw; if a dialogue is open: dialogue mouse, dialogue draw; cua::HandleMouse; cursor; flip |
| 4 | book | book::Draw; if a dialogue is open: dialogue mouse, dialogue draw, else book::HandleMouse; cursor; flip **only every other tick** |
| 5 | unreachable (below) | mode5::Draw; mode5::HandleMouse; cursor; flip |

Then the stream updates of every mode (`boot.md`, `rooms.md`). The room (mode 1) shows the
dialogue the same way (`rooms.md`).

## Close-ups (mode 2)

### Entering (GEInit call-back 3, cua::Load 0x47a838)

ge.dll's GotoCUA (event type 3) calls call-back 3 with the CUA ID, then call-back 4 (the
objects), then the CUA's first-visit or later event (`logic.md`). Call-back 3 (E-0500):

1. The timer stops; every sound stream stops.
2. The close-up picture list is emptied and loaded: ID 999 → `Data/maps/!global/kartmap.wxi`;
   any other → `Data/maps/<current room>/cua<ID>.wxi` (resolve). The folder is the room shown
   now, not the walkmap named by the event.
3. Object count := 0; for IDs other than 999 the radar values are read again
   (GEWalkmapGetRadarRect, `rooms.md`); mode := 2.
4. The room music, if one is set, starts again from the beginning (looped); the timer runs.

No fade. Item 0 of the collection is the background (512×320 in most, 512×340 or 580×340 in
three, 512×324 for the map), the others are the object pictures.

`cua999.wxi` in every room folder (and in `Data/maps/`) is a byte-for-byte copy of
`kartmap.wxi` that the game never opens (E-0500).

### Objects (GEInit call-back 4)

Call-back 4 (gecb::RefreshCUAObjects 0x474a38) refills the CUA table from
GECUAGetNumObjects and GECUAGetObjectData (out-parameters: code, picture, icon, x, y,
pickable, text) and computes each rectangle from the picture's size (E-0501). ge.dll calls
it when the close-up opens, after taking or using an object, and whenever an object's anim
moves to its next anim. ge.dll lists at most 100 visible objects, ordered by anim z from the
highest (index 0) to the lowest. The picture is the anim's picture index (CAnim +0x28) in
the close-up's collection; x and y are the state's first anim's +0x1c, +0x20.

### Frame (cua::Draw 0x4794c0)

In this order (E-0502, E-0503):

1. Clear; the background (item 0) at (64, 50).
2. The objects from the last table index to the first (lowest z first), each its picture at
   (64 + x, 50 + y); skipped: the object on the cursor and pictures outside the collection.
3. The frame (cua::DrawFrame 0x46e414): `i1[0]` at (64, 50); the eggs by variable 199
   (`rooms.md`) at (296, 374); `i2[5]` iscr13 (the inventory box, 167×50) at (371, 375); the
   inventory items (below); `i2[6]` the radar island at (151, 347) with its pulsing rectangle
   (as in the room, `rooms.md`, but the alpha runs 0..150 here); `i2[0x26]` Menu at (70, 368);
   `i2[0x98]` a red, inactive "Kort" at (70, 396); scroll up `i2[0x2c]` at (537, 380) and down
   `i2[0x2d]` at (537, 400); the book button `i2[8]` at (298, 333), blinking while a topic is
   new (`rooms.md`); `i2[0x77]` at (509, 336) and back `i2[0x73]` at (513, 340).
4. Hover pictures: Menu `i2[0x28]`, up `i2[0x2e]`, down `i2[0x2f]`, back `i2[0x74]`; pressed:
   Menu `i2[0x2a]`, up `i2[0x30]`, down `i2[0x31]`, back `i2[0x75]`, each with its action
   (below). The book button and "Kort" can be hovered and pressed but show nothing and do
   nothing here.
5. The descriptions (below): the hovered object's, then the hovered inventory item's.
6. The carried object (below).

### Mouse (cua::HandleMouse 0x473008)

Each tick (E-0504, E-0505):

1. Hovered object := the first table entry under the mouse; hovered inventory item := the
   last one under the mouse. Cursor 0.
2. Hovered button := the first hit of the book button, Menu, Kort (0x27, at its room place),
   up, down, back; else none.
3. On a press: for **every** object under the mouse, in table order, unless the point is in
   (509, 336)–(589, 396) (the back button's corner): `GEClickObjectInCUA(code)`; ge.dll runs
   the state's click event only if the state is not pickable. Then the pressed button := the
   same first hit as the hover.

### Descriptions (ui::DrawTooltip 0x477fbc)

For the hovered object: text at x = rect left, y = the rectangle's vertical middle
(top + (bottom − top) div 2); for the hovered inventory item: x = its cell's left, y = its
top − 10. An empty text draws nothing. Arial 8 regular, w = its width; x kept in 80..560, y
≥ 66, and x −= w when x + w > 560. A black box at alpha 120 (Q-0202) fills (x − 4, y − 2)–
(x + w + 4, y + 16), then the text in tan (221, 189, 142) at (x, y) (E-0505).

### Taking and using (cua::PickUp 0x475c14, cua::Drop 0x475d04)

- **Mouse down** (either button) in mode 2 (E-0506): the last pickable object under the
  mouse goes on the cursor, and the last inventory item under the mouse goes on the cursor;
  each remembers the grab offset (point − rect top-left). While carried, an object is drawn
  as its inventory icon at (x − 16, y − 16) and left out of the view; an inventory item is
  drawn at (x − offset x, y − offset y) and left out of the grid.
- **Mouse up** (either button), with something carried, in mode 2:
  1. No objects in the table → nothing.
  2. A close-up object carried and the point in (364, 367)–(576, 429) (the inventory box) →
     `GEObjectToInventory(its code)`: ge.dll moves it to the inventory, runs its take event and
     calls call-backs 4 and 5 (the tables are rebuilt at once).
  3. A close-up object carried: for every other object under the mouse,
     `GEUseObjectOnObject(carried code, that code)`.
  4. An inventory item carried: for every object under the mouse, `GEUseObjectOnObject(item
     code, object code)`. ge.dll runs the matching use event, or nothing if the pair has none.
  5. Nothing is carried any more.

  In any other mode, mouse up just drops what is carried. Inventory items can only be used on
  close-up objects; dropping one elsewhere does nothing.

### Buttons (gmenu::Action in mode 2)

| Item | Action |
|---|---|
| up 0x2c | click 1; if the inventory top > 5: top −= 6, new layout |
| down 0x2d | click 1; if top + 12 ≤ count: top += 6, new layout |
| back 0x73 (only when no dialogue is open) | click 4, stop all sounds, mode 1, `GECUAEnd` (ge.dll rebuilds the room's objects and runs the CUA's end event), the room music again (looped) if set |
| Menu 0x26 | click 2, stop all sounds, mode 0 (the menu stays silent: the counter is not reset and `menu1` not opened; Q-0501) |

Each clears the hover and pressed items (E-0504). Leaving happens only through back, Menu or
an event (a walkmap change, `logic.md`); no key does anything here.

### While a dialogue is open

The dialogue takes the press first (below), so no object is clicked and no button pressed;
hovering and the descriptions go on, and a mouse down still picks up an object under the
box (E-0506, E-0510).

## The map (close-up 999)

"Kort" in the room (`rooms.md`) calls `GEWalkmapAreaHit(99999)`, i.e. event room · 100 + 99;
each of the 38 rooms has one: Goto CUA 999 (E-0514). So the map is an ordinary close-up:
`kartmap.wxi`'s background (the island, 512×324) and nine place symbols (CUA 999's objects
99901..99909: beach, desert, pier, forest ×2, glacier, glade, laboratory, mine; pictures 1,
3, 5, 7, 8, 11, 13, 15, 17 of `kartmap.wxi`), each with a description ("Til stranden" …).
Clicking a symbol runs its event 9901..9909: go to a room at a start point, and a sound.
Back returns to the room. The radar values are not re-read for the map.

## Inventory

(E-0507, E-0506)

- **Pictures:** `Data/maps/!global/inventory.wxi` is one strip `inv` of 3563×20 with a
  pattern width of 22: 161 icons of 22×20, numbered 0..160. An object state's icon is
  CObjState +0x1c (every pickable state has one). `inventory-num.wxi` is never loaded.
- **Contents (GEInit call-back 5):** count := `GEInventoryGetNumObjects`; per item
  `GEInventoryGetObjectData(i)`: code, icon, text; the visible inventory objects in the order
  they were taken. Then the layout.
- **Layout:** 12 cells shown from *top* (0 at a new game or load): item k (top ≤ k <
  min(top + 12, count)), column c = (k − top) mod 6, row r = (k − top) div 6: cell (377 + 27c,
  377 + 26r)–(404 + 27c, 403 + 26r), icon drawn at (378 + 27c, 377 + 26r). Items not shown
  get an empty rectangle. Scrolling by 6 with the arrows (Buttons, above).
- **Where:** only in close-ups: the room's panel draws neither the box's contents nor the
  arrows as active (`rooms.md`), and taking and dropping work only in mode 2.

## Dialogues

### Opening (GEInit call-back 6, gecb::Dialog 0x47454c)

ge.dll calls call-back 6 when a dialogue starts (event type 9). It reads (E-0508): the title
(`GEDialogGetTitle`; shorter than 3 characters → two spaces), the text (`GEDialogGetText`,
the same rule), the choices (`GEDialogGetNumChoices`, `GEDialogGetChoice(i)`) and opens the
box. The **print message** (the book's Udskriv button) uses the same box: title three spaces,
text = language lines 20..24 each followed by LF (lines 21..24 only if longer than 2
characters), one choice, line 25 ("Okay").

### Layout (dialog::Layout 0x475fdc, every tick)

(E-0509; pixel sizes depend on the font, Q-0205)

1. Choices in Arial 8 regular: width and height of each; W = the widest; H = 18 · n.
2. Title in Arial 9 bold: W = max(W, its width); H += its height.
3. Text split at each LF, each line trimmed; L = the number of LFs; *off* = (height of line 0
   in Arial 9 bold) · L.
4. Lines in Arial 8 regular: W = max(W, widest line); H += the height of each line.
5. Box (left, top, right, bottom) = (310 − W div 2, 240 − H div 2, 330 + W div 2, 240 + H div 2).
6. Choice k's row: (left + 5, top + 25 + 18k + off)–(right − 5, top + 41 + 18k + off).

### Drawing (dialog::Draw 0x479018)

Over the screen's frame, before the cursor (E-0509):

1. Black at alpha 180 over (left, top − 16)–(right, bottom).
2. Corners `i2[0x9f]` at (left − 2, top − 17), `i2[0xa0]` at (right − 8, top − 17),
   `i2[0xa1]` at (left − 2, bottom − 8), `i2[0xa2]` at (right − 8, bottom − 8); edges stretched:
   `i2[0xa3]` (10×3) to (left + 2, top − 17)–(right − 2, top − 14) and (left + 2, bottom − 1)–
   (right − 2, bottom + 2), `i2[0xa4]` (3×10) to (left − 2, top − 14)–(left + 1, bottom − 8)
   and (right − 1, top − 14)–(right + 2, bottom − 8).
3. Text line i at (left + 10, top − 6 + 12i), Arial 8, tan.
4. Choice k at (left + 10, top + 20 + 18k + off), Arial 8: tan when hovered or pressed,
   grey (127, 127, 127) otherwise.

The title is measured but never drawn (the database's titles are internal names).

### Choosing (dialog::HandleMouse 0x473f74)

Hovered choice := the last k whose (row left, row top)–(row left + its width + 10, row
bottom) is hit. On a press: pressed := the last such k; if there is one, the box closes and
`GEDialogEnd(k)` runs choice k's event (nothing for the print message). Right clicks and
keys do nothing (E-0510).

### Voices

The box does not play anything. The event that starts a dialogue also has a type-6 record
whose sound name is a number and whose kind is 1: call-back 10 then stops every stream (the
room music too, until a close-up opens or closes or the room changes) and plays
`Data/Sounds/Dialog/<name>.wav` once on the dialogue stream (E-0510, E-0308). The numbers
are data, not derived from dialogue IDs (377 names; `8456` has no file; 235 files are never
named). There is no lip sync and no subtitle timing: the text stays until a
choice is clicked, the voice runs on independently.

## Books (mode 4)

### Opening and leaving

The room panel's book button (`rooms.md`) loads `bookimages.wxi` (again, each time), builds
the list of book 1 from topic 0, sets the tab to Ordliste, clears the new-topic blink and
sets mode 4 (E-0306, E-0513). Tilbage returns to the room (mode 1). Close-ups have no way
into the book.

### Tabs

| Button (item, place) | Book | Title picture at (192, 56) |
|---|---:|---|
| Ordliste (0x4e, (88, 354)) | 1 | `i2[0x7b]` |
| Tips (0x52, (206, 354)) | 0 | `i2[0x7a]` |
| Gilberts venner (0x53, (88, 387)) | 2 | `i2[0x79]` |
| Eksperimenter (0x51, (206, 387)) | 3 | `i2[0x78]` |
| Udskriv (0x50, (325, 387)) | print message | — |
| Tilbage (0x4f, (443, 387)) | back to the room | — |

Hover pictures are item + 6 (0x54..0x59), pressed item + 12 (0x5a..0x5f), at the same
places. A pressed tab stays pressed (and shows its title) until another button in the bar
is pressed; its action runs every tick the mouse is over it, but does its work only the
first time and only if the book differs from the current one: click 2, list of that book
from topic 0, scroll 0 (E-0511, E-0513).

### Frame (book::Draw 0x46ec90)

`i2[0]` and `i2[0x6f]` s03bkg at (64, 50); the list or the page (below) at (135, 95), rows
of its surface 355 wide and 320 high, fuchsia transparent; `i1[0]` at (64, 50); `i2[0x41]`
ilbkg01 at (64, 337); the six buttons; the arrows back-to-list `i2[0x69]` at (115, 93), up
`i2[0x7e]` at (503, 93), down `i2[0x81]` at (503, 343), hover picture item + 1, pressed item + 2;
the tab's title. The flip happens every second tick (E-0511).

### The list (book::BuildList 0x46aa54)

Up to 20 topic titles of the book from rank *first* (the shown topics in book order,
`GEBookGetNumTopics`, `GEBookGetTopicFromIndex`, `GEBookGetTopicTitle`), drawn onto a 355×320
fuchsia surface (E-0512). Per title, from (10, y), y = 0, 12, 24, …: the title's markup is
parsed (`GEBookParseFirst`/`Next`): text in (128, 45, 25) with the current format (Arial 8,
`\f` formats below), `\t` → x = (x div 20 + 1) · 20, line feed → next line; links and
pictures are ignored. Each title's click rectangle on screen: (x₀ + 135, y₀ + 103)–(x₁ + 135,
y₁ + 115), from its start and end positions.

### A topic page (book::BuildPage 0x46ada0)

`BuildPage(book, topic ID)` looks up the topic's rank (`GEBookGetIndexFromTopic`) and parses
its text (`GEBookGetTopic`) onto a 355×1000 fuchsia surface (E-0512):

- Start at (10, 10), Arial 8 regular in (64, 46, 26), line height 12.
- **Text** (each word and each space is its own token): if x + width > 344 → new line; draw at
  (x, y); x += width.
- **Formats** `\f<n>`: 0 size 8 regular; 1 adds bold; 2 adds underline; 3 adds both; 4 size
  10 regular; 5 size 10 bold (other numbers: no change).
- **Links** `\h<book>[:<topic>]` … `\h`: the text between is drawn in (128, 45, 25),
  underlined; its rectangle is (x₀ + 135, y₀ + 103)–(x₁ + 135, y₁ + 115) from the first word's
  place to the end position; after it the colour and format return.
- **Pictures** `\g<n>`: `bookimages.wxi` item n drawn at (x, y) (new line first if it would
  pass 354); x += its width; the line height becomes at least its height. Its fuchsia pixels
  end up transparent with the surface.
- `\t` → x = (x div 50 + 1) · 50 (new line if past 344); line feed → y += line height,
  x = 10, line height 12.

New line = y += the line height, x = 10, line height 12. A link to a hidden topic shows the
book's first hidden topic (ge.dll's lookup by rank −1, E-0512).

### Mouse (book::HandleMouse 0x4734b8)

(E-0513)

- Cursor 0, or 7 over a list title (list view) or a link (page view, rectangles moved up by
  the scroll) while no button is held.
- Hovered tab: the first bar button hit, when the mouse is in (64, 360)–(576, 430). Hovered
  arrow: the first of up, down, back-to-list hit, when the mouse is in (500, 90)–(525, 360)
  or (114, 90)–(130, 125).
- On a press: a link → switch to its book (tab: 0 Tips, 1 Ordliste, 2 Gilberts venner, 3
  Eksperimenter; scroll 0) and show its page; a list title → show its page. Otherwise the
  pressed tab and arrow := the ones hit (inside their regions).

### Arrows

| Arrow | List view | Page view |
|---|---|---|
| up (0x7e → action 0x63) | click 1; first −= 10 (not below 0), rebuild | click 1; scroll −= 24 (not below 0) |
| down (0x81 → action 0x66) | click 1; first += 10, at most count − 20 (not below 0), rebuild | click 1; scroll += 24; from 1000 on it becomes 999 (Q-0500) |
| back to list (0x69) | click 1; the list from 0, scroll 0 | the same |

The page shows surface rows scroll..scroll + 320.

## Mode 5

Mode 5 is set only by Kort pressed in mode 2, which the close-up frame never acts on, so it
cannot be reached (E-0514). Its frame would draw an empty image list. The engine does not
need it.

## Fades

None of these screens fades; the only fades are the room's (`rooms.md`).

## GEInit call-backs used here

(`boot.md` lists all 22.)

| # | Here |
|---|---|
| 3 | GotoCUA → cua::Load |
| 4 | refresh the CUA table |
| 5 | refresh the inventory table and layout |
| 6 | open the dialogue box |
| 10 | kind 1: a dialogue voice (`rooms.md` for the others) |
| 12 | play a film (`boot.md`) |
| 15, 16, 22 | nothing |
| 20 | Gilbert's facing (`rooms.md`), not used here |
| 21 | a new topic: the book button blinks, sound `NewTop` |

## Quirks kept from the original

- Clicking in a close-up clicks every object under the mouse, top first, not just the top
  one; picking up takes the lowest pickable one (E-0504, E-0506).
- Dropping an inventory item first tries "use" with object code 0 (a table read one record
  too early), which matches nothing (E-0506).
- Menu from a close-up leaves ge.dll's close-up open and the menu silent (Q-0501).
- The book redraws on every tick but flips on every second one (E-0511).
- The dialogue's choice rows sit lower for texts with several lines, by the bold 9-point line
  height per line feed, though lines are 12 apart (E-0509).
