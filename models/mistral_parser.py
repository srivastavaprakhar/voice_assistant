
from llama_cpp import Llama
import json

llm = Llama(
    model_path="C:/Users/Prakhar Srivastava/Desktop/PROJECTS/voice_assistant/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=4,
    temperature=0.2,
)

def parse_with_mistral(user_text):
    system_prompt = """
You are an AI assistant. Extract the following fields from a user's voice command.
Rules:
- Only extract subject if clearly mentioned.
- Return null for fields not mentioned.
Respond ONLY with JSON:
{
  "intent": "send_email",
  "recipient": "...",
  "subject": null or "...",
  "body": null or "..."
}
"""
    full_prompt = f"<s>[INST] <<SYS>>{system_prompt}<</SYS>>\n{user_text} [/INST]"

    response = llm(full_prompt, stop=["</s>"], max_tokens=512)
    text = response["choices"][0]["text"].strip()

    try:
        return json.loads(text)
    except:
        return {
            "intent": "unknown",
            "recipient": None,
            "subject": None,
            "body": None
        }
