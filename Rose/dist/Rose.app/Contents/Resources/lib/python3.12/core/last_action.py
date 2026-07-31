"""
core/last_action.py

Tracks the most recent action Rose took, so a garbled/ambiguous follow-up
can be reinterpreted in light of what was just attempted.
"""

import json

from core.paths import path_for
LAST_ACTION_PATH = path_for("logs", "last_action.json")


def set_last_action(action: str, query: str, result: str) -> None:
    with open(LAST_ACTION_PATH, "w") as f:
        json.dump({"action": action, "query": query, "result": result}, f)


def get_last_action() -> dict | None:
    try:
        with open(LAST_ACTION_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None