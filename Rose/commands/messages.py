"""
commands/messages.py
"""

import subprocess


def send_message(recipient: str, content: str) -> str:
    """Sends an iMessage to `recipient` (an exact Contacts full name) with `content`."""

    script = f'''
    tell application "Contacts"
        set thePerson to first person whose name is "{recipient}"
        set theNumber to value of first phone of thePerson
    end tell

    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy theNumber of targetService
        send "{content}" to targetBuddy
    end tell
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return "Sorry, I couldn't send that message"

    return "Successfully sent message"


def find_contact_matches(name: str) -> list[str]:
    """Returns a list of full names in Contacts matching `name`."""
    script = f'''
    tell application "Contacts"
        set matchingPeople to every person whose name contains "{name}"
        set nameList to {{}}
        repeat with aPerson in matchingPeople
            set end of nameList to (name of aPerson as string)
        end repeat
        return nameList
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if not result.stdout.strip():
        return []
    return [n.strip() for n in result.stdout.strip().split(",")]