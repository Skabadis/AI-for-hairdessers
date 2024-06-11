from dotenv import load_dotenv
import requests
import logging
import os

def initiate_call_recording(call_sid):
    load_dotenv()
    TWILIO_ACCOUNT_SID,  = os.getenv("TWILIO_ACCOUNT_SID"),
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls/{call_sid}/Recordings.json"
    
    access_point_ip = os.getenv("EC2_HOST")
    recording_callback_url = f"http://{access_point_ip}:8000/recording-events"

    payload = {
        "RecordingStatusCallback": recording_callback_url,
        "RecordingStatusCallbackEvent": "in-progress completed absent"
    }

    response = requests.post(
        twilio_recording_url,
        data=payload,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )

    if response.status_code == 201:
        logging.info("Call recording initiated successfully.")
    else:
        logging.error(
            f"Failed to initiate call recording. Status code: {response.status_code}, Error: {response.text}")
      
    # return f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Recordings/{call_sid}.wav"
      