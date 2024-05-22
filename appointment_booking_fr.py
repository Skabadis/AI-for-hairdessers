import os
import json
from datetime import datetime, timedelta
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

# Simulated schedule data
schedule = {
    "lundi": [("9:00", "9:30"), ("10:00", "10:30"), ("14:00", "14:30")],
    "mardi": [("11:00", "11:30"), ("13:00", "13:30")],
    "mercredi": [("9:00", "9:30"), ("10:00", "10:30"), ("15:00", "15:30")],
    "jeudi": [("11:00", "11:30"), ("14:00", "14:30")],
    "vendredi": [("9:00", "9:30"), ("13:00", "13:30")],
    "samedi": [("10:00", "10:30"), ("11:00", "11:30")],
    "dimanche": []
}

def speak(text):
    """
    Convert the given text to speech and play it.
    
    Args:
    text (str): The text to be converted to speech.
    
    This function uses gTTS to convert the given text to speech in French,
    saves the speech as an MP3 file, plays it, and then removes the MP3 file.
    """
    tts = gTTS(text=text, lang='fr')
    tts.save("response.mp3")
    playsound("response.mp3")
    os.remove("response.mp3")

def listen():
    """
    Listen to the user's voice input and return the recognized text.
    
    Returns:
    str: The recognized text from the user's voice input.
    
    This function uses the SpeechRecognition library to listen to the user's
    voice input through the microphone and convert it to text using Google's
    speech recognition API.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='fr-FR')
        print(f"Vous avez dit: {text}")
        return text
    except sr.UnknownValueError:
        speak("Désolé, je n'ai pas compris. Pouvez-vous répéter?")
        return None
    except sr.RequestError:
        speak("Désolé, le service de reconnaissance vocale est indisponible.")
        return None

def is_slot_available(day, time):
    """
    Check if the given time slot is available on the specified day.
    
    Args:
    day (str): The day of the week (in French).
    time (str): The time slot in HH:MM format.
    
    Returns:
    bool: True if the time slot is available, False otherwise.
    """
    if day in schedule:
        for slot in schedule[day]:
            if slot[0] == time:
                return False
        return True
    return False

def book_appointment(day, time):
    """
    Book an appointment at the given time slot on the specified day.
    
    Args:
    day (str): The day of the week (in French).
    time (str): The time slot in HH:MM format.
    
    Returns:
    str: A confirmation message for the booking.
    """
    if is_slot_available(day, time):
        schedule[day].append((time, (datetime.strptime(time, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")))
        return f"Votre rendez-vous est confirmé le {day} à {time}."
    else:
        return f"Désolé, le créneau de {time} est déjà pris le {day}."

def main():
    speak("Bonjour, bienvenue chez le coiffeur. Comment puis-je vous aider?")
    while True:
        text = listen()
        if text:
            if "rendez-vous" in text.lower():
                speak("Quel jour souhaitez-vous prendre rendez-vous?")
                day = listen().lower()
                if day in schedule:
                    speak("À quelle heure souhaitez-vous prendre rendez-vous?")
                    time = listen()
                    if time:
                        try:
                            datetime.strptime(time, "%H:%M")  # Validate time format
                            confirmation = book_appointment(day, time)
                            speak(confirmation)
                        except ValueError:
                            speak("Le format de l'heure n'est pas valide. Veuillez réessayer.")
                else:
                    speak("Désolé, ce jour n'est pas valide. Veuillez réessayer.")
            elif "arrêter" in text.lower():
                speak("Merci de votre visite. Au revoir!")
                break
            else:
                speak("Je n'ai pas compris. Pouvez-vous répéter?")

if __name__ == "__main__":
    main()
