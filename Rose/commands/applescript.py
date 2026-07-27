"""
commands/applescript.py

Shared helper for running AppleScript commands and checking success/failure.
Used by any Mac-app-control feature: calendar.py, applications.py's control_app, etc.
"""

import subprocess


def run_applescript(script: str) -> tuple[bool, str]:
    """
    Runs an AppleScript string. Returns (success, message) -
    message is either a success confirmation or the error text.
    """
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    success = result.returncode == 0
    message = result.stderr.strip() if not success else ""
    return success, message