r"""X3D's object lookup order for a unit scene, and which file wins a duplicate name.

Model (E-0530): `X3d_Load_Sdk_o3d` adds only the file's object 0 (its single root) to the
scene list, by prepending (`X3d_Scene_Add_Object`); children link to the end of their
parent's child list in file order (`FUN_10012920`). `X3d_Object_Add_Lod` unlinks a `lod=`
file's root from the scene list when the base object is a root and both roots have the same
welded flag (+0x40); otherwise the LOD root stays in the list. `X3d_Scene_Get_Object` walks
the list from its head (newest file first) and each tree depth first, self before children,
with a case-sensitive compare.

    python tools/object_order.py Data/U03/U33.X3D GeoSphere0 pedalegch
    python tools/object_order.py --selftest
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import o3d  # noqa: E402
import x3d  # noqa: E402
from common import default_root  # noqa: E402


def _resolve(base: Path, rel: str) -> Path:
    cur = base
    for part in rel.replace("\\", "/").split("/"):
        cur = next(p for p in cur.iterdir() if p.name.lower() == part.lower())
    return cur


def _preorder(objects: list) -> list:
    kids: dict = {}
    for o in objects:
        kids.setdefault(o["parent"], []).append(o["name"])
    out = []

    def walk(name):
        out.append(name)
        for k in kids.get(name, []):
            walk(k)
    walk(objects[0]["name"])
    return out


def scene_list(root: Path, script: Path) -> list:
    """[(file, [object names in lookup order])], head of the scene list first."""
    base = x3d.asset_dir(root, script)
    files = []  # load order
    for st in x3d.parse(script.read_bytes()):
        if st[0] not in ("object", "lod"):
            continue
        path = _resolve(base, st[1])
        doc = o3d.parse(path.read_bytes())
        if st[0] == "lod":
            last = files[-1][2]
            if last["objects"][0]["welded"] == doc["objects"][0]["welded"]:
                continue  # unlinked by X3d_Object_Add_Lod
        files.append((st[1], _preorder(doc["objects"]), doc))
    return [(f, names) for f, names, _ in reversed(files)]


def first_match(lst: list, name: str):
    for f, names in lst:
        if name in names:
            return f
    return None


def selftest() -> int:
    root = default_root()
    lst = scene_list(root, root / "U33" / "U33.x3d")
    # E-0421 names these duplicates; the later file must win.
    assert first_match(lst, "GeoSphere0").lower().endswith("coffre.o3d"), lst
    assert first_match(lst, "pedalegch").lower().endswith("u03.o3d")
    print("selftest ok")
    return 0


def main(argv: list) -> int:
    if argv[:1] == ["--selftest"]:
        return selftest()
    root = default_root()
    lst = scene_list(root, Path(argv[0]) if Path(argv[0]).exists() else root / argv[0])
    if len(argv) == 1:
        for f, names in lst:
            print(f, len(names))
    for name in argv[1:]:
        print(name, "->", first_match(lst, name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
