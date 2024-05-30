from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_calendar_api.get_credentials import get_credentials


def add_event(event):
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    event = {'summary': 'Skandere Sahli - 0651164070',
             'description': 'Coupe de cheveux pour femme',
             'start': {'dateTime': '2024-05-28T14:00:00+02:00', 'timeZone': 'Europe/Paris'},
             'end': {'dateTime': '2024-05-28T14:30:00', 'timeZone': 'Europe/Paris'}}
    add_event(event)


# event = {
#                 'summary': 'Rdv - Skandere ajouté automatiquement',
#               #   'location': '800 Howard St., San Francisco, CA 94103',
#                 'description': 'Coupe homme tondeuse',
#                 'start': {
#                   'dateTime': '2024-05-28T11:00:00+02:00',
#                   'timeZone': 'Europe/Paris',
#                 },
#                 'end': {
#                   'dateTime': '2024-05-28T11:30:00+02:00',
#                   'timeZone': 'Europe/Paris',
#                 },
#               #   'recurrence': [
#               #     'RRULE:FREQ=DAILY;COUNT=2'
#               #   ],
#                 'attendees': [
#                   {'email': 'badrelidrissimokdad12@gmail.com'},
#                   # {'email': 'sbrin@example.com'},
#                 ],
#                 'reminders': {
#                   'useDefault': False,
#                   'overrides': [
#                     {'method': 'email', 'minutes': 24 * 60},
#                     {'method': 'popup', 'minutes': 10},
#                   ],
#                 },
#               }