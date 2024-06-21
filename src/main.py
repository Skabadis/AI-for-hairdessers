from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from llms_connectors.openai_connector import get_openai_client
from workers.shutdown_worker import shutdown_worker
from utils.read_params import read_params
from utils.logging_config import initialize_logger
from db_connectors.s3_interactions import upload_log_to_s3, upload_content_to_s3
from conversation.text_to_text import agentic_answer
from conversation.recording import initiate_call_recording
from conversation.audio_processing import url_wav_to_audio_file
import logging
import traceback

app = Flask(__name__)

# Initialize global variables
# parameters = None
# conversation_history = None
# openai_client = None
# log_filename = None
# recording_url = None
# current_time = None

# Global in-memory storage for call data
call_data_store = {}

@app.route("/announce-recording", methods=['GET', 'POST'])
def announce_recording():
    # Create a TwiML response
    resp = VoiceResponse()
    
    # Have the bot say something
    resp.say("Cet appel peut etre enregistré pour des contrôle de qualité.", voice='Polly.Lea-Neural', language='fr-FR')
    
    # Redirect to another URL to trigger an action
    resp.redirect('/initialize')
    
    return str(resp)    
    
@app.route("/initialize", methods=['GET', 'POST'])
def initialize():
    # global parameters, conversation_history, openai_client, log_filename, current_time
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
    
    # Save necessary data to the call data store with call_sid
    global call_data_store
    call_data_store[call_sid] = {
        'log_filename': log_filename,
        'current_time': current_time,
        'parameters': parameters,
        'conversation_history': conversation_history,
        'openai_client': openai_client
    }
    
    logging.info(f"Call data store: {call_data_store}")

    return str(resp)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    call_sid = request.values.get('CallSid')
    resp = VoiceResponse()
    try:
        user_input = request.form.get('SpeechResult')
        logging.info(f"User said: {user_input}")

        # Get state variables
        current_time = call_data_store[call_sid]['current_time']
        parameters = call_data_store[call_sid]['parameters']
        conversation_history = call_data_store[call_sid]['conversation_history']
        openai_client = call_data_store[call_sid]['openai_client']
        
        # logging.info(f"Conversation history: {conversation_history}")
        logging.info(f"Call data store: {call_data_store}")
        # Get Sandra_response
        if not user_input:  # If no user input detected say no user input message
            Sandra_response = parameters['discussion']['no_user_input_message']
            conversation_history.append({"role": "assistant", "content": Sandra_response})
        else:  # If user input detected, regular conversation
            Sandra_response = agentic_answer(
                conversation_history, user_input, openai_client, current_time, call_sid)

        # TODO: improve to have the worker start and shutdown based call start and end
        if 'au revoir' in Sandra_response.lower():
            # Use alice to save cost, Polly.Lea-Neural for the best one
            resp.say(Sandra_response, voice='Polly.Lea-Neural',
                     language='fr-FR')
            return str(resp)

        gather = Gather(input='speech', action='/voice',
                        speechTimeout='auto', language='fr-FR', actionOnEmptyResult=True, speechModel="experimental_conversations")
        # Use alice to save cost, Polly.Lea-Neural for the best one
        gather.say(Sandra_response, voice='Polly.Lea-Neural', language='fr-FR')
        logging.info(f"Sandra's response: {Sandra_response}")

        resp.append(gather)
        
        # Save updated state to the Flask's request context
        call_data_store[call_sid]['conversation_history'] = conversation_history
        
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error: {e}\n Traceback: {tb}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='Polly.Lea-Neural',
                 language='fr-FR')  # use alice to save cost, Polly.Lea-Neural for the best one

    return str(resp)


@app.route("/call-status", methods=['POST'])
def call_status():
    call_status = request.values.get('CallStatus')
    call_sid = request.values.get('CallSid')
    if call_status in ['completed', 'canceled', 'no-answer']:
        logging.info(f"Call status: {call_status}")
        
        # Get data store variables
        log_filename = call_data_store[call_sid]['log_filename']
        parameters = call_data_store[call_sid]['parameters']
        recording_url = call_data_store[call_sid]['recording_url']
        
        # Upload recording to S3
        _, recording_content = url_wav_to_audio_file(recording_url)
        content_folder, bucket_name = parameters["paths"]["logs_recording"], parameters["paths"]["s3_bucket_name"]
        recording_filename = log_filename.replace(".log", ".wav")
        if recording_content:
          upload_content_to_s3(recording_content, recording_filename,
                              content_folder, bucket_name)
        else:
            logging.info('Recording_content is null, no recording to be saved.')
        # Shutdown the worker at the end of the call
        shutdown_worker()

        # Upload the log file to S3
        log_folder, bucket_name = parameters["paths"]["logs_info"], parameters["paths"]["s3_bucket_name"]
        upload_log_to_s3(log_filename, log_folder, bucket_name)
    return ('', 204)

@app.route("/recording-events", methods=['POST'])
def recording_events():
    call_sid = request.values.get('CallSid')
    # Retrieve recording URL and other details from Twilio's POST request
    recording_url = request.form['RecordingUrl'] + ".wav"
    
    # Save recording_url in call_data_store
    call_data_store[call_sid]['recording_url'] = recording_url
    logging.info(f"Recording URL: {recording_url}")
    return "", 200