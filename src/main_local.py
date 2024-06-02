from conversation.speech_to_text import listen
from conversation.text_to_speech import speak
from llms_connectors.openai_connector import get_openai_client, chat
from google_calendar_api.read_calendar import read_calendar
from utils.read_params import read_params
from conversation.text_to_text import agentic_answer
import utils.logging_config
import logging

"""
   Current issues:
   1. Long latency
   2. Appointments are suggested even though they are not long enough for the treatment 
   3. Sometimes the mike doesnt turn off and Listening goes on forever
"""

if __name__ == "__main__":
    parameters = read_params()
    
    # Initial conversation history for the OpenAI model
    conversation_history = [
        {"role": "system", 
        "content": parameters["prompts"]["conversation_initial_prompt"]}
    ]
    openai_client = get_openai_client()


    Sandra_response = parameters['discussion']['welcome_message']
    conversation_history.append( 
                                {"role": "assistant", 
                                "content": Sandra_response})
    print(Sandra_response)
    logging.info(Sandra_response)
    speak(Sandra_response)
    
    while True:
        user_input = listen()
        if user_input:
            if Sandra_response == "End conversation":
                speak("Au revoir")
                break
            Sandra_response = agentic_answer(conversation_history, user_input, openai_client)
            # Print the last message in conversation which is supposed to be SAndra's. 
            print(f"Sandra: {Sandra_response}")
            logging.info(Sandra_response)
            speak(Sandra_response)
            

        