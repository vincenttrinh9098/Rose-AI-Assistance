"""
commands/applications.py

Generic app launcher, driven entirely by config/apps.json.
Adding a new app should mean editing the JSON file, not writing new Python.
"""

import json
import subprocess
import webbrowser

APPS_CONFIG_PATH = "config/apps.json"

# TODO: load the JSON config once here, at import time (same pattern as _model in audio_io.py -
# don't re-read the file from disk on every single call)
# json.load(open(path)) reads and parses a JSON file into a Python dict in one step
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

    # Step 1: use _find_app() to look up the app
    app = _find_app(name) 

    # Step 2: handle the "not found" case first
    # if app is None, return a string saying you don't know that app
    if app is None:
        return "Sorry, I did not find that app within the system"
    
    # Step 3: branch on app["type"]
    # - if "url": use webbrowser.open(app["target"])
    # - if "native_app": use subprocess.run(["open", "-a", app["target"]])
    #   ("open -a AppName" is the macOS command to launch an installed application by name)

    if(app['type'] == 'url'):
        webbrowser.open(app["target"])
    elif(app['type'] == 'native_app'):
        subprocess.run(["open", "-a", app["target"]])



    # Step 4: return a confirmation string either way, e.g. f"Opening {name} for you"
    return f"Opening {name} for you"


def control_app(name: str, control_action: str) -> str:
    """
    Looks up `name` in the config, finds the AppleScript command for `control_action`
    (e.g. "play", "pause", "quit"), and runs it.
    """

    # TODO: use _find_app(name) same as open_app() does
    app = _find_app(name) 

    # TODO: if app is None, return "app not found" message
    if app is None:
        return "Sorry, I did not find that app within the system"


    # TODO: check if app has a "controls" key at all, and if control_action exists within it
    # (not every app in your config will have controls defined - browser-type apps won't)
    # if missing, return a "that app doesn't support that control" message
    # TODO: get the actual AppleScript string: app["controls"][control_action]

    # TODO: run it with subprocess.run(["osascript", "-e", script])
    # (same pattern as get_active_chrome_url())

    controls = app.get("controls")
    if controls is None or control_action not in controls:
        return "that app doesn't support that control"

    script = controls[control_action]
    subprocess.run(["osascript", "-e", script])

    # TODO: return a confirmation string, e.g. f"{control_action} on {name}"
    return f"{control_action} on {name}"