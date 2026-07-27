"""
commands/notes.py
"""

import subprocess


def add_note(content: str) -> str:
    """Creates a new note in Notes.app with the given content."""
    # TODO: build the AppleScript - "tell application "Notes"" then
    # "make new note with properties {body:"..."}"
    # (Notes uses "body" as the property name, not "name" or "summary")
    script = f'''
    tell application "Notes"
        tell folder "Notes"
            make new note with properties {{body:"{content}"}}
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return "Sorry, I couldn't add your notes"


    return "Succesfully added to notes"