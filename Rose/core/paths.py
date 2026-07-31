"""
core/paths.py

Provides the correct base directory for config/logs/screenshots,
whether running as a normal script or as a bundled .app.
"""

import sys
import os


def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        # running inside a py2app bundle - use a writable, persistent location
        base = os.path.expanduser("~/Library/Application Support/Rose")
        os.makedirs(base, exist_ok=True)
        return base
    else:
        # running normally - use the project directory
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path_for(*parts) -> str:
    """Builds a path relative to the correct base directory (e.g. path_for('config', 'apps.json'))."""
    full_path = os.path.join(get_base_dir(), *parts)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path