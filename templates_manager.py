#!/usr/bin/env python3
"""
Template Manager for Pomodoro CLI
Handles saving, loading, and managing custom Pomodoro session templates.
Templates are stored as individual JSON files in the templates/ folder.
"""

import json
import os
from pathlib import Path
from typing import Optional

# Templates directory (same directory as script)
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Global cache for templates
_TEMPLATE_CACHE = None


def _populate_cache():
    """Load all templates from disk into the global cache."""
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return

    ensure_templates_dir()
    templates = []
    
    for file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                templates.append({
                    "name": data.get("name", file.stem),
                    "filename": file.stem,
                    "settings": data
                })
        except (json.JSONDecodeError, IOError):
            continue
    
    # Sort by name
    templates.sort(key=lambda x: x["name"].lower())
    _TEMPLATE_CACHE = templates


def ensure_templates_dir():
    """Create templates directory if it doesn't exist."""
    TEMPLATES_DIR.mkdir(exist_ok=True)


def get_template_path(name: str) -> Path:
    """Get the path for a template file."""
    # Sanitize name for filename
    safe_name = "".join(c if c.isalnum() or c in "_- " else "_" for c in name)
    safe_name = safe_name.strip().replace(" ", "_").lower()
    return TEMPLATES_DIR / f"{safe_name}.json"


def list_templates() -> list:
    """
    Return list of available templates with their settings.
    Returns: [{"name": str, "filename": str, "settings": dict}, ...]
    """
    _populate_cache()
    return _TEMPLATE_CACHE


def load_template(name: str) -> Optional[dict]:
    """
    Load a template by name or filename.
    Returns: dict with template settings or None if not found.
    """
    _populate_cache()
    
    name_lower = name.lower()
    
    # Try exact filename match first (case-insensitive)
    for t in _TEMPLATE_CACHE:
        if t["filename"].lower() == name_lower:
            return t["settings"].copy()

    # Try matching by template name (case-insensitive)
    for t in _TEMPLATE_CACHE:
        if t["name"].lower() == name_lower:
            return t["settings"].copy()
    
    return None


def save_template(name: str, work: int, note: int, break_time: int, 
                  cycles: int, chime: str = None, theme: str = None) -> bool:
    """
    Save a new template or overwrite existing one.
    Returns: True if saved successfully.
    """
    ensure_templates_dir()
    
    template = {
        "name": name,
        "work": work,
        "note": note,
        "break": break_time,
        "cycles": cycles
    }
    
    if chime:
        template["chime"] = chime
    if theme:
        template["theme"] = theme
    
    path = get_template_path(name)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)

        # Invalidate cache
        global _TEMPLATE_CACHE
        _TEMPLATE_CACHE = None

        return True
    except IOError:
        return False


def delete_template(name: str) -> bool:
    """Delete a template by name or filename."""
    global _TEMPLATE_CACHE
    _populate_cache()
    
    name_lower = name.lower()
    target_filename = None

    # Try exact filename match first
    for t in _TEMPLATE_CACHE:
        if t["filename"].lower() == name_lower:
            target_filename = t["filename"]
            break

    if not target_filename:
        # Try matching by template name
        for t in _TEMPLATE_CACHE:
            if t["name"].lower() == name_lower:
                target_filename = t["filename"]
                break

    if target_filename:
        path = TEMPLATES_DIR / f"{target_filename}.json"
        try:
            if path.exists():
                path.unlink()
                # Invalidate cache
                _TEMPLATE_CACHE = None
                return True
        except IOError:
            return False

    return False


def format_template_list() -> str:
    """Return formatted string listing all templates for display."""
    templates = list_templates()
    
    if not templates:
        return "No saved templates. Create one with --save-template option."
    
    lines = ["📋 Saved Templates:", ""]
    for i, t in enumerate(templates, 1):
        s = t["settings"]
        lines.append(f"  {i}. {t['name']}")
        lines.append(f"     Work: {s.get('work', 25)}m | Note: {s.get('note', 5)}m | "
                    f"Break: {s.get('break', 10)}m | Cycles: {s.get('cycles', 4)}")
        if s.get('theme'):
            lines.append(f"     Theme: {s.get('theme')}")
        lines.append("")
    
    return "\n".join(lines)


def get_template_by_index(index: int) -> Optional[dict]:
    """Get a template by its index in the list (1-based)."""
    templates = list_templates()
    if 1 <= index <= len(templates):
        return templates[index - 1]["settings"].copy()
    return None
