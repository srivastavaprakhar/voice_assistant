import speech_recognition as sr
from logger import log_system

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        log_system(f"Recognized speech: {text}")
        return text
    except Exception as e:
        log_system(f"Speech recognition failed: {e}")
        return None
