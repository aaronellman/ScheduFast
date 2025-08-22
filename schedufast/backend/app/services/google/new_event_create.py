import os
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"C:\GitHub\SchedEase\schedufast\credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def delete_existing_calendar(service, name="University Timetable"):
    calendars = service.calendarList().list().execute()
    for cal in calendars.get("items", []):
        if cal.get("summary") == name:
            service.calendars().delete(calendarId=cal["id"]).execute()
            print(f"Deleted existing calendar: {name} ({cal['id']})")
            return True
    return False

def create_calendar(service, name="University Timetable"):
    # Remove old one if present
    delete_existing_calendar(service, name)

    # Create calendar
    body = {"summary": name, "timeZone": "Africa/Johannesburg"}
    calendar = service.calendars().insert(body=body).execute()
    calendar_id = calendar["id"]
    print(f"Created calendar: {calendar_id}")

    # Remove default reminders
    calendar["defaultReminders"] = []
    service.calendars().update(calendarId=calendar_id, body=calendar).execute()
    print("Disabled all default reminders")

    # Return calendar ID and web link
    return calendar_id, calendar.get("htmlLink")

def insert_events_from_json(service, calendar_id, json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        events = json.load(f)

    for event in events:
        try:
            service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates="none",
                sendNotifications=False
            ).execute()
            print(f"Inserted event: {event['summary']}")
            time.sleep(0.1)  # throttle
        except HttpError as e:
            print(f"Error inserting event {event.get('summary')}: {e}")

def main(json_path):
    service = get_service()
    calendar_id, calendar_link = create_calendar(service)
    print(f"Open your calendar here: {calendar_link}")
    insert_events_from_json(service, calendar_id, json_path)

if __name__ == "__main__":
    main()
