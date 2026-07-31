import json

from core.paths import path_for
LAST_EVENT_PATH = path_for("logs", "last_calendar_event.json")


def set_last_event(event_id: str, summary: str) -> None:
    with open(LAST_EVENT_PATH, "w") as f:
        json.dump({"id": event_id, "summary": summary}, f)


def get_last_event() -> dict | None:
    try:
        with open(LAST_EVENT_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None