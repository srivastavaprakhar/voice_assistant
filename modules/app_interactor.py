import subprocess
from time import sleep
import ast
from difflib import get_close_matches
from pywinauto import Application
from pywinauto.findwindows import find_windows, find_elements
from voice import speak, recognize_speech
from settings.path_config import APP_REGISTRY
from logger import log_system, log_llm
from classifier import llm, suppress_output
from LLM.generate_prompt_from_controls import generate_prompt_from_controls
from LLM.format_user_response_for_action import format_user_response_for_action


INTERACTIVE_TYPES = [
    "Edit", "Document", "Button", "ComboBox", "CheckBox",
    "RadioButton", "MenuItem", "Hyperlink", "Slider", "ListItem"
]


def handle_app_interaction(entities):
    app_name = entities.get("app_name", "").lower()
    app_info = APP_REGISTRY.get(app_name)

    if not app_info:
        log_system(f"[ERROR] App '{app_name}' not found in registry.")
        speak(f"I don't know how to open {app_name}.")
        return

    log_system(f"[INFO] Opening app: {app_name} with info: {app_info}")
    speak(f"Opening {app_name}...")

    try:
        open_app(app_info)
        try_interact_with_desktop(app_name)
    except Exception as e:
        log_system(f"[ERROR] Failed to launch app: {e}")
        speak(f"Sorry, I couldn't open {app_name}. Please try again later.")


def open_app(app_info):
    if app_info["type"] == "desktop":
        subprocess.Popen(app_info["path"])
    elif app_info["type"] == "uwp":
        subprocess.Popen(["explorer", f"shell:AppsFolder\\{app_info['aumid']}"])
    elif app_info["type"] == "shortcut":
        subprocess.Popen(app_info["path"], shell=True)
    else:
        raise ValueError("Unknown app type.")


def try_interact_with_desktop(app_name):
    app_info = APP_REGISTRY.get(app_name)
    sleep(6)
    speak("Connecting to the app window...")

    app = connect_to_app(app_info)
    if not app:
        return

    try:
        dlg = app.top_window()
        dlg.set_focus()
        speak(f"Connected to {app_name}. Now scanning for controls...")

        interaction_loop(dlg)
    except Exception as e:
        speak(f"App interaction failed: {str(e)}")
        log_system(f"[ERROR] Interaction: {e}")


def connect_to_app(app_info):
    app = None

    # Try connecting by path
    if app_info.get("launch_mode") == "path":
        for _ in range(3):
            try:
                app = Application(backend="uia").connect(path=app_info["path"])
                return app
            except Exception as e:
                log_system(f"[WARN] Connection by path failed: {e}")
                sleep(2)

    # Try connecting by title
    try:
        app = Application(backend="uia").connect(title_re=app_info["title_re"], found_index=0)
    except Exception as e:
        log_system(f"[WARN] Title regex connection failed: {e}")
        matches = find_windows(title_re=app_info["title_re"], backend="uia")
        if matches:
            app = Application(backend="uia").connect(handle=matches[0])
        else:
            speak(f"I couldn't find any matching windows for {app_info['title_re']}.")
            all_windows = find_elements()
            log_system("Available windows: " + str([(w.name, w.handle) for w in all_windows]))
            return None

    return app


def interaction_loop(dlg):
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        attempts += 1
        all_controls = dlg.descendants()
        filtered_controls = [
            c for c in all_controls if c.element_info.control_type in INTERACTIVE_TYPES
        ]

        log_system(f"[INFO] Found {len(filtered_controls)} interactive controls.")

        if not filtered_controls:
            speak("No buttons or fields found.")
            return

        controls_json = extract_ui_elements_description(filtered_controls)
        prompt = generate_prompt_from_controls(controls_json)

        with suppress_output():
            response = llm(prompt, max_tokens=250, temperature=0.3)

        llm_question = response["choices"][0]["text"].strip()
        speak(llm_question)

        user_input = recognize_speech()
        if not user_input:
            speak("I didn't hear anything. Please try again.")
            continue

        if "exit" in user_input.lower():
            speak("Closing interaction.")
            break

        if not handle_user_input(user_input, controls_json, filtered_controls):
            speak("Sorry, I couldn't perform that action.")
            continue


def handle_user_input(user_input, controls_json, filtered_controls):
    action_prompt = format_user_response_for_action(user_input, controls_json)

    try:
        with suppress_output():
            parsed = llm(action_prompt, max_tokens=64, temperature=0.1)

        action_data = ast.literal_eval(parsed["choices"][0]["text"].strip())
        log_llm(f"[PARSE OK] {action_data}")
    except Exception as e:
        log_llm(f"[ERROR] LLM parse failed: {e}\nRaw: {parsed}")
        speak("Sorry, I couldn't understand that. Please rephrase.")
        return False

    action_type = action_data.get("action")
    if action_type == "click":
        return handle_click_action(action_data, filtered_controls)
    elif action_type == "type":
        return handle_type_action(action_data, filtered_controls)
    return False


def handle_click_action(action_data, controls):
    labels = {
        c.window_text().lower(): c
        for c in controls if c.window_text().strip()
    }
    closest = get_close_matches(action_data["target"].lower(), labels.keys(), n=1, cutoff=0.3)
    if closest:
        ctrl = labels[closest[0]]
        if smart_click(ctrl):
            speak(f"Activated {closest[0]}.")
            return True
        else:
            speak(f"I tried, but {closest[0]} wouldn’t respond.")
    return False


def handle_type_action(action_data, controls):
    target = action_data.get("target", "")
    text = action_data.get("text", "")

    match_ctrl = next((
        c for c in controls
        if target.lower() in c.window_text().lower() and c.is_keyboard_focusable()
    ), None)

    if not match_ctrl:
        match_ctrl = next((
            c for c in controls
            if c.element_info.control_type in ["Edit", "Document"] and c.is_keyboard_focusable()
        ), None)

    if not match_ctrl:
        match_ctrl = next((
            c for c in controls
            if c.element_info.control_type == "Document"
        ), None)

    if match_ctrl:
        try:
            match_ctrl.set_focus()
            try:
                match_ctrl.set_edit_text(text)
            except Exception:
                match_ctrl.type_keys(text, with_spaces=True, pause=0.05)
            speak("Typed the text.")
            return True
        except Exception as e:
            log_llm(f"[ERROR] Typing: {e}")
            speak("Typing failed.")
    else:
        speak("I couldn't find any place to type.")
    return False


def smart_click(ctrl):
    try:
        ctrl.invoke()
        return True
    except Exception:
        pass
    try:
        ctrl.double_click_input()
        return True
    except Exception:
        pass
    try:
        ctrl.click_input()
        ctrl.type_keys("{ENTER}")
        return True
    except Exception as e:
        log_system(f"[CLICK FAIL] All smart_click methods failed: {e}")
        return False


def extract_ui_elements_description(filtered_controls):
    descriptions = []
    for ctrl in filtered_controls:
        ctrl_type = ctrl.element_info.control_type.lower()
        label = ctrl.window_text().strip()
        descriptions.append({
            "type": ctrl_type,
            "label": label or f"unlabeled {ctrl_type}"
        })
    return descriptions
