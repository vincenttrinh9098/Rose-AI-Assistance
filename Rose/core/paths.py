"""
core/paths.py

Provides the correct base directory for config/logs/screenshots,
whether running as a normal script or as a bundled .app.
"""

import sys
import os
import json
import shutil


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


DEFAULT_CONFIGS = {
    ("config", "apps.json"): {},
    ("config", "steam_games.json"): {},
    ("config", "projects.json"): {},
    ("config", "github_repos.json"): {},
    ("config", "search_sites.json"): {
        "google": "https://google.com/search?q={query}",
        "youtube": "https://youtube.com/results?search_query={query}",
    },
    ("config", "settings.json"): {"hotkey": "<cmd>+<shift>+0"},
    ("config", "long_term_memory.json"): {
        "identity": {}, "goals": {}, "interests": {}, "technical": {},
        "preferences": {}, "knowledge": {}, "projects": [], "lifestyle": {},
    },
}

BUNDLED_DEFAULTS = {
    ("config", "apps.json"): "apps.json",
    ("config", "search_sites.json"): "search_sites.json",
}


def _get_bundled_default_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "..", "Resources", "default_config")
    else:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")


def ensure_default_configs() -> None:
    """Creates any missing config files - using bundled real defaults where available,
    otherwise empty defaults. Safe to call every startup - never overwrites existing files."""
    bundled_dir = _get_bundled_default_dir()

    for (folder, filename), default_content in DEFAULT_CONFIGS.items():
        full_path = path_for(folder, filename)
        if os.path.exists(full_path):
            continue

        bundled_filename = BUNDLED_DEFAULTS.get((folder, filename))
        if bundled_filename:
            bundled_path = os.path.join(bundled_dir, bundled_filename)
            if os.path.exists(bundled_path):
                shutil.copy(bundled_path, full_path)
                print(f"Copied bundled default for {filename}")
                continue

        with open(full_path, "w") as f:
            json.dump(default_content, f, indent=2)
        print(f"Created empty default {filename}")