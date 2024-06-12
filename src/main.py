from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from llms_connectors.openai_connector import get_openai_client
from workers.shutdown_worker import shutdown_worker
from utils.read_params import read_params
from utils.logging_config import initialize_logger
from utils.s3_interactions import upload_log_to_s3, upload_content_to_s3
from conversation.text_to_text import agentic_answer
from conversation.recording import initiate_call_recording
from conversation.audio_processing import url_wav_to_audio_file
import logging

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
    call_sid = request.values.get('CallSid')
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
                conversation_history, user_input, openai_client, current_time, call_sid)

        # Add Sandra_reponse to conversation history
        conversation_history.append(
            {"role": "assistant", "content": Sandra_response})

        logging.info(f"Conversation history: {conversation_history[1:]}")
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