@echo off
rem Started by Windows Task Scheduler (task "Game Reimplementations nightly", daily 04:30); see tools/nightly.sh.
cd /d "%~dp0.."
"C:\Program Files\Git\bin\bash.exe" -lc "bash tools/nightly.sh" >> logs\nightly-task.log 2>&1
