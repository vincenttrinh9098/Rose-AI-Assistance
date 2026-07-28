"""
commands/steam.py
"""

import webbrowser
import json

APPS_CONFIG_PATH = "config/steam_games.json"

try:
    with open(APPS_CONFIG_PATH) as f:
        _games = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: couldn't load {APPS_CONFIG_PATH}: {e}")
    _games = {}


def launch_game(name: str) -> str:
    """Launches a Steam game by name, looked up in config/steam_games.json."""
    app_id = _games.get(name.lower())
    if app_id is None:
        return f"I couldn't find a game called {name} in your Steam library config"
    webbrowser.open(f"steam://run/{app_id}")
    return f"Launching {name}"