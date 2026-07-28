"""
commands/vscode.py
"""

import subprocess
import json

with open("config/projects.json") as f:
    _projects = json.load(f)


def open_project(name: str) -> str:
    """Opens a project folder in VS Code, looked up by name in config/projects.json."""
    path = _projects.get(name.lower())

    if path is None:
        return f"I don't know a project called {name}"

    subprocess.run(["code", path])
    return f"Opening {name} in VS Code"