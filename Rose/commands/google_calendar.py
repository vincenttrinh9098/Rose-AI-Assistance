"""
commands/google_calendar.py

Google Calendar integration via OAuth. First run opens a browser for you
to authorize access; after that, a saved token is reused automatically.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
from core.paths import path_for
CREDENTIALS_PATH = path_for("config", "google_credentials.json")
TOKEN_PATH = path_for("config", "google_token.json")

from datetime import datetime, timedelta


def add_google_calendar_event(title: str, date: str, time: str, duration_hours: float) -> tuple:
    """Adds an event to the user's primary Google Calendar. Returns (message, event_id)."""
    try:
        creds = _get_credentials()
        service = build("calendar", "v3", credentials=creds)

        start_dt = datetime.strptime(f"{date} {time}", "%B %d, %Y %I:%M %p")
        end_dt = start_dt + timedelta(hours=duration_hours)

        event = {
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Los_Angeles"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()

    except Exception as e:
        print(f"add_google_calendar_event() failed: {e}")
        return "Sorry, I couldn't add that to your Google Calendar", None

    return f"I Successfully added {title} to your Google Calendar at {time} on {date}", created_event["id"]




def list_todays_google_events(date_str: str) -> str:
    """Returns a spoken-friendly summary of the date's Google Calendar events."""

    try:
        creds = _get_credentials()
        service = build("calendar", "v3", credentials=creds)

        parsed_date = datetime.strptime(date_str, "%B %d, %Y")
        start_of_day = f"{parsed_date.strftime('%Y-%m-%d')}T00:00:00-07:00"
        end_of_day = f"{parsed_date.strftime('%Y-%m-%d')}T23:59:59-07:00"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        if not events:
            return f"You don't have anything on your calendar for {date_str}"

        summaries = []
        for event in events:
            title = event.get("summary", "an untitled event")
            start_raw = event["start"].get("dateTime", event["start"].get("date"))

            if "T" in start_raw:
                # has a real time component - format it naturally, e.g. "5:00 PM"
                start_dt = datetime.fromisoformat(start_raw)
                time_str = start_dt.strftime("%-I:%M %p")
                summaries.append(f"{title} at {time_str}")
            else:
                # all-day event, no specific time
                summaries.append(f"{title} (all day)")

    except Exception as e:
        print(f"list_todays_google_events() failed: {e}")
        return "Sorry, I couldn't check your calendar"

    if len(summaries) == 1:
        return f"On {date_str}, you have {summaries[0]}"

    return f"On {date_str}, you have {len(summaries)} things: " + ", ".join(summaries[:-1]) + f", and {summaries[-1]}"



from difflib import SequenceMatcher

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_google_events_for_edit(date_str: str, title_hint: str = None) -> list:
    try:
        creds = _get_credentials()
        service = build("calendar", "v3", credentials=creds)

        parsed_date = datetime.strptime(date_str, "%B %d, %Y")
        start_of_day = f"{parsed_date.strftime('%Y-%m-%d')}T00:00:00-07:00"
        end_of_day = f"{parsed_date.strftime('%Y-%m-%d')}T23:59:59-07:00"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        results = []
        for event in events:
            summary = event.get("summary", "Untitled event")
            start = event["start"].get("dateTime", event["start"].get("date"))
            results.append({"id": event["id"], "summary": summary, "start": start})

        if title_hint:
            # substring match OR fuzzy similarity - catches both exact and loose matches
            filtered = []
            for e in results:
                if title_hint.lower() in e["summary"].lower():
                    filtered.append(e)
                elif _similarity(title_hint, e["summary"]) > 0.55:
                    filtered.append(e)
            results = filtered

        return results

    except Exception as e:
        print(f"find_google_events_for_edit() failed: {e}")
        return []

    

def edit_google_calendar_event(event_id: str, new_date: str = None, new_time: str = None, new_title: str = None, new_duration_hours: float = None) -> str:
    try:
        creds = _get_credentials()
        service = build("calendar", "v3", credentials=creds)

        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if new_title:
            event["summary"] = new_title

        if new_time:
            # if no new date given, use the event's existing date
            if new_date:
                date_to_use = new_date
            else:
                existing_start = event["start"].get("dateTime", event["start"].get("date"))
                existing_dt = datetime.fromisoformat(existing_start.replace("Z", "+00:00"))
                date_to_use = existing_dt.strftime("%B %d, %Y")

            start_dt = datetime.strptime(f"{date_to_use} {new_time}", "%B %d, %Y %I:%M %p")
            duration = new_duration_hours if new_duration_hours else 1
            end_dt = start_dt + timedelta(hours=duration)

            event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": "America/Los_Angeles"}
            event["end"] = {"dateTime": end_dt.isoformat(), "timeZone": "America/Los_Angeles"}

        service.events().patch(calendarId="primary", eventId=event_id, body=event).execute()

    except Exception as e:
        print(f"edit_google_calendar_event() failed: {e}")
        return "Sorry, I couldn't update that event"

    return "I Successfully updated the event for you"


def delete_google_calendar_event(event_id: str) -> str:
    try:
        creds = _get_credentials()
        service = build("calendar", "v3", credentials=creds)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
    except Exception as e:
        print(f"delete_google_calendar_event() failed: {e}")
        return "Sorry, I couldn't delete that event"

    return "I Successfully deleted the event for you"




def _get_credentials():
    """Returns valid credentials, running the login flow if needed."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds