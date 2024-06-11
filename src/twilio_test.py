from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Record, Say
import logging
from utils.logging_config import initialize_logger
from conversation.speech_to_text import audio_file_to_text
from conversation.audio_processing import url_wav_to_audio_file

app = Flask(__name__)


@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    call_sid = request.values.get('CallSid')
    if call_sid:
        initialize_logger(call_sid)
        # Prepare initial response with Gather to start the conversation
    resp = VoiceResponse()
    record = Record(action='/voice', timeout=1, playBeep=False)
    answer = Say("Ceci est un test", voice='alice', language='fr-FR')
    resp.append(answer)
    resp.append(record)
    return str(resp)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    # logging.info(f"Request values: {request.values}")
    recording_url = request.values.get('RecordingUrl', None) + ".wav"
    if recording_url:
        logging.info(f'Recording URL: {recording_url}')
        audio_file, _ = url_wav_to_audio_file(recording_url)
        text = audio_file_to_text(audio_file)
        logging.info(f"User input: {text}")
    else:
        logging.info("No recording URL")
    resp = VoiceResponse()
    record = Record(action='/voice', timeout=3, playBeep=False)
    answer = Say("Ceci est un test", voice='alice', language='fr-FR')
    resp.append(answer)
    resp.append(record)
    return str(resp)