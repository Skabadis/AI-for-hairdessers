import speech_recognition as sr
# Initialize OpenAI client
recognizer = sr.Recognizer()

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
        
if __name__ == "__main__":
    listen()