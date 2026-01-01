from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import datetime
import pytz

SCOPES = ["https://www.googleapis.com/auth/calendar",'https://www.googleapis.com/auth/contacts.readonly','https://www.googleapis.com/auth/gmail.send']

def get_calendar_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def check_event_conflict(start_time: datetime.datetime, event_id_to_exclude=None):
    """
    Check if there's already an event at the given start time
    Returns: (has_conflict, conflicting_event_title) or (False, None) if no conflict
    """
    service = get_calendar_service()
    
    # Check 1 hour window around the event
    end_time = start_time + datetime.timedelta(hours=1)

    tz = pytz.timezone("Asia/Kolkata")
    ist_start = tz.localize(start_time) if start_time.tzinfo is None else start_time
    ist_end = tz.localize(end_time) if end_time.tzinfo is None else end_time
    
    utc_start = ist_start.astimezone(pytz.UTC).isoformat()
    utc_end = ist_end.astimezone(pytz.UTC).isoformat()
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=utc_start,
            timeMax=utc_end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Check if there are any events at this time (excluding the one we're updating)
        for event in events:
            if event_id_to_exclude and event['id'] == event_id_to_exclude:
                continue
            return True, event.get('summary', 'Unknown event')
        
        return False, None
        
    except Exception as e:
        print(f"Error checking conflict: {str(e)}")
        return False, None


def create_event(title: str, start_time: datetime.datetime, duration_minutes=60, reminder_minutes=15):
    service = get_calendar_service()

    has_conflict, conflicting_title = check_event_conflict(start_time)
    if has_conflict:
        return f"❌ You already have '{conflicting_title}' at that time. Please choose a different time."

    end_time = start_time + datetime.timedelta(minutes=duration_minutes)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",  
                    "minutes": reminder_minutes
                },
                {
                    "method": "email",  
                    "minutes": reminder_minutes
                }
            ]
        }
    }

    created_event = service.events().insert(
        calendarId="primary", body=event
    ).execute()

    return f"✓ Event added with {reminder_minutes} min reminder: {created_event.get('htmlLink')}"

def delete_event(event_id: str):
    """Delete an event by ID"""
    service = get_calendar_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return True

def find_event_by_title(title: str):
    """Find event ID by title with smart matching"""
    service = get_calendar_service()
    
    # Get events from next 30 days
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=50,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    if not events:
        return None, None
    
    title_lower = title.lower().strip()
    
    for event in events:
        if title_lower == event['summary'].lower():
            return event['id'], event['summary']

    for event in events:
        if title_lower in event['summary'].lower():
            return event['id'], event['summary']
    
    for event in events:
        if event['summary'].lower() in title_lower:
            return event['id'], event['summary']

    for event in events:
        event_summary = event['summary'].lower()
        # Check if the search term is in the event as a word
        words = event_summary.replace('meeting with ', '').replace('appointment with ', '').split()
        if title_lower in words or any(title_lower in word for word in words):
            return event['id'], event['summary']
    
    return None, None


def update_event(event_id: str, new_start_time: datetime.datetime, duration_minutes=60):
    """Update event time - CHECK FOR CONFLICT"""
    service = get_calendar_service()
    
    has_conflict, conflicting_title = check_event_conflict(new_start_time, event_id_to_exclude=event_id)
    if has_conflict:
        return f"❌ You already have '{conflicting_title}' at that time. Please choose a different time."

    new_end_time = new_start_time + datetime.timedelta(minutes=duration_minutes)
    
    tz = pytz.timezone("Asia/Kolkata")
    ist_start = tz.localize(new_start_time) if new_start_time.tzinfo is None else new_start_time
    ist_end = tz.localize(new_end_time) if new_end_time.tzinfo is None else new_end_time
    
    utc_start = ist_start.astimezone(pytz.UTC)
    utc_end = ist_end.astimezone(pytz.UTC)
    
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    event['start'] = {'dateTime': utc_start.isoformat()}
    event['end'] = {'dateTime': utc_end.isoformat()}
    
    updated_event = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event
    ).execute()
    
    return updated_event.get("htmlLink")

def set_reminder(event_id: str, reminder_minutes: int):
    """Update reminder for existing event"""
    service = get_calendar_service()
    
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
        event['reminders'] = {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                "minutes": reminder_minutes
                },
                {
                "method": "email",
                "minutes": reminder_minutes
                }
            ]
        }
    
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        return True
    except Exception as e:
        print(f"Error in set_reminder: {str(e)}")
        raise
