# Pomodoro Timer Launcher - PowerShell Edition
# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Pomodoro Timer Launcher"
Set-Location -Path $PSScriptRoot

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║           🍅 POMODORO TIMER LAUNCHER 🍅                    ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Select your Pomodoro preset:" -ForegroundColor White
    Write-Host ""
    # Intensity colors based on work time: longer work = more intense color
    Write-Host "  [1] Deep Flow Session    - 90M work │ 10M notes │ 25M break │ x2  ~ aspirational / advanced" -ForegroundColor Magenta
    Write-Host "  [2] Deep Work Session    - 50M work │ 10M notes │ 15M break │ x3  ~ deeper cognitive work" -ForegroundColor Red
    Write-Host "  [3] Extended Focus       - 45M work │ 10M notes │ 10M break │ x4  ~ sweet spot for many" -ForegroundColor DarkYellow
    Write-Host "  [4] Study Session        - 30M work │ 05M notes │ 10M break │ x5  ~ learning heavy days" -ForegroundColor Green
    Write-Host ""
    Write-Host "  [5] Classic Pomodoro     - 25M work │ 05M notes │ 05M break │ x4  ~ default / everyday" -ForegroundColor Cyan
    Write-Host "  [6] Quick Sprint         - 15M work │ 03M notes │ 05M break │ x6  ~ warm-up / light tasks" -ForegroundColor Yellow
    Write-Host "  [7] Ultra Sprint         - 10M work │ 02M notes │ 03M break │ x8  ~ momentum killer" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [8] Custom Settings      - Enter your own timings" -ForegroundColor Gray
    Write-Host "  [9] Test Mode            - 01M work │ 01M notes │ 01M break │ x2  ~ testing" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [R] Review Sessions      - View session history" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [0] Exit" -ForegroundColor Red
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

function Start-PomodoroSession {
    param(
        [int]$Work,
        [int]$Notes,
        [int]$Break,
        [int]$Cycles,
        [string]$Chime = "",
        [switch]$SelectChime
    )
    
    $args = @("-w", $Work, "-n", $Notes, "-b", $Break, "-c", $Cycles)
    
    if ($SelectChime) {
        $args += "--select-chime"
    } elseif ($Chime) {
        $args += @("--chime", $Chime)
    }
    
    python pomodoro.py @args
}

function Start-CustomSession {
    Clear-Host
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   CUSTOM POMODORO SETTINGS" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    $work = Read-Host "Work duration (minutes)"
    $note = Read-Host "Note-taking duration (minutes)"
    $break = Read-Host "Break duration (minutes)"
    $cycles = Read-Host "Number of cycles"
    
    Write-Host ""
    Write-Host "Starting custom session..." -ForegroundColor Green
    Start-PomodoroSession -Work $work -Notes $note -Break $break -Cycles $cycles -SelectChime
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (0-9)"
    
    switch ($choice) {
        "1" {
            Clear-Host
            Write-Host "Starting Deep Flow Session..." -ForegroundColor Magenta
            Start-PomodoroSession -Work 90 -Notes 10 -Break 25 -Cycles 2 -Chime "mixkit-melodical-flute-music.wav"
        }
        "2" {
            Clear-Host
            Write-Host "Starting Deep Work Session..." -ForegroundColor Red
            Start-PomodoroSession -Work 50 -Notes 10 -Break 15 -Cycles 3 -Chime "mixkit-melodical-flute-music.wav"
        }
        "3" {
            Clear-Host
            Write-Host "Starting Extended Focus..." -ForegroundColor DarkYellow
            Start-PomodoroSession -Work 45 -Notes 10 -Break 10 -Cycles 4 -Chime "mixkit-melodical-flute-music.wav"
        }
        "4" {
            Clear-Host
            Write-Host "Starting Study Session..." -ForegroundColor Green
            Start-PomodoroSession -Work 30 -Notes 5 -Break 10 -Cycles 5 -Chime "mixkit-melodical-flute-music.wav"
        }
        "5" {
            Clear-Host
            Write-Host "Starting Classic After Study..." -ForegroundColor Cyan
            Start-PomodoroSession -Work 25 -Notes 5 -Break 5 -Cycles 4 -Chime "mixkit-arabian-mystery-harp.wav"
        }
        "6" {
            Clear-Host
            Write-Host "Starting Quick Sprint..." -ForegroundColor Yellow
            Start-PomodoroSession -Work 15 -Notes 3 -Break 5 -Cycles 6 -Chime "mixkit-arabian-mystery-harp.wav"
        }
        "7" {
            Clear-Host
            Write-Host "Starting Ultra Sprint..." -ForegroundColor Yellow
            Start-PomodoroSession -Work 10 -Notes 2 -Break 3 -Cycles 8 -Chime "mixkit-arabian-mystery-harp.wav"
        }
        "8" {
            Start-CustomSession
        }
        "9" {
            Clear-Host
            Write-Host "Starting Test Mode (1 min each)..." -ForegroundColor Gray
            Start-PomodoroSession -Work 1 -Notes 1 -Break 1 -Cycles 2 -SelectChime
        }
        "R" {
            Clear-Host
            & cmd /c "pomodoro_review.bat"
        }
        "0" {
            Clear-Host
            Write-Host ""
            Write-Host "Thank you for using Pomodoro Timer! 🍅" -ForegroundColor Cyan
            Write-Host ""
            Start-Sleep -Seconds 2
            exit
        }
        default {
            Write-Host "Invalid choice! Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
    
    if ($choice -ne "0" -and $choice -ne "R") {
        Write-Host ""
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        $again = Read-Host "Run another session? (Y/N)"
        
        if ($again -notmatch "^[Yy]") {
            Clear-Host
            Write-Host ""
            Write-Host "Thank you for using Pomodoro Timer! 🍅" -ForegroundColor Cyan
            Write-Host ""
            Start-Sleep -Seconds 2
            exit
        }
    }
} while ($true)