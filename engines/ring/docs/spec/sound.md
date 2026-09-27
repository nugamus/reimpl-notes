# Sound: sounds, dialogues, ambient sounds (Ring, DVD)

Evidence: E-0050 (sounds), E-0051 (dialogues), E-0052 (ambient and 3D sounds). Addresses
are `RING_DVD.EXE`. File formats: `docs/formats/README.md` (`.wav`, `.wac`, `.was`, `.dia`,
`.dan`).

## The sound list

`SouAdd(id, type, file, load_from, kind, unk_6)` (0x406ba0; the 4-argument entry 0x406970
passes the same with defaults) checks the name (at least 4 characters; the extension,
compared case-insensitively, gives the format: `wav` 0, `wac` 1, `was` 2, anything else is
refused), checks that the file exists and appends a sound to the global list (0x4683c0; an
id already in the list is refused). Every call in the game passes kind 2, which makes a
streamed sound (vtable 0x47e86c); `unk_6` is stored (+0x16a) and handed to the stream
unread by anything specified here.

Types (Templier's names; the checks below confirm 2, 3 and 5):

| Type | Name | Special handling |
|---:|---|---|
| 1 | background music | — |
| 2 | ambient music | the only type `PuzAddAmbSou` / `RotAddAmbSou` accept |
| 3 | ambient effect | the only type `PuzAdd3DSou` / `RotAdd3DSou` accept |
| 4 | effect | stopped when the player leaves a puzzle or rotation (0x40b650) |
| 5 | dialogue | played with subtitles and lip sync ("Dialogues" below); stopped when the player leaves a puzzle or rotation; its volume is the dialogue volume |

File: `<prefix>DATA\<zone folder>\SOUND\<file>` (format `%s%s\%s\%s\%s`: prefix, `DATA`,
the current zone's folder, `SOUND`, the name), type 5 `<prefix>DATA\<zone>\SOUND\<language>\<file>`
(`%s%s\%s\%s\%s\%s`, the language's folder name from 0x4076e0). The prefix is the CD path
(0x402470) when `load_from` is 1, else the install path (0x402480). The zone is the one
current when the sound is added and again when it is played (the path is rebuilt at each
play, 0x468ae0).

Each sound keeps: id (+4), type (+8), file name (+0xc), a "started" flag (+0x10c), the
load-from byte (+0x110), its own volume (+0x111, 100), the type volume (+0x115, 100), a
pan (+0x119, 0), the format (+0x121).

## Volume and pan

Whenever one of the three changes (0x468100), DirectSound gets

- volume = −10000 − trunc(own/100 × type/100 × master × −10000) hundredths of a decibel,
  master being the float at 0x4932a8 (1.0); so the attenuation in dB is
  100 × (1 − own × type / 10000): full at 100 × 100, −50 dB at half;
- pan = −10000 − trunc((pan + 100) × −100) = 100 × pan (−100 left … 100 right, in
  hundredths of a decibel of attenuation of the other side).

Own volume (0x468060, `SouSet_406e20` → 0x4690f0) and type volume (0x468090) are clamped
to 0..100, the pan (0x4680c0, 0x406ec0 → 0x469120) to −100..100. The preferences set the
type volume of every sound: the dialogue volume for type 5, the volume for the others
(`games/ring/docs/sy.md`, "Preferences"). Without a sound device (0x4a1d04 null) nothing
plays; dialogues still show their subtitles.

## Playing, stopping, events

The zone code calls these wrappers:

| Call | Address | Does |
|---|---|---|
| play(id, n) | 0x406de0 → `NoiceIdPlay` 0x468e20(id, n != 1) | below; n = 1 plays once, any other value loops |
| stop(id, reason) | 0x406e00 → 0x469010 | stops it; raises the sound event with `reason` if it was playing |
| stop type(type, reason) | 0x406e40 → 0x469150 | stops every playing sound of the type (for type 5 only the first dialogue removed) |
| stop all(reason) | 0x406ea0 → 0x4693b0 | stops every playing sound (and the first dialogue) |
| volume(id, v) | 0x406e20 → 0x4690f0 | own volume |
| pan(id, p) | 0x406ec0 → 0x469120 | pan |
| playing(id) | 0x406ef0 → 0x469540 | the sound is playing (type 5: its dialogue is in the list) |
| type playing(type) | 0x406f00 → 0x4695b0 | a sound of the type is playing (type 5: any dialogue) |

**Play** (`NoiceIdPlay`): waits while Escape is held; for type 5 first stops all type-5
sounds with reason 0x20; for another type, when this sound is playing, stops it and raises
the event with 0x20. A type-5 sound then gets its dialogue ("Dialogues"); when the dialogue
cannot be read the event is raised with 0x20 and nothing plays. The sound starts (0x468ae0:
stream opened, looping when the flag is set, volume and pan applied), its "started" flag is
set, and a dialogue's clock restarts.

A stream that reaches its end without the loop flag plays silence until the buffer
drains, then stops; with the flag it rewinds and goes on.

**The sound event** (0x40ced0, `spec/events.md`): (id, type, reason) goes to the current
zone's handler as (id, type, reason without bit 0x1000, reason & 0x1000). Reasons: 0x1001
a natural end, 0x20 restarted, 0x400 / 0x10 / 0x1002 stopped by the code (the value the
caller passes). Handlers test the fourth argument to act only on natural ends.

**Natural ends** are found once per frame, after the frame is drawn (0x40f6c0 → 0x468da0):
every sound whose "started" flag is set and that no longer plays gets the flag cleared, is
stopped, and, unless it is of type 5, raises (id, type, 0x1001) (0x40f690). Dialogues end
through their text ("Dialogues").

**Leaving** a puzzle or rotation (0x40b650, at the start of `PuzSetAct` and `RotSetAct`):
all sounds of types 4 and 5 are stopped with reason 0x10.

## Dialogues (`aDialog`, handler app+0xc)

A type-5 sound's dialogue (0x426d00, `aDialog::Init` 0x426ef0) reads, with the sound's
file name less its last three characters (`1072.` of `1072.wac`):

- `<install>DATA\<zone>\DIA\<language>\<name>dia`: required (`ReadLyrics` 0x427090; format
  README "Dialog text"). Each line is a time in milliseconds and a text; `#` splits the
  text into a first and a second line; for Greek (language 9) the bytes 0xA0 become
  spaces. The file's last line (conventionally `END`) marks the end and is never shown.
- `<install>DATA\<zone>\DIA\<language>\<name>dan`: optional lip sync (`ReadDialogAnimation`
  0x4271b0): a count N, N triples `level object presentation`, then triples `start end
  level` (milliseconds) until the scan fails.

`AddDialog` (0x427f20) appends it to the handler's list and sets its clock (tick count);
`RemoveDialog` (0x428050) hides its lip-sync presentations (0x4279b0) and drops it; the
sound is not stopped there.

**Every frame** (0x427c70, after tracking), the first dialogue of the list only:

1. t = now − clock. The shown line is the first i (0 ≤ i < count − 1) with time[i] ≤ t ≤
   time[i + 1] (0x427880); when there is none (t past the last time, or a file of one
   line) the dialogue is removed and the event (id, 5, 0x1001) raised.
2. Texts: the first part always, the second only when not empty, each an `aText` in the
   handler's font and colours (0x427b30 / 0x427c20 set font 1, colour (200, 200, 30),
   background (0, 0, 0): opaque; `SubTitSetCol` 0x406f10 and `SubTitSetBgrCol` 0x406f50
   change them). One part: at x = 320 − width / 2, y = 461 − height. Two parts: the first
   at y = 461 − height1 − 3 − height2, the second at y = 461 − height2, each centred.
   They are drawn (0x414df0, `spec/text.md`) only when subtitles are on (handler +0x28,
   the preferences).
3. Lip sync (0x427a10, when a `.dan` was read): level = that of the first entry with start
   ≤ t ≤ end, else 0. When it differs from the last level: every mapped presentation is
   hidden (`ObjPreHid(object, presentation)`), then, for a level other than 0, the first
   mapping with that level is shown (`ObjPreSho`).

## Ambient and 3D sounds (`aSoundItem`, handler app+0x62)

`PuzAddAmbSou` / `RotAddAmbSou(owner, sound, volume, pan, same_mode, leave_mode, fade)`
(0x404b00 / 0x405d50; sound of type 2) and `PuzAdd3DSou` / `RotAdd3DSou(owner, sound,
same_mode, leave_mode, fade, volume, f32 angle, amplitude)` (0x404c30 / 0x405e80; type 3)
add a sound item to the puzzle's (+0x1c) or rotation's (+0x24) list (`aSoundItem::Init`
0x41a150): the sound, volume (+8), pan (+0xc), active (+0x18, 1), same mode (+0x10), leave
mode (+0x14), fade − 1 (+0x19; `fade` must be at least 2), amplitude (+0x1d, kept when
0..100) and angle offset (+0x21 = LR × angle × π/180, kept when −360 ≤ angle ≤ 360; LR is
the stereo preference, −1 or 1). A 3D item's pan is computed at once from the rotation's
current angle.

**3D pan** (0x41a4a0): pan = trunc(sin(alpha × π/180 + offset) × amplitude) × s, with
alpha the rotation's view angle (its stored alpha + 135, less 360 when above 360) and s
= 1 when LR is 1.0, else −1. It is recomputed for every type-3 item of a rotation when
the rotation is entered (0x41ee10: `RotSetAct` through 0x41ecc0, and at a movability
click with the arrival alpha), not while the player looks around.

`PuzSetAmbSouOff` / `RotSetAmbSouOff`, `…3DSouOff` (item inactive, 0x41a280) and
`PuzSet3DSouOn` / `RotSet3DSouOn` (active, 0x41a220) also stop / start the item at once
when its owner is the current puzzle or rotation (the rotation wins when both are set).
`aPuzzle::SetAmbientSoundVolume` sets an item's volume.

**Starting an item** (0x41a350): the sound is stopped if playing, gets the item's volume
and pan, and plays looping; its "started" flag is set. **Stopping** (0x41a3b0): stopped
if playing, without an event (the stream's stop, 0x468c90, also clears the "started"
flag).

### Changing place

`PuzSetAct(puzzle, start, stop)` / `RotSetAct(rotation, start, stop)` (0x402490 /
0x4025b0), when no transition is pending (handler byte +0): the new place's list becomes
the handler's "new" list (+5) beside the "old" one (+1, the place left); when both exist
a transition is computed (0x41aa00, below) and finished at once (0x41b130, 0x41aee0(2),
0x41b180(3), 0x41b350(3), 0x41b520); when it cannot be (no old list: the first place),
the old items are stopped if `stop` and the new place's items started if `start`: every
active item that is not playing starts, every inactive one is stopped (0x41ecc0 /
0x41d530; for a rotation after its 3D pans are computed). When a transition is pending
(set up by a movability click, below) only its start step runs (0x41b520). Then the lists
are cleared (0x41a820) and the new place's list becomes the old one (0x41a990).

**The transition** (0x41aa00) sorts every item into four lists: stop now (+9), fade out
(+0xd), fade to new values (+0x11), start (+0x15):

- an old item whose sound is not in the new list, or is there but inactive while the old
  one is active: leave mode 1 → fade out from its volume to 40 (pan unchanged); leave
  mode 2 → stop now;
- an old item whose sound is in the new list and active there: its same mode 1 → fade
  from the old to the new volume and pan (the old item keeps playing); 2 → the old fades
  out to 40 and the new one starts; 3 → the old stops now and the new one starts;
- both inactive: nothing;
- a new item whose sound is not in the old list, or is there but inactive while the new
  one is active: start.

Then: stop-now items are stopped (0x41b130); fades get `steps` = n − 1 when n is below
the item's fade − 1, else fade − 1, with n the step count asked (0x41aee0: 2 when finished
at once, the ride video's frame count otherwise), and per-step increments (target −
start) / steps for volume and pan; a transition with a step count ≤ 0 is abandoned (the
old items stopped, the pending flag cleared). Each step k (0x41b180 fade-outs, 0x41b350
fades): an item with steps ≤ k is finished (a fade-out stopped and dropped; a fade set to
its target values); otherwise its volume and pan advance one increment and are applied.
The start step (0x41b520) starts every active start item that is not playing.

**On a movability click** (`MouseLeftEvent`, `spec/rotation.md`): the target's list
becomes the new list (for a rotation after its 3D pans are computed for the arrival
angle), the pending flag is set and the transition computed (none possible: pending
cleared, old items stopped). The ride video (`aCinMov::Init` / `Play`) then steps it:
0x41aee0(frame count) at the start, 0x41b180(k) and 0x41b350(k) after each frame k (from
0); Escape finishes it (step = frame count). Without a ride video (or when the video
fails) it is finished at once as above. The target's `PuzSetAct` / `RotSetAct` then runs
the start step.
