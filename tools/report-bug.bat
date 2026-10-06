@echo off
rem Desktop shortcut "Report a game bug": gathers the play folder's newest screenshot, save,
rem recording and log, then opens a filled-in GitHub issue (tools/report_bug.py).
cd /d "%~dp0.."
python tools\report_bug.py %*
if errorlevel 1 pause
