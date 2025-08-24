MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
APP_REGISTRY = {
    "notepad": {
        "type": "desktop",
        "path": "notepad.exe",
        "title_re": ".*Notepad.*",
        "launch_mode": "exe"
    },
    "calculator": {
        "type": "desktop",
        "path": "calc.exe",
        "title_re": ".*Calculator.*",
        "launch_mode": "exe"
    },
    "spotify": {
        "type": "shortcut",
        "path": "C:\\VoiceAssistantShortcuts\\Spotify.lnk",
        "title_re": ".*Spotify.*",
        "launch_mode": "title"
    },
    "netflix": {
        "type": "shortcut",
        "path": "C:/Users/Prakhar Srivastava/Desktop/Netflix.lnk",
        "title_re": ".*Netflix.*",
        "launch_mode": "title"
    },
    "prime video": {
        "type": "shortcut",
        "path": "C:\\VoiceAssistantShortcuts\\PrimeVideo.lnk",
        "title_re": ".*Prime Video.*",
        "launch_mode": "title"
    },
    "youtube": {
        "type": "shortcut",
        "path": "C:/Users/Prakhar Srivastava/Desktop/YouTube.lnk",
        "title_re": ".*YouTube.*",
        "launch_mode": "title"   
    },
    "word": {
        "type": "shortcut",
        "path": "c:/ProgramData/Microsoft/Windows/Start Menu/Programs/Word.lnk",
        "title_re": ".*Word.*",
        "launch_mode": "title"
    },
    "microsoft edge": {
    "type": "shortcut",
    "path": "C:/Users/Public/Desktop/Microsoft Edge.lnk",
    "title_re": ".*Edge.*",
    "launch_mode": "title_re"
}}