from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
from utils.logging_config import initialize_logger
from utils.s3_interactions import upload_log_to_s3
from workers.shutdown_worker import shutdown_worker
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

log_filename = None


@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global log_filename
    call_sid = request.values.get('CallSid')
    if call_sid:
        log_filename = initialize_logger(call_sid)
        initiate_call_recording(call_sid)
        
    resp = VoiceResponse()
    gather = Gather(input='speech', action='/voice',
                    speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True, speechModel="experimental_conversations")
    gather.say("Ceci est un test", voice='alice', language='fr-FR')
    # Append gather to the response
    resp.append(gather)

    return str(resp)

@app.route("/voice", methods=["POST", "GET"])
def voice():
    resp = VoiceResponse()
    # Process the gather input (you can add your own logic here)
    if 'SpeechResult' in request.form:
        speech_result = request.form['SpeechResult']
        logging.info(f"User said: {speech_result}")

    gather = Gather(input='speech', action='/process_gather',
                    speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True, speechModel="experimental_conversations")
    gather.say("Ceci est un test", voice='alice', language='fr-FR')
    # Append gather to the response
    resp.append(gather)

    return str(resp)

@app.route("/call-status", methods=['POST'])
def call_status():
    call_status = request.values.get('CallStatus')
    if call_status in ['completed', 'canceled', 'no-answer']:
        logging.info(f"Call status: {call_status}")
        # Shutdown the worker at the end of the call
        shutdown_worker()
        # Upload the log file to S3
        upload_log_to_s3(log_filename)
    return ('', 204)

@app.route("/recording-events", methods=['POST'])
def recording_events():
    # Retrieve recording URL and other details from Twilio's POST request
    recording_url = request.form['RecordingUrl']
    recording_sid = request.form['RecordingSid']
    call_sid = request.form['CallSid']

    # Log the recording information
    logging.info(f"Recording URL: {recording_url}, Recording SID: {recording_sid}, Call SID: {call_sid}")

    # You can save this information to a database or take other actions
    # For example, you can save the recording URL to a database for future reference

    # Return an empty response as required by Twilio
    return "", 200

def initiate_call_recording(call_sid):
    load_dotenv()
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN = os.getenv(
        "TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
    recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls/{call_sid}/Recordings.json"
    recording_callback_url = "http://13.50.101.111:8000/recording-events"

    payload = {
        "RecordingStatusCallback": recording_callback_url,
        "RecordingStatusCallbackEvent": "in-progress completed absent"
    }

    response = requests.post(
        recording_url,
        data=payload,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )

    if response.status_code == 200:
        logging.info("Call recording initiated successfully.")
    else:
        logging.error(
            f"Failed to initiate call recording. Status code: {response.status_code}, Error: {response.text}")
