# Game rules: ge.dll (Gilbert)

What `ge.dll` does behind its `GE*` exports: the game object and its call-backs into
`Gilbert.exe`, the tick (animations, path stepping), walkmaps and close-ups (CUAs), objects,
inventory, events, dialogues, books, texts, variables and the path finder. The data is
`default.dat` (formats README, `default.dat` section: classes, fields, event types); this
spec adds the behaviour. Addresses are `ge.dll` (`/gilbert-import/GE.DLL`); names in
`engines/gilbert/notes/names/GE.DLL-gamedat.csv` and `GE.DLL-logic.csv`. What `Gilbert.exe`
does with the results belongs to the rooms spec; where this spec needs an EXE fact it says so.

## Conventions

- **Object code** = `id * 100 + state` (formats README). `code / 100` and `code % 100` are C
  integer division and remainder.
- **Lists** keep file order (MFC `CObList`); "the first X with id n" is the first in that
  order. Anim IDs are unique except 40340, which occurs twice: the first wins (E-0402).
- **Runtime fields** not in the file: the game object's current walkmap and current CUA
  (0 = none), the current dialogue, the path state, the two object arrays below, and each
  CObjState's *current anim* (a CAnim, 0 at creation) (E-0400, E-0402).
- **Logging**: ge.dll formats log lines (the strings quoted in the formats README) into an
  empty sink (`GameObj::Log` 0x10009340 is `ret`); nothing is shown (E-0400).
- **Call-back n** = the n-th argument of `GEInit` (below). "Refresh walkmap" = call-back 2,
  "refresh CUA" = call-back 4, "refresh inventory" = call-back 5.

## Game object and call-backs (GEInit, GEExit)

`GEInit(cb1..cb22)` stores the 22 function pointers, then creates a fresh game object
(E-0400): no walkmap, no CUA, no dialogue, no path (stopped, 0 items), empty lists, empty
object arrays, and seeds the random generator with the time (`srand(time(NULL))`). Nothing
is loaded: the EXE calls `GELoadFile` next (boot spec). `GEExit` destroys the object.
While no object exists every export does nothing and returns 0 or an empty string (texts
and books ""; `GETextGetText` a null pointer) (E-0400).

Who calls each call-back, with what (E-0400; EXE meaning from E-0217, E-0308, E-0406,
E-0410):

| n | Arguments | Called by | EXE meaning |
|---:|---|---|---|
| 1 | walkmap id, x, y, direction, 0 | GotoWalkmap | load the room, place Gilbert at x, y facing *direction* |
| 2 | — | GotoWalkmap, CUAEnd, the tick | re-read the walkmap objects |
| 3 | CUA id | GotoCUA | open the close-up |
| 4 | — | GotoCUA, UpdateCUA | re-read the CUA objects |
| 5 | — | UpdateInventory | re-read the inventory |
| 6 | — | StartDialog | show the current dialogue |
| 7 | list, index, loop, 0 | event 6 (numbered sound) | PlayWave(list, index, loop ≠ 0, wait ≠ 0) |
| 8 | list, index | event 17 (numbered) | StopWave |
| 9 | — | never | — |
| 10 | name, loop, kind | event 6 (named sound) | stream `name`: kind 0 room music, 1 dialogue voice, 2 other |
| 11 | — | event 17 (named) | nothing |
| 12 | film name | event 10 | play the film |
| 13, 14 | — → x, y | path finder, GESaveFile | Gilbert's position in room pixels |
| 15, 16 | — → w, h | path finder | cell size: the EXE returns 16, 16 |
| 17, 18 | — → w, h | GEPathNewPath | the room's control map size in cells |
| 19 | x, y → value | GEPathNewPath | one control-map cell |
| 20 | direction code or −1 | path stepping, PathStop | walk in that direction / stop |
| 21 | 1 or 0 | events 5, 21 (0), 22 | a book topic appeared (the EXE ignores the argument: flag + sound "NewTop", list 1 item 10) |
| 22 | — | never | — |

**Direction codes** (call-backs 1 and 20): 0 N, 4 NE, 8 E, 12 SE, 16 S, 20 SW, 24 W, 28
NW (clockwise from north in steps of 4; y grows downwards) (E-0410).

## The tick (GEEllapsed)

The EXE calls `GEEllapsed` once per timer tick in every mode, the main menu included (boot
spec E-0210). Each call (E-0401):

```
now = timeGetTime(); dt = now - last; last = now          (milliseconds)
list = current CUA ? cuaObjects : walkmapObjects
changed = false; ends[] = 0
for i in list:  changed |= StepAnim(list[i], dt, &ends[i])
if changed:
    current CUA ? UpdateCUA() (call-back 4) : call-back 2
    for i in list order: if ends[i] != 0: DoEvent(ends[i])
PathEllapsed()                                             (path stepping, below)
```

`StepAnim(obj, dt)`: `a` = the current anim of the object's current state; if there is none,
or its duration is 0, nothing. Else `t = a.time + dt`:

- `t > duration` (strictly): the end event is `a.end_event`; `a.time = t % duration`; the
  state's current anim becomes `FindAnim(a.next)` if that exists (else stays `a`); the
  (new) current anim's time := 0; returns *changed*.
- otherwise `a.time = t % duration` (so `t == duration` wraps to 0 without switching, no end
  event, not *changed*).

`time` belongs to the CAnim, not to the object: two objects shown with the same anim advance
it twice per tick (5 anim IDs are shared within one walkmap or CUA in default.dat) (E-0402).
While a CUA is open only the CUA's objects advance; the walkmap's are frozen, and vice
versa. `last` is reset when an object list is built with a reset (walkmap build, CUA
entry), so the first tick after it has dt ≈ 0.

Every anim that wraps with a nonzero duration counts as *changed*, even a self-looping one
(470 anims have `next` = their own id, 460 have duration 0 and never step; 58 have an end
event) (E-0402).

## Walkmap and CUA objects

### The lists

**Walkmap list** (`BuildWalkmapObjects` 0x10008170; built by GotoWalkmap and CUAEnd,
E-0402): for each CCUA of the current walkmap (list order), for each of its CObjs (list
order): if the object is visible and its current state's `walkmap_anim` names an existing
anim, append it and set that state's current anim to it. At most 100 entries (the walkmap
with the most objects has 72). Then `ClearAnims` (below), `last` := now, BuildSort.

**CUA list** (`BuildCUAObjects(reset)` 0x10008220, only while a CUA is current): the current
CUA's CObjs (list order) that are visible and whose current state's `cua_anim` exists;
at most 100 (largest CUA: 31). It does **not** set the states' current anims. With
`reset` (GotoCUA only): `ClearAnims`, `last` := now. Then BuildSort. Without a current
CUA it does nothing. Events and the inventory exports call it without reset (below).

**ClearAnims** (0x10008300): for each listed object, for **every** state of it: the state's
current anim := FindAnim(walkmap_anim) (walkmap list) or FindAnim(cua_anim) (CUA list),
and that anim's time := 0; states whose anim field is 0 are skipped; an ID that does not
exist stops ClearAnims there (none in default.dat).

**BuildSort** (0x10007e90 walkmap, 0x10008000 CUA): a selection sort into descending z,
where z is the `z` of FindAnim(state.walkmap_anim) (resp. `cua_anim`) of the object's
current state (the state's base anim, not its current anim; 0 if missing). For each output
position, the scan keeps the **last** entry with the highest remaining z (`best <= z`), so
equal z come out in reverse list order. z is 0..10 in default.dat (E-0402).

The walkmap list is rebuilt only by GotoWalkmap and CUAEnd. Events that show, hide,
remove or change objects rebuild the CUA list only (below), so while the walkmap is shown a
changed walkmap object keeps its old entry until the next rebuild (Q-0401).

### GEWalkmapGetNumObjects, GEWalkmapGetObjectData

`GEWalkmapGetNumObjects()` = the walkmap list's length (also while a CUA is open).
`GEWalkmapGetObjectData(i, &code, &picture, &icon, &x, &y, &pickable, &text)`, for
`i` < length, with `s` = the object's current state and `a` = s's current anim (E-0402):

| Out | Value |
|---|---|
| code | `obj.id * 100 + s.state` |
| picture | `a` +0x28: item of the room's object collection (`w<room>o.wxi`) |
| icon | `s` +0x1c: pattern of `inventory.wxi` |
| x, y | `a` +0x1c, +0x20: the picture's top-left corner |
| pickable | `s.pickable` |
| text | `s.text` (Danish description) |

Returns 1; 0 (outputs untouched) when `i` is out of range, there is no state or no current
anim. The EXE draws the picture's rectangle at (x + 64, y + 50) (E-0403).

### GECUAGetNumObjects, GECUAGetObjectData

The same for the CUA list, with these differences (E-0402): x, y come from
`FindAnim(s.cua_anim)` (the state's base CUA anim), not from its current anim; picture is
the current anim's +0x28, or −1 if the state has no current anim; the call returns 0 when
`s.cua_anim` is 0 or does not exist. picture is an item of `cua<id>.wxi` (E-0403).

### GEWalkmapGetRadarRect, GEWalkmapGetTitle

`GEWalkmapGetRadarRect(&x, &y, &w, &h)`: the radar rectangle (left, top, right, bottom) of
the current CUA's walkmap if a CUA is current, else of the current walkmap, else all 0;
returned as x = left, y = top, w = right − left, h = bottom − top (E-0404).
`GEWalkmapGetTitle()` returns the current walkmap's title (not imported by the EXE).

## Moving between places

**GotoWalkmap(id, x, y, direction)** (0x10008fa0, E-0404): PathStop; current walkmap :=
FindWalkmap(id) (0 if none: logged, nothing else); build the walkmap list; call-back 1(id,
x, y, direction, 0); call-back 2. It does not touch the current CUA (event 4 ends it first).

**GotoCUA(id)** (0x10009090): PathStop; current CUA := FindCUA(id) over all walkmaps' CUAs
(0 if none: logged, nothing else); BuildCUAObjects(reset); call-back 3(id); call-back 4;
then if the CUA's `first_visit` ≠ 0: DoEvent(first_event), first_visit := 0; else
DoEvent(event). The current walkmap stays.

**GECUAEnd()** (CUAEnd 0x10008930): without a current CUA nothing. Else remember its
`end_event`, current CUA := 0; if a walkmap is current: build the walkmap list, call-back 2;
then DoEvent(end_event) if ≠ 0.

**GEWalkmapAreaHit(n)** (0x10008710): DoEvent(current walkmap id * 100 + n % 100) (needs a
current walkmap). The EXE calls it with n = cell value − 1 when Gilbert, on his path,
walks into control-map cells 2..31 (E-0307), and with n = 99999 from the game screen's
button `ibutt15` (interface2 item 0x27), i.e. event `walkmap * 100 + 99`, which opens CUA
999, the travel map ("Till karta för snabb förflyttning") (E-0411). An area without an
event (rooms 556 and 558, value 10) does nothing.

## Objects and the inventory

**Finding objects**: `FindObj(id)` searches every object of every CUA and the inventory as
they were at load time (an index list built by GELoadFile); objects keep their entry when
they move to the inventory (E-0404). Events 1 and 8 delete objects; the original leaves
their index entry dangling (Q-0401).

**SetState(obj, n)** (`CObj::SetState` 0x10009e40): the state with number n; if there is
none the original stores a list node instead of the first state (a bug, Q-0400). All
default.dat records that set a state name an existing one (E-0405).

**ResetStateAnim(s)** (0x100082c0): s's current anim := FindAnim(s.cua_anim) (if it exists)
with time 0. Used by events 2 and 14 even on the walkmap.

**UpdateCUA()**: call-back 4 (whether or not a CUA is open). **UpdateInventory()**
(0x10009230): the *shown inventory* := the inventory objects (in the order they were
added) whose `visible` ≠ 0; call-back 5.

**GEClickObjectInCUA(code)** (0x10008a20): o = FindObj(code / 100); if o has a current
state and that state is not pickable: DoEvent(state.click_event). A pickable state's click
does nothing here (the EXE takes it with GEObjectToInventory).

**GEObjectToInventory(code)** (0x10008b50): o = FindObj(code / 100); if o is in its CUA's
object list (the EXE only passes CUA objects; the original dereferences the owner without
a check) it is removed from it (else nothing happens), its owner := none, it is appended to the inventory; DoEvent(current
state's take_event); BuildCUAObjects(no reset); UpdateCUA; UpdateInventory. State and
`visible` are unchanged.

**GEUseObjectOnObject(code, target)** (0x10008cc0): the first CUseObj with `obj == code`
and `target == target` (exact codes, states included); if found: DoEvent(its event),
BuildCUAObjects(no reset), UpdateCUA, UpdateInventory; else nothing (logged).

**GEInventoryGetNumObjects()** = shown-inventory length. **GEInventoryGetObjectData(i,
&code, &icon, &text)**: the i-th shown object: code, current state +0x1c (the
`inventory.wxi` pattern), current state's text; nothing written when i is out of range or
the object has no state (E-0404, E-0403).

## Events (DoEvent, RunEvent)

`DoEvent(id)` (0x10005f70, E-0105): id 0 does nothing. Otherwise walk the event list from
the start and run every record whose id matches, in list order; when a record returns a
jump (only type 18), restart the walk from the start with the jump ID and forget the rest
of the current one. Events nest: a record can start other event chains (GotoCUA's events,
CUAEnd's end event, …), which run to completion before the next record.

Per type (0x100060f0, E-0405; operands as in the formats README; "obj" = the record's
object code, `id = obj / 100`, `st = obj % 100`):

| Type | Effect, in order |
|---:|---|
| 0, 11, other | nothing |
| 1 | o = FindObj(id); none → nothing. If o is in the inventory: delete it, UpdateInventory. Else if o is in its CUA's list: delete it, BuildCUAObjects, UpdateCUA. |
| 2 | o = FindObj(id); none → nothing. SetState(o, st); ResetStateAnim; BuildCUAObjects; UpdateCUA. |
| 3 | walkmap = 0 or cua = 0 → nothing. Else GotoCUA(cua); the walkmap operand is not used (41 of 117 records name another walkmap, mostly CUA 999). |
| 4 | if a CUA is current: CUAEnd (with its end event); then GotoWalkmap(walkmap, x, y, direction = +0x58). |
| 5 | t = FindTopic(book, topic); none → nothing. t.shown := 1; renumber the book ranks; call-back 21(1). |
| 6 | sound name empty: call-back 7(+0x38 list, +0x3c index, +0x48 loop, 0); else call-back 10(name, +0x48 loop, +0x44 kind). |
| 7 | o = FindObj(id); none, or o not in a CUA (already in the inventory), or not in its CUA's list → nothing. Else remove it from the CUA, append it to the inventory, SetState(o, st), visible := 1, UpdateInventory, BuildCUAObjects, UpdateCUA. No take event. |
| 8 | o = FindObj(id); if o is in the inventory: delete it, UpdateInventory. |
| 9 | StartDialog(dialog). |
| 10 | video name not empty: call-back 12(video). |
| 12 / 13 | the first object with that id that has a state st (and a current state): that state's pickable := 1 / 0. No call-back. |
| 14 | o = FindObj(id) with a current state: SetState(o, current state number + 1); ResetStateAnim; BuildCUAObjects; UpdateCUA. |
| 15 / 16 | o = FindObj(id); none → nothing. If o has a current state s: FindAnim(s.cua_anim) must exist (else stop here, `visible` unchanged); s's current anim := it, time 0. Then visible := 1 / 0; (15 only: ResetStateAnim); BuildCUAObjects; UpdateCUA; UpdateInventory. |
| 17 | sound name empty: call-back 8(+0x38, +0x3c); else call-back 11() (unused in the data). |
| 18 | jump (formats README); cond ≥ 6 never jumps. `rand() % 101` in the original: a number 0..100. |
| 19 / 20 | SetVariable (below). 20 adds to GetVariable's value. |
| 21 | t = FindTopic(book, topic); none → nothing. t.shown := 0; renumber; call-back 21(0). |
| 22 | t = FindTopic(book, topic), t2 = FindTopic(book, topic2); either missing, or t2's title and text both empty → nothing. Else t.title += t2.title, t.text += t2.text (no separator), t2's title and text := ""; renumber; **then** t.shown := 1; call-back 21(1). |

"BuildCUAObjects" in this table is without reset. Removing (1) or changing (2, 14, 15, 16)
an object that sits in the walkmap list does not rebuild it (Q-0401).

## Dialogues

`StartDialog(id)` (0x10009300): PathStop; current dialogue := FindDialog(id) (0 if none);
call-back 6. The EXE then asks (E-0407):

- `GEDialogGetTitle()` / `GEDialogGetText()`: the current dialogue's title / text;
  `*NO DIALOG*` (both) without one.
- `GEDialogGetNumChoices()`: its number of choices (0 without one).
- `GEDialogGetChoice(i)`: the i-th choice's text (list order); `*NO CHOICE*` when i is out
  of range or there is no dialogue.
- `GEDialogEnd(i)` (0x10008f60): current dialogue := 0 first; then, if the i-th choice
  exists, DoEvent(its event). Out of range: the dialogue just ends.

Choice +4 is never used (Q-0103).

## Books

Ten book types (0..9); default.dat fills 0..3. Each topic has `shown` and a *rank*: the
shown topics of a book numbered 0, 1, … in list order, −1 when hidden. Ranks are
renumbered after loading and by events 5, 21, 22 (E-0408). The EXE addresses topics by
rank (E-0408):

| Export | Returns |
|---|---|
| `GEBookGetNumBookTypes()` | books before the first empty one (4) (not imported by the EXE) |
| `GEBookGetNumTopics(book)` | shown topics in the book; 0 for book > 9 |
| `GEBookGetTopicTitle(book, rank)` / `GEBookGetTopic(book, rank)` | that topic's title / text; "" if book ≥ 10 or no topic has that rank |
| `GEBookGetTopicFromIndex(book, rank)` | its topic ID, 0 if none |
| `GEBookGetIndexFromTopic(book, id)` | the rank of the topic with that ID (−1 if hidden), 0 if none |

A rank lookup matches the stored rank exactly, so rank −1 (from a hidden topic) finds the
book's first hidden topic (E-0408).

**Parser.** `GEBookParseFirst(text)` points the cursor at `text` and returns the first
token; `GEBookParseNext()` the next one; `GEBookParseGetText/Format/LinkBook/LinkTopic/
Picture()` return the values the last tokens stored. Each call (0x10007b00, E-0408):

```
c = *cursor
NUL                 → 0 (end)
'\' 'f'  n          → format = atoi(n), skip the digits, skip one space → 2
'\' 'g'  n          → picture = atoi(n), skip the digits, skip one space → 5
'\' 'h'  digit…     → link book = atoi, skip digits; if ':' follows: link topic = atoi,
                      skip digits; skip one space → 3   (without ':' link topic keeps its
                      previous value)
'\' 'h'  other      → skip one space → 4
'\' 't'             → 6 (no space skipped)
'\' other           → text = "\", cursor on the character after '\' → 1
LF                  → text = "\n" → 7
' '                 → text = " " → 1
other control (CR…) → skip it, then as below (an empty run gives text = "")
otherwise           → text = the run up to '\', a space, a control character or the end
                      (bytes ≥ 0x80 belong to the run) → 1
```

`atoi` is C's `atol` (leading white space, a sign, digits); "skip the digits" skips only
digits, so a sign or space before the number stays in the text.

## Texts and variables

`GETextGetText(id)`: the text of the first CText with that ID, "" if none (not imported by
the EXE; the EXE has no other texts from ge.dll). `GEGetVariable(n)`: variable n for n ≤ 199,
0 above; `GESetVariable(n, v)` stores for n < 200 (not imported). Negative n is not checked
(none in the data). The EXE reads variable 198 every tick: ≠ 0 ends the game (boot spec).

## Starting, loading, saving

- `GELoadFile(path)` (formats README): replaces every list; renumbers the ranks; builds the
  object index and each object's owner CUA. Non-zero = loaded (E-0412).
- `GEStartNewGame()`: DoEvent(1), then UpdateInventory. Event 1's chain sets up the game and
  goes to the first walkmap (event 4) (E-0412).
- `GEContinueGame()`: GotoWalkmap(header walkmap, start x, start y, header +0x10), then
  UpdateInventory. A game saved inside a CUA resumes on its walkmap.
- `GESaveFile(path)`: writes the header with the current walkmap's ID, call-backs 13 and 14
  (Gilbert's position) and direction 0 (so a loaded game faces north), then every list
  as loaded, runtime changes included (object states, visibility, owners, inventory,
  topics, `first_visit`, anim times, variables).
- `GELoadTextFiles()` builds the lists from `db\*.txt` files that are not on the disc
  (development only; not imported).

## Path finding

### GEPathNewPath(x, y)

`x, y` = the clicked point in room pixels (E-0411). Steps (0x100055a0, E-0409):

1. `mw` = call-back 17, `mh` = 18, `cw` = 15, `ch` = 16. `cw` or `ch` = 0 → return 0.
   `mw > 100` or `mh > 80` → return 0.
2. Load the grid: `cell[x][y]` = call-back 19(x, y) for 0 ≤ x < mw, 0 ≤ y < mh.
3. start = (call-back 13 / cw, call-back 14 / ch) (unsigned), target = (x / cw, y / ch).
4. FindPath (below). Success → start stepping (PathEllapsed with *start*), return 1. Failure
   → PathStop, return 0 (the previous path's items stay readable, the path is stopped).

**Walkable** (0x10009930): a cell inside the search rectangle is walkable when its value is
0, never when it is 1, and otherwise only when it equals the target cell's value. So cells
≥ 2 (areas, E-0411) can be crossed only by a path that ends in the same area; a target
cell of value 1 is unreachable.

**FindPath(start, target)** (0x100095a0):

```
rect = [min(sx,tx) - 3, max(sx,tx) + 4) × [min(sy,ty) - 3, max(sy,ty) + 4)   (half-open)
rect = rect ∩ [0, mw) × [0, mh)
Search(rect)
if target has no parent: Search([0, mw) × [0, mh))
if target has no parent (or start == target): fail
walk parents from target back to start: n0 = start, n1, …, nK = target
items[i] = (x, y) of n_i and dirs[i] = direction index from n_i to n_(i+1), i = 0..K-1
count = K
```

The target cell is not among the items; `items[0]` is the start cell.

**Search(rect)** (0x10009b60), a FIFO label-correcting search:

```
for every node: parent = none, next = none, cost = 0x7FFFFFFF
start.cost = 0; tail = start; n = start
while n:
    if n != target:
        for d in 0..7:  (E, NE, N, NW, W, SW, S, SE: dx = 1,1,0,-1,-1,-1,0,1;
                         dy = 0,-1,-1,-1,0,1,1,1)
            m = n + (dx[d], dy[d])
            if m in rect and Walkable(m):
                c = n.cost + StepCost(n, target, d)
                if c <= m.cost:                      (ties replace the parent)
                    m.cost = c; m.parent = n
                    if m.next == none and m != tail: tail.next = m; tail = m
    nxt = n.next; n.next = none; n = nxt
```

**StepCost(n, target, d)** (0x100097d0):

```
dx = target.x - n.x;  ndy = n.y - target.y          (y up)
bearing = dx != 0 ? trunc(atan(ndy / dx) * 57.29577951308232) : (ndy > 0 ? 90 : ndy < 0 ? -90 : 0)
if dx < 0: bearing += 180
a = (bearing + 45 * (16 - d)) % 360;  if a >= 180: a = 359 - a
cost = (a + 22.5) / 45 + 1;  if d is odd: cost *= 1.41
return trunc(cost)
```

(a is the angle between step d and the straight line to the target; a step straight at the
target costs 1, or 2 diagonally; straight away 5, or 7.)

### Stepping (PathEllapsed, every tick)

Direction index → code for call-back 20: 0 → 8 (E), 1 → 4 (NE), 2 → 0 (N), 3 → 28 (NW),
4 → 24 (W), 5 → 20 (SW), 6 → 16 (S), 7 → 12 (SE) (E-0410). The ge.dll never moves Gilbert:
it sets the walking direction and the EXE moves him at its own speed. `cell(p)` = (x /
cw, y / ch) of Gilbert's position from call-backs 13, 14. State: index `k`, target cell,
`dist`, `drift` flag, last position (0x10005890):

```
start (from GEPathNewPath):
    call-back 20(code(dirs[0])); target = items[count > 1 ? 1 : 0]; k = 1
    stopped = false; drift = false; dist = 0; last = Gilbert's position
each tick (after the anims), unless stopped or count == 0:
    if k >= count: call-back 20(-1); stopped = true; return
    if cell(Gilbert) == target:
        call-back 20(code(dirs[k])); k += 1
        target = items[min(k, count - 1)]; drift = false; dist = 0
    else:
        dist += trunc(sqrt((last.x - x)² + (last.y - y)²)); last = (x, y)
        if dist² > ch² + 2·cw² (768):  drift = true
        elif not drift: return
        (drift) head straight for the target cell, one axis at a time:
            cell.x < target.x → 8 (E); cell.x > target.x → 24 (W);
            else cell.y < target.y → 16 (S), otherwise 0 (N)
        call-back 20(that code)
```

So Gilbert follows the cell chain; once the last item is reached he gets the last
direction (into the target cell) for one tick and then stops. `PathStop` (0x10005d00,
also `GEPathStop`, and GotoWalkmap, GotoCUA, StartDialog): call-back 20(−1), stopped.
`count` and the items are kept.

### Path exports

`GEPathGetNumItems()` = count. `GEPathGetItem(i, &x, &y)` = items[i] in cells, (0, 0) for
i ≥ count. `GEPathGetMapData(x, y)` = the loaded cell value, 0 outside the grid (not
imported). The EXE uses the items to check that Gilbert is on his path before an area hit
(E-0411).

## Quirks kept from the original

- Anim time is shared by every object showing the same anim (E-0401, E-0402).
- `t == duration` wraps silently (E-0401).
- The walkmap list is not rebuilt by events (Q-0401).
- Event 22 renumbers before showing (all 127 records join into topics shown from the start,
  so this does not show in play) (E-0405).
- A saved game resumes facing north, on the walkmap (E-0412).
