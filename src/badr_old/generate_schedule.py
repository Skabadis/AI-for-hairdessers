import pandas as pd
from datetime import datetime, timedelta

def generate_schedule():
    # Define working hours and days
    working_hours = [(10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0)]
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 31)

    # Generate dates for the month excluding weekends
    dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Exclude Saturday and Sunday
            dates.append(current_date)
        current_date += timedelta(days=1)

    # Create a DataFrame for the schedule
    schedule_data = []
    for date in dates:
        for hour, minute in working_hours:
            schedule_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Time': f'{hour:02d}:{minute:02d}',
                'Booking': '',
                'Details': ''
            })

    schedule_df = pd.DataFrame(schedule_data)
    schedule_df.to_csv('schedule_january_2025.csv', index=False)
    print("Schedule file created.")

if __name__ == "__main__":
    generate_schedule()
