# INFOOBJ.BIN format findings

## TL;DR

`Data/U##/INFOOBJ.BIN` is a per-unit object-info container: a fixed-width table of
68-byte entries preceded by a `u32 count` and terminated by a 32-byte `#OBJECTS#`
footer. The on-disk layout is fully pinned down. Every byte is consumed by
`tools/parsers/infoobj.py` over all 9 corpus files (100% pass, 183 entries, 12,768
bytes total).

## Loader evidence

Two loaders in `MissionMonet.exe` reference `INFOOBJ.BIN`:

* `FUN_0041d490` (`0x0041d490`) — opens INFOOBJ.BIN standalone when called with a
  null reader (`notes/decomp/MissionMonet.exe__FUN_0041d490.c:42-69`); also serves as
  the entry point for a generic reader that processes `SCENE` / `ANIMATIONS` /
  `OBJECTS` sections in `Scene.bin` when called with a non-null reader
  (`notes/decomp/MissionMonet.exe__FUN_0041d490.c:70-91`).
* `FUN_0041d6f0` (`0x0041d6f0`) — the actual OBJECTS-sub-loader; reads the entries
  (`notes/decomp/MissionMonet.exe__FUN_0041d6f0.c:64-79`).

The string `s_INFOOBJ_BIN_00441b88` lives at `MissionMonet.exe + 0x41b88` and
spells `INFOOBJ.BIN\0`. The OBJECTS-section string lives at `0x41bc0` (`OBJECTS\0`).
The path is built by `sprintf(buf, "Data/U%02d/INFOOBJ.BIN", DAT_00442640 + 8)`
(line 44/46 of the two decompiled files), where `DAT_00442640` is the unit-number
slot populated earlier in the engine.

`FUN_0041d6f0` reads:

```c
iVar1 = FUN_00415190(this_00, s_OBJECTS_00441bc0);   // find "OBJECTS" tag
if (iVar1 != 0) {
    FUN_004153a0(this_00, &local_118, 4);            // u32 count
    if (local_118 == 0) { ExceptionList = local_c; return 1; }
    local_114 = operator_new(local_118 * 0x44);
    FUN_004153a0(this_00, local_114, local_118 * 0x44);   // count * 68 bytes
    FUN_00415180((int)this_00);                      // close section
}
```

`FUN_00415190` is the seek-to-tag reader primitive. `FUN_004153a0` is a bulk-copy
read. `FUN_00415180` is the close-section primitive.

After the entries are in memory, the loader iterates them and calls
`FUN_0041b440` per entry (`notes/decomp/MissionMonet.exe__FUN_0041d6f0.c:84-108`).
That sub-loader is what interprets each 68-byte blob; the raw fields are not parsed
inside `FUN_0041d6f0` itself.

## On-disk layout

The 9 corpus files all follow this exact layout (verified by `tools/parsers/infoobj.py`):

```
+0x000  u32          count
+0x004  entry[0]     68 bytes
+0x048  entry[1]     68 bytes
...
+0x004 + count * 68  terminator  (32 bytes)
```

where each entry is:

```
+0x00  8  bytes     name (NUL-terminated, e.g. "*U04_03\0")
+0x08  32 bytes     reserved (every byte is 0xCD in the corpus)
+0x28  4  bytes     u32 field_a
+0x2C  4  bytes     u32 field_b   <-- overwritten at runtime with a pointer
+0x30  4  bytes     u32 field_c
+0x34  4  bytes     f32 field_d
+0x38  4  bytes     u32 field_e
+0x3C  4  bytes     u32 field_f
+0x40  4  bytes     u32 field_g
```

and the terminator is:

```
+0x00  10 bytes     "#OBJECTS#\0"
+0x0A  10 bytes     0xCD padding
+0x14  4  bytes     u32 = 0          (count of this OBJECTS section)
+0x18  4  bytes     u32 = offset_of_OBJECTS_tag
+0x1C  4  bytes     u32 = 1          (flag)
```

## Why the terminator has `count = 0`

`FUN_0041d6f0` short-circuits when it reads `count == 0` (line 69-72). The trailing
`#OBJECTS#` tag in every corpus file carries `count = 0`, so the loader opens the
section, reads `count`, returns `1`, and never reads past the tag. The 32 bytes after
the tag are therefore only there to keep the file size predictable / align to 32 bytes
past the last entry.

The real entries (with `count > 0`) sit *before* the trailing terminator and are NOT
inside an `OBJECTS` section header of their own — the file simply starts with the
`u32 count`. The engine's tag-seek machinery must therefore look at the trailing
`#OBJECTS#` first when called for `OBJECTS`, then somehow get back to the entries
block to actually read them. This is consistent with the call order in
`FUN_0041d490` (the parent loader), which calls `FUN_00415180` to *close* a section
and then re-issues `FUN_0041d8e0` to rewind the reader, before the OBJECTS sub-loader
runs. The rewind mechanism is opaque to static analysis here and is left as a future
task (the data layout itself is fully pinned regardless).

## Corpus inventory

| File | Size | Entries | Names |
|---|---:|---:|---|
| `U00/Infoobj.bin` | 376 | 5 | `*U04_03 *U04_32 *U04_36 *U04_43 *U04_80` |
| `U01/INFOOBJ.BIN` | 1736 | 25 | `*U01_01 .. *U01_24, *Ernest` |
| `U02/INFOOBJ.BIN` | 1192 | 17 | `*U02_01 .. *U02_14, *U02_06a, *U02_07a, *U02_09a` |
| `U03/INFOOBJ.BIN` | 1804 | 26 | `*U03_01 .. *U03_29` (gaps) |
| `U04/INFOOBJ.BIN` | 3300 | 48 | `*U04_01 .. *U04_53` (gaps), `*Ernest`, `*U03_06` |
| `U05/Infoobj.bin` | 1056 | 15 | `*U05_01 .. *U05_13, *Fil, *U04_04` |
| `U06/INFOOBJ.BIN` | 580 | 8 | `*U06_15 .. *U06_21, *U03_02` |
| `U07/INFOOBJ.BIN` | 784 | 11 | `*U06_22 .. *U06_30, *Eteint01, *U06_19` |
| `U33/INFOOBJ.BIN` | 1940 | 28 | `*U03_01 .. *U03_37` (gaps) |

Entry names are not necessarily unique across files — `*U03_06` appears in both
`U04/INFOOBJ.BIN` and `U33/INFOOBJ.BIN`, `*Ernest` appears in both `U01` and `U04`,
`*U04_04` appears in both `U04` and `U05`. This is consistent with the engine
referencing scene objects by name across unit boundaries.

## Unexplained / opaque

* **`reserved` (entry offset `+0x08`, 32 bytes)**: every byte is `0xCD` across all 9
  files and 183 entries. This is MSVC's uninitialised-heap pattern, and the runtime
  loader overwrites the first 4 bytes of this region (entry offset `+0x2C`) with a
  pointer to the loaded object's handle (see `FUN_0041d6f0:88-96`). The remaining 28
  bytes presumably hold pointer-sized slots that get populated by `FUN_0041b440` (the
  per-entry sub-loader), but `FUN_0041b440` is not decompiled here. The slot
  semantically becomes 8 pointer fields at runtime, so the writer never bothered to
  serialise them. See OPEN-QUESTIONS for the full picture.

* **Seven numeric fields** (`field_a` .. `field_g`): values are stable per field
  across the corpus, suggesting well-defined semantics, but the meaning of each is
  unknown without decompiling `FUN_0041b440`. Empirical notes:
    * `field_a` (`+0x28`): mode 4 or 5, occasional 6.
    * `field_b` (`+0x2C`): on-disk values 0..5, but the runtime value is a pointer.
    * `field_c` (`+0x30`): almost always 1.
    * `field_d` (`+0x34`): almost always 1.0; one entry in U01 has 20.0.
    * `field_e` (`+0x38`): almost always 1.
    * `field_f` (`+0x3C`): strong mode at 15 (170/183), with 0, 2, 4, 50 outliers.
    * `field_g` (`+0x40`): mode 1 (139/183), rest 0.

* **Terminator `flag = 1`**: present in every corpus file; semantics unknown.

## Validator output

```
$ python tools/parsers/infoobj.py
corpus: C:\...\Original Game Files\Data
files: 9  passed: 9  failed: 0
  objects: 183
  bytes:   12768
100% of corpus parsed
```
