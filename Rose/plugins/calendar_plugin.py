from plugins.base import Plugin
from commands.apple_calendar import add_calendar_event, list_todays_events
from ai.event_parser import extract_event


class AddCalendarEventPlugin(Plugin):
    name = "add_calendar_event"
    description = "Adds an event to the calendar, given a phrase with date/time/title details."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        event = extract_event(query)
        return add_calendar_event(event["title"], event.get("date"), event.get("time"), event.get("duration_hours"))


class ListTodaysEventsPlugin(Plugin):
    name = "list_todays_events"
    description = "Lists today's calendar events."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return list_todays_events()