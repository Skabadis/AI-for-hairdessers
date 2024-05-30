import pandas as pd

def convert_dt_to_time_str(datetime):
    return pd.Timestamp(datetime).time().strftime("%H:%M:%S")