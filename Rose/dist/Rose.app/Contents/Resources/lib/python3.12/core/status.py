"""
core/status.py

Tracks Rose's current state (idle/listening/speaking) in a small shared file,
so the GUI (a separate process) can display it live.
"""

import json

from core.paths import path_for
STATUS_PATH = path_for("logs", "status.json")

def set_status(state: str) -> None:
    """state: 'idle', 'listening', or 'speaking'"""
    with open(STATUS_PATH, "w") as f:
        json.dump({"state": state}, f)


def get_status() -> str:
    try:
        with open(STATUS_PATH) as f:
            return json.load(f).get("state", "idle")
    except (FileNotFoundError, json.JSONDecodeError):
        return "idle"