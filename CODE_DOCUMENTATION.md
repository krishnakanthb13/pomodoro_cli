# Pomodoro CLI - Technical Documentation

## Overview

This project is a multi-platform CLI Pomodoro timer designed for high productivity, featuring interruptions handling, seamless note-taking, and detailed session reviews. It includes:

- **Core Timer Logic (`pomodoro.py`)**: A Python-based timer that manages Work, Note, and Break cycles, plays audio chimes, and handles concurrent note-taking via threads.
- **Launchers**: Native scripts for Windows (`.bat`, `.ps1`) and Unix-like (`.sh`) systems to provide easier entry points and preset configurations.
- **Review System**: A local HTML/React web application (`pomodoro_review.html`) served via simple HTTP servers to visualize session data and generate AI summaries using Google Gemini.

## Project Features

- **Timer Engine**: Accurate countdown, phase management, and visual terminal handling.
- **Goal Setting**: Intention setting prompts before cycles to align focus.
- **Journaling**: Asynchronous, non-blocking input queue allowing notes to be typed without pausing the timer.
- **Audio Chimes**: Context-aware sounds for phase completion (Work vs Break).
- **Persistence**: Human-readable log format (`pomodoro.txt`) that enables portability and simple parsing.
- **Review Dashboard**: React-based visualization with Date grouping and Calendar view.
- **AI Summarization**: Integration with Google Gemini API to generate daily summaries from your raw notes.
- **Cross-Platform**: Full support for Windows (CMD/PowerShell), Linux (Bash), and macOS.

## File Structure

```
├── pomodoro.py            # Main application logic (Python)
├── pomodoro.bat           # Windows Command Prompt launcher
├── pomodoro.ps1           # Windows PowerShell launcher
├── pomodoro.sh            # Linux/macOS Bash launcher
├── pomodoro.txt           # Flat-file database for storing session logs and notes
├── pomodoro_review.html   # Single-page React app for reviewing history
├── pomodoro_review.tsx    # Source code for the UI (reference/development)
├── pomodoro_review.bat    # Windows launcher for the review server
├── pomodoro_review.ps1    # PowerShell launcher for the review server
├── pomodoro_review.sh     # Linux/macOS launcher for the review server
├── requirements.txt       # Python dependencies (pygame)
├── LICENSE                # GPL v3 License
└── *.wav                  # Audio assets for chimes
```

## Architecture

### 1. The Timer (`pomodoro.py`)
- **Threading**: Uses a daemon thread `listen_for_notes` to capture keyboard input asynchronously while the main thread updates the timer display.
- **Input Handling**: 
    - Windows: Uses `msvcrt` for non-blocking key reads.
    - Unix: Uses `select` and `sys.stdin` to achieve similar non-blocking behavior.
- **State Management**: Tracks current phase (Work/Journal/Break) and handles transitions automatically.
- **Data Persistence**: Appends all events (Goal setting, Phases, Notes) to `pomodoro.txt` with timestamps.

### 2. The Launchers
- **Uniformity**: Each launcher (`.bat`, `.ps1`, `.sh`) implements the same menu system with 7 presets (e.g., Deep Work, Study Session) and custom options.
- **Argument Passing**: They parse user selection and construct the appropriate command line arguments for `pomodoro.py` (e.g., `-w 50 -n 10 -b 15 -c 3`).

### 3. The Reviewer
- **Frontend**: A React application embedded in a single HTML file (`pomodoro_review.html`) for portability.
- **Data Loading**: Fetches `pomodoro.txt` directly from the local server to parse and display entries.
- **AI Integration**: Connects directly to Google Gemini API (client-side) to generate summaries of the day's work based on the parsed notes.

## Code Structure & Workflow

```
   +----------------+       +-------------+
   |    Launcher    |------>| pomodoro.py |
   | (.bat/.ps1/.sh)|       +------+------+
   +----------------+              |
           ^                       | (Writes)
           |                       v
   +-------+--------+       +------+------+
   |   User Input   |       | pomodoro.txt|
   +----------------+       +------+------+
                                   ^
                                   | (Reads)
                            +------+------+
                            | Review App  |
                            | (.html/js)  |
                            +------+------+
                                   |
                                   v
                            +------+------+
                            | Gemini API  |
                            +-------------+
```

## Core Functions

| File | Function | Description |
|------|----------|-------------|
| `pomodoro.py` | `PomodoroTimer.listen_for_notes` | Background thread processing key presses into a buffer without blocking the timer loop. |
| `pomodoro.py` | `PomodoroTimer.run_timer` | Main loop that updates the display 50 times/sec for smooth typing while counting down seconds. |
| `pomodoro.py` | `PomodoroTimer.save_note` | Formats and writes notes to `pomodoro.txt` with context (Phase + Elapsed Time). |
| `pomodoro_review.html` | `extractAndGroupDates` | Groups raw text entries by Year/Month/Date for the UI navigation. |
| `pomodoro_review.html` | `generateSummary` | Constructs a prompt from a day's entries and calls the Gemini API. |

## Data Flow

1. **User Action**: User selects a preset in `pomodoro.bat`.
2. **Execution**: Batch script calls `python pomodoro.py -w ...`.
3. **Session**:
   - User types notes during the timer.
   - `pomodoro.py` writes lines to `pomodoro.txt`: `[Timestamp] (Phase): Note content`.
4. **Review**:
   - User launches `pomodoro_review.bat`.
   - Local server starts hosting the directory.
   - Browser opens `pomodoro_review.html`.
   - App reads `pomodoro.txt` and renders the timeline.

## Dependencies

- **Python 3.x**: Required for the core timer.
- **Pygame** (Optional): For high-quality audio playback. Falls back to `winsound` or system beep.
- **Node.js (`http-server`)** OR **Python**: Required only to host the review HTML file locally.
