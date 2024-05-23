import speech_recognition as sr
from gtts import gTTS
import time
import os
import re
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Function to convert text to speech and play it
def speak(text):
    tts = gTTS(text=text, lang='fr')  # Convert text to speech in French
    tts.save("response.mp3")  # Save the speech to a file
    print(f"TTS Output: {text}")  # Print the text
    pygame.mixer.music.load("response.mp3")  # Load the MP3 file
    pygame.mixer.music.play()  # Play the MP3 file
    while pygame.mixer.music.get_busy():  # Wait until the MP3 file is done playing
        time.sleep(0.1)
    os.remove("response.mp3")  # Remove the MP3 file

# Function to recognize speech from the microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant...")  # Prompt the user to speak
        audio = recognizer.listen(source)  # Listen for speech

    try:
        text = recognizer.recognize_google(audio, language='fr-FR')  # Recognize the speech using Google's API
        print(f"Vous avez dit: {text}")  # Print the recognized text
        return text
    except sr.UnknownValueError:
        print("Désolé, je n'ai pas compris.")  # Print error if speech was not understood
        return ""
    except sr.RequestError:
        print("Erreur de service; veuillez vérifier votre connexion.")  # Print error if there was a service issue
        return ""

# Function to check if a specific time slot is available
def check_availability(schedule, day, time, duration=0.5):
    if day in schedule:
        for start, end in schedule[day]:
            if start < time + duration and time < end:  # Check if the time overlaps with any booked slots
                return False
    return True

# Function to book an appointment
def book_appointment(schedule, day, time, duration):
    if day not in schedule:
        schedule[day] = []
    schedule[day].append((time, time + duration))  # Add the new appointment to the schedule
    speak(f"Votre rendez-vous est réservé pour {day} à {format_time(time)}. Merci!")  # Confirm the booking

# Function to parse different time formats into a float value representing hours
def parse_time(time_str):
    patterns = [
        (r'(\d{1,2})h', lambda m: float(m.group(1))),  # Matches "9h", "10h", etc.
        (r'(\d{1,2}):(\d{2})', lambda m: float(m.group(1)) + float(m.group(2))/60),  # Matches "9:00", "10:30", etc.
        (r'(\d{1,2})\s?(AM|PM)', lambda m: float(m.group(1)) + (12 if m.group(2).upper() == 'PM' else 0))  # Matches "9AM", "10PM", etc.
    ]
    for pattern, parser in patterns:
        match = re.match(pattern, time_str)
        if match:
            return parser(match)
    return None

# Function to format a float value (representing hours) into a readable time string
def format_time(time_float):
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours}h{minutes:02d}"

# Function to find and suggest the closest available time slots
def suggest_alternatives(schedule, day, requested_time, duration=0.5):
    step = 0.5  # 30 minutes step
    max_steps = 4  # Check 2 hours ahead and 2 hours back
    alternatives = []
    for i in range(1, max_steps + 1):
        earlier_time = requested_time - i * step
        later_time = requested_time + i * step
        if earlier_time >= 0 and check_availability(schedule, day, earlier_time, duration):
            alternatives.append(earlier_time)
        if check_availability(schedule, day, later_time, duration):
            alternatives.append(later_time)
    return alternatives

# Main function to handle the interaction
def main(schedule):
    speak("Bonjour, comment puis-je vous aider?")  # Greet the user
    while True:
        command = recognize_speech().lower()  # Recognize and get the user's command
        if 'rendez-vous' in command:
            # Extract day and time from the command
            day = None
            time = None
            for d in schedule.keys():
                if d in command:
                    day = d
                    break
            time_match = re.search(r'\b(\d{1,2}h|\d{1,2}:\d{2}|\d{1,2}\s?(AM|PM))\b', command)
            if time_match:
                time_str = time_match.group(1)
                time = parse_time(time_str)

            if day and time is not None:
                duration = 0.5  # 30 minutes
                if check_availability(schedule, day, time, duration):
                    book_appointment(schedule, day, time, duration)  # Book the appointment if available
                else:
                    speak(f"Désolé, {day} à {format_time(time)} est déjà pris.")  # Announce if the slot is taken
                    alternatives = suggest_alternatives(schedule, day, time, duration)
                    if alternatives:
                        message = "Les créneaux disponibles les plus proches sont : " + ', '.join([format_time(t) for t in alternatives])
                        speak(message)
                    else:
                        speak("Je suis désolé, il n'y a pas de créneaux disponibles proches.")
            else:
                speak("Je n'ai pas compris le jour ou l'heure. Veuillez réessayer.")  # Announce if the input was not understood
        elif 'quitter' in command or 'stop' in command:
            speak("Au revoir!")  # Say goodbye and exit
            break

if __name__ == "__main__":
    # Sample schedule; modify to test different scenarios
    schedule = {
        'lundi': [(9.0, 9.5), (10.0, 10.5)],  # 9:00-9:30 and 10:00-10:30 booked
        'mardi': [(11.0, 11.5)],  # 11:00-11:30 booked
    }
    main(schedule)  # Start the main function with the sample schedule
