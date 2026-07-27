"""
core/pending_action.py

Holds a single pending action awaiting confirmation - e.g. "send a message to X" -
so the NEXT utterance can be interpreted as a yes/no confirmation instead of a
brand new command.
"""

_pending = None  # will hold a dict like {"type": "send_message", "recipient": ..., "content": ...}


def set_pending(action_type: str, **kwargs) -> None:
    """Stores a pending action awaiting confirmation."""
    global _pending
    _pending = {"type": action_type, **kwargs}


def get_pending() -> dict | None:
    """Returns the current pending action, or None if there isn't one."""
    return _pending


def clear_pending() -> None:
    """Clears the pending action - call this after it's confirmed or rejected."""
    global _pending
    _pending = None