@echo off
rem Shared by the play-*.bat files: _play.bat <play folder, e.g. C:\GilbertPlay>.
rem Updates the folder to the latest committed engine (only when monet moved), then starts
rem the game added there straight away (the launcher the first time, for Add Game...).
rem Its settings and saves stay in that folder.
C:\msys64\usr\bin\env.exe MSYSTEM=UCRT64 CHERE_INVOKING=1 C:\msys64\usr\bin\bash.exe -lc "bash '%~dp0build_play.sh' $(cygpath -u '%~1')"
if errorlevel 1 (pause & exit /b 1)
set TARGET=
set /p TARGET=<"%~1\.play-target"
start "" /D "%~1" "%~1\scummvm.exe" --config="%~1\scummvm.ini" %TARGET%
