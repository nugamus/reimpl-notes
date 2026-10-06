# Getting names into Ghidra

Thousands of `FUN_` functions are the main cost of reverse engineering. Name in bulk
first, then read only what is left, in order of how much it is called.

1. **Compiler spec at import**: Delphi and C++ Builder use `borlanddelphi`/`__register`
   (EAX, EDX, ECX), as Gilbert's `GILBERT.EXE`; MSVC uses the default.
2. **Library code**: Ghidra's Function ID (on by default in analysis) names the C runtime,
   STL and MFC from the bundled `vsOlder`..`vs2019` databases. MSVC links the libraries as
   one block after the game's objects: `tools/coverage.py <engine>` tags unnamed functions
   in that block as `lib?` and lists the game's unknown functions by caller count.
3. **Classes from RTTI** (MSVC with /GR): Ghidra's `RecoverClassesFromRTTIScript.java`
   (headless `-postScript`, back up the project first). It found nothing in Grumpa's dump
   (RTTI off); try it on every new MSVC game anyway, it costs ten seconds.
4. **Delphi VMTs**: class names, method tables and published fields come from the VMTs;
   `engines/gilbert/tools/delphi_vmt.py` reads them. IDR (Interactive Delphi
   Reconstructor) does the same interactively and exports a map Ghidra can import.
5. **Asserts with source paths** (`D:\MissionD\Source\XScene.cpp`, debug runtimes):
   `tools/ghidra/scripts/assert_namer.py` names each function after its file and line, which
   also gives the original source layout (Monet).
6. **Error strings naming their method** (`aApplication::AddRot -> ...`, `CFXScene::Load:
   Failed to ...`): `find_str_funcs.py` and `ring_string_namer.py` name the function that
   references each one (Ring, Grumpa).
7. **Vtables**: `ring_vtables.py`, `actor_vtables.py` list them; one class per vtable, its
   slots name the virtual methods once one is known.
8. **Between programs of one engine** (two editions, a sequel): the Ghidra MCP's
   `get_bulk_function_hashes`, `bulk_fuzzy_match` and `merge_program_documentation` carry
   names and comments over.

Then `decompile_all.py` (with the new names) and `coverage.py` for the work list.
