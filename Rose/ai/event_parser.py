

from datetime import datetime
from ai.llm import client

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
            },
            "required": ["title", "date", "time", "duration_hours"],
        },
    }
]


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
            event_data = block.input

    return event_data