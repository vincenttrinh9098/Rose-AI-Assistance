"""
core/conversation.py

Tracks short-term conversation history for general_question(), so follow-up
questions like "should I sell it" can resolve to earlier context ("my PC").
Automatically expires after a period of inactivity.
"""

from datetime import datetime, timedelta

EXPIRY_MINUTES = 5

_history = []
_last_updated = None


def get_history() -> list:
    """Returns the current conversation history, clearing it first if it's expired."""
    global _history, _last_updated

    if _last_updated is None or (datetime.now() - _last_updated) > timedelta(minutes=EXPIRY_MINUTES):
        _history = []

    return _history


def add_exchange(user_text: str, assistant_text: str) -> None:
    """Appends a user message + assistant reply to history, updates the timestamp."""
    global _last_updated 

    _history.append({"role": "user", "content": user_text})
    _history.append({"role": "assistant", "content": assistant_text})

    _last_updated = datetime.now()

    return 


def clear() -> None:
    """Manually clears history - e.g. when a non-conversational action fires."""
    global _history, _last_updated
    _history = []
    _last_updated = None