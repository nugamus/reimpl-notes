# /// script
# requires-python = ">=3.11"
# dependencies = ["capstone"]
# ///
"""Write the engine's China place procedures from the place logic spec.

The spec is games/china/docs/places-logic.md, which china_places.py generates from
CHINE.EXE (E-0710..E-0712); this tool reads the same statement trees (`china_places.py
--json`) and writes them as C++ calls on the engine's place API
(engines/cryomni3d/docs/spec/china-zones.md), one function per procedure, plus the
procedure list in list order and the variable and object numbers (sav.py --tables, E-0208).

    uv run engines/cryomni3d/tools/china_gen_places.py C:/scummvm-dev/cryomni3d/engines/cryomni3d/china/places.cpp
    uv run engines/cryomni3d/tools/china_gen_places.py --selftest
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

HEADER = """/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

// China's place procedures: one function per place, in the game's list order. Each runs
// its entry part once on arrival, then its event part every frame.
// Generated from the place logic specification; regenerate rather than edit.

#include "cryomni3d/china/engine.h"

namespace CryOmni3D {
namespace China {

"""

FOOTER = """} // End of namespace China
} // End of namespace CryOmni3D
"""


def ident(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def cstr(s) -> str:
    return "nullptr" if s is None else json.dumps(s)


def num(v) -> str:
    if isinstance(v, float):
        r = repr(v)
        return r if "." in r or "e" in r else r + ".0"
    return str(v)


class Gen:
    def __init__(self, variables: dict[str, int], objects: dict[str, int]):
        self.vars, self.objs = variables, objects
        self.used_vars: set[str] = set()
        self.used_objs: set[str] = set()

    def var(self, name: str) -> str:
        if name not in self.vars:
            m = re.fullmatch(r"var(\d+)", name)  # unnamed variables print by number
            if not m:
                raise KeyError(f"unknown variable {name}")
            self.vars[name] = int(m[1])
        self.used_vars.add(name)
        return f"kV_{ident(name)}"

    def obj(self, name) -> str:
        if isinstance(name, int):
            return str(name)
        if name not in self.objs:
            m = re.fullmatch(r"obj(\d+)", name)
            if not m:
                raise KeyError(f"unknown object {name}")
            self.objs[name] = int(m[1])
        self.used_objs.add(name)
        return f"kO_{ident(name)}"

    def expr(self, v) -> str:
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, (int, float)):
            return num(v)
        if isinstance(v, str):
            return cstr(v)
        if "var" in v:
            return f"(int32)g.var({self.var(v['var'])})"
        if "zone" in v:
            return "g.clickedZone()"
        if "mem" in v:
            return f"g.mem({v['mem']})"
        if "cond" in v:
            return f"({self.cond(v['cond'])} ? 1 : 0)"
        if "op" in v:
            return f"({self.expr(v['lhs'])} {v['op']} {self.expr(v['rhs'])})"
        if "call" in v:
            return self.call_expr(v["call"], v.get("args", []), v.get("addr"))
        if "reg" in v:  # a register kept across calls (only `fight`, set by a `let`)
            return "g.mem(0)"
        if "stackaddr" in v:
            return "0"
        raise ValueError(f"expression {v}")

    def call_expr(self, fn: str, a: list, addr) -> str:
        if fn == "zone_default":
            return "(g.zoneHandler() ? 1 : 0)"
        if fn == "obj_is_cursor":
            return f"(g.heldObject() == {self.obj(a[0])} ? 1 : 0)"
        if fn == "obj_not_initial":
            return f"(g.objectState({self.obj(a[0])}) != 0 ? 1 : 0)"
        if fn == "obj_is_destroyed":
            return f"(g.objectState({self.obj(a[0])}) == 3 ? 1 : 0)"
        if fn == "puzzle":
            return f"g.puzzle({', '.join(self.expr(x) for x in a)})"
        if fn == "obj_in_inventory":
            return f"(g.objectState({self.obj(a[0])}) == 2 ? 1 : 0)"
        if fn == "key_down":
            return f"(g.keyDown({self.expr(a[0])}) ? 1 : 0)"
        if fn == "time_ms":
            return "(int32)g.timeMs()"
        return f"g.unknownCall({addr or fn}{''.join(', ' + self.expr(x) for x in a)})"

    def cond(self, c) -> str:
        if "and" in c:
            return " && ".join(f"({self.cond(x)})" for x in c["and"])
        if "or" in c:
            return " || ".join(f"({self.cond(x)})" for x in c["or"])
        if "not" in c:
            return f"!({self.cond(c['not'])})"
        if "bit" in c:
            test = f"({self.expr(c['lhs'])} & {c['bit']})"
            return f"{test} != 0" if c.get("set", True) else f"{test} == 0"
        if "cmp" in c:
            return f"{self.expr(c['lhs'])} {c['cmp']} {self.expr(c['rhs'])}"
        raise ValueError(f"condition {c}")

    def call(self, fn: str, a: list, addr) -> str:
        def rect(r):
            return f"{r[0]}, {r[1]}, {r[2]}, {r[3]}"
        e = self.expr
        simple = {
            "zones_reset": "g.zonesReset()",
            "zone_default": "g.zoneHandler()",
            "sound_stop": "g.soundStop()",
            "screen_effect": "g.screenEffect()",
        }
        if fn in simple:
            return simple[fn]
        if fn == "zone_goto":
            return f"g.zoneGo({rect(a[0])}, {e(a[1])}, {cstr(a[2])}, {e(a[3])}, {num(float(a[4]))}, {num(float(a[5]))})"
        if fn == "zone_type2":
            return f"g.zoneLook({rect(a[0])}, {e(a[1])}, {cstr(a[2])}, {e(a[3])})"
        if fn == "zone_take":
            return f"g.zoneTake({rect(a[0])}, {e(a[1])}, {cstr(a[2])})"
        if fn == "zone_type6":
            return f"g.zoneUse({rect(a[0])}, {e(a[1])})"
        if fn == "zone_label":
            return f"g.zoneLabel({rect(a[0])}, {e(a[1])}, {cstr(a[2])})"
        if fn == "zone_doc":
            return f"g.zoneDoc({rect(a[0])}, {e(a[1])}, {cstr(a[2])})"
        if fn == "zone_type9":
            return f"g.zoneTalk({rect(a[0])}, {e(a[1])})"
        if fn in ("zone_enable", "zone_disable"):
            return f"g.{'zoneEnable' if fn == 'zone_enable' else 'zoneDisable'}({e(a[0])})"
        if fn in ("warp", "image", "goto", "minutes_add", "sound_queue", "sound_wait", "dialogue"):
            m = {"warp": "warp", "image": "image", "goto": "gotoPlace", "minutes_add": "minutesAdd",
                 "sound_queue": "soundQueue", "sound_wait": "soundPlayWait", "dialogue": "voice"}[fn]
            return f"g.{m}({cstr(a[0])})"
        if fn == "video_hns":
            return f"g.video({cstr(a[0])})"
        if fn == "set_angles":
            return f"g.setAngles({num(float(a[0]))}, {num(float(a[1]))})"
        if fn == "var_set":
            return f"g.setVar({self.var(a[0])}, {e(a[1])})"
        if fn == "sync_video":
            return f"g.dialogue({cstr(a[0])}, {cstr(a[1])}, {cstr(a[2])})"
        if fn in ("obj_to_inventory", "obj_to_cursor", "obj_destroy"):
            m = {"obj_to_inventory": "objectToInventory", "obj_to_cursor": "objectToCursor",
                 "obj_destroy": "objectDestroy"}[fn]
            return f"g.{m}({self.obj(a[0])})"
        if fn == "interface_screen":
            return "g.interfaceScreen()"
        if fn == "epilogue":
            return "g.epilogue()"
        if fn in ("obj_set_label", "obj_set_examine"):
            m = "objectSetLabel" if fn == "obj_set_label" else "objectSetExamine"
            return f"g.{m}({self.obj(a[0])}, {cstr(a[1])})"
        return self.call_expr(fn, a, addr)

    def stmts(self, st: list, depth: int) -> list[str]:
        pad = "\t" * depth
        out = []
        for s in st:
            op = s["op"]
            if op == "call":
                out.append(f"{pad}{self.call(s['fn'], s['args'], s.get('addr'))};")
            elif op == "return":
                out.append(f"{pad}return;")
            elif op == "store":
                out.append(f"{pad}g.setMem({s['addr']}, {self.expr(s['value'])});")
            elif op == "let":
                out.append(f"{pad}g.setMem(0, {self.expr(s['value'])}); // {s['reg']}")
            elif op == "if":
                out.append(f"{pad}if ({self.cond(s['cond'])}) {{")
                out += self.stmts(s["then"], depth + 1)
                if s.get("else"):
                    out.append(f"{pad}}} else {{")
                    out += self.stmts(s["else"], depth + 1)
                out.append(f"{pad}}}")
            else:
                raise ValueError(f"statement {s}")
        return out

    def place(self, p: dict) -> list[str]:
        out = [f"// {p['name']} ({p['addr']})",
               f"static void place_{ident(p['name'])}(CryOmni3DEngine_China &g, bool entry) {{",
               "\tif (entry) {"]
        out += self.stmts(p["entry"], 2)
        out.append("\t}")
        out += self.stmts(p["event"], 1)
        out.append("}")
        return out


def load_tables() -> tuple[dict[str, int], dict[str, int]]:
    text = subprocess.run([sys.executable, str(HERE / "parsers" / "sav.py"), "--tables"],
                          capture_output=True, text=True, check=True).stdout
    variables, objects = {}, {}
    for line in text.splitlines():
        m = re.match(r"(var|obj)\s+(\d+)\s+(.+?)\s*$", line)
        if m:
            (variables if m[1] == "var" else objects).setdefault(m[3], int(m[2]))
    return variables, objects


def generate(places: list[dict], variables: dict[str, int], objects: dict[str, int]) -> str:
    g = Gen(variables, objects)
    bodies = []
    for p in places:
        bodies += g.place(p) + [""]
    lines = ["// Game variables (the variable table's order, E-0208)", "enum {"]
    lines += [f"\tkV_{ident(n)} = {variables[n]}," for n in sorted(g.used_vars, key=lambda n: variables[n])]
    lines += ["};", "", "// Objects (E-0905)", "enum {"]
    lines += [f"\tkO_{ident(n)} = {objects[n]}," for n in sorted(g.used_objs, key=lambda n: objects[n])]
    lines += ["};", ""]
    table = ["const CryOmni3DEngine_China::PlaceDef CryOmni3DEngine_China::kPlaces[] = {"]
    table += [f"\t{{ {cstr(p['name'])}, &place_{ident(p['name'])} }}," for p in places]
    table += ["\t{ nullptr, nullptr }", "};", ""]
    return HEADER + "\n".join(lines + bodies + table) + "\n" + FOOTER


def selftest() -> None:
    g = Gen({"CHAPITRE": 1, "crans": 7}, {"TOURNEVIS": 20})
    assert g.cond({"cmp": "==", "lhs": {"var": "CHAPITRE"}, "rhs": 1}) == "(int32)g.var(kV_CHAPITRE) == 1"
    assert g.cond({"bit": 1, "lhs": {"var": "crans"}, "set": False}) == "((int32)g.var(kV_crans) & 1) == 0"
    assert g.call("zone_goto", [[1, 2, 3, 4], 0, "pne150", 0, -1.0, -1.0], None) == \
        'g.zoneGo(1, 2, 3, 4, 0, "pne150", 0, -1.0, -1.0)'
    p = {"name": "x", "addr": "0x1", "entry": [{"op": "call", "fn": "warp", "args": ["x"]}, {"op": "return"}],
         "event": [{"op": "if", "cond": {"cmp": "!=", "lhs": {"call": "zone_default", "args": []}, "rhs": 0},
                    "then": [{"op": "return"}], "else": []}]}
    src = "\n".join(g.place(p))
    assert 'g.warp("x");' in src and "if ((g.zoneHandler() ? 1 : 0) != 0) {" in src
    print("china_gen_places selftest ok")


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        selftest()
        return 0
    if len(argv) != 1:
        print(__doc__)
        return 2
    data = subprocess.run([sys.executable, str(HERE / "china_places.py"), "--json"],
                          capture_output=True, text=True, check=True).stdout
    places = json.loads(data)
    variables, objects = load_tables()
    Path(argv[0]).write_text(generate(places, variables, objects), encoding="utf-8", newline="\n")
    print(f"{len(places)} places -> {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
