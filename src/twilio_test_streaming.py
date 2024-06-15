from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
import asyncio
import websockets
import logging
from utils.logging_config import initialize_logger
from conversation.recording import initiate_call_recording

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
