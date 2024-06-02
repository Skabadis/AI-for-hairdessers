from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from llms_connectors.openai_connector import get_openai_client
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
from workers.shutdown_worker import shutdown_worker
# Runs logging_config.py file which sets up the logs - do not remove
import utils.logging_config

app = Flask(__name__)

# Initialize global variables
parameters = None
conversation_history = None
openai_client = None


@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global parameters, conversation_history, openai_client

    # Load parameters
    parameters = read_params()
    app.logger.info(f"Parameters retrieved properly: {parameters}")

    # Provide conversation prompt
    conversation_history = [
        {"role": "system",
            "content": parameters["prompts"]["conversation_initial_prompt"]}
    ]
    app.logger.info(
        f"Conversation history retrieved properly: len = {len(conversation_history)}")

    # Get OpenAI client
    openai_client = get_openai_client()
    app.logger.info(f"OpenAI client retrieved properly: {openai_client}")

    # Prepare initial response with Gather to start the conversation
    resp = VoiceResponse()
    Sandra_response = parameters['discussion']['welcome_message']
    conversation_history.append(
        {"role": "assistant", "content": Sandra_response})
    gather = Gather(input='speech', action='/voice', speechTimeout='auto',
                    language='fr-FR', actionOnEmptyResult=True)
    gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')
    resp.append(gather)
    return str(resp)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()
    app.logger.info(f"Request parameters: {request.form}")
    app.logger.info(f"VoiceResponse object: {resp}")
    try:
        user_input = request.form.get('SpeechResult')
        app.logger.info(f"User said: {user_input}")

        # Get Sandra_response
        if not user_input:  # If no user input detected say no user input message
            Sandra_response = parameters['discussion']['no_user_input_message']
        else:  # If user input detected, regular conversation
            conversation_history.append(
                {"role": "user", "content": user_input})
            Sandra_response = agentic_answer(
                conversation_history, user_input, openai_client)

        # Add Sandra_reponse to conversation history
        conversation_history.append(
            {"role": "assistant", "content": Sandra_response})
        app.logger.info(f"Sandra's response: {Sandra_response}")

        # Case when end of conversation
        # TODO: improve to have the worker start and shutdown based call start and end
        if Sandra_response.lower() == "end conversation":
            # Use alice to save cost, Polly.Lea-Neural for the best one
            resp.say("Au revoir", voice='Polly.Lea-Neural',
                     language='fr-FR')
            # Shutdown the worker at the end of the call
            shutdown_worker()
            return str(resp)

        gather = Gather(input='speech', action='/voice',
                        speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True)
        # Use alice to save cost, Polly.Lea-Neural for the best one
        gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')

        resp.append(gather)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='Polly.Lea-Neural',
                 language='fr-FR')  # use alice to save cost, Polly.Lea-Neural for the best one

    return str(resp)
