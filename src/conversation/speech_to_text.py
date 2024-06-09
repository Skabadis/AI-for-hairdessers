import speech_recognition as sr
import logging
import time

# Function to listen to the user's speech and convert it to text
def listen():
    recognizer = sr.Recognizer()
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

def audio_file_to_text(audio_file):
    recognizer = sr.Recognizer()
    # Load and process the audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        # Speech to text using Google speech model
        start_time = time.time()
        try:
            text = recognizer.recognize_google(audio_data, language='fr-FR')
            end_time = time.time()
            logging.info(f"Converting speech to text: {end_time - start_time:.2f} seconds")
            return text
        except sr.UnknownValueError:
            logging.info("Google could not understand the audio. This happens when the audio quality is poor.")
            end_time = time.time()
            logging.info(f"Converting speech to text: {end_time - start_time:.2f} seconds")
            return None
        except sr.RequestError as e:
            logging.info(f"Error occurred; {e}")
            end_time = time.time()
            logging.info(f"Converting speech to text: {end_time - start_time:.2f} seconds")
            return None
        
        
