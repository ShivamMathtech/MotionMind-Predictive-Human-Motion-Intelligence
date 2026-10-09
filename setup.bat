@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Install Python 3.12 with the Python Launcher, then run setup.bat again.
 pause
 exit /b 1
)
py -3.12 -c "import sys" >nul 2>nul
if errorlevel 1 (
 py -3.11 scripts\setup.py
) else (
 py -3.12 scripts\setup.py
)
if errorlevel 1 (
 echo Setup failed. Read the message above and docs\TROUBLESHOOTING.md.
 pause
 exit /b 1
)
call start.bat
