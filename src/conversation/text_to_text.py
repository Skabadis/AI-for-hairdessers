from llms_connectors.openai_connector import chat
from google_calendar_api.read_calendar import read_calendar
from google_calendar_api.write_event import add_event
from google_calendar_api.get_credentials import get_credentials
from calendar_operations.open_slots import get_open_slots_str

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
  
  conversation_history.append({"role": "user", "content": user_input})
  Sandra_response = chat(conversation_history, openai_client)
  conversation_history.append({"role": "assistant", "content": Sandra_response})

  if 'au revoir' in Sandra_response.lower():
      print(Sandra_response)
      return "End conversation"
      # Ajouter le rendez-vous au calendrier
      # creds = get_credentials()

      # add_event(event, creds)

  if 'regarde le calendrier' in Sandra_response:
      events_df = read_calendar()
      appointments = events_df[["event_start", "event_end"]]
      print(appointments)
      
      Sandra_response = get_open_slots_str(appointments, "2024-05-30")
      # Sandra_response = "Nous avons des disponibilités demain de 9h à 11h et de 13h à 15h"
      conversation_history.append({"role": "assistant", "content": Sandra_response})
  # if 'save event' in Sandra_response:
      
  print(f"Sandra: {Sandra_response}")
  return Sandra_response






      # event = {
      #     'summary': 'Rdv - Skabadis',
      #     'description': 'Rendez-vous pris par téléphone',
      #     'start': {
      #         'dateTime': '2024-05-28T11:00:00+02:00',  # Utilisez les données de l'utilisateur ici
      #         'timeZone': 'Europe/Paris',
      #     },
      #     'end': {
      #         'dateTime': '2024-05-28T11:30:00+02:00',  # Utilisez les données de l'utilisateur ici
      #         'timeZone': 'Europe/Paris',
      #     },
      #     'attendees': [
      #         {'email': 'contactskabadis@gmail.com'},
      #     ],
      # }