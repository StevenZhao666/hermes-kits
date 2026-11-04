@echo off
cd /d "%~dp0"
set "MAIN="
for %%f in ("%~dp0*.bat") do (
    findstr /m /c:"::B64:" "%%f" >nul 2>&1 && set "MAIN=%%f"
)
if not defined MAIN (
    echo   Cannot find the main script in this folder.
    pause
    exit /b 1
)
call "%MAIN%" /restore
