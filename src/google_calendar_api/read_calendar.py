import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_calendar_api.get_credentials import get_credentials
# from get_credentials import get_credentials
import pandas as pd


"""
TODO: Figure out better schema to account for having multiple hairdresser in the same salon. For now models agenda of only one hairdresser.
"""

def get_events(creds, date):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  try:
    service = build("calendar", "v3", credentials=creds)
    
    # TODO: adjsut start and end to the right timezone, right now it is using UTC timezone
    date_ts = pd.Timestamp(date)
    start = (datetime.datetime(date_ts.year, date_ts.month, date_ts.day, 00, 00)).isoformat() + 'Z'
    tomorrow = date_ts + datetime.timedelta(days=1)
    end =  (datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 00, 00)).isoformat() + 'Z'

    # Calling google calendar API
    print(f"Getting the events for date {date}")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            # maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return pd.DataFrame(columns=['kind', 'etag', 'id', 'status', 'htmlLink', 'created', 'updated',
                                   'summary', 'creator', 'organizer', 'start', 'end', 'iCalUID',
                                   'sequence', 'reminders', 'eventType'])

    # Prints the start and name of the events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")
    
  events_df = pd.DataFrame(events) 
  return  events_df

def process_events_df(df):
  # Converts datetime to make sure it is referred to in Paris timezone
  if len(df) > 0:
    df[['start_datetime', 
        'start_timezone']] = df['start'].apply(lambda x: pd.Series([x['dateTime'], x['timeZone']]))
    df['start_datetime_paris'] = pd.to_datetime(df['start_datetime']).dt.tz_convert('Europe/Paris')

    df[['end_datetime',
        'end_timezone']] = df['end'].apply(lambda x: pd.Series([x['dateTime'], x['timeZone']]))
    df['end_datetime_paris'] = pd.to_datetime(df['end_datetime']).dt.tz_convert('Europe/Paris')
    
    # Converting relevant time columns to datetime
    # df['day'] = pd.to_datetime(df['start_datetime_paris'].dt.date)
    df['event_start'] = df['start_datetime_paris'].dt.tz_convert(None)
    df['event_end'] = df['end_datetime_paris'].dt.tz_convert(None)

  else:
      columns = list(df.columns) + ['start_datetime', 'start_timezone', 'start_datetime_paris', 'end_datetime', 'end_timezone', 'end_datetime_paris', 'event_start', 'event_end']
      return pd.DataFrame(columns=columns)
  return df

def read_calendar(date):
  creds = get_credentials()
  events_df = get_events(creds, date)
  events_df = process_events_df(events_df)
  return events_df

# date = "2024-05-30"
# read_calendar(date)