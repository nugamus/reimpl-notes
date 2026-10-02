# Saved games (Ring, DVD)

Evidence: E-0250..E-0259 (format, entry 1000, files), E-0093 (`LoadSaveTimer`), the screens
in `games/ring/docs/sy.md` (E-0260..E-0264). Addresses are `RING_DVD.EXE`. All integers
are little-endian; `u8`/`u32`/`i32`/`f32` as stored by the original (raw copies of the
object's fields, no padding). `str` is an `aString` record (0x428be0): `u32 length`
(strlen + 1) and `length` bytes including the NUL.

## Files

Everything lives in `<install>DATA\SAVE\` (the install prefix 0x402480 ends in `\`; the SY
code builds the same folder as `%s\data\Save\`):

| File | Written by | Holds |
|---|---|---|
| `SaveGame.ars` | `StartMenu(1)` (F12 in play), "Format" below | the game as it was when the menu opened |
| `alb.ars`, `sie.ars`, `log.ars`, `bru.ars` | `LoadSaveTimer(name, 2)` at the hub (`spec/bag.md`, Erda) | one world's timers, bag and sounds ("World files") |
| `ArSa<n>.ars`, `ArSa<n>.bmp`, `ArSa<n>_ALB.ars`, `_SIE`, `_LOG`, `_BRU` | the save screen's OK | copies: `SaveGame.ars`, the thumbnail, the four world files that exist |
| `Save.aba` | the save screen's OK, the load screen's delete | the list of saved games ("The list") |
| `DATA\SY\Image\osc.bmp` (not in `SAVE`) | opening the save screen | the thumbnail being offered |

The discs ship `SAVE.ABA` and `ZERO.ABA` (4 zero bytes: an empty list) and `DUMMYLS.BMP`
(a 4×4 black 24-bit BMP) in `DATA\SAVE` (E-0256). `ZERO.ABA` is not named by the EXE.

`<n>` is the smallest integer from 1 for which `<install>\data\Save\ArSa<n>.ars` does not
exist (`FindTempFileName` 0x40e620 tries 1 .. 100001, `_access`; past that the save fails).

## Game save (`aApplication::LoadSave` 0x40d6a0)

`LoadSave(name, mode)`: mode 1 loads, any other value (the callers pass 2) saves. The file
is `<install>DATA\SAVE\<name>.ars` (`%s%s\%s\%s.ars` with `DATA`, `SAVE`); saving creates
or truncates it (`CREATE_ALWAYS`), loading opens it for reading. The tick count
(`GetTickCount`) is taken once at the start: every time below is stored relative to it.

### Header (20 bytes)

| Offset | Type | Value |
|---:|---|---|
| 0 | char[12] | `"ArxSav 1.00"` and its NUL |
| 12 | i32 | `st_size` of `<install>ring.exe` (`_stat` 0x47bf41) |
| 16 | i32 | `st_mtime` of the same file |

Loading reads the 20 bytes and refuses the file ("CODE is not the same") unless the first
string equals `"ArxSav 1.00"`; when `CHECKLOADSAVE` (fl.ini, app+0x53) is set it also
refuses a different size ("SIZE is not the same") or time ("MTIME is not the same"). Every
edition's `fl.ini` sets `CHECKLOADSAVE: 1` (E-0250): a save only loads in the installation
whose `ring.exe` wrote it.

### Body

No counts: each list is walked in its current order and every element writes its record,
so a file only reads back into an application that declared the same puzzles, rotations,
objects and their sub-elements in the same order (the zone set-ups, which the callers rerun
before loading: 0x408bc0, 0x431040).

1. every **puzzle** of the application's list (app+0x7d), "Puzzle";
2. every **rotation** (app+0x85), "Rotation";
3. every **object** (app+0x79), "Object";
4. the **variables** (app+0x95), "Variables";
5. the **bag** (app+0x8d), "Bag";
6. the **timers** (app+0x91), "Timers";
7. the **trailer**, 0x1a bytes;
8. the **sounds**, "Sounds".

Saving writes all eight and closes the file. Loading reads 1..7 and then, from the
trailer, sets the application's mode (app+0x66, 0x40b7b0) and the timers-paused byte
(app+0x6a), and calls `GoZone(zone, 1000)` (0x402280); the file stays open and entry 1000
reads the sounds ("Entry 1000"). A failed read or write of any part is logged and the
function returns 0 (on load with whatever was read so far applied).

### Trailer (0x1a bytes, global 0x495348)

| Offset | Type | Saved from | On load |
|---:|---|---|---|
| 0 | u32 | app+0x66, the application's mode | 0x40b7b0 |
| 4 | u8 | app+0x6a, timers paused | app+0x6a |
| 5 | u8 | app+0x6e, the current zone | `GoZone(zone, 1000)` |
| 6 | u8 | 1 if a puzzle is current (0x402700), else 0 | entry 1000 |
| 7 | u32 | the current puzzle's id (0x402720), else 0 | entry 1000 |
| 0xb | u8 | 1 if a rotation is current (0x402710), else 0 | entry 1000 |
| 0xc | u32 | the current rotation's id (0x402730), else 0 | entry 1000 |
| 0x10 | u8 | 0x495570: the rotation's frozen byte (+0x67) before the bag opened (`spec/bag.md`) | the rotation's +0x67 |
| 0x11 | u8 | app+0x5d, the declaration kind (`spec/resources.md`) | app+0x5d |
| 0x12 | u32 | app+0x54 (1 from `Init`; Q-0091) | app+0x54 |
| 0x16 | i32 | app+0x58 sign-extended, the load-from mode | app+0x58 (low byte) |

### Puzzle (`aPuzzle::LoadSave` 0x41bb70; E-0252)

1. the background image handle (+4) if any: "Image handle";
2. each movability (+8): "Movability";
3. each sound item (+0x1c): "Sound item";
4. each visual object (+0x20): its virtual +0x20, which for both kinds (0x46efe0) reads
   and writes nothing;
5. 9 bytes: u32 mode (+0x24, `PuzSetMod`), u8 +0x28 (animations held), u32 the dialogue
   object (+0x29).

Accessibilities, presentation images, animations and texts are saved through their objects.

### Rotation (`aRotation::LoadSave` 0x41df30)

1. the image handle (+0x29): "Image handle";
2. each movability (+0x10);
3. each animation layer (+0x1c): its `aAnimation` record ("Animation"), then u32 whether
   the layer is shown (written from 0x4103f0, read through 0x4103d0);
4. each sound item (+0x24);
5. 0x44 bytes: u8 +0x28; 13 × u32 +0x31 .. +0x61 (the effects: strength +0x31, juggle
   amplitude +0x39, speed +0x41, the others Q-0091; `spec/rotation.md`); u8 wave (+0x65),
   u8 juggle (+0x66), u8 frozen (+0x67); f32 alpha (+0x68), beta (+0x6c), ran (+0x70).

### Image handle (`aImageHandle::LoadSave` 0x42d480, 13 bytes after the strings)

`str` directory (+0x4d) if set, `str` name (+0x51) if set, then x (i32, +0x55), y (i32,
+0x59), active (u8, +0x65; loading calls `SetActive`), zone (u8, +0x79), kind (u8, +0x7a),
extension index (u8, +0x70), load-from (u8, +0x7b).

### Movability, hot spot, accessibility, sound item

- **Movability** (`aMovability::LoadSave` 0x423470): its hot spot ("Hot spot"), `str` ride name (+0x10) if
  set, then 0x25 bytes: target id (+0xc), kind (+0x14), the transition from +0x18: f32
  alpha1, f32 beta1, f32 ran1, i32 +0x24, u8 turn kind (+0x28), f32 alpha2, f32 beta2,
  f32 ran2 (`spec/api.md`, "Model").
- **Hot spot** (`aHotSpot::LoadSave` 0x4237c0, 0x21 bytes, the object's bytes in order): i32 x1, y1, x2, y2; u8 enabled;
  i32 kind; i32 cursor; i32 `unk_19`; i32 key.
- **Accessibility** (0x423120): its hot spot only.
- **Sound item** (0x41a080, 9 bytes): i32 volume (+8), i32 pan (+0xc), u8 active (+0x18).

### Object (`aObject::LoadSave` 0x41fcd0)

1. 0x74 bytes: the four cursor definitions as stored (passive +0x15, active +0x32,
   passive-drag +0x4f, active-drag +0x6c; each 7 × u32 and a load-from byte; `spec/api.md`);
2. each accessibility (+0xd): "Accessibility";
3. each presentation (+0x11): "Presentation";
4. the bag animation (+0x89, `ObjAddBagAni`) if any: "Animation image".

**Presentation** (`aObjectPresentation::LoadSave` 0x42e020): each image handle (+5), each animation
image (+0xd), each text of the two text lists (+0x29, +0x31: "Text"), then u8 shown (+4).

**Text** (`aText::LoadSave` 0x42c340): `str` the string (+0) if set, then 0x1d bytes: 6 × u32 +4 ..
+0x18 (width +0x14 and height +0x18 among them, `spec/text.md`; the others Q-0091), u8
+0x1c, u32 +0x1d.

### Animation (`aAnimation::LoadSave` 0x416070, 0xa1 bytes)

| Offset | Size | Field (`spec/animation.md`) |
|---:|---:|---|
| 0 | 64 | the name, copied with `strcpy` into an uninitialised stack buffer: after the NUL the bytes are whatever the stack held (E-0255); loading calls `SetName` with it |
| 0x40 | 4 × 6 | frames (+8), fps (+0xc), start (+0x10), mode (+0x14), mode at `Init` (+0x18), +0x1c |
| 0x58 | 1, 1 | restart (+0x20), timing (+0x21) |
| 0x5a | 4 | current frame (+0x22) |
| 0x5e | 1, 1 | active (+0x26), paused (+0x27) |
| 0x60 | 4 | **time** +0x28 |
| 0x64 | 1, 1 | +0x2c, stop at the wrap (+0x2d) |
| 0x66 | 4 | +0x2e |
| 0x6a | 4 | **time** +0x32 |
| 0x6e | 4 × 5 | +0x36, +0x3a, +0x3e, target frame (+0x42), hold ms (+0x46) |
| 0x82 | 4 | **time** +0x4a (0 disarmed, 1 armed, else the hold's start) |
| 0x86 | 1 | just started (+0x4e) |
| 0x87 | 4 | **time** +0x4f |
| 0x8b | 4 | frame time (+0x53) |
| 0x8f | 1 | +0x57 |
| 0x90 | 4, 4 | counter (+0x58), +0x5c |
| 0x98 | 1 | stepped (+0x60) |
| 0x99 | 4, 4 | last reported frame (+0x61), +0x65 |

Times: +0x28, +0x32 and +0x4a are written as `tick − value` when the value, read as an
unsigned number, is above 1.0, else as is; +0x4f as `tick − value` unless 0. Loading
applies the same rule (`tick − stored`) with the load's tick count.

**Animation image** (`aAnimationImage::LoadSave` 0x421930): the animation record, then u32 +0x71,
u32 +0x75, u8 +0x89 (Q-0091).

### Variables (`aVar::LoadSave` 0x424290, E-0253)

Five lists in this order, each `u32 count` then its entries: bytes (`u32 id, u8 value`),
words (`u32 id, u16`), dwords (`u32 id, u32`), floats (`u32 id, f32`), strings (`u32 id,
u32 length, length bytes` with the NUL). Loading first deletes every variable (0x424860)
and redefines them from the file (`VarDefByte`, … ; a string through a temporary buffer).

### Bag (`aList::LoadSave` 0x4172a0)

`u32 count`, then the object ids from the **last** item to the first, then u32 +0x95 (the
bag's field after its lists). Loading `add`s the ids in file order (`spec/bag.md`, `add`).

### Timers (`aTimer::LoadSave` 0x425910)

`u32 count`, then per timer 16 bytes: u32 id (+0), u32 elapsed = tick − its start (+4),
u32 times fired (+8, one more per `WM_TIMER`: `spec/api.md`), u32 period in ms (+0xc). Loading
starts each timer again (`StartTimer(id, period)`, the last argument 1 in both callers),
then sets its start to tick − elapsed (0x423c70) and the times fired (0x425750).

### Sounds (0x469790)

1. f32 master volume (0x4932a8, 1.0; `spec/sound.md`);
2. for every sound of the sound list (0x4a1cfc, its count 0x4a1cf4), in list order, 12
   bytes: own volume (+0x111), type volume (+0x115), pan (+0x119);
3. `u32 count` and the ids of the sounds whose virtual +0x24 is true (the streamed sound's
   is `return 0`, so 0; loading calls each one's virtual +0x1c, a no-op; Q-0092);
4. `u32 count` and, per **playing** sound (virtual +0xc: the DirectSound buffer's status
   has `DSBSTATUS_PLAYING`), `u32 id, u32 loop` (+0x11d). Loading keeps this list
   (0x4a1f08); 0x4696f0 then plays each one with `NoiceIdPlay(id, loop)` and drops it.

(The function's last argument, always 0 here, would write the kept list instead of the
playing sounds.)

## Entry 1000 (`GameSetZone` 0x40d220)

`GoZone(zone, 1000)` (0x402280) from a load checks the zone's CD (`GameZoneOnCD`; not for
the hub, below; a missing CD shows the insert-CD screen and keeps the entry in 0x495238),
leaves the current puzzle or rotation (0x40b650), stops all sounds with reason 8, and calls
0x40d220, which for entry 1000 runs **no** zone set-up or handler; instead:

1. the zone's archive is opened as for any entry, except in AS (zone 7) when the saved
   puzzle is one of 80002..80010 or the saved rotation is 80101 (the hub's rooms; also no
   CD check, 0x402280);
2. the saved puzzle, if any, is made current (`PuzSetAct(id, 0, 1)`);
3. the saved rotation, if any, is made current (`RotSetAct(id, 0, 1)`) and its frozen byte
   (+0x67) set from trailer byte 0x10;
4. app+0x5d, app+0x54, app+0x58 from the trailer;
5. the sounds are read (mode 1) and the file closed;
6. the preferences are reloaded from `aPre.ini` (`aPreFer::Load`);
7. the kept sounds are played (0x4696f0).

## World files (`LoadSaveTimer` 0x40d4b0, E-0093)

`<install>DATA\SAVE\<name>.ars` without a header: the timers, the bag and the sounds, in
the layouts above (sounds with the function's last argument 0). Written at the hub when
the player leaves a world (`alb` for NI and RH, `sie` FO, `log` RO and N2, `bru` WA;
`spec/bag.md`) and read when entering it again.

## The list (`Save.aba`, `aFileList`)

`<install>\data\Save\Save.aba`: `u32 count`, then per saved game three `str`: the file name
(`ArSa<n>`), the description line (`"<character>  <time>   <date>"`, `games/ring/docs/sy.md`,
"Save"), the name the player typed. `Init` (0x47a0e0, through `Load` 0x47a1d0) reads the
whole file (a missing file fails); `Add` (0x47a5e0) appends; 0x47a790 removes one entry;
`Save` (0x47a470) rewrites the file (`CREATE_ALWAYS`).

## Thumbnails

`StartMenu(1)` copies the screen into a 640×480 24-bit picture (`CopyBufferToImage`,
0x49556c). Opening the save screen scales it with `aImage::Zoom(0.40645, 1.0)` (0x413a90:
width × 0.40645, height × 1.0, so 260 × 480; rows 0 .. 478 copied by nearest neighbour,
the last row left as created) and writes it as `<install>\data\SY\Image\osc.bmp`
(`aImage::Save` 0x4135a0), which the save screen shows and the save's OK copies to
`ArSa<n>.bmp`. The load screen shows `ArSa<n>.bmp` of the selected game.

## Recommendation for ScummVM

Do not write the original files byte for byte; keep ScummVM saves (its slot list, header,
thumbnail and description), and write in their body the same records in the same order as
above, so this page stays the checklist of what a save holds. Reasons, all from the code:

- the header holds the size and modification time of the user's `ring.exe` and every
  edition checks them (`CHECKLOADSAVE: 1`): the original could only load our file if the
  engine knew the original installation's `ring.exe`;
- each animation record carries 64-byte names whose bytes after the NUL are uninitialised
  stack (E-0255): no two runs of the original write the same file, so "byte for byte" has
  no reference to match;
- one saved game is up to six files, an entry in `Save.aba` and a picture written into the
  game's own `DATA\SY\Image` folder, named by the first free number: none of it fits
  ScummVM's save manager, which owns one file per slot;
- the records are raw dumps of the original's objects, including fields we do not use or
  know (Q-0091) and times relative to the tick count; ScummVM's own records can drop or
  name them.

Loading the original's `.ars` files stays possible later as an import (read the header,
skip the size and time check as `CHECKLOADSAVE: 0` does, ignore the name bytes after the
NUL), if the user wants it.
