

# # Define working hours
# day = pd.to_datetime("2024-05-28")
# opening_time = pd.Timestamp("2024-05-28 09:00:00")
# closing_time = pd.Timestamp("2024-05-28 17:00:00")

# # Sample appointments DataFrame
# appointments = pd.DataFrame({
#     'day': [day] * 3,
#     'event_start': [pd.Timestamp("2024-05-28 09:30:00"), pd.Timestamp("2024-05-28 11:00:00"), pd.Timestamp("2024-05-28 13:00:00")],
#     'event_end': [pd.Timestamp("2024-05-28 10:30:00"), pd.Timestamp("2024-05-28 12:00:00"), pd.Timestamp("2024-05-28 14:00:00")]
# })


# availabilities_string = get_open_slots_str(appointments, day, opening_time, closing_time)