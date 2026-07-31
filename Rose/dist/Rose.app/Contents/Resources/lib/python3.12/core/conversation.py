"""
core/conversation.py

Tracks short-term conversation history for general_question(), so follow-up
questions like "should I sell it" can resolve to earlier context ("my car").
Automatically expires after a period of inactivity.

File-backed so voice (main.py) and GUI text input (gui.py) share the same
conversation memory, since they run as separate processes.
"""

import json
from datetime import datetime, timedelta

EXPIRY_MINUTES = 5
from core.paths import path_for
HISTORY_PATH = path_for("logs", "short_term_memory.json")


def _load() -> dict:
    try:
        with open(HISTORY_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"history": [], "last_updated": None}


def _save(history: list, last_updated: datetime) -> None:
    with open(HISTORY_PATH, "w") as f:
        json.dump({
            "history": history,
            "last_updated": last_updated.isoformat() if last_updated else None,
        }, f)


def get_history() -> list:
    """Returns the current conversation history, clearing it first if it's expired."""
    data = _load()
    history = data.get("history", [])
    last_updated_str = data.get("last_updated")
    last_updated = datetime.fromisoformat(last_updated_str) if last_updated_str else None

    if last_updated is None or (datetime.now() - last_updated) > timedelta(minutes=EXPIRY_MINUTES):
        history = []
        _save(history, None)

    return history


def add_exchange(user_text: str, assistant_text: str) -> None:
    """Appends a user message + assistant reply to history, updates the timestamp."""
    if not user_text or not user_text.strip():
        return  # don't save empty exchanges at all

    data = _load()
    history = data.get("history", [])

    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": assistant_text})

    _save(history, datetime.now())


def clear() -> None:
    """Manually clears history."""
    _save([], None)