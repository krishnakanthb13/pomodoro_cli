# Design Philosophy

## The Problem
Productivity tools often force a choice between structure and flexibility.
- **Strict Timers** force you to work without tracking the micro-thoughts and tasks that occur.
- **Note-taking apps** lack the urgency and rhythm of a timer.
- **GUI Apps** often introduce distraction and slow down "power users" who live in the terminal.
- **Plain CLI Timers** lack visual feedback, making it hard to gauge progress at a glance.

## The Solution
**Pomodoro CLI** bridges this gap by embedding a **frictionless note-taking system inside a strict timer** with a **modern, visually rich terminal experience**.

### 1. Speed & Flow
- **Keyboard-First**: Every action, from starting a session to validating a thought, happens via the keyboard. No mouse required.
- **Non-Blocking Input**: You can type a thought *instantly* while the timer ticks. The interface essentially says: *"Don't keep that thought in your head. Dump it here and keep working."*
- **Instant Start**: Presets like "Deep Work" or "Study Session" allow you to start a complex 2-hour block in 2 seconds.
- **Blinking Cursor**: A visual cue that the system is alive and ready for your input.

### 2. Visual Feedback
- **Progress Bar**: A color-coded progress bar transitions from green through yellow to red as time runs out, giving you an instant sense of urgency without requiring you to read numbers.
- **Dynamic Terminal Title**: The window title always shows the current phase and remaining time—visible even when the terminal is minimized or in the taskbar.
- **Neon/Cyberpunk Theme**: A carefully chosen color palette (cyan, yellow, green) that's easy on the eyes during long sessions while remaining visually distinct.

### 3. Context Preservation
Standard Pomodoro timers treat "Work" as a black box. This tool treats it as a **stream of consciousness** by recording thoughts with:
- Timestamp
- Phase (Work vs Journal vs Break)
- Elapsed time within the phase (e.g., `(Work - 14)`)

You create a detailed "Flight Recorder" of your session. Only by seeing *when* you get distracted or have an idea can you improve your workflow.

### 4. Intentional Start
Before each cycle, the tool prompts you to set your **Adventure(s)** (or Goals/Focus—configurable). This small ritual:
- Forces you to articulate what you're about to do.
- Creates a record to compare against your actual work.
- Provides psychological commitment to the task.

### 5. Simplicity & Portability
- **Zero-Install (mostly)**: Written in standard Python with two dependencies (`rich` for UI, `pygame` for audio).
- **Universal Access**: Works on Windows (CMD/PowerShell), macOS, and Linux.
- **Plain Text Data**: All data is stored in `pomodoro.txt`. No databases, no proprietary formats. You own your data forever.

### 6. Seamless Completion
When your session ends or you press Ctrl+C:
- A chime plays to signal completion.
- Your notes file opens automatically in your default editor.
- No extra steps required to review what you captured.

## Workflow Integration
This tool is designed to run side-by-side with your code editor or terminal work.

1. **The Setup**: Open a small terminal window in the corner of your screen.
2. **The Ritual**: Set your Adventure—what you intend to accomplish this cycle.
3. **The Session**: Start the timer. Watch the progress bar. When you have a stray thought ("I need to email Bob", "Check that bug later"), type it into the timer window and hit Enter.
4. **The Benefit**: Your main focus remains unbroken. The thought is safe. The progress bar keeps you aware of time without constant checking.
5. **The Review**: At the end of the day, open the **Reviewer**. Use the AI summary to convert your stream of jagged notes into a coherent log of what you achieved.

## Target Audience
- Developers who live in the terminal.
- Writers who need to track word sprints.
- Students who need strict study/break discipline.
- Anyone who struggles with "open loops" or distracting thoughts while trying to focus.
- Power users who appreciate aesthetic terminal applications.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Rich library over plain ANSI | Consistent cross-platform rendering and easier maintenance of complex UI elements |
| 50 Hz display loop | Smooth typing experience without visible lag between keypress and display |
| Progress bar above timer text | Visual hierarchy—see progress at a glance, detailed time below |
| Configurable phrase options | Different users prefer different motivation styles (Adventure vs Goals vs Focus) |
| Auto-open notes file | Reduce friction in the "capture → review" workflow |
| Dynamic terminal title | Allows monitoring timer while focused on other windows |
