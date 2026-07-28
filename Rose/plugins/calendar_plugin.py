from plugins.base import Plugin
from commands.apple_calendar import add_apple_calendar_event, list_events_for_date
from commands.google_calendar import add_google_calendar_event, list_todays_google_events
from ai.event_parser import extract_event,extract_date


class AddAppleCalendarEventPlugin(Plugin):
    name = "add_apple_calendar_event"
    description = (
        "Adds an event to the user's calendar. This is the DEFAULT calendar action - "
        "use this unless the user explicitly says 'Google Calendar'."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        event = extract_event(query)
        return add_apple_calendar_event(event["title"], event.get("date"), event.get("time"), event.get("duration_hours"))


class AddGoogleCalendarEventPlugin(Plugin):
    name = "add_google_calendar_event"
    description = (
        "Adds an event to Google Calendar SPECIFICALLY. "
        "ONLY use this if the user explicitly says 'Google Calendar' or 'Google' - "
        "otherwise use add_apple_calendar_event instead."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        event = extract_event(query)
        return add_google_calendar_event(event["title"], event.get("date"), event.get("time"), event.get("duration_hours"))


class ListEventsPlugin(Plugin):
    name = "list_events"
    description = (
        "Lists calendar events for a specific day. This is the DEFAULT calendar. "
        "Use this UNLESS the words 'Google' or 'Google Calendar' appear in the request. "
        "If the user says 'Google Calendar' or 'Google', do NOT use this - use list_google_events instead."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        date_str = extract_date(query)
        return list_events_for_date(date_str)


class ListGoogleEventsPlugin(Plugin):
    name = "list_todays_google_events"
    description = (
        "Lists Google Calendar events for a specific day. "
        "ONLY use this when the user's words include 'Google' or 'Google Calendar'. "
        "This is NOT the default - if unsure, use list_events instead."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        date_str = extract_date(query)
        return list_todays_google_events(date_str)