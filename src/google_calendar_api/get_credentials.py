
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path


def get_credentials():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    token_path = Path("src/google_calendar_api/token.json")
    creds_path = Path("src/google_calendar_api/credentials.json")
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(Path("token.json"), SCOPES)
        print("Token found, no need to reauthenticate")
        print(creds)
        # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token found but is expired. Need to refresh.")
            creds.refresh(Request())
        else:
            if creds_path.exists:
              print("Token not found. Creating new token.")
              flow = InstalledAppFlow.from_client_secrets_file(
                  creds_path, SCOPES
              )
              creds = flow.run_local_server(port=0)
            else:
                print("Credentials path does not exist.")
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    print(creds)
    return creds