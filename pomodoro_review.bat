@echo off
chcp 65001 >nul
title Pomodoro Reviewer
setlocal
cd /d "%~dp0"

echo ════════════════════════════════════════════════════════════
echo            POMODORO REVIEWER SERVER
echo ════════════════════════════════════════════════════════════
echo.

if not exist "pomodoro_review.html" (
    echo [ERROR] pomodoro_review.html not found!
    echo Please make sure all project files are in this folder.
    pause
    exit /b
)

if not exist "pomodoro.txt" (
    echo [ERROR] pomodoro.txt not found!
    echo No history found to review.
    pause
    exit /b
)

echo Starting server and browser...
echo.

REM Launch a background task to wait for the port to be active
REM This ensures the server starts first
start /b powershell -noprofile -command "$client = New-Object System.Net.Sockets.TcpClient; $maxRetries = 20; $retryCount = 0; $connected = $false; while (-not $connected -and $retryCount -lt $maxRetries) { try { $client.Connect('localhost', 8080); $connected = $true; $client.Close() } catch { Start-Sleep -Milliseconds 500; $retryCount++ } }; if ($connected) { Start-Process 'http://localhost:8080/pomodoro_review.html' }"

echo [INFO] Attempting to start server on port 8080...
echo [TIP] If the browser loads too fast, just REFRESH (F5).
echo.

REM Detect and run server
where http-server >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using http-server (Node.js)
    call http-server -p 8080 -c-1
    goto SERVER_DONE
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using Python server
    python -m http.server 8080
    goto SERVER_DONE
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using Python3 server
    python3 -m http.server 8080
    goto SERVER_DONE
)

echo.
echo [ERROR] No server engine found!
echo Please install Python (python.org) or Node.js (nodejs.org).
echo.
pause
exit /b

:SERVER_DONE
echo.
echo Server has been stopped.
pause