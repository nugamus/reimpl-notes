"""Build engines/peintre/notes/function-map.csv from the Ghidra dump.

Every function of /MISSION.EXE gets its module (by address range, module-map.md says why)
and, where a string proves it, a name with the evidence string. The names are applied
back to Ghidra with tools/ghidra/scripts/apply_names.py.

    python engines/peintre/tools/funcmap.py            # reads notes/function-dump.tsv
    python engines/peintre/tools/funcmap.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

NOTES = Path(__file__).resolve().parents[1] / "notes"

# (first address, module). A function belongs to the last range starting at or below it.
MODULES = [
    (0x401000, "link/thunks"),        # incremental-link jump stubs
    (0x4022C0, "game/puzzles"),       # 2D puzzles, strings A01_/A03_/A13_/A14_ assets
    (0x408CF1, "game/shell"),         # 2D shell on the Cryo libraries: time, sprites, fonts,
                                      # movies, TGP, cursor, menus, saves, window procedure
    (0x416650, "game/sound"),         # DirectSound use: streams, statics, WAV/APC loading
    (0x4180C0, "game/users"),         # registry, USERS.BIN, player-name window, display
    (0x419F0E, "game3d/scenes"),      # per-scene LoadBox*/LoadAnims* and scene logic, one
                                      # object file per scene in alphabetical order
    (0x41AB80, "game3d/tga"),         # LoadTga, screen dumps to D:/VANGOGH/TGA
    (0x41B5A0, "game3d/scenes"),      # cafe .. champ
    (0x41ED13, "game3d/world"),       # PEINTRE.INI, scene table, C_Monde, 3D main loop
    (0x4241F0, "game3d/scenes"),      # eglise .. terrasse
    (0x42E630, "game3d/app"),         # Vangogh error box, scene file loading, 3D saves
    (0x42FBD6, "game3d/cinematics"),
    (0x430700, "engine3d"),           # 3D engine: heap, 3DM/3DC/3DI/3DA loading, camera
    (0x455470, "engine3d/asm"),       # assembly without C prologues (Q-0002)
    (0x465BD0, "cryo/codec"),         # APC ADPCM
    (0x466D40, "cryo/file"),          # Win32 File I/O library
    (0x467290, "cryo/font"),          # Win32 Fonts library
    (0x467514, "cryo/misc"),          # unattributed Cryo code up to the memory manager
    (0x4709E0, "cryo/memory"),        # Memory Manager (m__malloc...)
    (0x471090, "cryo/ddraw"),         # DirectDraw 5 library
    (0x472410, "cryo/dinput"),
    (0x472D40, "cryo/dsound"),        # DirectSound 5 library
    (0x474CC0, "msvcrt"),             # static debug C runtime
]

# address -> (name, proving string). Names are ours unless the string spells them.
NAMES = {
    0x408D43: ("FatalError", "Fatal Error !"),
    0x4097F0: ("AllocFrameBuffers", "Could not allocate frame-buffer ..."),
    0x40A24C: ("Sprite_Open", "Sprite '%s': plus de slot banque disponible..."),
    0x40A766: ("Sprite_LoadFile", "%sDATA\\SPRITES\\%s.SPR"),
    0x40ACDE: ("Font_LoadAwf", "%sDATA\\FONTS\\%s.AWF"),
    0x40B992: ("Hnm_AllocDecBuffers", "'%s': could not allocate HNM dec buffers ..."),
    0x40BA64: ("Hnm_Open", "%sDATA\\MOVIES\\%s.CVY / .HNM"),
    0x40C072: ("Hnm_Stream", "Cannot stream closed movie !"),
    0x40C3D8: ("Hnm_StartReadThread", "Could not create HNM read thread ..."),
    0x40D9C0: ("Tgp_Load", "%sDATA\\GFX\\%s.TGP"),
    0x414779: ("Tgp_Load2", "%sDATA\\GFX\\%s.TGP"),
    0x40E78a: ("Save_ListGames", "%sSAVE\\GAME%02u%02u.BIN + CompareFileTime"),
    0x40ECD4: ("OptionMenu", "load|scrsize|keyboard|quit|option"),
    0x40FBE9: ("Timer_Begin", "Could not begin timer ..."),
    0x40FDC6: ("Entry2D", "Entrée 2D: n° de ZA (%u) pas valide..."),
    0x40FF77: ("Save_WriteGame", "%sSAVE\\GAME%02u%02u.BIN, Game save: create file failed..."),
    0x410153: ("Save_WriteGGame", "%sSAVE\\GGAME%u.BIN, Game save: create file failed..."),
    0x4105F3: ("Timer_End", "timeKillEvent + timeEndPeriod"),
    0x4122BB: ("MainWndProc", "DefWindowProcA; Could not re-init DirectDraw ..."),
    0x416650: ("Snd_Init", "DirectSound initialisation failed..."),
    0x4166F1: ("Snd_InitMovieBuffer", "Movie sound-buffer initialization failed..."),
    0x416D9F: ("Snd_CreateStatic", "Static Sound: could not create '%s'..."),
    0x416E7F: ("Wav_Open", "'%s': not a wav file..."),
    0x417084: ("Snd_Load", "%sDATA\\SOUND\\%s.APC / .WAV"),
    0x4176C6: ("Adpcm_StreamInit", "ADPCM stream initialization failed..."),
    0x41794B: ("Wav_LoadResource", "FindResourceA 'WAVE'"),
    0x4180C0: ("App_Init", "Could not retrieve registry informations..."),
    0x418416: ("Registry_Read", "SOFTWARE\\Cryo\\Mission Sunlight: Path, Target, Language, Install Level"),
    0x41861D: ("Users_CheckSessions", "'%s' previous session was not properly closed"),
    0x418C21: ("Accueil_WndProc", "ACCUEIL_BMP, BOUTONS_BMP, player's name"),
    0x419D22: ("Display_Flip", "Could not flip display:"),
    0x419F0E: ("LoadBoxAuberge", "LoadBoxAuberge => %s"),
    0x419FDE: ("LoadAnimsauberge", "LoadAnimsauberge::%s manque"),
    0x41AB80: ("SaveScreenTga", "D:/VANGOGH/TGA/%04d.TGA"),
    0x41AC86: ("SaveScreenBtm", "D:/VANGOGH/TGA/%04d.BTM"),
    0x41AD98: ("LoadTga", "LoadTga::Erreur ouverture %s"),
    0x41AF1C: ("LoadTga2", "LoadTga::Erreur ouverture %s"),
    0x41B6AB: ("LoadAnimscafe", "LoadAnimscafe::%s manque"),
    0x41C8A7: ("LoadAnimschambreb", "LoadAnimschambreb::%s manque"),
    0x41DCAD: ("LoadAnimschambrev", "LoadAnimschambrev::%s manque"),
    0x41E2B1: ("LoadAnimschamp", "LoadAnimschamp::%s manque"),
    0x41ED13: ("ReadPeintreIni", "\\PEINTRE.INI, PATH = %s"),
    0x4210B9: ("CheckObjectCount", "NbObjets > MAX_OBJETS_SCENE"),
    0x421E56: ("C_Monde::LoadScene", "C_Monde::LoadScene => %s"),
    0x421FCA: ("DebugInfo", "Pos => %d %d %d|Angle => %d %d %d|pick name => %s"),
    0x422869: ("Alloc3DMemory", "Memory3D => NULL"),
    0x4240F0: ("Cursor_Check", "Curseur->Buf => NULL"),
    0x42421B: ("LoadAnimsEglise", "LoadAnimsEglise::%s manque"),
    0x424978: ("LoadBoxHopiExt", "LoadBoxHopiExt => %s"),
    0x4249D6: ("LoadAnimsHopiExt", "LoadAnimsHopiExt::%s manque"),
    0x425420: ("LoadAnimshopiint", "LoadAnimshopiint::%s manque"),
    0x426BF8: ("LoadBoxJardin", "LoadBoxJardin => %s"),
    0x426CC9: ("LoadAnimsjardin", "LoadAnimsjardin::%s manque"),
    0x4278D1: ("LoadAnimsMaisonet", "LoadAnimsMaisonet::%s manque"),
    0x4286E2: ("LoadBoxMaisonj", "LoadBoxMaisonj => %s"),
    0x428832: ("LoadAnimsmaisonj", "LoadAnimsmaisonj::%s manque"),
    0x429813: ("LoadAnimsmangeurs", "LoadAnimsmangeurs::%s manque"),
    0x42AAB8: ("LoadBoxMusee", "LoadBoxMusee => %s"),
    0x42AC4A: ("LoadAnimsmusee", "LoadAnimsmusee::%s manque"),
    0x42CE08: ("LoadBoxPont", "LoadBoxPont => %s"),
    0x42CEC7: ("LoadAnimspont", "LoadAnimspont::%s manque"),
    0x42DCED: ("LoadAnimsterrasse", "LoadAnimsterrasse::%s manque"),
    0x42E630: ("VangoghError", "wvsprintfA + MessageBoxA 'Vangogh Erreur'"),
    0x42E6E0: ("OpenError3D", "Erreur ouverture %s|Pas assez de ram pour 3d"),
    0x42E85C: ("LoadSceneFile", "DATA\\SCENES_3D\\ + GetFileSize, ptrdata => NULL"),
    0x42EB21: ("App3D_InitPaths", "DATA\\GRAPHS_2D\\|DATA\\SCENES_3D\\|\\SCENES\\|SAVE\\"),
    0x42EF0F: ("Load3DGame", "%sSAVE\\GAME%04d.BIN + ReadFile"),
    0x42F111: ("Load3DGGame", "%sSAVE\\GGAME%d.BIN + ReadFile"),
    0x42FB5E: ("Timer3D_Begin", "Could not begin timer 3D ..."),
    0x42FBAA: ("Timer3D_End", "timeKillEvent + timeEndPeriod"),
    0x433680: ("Heap_Alloc", "Heap overflow"),
    0x4348C0: ("CheckHeader", "Type d'entete non valide !!!!"),
    0x435EC0: ("BadHandle", "Bad_Handle!"),
    0x4668C9: ("Adpcm_ErrorString", "ADPCMERR_*"),
    0x467380: ("Font_StyleName", "Regular|Italic|Bold|Bold Italic"),
    0x4709E0: ("m__purge", "> m__purge ()"),
    0x470A80: ("m__malloc", "> m__malloc (%u)"),
    0x470BA0: ("m__calloc", "> m__calloc (%u, %u)"),
    0x470E10: ("m__free", "> m__free (0x%08X)"),
    0x470EA0: ("m__defrag", "> m__defrag()"),
    0x4710E0: ("DD_Create", "DirectDrawCreate"),
    0x472410: ("DI_Create", "DirectInputCreateA"),
    0x472D40: ("DS_Create", "DirectSoundCreate"),
}

CRT_FILE = re.compile(r"(?:^|\|)([a-z_]+\.c)(?:\||$)")


def module_of(addr: int) -> str:
    mod = MODULES[0][1]
    for start, name in MODULES:
        if addr >= start:
            mod = name
    return mod


def build() -> None:
    rows = list(csv.DictReader((NOTES / "function-dump.tsv").open(encoding="utf-8"),
                               delimiter="\t", quoting=csv.QUOTE_NONE))
    out = []
    for r in rows:
        addr = int(r["address"], 16)
        name, why = NAMES.get(addr, ("", ""))
        mod = module_of(addr)
        m = CRT_FILE.search(r["strings"])
        if mod == "msvcrt" and m and not name:
            why = f"CRT source {m.group(1)}"
        out.append({"address": f"0x{addr:08x}", "module": mod, "name": name,
                    "ghidra": r["name"], "size": r["size"], "callers": r["callers"],
                    "evidence": why})
    with (NOTES / "function-map.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    per = {}
    for o in out:
        n, s, k = per.get(o["module"], (0, 0, 0))
        per[o["module"]] = (n + 1, s + int(o["size"]), k + bool(o["name"]))
    for mod, (n, s, k) in per.items():
        print(f"{mod:20} {n:4} functions {s:7} bytes {k:3} named")
    print(f"total {len(out)}, named {sum(bool(o['name']) for o in out)}")


def selftest() -> None:
    assert module_of(0x4022C0) == "game/puzzles"
    assert module_of(0x421E56) == "game3d/world"
    assert module_of(0x42AAB8) == "game3d/scenes"
    assert module_of(0x470A80) == "cryo/memory"
    assert module_of(0x476510) == "msvcrt"
    assert CRT_FILE.search("str != NULL|fclose.c").group(1) == "fclose.c"
    assert all(module_of(a) for a in NAMES)
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        build()
