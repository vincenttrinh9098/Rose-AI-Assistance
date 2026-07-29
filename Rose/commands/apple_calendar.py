import subprocess
from commands.applescript import run_applescript


def add_apple_calendar_event(title: str, date: str, time: str, duration_hours:float) -> str:
    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set startDate to date "{date} {time}"
            set endDate to startDate + ({duration_hours} * hours)
            make new event with properties {{summary:"{title}", start date:startDate, end date:endDate}}
        end tell
    end tell
    '''
    success, output = run_applescript(script, app_name="Calendar")
    if not success:
        print(output)
        return "Sorry, I couldn't create that calendar event"
    return "Successfully made a calendar date for you"


def list_events_for_date(date_str: str) -> str:
    """Returns a spoken-friendly summary of Calendar events for a given date (e.g. 'July 29, 2026')."""

    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set dayStart to date "{date_str}"
            set time of dayStart to 0
            set dayEnd to dayStart + (1 * days)
            set matchingEvents to (every event whose start date is greater than or equal to dayStart and start date is less than dayEnd)
            set eventList to {{}}
            repeat with anEvent in matchingEvents
                set end of eventList to (summary of anEvent as string) & "|" & (start date of anEvent as string)
            end repeat
            return eventList
        end tell
    end tell
    '''

    success, output = run_applescript(script, app_name="Calendar")
    if not success:
        print(output)
        return "Sorry, I couldn't check your calendar"

    if not output.strip():
        return f"You have no apple calendar events on {date_str}"

    return f"Here's what's on your calendar for {date_str}: {output.strip()}"