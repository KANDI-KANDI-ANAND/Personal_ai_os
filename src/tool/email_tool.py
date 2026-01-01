import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/contacts.readonly','https://www.googleapis.com/auth/calendar']

def get_gmail_service():
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

    return build("gmail", "v1", credentials=creds)

def send_email(to_email:str, subject:str, body:str):
    service = get_gmail_service()
    
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to_email
    message["From"] = "kandianand2004@gmail.com"
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()

    print(f"📧 Email sent to {to_email}")
    