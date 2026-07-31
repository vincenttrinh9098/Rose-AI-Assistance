from plugins.base import Plugin
from commands.reminders import add_reminder
from ai.event_parser import extract_event


class AddReminderPlugin(Plugin):
    name = "add_reminder"
    description = "Adds a reminder, given a phrase with title and optionally date/time."
    extra_fields = {}
    user_facing_description = "Say \"remind me to [something]\" and I'll add it to your Reminders app."

    def handle(self, query: str, **kwargs) -> str:
        event = extract_event(query)
        if not event.get("has_details"):
            return "What would you like me to remind you about?"
        return add_reminder(event["title"], event.get("date"), event.get("time"))