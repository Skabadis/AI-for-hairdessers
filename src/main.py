from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from llms_connectors.openai_connector import get_openai_client
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
from workers.shutdown_worker import shutdown_worker
# Runs logging_config.py file which sets up the logs - do not remove
from utils.logging_config import initialize_logger
from utils.s3_interactions import upload_log_to_s3
import logging

app = Flask(__name__)

# Initialize global variables
parameters = None
conversation_history = None
openai_client = None
log_filename = None

@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    global parameters, conversation_history, openai_client, log_filename

    call_sid = request.values.get('CallSid')
    if call_sid:
        log_filename = initialize_logger(call_sid)

    # Load parameters
    parameters = read_params()
    logging.info(f"Parameters retrieved properly")

    # Provide conversation prompt
    conversation_history = [
        {"role": "system",
            "content": parameters["prompts"]["conversation_initial_prompt"]}
    ]
    logging.info(
        f"Conversation history retrieved properly: len = {len(conversation_history)}")

    # Get OpenAI client
    openai_client = get_openai_client()
    logging.info(f"OpenAI client retrieved properly: {openai_client}")

    # Prepare initial response with Gather to start the conversation
    resp = VoiceResponse()
    Sandra_response = parameters['discussion']['welcome_message']
    conversation_history.append(
        {"role": "assistant", "content": Sandra_response})
    gather = Gather(input='speech', action='/voice',
                    speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True, speechModel="experimental_conversations")
    gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')
    resp.append(gather)
    return str(resp)

# TODO: check how we are managing the conversation_history. We are adding user_input and Sandra_response here AND in agentic_answer, let's make sure we are not double adding everything
@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()
    try:
        user_input = request.form.get('SpeechResult')
        logging.info(f"User said: {user_input}")

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

        # Case when end of conversation
        # TODO: improve to have the worker start and shutdown based call start and end
        if Sandra_response.lower() == "end conversation":
            # Use alice to save cost, Polly.Lea-Neural for the best one
            resp.say("Au revoir", voice='Polly.Lea-Neural',
                     language='fr-FR')
            return str(resp)

        gather = Gather(input='speech', action='/voice',
                        speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True, speechModel="experimental_conversations")
        # Use alice to save cost, Polly.Lea-Neural for the best one
        gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')
        logging.info(f"Sandra's response: {Sandra_response}")

        resp.append(gather)
    except Exception as e:
        logging.error(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='Polly.Lea-Neural',
                 language='fr-FR')  # use alice to save cost, Polly.Lea-Neural for the best one

    return str(resp)

@app.route("/call-status", methods=['POST'])
def call_status():
    call_status = request.values.get('CallStatus')
    if call_status in ['completed', 'canceled', 'unanswered']:
        # Upload the log file to S3
        upload_log_to_s3(log_filename)
        # Shutdown the worker at the end of the call
        shutdown_worker()

    return ('', 204)