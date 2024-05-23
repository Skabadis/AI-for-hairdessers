from conversation.speech_to_text import listen
from conversation.text_to_speech import speak
from llms_connectors.openai_connector import get_openai_client, chat
from google_calendar_api.read_calendar import read_calendar

"""
   Current issues:
   1. Long latency
   2. Appointments are suggested even though they are not long enough for the treatment 
   3. Sometimes the mike doesnt turn off and Listening goes on forever
"""

if __name__ == "__main__":
    print("Bienvenue chez Skabadis, je suis Sandra, comment puis-je vous aider?")
    speak("Bienvenue chez Skabadis, je suis Sandra, comment puis-je vous aider?")

    # Initial conversation history for the OpenAI model
    conversation_history = [
        {"role": "system", 
         "content": """
         
        Vous êtes Sandra, une assistante sympathique et serviable de Skabadis, un coiffeur parisien. Vous répondez en français et aidez les clients à prendre rendez-vous. 
         
        Tout d'abord, vous devez déterminer le service que le client souhaite recevoir. Il y a trois options : coupe de cheveux pour homme (rendez-vous de 30 minutes), coupe de cheveux pour femme (rendez-vous d'une heure) et teinture de cheveux pour femme (rendez-vous de 45 minutes). 
         
        Deuxièmement, après avoir déterminé ce que le client veut faire, vous devez trouver un bon moment pour le rendez-vous. Pour ce faire il faut que tu regarde notre calendrier. Repond: "Je regarde le calendrier." 
               
        Troisièmement, une fois que vous avez trouvé un bon moment pour le rendez-vous, vous devez demander au client ses coordonnées (nom, prénom et numéro de téléphone). 
         
        Quatrièmement, confirmez les coordonnées du client et assurez-vous qu'elles sont correctes. Si vous avez fait une erreur, répétez avec le client jusqu'à ce qu'il confirme que vous avez bien fait les choses.
         
        Cinquièmement, confirmez au client que son rendez-vous a été pris et attendez sa réponse.
         
        Enfin, lorsque toutes les étapes sont terminées ou que l'utilisateur vous dit au revoir, vous devez dire au revoir au client. Veuillez dire explicitement « au revoir » dans votre message.
         
        Vous devez avoir une conversation avec le client et interagir avec lui comme si vous étiez un être humain au téléphone. Ne demandez pas tout d'emblée. Passez chaque étape une par une et attendez que le client réponde, et assurez-vous de terminer chaque étape avant de passer à la suivante.
        """}
    ]

    user_data = {}

    client = get_openai_client()
    
    Sandra_response = chat(conversation_history, client)
    while True:
        user_input = listen()
        if user_input:
            conversation_history.append({"role": "user", "content": user_input})

            # Get Sandra's response from the OpenAI model
            Sandra_response = chat(conversation_history, client)
            
            conversation_history.append({"role": "assistant", "content": Sandra_response})
            
            if 'au revoir' in Sandra_response.lower():
                print(Sandra_response)
                break
            
            # C'est la partie tendue. En gros il faut qu'on arrive a comprendre que c'est le moment de lire le calendrier. Ensuite faut lire le calendrier pour la bonne journée (ca aussi faut le capter de la conv), puis comprendre quels creneaux sont encore dispo (ca ca va faut juste faire une fonction qui prend en params horaire d'ouverture et de fermeture et te pond les horaires dispo dans une string pour la journee consideree). Ensuite faut resortir la string au user. 
            # 
            # Faut qu'on se renseigne plus sur les LLM workflow, la faire tout d'un bloc c'est pas bien. Je sais pas exactement comment implementer le truc, https://github.com/shane-kercheval/llm-workflow ce github donne une idée de ce a quoi ca devrait ressembler mais c'est pas top faut qu'on trouve mieux
            
            if 'regarde le calendrier' in Sandra_response:
                events_df = read_calendar()
                print(events_df)
                Sandra_response = "Nous avons des disponibilités demain de 9h a 11h et de 13h a 15h"
                conversation_history.append({"role": "assistant", "content": Sandra_response})
                
            
            # Print the last message in conversation which is supposed to be SAndra's. 
            print(f"Sandra: {Sandra_response}")
            speak(Sandra_response)

