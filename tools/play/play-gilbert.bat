@echo off
rem Play Gilbert in ScummVM like a normal user: updates C:\GilbertPlay to the latest
rem committed engine, then opens the ScummVM launcher (Add Game... the first time, on
rem games\gilbert\discs\cd\Program). Its settings and saves stay in C:\GilbertPlay.
C:\msys64\usr\bin\env.exe MSYSTEM=UCRT64 CHERE_INVOKING=1 C:\msys64\usr\bin\bash.exe -lc "bash '%~dp0build_play.sh' gilbert /c/scummvm-play-gilbert /c/GilbertPlay"
if errorlevel 1 (pause & exit /b 1)
start "" /D C:\GilbertPlay C:\GilbertPlay\scummvm.exe --config=C:\GilbertPlay\scummvm.ini
