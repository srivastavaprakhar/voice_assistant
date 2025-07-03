import requests
import logging
from settings.api_config import SERP_API_KEY
from logger import log_system

SERP_API_KEY = SERP_API_KEY

def perform_web_search(query: str, num_results: int = 5):
    log_system(f"WEB SEARCH QUERY: {query}")
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
        return snippets[:num_results]
    except Exception as e:
        logging.error(f"[web_search_plugin] Web search failed: {e}")
        return []

def build_prompt(snippets, user_query):
    context = "\n".join(f"- {s}" for s in snippets)
    prompt = f"""You are an assistant that summarizes information from web results.

Search Results:
{context}

Question: {user_query}

Answer in a concise and helpful way:"""
    return prompt
