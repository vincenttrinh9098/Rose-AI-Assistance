

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


def extract_date(text: str) -> str:
    """Given natural language like 'tomorrow' or 'next Tuesday', returns a
    resolved date string like 'July 29, 2026'."""

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

    today_str = datetime.now().strftime("%A, %B %d, %Y")

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        tools=EVENT_TOOL,
        system=f"Today's date is {today_str}. Extract calendar event details from what the user says.",
        tool_choice={"type": "tool", "name": "extract_event"},
        messages=[{"role": "user", "content": text}],

    ) 


    for block in response.content:
        if block.type == "tool_use":
            event = block.input
            event["has_details"] = bool(event.get("title")) and event["title"].strip().lower() not in ("unknown", "event", "reminder", "")
            return event

    return "empty"