from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
import asyncio
import websockets

app = Flask(__name__)

@app.route("/answer-call", methods=['POST'])
def answer_call():
    response = VoiceResponse()

    response.say("Hello, you are speaking with our AI receptionist.")
    response.start(
        Stream(
            url="wss://your-websocket-server-url/stream"
        )
    )
    return str(response)

async def handle_stream(websocket, path):
    async for message in websocket:
        print(f"Received audio stream data: {message}")
        # Process the audio stream data with your AI system
        # Respond to the caller if necessary

# Run the WebSocket server
start_server = websockets.serve(handle_stream, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    app.run(debug=True)
