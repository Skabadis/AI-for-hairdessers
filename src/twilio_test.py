from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
# Runs logging_config.py file which sets up the logs - do not remove
from utils.logging_config import initialize_logger

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def initialize():
    call_sid = request.values.get('CallSid')
    if call_sid:
        initialize_logger(call_sid)
    # Prepare initial response with Gather to start the conversation
    resp = VoiceResponse()
    gather = Gather(input='speech', action='/voice', speechTimeout='auto',
                    language='fr-FR', actionOnEmptyResult=True)
    gather.say("Ceci est un test", voice='alice', language='fr-FR')
    resp.append(gather)
    return str(resp)
