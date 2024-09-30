import os
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required by the Gmail API for reading emails and downloading attachments
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to the folder where attachments will be downloaded
ATTACHMENT_DIR = 'attachments/'

def authenticate_gmail():
    """Authenticates the user with Gmail API and returns the service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def search_email(service, query):
    """Searches for an email using a query string (e.g., subject, sender)."""
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        if not messages:
            print('No messages found.')
            return None
        print(f'{len(messages)} message(s) found.')
        return messages[0]['id']  # Return the first email's ID
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def download_attachments(service, msg_id):
    """Downloads all attachments from a specific email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        parts = message['payload'].get('parts', [])

        if not os.path.exists(ATTACHMENT_DIR):
            os.makedirs(ATTACHMENT_DIR)

        for part in parts:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                elif 'attachmentId' in part['body']:
                    att_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(
                        userId='me', messageId=msg_id, id=att_id).execute()
                    data = attachment['data']
                else:
                    continue

                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = os.path.join(ATTACHMENT_DIR, part['filename'])

                with open(path, 'wb') as f:
                    f.write(file_data)
                print(f'Attachment {part["filename"]} downloaded successfully.')
    except HttpError as error:
        print(f'An error occurred: {error}')

def upload_attachments(service):
    """Uploads attachments to google drive"""
    try:
        print("Uploading attachments")
    except HttpError as error:
        print(f'An error occurred: {error}')

def delete_emails(service):
    """Delete emails from attachment pull"""
    try:
        print("Deleting emails")
    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    # Authenticate with Gmail API
    service = authenticate_gmail()
    if not service:
        return

    # Specify the search query (e.g., subject, sender, or specific term)
    query = 'subject:"test"'

    # Search for the email
    msg_id = search_email(service, query)
    if not msg_id:
        print("No email found with the specified query.")
        return

    # Download attachments from the found email
    download_attachments(service, msg_id)

    #upload to google drive
    upload_attachments(service)

    #delete relevant emails
    delete_emails(service)

if __name__ == '__main__':
    main()