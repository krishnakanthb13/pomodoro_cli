@echo off
title Pomodoro Reviewer
setlocal
cd /d "%~dp0"

if not exist "pomodoro.txt" (
    echo [ERROR] pomodoro.txt not found!
    echo Please ensure pomodoro.txt is in the same folder.
    pause
    exit /b
)

echo Starting Pomodoro Reviewer...
echo.

REM Open browser first (it will wait for server)
echo Opening browser...
start "" "http://localhost:8080/pomodoro_review.html"

echo Starting server on port 8080...
echo.

REM Try http-server (NPM), fallback to Python, then give error
where http-server >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Using http-server...
    cmd /c http-server -p 8080 -c-1
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] http-server not found, using Python fallback...
        python -m http.server 8080
    ) else (
        echo [ERROR] Neither http-server nor Python found!
        echo Please install http-server (npm install -g http-server) or Python.
        pause
    )
)

echo.
echo Server stopped. Press Enter to close this window.
pause > nul