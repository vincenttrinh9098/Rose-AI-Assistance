

import subprocess
from commands.applescript import run_applescript


def add_reminder(title: str, date: str = None, time: str = None) -> str:
    if date and time:
        script = f'''
        tell application "Reminders"
            tell list "Reminders"
                make new reminder with properties {{name:"{title}", due date:date "{date} {time}"}}
            end tell
        end tell
        '''
    else:
        script = f'''
        tell application "Reminders"
            tell list "Reminders"
                make new reminder with properties {{name:"{title}"}}
            end tell
        end tell
        '''

    success, output = run_applescript(script, app_name="Reminders")
    if not success:
        print(output)
        return "Sorry, I couldn't make that reminder for you"
    return f"Added a reminder: {title}"