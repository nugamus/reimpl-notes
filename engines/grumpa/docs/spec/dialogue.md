# Dialogue: voice lines (engine behaviour)

Grumpa has no dialogue screens, choices or subtitles. Characters talk through voice lines:
`CFXSound` actors (types 0x18 and 0x2a) in the scene files, started by commands and chained by
the commands they run when they end. Evidence: E-0405, E-1620. Open: Q-0400.

## The sound actor

After the common header (`id, active, visible, n × u32`, E-0400) a sound record holds:

| field | meaning |
|---|---|
| volume flag, volume | if the flag is 1, the volume in hundredths of a dB (0 = full, −10000 = silent) |
| pan flag, pan | if the flag is 1, the pan in hundredths of a dB (−10000 left .. 10000 right) |
| frequency flag, frequency | if the flag is 1, the playback rate in Hz |
| loop | 1 = loop until stopped |
| playing | 1 = playing when saved |
| on entry | 1 = start when the scene is entered |
| speaker | the id of the character who says the line; 0 = not speech |
| name | the `.wav` file |
| commands | a CC list run when the sound ends (`events.md`) |

## Files

The original opens `<data>\Sounds\<name>`. The disc's cabinet splits that folder into
`Sounds_` (language-independent effects and music) and `Sounds_<language>` (the voices); a name
in both is the language's voice (Q-0400). The engine looks in `Sounds_<language>` first, then
`Sounds_`. Names with non-ASCII letters (`Släpp_Lås_mig_SV.wav`) were extracted with `_` in
their place (`Sl_pp_L_s_mig_SV.wav`); the engine tries that spelling too.

## Commands

| opcode | effect |
|---:|---|
| 0, 500 | play (`active = 1`) |
| 1, 501 | stop and run the command list (501 also `active = 0`) |
| 0xb / 0xc | `active = 1 / 0` |
| 0xd | stop without running the command list, `active = visible = 0`, latched (one-shot) |
| 0x17 | scene entry: play if `playing` or `on entry` is set (E-0406) |

Playing marks the speaker as talking until the sound stops (E-1620). "Talking" is the
speaker character's **state slot 5**: play sets it to 1 (speaker id > 0), stop sets it to 0.
Nothing in the animation, mesh, render or input code reads it: no talk clip, no mouth or head
motion, no block on walking or on other sounds. Only event conditions read it; in the data
these are 31 conditions `c16[4] == 2 & c16[5] == 0` on the companion's hint lines and walk-in
triggers, so a new companion hint starts only while he is silent. Before setting the flag,
play flushes the speaker's speech queue if the speaker is not in the current scene (stop the
line at its front, empty the queue). The speech queue (character op 0x48, slots ≥ 60 or 32;
E-1223) uses the same slot: the first queued line plays at once only if slot 5 is 0 and then
sets it; on each animation step of the active, present character, a front line whose sound has
stopped is popped, slot 5 = 0, and the next queued line (if any) plays with slot 5 = 1.
Character op 0x60 stops all 100 of the character's sound slots without running command
lists; their speaker is 0, so slot 5 is left to the queue (`characters.md`, E-1640).

A sound that is not
looping stops by itself at its end; **stopping runs the sound's command list**, which is how a
conversation goes on: the end of one line starts the next (or opens a door, moves a character).

## Messages

A character's message list (`characters.md`) would be shown as a fading caption by opcode
0x44 (through the scene manager, 185). Every list is empty in this edition: there is no
on-screen text besides the menus, help and credits (`Local_<language>`).

## Languages (E-0002, E-1770)

One disc holds Danish, Finnish, Norwegian and Swedish (the installer's default). A language
has its own `Local_<language>/` texts (`Text.txt`, `Help.txt`, `Credits.txt`, `license.txt`;
the menu folder `UI/001_Menu/` carries the Swedish copies), `Sounds_<language>/` voices and
`Movies_<language>/grumpa_intro.mpg` (the Swedish intro and the other films are in the CD's
`Movies/`). Sounds are looked up in the language's folder, then the common `Sounds_/`; a
name a language lacks (four Swedish names: the pirate boss's yell, two Kraken lines, the
fat man's breathing) comes from `Sounds_/`. The engine takes the language from ScummVM's
detection: the CD has four entries, the same files, one per language; an installed folder
(whose languages are not known) has one, and the game options' language picks.
