# Video playback and full-screen fades (Ring, DVD)

Evidence: E-0037 (and E-0024, E-0028, E-0029 for the file format). Addresses are
`RING_DVD.EXE`.

## Playing a `.cnm` (`aCinMov::Play` 0x415990, from `PlyCin` 0x401490)

- **Path:** `PlyCin(name, rate)` plays `<prefix>DATA\<zone folder>\PLA\<name>.cnm`
  (0x401490: `%s%s\%s\%s` + `.cnm`); it first waits for Escape to be released.
- **Picture:** each 'S' chunk decodes into one 640×448 picture kept between frames
  (formats README "HBR video codec") and is drawn at (0, 16).
- **Timing:** the frame time is `1000 / (header[+0x12] × 0.01)` ms (Init, constants
  0x47e270 = 1000.0, 0x47e408 = 0.01): 80 ms for the Ring value 1250 (12.5 frames per
  second). `PlyCin`'s `rate` argument, when not 0, replaces it with `1000 / rate`. The
  clock starts at the first picture. For each 'S' chunk: if the picture is due later than
  now + 50 ms, the player waits until 50 ms before it is due, then decodes and draws it;
  if it is already late, the chunk is skipped unread (`aCin::Decompress` 0x42cb90 only
  seeks past it).
- **Sound:** the sound chunk of the language channel (`spec` E-0029: 'Z' for channels 0/1,
  'A' for 2, 'B' for 3) is appended to one streaming sound as raw PCM in the header's
  format; the other channels are skipped. The stream starts with the first sound chunk.
- **Subtitles:** `aCinMov::Init` looks for `<name>.dia` in the language's DIA folder; when
  present it is shown as a dialogue during the video (`spec/dialogue.md`, to come).
- **End:** after `frame_count` pictures, or at once when Escape is pressed (the key is
  drained first).

## Fading between two pictures (`aApplication::DisFad` 0x4018c0)

`DisFad(from, to, frames, hold_ms, kind, load_from)`: both pictures are loaded (disk or
archive per `spec/resources.md`); they must be 24-bit and of the same size, else nothing
happens (error). For every byte of every pixel a step `(from − to) / frames` (C integer
division) is computed. An animation clock of `frames` frames at 25 frames per second
(`aAnimation::Init(frames, 25.0, …)`) then drives the fade: at each new clock frame every
byte of the *from* picture has its step subtracted (8-bit wrap-around) and the picture is
drawn at (0, 16); the loop stops after `frames` frames or when Escape is held. The *to*
picture is then drawn, and the function waits `hold_ms` milliseconds (0x402890: polls the
tick count, returns early when Escape is held).
