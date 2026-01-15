# Pomodoro CLI 🍅

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

A high-performance, keyboard-centric Pomodoro timer designed for developers and power users who live in the terminal.

## Features
- **Distraction-Free**: Runs entirely in your localized terminal.
- **Integrated Note-Taking**: Capture thoughts ("Input Queue") instantly without stopping the timer or switching windows.
- **Cross-Platform**: Native launchers for Windows (`.bat`, `.ps1`) and Linux/macOS (`.sh`).
- **Review System**: Built-in dashboard to visualize your sessions and generate AI summaries of your day.

## Quick Start

### Windows
Double-click `pomodoro.bat` or `pomodoro_ps.bat` or run in terminal:
```cmd
pomodoro.bat
```

### Linux / macOS
```bash
./pomodoro.sh
```

### Python (Direct)
```bash
python pomodoro.py -w 25 -n 5 -b 5 -c 4
```

## Documentation

- **[Technical Documentation](CODE_DOCUMENTATION.md)**: Architecture, file structure, and implementation details.
- **[Design Philosophy](DESIGN_PHILOSOPHY.md)**: Why this tool exists and the principles behind it.
- **[Contributing](CONTRIBUTING.md)**: How to set up development environment and submit PRs.

## License

Copyright (C) 2026 Krishna Kanth B.
This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
