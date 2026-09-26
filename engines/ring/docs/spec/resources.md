# Resources: where an image, archive or sound is read from (Ring, DVD)

Evidence: E-0034. Addresses are `RING_DVD.EXE`.

## Load-from and kind

Every image handle (0x42d260) records the zone it was declared in (+0x79), a *kind*
(+0x7a) and a *load-from* byte (+0x7b):

- load-from `'e'` (disk) or `'f'` (archive), from `GetreadFrom(zone)` (0x402130,
  `spec/boot.md`) at declaration time;
- kind = app+0x5d at declaration time: 2 while the SY zone is set up, 1 for the other
  zones (0x431040); 5 for handles given an explicit directory (0x42d710).

## Image paths (`aPuzzle::Alloc` 0x41bdc0 and the other `Alloc`s)

| Load-from | Kind | Path |
|---|---|---|
| `'e'` | 1 | `<CD path>DATA\<zone folder>\IMAGE\<name>` (prefix 0x402470) |
| `'e'` | 2 | `<install path>DATA\<zone folder>\IMAGE\<name>` (prefix 0x402480) |
| `'e'`/`'f'` | 5 | `<directory><name>` |
| `'f'` | 1, 2 | archive member `\IMAGE\<name>` |

Zone folders are 0x402010's (`sy ni rh fo ro wa as n2`). Animations use their own
directory (e.g. archive members `\ani\<name>\<name>.%04d.bmp`, `\cursor\…`, `\lsticon\…`,
`\list\…`), specified with animations and cursors.

`aImage::Load` (0x413150) picks the decoder by the name's last three letters:

| Extension | From disk (`'e'`) | From an archive (`'f'`) |
|---|---|---|
| `bmp` (or a name under 3 letters, or anything else) | plain BMP | packed BMA |
| `bma` | packed BMA | packed BMA |
| `tga` | plain TGA | packed TGC |
| `tgc` | packed TGC | packed TGC |
| `cnm` | CNM frame (0x42a510) | — |

## Archives

`aArtHandler::Open(zone, kind)` (0x419bc0) opens `<prefix>DATA\<zone folder>.at2`
(format `%s%s\%s.at2` with the prefix, `DATA` and 0x402010's folder; prefix per kind as
above) once. `aApplication::Init` opens SY's
(from the install path); entering a zone (`GameSetZone` 0x40d220) opens that zone's with
kind 1 when its load-from is `'f'`. A lookup (`aArtHandler::GetData` 0x419e10 → 0x419b50)
finds the archive by (zone, kind), except that kinds 2..5 always use (1, 2): SY's archive.
Member names are compared case-insensitively (0x479410) and must match exactly.

## Language

The discs keep SY's archive per language (`DATA\<LAN>\SY.AT2`, E-0008) while the path
above is `DATA\sy.at2` (the ISO version also has a `data\sy.at2`, the English one): which
one an installed game reads is Q-0008; dialogue sounds and
subtitles use the language folder of `GetLanNam` (`…\<zone>\SOUND\<LAN>\…`,
`…\DIA\<LAN>\…`), specified with sound and dialogue.

## Open

- Q-0006 (partly answered here): the CD path is `CDPATH` from `fl.ini`, the install
  path app+0x18; ScummVM keeps both under the game directory.
- Q-0007: the AS zone declares `.bma` backgrounds (`Old_Ish.bma`, `ASV01.bma`, …) that
  exist only as loose files, while the DVD's `fl.ini` sets `ART_AS: 1` and `AS.AT2` holds
  the same pictures under other names (`\image\old_ish.bmp`, `\image\ass01n01_v01.bmp`).
