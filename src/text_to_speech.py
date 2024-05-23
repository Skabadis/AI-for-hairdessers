from gtts import gTTS
import pygame
import time

# Function to convert text to speech and play it
def speak(text):
    tts = gTTS(text=text, lang='fr')
    tts.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.music.unload()
        
if __name__ == "__main__":
    text = "Salut Skandère j'espère que tu vas bien! Bienvenue au salon Lotfi barber."
    speak(text)