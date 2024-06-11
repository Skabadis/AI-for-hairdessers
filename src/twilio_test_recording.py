from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
from utils.logging_config import initialize_logger
from utils.s3_interactions import upload_log_to_s3
from workers.shutdown_worker import shutdown_worker


app = Flask(__name__)

log_filename = None

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global log_filename
    call_sid = request.values.get('CallSid')
    if call_sid:
        log_filename = initialize_logger(call_sid)
        
    resp = VoiceResponse()
    # Record the call
    resp.record(max_length=3600, recording_status_callback='/recording-status')  # Adjust max_length as needed
    # Redirect to /gather after starting the recording
    resp.redirect('/process_gather')
    
    return str(resp)

@app.route("/process_gather", methods=['GET', 'POST'])
def process_gather():
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

@app.route("/recording-status", methods=['POST'])
def recording_status():
    # Retrieve recording URL and other details from Twilio's POST request
    recording_url = request.form['RecordingUrl']
    recording_sid = request.form['RecordingSid']
    call_sid = request.form['CallSid']

    # You can save this information to a database or take other actions
    logging.info(f"Recording URL: {recording_url}, Recording SID: {recording_sid}, Call SID: {call_sid}")
    
    # Return an empty response as required by Twilio
    return "", 200

@app.route("/call-status", methods=['POST'])
def call_status():
    call_status = request.values.get('CallStatus')
    if call_status in ['completed', 'canceled', 'no-answer']:
        # Shutdown the worker at the end of the call
        shutdown_worker()
        # Upload the log file to S3
        upload_log_to_s3(log_filename)
    return ('', 204)