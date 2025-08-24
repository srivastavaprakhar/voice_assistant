import pyttsx3
from recognizer import recognize_speech

engine = pyttsx3.init()
engine.setProperty('rate', 175)

def speak(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

def ask_via_voice(prompt_text, validator=None, retry_message="I didn’t catch that. Please try again."):
    while True:
        speak(prompt_text)
        response = recognize_speech()
        if response:
            response = response.strip()
            if validator and not validator(response):
                speak("That didn’t seem valid.")
            else:
                return response
        else:
            speak(retry_message)

YES_WORDS = {"yes", "yeah", "yep", "sure", "affirmative", "ok", "okay", "send it", "do it"}
NO_WORDS = {"no", "nope", "nah", "never", "cancel", "don't", "stop"}

def ask_confirmation(prompt_text="Should I proceed?"):
    while True:
        speak(prompt_text)
        response = recognize_speech()
        if not response:
            speak("I didn’t catch that. Please say yes or no.")
            continue

        response = response.strip().lower()

        if any(word in response for word in YES_WORDS):
            return True
        if any(word in response for word in NO_WORDS):
            return False

        speak("Please say yes or no.")