from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from llms_connectors.openai_connector import get_openai_client
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
import os
import signal
# Runs logging_config.py file which sets up the logs
import utils.logging_config

app = Flask(__name__)

# Load parameters and initialize OpenAI client
parameters = read_params()
conversation_history = [
    {"role": "system",
        "content": parameters["prompts"]["conversation_initial_prompt"]}
]
openai_client = get_openai_client()

app.logger.info("OpenAI client retrieved properly")


def shutdown_worker():
    """Send a signal to stop the current worker."""
    worker_pid = os.getpid()
    app.logger.info(
        f"Shutting down worker because shutdown_worker function was called. PID: {worker_pid}")
    os.kill(worker_pid, signal.SIGTERM)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()

    try:
        user_input = request.form.get('SpeechResult')
        app.logger.info(f"User said: {user_input}")

        # Initial interaction or no user input detected
        if not user_input:
            if len(conversation_history) == 1:  # First interaction
                Sandra_response = parameters['discussion']['welcome_message']
            else:  # No response during conversation
                Sandra_response = "Je n'ai pas entendu votre réponse. Pouvez-vous répéter?"

            conversation_history.append(
                {"role": "assistant", "content": Sandra_response})
        # User input detected, regular conversation
        else:
            conversation_history.append(
                {"role": "user", "content": user_input})
            Sandra_response = agentic_answer(
                conversation_history, user_input, openai_client)
            if Sandra_response.lower() == "end conversation":
                # Use alice to save cost, Polly.Lea-Neural for the best one
                resp.say("Au revoir", voice='Polly.Lea-Neural',
                         language='fr-FR')
                # Shutdown the worker at the end of the call
                shutdown_worker()  
                return str(resp)

        conversation_history.append(
            {"role": "assistant", "content": Sandra_response})
        app.logger.info(f"Sandra's response: {Sandra_response}")

        gather = Gather(input='speech', action='/voice',
                        speechTimeout='auto', language='fr-FR')
        # Use alice to save cost, Polly.Lea-Neural for the best one
        gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')

        resp.append(gather)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='Polly.Lea-Neural',
                 language='fr-FR')  # use alice to save cost, Polly.Lea-Neural for the best one

    return str(resp)
