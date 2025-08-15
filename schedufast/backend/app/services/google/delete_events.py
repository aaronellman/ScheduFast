from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

#TODO: Add try-catch block for when the token/credentials expire.

# If modifying the scope, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    """Authenticate and return a service object for the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def delete_event(service, event_id):
    """Deletes an event from the Google Calendar."""
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Event {event_id} deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_test_events(service):
    """List and delete test events from your Google Calendar."""
    # List the events from the calendar
    events_result = service.events().list(calendarId='primary', maxResults=250, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No events found.')
    else:
        for event in events:
            # Modify this condition to match the events you want to delete
            keywords = ['PROG5121 CR03', 'MAPC5112 CR03', 'INSY5111 CR03', 'CONE5111 CR03', 'ACADEMIC MERIDIAN', 'FAMILY DAY', 'FREEDOM DAY', 'GOOGLE HACKATHON', 'ASSESSMENTS', 'MAPC5112 WKSP', 'ITPP5112 CR02', 'SOCIAL MERIDIAN', 'WORKERS DAY', 'MAPC5112 LR24','ITPP5112 CR02']
            if any(key in event.get('summary', '') for key in keywords) :
                print(f"Deleting event: {event['summary']} ({event['id']})") 
                delete_event(service, event['id'])
                

def main():
    # Authenticate and create a service object
    service = authenticate_google()

    # Delete test events
    delete_test_events(service)

main()


