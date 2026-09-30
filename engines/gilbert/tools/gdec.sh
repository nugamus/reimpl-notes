#!/bin/sh
# usage: engines/gilbert/tools/gdec.sh PROGRAM addr...   decompile into engines/gilbert/notes/decomp
p=$1; shift
python -m pyghidra.ghidra_launch --install-dir 'C:\ghidra' ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Gilbert/gilbert-import -process $p -noanalysis -readOnly -scriptPath tools/ghidra/scripts -postScript decompile_one.py engines/gilbert/notes/decomp "$@" 2>&1 | grep -E ' @ 0x|no function|failed'
