"""
commands/steam.py
"""

import webbrowser
import json

with open("config/steam_games.json") as f:
    _games = json.load(f)


def launch_game(name: str) -> str:
    """Launches a Steam game by name, looked up in config/steam_games.json."""
    app_id = _games.get(name.lower())
    if app_id is None:
        return f"I couldn't find a game called {name} in your Steam library config"
    webbrowser.open(f"steam://run/{app_id}")
    return f"Launching {name}"