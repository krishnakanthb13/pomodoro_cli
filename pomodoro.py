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
from datetime import datetime
from pathlib import Path
import queue
import warnings
import subprocess
import platform

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
PHRASE_OPTION = 3  # 1: Goals, 2: Focus/Leap, 3: Adventure (Default)

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
            
            # Move cursor UP to the gap line, print the note, and restore the gap
            
            # Calculate how many lines the current timer display occupies
            try:
                term_cols = os.get_terminal_size().columns
            except OSError:
                term_cols = 80
            
            # Calculate visual lines (subtract 1 for leading \r)
            vis_len = max(0, self.last_display_length - 1)
            lines_occupied = max(1, (vis_len + term_cols - 1) // term_cols)
            
            # Clear the current (bottom-most) line
            sys.stdout.write('\r' + ' ' * (term_cols - 1) + '\r')
            
            # Move up past the timer block
            for _ in range(lines_occupied):
                sys.stdout.write('\033[F')
            
            # Print the note
            print(f" ✓ Added: {note_text[:40]}{'...' if len(note_text) > 40 else ''}")
            
            # Create the new gap line (and ensure it's clean)
            sys.stdout.write(' ' * (term_cols - 1)) # Clear line logic
            sys.stdout.write('\r') # Back to start
            sys.stdout.write('\n') # Move to the next line
            sys.stdout.flush()
    
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

        print(f"\n{'─'*60}")
        print(header_text)
        print(f"{'─'*60}")
        print()
        
        goal = input(input_prompt).strip()
        
        if goal:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(self.notes_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{timestamp} (CYCLE {cycle} of {self.cycles} - GOAL): {goal}\n")
            print(f"✓ Goal saved successfully!")
        else:
            print("No goal set.")
        
        # Brief countdown to prepare (no extra Enter needed)
        print("Starting in: ", end="", flush=True)
        for i in range(5, 0, -1):
            print(f"{i}...", end="", flush=True)
            time.sleep(1)
        print(" GO!")
        
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
        
        print(f"\n{'='*60}")
        print(f"  {phase_name.upper()} TIME STARTED")
        print(f"{'='*60}")
        print("Type notes anytime and press Enter to save them.")
        print() # Permanent gap after instructions
        print() # Initial gap above the timer
        
        while remaining > 0 and not self.stop_timer:
            # Process any queued notes
            self.process_notes()
            
            mins, secs = divmod(remaining, 60)
            timer_display = f"\r{phase_name} time: {mins:02d}:{secs:02d} remaining >> {self.line_buffer}"
            # Update terminal title
            sys.stdout.write(f"\033]2;{phase_name}: {mins:02d}:{secs:02d} remaining\007")
            # Pad with spaces to clear any old characters
            padded_display = timer_display + " " * max(0, self.last_display_length - len(timer_display))
            self.last_display_length = len(timer_display)
            sys.stdout.write(padded_display)
            sys.stdout.flush()
            
            # Update display 50 times per second for smoother typing/backspacing
            # but only decrement timer once per second
            for _ in range(50):
                if self.stop_timer:
                    break
                time.sleep(0.02)
                # Process any queued notes (typing happens here)
                self.process_notes()
                
                timer_display = f"\r{phase_name} time: {mins:02d}:{secs:02d} remaining >> {self.line_buffer}"
                padded_display = timer_display + " " * max(0, self.last_display_length - len(timer_display))
                self.last_display_length = len(timer_display)
                sys.stdout.write(padded_display)
                sys.stdout.flush()
            
            remaining -= 1
        
        if not self.stop_timer:
            sys.stdout.write(f"\r{phase_name} time: 00:00 - COMPLETED!{' '*20}\n")
            sys.stdout.write("="*60 + "\n")
            sys.stdout.flush()
            self.play_chime()
    
    def start(self):
        """Start the Pomodoro timer cycles"""
        print("\n" + "="*60)
        print("  🍅 POMODORO TIMER STARTED")
        print("="*60)
        print(f"Cycles: {self.cycles}", end=" | ", flush=True)
        print(f"Work: {self.work_duration//60} min | Note: {self.note_duration//60} min | Break: {self.break_duration//60} min")
        if self.chime_file:
            print(f"Chime: {self.chime_file}", end=" | ", flush=True)
        if AUDIO_AVAILABLE:
            print(f"Audio: {AUDIO_METHOD}")
        print(f"Notes saved to: {self.notes_file}")
        print("💡 TIP: Press Ctrl+C at any time to stop the timer.")
        print("="*60)
        
        # Start ONE note-listening thread for the entire session
        note_thread = threading.Thread(target=self.listen_for_notes, daemon=True)
        note_thread.start()
        
        try:
            for cycle in range(1, self.cycles + 1):
                print(f"\n🔄 CYCLE {cycle} of {self.cycles}")
                
                # Ask for goal (note-taking disabled inside this function)
                self.ask_for_goal(cycle)
                
                # Work phase
                self.run_timer(self.work_duration, "Work")
                
                # Note-taking phase
                self.run_timer(self.note_duration, "Journal")
                
                # Break phase (skip on last cycle)
                if cycle < self.cycles:
                    self.run_timer(self.break_duration, "Break")
            
            print("\n\n" + "="*60)
            print("  🎉 ALL CYCLES COMPLETED! Great work!")
            print("="*60)
            print(f"📄 All notes saved to: {self.notes_file}")
            sys.stdout.write("\033]2;Pomodoro Timer: Completed!\007")
            self.play_chime()
            self.open_notes_file()
            
        except KeyboardInterrupt:
            print("\n\n⏸️ Timer stopped by user (Ctrl+C pressed)")
            print(f"📄 Notes saved to: {self.notes_file}")
            # input("\nPress Enter to open notes file and exit...")
            self.open_notes_file()
            time.sleep(0.5)  # Give threads time to clean up
        finally:
            self.stop_timer = True
            time.sleep(0.5)  # Give threads time to clean up


def find_wav_files():
    """Find all .wav files in current and subdirectories"""
    wav_files = []
    current_dir = Path('.')
    
    # Search current directory and one level down
    for pattern in ['*.wav', '*/*.wav']:
        wav_files.extend(current_dir.glob(pattern))
    
    return sorted([str(f) for f in wav_files])


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


def main():
    parser = argparse.ArgumentParser(
        description='CLI Pomodoro Timer with note-taking capability',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run (25 min work, 5 min notes, 10 min break, 4 cycles)
    python pomodoro.py -w 25 -n 5 -b 10 -c 4

    # With a custom sound file
    python pomodoro.py -w 25 -n 5 -b 10 -c 4 --chime mysound.wav

    # Interactive sound selection
    python pomodoro.py -w 25 -n 5 -b 10 -c 4 --select-chime

    # Quick test (1 min each phase)
    python pomodoro.py -w 1 -n 1 -b 1 -c 2
        """
    )
    
    parser.add_argument('--work', '-w', type=int, default=25,
                        help='Work duration in minutes (default: 25)')
    parser.add_argument('--note', '-n', type=int, default=5,
                        help='Note-taking duration in minutes (default: 5)')
    parser.add_argument('--break', '-b', type=int, default=10, dest='break_time',
                        help='Break duration in minutes (default: 10)')
    parser.add_argument('--cycles', '-c', type=int, default=4,
                        help='Number of cycles to complete (default: 4)')
    parser.add_argument('--chime', type=str, default=None,
                        help='Path to .wav file for chime sound')
    parser.add_argument('--select-chime', action='store_true',
                        help='Select chime from available .wav files')
    
    args = parser.parse_args()
    
    # Handle chime selection
    chime_file = args.chime
    if args.select_chime:
        chime_file = select_chime()
    
    # Create and start timer
    timer = PomodoroTimer(
        work_min=args.work,
        note_min=args.note,
        break_min=args.break_time,
        cycles=args.cycles,
        chime_file=chime_file
    )
    
    timer.start()


if __name__ == "__main__":
    main()