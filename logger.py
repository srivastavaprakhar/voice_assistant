import datetime
import traceback

def log_llama(msg):
    with open("llm.logs", "a") as f:
        f.write(f"[{timestamp()}] {msg}\n")

def log_system(msg):
    with open("system.log", "a") as f:
        f.write(f"[{timestamp()}] {msg}\n")

def log_exception():
    log_system(traceback.format_exc())

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
