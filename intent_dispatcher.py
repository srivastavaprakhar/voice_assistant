from modules import email_module
from logger import log_system
from voice import speak
from modules.web_search import perform_web_search
from modules.web_automation import open_and_fill_website
from modules.app_interactor import handle_app_interaction

INTENT_HANDLERS = {
    "send_email": email_module.handle_email,
    "search_web": lambda entities: perform_web_search(entities.get("query", "")),
    "web_automation": lambda entities: open_and_fill_website(entities.get("website","")),
    "interact_with_app": handle_app_interaction
}

def dispatch(intent_data):
    intent = intent_data.get("intent")
    log_system(f"Dispatching intent: {intent}")
    handler = INTENT_HANDLERS.get(intent)
    if handler:
        handler(intent_data["entities"])
    else:
        speak("Sorry, I don’t understand that yet.")