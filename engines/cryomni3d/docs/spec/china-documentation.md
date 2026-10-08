# China: the documentation base

Two screens: the contents (0x4085d0) and the fiche viewer (0x40c5a0). Data: Fichetxt.txt
(themes, fiches, tables; E-0204) and LISTE.TXT (index rows; E-0203, corrected by E-1301).
Screen 640x480, 16-bit. Coordinates are (x, y). Sprites (`.spr`) carry their own screen
position (E-1101); "at its own position" below means that. Colour 0x7020 is RGB565.
Every frame: pump messages, music, poll the mouse; Escape (DIK 1) leaves either screen.
A "press" is a fresh left-button press (latched until release, E-0954 style).

## Entry and exit (E-1300, E-1106)

| From | Opens | After it returns |
|---|---|---|
| Main menu item 5 (E-0505) | contents | back to the main menu |
| Contents: a fiche title or an index row | fiche viewer with that fiche label | contents reloaded, same theme still open, index closed |
| Zone type 8 with empty hands (E-0903) | fiche viewer with the zone's key | the place is re-entered (0x41f170) |
| Map spot of type 8 (E-1105) | fiche viewer with the spot's key | the map loop continues |

The key is a fiche label, matched case-insensitively against all fiches of all themes
(theme index, then fiche index). An unknown label: the viewer frees what it loaded and
returns 3 at once. The contents screen frees its sprites before opening a fiche and loads
them again after. Leaving either screen: the exit spiral (contents `som_spir`, viewer
`ico_spir`) on a press, or Escape; the result is 0.

## Contents screen (0x4085d0; E-1300)

Loads `fond_som` (INTERF, the background), then in this order `som_ying`, `som_tron`,
`som_the`, `som_pinc`, `som_boul`, `som_arch`, `som_pers`, `som_lieu` (theme 0..7, the
order of the themes in Fichetxt.txt), `som_spir` (exit), `fl_hajau`, `fl_bajau` (index
arrows up/down), `fl_hablc`, `fl_bablc` (the same, lit), `ico_indx` (index button),
`i_indinv` (index button lit), `i_sprinv` (exit lit).

**Themes.** Each `som_*` is drawn at its own position (rectangle T = its x, y, width,
height). Its theme `<title>` is drawn in font 10 at (centre x of T + 40, centre y of T - 5),
in white when hovered or open, else 0x7020. The hot area of theme k runs from that text
origin to (right of T + 30 + title width, bottom of T). A press in it toggles theme k's
fiche list (one theme open at a time; opening closes the index). Hover lighting is off
while a list or the index is open.

**Fiche list** of the open theme: the fiche `<title>`s in font 7, one per 15 px, at
x = T.x + 220, starting at y0 = centre y of T - 5; if y0 + 15 * count > 480 the list is
moved up to y0 = 480 - 15 * count. Hovered title 0x7020, others white. The hot rectangle of
title j is x from T.x + 220 to T.x + 220 + width, y from T.y + 2 + 15j to T.y + 13 + 15j,
moved up by the same shift (the drawn text and its hot strip are offset by the icon's
half height minus 7; keep both as given). A press opens that fiche.

**Index.** `ico_indx` at its own position (lit `i_indinv` when hovered or open). A press
toggles the index panel (closes the theme list). W = widest index row text in font 10
(0x4095a0: the part before `/`; header rows count 0). The panel: the screen rectangle at
x = 638 - W, y = 50, width W + 2, height = `fl_hajau` height + 315 is replaced, once when
opened, by itself with each channel (c + t) / 2 (t = tint 0 by default: half brightness).
Twenty rows of LISTE.TXT from the scroll position, one per 15 px from y = 65 to 350, at
x = 640 - W, font 10: a header row (`-C-`, or `-`) as is, in white, not clickable; an entry
row shows the text before `/`, 0x7020 when hovered, else white. Row hot rectangle: y from
65 + 15i to 78 + 15i, x from 640 - W to 640 - W + width. A press on an entry row opens the
fiche named after the `/`. Arrows `fl_hajau` at (640 - W/2, 50) and `fl_bajau` at
(640 - W/2, 365), lit versions while active: with the index open, merely hovering an arrow
scrolls one row per frame after a 10 ms busy wait, up to 0 and down to (row count - 20).
Debug keys (R, G or B held with P/O) change the tint channels 0..31, A resets them
(E-1300); not needed by the engine.

## Fiche viewer (0x40c5a0; E-1302..E-1305)

**Images** (0x40b8e0): `fl_hajau`/`fl_bajau` (history back/forward), `fl_hablc`/`fl_bablc`
(lit), `fl_drrou`/`fl_gcrou` (next/previous fiche of the theme), `fl_drblc`/`fl_gcblc`
(lit), `ico_spir` (exit), `ico_indx` (index), `ico_thei`, `ico_tron`, `ico_ying`, `ico_pinc`,
`ico_boul`, `ico_arch`, `ico_pers`, `ico_lieu` (theme badges), a second `fl_hajau`/`fl_bajau`/
`fl_hablc`/`fl_bablc` set (index arrows), `i_indinv`, `i_sprinv`. Background per theme
(0x40b7e0): theme 0..7 = `fondbeig`, `fondbrun`, `fondgris`, `fondoran`, `fondrose`,
`fondturk`, `fondvert`, `fondviol` (INTERF), reloaded whenever the theme changes.

**Page** (0x40c100, redrawn only when something changed): background; the four arrows at
their own positions, each lit when hovered and usable (below); the exit spiral (lit
`i_sprinv` on hover); the theme badge (theme 0 `ico_ying` +25,+15; 1 `ico_tron` +10,+5;
2 `ico_thei` -5,-5; 3 `ico_pinc` +20,+10; 4 `ico_boul` +15,+15; 5 `ico_arch` +15,+5;
6 `ico_pers` +20,+10; 7 `ico_lieu` +20,+10, offsets (x, y) added to a position the code
never sets except for `ico_thei`'s own; Q-1350); the fiche `<title>` in font 3, white,
centred on x = 320 at y = 10. The index button (lit when hovered or open) is drawn over it
every frame.

*Picture fiche* (`!name!`): `INTERF\name.tga` is loaded (0x416510), w x h. It is centred in
the box x 10..340, y 50..380: x = 176 - ceil(w/2), y = 216 - ceil(h/2) (w = 330 gives 11,
h = 330 gives 51). Wider or taller than 330: instead "Image trop large" / "Image trop haute"
at (100, 100), font 0, white. Every corpus picture is exactly 330 on one side (E-1303).
Caption: word-wrapped to w (330 if w < 165), font 8, white, lines 10 px apart, at
x = picture x (10 if w < 165), y = picture y + h + 1. Text: word-wrapped to 280 px in font 1
(the `$` signs count no width), trailing spaces cut, at x = 350 from y = 60, lines 15 px
apart, no scrolling or paging (the corpus fits). A line is justified to 280 px (spare
width spread over its spaces) when at least two more lines follow it. Words of a `$...$`
link are drawn without the `$` in 0x7020, other words in white. Each link word gets a hot
rectangle (x, y - 2, word width, 13 px high) with the link's number (0..9, the n-th `$..$`
pair of the text) (E-1304).

*Special fiche* (`!speciale!`, one: `fiche 85`, the Chinese sign): no picture; caption and
text each drawn by Text::drawBox (0x40e120), font 1, white, in boxes (100, 150)-(600, 400)
and (200, 150)-(600, 400) (two columns).

*Table fiche* (`!!`, `fiche 2` = table 0, `fiche 3` = table 1; 0x40bfe0): rows `<a>` at
x = 50, y = 50 + 20i, font 1; the selected row white, the others 0x7020. Hovering a row
whose `<b>` is not empty selects it (it stays selected). The selected row's `<b>`: table 0
in the box x 300..630 from the row's y down to 400 (0x409f20, font 1, white; Q-1351);
table 1 by Text::drawBox at x = 60 + width of `<a>`, from the row's y, right 630, bottom
480. The row's links take the selected row's link list (E-1305).

**Hover** (nothing happens while the index is open): over a link the cursor is 8 and the
target fiche's `<title>` is shown at (355, 435), font 10, 0x7020; elsewhere cursor 11.

**Presses:**
- Link: open the linked fiche (its theme's background is loaded), push it on the history.
- `fl_gcrou`: previous fiche of the same theme, if not the first; `fl_drrou`: next, if not
  the last; both push it on the history. No wrap.
- `fl_hajau`: history back; `fl_bajau`: history forward (they do not push).
- `ico_spir`: leave. `ico_indx`: toggle the index panel. Any press outside the index
  button while the index is open closes it (a press on an entry row first opens that
  fiche and pushes it).

**History** (global, kept between visits; 50 labels at 0x4cdd58, E-1302): every fiche
shown by opening the viewer, a link, the theme arrows or the index is written at the end
position and becomes current (going back and then opening a fiche does not cut the
forward part; the new entry goes after the last one). When the end reaches 50 the list
restarts at slot 0 holding only the new entry, in "wrapped" mode, where back from slot 0
goes to 49 and forward from 49 to 0. Back is usable when current is not the end and not
0 (unless wrapped); forward when current + 1 is not the end. Original bug: the 51st write
lands one slot past the 50-label array before the restart (E-1302); the engine keeps 50.

**Index panel** in the viewer: as on the contents screen, but the panel is darkened to
1/8 of each channel (mode 1, tint 0), and the panel is redrawn over the page each frame.
