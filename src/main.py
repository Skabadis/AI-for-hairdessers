from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from llms_connectors.openai_connector import get_openai_client, chat
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
from dotenv import load_dotenv
import os
import logging
import signal

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

# Load parameters and initialize OpenAI client
parameters = read_params()
conversation_history = [
    {"role": "system", "content": parameters["prompts"]["conversation_initial_prompt"]}
]
openai_client = get_openai_client()

app.logger.info("OpenAI client retrieved properly")

def shutdown_worker():
    """Send a signal to stop the current worker."""
    worker_pid = os.getpid()
    app.logger.info(f"Shutting down worker with PID: {worker_pid}")
    os.kill(worker_pid, signal.SIGTERM)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()

    try:
        user_input = request.form.get('SpeechResult')
        
        if not user_input:  # If no user input, provide the initial response
            Sandra_response = parameters['discussion']['welcome_message']
            conversation_history.append({"role": "assistant", "content": Sandra_response})
        else:
            app.logger.info(f"User said: {user_input}")
            conversation_history.append({"role": "user", "content": user_input})
            Sandra_response = agentic_answer(conversation_history, user_input, openai_client)
            if Sandra_response.lower() == "end conversation":
                resp.say("Au revoir", voice='alice', language='fr-FR')
                shutdown_worker()  # Shutdown the worker at the end of the call
                return str(resp)
        
        conversation_history.append({"role": "assistant", "content": Sandra_response})
        app.logger.info(f"Sandra's response: {Sandra_response}")

        gather = Gather(input='speech', action='/voice', timeout=4, language='fr-FR')
        gather.say(Sandra_response, voice='alice', language='fr-FR')
    
        resp.append(gather)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='Polly.Mathieu-Neural', language='fr-FR')

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
        app.run(debug=True, host='0.0.0.0', port=8000)
    except Exception as e:
        app.logger.error(f"Failed to start the application: {e}")
