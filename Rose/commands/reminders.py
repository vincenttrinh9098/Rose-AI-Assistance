

import subprocess

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

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return "Sorry, I couldn't make that reminder for you"

    return f"Added a reminder: {title}"