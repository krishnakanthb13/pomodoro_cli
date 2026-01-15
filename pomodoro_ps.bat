@echo off
chcp 65001 >nul
title Pomodoro
REM Batch file to launch the Pomodoro PowerShell script
REM This bypasses execution policy restrictions for this script only

powershell.exe -ExecutionPolicy Bypass -File "%~dp0pomodoro.ps1"