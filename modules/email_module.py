import smtplib
from email.message import EmailMessage
from logger import log_system
import json
import os
from settings.mail_config import SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT
from voice import speak, ask_via_voice, ask_confirmation
from classifier import format_email_with_llm


CONTACTS_PATH = "data/contacts.json"

def load_contacts():
    if os.path.exists(CONTACTS_PATH):
        with open(CONTACTS_PATH) as f:
            return json.load(f)
    return {}

def save_contacts(contacts):
    os.makedirs(os.path.dirname(CONTACTS_PATH), exist_ok=True)
    with open(CONTACTS_PATH, "w") as f:
        json.dump(contacts, f, indent=2)

def handle_email(entities):
    contacts = load_contacts()
    recipient = entities.get("recipient")
    subject = entities.get("subject")
    body = entities.get("body")

    # 📧 Resolve recipient email
    email = contacts.get(recipient)
    if not email:
        spoken_email = ask_via_voice(f"I don’t have an email for {recipient}. Please say the email address clearly")
        email = format_email_with_llm(spoken_email)
        contacts[recipient] = email
        save_contacts(contacts)
        log_system(f"New contact added: {recipient} -> {email}")

    # 📝 Subject
    if not subject:
        subject = ask_via_voice("What should be the subject of the email?")

    # 💬 Body
    if not body:
        body = ask_via_voice("What should I say in the email?")

    speak(f"Here is the email:\nTo: {email}\nSubject: {subject}\nBody: {body}")
    
    if ask_confirmation("Should I send this email? Say yes to confirm or no to cancel."):
        try:
            msg = EmailMessage()
            msg['From'] = SMTP_USER
            msg['To'] = email
            msg['Subject'] = subject
            msg.set_content(body)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)

            log_system("Email sent successfully.")
            speak("Email sent successfully.")
        except Exception as e:
            log_system(f"Failed to send email: {e}")
            speak("Failed to send the email.")
    else:
        speak("Email not sent.")
