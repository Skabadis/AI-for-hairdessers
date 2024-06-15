from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
import asyncio
import websockets
import logging
from utils.logging_config import initialize_logger
from conversation.recording import initiate_call_recording
from db_connectors.s3_interactions import upload_log_to_s3, upload_content_to_s3
from workers.shutdown_worker import shutdown_worker
from conversation.audio_processing import url_wav_to_audio_file


app = Flask(__name__)

# Initialize global variables
parameters = None
conversation_history = None
openai_client = None
log_filename = None
recording_url = None
current_time = None

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global parameters, conversation_history, openai_client, log_filename, current_time

    call_sid = request.values.get('CallSid')
    if call_sid:
        log_filename, current_time = initialize_logger(call_sid)
        initiate_call_recording(call_sid)
    logging.info('Entered answer_call')
    response = VoiceResponse()        
    response.say("Hello, you are speaking with our AI receptionist.")
    response.start(
        Stream(
            url="wss://13.50.101.111:8765/stream"
        )
    )
    return str(response)


@app.route("/call-status", methods=['POST'])
def call_status():
    call_status = request.values.get('CallStatus')
    if call_status in ['completed', 'canceled', 'no-answer']:
        logging.info(f"Call status: {call_status}")

        # Upload recording to S3
        _, recording_content = url_wav_to_audio_file(recording_url)
        content_folder, bucket_name = parameters["paths"]["logs_recording"], parameters["paths"]["s3_bucket_name"]
        recording_filename = log_filename.replace(".log", ".wav")
        upload_content_to_s3(recording_content, recording_filename,
                             content_folder, bucket_name)

        # Shutdown the worker at the end of the call
        shutdown_worker()

        # Upload the log file to S3
        log_folder, bucket_name = parameters["paths"]["logs_info"], parameters["paths"]["s3_bucket_name"]
        upload_log_to_s3(log_filename, log_folder, bucket_name)
    return ('', 204)

@app.route("/recording-events", methods=['POST'])
def recording_events():
    global recording_url
    # Retrieve recording URL and other details from Twilio's POST request
    recording_url = request.form['RecordingUrl'] + ".wav"
    logging.info(f"Recording URL: {recording_url}")
    return "", 200

async def handle_stream(websocket, path):
    logging.info("Entered handle_stream")
    print("Entered handle_stream")
    async for message in websocket:
        print(f"Received audio stream data: {message}")
        logging.info(f"Received audio stream data: {message}")
        # Process the audio stream data with your AI system
        # Respond to the caller if necessary

# Run the WebSocket server
start_server = websockets.serve(handle_stream, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    app.run(debug=True)
