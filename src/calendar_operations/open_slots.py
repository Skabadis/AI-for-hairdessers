import pandas as pd
import numpy as np
from datetime import timedelta
from utils.utils import convert_dt_to_time_str

def get_open_slots(appointments, day, opening_time, closing_time, freq, duration):
  opening_time = pd.Timestamp(f'{day} {opening_time}')
  closing_time = pd.Timestamp(f'{day} {closing_time}')
  day = pd.to_datetime(day) 
  
  # Generate frea-minute intervals within the working hours
  time_slots = pd.date_range(start=opening_time, end=closing_time, freq=freq)

  # Create the spine dataframe
  spine_df = pd.DataFrame({
      'day': [day] * len(time_slots),
      'time': [x for x in time_slots],
      'available': True
  })

  # Add closing as an appointment to avoid having appointments booked at closing time
  open_close_appointments = pd.DataFrame({
      'day': [day] ,
      'event_start': [closing_time],
      'event_end': [closing_time]
  })
  appointments = pd.concat([appointments, 
                            open_close_appointments])

  print(f"Spine df: {spine_df}")
  print(f"Spine df types: {spine_df.dtypes}")
  
  print(f"appointments df: {appointments}")
  print(f"appointments df types: {appointments.dtypes}")
  # Get appointments already booked on spine
  open_slots = pd.merge(spine_df,
                        appointments,
                        left_on=['time'],
                        right_on=[ 'event_start'],
                        how='left',
                        validate='1:1')

  # Figure out reamining available slots
  td = timedelta(minutes=duration)
  open_slots['previous_event_end'] = open_slots['event_end'].ffill()
  open_slots['next_event_start'] = open_slots['event_start'].bfill()
  open_slots['available'] = np.where((open_slots['time'] < open_slots['previous_event_end']) | 
                                    (open_slots['time'] + td > open_slots["next_event_start"]),
                                    False,
                                    True)

  # Gather the available windows to get the availability start and end (available from 2pm to 4pm for example)
  open_slots['available_window_nbr'] = ((open_slots['available'].shift(1) != 
                                        open_slots['available']) & 
                                        open_slots['available']).cumsum() * open_slots['available']

  open_slots = open_slots.loc[open_slots['available']]\
                        .groupby('available_window_nbr').agg({'time': ('min', 'max'),
                                                              })

  # df formatting
  open_slots.columns = [x[0] + '_' + x[1] for x in open_slots.columns]
  open_slots = open_slots.reset_index()
  return open_slots

def convert_open_slots_to_str(open_slots):
  # Get start and end of available time windows in string, only get start if there is only one time available in the window
  availabilities_string = [f"{convert_dt_to_time_str(x[0])} a {convert_dt_to_time_str(x[1])}" if x[0] != x[1] else f"{convert_dt_to_time_str(x[0])}" for x in open_slots[['time_min', 'time_max']].values]

  availabilities_string = ' , '.join(availabilities_string)
  return f'Nous avons des disponibilites a {availabilities_string}'

def get_open_slots_str(appointments, day, opening_time="09:00:00", closing_time="17:00:00", freq='30min', duration=30):
    open_slots = get_open_slots(appointments, day, opening_time=opening_time, closing_time=closing_time, freq=freq, duration=duration)
    availabilities_string = convert_open_slots_to_str(open_slots)
    return availabilities_string