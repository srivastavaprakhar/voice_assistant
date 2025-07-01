from recognizer import recognize_speech
from classifier import classify_intent
from intent_dispatcher import dispatch
from voice import speak,ask_confirmation

def main():
    speak("How can I help you?")
    text = recognize_speech()
    if not text:
        speak("Couldn't understand. Please try again.")
        return

    intent_data = classify_intent(text)
    dispatch(intent_data)

if __name__ == "__main__":
    while True:
        main()
        again = ("Do you want to continue? (y/n): ")
        if not ask_confirmation():
            speak("Goodbye.")
            break
