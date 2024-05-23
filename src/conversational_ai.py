from openai import OpenAI

import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import pandas as pd
import dateparser
from openai_connector import get_openai_client, chat_with_pia

# Initialize OpenAI client
recognizer = sr.Recognizer()

client = get_openai_client()

# Function to convert text to speech and play it
def speak(text):
    tts = gTTS(text=text, lang='fr')
    tts.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

# Function to listen to the user's speech and convert it to text
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio, language="fr-FR")
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

# Function to check if a given date and time slot is available
def check_availability(date, time):
    schedule_df = pd.read_csv('schedule_january_2025.csv')
    slot = schedule_df[(schedule_df['Date'] == date) & (schedule_df['Time'] == time)]
    if not slot.empty and slot.iloc[0]['Booking'] == '':
        return True
    return False

# Function to get the next available date and time slot
def get_next_available_date():
    schedule_df = pd.read_csv('schedule_january_2025.csv')
    available_slot = schedule_df[schedule_df['Booking'] == ''].iloc[0]
    return available_slot['Date'], available_slot['Time']

# Function to book an appointment by updating the schedule CSV file
def book_appointment(date, time, name, service, phone):
    schedule_df = pd.read_csv('schedule_january_2025.csv')
    schedule_df.loc[(schedule_df['Date'] == date) & (schedule_df['Time'] == time), ['Booking', 'Details']] = [name, f'{service}, Tel: {phone}']
    schedule_df.to_csv('schedule_january_2025.csv', index=False)

# Function to parse the date from the user's input
def parse_date(input_text):
    result = dateparser.parse(input_text, settings={'PREFER_DATES_FROM': 'future'})
    if result:
        return result.strftime('%Y-%m-%d')
    return None

if __name__ == "__main__":
    print("Bienvenue chez Skabadis, je suis Pia, comment puis-je vous aider?")
    speak("Bienvenue chez Skabadis, je suis Pia, comment puis-je vous aider?")

    # Initial conversation history for the OpenAI model
    conversation_history = [
        {"role": "system", "content": "You are Pia, a friendly and helpful assistant for Skabadis, a Parisian hairdresser. You respond in French and assist clients with booking appointments."}
    ]

    user_data = {}

    while True:
        user_input = listen()
        if user_input:
            conversation_history.append({"role": "user", "content": user_input})

            # Exit the conversation loop if the user says goodbye
            if any(word in user_input.lower() for word in ['quitte', 'sortir', 'arrêter', 'au revoir', 'bye']):
                speak("Au revoir! Passez une excellente journée!")
                print("Au revoir!")
                break

            # Get Pia's response from the OpenAI model
            pia_response = chat_with_pia(conversation_history, client), 
            conversation_history.append({"role": "assistant", "content": pia_response})

            print(f"Pia: {pia_response}")
            speak(pia_response)

            # If the user mentions booking an appointment, proceed with the booking process
            if "rendez-vous" in user_input.lower():
                parsed_date = parse_date(user_input)
                parsed_time = None

                # Check if the user specified a time of day
                if "matin" in user_input:
                    parsed_time = "10:00"
                elif "après-midi" in user_input:
                    parsed_time = "14:00"
                else:
                    time_parts = user_input.split()
                    for part in time_parts:
                        if ":" in part:
                            parsed_time = part
                            break

                # If both date and time are parsed, check availability
                if parsed_date and parsed_time:
                    if check_availability(parsed_date, parsed_time):
                        # Ask for service if not already provided
                        if 'service' not in user_data:
                            speak("Pour quel service souhaitez-vous réserver?")
                            service = listen()
                            if not service:
                                speak("Je n'ai pas compris le service.")
                                continue
                            user_data['service'] = service

                        # Ask for the user's name if not already provided
                        if 'name' not in user_data:
                            speak("Quel est votre nom?")
                            name = listen()
                            if not name:
                                speak("Je n'ai pas compris votre nom.")
                                continue
                            user_data['name'] = name

                        # Ask for the user's phone number if not already provided
                        if 'phone' not in user_data:
                            speak("Quel est votre numéro de téléphone?")
                            phone = listen()
                            if not phone:
                                speak("Je n'ai pas compris votre numéro de téléphone.")
                                continue
                            user_data['phone'] = phone

                        speak(f"Merci, {user_data['name']}. Je vais maintenant confirmer votre rendez-vous.")
                        book_appointment(parsed_date, parsed_time, user_data['name'], user_data['service'], user_data['phone'])
                        speak(f"Votre rendez-vous est réservé pour le {parsed_date} à {parsed_time} pour {user_data['name']} pour un {user_data['service']}. Merci!")
                        print(f"Appointment booked for {parsed_date} at {parsed_time} for {user_data['name']} for a {user_data['service']}.")
                    else:
                        speak("Désolé, cette heure est déjà réservée. Je vais vérifier les prochaines disponibilités.")
                        next_date, next_time = get_next_available_date()
                        speak(f"La prochaine disponibilité est le {next_date} à {next_time}. Voulez-vous réserver pour ce créneau?")
                        user_response = listen()
                        if user_response and user_response.lower() in ['oui', 'yes', 'd\'accord']:
                            if 'name' not in user_data:
                                speak("Quel est votre nom?")
                                name = listen()
                                if not name:
                                    speak("Je n'ai pas compris votre nom.")
                                    continue
                                user_data['name'] = name

                            if 'service' not in user_data:
                                speak("Pour quel service souhaitez-vous réserver?")
                                service = listen()
                                if not service:
                                    speak("Je n'ai pas compris le service.")
                                    continue
                                user_data['service'] = service

                            if 'phone' not in user_data:
                                speak("Quel est votre numéro de téléphone?")
                                phone = listen()
                                if not phone:
                                    speak("Je n'ai pas compris votre numéro de téléphone.")
                                    continue
                                user_data['phone'] = phone

                            speak(f"Merci, {user_data['name']}. Je vais maintenant confirmer votre rendez-vous.")
                            book_appointment(next_date, next_time, user_data['name'], user_data['service'], user_data['phone'])
                            speak(f"Votre rendez-vous est réservé pour le {next_date} à {next_time} pour {user_data['name']} pour un {user_data['service']}. Merci!")
                            print(f"Appointment booked for {next_date} at {next_time} for {user_data['name']} for a {user_data['service']}.")
                        else:
                            speak("D'accord, n'hésitez pas à me dire quand vous souhaitez réserver.")

    # Display the updated schedule
    schedule_df = pd.read_csv('schedule_january_2025.csv')
    print(schedule_df)
