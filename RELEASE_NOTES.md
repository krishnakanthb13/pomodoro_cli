# Release Notes - v1.0.0

## 🚀 Initial Release

We are excited to announce the first public release of **Pomodoro CLI**! This tool is designed to bring focus and flow to your terminal workflow.

### ✨ Key Features

- **Distraction-Free Timer**: A robust Python-based timer that runs directly in your terminal.
- **Integrated Note-Taking**: Capture thoughts instantly without breaking your flow. Notes are timestamped and tagged with your current phase (Work/Break).
- **Cross-Platform Support**: Native launchers for effortless usage on **Windows** (`.bat`, `.ps1`), **Linux**, and **macOS** (`.sh`).
- **AI-Powered Review**: A built-in dashboard (`pomodoro_review.html`) that visualizes your sessions and uses **Google Gemini** to generate daily summaries of your achievements.
- **Customizable Audio**: Comes with high-quality chimes or use your own `.wav` files.

### 📦 Installation

No complex installation required.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/krishnakanthb13/pomodoro_cli.git
   cd pomodoro_cli
   ```

2. **Run it**:
   - **Windows**: Double-click `pomodoro.bat` or `pomodoro_ps.bat`
   - **Linux/Mac**: Run `./pomodoro.sh`

3. **(Optional) Install Audio Support**:
   ```bash
   pip install pygame
   ```

### 📝 Documentation

- [Technical Documentation](CODE_DOCUMENTATION.md)
- [Design Philosophy](DESIGN_PHILOSOPHY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

### 🙌 Credits

Developed by **Krishna Kanth B.**
Licensed under **GPL v3**.

# Release Notes - v1.0.7

## ⏯️ Pause Functionality & Asset Cleanup

This update adds a highly requested feature for better control over your sessions and improves project organization.

### ✨ New Features

- **Pause/Resume Support**: You can now pause the timer at any time by pressing **Ctrl+P**.
  - **Visual Indicator**: A `(PAUSED)` status appears in red when active.
  - **Accurate Tracking**: Pausing stops the countdown and pauses the "elapsed time" counter in your notes, ensuring your logs remain accurate.

### 🧹 Improvements

- **Asset Reorganization**: Image assets have been moved to a dedicated `assets/` directory to keep the root folder clean.
- **Documentation Updates**: Updated README and Technical Documentation to reflect the new pause functionality.

# Release Notes - v1.1.0

## 📈 Analytics Dashboard, Themes & Productivity Boosts

A major update transforming Pomodoro CLI into a complete productivity system with advanced analytics, customization, and workflow enhancements.

### 📊 Review Dashboard Upgrade

- **New Analytics Tab**: A dedicated visual dashboard for your productivity data.
- **Heatmap Calendar**: GitHub-style contribution graph showing your activity intensity over the past year.
- **Productivity Charts**: Interactive bar charts visualizing your daily focus time and notes (Last 14 days).
- **Streak Tracking**: Stay motivated with daily streak counters (Current/Longest streak).
- **Daily/Weekly Stats**: At-a-glance cards for total focus time, notes, and work phases.

### 🎨 CLI Customization

- **Themes**: Switch between 5 stunning color schemes!
  - `cyberpunk` (Default neon)
  - `minimal` (Distraction-free monochrome)
  - `forest` (Calming greens)
  - `ocean` (Cool blues)
  - `sunset` (Warm gradients)
  - Usage: `python pomodoro.py --theme forest` or set default with `--set-theme`
- **Templates**: Save your favorite timer configurations.
  - Comes with built-in templates: `deep_work`, `study_session`, `quick_tasks`.
  - Create your own: `python pomodoro.py -w 50 -b 10 --save-template my_custom`
  - Load and go: `python pomodoro.py --template deep_work`

### ✨ Productivity Features

- **Skip Phase**: Done early? Press **Ctrl+K** to instantly skip the current phase and move to the next.
- **Desktop Notifications**: Get native system notifications when a phase ends or timer pauses (requires `plyer`).
  - Toggle anytime: `python pomodoro.py --toggle-notifications`

### 🛠️ Technical Improvements

- **Persistent Config**: Settings are now saved to `config.json` (Theme, Notifications, Defaults).
- **Notification Fallback**: Gracefully handles missing optional dependencies like `plyer`.
- **Enhanced Encodings**: Improved unicode handling for Windows terminals and file exports.

# Release Notes - v1.1.1

## 🐧 Linux & macOS Parity + Launcher Refinement

This update focuses on bringing full feature parity and visual consistency to our non-Windows launchers, ensuring a seamless experience regardless of your OS.

### ✨ New Features

- **Full Linux/macOS Parity**: Updated `pomodoro.sh` to include all features previously exclusive to the Windows launchers.
- **Settings Integration**: You can now access the full interactive settings menu (`python pomodoro.py --settings`) directly from the `.sh` launcher (Linux/macOS).
- **Custom Settings Sync**: The `Custom Settings` option in the bash launcher now uses the robust internal `--custom` flag of `pomodoro.py`, matching the Windows behavior.

### 🎨 Visual & UI Polish

- **Theme Consistency**: ANSI color codes in the shell scripts have been updated to use "bright" variants, matching the vibrant UI of the Windows `.bat` and `.ps1` versions.
- **Workflow Improvements**: Refined the navigation logic in all launchers to prevent redundant prompts when returning from the Reviewer or Settings menus.
- **Bug Fixes**: Corrected minor typos in the PowerShell launcher messages and synchronized session labeling across all platforms.

### 🛠️ Technical Improvements

- **Execution Safety**: Improved script reliability on macOS by ensuring correct directory context and execution permissions.
- **Exit Logic**: Standardized the session exit sequence across all platforms with consistent delays and "thank you" messages.

# Release Notes - v1.1.3

## ⏱️ Precision Analytics & Visual Polish

This release brings a fundamental improvement to how we track your focus time-moving from estimates to actual data, along with a major visual polish for the dashboard.

### ⚡ Core Updates

- **Accurate Focus Time**: The Review Dashboard now calculates "Focus Time" by measuring the actual duration between a cycle start and your last note in that cycle.
  - *Previously:* Assumed a flat 25 minutes per cycle.
  - *Now:* Reflects your actual time in the chair.
- **Contextual Help**: Added interactive "Info" buttons (ℹ️) with a pulsing green glow to every analytics card, explaining exactly how metrics are calculated.

### ✨ Visual Enhancements

- **Simplified Charts**: The "Last 14 Days" activity chart now uses clean day numbers (e.g., "10", "11") on the x-axis to reduce clutter.
- **Consistent Tooltips**: Standardized hover tooltips across all charts to use ISO date format (YYYY-MM-DD) and clear entry counts.
- **Navigation**: Moved the "View Analytics" button to the top of the Overview page for instant access.

### 📚 Documentation

- **Updated Docs**: Comprehensive updates to `README.md` and `CODE_DOCUMENTATION.md` covering the new analytics engine and tracking logic.

# Release Notes - v1.1.4

## 📝 Enhanced AI Summary Presentation

This release focuses on making AI-generated Daily Summaries more readable, professional, and user-friendly with comprehensive markdown support and improved layout.

### ✨ New Features

- **Full Markdown Support**: Daily summaries now render with complete markdown formatting:
  - Headings (H1-H6) with proper hierarchy and styling
  - Ordered and unordered lists with proper indentation
  - Nested lists with different bullet styles (disc → circle → square)
  - Code blocks with syntax highlighting and inline code
  - Blockquotes with styled borders
  - Tables, horizontal rules, and links
  - Bold, italic, and all standard markdown elements

- **Compact Layout**: Optimized spacing for better readability:
  - Reduced line-height from 1.75 to 1.4
  - Minimized vertical margins between elements
  - Tight list spacing for cleaner presentation
  - Overall more compact and scannable layout

- **Collapsible Interface**: 
  - Toggle button with animated chevron icon (rotates 180°)
  - Expand/collapse the summary with a single click
  - Starts expanded by default
  - Smooth transitions for polished user experience
  - Hover effects for better interactivity

### 🎨 Visual Improvements

- **Professional Typography**: Proper heading hierarchy with distinct sizes and weights
- **Color-Coded Elements**: Inline code in amber, links in blue, headings in bright white
- **Structured Lists**: Clear visual hierarchy with proper indentation and marker colors
- **Clean Spacing**: Balanced margins and padding throughout

### 📚 Documentation

- **Updated Docs**: Added Daily Summary enhancements to `README.md`, `CODE_DOCUMENTATION.md`, and `DESIGN_PHILOSOPHY.md`

# Release Notes - v1.1.5

## 🧭 Enhanced Navigation & UI Consistency

This release improves the review interface with collapsible navigation, better button organization, and consistent layout across all views.

### ✨ New Features

- **Collapsible Date Lists**: Year and month sections now collapse/expand individually with animated chevron icons for organized browsing
- **Quick Controls**: Added "Collapse All" and "Expand All" buttons for instant date list management
- **Icon-Enhanced Buttons**: All navigation buttons now include relevant icons for better visual clarity

### 🎨 UI Improvements

- **Consistent Button Layout**: Navigation buttons (Back to Dates, View All Entries) moved to the top of each view for easy access
- **Unified Page Layout**: All views now use consistent width (`max-w-4xl`) and padding for a professional appearance
- **Better Organization**: Streamlined button placement across Overview, Details, Analytics, and All Entries pages

### 📚 Documentation

- **Updated Docs**: Added navigation enhancements to `README.md`, `CODE_DOCUMENTATION.md`, and `DESIGN_PHILOSOPHY.md`


# Release Notes - v1.1.6

## 📝 Immediate Notes Access

This release adds a frequently requested feature: the ability to open your notes file instantly while the timer is running.

### ✨ New Features

- **Open Notes Shortcut (`Ctrl+O`)**: Press `Ctrl+O` at any time during a running timer to open your `pomodoro.txt` file in the default editor without stopping or interrupting the session.
- **Improved Input Handling**: The non-blocking input listener now handles the new shortcut seamlessly across Windows, Linux, and macOS.

### 🛠️ Improvements

- **UI Updates**: The timer start screen now explicitly lists `Ctrl+O` in the shortcuts tip for better discoverability.
- **Project Structure**: Added `.gemini/` and feature summary files to `.gitignore` to keep the repo clean.

### 📚 Documentation

- **Updated Docs**: 
    - `README.md`: Added `Ctrl+O` to the shortcuts list and feature descriptions.
    - `CODE_DOCUMENTATION.md`: Updated technical details about input handling and auto-open behavior.
