@echo off
rem Shared by the play-*.bat files: _play.bat <play folder, e.g. C:\GilbertPlay>.
rem Updates the folder to the latest committed engine (only when monet moved), then opens the
rem ScummVM launcher for that folder. Pick the game and press Start; to change engine
rem enhancements, select the game and use Edit Game before starting. Add Game... the first
rem time. Settings and saves stay in that folder.
C:\msys64\usr\bin\env.exe MSYSTEM=UCRT64 CHERE_INVOKING=1 C:\msys64\usr\bin\bash.exe -lc "bash '%~dp0build_play.sh' $(cygpath -u '%~1')"
if errorlevel 1 (pause & exit /b 1)
start "" /D "%~1" "%~1\scummvm.exe" --config="%~1\scummvm.ini"
