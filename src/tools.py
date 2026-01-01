from datetime import datetime
import pytz
from .tool.google_calendar import create_event, delete_event, update_event, find_event_by_title, set_reminder,check_event_conflict
from .tool.contacts import find_contact_by_name
from .tool.telegram_client import send_message_sync, get_all_telegram_contacts

def add_calendar_event(title:str, date:str, time:str, reminder_minutes: int=15):
    """
    date format: DD-MM-YYYY
    time format: HH:MM (24h)
    """
    try:

        # Parse DD-MM-YYYY format
        date_obj = datetime.strptime(date, "%d-%m-%Y")
        time_obj = datetime.strptime(time, "%H:%M").time()

        start_dt = datetime.combine(date_obj, time_obj)
        
        link = create_event(title, start_dt, reminder_minutes=reminder_minutes)
        return link
    except ValueError as e:
        return f"Error: Invalid date or time format. {str(e)}"
    
def delete_calendar_event(title: str):
    """Delete calendar event by title"""
    try:
        event_id, event_title = find_event_by_title(title)
        
        if not event_id:
            return f"Could not find event matching '{title}'"
        
        delete_event(event_id)
        return f"✓ Deleted event: {event_title}"
    except Exception as e:
        return f"Error deleting event: {str(e)}"


def update_calendar_event(title: str, new_date: str, new_time: str):
    """Update calendar event time/date"""
    try:
        event_id, event_title = find_event_by_title(title)
        
        if not event_id:
            return f"Could not find event matching '{title}'"
        
        date_obj = datetime.strptime(new_date, "%d-%m-%Y")
        time_obj = datetime.strptime(new_time, "%H:%M").time()
        new_start_dt = datetime.combine(date_obj.date(), time_obj)
        
        link = update_event(event_id, new_start_dt)
        return link
    except ValueError as e:
        return f"Error: Invalid date or time format. {str(e)}"


def update_calendar_reminder(title: str, reminder_minutes: int):
    """Update reminder for existing event"""
    try:
        event_id, event_title = find_event_by_title(title)

        if not event_id:
            # Try to find by partial match - remove common prefixes
            for search_title in [title, title.replace("meeting with ", ""), title.replace("appointment with ", "")]:
                event_id, event_title = find_event_by_title(search_title)
                if event_id:
                    break
        
        if not event_id:
            return f"Could not find event matching '{title}'"
        
        set_reminder(event_id, reminder_minutes)
        return f"✓ Set {reminder_minutes} minute reminder for '{event_title}'"
    except Exception as e:
        return f"Error setting reminder: {str(e)}"


def send_message(recipient_name: str, message: str, platform: str = "telegram"):
    """Send message to contact"""
    try:
        if platform.lower() == "telegram":
            result = send_message_sync(recipient_name, message)
            return result
        else:
            return f"❌ Platform '{platform}' not supported"
    except Exception as e:
        return f"❌ Error: {str(e)}"