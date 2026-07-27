

import subprocess


def add_calendar_event(title: str, date: str, time: str, duration_hours:float) -> str:
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

def list_todays_events() -> str:
    """Returns a spoken-friendly summary of today's Calendar events."""

    script = '''
    tell application "Calendar"
        tell calendar "Home"
            set todayStart to current date
            set time of todayStart to 0
            set todayEnd to todayStart + (1 * days)
            set todaysEvents to (every event whose start date is greater than or equal to todayStart and start date is less than todayEnd)
            set eventList to {}
            repeat with anEvent in todaysEvents
                set end of eventList to (summary of anEvent as string) & "|" & (start date of anEvent as string)
            end repeat
            return eventList
        end tell
    end tell
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return "Sorry, I couldn't check your calendar"

    if not result.stdout.strip():
        return "You have no events today"

    return f"Here's what's on your calendar today: {result.stdout.strip()}"