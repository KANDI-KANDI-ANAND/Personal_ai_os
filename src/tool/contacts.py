from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# For Google Contacts API
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly','https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.send']

def get_contacts_service():
    """Get Google Contacts service"""
    
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build('people', 'v1', credentials=creds)


def find_contact_by_name(name: str):
    """Find contact by name and return phone/email/telegram-username"""
    try:
        service = get_contacts_service()
        
        results = service.people().searchContacts(
            query=name,
            readMask='names,phoneNumbers,emailAddresses,nicknames,biographies'
        ).execute()
        
        contacts = results.get('results', [])
        
        if not contacts:
            return None
        
        contact = contacts[0].get('person', {})

        telegram_username = extract_telegram_username(contact)
        contact_data = {
            "name": contact.get('names', [{}])[0].get('displayName', name),
            "phone_numbers": [p.get('value') for p in contact.get('phoneNumbers', [])],
            "emails": [e.get('value') for e in contact.get('emailAddresses', [])],
            "telegram_username": telegram_username
        }
        
        print(f"✓ Found contact: {contact_data['name']}")
        return contact_data
        
    except Exception as e:
        print(f"Error finding contact: {str(e)}")
        return None

def extract_telegram_username(contact):
    """Extract Telegram username from contact notes or nicknames"""
    
    # Check nicknames first
    nicknames = contact.get('nicknames', [])
    for nickname in nicknames:
        value = nickname.get('value', '').lower()
        if 'telegram' in value or value.startswith('@'):
            # Extract username (remove @ if present)
            username = value.replace('telegram:', '').strip()
            if username.startswith('@'):
                return username
            return f"@{username}"
    
    # Check notes for Telegram username
    notes = contact.get('biographies', [])
    for note in notes:
        text = note.get('value', '').lower()
        if 'telegram' in text:
            # Look for @username pattern
            import re
            match = re.search(r'@[\w]+', text)
            if match:
                return match.group(0)
            
            # Look for "telegram: username" pattern
            match = re.search(r'telegram:\s*(@?[\w]+)', text, re.IGNORECASE)
            if match:
                username = match.group(1)
                return username if username.startswith('@') else f"@{username}"
    
    return None