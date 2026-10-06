# /// script
# requires-python = ">=3.11"
# dependencies = ["frida>=17"]
# ///
"""Trace function calls in a running original game, to a file you grep afterwards.

Hooks addresses in a 32- or 64-bit Windows process (spawned or attached) and writes one
tab-separated line per call: time (ms), thread, hook, the first argument words (stack
arguments, plus ECX for __thiscall), the return value. Nothing lands in the conversation
but the summary, so a trace of thousands of calls costs a few lines of context.

    uv run tools/trace/trace.py --spawn C:/MonetRun/MissionMonet.exe --cwd C:/MonetRun \\
        --hook MissionMonet.exe!0x1a970=XScene::Load --hook kernel32.dll!CreateFileA \\
        --args 4 --seconds 60 --out engines/x3d/traces/xscene-load.tsv
    uv run tools/trace/trace.py --attach GRUMPA.EXE --hook GRUMPA.EXE!0x1fde0 --out t.tsv

A hook is `module!export`, `module!0xRVA` (offset from the module base, as Ghidra shows
it minus the image base) or `0xVA`, optionally `=label`. `--max` caps calls per hook.
Traces of the originals stay local (traces/ logs are gitignored); summarise what they show
in EVIDENCE.md.
"""

from __future__ import annotations

import argparse
import sys
import time

AGENT = r"""
const hooks = %HOOKS%, nargs = %NARGS%, max = %MAX%;
const counts = {};
function resolve(h) {
  if (h.module === null) return ptr(h.where);
  const m = Process.findModuleByName(h.module);
  if (m === null) return null;
  return h.where.startsWith('0x') ? m.base.add(ptr(h.where)) : m.findExportByName(h.where);
}
function install() {
  for (const h of hooks) {
    if (h.done) continue;
    const at = resolve(h);
    if (at === null) continue;
    h.done = true;
    counts[h.label] = 0;
    Interceptor.attach(at, {
      onEnter(args) {
        if (++counts[h.label] > max) { this.skip = true; return; }
        const words = [];
        const sp = this.context.esp !== undefined ? this.context.esp : this.context.rsp;
        if (Process.pointerSize === 4) {
          for (let i = 1; i <= nargs; i++) words.push(sp.add(4 * i).readU32().toString(16));
          words.push('ecx=' + this.context.ecx.toString(16));
        } else {
          for (let i = 0; i < nargs; i++) words.push(args[i].toString(16));
        }
        this.line = [Date.now(), this.threadId, h.label, words.join(' ')];
      },
      onLeave(ret) {
        if (this.skip) return;
        this.line.push(ret.toString(16));
        send(this.line.join('\t'));
      }
    });
    send('#hooked ' + h.label + ' at ' + at);
  }
}
install();
setInterval(install, 500);  // modules loaded later (DLLs, unpacked code)
"""


def parse_hook(spec: str) -> dict:
    where, _, label = spec.partition("=")
    module, sep, sym = where.rpartition("!")
    if not sep:
        return {"module": None, "where": where, "label": label or where}
    return {"module": module, "where": sym, "label": label or where}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--spawn", help="exe to start")
    target.add_argument("--attach", help="process name or pid to attach to")
    ap.add_argument("--cwd", help="working directory for --spawn")
    ap.add_argument("--hook", action="append", required=True, type=parse_hook)
    ap.add_argument("--args", type=int, default=4, help="argument words to log")
    ap.add_argument("--max", type=int, default=10000, help="calls logged per hook")
    ap.add_argument("--seconds", type=float, default=30, help="trace this long, then detach")
    ap.add_argument("--out", required=True)
    ap.add_argument("--kill", action="store_true", help="end a spawned process when done")
    a = ap.parse_args()

    import json

    import frida

    device = frida.get_local_device()
    pid = device.spawn([a.spawn], cwd=a.cwd) if a.spawn else (int(a.attach) if a.attach.isdigit() else a.attach)
    session = device.attach(pid)
    lines, hooked = [], []

    def on_message(msg, _data):
        if msg["type"] == "send":
            (hooked if msg["payload"].startswith("#") else lines).append(msg["payload"])
        elif msg["type"] == "error":
            print("agent error:", msg.get("description"), file=sys.stderr)

    src = (AGENT.replace("%HOOKS%", json.dumps(a.hook)).replace("%NARGS%", str(a.args))
           .replace("%MAX%", str(a.max)))
    script = session.create_script(src)
    script.on("message", on_message)
    script.load()
    if a.spawn:
        device.resume(pid)
    try:
        end = time.time() + a.seconds
        while time.time() < end:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    try:
        session.detach()
    except frida.InvalidOperationError:
        pass  # the process ended first
    if a.spawn and a.kill:
        try:
            device.kill(pid)
        except frida.ProcessNotFoundError:
            pass

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("ms\tthread\thook\targs\treturn\n")
        f.write("\n".join(lines) + ("\n" if lines else ""))
    per = {}
    for l in lines:
        per[l.split("\t")[2]] = per.get(l.split("\t")[2], 0) + 1
    print(f"{len(lines)} calls -> {a.out}; " + ", ".join(f"{k} {v}" for k, v in per.items()))
    for h in hooked:
        print(" ", h[1:])
    missing = {h["label"] for h in a.hook} - {h.split()[1] for h in hooked}
    if missing:
        print("  never hooked (module not loaded or no such export):", ", ".join(sorted(missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
