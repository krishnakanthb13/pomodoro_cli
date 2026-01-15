# Design Philosophy

## The Problem
Productivity tools often force a choice between structure and flexibility.
- **Strict Timers** force you to work without tracking the micro-thoughts and tasks that occur.
- **Note-taking apps** lack the urgency and rhythm of a timer.
- **GUI Apps** often introduce distraction and slow down "power users" who live in the terminal.

## The Solution
**Pomodoro CLI** bridges this gap by embedding a **frictionless note-taking system inside a strict timer**.

### 1. Speed & Flow
- **Keyboard-First**: Every action, from starting a session to validating a thought, happens via the keyboard. No mouse required.
- **Non-Blocking Input**: You can type a thought *instantly* while the timer ticks. The interface essentially says: *"Don't keep that thought in your head. Dump it here and keep working."*
- **Instant Start**: Presets like "Deep Work" or "Study Session" allow you to start a complex 2-hour block in 2 seconds.

### 2. Context Preservation
Standard Pomodoro timers treat "Work" as a black box. This tool treats it as a **stream of consciousness**. by recording thoughts with:
- Timestamp
- Phase (Work vs Break)
- Elapsed time (e.g., `(Work - 14)`)

You create a detailed "Flight Recorder" of your session. Only by seeing *when* you get distracted or have an idea can you improve your workflow.

### 3. Simplicity & Portability
- **Zero-Install (mostly)**: Written in standard Python with minimal dependencies.
- **Universal Access**: Works on Windows (CMD/PowerShell), macOS, and Linux.
- **Plain Text Data**: All data is stored in `pomodoro.txt`. No databases, no proprietary formats. You own your data forever.

## Workflow Integration
This tool is designed to run side-by-side with your code editor or terminal work.

1. **The Setup**: Open a small terminal window in the corner of your screen.
2. **The Session**: Start a timer. When you have a stray thought ("I need to email Bob", "Check that bug later"), type it into the timer window and hit Enter.
3. **The Benefit**: Your main focus remains unbroken. The thought is safe.
4. **The Review**: At the end of the day, open the **Reviewer**. Use the AI summary to convert your stream of jagged notes into a coherent log of what you achieved.

## Target Audience
- Developers who live in the terminal.
- Writers who need to track word sprints.
- Students who need strict study/break discipline.
- Anyone who struggles with "open loops" or distracting thoughts while trying to focus.
