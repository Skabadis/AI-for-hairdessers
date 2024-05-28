from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from llms_connectors.openai_connector import get_openai_client, chat
from google_calendar_api.read_calendar import read_calendar
from google_calendar_api.write_event import add_event
from google_calendar_api.get_credentials import get_credentials

app = Flask(__name__)

# Twilio credentials
account_sid = 'ACafb4c3e0b611e9b7c209a99fdac2f235'
auth_token = 'e47a742920fc8ba7a4363dc4580a03ba'
client = Client(account_sid, auth_token)

# Initialize AI conversation agent
conversation_history = [
    {"role": "system", 
     "content": """
    Vous êtes Sandra, une assistante sympathique et serviable de Skabadis, un coiffeur parisien. Vous répondez en français et aidez les clients à prendre rendez-vous. 
     
    Tout d'abord, vous devez déterminer le service que le client souhaite recevoir. Il y a trois options : coupe de cheveux pour homme (rendez-vous de 30 minutes), coupe de cheveux pour femme (rendez-vous d'une heure) et teinture de cheveux pour femme (rendez-vous de 45 minutes). 
     
    Deuxièmement, après avoir déterminé ce que le client veut faire, vous devez trouver un bon moment pour le rendez-vous. Pour ce faire il faut que tu regardes notre calendrier. Réponds: "Je regarde le calendrier." 
           
    Troisièmement, une fois que vous avez trouvé un bon moment pour le rendez-vous, vous devez demander au client ses coordonnées (nom, prénom et numéro de téléphone). 
     
    Quatrièmement, confirmez les coordonnées du client et assurez-vous qu'elles sont correctes. Si vous avez fait une erreur, répétez avec le client jusqu'à ce qu'il confirme que vous avez bien fait les choses.
     
    Cinquièmement, confirmez au client que son rendez-vous a été pris et attendez sa réponse. Ne dites surtout pas au revoir à cette étape!
     
    Enfin, lorsque toutes les étapes sont terminées ou que l'utilisateur vous dit au revoir, vous devez dire au revoir au client. Veuillez dire explicitement « au revoir » dans votre message.
     
    Vous devez avoir une conversation avec le client et interagir avec lui comme si vous étiez un être humain au téléphone. Ne demandez pas tout d'emblée. Passez chaque étape une par une et attendez que le client réponde, et assurez-vous de terminer chaque étape avant de passer à la suivante.
    """}
]

user_data = {}

openai_client = get_openai_client()

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming calls with a simple message."""
    print("Received a call request at /voice")
    resp = VoiceResponse()

    # Welcome message
    resp.say("Bonjour, bienvenue chez Skabadis. Veuillez patienter pendant que nous traitons votre appel.", voice='alice', language='fr-FR')

    # Redirect to handle the call
    resp.redirect("/handle_call")

    return str(resp)

@app.route("/handle_call", methods=['GET', 'POST'])
def handle_call():
    print("Handling call at /handle_call")
    resp = VoiceResponse()

    try:
        # Initialize the AI conversation
        Sandra_response = chat(conversation_history, openai_client)
        conversation_history.append({"role": "assistant", "content": Sandra_response})
        
        # Debug message
        print(f"Sandra's response: {Sandra_response}")

        gather = Gather(input='speech', action='/process_input', timeout=5, language='fr-FR')
        gather.say(Sandra_response, voice='alice', language='fr-FR')
        resp.append(gather)
    except Exception as e:
        print(f"Error: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='alice', language='fr-FR')

    return str(resp)

@app.route("/process_input", methods=['POST'])
def process_input():
    resp = VoiceResponse()
    try:
        user_input = request.form.get('SpeechResult')
        print(f"User said: {user_input}")

        if user_input:
            conversation_history.append({"role": "user", "content": user_input})
            Sandra_response = chat(conversation_history, openai_client)
            conversation_history.append({"role": "assistant", "content": Sandra_response})

            if 'au revoir' in Sandra_response.lower():
                print(Sandra_response)
                # Ajouter le rendez-vous au calendrier
                creds = get_credentials()
                event = {
                    'summary': 'Rdv - Skabadis',
                    'description': 'Rendez-vous pris par téléphone',
                    'start': {
                        'dateTime': '2024-05-28T11:00:00+02:00',  # Utilisez les données de l'utilisateur ici
                        'timeZone': 'Europe/Paris',
                    },
                    'end': {
                        'dateTime': '2024-05-28T11:30:00+02:00',  # Utilisez les données de l'utilisateur ici
                        'timeZone': 'Europe/Paris',
                    },
                    'attendees': [
                        {'email': 'contactskabadis@gmail.com'},
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 10},
                        ],
                    },
                }
                add_event(event, creds)

                resp.say(Sandra_response, voice='alice', language='fr-FR')
                return str(resp)

            if 'regarde le calendrier' in Sandra_response:
                events_df = read_calendar()
                print(events_df)
                Sandra_response = "Nous avons des disponibilités demain de 9h à 11h et de 13h à 15h"
                conversation_history.append({"role": "assistant", "content": Sandra_response})

            print(f"Sandra: {Sandra_response}")
            gather = Gather(input='speech', action='/process_input', timeout=5, language='fr-FR')
            gather.say(Sandra_response, voice='alice', language='fr-FR')
            resp.append(gather)
    except Exception as e:
        print(f"Error in process_input: {e}")
        resp.say("Une erreur est survenue. Veuillez réessayer plus tard.", voice='alice', language='fr-FR')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
