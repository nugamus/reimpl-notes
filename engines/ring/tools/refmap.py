"""Map the binaries' class::method names to Templier's reference engine, and line the four
programs up against each other by name.

Input: engines/ring/notes/names/<PROGRAM>.csv (tools/ghidra/scripts/ring_string_namer.py)
and reference/templier-scummvm-ring/engines/ring. Output: engines/ring/notes/reference-map.md.

The class table below is a map, not evidence: it says where in Templier's tree to read, and
a row becomes a fact only once the binary confirms it. Method names are
matched mechanically: the original abbreviations (`ObjPreAddAniToPuz`) are expanded word by
word (`objectPresentationAddAnimationToPuzzle`) and compared case-insensitively with every
method name declared in the reference headers.

    python engines/ring/tools/refmap.py
    python engines/ring/tools/refmap.py --selftest
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
NAMES = REPO / "engines/ring/notes/names"
REF = REPO / "reference/templier-scummvm-ring/engines/ring"
PROGRAMS = ["RING_DVD.EXE", "RING_ISO.EXE", "RING_CD.EXE", "LEGEND.EXE"]

# Binary class -> (reference class, reference file). Where to read, not proof.
CLASSES = {
    "aAccesibility": ("Accessibility", "base/accessibility"),
    "aAnimation": ("Animation", "graphics/animation"),
    "aAnimationImage": ("AnimationImage", "graphics/animation"),
    "aApplication": ("Application", "base/application, game/*/*_application"),
    "aArt": ("Art", "base/art"),
    "aArtHandler": ("ArtHandler", "base/art"),
    "aByte": ("VarEntry", "base/var"),
    "aWord": ("VarEntry", "base/var"),
    "aDoubleWord": ("VarEntry", "base/var"),
    "aFloat": ("VarEntry", "base/var"),
    "aVarString": ("VarEntry", "base/var"),
    "aVar": ("Var", "base/var"),
    "aCin": ("Cinematic", "graphics/movies/cinematic"),
    "aCinMov": ("Movie", "graphics/movies/movie"),
    "aCinemaCompression": ("Cinematic2", "graphics/movies/cinematic2"),
    "aCursor": ("CursorBase", "base/cursor"),
    "aCursorAnimation": ("CursorAnimation", "base/cursor"),
    "aCursorImage": ("CursorImage", "base/cursor"),
    "aCursorHandler": ("CursorHandler", "base/cursor"),
    "aDialog": ("Dialog", "base/dialog"),
    "aDialogHandler": ("DialogHandler", "base/dialog"),
    "aFileIo": ("CompressedStream", "base/stream"),
    "aFileIoBuf": ("CompressedStream", "base/stream"),
    "aFileIoArt": ("CompressedStream", "base/stream"),
    "aFileList": ("SaveManager", "base/saveload"),
    "aFont": ("Font", "base/font"),
    "aFontHandler": ("FontHandler", "base/font"),
    "aHotSpot": ("Hotspot", "graphics/hotspot"),
    "aImage": ("ImageSurface", "graphics/image"),
    "aImageHandle": ("ImageHandle", "graphics/image"),
    "aImageFileBMP": ("ImageLoaderBMP", "graphics/codecs/imageloader_bmp"),
    "aImageFileBma": ("ImageLoaderBMA", "graphics/codecs/imageloader_bma"),
    "aImageFileCin": ("ImageLoaderCIN", "graphics/codecs/imageloader_cin"),
    "aImageFileCinema": ("ImageLoaderCI2", "graphics/codecs/imageloader_ci2"),
    "aImageFileTGA": ("ImageLoaderTGA", "graphics/codecs/imageloader_tga"),
    "aImageFileTgc": ("ImageLoaderTGC", "graphics/codecs/imageloader_tgc"),
    "aLanguage": ("Language", "base/language"),
    "aLanguageHandler": ("LanguageHandler", "base/language"),
    "aList": ("VisualObjectList", "graphics/visual/visual_list"),
    "aMovability": ("Movability", "base/movability"),
    "aObject": ("Object", "base/object"),
    "aObjectHandler": ("ObjectHandler", "base/object"),
    "aObjectPresentation": ("ObjectPresentation", "base/object"),
    "aPreFer": ("PreferenceHandler", "base/preferences"),
    "aPuzzle": ("Puzzle", "base/puzzle"),
    "aRotation": ("Rotation", "base/rotation"),
    "aSecComAqi": ("AquatorStream", "graphics/aquator/aquator_stream"),
    "aSecComSou": ("CompressedSound", "sound/sound_loader"),
    "aSecComSouMono": ("CompressedSoundMono", "sound/sound_loader"),
    "aSecComSouStereo": ("CompressedSoundStereo", "sound/sound_loader"),
    "aSecComRes": ("SoundResource", "sound/sound_loader"),
    "aSoundHandler": ("SoundHandler", "sound/sound_handler"),
    "aSoundItem": ("SoundItem", "sound/sound_handler"),
    "aText": ("Text", "base/text"),
    "aTimer": ("Timer", "base/timer"),
    "aTimerHandler": ("TimerHandler", "base/timer"),
    "aVideoDeviceRaw": ("ScreenManager", "graphics/screen"),
    "aZone": ("Zone", "base/zone"),
    "aZoneHandler": ("ZoneHandler", "base/zone"),
    "aEpizode": ("Episode", "game/pilgrim2"),
}

# Original abbreviation -> word(s), from the names in the error strings.
ABBR = {
    "Obj": "object", "Pre": "presentation", "Puz": "puzzle", "Rot": "rotation",
    "Acc": "accessibility", "Mov": "movability", "Ani": "animation", "Img": "image",
    "Coo": "coordinates", "Sou": "sound", "Amb": "ambient", "Bgr": "background",
    "Txt": "text", "Wid": "width", "Sho": "show", "Hid": "hide", "Pau": "pause",
    "Fra": "frame", "Sta": "start", "Act": "active", "Ori": "original", "Cur": "cursor",
    "Pas": "passive", "Dra": "draw", "Rem": "remove", "Fon": "font", "Lan": "language",
    "Cha": "channel", "Nam": "name", "Tit": "title", "Col": "color", "Tim": "timer",
    "Sto": "stop", "Vis": "visual", "Lis": "list", "Ind": "index", "Cli": "clicked",
    "Num": "number", "Ite": "items", "Rid": "ride", "Com": "compression", "Buf": "buffer",
    "Len": "length", "Ply": "play", "Dis": "display", "Fad": "fade", "Vol": "volume",
    "Dea": "dealloc", "Sub": "sub", "Is": "has", "In": "", "Ide": "",
}


def expand(name: str) -> str:
    """`ObjPreAddAniToPuz` -> `objectpresentationaddanimationtopuzzle`."""
    parts = re.findall(r"3D|[A-Z][a-z]*|[a-z]+|\d+", name)
    return "".join(ABBR.get(p, p).lower() for p in parts)


def keys(name: str) -> list[str]:
    """Candidate reference names for `Class::Method`: the expansion, the literal name,
    verb moved behind its noun (`AddObj` -> `objectadd`), constructors (`aX::aX` -> `x`)."""
    meth = name.split("::")[-1]
    out = [expand(meth), meth.lower()]
    parts = re.findall(r"3D|[A-Z][a-z]*|[a-z]+|\d+", meth)
    if len(parts) >= 2 and parts[0] in ("Add", "Rem", "Get", "Set", "Is"):
        out.append(expand("".join(parts[1:2] + parts[:1] + parts[2:])))
    if "::" in name and name.split("::")[0] == meth and meth in CLASSES:
        out.append(CLASSES[meth][0].lower())
    return list(dict.fromkeys(out))


def ref_methods() -> dict[str, list[str]]:
    """lower-cased method name -> ['Class::method (file)'] over every reference header."""
    out = defaultdict(list)
    decl = re.compile(r"^\s*(?:virtual\s+|static\s+)?[\w:<>&*\s]+?\b(\w+)\s*\([^;{]*\)\s*(?:const)?\s*[;{=]")
    for h in REF.rglob("*.h"):
        cls = None
        for line in h.read_text(encoding="latin1").splitlines():
            m = re.match(r"^class (\w+)", line)
            if m:
                cls = m.group(1)
            m = decl.match(line)
            if m and cls:
                out[m.group(1).lower()].append(f"{cls}::{m.group(1)} ({h.relative_to(REF).as_posix()})")
    return out


def load(program: str) -> dict[str, list[str]]:
    rows = csv.DictReader((NAMES / f"{program}.csv").open(encoding="utf-8"))
    out = defaultdict(list)
    for r in rows:
        if r["verdict"] == "named":
            out[r["name"]].append(r["address"])
    return out


def main() -> None:
    progs = {p: load(p) for p in PROGRAMS}
    refs = ref_methods()
    names = sorted(set().union(*progs.values()))
    lines = [
        "# Reference map: binary names → Templier's engine",
        "",
        "Generated by `engines/ring/tools/refmap.py` from `notes/names/*.csv`",
        "(`ring_string_namer.py`). A map of where to read, not evidence: every row is",
        "confirmed in the binary before it enters a spec. Addresses are function entries.",
        "",
        "## Classes",
        "",
        "| Binary class | Reference class | Reference file | Named methods (DVD/ISO/CD/Prophet) |",
        "|---|---|---|---|",
    ]
    by_class = defaultdict(lambda: [0] * len(PROGRAMS))
    for i, p in enumerate(PROGRAMS):
        for n in progs[p]:
            by_class[n.split("::")[0] if "::" in n else "(no class)"][i] += 1
    for cls, counts in sorted(by_class.items()):
        ref_cls, ref_file = CLASSES.get(cls, ("?", "?"))
        lines.append(f"| `{cls}` | {ref_cls} | `{ref_file}` | {'/'.join(map(str, counts))} |")
    matched = 0
    lines += ["", "## Methods", "",
              "| Name | " + " | ".join(PROGRAMS) + " | Reference |",
              "|---|" + "---|" * len(PROGRAMS) + "---|"]
    for n in names:
        meth = n.split("::")[-1]
        cands = [c for k in keys(n) for c in refs.get(k, [])]
        cls = n.split("::")[0] if "::" in n else None
        if cls in CLASSES:  # prefer candidates in the mapped class
            same = [c for c in cands if c.startswith(CLASSES[cls][0] + "::")]
            cands = same or cands
        matched += bool(cands)
        addrs = [", ".join(f"`{a}`" for a in progs[p].get(n, [])) or "—" for p in PROGRAMS]
        lines.append(f"| `{n}` | " + " | ".join(addrs) + " | " + ("; ".join(sorted(set(cands))[:3]) or "—") + " |")
    lines[5:5] = [f"{len(names)} distinct names over the four programs; {matched} have a "
                  "reference method with the expanded name.", ""]
    (REPO / "engines/ring/notes/reference-map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(names)} names, {matched} matched")


def selftest() -> None:
    assert expand("ObjPreAddAniToPuz") == "objectpresentationaddanimationtopuzzle"
    assert expand("PuzAdd3DSou") == "puzzleadd3dsound"
    assert expand("RotSetMovRidNam") == "rotationsetmovabilityridename"
    assert expand("AddAmbientSound") == "addambientsound"
    assert "objectadd" in keys("aApplication::AddObj")
    assert "accessibility" in keys("aAccesibility::aAccesibility")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
