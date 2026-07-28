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
TOKEN_PATH = "config/google_token.json"
CREDENTIALS_PATH = "config/google_credentials.json"

from datetime import datetime, timedelta


def add_google_calendar_event(title: str, date: str, time: str, duration_hours: float) -> str:
    """Adds an event to the user's primary Google Calendar."""

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

    return f"Successfully added {title} to your Google Calendar"



def list_todays_google_events(date_str: str) -> str:
    """Returns a spoken-friendly summary of the date's Google Calendar events."""

    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    parsed_date = datetime.strptime(date_str, "%B %d, %Y")
    start_of_day = datetime(parsed_date.year, parsed_date.month, parsed_date.day, 0, 0, 0).isoformat() + "Z"
    end_of_day = datetime(parsed_date.year, parsed_date.month, parsed_date.day, 23, 59, 59).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return "You have no events for this date on Google Calendar"

    summaries = []
    for event in events:
        title = event.get("summary", "Untitled event")
        start = event["start"].get("dateTime", event["start"].get("date"))
        summaries.append(f"{title} at {start}")
    return f"Here's what's on your calendar for {date_str}: {', '.join(summaries)}"




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