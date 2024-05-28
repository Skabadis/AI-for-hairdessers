from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    # Utiliser des chemins absolus
    project_root = Path(__file__).resolve().parent.parent.parent
    token_path = project_root / "src/google_calendar_api/token.json"
    creds_path = project_root / "src/google_calendar_api/credentials.json"

    print(f"Looking for credentials at: {creds_path}")

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print("Token found, no need to reauthenticate")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token found but is expired. Need to refresh.")
            creds.refresh(Request())
        else:
            if creds_path.exists():
                print("Token not found. Creating new token.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES
                )
                creds = flow.run_local_server(port=8080)
            else:
                print("Credentials path does not exist.")
                return None
        
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return creds

if __name__ == "__main__":
    credentials = get_credentials()
    print(credentials)
