def format_user_response_for_action(user_input, controls):
    controls_list = "\n".join(f"- {c['type']}: '{c['label']}'" for c in controls)
    return f"""[INST]
You are an assistant that formats natural user instructions into structured JSON commands to interact with an app.

Available controls:
{controls_list}

User said: "{user_input}"

Your job:
- Match the user instruction to one of the controls above.
- Output a JSON object with one of the following formats:

Clicking:
{{ "action": "click", "target": "<label>" }}

Typing:
{{ "action": "type", "target": "<label>", "text": "<what to type>" }}

Important:
- Only use labels from the above list.
- Only output the JSON. No text or explanation.
- The label in "target" must exactly match one of the control labels above.
[/INST]"""
