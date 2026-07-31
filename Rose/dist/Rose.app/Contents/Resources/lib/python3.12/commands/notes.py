"""
commands/notes.py
"""

import subprocess
from commands.applescript import run_applescript


def add_note(content: str) -> str:
    """Creates a new note in Notes.app with the given content."""

    script = f'''
    tell application "Notes"
        tell folder "Notes"
            make new note with properties {{body:"{content}"}}
        end tell
    end tell
    '''


    success, output = run_applescript(script, app_name="Notes")
    if not success:
        print(output)
        return "Sorry, I couldn't add your notes"
    return "Succesfully added to notes"