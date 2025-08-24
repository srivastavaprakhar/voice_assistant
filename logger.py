import datetime
import traceback

def log_llm(msg):
    with open("logs/llm.logs", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp()}] {msg}\n")

def log_system(msg):
    with open("logs/system.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp()}] {msg}\n")

def log_exception():
    log_system(traceback.format_exc())

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
