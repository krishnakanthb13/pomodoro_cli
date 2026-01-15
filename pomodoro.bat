@echo off
chcp 65001 >nul
title Pomodoro Timer Launcher
cd /d "%~dp0"

REM Define ESC character for colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"

:MENU
cls
echo.
echo  %ESC%[96m╔════════════════════════════════════════════════════════════╗%ESC%[0m
echo  %ESC%[96m║           🍅 %ESC%[1mPOMODORO TIMER LAUNCHER%ESC%[0m%ESC%[96m 🍅                    ║%ESC%[0m
echo  %ESC%[96m╚════════════════════════════════════════════════════════════╝%ESC%[0m
echo.
echo  %ESC%[37mSelect your Pomodoro preset:%ESC%[0m
echo.
echo  %ESC%[95m[1] Deep Flow Session    - 90M work │ 10M notes │ 25M break │ x2  ~ aspirational%ESC%[0m
echo  %ESC%[91m[2] Deep Work Session    - 50M work │ 10M notes │ 15M break │ x3  ~ deeper work%ESC%[0m
echo  %ESC%[33m[3] Extended Focus       - 45M work │ 10M notes │ 10M break │ x4  ~ sweet spot%ESC%[0m
echo  %ESC%[92m[4] Study Session        - 30M work │ 05M notes │ 10M break │ x5  ~ learning%ESC%[0m
echo.
echo  %ESC%[96m[5] Classic Pomodoro     - 25M work │ 05M notes │ 05M break │ x4  ~ default%ESC%[0m
echo  %ESC%[33m[6] Quick Sprint         - 15M work │ 03M notes │ 05M break │ x6  ~ warm-up%ESC%[0m
echo  %ESC%[33m[7] Ultra Sprint         - 10M work │ 02M notes │ 03M break │ x8  ~ momentum%ESC%[0m
echo.
echo  %ESC%[90m[8] Custom Settings      - Enter your own timings%ESC%[0m
echo  %ESC%[90m[9] Test Mode            - 01M work │ 01M notes │ 01M break │ x2  ~ testing%ESC%[0m
echo.
echo  %ESC%[36m[R] Review Sessions      - View session history%ESC%[0m
echo.
echo  %ESC%[31m[0] Exit%ESC%[0m
echo.
echo  %ESC%[96m════════════════════════════════════════════════════════════%ESC%[0m
echo.

set "choice="
set /p choice="%ESC%[37mEnter your choice (0-9/R): %ESC%[0m"

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
echo  %ESC%[95mStarting Deep Flow Session...%ESC%[0m
python pomodoro.py -w 90 -n 10 -b 25 -c 2 --chime mixkit-melodical-flute-music.wav
goto END

:DEEPWORK
cls
echo  %ESC%[91mStarting Deep Work Session...%ESC%[0m
python pomodoro.py -w 50 -n 10 -b 15 -c 3 --chime mixkit-melodical-flute-music.wav
goto END

:EXTENDED
cls
echo  %ESC%[33mStarting Extended Focus...%ESC%[0m
python pomodoro.py -w 45 -n 10 -b 10 -c 4 --chime mixkit-melodical-flute-music.wav
goto END

:STUDY
cls
echo  %ESC%[92mStarting Study Session...%ESC%[0m
python pomodoro.py -w 30 -n 5 -b 10 -c 5 --chime mixkit-melodical-flute-music.wav
goto END

:CLASSIC
cls
echo  %ESC%[96mStarting Classic Pomodoro...%ESC%[0m
python pomodoro.py -w 25 -n 5 -b 5 -c 4 --chime mixkit-arabian-mystery-harp.wav
goto END

:QUICK
cls
echo  %ESC%[33mStarting Quick Sprint...%ESC%[0m
python pomodoro.py -w 15 -n 3 -b 5 -c 6 --chime mixkit-arabian-mystery-harp.wav
goto END

:ULTRA
cls
echo  %ESC%[33mStarting Ultra Sprint...%ESC%[0m
python pomodoro.py -w 10 -n 2 -b 3 -c 8 --chime mixkit-arabian-mystery-harp.wav
goto END

:CUSTOM
cls
echo.
echo  %ESC%[96m═══════════════════════════════════════%ESC%[0m
echo    %ESC%[1mCUSTOM POMODORO SETTINGS%ESC%[0m
echo  %ESC%[96m═══════════════════════════════════════%ESC%[0m
echo.
set /p work="%ESC%[37mWork duration (minutes): %ESC%[0m"
set /p note="%ESC%[37mNote-taking duration (minutes): %ESC%[0m"
set /p break="%ESC%[37mBreak duration (minutes): %ESC%[0m"
set /p cycles="%ESC%[37mNumber of cycles: %ESC%[0m"
echo.
echo  %ESC%[92mStarting custom session...%ESC%[0m
python pomodoro.py -w %work% -n %note% -b %break% -c %cycles% --select-chime
goto END

:TEST
cls
echo  %ESC%[90mStarting Test Mode (1 min each)...%ESC%[0m
python pomodoro.py -w 1 -n 1 -b 1 -c 2 --select-chime
goto END

:REVIEW
cls
call pomodoro_review.bat
goto MENU

:END
echo.
echo  %ESC%[96m════════════════════════════════════════════════════════════%ESC%[0m
echo.
set /p again="%ESC%[37mRun another session? (Y/N): %ESC%[0m"
if /i "%again%"=="Y" goto MENU
if /i "%again%"=="YES" goto MENU

:EXIT
cls
echo.
echo  %ESC%[96mThank you for using Pomodoro Timer! 🍅%ESC%[0m
echo.
timeout /t 5 >nul
exit