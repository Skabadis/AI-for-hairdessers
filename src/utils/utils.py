import pandas as pd

def convert_dt_to_time_str(datetime):
    return pd.Timestamp(datetime).time().strftime("%H:%M:%S")

def convert_dt_to_date_short_str(datetime):
    return pd.Timestamp(datetime).date().strftime("%Y-%m-%d")

def convert_dt_to_date_long_str(datetime):
    return format_date_to_french(pd.Timestamp(datetime).date())

def convert_dt_to_date_long_no_year_str(datetime):
    return format_date_to_french(pd.Timestamp(datetime).date(), with_year=False)

def format_date_to_french(date, with_year=True):
    """Takes as input a datetime date and returns a long date format in French

    Args:
        date (datetime): date
        with_year (bool, optional): Returns the year if True, without year if False. Defaults to True.

    Returns:
        str: Long format date. Ex: 1er juin, 2024 or 6 janvier, 2025
    """
    # Define mapping of month names
    month_names = {
        1: "janvier",
        2: "février",
        3: "mars",
        4: "avril",
        5: "mai",
        6: "juin",
        7: "juillet",
        8: "août",
        9: "septembre",
        10: "octobre",
        11: "novembre",
        12: "décembre"
    }

    # Extract year, month, and day from the date string
    year, month, day = date.year, date.month, date.day

    # Convert month number to month name
    month_name = month_names.get(month)
    
    if day == 1:
        day = "1er"

    # Construct the French date string
    french_date_long, french_date_long_no_year = f"{day} {month_name}, {year}", f"{day} {month_name}"
    if with_year:
      return french_date_long
    else:
        return french_date_long_no_year

