"""
commands/steam.py
"""

import webbrowser
import json

from core.paths import path_for
STEAM_GAMES_PATH = path_for("config", "steam_games.json")

try:
    with open(STEAM_GAMES_PATH) as f:
        _games = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: couldn't load {STEAM_GAMES_PATH}: {e}")
    _games = {}


def launch_game(name: str) -> str:
    """Launches a Steam game by name, looked up in config/steam_games.json."""
    app_id = _games.get(name.lower())
    if app_id is None:
        return f"I couldn't find a game called {name} in your Steam library config"
    webbrowser.open(f"steam://run/{app_id}")
    return f"Launching {name}"