import sys
import json
import re
from llama_cpp import Llama
from logger import log_llama
from contextlib import contextmanager
import os

@contextmanager
def suppress_output():
    # Redirect both stdout and stderr to null
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Suppress load-time tensor spam
with suppress_output():
    llm = Llama(
        model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",  # ✅ UPDATE if needed
        n_ctx=2048,
        n_threads=4,
        n_batch=64,
        use_mlock=True
    )

def format_prompt(user_text):
    return f"""[INST]Extract the user's intent and structured fields from this command.

Command: "{user_text}"

Respond ONLY with valid JSON in this format:
{{
  "intent": "send_email",
  "entities": {{
    "recipient": "...",
    "subject": "...",
    "body": "..."
  }}
}}[/INST]"""

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            log_llama(f"JSON decode error: {e}")
    raise ValueError("No valid JSON found in LLM output.")

def classify_intent(user_text):
    prompt = format_prompt(user_text)
    log_llama(f"Prompt to LLM:\n{prompt}")
    with suppress_output():
     output = llm(
     prompt,
     stop=["</s>"],
     temperature=0.2,
     top_p=0.95,
     max_tokens=256,  # 🔼 Increase output budget
     echo=False
)
    raw_output = output["choices"][0]["text"]
    log_llama(f"Raw LLM output: {raw_output}")

    try:
        structured = extract_json(raw_output)
        return structured
    except Exception as e:
        log_llama(f"Failed to parse LLM output: {e}")
        return {"intent": "unknown", "entities": {}}

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
6. Output ONLY the final formatted email, like: `john.doe@gmail.com`

Spoken email: "{spoken_email}"

Respond with only the formatted email:
[/INST]"""
    with suppress_output():
        response = llm(prompt, stop=["</s>"], temperature=0.1, max_tokens=32)
    
    result = response["choices"][0]["text"].strip()
    log_llama(f"Formatted email from '{spoken_email}' -> '{result}'")
    return result
