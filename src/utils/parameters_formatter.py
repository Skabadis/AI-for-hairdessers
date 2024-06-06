from utils.utils import convert_dt_to_date_short_str, convert_dt_to_date_long_str, convert_dt_to_date_long_no_year_str
from datetime import datetime, timedelta


def format_read_calendar_prompt(prompt):
    # Get today's date
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    after_tomorrow = today + timedelta(days=2)

    # Format the dates to desired string format (e.g., "2024-01-01" and January 1, 2024)
    today_short_str, today_long_str = convert_dt_to_date_short_str(
        today), convert_dt_to_date_long_str(today)
    tomorrow_short_str, tomorrow_long_str = convert_dt_to_date_short_str(
        tomorrow), convert_dt_to_date_long_str(tomorrow)
    after_tomorrow_short_str, after_tomorrow_long_str = convert_dt_to_date_short_str(
        after_tomorrow), convert_dt_to_date_long_str(after_tomorrow)

    prompt_formatted = prompt.format(
        today_long_str, today_short_str, tomorrow_long_str, tomorrow_short_str, after_tomorrow_long_str, after_tomorrow_short_str)
    return prompt_formatted


def format_availability_message(message, date, availabilities_string):
    return message.format(convert_dt_to_date_long_no_year_str(date), availabilities_string)
