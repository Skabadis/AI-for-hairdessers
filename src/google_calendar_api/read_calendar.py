import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from get_credentials import get_credentials
import pandas as pd


"""
TODO: Figure out better schema to account for having multiple hairdresser in the same salon. For now models agenda of only one hairdresser.
"""

def get_events(creds):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")
    
  events_df = pd.DataFrame(events) 
  return  events_df

def process_events_df(df):
  # Converts datetime to make sure it is referred to in Paris timezone
  df[['start_datetime', 
  	  'start_timezone']] = df['start'].apply(lambda x: pd.Series([x['dateTime'], x['timeZone']]))
  df['start_datetime_paris'] = pd.to_datetime(df['start_datetime']).dt.tz_convert('Europe/Paris')

  df[['end_datetime',
      'end_timezone']] = df['end'].apply(lambda x: pd.Series([x['dateTime'], x['timeZone']]))
  df['end_datetime_paris'] = pd.to_datetime(df['end_datetime']).dt.tz_convert('Europe/Paris')
  return df

def read_calendar():
  creds = get_credentials()
  events_df = read_calendar(creds)
  events_df = process_events_df(events_df)

# if __name__ == "__main__":
#     print(events[['summary',
#        'start_datetime_paris', 'end_datetime_paris']].loc[0])
#     print(events.columns)