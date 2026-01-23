#!/usr/bin/env python3
"""
Theme definitions for Pomodoro CLI
Provides multiple color schemes for terminal UI customization.
Themes are stored as individual JSON files in the themes/ folder.
"""

import json
import os
from pathlib import Path

# Themes directory (same directory as script)
THEMES_DIR = Path(__file__).parent / "themes"

# Default theme
DEFAULT_THEME = "cyberpunk"

def ensure_themes_dir():
    """Create themes directory if it doesn't exist."""
    THEMES_DIR.mkdir(exist_ok=True)

def load_all_themes():
    """Load all themes from the themes directory."""
    ensure_themes_dir()
    themes = {}
    
    # Defaults in case of error or empty dir, but mainly relying on files
    # If no files, we could provide fallback, but let's assume files are present
    
    for file in THEMES_DIR.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Use filename stem as ID (same as before: "cyberpunk", "forest", etc)
                theme_id = file.stem.lower()
                themes[theme_id] = data
        except (json.JSONDecodeError, IOError):
            continue
            
    return themes

def get_theme(name: str) -> dict:
    """Get a theme by name, returns default if not found."""
    themes = load_all_themes()
    return themes.get(name.lower(), themes.get(DEFAULT_THEME, {}))


def list_themes() -> list:
    """Return list of available theme names."""
    themes = load_all_themes()
    return list(themes.keys())


def get_theme_info() -> str:
    """Return formatted string of all themes with descriptions."""
    themes = load_all_themes()
    lines = ["Available Themes:", ""]
    for key, theme in themes.items():
        marker = " (default)" if key == DEFAULT_THEME else ""
        lines.append(f"  • {theme.get('name', key.capitalize())}{marker}: {theme.get('description', '')}")
    return "\n".join(lines)
