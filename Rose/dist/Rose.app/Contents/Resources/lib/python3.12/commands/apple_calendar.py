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


def find_events_for_edit(date_str: str, title_hint: str = None) -> list:
    """
    Returns a list of (event_id, summary, start_time_str) tuples for events
    on the given date, optionally filtered by a title hint.
    """
    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set dayStart to date "{date_str}"
            set time of dayStart to 0
            set dayEnd to dayStart + (1 * days)
            set matchingEvents to (every event whose start date is greater than or equal to dayStart and start date is less than dayEnd)
            set eventList to {{}}
            repeat with anEvent in matchingEvents
                set end of eventList to (uid of anEvent as string) & "|" & (summary of anEvent as string) & "|" & (start date of anEvent as string)
            end repeat
            return eventList
        end tell
    end tell
    '''
    success, output = run_applescript(script, app_name="Calendar")
    if not success or not output:
        return []

    events = []
    for entry in output.split(","):
        parts = entry.strip().split("|")
        if len(parts) == 3:
            events.append({"uid": parts[0].strip(), "summary": parts[1].strip(), "start": parts[2].strip()})

    if title_hint:
        title_hint_lower = title_hint.lower()
        events = [e for e in events if title_hint_lower in e["summary"].lower()]

    return events


def edit_calendar_event(uid: str, new_date: str = None, new_time: str = None, new_title: str = None, new_duration_hours: float = None) -> str:
    """Modifies an existing event, identified by uid, changing only the fields provided."""

    set_statements = []

    if new_title:
        set_statements.append(f'set summary of theEvent to "{new_title}"')

    if new_date and new_time:
        set_statements.append(f'set startDate to date "{new_date} {new_time}"')
        set_statements.append('set start date of theEvent to startDate')
        if new_duration_hours:
            set_statements.append(f'set end date of theEvent to startDate + ({new_duration_hours} * hours)')
        else:
            set_statements.append('set end date of theEvent to startDate + (1 * hours)')

    if not set_statements:
        return "Nothing to change"

    set_block = "\n".join(set_statements)

    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set theEvent to (first event whose uid is "{uid}")
            {set_block}
        end tell
    end tell
    '''

    success, output = run_applescript(script, app_name="Calendar")
    if not success:
        print(output)
        return "Sorry, I couldn't update that event"

    return "Successfully updated the event"