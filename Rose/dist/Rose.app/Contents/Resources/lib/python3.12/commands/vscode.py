"""
commands/vscode.py
"""

import subprocess
import json


from core.paths import path_for
APPS_CONFIG_PATH = path_for("config", "projects.json")

try:
    with open(APPS_CONFIG_PATH) as f:
        _projects = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: couldn't load {APPS_CONFIG_PATH}: {e}")
    _projects = {}


def open_project(name: str) -> str:
    """Opens a project folder in VS Code, looked up by name in config/projects.json."""
    path = _projects.get(name.lower())

    if path is None:
        return f"I don't know a project called {name}"

    subprocess.run(["code", path])
    return f"Opening {name} in VS Code"