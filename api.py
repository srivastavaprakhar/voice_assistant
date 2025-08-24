from fastapi import FastAPI
from pydantic import BaseModel
from recognizer import recognize_speech
from classifier import classify_intent
from intent_dispatcher import dispatch
from voice import speak

app = FastAPI()

class VoiceInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "✅ JARVIS API is online. Use /process-text or /listen endpoints."}

@app.post("/process-text")
def process_text(input: VoiceInput):
    """
    Process plain text input, classify the intent, and dispatch it.
    """
    speak("Processing your request.")
    intent_data = classify_intent(input.text)
    result = dispatch(intent_data)
    return {
        "input_text": input.text,
        "intent_data": intent_data,
        "result": result
    }

@app.get("/listen")
def listen_and_process():
    """
    Listen for voice input, recognize speech, classify intent, and dispatch.
    """
    speak("Listening...")
    text = recognize_speech()
    if not text:
        speak("Couldn't understand. Please try again.")
        return {"error": "Speech not recognized"}

    intent_data = classify_intent(text)
    result = dispatch(intent_data)
    return {
        "recognized_text": text,
        "intent_data": intent_data,
        "result": result
    }
