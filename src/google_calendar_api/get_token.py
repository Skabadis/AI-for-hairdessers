from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    project_root = Path(__file__).resolve().parent.parent.parent
    token_path = project_root / "src/google_calendar_api/token.json"
    creds_path = project_root / "src/google_calendar_api/credentials.json"

    print(f"Looking for credentials at: {creds_path}")

    if not creds_path.exists():
        print("Credentials path does not exist.")
        return None

    print("Creating new token.")
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=8080)

    with open(token_path, "w") as token:
        token.write(creds.to_json())

    return creds

if __name__ == "__main__":
    get_credentials()
