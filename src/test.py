from calendar_operations.open_slots import get_open_slots_str
import pandas as pd

# Define working hours
day = "2024-05-28"
opening_time = "09:00:00"
closing_time = "17:00:00"

# Sample appointments DataFrame
appointments = pd.DataFrame({
    'day': [pd.to_datetime(day)] * 3,
    'event_start': [pd.Timestamp("2024-05-28 09:30:00"), pd.Timestamp("2024-05-28 11:00:00"), pd.Timestamp("2024-05-28 13:00:00")],
    'event_end': [pd.Timestamp("2024-05-28 10:30:00"), pd.Timestamp("2024-05-28 12:00:00"), pd.Timestamp("2024-05-28 14:00:00")]
})


availabilities_string = get_open_slots_str(appointments, day, opening_time, closing_time)