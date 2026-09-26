# Text: fonts, texts on puzzles, messages

Ring draws its texts with Windows GDI: a raster font from `arxrin.fon`, `TextOutA` on the
back buffer's device context. Evidence E-0043 (font file), E-0044 (everything else).

## Fonts

`aApplication::Init` (0x407b80) adds `arxrin.fon` (`aFontHandler::AddResource` 0x4265b0:
`AddFontResourceA` on the name, relative to the game folder; failure is logged and the
game goes on) and creates font 1 with `FonAdd` (0x406900 → `aFontHandler::Add` 0x426820 →
0x4262d0):

| Language (id) | Face | Height |
|---|---|---|
| HEB (8) | `ArxelHebrew` | 12 |
| GRE (9) | `Arial` | 16 |
| any other | `ARX Pilgrim L` | 12 |

`FonAdd(id, face, height, weight, underline, italic, strikeout)` (here `1, face, height,
1, 2, 2, 2`) fills a `LOGFONTA`: `lfHeight` = height (positive: a cell height), weight 400
when the argument is 1 else 700, underline / italic / strikeout set when their argument is
1, `lfCharSet` 2 for language 8 and 0xA1 for language 9, 0 otherwise, face name copied;
then `CreateFontIndirectA`. Fonts are looked up by id (`GetFontHandler` 0x426a90).

`arxrin.fon` has no 12-pixel cell: its "ARX Pilgrim L" sizes have cells of 13, 16, 20, 24,
29 and 37 pixels (formats README "Fonts"). Which one GDI picks for 12 is Q-0010; the
closest is 13 (8 points).

## Texts (`aText`)

`ObjPreAddTxtToPuz(object, presentation, puzzle, text, x, y, font, r, g, b, bg_r, bg_g,
bg_b)` (0x403b10 → `aObjectPresentation::ObjPreAddTxtToPuz` 0x42f270) creates a text,
`aText::Init` (0x42c450):

- position (x, y), font id, colour `RGB(r, g, b)`;
- background: all three `bg_*` −1 means transparent, otherwise the opaque colour
  `RGB(bg_r, bg_g, bg_b)`;
- the string is set (0x42c550, below).

The text is linked to its presentation (0x42c730, text +0x21), which keeps it in its text
list (+0x29, with the puzzle in a parallel list +0x2d), and it is appended to the puzzle's
text list (+0x18, 0x41cee0).

Setting a string (0x42c550; also `ObjPreSetTxtToPuz(object, presentation, index, string)`
0x403ba0 → 0x421010 → 0x42f520, `index` = the presentation's n-th text) copies it and measures it
with `GetTextExtentPoint32A` in its font: width +0x14, height +0x18 (0 and 0 when the font
does not exist). `ObjPreGetTxtWid` (0x42f5d0) returns the width.
`ObjPreSetTxtCooToPuz(object, presentation, index, x, y)` (0x403bf0 → 0x421080) moves a text.

## Drawing

`aPuzzle::Update` (0x41c320) draws the puzzle's texts after its presentation images
(`spec/drawing.md`), in list order, each with 0x414df0: skipped when it belongs to a
presentation that is not shown; otherwise on the back buffer's DC, background mode opaque
with the background colour or transparent, text colour, its font selected, then
`TextOutA(x, y, string)`. With the default text alignment (x, y) is the top left of the
character cells; a transparent text draws only the glyphs' set pixels, an opaque one also
fills each cell with the background colour. Characters outside the font's range are drawn
as its default character.

## Messages (`GetMultiLanMes` 0x40e150)

`GetMultiLanMes(key)` reads `aMes.ini` from the game folder (`%sames.ini`, text mode):

1. `fscanf("%s\n")` words until one equals the key (the whole file: not found logs
   "Can not find Message").
2. Up to ten lines follow, each read up to `\n` (at most 253 characters). A line shorter
   than 3 characters ends the search ("Wrong Line"); the first line whose first three
   characters are the current language's name (`ENG`, `FRA`, …) is the one.
3. In that line, the last `#` ends the title and starts the text; the `#` before it starts
   the title: `ENG     #Warning#Cannot load game: %s` gives title `Warning`, text
   `Cannot load game: %s`; `ENG     ##Do you want to start a new game?` gives an empty
   title.

The title goes to a global buffer (0x49536c), the text to another (0x49546c); both are set
to the empty string at 0x49523c when the file cannot be opened. The warning and question dialogues
(`games/ring/docs/sy.md`) show them as their two lines: title at (225, 193), text at
(225, 213).
