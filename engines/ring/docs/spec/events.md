# Events: how input and engine activity reach the zone code (Ring, DVD)

The engine calls the zone code through 17 dispatchers. Each reads the current zone
(0x402450, app+0x6e) and calls that zone's handler; zones that do not handle an event
point at an empty default (0x443700, 0x444b30, 0x44a100, 0x44a110). Some dispatchers
first check `(puzzle == 1 && flag)` and then call the SY handler whatever the zone:
puzzle 1 is SY's (the quit dialog, `WM_CLOSE` in `spec/boot.md`). Evidence: E-0033.

| Dispatcher | Called from | SY override | SY | NI | RH | FO | RO | WA | AS | N2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0x40bbb0 object click | `MouseLeftEvent` 0x409d90 | 0x431660 | 0x431660 | 0x445c80 | 0x443990 | 0x43dac0 | 0x43afa0 | 0x437d60 | 0x4364a0 | 0x4341e0 |
| 0x40bd40 button down on an object | 0x409630 (`WM_LBUTTONDOWN`) | — | — | 0x4472b0 | — | 0x441860 | 0x43b9a0 | — | — | 0x434740 |
| 0x40bed0 click on an object with flag bit 3 | `MouseLeftEvent` | — | — | — | — | 0x441860 | — | 0x4392a0 | — | — |
| 0x40c060 drag released | 0x409520, 0x409630, `MouseLeftEvent` | 0x4331b0 | 0x4331b0 | 0x4477d0 | — | 0x441890 | 0x43bbf0 | — | — | 0x4349b0 |
| 0x40c1f0 inventory list click | `MouseLeftEvent` (list shown) | — | — | — | — | 0x441d50 | — | — | — | — |
| 0x40c2b0 before a movability | `MouseLeftEvent` | — | 0x433530 | 0x449080 | 0x444b40 | 0x4420b0 | 0x43c290 | 0x439f40 | 0x436c10 | 0x435390 |
| 0x40c420 after a movability | `MouseLeftEvent` | — | 0x433570 | 0x449320 | 0x444ba0 | 0x442580 | 0x43c450 | 0x43a050 | 0x436d60 | 0x435410 |
| 0x40c590 timer | 0x40b4a0 (`WM_TIMER`, app+0x6a clear) | — | — | 0x4497b0 | 0x444d30 | 0x442810 | 0x43c500 | — | 0x436df0 | 0x435470 |
| 0x40c650 | 0x416c10 (animation) | — | all 0x44a100 (none) | | | | | | | |
| 0x40c7a0 | 0x416720, 0x416c50 (animation) | — | all 0x44a110 (none) | | | | | | | |
| 0x40c910 | 0x416720, 0x416c90 (animation) | — | — | — | — | — | — | 0x43a6f0 | — | — |
| 0x40ca80 on an accessibility (every frame, `spec/cursor.md`) | 0x408dd0 (hot spot tracking) | 0x4335a0 | 0x4335a0 | 0x44a120 | — | — | — | — | — | 0x435970 |
| 0x40cc10 on a movability (every frame) | 0x408dd0 | — | 0x433b80 | 0x44a1b0 | 0x44a1b0 | 0x433b80 | 0x433b80 | 0x433b80 | 0x433b80 | 0x44a1b0 |
| 0x40cde0 on nothing (every frame) | 0x408dd0 | — | 0x433bc0 | 0x442e30 | 0x442e30 | 0x442e30 | 0x442e30 | 0x442e30 | 0x442e30 | 0x442e30 |
| 0x40ced0 sound or dialog finished | sound 0x469010, 0x469150, 0x4693b0, dialog 0x427c70, `NoiceIdPlay`, 0x40f690 | — | 0x433cf0 | 0x44a1c0 | 0x444e60 | 0x442e40 | 0x43d4a0 | 0x43a860 | 0x437190 | 0x435a00 |
| 0x40cff0 animation event | 0x416870 (animation) | — | — | 0x4499e0 | 0x444dc0 | 0x442b60 | 0x43c5e0 | 0x43a400 | 0x437110 | 0x4354b0 |
| 0x40d130 key | 0x40b060 (`WM_CHAR`/Delete) | — | 0x433d30 | — | — | — | — | — | — | — |
| 0x40d1f0 | 0x46bc50 | (no zone switch found yet) | | | | | | | | |

"—" = the empty default. The names in the first column come from the caller; what each
passes (object id, accessibility index, puzzle/rotation id, movability index, cursor,
kind, animation id, sound id, timer id) is read per handler in the zone specs
(`games/ring/docs/`).

## Keys and accessibilities

A key (0x40b060) first goes to the zone's key handler (SY only). Otherwise it is matched
against the `key` of each enabled accessibility of the current puzzle (or of the active
rotation, whose hot spot is then projected to the screen, 0x4107f0) and, on a match,
behaves as a left click on that hot spot (0x40af80, or 0x40afb0 with Ctrl). Escape is
first drained from the keyboard state and 0x406e40(5, 0x1002) is called.

## Right button

Right button up (0x40afe0), when no drag is active and the menu is not up (app+0x6f): if
puzzle 1 (SY's dialog puzzle, looked up by id with 0x40b760) is missing or its mode (+0x24)
is not 2, it toggles the inventory: hides it (0x419350,
0x40ded0) when shown, else shows it (0x406570, 0x4192e0, 0x40de90).
