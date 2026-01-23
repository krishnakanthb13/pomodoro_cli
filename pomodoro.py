#!/usr/bin/env python3
"""
CLI Pomodoro Timer with Note-Taking
A productivity timer that cycles through work, journaling, and break periods
with audio notifications and always-available note-taking capability.
"""

import argparse
import time
import threading
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import queue
import warnings
import subprocess
import platform

# Rich imports
from rich.console import Console, Group
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text

# Local modules
from config_manager import load_config, get_setting, set_setting
from themes import get_theme, list_themes, get_theme_info, DEFAULT_THEME
from templates_manager import (
    list_templates, load_template, save_template, 
    format_template_list, get_template_by_index
)
import notifications

# Initialize rich console
console = Console()

# Non-blocking keyboard input
if sys.platform == "win32":
    import msvcrt
    NONBLOCKING_INPUT = True
else:
    import select
    import tty
    import termios
    NONBLOCKING_INPUT = False

# Suppress pygame's pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pygame")
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

# Try multiple audio libraries
AUDIO_AVAILABLE = False
AUDIO_METHOD = None

# Load config and set globals
CONFIG = load_config()
PHRASE_OPTION = CONFIG.get("phrase_option", 3)
CURSOR_BLINK_SPEED = CONFIG.get("cursor_blink_speed", 20)
NOTIFICATIONS_ENABLED = CONFIG.get("notifications_enabled", True)

# Load theme from config
THEME = get_theme(CONFIG.get("theme", DEFAULT_THEME))

# UI Colors from theme
COLOR_SEPARATOR = THEME["separator"]
COLOR_HEADER = THEME["header"]
COLOR_INFO = THEME["info"]
COLOR_TIP = THEME["tip"]
COLOR_SUCCESS = THEME["success"]
COLOR_PROGRESS_LOW = THEME["progress_low"]
COLOR_PROGRESS_MID = THEME["progress_mid"]
COLOR_PROGRESS_HIGH = THEME["progress_high"]
COLOR_PROGRESS_CRITICAL = THEME["progress_critical"]
COLOR_CURSOR = THEME["cursor"]
COLOR_PAUSED = THEME["paused"]

# Try pygame first (most reliable)
try:
    # Suppress pygame welcome message
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    AUDIO_METHOD = "pygame"
except ImportError:
    pass

# Try winsound on Windows
if not AUDIO_AVAILABLE and sys.platform == "win32":
    try:
        import winsound
        AUDIO_AVAILABLE = True
        AUDIO_METHOD = "winsound"
    except ImportError:
        pass

if not AUDIO_AVAILABLE:
    print("Warning: No audio library available. Install pygame with: pip install pygame")
    print("Chimes will use system beep.\n")


class PomodoroTimer:
    def __init__(self, work_min, note_min, break_min, cycles, chime_file):
        self.work_duration = work_min * 60
        self.note_duration = note_min * 60
        self.break_duration = break_min * 60
        self.cycles = cycles
        self.chime_file = chime_file
        self.current_phase = ""
        self.stop_timer = False
        self.notes_file = "pomodoro.txt"
        self.accepting_notes = False
        self.note_queue = queue.Queue()
        self.last_display_length = 0
        self.line_buffer = ""  # Buffer for non-blocking input
        self.phase_start_time = None  # Track when each phase starts for elapsed time
        self.paused = False
        self.skip_phase = False  # Flag to skip current phase early
        self.notifications_enabled = NOTIFICATIONS_ENABLED
        
    def play_chime(self):
        """Play the chime sound using available method"""
        if not AUDIO_AVAILABLE or not self.chime_file or not os.path.exists(self.chime_file):
            # Fallback beep
            print('\a')
            return
        
        try:
            if AUDIO_METHOD == "pygame":
                pygame.mixer.music.load(self.chime_file)
                pygame.mixer.music.play()
                # Wait for sound to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            elif AUDIO_METHOD == "winsound":
                winsound.PlaySound(self.chime_file, winsound.SND_FILENAME)
        except Exception as e:
            print(f"\nError playing sound: {e}")
            print('\a')  # Fallback beep
    
    def open_notes_file(self):
        """Open the notes file in the default text editor"""
        if not os.path.exists(self.notes_file):
            print(f"Note: {self.notes_file} doesn't exist yet.")
            return
        
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(self.notes_file)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', self.notes_file])
            else:  # Linux and others
                subprocess.run(['xdg-open', self.notes_file])
            print(f"📂 Opening {self.notes_file}...")
        except Exception as e:
            print(f"Could not open file automatically: {e}")
            print(f"Please open manually: {self.notes_file}")
    
    def save_note(self, note_text):
        """Save a note with timestamp, elapsed minutes, and current phase"""
        if note_text.strip():
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            elapsed_mins = 0
            if self.phase_start_time:
                elapsed_secs = (datetime.now() - self.phase_start_time).total_seconds()
                elapsed_mins = int(elapsed_secs // 60)
            phase_label = f"({self.current_phase} - {elapsed_mins})"
            
            with open(self.notes_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} {phase_label}: {note_text}\n")
            
            # Print the note above the timer using rich console
            console.print(f"[{COLOR_SUCCESS}] ✓ Added:[/{COLOR_SUCCESS}] {note_text[:40]}{'...' if len(note_text) > 40 else ''}")
    
    def ask_for_goal(self, cycle):
        """Ask user for their goal/target before starting a cycle"""
        self.accepting_notes = False  # Disable note saving
        self.line_buffer = ""  # Clear any partial input
        
        # Phrase configuration
        # 1: Standard Goals
        # 2: Focus/Leap
        # 3: Adventure (Default)
        
        if PHRASE_OPTION == 1:
            header_text = f"📝 Before starting Cycle {cycle} of {self.cycles}, set your Goal(s):"
            input_prompt = "What do you want to accomplish this cycle? "
        elif PHRASE_OPTION == 2:
            header_text = f"🎯 Before starting Cycle {cycle} of {self.cycles}, set your Focus/Goal(s):"
            input_prompt = "What Leap you are willing to take this time? "
        else: # Default to 3
            header_text = f"🚀 Before starting Cycle {cycle} of {self.cycles}, set your Adventure(s):"
            input_prompt = "What Adventures you have in mind? "

        console.print(f"\n[{COLOR_SEPARATOR}]{'─'*60}[/{COLOR_SEPARATOR}]")
        console.print(f"[{COLOR_HEADER}]{header_text}[/{COLOR_HEADER}]")
        console.print(f"[{COLOR_SEPARATOR}]{'─'*60}[/{COLOR_SEPARATOR}]")
        console.print()
        
        console.print(f"[{COLOR_TIP}]{input_prompt}[/{COLOR_TIP}]", end="")
        goal = input().strip()
        
        if goal:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(self.notes_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{timestamp} (CYCLE {cycle} of {self.cycles} - GOAL): {goal}\n")
            console.print(f"[{COLOR_SUCCESS}]✓ Goal saved successfully![/{COLOR_SUCCESS}]")
        else:
            console.print("No goal set.")
        
        # Brief countdown to prepare (no extra Enter needed)
        console.print(f"[{COLOR_TIP}]Starting in: [/{COLOR_TIP}]", end="")
        for i in range(5, 0, -1):
            console.print(f"{i}...", end="")
            sys.stdout.flush()
            time.sleep(1)
        console.print(f"[{COLOR_HEADER}] GO![/{COLOR_HEADER}]")
        
        self.accepting_notes = True  # Re-enable note saving
    
    def listen_for_notes(self):
        """Background thread to listen for note input using non-blocking keyboard input"""
        while not self.stop_timer:
            try:
                # Only listen for notes when accepting_notes is True
                if not self.accepting_notes:
                    time.sleep(0.05)  # Small delay to avoid busy-waiting
                    continue
                
                if NONBLOCKING_INPUT:
                    # Windows: Use msvcrt for non-blocking input
                    if msvcrt.kbhit():
                        char = msvcrt.getwch()
                        
                        # Check again in case flag changed
                        if not self.accepting_notes:
                            continue
                        
                        if char == '\r':  # Enter pressed
                            if self.line_buffer.strip():
                                self.note_queue.put(self.line_buffer)
                            self.line_buffer = ""
                            # No need to write newline - timer display will handle it
                        elif char == '\x08':  # Backspace
                            if self.line_buffer:
                                self.line_buffer = self.line_buffer[:-1]
                            # Timer display will update on next tick
                        elif char == '\x03':  # Ctrl+C
                            raise KeyboardInterrupt
                        elif char == '\x10':  # Ctrl+P
                            self.paused = not self.paused
                            if self.notifications_enabled:
                                if self.paused:
                                    notifications.notify_paused()
                                else:
                                    notifications.notify_resumed()
                        elif char == '\x0b':  # Ctrl+K - Skip phase
                            self.skip_phase = True
                        elif ord(char) >= 32:  # Printable character
                            self.line_buffer += char
                            # Timer display will show this on next tick
                    else:
                        time.sleep(0.05)  # No key pressed, small delay
                else:
                    # Linux/macOS: Use select for polling stdin
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                         # Read line if available
                         try:
                             line = sys.stdin.read(1)
                             if line == '\x10':
                                 self.paused = not self.paused
                                 continue
                             if line == '\x0b':  # Ctrl+K - Skip phase
                                 self.skip_phase = True
                                 continue
                             if line: # if char received
                                 # We need to accumulate chars similar to Windows logic ideally,
                                 # but for standard terminal, readline is safer if not in raw mode.
                                 # Let's just use readline for simplicity as raw mode is complex here
                                 full_line = sys.stdin.readline()
                                 # Combine the first char + rest
                                 note = line + full_line
                                 if note.strip() and self.accepting_notes:
                                     self.note_queue.put(note.strip())
                         except IOError:
                             pass
                    else:
                        pass # No input, continue loop
            except EOFError:
                break
            except KeyboardInterrupt:
                self.stop_timer = True
                break
            except Exception:
                pass
    
    def process_notes(self):
        """Process any notes in the queue"""
        try:
            while not self.note_queue.empty():
                note = self.note_queue.get_nowait()
                self.save_note(note)
        except queue.Empty:
            pass
    
    def run_timer(self, duration, phase_name):
        """Run a countdown timer for the specified duration"""
        self.current_phase = phase_name
        self.phase_start_time = datetime.now()  # Track phase start for elapsed time in notes
        remaining = duration
        
        console.print(f"\n[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
        console.print(f"  [{COLOR_HEADER}]{phase_name.upper()} TIME STARTED[/{COLOR_HEADER}]")
        console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
        console.print(f"[{COLOR_TIP}]Type notes anytime and press Enter to save them.[/{COLOR_TIP}]")
        console.print() # Permanent gap after instructions
        
        # Initialize Progress Bar
        # Width set to 60 to match the separator lines ('='*60)
        # Note: 'expand=False' ensures it respects the width passed to BarColumn or calculated differently.
        # However, to force the whole Progress renderable to be 60 chars, we can rely on BarColumn sizing
        # but exact 60 char width for the whole line is tricky with TextColumns.
        # A better approach is to rely on BarColumn(bar_width=40) + TextColumn...
        # The user specifically asked "make the progress width with the lines ('='*60)".
        # Let's try to constrain the Live display or Console options, but simpler is tuning the bar width.
        # 60 chars total:
        # [progress.percentage] is approx 4-5 chars.
        # So BarColumn should be around 55 chars.
        # Let's try a fixed bar width of 52 + percentage column.

        progress = Progress(
            BarColumn(bar_width=52),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            expand=False
        )
        task_id = progress.add_task("Timer", total=duration)

        # Use Rich Live display
        # Initialize blink state
        blink_visible = True
        frame_count = 0

        with Live(console=console, refresh_per_second=20, transient=True) as live:
            while remaining > 0 and not self.stop_timer and not self.skip_phase:
                # Process any queued notes
                self.process_notes()
                
                # Calculate color based on percentage elapsed
                elapsed = duration - remaining
                pct = elapsed / duration

                # Green < 70% < Yellow < 80% < Red < 90%
                # Green < 70% < Yellow < 80% < Red < 90%
                if pct > 0.9:
                    style = COLOR_PROGRESS_CRITICAL
                elif pct > 0.8:
                    style = COLOR_PROGRESS_HIGH
                elif pct > 0.7:
                    style = COLOR_PROGRESS_MID
                else:
                    style = COLOR_PROGRESS_LOW

                # Update bar style
                progress.columns[0].complete_style = style
                progress.columns[0].finished_style = style

                progress.update(task_id, completed=elapsed)

                mins, secs = divmod(remaining, 60)

                # Update terminal title
                # Use sys.__stdout__ to bypass rich capture and avoid artifacts in the Live display
                try:
                    sys.__stdout__.write(f"\033]2;{phase_name}: {mins:02d}:{secs:02d} remaining\007")
                    sys.__stdout__.flush()
                except (AttributeError, IOError):
                    pass

                # Manual blink logic for main loop tick
                cursor_markup = f"[{COLOR_CURSOR}]█[/{COLOR_CURSOR}]" if blink_visible else " "

                # Create the text line with emulated cursor
                status_text = f"[{COLOR_PAUSED}](PAUSED) [/{COLOR_PAUSED}]>> " if self.paused else ">> "
                timer_text = Text.from_markup(f"{phase_name} time: {mins:02d}:{secs:02d} remaining {status_text}{self.line_buffer}{cursor_markup}")

                # Update the Live display
                # User requested Group(progress, timer_text) - Progress ON TOP
                live.update(Group(progress, timer_text))

                # Update display 50 times per second for smoother typing/backspacing
                # but only decrement timer once per second
                for _ in range(50):
                    if self.stop_timer or self.skip_phase:
                        break
                    time.sleep(0.02)
                    self.process_notes()

                    # Blink logic: Toggle every CURSOR_BLINK_SPEED frames
                    frame_count += 1
                    if frame_count >= CURSOR_BLINK_SPEED:
                        blink_visible = not blink_visible
                        frame_count = 0

                    cursor_markup = f"[{COLOR_CURSOR}]█[/{COLOR_CURSOR}]" if blink_visible else " "

                    # Update text with new input buffer
                    status_text = f"[{COLOR_PAUSED}](PAUSED) [/{COLOR_PAUSED}]>> " if self.paused else ">> "
                    timer_text = Text.from_markup(f"{phase_name} time: {mins:02d}:{secs:02d} remaining {status_text}{self.line_buffer}{cursor_markup}")
                    live.update(Group(progress, timer_text))

                if not self.paused:
                    remaining -= 1
                elif self.phase_start_time:
                    self.phase_start_time += timedelta(seconds=1)
        
        if self.skip_phase:
            # Phase was skipped
            console.print(f"\r[{COLOR_INFO}]⏭️ {phase_name} phase skipped![/{COLOR_INFO}]{' '*20}")
            console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
            # Log skip to notes file
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(self.notes_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} ({phase_name} - SKIPPED)\n")
            self.skip_phase = False  # Reset for next phase
        elif not self.stop_timer:
            # We use transient=True, so the live display clears. We can just print normally.
            console.print(f"\r{phase_name} time: 00:00 - COMPLETED!{' '*20}")
            console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
            self.play_chime()
            # Send desktop notification
            if self.notifications_enabled:
                notifications.notify_phase_complete(phase_name)
    
    def start(self):
        """Start the Pomodoro timer cycles"""
        console.print(f"\n[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
        console.print(f"  [{COLOR_HEADER}]🍅 POMODORO TIMER STARTED[/{COLOR_HEADER}]")
        console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
        console.print(f"[{COLOR_INFO}]Cycles: {self.cycles}[/{COLOR_INFO}]", end=" | ")
        console.print(f"[{COLOR_INFO}]Work: {self.work_duration//60} min | Note: {self.note_duration//60} min | Break: {self.break_duration//60} min[/{COLOR_INFO}]")
        if self.chime_file:
            console.print(f"[{COLOR_INFO}]Chime: {self.chime_file}[/{COLOR_INFO}]", end=" | ")
        if AUDIO_AVAILABLE:
            console.print(f"[{COLOR_INFO}]Audio: {AUDIO_METHOD}[/{COLOR_INFO}]")
        console.print(f"[{COLOR_INFO}]Notes saved to: {self.notes_file}[/{COLOR_INFO}]")
        console.print(f"[{COLOR_TIP}]💡 Ctrl+C to stop | Ctrl+P to pause | Ctrl+K to skip phase[/{COLOR_TIP}]")
        console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
        
        # Start ONE note-listening thread for the entire session
        note_thread = threading.Thread(target=self.listen_for_notes, daemon=True)
        note_thread.start()
        
        try:
            for cycle in range(1, self.cycles + 1):
                console.print(f"\n[{COLOR_HEADER}]🔄 CYCLE {cycle} of {self.cycles}[/{COLOR_HEADER}]")
                
                # Ask for goal (note-taking disabled inside this function)
                self.ask_for_goal(cycle)
                
                # Work phase
                self.run_timer(self.work_duration, "Work")
                
                # Note-taking phase
                self.run_timer(self.note_duration, "Journal")
                
                # Break phase (skip on last cycle)
                if cycle < self.cycles:
                    self.run_timer(self.break_duration, "Break")
            
            console.print(f"\n\n[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
            console.print(f"  [{COLOR_HEADER}]🎉 ALL CYCLES COMPLETED! Great work![/{COLOR_HEADER}]")
            console.print(f"[{COLOR_SEPARATOR}]{'='*60}[/{COLOR_SEPARATOR}]")
            console.print(f"[{COLOR_INFO}]📄 All notes saved to: {self.notes_file}[/{COLOR_INFO}]")

            try:
                sys.__stdout__.write("\033]2;Pomodoro Timer: Completed!\007")
                sys.__stdout__.flush()
            except:
                pass

            self.play_chime()
            self.open_notes_file()
            
        except KeyboardInterrupt:
            console.print(f"\n\n[{COLOR_HEADER}]⏸️ Timer stopped by user (Ctrl+C pressed)[/{COLOR_HEADER}]")
            console.print(f"[{COLOR_INFO}]📄 Notes saved to: {self.notes_file}[/{COLOR_INFO}]")
            # input("\nPress Enter to open notes file and exit...")
            self.open_notes_file()
            time.sleep(0.5)  # Give threads time to clean up
        finally:
            self.stop_timer = True
            time.sleep(0.5)  # Give threads time to clean up


def find_wav_files():
    """Find all .wav files in sounds directory"""
    wav_files = []
    
    # Check sounds directory first
    sounds_dir = Path('sounds')
    if sounds_dir.exists():
        wav_files.extend(sounds_dir.glob('*.wav'))
    
    # Also check current directory as fallback/addition
    current_dir = Path('.')
    wav_files.extend(current_dir.glob('*.wav'))
    
    # Remove duplicates and sort
    unique_files = sorted(list(set([str(f) for f in wav_files])))
    return unique_files


def select_chime():
    """Let user select a chime from available .wav files"""
    wav_files = find_wav_files()
    
    if not wav_files:
        print("No .wav files found in current directory or subdirectories.")
        return None
    
    print("\nAvailable chime sounds:")
    for i, wav in enumerate(wav_files, 1):
        print(f"  {i}. {wav}")
    
    while True:
        try:
            choice = input(f"\nSelect chime (1-{len(wav_files)}) or press Enter to skip: ").strip()
            if not choice:
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(wav_files):
                return wav_files[choice_num - 1]
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            return None


def select_theme():
    """Let user select a theme from available themes"""
    themes = list_themes()
    print("\nAvailable Themes:")
    for i, name in enumerate(themes, 1):
        info = get_theme_info().split('\n')[i+1] # Hacky but works to reuse description text
        # Or just fetch clean list
        print(f"  {i}. {name.capitalize()}")
    
    while True:
        try:
            choice = input(f"\nSelect theme (1-{len(themes)}) or press Enter to skip: ").strip()
            if not choice:
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(themes):
                return themes[choice_num - 1]
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            return None

def select_template():
    """Let user select a template from available templates"""
    templates = list_templates()
    if not templates:
        return None
        
    print("\nAvailable Templates:")
    for i, t in enumerate(templates, 1):
        s = t["settings"]
        print(f"  {i}. {t['name']} ({s.get('work')}m/{s.get('note')}m/{s.get('break')}m x{s.get('cycles')})")
        
    while True:
        try:
            choice = input(f"\nSelect template (1-{len(templates)}) or press Enter to skip: ").strip()
            if not choice:
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(templates):
                return templates[choice_num - 1]["settings"]
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            return None

def run_custom_wizard():
    """Interactive wizard for custom session setup"""
    print("\n" + "="*40)
    print("   CUSTOM SESSION CONFIGURATION")
    print("="*40)
    
    # Defaults
    work = 25
    note = 5
    break_time = 10
    cycles = 4
    chime_file = CONFIG.get("default_chime")
    theme_name = CONFIG.get("theme", DEFAULT_THEME)
    
    # 1. Template
    templates = list_templates()
    if templates:
        use_template = input("\nLoad from template? (y/N): ").lower().startswith('y')
        if use_template:
            template = select_template()
            if template:
                work = template.get("work", work)
                note = template.get("note", note)
                break_time = template.get("break", break_time)
                cycles = template.get("cycles", cycles)
                chime_file = template.get("chime", chime_file)
                theme_name = template.get("theme", theme_name)
                print(f"[green]✓ Loaded template settings[/green]")
                
                # Ask if user wants to modify anything from template?
                # For now, let's assume template implies readiness, but maybe allow overrides?
                # Simpler: If template loaded, skip to confirmation/start unless flags override (which args do)
                # But here we are in wizard.
                pass

    # If no template selected, or asking for overrides (currently just manual if no template)
    if not templates or (templates and not 'template' in locals()):
        try:
            w = input(f"\nWork duration [{work}]: ").strip()
            if w: work = int(w)
            
            n = input(f"Note duration [{note}]: ").strip()
            if n: note = int(n)
            
            b = input(f"Break duration [{break_time}]: ").strip()
            if b: break_time = int(b)
            
            c = input(f"Cycles [{cycles}]: ").strip()
            if c: cycles = int(c)
        except ValueError:
            print("Invalid number entered. Using defaults.")

    # 2. Chime
    if input(f"\nChange chime sound? (Current: {os.path.basename(str(chime_file)) if chime_file else 'None'}) (y/N): ").lower().startswith('y'):
        c = select_chime()
        if c: chime_file = c

    # 3. Theme
    if input(f"\nChange theme? (Current: {theme_name}) (y/N): ").lower().startswith('y'):
        t = select_theme()
        if t: theme_name = t
        
    return work, note, break_time, cycles, chime_file, theme_name


def configure_settings():
    """Interactive settings menu to configure all options"""
    while True:
        # Load fresh config each time
        config = load_config()
        
        print("\n" + "="*40)
        print("   POMODORO CONFIGURATION")
        print("="*40)
        print(f"1. Theme                [{config.get('theme', 'cyberpunk')}]")
        print(f"2. Default Chime        [{os.path.basename(str(config.get('default_chime', 'None')))}]")
        print(f"3. Phrase Style         [{'Adventure' if config.get('phrase_option') == 3 else 'Focus' if config.get('phrase_option') == 2 else 'Standard'}]")
        print(f"4. Notifications        [{'Enabled' if config.get('notifications_enabled') else 'Disabled'}]")
        print(f"5. Cursor Blink Speed   [{config.get('cursor_blink_speed', 20)}] (Higher = Slower)")
        print("-" * 40)
        print("0. Back to Main Menu")
        
        choice = input("\nSelect setting to change (0-5): ").strip()
        
        if choice == '1':
            t = select_theme()
            if t:
                from config_manager import set_theme
                set_theme(t)
                print(f"[green]✓ Theme updated to: {t}[/green]")
                
        elif choice == '2':
            print("\nSelect default chime sound:")
            c = select_chime()
            if c:
                set_setting("default_chime", str(c))
                print(f"[green]✓ Default chime updated[/green]")
                
        elif choice == '3':
            print("\nPhrase Options:")
            print("1. Standard (What is your goal?)")
            print("2. Focus (What Leap to take?)")
            print("3. Adventure (What Adventure to take?)")
            try:
                p = int(input("Select style (1-3): "))
                if 1 <= p <= 3:
                    set_setting("phrase_option", p)
                    print(f"[green]✓ Phrase style updated[/green]")
            except ValueError:
                pass
                
        elif choice == '4':
            current = config.get("notifications_enabled", True)
            set_setting("notifications_enabled", not current)
            print(f"[green]✓ Notifications {'enabled' if not current else 'disabled'}[/green]")
            
        elif choice == '5':
            try:
                s = int(input("\nEnter blink speed (10-50, default 20): "))
                if 10 <= s <= 50:
                    set_setting("cursor_blink_speed", s)
                    print(f"[green]✓ Blink speed updated[/green]")
            except ValueError:
                pass
                
        elif choice == '0':
            break


def main():
    global THEME, COLOR_SEPARATOR, COLOR_HEADER, COLOR_INFO, COLOR_TIP, COLOR_SUCCESS
    global COLOR_PROGRESS_LOW, COLOR_PROGRESS_MID, COLOR_PROGRESS_HIGH, COLOR_PROGRESS_CRITICAL
    global COLOR_CURSOR, COLOR_PAUSED
    parser = argparse.ArgumentParser(
        description='CLI Pomodoro Timer with note-taking capability',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run (25 min work, 5 min notes, 10 min break, 4 cycles)
    python pomodoro.py -w 25 -n 5 -b 10 -c 4

    # With a custom sound file
    python pomodoro.py -w 25 -n 5 -b 10 -c 4 --chime mysound.wav

    # Interactive Settings Menu
    python pomodoro.py --settings

    # Use a saved template
    python pomodoro.py --template deep_work
        """
    )
    
    # Timer settings
    parser.add_argument('--work', '-w', type=int, default=None,
                        help='Work duration in minutes (default: 25)')
    parser.add_argument('--note', '-n', type=int, default=None,
                        help='Note-taking duration in minutes (default: 5)')
    parser.add_argument('--break', '-b', type=int, default=None, dest='break_time',
                        help='Break duration in minutes (default: 10)')
    parser.add_argument('--cycles', '-c', type=int, default=None,
                        help='Number of cycles to complete (default: 4)')
    
    # Audio options
    parser.add_argument('--chime', type=str, default=None,
                        help='Path to .wav file for chime sound')
    parser.add_argument('--select-chime', action='store_true',
                        help='Select chime from available .wav files')
    
    # Template options
    parser.add_argument('--template', '-t', type=str, default=None,
                        help='Load settings from a saved template')
    parser.add_argument('--save-template', type=str, default=None, metavar='NAME',
                        help='Save current settings as a new template')
    parser.add_argument('--list-templates', action='store_true',
                        help='List all saved templates and exit')
    
    # Theme options
    parser.add_argument('--theme', type=str, default=None,
                        help='Color theme (cyberpunk, minimal, forest, ocean, sunset)')
    parser.add_argument('--list-themes', action='store_true',
                        help='List available themes and exit')
    parser.add_argument('--set-theme', type=str, default=None, metavar='THEME',
                        help='Set default theme in config and exit')
    parser.add_argument('--configure-theme', action='store_true',
                        help='(Legacy) Interactively select and set the default theme')
    parser.add_argument('--select-theme', action='store_true',
                        help='Select theme from available list interactively')
    
    # Custom Wizard
    parser.add_argument('--custom', action='store_true',
                        help='Run interactive custom session wizard')
    
    # Settings
    parser.add_argument('--settings', action='store_true',
                        help='Open interactive settings configuration menu')

    # Notification options
    parser.add_argument('--notifications', type=str, choices=['on', 'off'], default=None,
                        help='Enable or disable desktop notifications')
    parser.add_argument('--toggle-notifications', action='store_true',
                        help='Toggle notifications on/off and exit')
    
    args = parser.parse_args()
    
    # Handle info-only commands first
    if args.list_themes:
        console.print(get_theme_info())
        return

    if args.settings or args.configure_theme:
        configure_settings()
        return
    
    if args.list_templates:
        console.print(format_template_list())
        return
    
    if args.set_theme:
        from config_manager import set_theme
        if set_theme(args.set_theme):
            console.print(f"[{COLOR_SUCCESS}]✓ Default theme set to: {args.set_theme}[/{COLOR_SUCCESS}]")
        else:
            console.print(f"[{COLOR_INFO}]✗ Unknown theme: {args.set_theme}[/{COLOR_INFO}]")
            console.print(get_theme_info())
        return
    
    if args.toggle_notifications:
        from config_manager import toggle_notifications
        new_state = toggle_notifications()
        status = "enabled" if new_state else "disabled"
        console.print(f"[{COLOR_SUCCESS}]✓ Desktop notifications: {status}[/{COLOR_SUCCESS}]")
        return
    
    # Load defaults
    work = 25
    note = 5
    break_time = 10
    cycles = 4
    chime_file = CONFIG.get("default_chime")
    
    # Use global THEME name for initial setup if needed, but THEME dict is already loaded
    # We might need to reload THEME if user changes it via args
    current_theme_name = CONFIG.get("theme", DEFAULT_THEME)

    # 1. Custom Wizard (Lowest Priority - gets overwritten by CLI args if mixed, but usually sets the base)
    if args.custom:
        c_work, c_note, c_break, c_cycles, c_chime, c_theme = run_custom_wizard()
        work = c_work
        note = c_note
        break_time = c_break
        cycles = c_cycles
        chime_file = c_chime
        current_theme_name = c_theme

    # 2. Template (Overrides defaults/wizard)
    if args.template:
        template = load_template(args.template)
        if template:
            work = template.get("work", work)
            note = template.get("note", note)
            break_time = template.get("break", break_time)
            cycles = template.get("cycles", cycles)
            chime_file = template.get("chime", chime_file)
            current_theme_name = template.get("theme", current_theme_name)
            console.print(f"[{COLOR_SUCCESS}]✓ Loaded template: {template.get('name', args.template)}[/{COLOR_SUCCESS}]")
        else:
            console.print(f"[{COLOR_INFO}]Template '{args.template}' not found. Using defaults.[/{COLOR_INFO}]")
    
    # 3. CLI Arguments (Highest Priority overrides)
    if args.work is not None:
        work = args.work
    if args.note is not None:
        note = args.note
    if args.break_time is not None:
        break_time = args.break_time
    if args.cycles is not None:
        cycles = args.cycles
    if args.chime:
        chime_file = args.chime
    if args.theme:
        current_theme_name = args.theme
    
    # Interactive selections (Overrides previous)
    if args.select_chime:
        c = select_chime()
        if c: chime_file = c
        
    if args.select_theme:
        t = select_theme()
        if t: current_theme_name = t
    
    # Smart path resolution for chime file
    if chime_file and not os.path.exists(chime_file):
        # Check in sounds directory
        possible_path = os.path.join("sounds", chime_file)
        if os.path.exists(possible_path):
            chime_file = possible_path
            
    # RELOAD THEME if it changed from default/config
    # This ensures the Timer uses the correct colors
    # global THEME, COLOR_SEPARATOR, COLOR_HEADER, COLOR_INFO, COLOR_TIP, COLOR_SUCCESS # Moved to top of main
    THEME = get_theme(current_theme_name)
    COLOR_SEPARATOR = THEME["separator"]
    COLOR_HEADER = THEME["header"]
    COLOR_INFO = THEME["info"]
    COLOR_TIP = THEME["tip"]
    COLOR_SUCCESS = THEME["success"]
    COLOR_PROGRESS_LOW = THEME["progress_low"]
    COLOR_PROGRESS_MID = THEME["progress_mid"]
    COLOR_PROGRESS_HIGH = THEME["progress_high"]
    COLOR_PROGRESS_CRITICAL = THEME["progress_critical"]
    COLOR_CURSOR = THEME["cursor"]
    COLOR_PAUSED = THEME["paused"]
    
    # Save template if requested
    if args.save_template:
        if save_template(args.save_template, work, note, break_time, cycles, 
                        chime_file, current_theme_name):
            console.print(f"[{COLOR_SUCCESS}]✓ Template saved: {args.save_template}[/{COLOR_SUCCESS}]")
        else:
            console.print(f"[red]✗ Failed to save template[/red]")
        return
    
    # Handle notification setting for this session
    if args.notifications:
        global NOTIFICATIONS_ENABLED
        NOTIFICATIONS_ENABLED = (args.notifications == 'on')
    
    # Create and start timer
    timer = PomodoroTimer(
        work_min=work,
        note_min=note,
        break_min=break_time,
        cycles=cycles,
        chime_file=chime_file
    )
    
    # Override notifications if specified
    if args.notifications:
        timer.notifications_enabled = (args.notifications == 'on')
    
    timer.start()


if __name__ == "__main__":
    main()
