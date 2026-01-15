# Pomodoro Reviewer - PowerShell Edition
# Launcher for the web-based Pomodoro Reviewer
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Pomodoro Reviewer"
Set-Location -Path $PSScriptRoot

$htmlFile = "pomodoro_review.html"
$notesFile = "pomodoro.txt"
$port = 8080

$lineChar = [char]0x2550
$separator = $lineChar.ToString() * 60

Write-Host $separator -ForegroundColor Cyan
Write-Host "           POMODORO REVIEWER SERVER" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $htmlFile)) {
    Write-Host "[ERROR] $htmlFile not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

if (-not (Test-Path $notesFile)) {
    Write-Host "[ERROR] $notesFile not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "Starting server and browser..." -ForegroundColor Cyan

# Launch browser in background after 2s delay
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8080/pomodoro_review.html"
} | Out-Null

Write-Host "[INFO] Attempting to start server on port 8080..." -ForegroundColor Gray
Write-Host "[TIP] If the browser loads too fast, just REFRESH (F5)." -ForegroundColor Yellow
Write-Host ""

# Detect server method
$httpServer = Get-Command http-server -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue
$python3 = Get-Command python3 -ErrorAction SilentlyContinue

if ($null -ne $httpServer) {
    Write-Host "[OK] Using http-server (Node.js)" -ForegroundColor Green
    & http-server -p $port -c-1
} elseif ($null -ne $python) {
    Write-Host "[OK] Using Python server" -ForegroundColor Green
    python -m http.server $port
} elseif ($null -ne $python3) {
    Write-Host "[OK] Using Python3 server" -ForegroundColor Green
    python3 -m http.server $port
} else {
    Write-Host "[ERROR] Neither http-server nor Python found!" -ForegroundColor Red
    Write-Host "Please install Python (python.org) or Node.js (nodejs.org)."
    Read-Host "Press Enter to exit"
}

Write-Host ""
Write-Host "Server stopped."
Read-Host "Press Enter to close this window"
