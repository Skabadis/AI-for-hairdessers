import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import logging
import time


def url_wav_to_audio_file(recording_url):
    if not recording_url:
        return None, None
    
    # Check if the URL ends with ".wav"
    if not recording_url.endswith('.wav'):
        logging.error("URL does not end with .wav")
        raise ValueError("The URL must end with '.wav'")

    # Access API key
    load_dotenv()
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not twilio_account_sid or not twilio_auth_token:
        logging.error(
            "Twilio account SID or auth token not found in environment variables")
        raise EnvironmentError(
            "Twilio account SID or auth token not found in environment variables")

    # Polling variables
    max_attempts = 30  # Max number of polling attempts
    delay_seconds = 0.1  # Delay between polling attempts

    for attempt in range(max_attempts):
        try:
            start_time = time.time()
            response = requests.get(recording_url, auth=(
                twilio_account_sid, twilio_auth_token))
            end_time = time.time()
            logging.info(
                f"Requesting audio file (attempt {attempt + 1}): {end_time - start_time:.2f} seconds")

            if response.status_code == 200:
                break
            elif response.status_code == 404:
                logging.info(
                    f"Attempt {attempt + 1}: Recording URL not available yet, retrying after {delay_seconds} seconds.")
                time.sleep(delay_seconds)  # Wait before trying again
            else:
                logging.error(
                    f"Error retrieving audio file from Twilio: {response.status_code}")
                raise ConnectionError(
                    f"Error retrieving audio file from Twilio: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request for audio file failed: {e}")
            raise ConnectionError(f"Request for audio file failed: {e}")

    # If after max_attempts the file is still not available
    if response.status_code != 200:
        logging.error("Max attempts reached. Recording URL not available.")
        raise ConnectionError(
            f"Max attempts reached. Recording URL not available. Error: {response.status_code}")

    # Check if the response content is not empty
    if not response.content:
        logging.error("The response content is empty")
        raise ValueError("The response content is empty")

    # Initialize the BytesIO object
    try:
        audio_file = BytesIO(response.content)
    except Exception as e:
        logging.error(
            f"Failed to create BytesIO object from response content: {e}")
        raise RuntimeError(
            f"Failed to create BytesIO object from response content: {e}")

    return audio_file, response.content
