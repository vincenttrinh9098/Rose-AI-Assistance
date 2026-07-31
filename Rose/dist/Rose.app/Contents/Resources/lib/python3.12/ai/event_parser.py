

from datetime import datetime
from ai.client import client

EVENT_TOOL = [
    {
        "name": "extract_event",
        "description": "Extracts calendar event details from natural language.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "A short title for the event"},
                "date": {
                    "type": "string",
                    "description": "The event's date, formatted exactly like 'July 28, 2026'",
                },
                "time": {
                    "type": "string",
                    "description": "The event's start time, formatted exactly like '3:00 PM'",
                },
                "duration_hours": {
                    "type": "number",
                    "description": "How long the event lasts, in hours. Default to 1 if not mentioned.",
                },
                "has_details": {
                    "type": "boolean",
                    "description": "True if the user's message contained actual event details (a title, activity, or purpose). False if the message was vague or contained no real event information.",
                },
            },
            "required": ["title", "date", "time", "duration_hours", "has_details"],
        },
    }
]

DATE_TOOL = [
    {
        "name": "extract_date",
        "description": "Extracts a specific date from natural language referring to a day.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The resolved date, formatted exactly like 'July 28, 2026'",
                },
            },
            "required": ["date"],
        },
    }
]


DATE_TOOL = [
    {
        "name": "extract_date",
        "description": "Extracts a specific date from natural language referring to a day.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The resolved date, formatted exactly like 'July 28, 2026'",
                },
            },
            "required": ["date"],
        },
    }
]

EDIT_TOOL = [
    {
        "name": "extract_edit",
        "description": "Extracts what calendar event to find and what to change about it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date the event is on, resolved to format like 'July 29, 2026'. If no date is mentioned, default to today's date.",
                },
                "title_hint": {
                    "type": ["string", "null"],
                    "description": "A word or phrase from the event's TITLE only (e.g. 'meeting', 'dentist') to help find it. Never put a time here. Null if no title is mentioned.",
                },
                "new_time": {"type": ["string", "null"], "description": "The new time, formatted like '5:00 PM'. Null if time isn't changing."},
                "new_title": {"type": ["string", "null"], "description": "The new title. Null if title isn't changing."},
            },
            "required": ["date", "title_hint", "new_time", "new_title"],
        },
    }
]

def extract_edit(text: str) -> dict:

    if not text or not text.strip():
        text = "change something"
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system=f"Today's date is {today_str}. Extract what calendar event the user wants to find and modify.",
        tools=EDIT_TOOL,
        tool_choice={"type": "tool", "name": "extract_edit"},
        messages=[{"role": "user", "content": text}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input
        
def extract_date(text: str) -> str:
    """Given natural language like 'tomorrow' or 'next Tuesday', returns a
    resolved date string like 'July 29, 2026'."""
    if not text or not text.strip():
        text = "today"
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        system=f"Today's date is {today_str}. Resolve the date being referred to.",
        tools=DATE_TOOL,
        tool_choice={"type": "tool", "name": "extract_date"},
        messages=[{"role": "user", "content": text}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input["date"]


def extract_event(text: str) -> dict:
    """Given natural language like 'dentist next Tuesday at 3pm', returns
    {"title": ..., "date": ..., "time": ...} in AppleScript-friendly formats."""
    if not text or not text.strip():
        text = "an event"

    today_str = datetime.now().strftime("%A, %B %d, %Y")
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system=f"Today's date is {today_str}. Extract calendar event details from what the user says.",
        tools=EVENT_TOOL,
        tool_choice={"type": "tool", "name": "extract_event"},
        messages=[{"role": "user", "content": text}],
    )

    for block in response.content:
        if block.type == "tool_use":
            event = block.input
            title = event.get("title", "")
            placeholder_words = ("UNKNOWN", "EVENT", "NONE", "NULL", "REMINDER", "APPOINTMENT", "MEETING", "")
            has_real_title = bool(title) and title.strip().upper() not in placeholder_words
            event["has_details"] = has_real_title

            return event