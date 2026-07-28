"""
commands/applications.py

Generic app launcher, driven entirely by config/apps.json.
Adding a new app should mean editing the JSON file, not writing new Python.
"""

import json
import subprocess
import webbrowser

APPS_CONFIG_PATH = "config/apps.json"
_apps = json.load(open(APPS_CONFIG_PATH))


def _find_app(name: str) -> dict | None:
    """
    Given a spoken app name (e.g. "spotify" or "music"), find the matching
    entry in _apps by checking its "aliases" list. Returns the app's dict,
    or None if nothing matches.
    """
    name = name.lower()

    # TODO: loop over _apps.values() (each value is one app's dict, like the
    # youtube/google/spotify entries in the JSON)
    # for each app entry, check if `name` is in that entry's "aliases" list
    # if it matches, return that entry
    # if the loop finishes with no match, return None
    for app_name, app_info in _apps.items():
        if name in app_info['aliases']:
            return app_info


    return None


def open_app(name: str) -> str:
    """
    Looks up `name` in the config and opens it the correct way based on its "type".
    Returns a string to be spoken back to the user.
    """

    app = _find_app(name) 
    if app is None:
        return "Sorry, I did not find that app within the system"


    if(app['type'] == 'url'):
        webbrowser.open(app["target"])
    elif(app['type'] == 'native_app'):
        subprocess.run(["open", "-a", app["target"]])

    return f"Opening {name} for you"


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