"""
commands/messages.py
"""

import subprocess
from commands.applescript import run_applescript
import time

def send_message(recipient: str, content: str) -> str:
    subprocess.run(["open", "-a", "Contacts"])
    subprocess.run(["open", "-a", "Messages"])
    time.sleep(1)

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

    success, output = run_applescript(script)  # no single app_name, since we launched both manually above
    if not success:
        print(output)
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
    success, output = run_applescript(script, app_name="Contacts")
    if not success or not output:
        return []
    return [n.strip() for n in output.split(",")]