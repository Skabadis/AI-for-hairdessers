from speech_to_text import listen
from text_to_speech import speak
from openai_connector import get_openai_client, chat_with_pia

"""
   Current issues:
   1. Long latency
   2. Appointments are suggested even though they are not long enough for the treatment 
"""

if __name__ == "__main__":
    print("Bienvenue chez Skabadis, je suis Pia, comment puis-je vous aider?")
    speak("Bienvenue chez Skabadis, je suis Pia, comment puis-je vous aider?")

    # Initial conversation history for the OpenAI model
    conversation_history = [
        {"role": "system", 
         "content": """
         
         You are Pia, a friendly and helpful assistant for Skabadis, a Parisian hairdresser. You respond in French and assist clients with booking appointments. 
         First, you need to figure out what service the customer wants to receive. There are three options, man hair cut (30 minutes appointment), women haircut (one hour appointment) and woman hair dying (45 mintues appointment). 
         
         Second, after figuring out what the customer wants to do, you need to find a good time for the appointment. Our available times for tomorrow are: 9am-11am, 1pm-2pm, 3.30pm - 4pm. You need to make sure to only suggest slots that are long enough for the service the customer wants. 
         
         Finally, once you found a good time for the appointment you need to ask the customer his relevant contact details (first name, last name qnd phone number). 
         
         You need to have a conversation with the customer and interact with the customer as if you were a human on the phone. Do not ask everyhting from the get go. Go through each step one by one and wait for the customer to reply, and make sure you finish each step before moving to the next one. 
         
         Finally, when all steps are complete or when the user says goodbye, you need to say the word 'Fin de discussion'. Say exactly that and nothing else."""}
    ]

    user_data = {}

    client = get_openai_client()
    while True:
        user_input = listen()
        if user_input:
            conversation_history.append({"role": "user", "content": user_input})

            # Get Pia's response from the OpenAI model
            pia_response = chat_with_pia(conversation_history, client)
            
            if 'Fin de discussion' in pia_response:
                print(pia_response)
                break
            conversation_history.append({"role": "assistant", "content": pia_response})

            print(f"Pia: {pia_response}")
            speak(pia_response)

