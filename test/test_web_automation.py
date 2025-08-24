import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.web_automation import open_and_fill_website

def test_open_website(site_input):
    print(f"[TEST] Attempting to open: {site_input}")
    try:
        open_and_fill_website(site_input)
        print("[TEST] Success!")
    except Exception as e:
        print(f"[TEST] Error: {e}")

if __name__ == "__main__":
    # 🔧 Change this input for testing
    test_open_website("amazon")  # Direct full URL or Site name
    # test_open_website("https://github.com")  # Direct full URL
    # ({"website": "bing.com"})  # Will trigger the ValueError guard
