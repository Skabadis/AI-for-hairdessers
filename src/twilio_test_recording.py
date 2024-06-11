from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
from utils.logging_config import initialize_logger
from utils.s3_interactions import upload_log_to_s3, upload_content_to_s3
from workers.shutdown_worker import shutdown_worker
from dotenv import load_dotenv
import os
import requests
from conversation.audio_processing import url_wav_to_audio_file
from utils.read_params import read_params

app = Flask(__name__)

log_filename = None
parameters = None
recording_url = None


@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global log_filename, parameters, recording_url

    parameters = read_params()
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

    gather = Gather(input='speech', action='/voice',
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
        # Upload the log file to S3
        log_folder, bucket_name = parameters["paths"]["logs_info"], parameters["paths"]["s3_bucket_name"]
        upload_log_to_s3(log_filename, log_folder, bucket_name)

        # Upload recording to S3
        _, recording_content = url_wav_to_audio_file(recording_url)
        content_folder, bucket_name = parameters["paths"]["logs_recording"], parameters["paths"]["s3_bucket_name"]
        upload_content_to_s3(recording_content, log_filename,
                             content_folder, bucket_name)

        # Shutdown the worker at the end of the call
        shutdown_worker()
    return ('', 204)


@app.route("/recording-events", methods=['POST'])
def recording_events():
    # Retrieve recording URL and other details from Twilio's POST request
    recording_url = request.form['RecordingUrl'] + ".wav"
    logging.info(f"Recording URL: {recording_url}")
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

    if response.status_code == 201:
        logging.info("Call recording initiated successfully.")
    else:
        logging.error(
            f"Failed to initiate call recording. Status code: {response.status_code}, Error: {response.text}")
