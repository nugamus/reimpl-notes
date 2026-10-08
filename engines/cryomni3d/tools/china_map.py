#!/usr/bin/env python3
"""China (CHINE.EXE): dump the map screen's data tables (E-1150..E-1152).

- "you are here" tables: 0x452040 (14 records of 0x108 bytes keyed by a 3-letter place
  prefix) and 0x452fb8 (full place names, ends at an empty name); x at +0x100, y at
  +0x104, in petiplan coordinates (screen x = x + 373).
- hot spots 0x45af38: 95 records of 9 dwords: top, left, bottom, right (granplan
  coordinates), label text (filled at run time), LABELS.TXT key, type (0 travel,
  8 documentation, 7 label only), pointer to {place name, view angle float}, unk_8.
- the `ico_bat` building list (0x402590): label key and the small-map point it scrolls to.

Usage: china_map.py [--selftest | --cpp OUT.h]
  --cpp writes the tables as the engine's china/map_tables.h (regenerate, never edit).
"""
from __future__ import annotations

import struct
import sys

from china_places import EXE, Exe

YAH3, YAH3_END, YAHFULL = 0x452040, 0x452EB0, 0x452FB8
HOT, HOT_END = 0x45AF38, 0x45BC94  # label init 0x402920 stops at 0x45bca4 (d4)
# ico_bat list (0x402590): key address, x, y (screen coordinates on petiplan)
BAT = [(0x45BDD4, 0x1FA, 0xFC), (0x45BDE0, 0x208, 0x9D), (0x45BDC4, 0x1D4, 0x87),
       (0x45BDBC, 0x1FA, 0x5F), (0x45BDB8, 0x205, 0x4F), (0x45BD84, 0x21B, 100),
       (0x45BDC0, 0x1FA, 0x8C), (0x45BDDC, 0x1E7, 0x96), (0x45BDC8, 0x1FA, 0x9D),
       (0x45BDE4, 0x1D6, 0xA5)]
SPECIAL = (0x45BE00, 0x45BDE8, 0x45BDF8)


def tables(e: Exe):
    short = [(e.cstr(a), e.u32(a + 0x100), e.u32(a + 0x104))
             for a in range(YAH3, YAH3_END, 0x108)]
    full, a = [], YAHFULL
    while e.cstr(a):
        full.append((e.cstr(a), e.u32(a + 0x100), e.u32(a + 0x104)))
        a += 0x108
    hot = []
    for a in range(HOT, HOT_END, 36):
        d = [e.u32(a + 4 * k) for k in range(9)]
        tgt = None
        if d[7]:
            ang = struct.unpack("<f", struct.pack("<I", e.u32(d[7] + 4)))[0]
            tgt = (e.cstr(e.u32(d[7])), round(ang, 3))
        hot.append((d[0], d[1], d[2], d[3], e.cstr(d[5]), d[6], tgt, d[8]))
    bat = [(e.cstr(k), x, y) for k, x, y in BAT]
    return short, full, hot, bat, [e.cstr(s) for s in SPECIAL]


GPL = """/* ScummVM - Graphic Adventure Engine
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
"""


def cpp(short, full, hot, bat) -> str:
    out = [GPL, "// China's map tables (spec/china-interface.md Map, E-1150..E-1152), included by map.cpp.",
           "// Generated from the game's data tables; regenerate rather than edit.", "",
           "#ifndef CRYOMNI3D_CHINA_MAP_TABLES_H", "#define CRYOMNI3D_CHINA_MAP_TABLES_H", "",
           "namespace CryOmni3D {", "namespace China {", "",
           "// You are here: place name prefix (3 letters) or full name, point on petiplan",
           "struct MapPoint {", "	const char *place;", "	int16 x, y;", "};", "",
           "static const MapPoint kMapPrefixPoints[] = {"]
    out += ['	{ "%s", %d, %d },' % r for r in short]
    out += ["};", "", "static const MapPoint kMapPlacePoints[] = {"]
    out += ['	{ "%s", %d, %d },' % r for r in full]
    out += ["};", "", "// Hot spots on granplan (inclusive rectangles); type 0 travel, 7 label, 8 documentation",
            "struct MapSpot {", "	int16 top, left, bottom, right;", "	const char *key;", "	byte type;",
            "	const char *place; // type 0: the travel target", "	float alpha;", "};", "",
            "static const MapSpot kMapSpots[] = {"]
    for h in hot:
        place, ang = (('"%s"' % h[6][0]), "%.3ff" % h[6][1]) if h[6] else ("nullptr", "0.f")
        out.append('	{ %d, %d, %d, %d, "%s", %d, %s, %s },' % (*h[:6], place, ang))
    out += ["};", "", "// The building list (ico_bat), bottom row first: label key, point on the screen",
            "static const MapPoint kMapBuildings[] = {"]
    out += ['	{ "%s", %d, %d },' % b for b in bat]
    out += ["};", "", "} // End of namespace China", "} // End of namespace CryOmni3D", "", "#endif", ""]
    return "\n".join(out)


def main() -> int:
    short, full, hot, bat, special = tables(Exe(EXE.read_bytes()))
    if "--cpp" in sys.argv:
        path = sys.argv[sys.argv.index("--cpp") + 1]
        open(path, "w", encoding="utf-8", newline="\n").write(cpp(short, full, hot, bat))
        print(f"wrote {path}: {len(short)} prefixes, {len(full)} places, {len(hot)} spots, {len(bat)} buildings")
        return 0
    if "--selftest" in sys.argv:
        assert len(short) == 14 and short[0] == ("shs", 132, 205)
        assert len(full) == 122 and full[0] == ("pne310", 96, 105)
        assert full[-1] == ("cth550", 105, 175)
        assert len(hot) == 95 and hot[0][:6] == (416, 295, 433, 305, "NWF", 0)
        assert hot[0][6] == ("cgc110", 3.13)
        assert sum(h[5] == 0 for h in hot) == 13 and {h[5] for h in hot} == {0, 7, 8}
        assert all((h[5] == 0) == (h[6] is not None) for h in hot)
        assert special == ["cpc600", "pdc010", "ctp330"]
        assert [b[0] for b in bat][:3] == ["SHS", "ESP", "PNE"]
        print("selftest ok: 14 short, 122 full, 95 hot spots, 10 buildings")
        return 0
    print("# you are here, 3-letter prefix (x on petiplan, y)")
    for r in short:
        print("%s\t%d\t%d" % r)
    print("# you are here, full name (overrides the prefix match)")
    for r in full:
        print("%s\t%d\t%d" % r)
    print("# hot spots: top left bottom right key type target(angle) unk_8")
    for h in hot:
        t = "%s(%.3f)" % h[6] if h[6] else "-"
        print("%d\t%d\t%d\t%d\t%s\t%d\t%s\t%d" % (*h[:6], t, h[7]))
    print("# ico_bat list (bottom row first): key x y")
    for b in bat:
        print("%s\t%d\t%d" % b)
    print("# special travel targets:", " ".join(special))
    return 0


if __name__ == "__main__":
    sys.exit(main())
