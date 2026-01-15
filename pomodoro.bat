@echo off
chcp 65001 >nul
title Pomodoro Timer Launcher
cd /d "%~dp0"
REM color 0A

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           🍅 POMODORO TIMER LAUNCHER 🍅                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo  Select your Pomodoro preset:
echo.
echo  [1] Deep Flow Session    - 90M work │ 10M notes │ 25M break │ x2  ~ aspirational / advanced
echo  [2] Deep Work Session    - 50M work │ 10M notes │ 15M break │ x3  ~ deeper cognitive work
echo  [3] Extended Focus       - 45M work │ 10M notes │ 10M break │ x4  ~ sweet spot for many
echo  [4] Study Session        - 30M work │ 05M notes │ 10M break │ x5  ~ learning heavy days
echo.
echo  [5] Classic Pomodoro     - 25M work │ 05M notes │ 05M break │ x4  ~ default / everyday
echo  [6] Quick Sprint         - 15M work │ 03M notes │ 05M break │ x6  ~ warm-up / light tasks
echo  [7] Ultra Sprint         - 10M work │ 02M notes │ 03M break │ x8  ~ momentum killer
echo.
echo  [8] Custom Settings      - Enter your own timings
echo  [9] Test Mode            - 01M work │ 01M notes │ 01M break │ x2  ~ testing
echo.
echo  [R] Review Sessions      - View session history
echo.
echo  [0] Exit
echo.
echo ════════════════════════════════════════════════════════════
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto DEEPFLOW
if "%choice%"=="2" goto DEEPWORK
if "%choice%"=="3" goto EXTENDED
if "%choice%"=="4" goto STUDY
if "%choice%"=="5" goto CLASSIC
if "%choice%"=="6" goto QUICK
if "%choice%"=="7" goto ULTRA
if "%choice%"=="8" goto CUSTOM
if "%choice%"=="9" goto TEST
if /i "%choice%"=="R" goto REVIEW
if "%choice%"=="0" goto EXIT

echo Invalid choice! Please try again.
timeout /t 2 >nul
goto MENU

:DEEPFLOW
cls
echo Starting Deep Flow Session...
python pomodoro.py -w 90 -n 10 -b 25 -c 2 --chime mixkit-melodical-flute-music.wav
goto END

:DEEPWORK
cls
echo Starting Deep Work Session...
python pomodoro.py -w 50 -n 10 -b 15 -c 3 --chime mixkit-melodical-flute-music.wav
goto END

:EXTENDED
cls
echo Starting Extended Focus...
python pomodoro.py -w 45 -n 10 -b 10 -c 4 --chime mixkit-melodical-flute-music.wav
goto END

:STUDY
cls
echo Starting Study Session...
python pomodoro.py -w 30 -n 5 -b 10 -c 5 --chime mixkit-melodical-flute-music.wav
goto END

:CLASSIC
cls
echo Starting Classic After Study...
python pomodoro.py -w 25 -n 5 -b 5 -c 4 --chime mixkit-arabian-mystery-harp.wav
goto END

:QUICK
cls
echo Starting Quick Sprint...
python pomodoro.py -w 15 -n 3 -b 5 -c 6 --chime mixkit-arabian-mystery-harp.wav
goto END

:ULTRA
cls
echo Starting Ultra Sprint...
python pomodoro.py -w 10 -n 2 -b 3 -c 8 --chime mixkit-arabian-mystery-harp.wav
goto END

:CUSTOM
cls
echo.
echo ═══════════════════════════════════════
echo   CUSTOM POMODORO SETTINGS
echo ═══════════════════════════════════════
echo.
set /p work="Work duration (minutes): "
set /p note="Note-taking duration (minutes): "
set /p break="Break duration (minutes): "
set /p cycles="Number of cycles: "
echo.
echo Starting custom session...
python pomodoro.py -w %work% -n %note% -b %break% -c %cycles% --select-chime
goto END

:TEST
cls
echo Starting Test Mode (1 min each)...
python pomodoro.py -w 1 -n 1 -b 1 -c 2 --select-chime
goto END

:REVIEW
cls
call pomodoro_review.bat
goto MENU

:END
echo.
echo ════════════════════════════════════════════════════════════
echo.
set /p again="Run another session? (Y/N): "
if /i "%again%"=="Y" goto MENU
if /i "%again%"=="YES" goto MENU

:EXIT
cls
echo.
echo Thank you for using Pomodoro Timer! 🍅
REM echo Your notes are saved in notes.txt
REM echo Your notes are saved in pomodoro.txt
echo.
timeout /t 5 >nul
exit