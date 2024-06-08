from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Record, Say
# Runs logging_config.py file which sets up the logs - do not remove
from utils.logging_config import initialize_logger
import logging

app = Flask(__name__)

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    call_sid = request.values.get('CallSid')
    if call_sid:
        initialize_logger(call_sid)
        # Prepare initial response with Gather to start the conversation
    resp = VoiceResponse()
    record = Record(input='speech', action='/voice', speechTimeout='auto',
                    language='fr-FR', actionOnEmptyResult=True)
    answer = Say("Ceci est un test", voice='alice', language='fr-FR')
    resp.append(answer)
    resp.append(record)
    return str(resp)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    logging.info(f"Request values: {request.values}")
    recording_url = request.values.get('RecordingUrl', None)
    if recording_url:
        logging.info(f'Recording URL: {recording_url}')
        text = transcribe_twilio_audio(recording_url)
        logging.info(f"User input: {text}")
    else:
        logging.info("No recording URL")
    resp = VoiceResponse()
    record = Record(input='speech', action='/voice', speechTimeout='auto',
                    language='fr-FR', actionOnEmptyResult=True)
    answer = Say("Ceci est un test", voice='alice', language='fr-FR')
    resp.append(answer)
    resp.append(record)
    return str(resp)


import requests
from io import BytesIO
import speech_recognition as sr

# Function to transcribe audio from Twilio
def transcribe_twilio_audio(recording_url):
    response = requests.get(recording_url)
    if response.status_code == 200:
        audio_data = response.content
        recognizer = sr.Recognizer()
        with sr.AudioFile(BytesIO(audio_data)) as source:
            audio = recognizer.record(source)
            # Perform speech recognition
            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Speech recognition could not understand the audio"
            except sr.RequestError as e:
                return "Could not request results from Google Speech Recognition service; {0}".format(e)
    else:
        return f"Error retrieving audio file from Twilio: {response.status_code}"

# Usage
recording_url = "https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid}"
text = transcribe_twilio_audio(recording_url)
print("Transcribed text:", text)
