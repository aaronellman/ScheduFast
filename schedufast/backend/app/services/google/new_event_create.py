import os
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest
from dotenv import load_dotenv
from utils import callback

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_NAME = "University Timetable"

def get_service() -> build:
    """Authenticate and return Google Calendar service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            load_dotenv()
            client_config = {
                "installed": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8000"],  
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=5500)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

def get_or_create_calendar(service, name=CALENDAR_NAME):
    """Return existing calendar ID or create a new one."""
    calendars = service.calendarList().list().execute()
    for cal in calendars.get("items", []):
        if cal.get("summary") == name:
            print(f"Using existing calendar: {name} ({cal['id']})")
            return cal["id"], cal.get("htmlLink")

    # If not found, create a new calendar
    body = {"summary": name, "timeZone": "Africa/Johannesburg"}
    calendar = service.calendars().insert(body=body).execute()
    calendar_id = calendar["id"]

    # Disable default reminders
    calendar["defaultReminders"] = []
    service.calendars().update(calendarId=calendar_id, body=calendar).execute()
    print(f"Created new calendar: {calendar_id}")

    return calendar_id, calendar.get("htmlLink")

def insert_events_from_json(service, calendar_id, json_file, throttle=1):
    """Insert events from a JSON file into the given calendar."""
    with open(json_file, "r", encoding="utf-8") as f:
        events = json.load(f)

    batch = BatchHttpRequest(callback=callback, batch_uri="https://www.googleapis.com/batch/calendar/v3")

    for i,event in enumerate(events):
        try:
            request = service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates="none",
                sendNotifications=False
            )

            batch.add(request, request_id=str(i))

            print(f"Inserted event: {event['summary']}")
            #time.sleep(throttle)  # throttling requests
        except HttpError as e:
            print(f"Error inserting event {event.get('summary')}: {e}")
    batch.execute()

def insert_multiple_json_files(json_files):
    """Insert events from multiple JSON files into a single calendar."""
    service = get_service()
    calendar_id, calendar_link = get_or_create_calendar(service)
    print(f"Open your calendar here: {calendar_link}")

    for json_file in json_files:
        print(f"\nProcessing file: {json_file}")
        insert_events_from_json(service, calendar_id, json_file)

if __name__ == "__main__":
    # Example usage: replace with your list of JSON files
    json_files = [
        r"split_sheets\Table_1_events.json",
        r"split_sheets\Table_3_events.json"
    ]
    insert_multiple_json_files(json_files)