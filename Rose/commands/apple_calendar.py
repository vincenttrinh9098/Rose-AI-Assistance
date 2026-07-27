


import subprocess


def add_event(title: str, date: str, time: str, duration_hours:float) -> str:
    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set startDate to date "{date} {time}"
            set endDate to startDate + ({duration_hours} * hours)
            make new event with properties {{summary:"{title}", start date:startDate, end date:endDate}}
        end tell
    end tell
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return "Sorry, I couldn't create that calendar event"

    return "Successfully made a calendar date for you"