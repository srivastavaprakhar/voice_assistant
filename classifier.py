import sys
import json
import re
from llama_cpp import Llama
from logger import log_llm
from contextlib import contextmanager
import os
from settings.path_config import MODEL_PATH
from LLM.intent_classification_llm import format_prompt
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
        model_path=MODEL_PATH,  # ✅ UPDATE if needed
        n_ctx=4096,  # 🔼 Increase context size
        n_threads=4,
        n_batch=64,
        use_mlock=True
    )


def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            log_llm(f"JSON decode error: {e}")
    raise ValueError("No valid JSON found in LLM output.")

def classify_intent(user_text):
    prompt = format_prompt(user_text)
    log_llm(f"Prompt to LLM:\n{prompt}")
    with suppress_output():
     output = llm(
     prompt,
     temperature=0.1,
     top_p=0.95,
     max_tokens=256,  # 🔼 Increase output budget
     echo=False
)
    raw_output = output["choices"][0]["text"]
    log_llm(f"Raw LLM output: {raw_output}")

    try:
        structured = extract_json(raw_output)
        return structured
    except Exception as e:
        log_llm(f"Failed to parse LLM output: {e}")
        return {"intent": "unknown", "entities": {}}

