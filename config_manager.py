#!/usr/bin/env python3
"""
Configuration Manager for Pomodoro CLI
Handles loading, saving, and accessing persistent settings from config.json
"""

import json
import os
from pathlib import Path

# Config file path (same directory as script)
CONFIG_FILE = Path(__file__).parent / "config.json"

# Default configuration values
DEFAULT_CONFIG = {
    "theme": "cyberpunk",
    "notifications_enabled": True,
    "default_chime": "sounds/gentle_chime.wav",
    "phrase_option": 3,
    "cursor_blink_speed": 20
}


def load_config() -> dict:
    """Load configuration from config.json, creating it with defaults if missing."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Merge with defaults to ensure all keys exist
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def get_setting(key: str, default=None):
    """Get a single setting value."""
    config = load_config()
    return config.get(key, default)


def set_setting(key: str, value) -> bool:
    """Set a single setting value and save."""
    config = load_config()
    config[key] = value
    return save_config(config)


def toggle_notifications() -> bool:
    """Toggle notifications on/off and return new state."""
    config = load_config()
    config["notifications_enabled"] = not config.get("notifications_enabled", True)
    save_config(config)
    return config["notifications_enabled"]


def set_theme(theme_name: str) -> bool:
    """Set the current theme."""
    from themes import list_themes
    if theme_name.lower() in list_themes():
        return set_setting("theme", theme_name.lower())
    return False
