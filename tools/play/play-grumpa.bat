@echo off
rem Play Grumpa in ScummVM like a normal user: updates C:\GrumpaPlay to the latest committed
rem engine, then opens the ScummVM launcher (Add Game... the first time, on the installed game
rem folder games\grumpa\discs\cab, which has Actors\Characters.abi + Items.abi for detection).
rem Its settings and saves stay in C:\GrumpaPlay. The engine is still in development, so the
rem "unsupported game" warning is turned off in C:\GrumpaPlay\scummvm.ini.
C:\msys64\usr\bin\env.exe MSYSTEM=UCRT64 CHERE_INVOKING=1 C:\msys64\usr\bin\bash.exe -lc "bash '%~dp0build_play.sh' grumpa /c/scummvm-play-grumpa /c/GrumpaPlay && (grep -q enable_unsupported_game_warning /c/GrumpaPlay/scummvm.ini || sed -i '/^\[scummvm\]/a enable_unsupported_game_warning=false' /c/GrumpaPlay/scummvm.ini)"
if errorlevel 1 (pause & exit /b 1)
start "" /D C:\GrumpaPlay C:\GrumpaPlay\scummvm.exe --config=C:\GrumpaPlay\scummvm.ini
