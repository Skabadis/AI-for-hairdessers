from llms_connectors.openai_connector import chat
from google_calendar_api.read_calendar import read_calendar
from google_calendar_api.write_event import add_event
from calendar_operations.open_slots import get_open_slots_str
from utils.read_params import read_params
from utils.parameters_formatter import format_read_calendar_prompt, format_availability_message
import json
import pandas as pd
import logging
import os

def get_events_workflow(json_input_str, conversation_history, params):
    date = json.loads(json_input_str)['date']
    logging.info(f"Success, dictionary well converted: {date}")

    events_df = read_calendar(date)
    appointments = events_df[["event_start", "event_end"]]
    logging.info(appointments)

    availabilities_string = get_open_slots_str(appointments, date)
    message = params["discussion"]["availability_message"]

    Sandra_response = format_availability_message(
        message, date, availabilities_string)
    conversation_history.append(
        {"role": "assistant", "content": Sandra_response})
    return Sandra_response


def save_event_workflow(json_input_str, conversation_history, params):
    event = json.loads(json_input_str)
    logging.info(f"Success, dictionary well converted: {event}")

    start = event["start"]
    endTime = pd.Timestamp(
        start["dateTime"], tz=start["timeZone"]) + pd.Timedelta(minutes=30)
    endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S')

    event["end"] = {"dateTime": endTime,
                    "timeZone": start["timeZone"]}
    add_event(event)

    # Confirm appointment was booked to customer
    conversation_history.append({"role": "assistant",
                                 "content": params["discussion"]["event_saved_message"]})
    Sandra_response = params["discussion"]["event_saved_message"]
    return Sandra_response

def save_request_workflow(json_input_str, conversation_history, params):
    request_json = json.loads(json_input_str)
    logging.info(f"Success, dictionary well converted: {request_json}")    
    df = pd.DataFrame(request_json)
    if not os.path.exists("data/"):
        os.makedirs("data/")
    df.to_csv("data/request.csv", index=False)
    logging.info("Saved request in csv")
    
    
def agentic_answer(conversation_history, user_input, openai_client):
    """
    Text to text module perfomring the interaction between the user input and the model output.

    Args:
        conversation_history (list): List with previous unteractions between user and model (context)
        user_input (text): Converted text of wht the user just said
        openai_client (object): OpenAI API client object

    Returns:
        Sandra_reponse (text): LLM response
    """
    params = read_params()

    # Regular answer workflow
    conversation_history.append({"role": "user", "content": user_input})
    Sandra_response = chat(conversation_history, openai_client)
    # TODO: put it after the ifs?
    conversation_history.append(
        {"role": "assistant", "content": Sandra_response})

    # Read calendar workflow
    # if ('regarde' in Sandra_response) and ('calendrier' in Sandra_response):

    #     read_calendar_prompt = format_read_calendar_prompt(
    #         params['prompts']['read_calendar_on_day_prompt'])
    #     logging.info("Regarde calendrier")
    #     conversation_history.append({"role": "system",
    #                                  "content": read_calendar_prompt})
    #     json_input_str = chat(conversation_history, openai_client)
    #     logging.info(json_input_str)
    #     try:
    #         Sandra_response = get_events_workflow(
    #             json_input_str, conversation_history, params)
    #         return Sandra_response
    #     except Exception as e:
    #         logging.info(
    #             f"An error occurred when trying to get date to read calendar: {e}")
    #         return params["discussion"]["error_message"]

    # Save event workflow
    if 'sauvegarde' in Sandra_response.lower():
        logging.info("Sauvegarde")
        conversation_history.append({"role": "system",
                                     "content": params["prompts"]["write_event_prompt"]})
        json_input_str = chat(conversation_history, openai_client)
        logging.info(f"This is supposed to be a JSON:\n {json_input_str}")
        try:
            Sandra_response = save_event_workflow(
                json_input_str, conversation_history, params)
            return Sandra_response
        except Exception as e:
            logging.info(
                f"An error occurred when trying to write event to calendar: {e}")
            return params["discussion"]["error_message"]

    # End conversation workflow
    if 'au revoir' in Sandra_response.lower():
        logging.info(f"Sandra's response: {Sandra_response}")
        logging.info("Au revoir")
        return "End conversation"
    return Sandra_response
