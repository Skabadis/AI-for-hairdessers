from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from llms_connectors.openai_connector import get_openai_client, chat
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming calls with a simple message."""
    print("Received a call request at /voice")
    resp = VoiceResponse()

    # Welcome message
    resp.say(parameters['welcome_message'], voice='alice', language='fr-FR')

    # Redirect to handle the call
    resp.redirect("/handle_call")

    return str(resp)

@app.route("/handle_call", methods=['GET', 'POST'])
def handle_call():
    print("Handling call at /handle_call")
    resp = VoiceResponse()

    try:
        # Initialize the AI conversation
        Sandra_response = chat(conversation_history, openai_client)
        conversation_history.append({"role": "assistant", "content": Sandra_response})
        
        # Debug message
        print(f"Sandra's response: {Sandra_response}")

        gather = Gather(input='speech', action='/process_input', timeout=5, language='fr-FR')
        gather.say(Sandra_response, voice='alice', language='fr-FR')
        resp.append(gather)
    except Exception as e:
        print(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='alice', language='fr-FR')

    return str(resp)

@app.route("/process_input", methods=['POST'])
def process_input():
    resp = VoiceResponse()
    try:
        user_input = request.form.get('SpeechResult')
        print(f"User said: {user_input}")

        if user_input:
            Sandra_response = agentic_answer(conversation_history, user_input, openai_client)
            print(f"Sandra: {Sandra_response}")
            gather = Gather(input='speech', action='/process_input', timeout=5, language='fr-FR')
            gather.say(Sandra_response, voice='alice', language='fr-FR')
            resp.append(gather)
    except Exception as e:
        print(f"Error in process_input: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='alice', language='fr-FR')

    return str(resp)

if __name__ == "__main__":
    parameters = read_params()

    # Twilio credentials
    load_dotenv()
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
                            
    client = Client(account_sid, auth_token)

    # Initialize AI conversation agent
    conversation_history = [
        {"role": "system", 
        "content": parameters["conversation_initial_prompt"]}
    ]

    user_data = {}

    openai_client = get_openai_client()

    app.run(debug=True)
