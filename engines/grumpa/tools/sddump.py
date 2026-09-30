"""Dump SafeDisc-decrypted Grumpa.exe from memory, with its imports rebuilt (Q-0001).

SafeDisc 2.60 decrypts the game's sections at run time (E-0003). This script starts the
game in the run folder through SafeDiscLoader2 (third_party/SafeDiscLoader2, built with
MSBuild: Release/version.dll + VersionInjector/Release/VersionInjector.exe; it emulates
secdrv.sys, which Windows 11 no longer loads), polls the process until `.text` differs
from the file and has stopped changing, suspends it, and then:

- reads the whole image;
- finds the game's own import descriptors (the header points at the stub's 12 imports;
  the game's are further on in `.rdata`, with the names of the redirected DLLs erased);
- names the IAT slots that can be named without running SafeDisc's code: slots left
  pointing at an API (named as the importing DLL exports it; Windows 11's kernel32
  forwards most of its exports to kernelbase and ntdll) and slots whose import name table
  survived. Slots pointing at a SafeDisc stub stay unnamed (`sd_<slot>`); their API is
  to be proved from how the game uses them;
- kills the process and SafeDisc's helper process.

Writes (build/ is gitignored; the dump is the original's code, not ours to publish):
  build/grumpa/Grumpa.dump.exe   PE in memory layout (raw offset = virtual address), an
                                 `.idata2` section with the rebuilt import directory
                                 (IAT slots stay where the code reads them), entry point
                                 = the MSVC start-up routine
  engines/grumpa/notes/iat.tsv   every IAT slot: DLL, how it was found, API name

    python engines/grumpa/tools/sddump.py            (run folder C:\\GrumpaRun)
    python engines/grumpa/tools/sddump.py --selftest
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import filecmp
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[3]
EXE = REPO / "games/grumpa/discs/cab/Profileshell/Grumpa.exe"
LOADER = REPO / "third_party/SafeDiscLoader2"
RUN = Path("C:/GrumpaRun")
OUT = REPO / "build/grumpa/Grumpa.dump.exe"
IAT_TSV = REPO / "engines/grumpa/notes/iat.tsv"
# MSVC 6 WinMainCRTStartup: push ebp; mov ebp,esp; push -1; push; push; mov eax,fs:[0]; ...; sub esp,58h
CRT_START = re.compile(rb"\x55\x8b\xec\x6a\xff\x68.{4}\x68.{4}\x64\xa1\0\0\0\0\x50\x64\x89\x25\0\0\0\0\x83\xec\x58", re.S)

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll")
k32.OpenProcess.restype = wt.HANDLE
k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
k32.CreateRemoteThread.restype = wt.HANDLE
k32.CreateRemoteThread.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                   ctypes.c_void_p, wt.DWORD, ctypes.c_void_p]
k32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.TerminateProcess.argtypes = [wt.HANDLE, wt.UINT]
psapi.EnumProcessModulesEx.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.DWORD]
psapi.GetModuleFileNameExW.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.LPWSTR, wt.DWORD]
ntdll.NtSuspendProcess.argtypes = [wt.HANDLE]
PROCESS_ALL_ACCESS = 0x1F0FFF
LIST_MODULES_32BIT = 1


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD), ("szExeFile", wt.WCHAR * 260)]


def find_pid(name: str) -> int | None:
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    e = PROCESSENTRY32W(dwSize=ctypes.sizeof(PROCESSENTRY32W))
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    pid = None
    while ok:
        if e.szExeFile.lower() == name.lower():
            pid = e.th32ProcessID
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return pid


def read(h, addr: int, size: int) -> bytes:
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t()
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(got)):
        raise OSError(ctypes.get_last_error(), f"ReadProcessMemory 0x{addr:x}+0x{size:x}")
    return buf.raw[:got.value]


def modules(h) -> dict[str, tuple[int, bytes]]:
    """Lower-case module name -> (base, image in memory layout), 32-bit modules only."""
    arr = (ctypes.c_uint64 * 1024)()
    need = wt.DWORD()
    psapi.EnumProcessModulesEx(h, arr, ctypes.sizeof(arr), ctypes.byref(need), LIST_MODULES_32BIT)
    out = {}
    for base in arr[:need.value // 8]:
        name = ctypes.create_unicode_buffer(260)
        psapi.GetModuleFileNameExW(h, ctypes.c_void_p(base), name, 260)
        head = read(h, base, 0x1000)
        size = struct.unpack_from("<I", head, struct.unpack_from("<I", head, 0x3C)[0] + 0x50)[0]
        try:
            out[Path(name.value).name.lower()] = (base, read(h, base, size))
        except OSError:
            pass
    return out


def exports(image: bytes, base: int) -> tuple[dict[int, str], dict[str, str]]:
    """(export address -> name, forwarded name -> 'dll.target') of a module image."""
    e_lfanew = struct.unpack_from("<I", image, 0x3C)[0]
    rva, size = struct.unpack_from("<II", image, e_lfanew + 0x78)
    if not rva:
        return {}, {}
    ordbase, nfun, nname, afun, aname, aord = struct.unpack_from("<6I", image, rva + 0x10)
    funcs = struct.unpack_from(f"<{nfun}I", image, afun)
    names = {}
    for i in range(nname):
        nrva = struct.unpack_from("<I", image, aname + 4 * i)[0]
        names[struct.unpack_from("<H", image, aord + 2 * i)[0]] = cstr(image, nrva)
    addrs, fwd = {}, {}
    for i, f in enumerate(funcs):
        name = names.get(i, f"#{ordbase + i}")
        if rva <= f < rva + size:
            fwd[name] = cstr(image, f)
        elif f:
            addrs.setdefault(base + f, name)
    return addrs, fwd


def cstr(b: bytes, off: int) -> str:
    return b[off:b.index(b"\0", off)].decode("latin1")


def namer(mods: dict[str, tuple[int, bytes]]):
    """name(dll, address) -> the name under which `dll` exports that address, following
    forwarders (api-ms-* sets are looked up in kernelbase and ntdll)."""
    exp = {m: exports(img, base) for m, (base, img) in mods.items()}
    by_name = {m: {n: a for a, n in e[0].items()} for m, e in exp.items()}
    cache = {}

    def target(dll: str, name: str, depth: int = 0) -> int | None:
        """Address `dll`!`name` ends at, through forwarders (kernel32 -> api set ->
        kernelbase -> ntdll is two hops)."""
        a = by_name.get(dll, {}).get(name)
        if a is not None or depth > 4:
            return a
        fw = exp.get(dll, ({}, {}))[1].get(name)
        if fw is None:
            return None
        tdll, _, tname = fw.rpartition(".")
        cands = [tdll.lower() + ".dll"]
        if tdll.lower().startswith(("api-ms-", "ext-ms-")):
            cands = ["kernelbase.dll", "ntdll.dll", "user32.dll", "gdi32.dll", "advapi32.dll"]
        for c in cands:
            if (a := target(c, tname, depth + 1)) is not None:
                return a
        return None

    def table(dll: str) -> dict[int, str]:
        if dll not in cache:
            addrs, fwd = exp.get(dll, ({}, {}))
            t = dict(addrs)
            for name in fwd:
                if (a := target(dll, name)) is not None:
                    t.setdefault(a, name)
            cache[dll] = t
        return cache[dll]

    def everywhere(addr: int) -> str:
        for m, (addrs, _) in exp.items():
            if addr in addrs:
                return f"{m}!{addrs[addr]}"
        return "?"

    return lambda dll, addr: table(dll.lower()).get(addr), everywhere


def import_descriptors(image: bytes, pe, skip_header: bool = True) -> list[tuple[str, int, int]]:
    """The game's import descriptors: (dll, OriginalFirstThunk, FirstThunk). The longest
    run of descriptors in .rdata whose names end in .dll and whose thunks lie in .rdata,
    by default not the one the header points at (the SafeDisc stub's)."""
    rd = next(s for s in pe.sections if s.Name.startswith(b".rdata"))
    lo, hi = rd.VirtualAddress, rd.VirtualAddress + rd.Misc_VirtualSize
    header = pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress

    def desc(o):
        oft, _, _, name, ft = struct.unpack_from("<5I", image, o)
        if not (lo <= name < hi and lo <= ft < hi):
            return None
        n = image[name:name + 64].split(b"\0")[0]
        return (n.decode("latin1"), oft, ft) if n.lower().endswith(b".dll") else None

    best = []
    for o in range(lo, hi - 20, 4):
        if skip_header and o == header:
            continue
        run = []
        while (d := desc(o + 20 * len(run))) is not None:
            run.append(d)
        if len(run) > len(best) and image[o + 20 * len(run):o + 20 * len(run) + 20] == bytes(20):
            best = run
    return best


def children(pid: int) -> list[int]:
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    e = PROCESSENTRY32W(dwSize=ctypes.sizeof(PROCESSENTRY32W))
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    out = []
    while ok:
        if e.th32ParentProcessID == pid:
            out.append(e.th32ProcessID)
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return out


def rebuild(image: bytes, groups: list[tuple[str, int, list[str]]], oep: int | None) -> bytes:
    """Memory-layout PE with an `.idata2` section holding a fresh import directory for
    `groups` [(dll, FirstThunk RVA, names)]; the IAT slots get their hint/name RVAs, as in
    an unbound file, so a loader or disassembler binds them by name."""
    img = bytearray(image)
    pe = pefile.PE(data=bytes(img), fast_load=True)
    oh, salign = pe.OPTIONAL_HEADER, pe.OPTIONAL_HEADER.SectionAlignment
    va = oh.SizeOfImage
    ndesc = (len(groups) + 1) * 20
    sec = bytearray(ndesc)
    ints = []
    for dll, ft, names in groups:
        ints.append(len(sec))
        sec += bytes(4 * (len(names) + 1))
    for gi, (dll, ft, names) in enumerate(groups):
        for k, n in enumerate(names):
            hn = va + len(sec)
            sec += b"\0\0" + n.encode() + b"\0"
            sec += b"\0" * (len(sec) & 1)
            struct.pack_into("<I", sec, ints[gi] + 4 * k, hn)
            struct.pack_into("<I", img, ft + 4 * k, hn)
        dname = va + len(sec)
        sec += dll.encode() + b"\0"
        sec += b"\0" * (len(sec) & 1)
        struct.pack_into("<5I", sec, 20 * gi, va + ints[gi], 0, 0, dname, ft)
    size = (len(sec) + salign - 1) & -salign
    img += bytes(va - len(img)) + sec + bytes(size - len(sec))
    # section header after the last one
    last = pe.sections[-1].get_file_offset() + 40
    struct.pack_into("<8s6IHHI", img, last, b".idata2", len(sec), va, size, va, 0, 0, 0, 0, 0xC0000040)
    struct.pack_into("<H", img, pe.FILE_HEADER.get_file_offset() + 2, len(pe.sections) + 1)
    o = oh.get_file_offset()
    struct.pack_into("<I", img, o + 0x38, va + size)  # SizeOfImage
    struct.pack_into("<II", img, o + 0x60 + 8 * 1, va, ndesc)  # import directory
    struct.pack_into("<II", img, o + 0x60 + 8 * 12, 0, 0)  # IAT directory: none, slots are in .rdata
    struct.pack_into("<II", img, o + 0x60 + 8 * 11, 0, 0)  # bound imports: none
    if oep is not None:
        struct.pack_into("<I", img, o + 0x10, oep)
    return memory_pe(bytes(img))


def memory_pe(image: bytes) -> bytes:
    """Headers rewritten so the image in memory layout loads as a file: every section's
    raw data at its virtual address, file alignment = section alignment."""
    img = bytearray(image)
    pe = pefile.PE(data=bytes(img), fast_load=True)
    salign = pe.OPTIONAL_HEADER.SectionAlignment
    struct.pack_into("<I", img, pe.OPTIONAL_HEADER.get_file_offset() + 0x24, salign)  # FileAlignment
    for s in pe.sections:
        vsize = (max(s.Misc_VirtualSize, s.SizeOfRawData) + salign - 1) & -salign
        struct.pack_into("<II", img, s.get_file_offset() + 0x10, vsize, s.VirtualAddress)
    return bytes(img)


def dump(timeout: float) -> None:
    pe = pefile.PE(str(EXE), fast_load=True)
    base, size = pe.OPTIONAL_HEADER.ImageBase, pe.OPTIONAL_HEADER.SizeOfImage
    text = next(s for s in pe.sections if s.Name.startswith(b".text"))
    file_text = text.get_data()[:text.Misc_VirtualSize]
    RUN.mkdir(exist_ok=True)
    for src in (EXE, LOADER / "Release/version.dll", LOADER / "VersionInjector/Release/VersionInjector.exe"):
        if not (RUN / src.name).exists() or not filecmp.cmp(src, RUN / src.name, shallow=False):
            shutil.copy2(src, RUN / src.name)
    if find_pid("Grumpa.exe"):
        sys.exit("a Grumpa.exe is already running")
    subprocess.Popen([str(RUN / "VersionInjector.exe"), str(RUN / "Grumpa.exe")], cwd=RUN)
    t0 = time.time()
    pid = None
    while pid is None and time.time() - t0 < timeout:
        pid = find_pid("Grumpa.exe")
    if pid is None:
        sys.exit("Grumpa.exe did not start")
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    try:
        last = None
        while True:
            if time.time() - t0 > timeout:
                sys.exit("timed out: .text never decrypted")
            try:
                cur = read(h, base + text.VirtualAddress, len(file_text))
            except OSError:
                cur = None
            if cur and cur != file_text and cur == last:
                break
            last = cur
            time.sleep(0.02)
        ntdll.NtSuspendProcess(h)
        print(f"decrypted after {time.time() - t0:.2f} s; suspended")
        image = read(h, base, size)
        mods = modules(h)
        in_module = lambda a: any(b <= a < b + len(img) for b, img in mods.values())
        descs = import_descriptors(image, pe)
        slots = []  # (dll, slot VA, value, INT name)
        for dll, oft, ft in descs:
            k = 0
            while v := struct.unpack_from("<I", image, ft + 4 * k)[0]:
                intname = None
                if oft:
                    hn = struct.unpack_from("<I", image, oft + 4 * k)[0]
                    intname = cstr(image, hn + 2) if hn and not hn & 0x80000000 else None
                slots.append((dll, base + ft + 4 * k, v, intname))
                k += 1
        stubs = {s for _, s, v, _ in slots if not in_module(v)}
    finally:
        helpers = children(pid)
        k32.TerminateProcess(h, 1)
        k32.CloseHandle(h)
        for c in helpers:  # SafeDisc's helper process (~f39a36.tmp)
            hc = k32.OpenProcess(PROCESS_ALL_ACCESS, False, c)
            k32.TerminateProcess(hc, 1)
            k32.CloseHandle(hc)
    name_in, everywhere = namer(mods)
    rows, groups, bad = [], {}, 0
    for dll, slot, v, intname in slots:
        how = "stub" if slot in stubs else "direct"
        addr = v
        name = None if slot in stubs else name_in(dll, addr)
        if intname and name and intname != name:
            sys.exit(f"slot 0x{slot:08x}: INT says {intname}, process says {name}")
        name = name or intname
        bad += name is None
        rows.append(f"0x{slot:08x}\t{dll}\t{how}\t0x{addr:08x}\t{everywhere(addr)}\t{name or '?'}\t{intname or ''}\n")
        groups.setdefault((dll, next(ft for d, _, ft in descs if d == dll)), []).append(name or f"sd_{slot:08x}")
    IAT_TSV.write_text("slot\tdll\thow\taddress\tprocess_export\tname\tint_name\n" + "".join(rows), encoding="utf-8")
    oeps = [m.start() for m in CRT_START.finditer(image, text.VirtualAddress, text.VirtualAddress + len(file_text))]
    oep = oeps[0] if len(oeps) == 1 else None
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(rebuild(image, [(d, ft, n) for (d, ft), n in groups.items()], oep))
    print(f"wrote {OUT}: {len(descs)} DLLs, {len(slots)} slots ({len(stubs)} SafeDisc stubs), "
          f"{bad} unnamed; entry {'0x%08x' % (base + oep) if oep is not None else 'unchanged'} "
          f"({len(oeps)} start-up candidates)")


def selftest() -> None:
    # A plain program of the same corpus, mapped the way the loader maps it.
    p = pefile.PE(str(REPO / "games/grumpa/discs/cab/Profileshell/GrumpaConfig.exe"))
    image = p.get_memory_mapped_image()
    q = pefile.PE(data=memory_pe(image))
    for a, b in zip(p.sections, q.sections):
        assert q.get_data(b.VirtualAddress, a.Misc_VirtualSize) == p.get_data(a.VirtualAddress, a.Misc_VirtualSize)
        assert b.PointerToRawData == b.VirtualAddress
    # Its import descriptors found by the scan, and rebuilt under their own names.
    descs = import_descriptors(image, p, skip_header=False)
    assert [d for d, _, _ in descs] == [e.dll.decode() for e in p.DIRECTORY_ENTRY_IMPORT], descs
    groups = [(e.dll.decode(), e.struct.FirstThunk, [i.name.decode() for i in e.imports if i.name])
              for e in p.DIRECTORY_ENTRY_IMPORT if all(i.name for i in e.imports)]
    r = pefile.PE(data=rebuild(image, groups, None))
    got = {(e.dll.decode(), i.address - r.OPTIONAL_HEADER.ImageBase, i.name.decode())
           for e in r.DIRECTORY_ENTRY_IMPORT for i in e.imports}
    want = {(d, ft + 4 * k, n) for d, ft, ns in groups for k, n in enumerate(ns)}
    assert got == want
    # Exports of the 32-bit kernel32, forwarders included.
    k = pefile.PE(r"C:\Windows\SysWOW64\kernel32.dll")
    addrs, fwd = exports(k.get_memory_mapped_image(), 0x10000000)
    want = next(s for s in k.DIRECTORY_ENTRY_EXPORT.symbols if s.name == b"GetTickCount")
    assert addrs[0x10000000 + want.address] == "GetTickCount" and "." in fwd["HeapAlloc"]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--timeout", type=float, default=60)
    a = ap.parse_args()
    selftest() if a.selftest else dump(a.timeout)
