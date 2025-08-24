from classifier import suppress_output
from logger import log_llm
from classifier import llm

def format_email_with_llm(spoken_email):
    prompt = f"""[INST]
You are a speech-to-text formatting assistant.

Convert the spoken form of an email address into a valid, properly formatted email address.

The user may say things like:
- "john dot doe at gmail dot com"
- "my name one two three at outlook dot com"
- "prakhar underscore srivastava at gmail dot com"
- "riya dash khanna at yahoo dot com"

Your job is to:
1. Replace "dot" with "."
2. Replace "at" with "@"
3. Replace "underscore" with "_"
4. Replace "dash" or "hyphen" with "-"
5. Remove any extra spaces
6. Output ONLY the final formatted email, like: johndoe@gmail.com

Spoken email: "{spoken_email}"

Respond with only the formatted email:
[/INST]"""
    with suppress_output():
        response = llm(prompt, stop=["</s>"], temperature=0.1, max_tokens=32)
    
    result = response["choices"][0]["text"].strip()
    log_llm(f"Formatted email from '{spoken_email}' -> '{result}'")
    return result