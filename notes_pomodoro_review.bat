@echo off
title Notes + Pomodoro Reviewer
setlocal
cd /d "%~dp0"

:menu
cls
echo ==========================================
echo           REVIEWER LAUNCHER
echo ==========================================
echo    1. Notes Review (Port 8081)
echo    2. Pomodoro Review (Port 8080)
echo    0. Exit
echo ==========================================
set /p choice=Select an option (0-2): 

if "%choice%"=="1" goto notes
if "%choice%"=="2" goto pomodoro
if "%choice%"=="0" goto end
goto menu

:notes
cls
echo Starting Notes Reviewer...
if not exist "notes.txt" (
    echo [ERROR] notes.txt not found!
    echo Please ensure notes.txt is in the same folder.
    pause
    goto menu
)
echo.

REM Open browser first (it will wait for server)
echo Opening browser...
start "" "http://localhost:8081/notes_review.html"

echo Starting http-server on port 8081...
echo.
echo Server is running. Press Ctrl+C to stop the server.
echo.

REM Run http-server in a sub-shell - Ctrl+C will terminate only the server
cmd /c http-server -p 8081 -c-1

echo.
echo Server stopped. Press Enter to return to menu.
pause > nul
goto menu

:pomodoro
cls
echo Starting Pomodoro Reviewer...
if not exist "pomodoro.txt" (
    echo [ERROR] pomodoro.txt not found!
    echo Please ensure pomodoro.txt is in the same folder.
    pause
    goto menu
)
echo.

REM Open browser first (it will wait for server)
echo Opening browser...
start "" "http://localhost:8080/pomodoro_review.html"

echo Starting http-server on port 8080...
echo.
echo Server is running. Press Ctrl+C to stop the server.
echo.

REM Run http-server in a sub-shell - Ctrl+C will terminate only the server
cmd /c http-server -p 8080 -c-1

echo.
echo Server stopped. Press Enter to return to menu.
pause > nul
goto menu

:end
exit /b
