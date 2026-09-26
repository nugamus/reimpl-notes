@echo off
rem Play Monet in ScummVM like a normal user: updates C:\MonetPlay to the latest
rem committed engine, then opens the ScummVM launcher (Add Game... the first time).
rem Its settings and saves stay in C:\MonetPlay, apart from the development runs.
C:\msys64\usr\bin\env.exe MSYSTEM=UCRT64 CHERE_INVOKING=1 C:\msys64\usr\bin\bash.exe -lc "bash '%~dp0build_play.sh'"
if errorlevel 1 (pause & exit /b 1)
start "" /D C:\MonetPlay C:\MonetPlay\scummvm.exe --config=C:\MonetPlay\scummvm.ini
