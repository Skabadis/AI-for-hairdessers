import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import logging
import time


def url_wav_to_audio_file(recording_url):
    # Check if the URL ends with ".wav"
    if not recording_url.endswith('.wav'):
        logging.error("URL does not end with .wav")
        raise ValueError("The URL must end with '.wav'")

    load_dotenv()
    
    # Access API key
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not twilio_account_sid or not twilio_auth_token:
        logging.error("Twilio account SID or auth token not found in environment variables")
        raise EnvironmentError("Twilio account SID or auth token not found in environment variables")
    
    # Request the audio file
    try:
        start_time = time.time()
        response = requests.get(recording_url, auth=(twilio_account_sid, twilio_auth_token))
        response.raise_for_status()  # Check if the request was successful
        end_time = time.time()
        logging.info(f"Requesting audio file: {end_time - start_time:.2f} seconds")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for audio file failed: {e}")
        raise ConnectionError(f"Request for audio file failed: {e}")
    
    # Check if the response content is not empty
    if not response.content:
        logging.error("The response content is empty")
        raise ValueError("The response content is empty")

    # Initialize the recognizer
    try:
        audio_file = BytesIO(response.content)
    except Exception as e:
        logging.error(f"Failed to create BytesIO object from response content: {e}")
        raise RuntimeError(f"Failed to create BytesIO object from response content: {e}")
    
    return audio_file