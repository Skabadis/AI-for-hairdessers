import pandas as pd

def convert_dt_to_time_str(datetime):
    return pd.Timestamp(datetime).time().strftime("%H:%M:%S")

def convert_dt_to_date_short_str(datetime):
    return pd.Timestamp(datetime).date().strftime("%Y-%m-%d")

def convert_dt_to_date_long_str(datetime):
    return pd.Timestamp(datetime).date().strftime("%d %B, %Y")

def convert_dt_to_date_long_no_year_str(datetime):
    return pd.Timestamp(datetime).date().strftime("%d %B")