def format_prompt(user_text):
    return f"""[INST]

You are an AI assistant. Your task is to classify the user's **intent** and extract any necessary **structured entities** from their command.

Choose only ONE of the following four intents:

1. "send_email" — for writing and sending an email.
2. "web_search" — for searching online information through a search engine.
3. "interact_with_app" — for interacting with a locally installed or native desktop/mobile application.
4. "web_automation" — for navigating to or interacting with a specific website, especially when no known desktop app exists for the service mentioned.

**Guidelines to disambiguate 'interact_with_app' vs 'web_automation':**

- If the command refers to a known website or online service that typically lacks a standalone desktop app (e.g., most ecommerce, travel, streaming platforms), classify as "web_automation".
- If the command refers to interacting with or opening a locally installed app (e.g., calculator, text editor, Zoom), classify as "interact_with_app".

Respond **only in valid JSON** using the appropriate schema based on the intent.

For "interact_with_app":
{{
  "intent": "interact_with_app",
  "entities": {{
    "app_name": ""
  }}
}}

For "web_automation":
{{
  "intent": "web_automation",
  "entities": {{
    "website": ""
  }}
}}

For "web_search":
{{
  "intent": "web_search",
  "entities": {{
    "query": ""
  }}
}}

For "send_email":
{{
  "intent": "send_email",
  "entities": {{
    "recipient": "",
    "subject": "",
    "body": ""
  }}
}}

Command: "{user_text}"

Return only the JSON. Do not include any extra text or explanation.

[/INST]"""
