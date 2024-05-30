from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from llms_connectors.openai_connector import get_openai_client, chat
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
from dotenv import load_dotenv
import os
import logging

app = Flask(__name__)

# Load parameters and initialize OpenAI client
parameters = read_params()
conversation_history = [
    {"role": "system", "content": parameters["prompts"]["conversation_initial_prompt"]}
]
user_data = {}
openai_client = get_openai_client()

app.logger.info("OpenAI client retrieved properly")

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()

    try:
        user_input = request.form.get('SpeechResult')
        if user_input:
            app.logger.info(f"User said: {user_input}")
            conversation_history.append({"role": "user", "content": user_input})
            Sandra_response = agentic_answer(conversation_history, user_input, openai_client)
            conversation_history.append({"role": "assistant", "content": Sandra_response})
        else:
            # Initialize the AI conversation if no input is present
            Sandra_response = chat(conversation_history, openai_client)
            conversation_history.append({"role": "assistant", "content": Sandra_response})

        app.logger.info(f"Sandra's response: {Sandra_response}")

        gather = Gather(input='speech', action='/voice', timeout=5, language='fr-FR')
        gather.say(Sandra_response, voice='alice', language='fr-FR')
        resp.append(gather)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='alice', language='fr-FR')

    return str(resp)

if __name__ == "__main__":
    try:
        app.logger.info("Parameters loaded successfully")

        # Load Twilio credentials from .env
        load_dotenv()
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        app.logger.info(f"Twilio SID: {account_sid}")

        client = Client(account_sid, auth_token)
        app.run(debug=True)
    except Exception as e:
        app.logger.error(f"Failed to start the application: {e}")
