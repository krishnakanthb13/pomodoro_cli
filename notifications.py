#!/usr/bin/env python3
"""
Desktop Notifications for Pomodoro CLI
Cross-platform desktop notifications using plyer library.
Falls back silently if plyer is not installed.
"""

import os
import sys

# Try to import plyer for notifications
NOTIFICATIONS_AVAILABLE = False
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    pass


def notify(title: str, message: str, timeout: int = 5) -> bool:
    """
    Send a desktop notification.
    
    Args:
        title: Notification title
        message: Notification body text
        timeout: Seconds to display (default 5)
    
    Returns:
        True if notification was sent, False otherwise
    """
    if not NOTIFICATIONS_AVAILABLE:
        return False
    
    try:
        # Resolve icon path - Prioritize .ico for Windows to avoid plyer errors
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        icon_path = None
        
        if os.path.exists(assets_dir):
            # Try .ico first
            ico_path = os.path.join(assets_dir, "pomodoro.ico")
            png_path = os.path.join(assets_dir, "pomodoro.png")
            
            if os.path.exists(ico_path):
                icon_path = ico_path
            elif os.path.exists(png_path):
                icon_path = png_path

        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Pomodoro CLI",
                app_icon=icon_path,
                timeout=timeout
            )
            return True
        except Exception as e:
            # If it failed (likely due to icon format on Windows), try without icon
            if icon_path:
                try:
                    notification.notify(
                        title=title,
                        message=message,
                        app_name="Pomodoro CLI",
                        app_icon=None,
                        timeout=timeout
                    )
                    return True
                except Exception:
                    return False
            return False
    except Exception:
        return False


def notify_phase_start(phase_name: str, duration_mins: int) -> bool:
    """Notify when a phase starts."""
    icons = {
        "Work": "🎯",
        "Journal": "📝",
        "Break": "☕"
    }
    icon = icons.get(phase_name, "🍅")
    return notify(
        f"{icon} {phase_name} Phase Started",
        f"{duration_mins} minutes - Stay focused!"
    )


def notify_phase_complete(phase_name: str) -> bool:
    """Notify when a phase completes."""
    icons = {
        "Work": "✅",
        "Journal": "📓",
        "Break": "⏰"
    }
    icon = icons.get(phase_name, "🔔")
    
    messages = {
        "Work": "Great work! Time for journaling.",
        "Journal": "Notes captured! Time for a break.",
        "Break": "Break's over! Ready for the next cycle?"
    }
    msg = messages.get(phase_name, "Phase complete!")
    
    return notify(f"{icon} {phase_name} Complete!", msg)


def notify_cycle_complete(cycle: int, total_cycles: int) -> bool:
    """Notify when a cycle completes."""
    if cycle == total_cycles:
        return notify(
            "🎉 All Cycles Complete!",
            f"You completed all {total_cycles} cycles. Amazing work!"
        )
    return notify(
        f"🔄 Cycle {cycle}/{total_cycles} Complete",
        f"Starting cycle {cycle + 1}..."
    )


def notify_session_start(cycles: int) -> bool:
    """Notify when a Pomodoro session starts."""
    return notify(
        "🍅 Pomodoro Session Started",
        f"Let's do this! {cycles} cycles to complete."
    )


def notify_paused() -> bool:
    """Notify when timer is paused."""
    return notify("⏸️ Timer Paused", "Press Ctrl+P to resume.")


def notify_resumed() -> bool:
    """Notify when timer is resumed."""
    return notify("▶️ Timer Resumed", "Back to work!")


def is_available() -> bool:
    """Check if notifications are available."""
    return NOTIFICATIONS_AVAILABLE


def get_status() -> str:
    """Get notification system status for display."""
    if NOTIFICATIONS_AVAILABLE:
        return "Desktop notifications: Enabled"
    return "Desktop notifications: Unavailable (install plyer: pip install plyer)"
