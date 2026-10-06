@echo off
rem Runs the ScummVM x3d engine build (see CLAUDE.md, Tooling).
rem Usage: run-engine.bat            game from C:\MonetRun
rem        run-engine.bat V:/        game from the CD
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
set "GAMEDIR=%~1"
if "%GAMEDIR%"=="" set "GAMEDIR=C:/MonetRun"
"C:\scummvm\scummvm.exe" --config="%~dp0scummvm.ini" -p "%GAMEDIR%" monet
