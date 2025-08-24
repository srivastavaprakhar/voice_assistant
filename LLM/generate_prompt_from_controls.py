from logger import log_llm

def generate_prompt_from_controls(controls_json):
    control_items = "\n".join(
        f"- {c['type'].capitalize()}: '{c.get('label', '').strip()}'" for c in controls_json if c.get('label')
    )
    return f"""[INSTRUCTION]
You are an intelligent assistant helping a user understand and interact with a desktop application interface. Your goal is to guide them toward the most relevant action.

The following are the UI controls currently visible in the app window. Analyze them and generate a natural response:

{control_items}

Your task is to:
1. Focus on controls that allow the user to take direct actions — like entering text (input fields) or clicking a main button (e.g., 'Submit', 'OK', 'Search').
2. Skip passive or system-level controls like 'Close', 'Settings', or 'Help', unless they are the only options.
3. Select the most relevant 3–5 controls and describe them clearly and naturally.
4. Enhance unclear labels (e.g., 'ComboBox' becomes 'dropdown', 'CheckBox' becomes 'check box').
5. End your message by asking the user what they would like to do — e.g., "Would you like to search, play a video, or open downloads?"

Speak naturally — your output should sound like one of these:
- "Would you like to enter your name or click 'Start'?"
- "You can type a search, open the calendar, or press 'Continue'."

Only include labels that are clear and user-facing. Avoid internal or generic labels like 'Button1' or 'Textbox123' unless they are the only controls present.

Now respond with the summarized options and the user prompt.
[/INSTRUCTION]
"""