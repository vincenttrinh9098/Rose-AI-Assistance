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


CANCEL_PATH = path_for("logs", "cancel_signal.json")

def request_cancel():
    with open(CANCEL_PATH, "w") as f:
        json.dump({"cancel": True}, f)

def check_and_clear_cancel() -> bool:
    try:
        with open(CANCEL_PATH) as f:
            data = json.load(f)
        if data.get("cancel"):
            with open(CANCEL_PATH, "w") as f:
                json.dump({"cancel": False}, f)
            return True
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return False
