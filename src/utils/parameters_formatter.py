from utils.utils import convert_dt_to_date_short_str, convert_dt_to_date_long_str
from datetime import datetime, timedelta
import locale


def format_read_calendar_prompt(prompt):
    # Set the locale to French
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

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
