from plugins.base import Plugin
from commands.apple_calendar import add_apple_calendar_event, list_events_for_date
from commands.google_calendar import add_google_calendar_event, list_todays_google_events,find_google_events_for_edit, edit_google_calendar_event,delete_google_calendar_event
from ai.event_parser import extract_event,extract_date,extract_edit
from core.pending_action import get_pending, set_pending, clear_pending
from core.last_calendar_event import set_last_event

class AddAppleCalendarEventPlugin(Plugin):
    name = "add_apple_calendar_event"
    description = (
        "Adds an event to the user's calendar. This is the DEFAULT calendar action - "
        "use this unless the user explicitly says 'Google Calendar'."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        event = extract_event(query)
        if not event.get("has_details"):
            return "What event would you like to add, and when?"
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
        if not event.get("has_details"):
            return "What event would you like to add, and when?"

        message, event_id = add_google_calendar_event(event["title"], event.get("date"), event.get("time"), event.get("duration_hours"))

        if event_id:
            from core.last_calendar_event import set_last_event
            set_last_event(event_id, event["title"])

        return message

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
    

class EditCalendarEventPlugin(Plugin):
    name = "edit_calendar_event"
    description = (
        "Edits or changes an EXISTING calendar event (e.g. 'change my 3pm to 5pm', "
        "'move my dentist appointment to tomorrow', 'actually make that 6pm', "
        "'actually call it something else'). Use this for ANY correction or change "
        "to a time/date/title, even brief ones like 'actually make that 1pm', since "
        "these usually refer to an event just discussed."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        edit_info = extract_edit(query)

        title_hint = edit_info.get("title_hint")
        has_real_title_hint = title_hint and "UNKNOWN" not in title_hint.upper() and title_hint.upper() not in ("NONE", "NULL", "")

        from core.last_calendar_event import get_last_event
        last = get_last_event()

        if last and not has_real_title_hint:
            correction_date = edit_info.get("date")
            # Claude resolves "no date mentioned" to today's date by default, which is ambiguous -
            # but if this correction phrase didn't actually mention a date/day word, we should preserve original
            # Simplest reliable fix: only pass date through if it's explicitly different from today
            from datetime import datetime
            today_str = datetime.now().strftime("%B %d, %Y")
            date_to_pass = correction_date if correction_date != today_str else None

            return self._apply_edit({"id": last["id"], "summary": last["summary"]}, {
                "date": date_to_pass,
                "new_time": edit_info.get("new_time"),
                "new_title": edit_info.get("new_title"),
            })
        date_str = edit_info.get("date")
        events = find_google_events_for_edit(date_str, title_hint if has_real_title_hint else None)

        if len(events) == 0:
            return f"I couldn't find any events on {date_str} to change"

        if len(events) == 1:
            return self._apply_edit(events[0], edit_info)

        numbered = [f"{i+1}. {e['summary']}" for i, e in enumerate(events)]
        from core.pending_action import set_pending
        set_pending("disambiguate_calendar_edit", matches=events, edit_info=edit_info)
        return f"I found a few events: {'. '.join(numbered)}. Which one, or say the number?"


    def _apply_edit(self, event, edit_info):
        return edit_google_calendar_event(
            event_id=event["id"],
            new_date=edit_info.get("date"),
            new_time=edit_info.get("new_time"),
            new_title=edit_info.get("new_title"),
        )

class DeleteCalendarEventPlugin(Plugin):
    name = "delete_calendar_event"
    description = (
        "Deletes or removes an EXISTING calendar event (e.g. 'delete my 3pm meeting', "
        "'remove the dentist appointment', 'cancel my walk today', 'delete that', "
        "'nevermind, delete that', 'actually just remove it'). Use this for ANY request "
        "to delete or remove a calendar event, even brief ones with no clear title mentioned, "
        "since these usually refer to an event just discussed."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        edit_info = extract_edit(query)
        title_hint = edit_info.get("title_hint")
        has_real_title_hint = title_hint and "UNKNOWN" not in title_hint.upper() and title_hint.upper() not in ("NONE", "NULL", "")

        from core.last_calendar_event import get_last_event
        last = get_last_event()

        if last and not has_real_title_hint:
            return delete_google_calendar_event(last["id"])

        date_str = edit_info.get("date")
        events = find_google_events_for_edit(date_str, title_hint if has_real_title_hint else None)

        if len(events) == 0:
            return f"I couldn't find any events on {date_str} to delete"

        if len(events) == 1:
            return delete_google_calendar_event(events[0]["id"])

        numbered = [f"{i+1}. {e['summary']}" for i, e in enumerate(events)]
        from core.pending_action import set_pending
        set_pending("disambiguate_calendar_delete", matches=events)
        return f"I found a few events: {'. '.join(numbered)}. Which one should I delete, or say the number?"