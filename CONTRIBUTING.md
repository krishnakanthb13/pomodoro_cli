# Contributing to Pomodoro CLI

Thank you for your interest in contributing! This project aims to be the fastest, most distraction-free terminal based productivity tool. We welcome contributions from everyone.

## Getting Started

1. **Fork the repository** to your GitHub account.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/krishnakanthb13/pomodoro_cli.git
   cd pomodoro_cli
   ```
3. **Install Dependencies** (Optional, for Audio):
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the tool** to make sure it works:
   ```bash
   python pomodoro.py
   ```

## Naming & Style
- **Python**: Follow PEP 8 guidelines.
- **Scripts**: Ensure parity between `.bat`, `.ps1`, and `.sh` scripts. If you add a feature to one, please attempt to add it to all three.
- **Frontend**: The `pomodoro_review.html` is a standalone file. Changes should be reflected in `pomodoro_review.tsx` (the source) if you are making logic changes, though currently the HTML is the distribution method.

## How to Submit Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/amazing-new-mode
   ```
2. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "Add 'Dark Mode' toggle to review dashboard"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/amazing-new-mode
   ```
4. Open a **Pull Request** on the main repository.

## Testing Checklist

Before submitting a PR, please verify:

- [ ] **Timer Accuracy**: Does the timer count down correctly?
- [ ] **Input Handling**: Can you type notes while the timer is running without visual glitches?
- [ ] **Audio**: Do chimes play correctly at the end of cycles?
- [ ] **Cross-Platform**: If modifying scripts, did you check that specific shell syntax is correct? (e.g., handling `%` in Batch vs `$` in Bash)
- [ ] **Reviewer**: Does `pomodoro_review.html` load the local `pomodoro.txt` correctly?

## Bug Reports

If you find a bug, please create an Issue and include:
- Your OS (Windows/Mac/Linux)
- Python version
- Terminal (cmd, powershell, bash, zsh, etc.)
- Steps to reproduce the error

Happy Coding! 🍅
