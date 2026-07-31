"""
commands/applescript.py

Shared helper for running AppleScript against apps that may not already be
running - launches the app first, waits briefly, then runs the script with
a timeout and clean error handling.
"""

import subprocess
import time


def run_applescript(script: str, app_name: str = None, timeout: int = 10) -> tuple[bool, str]:
    """
    Runs an AppleScript string, optionally ensuring `app_name` is launched first.
    Returns (success, output_or_error).
    """
    if app_name:
        subprocess.run(["open", "-a", app_name])
        time.sleep(1)

    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"Timed out waiting for {app_name or 'AppleScript'}"

    if result.returncode != 0:
        return False, result.stderr.strip()

    return True, result.stdout.strip()