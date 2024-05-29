from google_calendar_api.read_calendar import read_calendar
from calendar_operations.open_slots import get_open_slots_str
import pandas as pd

events_df = read_calendar()
appointments = events_df[[ 
                          'start_datetime_paris', 
                          'end_datetime_paris']]
print(appointments)

  # Generate frea-minute intervals within the working hours
appointments['event_start'] = appointments['start_datetime_paris'].dt.tz_convert(None)
appointments['event_end'] = appointments['end_datetime_paris'].dt.tz_convert(None)

opening_time="09:00:00"
closing_time="17:00:00"
freq='30min'
day='2024-05-30'
time_slots = pd.date_range(start=opening_time, end=closing_time, freq=freq)

# Create the spine dataframe
spine_df = pd.DataFrame({
    'day': [day] * len(time_slots),
    'time': [x for x in time_slots],
    'available': True
})



pd.merge(spine_df,
                        appointments,
                        left_on=['time'],
                        right_on=[ 'event_start'],
                        how='left',
                        validate='1:1')


Sandra_response = get_open_slots_str(appointments, "2024-05-30")
