import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.app_interactor import handle_app_interaction

def test_open_app(app_name: str):
    print(f"Testing app: {app_name}")
    try:
        handle_app_interaction({"app_name": app_name})
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
   test_open_app("notepad") # Desktop app
