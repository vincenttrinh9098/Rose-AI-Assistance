"""
commands/applications.py

Generic app launcher, driven entirely by config/apps.json.
Adding a new app should mean editing the JSON file, not writing new Python.
"""

import json
import subprocess
import webbrowser

from ai.text_analysis import guess_url



APPS_CONFIG_PATH = "config/apps.json"
_apps = json.load(open(APPS_CONFIG_PATH))


def _find_app(name: str) -> dict | None:
    """
    Given a spoken app name (e.g. "spotify" or "music"), find the matching
    entry in _apps by checking its "aliases" list. Returns the app's dict,
    or None if nothing matches.
    """
    if name is None:
        return None
    name = name.lower()

    for app_name, app_info in _apps.items():
        if name in app_info['aliases']:
            return app_info


    return None


def open_app(name: str) -> str:
    """
    Looks up `name` in the config and opens it the correct way based on its "type".
    Returns a string to be spoken back to the user.
    """
    if not name:
        return "I'm not sure what you want me to open"
    
    app = _find_app(name) 

    if app is not None:
        if(app['type'] == 'url'):
            webbrowser.open(app["target"])
        elif(app['type'] == 'native_app'):
            subprocess.run(["open", "-a", app["target"]])
        return f"Opening {name} for you"

    guessed_url = guess_url(name)
    if guessed_url:
        webbrowser.open(guessed_url)
        return f"Opening {name}"


    


def control_app(name: str, control_action: str) -> str:
    """
    Looks up `name` in the config, finds the AppleScript command for `control_action`
    (e.g. "play", "pause", "quit"), and runs it.
    """

    app = _find_app(name) 

    if app is None:
        return "Sorry, I did not find that app within the system"

    controls = app.get("controls")
    if controls is None or control_action not in controls:
        return "that app doesn't support that control"

    script = controls[control_action]
    subprocess.run(["osascript", "-e", script])

    return f"{control_action} on {name}"