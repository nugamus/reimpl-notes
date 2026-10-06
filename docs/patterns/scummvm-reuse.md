# What ScummVM already has

Check here, and with `python tools/ref.py -s scummvm-src <thing>`, before writing code.
Reviewers ask why an engine carries its own copy of something ScummVM provides.

**Video** (`video/`): 3DO, 4XM, AVI, Bink, Coktel IMD/VMD, DXA, FLIC, HNM (Cryo, used by
Peintre), MKV, MPEG-PS (`mpegps_decoder`, used by Grumpa), MVE, PACo, PSX streams, QuickTime,
Smacker, Theora. `Video::VideoDecoder` is the common interface.
**Images** (`image/`): ANI, BMP, CEL (3DO), GIF, ICO/CUR, IFF, JPEG, PCX, PICT, PNG, TGA, XBM,
plus codecs (`image/codecs/`: Cinepak, Indeo 3/4/5, MJPEG, MPEG, MS MPEG-4, MS RLE, MS Video 1,
QuickTime RLE/RPZA/SMC, SVQ1, TrueMotion 1, Xan, ...). **Audio** (`audio/decoders/`): WAV
(PCM, ADPCM variants), MP3, Vorbis, FLAC, AAC, AIFF, QuickTime, VOC, raw; mixers and MIDI
drivers in `audio/`.
**Archives and executables** (`common/compression/`, `common/formats/`): InstallShield
`.cab` and v3 archives, Clickteam, Gentee and VISE installers, StuffIt, ARJ, zip, deflate,
DCL (PKWARE implode), RNC, PowerPacker; Windows PE and NE resources (`winexe_pe`,
`winexe_ne`: icons, cursors, strings, fonts), QuickTime atoms, IFF containers, INI files,
CUE sheets and disk images.
**Graphics**: `Graphics::ManagedSurface`, pixel formats and conversion, `Graphics::Font`
(Windows FON via `WinFont`, TrueType via FreeType), `CursorMan`, TinyGL (software 3D with
an OpenGL-like API) and OpenGL/OpenGL ES backends, MacGUI.
**Engine services**: `SearchMan` (find game files), `ConfMan` (settings), save/load with
thumbnails and metadata (`MetaEngine`), extra GUI options (game-specific checkboxes),
the keymapper, debug channels (`debugC`) and the GUI debugger console, `Common::RandomSource`
(registered, so the event recorder can replay it), the event recorder, translations.

**Engines worth reading for a similar problem**
- Pre-rendered scenes with 3D characters, z-buffer compositing: Grim (`grim`), Myst 3
  (`myst3`, also panoramas and video), Stark (`stark`).
- Panoramas and VR nodes: PhoenixVR (`phoenixvr`), Myst 3, Riven (`mohawk`).
- Software 3D renderers: anything on TinyGL (`grim`, `myst3`, `stark`, `freescape`).
- Script VMs with an event queue: Wintermute (`wintermute`), SCI (`sci`), Director (`director`).
- Delphi/DirectX-era adventures and their detection: `phoenixvr`, `cryomni3d`, `pink`.
- Cursor and inventory UI as in point-and-click games: `cryomni3d`, `pegasus`.
