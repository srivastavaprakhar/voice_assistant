import requests
import logging
from settings.api_config import SERP_API_KEY
from logger import log_system
from voice import speak
from classifier import llm, suppress_output

SERP_API_KEY = SERP_API_KEY

def perform_web_search(query: str, num_results: int = 5):
    log_system(f"WEB SEARCH QUERY: {query}")
    
    if not query.strip():
        speak("I didn't understand what to search for.")
        return

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": num_results
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        results = response.json().get("organic_results", [])
        snippets = [r["snippet"] for r in results if "snippet" in r]
    except Exception as e:
        log_system(f"[web_search_plugin] Web search failed: {e}")
        speak("Sorry, I had trouble fetching results.")
        return

    if not snippets:
        speak("I couldn't find anything useful.")
        return
    
    log_system(f"Web search results: {snippets}")
    prompt = build_prompt(snippets, query)
    
    try:
        with suppress_output():
            output = llm(prompt, max_tokens=256, temperature=0.1, top_p=0.95, echo=False)
        answer = output["choices"][0]["text"].strip()
        log_system(f"LLM Response: {answer}")
        speak(answer if answer else "Sorry, I couldn’t find a useful answer.")
    except Exception as e:
        log_system(f"[web_search_plugin] LLM summarization failed: {e}")
        speak("Sorry, I had trouble generating an answer.")    

def build_prompt(snippets, user_query):
    context = "\n".join(f"- {s}" for s in snippets)
    prompt = f"""You are an assistant that summarizes information from web results.

Search Results:
{context}

Question: {user_query}

Answer in a concise and helpful way:"""
    return prompt
