import os
import json
import urllib.parse
from difflib import get_close_matches
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from voice import speak, ask_via_voice
from logger import log_system, log_llm
from classifier import llm, suppress_output
from LLM.generate_prompt_from_controls import generate_prompt_from_controls
from LLM.format_user_response_for_action import format_user_response_for_action

import ast

CREDENTIAL_FILE = os.path.join("data", "credentials.json")

INTERACTIVE_TYPES = ["input", "button"]


def load_credentials(site_key):
    try:
        with open(CREDENTIAL_FILE, "r") as f:
            data = json.load(f)
        return data.get(site_key.lower())
    except Exception as e:
        log_system(f"[ERROR] Failed to load credentials: {e}")
        return None


def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def resolve_url(site_name_or_url):
    if site_name_or_url.startswith("http"):
        return site_name_or_url
    else:
        return f"https://www.{site_name_or_url}.com/"


def get_site_key_from_url(url):
    hostname = urllib.parse.urlparse(url).hostname or ""
    parts = hostname.split(".")
    return parts[1] if "www" in hostname else parts[0]

def open_and_fill_website(site_name_or_url):
    if not site_name_or_url or not isinstance(site_name_or_url, str):
        speak("I couldn't understand the website name.")
        log_system(f"[ERROR] Invalid website name or URL: {site_name_or_url}")
        return

    url = resolve_url(site_name_or_url)

    # Basic validation to avoid malformed URLs
    if " " in url or not url.startswith("http"):
        speak("That doesn't look like a valid website.")
        log_system(f"[ERROR] Malformed URL: {url}")
        return

    try:
        speak("Opening the browser.")
        driver = setup_browser()
        driver.get(url)
    except Exception as e:
        speak("Failed to open the website. Please check your internet or the website name.")
        log_system(f"[ERROR] Failed to load URL '{url}': {e}")
        return

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
    except Exception as e:
        speak("The page took too long to load.")
        log_system(f"[ERROR] Web elements not found on page: {e}")
        return

    site_key = get_site_key_from_url(url)
    creds = load_credentials(site_key)
    fill_known_inputs(driver, creds)

    # Start interactive loop
    interactive_web_control(driver)

def fill_known_inputs(driver, creds):
    inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='password']")
    
    for i, input_field in enumerate(inputs):
        if not input_field.is_displayed():
            continue

        label = (
            input_field.get_attribute("aria-label") or
            input_field.get_attribute("placeholder") or
            input_field.get_attribute("name") or
            f"field {i+1}"
        ).lower()

        try:
            value = get_input_value(label, creds)

            if value:
                input_field.clear()
                input_field.send_keys(value)
                speak(f"I filled your {label}.")
        except Exception as e:
            speak(f"I couldn’t fill {label}.")
            log_system(f"[ERROR] Fill error for {label}: {e}")


def get_input_value(label, creds):
    if not creds:
        return None
    if "user" in label or "email" in label or "login" in label:
        return creds.get("username")
    elif "pass" in label:
        return creds.get("password")
    return None


def extract_web_controls(driver):
    controls = []

    inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='search' or @type='email' or @type='password']")
    for i, ctrl in enumerate(inputs):
        if not ctrl.is_displayed():
            continue
        label = (
            ctrl.get_attribute("aria-label") or
            ctrl.get_attribute("placeholder") or
            ctrl.get_attribute("name") or
            f"input {i+1}"
        ).strip()
        controls.append({"type": "input", "label": label, "element": ctrl})

    buttons = driver.find_elements(By.XPATH, "//button[normalize-space(text()) != '']")
    for i, ctrl in enumerate(buttons):
        if not ctrl.is_displayed():
            continue
        label = ctrl.text.strip() or f"button {i+1}"
        controls.append({"type": "button", "label": label, "element": ctrl})

    return controls


def interactive_web_control(driver):
    for _ in range(10):  # max 10 rounds
        controls = extract_web_controls(driver)
        if not controls:
            speak("No interactive elements found.")
            return

        # Convert for LLM prompt
        controls_json = [{"type": c["type"], "label": c["label"]} for c in controls]
        prompt = generate_prompt_from_controls(controls_json)

        with suppress_output():
            response = llm(prompt, max_tokens=150, temperature=0.3)

        llm_question = response["choices"][0]["text"].strip()
        speak(llm_question)

        user_input = ask_via_voice("What should I do next?")
        if not user_input or "exit" in user_input.lower():
            speak("Closing interaction.")
            break

        action_prompt = format_user_response_for_action(user_input, controls_json)
        with suppress_output():
            parsed = llm(action_prompt, max_tokens=64, temperature=0.1)
            log_llm(f"[LLM] Action parsed: {parsed}")

        try:
            action_data = ast.literal_eval(parsed["choices"][0]["text"].strip())
        except Exception as e:
            speak("I couldn't understand that. Please try again.")
            log_system(f"[ERROR] LLM parse failed: {e}")
            continue

        # Find closest matching control
        match = find_matching_web_control(action_data, controls)
        if not match:
            speak(f"I couldn't find anything matching {action_data.get('target')}.")
            continue

        try:
            if action_data["action"] == "click":
                match["element"].click()
                speak(f"Clicked {match['label']}")
            elif action_data["action"] == "type":
                match["element"].clear()
                match["element"].send_keys(action_data["text"])
                speak(f"Typed in {match['label']}")
        except Exception as e:
            speak("Action failed.")
            log_system(f"[ERROR] Action on control failed: {e}")


def find_matching_web_control(action_data, controls):
    labels = {c["label"].lower(): c for c in controls}
    match = get_close_matches(action_data.get("target", "").lower(), labels.keys(), n=1, cutoff=0.3)
    return labels[match[0]] if match else None
