import sys
from unittest.mock import MagicMock
import time
import threading
from rich.console import Console

# Import the module
import pomodoro

# Force console to output to stdout even if not tty
pomodoro.console = Console(force_terminal=True, width=80)

# Patch select
pomodoro.select = MagicMock()
pomodoro.select.select.return_value = ([], [], [])

def test_run():
    print("Initializing Timer...")
    timer = pomodoro.PomodoroTimer(work_min=1, note_min=1, break_min=1, cycles=1, chime_file=None)

    # Override durations for quick test
    timer.work_duration = 3 # 3 seconds

    # Mock play_chime
    timer.play_chime = MagicMock()

    # Start note listener thread (daemon)
    note_thread = threading.Thread(target=timer.listen_for_notes, daemon=True)
    note_thread.start()

    print("Running Timer logic...")
    timer.run_timer(3, "TestWork")

    timer.stop_timer = True
    print("\nTest Complete.")

if __name__ == "__main__":
    test_run()
