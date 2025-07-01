from modules import email_module
from logger import log_system
from voice import speak

INTENT_HANDLERS = {
    "send_email": email_module.handle_email
    # Future: "set_reminder": reminder_module.handle_reminder
}

def dispatch(intent_data):
    intent = intent_data.get("intent")
    log_system(f"Dispatching intent: {intent}")
    handler = INTENT_HANDLERS.get(intent)
    if handler:
        handler(intent_data["entities"])
    else:
        speak("Sorry, I don’t understand that yet.")