"""
core/long_term_memory.py

Persistent, file-backed long-term memory - facts about the user that
should be remembered indefinitely, unlike short-term conversation memory.
"""

import json

from core.paths import path_for
MEMORY_PATH = path_for("config", "long_term_memory.json")

DEFAULT_MEMORY = {
    "identity": {},
    "goals": {},
    "interests": {},
    "technical": {},
    "preferences": {},
    "knowledge": {},
    "projects": [],
    "lifestyle": {},
}


def load_memory() -> dict:
    try:
        with open(MEMORY_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_MEMORY)


def save_memory(memory: dict) -> None:
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)


def remember_fact(category: str, key: str, value) -> None:
    """Stores a fact under a category (e.g. 'identity', 'preferences')."""
    memory = load_memory()

    if category not in memory:
        memory[category] = {}

    if category == "projects":
        # projects is a list, not a dict - append instead
        if value not in memory["projects"]:
            memory["projects"].append(value)
    else:
        memory[category][key] = value

    save_memory(memory)


def format_memory_for_prompt() -> str:
    """Returns a compact, human-readable summary of stored facts, for injecting into prompts."""
    memory = load_memory()
    lines = []

    for category, contents in memory.items():
        if not contents:
            continue
        if isinstance(contents, dict):
            for key, value in contents.items():
                lines.append(f"{key}: {value}")
        elif isinstance(contents, list):
            for item in contents:
                lines.append(f"project: {item}")

    if not lines:
        return ""

    return "Known facts about the user: " + "; ".join(lines)